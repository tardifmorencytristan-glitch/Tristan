from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class CreationIR:
    object_id: str
    claim_ids: tuple[str, ...] = ()
    transformation_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    book0_ref: str | None = None

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.object_id.strip():
            errors.append("object_id required")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ClaimIR:
    claim_id: str
    statement: str
    assumptions: tuple[str, ...] = ()
    predicted_observables: tuple[str, ...] = ()
    witness: str | None = None
    competing_models: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    counter_evidence_ids: tuple[str, ...] = ()
    uncertainty: str = "UNKNOWN"
    status: str = "ACTIVE"

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.claim_id.strip():
            errors.append("claim_id required")
        if not self.statement.strip():
            errors.append("statement required")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EvidenceIR:
    evidence_id: str
    kind: str
    source: str
    method: str
    result: str
    uncertainty: str = "UNKNOWN"
    provenance: tuple[str, ...] = ()

    def validate(self) -> list[str]:
        errors: list[str] = []
        for name, value in (
            ("evidence_id", self.evidence_id),
            ("kind", self.kind),
            ("source", self.source),
            ("method", self.method),
            ("result", self.result),
        ):
            if not value.strip():
                errors.append(f"{name} required")
        if not self.provenance:
            errors.append("provenance required")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TransformationIR:
    transformation_id: str
    operator: str
    source_id: str
    target_kind: str
    preconditions: tuple[str, ...] = ()
    preserved_invariants: tuple[str, ...] = ()
    expected_gain: float = 0.0
    cost: float = 1.0
    risk: float = 0.0
    evidence_debt: float = 0.0
    rollback: str = ""

    def validate(self) -> list[str]:
        errors: list[str] = []
        for name, value in (
            ("transformation_id", self.transformation_id),
            ("operator", self.operator),
            ("source_id", self.source_id),
            ("target_kind", self.target_kind),
            ("rollback", self.rollback),
        ):
            if not value.strip():
                errors.append(f"{name} required")
        for name, value in (
            ("expected_gain", self.expected_gain),
            ("cost", self.cost),
            ("risk", self.risk),
            ("evidence_debt", self.evidence_debt),
        ):
            if value < 0:
                errors.append(f"{name} must be non-negative")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExperimentIR:
    experiment_id: str
    hypothesis_claim_id: str
    alternative_claim_ids: tuple[str, ...] = ()
    controls: tuple[str, ...] = ()
    observables: tuple[str, ...] = ()
    success_criteria: tuple[str, ...] = ()
    failure_criteria: tuple[str, ...] = ()
    stop_rules: tuple[str, ...] = ()

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.experiment_id.strip():
            errors.append("experiment_id required")
        if not self.hypothesis_claim_id.strip():
            errors.append("hypothesis_claim_id required")
        if not self.observables:
            errors.append("at least one observable required")
        if not self.success_criteria:
            errors.append("success criteria required")
        if not self.failure_criteria:
            errors.append("failure criteria required")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
