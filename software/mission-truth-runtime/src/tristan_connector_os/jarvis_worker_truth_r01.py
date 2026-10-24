from __future__ import annotations

"""Fail-closed worker execution-truth kernel.

This module does not execute arbitrary commands, grant authority, schedule
machines, or verify its own high-risk side effects. It turns a selected,
authorized pure handler invocation into an evidence-bearing receipt.

DONE is intentionally not a state in this protocol.
"""

from dataclasses import asdict, dataclass, replace
from hashlib import sha256
import json
import math
import socket
from typing import Callable, Mapping, MutableMapping

PROTOCOL = "OMEGA-JARVIS-WORKER-TRUTH-R0.1"
FINAL_STATES = frozenset(
    {"VERIFIED", "FAILED", "HOLD_AUTHORITY", "HOLD_VERIFICATION", "NOOP_ACK"}
)

BLOCKING_SEMANTIC_PREFIXES = (
    "HOLD",
    "FAIL",
    "ERROR",
    "BLOCK",
    "REJECT",
    "DENY",
)
def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
        allow_nan=False,
    ).encode("utf-8")


def digest(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


def _positive(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and > 0")
    return value


def semantic_status_from_stdout(stdout: str) -> str | None:
    """Read the last explicit JSON status emitted by a child process."""

    for line in reversed((stdout or "").splitlines()):
        candidate = line.strip()
        if not candidate:
            continue
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(value, Mapping):
            status = value.get("status")
            if isinstance(status, str) and status.strip():
                return status.strip().upper()
    return None


def semantic_status_is_blocking(status: str | None) -> bool:
    return bool(status) and str(status).upper().startswith(
        BLOCKING_SEMANTIC_PREFIXES
    )


def observe_process_truth(
    process_returncode: int,
    stdout: str,
) -> ProcessTruthObservation:
    """Classify process success separately from child semantic truth.

    A zero process exit never creates a VERIFIED claim. Explicit child HOLD/FAIL
    families dominate process success and remain a semantic hold.
    """

    code = int(process_returncode)
    semantic_status = semantic_status_from_stdout(stdout)
    semantic_blocking = semantic_status_is_blocking(semantic_status)
    if code != 0:
        state = "PROCESS_FAILED"
    elif semantic_blocking:
        state = "SEMANTIC_HOLD"
    else:
        state = "PROCESS_SUCCESS_UNVERIFIED"
    return ProcessTruthObservation(
        process_returncode=code,
        process_succeeded=code == 0,
        semantic_status=semantic_status,
        semantic_blocking=semantic_blocking,
        state=state,
    )


@dataclass(frozen=True)
class HandlerSpec:
    handler_id: str
    version: str
    authority_scope: str
    side_effect_class: str
    timeout_seconds: float = 30.0
    def __post_init__(self) -> None:
        if not self.handler_id.strip() or not self.version.strip():
            raise ValueError("handler_id and version are required")
        if not self.authority_scope.strip():
            raise ValueError("authority_scope is required")
        if not self.side_effect_class.strip():
            raise ValueError("side_effect_class is required")
        _positive(self.timeout_seconds, "timeout_seconds")


@dataclass(frozen=True)
class ProcessTruthObservation:
    process_returncode: int
    process_succeeded: bool
    semantic_status: str | None
    semantic_blocking: bool
    state: str


@dataclass(frozen=True)
class WorkerReceipt:
    protocol: str
    job_id: str
    job_type: str
    input_digest: str
    status: str
    node: str
    handler_id: str | None = None
    handler_version: str | None = None
    authority_scope: str | None = None
    side_effect_class: str | None = None
    executed: bool = False
    verified: bool = False
    output_digest: str | None = None
    error_type: str | None = None
    idempotency_key: str | None = None
    reused_receipt: bool = False
    receipt_digest: str = ""
    def with_digest(self) -> "WorkerReceipt":
        body = asdict(replace(self, receipt_digest=""))
        return replace(self, receipt_digest=digest(body))


Handler = Callable[[Mapping[str, object]], Mapping[str, object]]
Verifier = Callable[[Mapping[str, object], Mapping[str, object]], bool]


@dataclass
class VerifiedReceiptStore:
    receipts: MutableMapping[str, WorkerReceipt]


def idempotency_key(
    job: Mapping[str, object],
    spec: HandlerSpec,
) -> str:
    return digest(
        {
            "job": job,
            "handler_id": spec.handler_id,
            "handler_version": spec.version,
            "authority_scope": spec.authority_scope,
        }
    )


def _base_receipt(job: Mapping[str, object]) -> WorkerReceipt:
    return WorkerReceipt(
        protocol=PROTOCOL,
        job_id=str(job.get("id", "")),
        job_type=str(job.get("type", "")),
        input_digest=digest(job),
        status="NOOP_ACK",
        node=socket.gethostname(),
    )
def process_job(
    job: Mapping[str, object],
    *,
    handlers: Mapping[str, tuple[HandlerSpec, Handler]],
    authority_scopes: frozenset[str],
    verifier: Verifier | None,
    store: VerifiedReceiptStore,
) -> WorkerReceipt:
    """Execute one explicitly registered handler under a bounded authority set."""

    base = _base_receipt(job)
    selected = handlers.get(base.job_type)
    if selected is None:
        return replace(base, status="NOOP_ACK").with_digest()

    spec, handler = selected
    bound = replace(
        base,
        handler_id=spec.handler_id,
        handler_version=spec.version,
        authority_scope=spec.authority_scope,
        side_effect_class=spec.side_effect_class,
    )
    if spec.authority_scope not in authority_scopes:
        return replace(bound, status="HOLD_AUTHORITY").with_digest()

    key = idempotency_key(job, spec)
    prior = store.receipts.get(key)
    if prior is not None:
        return replace(prior, reused_receipt=True).with_digest()

    payload = job.get("payload", {})
    if not isinstance(payload, Mapping):
        payload = {}
    try:
        output = dict(handler(payload))
    except Exception as exc:
        return replace(
            bound,
            status="FAILED",
            error_type=type(exc).__name__,
            idempotency_key=key,
        ).with_digest()
    observed = replace(
        bound,
        status="HOLD_VERIFICATION",
        executed=True,
        output_digest=digest(output),
        idempotency_key=key,
    )
    if verifier is None:
        return observed.with_digest()
    if not verifier(payload, output):
        return observed.with_digest()

    verified = replace(observed, status="VERIFIED", verified=True).with_digest()
    store.receipts[key] = verified
    return verified


def assert_truthful(receipt: WorkerReceipt) -> None:
    """Fail if a terminal receipt overclaims execution or verification."""

    if receipt.status not in FINAL_STATES:
        raise ValueError(f"unexpected terminal state: {receipt.status}")
    if receipt.status == "VERIFIED":
        if not receipt.executed or not receipt.verified or not receipt.output_digest:
            raise ValueError("VERIFIED requires observed execution and output")
    if receipt.status in {"NOOP_ACK", "HOLD_AUTHORITY", "FAILED"}:
        if receipt.verified:
            raise ValueError(f"{receipt.status} cannot be verified")
    if receipt.status == "NOOP_ACK" and receipt.executed:
        raise ValueError("NOOP_ACK cannot claim execution")


def hash_text(payload: Mapping[str, object]) -> Mapping[str, object]:
    data = str(payload.get("text", "")).encode("utf-8")
    return {"sha256": sha256(data).hexdigest(), "bytes": len(data)}


HASH_TEXT_SPEC = HandlerSpec(
    handler_id="HASH_TEXT",
    version="1",
    authority_scope="local_pure",
    side_effect_class="PURE",
)


def verify_hash_text(
    payload: Mapping[str, object],
    output: Mapping[str, object],
) -> bool:
    return dict(output) == dict(hash_text(payload))
