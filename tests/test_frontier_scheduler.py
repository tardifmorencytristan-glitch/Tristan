import unittest

from tristan.frontier_loop import FrontierReceipt
from tristan.frontier_scheduler import next_continuation_directive


def receipt(status, resume_required=False):
    return FrontierReceipt(
        schema_version="tristan-frontier-loop-r2",
        status=status,
        stop_reason=status,
        context={"seed": {"intent": "x"}},
        steps=(),
        resume_required=resume_required,
        authority_granted=False,
        scientific_pass=False,
        boundaries=(),
    )


class FrontierSchedulerTests(unittest.TestCase):
    def test_checkpoint_resumes_immediately(self):
        d = next_continuation_directive(receipt("CHECKPOINT", True))
        self.assertEqual(d.mode, "RESUME_FRONTIER")
        self.assertEqual(d.wake_condition, "immediate")
        self.assertTrue(d.autonomous)

    def test_p0_becomes_dormant_scan_not_termination(self):
        d = next_continuation_directive(receipt("P0"))
        self.assertEqual(d.mode, "DORMANT_SCAN")
        self.assertIn("new evidence", d.wake_condition)
        self.assertTrue(d.preserve_context)

    def test_repeat_forces_diversification(self):
        d = next_continuation_directive(receipt("HOLD_REPEAT_LOOP"))
        self.assertEqual(d.mode, "DIVERSIFY_SEARCH")

    def test_failure_routes_to_failure_analysis(self):
        d = next_continuation_directive(receipt("HOLD_EXECUTION_FAILURE"))
        self.assertEqual(d.mode, "FAILURE_ANALYSIS")

    def test_authority_boundary_searches_for_safe_alternative(self):
        d = next_continuation_directive(receipt("HOLD_AUTHORITY_BOUNDARY"))
        self.assertEqual(d.mode, "SEARCH_WITHIN_AUTHORITY")
        self.assertIn("authorization", d.wake_condition)


if __name__ == "__main__":
    unittest.main()
