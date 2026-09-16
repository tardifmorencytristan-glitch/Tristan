from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any

IR_TYPES = {
    "INTENT", "RESEARCH", "SCIENTIFIC", "KNOWLEDGE", "CODE", "GIT", "DATA",
    "EQUATION", "FIGURE", "SPEC", "COMPLIANCE", "DOCUMENT", "ARTIFACT"
}

STATUSES = {"ACTIVE", "PROVISIONAL", "VERIFIED", "SUPERSEDED", "REFUTED", "UNKNOWN", "HOLD"}


@dataclass
class UniversalIRObject:
    id: str
    type: str
    status: str = "PROVISIONAL"
    provenance: list[str] = field(default_factory=list)
    version: str | None = None
    dependencies: list[str] = field(default_factory=list)
    scope: str = ""
    assumptions: list[str] = field(default_factory=list)
    uncertainty: str = ""
    evidence_ids: list[str] = field(default_factory=list)
    payload: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.id:
            errors.append("id required")
        if self.type not in IR_TYPES:
            errors.append(f"unknown type: {self.type}")
        if self.status not in STATUSES:
            errors.append(f"unknown status: {self.status}")
        if not self.provenance:
            errors.append("provenance required")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
