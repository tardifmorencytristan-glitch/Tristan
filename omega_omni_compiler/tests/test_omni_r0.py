import unittest

from omega_omni_compiler.src.universal_ir import UniversalIRObject
from omega_omni_compiler.src.transformations import default_registry
from omega_omni_compiler.src.path_router import find_path
from omega_omni_compiler.src.loss_ledger import LossEntry, summarize
from omega_omni_compiler.src.roundtrip import verify_round_trip
from omega_omni_compiler.src.scientific_bridge import scientific_ir_to_universal, universal_to_scientific_ir


class OmniR0Tests(unittest.TestCase):
    def test_universal_ir_requires_provenance(self):
        obj = UniversalIRObject(id="X", type="SCIENTIFIC")
        self.assertIn("provenance required", obj.validate())

    def test_path_router_finds_scientific_to_artifact(self):
        path = find_path(default_registry(), "SCIENTIFIC", "ARTIFACT")
        self.assertIsNotNone(path)
        self.assertEqual(path.transforms, ("scientific_to_document", "document_to_artifact"))

    def test_path_router_prefers_lower_loss_route(self):
        path = find_path(default_registry(), "ARTIFACT", "SCIENTIFIC")
        self.assertIsNotNone(path)
        self.assertEqual(path.transforms, ("artifact_to_document", "document_to_scientific"))
        self.assertGreater(path.total_loss_count, 0)

    def test_loss_ledger_keeps_explicit_loss_state(self):
        report = summarize([
            LossEntry("artifact_to_document", "layout", "PRESERVED"),
            LossEntry("artifact_to_document", "source_semantics", "LOST"),
        ])
        self.assertEqual(report["counts"]["LOST"], 1)
        self.assertEqual(report["counts"]["PRESERVED"], 1)

    def test_scientific_bridge_round_trip_preserves_core_sets(self):
        source = {
            "project": {"id": "demo", "title": "Demo", "document_type": "article"},
            "claims": [{"id": "C1", "statement": "x", "status": "OBSERVATION", "evidence_ids": ["E1"], "scope": "demo", "uncertainty": "bounded"}],
            "evidence": [{"id": "E1", "kind": "other", "provenance": "demo"}],
            "equations": [], "figures": [], "citations": [], "results": []
        }
        obj = scientific_ir_to_universal(source)
        recovered = universal_to_scientific_ir(obj)
        self.assertEqual(source, recovered)

    def test_generic_round_trip_detects_semantic_drift(self):
        source = {"claims": ["C1"], "scope": "A"}
        forward = lambda x: dict(x)
        reverse = lambda x: {**x, "scope": "B"}
        receipt = verify_round_trip(source, forward, reverse, ["claims", "scope"], "SCIENTIFIC", "DOCUMENT")
        self.assertFalse(receipt.passed)
        self.assertEqual(receipt.mismatches, ("scope",))


if __name__ == "__main__":
    unittest.main()
