import unittest

from tristan.jarvis_ir import ClaimIR, EvidenceIR
from omega_omni_compiler.src.communication_projection import (
    CommunicationProjectionSpec,
    TimedProjectionIR,
    TimedProjectionSegment,
    evaluate_projection,
)
from omega_omni_compiler.src.provenance import ProvenanceAnchor
from omega_omni_compiler.src.representation_ir import RepresentationGraph, RepresentationNode


class CommunicationProjectionBridgeTests(unittest.TestCase):
    def test_jarvis_claim_evidence_ir_structurally_satisfies_omni_projection_protocol(self):
        anchor = ProvenanceAnchor(
            source_artifact_id="bridge",
            source_content_hash="a" * 64,
            extractor="bridge-test",
            extractor_version="1",
            confidence=1.0,
        )
        graph = RepresentationGraph()
        graph.add_node(RepresentationNode("p1", "PARAGRAPH", content="bounded", provenance=[anchor]))
        claim = ClaimIR("c1", "bounded", evidence_ids=("e1",), uncertainty="BOUNDED")
        evidence = EvidenceIR("e1", "dataset", "source", "method", "result", "BOUNDED", ("source",))
        projection = TimedProjectionIR(
            CommunicationProjectionSpec("bridge", "TEXT", "technical", "en", 5.0),
            (
                TimedProjectionSegment(
                    "s1", 0.0, 1.0, ("p1",), ("c1",), ("e1",),
                    on_screen_text="bounded", provenance_ids=("source",),
                ),
            ),
        )
        receipt = evaluate_projection(projection, graph, (claim,), (evidence,))
        self.assertEqual(receipt.status, "PASS_STRUCTURAL")
        self.assertFalse(receipt.authority_granted)


if __name__ == "__main__":
    unittest.main()
