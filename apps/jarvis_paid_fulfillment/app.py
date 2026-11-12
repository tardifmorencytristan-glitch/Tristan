from __future__ import annotations

import os
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse

from core import (
    claim_result_slot,
    intake_from_checkout_session,
    QUICKCHECK_MAX_FILES,
    QUICKCHECK_MAX_TOTAL_BYTES,
    load_result,
    render_report_html,
    run_public_github_audit,
    store_result,
    verify_stripe_signature,
)

app = FastAPI(title="Jarvis Paid Fulfillment R1.1", version="1.1")
def result_db_path() -> str:
    """Single source of truth for storage used by readiness, workers, and reads."""
    return os.environ.get("JARVIS_RESULT_DB", "/tmp/jarvis_paid_fulfillment_r1.sqlite3")


def fulfillment_prerequisites() -> dict[str, bool]:
    """Local configuration checks, never a proof of live delivery or authority."""
    db_path = result_db_path().strip()
    ephemeral = (
        not os.environ.get("JARVIS_RESULT_DB", "").strip()
        or db_path == ":memory:"
        or db_path.startswith(("file::memory:", "/tmp/", "/var/tmp/"))
    )
    enabled = os.environ.get("JARVIS_AUTOFULFILLMENT_ENABLED", "").lower() in {"1", "true"}
    secret_set = bool(os.environ.get("STRIPE_WEBHOOK_SECRET", "").strip())
    non_temp_path = not ephemeral
    return {
        "webhook_secret_configured": secret_set,
        "fulfillment_opt_in": enabled,
        "sqlite_non_temp_path_configured": non_temp_path,
        "configuration_ready": secret_set and enabled and non_temp_path,
        "durable_storage_verified": False,
        "external_webhook_destination_verified": False,
        "independent_delivery_verified": False,
    }


@app.middleware("http")
async def protect_paid_result_responses(request: Request, call_next):
    response = await call_next(request)
    if request.url.path == "/result" or request.url.path.startswith("/receipt/"):
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
        response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/health")
def health():
    config = fulfillment_prerequisites()
    return {
        "status": "alive",
        "service": "jarvis-paid-fulfillment-r1.1",
        "storage": "sqlite-path-unverified" if config["sqlite_non_temp_path_configured"] else "sqlite-ephemeral",
        "commercial_fulfillment_authority_granted": False,
        "scientific_authority_granted": False,
        "configuration_ready": config["configuration_ready"],
        "delivery_verified": False,
    }


@app.get("/ready")
def ready():
    """Local operational prerequisite probe; NOT payment/delivery proof."""
    checks = fulfillment_prerequisites()
    return JSONResponse(checks, status_code=200 if checks["configuration_ready"] else 503)


@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    signature = request.headers.get("stripe-signature", "")
    if not verify_stripe_signature(payload, signature, secret):
        raise HTTPException(400, "invalid Stripe signature")
    import json
    event = json.loads(payload.decode("utf-8"))
    if event.get("type") not in {
        "checkout.session.completed",
        "checkout.session.async_payment_succeeded",
    }:
        return {"received": True, "action": "NO_ACTION"}
    if not fulfillment_prerequisites()["configuration_ready"]:
        # Return a retryable failure: never ACK a paid order while intake cannot persist.
        raise HTTPException(503, "fulfillment disabled or persistent result store not configured")
    session = (event.get("data") or {}).get("object") or {}
    try:
        intake = intake_from_checkout_session(session)
    except ValueError:
        return {"received": True, "action": "HOLD_NOT_AUDIT_OFFER"}

    claimed = claim_result_slot(
        result_db_path(),
        intake.session_id,
        {"status": "PROCESSING", "intake_digest": intake.digest},
    )
    if not claimed:
        return {"received": True, "action": "IDEMPOTENT_ALREADY_CLAIMED"}

    try:
        limits = (
            {"max_files": QUICKCHECK_MAX_FILES, "max_total_bytes": QUICKCHECK_MAX_TOTAL_BYTES}
            if intake.offer in {"repo_quickcheck_first_5", "repo_quickcheck_9"}
            else {}
        )
        report = run_public_github_audit(
            intake.project,
            intake.problem,
            intake.scope,
            **limits,
        )
        record = {
            "status": "READY",
            "created_at": int(time.time()),
            "session_id": intake.session_id,
            "intake_digest": intake.digest,
            "customer_email_present": bool(intake.customer_email),
            "report": report,
        }
    except Exception as exc:
        record = {
            "status": "HOLD",
            "created_at": int(time.time()),
            "session_id": intake.session_id,
            "intake_digest": intake.digest,
            "reason": type(exc).__name__ + ": " + str(exc)[:300],
            "boundaries": [
                "UnsupportedOrFailed != FabricatedReport",
                "Payment != SecurityCertification",
            ],
        }
    store_result(result_db_path(), intake.session_id, record)
    return {
        "received": True,
        "action": record["status"],
        "session_id": intake.session_id,
    }


@app.get("/result", response_class=HTMLResponse)
def result(session_id: str):
    if not session_id.startswith("cs_") or len(session_id) > 200:
        raise HTTPException(400, "invalid session_id")
    record = load_result(result_db_path(), session_id)
    if record is None:
        return HTMLResponse(
            "<html><meta http-equiv='refresh' content='3'>"
            "<body><h1>Preparing your Jarvis audit...</h1>"
            "<p>This page refreshes automatically. R1.1 storage is ephemeral; "
            "if the service was redeployed after purchase, support may need to replay the Stripe event.</p>"
            "</body></html>",
            status_code=202,
        )
    if record.get("status") == "PROCESSING":
        return HTMLResponse(
            "<html><meta http-equiv='refresh' content='3'>"
            "<body><h1>Audit in progress...</h1></body></html>",
            status_code=202,
        )
    if record.get("status") == "HOLD":
        return HTMLResponse(
            "<html><body><h1>Audit held safely</h1>"
            "<p>The submitted public project could not be processed inside the "
            "bounded automation envelope. No result was invented.</p></body></html>",
            status_code=200,
        )
    return HTMLResponse(render_report_html(record["report"]))


@app.get("/receipt/{session_id}")
def receipt(session_id: str):
    if not session_id.startswith("cs_") or len(session_id) > 200:
        raise HTTPException(400, "invalid session_id")
    record = load_result(result_db_path(), session_id)
    if record is None:
        raise HTTPException(404, "receipt not ready")
    if record.get("status") != "READY":
        return JSONResponse(record, status_code=202)
    return record
