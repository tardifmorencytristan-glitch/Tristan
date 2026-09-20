import unittest

from tristan.tesla_omega.geometry import (
    conductor_length_proxy,
    geometric_couplings,
    hex_bridge_geometry,
)
from tristan.tesla_omega.geometry_court import geometry_matched_tree_court
from tristan.tesla_omega.runner_r04 import compile_tesla_omega_r04
from tristan.tesla_omega.topology import chain


class TeslaOmegaR04Tests(unittest.TestCase):
    def test_geometry_has_fixed_tx_rx_distance(self):
        pts=hex_bridge_geometry()
        self.assertEqual(len(pts),6)
        self.assertAlmostEqual(pts[-1].x-pts[0].x,0.5)

    def test_coupling_decays_with_distance(self):
        t=chain(3)
        pts=(hex_bridge_geometry()[0],hex_bridge_geometry()[1],hex_bridge_geometry()[5])
        ks=geometric_couplings(t,pts)
        self.assertGreater(ks[(0,1)],ks[(1,2)])

    def test_conductor_proxy_positive(self):
        self.assertGreater(conductor_length_proxy(chain(6),hex_bridge_geometry()),0)

    def test_geometry_court_has_six_tree_classes(self):
        court=geometry_matched_tree_court()
        self.assertEqual(len(court),6)
        self.assertTrue(all(r["best_embedding"]["peak"]["efficiency"]>=0 for r in court))

    def test_r04_non_authoritative(self):
        r=compile_tesla_omega_r04()
        self.assertFalse(r["authority_granted"])
        self.assertFalse(r["physical_validation_claimed"])
        self.assertEqual(r["status"],"GEOMETRY_MATCHED_COMPUTATIONAL_SCREENING_ONLY")


if __name__=="__main__":
    unittest.main()
