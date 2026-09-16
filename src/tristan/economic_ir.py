from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BuyerIR:
    """Backward-compatible human/organization buyer adapter."""
    buyer_id: str
    buyer_type: str
    sector: str = ""
    jurisdiction: str = ""
    procurement_methods: tuple[str, ...] = ()


@dataclass(frozen=True)
class EconomicActorIR:
    actor_id: str
    actor_type: str
    sector: str = ""
    jurisdiction: str = ""
    protocols: tuple[str, ...] = ()
    controller_id: str | None = None
    autonomous: bool = False

    @classmethod
    def from_buyer(cls, buyer: BuyerIR) -> "EconomicActorIR":
        return cls(
            actor_id=buyer.buyer_id,
            actor_type=buyer.buyer_type,
            sector=buyer.sector,
            jurisdiction=buyer.jurisdiction,
            protocols=buyer.procurement_methods,
            controller_id=buyer.buyer_id,
            autonomous=False,
        )


@dataclass(frozen=True)
class ActorAuthorityIR:
    actor_id: str
    authority_source: str
    allowed_actions: tuple[str, ...] = ()
    budget_ceiling: float = 0.0
    currency: str = "CAD"
    expires_at: str | None = None
    revocable: bool = True

    def authorizes(self, action: str, amount: float = 0.0, currency: str | None = None) -> bool:
        if action not in self.allowed_actions:
            return False
        if currency is not None and currency != self.currency:
            return False
        return 0.0 <= amount <= self.budget_ceiling


@dataclass(frozen=True)
class NeedIR:
    need_id: str
    actor_id: str
    capability: str
    trigger: str
    max_budget: float = 0.0
    currency: str = "CAD"
    latency_limit_s: float | None = None
    evidence_required: tuple[str, ...] = ()
    recurring: bool = False


@dataclass(frozen=True)
class UsageReceipt:
    usage_id: str
    actor_id: str
    offer_id: str
    capability: str
    units: float
    unit_name: str
    measured_cost: float = 0.0
    currency: str = "CAD"


@dataclass(frozen=True)
class ProblemIR:
    problem_id: str
    description: str
    frequency: float = 0.0
    failure_cost: float = 0.0
    labor_cost: float = 0.0
    delay_cost: float = 0.0
    regulatory_pressure: float = 0.0

    @property
    def economic_pain(self) -> float:
        return max(0.0, self.failure_cost + self.labor_cost + self.delay_cost + self.regulatory_pressure)


@dataclass(frozen=True)
class OfferGenome:
    offer_id: str
    problem_ids: tuple[str, ...]
    capability_names: tuple[str, ...]
    evidence_ids: tuple[str, ...] = ()
    deliverable: str = ""
    price_model: str = "UNKNOWN"
    automation_level: str = "MANUAL"
    expansion_paths: tuple[str, ...] = ()


@dataclass(frozen=True)
class ChannelIR:
    channel_id: str
    buyer_types: tuple[str, ...]
    reach: float
    buyer_fit: float
    arpa: float
    conversion_potential: float
    retention: float
    friction: float
    cac: float
    integration_cost: float
    platform_fees: float = 0.0
    actor_types: tuple[str, ...] = ()

    @property
    def compatible_actor_types(self) -> tuple[str, ...]:
        return self.actor_types or self.buyer_types


@dataclass(frozen=True)
class PaymentRailIR:
    rail_id: str
    channel_ids: tuple[str, ...]
    settlement_type: str
    recurring_supported: bool = False


@dataclass(frozen=True)
class ContractIR:
    contract_id: str
    buyer_id: str
    offer_id: str
    channel_id: str
    payment_rail_id: str
    status: str
    gross_value: float = 0.0
    currency: str = "CAD"
    actor_id: str | None = None

    @property
    def economic_actor_id(self) -> str:
        return self.actor_id or self.buyer_id


@dataclass(frozen=True)
class SettlementReceipt:
    settlement_id: str
    contract_id: str
    gross: float
    fees: float
    tax: float
    currency: str

    @property
    def net(self) -> float:
        return self.gross - self.fees - self.tax
