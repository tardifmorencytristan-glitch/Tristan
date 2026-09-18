import unittest

from tristan.tesla_omega.architecture_r05 import coils_from_radii
from tristan.tesla_omega.neumann import neumann_convergence, neumann_mutual_inductance_h
from tristan.tesla_omega.runner_r07 import compile_tesla_omega_r07


class TeslaOmegaR07Tests(unittest.TestCase):
    def test_neumann_reciprocity(self):
        coils=coils_from_radii((0.03,)*6)
        a=neumann_mutual_inductance_h(coils[0],coils[1],32)
        b=neumann_mutual_inductance_h(coils[1],coils[0],32)
        self.assertAlmostEqual(a,b,places=15)

    def test_neumann_converges_for_adjacent_baseline_pair(self):
        coils=coils_from_radii((0.03,)*6)
        c=neumann_convergence(coils[0],coils[1],(16,32,64))
        self.assertLess(c["relative_last_change"],0.02)

    def test_r07_closure(self):
        r=compile_tesla_omega_r07(top_candidates=2)
        self.assertFalse(r["authority_granted"])
        self.assertLess(r["verification"]["best_solver_delta_a"],1e-10)
        self.assertLess(r["verification"]["best_power_closure_error_w"],1e-9)

    def test_r07_is_bounded(self):
        r=compile_tesla_omega_r07(top_candidates=2)
        self.assertEqual(r["candidate_count"],2)
        self.assertEqual(r["status"],"NEUMANN_FILAMENT_SCREENING_ONLY")


if __name__=="__main__":
    unittest.main()
