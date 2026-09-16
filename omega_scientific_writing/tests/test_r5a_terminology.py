import unittest
from omega_scientific_writing.src.report_ir import ReportMeta, ConceptTermIR
from omega_scientific_writing.src.terminology_court import audit_terminology


class R5ATerminologyTests(unittest.TestCase):
    def setUp(self):
        self.concepts = (
            ConceptTermIR(
                ReportMeta("TERM1"),
                canonical_terms=(("fr", "débit volumique"), ("en", "volumetric flow rate")),
                aliases=("débit", "volume flow rate"),
                ambiguous_terms=("flux",),
                forbidden_substitutions=("flow",),
                definition="Volume transported per unit time",
                source_ids=("SRC1",),
            ),
        )

    def test_alias_is_detected_without_losing_canonical_identity(self):
        findings = audit_terminology(
            [{"object_id": "P1", "language": "fr", "term": "débit"}], self.concepts
        )
        self.assertTrue(any(f["code"] == "TERM_ALIAS_USED" for f in findings))
        self.assertFalse(any(f["severity"] == "ERROR" for f in findings))

    def test_ambiguous_term_holds(self):
        findings = audit_terminology(
            [{"object_id": "P2", "language": "fr", "term": "flux"}], self.concepts
        )
        self.assertTrue(any(f["code"] == "TERM_AMBIGUOUS" and f["severity"] == "HOLD" for f in findings))

    def test_unknown_ai_term_is_not_auto_accepted(self):
        findings = audit_terminology(
            [{"object_id": "P3", "language": "fr", "term": "hyperflux", "origin": "ai_generated"}], self.concepts
        )
        self.assertTrue(any(f["code"] == "AI_TERM_UNREGISTERED" for f in findings))


if __name__ == "__main__":
    unittest.main()
