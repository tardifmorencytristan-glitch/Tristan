from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path

from tristan.jarvis_ir import ClaimIR, EvidenceIR
from omega_omni_compiler.src.communication_projection import (
    CommunicationProjectionSpec,
    TimedProjectionIR,
    TimedProjectionSegment,
    evaluate_projection,
    projection_digest,
    to_webvtt,
)
from omega_omni_compiler.src.provenance import ProvenanceAnchor
from omega_omni_compiler.src.representation_ir import (
    RepresentationGraph,
    RepresentationNode,
    RepresentationRelation,
)


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "omega_scientific_writing" / "fixtures" / "battery_t_r0_4_writing_court.json"
OUT_DIR = ROOT / "omega_omni_compiler" / "benchmarks"


def build() -> tuple[TimedProjectionIR, RepresentationGraph, ClaimIR, EvidenceIR, dict]:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    text = next(row["text"] for row in data["candidates"] if row["origin"] == "R4_BOUNDED")
    source_ref = f'{data["source"]["repository"]}@{data["source"]["commit"]}:{data["source"]["path"]}'
    fixture_hash = sha256(FIXTURE.read_bytes()).hexdigest()
    anchor = ProvenanceAnchor(
        source_artifact_id="battery-t-writing-court",
        source_content_hash=fixture_hash,
        extractor="exact-json-fixture",
        extractor_version="r4.1",
        confidence=1.0,
    )
    graph = RepresentationGraph()
    graph.add_node(RepresentationNode("battery-doc", "DOCUMENT", provenance=[anchor]))
    graph.add_node(RepresentationNode("battery-paragraph", "PARAGRAPH", content=text, provenance=[anchor]))
    graph.add_relation(RepresentationRelation("contains", "CONTAINS", ("battery-doc",), ("battery-paragraph",)))
    claim = ClaimIR("battery-bounded", text, evidence_ids=("calce-r04",), uncertainty="BOUNDED")
    evidence = EvidenceIR(
        "calce-r04",
        "dataset",
        source_ref,
        "zero-fit transfer court",
        "DFN/SPM/SPMe bounded CALCE first-cycle comparison",
        "BOUNDED",
        (source_ref,),
    )
    spec = CommunicationProjectionSpec(
        projection_id="battery-video-r01",
        channel="VIDEO",
        audience="battery-modeling",
        language="en",
        duration_budget_s=45.0,
        semantic_loss_budget=0.05,
        interaction_mode="LINEAR",
        accessibility_requirements=("CAPTIONS",),
        rights_refs=("fixture-source-provenance-only",),
    )
    projection = TimedProjectionIR(
        spec,
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
    return projection, graph, claim, evidence, data


def main() -> int:
    projection, graph, claim, evidence, data = build()
    receipt = evaluate_projection(projection, graph, (claim,), (evidence,))
    vtt = to_webvtt(projection)
    fixture_hash = sha256(FIXTURE.read_bytes()).hexdigest()
    payload = {
        "schema": "communication-projection-r0.1-battery-court",
        "source_fixture": str(FIXTURE.relative_to(ROOT)).replace("\\", "/"),
        "source_fixture_sha256": fixture_hash,
        "source_commit": data["source"]["commit"],
        "projection_digest": projection_digest(projection),
        "webvtt_sha256": sha256(vtt.encode("utf-8")).hexdigest(),
        "court": asdict(receipt),
        "boundaries": [
            "PASS_STRUCTURAL != SemanticEquivalence",
            "DeclaredSemanticLoss != MeasuredSemanticLoss",
            "WebVTTExport != VideoRender",
            "Generated != Verified",
            "Capability != Authority",
        ],
    }
    receipt_path = OUT_DIR / "communication_projection_battery_r01_receipt.json"
    vtt_path = OUT_DIR / "communication_projection_battery_r01.vtt"
    receipt_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    vtt_path.write_text(vtt, encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    return 0 if receipt.status == "PASS_STRUCTURAL" else 2


if __name__ == "__main__":
    raise SystemExit(main())