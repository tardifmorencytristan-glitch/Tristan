import json
import unittest
from pathlib import Path

from omega_scientific_writing.src.thesis_state import compile_r4_manifest
from omega_scientific_writing.src.r5_candidate import build_r5_candidate, validate_no_epistemic_upgrade


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "benchmarks" / "r4_living_delta_manifest.json"


class ThesisStateR2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.state = compile_r4_manifest(cls.manifest)

    def test_all_eight_crystallizations_become_observation_claims(self):
        self.assertEqual(len(self.state["claims"]), 8)
        self.assertTrue(all(c["status"] == "OBSERVATION" for c in self.state["claims"]))

    def test_each_claim_has_snapshot_evidence_and_boundary(self):
        self.assertEqual(len(self.state["evidence"]), 8)
        evidence_ids = {e["id"] for e in self.state["evidence"]}
        for claim in self.state["claims"]:
            self.assertEqual(len(claim["evidence_ids"]), 1)
            self.assertIn(claim["evidence_ids"][0], evidence_ids)
            self.assertIn("not been independently revalidated", claim["uncertainty"])

    def test_r4_open_frontiers_survive_as_residuals(self):
        self.assertEqual(len(self.state["residuals"]), len(self.manifest["open_frontiers"]))
        self.assertTrue(all(r["status"] == "OPEN" for r in self.state["residuals"]))

    def test_r5_candidate_preserves_claim_set_and_forbids_upgrade(self):
        candidate = build_r5_candidate(self.state)
        self.assertEqual(validate_no_epistemic_upgrade(self.state, candidate), [])
        self.assertTrue(candidate["epistemic_policy"]["no_status_upgrade"])


if __name__ == "__main__":
    unittest.main()
