import unittest

from tristan.portfolio_qualification import (
    PullRequestObservation,
    WorkflowObservation,
    qualify_portfolio,
    qualify_pr,
)


MAIN = "a" * 40
HEAD = "b" * 40


class PortfolioQualificationR11Tests(unittest.TestCase):
    def _pr(self, **overrides):
        data = dict(
            number=1,
            title="candidate",
            base_sha=MAIN,
            head_sha=HEAD,
            mergeable=True,
            draft=False,
            required_workflows=("kernel-ci",),
            workflows=(WorkflowObservation("kernel-ci", "completed", "success"),),
            blocking_review_threads=0,
        )
        data.update(overrides)
        return PullRequestObservation(**data)

    def test_exact_head_green_candidate_qualifies_without_granting_authority(self):
        receipt = qualify_pr(self._pr(), current_main_sha=MAIN)
        self.assertEqual(receipt.decision, "QUALIFIED_EXACT_HEAD")
        self.assertTrue(receipt.exact_head_qualified)
        self.assertFalse(receipt.merge_authority_granted)
        self.assertFalse(receipt.scientific_pass)

    def test_stale_base_fails_closed(self):
        receipt = qualify_pr(
            self._pr(base_sha="c" * 40),
            current_main_sha=MAIN,
        )
        self.assertEqual(receipt.decision, "HOLD_REPLAY_ON_CURRENT_MAIN")
        self.assertIn("STALE_BASE", receipt.blockers)

    def test_queued_required_workflow_fails_closed(self):
        receipt = qualify_pr(
            self._pr(
                workflows=(WorkflowObservation("kernel-ci", "queued", None),),
            ),
            current_main_sha=MAIN,
        )
        self.assertEqual(receipt.decision, "HOLD_CI")
        self.assertIn("WORKFLOW_NOT_GREEN:kernel-ci", receipt.blockers)

    def test_conflict_has_priority_over_stale_base(self):
        receipt = qualify_pr(
            self._pr(mergeable=False, base_sha="c" * 40),
            current_main_sha=MAIN,
        )
        self.assertEqual(receipt.decision, "HOLD_REBASE_OR_RESOLVE")
        self.assertIn("MERGE_CONFLICT", receipt.blockers)

    def test_portfolio_is_deterministic(self):
        receipts = qualify_portfolio(
            (
                self._pr(number=2, title="two"),
                self._pr(number=1, title="one", draft=True),
            ),
            current_main_sha=MAIN,
        )
        self.assertEqual({row.pr_number for row in receipts}, {1, 2})


if __name__ == "__main__":
    unittest.main()
