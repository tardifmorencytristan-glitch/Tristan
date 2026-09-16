import unittest
from omega_scientific_writing.src.report_ir import (
    ReportMeta, ObjectiveIR, MethodIR, ResultIR, ConclusionIR, ReportGraphIR,
)
from omega_scientific_writing.src.report_court import evaluate_report


class R5AReportCourtTests(unittest.TestCase):
    def test_clean_bounded_packet_passes_r5a_structure(self):
        doc = {
            "claims": [{
                "id": "CL1", "statement": "temperature remains below limit",
                "claim_type": "EMPIRICAL", "status": "MEASURED", "scope": "test A",
                "uncertainty": "+/-0.4 C", "evidence_ids": ["E1"],
                "obligations_satisfied": [
                    "measurement_or_experiment", "uncertainty", "sample_or_acquisition_protocol",
                    "controls_or_baseline", "limitations",
                ],
            }],
            "evidence": [{"id": "E1", "kind": "measurement"}],
            "equations": [], "figures": [], "citations": [],
            "results": [{"id": "R1", "evidence_ids": ["E1"]}],
        }
        graph = ReportGraphIR(
            project_id="P1",
            objectives=(ObjectiveIR(ReportMeta("O1"), "Verify thermal limit"),),
            methods=(MethodIR(
                ReportMeta("M1"), "Measure maximum temperature",
                input_ids=("D1",), steps=("measure", "compute maximum"),
                output_ids=("R1",), validation_methods=("calibration check",),
            ),),
            results=(ResultIR(ReportMeta("R1"), "42.1 +/- 0.4 C", evidence_ids=("E1",), objective_ids=("O1",)),),
            conclusions=(ConclusionIR(
                ReportMeta("C1"), "limit satisfied in test A",
                claim_ids=("CL1",), result_ids=("R1",), objective_ids=("O1",),
            ),),
        )
        out = evaluate_report(doc, graph)
        self.assertEqual(out["verdict"], "PASS")
        self.assertEqual(out["blocking_residuals"], [])

    def test_unsupported_conclusion_forces_hold(self):
        out = evaluate_report({}, ReportGraphIR(
            project_id="P1",
            conclusions=(ConclusionIR(ReportMeta("C1"), "unsupported"),),
        ))
        self.assertEqual(out["verdict"], "HOLD")
        self.assertTrue(any(f["code"] == "CONCLUSION_UNSUPPORTED" for f in out["findings"]))

    def test_repository_pass_does_not_emit_scientific_pass(self):
        out = evaluate_report({}, ReportGraphIR(project_id="P1"))
        self.assertNotEqual(out.get("scientific_status"), "ScientificPASS")
        self.assertIn("CompilationPASS != ScientificPASS", out["invariants"])


if __name__ == "__main__":
    unittest.main()
