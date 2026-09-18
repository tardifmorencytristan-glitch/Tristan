from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Mapping


@dataclass(frozen=True)
class WorldState:
    state_id: str
    variables: tuple[tuple[str, float], ...]
    provenance: tuple[str, ...]

    def as_map(self) -> dict[str, float]:
        return dict(self.variables)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.state_id.strip():
            errors.append("state_id required")
        if not self.variables:
            errors.append("variables required")
        if not self.provenance:
            errors.append("provenance required")
        return errors


@dataclass(frozen=True)
class TransitionHypothesis:
    hypothesis_id: str
    deltas: tuple[tuple[str, float], ...]
    assumptions: tuple[str, ...]
    uncertainty: float

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.hypothesis_id.strip():
            errors.append("hypothesis_id required")
        if not self.deltas:
            errors.append("deltas required")
        if not self.assumptions:
            errors.append("assumptions required")
        if not 0.0 <= self.uncertainty <= 1.0:
            errors.append("uncertainty must be in [0,1]")
        return errors


@dataclass(frozen=True)
class PredictionReceipt:
    source_state_id: str
    hypothesis_id: str
    predicted_variables: tuple[tuple[str, float], ...]
    uncertainty: float
    status: str
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class WorldModelResidual:
    predicted_state_id: str
    observed_state_id: str
    residuals: tuple[tuple[str, float], ...]
    mean_absolute_residual: float
    status: str
    scientific_pass: bool
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def predict_transition(
    state: WorldState,
    hypothesis: TransitionHypothesis,
) -> PredictionReceipt:
    errors = state.validate() + hypothesis.validate()
    if errors:
        raise ValueError("; ".join(errors))
    predicted = state.as_map()
    for key, delta in hypothesis.deltas:
        predicted[key] = predicted.get(key, 0.0) + delta
    return PredictionReceipt(
        source_state_id=state.state_id,
        hypothesis_id=hypothesis.hypothesis_id,
        predicted_variables=tuple(sorted(predicted.items())),
        uncertainty=hypothesis.uncertainty,
        status="MODEL_PREDICTION_ONLY",
        boundaries=(
            "ModelPrediction != Observation",
            "StateEstimate != WorldTruth",
            "AssumptionDependent",
        ),
    )


def compare_prediction_to_observation(
    prediction: PredictionReceipt,
    observed: WorldState,
) -> WorldModelResidual:
    errors = observed.validate()
    if errors:
        raise ValueError("; ".join(errors))
    predicted = dict(prediction.predicted_variables)
    actual = observed.as_map()
    common = sorted(set(predicted) & set(actual))
    if not common:
        raise ValueError("prediction and observation share no variables")
    residuals = tuple((key, actual[key] - predicted[key]) for key in common)
    mean_abs = sum(abs(value) for _, value in residuals) / len(residuals)
    return WorldModelResidual(
        predicted_state_id=f"{prediction.source_state_id}:{prediction.hypothesis_id}",
        observed_state_id=observed.state_id,
        residuals=residuals,
        mean_absolute_residual=mean_abs,
        status="RESIDUAL_MEASURED",
        scientific_pass=False,
        boundaries=(
            "ResidualFit != Causality",
            "LowResidual != ScientificTruth",
            "ObservationQualityLimitsInference",
        ),
    )
