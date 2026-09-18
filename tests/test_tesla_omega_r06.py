import unittest

from tristan.tesla_omega.architecture_r05 import BASE_RADIUS_M, coils_from_radii
from tristan.tesla_omega.independent_solver import solve_lu_partial_pivot
from tristan.tesla_omega.runner_r06 import compile_tesla_omega_r06
from tristan.tesla_omega.validity_r06 import independent_solver_check, minimum_pair_separation_ratio


class TeslaOmegaR06Tests(unittest.TestCase):
    def test_second_solver(self):
        a=[[2+0j,1+0j],[1+0j,3+0j]]
        b=[1+0j,2+0j]
        x=solve_lu_partial_pivot(a,b)
        self.assertAlmostEqual(x[0].real,0.2)
        self.assertAlmostEqual(x[1].real,0.6)

    def test_baseline_has_positive_validity_ratio(self):
        ratio=minimum_pair_separation_ratio(coils_from_radii((BASE_RADIUS_M,)*6))
        self.assertGreater(ratio,0)

    def test_independent_solvers_agree(self):
        check=independent_solver_check((BASE_RADIUS_M,)*6,159154.94309189534)
        self.assertLess(check["max_current_solution_delta_a"],1e-10)

    def test_r06_gates_candidates(self):
        r=compile_tesla_omega_r06()
        self.assertGreater(r["candidate_count"],0)
        self.assertLessEqual(r["survivor_count"],r["candidate_count"])
        self.assertFalse(r["authority_granted"])

    def test_r06_keeps_boundary(self):
        r=compile_tesla_omega_r06()
        self.assertIn("IndependentLinearSolverAgreement != PhysicsValidation",r["boundaries"])


if __name__=="__main__":
    unittest.main()
