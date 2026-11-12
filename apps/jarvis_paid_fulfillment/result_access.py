"""R150: narrowly scoped, short-lived capability tokens for report reads.

This module does not authenticate a buyer or deliver a token. An already-authorized
fulfillment owner must verify the recipient independently before issuing one.
"""
from __future__ import annotations

import hashlib
import hmac
import re
import time


MAX_ACCESS_TTL_SECONDS = 900
_MIN_SECRET_BYTES = 32
_SESSION_ID = re.compile(r"cs_[A-Za-z0-9_-]{6,197}\Z")
_SIGNATURE = re.compile(r"[a-f0-9]{64}\Z")
_PURPOSE = "jarvis-paid-fulfillment/report-read/r150"


def _session_valid(session_id: str) -> bool:
    return isinstance(session_id, str) and bool(_SESSION_ID.fullmatch(session_id))


def access_secret_valid(secret: str) -> bool:
    return isinstance(secret, str) and len(secret.encode("utf-8")) >= _MIN_SECRET_BYTES


def _signature(session_id: str, expires_at: int, secret: str) -> str:
    message = f"{_PURPOSE}|{session_id}|{expires_at}".encode("utf-8")
    return hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()


def issue_result_access_token(
    session_id: str, secret: str, *,
    ttl_seconds: int = 600, now: int | None = None,
) -> str:
    """Issue only after external recipient authorization (not done here)."""
    if not _session_valid(session_id):
        raise ValueError("invalid session identifier")
    if not access_secret_valid(secret):
        raise ValueError("separate result access secret must have at least 32 UTF-8 bytes")
    if type(ttl_seconds) is not int or not 1 <= ttl_seconds <= MAX_ACCESS_TTL_SECONDS:
        raise ValueError("invalid result access TTL")
    timestamp = int(time.time()) if now is None else int(now)
    expiry = timestamp + ttl_seconds
    return f"r150.{expiry}.{_signature(session_id, expiry, secret)}"


def verify_result_access(
    session_id: str, authorization: str, secret: str, *,
    now: int | None = None,
) -> bool:
    """No session ID, Stripe webhook secret, or query string alone grants access."""
    if not _session_valid(session_id) or not access_secret_valid(secret):
        return False
    if not isinstance(authorization, str) or not authorization.startswith("Bearer "):
        return False
    parts = authorization[7:].split(".")
    if len(parts) != 3 or parts[0] != "r150":
        return False
    raw_expiry, supplied = parts[1], parts[2]
    if not raw_expiry.isascii() or not raw_expiry.isdecimal() or len(raw_expiry) > 11:
        return False
    if not _SIGNATURE.fullmatch(supplied):
        return False
    expiry = int(raw_expiry)
    timestamp = int(time.time()) if now is None else int(now)
    if not 0 < expiry - timestamp <= MAX_ACCESS_TTL_SECONDS:
        return False
    expected = _signature(session_id, expiry, secret)
    return hmac.compare_digest(expected, supplied)
