from __future__ import annotations

import os
import json
import sqlite3

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse

from core import (
    intake_from_checkout_session,
    load_result,
    render_report_html,
    verify_stripe_signature,
)
from fulfillment_queue import enqueue_paid_checkout
from result_access import access_secret_valid, verify_result_access


app = FastAPI(title="Jarvis Paid Fulfillment R1.3", version="1.3")
def result_db_path() -> str:
    """Single source of truth for storage used by readiness, workers, and reads."""
    return os.environ.get("JARVIS_RESULT_DB", "/tmp/jarvis_paid_fulfillment_r1.sqlite3")


def require_result_access(session_id: str, request: Request) -> None:
    """Fail closed; authentication must precede even looking up an order."""
    secret = os.environ.get("JARVIS_RESULT_ACCESS_SECRET", "")
    header = request.headers.get("authorization", "")
    if (
        secret == os.environ.get("STRIPE_WEBHOOK_SECRET", "")
        or not verify_result_access(session_id, header, secret)
    ):
        raise HTTPException(
            status_code=401, detail="report access denied",
            headers={"WWW-Authenticate": "Bearer"},
        )


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
        "result_access_secret_configured": (
            access_secret_valid(os.environ.get("JARVIS_RESULT_ACCESS_SECRET", ""))
            and os.environ.get("JARVIS_RESULT_ACCESS_SECRET", "")
            != os.environ.get("STRIPE_WEBHOOK_SECRET", "")
        ),
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
        "service": "jarvis-paid-fulfillment-r1.3",
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
    if len(payload) > 262_144:
        raise HTTPException(413, "webhook payload exceeds limit")
    secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    signature = request.headers.get("stripe-signature", "")
    if not verify_stripe_signature(payload, signature, secret):
        raise HTTPException(400, "invalid Stripe signature")
    try:
        event = json.loads(payload)
    except (ValueError, UnicodeDecodeError):
        raise HTTPException(400, "invalid webhook JSON") from None
    if not isinstance(event, dict) or not isinstance(event.get("data"), dict):
        raise HTTPException(400, "invalid webhook event")
    if event.get("type") not in {
        "checkout.session.completed",
        "checkout.session.async_payment_succeeded",
    }:
        return {"received": True, "action": "NO_ACTION"}
    if not fulfillment_prerequisites()["configuration_ready"]:
        raise HTTPException(503, "fulfillment disabled or persistent result store not configured")
    session = event["data"].get("object")
    if not isinstance(session, dict):
        raise HTTPException(400, "invalid Checkout Session object")
    try:
        intake = intake_from_checkout_session(session)
    except ValueError:
        return {"received": True, "action": "HOLD_NOT_PAID_OR_SUPPORTED"}
    try:
        outcome = enqueue_paid_checkout(result_db_path(), intake)
    except sqlite3.Error:
        # Stripe retries when a signed event cannot be committed to storage.
        raise HTTPException(503, "checkout queue unavailable") from None
    except ValueError:
        raise HTTPException(409, "conflicting Checkout intake; manual reconciliation required") from None
    return {"received": True, "action": outcome, "session_id": intake.session_id}


@app.get("/result", response_class=HTMLResponse)
def result(session_id: str, request: Request):
    if not session_id.startswith("cs_") or len(session_id) > 200:
        raise HTTPException(400, "invalid session_id")
    require_result_access(session_id, request)
    record = load_result(result_db_path(), session_id)
    if record is None:
        return HTMLResponse(
            "<html><meta http-equiv='refresh' content='3'>"
            "<body><h1>Preparing your Jarvis audit...</h1>"
            "<p>Status is not yet available. Storage and delivery require operational verification; "
            "if processing is interrupted, support must reconcile the order.</p>"
            "</body></html>",
            status_code=202,
        )
    if record.get("status") in {"QUEUED", "PROCESSING", "RETRY"}:
        return HTMLResponse(
            "<html><meta http-equiv='refresh' content='3'>"
            "<body><h1>Audit queued, in progress, or awaiting safe retry.</h1></body></html>",
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
def receipt(session_id: str, request: Request):
    if not session_id.startswith("cs_") or len(session_id) > 200:
        raise HTTPException(400, "invalid session_id")
    require_result_access(session_id, request)
    record = load_result(result_db_path(), session_id)
    if record is None:
        raise HTTPException(404, "receipt not ready")
    if record.get("status") != "READY":
        return JSONResponse(
            {"status": record.get("status"), "session_id": session_id,
             "delivery_verified": False},
            status_code=200 if record.get("status") == "HOLD" else 202,
        )
    return record