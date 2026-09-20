import unittest

from tristan.tesla_omega.architecture_r05 import coils_from_radii
from tristan.tesla_omega.finite_wire_r11 import (
    cross_section_filaments,
    finite_wire_mutual_inductance_h,
)
from tristan.tesla_omega.runner_r11 import compile_tesla_omega_r11


class TeslaOmegaR11Tests(unittest.TestCase):
    def test_cross_section_has_four_filaments(self):
        c=coils_from_radii((0.03,)*6)[0]
        self.assertEqual(len(cross_section_filaments(c)),4)

    def test_finite_wire_reciprocity(self):
        coils=coils_from_radii((0.03,)*6)
        a=finite_wire_mutual_inductance_h(coils[0],coils[1],24)
        b=finite_wire_mutual_inductance_h(coils[1],coils[0],24)
        self.assertAlmostEqual(a,b,places=15)

    def test_r11_closure(self):
        r=compile_tesla_omega_r11(segments=24)
        self.assertFalse(r["authority_granted"])
        self.assertLess(r["verification"]["candidate_solver_delta_a"],1e-10)
        self.assertLess(r["verification"]["candidate_power_closure_error_w"],1e-9)


if __name__=="__main__":
    unittest.main()
