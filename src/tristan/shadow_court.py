from __future__ import annotations

from dataclasses import asdict, dataclass


REQUIRED_ROLES = ("CURRENT", "SHADOW", "COUNTER", "EXTERNAL", "NO_ACTION")


@dataclass(frozen=True)
class StrategyCandidate:
    candidate_id: str
    role: str
    planner_id: str
    plan_digest: str
    origin: str = "unknown"

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.candidate_id.strip():
            errors.append("candidate_id required")
        if self.role not in REQUIRED_ROLES:
            errors.append(f"unsupported role: {self.role}")
        if not self.planner_id.strip():
            errors.append("planner_id required")
        if not self.plan_digest.strip():
            errors.append("plan_digest required")
        return errors


@dataclass(frozen=True)
class StrategyEvaluation:
    candidate_id: str
    mission_id: str
    metric: str
    score: float
    valid: bool = True
    uncertainty: float = 0.0

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.candidate_id.strip():
            errors.append("candidate_id required")
        if not self.mission_id.strip():
            errors.append("mission_id required")
        if not self.metric.strip():
            errors.append("metric required")
        if not 0.0 <= self.uncertainty <= 1.0:
            errors.append("uncertainty must be in [0,1]")
        return errors


@dataclass(frozen=True)
class ShadowCourtReceipt:
    metric: str
    direction: str
    role_coverage: tuple[str, ...]
    ordered_candidates: tuple[str, ...]
    aggregate_scores: tuple[dict, ...]
    status: str
    promotion_authority: bool
    scientific_pass: bool
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def run_shadow_court(
    candidates: tuple[StrategyCandidate, ...],
    evaluations: tuple[StrategyEvaluation, ...],
    *,
    metric: str,
    direction: str = "higher",
) -> ShadowCourtReceipt:
    if direction not in {"higher", "lower"}:
        raise ValueError("direction must be higher or lower")
    if not candidates:
        raise ValueError("candidates required")

    for candidate in candidates:
        errors = candidate.validate()
        if errors:
            raise ValueError("; ".join(errors))
    for evaluation in evaluations:
        errors = evaluation.validate()
        if errors:
            raise ValueError("; ".join(errors))

    roles = {candidate.role for candidate in candidates}
    missing_roles = set(REQUIRED_ROLES) - roles
    if missing_roles:
        return ShadowCourtReceipt(
            metric=metric,
            direction=direction,
            role_coverage=tuple(sorted(roles)),
            ordered_candidates=(),
            aggregate_scores=(),
            status="HOLD_MISSING_ROLE_COVERAGE",
            promotion_authority=False,
            scientific_pass=False,
            boundaries=(
                "CourtCoverage != Evidence",
                "OriginBonus = 0",
                "Winner != PromotionAuthority",
                "NO_ACTION is mandatory",
            ),
        )

    candidate_ids = {candidate.candidate_id for candidate in candidates}
    relevant = [
        evaluation
        for evaluation in evaluations
        if evaluation.metric == metric
        and evaluation.candidate_id in candidate_ids
        and evaluation.valid
    ]

    by_candidate: dict[str, list[StrategyEvaluation]] = {cid: [] for cid in candidate_ids}
    for evaluation in relevant:
        by_candidate[evaluation.candidate_id].append(evaluation)

    if any(not rows for rows in by_candidate.values()):
        return ShadowCourtReceipt(
            metric=metric,
            direction=direction,
            role_coverage=tuple(sorted(roles)),
            ordered_candidates=(),
            aggregate_scores=(),
            status="HOLD_INCOMPLETE_EVALUATION",
            promotion_authority=False,
            scientific_pass=False,
            boundaries=(
                "IncompleteEvaluation -> HOLD",
                "OriginBonus = 0",
                "Winner != PromotionAuthority",
            ),
        )

    aggregates = []
    for candidate_id, rows in by_candidate.items():
        mean_score = sum(row.score for row in rows) / len(rows)
        mean_uncertainty = sum(row.uncertainty for row in rows) / len(rows)
        effective_score = (
            mean_score - mean_uncertainty
            if direction == "higher"
            else mean_score + mean_uncertainty
        )
        aggregates.append(
            {
                "candidate_id": candidate_id,
                "mean_score": mean_score,
                "mean_uncertainty": mean_uncertainty,
                "effective_score": effective_score,
                "mission_count": len(rows),
            }
        )

    reverse = direction == "higher"
    ordered = tuple(
        row["candidate_id"]
        for row in sorted(
            aggregates,
            key=lambda row: (row["effective_score"], row["candidate_id"]),
            reverse=reverse,
        )
    )

    return ShadowCourtReceipt(
        metric=metric,
        direction=direction,
        role_coverage=tuple(sorted(roles)),
        ordered_candidates=ordered,
        aggregate_scores=tuple(aggregates),
        status="CONTEXTUAL_COMPARISON_ONLY",
        promotion_authority=False,
        scientific_pass=False,
        boundaries=(
            "ContextualWinner != UniversalWinner",
            "Winner != PromotionAuthority",
            "OriginBonus = 0",
            "CounterJarvis != FalsificationProof",
            "NO_ACTION is mandatory",
        ),
    )
