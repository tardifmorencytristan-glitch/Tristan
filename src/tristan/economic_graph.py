from __future__ import annotations

from dataclasses import dataclass, field

from .economic_ir import BuyerIR, ChannelIR, ContractIR, OfferGenome, PaymentRailIR, ProblemIR, SettlementReceipt


@dataclass(frozen=True)
class EconomicLink:
    source_id: str
    relation: str
    target_id: str


@dataclass
class EconomicGraph:
    buyers: dict[str, BuyerIR] = field(default_factory=dict)
    problems: dict[str, ProblemIR] = field(default_factory=dict)
    offers: dict[str, OfferGenome] = field(default_factory=dict)
    channels: dict[str, ChannelIR] = field(default_factory=dict)
    rails: dict[str, PaymentRailIR] = field(default_factory=dict)
    contracts: dict[str, ContractIR] = field(default_factory=dict)
    settlements: dict[str, SettlementReceipt] = field(default_factory=dict)
    links: list[EconomicLink] = field(default_factory=list)

    def link(self, source_id: str, relation: str, target_id: str) -> None:
        self.links.append(EconomicLink(source_id, relation, target_id))

    def settled_revenue(self, currency: str | None = None) -> float:
        rows = self.settlements.values()
        if currency is not None:
            rows = [s for s in rows if s.currency == currency]
        return sum(s.net for s in rows)


def channel_score(channel: ChannelIR, buyer: BuyerIR) -> float:
    if channel.buyer_types and buyer.buyer_type not in channel.buyer_types:
        return 0.0
    numerator = channel.reach * channel.buyer_fit * channel.arpa * channel.conversion_potential * channel.retention
    denominator = channel.friction + channel.cac + channel.integration_cost + channel.platform_fees
    if denominator <= 0:
        denominator = 1.0
    return numerator / denominator


def rank_channels(channels: tuple[ChannelIR, ...], buyer: BuyerIR) -> tuple[tuple[str, float], ...]:
    ranked = [(c.channel_id, channel_score(c, buyer)) for c in channels]
    ranked.sort(key=lambda item: (-item[1], item[0]))
    return tuple((cid, round(score, 6)) for cid, score in ranked)


def external_economic_proof(graph: EconomicGraph) -> tuple[str, ...]:
    proofs: list[str] = []
    if graph.settlements:
        proofs.append("SETTLEMENT")
    if any(c.status == "CONTRACTED" for c in graph.contracts.values()):
        proofs.append("CONTRACT")
    if any(c.status == "PAID" for c in graph.contracts.values()):
        proofs.append("PAID")
    return tuple(proofs)
