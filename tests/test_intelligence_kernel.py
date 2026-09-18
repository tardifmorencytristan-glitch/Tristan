import unittest

from tristan.intelligence_kernel import compile_intelligence_mission
from tristan.jarvis_ir import ClaimIR
from tristan.model_tournament import ModelCandidate, ModelScore, compare_models
from tristan.prediction_ledger import PredictionLedger


class IntelligenceKernelTests(unittest.TestCase):
    def test_claim_compiles_to_frozen_adversarial_mission(self):
        ledger = PredictionLedger()
        claim = ClaimIR(
            claim_id="LC-FRACTAL-001",
            statement="Fractal LC topology differs from matched control",
            predicted_observables=("impedance-spectrum", "resonance-frequencies"),
            competing_models=("FRACTAL", "REGULAR"),
        )
        receipt = compile_intelligence_mission(
            claim,
            "Compare LC fractal circuits using scientific data and simulation",
            ledger,
        )
        self.assertEqual(receipt.status, "READY_FOR_ADVERSARIAL_EXECUTION")
        self.assertFalse(receipt.scientific_pass)
        self.assertFalse(receipt.authority_granted)
        self.assertTrue(receipt.prediction_record["record_hash"])
        self.assertEqual(
            receipt.claim["witness"],
            "prediction-ledger:" + receipt.prediction_record["record_hash"],
        )
        self.assertIn("FALSIFIER", receipt.adversarial_roles)
        self.assertTrue(ledger.verify())

    def test_missing_observable_holds(self):
        claim = ClaimIR(claim_id="C", statement="untestable claim")
        receipt = compile_intelligence_mission(claim, "cern", PredictionLedger())
        self.assertEqual(receipt.status, "HOLD")
        self.assertTrue(receipt.errors)
        self.assertEqual(receipt.prediction_record, {})

    def test_model_tournament_is_comparison_not_certification(self):
        receipt = compare_models(
            (
                ModelCandidate("NULL", "null", True),
                ModelCandidate("A", "candidate A"),
            ),
            (
                ModelScore("NULL", "rmse", 2.0),
                ModelScore("A", "rmse", 1.0),
            ),
            metric="rmse",
            direction="lower",
        )
        self.assertEqual(receipt.ordered_models, ("A", "NULL"))
        self.assertEqual(receipt.status, "COMPARISON_ONLY")
        self.assertFalse(receipt.scientific_pass)


if __name__ == "__main__":
    unittest.main()
