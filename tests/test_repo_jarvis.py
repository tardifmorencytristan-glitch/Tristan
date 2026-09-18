import unittest
from pathlib import Path

from tristan.repo_jarvis import (
    LOCAL_REPOSITORY,
    ROOT_REPOSITORY,
    PublicSafeClaim,
    PublicSafeSource,
    audit_public_safe_draft,
    load_profile,
)


ROOT = Path(__file__).resolve().parents[1]


class PublicSafeRepoJarvisTests(unittest.TestCase):
    def test_profile_is_public_safe_only(self):
        profile = load_profile(ROOT)
        self.assertEqual(profile["target_visibility"], "PUBLIC_SAFE")
        self.assertEqual(profile["root_access_mode"], "PUBLIC_SAFE_PROJECTION_ONLY")
        self.assertFalse(profile["authority_granted"])

    def test_root_and_local_sources_can_ground_public_output(self):
        receipt = audit_public_safe_draft(
            (
                PublicSafeClaim(
                    "root",
                    "Rooted public claim",
                    (PublicSafeSource(ROOT_REPOSITORY, "public/projection.json", "a" * 40, "claim:1"),),
                ),
                PublicSafeClaim(
                    "local",
                    "Local claim",
                    (PublicSafeSource(LOCAL_REPOSITORY, "README.md", "b" * 40, "README#architecture"),),
                ),
            )
        )
        self.assertEqual(receipt.status, "PASS_GROUNDED")
        self.assertEqual(receipt.weighted_grounding_coverage, 1.0)
        self.assertFalse(receipt.authority_granted)
        self.assertFalse(receipt.scientific_pass)

    def test_private_root_material_is_blocked(self):
        receipt = audit_public_safe_draft(
            (
                PublicSafeClaim(
                    "private",
                    "Must not leak",
                    (
                        PublicSafeSource(
                            ROOT_REPOSITORY,
                            "private/secret.md",
                            "a" * 40,
                            "private",
                            visibility="PRIVATE",
                        ),
                    ),
                ),
            )
        )
        self.assertEqual(receipt.status, "HOLD_VISIBILITY")

    def test_unsourced_claim_is_blocked(self):
        receipt = audit_public_safe_draft((PublicSafeClaim("x", "unsupported", ()),))
        self.assertEqual(receipt.status, "HOLD_UNSOURCED")


if __name__ == "__main__":
    unittest.main()
