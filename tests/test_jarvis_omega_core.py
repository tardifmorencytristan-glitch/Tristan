import unittest
from pathlib import Path

from tristan.book0 import Book0Seed, compare_seeds
from tristan.jarvis import compile_jarvis_plan
from tristan.jarvis_ir import ClaimIR, EvidenceIR, ExperimentIR, TransformationIR
from tristan.oak import EvidenceVector, promote, promotion_errors
from tristan.registry import Registry
from tristan.router import ActionCandidate, choose_next_action, rank_actions


ROOT = Path(__file__).resolve().parents[1]


class JarvisOmegaCoreTests(unittest.TestCase):
    def test_ir_validators_fail_closed(self):
        claim = ClaimIR("", "")
        self.assertTrue(claim.validate())

        evidence = EvidenceIR("e1", "test", "", "m", "r")
        self.assertIn("source required", evidence.validate())
        self.assertIn("provenance required", evidence.validate())

        tx = TransformationIR("t1", "formalize", "x", "claim", rollback="")
        self.assertIn("rollback required", tx.validate())

        experiment = ExperimentIR("e", "c")
        self.assertIn("at least one observable required", experiment.validate())

    def test_oak_blocks_status_skips(self):
        claim = ClaimIR("c1", "bounded claim", witness="observable-x", status="ACTIVE")
        errs = promotion_errors("ACTIVE", "MEASURED", claim, EvidenceVector(experimental=True))
        self.assertTrue(errs)
        with self.assertRaises(ValueError):
            promote("ACTIVE", "MEASURED", claim, EvidenceVector(experimental=True))

    def test_oak_requires_domain_specific_evidence(self):
        claim = ClaimIR("c1", "theorem", witness="lean-kernel", status="FORMALIZED")
        self.assertEqual(promote("FORMALIZED", "CERTIFIED_MATH", claim, EvidenceVector(formal=True)), "CERTIFIED_MATH")
        with self.assertRaises(ValueError):
            promote("FORMALIZED", "CERTIFIED_MATH", claim, EvidenceVector(computational=True))

    def test_router_prefers_verified_gain_per_burden(self):
        candidates = [
            ActionCandidate("novel", "generate", capability_gain=4, cost=4, complexity=1),
            ActionCandidate("debt", "validate", evidence_gain=3, debt_reduction=4, cost=1, complexity=1),
        ]
        self.assertEqual(choose_next_action(candidates).action_id, "debt")
        self.assertEqual(rank_actions(candidates)[0].action_id, "debt")

    def test_book0_semantic_digest_is_order_independent(self):
        a = Book0Seed("jarvis", ("B", "A"), ("d2", "d1"), ("t2", "t1"), ("f2", "f1"), "python -m tristan")
        b = Book0Seed("jarvis", ("A", "B"), ("d1", "d2"), ("t1", "t2"), ("f1", "f2"), "python -m tristan")
        self.assertTrue(compare_seeds(a, b).valid)

    def test_jarvis_plan_is_evidence_bounded(self):
        reg = Registry.load(ROOT / "registry/objects.jsonl")
        plan = compile_jarvis_plan("context regeneration evidence", reg)
        self.assertEqual(plan.epistemic_status, "PROVISIONAL_ENGINEERING_PLAN")
        self.assertIn("Generated != Verified", plan.boundaries)
        self.assertIn(plan.next_action, {
            "RETRIEVE_EVIDENCE",
            "CLOSE_EVIDENCE_DEBT",
            "ADVERSARIAL_CHALLENGE",
            "REUSE_VERIFIED_CONTEXT",
            "SEARCH_PRIOR_ART",
            "NO_ACTION",
        })


if __name__ == "__main__":
    unittest.main()
