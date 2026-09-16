from tristan.demand_ir import (
    CapabilityIR, OpportunityIR, RequirementIR,
    assess_opportunity, no_action_reason, smallest_capability_cover,
)


def test_actionable_with_evidence():
    opp = OpportunityIR(
        source_url="https://example.test/rfp",
        issuer="Buyer",
        title="Model validation automation",
        opportunity_type="RFP",
        eligibility=("canadian_supplier",),
        requirements=(
            RequirementIR("model_validation", "Automate validation", evidence_required=True),
            RequirementIR("traceability", "Provide traceability", evidence_required=True),
        ),
    )
    caps = [
        CapabilityIR("ScientificConsistency", ("model_validation",), ("bench:r0_5",), "AUTOMATED"),
        CapabilityIR("EvidenceGraph", ("traceability",), ("receipt:r4",), "AUTOMATED"),
    ]
    a = assess_opportunity(opp, caps, {"canadian_supplier"})
    assert a.actionable
    assert a.mandatory_coverage == 1.0
    assert no_action_reason(a) is None


def test_capability_gap_blocks_action():
    opp = OpportunityIR(
        source_url="x", issuer="B", title="T", opportunity_type="RFP",
        requirements=(RequirementIR("air_gapped", "Air-gapped deployment"),),
    )
    a = assess_opportunity(opp, [])
    assert a.gaps == ["air_gapped"]
    assert no_action_reason(a) == "CAPABILITY_GAP"


def test_evidence_gap_blocks_action():
    opp = OpportunityIR(
        source_url="x", issuer="B", title="T", opportunity_type="RFP",
        requirements=(RequirementIR("verification", "Verification", evidence_required=True),),
    )
    a = assess_opportunity(opp, [CapabilityIR("Verifier", ("verification",))])
    assert a.evidence_gaps == ["verification"]
    assert no_action_reason(a) == "EVIDENCE_GAP"


def test_eligibility_blocker():
    opp = OpportunityIR(
        source_url="x", issuer="B", title="T", opportunity_type="GRANT",
        eligibility=("us_small_business",),
    )
    a = assess_opportunity(opp, [], {"canadian_supplier"})
    assert no_action_reason(a) == "ELIGIBILITY_BLOCKED"


def test_smallest_cover():
    opp = OpportunityIR(
        source_url="x", issuer="B", title="T", opportunity_type="RFP",
        requirements=(RequirementIR("a", "A"), RequirementIR("b", "B"), RequirementIR("c", "C")),
    )
    caps = [
        CapabilityIR("AB", ("a", "b")),
        CapabilityIR("C", ("c",)),
        CapabilityIR("A", ("a",)),
    ]
    assert smallest_capability_cover(opp, caps) == ["AB", "C"]
