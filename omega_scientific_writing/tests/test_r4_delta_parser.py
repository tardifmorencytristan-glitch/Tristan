import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).parents[1] / "src" / "r4_delta_parser.py"
spec = importlib.util.spec_from_file_location("r4_delta_parser", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


class R4DeltaParserTests(unittest.TestCase):
    def test_extracts_bounded_delta_block(self):
        text = """D5 - Eigen-Becherel R0.2
Commit exact : 3443b6211538cf62aae9f6a1b5b6b1226fa449a0
Statut : MERGED / validated software scaffold
Delta : Adds benchmark and semantic receipts.
Preuve bornée : Integrated suite 111/111 on declared environment.
Frontière OAK : Mathematical novelty and universal optimality remain unverified.
3. Corrections et supersessions de R3
"""
        parsed = mod.parse_delta(text)
        self.assertEqual(len(parsed["items"]), 1)
        item = parsed["items"][0]
        self.assertEqual(item["id"], "D5")
        self.assertEqual(item["commit"], "3443b6211538cf62aae9f6a1b5b6b1226fa449a0")
        self.assertIn("111/111", item["bounded_evidence"])
        self.assertIn("unverified", item["oak_boundary"])

    def test_rejects_unstructured_text_by_returning_no_items(self):
        self.assertEqual(mod.parse_delta("no structured delta here")["items"], [])


if __name__ == "__main__":
    unittest.main()
