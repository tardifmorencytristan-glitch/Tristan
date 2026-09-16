import unittest

from omega_omni_compiler.src.domain_ir import CodeIR, GitIR, DocumentIR, SpecIR, validate_domain_ir
from omega_omni_compiler.src.domain_adapters import spec_to_code, code_to_git, git_to_document, document_to_artifact, artifact_to_document
from omega_omni_compiler.src.receipts import receipt_from_transition


class OmniR1DomainTests(unittest.TestCase):
    def test_domain_ir_validation(self):
        spec = SpecIR(id="S1", title="Demo", constraints=[], provenance="fixture")
        self.assertEqual(validate_domain_ir(spec), [])
        self.assertTrue(validate_domain_ir(SpecIR(id="", title="", provenance="")))

    def test_spec_code_git_document_artifact_roundtrip(self):
        spec = SpecIR(
            id="S1",
            title="Voltage spec",
            constraints=[{"name": "operating_voltage", "min": 3.0, "max": 3.6, "unit": "V"}],
            provenance="fixture:spec",
        )
        code = spec_to_code(spec)
        git = code_to_git(code, "owner/repo", "feat/spec", "abc123")
        doc = git_to_document(git, code)
        art = document_to_artifact(doc)
        reconstructed = artifact_to_document(art, doc)

        self.assertEqual(code.invariants, ["operating_voltage"])
        self.assertEqual(git.head_sha, "abc123")
        self.assertEqual(doc.sections, reconstructed.sections)
        self.assertEqual(doc.title, reconstructed.title)
        self.assertEqual(art["status"], "CANDIDATE_NOT_RENDERED")

    def test_receipt_digest_is_deterministic(self):
        r1 = receipt_from_transition("SPEC_TO_CODE", [{"id": "S1"}], [{"id": "C1"}], preserved=["constraints"], losses=[])
        r2 = receipt_from_transition("SPEC_TO_CODE", [{"id": "S1"}], [{"id": "C1"}], preserved=["constraints"], losses=[])
        self.assertEqual(r1.digest(), r2.digest())


if __name__ == "__main__":
    unittest.main()
