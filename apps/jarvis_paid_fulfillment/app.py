from __future__ import annotations

import os
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse

from core import (
    claim_result_slot,
    intake_from_checkout_session,
    load_result,
    render_report_html,
    run_public_github_audit,
    store_result,
    verify_stripe_signature,
)

app = FastAPI(title="Jarvis Paid Fulfillment R1.1", version="1.1")
RESULT_DB = os.environ.get(
    "JARVIS_RESULT_DB",
    "/tmp/jarvis_paid_fulfillment_r1.sqlite3",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "jarvis-paid-fulfillment-r1.1",
        "storage": "sqlite-ephemeral",
        "authority_granted": False,
    }


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
    session = (event.get("data") or {}).get("object") or {}
    try:
        intake = intake_from_checkout_session(session)
    except ValueError:
        return {"received": True, "action": "HOLD_NOT_AUDIT_OFFER"}

    claimed = claim_result_slot(
        RESULT_DB,
        intake.session_id,
        {"status": "PROCESSING", "intake_digest": intake.digest},
    )
    if not claimed:
        return {"received": True, "action": "IDEMPOTENT_ALREADY_CLAIMED"}

    try:
        report = run_public_github_audit(
            intake.project,
            intake.problem,
            intake.scope,
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
    store_result(RESULT_DB, intake.session_id, record)
    return {
        "received": True,
        "action": record["status"],
        "session_id": intake.session_id,
    }


@app.get("/result", response_class=HTMLResponse)
def result(session_id: str):
    if not session_id.startswith("cs_") or len(session_id) > 200:
        raise HTTPException(400, "invalid session_id")
    record = load_result(RESULT_DB, session_id)
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
    record = load_result(RESULT_DB, session_id)
    if record is None:
        raise HTTPException(404, "receipt not ready")
    if record.get("status") != "READY":
        return JSONResponse(record, status_code=202)
    return record
