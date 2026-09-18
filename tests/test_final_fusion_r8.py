import unittest
from pathlib import Path

from tristan.final_fusion import (
    SourceObservation,
    apply_atlas_outcome,
    build_live_atlas_snapshot,
    compile_final_fusion,
    rank_atlas_missions,
)
from tristan.frontier_loop import ActionOutcome
from tristan.registry import Registry


ROOT = Path(__file__).resolve().parents[1]


class FinalFusionR8Tests(unittest.TestCase):
    def setUp(self):
        self.registry = Registry.load(ROOT / "registry/objects.jsonl")

    def test_intent_changes_ranking(self):
        atlas_obs = SourceObservation(
            source_id="drive-atlas-family",
            family="drive-atlas",
            kind="document-family",
            visibility="private-or-shared",
            observed_at="2026-09-18T16:40:00Z",
            materialized=False,
            exact_version_bound=False,
            duplicate_family_observed=True,
            tags=("atlas", "hgfm"),
            note="Atlas and HGFM materials",
        )
        tfuga_obs = SourceObservation(
            source_id="drive-tfuga-family",
            family="drive-tfuga",
            kind="document-family",
            visibility="private-or-shared",
            observed_at="2026-09-18T16:40:00Z",
            materialized=False,
            exact_version_bound=False,
            duplicate_family_observed=True,
            tags=("tfuga", "axiom"),
            note="TFUGA formalization material",
        )
        a = compile_final_fusion("improve HGFM atlas", self.registry, observations=(atlas_obs, tfuga_obs))
        b = compile_final_fusion("formalize TFUGA axiom", self.registry, observations=(atlas_obs, tfuga_obs))
        self.assertNotEqual(a.next_atlas_mission_id, b.next_atlas_mission_id)

    def test_autonomy_preview_is_internal_and_reversible(self):
        receipt = compile_final_fusion("fuse atlas", self.registry)
        self.assertEqual(receipt.schema_version, "jarvis-final-fusion-r8")
        self.assertIsNotNone(receipt.next_action_proposal)
        self.assertIsNotNone(receipt.autonomy_preview)
        self.assertIn(
            receipt.autonomy_preview["decision"],
            {"EXECUTE_AUTONOMOUSLY", "NO_ACTION", "HOLD_LOW_CONFIDENCE", "HOLD_NO_EVIDENCE"},
        )
        self.assertFalse(receipt.scientific_pass)
        self.assertFalse(receipt.authority_granted)

    def test_successful_outcome_updates_snapshot(self):
        obs = SourceObservation(
            source_id="drive-atlas-family",
            family="drive-atlas",
            kind="document-family",
            visibility="private-or-shared",
            observed_at="2026-09-18T16:40:00Z",
            materialized=False,
            exact_version_bound=True,
            duplicate_family_observed=False,
            boundary_preserved=True,
            tags=("atlas",),
        )
        snapshot = build_live_atlas_snapshot(self.registry, intent="atlas", observations=(obs,))
        ranked = rank_atlas_missions("atlas", snapshot)
        target = next(
            row for row in ranked
            if row.mission["target_id"] == "drive-atlas-family"
            and row.mission["transformation"] == "MATERIALIZE_BOUNDED_SOURCE"
        )
        outcome = ActionOutcome(
            action_id=target.mission["mission_id"],
            success=True,
            verified_gain=1.0,
            evidence_refs=("receipt:test",),
        )
        updated = apply_atlas_outcome(snapshot, target, outcome)
        before = next(s for s in snapshot.sources if s["source_id"] == "drive-atlas-family")
        after = next(s for s in updated.sources if s["source_id"] == "drive-atlas-family")
        self.assertFalse(before["materialized"])
        self.assertTrue(after["materialized"])
        self.assertNotEqual(snapshot.digest, updated.digest)


if __name__ == "__main__":
    unittest.main()
