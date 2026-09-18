from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class AblationResult:
    component_id: str
    metric: str
    baseline_score: float
    ablated_score: float
    higher_is_better: bool = True

    @property
    def contribution(self) -> float:
        raw = self.baseline_score - self.ablated_score
        return raw if self.higher_is_better else -raw


@dataclass(frozen=True)
class CausalCreditReceipt:
    metric: str
    contributions: tuple[dict, ...]
    ranked_components: tuple[str, ...]
    status: str
    scientific_pass: bool
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def assign_ablation_credit(results: tuple[AblationResult, ...]) -> CausalCreditReceipt:
    if not results:
        raise ValueError("ablation results required")
    metrics = {result.metric for result in results}
    if len(metrics) != 1:
        raise ValueError("all ablations must use the same metric")
    component_ids = [result.component_id for result in results]
    if len(component_ids) != len(set(component_ids)):
        raise ValueError("duplicate component_id")

    ordered = sorted(results, key=lambda result: result.contribution, reverse=True)
    return CausalCreditReceipt(
        metric=results[0].metric,
        contributions=tuple(
            {
                "component_id": result.component_id,
                "baseline_score": result.baseline_score,
                "ablated_score": result.ablated_score,
                "contribution": result.contribution,
            }
            for result in results
        ),
        ranked_components=tuple(result.component_id for result in ordered),
        status="ABLATION_CREDIT_ONLY",
        scientific_pass=False,
        boundaries=(
            "AblationContribution != CausalProof",
            "LocalCredit != GlobalTransfer",
            "CorrelationBetweenComponents != IndependentEffect",
            "CreditReceipt != PromotionAuthority",
        ),
    )
