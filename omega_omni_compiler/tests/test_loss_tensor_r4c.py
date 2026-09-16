import unittest

from omega_omni_compiler.src.loss_ledger import LossEntry
from omega_omni_compiler.src.loss_tensor import LossObservation, LossTensor


class LossTensorR4CTests(unittest.TestCase):
    def test_multidimensional_loss_is_transform_attributed(self):
        tensor = LossTensor()
        tensor.add(LossObservation("pdf_to_doc", "eq:1", "EQUATION", "LOST", severity=0.9, recoverability=0.2, cause="parser omitted exponent"))
        tensor.add(LossObservation("pdf_to_doc", "layout:1", "LAYOUT", "LOST", severity=0.2, recoverability=0.9, intentional=True, cause="semantic-only projection"))
        self.assertEqual(len(tensor.by_transform("pdf_to_doc")), 2)
        self.assertEqual(len(tensor.by_dimension("EQUATION")), 1)
        summary = tensor.summary()
        self.assertEqual(summary["by_dimension"]["EQUATION"]["LOST"], 1)
        self.assertEqual(summary["intentional_count"], 1)
        self.assertGreater(summary["total_residual_weight"], 0)

    def test_preserved_requires_zero_severity(self):
        entry = LossObservation("t", "x", "SEMANTIC", "PRESERVED", severity=0.1)
        self.assertTrue(any("zero severity" in e for e in entry.validate()))

    def test_invalid_dimension_and_ranges_fail_closed(self):
        entry = LossObservation("t", "x", "MAGIC", "LOST", severity=2.0, recoverability=-1.0)
        errors = entry.validate()
        self.assertTrue(any("dimension" in e for e in errors))
        self.assertTrue(any("severity" in e for e in errors))
        self.assertTrue(any("recoverability" in e for e in errors))

    def test_legacy_ledger_roundtrip_preserves_legacy_fields(self):
        legacy = [
            LossEntry("t1", "claim", "PRESERVED", "kept"),
            LossEntry("t1", "layout", "LOST", "dropped"),
            LossEntry("t2", "citation", "UNKNOWN", "not checked"),
        ]
        tensor = LossTensor.from_legacy(legacy, dimension="SEMANTIC", default_severity=0.8, default_recoverability=0.25)
        restored = tensor.to_legacy()
        self.assertEqual(restored, legacy)
        self.assertEqual(tensor.entries[0].severity, 0.0)
        self.assertEqual(tensor.entries[0].recoverability, 1.0)
        self.assertEqual(tensor.entries[1].severity, 0.8)
        self.assertEqual(tensor.entries[1].recoverability, 0.25)

    def test_intentional_loss_is_not_relabelled_preserved(self):
        entry = LossObservation("t", "font", "TYPOGRAPHY", "LOST", severity=0.1, recoverability=1.0, intentional=True)
        self.assertEqual(entry.validate(), [])
        self.assertEqual(entry.state, "LOST")
        self.assertTrue(entry.intentional)
        self.assertEqual(entry.residual_weight, 0.0)


if __name__ == "__main__":
    unittest.main()
