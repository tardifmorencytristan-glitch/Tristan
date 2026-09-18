from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json


def _digest(payload: dict) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class ExecutionLease:
    plan_digest: str
    executor_id: str
    allowed_actions: tuple[str, ...]
    authorized: bool = False
    reversible_only: bool = True

    def validate(self, *, plan_digest: str, requested_actions: tuple[str, ...]) -> list[str]:
        errors: list[str] = []
        if not self.authorized:
            errors.append("execution lease not authorized")
        if self.plan_digest != plan_digest:
            errors.append("execution lease plan digest mismatch")
        missing = sorted(set(requested_actions) - set(self.allowed_actions))
        if missing:
            errors.append("lease does not cover actions: " + ", ".join(missing))
        if not self.executor_id.strip():
            errors.append("executor_id required")
        return errors

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class RealityReceipt:
    plan_digest: str
    observer_id: str
    success_criteria: tuple[str, ...]
    passed_criteria: tuple[str, ...]
    failed_criteria: tuple[str, ...]
    reality_gap: float
    status: str
    scientific_pass: bool = False
    authority_granted: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


def plan_digest(plan: dict) -> str:
    return _digest(plan)


def observe_reality(
    *,
    plan_digest_value: str,
    observer_id: str,
    success_criteria: tuple[str, ...],
    passed_criteria: tuple[str, ...],
) -> RealityReceipt:
    if not observer_id.strip():
        raise ValueError("observer_id required")
    if not success_criteria:
        raise ValueError("success_criteria required")

    declared = set(success_criteria)
    passed = set(passed_criteria)
    if not passed <= declared:
        raise ValueError("passed criteria must be declared success criteria")

    failed = tuple(criterion for criterion in success_criteria if criterion not in passed)
    reality_gap = len(failed) / len(success_criteria)
    return RealityReceipt(
        plan_digest=plan_digest_value,
        observer_id=observer_id,
        success_criteria=success_criteria,
        passed_criteria=tuple(criterion for criterion in success_criteria if criterion in passed),
        failed_criteria=failed,
        reality_gap=reality_gap,
        status="PASS" if reality_gap == 0 else "RESIDUAL",
    )
