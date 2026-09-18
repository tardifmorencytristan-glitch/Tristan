from __future__ import annotations

import json
import os
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from redis import Redis

from core import (
    intake_from_checkout_session,
    render_report_html,
    run_public_github_audit,
    verify_stripe_signature,
)

app = FastAPI(title="Jarvis Paid Fulfillment R1", version="1.0")
RESULT_TTL = 60 * 60 * 24 * 30

def _redis() -> Redis:
    url = os.environ.get("REDIS_URL", "").strip()
    if not url:
        raise RuntimeError("REDIS_URL is not configured")
    return Redis.from_url(url, decode_responses=True)

def _key(session_id: str) -> str:
    return "jarvis:fulfillment:r1:" + session_id

@app.get("/health")
def health():
    return {"status": "ok", "service": "jarvis-paid-fulfillment-r1", "authority_granted": False}

@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    signature = request.headers.get("stripe-signature", "")
    if not verify_stripe_signature(payload, signature, secret):
        raise HTTPException(400, "invalid Stripe signature")
    event = json.loads(payload.decode("utf-8"))
    if event.get("type") not in {"checkout.session.completed", "checkout.session.async_payment_succeeded"}:
        return {"received": True, "action": "NO_ACTION"}
    session = (event.get("data") or {}).get("object") or {}
    try:
        intake = intake_from_checkout_session(session)
    except ValueError:
        return {"received": True, "action": "HOLD_NOT_AUDIT_OFFER"}
    redis = _redis()
    key = _key(intake.session_id)
    existing = redis.get(key)
    if existing:
        return {"received": True, "action": "IDEMPOTENT_ALREADY_FULFILLED"}
    redis.set(key, json.dumps({"status": "PROCESSING", "intake_digest": intake.digest}), ex=RESULT_TTL, nx=True)
    try:
        report = run_public_github_audit(intake.project, intake.problem, intake.scope)
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
            "boundaries": ["UnsupportedOrFailed != FabricatedReport", "Payment != SecurityCertification"],
        }
    redis.set(key, json.dumps(record, sort_keys=True), ex=RESULT_TTL)
    return {"received": True, "action": record["status"], "session_id": intake.session_id}

@app.get("/result", response_class=HTMLResponse)
def result(session_id: str):
    if not session_id.startswith("cs_") or len(session_id) > 200:
        raise HTTPException(400, "invalid session_id")
    raw = _redis().get(_key(session_id))
    if not raw:
        return HTMLResponse("<html><meta http-equiv='refresh' content='3'><body><h1>Preparing your Jarvis audit...</h1><p>This page refreshes automatically.</p></body></html>", status_code=202)
    record = json.loads(raw)
    if record.get("status") == "PROCESSING":
        return HTMLResponse("<html><meta http-equiv='refresh' content='3'><body><h1>Audit in progress...</h1></body></html>", status_code=202)
    if record.get("status") == "HOLD":
        return HTMLResponse("<html><body><h1>Audit held safely</h1><p>The submitted public project could not be processed inside the bounded automation envelope. No result was invented.</p></body></html>", status_code=200)
    return HTMLResponse(render_report_html(record["report"]))

@app.get("/receipt/{session_id}")
def receipt(session_id: str):
    raw = _redis().get(_key(session_id))
    if not raw:
        raise HTTPException(404, "receipt not ready")
    record = json.loads(raw)
    if record.get("status") != "READY":
        return JSONResponse(record, status_code=202)
    return record
