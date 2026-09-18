import unittest

from tristan.tesla_omega.robust_neumann_r08 import paired_robustness, perturb_coils
from tristan.tesla_omega.runner_r08 import BEST_R07, compile_tesla_omega_r08
from tristan.tesla_omega.architecture_r05 import BASE_RADIUS_M
import random


class TeslaOmegaR08Tests(unittest.TestCase):
    def test_perturbation_is_deterministic(self):
        a=perturb_coils(BEST_R07,random.Random(123))
        b=perturb_coils(BEST_R07,random.Random(123))
        self.assertEqual(a,b)

    def test_paired_robustness_is_deterministic(self):
        a=paired_robustness((BASE_RADIUS_M,)*6,BEST_R07,samples=2,seed=1,segments=16)
        b=paired_robustness((BASE_RADIUS_M,)*6,BEST_R07,samples=2,seed=1,segments=16)
        self.assertEqual(a,b)

    def test_candidate_win_fraction_bounded(self):
        r=paired_robustness((BASE_RADIUS_M,)*6,BEST_R07,samples=2,seed=2,segments=16)
        self.assertGreaterEqual(r["candidate_win_fraction"],0.0)
        self.assertLessEqual(r["candidate_win_fraction"],1.0)

    def test_r08_non_authoritative(self):
        r=compile_tesla_omega_r08(samples=2,seed=3,segments=16)
        self.assertFalse(r["authority_granted"])
        self.assertFalse(r["physical_validation_claimed"])


if __name__=="__main__":
    unittest.main()
