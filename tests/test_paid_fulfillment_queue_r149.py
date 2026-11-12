"""Deterministic, network-free R149 queue/lease/replay tests."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sqlite3
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "jarvis_paid_fulfillment"))
from core import PaidAuditIntake, load_result
from fulfillment_queue import (
    MAX_ATTEMPTS, QUEUE_SCHEMA, claim_next_job, enqueue_paid_checkout,
    finish_claim, process_one,
)


def sample(session="cs_test_r149", project="https://github.com/example/repo", email="private@example.com"):
    return PaidAuditIntake(
        session_id=session, project=project, problem="Review dependencies",
        scope="read-only analysis", customer_email=email,
        payment_link="plink_test", offer="repo_quickcheck_first_5",
    ).with_digest()


def job_table(db):
    with sqlite3.connect(db) as cx:
        return cx.execute(
            "SELECT session_id,state,attempts,intake_json FROM fulfillment_jobs ORDER BY session_id"
        ).fetchall()


def test_enqueue_is_atomic_and_preserves_minimal_information(tmp_path):
    db = str(tmp_path / "job.sqlite3")
    intake = sample(project="https://github.com/example/repo?secret=DO_NOT_PERSIST")
    assert enqueue_paid_checkout(db, intake, now=10) == "QUEUED"
    rows = job_table(db)
    assert len(rows) == 1 and rows[0][1] == "QUEUED"
    assert rows[0][2] == 0 and load_result(db, intake.session_id)["status"] == "QUEUED"
    raw = rows[0][3]
    assert QUEUE_SCHEMA.startswith("jarvis-")
    assert "DO_NOT_PERSIST" not in raw
    assert "private@example.com" not in raw
    assert json.loads(raw)["project"] == "https://github.com/example/repo"
    assert json.loads(raw)["customer_email_present"] is True


def test_second_event_for_same_paid_session_does_not_restart_work(tmp_path):
    db = str(tmp_path / "job.sqlite3")
    intake = sample()
    assert enqueue_paid_checkout(db, intake, now=10) == "QUEUED"
    assert enqueue_paid_checkout(db, intake, now=11) == "DUPLICATE_QUEUED"
    assert len(job_table(db)) == 1
    c = claim_next_job(db, now=12)
    assert c is not None and c.attempt == 1
    assert enqueue_paid_checkout(db, intake, now=13) == "DUPLICATE_PROCESSING"
    assert len(job_table(db)) == 1


def test_conflicting_intake_fails_closed(tmp_path):
    db = str(tmp_path / "job.sqlite3")
    assert enqueue_paid_checkout(db, sample(), now=10) == "QUEUED"
    try:
        enqueue_paid_checkout(db, sample(project="https://github.com/example/different"), now=11)
    except ValueError:
        pass
    else:
        raise AssertionError("conflict must not silently mutate an active order")
    assert len(job_table(db)) == 1


def test_invalid_project_is_held_without_storing_user_supplied_url(tmp_path):
    db = str(tmp_path / "job.sqlite3")
    intake = sample(project="https://user:private@evil.example/a/b?token=hidden")
    assert enqueue_paid_checkout(db, intake, now=10) == "HOLD"
    raw = job_table(db)[0][3]
    assert "token" not in raw and "private" not in raw
    assert json.loads(raw)["project"] == ""
    assert claim_next_job(db, now=11) is None


def test_expired_lease_reclaim_and_fencing(tmp_path):
    db = str(tmp_path / "job.sqlite3")
    assert enqueue_paid_checkout(db, sample(), now=10) == "QUEUED"
    first = claim_next_job(db, now=11, lease_seconds=10)
    assert first and first.attempt == 1
    assert claim_next_job(db, now=19, lease_seconds=10) is None
    second = claim_next_job(db, now=22, lease_seconds=10)
    assert second and second.token != first.token and second.attempt == 2
    assert not finish_claim(db, first, result={"digest": "old"}, now=23)
    assert finish_claim(db, second, result={"digest": "new"}, now=24)
    ready = load_result(db, sample().session_id)
    assert ready["status"] == "READY" and ready["report"]["digest"] == "new"
    assert ready["delivery_verified"] is False
    assert claim_next_job(db, now=100) is None


def test_worker_processes_single_bounded_job_without_external_delivery(tmp_path):
    db = str(tmp_path / "job.sqlite3")
    enqueue_paid_checkout(db, sample(), now=10)
    calls = []
    def fake(project, problem, scope, **limits):
        calls.append((project, problem, scope, limits))
        return {"status": "REVIEW", "digest": "synthetic"}
    assert process_one(db, audit_fn=fake, now=11) == "READY_NOT_DELIVERED"
    assert len(calls) == 1
    assert calls[0][3] == {"max_files": 10, "max_total_bytes": 500_000}
    assert load_result(db, sample().session_id)["report"]["digest"] == "synthetic"
    assert process_one(db, audit_fn=fake, now=100) == "NO_ACTION"
    assert len(calls) == 1


def test_network_timeout_backoff_then_succeeds(tmp_path):
    db = str(tmp_path / "job.sqlite3")
    enqueue_paid_checkout(db, sample(), now=10)
    def fail(*args, **kwargs):
        raise TimeoutError("do not echo sensitive exception")
    assert process_one(db, audit_fn=fail, now=11) == "RETRY_OR_HOLD"
    assert load_result(db, sample().session_id)["status"] == "RETRY"
    assert claim_next_job(db, now=40) is None
    assert process_one(db, audit_fn=lambda *a, **k: {"digest": "retry-ok"}, now=42) == "READY_NOT_DELIVERED"
    assert load_result(db, sample().session_id)["report"]["digest"] == "retry-ok"


def test_failed_retry_is_bounded(tmp_path):
    db = str(tmp_path / "job.sqlite3")
    enqueue_paid_checkout(db, sample(), now=1)
    def fail(*args, **kwargs):
        raise TimeoutError("private_access_token")
    for tick in (2, 33, 95):
        assert process_one(db, audit_fn=fail, now=tick) == "RETRY_OR_HOLD"
    result = load_result(db, sample().session_id)
    assert result["status"] == "HOLD"
    assert "private_access_token" not in json.dumps(result)
    assert job_table(db)[0][2] == MAX_ATTEMPTS
    assert claim_next_job(db, now=9999) is None


def test_nontransient_error_requires_manual_review(tmp_path):
    db = str(tmp_path / "job.sqlite3")
    enqueue_paid_checkout(db, sample(), now=1)
    def invalid(*a, **k):
        raise ValueError("secret should never enter public receipt")
    assert process_one(db, audit_fn=invalid, now=2) == "HOLD"
    result = load_result(db, sample().session_id)
    assert result["reason_code"] == "AUDIT_REQUIRES_REVIEW"
    assert "secret" not in json.dumps(result)


def test_legacy_processing_is_not_silently_reprocessed(tmp_path):
    from core import store_result
    db = str(tmp_path / "job.sqlite3")
    store_result(db, sample().session_id, {"status": "PROCESSING", "version": "R148"})
    assert enqueue_paid_checkout(db, sample(), now=10) == "LEGACY_RESULT_UNCHANGED"
    assert claim_next_job(db, now=11) is None
    assert load_result(db, sample().session_id)["status"] == "PROCESSING"


def test_concurrent_deliveries_create_one_job(tmp_path):
    db = str(tmp_path / "job.sqlite3")
    intake = sample()
    with ThreadPoolExecutor(max_workers=6) as pool:
        outcomes = list(pool.map(lambda _: enqueue_paid_checkout(db, intake), range(12)))
    assert outcomes.count("QUEUED") == 1
    assert outcomes.count("DUPLICATE_QUEUED") == 11
    assert len(job_table(db)) == 1


def test_missing_storage_directory_never_acknowledges(tmp_path):
    db = str(tmp_path / "absent_parent" / "jobs.sqlite3")
    try:
        enqueue_paid_checkout(db, sample())
    except sqlite3.OperationalError:
        pass
    else:
        raise AssertionError("cannot acknowledge when queue cannot persist")
