"""R149 signed webhook → durable queue → receipt integration tests (offline only)."""
from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "jarvis_paid_fulfillment"))
from fastapi.testclient import TestClient
from app import app
from core import QUICKCHECK_PAYMENT_LINK_ID, load_result
from fulfillment_queue import process_one
from result_access import issue_result_access_token
from worker import main as worker_main


SECRET = "whsec_r149_fixture_not_live"
ACCESS_SECRET = "r149_test_access_secret_only_ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def access_headers(session_id="cs_test_r149"):
    return {"Authorization": "Bearer " + issue_result_access_token(session_id, ACCESS_SECRET)}


def paid(session_id="cs_test_r149", project="https://github.com/example/repo",
         payment_status="paid", event_id="evt_r149"):
    return {
        "id": event_id, "type": "checkout.session.completed",
        "data": {"object": {
            "id": session_id, "payment_status": payment_status,
            "payment_link": QUICKCHECK_PAYMENT_LINK_ID,
            "metadata": {"offer": "repo_quickcheck_first_5",
                         "fulfillment": "jarvis_quickcheck_v1"},
            "custom_fields": [{"key": "project", "text": {"value": project}}],
            "customer_details": {"email": "private-buyer@example.org"},
        }},
    }


def signature(payload: bytes, secret: str = SECRET):
    stamp = int(time.time())
    digest = hmac.new(secret.encode(), str(stamp).encode() + b"." + payload, hashlib.sha256).hexdigest()
    return f"t={stamp},v1={digest}"


def post(client, event, **overrides):
    payload = json.dumps(event, separators=(",", ":")).encode()
    return client.post("/stripe/webhook", content=payload,
                       headers={"stripe-signature": overrides.get("signature", signature(payload))})


def configure(monkeypatch, tmp_path):
    dest = str(tmp_path / "store.sqlite3")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", SECRET)
    monkeypatch.setenv("JARVIS_RESULT_ACCESS_SECRET", ACCESS_SECRET)
    monkeypatch.setenv("JARVIS_AUTOFULFILLMENT_ENABLED", "true")
    monkeypatch.setenv("JARVIS_RESULT_DB", dest)
    return dest


def test_signed_paid_event_is_queued_without_running_analysis(monkeypatch, tmp_path):
    dest = configure(monkeypatch, tmp_path)
    with TestClient(app) as client:
        reply = post(client, paid())
        assert reply.status_code == 200
        assert reply.json()["action"] == "QUEUED"
        again = post(client, paid(event_id="evt_r149_duplicate"))
        assert again.status_code == 200
        assert again.json()["action"] == "DUPLICATE_QUEUED"
        queued = client.get("/receipt/cs_test_r149", headers=access_headers())
        progress = client.get("/result?session_id=cs_test_r149", headers=access_headers())
    assert queued.status_code == 202
    assert queued.json()["status"] == "QUEUED"
    assert "private-buyer" not in queued.text
    assert "example/repo" not in queued.text
    assert progress.status_code == 202
    assert load_result(dest, "cs_test_r149")["delivery_verified"] is False


def test_async_payment_not_fulfilled_until_paid(monkeypatch, tmp_path):
    dest = configure(monkeypatch, tmp_path)
    e = paid(payment_status="unpaid")
    with TestClient(app) as client:
        unpaid = post(client, e)
        assert unpaid.status_code == 200
        assert unpaid.json()["action"] == "HOLD_NOT_PAID_OR_SUPPORTED"
        e["id"] = "evt_r149_async"
        e["type"] = "checkout.session.async_payment_succeeded"
        e["data"]["object"]["payment_status"] = "paid"
        done = post(client, e)
        assert done.status_code == 200 and done.json()["action"] == "QUEUED"
    assert load_result(dest, "cs_test_r149")["status"] == "QUEUED"


def test_invalid_signature_json_and_oversize_are_rejected(monkeypatch, tmp_path):
    configure(monkeypatch, tmp_path)
    payload = b'{invalid'
    with TestClient(app) as client:
        forged = post(client, paid(), signature="t=1,v1=invalid")
        assert forged.status_code == 400
        malformed = client.post("/stripe/webhook", content=payload,
                                headers={"stripe-signature": signature(payload)})
        assert malformed.status_code == 400
        oversize = client.post("/stripe/webhook", content=b"x" * 262_145,
                               headers={"stripe-signature": signature(b"x" * 262_145)})
        assert oversize.status_code == 413
    assert not (tmp_path / "store.sqlite3").exists()


def test_unavailable_sqlite_returns_retryable_503(monkeypatch, tmp_path):
    configure(monkeypatch, tmp_path)
    monkeypatch.setenv("JARVIS_RESULT_DB", str(tmp_path / "missing" / "store.sqlite3"))
    with TestClient(app) as client:
        r = post(client, paid())
    assert r.status_code == 503


def test_mismatched_resubmission_is_not_silent(monkeypatch, tmp_path):
    configure(monkeypatch, tmp_path)
    with TestClient(app) as client:
        first = post(client, paid())
        assert first.status_code == 200
        second = post(client, paid(project="https://github.com/example/different",
                                   event_id="evt_r149_change"))
    assert second.status_code == 409


def test_worker_result_is_generated_not_delivered(monkeypatch, tmp_path):
    dest = configure(monkeypatch, tmp_path)
    with TestClient(app) as client:
        assert post(client, paid()).json()["action"] == "QUEUED"
    def fake_audit(project, problem, scope, **kwargs):
        return {
            "status": "REVIEW",
            "repository": {"full_name": "example/repo"},
            "digest": "synthetic-proof-r149", "findings": [],
            "boundaries": ["Audit != Certification"],
        }
    assert process_one(dest, audit_fn=fake_audit) == "READY_NOT_DELIVERED"
    with TestClient(app) as client:
        ready = client.get("/receipt/cs_test_r149", headers=access_headers())
        page = client.get("/result?session_id=cs_test_r149", headers=access_headers())
    assert ready.status_code == 200
    assert ready.json()["status"] == "READY"
    assert ready.json()["delivery_verified"] is False
    assert "private-buyer" not in ready.text
    assert page.status_code == 200 and "synthetic-proof-r149" in page.text
    assert page.headers["cache-control"] == "private, no-store"


def test_no_public_worker_endpoint_and_check_does_not_process(monkeypatch, tmp_path, capsys):
    configure(monkeypatch, tmp_path)
    with TestClient(app) as client:
        assert client.post("/worker").status_code == 404
    assert worker_main(["--check"]) == 0
    msg = capsys.readouterr().out
    assert "configuration_ready" in msg
    assert SECRET not in msg


def test_failed_order_receipt_discloses_only_status(monkeypatch, tmp_path):
    configure(monkeypatch, tmp_path)
    with TestClient(app) as client:
        assert post(client, paid(project="invalid-private-url?secret=XYZ")).json()["action"] == "HOLD"
        hold = client.get("/receipt/cs_test_r149", headers=access_headers())
        rendered = client.get("/result?session_id=cs_test_r149", headers=access_headers())
    assert hold.status_code == 200
    assert hold.json()["status"] == "HOLD"
    assert "XYZ" not in hold.text
    assert rendered.status_code == 200
