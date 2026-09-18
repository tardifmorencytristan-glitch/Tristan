from __future__ import annotations

from dataclasses import asdict, dataclass
from math import sqrt


@dataclass(frozen=True)
class StrategyOutcome:
    strategy_id: str
    context: tuple[str, ...]
    score: float
    success: bool
    uncertainty: float = 0.0

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.strategy_id.strip():
            errors.append("strategy_id required")
        if not self.context:
            errors.append("context required")
        if not 0.0 <= self.uncertainty <= 1.0:
            errors.append("uncertainty must be in [0,1]")
        return errors


@dataclass(frozen=True)
class StrategyProfile:
    strategy_id: str
    sample_count: int
    mean_score: float
    success_rate: float
    standard_error: float
    mean_uncertainty: float
    conservative_utility: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class MetaLearningReceipt:
    context: tuple[str, ...]
    profiles: tuple[dict, ...]
    recommended_strategy: str | None
    status: str
    authority_granted: bool
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def _profile(strategy_id: str, rows: list[StrategyOutcome]) -> StrategyProfile:
    n = len(rows)
    mean = sum(row.score for row in rows) / n
    success_rate = sum(1 for row in rows if row.success) / n
    variance = sum((row.score - mean) ** 2 for row in rows) / n
    standard_error = sqrt(variance / n) if n else 0.0
    mean_uncertainty = sum(row.uncertainty for row in rows) / n
    conservative = mean - standard_error - mean_uncertainty
    return StrategyProfile(
        strategy_id=strategy_id,
        sample_count=n,
        mean_score=mean,
        success_rate=success_rate,
        standard_error=standard_error,
        mean_uncertainty=mean_uncertainty,
        conservative_utility=conservative,
    )


def learn_strategy_preferences(
    outcomes: tuple[StrategyOutcome, ...],
    *,
    target_context: tuple[str, ...],
    min_samples: int = 2,
) -> MetaLearningReceipt:
    if not target_context:
        raise ValueError("target_context required")
    if min_samples < 1:
        raise ValueError("min_samples must be >= 1")
    for outcome in outcomes:
        errors = outcome.validate()
        if errors:
            raise ValueError("; ".join(errors))

    target = set(target_context)
    relevant = [row for row in outcomes if target <= set(row.context)]
    grouped: dict[str, list[StrategyOutcome]] = {}
    for row in relevant:
        grouped.setdefault(row.strategy_id, []).append(row)

    profiles = tuple(
        _profile(strategy_id, rows)
        for strategy_id, rows in sorted(grouped.items())
        if len(rows) >= min_samples
    )

    if not profiles:
        return MetaLearningReceipt(
            context=target_context,
            profiles=(),
            recommended_strategy=None,
            status="HOLD_INSUFFICIENT_CONTEXTUAL_EVIDENCE",
            authority_granted=False,
            boundaries=(
                "PastPerformance != FutureGuarantee",
                "MetaPreference != Authority",
                "ContextMatchRequired",
                "NO_ACTION is admissible",
            ),
        )

    best = max(profiles, key=lambda p: (p.conservative_utility, p.success_rate, p.strategy_id))
    return MetaLearningReceipt(
        context=target_context,
        profiles=tuple(profile.to_dict() for profile in profiles),
        recommended_strategy=best.strategy_id,
        status="CONTEXTUAL_PREFERENCE_ONLY",
        authority_granted=False,
        boundaries=(
            "PastPerformance != FutureGuarantee",
            "Recommended != Authorized",
            "ContextualPreference != UniversalWinner",
            "NO_ACTION is admissible",
        ),
    )
