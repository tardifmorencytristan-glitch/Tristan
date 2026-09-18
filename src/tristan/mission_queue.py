from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Mission:
    mission_id: str
    target_id: str
    transformation: str
    evaluator: str
    expected_verified_gain: float = 0.0
    debt_reduction: float = 0.0
    reuse_potential: float = 0.0
    gaia_impact: float = 0.0
    cost: float = 0.0
    risk: float = 0.0
    dependency_depth: float = 0.0
    dependencies: tuple[str, ...] = ()

    def validate(self) -> list[str]:
        errors: list[str] = []
        for name, value in (
            ("mission_id", self.mission_id),
            ("target_id", self.target_id),
            ("transformation", self.transformation),
            ("evaluator", self.evaluator),
        ):
            if not value.strip():
                errors.append(f"{name} required")
        for name, value in (
            ("expected_verified_gain", self.expected_verified_gain),
            ("debt_reduction", self.debt_reduction),
            ("reuse_potential", self.reuse_potential),
            ("gaia_impact", self.gaia_impact),
            ("cost", self.cost),
            ("risk", self.risk),
            ("dependency_depth", self.dependency_depth),
        ):
            if value < 0:
                errors.append(f"{name} must be non-negative")
        return errors

    @property
    def value(self) -> float:
        return self.expected_verified_gain + self.debt_reduction + self.reuse_potential + self.gaia_impact

    @property
    def burden(self) -> float:
        return self.cost + self.risk + self.dependency_depth

    @property
    def priority(self) -> float:
        return self.value / max(self.burden, 1e-9)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["priority"] = self.priority
        return data


def rank_missions(missions: list[Mission], completed: set[str] | None = None) -> list[Mission]:
    completed = completed or set()
    eligible = [
        m for m in missions
        if not m.validate()
        and m.value > 0
        and all(dep in completed for dep in m.dependencies)
    ]
    return sorted(eligible, key=lambda m: (-m.priority, -m.debt_reduction, m.mission_id))


@dataclass(frozen=True)
class MissionDecision:
    next_mission_id: str
    status: str
    reason: str


def next_mission(missions: list[Mission], completed: set[str] | None = None) -> MissionDecision:
    ranked = rank_missions(missions, completed)
    if not ranked:
        return MissionDecision("NO_ACTION", "NO_ACTION", "No valid dependency-satisfied positive-value mission.")
    return MissionDecision(ranked[0].mission_id, "SELECTED", "Highest bounded value-per-burden among eligible missions.")
