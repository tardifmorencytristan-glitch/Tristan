import unittest

from tristan.autonomous_decision import ActionProposal, decide_action, select_autonomous_action


class AutonomousDecisionTests(unittest.TestCase):
    def test_reversible_internal_action_gets_authorized_lease(self):
        proposal = ActionProposal(
            action_id="A1",
            action_kind="run_internal_test",
            plan={"cmd": "python -m unittest"},
            reversible=True,
            external_side_effect=False,
            rollback="discard generated artifacts",
            evidence_refs=("ci-green",),
            confidence=0.95,
            expected_verified_gain=5,
            cost=1,
            risk=0.2,
        )
        decision = decide_action(proposal)
        self.assertEqual(decision.decision, "EXECUTE_AUTONOMOUSLY")
        self.assertTrue(decision.authority_granted)
        self.assertTrue(decision.execution_lease["authorized"])
        self.assertTrue(decision.execution_lease["reversible_only"])

    def test_external_action_requires_authorization(self):
        proposal = ActionProposal(
            action_id="A2",
            action_kind="external_deployment",
            plan={"target": "production"},
            reversible=True,
            external_side_effect=True,
            rollback="rollback deploy",
            evidence_refs=("ci-green",),
            confidence=0.99,
            expected_verified_gain=10,
            cost=1,
            risk=0.1,
        )
        decision = decide_action(proposal)
        self.assertEqual(decision.decision, "REQUIRE_AUTHORIZATION")
        self.assertFalse(decision.authority_granted)

    def test_scientific_promotion_requires_authorization(self):
        proposal = ActionProposal(
            action_id="A3",
            action_kind="scientific_promotion",
            plan={"claim": "C1", "target": "CERTIFIED_PHYSICS"},
            reversible=True,
            external_side_effect=False,
            rollback="restore prior OAK status",
            evidence_refs=("replication-1",),
            confidence=1.0,
            expected_verified_gain=9,
            cost=1,
            risk=0.1,
        )
        self.assertEqual(decide_action(proposal).decision, "REQUIRE_AUTHORIZATION")

    def test_low_confidence_holds(self):
        proposal = ActionProposal(
            action_id="A4",
            action_kind="run_internal_test",
            plan={"cmd": "test"},
            reversible=True,
            external_side_effect=False,
            rollback="discard",
            evidence_refs=("receipt",),
            confidence=0.5,
            expected_verified_gain=3,
            cost=1,
            risk=0,
        )
        self.assertEqual(decide_action(proposal).decision, "HOLD_LOW_CONFIDENCE")

    def test_selector_prefers_highest_utility_executable(self):
        p1 = ActionProposal("A1", "internal_refactor", {"x": 1}, True, False, "revert", ("e1",), 0.9, 4, 1, 0)
        p2 = ActionProposal("A2", "internal_refactor", {"x": 2}, True, False, "revert", ("e2",), 0.9, 6, 1, 0)
        decision = select_autonomous_action((p1, p2))
        self.assertEqual(decision.action_id, "A2")
        self.assertEqual(decision.decision, "EXECUTE_AUTONOMOUSLY")


if __name__ == "__main__":
    unittest.main()
