import json
import unittest
from pathlib import Path

from omega_scientific_writing.src.exact_evidence import evidence_from_exact_commit, may_promote_snapshot_evidence


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "benchmarks" / "r3_exact_evidence_pilot.json"


class R3ExactEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = json.loads(PILOT.read_text(encoding="utf-8"))["records"]

    def test_exact_records_materialize_provenance(self):
        evidence = [evidence_from_exact_commit(r) for r in self.records]
        self.assertEqual({e["id"] for e in evidence}, {"EXACT-D2", "EXACT-D5"})
        self.assertTrue(all(e["exact_commit_read"] for e in evidence))
        self.assertTrue(all(e["provenance"].startswith("github:") for e in evidence))

    def test_exact_commit_read_does_not_auto_promote(self):
        self.assertFalse(may_promote_snapshot_evidence(self.records[0]))
        self.assertFalse(may_promote_snapshot_evidence(self.records[1]))

    def test_missing_exact_fields_fail_closed(self):
        with self.assertRaises(ValueError):
            evidence_from_exact_commit({"object_id": "D_BAD"})


if __name__ == "__main__":
    unittest.main()
