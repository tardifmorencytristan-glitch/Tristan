import json
from hashlib import sha256
from pathlib import Path
import unittest

from tristan.jarvis_ir import ClaimIR, EvidenceIR
from omega_omni_compiler.src.communication_projection import (
    CommunicationProjectionSpec,
    TimedProjectionIR,
    TimedProjectionSegment,
    evaluate_projection,
    projection_digest,
    projection_from_dict,
    projection_to_dict,
    to_webvtt,
)
from omega_omni_compiler.src.provenance import ProvenanceAnchor
from omega_omni_compiler.src.representation_ir import (
    RepresentationGraph,
    RepresentationNode,
    RepresentationRelation,
)


def anchor(source: str = "fixture") -> ProvenanceAnchor:
    return ProvenanceAnchor(
        source_artifact_id=source,
        source_content_hash=sha256(source.encode()).hexdigest(),
        extractor="communication-r01-test",
        extractor_version="1.0",
        confidence=1.0,
    )


def graph() -> RepresentationGraph:
    g = RepresentationGraph()
    g.add_node(RepresentationNode("doc", "DOCUMENT", provenance=[anchor("doc")]))
    g.add_node(RepresentationNode("p1", "PARAGRAPH", content="bounded result", provenance=[anchor("p1")]))
    g.add_relation(RepresentationRelation("r1", "CONTAINS", ("doc",), ("p1",)))
    return g


def spec(**kwargs) -> CommunicationProjectionSpec:
    base = dict(
        projection_id="projection-1",
        channel="VIDEO",
        audience="technical",
        language="en",
        duration_budget_s=30.0,
        semantic_loss_budget=0.1,
        interaction_mode="LINEAR",
        accessibility_requirements=("CAPTIONS",),
    )
    base.update(kwargs)
    return CommunicationProjectionSpec(**base)


def segment(**kwargs) -> TimedProjectionSegment:
    base = dict(
        segment_id="s1",
        start_s=0.0,
        end_s=5.0,
        source_representation_ids=("p1",),
        claim_ids=("c1",),
        evidence_ids=("e1",),
        spoken_text="bounded result",
        on_screen_text="bounded result",
        caption_text="bounded result",
        provenance_ids=("source:fixture",),
        declared_semantic_loss=0.01,
    )
    base.update(kwargs)
    return TimedProjectionSegment(**base)


def claim(evidence_ids=("e1",)) -> ClaimIR:
    return ClaimIR(
        claim_id="c1",
        statement="bounded result",
        evidence_ids=tuple(evidence_ids),
        uncertainty="BOUNDED",
    )


def evidence(eid="e1") -> EvidenceIR:
    return EvidenceIR(
        evidence_id=eid,
        kind="dataset",
        source="source",
        method="bounded court",
        result="observed result",
        uncertainty="BOUNDED",
        provenance=("source:fixture",),
    )


class CommunicationProjectionR01Tests(unittest.TestCase):
    def test_happy_path_is_structural_pass_without_authority_promotion(self):
        projection = TimedProjectionIR(spec(), (segment(),))
        receipt = evaluate_projection(projection, graph(), (claim(),), (evidence(),))
        self.assertEqual(receipt.status, "PASS_STRUCTURAL")
        self.assertFalse(receipt.generated_is_verified)
        self.assertFalse(receipt.authority_granted)
        self.assertEqual(receipt.unsupported_claim_ids, ())

    def test_missing_representation_fails_closed(self):
        projection = TimedProjectionIR(spec(), (segment(source_representation_ids=("missing",)),))
        receipt = evaluate_projection(projection, graph(), (claim(),), (evidence(),))
        self.assertEqual(receipt.status, "HOLD")
        self.assertEqual(receipt.missing_representation_ids, ("missing",))

    def test_claim_requires_linked_evidence_in_same_segment(self):
        projection = TimedProjectionIR(spec(), (segment(evidence_ids=()),))
        receipt = evaluate_projection(projection, graph(), (claim(),), (evidence(),))
        self.assertEqual(receipt.status, "HOLD")
        self.assertEqual(receipt.unsupported_claim_ids, ("c1",))

    def test_caption_requirement_is_enforced_for_spoken_video(self):
        projection = TimedProjectionIR(spec(), (segment(caption_text=""),))
        receipt = evaluate_projection(projection, graph(), (claim(),), (evidence(),))
        self.assertEqual(receipt.caption_gap_segments, ("s1",))
        self.assertEqual(receipt.status, "HOLD")

    def test_duration_budget_fails_closed(self):
        projection = TimedProjectionIR(spec(duration_budget_s=4.0), (segment(end_s=5.0),))
        receipt = evaluate_projection(projection, graph(), (claim(),), (evidence(),))
        self.assertIn("duration budget exceeded", receipt.structural_errors)

    def test_declared_semantic_loss_budget_is_compositional(self):
        segments = (
            segment(segment_id="s1", start_s=0, end_s=5, declared_semantic_loss=0.08),
            segment(segment_id="s2", start_s=5, end_s=10, declared_semantic_loss=0.08),
        )
        projection = TimedProjectionIR(spec(semantic_loss_budget=0.1), segments)
        receipt = evaluate_projection(projection, graph(), (claim(),), (evidence(),))
        self.assertEqual(receipt.status, "HOLD")
        self.assertIn("semantic loss budget exceeded", receipt.structural_errors)
        self.assertGreater(receipt.declared_semantic_loss, 0.1)

    def test_projection_json_round_trip_and_digest_are_deterministic(self):
        original = TimedProjectionIR(spec(), (segment(),))
        payload = projection_to_dict(original)
        rebuilt = projection_from_dict(payload)
        self.assertEqual(rebuilt, original)
        self.assertEqual(projection_digest(rebuilt), projection_digest(original))

    def test_unknown_round_trip_fields_fail_closed(self):
        payload = projection_to_dict(TimedProjectionIR(spec(), (segment(),)))
        payload["shadow_authority"] = True
        with self.assertRaises(ValueError):
            projection_from_dict(payload)

    def test_webvtt_export_is_deterministic_and_timed(self):
        projection = TimedProjectionIR(spec(), (segment(start_s=1.25, end_s=3.5),))
        body = to_webvtt(projection)
        self.assertTrue(body.startswith("WEBVTT\n\n"))
        self.assertIn("00:00:01.250 --> 00:00:03.500", body)
        self.assertIn("bounded result", body)

    def test_real_battery_t_writing_fixture_compiles_as_bounded_projection(self):
        root = Path(__file__).resolve().parents[2]
        fixture_path = root / "omega_scientific_writing" / "fixtures" / "battery_t_r0_4_writing_court.json"
        data = json.loads(fixture_path.read_text(encoding="utf-8"))
        text = next(row["text"] for row in data["candidates"] if row["origin"] == "R4_BOUNDED")
        source_ref = f'{data["source"]["repository"]}@{data["source"]["commit"]}:{data["source"]["path"]}'
        source_hash = sha256(fixture_path.read_bytes()).hexdigest()
        a = ProvenanceAnchor(
            source_artifact_id="battery-t-writing-court",
            source_content_hash=source_hash,
            extractor="exact-json-fixture",
            extractor_version="r4.1",
            confidence=1.0,
        )
        g = RepresentationGraph()
        g.add_node(RepresentationNode("battery-doc", "DOCUMENT", provenance=[a]))
        g.add_node(RepresentationNode("battery-paragraph", "PARAGRAPH", content=text, provenance=[a]))
        g.add_relation(RepresentationRelation("contains", "CONTAINS", ("battery-doc",), ("battery-paragraph",)))
        c = ClaimIR("battery-bounded", text, evidence_ids=("calce-r04",), uncertainty="BOUNDED")
        e = EvidenceIR(
            "calce-r04",
            "dataset",
            source_ref,
            "zero-fit transfer court",
            "DFN/SPM/SPMe bounded CALCE first-cycle comparison",
            "BOUNDED",
            (source_ref,),
        )
        projection = TimedProjectionIR(
            spec(
                projection_id="battery-video-r01",
                audience="battery-modeling",
                duration_budget_s=45.0,
                semantic_loss_budget=0.05,
            ),
            (
                TimedProjectionSegment(
                    "battery-s1",
                    0.0,
                    25.0,
                    ("battery-paragraph",),
                    ("battery-bounded",),
                    ("calce-r04",),
                    text,
                    "DFN 0.0722 V | SPM 0.1709 V | SPMe 0.2550 V",
                    text,
                    "RESULT_CARD",
                    "BOUNDED",
                    (source_ref,),
                    0.01,
                ),
            ),
        )
        receipt = evaluate_projection(projection, g, (c,), (e,))
        self.assertEqual(receipt.status, "PASS_STRUCTURAL")
        self.assertEqual(receipt.claim_count, 1)
        self.assertEqual(receipt.evidence_count, 1)
        self.assertIn("0.0722", to_webvtt(projection))


if __name__ == "__main__":
    unittest.main()
