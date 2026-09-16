from __future__ import annotations

from dataclasses import dataclass

from .demand_research import ResearchResidual


@dataclass(frozen=True)
class ResidualCandidate:
    residual: ResearchResidual
    demand_strength: float
    economic_value: float
    evidence_gain: float
    reuse_potential: float
    cost: float
    risk: float
    time: float

    @property
    def priority(self) -> float:
        numerator = self.demand_strength * self.economic_value * self.evidence_gain * self.reuse_potential
        denominator = max(self.cost + self.risk + self.time, 1e-9)
        return numerator / denominator


def rank_residuals(candidates: list[ResidualCandidate]) -> list[ResidualCandidate]:
    return sorted(candidates, key=lambda x: x.priority, reverse=True)


def next_action(candidate: ResidualCandidate | None) -> str:
    if candidate is None:
        return "NO_ACTION"
    hint = candidate.residual.priority_hint
    if hint in {"RETRIEVE_SOURCE", "VALIDATE", "BUILD_OR_REUSE", "INVESTIGATE"}:
        return hint
    return "NO_ACTION"
