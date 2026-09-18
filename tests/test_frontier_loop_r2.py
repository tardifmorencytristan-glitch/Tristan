import unittest

from tristan.autonomous_decision import ActionProposal
from tristan.frontier_loop import (
    ActionOutcome,
    FrontierPolicy,
    run_frontier_loop,
)


def proposal(action_id, gain=3.0):
    return ActionProposal(
        action_id=action_id,
        action_kind="internal_research_step",
        plan={"action": action_id},
        reversible=True,
        external_side_effect=False,
        rollback="discard generated candidate",
        evidence_refs=("seed-evidence",),
        confidence=0.95,
        expected_verified_gain=gain,
        cost=0.5,
        risk=0.1,
    )


class FrontierLoopR2Tests(unittest.TestCase):
    def test_continues_from_residual_to_next_action(self):
        def propose(context):
            if context.step_index == 0:
                return (proposal("A1"),)
            if context.step_index == 1:
                return (proposal("A2"),)
            return ()

        def execute(selected, decision, context):
            self.assertTrue(decision.authority_granted)
            return ActionOutcome(
                action_id=selected.action_id,
                success=True,
                verified_gain=1.0,
                evidence_refs=(f"receipt-{selected.action_id}",),
                residuals=(f"residual-after-{selected.action_id}",),
            )

        receipt = run_frontier_loop(
            seed={"intent": "continue"},
            propose=propose,
            execute=execute,
        )
        self.assertEqual(receipt.status, "P0")
        self.assertEqual(len(receipt.steps), 2)
        self.assertEqual(
            receipt.context["completed_action_ids"],
            ("A1", "A2"),
        )

    def test_checkpoint_requires_resume_instead_of_claiming_completion(self):
        def propose(context):
            return (proposal(f"A{context.step_index}"),)

        def execute(selected, decision, context):
            return ActionOutcome(
                selected.action_id,
                True,
                1.0,
                (f"receipt-{selected.action_id}",),
                ("more-work",),
            )

        receipt = run_frontier_loop(
            seed={"intent": "frontier"},
            propose=propose,
            execute=execute,
            policy=FrontierPolicy(max_steps_per_checkpoint=3),
        )
        self.assertEqual(receipt.status, "CHECKPOINT")
        self.assertTrue(receipt.resume_required)
        self.assertEqual(len(receipt.steps), 3)

    def test_external_action_stops_at_authority_boundary(self):
        def propose(context):
            return (
                ActionProposal(
                    action_id="DEPLOY",
                    action_kind="external_deployment",
                    plan={"target": "production"},
                    reversible=True,
                    external_side_effect=True,
                    rollback="rollback",
                    evidence_refs=("ci",),
                    confidence=0.99,
                    expected_verified_gain=10,
                    cost=1,
                    risk=0.1,
                ),
            )

        def execute(*args):
            raise AssertionError("executor must not run beyond authority boundary")

        receipt = run_frontier_loop(
            seed={"intent": "deploy"},
            propose=propose,
            execute=execute,
        )
        self.assertEqual(receipt.status, "HOLD_AUTHORITY_BOUNDARY")
        self.assertEqual(receipt.stop_reason, "REQUIRE_AUTHORIZATION")

    def test_repeated_action_is_detected(self):
        def propose(context):
            return (proposal("SAME"),)

        def execute(selected, decision, context):
            return ActionOutcome(
                "SAME",
                True,
                1.0,
                (f"receipt-{context.step_index}",),
                ("still-open",),
            )

        receipt = run_frontier_loop(
            seed={"intent": "repeat"},
            propose=propose,
            execute=execute,
            policy=FrontierPolicy(max_same_action_repeats=2, max_steps_per_checkpoint=8),
        )
        self.assertEqual(receipt.status, "HOLD_REPEAT_LOOP")

    def test_stagnation_converges_to_p0(self):
        def propose(context):
            return (proposal(f"A{context.step_index}"),)

        def execute(selected, decision, context):
            return ActionOutcome(
                selected.action_id,
                True,
                0.0,
                (f"receipt-{selected.action_id}",),
                ("low-value-residual",),
            )

        receipt = run_frontier_loop(
            seed={"intent": "stagnation"},
            propose=propose,
            execute=execute,
            policy=FrontierPolicy(max_stagnant_steps=2),
        )
        self.assertEqual(receipt.status, "P0")
        self.assertIn("no further verified gain", receipt.stop_reason)


if __name__ == "__main__":
    unittest.main()
