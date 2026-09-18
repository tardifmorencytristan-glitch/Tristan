from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import hashlib
import json
import re
from typing import Any, Iterable

from .atlas_federation import compile_atlas_federation
from .autonomous_decision import ActionProposal, decide_action
from .frontier_loop import ActionOutcome
from .mission_queue import Mission
from .registry import Registry


FINAL_FUSION_BOUNDARIES = (
    "ObservationDescriptor != ConnectorExecution",
    "ConnectorRead != ScientificEvidence",
    "AtlasProjection != ScientificRanking",
    "IntentRelevance != Truth",
    "AutonomyPreview != Execution",
    "ActionProposal != ActionOutcome",
    "PrivateSource != PublicPayload",
    "StateTransitionRequiresEvidence",
    "NO_ACTION is admissible",
)


@dataclass(frozen=True)
class SourceObservation:
    source_id: str
    family: str
    kind: str
    visibility: str
    observed_at: str
    materialized: bool
    exact_version_bound: bool
    duplicate_family_observed: bool = False
    boundary_preserved: bool = False
    content_hash: str | None = None
    version_ref: str | None = None
    tags: tuple[str, ...] = ()
    note: str = ""

    def validate(self) -> list[str]:
        errors: list[str] = []
        for name, value in (
            ("source_id", self.source_id),
            ("family", self.family),
            ("kind", self.kind),
            ("visibility", self.visibility),
            ("observed_at", self.observed_at),
        ):
            if not value.strip():
                errors.append(f"{name} required")
        if self.content_hash is not None and not self.content_hash.strip():
            errors.append("content_hash must be non-empty when supplied")
        if self.version_ref is not None and not self.version_ref.strip():
            errors.append("version_ref must be non-empty when supplied")
        return errors

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class RankedAtlasMission:
    mission: dict
    intent_relevance: float
    projection_score: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class LiveAtlasSnapshot:
    schema_version: str
    observed_at: str
    sources: tuple[dict, ...]
    digest: str
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class FinalFusionReceipt:
    schema_version: str
    intent: str
    atlas_snapshot: dict
    missions: tuple[dict, ...]
    top16: tuple[str, ...]
    top64: tuple[str, ...]
    top256: tuple[str, ...]
    next_atlas_mission_id: str
    next_action_proposal: dict | None
    autonomy_preview: dict | None
    epistemic_status: str
    scientific_pass: bool
    authority_granted: bool
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) >= 3
        and token not in {"and", "the", "for", "with", "from", "this", "that"}
    }


def _source_from_r7(data: dict[str, Any]) -> SourceObservation:
    return SourceObservation(
        source_id=str(data["source_id"]),
        family=str(data["family"]),
        kind=str(data["kind"]),
        visibility=str(data["visibility"]),
        observed_at=str(data.get("observed_at") or "unknown"),
        materialized=bool(data.get("materialized", False)),
        exact_version_bound=bool(data.get("exact_version_bound", False)),
        duplicate_family_observed=bool(data.get("duplicate_family_observed", False)),
        boundary_preserved=bool(data.get("boundary_preserved", False)),
        note=str(data.get("note", "")),
    )


def _merge_sources(
    base_sources: Iterable[SourceObservation],
    observations: Iterable[SourceObservation],
) -> tuple[SourceObservation, ...]:
    merged = {source.source_id: source for source in base_sources}
    for observation in observations:
        errors = observation.validate()
        if errors:
            raise ValueError("; ".join(errors))
        merged[observation.source_id] = observation
    return tuple(sorted(merged.values(), key=lambda s: (s.family, s.source_id)))


def _snapshot_digest(sources: tuple[SourceObservation, ...]) -> str:
    payload = [
        {
            "source_id": s.source_id,
            "family": s.family,
            "kind": s.kind,
            "visibility": s.visibility,
            "observed_at": s.observed_at,
            "materialized": s.materialized,
            "exact_version_bound": s.exact_version_bound,
            "duplicate_family_observed": s.duplicate_family_observed,
            "boundary_preserved": s.boundary_preserved,
            "content_hash": s.content_hash,
            "version_ref": s.version_ref,
            "tags": list(s.tags),
        }
        for s in sources
    ]
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def build_live_atlas_snapshot(
    registry: Registry,
    *,
    intent: str,
    observations: tuple[SourceObservation, ...] = (),
) -> LiveAtlasSnapshot:
    base = compile_atlas_federation(intent, registry)
    base_sources = tuple(_source_from_r7(source) for source in base.sources)
    sources = _merge_sources(base_sources, observations)
    observed_at = max((source.observed_at for source in sources), default="unknown")
    return LiveAtlasSnapshot(
        schema_version="tristan-live-atlas-r8",
        observed_at=observed_at,
        sources=tuple(source.to_dict() for source in sources),
        digest=_snapshot_digest(sources),
        boundaries=(
            "Snapshot != ScientificEvidence",
            "ObservedAt != FreshForever",
            "PrivateSource != PublicPayload",
        ),
    )


def _missions_for_source(source: SourceObservation) -> list[Mission]:
    missions: list[Mission] = []
    sid = re.sub(r"[^a-z0-9]+", "-", source.source_id.lower()).strip("-") or "source"
    family = re.sub(r"[^a-z0-9]+", "-", source.family.lower()).strip("-") or "family"

    if not source.materialized:
        missions.append(Mission(
            f"M-R8-MATERIALIZE-{sid}",
            source.source_id,
            "MATERIALIZE_BOUNDED_SOURCE",
            "source-provenance-court",
            expected_verified_gain=3.0,
            debt_reduction=4.0,
            reuse_potential=2.0,
            cost=1.0,
            risk=0.2,
        ))
    if not source.exact_version_bound:
        missions.append(Mission(
            f"M-R8-PIN-{sid}",
            source.source_id,
            "BIND_EXACT_VERSION",
            "provenance-version-court",
            expected_verified_gain=2.0,
            debt_reduction=3.0,
            reuse_potential=2.0,
            cost=0.6,
            risk=0.1,
        ))
    if source.duplicate_family_observed:
        missions.append(Mission(
            f"M-R8-DEDUP-{family}",
            source.source_id,
            "CANONICALIZE_DUPLICATE_FAMILY",
            "content-hash-and-lineage-court",
            expected_verified_gain=2.0,
            debt_reduction=4.0,
            reuse_potential=3.0,
            cost=0.8,
            risk=0.1,
        ))
    if source.visibility in {"private", "private-or-shared"} and not source.boundary_preserved:
        missions.append(Mission(
            f"M-R8-BOUNDARY-{sid}",
            source.source_id,
            "PRESERVE_PRIVATE_FEDERATION_BOUNDARY",
            "privacy-and-provenance-court",
            expected_verified_gain=1.0,
            debt_reduction=2.0,
            reuse_potential=2.0,
            cost=0.4,
            risk=0.1,
        ))
    return missions


def rank_atlas_missions(
    intent: str,
    snapshot: LiveAtlasSnapshot,
) -> tuple[RankedAtlasMission, ...]:
    source_by_id = {
        source["source_id"]: SourceObservation(
            source_id=source["source_id"],
            family=source["family"],
            kind=source["kind"],
            visibility=source["visibility"],
            observed_at=source["observed_at"],
            materialized=source["materialized"],
            exact_version_bound=source["exact_version_bound"],
            duplicate_family_observed=source.get("duplicate_family_observed", False),
            boundary_preserved=source.get("boundary_preserved", False),
            content_hash=source.get("content_hash"),
            version_ref=source.get("version_ref"),
            tags=tuple(source.get("tags", ())),
            note=source.get("note", ""),
        )
        for source in snapshot.sources
    }

    query_tokens = _tokens(intent)
    ranked: list[RankedAtlasMission] = []
    for source in source_by_id.values():
        source_tokens = _tokens(" ".join((
            source.source_id,
            source.family,
            source.kind,
            source.note,
            " ".join(source.tags),
        )))
        overlap = len(query_tokens & source_tokens)
        relevance = overlap / max(len(query_tokens), 1)
        for mission in _missions_for_source(source):
            projection_score = mission.priority * (1.0 + 2.0 * relevance)
            ranked.append(RankedAtlasMission(
                mission=mission.to_dict(),
                intent_relevance=relevance,
                projection_score=projection_score,
            ))

    return tuple(sorted(
        ranked,
        key=lambda row: (
            -row.projection_score,
            -row.mission["debt_reduction"],
            row.mission["mission_id"],
        ),
    ))


def mission_to_action_proposal(
    ranked_mission: RankedAtlasMission,
    snapshot: LiveAtlasSnapshot,
) -> ActionProposal:
    mission = ranked_mission.mission
    return ActionProposal(
        action_id=mission["mission_id"],
        action_kind="atlas_internal_reconciliation",
        plan={
            "target_id": mission["target_id"],
            "transformation": mission["transformation"],
            "evaluator": mission["evaluator"],
            "atlas_snapshot_digest": snapshot.digest,
        },
        reversible=True,
        external_side_effect=False,
        rollback="restore previous immutable Atlas snapshot",
        evidence_refs=(f"atlas-snapshot:{snapshot.digest}",),
        confidence=0.90,
        expected_verified_gain=float(
            mission["expected_verified_gain"]
            + mission["debt_reduction"]
            + mission["reuse_potential"]
            + mission["gaia_impact"]
        ),
        cost=float(mission["cost"]),
        risk=float(mission["risk"]),
    )


def apply_atlas_outcome(
    snapshot: LiveAtlasSnapshot,
    ranked_mission: RankedAtlasMission,
    outcome: ActionOutcome,
) -> LiveAtlasSnapshot:
    if outcome.action_id != ranked_mission.mission["mission_id"]:
        raise ValueError("outcome action_id must match mission_id")
    errors = outcome.validate()
    if errors:
        raise ValueError("; ".join(errors))
    if not outcome.success:
        return snapshot

    target_id = ranked_mission.mission["target_id"]
    transformation = ranked_mission.mission["transformation"]
    sources = [
        SourceObservation(
            source_id=source["source_id"],
            family=source["family"],
            kind=source["kind"],
            visibility=source["visibility"],
            observed_at=source["observed_at"],
            materialized=source["materialized"],
            exact_version_bound=source["exact_version_bound"],
            duplicate_family_observed=source.get("duplicate_family_observed", False),
            boundary_preserved=source.get("boundary_preserved", False),
            content_hash=source.get("content_hash"),
            version_ref=source.get("version_ref"),
            tags=tuple(source.get("tags", ())),
            note=source.get("note", ""),
        )
        for source in snapshot.sources
    ]

    updated: list[SourceObservation] = []
    for source in sources:
        if source.source_id != target_id:
            updated.append(source)
            continue
        if transformation == "MATERIALIZE_BOUNDED_SOURCE":
            source = replace(source, materialized=True)
        elif transformation == "BIND_EXACT_VERSION":
            source = replace(source, exact_version_bound=True)
        elif transformation == "CANONICALIZE_DUPLICATE_FAMILY":
            source = replace(source, duplicate_family_observed=False)
        elif transformation == "PRESERVE_PRIVATE_FEDERATION_BOUNDARY":
            source = replace(source, boundary_preserved=True)
        updated.append(source)

    updated_tuple = tuple(sorted(updated, key=lambda s: (s.family, s.source_id)))
    return LiveAtlasSnapshot(
        schema_version=snapshot.schema_version,
        observed_at=snapshot.observed_at,
        sources=tuple(source.to_dict() for source in updated_tuple),
        digest=_snapshot_digest(updated_tuple),
        boundaries=snapshot.boundaries,
    )


def compile_final_fusion(
    intent: str,
    registry: Registry,
    *,
    observations: tuple[SourceObservation, ...] = (),
) -> FinalFusionReceipt:
    snapshot = build_live_atlas_snapshot(
        registry,
        intent=intent,
        observations=observations,
    )
    ranked = rank_atlas_missions(intent, snapshot)
    ids = tuple(row.mission["mission_id"] for row in ranked)
    proposal = mission_to_action_proposal(ranked[0], snapshot) if ranked else None
    preview = decide_action(proposal).to_dict() if proposal is not None else None

    return FinalFusionReceipt(
        schema_version="jarvis-final-fusion-r8",
        intent=intent,
        atlas_snapshot=snapshot.to_dict(),
        missions=tuple(row.to_dict() for row in ranked),
        top16=ids[:16],
        top64=ids[:64],
        top256=ids[:256],
        next_atlas_mission_id=ids[0] if ids else "NO_ACTION",
        next_action_proposal=asdict(proposal) if proposal is not None else None,
        autonomy_preview=preview,
        epistemic_status="PROVISIONAL_LIVE_ATLAS_PLAN",
        scientific_pass=False,
        authority_granted=False,
        boundaries=FINAL_FUSION_BOUNDARIES,
    )
