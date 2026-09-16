from tristan.economic_graph import EconomicGraph, channel_score, external_economic_proof, need_is_executable, rank_channels
from tristan.economic_ir import (
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


def test_problem_economic_pain_is_cost_sum():
    p = ProblemIR("p", "validation drift", failure_cost=100, labor_cost=50, delay_cost=25, regulatory_pressure=10)
    assert p.economic_pain == 185


def test_channel_tournament_is_buyer_specific():
    buyer = BuyerIR("b", "government")
    procurement = ChannelIR("procurement", ("government",), 0.8, 0.9, 20000, 0.2, 0.8, 5, 500, 1000)
    selfserve = ChannelIR("selfserve", ("smb",), 1.0, 1.0, 99, 0.5, 0.5, 1, 20, 10)
    ranked = rank_channels((selfserve, procurement), buyer)
    assert ranked[0][0] == "procurement"
    assert channel_score(selfserve, buyer) == 0.0


def test_nonhuman_actor_can_use_agent_native_channel():
    agent = EconomicActorIR("ci-agent", "software_agent", protocols=("api",), autonomous=True)
    agent_api = ChannelIR("agent_api", (), 0.9, 0.9, 100, 0.8, 0.9, 1, 5, 10, actor_types=("software_agent", "service"))
    human_only = ChannelIR("human_sales", ("enterprise",), 0.8, 0.8, 5000, 0.2, 0.8, 5, 500, 1000)
    assert channel_score(agent_api, agent) > 0
    assert channel_score(human_only, agent) == 0


def test_buyer_is_backward_compatible_economic_actor_adapter():
    g = EconomicGraph()
    actor = g.register_buyer(BuyerIR("gov", "government", procurement_methods=("purchase_order",)))
    assert actor.actor_id == "gov"
    assert actor.actor_type == "government"
    assert actor.autonomous is False
    assert "gov" in g.actors and "gov" in g.buyers


def test_capability_does_not_imply_spending_authority():
    g = EconomicGraph()
    g.actors["agent"] = EconomicActorIR("agent", "software_agent", autonomous=True)
    g.needs["n"] = NeedIR("n", "agent", "ScientificConsistency", "PR_OPENED", max_budget=50)
    assert need_is_executable(g, "n") is False


def test_agent_purchase_requires_explicit_bounded_authority():
    g = EconomicGraph()
    g.actors["agent"] = EconomicActorIR("agent", "software_agent", autonomous=True)
    g.needs["n"] = NeedIR("n", "agent", "ScientificConsistency", "PR_OPENED", max_budget=50)
    g.authorities["agent"] = ActorAuthorityIR("agent", "org-policy", ("purchase",), budget_ceiling=100, currency="CAD")
    assert need_is_executable(g, "n") is True
    g.needs["too-expensive"] = NeedIR("too-expensive", "agent", "ScientificConsistency", "PR_OPENED", max_budget=101)
    assert need_is_executable(g, "too-expensive") is False


def test_authority_is_currency_scoped():
    authority = ActorAuthorityIR("agent", "policy", ("purchase",), budget_ceiling=100, currency="CAD")
    assert authority.authorizes("purchase", 50, "CAD")
    assert not authority.authorizes("purchase", 50, "USD")


def test_payment_rail_is_separate_from_offer():
    offer = OfferGenome("audit", ("p",), ("ScientificConsistency",), price_model="VALUE_BASED")
    rail = PaymentRailIR("invoice", ("direct_b2b",), "INVOICE", True)
    assert offer.offer_id == "audit"
    assert rail.rail_id == "invoice"


def test_contract_without_settlement_is_not_revenue():
    g = EconomicGraph()
    g.contracts["c"] = ContractIR("c", "b", "o", "direct", "invoice", "CONTRACTED", 5000)
    assert g.settled_revenue("CAD") == 0
    assert external_economic_proof(g) == ("CONTRACT",)


def test_settlement_records_net_revenue():
    g = EconomicGraph()
    g.settlements["s"] = SettlementReceipt("s", "c", gross=1000, fees=30, tax=100, currency="CAD")
    assert g.settled_revenue("CAD") == 870
    assert external_economic_proof(g) == ("SETTLEMENT",)


def test_machine_usage_is_economic_evidence_but_not_revenue():
    g = EconomicGraph()
    g.usages["u"] = UsageReceipt("u", "agent", "verify-api", "ScientificConsistency", 1, "verification", 0.02)
    assert external_economic_proof(g) == ("USAGE",)
    assert g.settled_revenue("CAD") == 0


def test_contract_can_identify_nonhuman_economic_actor():
    c = ContractIR("c", "", "api", "agent_api", "metered", "CONTRACTED", actor_id="agent-7")
    assert c.economic_actor_id == "agent-7"


def test_graph_keeps_multiple_payment_rails_possible():
    g = EconomicGraph()
    g.rails["stripe"] = PaymentRailIR("stripe", ("selfserve",), "CARD", True)
    g.rails["po"] = PaymentRailIR("po", ("procurement",), "PURCHASE_ORDER", False)
    g.rails["marketplace"] = PaymentRailIR("marketplace", ("cloud_marketplace",), "MARKETPLACE_CONTRACT", True)
    assert set(g.rails) == {"stripe", "po", "marketplace"}
