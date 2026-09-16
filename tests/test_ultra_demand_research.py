from tristan.capability_hypergraph import CapabilityComposition, CapabilityHypergraph
from tristan.capability_registry import default_capability_registry
from tristan.demand_optimizer import ResidualCandidate, next_action, rank_residuals
from tristan.demand_research import ResearchResidual
from tristan.requirements_r2 import extract_requirements_r2


def test_requirement_r2_extracts_deadline_and_acceptance():
    rows = extract_requirements_r2("The supplier must provide validation evidence no later than September 30, 2026.")
    assert len(rows) == 1
    assert rows[0].requirement.mandatory
    assert rows[0].requirement.evidence_required
    assert rows[0].deadline == "September 30, 2026"
    assert rows[0].acceptance_test is not None


def test_requirement_r2_silence_on_title_only():
    assert extract_requirements_r2("Model Validation Automation Technologies") == []


def test_capability_hypergraph_composition():
    g = CapabilityHypergraph.from_registry(default_capability_registry())
    g.add_composition(CapabilityComposition(
        "ModelValidationStack",
        ("ScientificConsistency", "SemanticIR", "ScientificWritingCompiler"),
        ("model_validation_stack",),
        cost_hint=2.0,
    ))
    alts = g.alternatives_for("model_validation_stack")
    assert alts and alts[0].name == "ModelValidationStack"


def test_optimizer_prefers_high_leverage_low_cost():
    a = ResidualCandidate(ResearchResidual("a", "A", "VALIDATE"), 1, 1, 1, 1, 1, 1, 1)
    b = ResidualCandidate(ResearchResidual("b", "B", "BUILD_OR_REUSE"), 2, 2, 2, 2, 1, 1, 1)
    ranked = rank_residuals([a, b])
    assert ranked[0] == b
    assert next_action(ranked[0]) == "BUILD_OR_REUSE"


def test_optimizer_no_action_on_empty():
    assert next_action(None) == "NO_ACTION"
