"""Fail-closed local readiness checks for Stripe paid fulfillment R148."""
from __future__ import annotations
import hashlib
import hmac
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "jarvis_paid_fulfillment"))
from fastapi.testclient import TestClient
from app import app


def sign(payload: bytes, secret: str) -> str:
    when = int(time.time())
    digest = hmac.new(secret.encode(), str(when).encode() + b"." + payload, hashlib.sha256).hexdigest()
    return f"t={when},v1={digest}"


def test_status_is_not_false_proof_of_authority(monkeypatch):
    monkeypatch.delenv("JARVIS_AUTOFULFILLMENT_ENABLED", raising=False)
    monkeypatch.delenv("JARVIS_RESULT_DB", raising=False)
    monkeypatch.delenv("STRIPE_WEBHOOK_SECRET", raising=False)
    with TestClient(app) as client:
        health = client.get("/health")
        ready = client.get("/ready")
    assert health.status_code == 200
    assert health.json()["commercial_fulfillment_authority_granted"] is False
    assert health.json()["delivery_verified"] is False
    assert health.json()["configuration_ready"] is False
    assert ready.status_code == 503
    assert ready.json()["external_webhook_destination_verified"] is False


def test_signed_paid_order_returns_503_without_storage(monkeypatch):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_nonproduction_test")
    monkeypatch.setenv("JARVIS_AUTOFULFILLMENT_ENABLED", "true")
    monkeypatch.delenv("JARVIS_RESULT_DB", raising=False)
    event = {"id": "evt_test", "type": "checkout.session.completed",
             "data": {"object": {"id": "cs_test_r148", "payment_status": "paid"}}}
    payload = json.dumps(event).encode()
    with TestClient(app) as client:
        response = client.post("/stripe/webhook", content=payload,
                               headers={"stripe-signature": sign(payload, "whsec_nonproduction_test")})
    assert response.status_code == 503
    assert "disabled" in response.json()["detail"]


def test_configured_not_equivalent_to_delivery_verified(monkeypatch, tmp_path):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_nonproduction_test")
    monkeypatch.setenv("JARVIS_AUTOFULFILLMENT_ENABLED", "true")
    monkeypatch.setenv("JARVIS_RESULT_DB", str(tmp_path / "result.sqlite3"))
    with TestClient(app) as client:
        response = client.get("/ready")
    assert response.status_code == 200
    checks = response.json()
    assert checks["configuration_ready"] is True
    assert checks["durable_storage_verified"] is False
    assert checks["independent_delivery_verified"] is False


def test_result_read_paths_are_not_cached(monkeypatch):
    with TestClient(app) as client:
        bad = client.get("/receipt/not-a-session")
        pending = client.get("/result?session_id=wrong")
    assert bad.status_code == 400 and pending.status_code == 400
    for resp in (bad, pending):
        assert resp.headers["cache-control"] == "private, no-store"
        assert resp.headers["referrer-policy"] == "no-referrer"
        assert resp.headers["x-robots-tag"] == "noindex, nofollow"
