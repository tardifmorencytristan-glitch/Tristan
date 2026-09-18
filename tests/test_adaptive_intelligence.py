import unittest

from tristan.adaptive_router import CapabilityCandidate, select_minimal_coalition
from tristan.calibration import CalibrationSample, calibration_report
from tristan.causal_credit import AblationResult, assign_ablation_credit
from tristan.epistemic_memory import (
    EpistemicMemory,
    MemoryKind,
    MemoryRecord,
    delta_record,
)


class AdaptiveIntelligenceTests(unittest.TestCase):
    def test_epistemic_memory_is_context_bound(self):
        memory = EpistemicMemory()
        memory.append(
            MemoryRecord(
                record_id="m1",
                kind=MemoryKind.POSITIVE,
                context_tags=("physics", "lc"),
                mechanism="matched-control",
                outcome="reduced confounding",
                confidence=0.8,
                provenance=("receipt:1",),
            )
        )
        self.assertEqual(len(memory.query(("physics", "lc"))), 1)
        self.assertEqual(len(memory.query(("chemistry",))), 0)
        self.assertTrue(memory.unresolved_for(("chemistry",)))

    def test_delta_record(self):
        record = delta_record(
            record_id="d1",
            context_tags=("ai",),
            mechanism="router",
            before=0.5,
            after=0.7,
            metric="accuracy",
            provenance=("bench:1",),
        )
        self.assertEqual(record.kind, MemoryKind.DELTA)
        self.assertIn("+0.2", record.outcome)

    def test_router_selects_smallest_covering_coalition(self):
        candidates = (
            CapabilityCandidate("A", ("search",), 0.9, 0.1, 1.0, 5.0),
            CapabilityCandidate("B", ("code",), 0.9, 0.1, 1.0, 5.0),
            CapabilityCandidate("C", ("search", "code"), 0.7, 0.2, 3.0, 10.0),
        )
        receipt = select_minimal_coalition(("search", "code"), candidates)
        self.assertEqual(receipt.status, "COALITION_SELECTED")
        self.assertEqual(len(receipt.selected_candidates), 1)
        self.assertEqual(receipt.selected_candidates, ("C",))
        self.assertFalse(receipt.authority_granted)

    def test_router_holds_without_coverage(self):
        receipt = select_minimal_coalition(
            ("search", "code"),
            (CapabilityCandidate("A", ("search",), 0.9, 0.1, 1.0, 5.0),),
        )
        self.assertEqual(receipt.status, "HOLD_NO_CAPABILITY_COVERAGE")
        self.assertEqual(receipt.selected_candidates, ())

    def test_calibration_report(self):
        report = calibration_report(
            (
                CalibrationSample(0.9, True),
                CalibrationSample(0.8, True),
                CalibrationSample(0.7, False),
            )
        )
        self.assertEqual(report.sample_count, 3)
        self.assertGreaterEqual(report.brier_score, 0.0)
        self.assertGreaterEqual(report.calibration_gap, 0.0)

    def test_ablation_credit_is_not_causal_proof(self):
        receipt = assign_ablation_credit(
            (
                AblationResult("router", "score", 0.9, 0.5),
                AblationResult("memory", "score", 0.9, 0.8),
            )
        )
        self.assertEqual(receipt.ranked_components[0], "router")
        self.assertFalse(receipt.scientific_pass)
        self.assertEqual(receipt.status, "ABLATION_CREDIT_ONLY")


if __name__ == "__main__":
    unittest.main()
