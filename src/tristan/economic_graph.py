from __future__ import annotations

from dataclasses import dataclass, field

from .economic_ir import (
    ActorAuthorityIR,
    BuyerIR,
    ChannelIR,
    ContractIR,
    EconomicActorIR,
    NeedIR,
    OfferGenome,
    PaymentRailIR,
    ProblemIR,
    SettlementReceipt,
    UsageReceipt,
)


@dataclass(frozen=True)
class EconomicLink:
    source_id: str
    relation: str
    target_id: str


@dataclass
class EconomicGraph:
    buyers: dict[str, BuyerIR] = field(default_factory=dict)
    actors: dict[str, EconomicActorIR] = field(default_factory=dict)
    authorities: dict[str, ActorAuthorityIR] = field(default_factory=dict)
    needs: dict[str, NeedIR] = field(default_factory=dict)
    usages: dict[str, UsageReceipt] = field(default_factory=dict)
    problems: dict[str, ProblemIR] = field(default_factory=dict)
    offers: dict[str, OfferGenome] = field(default_factory=dict)
    channels: dict[str, ChannelIR] = field(default_factory=dict)
    rails: dict[str, PaymentRailIR] = field(default_factory=dict)
    contracts: dict[str, ContractIR] = field(default_factory=dict)
    settlements: dict[str, SettlementReceipt] = field(default_factory=dict)
    links: list[EconomicLink] = field(default_factory=list)

    def register_buyer(self, buyer: BuyerIR) -> EconomicActorIR:
        self.buyers[buyer.buyer_id] = buyer
        actor = EconomicActorIR.from_buyer(buyer)
        self.actors[actor.actor_id] = actor
        return actor

    def link(self, source_id: str, relation: str, target_id: str) -> None:
        self.links.append(EconomicLink(source_id, relation, target_id))

    def settled_revenue(self, currency: str | None = None) -> float:
        rows = self.settlements.values()
        if currency is not None:
            rows = [s for s in rows if s.currency == currency]
        return sum(s.net for s in rows)

    def authorize_action(self, actor_id: str, action: str, amount: float = 0.0, currency: str | None = None) -> bool:
        authority = self.authorities.get(actor_id)
        if authority is None:
            return False
        return authority.authorizes(action, amount, currency)


def _actor_type(actor: BuyerIR | EconomicActorIR) -> str:
    return actor.buyer_type if isinstance(actor, BuyerIR) else actor.actor_type


def channel_score(channel: ChannelIR, actor: BuyerIR | EconomicActorIR) -> float:
    actor_type = _actor_type(actor)
    compatible = channel.compatible_actor_types
    if compatible and actor_type not in compatible:
        return 0.0
    numerator = channel.reach * channel.buyer_fit * channel.arpa * channel.conversion_potential * channel.retention
    denominator = channel.friction + channel.cac + channel.integration_cost + channel.platform_fees
    if denominator <= 0:
        denominator = 1.0
    return numerator / denominator


def rank_channels(channels: tuple[ChannelIR, ...], actor: BuyerIR | EconomicActorIR) -> tuple[tuple[str, float], ...]:
    ranked = [(c.channel_id, channel_score(c, actor)) for c in channels]
    ranked.sort(key=lambda item: (-item[1], item[0]))
    return tuple((cid, round(score, 6)) for cid, score in ranked)


def need_is_executable(graph: EconomicGraph, need_id: str, action: str = "purchase") -> bool:
    need = graph.needs.get(need_id)
    if need is None or need.actor_id not in graph.actors:
        return False
    return graph.authorize_action(need.actor_id, action, need.max_budget, need.currency)


def external_economic_proof(graph: EconomicGraph) -> tuple[str, ...]:
    proofs: list[str] = []
    if graph.settlements:
        proofs.append("SETTLEMENT")
    if any(c.status == "CONTRACTED" for c in graph.contracts.values()):
        proofs.append("CONTRACT")
    if any(c.status == "PAID" for c in graph.contracts.values()):
        proofs.append("PAID")
    if graph.usages:
        proofs.append("USAGE")
    return tuple(proofs)
