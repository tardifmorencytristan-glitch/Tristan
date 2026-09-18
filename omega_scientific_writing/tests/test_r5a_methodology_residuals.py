import unittest
from omega_scientific_writing.src.report_ir import ReportMeta, MethodIR, ObjectiveIR, ReportGraphIR
from omega_scientific_writing.src.methodology_court import audit_method
from omega_scientific_writing.src.residual_engine import derive_residuals, blocking_residuals


class R5AMethodologyResidualTests(unittest.TestCase):
    def test_method_without_validation_is_non_reproducible_residual(self):
        method = MethodIR(
            meta=ReportMeta("M1"), objective="Measure X",
            input_ids=("D1",), steps=("measure X",), output_ids=("R1",),
            validation_methods=(),
        )
        codes = {f["code"] for f in audit_method(method)}
        self.assertIn("METHOD_VALIDATION_MISSING", codes)

    def test_unanswered_objective_becomes_critical_residual(self):
        graph = ReportGraphIR(
            project_id="P1",
            objectives=(ObjectiveIR(ReportMeta("O1"), "Determine X"),),
        )
        residuals = derive_residuals(graph)
        types = {r.residual_type for r in residuals}
        self.assertIn("UNANSWERED_OBJECTIVE", types)
        self.assertEqual(len(blocking_residuals(residuals)), 1)


if __name__ == "__main__":
    unittest.main()
