import unittest

from tristan.tesla_omega.architecture_r05 import BASE_RADIUS_M, equal_copper_symmetric_search, evaluate_radius_schedule
from tristan.tesla_omega.coil_physics import CoilSpec, Vec3, ac_resistance_skin_approx, dipole_mutual_inductance_h, skin_depth_m
from tristan.tesla_omega.runner_r05 import compile_tesla_omega_r05


class TeslaOmegaR05Tests(unittest.TestCase):
    def test_skin_depth_decreases_with_frequency(self):
        self.assertGreater(skin_depth_m(1e3),skin_depth_m(1e6))

    def test_ac_resistance_increases_with_frequency(self):
        c=CoilSpec(Vec3(0,0,0),Vec3(0,0,1),0.03)
        self.assertGreater(ac_resistance_skin_approx(c,1e6),ac_resistance_skin_approx(c,1e3))

    def test_coplanar_parallel_dipoles_have_negative_mutual(self):
        a=CoilSpec(Vec3(0,0,0),Vec3(0,0,1),0.02)
        b=CoilSpec(Vec3(0.2,0,0),Vec3(0,0,1),0.02)
        self.assertLess(dipole_mutual_inductance_h(a,b),0)

    def test_equal_copper_search_preserves_wire_length(self):
        base=evaluate_radius_schedule((BASE_RADIUS_M,)*6,frequency_points=5)
        rows=equal_copper_symmetric_search(step_m=0.015)
        for row in rows:
            self.assertAlmostEqual(row["wire_length_m"],base["wire_length_m"],places=12)

    def test_r05_has_closure_checks(self):
        r=compile_tesla_omega_r05()
        self.assertFalse(r["authority_granted"])
        self.assertFalse(r["physical_validation_claimed"])
        self.assertLess(r["verification"]["best_max_linear_residual"],1e-9)
        self.assertLess(r["verification"]["best_power_closure_error_w"],1e-9)


if __name__=="__main__":
    unittest.main()
