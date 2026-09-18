import unittest
from omega_scientific_writing.src.report_ir import (
    ReportMeta, ObjectiveIR, ResultIR, ConclusionIR, ContradictionIR, ReportGraphIR,
)
from omega_scientific_writing.src.report_traceability import build_traceability_index, proof_cone, audit_traceability
from omega_scientific_writing.src.contradiction_court import audit_contradictions


class R5ATraceabilityContradictionTests(unittest.TestCase):
    def test_conclusion_proof_cone_reaches_result_and_claim(self):
        graph = ReportGraphIR(
            project_id="P1",
            objectives=(ObjectiveIR(ReportMeta("O1"), "Determine X"),),
            results=(ResultIR(ReportMeta("R1"), "X=2", evidence_ids=("E1",)),),
            conclusions=(ConclusionIR(ReportMeta("C1"), "X criterion met", claim_ids=("CL1",), result_ids=("R1",)),),
        )
        claims = [{"id": "CL1", "evidence_ids": ["E1"], "scope": "test A"}]
        index = build_traceability_index(graph, claims)
        cone = proof_cone("C1", index)
        self.assertIn("R1", cone["reachable_ids"])
        self.assertIn("CL1", cone["reachable_ids"])
        self.assertIn("E1", cone["reachable_ids"])

    def test_conclusion_without_support_holds(self):
        graph = ReportGraphIR(
            project_id="P1",
            conclusions=(ConclusionIR(ReportMeta("C1"), "unsupported"),),
        )
        codes = {f["code"] for f in audit_traceability(graph, [])}
        self.assertIn("CONCLUSION_UNSUPPORTED", codes)

    def test_unresolved_contradiction_holds(self):
        graph = ReportGraphIR(
            project_id="P1",
            contradictions=(ContradictionIR(
                ReportMeta("X1"), subject_ids=("CL1", "CL2"),
                conflict_type="STATEMENT", description="same scope conflict",
            ),),
        )
        findings = audit_contradictions(graph)
        self.assertTrue(any(f["code"] == "CONTRADICTION_UNRESOLVED" and f["severity"] == "HOLD" for f in findings))


if __name__ == "__main__":
    unittest.main()
