from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Iterable

from .loss_ledger import LossEntry, VALID_STATES


LOSS_DIMENSIONS = {
    "SEMANTIC", "NUMERIC", "UNITS", "EQUATION", "CITATION", "LAYOUT", "VISUAL",
    "PROVENANCE", "RELATION", "UNCERTAINTY", "READING_ORDER", "TYPOGRAPHY", "IMAGE"
}


@dataclass(frozen=True)
class LossObservation:
    transform_id: str
    item_id: str
    dimension: str
    state: str
    severity: float = 0.0
    recoverability: float = 1.0
    intentional: bool = False
    cause: str = ""
    detail: str = ""
    evidence_ids: tuple[str, ...] = ()

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.transform_id:
            errors.append("LossObservation.transform_id required")
        if not self.item_id:
            errors.append("LossObservation.item_id required")
        if self.dimension not in LOSS_DIMENSIONS:
            errors.append(f"invalid loss dimension: {self.dimension}")
        if self.state not in VALID_STATES:
            errors.append(f"invalid loss state: {self.state}")
        if not 0.0 <= self.severity <= 1.0:
            errors.append("LossObservation.severity must be within [0,1]")
        if not 0.0 <= self.recoverability <= 1.0:
            errors.append("LossObservation.recoverability must be within [0,1]")
        if self.state == "PRESERVED" and self.severity != 0.0:
            errors.append("PRESERVED observations must have zero severity")
        return errors

    @property
    def residual_weight(self) -> float:
        """Heuristic residual weight, not a probability or truth score."""
        if self.state == "PRESERVED":
            return 0.0
        return self.severity * (1.0 - self.recoverability)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["residual_weight"] = self.residual_weight
        return payload


@dataclass
class LossTensor:
    entries: list[LossObservation] = field(default_factory=list)

    def add(self, observation: LossObservation) -> None:
        errors = observation.validate()
        if errors:
            raise ValueError(errors)
        self.entries.append(observation)

    def validate(self) -> list[str]:
        errors: list[str] = []
        for entry in self.entries:
            errors.extend(entry.validate())
        return errors

    def by_transform(self, transform_id: str) -> list[LossObservation]:
        return [e for e in self.entries if e.transform_id == transform_id]

    def by_dimension(self, dimension: str) -> list[LossObservation]:
        if dimension not in LOSS_DIMENSIONS:
            raise ValueError(f"invalid loss dimension: {dimension}")
        return [e for e in self.entries if e.dimension == dimension]

    def summary(self) -> dict[str, Any]:
        errors = self.validate()
        if errors:
            raise ValueError(errors)
        by_dimension = {
            d: {state: 0 for state in sorted(VALID_STATES)}
            for d in sorted(LOSS_DIMENSIONS)
        }
        total_severity = 0.0
        total_residual_weight = 0.0
        intentional_count = 0
        for entry in self.entries:
            by_dimension[entry.dimension][entry.state] += 1
            total_severity += entry.severity
            total_residual_weight += entry.residual_weight
            intentional_count += int(entry.intentional)
        return {
            "entry_count": len(self.entries),
            "by_dimension": by_dimension,
            "total_severity": total_severity,
            "total_residual_weight": total_residual_weight,
            "intentional_count": intentional_count,
            "entries": [e.to_dict() for e in self.entries],
        }

    @classmethod
    def from_legacy(
        cls,
        entries: Iterable[LossEntry],
        *,
        dimension: str = "SEMANTIC",
        default_severity: float = 1.0,
        default_recoverability: float = 0.0,
    ) -> "LossTensor":
        if dimension not in LOSS_DIMENSIONS:
            raise ValueError(f"invalid loss dimension: {dimension}")
        tensor = cls()
        for entry in entries:
            severity = 0.0 if entry.state == "PRESERVED" else default_severity
            recoverability = 1.0 if entry.state == "PRESERVED" else default_recoverability
            tensor.add(
                LossObservation(
                    transform_id=entry.transform_id,
                    item_id=entry.item,
                    dimension=dimension,
                    state=entry.state,
                    severity=severity,
                    recoverability=recoverability,
                    detail=entry.detail,
                )
            )
        return tensor

    def to_legacy(self) -> list[LossEntry]:
        errors = self.validate()
        if errors:
            raise ValueError(errors)
        return [
            LossEntry(
                transform_id=e.transform_id,
                item=e.item_id,
                state=e.state,
                detail=e.detail,
            )
            for e in self.entries
        ]
