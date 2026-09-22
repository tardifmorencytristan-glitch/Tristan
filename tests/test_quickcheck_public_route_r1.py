import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts" / "QUICKCHECK_PUBLIC_ROUTE_R1_20260922.json"
README = ROOT / "README.md"
PAGE = ROOT / "quickcheck.html"

class QuickCheckPublicRouteR1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = json.loads(RECEIPT.read_text(encoding="utf-8"))
        cls.readme = README.read_text(encoding="utf-8")
        cls.page = PAGE.read_text(encoding="utf-8")

    def test_production_route_is_immutable_source_commit(self):
        self.assertIn(self.r["source_commit"], self.r["production_route"])
        self.assertIn(self.r["production_route"], self.readme)
        self.assertNotIn("/main/quickcheck.html", self.r["production_route"])

    def test_existing_checkout_identity_is_preserved(self):
        stripe = self.r["stripe"]
        self.assertTrue(stripe["active"])
        self.assertEqual(stripe["unit_amount"], 500)
        self.assertEqual(stripe["currency"], "cad")
        self.assertEqual(stripe["type"], "one_time")
        self.assertIn(stripe["url"], self.page)
        self.assertEqual(stripe["completed_session_limit"], 1)

    def test_route_readback_and_payment_truth_are_separate(self):
        ext = self.r["external_readback"]
        truth = self.r["live_payment_truth"]
        self.assertEqual(ext["production_http_status"], 200)
        self.assertTrue(ext["contains_quickcheck"])
        self.assertTrue(ext["contains_first_customer_checkout"])
        self.assertEqual(truth["paid_quickcheck_sessions"], 0)
        self.assertEqual(truth["payment_intents_account_total"], 0)
        self.assertEqual(
            self.r["decision"],
            "USE_EXISTING_IMMUTABLE_RAWCDN_ROUTE_NO_NEW_DEPLOYMENT",
        )

if __name__ == "__main__":
    unittest.main()
