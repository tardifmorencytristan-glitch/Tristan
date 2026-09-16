import json
import unittest
from pathlib import Path

from omega_omni_compiler.src.pdf_roundtrip import PDFRoundTripEvidence, semantic_readback, preserved_from_checks


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "benchmarks" / "r3_r4_p1p2_roundtrip_receipt.json"
DOCIR = ROOT / "benchmarks" / "r3_r4_p1p2_document_ir.json"
READBACK = ROOT / "benchmarks" / "r3_r4_p1p2_readback.txt"


class OmniR3PDFRoundTripTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        cls.docir = json.loads(DOCIR.read_text(encoding="utf-8"))
        cls.readback = READBACK.read_text(encoding="utf-8")

    def test_real_pdf_receipt_is_bounded_and_hashed(self):
        self.assertEqual(self.receipt["source"]["pages"], [1, 2])
        self.assertEqual(len(self.receipt["source"]["sha256"]), 64)
        self.assertEqual(len(self.receipt["output"]["sha256"]), 64)
        self.assertGreater(self.receipt["source"]["bytes"], 0)
        self.assertTrue(self.receipt["losses"])

    def test_selected_semantic_invariants_survived_real_readback_text(self):
        expected = [
            self.docir["anchors"]["r3_anchor"],
            self.docir["anchors"]["r4_frozen_head"],
            *self.docir["claims"],
            self.docir["status"],
        ]
        checks = semantic_readback(expected, self.readback)
        self.assertTrue(all(checks.values()))
        self.assertIn("+68 / -0", self.readback)
        self.assertEqual(self.docir["anchors"]["delta_commits_ahead"], 68)
        self.assertEqual(self.docir["anchors"]["delta_commits_behind"], 0)

    def test_receipt_checks_match_persisted_readback(self):
        for invariant, recorded in self.receipt["readback_checks"].items():
            if invariant == "delta_+68_-0":
                observed = "+68 / -0" in self.readback
            else:
                observed = invariant in self.readback
            self.assertEqual(recorded, observed)

    def test_evidence_model_requires_explicit_losses(self):
        expected = [
            self.docir["anchors"]["r3_anchor"],
            self.docir["anchors"]["r4_frozen_head"],
            *self.docir["claims"],
            self.docir["status"],
            "delta_+68_-0",
        ]
        checks = dict(self.receipt["readback_checks"])
        evidence = PDFRoundTripEvidence(
            source_pdf_sha256=self.receipt["source"]["sha256"],
            output_pdf_sha256=self.receipt["output"]["sha256"],
            source_pages=self.receipt["source"]["pages"],
            expected_invariants=expected,
            preserved_invariants=preserved_from_checks(checks),
            losses=self.receipt["losses"],
            boundaries=self.receipt["boundaries"],
            latex_engine=self.receipt["latex_engine"],
            source_bytes=self.receipt["source"]["bytes"],
            output_pages=self.receipt["output"]["pages"],
        )
        self.assertEqual(evidence.validate(), [])
        self.assertTrue(evidence.semantic_roundtrip_pass())

    def test_semantic_readback_fails_when_one_invariant_disappears(self):
        checks = semantic_readback(["Generated != Verified", "Capability != Authority"], "Generated != Verified")
        self.assertTrue(checks["Generated != Verified"])
        self.assertFalse(checks["Capability != Authority"])


if __name__ == "__main__":
    unittest.main()
