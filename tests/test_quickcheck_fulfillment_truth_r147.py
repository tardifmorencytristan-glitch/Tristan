import unittest
from pathlib import Path

PAGE = (Path(__file__).resolve().parents[1] / "quickcheck-after-purchase.html")

class QuickCheckFulfillmentTruthR147(unittest.TestCase):
    def test_no_unverified_automatic_fulfillment_promise(self):
        html = PAGE.read_text(encoding="utf-8")
        self.assertIn("server-side verification", html)
        self.assertIn("does not confirm that an automated Jarvis dispatch", html)
        self.assertNotIn("No additional intake step is required.", html)
        self.assertNotIn("Jarvis fulfills only after Stripe reports", html)

    def test_payment_is_not_delivery(self):
        html = PAGE.read_text(encoding="utf-8")
        self.assertIn("payment alone is not delivery", html)
        self.assertIn("independently recorded delivery receipt", html)
        self.assertIn('name="robots" content="noindex,nofollow"', html)

if __name__ == "__main__":
    unittest.main()
