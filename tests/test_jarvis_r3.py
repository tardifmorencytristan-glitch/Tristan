import unittest
from pathlib import Path

from tristan.book0 import Book0Seed
from tristan.crystal import CrystalCandidate
from tristan.dependency_rebuild import differential_rebuild_plan
from tristan.domain_adapters import default_domain_adapters, validate_default_domain_adapters
from tristan.failure_causal import CauseHypothesis, DiscriminatingTest, choose_discriminating_test
from tristan.r3 import compile_r3_status
from tristan.regenerable_crystal import qualify_regenerable_crystal
from tristan.registry import Registry


ROOT = Path(__file__).resolve().parents[1]


class JarvisR3Tests(unittest.TestCase):
    def test_differential_rebuild_only_touches_dependents(self):
        dependencies = {
            "B": {"A"},
            "C": {"B"},
            "D": {"X"},
        }
        plan = differential_rebuild_plan({"A"}, dependencies)
        self.assertEqual(plan.affected_ids, ("A", "B", "C"))
        self.assertEqual(plan.rebuild_order, ("A", "B", "C"))
        self.assertFalse(plan.full_rebuild)

    def test_differential_rebuild_rejects_cycles(self):
        dependencies = {"A": {"B"}, "B": {"A"}}
        with self.assertRaises(ValueError):
            differential_rebuild_plan({"A"}, dependencies)

    def test_failure_causal_router_selects_discriminating_test(self):
        causes = [
            CauseHypothesis("c1", "f1", "parameter mismatch"),
            CauseHypothesis("c2", "f1", "topology mismatch"),
        ]
        tests = [
            DiscriminatingTest("weak", cost=1, risk=0, predictions={"c1": "same", "c2": "same"}),
            DiscriminatingTest("strong", cost=1, risk=0, predictions={"c1": "pass", "c2": "fail"}),
        ]
        self.assertEqual(choose_discriminating_test(causes, tests).test_id, "strong")

    def test_regenerable_crystal_requires_matching_book0(self):
        candidate = CrystalCandidate(
            "jarvis-r3", "spec", "impl", ("tests",), ("e1",), ("f1",),
            "digest-present", ("cli",), benchmarks=("bench",),
            oak_status="COMPUTATIONALLY_VERIFIED",
        )
        expected = Book0Seed("r3", ("I1",), ("dep",), ("test",), ("f1",), "regen")
        same = Book0Seed("r3", ("I1",), ("dep",), ("test",), ("f1",), "regen")
        changed = Book0Seed("r3", ("I2",), ("dep",), ("test",), ("f1",), "regen")
        self.assertEqual(
            qualify_regenerable_crystal(candidate, expected, same).status,
            "REGENERABLE_ENGINEERING_CRYSTAL",
        )
        self.assertEqual(
            qualify_regenerable_crystal(candidate, expected, changed).status,
            "HOLD",
        )

    def test_domain_adapters_are_explicit_and_bounded(self):
        adapters = default_domain_adapters()
        self.assertEqual(set(adapters), {"tfuga", "prime", "lc_fractal", "gaia"})
        self.assertTrue(all(not errors for errors in validate_default_domain_adapters().values()))
        self.assertIn("Simulation != Measurement", adapters["lc_fractal"].constraints)
        self.assertIn("SimulatedImpact != MeasuredImpact", adapters["gaia"].constraints)

    def test_r3_status_never_claims_science(self):
        reg = Registry.load(ROOT / "registry/objects.jsonl")
        status = compile_r3_status(reg)
        self.assertEqual(status.status, "PROVISIONAL_ENGINEERING_R3")
        self.assertFalse(status.scientific_pass)
        self.assertIn("RegenerableEngineeringCrystal != ScientificPASS", status.boundaries)


if __name__ == "__main__":
    unittest.main()
