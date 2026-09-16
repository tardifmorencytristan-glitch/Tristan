from tristan.capability_registry import default_capability_registry
from tristan.evidence_graph import EvidenceGraph, EvidenceNode
from tristan.requirements import extract_requirements


def test_requirement_extractor_explicit_mandatory():
    rows = extract_requirements("The supplier must provide model validation evidence. Optional training may be included.")
    assert len(rows) == 2
    assert rows[0].requirement.mandatory
    assert rows[0].requirement.evidence_required
    assert rows[0].category == "ELIGIBILITY" or rows[0].category == "TECHNICAL"
    assert not rows[1].requirement.mandatory


def test_requirement_extractor_does_not_infer_from_title_only():
    assert extract_requirements("Model Validation Automation Technologies") == []


def test_evidence_graph_support_and_contested():
    g = EvidenceGraph()
    g.add_node(EvidenceNode("r", "RECEIPT", "VERIFIED"))
    g.add_node(EvidenceNode("c", "CAPABILITY", "CLAIMED"))
    g.link("r", "SUPPORTS", "c")
    assert g.support_status("c") == "SUPPORTED"
    g.add_node(EvidenceNode("f", "FAILURE", "OBSERVED"))
    g.link("f", "CONTRADICTS", "c")
    assert g.support_status("c") == "CONTESTED"


def test_capability_registry_preserves_realworld_limitations():
    records = {r.capability.name: r for r in default_capability_registry()}
    sc = records["ScientificConsistency"]
    assert sc.status == "PARTIAL_REALWORLD_EVIDENCE"
    assert any("0.35" in x for x in sc.limitations)
    assert any("precision" in x for x in sc.limitations)


def test_registry_has_demand_compiler():
    records = {r.capability.name: r for r in default_capability_registry()}
    assert "DemandToCapability" in records
    assert "opportunity_assessment" in records["DemandToCapability"].capability.covers
