import datetime as dt
import json
import pathlib
import sys
import tempfile
import unittest

SRC = pathlib.Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from capability_auction_r201 import compile_auction as compile_r201
from capability_auction_r203 import compile_auction as compile_r203
from capability_pipeline_r202 import compile_pipeline, execute_pipeline
from effect_verifier_r204 import (
    verify_external_outcome,
    verify_local_effect,
    verify_peer_quorum,
)


class MissionTruthRuntimeCrystalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(self.tmp.name)
        self.capabilities = root / "fleet-capabilities.json"
        self.resources = root / "fleet-resources.json"
        self.now = dt.datetime(2026, 9, 29, 1, 30, 0, tzinfo=dt.timezone.utc)

        self.capabilities.write_text(
            json.dumps(
                {
                    "nodes": [
                        {"node": "DESKTOP-SHA9IHL", "python_version": "3.13.15", "node_version": "24.0.0"},
                        {"node": "DESKTOP-2G1SSMT", "python_version": "3.13.15", "node_version": "24.0.0"},
                        {"node": "LAPTOP-AIU36QN6", "python_version": "3.8.5", "node_version": "20.0.0"},
                    ]
                }
            ),
            encoding="utf-8",
        )
        self.resources.write_text(
            json.dumps(
                {
                    "nodes": [
                        {
                            "node": "DESKTOP-SHA9IHL",
                            "available": True,
                            "observed_at": "2026-09-29T01:00:00+00:00",
                            "python_version": "3.13.15",
                            "node_version": "24.0.0",
                            "free_ram_gb": 20,
                            "disk_free_gb": 200,
                            "cpu_load_pct": 20,
                        },
                        {
                            "node": "DESKTOP-2G1SSMT",
                            "available": True,
                            "observed_at": "2026-09-29T01:00:00+00:00",
                            "python_version": "3.13.15",
                            "node_version": "24.0.0",
                            "free_ram_gb": 12,
                            "disk_free_gb": 120,
                            "cpu_load_pct": 30,
                        },
                        {
                            "node": "LAPTOP-AIU36QN6",
                            "available": True,
                            "observed_at": "2026-09-29T01:00:00+00:00",
                            "python_version": "3.8.5",
                            "node_version": "20.0.0",
                            "free_ram_gb": 6,
                            "disk_free_gb": 80,
                            "cpu_load_pct": 40,
                        },
                    ]
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def task(self, tid="x", **requires):
        return {
            "id": tid,
            "kind": "CRYSTAL_TEST",
            "target": "bounded-runtime",
            "action": "design_zero_spend_canary",
            "gate": "OAK rollback no_spend",
            "depends_on": [],
            "status": "READY",
            "priority": 1.0,
            "requires": requires,
        }

    def test_r201_holds_uncovered_requirement(self):
        out = compile_r201(
            [self.task("impossible", python_min="99.0")],
            fleet_path=self.capabilities,
        )
        self.assertEqual(out["status"], "HOLD_UNCOVERED_REQUIREMENTS")

    def test_r202_executes_bounded_compatible_task(self):
        compiled = compile_pipeline(
            "r202-crystal-test",
            [self.task("compatible", python_min="3.13")],
            fleet_path=self.capabilities,
        )
        self.assertEqual(compiled["status"], "READY")
        with tempfile.TemporaryDirectory() as tmp:
            out = execute_pipeline(compiled, pathlib.Path(tmp), max_tasks_per_node=2)
        self.assertEqual(out["status"], "PASS")
        self.assertEqual(out["selected"], 1)
        self.assertEqual(out["verified"], 1)
        self.assertFalse(out["authority_granted"])
        self.assertFalse(out["external_side_effects"])

    def test_r203_resource_auction_and_failover(self):
        tasks = [
            self.task(
                "general",
                python_min="3.13",
                min_free_ram_gb=10,
                max_cpu_load_pct=80,
            )
        ]
        normal = compile_r203(
            tasks,
            snapshot_path=self.resources,
            max_age_s=3600,
            now=self.now,
        )
        self.assertEqual(normal["status"], "PASS")
        self.assertEqual(normal["coalition"], ["DESKTOP-SHA9IHL"])
        failover = compile_r203(
            tasks,
            snapshot_path=self.resources,
            max_age_s=3600,
            now=self.now,
            exclude_nodes=("DESKTOP-SHA9IHL",),
        )
        self.assertEqual(failover["status"], "PASS")
        self.assertEqual(failover["coalition"], ["DESKTOP-2G1SSMT"])

    def test_r203_stale_snapshot_holds(self):
        tasks = [self.task("general", python_min="3.13")]
        now = dt.datetime(2026, 9, 29, 2, 0, 0, tzinfo=dt.timezone.utc)
        out = compile_r203(
            tasks,
            snapshot_path=self.resources,
            max_age_s=1,
            now=now,
        )
        self.assertEqual(out["status"], "HOLD_UNCOVERED_OR_STALE_REQUIREMENTS")

    def test_r204_separates_execution_effect_and_outcome(self):
        receipt = {
            "mission_id": "m",
            "execution_status": "VERIFIED",
            "artifact_sha256": "abc",
            "authority_granted": False,
            "external_side_effects": False,
            "money_spent": 0,
            "public_publish": False,
        }
        local = verify_local_effect(receipt, "abc")
        self.assertTrue(local["local_effect_verified"])
        self.assertFalse(local["mission_outcome_verified"])
        peers = [
            {
                "verifier_node": "a",
                "status": "INDEPENDENT_INTEGRITY_PASS",
                "receipt_digest_match": True,
                "artifact_hash_match": True,
                "boundary_ok": True,
            },
            {
                "verifier_node": "b",
                "status": "INDEPENDENT_INTEGRITY_PASS",
                "receipt_digest_match": True,
                "artifact_hash_match": True,
                "boundary_ok": True,
            },
        ]
        quorum = verify_peer_quorum(peers, 2)
        self.assertEqual(quorum["status"], "INTEGRITY_QUORUM_VERIFIED")
        external = verify_external_outcome(local, [])
        self.assertEqual(external["status"], "HOLD_EXTERNAL_OUTCOME_EVIDENCE")


if __name__ == "__main__":
    unittest.main()
