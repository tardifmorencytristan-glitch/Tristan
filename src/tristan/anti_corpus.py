from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AlternativeCandidate:
    candidate_id: str
    claim_id: str
    description: str
    evidence_count: int = 0
    contradiction_count: int = 0
    predictive_hits: int = 0
    complexity: float = 0.0
    cost: float = 0.0

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.candidate_id.strip():
            errors.append("candidate_id required")
        if not self.claim_id.strip():
            errors.append("claim_id required")
        if not self.description.strip():
            errors.append("description required")
        for name, value in (
            ("evidence_count", self.evidence_count),
            ("contradiction_count", self.contradiction_count),
            ("predictive_hits", self.predictive_hits),
        ):
            if value < 0:
                errors.append(f"{name} must be non-negative")
        for name, value in (("complexity", self.complexity), ("cost", self.cost)):
            if value < 0:
                errors.append(f"{name} must be non-negative")
        return errors


def dominates(a: AlternativeCandidate, b: AlternativeCandidate) -> bool:
    at_least_as_good = (
        a.evidence_count >= b.evidence_count
        and a.predictive_hits >= b.predictive_hits
        and a.contradiction_count <= b.contradiction_count
        and a.complexity <= b.complexity
        and a.cost <= b.cost
    )
    strictly_better = (
        a.evidence_count > b.evidence_count
        or a.predictive_hits > b.predictive_hits
        or a.contradiction_count < b.contradiction_count
        or a.complexity < b.complexity
        or a.cost < b.cost
    )
    return at_least_as_good and strictly_better


def pareto_frontier(candidates: list[AlternativeCandidate]) -> list[AlternativeCandidate]:
    valid = [c for c in candidates if not c.validate()]
    frontier = [
        c for c in valid
        if not any(d.candidate_id != c.candidate_id and dominates(d, c) for d in valid)
    ]
    return sorted(frontier, key=lambda c: c.candidate_id)


def anti_corpus_decision(candidates: list[AlternativeCandidate]) -> dict:
    frontier = pareto_frontier(candidates)
    return {
        "status": "BOUNDED_PARETO_FRONTIER" if frontier else "HOLD_NO_VALID_ALTERNATIVES",
        "frontier_ids": [c.candidate_id for c in frontier],
        "winner_declared": False,
        "boundary": "Pareto survival is not truth, scientific proof, or universal superiority.",
    }
