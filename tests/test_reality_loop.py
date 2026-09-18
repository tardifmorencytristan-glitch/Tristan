import unittest

from tristan.reality_loop import ExecutionLease, observe_reality, plan_digest


class RealityLoopTests(unittest.TestCase):
    def test_lease_fails_closed_without_authority(self):
        digest = plan_digest({"mission": "x"})
        lease = ExecutionLease(
            plan_digest=digest,
            executor_id="runner",
            allowed_actions=("simulate",),
            authorized=False,
        )
        self.assertTrue(
            lease.validate(plan_digest=digest, requested_actions=("simulate",))
        )

    def test_exact_lease_can_cover_reversible_action(self):
        digest = plan_digest({"mission": "x"})
        lease = ExecutionLease(
            plan_digest=digest,
            executor_id="runner",
            allowed_actions=("simulate",),
            authorized=True,
        )
        self.assertEqual(
            lease.validate(plan_digest=digest, requested_actions=("simulate",)),
            [],
        )

    def test_reality_gap(self):
        digest = plan_digest({"mission": "x"})
        receipt = observe_reality(
            plan_digest_value=digest,
            observer_id="independent-observer",
            success_criteria=("a", "b"),
            passed_criteria=("a",),
        )
        self.assertEqual(receipt.status, "RESIDUAL")
        self.assertEqual(receipt.reality_gap, 0.5)
        self.assertFalse(receipt.scientific_pass)
        self.assertFalse(receipt.authority_granted)


if __name__ == "__main__":
    unittest.main()
