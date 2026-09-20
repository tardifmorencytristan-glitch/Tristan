import unittest

from tristan.intent_reality import (
    IntentAxisPatch,
    IntentEvent,
    IntentLineageEdge,
    ObjectRef,
    deduplicate_intent_events,
    project_intent_state,
)
from tristan.intent_weekly_simple import (
    WeeklyIntentSnapshot,
    diff_snapshots,
    supports_bitemporal_history,
    supports_collision_safe_event_identity,
)


class R12VsWeeklySimpleCourt(unittest.TestCase):
    def _event(self, event_id, **overrides):
        data = dict(
            event_id=event_id,
            intent_id="I-WEEK",
            valid_at="2026-09-14T12:00:00Z",
            recorded_at="2026-09-14T12:00:00Z",
            source_id="chat:weekly",
            event_kind="OBSERVED",
            surface_state="partial",
            object_refs=(ObjectRef("intent", "I-WEEK", "subject"),),
        )
        data.update(overrides)
        return IntentEvent(**data)

    def test_simple_matches_r12_for_ordinary_weekly_snapshot_delta(self):
        before_simple = WeeklyIntentSnapshot(
            intent_id="I-WEEK",
            surface_state="partial",
            recovered=True,
            accomplished=False,
            verified=False,
            evidence_refs=("sha256:old",),
        )
        after_simple = WeeklyIntentSnapshot(
            intent_id="I-WEEK",
            surface_state="realized",
            recovered=True,
            accomplished=True,
            verified=True,
            evidence_refs=("sha256:old", "sha256:new"),
        )
        simple_delta = diff_snapshots(before_simple, after_simple)

        before_r12 = project_intent_state((
            self._event("E1", axis_patch=IntentAxisPatch(recovered=True), evidence_refs=("sha256:old",)),
        ))
        after_r12 = project_intent_state((
            self._event("E1", axis_patch=IntentAxisPatch(recovered=True), evidence_refs=("sha256:old",)),
            self._event(
                "E2",
                valid_at="2026-09-20T12:00:00Z",
                recorded_at="2026-09-20T12:00:00Z",
                surface_state="realized",
                axis_patch=IntentAxisPatch(accomplished=True, verified=True),
                evidence_refs=("sha256:new",),
            ),
        ))
        self.assertEqual(simple_delta.surface_transition, ("partial", "realized"))
        self.assertIn("accomplished:False->True", simple_delta.axis_changes)
        self.assertIn("verified:False->True", simple_delta.axis_changes)
        self.assertEqual(simple_delta.evidence_added, ("sha256:new",))
        self.assertEqual(after_r12.surface_state, "realized")
        self.assertTrue(after_r12.accomplished)
        self.assertTrue(after_r12.verified)
        self.assertIn("sha256:new", after_r12.evidence_refs)

    def test_late_evidence_discriminates_r12_from_simple(self):
        late = self._event(
            "E-LATE",
            valid_at="2026-01-10T09:00:00Z",
            recorded_at="2026-09-20T14:00:00Z",
            axis_patch=IntentAxisPatch(recovered=True),
        )
        self.assertIsNone(project_intent_state((late,), as_known_at="2026-09-19T23:59:59Z"))
        now = project_intent_state((late,), as_known_at="2026-09-20T14:00:00Z")
        self.assertTrue(now.recovered)
        self.assertEqual(now.latest_valid_at, "2026-01-10T09:00:00Z")
        self.assertFalse(supports_bitemporal_history())

    def test_event_id_collision_is_a_distinct_r12_capability(self):
        first = self._event("E-COLLIDE")
        second = self._event("E-COLLIDE", surface_state="failed")
        with self.assertRaisesRegex(ValueError, "event_id collision"):
            deduplicate_intent_events((first, second))
        self.assertFalse(supports_collision_safe_event_identity())

    def test_terminal_lineage_remains_queryable_in_r12(self):
        edge = IntentLineageEdge("SUPERSEDES", "I-NEW", "I-WEEK")
        state = project_intent_state((
            self._event("E-SUPER", surface_state="superseded", lineage=(edge,)),
            self._event(
                "E-REACT",
                valid_at="2026-09-20T12:00:00Z",
                recorded_at="2026-09-20T12:00:00Z",
                surface_state="partial",
                lineage=(IntentLineageEdge("REACTIVATES", "I-WEEK", "I-WEEK"),),
            ),
        ))
        relations = {x["relation"] for x in state.lineage}
        self.assertEqual(state.surface_state, "partial")
        self.assertIn("SUPERSEDES", relations)
        self.assertIn("REACTIVATES", relations)

    def test_simple_remains_preferred_when_history_is_not_required(self):
        before = WeeklyIntentSnapshot(intent_id="I-WEEK", surface_state="pending", recovered=True)
        after = WeeklyIntentSnapshot(intent_id="I-WEEK", surface_state="partial", recovered=True, accomplished=True)
        delta = diff_snapshots(before, after)
        self.assertEqual(delta.surface_transition, ("pending", "partial"))
        self.assertEqual(delta.axis_changes, ("accomplished:False->True",))


if __name__ == "__main__":
    unittest.main()
