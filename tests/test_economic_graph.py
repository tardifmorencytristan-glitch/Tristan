from tristan.economic_graph import EconomicGraph, channel_score, external_economic_proof, rank_channels
from tristan.economic_ir import BuyerIR, ChannelIR, ContractIR, OfferGenome, PaymentRailIR, ProblemIR, SettlementReceipt


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


def test_graph_keeps_multiple_payment_rails_possible():
    g = EconomicGraph()
    g.rails["stripe"] = PaymentRailIR("stripe", ("selfserve",), "CARD", True)
    g.rails["po"] = PaymentRailIR("po", ("procurement",), "PURCHASE_ORDER", False)
    g.rails["marketplace"] = PaymentRailIR("marketplace", ("cloud_marketplace",), "MARKETPLACE_CONTRACT", True)
    assert set(g.rails) == {"stripe", "po", "marketplace"}
