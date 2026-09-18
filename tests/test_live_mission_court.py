import json
from pathlib import Path
import unittest

from tristan.live_mission_court import (
    assess_render_staging,
    compile_scientific_source_mission,
    decide_drive_reuse,
    qualify_exact_head,
)


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts" / "INTELLIGENCE_OMEGA_LIVE_MISSIONS_R0_6.json"


class LiveMissionCourtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(RECEIPT.read_text(encoding="utf-8"))

    def test_frozen_live_missions_reproduce_expected_decisions(self):
        decisions = {}
        for mission in self.payload["missions"]:
            kind = mission["kind"]
            if kind == "drive_reuse":
                receipt = decide_drive_reuse(
                    mission_id=mission["mission_id"],
                    matching_artifact_ids=tuple(mission["matching_artifact_ids"]),
                )
            elif kind == "github_exact_head":
                receipt = qualify_exact_head(
                    mission_id=mission["mission_id"],
                    candidate_head=mission["candidate_head"],
                    observed_head=mission["observed_head"],
                    required_workflows=tuple(tuple(row) for row in mission["required_workflows"]),
                )
            elif kind == "render_staging":
                receipt = assess_render_staging(
                    mission_id=mission["mission_id"],
                    candidate_repo=mission["candidate_repo"],
                    candidate_branch=mission["candidate_branch"],
                    service_repo=mission["service_repo"],
                    service_branch=mission["service_branch"],
                    service_id=mission["service_id"],
                )
            elif kind == "scientific_source_plan":
                receipt = compile_scientific_source_mission(
                    mission_id=mission["mission_id"],
                    intent=mission["intent"],
                )
                required = set(mission["required_sources"])
                self.assertTrue(required <= set(receipt.evidence_refs))
            else:
                self.fail(f"unknown mission kind: {kind}")

            decisions[mission["mission_id"]] = receipt.decision
            self.assertEqual(receipt.decision, mission["expected_decision"])
            self.assertFalse(receipt.authority_granted)
            self.assertFalse(receipt.scientific_pass)

        self.assertEqual(len(decisions), 4)

    def test_exact_head_fails_closed_on_mismatch(self):
        receipt = qualify_exact_head(
            mission_id="m",
            candidate_head="a",
            observed_head="b",
            required_workflows=(("ci", "success", "1"),),
        )
        self.assertEqual(receipt.decision, "HOLD_HEAD_MISMATCH")

    def test_render_matching_repo_but_wrong_branch_does_not_deploy(self):
        receipt = assess_render_staging(
            mission_id="m",
            candidate_repo="repo",
            candidate_branch="feature",
            service_repo="repo",
            service_branch="main",
            service_id="service",
        )
        self.assertEqual(receipt.decision, "NO_DEPLOY_BRANCH_MISMATCH")

    def test_science_plan_does_not_claim_retrieval(self):
        receipt = compile_scientific_source_mission(
            mission_id="m",
            intent="CERN JWST multi-instrument physics",
        )
        self.assertEqual(receipt.decision, "SOURCE_PLAN_ONLY")
        self.assertIn("cern_open_data", receipt.evidence_refs)
        self.assertIn("jwst_mast", receipt.evidence_refs)
        self.assertFalse(receipt.scientific_pass)


if __name__ == "__main__":
    unittest.main()
