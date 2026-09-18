from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ExperimentCandidate:
    experiment_id: str
    expected_information_gain: float
    cost: float
    risk: float
    time: float
    reproducibility: float
    falsification_power: float

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.experiment_id.strip():
            errors.append("experiment_id required")
        for name, value in (
            ("expected_information_gain", self.expected_information_gain),
            ("cost", self.cost),
            ("risk", self.risk),
            ("time", self.time),
        ):
            if value < 0:
                errors.append(f"{name} must be non-negative")
        for name, value in (
            ("reproducibility", self.reproducibility),
            ("falsification_power", self.falsification_power),
        ):
            if not 0.0 <= value <= 1.0:
                errors.append(f"{name} must be in [0,1]")
        return errors

    @property
    def utility(self) -> float:
        evidence_value = (
            self.expected_information_gain
            * self.reproducibility
            * self.falsification_power
        )
        burden = self.cost + self.risk + self.time
        return evidence_value / max(burden, 1e-9)


@dataclass(frozen=True)
class ExperimentDesignReceipt:
    ordered_experiments: tuple[str, ...]
    utilities: tuple[tuple[str, float], ...]
    selected_experiment: str | None
    status: str
    authority_granted: bool
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def rank_experiments(
    candidates: tuple[ExperimentCandidate, ...],
    *,
    minimum_utility: float = 0.0,
) -> ExperimentDesignReceipt:
    if minimum_utility < 0:
        raise ValueError("minimum_utility must be non-negative")
    for candidate in candidates:
        errors = candidate.validate()
        if errors:
            raise ValueError("; ".join(errors))

    ranked = sorted(candidates, key=lambda c: (c.utility, c.experiment_id), reverse=True)
    selected = ranked[0] if ranked and ranked[0].utility >= minimum_utility else None
    return ExperimentDesignReceipt(
        ordered_experiments=tuple(c.experiment_id for c in ranked),
        utilities=tuple((c.experiment_id, c.utility) for c in ranked),
        selected_experiment=selected.experiment_id if selected else None,
        status="EXPERIMENT_CANDIDATE_SELECTED" if selected else "NO_ACTION",
        authority_granted=False,
        boundaries=(
            "ExpectedInformationGain != ObservedInformationGain",
            "SelectedExperiment != AuthorizedExperiment",
            "LowUtility -> NO_ACTION",
        ),
    )
