"""Crash-recoverable, bounded SQLite work queue for existing Jarvis fulfillment.

No billing mutations, no external delivery, and no secret persistence.
A local worker must be invoked by an existing authorized operator/runtime.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import secrets
import sqlite3
import time
from typing import Callable, Mapping
from urllib.error import URLError

from core import (
    PaidAuditIntake, QUICKCHECK_MAX_FILES, QUICKCHECK_MAX_TOTAL_BYTES,
    parse_public_github_repo, run_public_github_audit,
)

QUEUE_SCHEMA = "jarvis-paid-fulfillment-queue-r149"
MAX_ATTEMPTS = 3
LEASE_SECONDS = 300
RETRY_BASE_SECONDS = 30


def _now(value: int | None = None) -> int:
    return int(time.time()) if value is None else int(value)


def _connect(path: str) -> sqlite3.Connection:
    db = sqlite3.connect(path, timeout=5)
    db.execute("PRAGMA busy_timeout=5000")
    db.execute(
        "CREATE TABLE IF NOT EXISTS fulfillment_results ("
        "session_id TEXT PRIMARY KEY, payload TEXT NOT NULL, updated_at INTEGER NOT NULL)"
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS fulfillment_jobs ("
        "session_id TEXT PRIMARY KEY, intake_digest TEXT NOT NULL, intake_json TEXT NOT NULL, "
        "state TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0, "
        "lease_until INTEGER NOT NULL DEFAULT 0, next_attempt_at INTEGER NOT NULL DEFAULT 0, "
        "claim_token TEXT, created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL)"
    )
    db.execute(
        "CREATE INDEX IF NOT EXISTS fulfillment_jobs_ready_idx "
        "ON fulfillment_jobs(state, next_attempt_at, lease_until, created_at)"
    )
    db.commit()
    return db


def _save_result(db: sqlite3.Connection, session_id: str, record: dict, now: int) -> None:
    db.execute(
        "INSERT INTO fulfillment_results(session_id,payload,updated_at) VALUES(?,?,?) "
        "ON CONFLICT(session_id) DO UPDATE SET payload=excluded.payload, "
        "updated_at=excluded.updated_at",
        (session_id, json.dumps(record, sort_keys=True), now),
    )


def enqueue_paid_checkout(path: str, intake: PaidAuditIntake, *, now: int | None = None) -> str:
    """Atomically persist one job, or preserve a prior result and existing job."""
    stamp = _now(now)
    if not intake.session_id.startswith("cs_") or len(intake.session_id) > 200:
        raise ValueError("invalid Checkout session identifier")
    try:
        owner, repo = parse_public_github_repo(intake.project)
        canonical_project = f"https://github.com/{owner}/{repo}"
        state = "QUEUED"
    except ValueError:
        canonical_project = ""
        state = "HOLD"
    safe_intake = {
        "schema": QUEUE_SCHEMA,
        "session_id": intake.session_id,
        "project": canonical_project,
        "problem": intake.problem[:200],
        "scope": intake.scope[:200],
        "offer": intake.offer,
        "intake_digest": intake.digest,
        "customer_email_present": bool(intake.customer_email),
    }
    db = _connect(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        old = db.execute(
            "SELECT payload FROM fulfillment_results WHERE session_id=?", (intake.session_id,)
        ).fetchone()
        row = db.execute(
            "SELECT intake_digest, state FROM fulfillment_jobs WHERE session_id=?",
            (intake.session_id,),
        ).fetchone()
        if row:
            if row[0] != intake.digest:
                raise ValueError("conflicting signed Checkout intakes for same session")
            db.commit()
            return "DUPLICATE_" + row[1]
        # Older R1/R148 rows are never automatically reprocessed.
        if old:
            db.commit()
            return "LEGACY_RESULT_UNCHANGED"
        db.execute(
            "INSERT INTO fulfillment_jobs("
            "session_id,intake_digest,intake_json,state,created_at,updated_at"
            ") VALUES(?,?,?,?,?,?)",
            (intake.session_id, intake.digest, json.dumps(safe_intake, sort_keys=True),
             state, stamp, stamp),
        )
        _save_result(
            db, intake.session_id,
            {"status": state, "session_id": intake.session_id,
             "intake_digest": intake.digest, "delivery_verified": False,
             "reason_code": "TARGET_OUT_OF_SCOPE" if state == "HOLD" else None}, stamp,
        )
        db.commit()
        return state
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@dataclass(frozen=True)
class Claim:
    session_id: str
    token: str
    attempt: int
    intake: dict


def claim_next_job(
    path: str, *, now: int | None = None, lease_seconds: int = LEASE_SECONDS,
    max_attempts: int = MAX_ATTEMPTS,
) -> Claim | None:
    """Fenced, atomic claim; leases make a worker crash recoverable."""
    if lease_seconds < 1 or max_attempts < 1:
        raise ValueError("lease_seconds and max_attempts must be positive")
    stamp = _now(now)
    db = _connect(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        for _ in range(100):
            row = db.execute(
                "SELECT session_id,intake_json,state,attempts FROM fulfillment_jobs "
                "WHERE (state='QUEUED' OR (state='RETRY' AND next_attempt_at<=?) "
                "OR (state='PROCESSING' AND lease_until<=?)) "
                "ORDER BY created_at,session_id LIMIT 1", (stamp, stamp),
            ).fetchone()
            if row is None:
                db.commit()
                return None
            session_id, raw_intake, _state, attempts = row
            if attempts >= max_attempts:
                db.execute(
                    "UPDATE fulfillment_jobs SET state='HOLD',claim_token=NULL,updated_at=? "
                    "WHERE session_id=?", (stamp, session_id),
                )
                _save_result(
                    db, session_id, {"status": "HOLD", "session_id": session_id,
                                     "reason_code": "RETRY_EXHAUSTED",
                                     "delivery_verified": False}, stamp,
                )
                continue
            token = secrets.token_hex(16)
            attempt = attempts + 1
            db.execute(
                "UPDATE fulfillment_jobs SET state='PROCESSING',attempts=?,claim_token=?,"
                "lease_until=?,updated_at=? WHERE session_id=?",
                (attempt, token, stamp + lease_seconds, stamp, session_id),
            )
            _save_result(
                db, session_id, {"status": "PROCESSING", "session_id": session_id,
                                 "attempt": attempt, "delivery_verified": False}, stamp,
            )
            db.commit()
            return Claim(session_id, token, attempt, json.loads(raw_intake))
        db.commit()
        return None
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def finish_claim(
    path: str, claim: Claim, *, result: Mapping[str, object] | None = None,
    reason_code: str = "", retryable: bool = False, now: int | None = None,
) -> bool:
    """A stale worker cannot overwrite a newer claim, READY receipt, or HOLD."""
    stamp = _now(now)
    db = _connect(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute(
            "SELECT state,claim_token,attempts FROM fulfillment_jobs WHERE session_id=?",
            (claim.session_id,),
        ).fetchone()
        if row is None or row[0] != "PROCESSING" or row[1] != claim.token:
            db.commit()
            return False
        if result is not None:
            state, next_at = "READY", 0
            record = {
                "status": "READY", "session_id": claim.session_id,
                "intake_digest": claim.intake["intake_digest"],
                "customer_email_present": claim.intake["customer_email_present"],
                "report": dict(result), "delivery_verified": False, "created_at": stamp,
            }
        else:
            can_retry = retryable and row[2] < MAX_ATTEMPTS
            state = "RETRY" if can_retry else "HOLD"
            next_at = stamp + RETRY_BASE_SECONDS * (2 ** (row[2] - 1)) if can_retry else 0
            record = {
                "status": state, "session_id": claim.session_id,
                "reason_code": reason_code or "AUDIT_FAILED",
                "delivery_verified": False,
            }
        db.execute(
            "UPDATE fulfillment_jobs SET state=?,claim_token=NULL,lease_until=0,"
            "next_attempt_at=?,updated_at=? WHERE session_id=?",
            (state, next_at, stamp, claim.session_id),
        )
        _save_result(db, claim.session_id, record, stamp)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def process_one(
    path: str, *,
    audit_fn: Callable[..., Mapping[str, object]] = run_public_github_audit,
    now: int | None = None,
) -> str:
    """One local bounded task; no HTTP worker endpoint or unsolicited delivery."""
    claim = claim_next_job(path, now=now)
    if claim is None:
        return "NO_ACTION"
    intake = claim.intake
    limits = (
        {"max_files": QUICKCHECK_MAX_FILES, "max_total_bytes": QUICKCHECK_MAX_TOTAL_BYTES}
        if intake["offer"] in {"repo_quickcheck_first_5", "repo_quickcheck_9"} else {}
    )
    try:
        report = audit_fn(intake["project"], intake["problem"], intake["scope"], **limits)
    except (TimeoutError, ConnectionError, URLError, OSError):
        finish_claim(path, claim, reason_code="TRANSIENT_SOURCE_FAILURE",
                     retryable=True, now=now)
        return "RETRY_OR_HOLD"
    except Exception:
        # Never put untrusted exception text (possibly containing secrets) in a receipt.
        finish_claim(path, claim, reason_code="AUDIT_REQUIRES_REVIEW", now=now)
        return "HOLD"
    if not finish_claim(path, claim, result=report, now=now):
        return "STALE_CLAIM_REJECTED"
    return "READY_NOT_DELIVERED"
