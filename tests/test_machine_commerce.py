from tristan.economic_graph import EconomicGraph
from tristan.economic_ir import ActorAuthorityIR, EconomicActorIR
from tristan.machine_commerce import EconomicEventIR, QuoteIR, compile_need, event_is_executable, quote_is_executable, renewal_candidate


def base_graph(actions=("purchase",), budget=100.0):
    g = EconomicGraph()
    g.actors["agent"] = EconomicActorIR("agent", "software_agent", autonomous=True)
    g.authorities["agent"] = ActorAuthorityIR(
        actor_id="agent",
        authority_source="controller-policy",
        allowed_actions=actions,
        budget_ceiling=budget,
        currency="CAD",
    )
    return g


def test_event_compiles_to_need():
    event = EconomicEventIR("e1", "agent", "MODEL_DRIFT", "ScientificConsistency", max_budget=25)
    need = compile_need(event)
    assert need.need_id == "need:e1"
    assert need.trigger == "MODEL_DRIFT"
    assert need.capability == "ScientificConsistency"


def test_autonomous_actor_without_authority_cannot_purchase():
    g = EconomicGraph()
    g.actors["agent"] = EconomicActorIR("agent", "software_agent", autonomous=True)
    event = EconomicEventIR("e1", "agent", "PR_OPENED", "ScientificCI", max_budget=10)
    assert event_is_executable(g, event) is False


def test_event_is_executable_inside_delegated_budget():
    g = base_graph(budget=50)
    event = EconomicEventIR("e1", "agent", "PR_OPENED", "ScientificCI", max_budget=20)
    assert event_is_executable(g, event) is True


def test_quote_must_fit_need_and_authority():
    g = base_graph(budget=50)
    need = compile_need(EconomicEventIR("e1", "agent", "MODEL_DRIFT", "ScientificConsistency", max_budget=30, evidence_required=("TRACE",), latency_limit_s=60))
    g.needs[need.need_id] = need
    good = QuoteIR("q1", "seller", "agent", "verify", 25, "CAD", latency_s=30, evidence_level=("TRACE",))
    too_expensive = QuoteIR("q2", "seller", "agent", "verify", 40, "CAD", latency_s=30, evidence_level=("TRACE",))
    missing_evidence = QuoteIR("q3", "seller", "agent", "verify", 20, "CAD", latency_s=30)
    assert quote_is_executable(g, need.need_id, good) is True
    assert quote_is_executable(g, need.need_id, too_expensive) is False
    assert quote_is_executable(g, need.need_id, missing_evidence) is False


def test_quote_is_not_contract_or_revenue():
    g = base_graph(budget=50)
    need = compile_need(EconomicEventIR("e1", "agent", "MODEL_DRIFT", "ScientificConsistency", max_budget=30))
    g.needs[need.need_id] = need
    quote = QuoteIR("q1", "seller", "agent", "verify", 25, "CAD")
    assert quote_is_executable(g, need.need_id, quote)
    assert g.contracts == {}
    assert g.settled_revenue("CAD") == 0


def test_renewal_candidate_requires_value_and_renew_authority():
    g = base_graph(actions=("purchase", "renew"), budget=100)
    candidate = renewal_candidate(g, actor_id="agent", offer_id="ci", observed_utility=2.0, utility_threshold=1.0, renewal_price=80, currency="CAD")
    assert candidate is not None
    assert candidate.economically_eligible


def test_renewal_candidate_does_not_self_authorize():
    g = base_graph(actions=("purchase",), budget=100)
    candidate = renewal_candidate(g, actor_id="agent", offer_id="ci", observed_utility=2.0, utility_threshold=1.0, renewal_price=80, currency="CAD")
    assert candidate is None
