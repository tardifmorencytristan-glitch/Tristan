from __future__ import annotations

from dataclasses import dataclass
from .economic_graph import EconomicGraph, need_is_executable
from .economic_ir import NeedIR


@dataclass(frozen=True)
class EconomicEventIR:
    event_id: str
    actor_id: str
    event_type: str
    capability: str
    max_budget: float = 0.0
    currency: str = "CAD"
    latency_limit_s: float | None = None
    evidence_required: tuple[str, ...] = ()
    recurring: bool = False


@dataclass(frozen=True)
class QuoteIR:
    quote_id: str
    seller_actor_id: str
    buyer_actor_id: str
    offer_id: str
    price: float
    currency: str
    latency_s: float | None = None
    evidence_level: tuple[str, ...] = ()
    scope: str = ""
    expires_at: str | None = None


@dataclass(frozen=True)
class RenewalCandidate:
    actor_id: str
    offer_id: str
    observed_utility: float
    utility_threshold: float
    price: float
    currency: str
    reason: str = "usage_value_above_threshold"

    @property
    def economically_eligible(self) -> bool:
        return self.observed_utility >= self.utility_threshold


def compile_need(event: EconomicEventIR) -> NeedIR:
    return NeedIR(
        need_id=f"need:{event.event_id}",
        actor_id=event.actor_id,
        capability=event.capability,
        trigger=event.event_type,
        max_budget=max(0.0, event.max_budget),
        currency=event.currency,
        latency_limit_s=event.latency_limit_s,
        evidence_required=event.evidence_required,
        recurring=event.recurring,
    )


def quote_satisfies_need(quote: QuoteIR, need: NeedIR) -> bool:
    if quote.buyer_actor_id != need.actor_id:
        return False
    if quote.price < 0 or quote.price > need.max_budget:
        return False
    if quote.currency != need.currency:
        return False
    if need.latency_limit_s is not None:
        if quote.latency_s is None or quote.latency_s > need.latency_limit_s:
            return False
    return set(need.evidence_required).issubset(set(quote.evidence_level))


def quote_is_executable(graph: EconomicGraph, need_id: str, quote: QuoteIR) -> bool:
    need = graph.needs.get(need_id)
    if need is None or not quote_satisfies_need(quote, need):
        return False
    # Quote != contract; this only checks bounded delegated authority.
    return graph.authorize_action(need.actor_id, "purchase", quote.price, quote.currency)


def renewal_candidate(
    graph: EconomicGraph,
    *,
    actor_id: str,
    offer_id: str,
    observed_utility: float,
    utility_threshold: float,
    renewal_price: float,
    currency: str,
) -> RenewalCandidate | None:
    candidate = RenewalCandidate(
        actor_id=actor_id,
        offer_id=offer_id,
        observed_utility=observed_utility,
        utility_threshold=utility_threshold,
        price=renewal_price,
        currency=currency,
    )
    if not candidate.economically_eligible:
        return None
    # Candidate generation is not renewal authority.
    if not graph.authorize_action(actor_id, "renew", renewal_price, currency):
        return None
    return candidate


def event_is_executable(graph: EconomicGraph, event: EconomicEventIR) -> bool:
    need = compile_need(event)
    graph.needs[need.need_id] = need
    return need_is_executable(graph, need.need_id)
