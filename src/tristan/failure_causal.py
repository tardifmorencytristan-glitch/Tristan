from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CauseHypothesis:
    cause_id: str
    failure_id: str
    description: str
    prior_weight: float = 1.0

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.cause_id.strip():
            errors.append("cause_id required")
        if not self.failure_id.strip():
            errors.append("failure_id required")
        if not self.description.strip():
            errors.append("description required")
        if self.prior_weight < 0:
            errors.append("prior_weight must be non-negative")
        return errors


@dataclass(frozen=True)
class DiscriminatingTest:
    test_id: str
    cost: float
    risk: float
    predictions: dict[str, str]

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.test_id.strip():
            errors.append("test_id required")
        if self.cost < 0 or self.risk < 0:
            errors.append("cost and risk must be non-negative")
        if not self.predictions:
            errors.append("predictions required")
        return errors


def separation_score(test: DiscriminatingTest, cause_ids: set[str]) -> float:
    labels = [test.predictions.get(cid, "UNKNOWN") for cid in sorted(cause_ids)]
    distinct = len(set(labels))
    unknown = sum(1 for label in labels if label == "UNKNOWN")
    raw = max(0, distinct - 1) - (unknown * 0.25)
    return raw / max(test.cost + test.risk, 1e-9)


def choose_discriminating_test(
    causes: list[CauseHypothesis],
    tests: list[DiscriminatingTest],
) -> DiscriminatingTest | None:
    valid_causes = {c.cause_id for c in causes if not c.validate()}
    valid_tests = [t for t in tests if not t.validate()]
    if len(valid_causes) < 2 or not valid_tests:
        return None
    ranked = sorted(valid_tests, key=lambda t: (-separation_score(t, valid_causes), t.test_id))
    return ranked[0] if separation_score(ranked[0], valid_causes) > 0 else None
