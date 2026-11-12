"""R150 zero-network tests: result access is independent of Checkout identity.

A correctly signed token is a read capability, NOT proof of buyer identity.
An authorized delivery owner must verify the recipient before issuance.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "jarvis_paid_fulfillment"))
import app as fulfillment
from core import store_result
from result_access import (
    MAX_ACCESS_TTL_SECONDS,
    issue_result_access_token,
    verify_result_access,
)

SECRET = "only_for_tests_result_access_123456789_ABCDEFGHIJKLM"
SESSION = "cs_test_r150_alpha"
OTHER_SESSION = "cs_test_r150_beta"


def auth(session=SESSION, secret=SECRET, ttl_seconds=600, now=None):
    return {"Authorization": "Bearer " + issue_result_access_token(
        session, secret, ttl_seconds=ttl_seconds, now=now
    )}


def fixture_ready(monkeypatch, tmp_path):
    db = str(tmp_path / "results.sqlite3")
    monkeypatch.setenv("JARVIS_RESULT_DB", db)
    monkeypatch.setenv("JARVIS_RESULT_ACCESS_SECRET", SECRET)
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "completely_separate_webhook_test_secret")
    store_result(db, SESSION, {
        "status": "READY", "session_id": SESSION,
        "report": {"status": "REVIEW", "repository": {"full_name": "org/private-context"},
                   "digest": "bounded-report-test-only", "findings": [],
                   "boundaries": ["Report != Delivery"]},
        "delivery_verified": False,
    })
    return db


def test_capability_accepts_correct_session_and_window():
    token = issue_result_access_token(SESSION, SECRET, ttl_seconds=300, now=1000)
    assert verify_result_access(SESSION, "Bearer " + token, SECRET, now=1000)
    assert verify_result_access(SESSION, "Bearer " + token, SECRET, now=1299)
    assert not verify_result_access(SESSION, "Bearer " + token, SECRET, now=1300)
    assert not verify_result_access(OTHER_SESSION, "Bearer " + token, SECRET, now=1000)
    assert not verify_result_access(SESSION, "Bearer " + token, SECRET + "tamper", now=1000)


@pytest.mark.parametrize("header", [
    "", "Bearer", "Bearer ", "Basic dGVzdA==", "Bearer r150.broken.signature",
    "Bearer r150.99999999999999999.x", "Bearer r150.1001." + "0" * 64,
    "Bearer r149.1001." + "0" * 64, "Bearer r150.1001." + "f" * 64 + "\n",
    "Bearer r150.1001." + "f" * 64 + ".extra",
])
def test_invalid_tokens_fail_closed(header):
    assert not verify_result_access(SESSION, header, SECRET, now=1000)


def test_token_cannot_outlive_maximum_ttl():
    with pytest.raises(ValueError):
        issue_result_access_token(SESSION, SECRET, ttl_seconds=MAX_ACCESS_TTL_SECONDS + 1)
    with pytest.raises(ValueError):
        issue_result_access_token(SESSION, SECRET, ttl_seconds=0)
    with pytest.raises(ValueError):
        issue_result_access_token(SESSION, SECRET, ttl_seconds=True)


def test_weak_secret_invalid_session_and_stripe_secret_fail():
    with pytest.raises(ValueError):
        issue_result_access_token(SESSION, "weak")
    with pytest.raises(ValueError):
        issue_result_access_token("not_cs", SECRET)
    assert not verify_result_access(SESSION, "Bearer ignored", "", now=10)
    assert not verify_result_access("cs_bad", auth()["Authorization"], SECRET, now=10)


def test_anonymous_result_and_receipt_are_rejected_before_database_lookup(monkeypatch, tmp_path):
    fixture_ready(monkeypatch, tmp_path)
    def forbidden_read(*args, **kwargs):
        raise AssertionError("No customer record may be loaded before authorization")
    monkeypatch.setattr(fulfillment, "load_result", forbidden_read)
    with TestClient(fulfillment.app) as client:
        pages = [
            client.get("/result", params={"session_id": SESSION}),
            client.get("/receipt/" + SESSION),
            client.get("/result", params={
                "session_id": SESSION, "access_token": issue_result_access_token(SESSION, SECRET)
            }),
        ]
    assert all(p.status_code == 401 for p in pages)
    assert all(p.headers["cache-control"] == "private, no-store" for p in pages)
    assert all("AccessDenied" not in p.text and "bounded-report-test-only" not in p.text for p in pages)


def test_authorized_read_requires_header_and_does_not_claim_delivery(monkeypatch, tmp_path):
    fixture_ready(monkeypatch, tmp_path)
    with TestClient(fulfillment.app) as client:
        denied = client.get("/receipt/" + SESSION, headers=auth(OTHER_SESSION))
        receipt = client.get("/receipt/" + SESSION, headers=auth())
        rendered = client.get("/result", params={"session_id": SESSION}, headers=auth())
    assert denied.status_code == 401
    assert receipt.status_code == 200
    assert receipt.json()["delivery_verified"] is False
    assert receipt.json()["report"]["digest"] == "bounded-report-test-only"
    assert rendered.status_code == 200
    assert "bounded-report-test-only" in rendered.text
    assert rendered.headers["x-robots-tag"] == "noindex, nofollow"
    assert rendered.headers["referrer-policy"] == "no-referrer"


def test_explicit_result_secret_absent_cannot_be_bypassed(monkeypatch, tmp_path):
    fixture_ready(monkeypatch, tmp_path)
    monkeypatch.delenv("JARVIS_RESULT_ACCESS_SECRET")
    with TestClient(fulfillment.app) as client:
        out = client.get("/receipt/" + SESSION, headers=auth())
        status = client.get("/ready")
    assert out.status_code == 401
    assert status.json()["result_access_secret_configured"] is False


def test_result_secret_cannot_equal_stripe_webhook_secret(monkeypatch, tmp_path):
    fixture_ready(monkeypatch, tmp_path)
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", SECRET)
    with TestClient(fulfillment.app) as client:
        out = client.get("/receipt/" + SESSION, headers=auth())
        ready = client.get("/ready")
    assert out.status_code == 401
    assert ready.json()["result_access_secret_configured"] is False


def test_invalid_session_id_is_rejected_before_authorization(monkeypatch):
    monkeypatch.delenv("JARVIS_RESULT_ACCESS_SECRET", raising=False)
    with TestClient(fulfillment.app) as client:
        assert client.get("/receipt/wrong").status_code == 400
        assert client.get("/result?session_id=wrong").status_code == 400
