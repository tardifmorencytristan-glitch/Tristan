import unittest

from tristan.tesla_omega.architecture_r05 import coils_from_radii
from tristan.tesla_omega.mechanical_r10 import (
    mechanically_valid,
    minimum_clearance_margin_m,
    paired_mechanical_robustness,
)
from tristan.tesla_omega.runner_r08 import BEST_R07
from tristan.tesla_omega.runner_r10 import compile_tesla_omega_r10


class TeslaOmegaR10Tests(unittest.TestCase):
    def test_nominal_candidate_has_finite_margin(self):
        m=minimum_clearance_margin_m(coils_from_radii(BEST_R07))
        self.assertTrue(m==m)

    def test_mechanical_validity_matches_margin(self):
        coils=coils_from_radii(BEST_R07)
        self.assertEqual(
            mechanically_valid(coils),
            minimum_clearance_margin_m(coils)>=0.0,
        )

    def test_mechanical_stress_accounting_closes(self):
        r=paired_mechanical_robustness(samples=4,seed=1,segments=16)
        self.assertEqual(r["accepted"]+r["rejected_mechanical"],4)
        self.assertEqual(r["wins"]+r["losses"],r["accepted"])

    def test_r10_non_authoritative(self):
        r=compile_tesla_omega_r10(samples=4,seed=2,segments=16)
        self.assertFalse(r["authority_granted"])
        self.assertFalse(r["physical_validation_claimed"])


if __name__=="__main__":
    unittest.main()
