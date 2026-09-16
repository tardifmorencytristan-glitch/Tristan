import json
import unittest
from pathlib import Path

from omega_scientific_writing.src.writing_court import run_court, score_text

ROOT = Path(__file__).resolve().parents[1]


class R41WritingCourtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads((ROOT / "fixtures" / "battery_t_r0_4_writing_court.json").read_text(encoding="utf-8"))

    def test_overclaim_is_penalized(self):
        spec = self.packet["frozen_spec"]
        bad = next(x for x in self.packet["candidates"] if x["origin"] == "ADVERSARIAL_OVERCLAIM")
        good = next(x for x in self.packet["candidates"] if x["origin"] == "R4_BOUNDED")
        self.assertLess(score_text(bad["text"], spec)["score"], score_text(good["text"], spec)["score"])

    def test_no_action_is_admissible(self):
        result = run_court(self.packet)
        self.assertIn("SOURCE_NO_ACTION", result["origin_map_audit_only"].values())
        self.assertIn("NO_ACTION is admissible", result["boundaries"])

    def test_blind_ranking_does_not_expose_origin(self):
        result = run_court(self.packet)
        self.assertTrue(result["ranking_blind"])
        self.assertTrue(all("origin" not in row for row in result["ranking_blind"]))

    def test_r4_bounded_preserves_frozen_numbers(self):
        spec = self.packet["frozen_spec"]
        r4 = next(x for x in self.packet["candidates"] if x["origin"] == "R4_BOUNDED")
        scored = score_text(r4["text"], spec)
        self.assertEqual(1.0, scored["components"]["numeric_fidelity"])
        self.assertEqual(1.0, scored["components"]["calibration"])

    def test_source_is_exact_commit_bound(self):
        src = self.packet["source"]
        self.assertEqual("d759105682704f037f21fef8f6d396b4d0408f3a", src["commit"])
        self.assertEqual("battery/evidence/CALCE_ZERO_FIT_TRANSFER_R0_4.json", src["path"])


if __name__ == "__main__":
    unittest.main()
