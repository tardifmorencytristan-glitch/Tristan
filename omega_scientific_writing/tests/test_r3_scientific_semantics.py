import unittest

from omega_scientific_writing.src.scientific_types import validate_claim_types
from omega_scientific_writing.src.proof_obligations import missing_obligations, evaluate_obligations
from omega_scientific_writing.src.epistemic_diff import diff_states, promotion_events


class R3ScientificSemanticsTests(unittest.TestCase):
    def test_blocks_software_only_evidence_for_physical_claim(self):
        doc = {
            "claims": [{"id": "C1", "claim_type": "PHYSICAL", "evidence_ids": ["E1"]}],
            "evidence": [{"id": "E1", "kind": "software_test"}],
        }
        codes = {f["code"] for f in validate_claim_types(doc)}
        self.assertIn("EVIDENCE_TYPE_MISMATCH", codes)

    def test_accepts_engineering_claim_with_software_test(self):
        doc = {
            "claims": [{"id": "C1", "claim_type": "ENGINEERING", "evidence_ids": ["E1"]}],
            "evidence": [{"id": "E1", "kind": "software_test"}],
        }
        errors = [f for f in validate_claim_types(doc) if f["severity"] == "ERROR"]
        self.assertEqual(errors, [])

    def test_proof_obligations_are_type_specific(self):
        claim = {
            "id": "P1",
            "claim_type": "PHYSICAL",
            "obligations_satisfied": ["physical_model", "units_or_dimensions"],
        }
        missing = missing_obligations(claim)
        self.assertIn("domain_of_validity", missing)
        self.assertIn("falsifier", missing)
        self.assertNotIn("physical_model", missing)

    def test_open_obligations_are_reported_not_silently_passed(self):
        doc = {"claims": [{"id": "C1", "claim_type": "COMPLIANCE", "obligations_satisfied": []}]}
        findings = evaluate_obligations(doc)
        self.assertEqual(findings[0]["code"], "PROOF_OBLIGATIONS_OPEN")

    def test_epistemic_diff_detects_status_evidence_and_scope_changes(self):
        before = {"claims": [{"id":"C1", "status":"SIMULATION", "evidence_ids":["E1"], "scope":"A"}]}
        after = {"claims": [{"id":"C1", "status":"MEASUREMENT", "evidence_ids":["E1","E2"], "scope":"A+B"}, {"id":"C2", "status":"IDEA"}]}
        diff = diff_states(before, after)
        self.assertEqual(diff["claims_added"], ["C2"])
        self.assertEqual(len(diff["status_changes"]), 1)
        self.assertEqual(len(diff["evidence_changes"]), 1)
        self.assertEqual(len(diff["scope_changes"]), 1)
        self.assertEqual(promotion_events(diff)[0]["id"], "C1")


if __name__ == "__main__":
    unittest.main()
