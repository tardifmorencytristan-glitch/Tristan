from tristan.bid_draft import compile_bid_draft
from tristan.capability_registry import default_capability_registry
from tristan.compliance import build_compliance_matrix
from tristan.demand_ir import OpportunityIR, RequirementIR
from tristan.demand_research import research_residuals


def test_unknown_requirements_hold():
    opp = OpportunityIR("x", "Buyer", "Vague title", "RFP")
    m = build_compliance_matrix(opp, default_capability_registry())
    assert m.status == "REQUIREMENTS_UNKNOWN"
    assert compile_bid_draft(m).status == "HOLD"
    assert research_residuals(m)[0].priority_hint == "RETRIEVE_SOURCE"


def test_partial_realworld_evidence_blocks_draft():
    opp = OpportunityIR(
        "x", "Buyer", "Model validation", "RFP",
        requirements=(RequirementIR("model_validation", "Must provide model validation", evidence_required=True),),
    )
    m = build_compliance_matrix(opp, default_capability_registry())
    assert m.rows[0].result == "PARTIAL"
    assert m.status == "HOLD"
    assert compile_bid_draft(m).status == "HOLD"
    assert research_residuals(m)[0].priority_hint == "VALIDATE"


def test_missing_capability_becomes_research_residual():
    opp = OpportunityIR(
        "x", "Buyer", "Air-gapped deployment", "RFP",
        requirements=(RequirementIR("air_gapped", "Must support air-gapped deployment"),),
    )
    m = build_compliance_matrix(opp, default_capability_registry())
    assert m.rows[0].result == "GAP"
    assert research_residuals(m)[0].priority_hint == "BUILD_OR_REUSE"


def test_fully_evidenced_capability_can_compile_draft():
    opp = OpportunityIR(
        "x", "Buyer", "Traceability", "RFP",
        requirements=(RequirementIR("traceability", "Must provide traceability"),),
    )
    m = build_compliance_matrix(opp, default_capability_registry())
    assert m.status == "SUPPORTED_FOR_DRAFT"
    d = compile_bid_draft(m)
    assert d.status == "DRAFT_ONLY"
    assert d.evidence_appendix


def test_draft_never_claims_submission():
    opp = OpportunityIR(
        "x", "Buyer", "Traceability", "RFP",
        requirements=(RequirementIR("traceability", "Must provide traceability"),),
    )
    d = compile_bid_draft(build_compliance_matrix(opp, default_capability_registry()))
    assert d.status != "SUBMITTED"
