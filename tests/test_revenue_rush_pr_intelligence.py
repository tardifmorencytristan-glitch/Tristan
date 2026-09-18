import importlib.util
import pathlib
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PATH = ROOT / "revenue_rush" / "pr_intelligence_service.py"

spec = importlib.util.spec_from_file_location("rush_pr", PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class RevenueRushPRIntelligenceTests(unittest.TestCase):
    def test_signature_verification(self):
        secret = "whsec_test"
        payload = b'{"id":"evt_1"}'
        ts = int(time.time())
        import hashlib, hmac
        sig = hmac.new(secret.encode(), str(ts).encode()+b"."+payload, hashlib.sha256).hexdigest()
        self.assertTrue(mod.verify_stripe_signature(payload, f"t={ts},v1={sig}", secret))
        self.assertFalse(mod.verify_stripe_signature(payload+b"x", f"t={ts},v1={sig}", secret))

    def test_build_report_flags_high_attention_surfaces(self):
        pr = {"html_url":"https://github.com/x/y/pull/1","title":"t","state":"open","draft":False,
              "base":{"ref":"main"},"head":{"ref":"feature"},"additions":900,"deletions":700,"changed_files":4}
        files = [
            {"filename":"src/auth/login.py","additions":400,"deletions":100},
            {"filename":"migrations/001.sql","additions":200,"deletions":0},
            {"filename":".github/workflows/ci.yml","additions":20,"deletions":10},
            {"filename":"requirements.txt","additions":2,"deletions":1},
        ]
        report = mod.build_report(pr, files)
        codes = {s["code"] for s in report["signals"]}
        self.assertIn("LARGE_CHANGESET", codes)
        self.assertIn("AUTH_OR_SECURITY_SURFACE_CHANGED", codes)
        self.assertIn("MIGRATION_SURFACE_CHANGED", codes)
        self.assertEqual(report["attention_band"], "HIGH")

    def test_pr_url_is_strict(self):
        self.assertIsNotNone(mod.PR_URL_RE.match("https://github.com/a/b/pull/12"))
        self.assertIsNone(mod.PR_URL_RE.match("https://example.com/a/b/pull/12"))

if __name__ == "__main__":
    unittest.main()
