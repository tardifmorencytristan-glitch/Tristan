from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from hashlib import sha256
import json
import math
from typing import Any, Mapping, Sequence

from tristan.jarvis_ir import ClaimIR, EvidenceIR
from omega_omni_compiler.src.representation_ir import RepresentationGraph

CHANNELS = {"TEXT", "VOICE", "VIDEO", "SLIDES", "WEB", "LIVE"}
INTERACTION_MODES = {"NONE", "LINEAR", "INTERRUPTIBLE", "INTERACTIVE"}


def _unit(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be finite in [0,1]")
    return value


def _digest(payload: object) -> str:
    body = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)
    return sha256(body.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CommunicationProjectionSpec:
    projection_id: str
    channel: str
    audience: str
    language: str
    duration_budget_s: float
    semantic_loss_budget: float = 0.1
    interaction_mode: str = "NONE"
    accessibility_requirements: tuple[str, ...] = ()
    rights_refs: tuple[str, ...] = ()
    authority_refs: tuple[str, ...] = ()

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.projection_id.strip():
            errors.append("projection_id required")
        if self.channel not in CHANNELS:
            errors.append(f"unknown channel: {self.channel}")
        if not self.audience.strip():
            errors.append("audience required")
        if not self.language.strip():
            errors.append("language required")
        if not math.isfinite(float(self.duration_budget_s)) or self.duration_budget_s <= 0:
            errors.append("duration_budget_s must be finite and positive")
        try:
            _unit(self.semantic_loss_budget, "semantic_loss_budget")
        except ValueError as exc:
            errors.append(str(exc))
        if self.interaction_mode not in INTERACTION_MODES:
            errors.append(f"unknown interaction_mode: {self.interaction_mode}")
        return errors


@dataclass(frozen=True)
class TimedProjectionSegment:
    segment_id: str
    start_s: float
    end_s: float
    source_representation_ids: tuple[str, ...]
    claim_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    spoken_text: str = ""
    on_screen_text: str = ""
    caption_text: str = ""
    visual_kind: str = ""
    uncertainty: str = "UNKNOWN"
    provenance_ids: tuple[str, ...] = ()
    declared_semantic_loss: float = 0.0

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.segment_id.strip():
            errors.append("segment_id required")
        if not math.isfinite(float(self.start_s)) or not math.isfinite(float(self.end_s)):
            errors.append("segment times must be finite")
        elif self.start_s < 0 or self.end_s <= self.start_s:
            errors.append("segment requires 0 <= start_s < end_s")
        if not self.source_representation_ids:
            errors.append("source_representation_ids required")
        if not self.provenance_ids:
            errors.append("provenance_ids required")
        if not any((self.spoken_text.strip(), self.on_screen_text.strip(), self.caption_text.strip(), self.visual_kind.strip())):
            errors.append("segment requires at least one rendered form")
        try:
            _unit(self.declared_semantic_loss, "declared_semantic_loss")
        except ValueError as exc:
            errors.append(str(exc))
        return errors


@dataclass(frozen=True)
class TimedProjectionIR:
    spec: CommunicationProjectionSpec
    segments: tuple[TimedProjectionSegment, ...]

    def validate(self) -> list[str]:
        errors = self.spec.validate()
        seen: set[str] = set()
        for segment in self.segments:
            errors.extend(f"{segment.segment_id}:{e}" for e in segment.validate())
            if segment.segment_id in seen:
                errors.append(f"duplicate segment_id: {segment.segment_id}")
            seen.add(segment.segment_id)
        if not self.segments:
            errors.append("at least one segment required")
        return errors


@dataclass(frozen=True)
class CommunicationCourtReceipt:
    projection_id: str
    status: str
    segment_count: int
    duration_s: float
    claim_count: int
    evidence_count: int
    missing_representation_ids: tuple[str, ...]
    missing_claim_ids: tuple[str, ...]
    missing_evidence_ids: tuple[str, ...]
    unsupported_claim_ids: tuple[str, ...]
    caption_gap_segments: tuple[str, ...]
    declared_semantic_loss: float
    semantic_loss_budget: float
    structural_errors: tuple[str, ...]
    generated_is_verified: bool
    authority_granted: bool
    digest: str


def _accumulated_loss(values: Sequence[float]) -> float:
    retained = 1.0
    for value in values:
        retained *= 1.0 - _unit(value, "declared_semantic_loss")
    return 1.0 - retained


def evaluate_projection(
    projection: TimedProjectionIR,
    representation_graph: RepresentationGraph,
    claims: Sequence[ClaimIR],
    evidence: Sequence[EvidenceIR],
) -> CommunicationCourtReceipt:
    errors = list(projection.validate())
    claim_map = {item.claim_id: item for item in claims}
    evidence_map = {item.evidence_id: item for item in evidence}
    if len(claim_map) != len(claims):
        errors.append("duplicate claim_id")
    if len(evidence_map) != len(evidence):
        errors.append("duplicate evidence_id")
    for item in claims:
        errors.extend(f"claim:{item.claim_id}:{e}" for e in item.validate())
    for item in evidence:
        errors.extend(f"evidence:{item.evidence_id}:{e}" for e in item.validate())

    rep_ids = {rid for seg in projection.segments for rid in seg.source_representation_ids}
    claim_ids = {cid for seg in projection.segments for cid in seg.claim_ids}
    evidence_ids = {eid for seg in projection.segments for eid in seg.evidence_ids}
    missing_rep = tuple(sorted(rep_ids - representation_graph.nodes.keys()))
    missing_claims = tuple(sorted(claim_ids - claim_map.keys()))
    missing_evidence = tuple(sorted(evidence_ids - evidence_map.keys()))

    unsupported: set[str] = set()
    caption_gaps: set[str] = set()
    for segment in projection.segments:
        for cid in set(segment.claim_ids) & claim_map.keys():
            linked = set(claim_map[cid].evidence_ids)
            if linked and not linked.intersection(segment.evidence_ids):
                unsupported.add(cid)
            if not linked:
                unsupported.add(cid)
        if "CAPTIONS" in projection.spec.accessibility_requirements and segment.spoken_text.strip() and not segment.caption_text.strip():
            caption_gaps.add(segment.segment_id)

    errors.extend(f"missing representation: {x}" for x in missing_rep)
    errors.extend(f"missing claim: {x}" for x in missing_claims)
    errors.extend(f"missing evidence: {x}" for x in missing_evidence)
    errors.extend(f"unsupported claim: {x}" for x in sorted(unsupported))
    errors.extend(f"caption required: {x}" for x in sorted(caption_gaps))

    duration = max((seg.end_s for seg in projection.segments), default=0.0)
    if duration > projection.spec.duration_budget_s + 1e-12:
        errors.append("duration budget exceeded")
    loss = _accumulated_loss([seg.declared_semantic_loss for seg in projection.segments])
    if loss > projection.spec.semantic_loss_budget + 1e-12:
        errors.append("semantic loss budget exceeded")

    payload = {
        "projection_id": projection.spec.projection_id,
        "status": "PASS_STRUCTURAL" if not errors else "HOLD",
        "segment_count": len(projection.segments),
        "duration_s": duration,
        "claim_count": len(claim_ids),
        "evidence_count": len(evidence_ids),
        "missing_representation_ids": missing_rep,
        "missing_claim_ids": missing_claims,
        "missing_evidence_ids": missing_evidence,
        "unsupported_claim_ids": tuple(sorted(unsupported)),
        "caption_gap_segments": tuple(sorted(caption_gaps)),
        "declared_semantic_loss": loss,
        "semantic_loss_budget": projection.spec.semantic_loss_budget,
        "structural_errors": tuple(errors),
        "generated_is_verified": False,
        "authority_granted": False,
    }
    return CommunicationCourtReceipt(**payload, digest=_digest(payload))


def projection_to_dict(projection: TimedProjectionIR) -> dict[str, Any]:
    return asdict(projection)


def projection_from_dict(data: Mapping[str, Any]) -> TimedProjectionIR:
    allowed = {f.name for f in fields(TimedProjectionIR)}
    unknown = set(data) - allowed
    if unknown:
        raise ValueError(f"unknown TimedProjectionIR fields: {sorted(unknown)}")
    spec_data = dict(data["spec"])
    for key in ("accessibility_requirements", "rights_refs", "authority_refs"):
        spec_data[key] = tuple(spec_data.get(key, ()))
    spec = CommunicationProjectionSpec(**spec_data)
    segments = []
    for raw in data.get("segments", ()):
        item = dict(raw)
        for key in ("source_representation_ids", "claim_ids", "evidence_ids", "provenance_ids"):
            item[key] = tuple(item.get(key, ()))
        segments.append(TimedProjectionSegment(**item))
    return TimedProjectionIR(spec=spec, segments=tuple(segments))


def projection_digest(projection: TimedProjectionIR) -> str:
    return _digest(projection_to_dict(projection))


def _timestamp(seconds: float) -> str:
    total_ms = int(round(float(seconds) * 1000))
    hours, rem = divmod(total_ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def to_webvtt(projection: TimedProjectionIR) -> str:
    cues = ["WEBVTT", ""]
    for segment in projection.segments:
        if not segment.caption_text.strip():
            continue
        cues.extend([
            segment.segment_id,
            f"{_timestamp(segment.start_s)} --> {_timestamp(segment.end_s)}",
            segment.caption_text.strip(),
            "",
        ])
    return "\n".join(cues)


def reuse_contract() -> tuple[str, ...]:
    return (
        "tristan.jarvis_ir.ClaimIR",
        "tristan.jarvis_ir.EvidenceIR",
        "omega_omni_compiler.src.representation_ir.RepresentationGraph",
        "omega_scientific_writing report/claim lineage by stable ids",
        "WebVTT as external timed-text projection",
    )