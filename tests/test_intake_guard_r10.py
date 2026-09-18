import unittest

from tristan.intake_guard import (
    GroundedClaim,
    GroundedSource,
    IntakeRequest,
    audit_grounded_claims,
    compile_intake_plan,
)
from tristan.ultra_closure import DebtVector


SHA_A = "a" * 40
SHA_B = "b" * 40


class IntakeGuardR10Tests(unittest.TestCase):
    def test_exact_grounding_passes(self):
        receipt = audit_grounded_claims(
            (
                GroundedClaim(
                    "c1",
                    "bounded repository claim",
                    "ARCHITECTURE",
                    (
                        GroundedSource(
                            "owner/repo",
                            "src/x.py",
                            SHA_A,
                            "L1-L4",
                            "PUBLIC_SAFE",
                        ),
                    ),
                ),
            ),
            allowed_repositories=("owner/repo",),
            allowed_paths=("src/x.py",),
            exact_commits={"owner/repo": SHA_A},
            allowed_roles=("ARCHITECTURE",),
        )
        self.assertEqual(receipt.status, "PASS_GROUNDED")
        self.assertEqual(receipt.weighted_grounding_coverage, 1.0)
        self.assertFalse(receipt.authority_granted)

    def test_wrong_commit_fails_closed(self):
        receipt = audit_grounded_claims(
            (
                GroundedClaim(
                    "c1",
                    "claim",
                    "ARCHITECTURE",
                    (GroundedSource("owner/repo", "src/x.py", SHA_B, "L1"),),
                ),
            ),
            allowed_repositories=("owner/repo",),
            allowed_paths=("src/x.py",),
            exact_commits={"owner/repo": SHA_A},
            allowed_roles=("ARCHITECTURE",),
        )
        self.assertEqual(receipt.status, "HOLD_COMMIT_MISMATCH")
        self.assertIn("c1", receipt.commit_violation_claim_ids)

    def test_private_to_public_fails_closed(self):
        receipt = audit_grounded_claims(
            (
                GroundedClaim(
                    "c1",
                    "claim",
                    "ARCHITECTURE",
                    (
                        GroundedSource(
                            "owner/repo",
                            "src/x.py",
                            SHA_A,
                            "L1",
                            "PRIVATE",
                        ),
                    ),
                ),
            ),
            allowed_repositories=("owner/repo",),
            allowed_paths=("src/x.py",),
            exact_commits={"owner/repo": SHA_A},
            allowed_roles=("ARCHITECTURE",),
            target_visibility="PUBLIC_SAFE",
        )
        self.assertEqual(receipt.status, "HOLD_VISIBILITY")

    def test_problem_intake_compiles_to_mission_genome(self):
        request = IntakeRequest(
            request_id="p1",
            source="github",
            domain="code",
            title="fix failing test",
            body="reproducer",
        )
        plan = compile_intake_plan(
            request,
            context_ids=("repo-main",),
            residuals=("TEST_GAP",),
            debt=DebtVector(evidence=1.0),
        )
        self.assertEqual(plan.schema_version, "tristan-intake-guard-r10")
        self.assertEqual(plan.mission_genome["mission_id"], "INTAKE-p1")
        self.assertIn("unit_tests", plan.verification_contract)
        self.assertFalse(plan.publication_allowed)
        self.assertIn("REPOSITORY_RULES_NOT_YET_VERIFIED", plan.publication_blockers)

    def test_publication_request_never_self_authorizes(self):
        request = IntakeRequest(
            request_id="p2",
            source="github",
            domain="engineering",
            title="external contribution",
            body="proposal",
            requested_publication=True,
        )
        plan = compile_intake_plan(request, context_ids=("repo-main",))
        self.assertEqual(plan.status, "HOLD")
        self.assertIn("PUBLICATION_REQUIRES_EXPLICIT_AUTHORITY", plan.publication_blockers)
        self.assertFalse(plan.authority_granted)


if __name__ == "__main__":
    unittest.main()
