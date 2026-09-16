import unittest
from pathlib import Path

from tristan.context import compile_context
from tristan.model import TristanObject
from tristan.pipeline import run_intent, stable_receipt_bytes
from tristan.registry import Registry
from tristan.verify import verify_repository


ROOT = Path(__file__).resolve().parents[1]


class KernelTests(unittest.TestCase):
    def test_registry_loads_and_ids_are_unique(self):
        reg = Registry.load(ROOT / "registry/objects.jsonl")
        self.assertGreaterEqual(len(reg.all()), 4)
        self.assertEqual(len(reg.all()), len({o.id for o in reg.all()}))

    def test_context_is_deterministic(self):
        reg = Registry.load(ROOT / "registry/objects.jsonl")
        a = compile_context("context registry evidence", reg)
        b = compile_context("context registry evidence", reg)
        self.assertEqual(a, b)
        self.assertIn("context-registry-v0-4", a.selected_ids)

    def test_empty_query_selects_nothing(self):
        reg = Registry.load(ROOT / "registry/objects.jsonl")
        receipt = compile_context("", reg)
        self.assertEqual(receipt.selected_ids, ())

    def test_run_receipt_has_stable_semantic_bytes(self):
        reg = Registry.load(ROOT / "registry/objects.jsonl")
        a = run_intent("generalize and verify context", reg)
        b = run_intent("generalize and verify context", reg)
        self.assertEqual(stable_receipt_bytes(a), stable_receipt_bytes(b))
        self.assertEqual(a.intent_sha256, b.intent_sha256)

    def test_right_to_lose_is_data_not_authority(self):
        reg = Registry.load(ROOT / "registry/objects.jsonl")
        obj = reg.require("omega-one-skill-tristan-r1")
        self.assertTrue(obj.metadata["right_to_lose"])
        self.assertFalse(obj.authority["scientific"])

    def test_invalid_status_rejected(self):
        payload = {
            "id": "x", "kind": "test", "title": "x", "status": "MAGIC", "summary": "x"
        }
        with self.assertRaises(ValueError):
            TristanObject.from_dict(payload)

    def test_repo_verifier_passes(self):
        result = verify_repository(ROOT)
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["context_debt_clean"])
        self.assertFalse(result["scientific_pass"])


if __name__ == "__main__":
    unittest.main()
