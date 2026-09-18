from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ModelCandidate:
    model_id: str
    description: str
    is_null: bool = False

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.model_id.strip():
            errors.append("model_id required")
        if not self.description.strip():
            errors.append("description required")
        return errors


@dataclass(frozen=True)
class ModelScore:
    model_id: str
    metric: str
    value: float
    uncertainty: float | None = None


@dataclass(frozen=True)
class TournamentReceipt:
    metric: str
    direction: str
    ordered_models: tuple[str, ...]
    scores: tuple[dict, ...]
    status: str
    scientific_pass: bool
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def compare_models(
    candidates: tuple[ModelCandidate, ...],
    scores: tuple[ModelScore, ...],
    *,
    metric: str,
    direction: str = "lower",
) -> TournamentReceipt:
    if direction not in {"lower", "higher"}:
        raise ValueError("direction must be lower or higher")
    if not candidates:
        raise ValueError("at least one candidate required")
    errors = [error for candidate in candidates for error in candidate.validate()]
    if errors:
        raise ValueError("; ".join(errors))

    candidate_ids = {candidate.model_id for candidate in candidates}
    relevant = [score for score in scores if score.metric == metric]
    if {score.model_id for score in relevant} != candidate_ids:
        raise ValueError("exactly one score per candidate required for selected metric")

    reverse = direction == "higher"
    ordered = tuple(
        score.model_id
        for score in sorted(relevant, key=lambda score: score.value, reverse=reverse)
    )
    return TournamentReceipt(
        metric=metric,
        direction=direction,
        ordered_models=ordered,
        scores=tuple(asdict(score) for score in relevant),
        status="COMPARISON_ONLY",
        scientific_pass=False,
        boundaries=(
            "MetricOrdering != ScientificTruth",
            "BestFit != Causality",
            "SingleDatasetPerformance != GeneralTheoryValidation",
            "TournamentReceipt != OAKPromotion",
        ),
    )
