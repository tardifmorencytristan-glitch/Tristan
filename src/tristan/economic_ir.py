from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BuyerIR:
    buyer_id: str
    buyer_type: str
    sector: str = ""
    jurisdiction: str = ""
    procurement_methods: tuple[str, ...] = ()


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
