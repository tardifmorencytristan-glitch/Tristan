import unittest

from tristan.capability_lease import CapabilityProof, ProofCarryingCapabilityLease
from tristan.epistemic_memory import MemoryKind, MemoryRecord
from tristan.ood_court import OODMission, OODResult, evaluate_ood_candidate
from tristan.outcome_readback import memory_from_reality
from tristan.reality_loop import observe_reality, plan_digest
from tristan.shadow_court import StrategyCandidate, StrategyEvaluation, run_shadow_court
from tristan.transfer_gate import evaluate_transfer


class ShadowOODTransferTests(unittest.TestCase):
    def test_shadow_court_requires_all_roles(self):
        candidates = (
            StrategyCandidate("current", "CURRENT", "p1", "d1"),
            StrategyCandidate("shadow", "SHADOW", "p2", "d2"),
        )
        receipt = run_shadow_court(candidates, (), metric="score")
        self.assertEqual(receipt.status, "HOLD_MISSING_ROLE_COVERAGE")
        self.assertFalse(receipt.promotion_authority)

    def test_complete_shadow_court_is_contextual_only(self):
        candidates = (
            StrategyCandidate("current", "CURRENT", "p1", "d1"),
            StrategyCandidate("shadow", "SHADOW", "p2", "d2"),
            StrategyCandidate("counter", "COUNTER", "p3", "d3"),
            StrategyCandidate("external", "EXTERNAL", "p4", "d4"),
            StrategyCandidate("no_action", "NO_ACTION", "p5", "d5"),
        )
        evaluations = tuple(
            StrategyEvaluation(cid, "m1", "score", score, True, 0.05)
            for cid, score in (
                ("current", 0.7),
                ("shadow", 0.9),
                ("counter", 0.6),
                ("external", 0.8),
                ("no_action", 0.1),
            )
        )
        receipt = run_shadow_court(candidates, evaluations, metric="score")
        self.assertEqual(receipt.status, "CONTEXTUAL_COMPARISON_ONLY")
        self.assertEqual(receipt.ordered_candidates[0], "shadow")
        self.assertFalse(receipt.promotion_authority)

    def test_ood_and_transfer_gate(self):
        missions = (
            OODMission("o1", "physics", "sig-new-1", ("search", "model")),
            OODMission("o2", "physics", "sig-new-2", ("search", "model")),
        )
        results = (
            OODResult("shadow", "o1", 0.9, True, 0.1),
            OODResult("shadow", "o2", 0.85, True, 0.1),
        )
        ood = evaluate_ood_candidate(
            "shadow",
            missions,
            results,
            training_signatures=("sig-train",),
        )
        self.assertTrue(ood.transfer_evidence)

        record = MemoryRecord(
            record_id="m1",
            kind=MemoryKind.POSITIVE,
            context_tags=("physics", "lc"),
            mechanism="shadow-planner",
            outcome="better contextual score",
            confidence=0.9,
            evidence_ids=("e1",),
            provenance=("court:1",),
            transfer_scope=("physics", "spectroscopy"),
        )
        transfer = evaluate_transfer(record, ("physics", "spectroscopy"), ood)
        self.assertTrue(transfer.eligible)
        self.assertEqual(transfer.status, "ELIGIBLE_FOR_CONTEXTUAL_RETEST")
        self.assertFalse(transfer.authority_granted)

    def test_outcome_readback(self):
        digest = plan_digest({"mission":"m"})
        reality = observe_reality(
            plan_digest_value=digest,
            observer_id="observer",
            success_criteria=("a", "b"),
            passed_criteria=("a",),
        )
        record = memory_from_reality(
            record_id="m-neg",
            context_tags=("physics",),
            mechanism="candidate",
            reality=reality,
            evidence_ids=("reality:1",),
            provenance=("run:1",),
        )
        self.assertEqual(record.kind, MemoryKind.NEGATIVE)
        self.assertIn("reality_residual", record.outcome)

    def test_proof_carrying_capability_lease(self):
        digest = plan_digest({"mission":"m"})
        lease = ProofCarryingCapabilityLease(
            plan_digest=digest,
            holder_id="coalition-1",
            proofs=(
                CapabilityProof("search", ("bench:search",), ("physics",)),
                CapabilityProof("model", ("bench:model",), ("physics",)),
            ),
        )
        errors = lease.validate(
            plan_digest=digest,
            required_capabilities=("search", "model"),
            target_scope=("physics",),
        )
        self.assertEqual(errors, [])
        self.assertFalse(lease.authority_granted)


if __name__ == "__main__":
    unittest.main()
