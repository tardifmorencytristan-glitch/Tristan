from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class FailureGenome:
    failure_id: str
    family: str
    classification: str
    observed: str
    action: str
    regression_gate: str
    source: str = ""
    boundaries: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> list[str]:
        errors: list[str] = []
        for name, value in (
            ("failure_id", self.failure_id),
            ("family", self.family),
            ("classification", self.classification),
            ("observed", self.observed),
            ("action", self.action),
            ("regression_gate", self.regression_gate),
        ):
            if not value.strip():
                errors.append(f"{name} required")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_failure_record(data: dict[str, Any], *, source: str = "") -> FailureGenome:
    failure_id = str(data.get("id") or data.get("failure_id") or data.get("family") or "").strip()
    family = str(data.get("family") or data.get("classification") or "UNCLASSIFIED").strip()
    classification = str(data.get("classification") or family).strip()

    observed_raw = data.get("observed")
    if isinstance(observed_raw, dict):
        observed = "; ".join(f"{k}={observed_raw[k]!r}" for k in sorted(observed_raw))
    else:
        observed = str(observed_raw or data.get("residual") or data.get("symptom") or "").strip()

    action = str(
        data.get("action")
        or data.get("need")
        or data.get("next_checker")
        or data.get("fix")
        or ""
    ).strip()
    regression_gate = str(
        data.get("regression_gate")
        or data.get("regression_requirement")
        or data.get("next_checker")
        or action
    ).strip()

    boundaries_raw = data.get("boundaries") or data.get("boundary") or ()
    if isinstance(boundaries_raw, str):
        boundaries = (boundaries_raw,)
    else:
        boundaries = tuple(str(x) for x in boundaries_raw)

    known = {
        "id", "failure_id", "family", "classification", "observed", "residual", "symptom",
        "action", "need", "next_checker", "fix", "regression_gate", "regression_requirement",
        "boundaries", "boundary",
    }
    metadata = {k: v for k, v in data.items() if k not in known}
    return FailureGenome(
        failure_id=failure_id,
        family=family,
        classification=classification,
        observed=observed,
        action=action,
        regression_gate=regression_gate,
        source=source,
        boundaries=boundaries,
        metadata=metadata,
    )
