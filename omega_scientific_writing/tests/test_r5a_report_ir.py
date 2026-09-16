import unittest

from omega_scientific_writing.src.report_ir import (
    ReportMeta, ObjectiveIR, RequirementIR, MethodIR, ResultIR,
    ConclusionIR, ReportGraphIR, validate_report_graph, report_graph_to_dict,
)


class R5AReportIRTests(unittest.TestCase):
    def test_valid_graph_serializes_deterministically(self):
        graph = ReportGraphIR(
            project_id="P1",
            objectives=(ObjectiveIR(ReportMeta("O1"), "Measure thermal compliance"),),
            requirements=(RequirementIR(ReportMeta("RQ1"), "Tmax < 45 C", "max_temperature_c < 45"),),
            methods=(MethodIR(
                meta=ReportMeta("M1"),
                objective="Measure maximum temperature",
                input_ids=("D1",),
                steps=("acquire temperature", "compute maximum"),
                output_ids=("R1",),
                validation_methods=("sensor calibration check",),
            ),),
            results=(ResultIR(ReportMeta("R1"), "Tmax = 42.1 C", evidence_ids=("E1",)),),
            conclusions=(ConclusionIR(
                ReportMeta("C1"),
                "Thermal requirement is satisfied in the stated test scope",
                claim_ids=("CL1",), result_ids=("R1",), requirement_ids=("RQ1",),
            ),),
        )
        self.assertEqual(validate_report_graph(graph), [])
        first = report_graph_to_dict(graph)
        second = report_graph_to_dict(graph)
        self.assertEqual(first, second)
        self.assertEqual(first["project_id"], "P1")

    def test_duplicate_ids_are_rejected(self):
        graph = ReportGraphIR(
            project_id="P1",
            objectives=(ObjectiveIR(ReportMeta("X"), "A"),),
            results=(ResultIR(ReportMeta("X"), "B"),),
        )
        codes = {f["code"] for f in validate_report_graph(graph)}
        self.assertIn("REPORT_DUPLICATE_OBJECT_ID", codes)

    def test_unknown_status_is_rejected(self):
        graph = ReportGraphIR(
            project_id="P1",
            objectives=(ObjectiveIR(ReportMeta("O1", status="MAGIC"), "A"),),
        )
        codes = {f["code"] for f in validate_report_graph(graph)}
        self.assertIn("REPORT_STATUS_UNKNOWN", codes)


if __name__ == "__main__":
    unittest.main()
