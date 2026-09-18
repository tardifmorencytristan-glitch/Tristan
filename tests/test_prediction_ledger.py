import unittest

from tristan.prediction_ledger import PredictionLedger


class PredictionLedgerTests(unittest.TestCase):
    def test_chain_verifies(self):
        ledger = PredictionLedger()
        a = ledger.freeze(
            "C1",
            "prediction one",
            ("observable-a",),
            created_at="2026-09-18T00:00:00+00:00",
        )
        b = ledger.freeze(
            "C2",
            "prediction two",
            ("observable-b",),
            created_at="2026-09-18T00:00:01+00:00",
        )
        self.assertEqual(a.previous_hash, "GENESIS")
        self.assertEqual(b.previous_hash, a.record_hash)
        self.assertTrue(ledger.verify())

    def test_requires_scope(self):
        ledger = PredictionLedger()
        with self.assertRaises(ValueError):
            ledger.freeze("C1", "prediction", ())


if __name__ == "__main__":
    unittest.main()
