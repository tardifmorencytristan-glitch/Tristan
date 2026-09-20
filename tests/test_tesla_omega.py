import math
import unittest

from tristan.tesla_omega.failures import Failure, FailureMemory
from tristan.tesla_omega.models import OAKVector, Status
from tristan.tesla_omega.oak import promote
from tristan.tesla_omega.physics import coupled_two_resonator_frequencies_hz, resonant_frequency_hz
from tristan.tesla_omega.pipeline import compile_tesla_omega_status
from tristan.tesla_omega.topology import binary_tree, chain, mutate_add_leaf, star


class TeslaOmegaTests(unittest.TestCase):
    def test_lc_resonance(self):
        f = resonant_frequency_hz(10e-6, 100e-9)
        expected = 1.0 / (2.0 * math.pi * math.sqrt(10e-6 * 100e-9))
        self.assertAlmostEqual(f, expected, places=9)

    def test_mode_splitting(self):
        lo, hi = coupled_two_resonator_frequencies_hz(10e-6, 100e-9, 0.2)
        f0 = resonant_frequency_hz(10e-6, 100e-9)
        self.assertLess(lo, f0)
        self.assertGreater(hi, f0)

    def test_oak_rejects_jump(self):
        with self.assertRaises(ValueError):
            promote(OAKVector(), "experimental", Status.MEASURED)

    def test_oak_single_step(self):
        v = promote(OAKVector(), "documentary", Status.DOCUMENTED)
        self.assertEqual(v.documentary, Status.DOCUMENTED)

    def test_topologies_have_distinct_signatures(self):
        signatures = {chain(5).signature(), star(5).signature(), binary_tree(3).signature()}
        self.assertEqual(len(signatures), 3)

    def test_mutation_add_leaf(self):
        t = chain(3)
        m = mutate_add_leaf(t, 1)
        self.assertEqual(len(m.nodes), 4)
        self.assertEqual(len(m.edges), 3)

    def test_failure_memory_is_append_only_by_id(self):
        memory = FailureMemory()
        failure = Failure("F001", "h", "c", "p", "o", "r", "do not repeat")
        memory.add(failure)
        with self.assertRaises(ValueError):
            memory.add(failure)
        self.assertEqual(memory.constraints(), ("do not repeat",))

    def test_status_is_non_authoritative(self):
        status = compile_tesla_omega_status()
        self.assertFalse(status["authority_granted"])
        self.assertFalse(status["physical_validation_claimed"])
        self.assertGreaterEqual(status["sources"], 7)


if __name__ == "__main__":
    unittest.main()
