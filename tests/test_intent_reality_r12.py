import unittest

from tristan.final_fusion import SourceObservation
from tristan.frontier_loop import ActionOutcome
from tristan.intent_reality import (
    IntentAxisPatch,
    IntentEvidenceDebt,
    IntentEvent,
    IntentLineageEdge,
    ObjectRef,
    action_outcome_to_event,
    compare_intent_states,
    compile_intent_reality,
    deduplicate_intent_events,
    project_intent_state,
    receipt_to_event,
    source_observation_to_event,
)


class IntentRealityR12Tests(unittest.TestCase):
    def _event(self, event_id, **overrides):
        data = dict(
            event_id=event_id,
            intent_id="I-1",
            valid_at="2026-09-01T12:00:00Z",
            recorded_at="2026-09-01T12:00:00Z",
            source_id="chat:1",
            event_kind="OBSERVED",
            surface_state="partial",
            object_refs=(ObjectRef("intent", "I-1", "subject"),),
        )
        data.update(overrides)
        return IntentEvent(**data)

    def test_recovered_does_not_imply_accomplished(self):
        state = project_intent_state((
            self._event(
                "E-1",
                axis_patch=IntentAxisPatch(recovered=True),
            ),
        ))
        self.assertTrue(state.recovered)
        self.assertFalse(state.accomplished)
        self.assertFalse(state.verified)
        self.assertFalse(state.closed)

    def test_late_recovery_is_bitemporal(self):
        event = self._event(
            "E-late",
            valid_at="2026-01-10T09:00:00Z",
            recorded_at="2026-09-19T14:00:00Z",
            axis_patch=IntentAxisPatch(recovered=True),
        )
        before_discovery = project_intent_state(
            (event,),
            as_known_at="2026-09-18T23:59:59Z",
        )
        after_discovery = project_intent_state(
            (event,),
            as_known_at="2026-09-19T14:00:00Z",
        )
        self.assertIsNone(before_discovery)
        self.assertTrue(after_discovery.recovered)
        self.assertEqual(after_discovery.latest_valid_at, "2026-01-10T09:00:00Z")
        self.assertEqual(after_discovery.latest_recorded_at, "2026-09-19T14:00:00Z")

    def test_event_is_object_centric(self):
        state = project_intent_state((
            self._event(
                "E-multi",
                object_refs=(
                    ObjectRef("intent", "I-1", "subject"),
                    ObjectRef("capability", "cap-oak", "requires"),
                    ObjectRef("artifact", "receipt-42", "produces"),
                    ObjectRef("worker", "tablet", "executed_by"),
                ),
            ),
        ))
        kinds = {ref["object_type"] for ref in state.object_refs}
        self.assertEqual(kinds, {"intent", "capability", "artifact", "worker"})

    def test_r8_source_observation_only_recovers(self):
        obs = SourceObservation(
            source_id="drive-intent-atlas",
            family="drive-atlas",
            kind="document",
            visibility="private-or-shared",
            observed_at="2026-09-18T03:57:38Z",
            materialized=True,
            exact_version_bound=True,
            content_hash="sha256:abc",
            version_ref="drive-rev:1",
            tags=("intent", "atlas"),
            note="bounded recovered source",
        )
        event = source_observation_to_event(
            obs,
            intent_id="I-1",
            event_id="E-drive",
            recorded_at="2026-09-19T14:00:00Z",
        )
        state = project_intent_state((event,))
        self.assertTrue(state.recovered)
        self.assertFalse(state.accomplished)
        self.assertIn("sha256:abc", state.evidence_refs)
        self.assertIn("drive-rev:1", state.evidence_refs)

    def test_lineage_survives_supersession(self):
        edge = IntentLineageEdge("SUPERSEDES", "I-2", "I-1")
        state = project_intent_state((
            self._event(
                "E-super",
                surface_state="superseded",
                lineage=(edge,),
            ),
        ))
        self.assertEqual(state.surface_state, "superseded")
        self.assertEqual(state.lineage[0]["relation"], "SUPERSEDES")
        self.assertEqual(state.lineage[0]["source_intent_id"], "I-2")

    def test_evidence_debt_projects_into_r9_debt(self):
        debt = IntentEvidenceDebt(
            source_completeness=1.0,
            semantic_certainty=2.0,
            execution_proof=3.0,
            freshness=4.0,
            independence=5.0,
            reality_level=6.0,
            authority=7.0,
            reproducibility=8.0,
        )
        receipt = compile_intent_reality(
            (self._event("E-debt"),),
            evidence_debt=debt,
        )
        self.assertTrue(receipt.evidence_debt_assessed)
        self.assertEqual(receipt.r9_debt["evidence"], 19.0)
        self.assertEqual(receipt.r9_debt["freshness"], 4.0)
        self.assertEqual(receipt.r9_debt["reality"], 6.0)
        self.assertEqual(receipt.r9_debt["authority"], 7.0)
        self.assertFalse(receipt.scientific_pass)
        self.assertFalse(receipt.authority_granted)

    def test_missing_evidence_debt_is_unassessed_not_zero_claim(self):
        receipt = compile_intent_reality((self._event("E-unassessed"),))
        self.assertFalse(receipt.evidence_debt_assessed)
        self.assertIn(
            "UnassessedEvidenceDebt != ZeroDebt",
            receipt.boundaries,
        )

    def test_delta_detects_regression_and_closure(self):
        before = project_intent_state((
            self._event(
                "E-1",
                axis_patch=IntentAxisPatch(
                    recovered=True,
                    accomplished=True,
                    verified=True,
                ),
            ),
        ))
        after = project_intent_state((
            self._event(
                "E-1",
                axis_patch=IntentAxisPatch(
                    recovered=True,
                    accomplished=True,
                    verified=True,
                ),
            ),
            self._event(
                "E-2",
                recorded_at="2026-09-02T12:00:00Z",
                valid_at="2026-09-02T12:00:00Z",
                surface_state="realized",
                axis_patch=IntentAxisPatch(
                    verified=False,
                    closed=True,
                ),
                evidence_refs=("receipt:new",),
            ),
        ))
        delta = compare_intent_states(before, after)
        self.assertIn("verified", delta.regressions)
        self.assertIn("closed:False->True", delta.axis_changes)
        self.assertEqual(delta.surface_transition, ("partial", "realized"))
        self.assertEqual(delta.evidence_added, ("receipt:new",))

    def test_action_outcome_ingestion_preserves_verification_boundary(self):
        outcome = ActionOutcome(
            action_id="A-1",
            success=True,
            verified_gain=1.5,
            evidence_refs=("receipt:action-1",),
            residuals=("EXTERNAL_VALIDATION_GAP",),
        )
        event = action_outcome_to_event(
            outcome,
            intent_id="I-1",
            event_id="E-action",
            valid_at="2026-09-19T14:30:00Z",
            recorded_at="2026-09-19T14:31:00Z",
        )
        state = project_intent_state((event,))
        self.assertTrue(state.accomplished)
        self.assertTrue(state.verified)
        self.assertFalse(state.externally_validated)
        self.assertFalse(state.closed)
        self.assertEqual(state.surface_state, "realized")

    def test_hashed_receipt_ingestion_does_not_embed_raw_payload(self):
        raw = {
            "task_id": "oak-check",
            "status": "DONE",
            "private_field": "do-not-copy-this-payload",
        }
        event = receipt_to_event(
            raw,
            intent_id="I-1",
            event_id="E-receipt",
            source_id="jarvis-tablet",
            event_kind="OAK_RECEIPT",
            valid_at="2026-09-19T14:38:42-04:00",
            recorded_at="2026-09-19T14:38:43-04:00",
            axis_patch=IntentAxisPatch(accomplished=True, verified=True),
            object_refs=(ObjectRef("worker", "tablet", "observer"),),
            note="raw receipt retained outside event payload",
        )
        rendered = str(event.to_dict())
        self.assertNotIn("do-not-copy-this-payload", rendered)
        self.assertTrue(any(ref.startswith("sha256:") for ref in event.evidence_refs))

    def test_event_id_collision_fails_closed(self):
        first = self._event("E-collision")
        second = self._event(
            "E-collision",
            surface_state="failed",
        )
        with self.assertRaisesRegex(ValueError, "event_id collision"):
            deduplicate_intent_events((first, second))

    def test_digest_is_order_independent_after_recorded_time_sort(self):
        first = self._event(
            "E-1",
            axis_patch=IntentAxisPatch(recovered=True),
        )
        second = self._event(
            "E-2",
            valid_at="2026-09-02T12:00:00Z",
            recorded_at="2026-09-02T12:00:00Z",
            axis_patch=IntentAxisPatch(accomplished=True),
        )
        a = compile_intent_reality((first, second))
        b = compile_intent_reality((second, first))
        self.assertEqual(a.event_digest, b.event_digest)
        self.assertEqual(a.state, b.state)


if __name__ == "__main__":
    unittest.main()
