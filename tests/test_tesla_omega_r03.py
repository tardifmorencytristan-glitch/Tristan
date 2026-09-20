import unittest

from tristan.tesla_omega.rlc import (
    default_couplings,
    frequency_sweep,
    terminal_pair,
    transfer_at_frequency,
)
from tristan.tesla_omega.runner_r03 import compile_tesla_omega_r03
from tristan.tesla_omega.topology import chain, star


class TeslaOmegaR03Tests(unittest.TestCase):
    def test_terminal_pair_uses_graph_diameter(self):
        self.assertEqual(terminal_pair(chain(6)), (0, 5))

    def test_passive_efficiency_is_bounded(self):
        t = chain(4)
        n = len(t.nodes)
        row = transfer_at_frequency(
            t,
            159154.94309189534,
            (10e-6,) * n,
            (100e-9,) * n,
            (0.2,) * n,
            default_couplings(t, 0.08),
        )
        self.assertGreaterEqual(row["efficiency"], 0.0)
        self.assertLessEqual(row["efficiency"], 1.0 + 1e-9)

    def test_frequency_sweep_returns_peak(self):
        result = frequency_sweep(star(5), points=21)
        self.assertGreaterEqual(result["best"]["efficiency"], 0.0)
        self.assertLessEqual(result["best"]["efficiency"], 1.0 + 1e-9)

    def test_r03_is_deterministic(self):
        a = compile_tesla_omega_r03(samples=4, seed=123)
        b = compile_tesla_omega_r03(samples=4, seed=123)
        self.assertEqual(a, b)

    def test_r03_remains_non_authoritative(self):
        result = compile_tesla_omega_r03(samples=4, seed=321)
        self.assertEqual(result["status"], "ROBUST_RLC_COMPUTATIONAL_SCREENING_ONLY")
        self.assertFalse(result["authority_granted"])
        self.assertFalse(result["physical_validation_claimed"])
        self.assertEqual(len(result["candidates"]), 6)


if __name__ == "__main__":
    unittest.main()
