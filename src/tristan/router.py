from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ActionCandidate:
    action_id: str
    transformation_id: str
    evidence_gain: float = 0.0
    capability_gain: float = 0.0
    utility_gain: float = 0.0
    debt_reduction: float = 0.0
    cost: float = 0.0
    risk: float = 0.0
    complexity: float = 0.0

    @property
    def verified_value(self) -> float:
        return self.evidence_gain + self.capability_gain + self.utility_gain + self.debt_reduction

    @property
    def burden(self) -> float:
        return self.cost + self.risk + self.complexity

    @property
    def score(self) -> float:
        return self.verified_value / max(self.burden, 1e-9)


def rank_actions(candidates: list[ActionCandidate]) -> list[ActionCandidate]:
    viable = [c for c in candidates if c.verified_value > 0]
    return sorted(viable, key=lambda c: (-c.score, -c.debt_reduction, c.action_id))


def choose_next_action(candidates: list[ActionCandidate]) -> ActionCandidate | None:
    ranked = rank_actions(candidates)
    return ranked[0] if ranked else None
