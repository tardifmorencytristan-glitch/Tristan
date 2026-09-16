import unittest

from omega_omni_compiler.src.artifact_graph import ArtifactIdentity, ArtifactNode, ArtifactGraph, canonical_hash
from omega_omni_compiler.src.invalidation import affected_closure, invalidate
from omega_omni_compiler.src.receipts import receipt_from_transition
from omega_omni_compiler.src.github_state import gitir_from_branch_payload, attach_check_runs, exact_head_checks_pass


class OmniR2Tests(unittest.TestCase):
    def test_artifact_lineage_and_invalidation(self):
        g = ArtifactGraph()
        spec_hash = canonical_hash({"voltage": [3.0, 3.6]})
        spec = ArtifactNode(ArtifactIdentity("A-spec", "SPEC", "fixture", content_hash=spec_hash))
        code = ArtifactNode(ArtifactIdentity("A-code", "CODE", "generated", content_hash=canonical_hash({"code": "x"})), parent_ids=["A-spec"])
        doc = ArtifactNode(ArtifactIdentity("A-doc", "DOCUMENT", "generated", content_hash=canonical_hash({"doc": "x"})), parent_ids=["A-code"])
        for node in (spec, code, doc):
            g.add(node)
        self.assertEqual(g.descendants("A-spec"), ["A-code", "A-doc"])
        self.assertEqual(g.lineage("A-doc"), ["A-code", "A-spec"])
        self.assertEqual(affected_closure(g, "A-spec"), ["A-spec", "A-code", "A-doc"])
        receipt = invalidate(g, "A-spec", "spec changed")
        self.assertEqual(receipt.invalidated_ids, ["A-spec", "A-code", "A-doc"])

    def test_receipt_contains_input_output_hashes(self):
        r = receipt_from_transition(
            "SPEC_TO_CODE",
            [{"id": "S1", "constraint": "3.0<=V<=3.6"}],
            [{"id": "C1", "test": "boundary"}],
            preserved=["constraint"],
            verifier="fixture",
            operator_version="r2",
            authority="sandbox",
            cost=1,
            risk=0.1,
        )
        self.assertEqual(r.validate(), [])
        self.assertEqual(len(r.input_hashes[0]), 64)
        self.assertEqual(len(r.output_hashes[0]), 64)
        self.assertEqual(r.digest(), r.digest())

    def test_exact_github_state_requires_same_head_success(self):
        branch = {"name": "main", "commit": {"sha": "abc123"}}
        git = gitir_from_branch_payload("owner/repo", branch, "github:branch-api")
        attach_check_runs(git, {"check_runs": [
            {"name": "ci", "head_sha": "abc123", "status": "completed", "conclusion": "success"},
            {"name": "stale", "head_sha": "old", "status": "completed", "conclusion": "success"},
        ]})
        self.assertTrue(exact_head_checks_pass(git))
        git.checks[0]["conclusion"] = "failure"
        self.assertFalse(exact_head_checks_pass(git))

    def test_empty_checks_are_not_pass(self):
        git = gitir_from_branch_payload("owner/repo", {"name": "main", "commit": {"sha": "abc123"}}, "fixture")
        self.assertFalse(exact_head_checks_pass(git))


if __name__ == "__main__":
    unittest.main()
