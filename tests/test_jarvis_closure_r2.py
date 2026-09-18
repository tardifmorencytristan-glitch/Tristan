import unittest
from pathlib import Path

from tristan.anti_corpus import AlternativeCandidate, anti_corpus_decision, pareto_frontier
from tristan.closure import compile_closure_plan
from tristan.crystal import CrystalCandidate, compile_crystal
from tristan.failure_genome import normalize_failure_record
from tristan.mission_queue import Mission, next_mission, rank_missions
from tristan.registry import Registry


ROOT = Path(__file__).resolve().parents[1]


class JarvisClosureR2Tests(unittest.TestCase):
    def test_failure_genome_normalizes_legacy_shape(self):
        genome = normalize_failure_record({
            "family": "FORMULA_AST_MISMATCH",
            "residual": "symbolic mismatch",
            "next_checker": "compare AST structure",
        }, source="receipts/R0_5_FAILURE_GENOMES.json")
        self.assertEqual(genome.family, "FORMULA_AST_MISMATCH")
        self.assertEqual(genome.action, "compare AST structure")
        self.assertEqual(genome.validate(), [])

    def test_anti_corpus_preserves_pareto_set_without_declaring_truth(self):
        candidates = [
            AlternativeCandidate("a", "c1", "simple", evidence_count=3, predictive_hits=2, complexity=1, cost=1),
            AlternativeCandidate("b", "c1", "dominated", evidence_count=2, predictive_hits=1, complexity=2, cost=2),
            AlternativeCandidate("c", "c1", "different tradeoff", evidence_count=4, predictive_hits=1, complexity=1, cost=3),
        ]
        ids = [c.candidate_id for c in pareto_frontier(candidates)]
        self.assertIn("a", ids)
        self.assertIn("c", ids)
        self.assertNotIn("b", ids)
        decision = anti_corpus_decision(candidates)
        self.assertFalse(decision["winner_declared"])

    def test_crystal_compiler_requires_evidence_and_book0(self):
        hold = compile_crystal(CrystalCandidate(
            "x", "spec", "impl", ("test",), (), (), "", ("api",), oak_status="COMPUTATIONALLY_VERIFIED"
        ))
        self.assertEqual(hold.status, "HOLD")
        ready = compile_crystal(CrystalCandidate(
            "x", "spec", "impl", ("test",), ("ev1",), ("f1",), "abc", ("api",),
            benchmarks=("bench1",), oak_status="COMPUTATIONALLY_VERIFIED"
        ))
        self.assertEqual(ready.status, "ENGINEERING_CRYSTAL_READY")
        self.assertFalse(ready.scientific_pass)

    def test_mission_queue_respects_dependencies_and_value_per_burden(self):
        missions = [
            Mission("m1", "x", "research", "court", expected_verified_gain=3, cost=1),
            Mission("m2", "x", "validate", "court", expected_verified_gain=4, debt_reduction=4, cost=1, dependencies=("m1",)),
        ]
        self.assertEqual(next_mission(missions).next_mission_id, "m1")
        ranked = rank_missions(missions, completed={"m1"})
        self.assertEqual(ranked[0].mission_id, "m2")

    def test_closure_plan_is_bounded_and_never_claims_science(self):
        reg = Registry.load(ROOT / "registry/objects.jsonl")
        plan = compile_closure_plan("context regeneration evidence", reg)
        self.assertEqual(plan.status, "PROVISIONAL_ENGINEERING_CLOSURE_PLAN")
        self.assertFalse(plan.scientific_pass)
        self.assertIn("EngineeringCrystal != ScientificPASS", plan.boundaries)
        self.assertTrue(plan.next_mission_id)


if __name__ == "__main__":
    unittest.main()
