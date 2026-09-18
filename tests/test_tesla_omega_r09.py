import unittest

from tristan.tesla_omega.runner_r09 import compile_tesla_omega_r09
from tristan.tesla_omega.stress_r09 import SCENARIOS, compile_stress_ladder


class TeslaOmegaR09Tests(unittest.TestCase):
    def test_stress_ladder_has_all_scenarios(self):
        rows=compile_stress_ladder(samples=1,seed=1,segments=16)
        self.assertEqual(len(rows),len(SCENARIOS))

    def test_stress_rows_are_bounded(self):
        rows=compile_stress_ladder(samples=1,seed=2,segments=16)
        for r in rows:
            self.assertGreaterEqual(r["candidate_win_fraction"],0.0)
            self.assertLessEqual(r["candidate_win_fraction"],1.0)
            self.assertGreater(r["ratio_min"],0.0)

    def test_r09_non_authoritative(self):
        r=compile_tesla_omega_r09(samples=1,seed=3,segments=16)
        self.assertFalse(r["authority_granted"])
        self.assertFalse(r["physical_validation_claimed"])


if __name__=="__main__":
    unittest.main()
