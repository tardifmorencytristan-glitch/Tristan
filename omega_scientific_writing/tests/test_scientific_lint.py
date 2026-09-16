import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scientific_lint import lint


class ScientificLintTests(unittest.TestCase):
    def load(self, name):
        return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))

    def test_valid_fixture_has_no_errors(self):
        findings = lint(self.load("minimal_valid.json"))
        errors = [f for f in findings if f["severity"] == "ERROR"]
        self.assertEqual(errors, [])

    def test_invalid_fixture_is_rejected(self):
        findings = lint(self.load("minimal_invalid.json"))
        codes = {f["code"] for f in findings}
        expected = {
            "CLAIM_MISSING_EVIDENCE",
            "CLAIM_MISSING_CITATION_OBJECT",
            "CLAIM_SCOPE_MISSING",
            "CLAIM_UNCERTAINTY_MISSING",
            "SYMBOL_COLLISION",
            "FIGURE_UNKNOWN_CLAIM",
            "RESULT_MISSING_EVIDENCE",
        }
        self.assertTrue(expected.issubset(codes))


if __name__ == "__main__":
    unittest.main()
