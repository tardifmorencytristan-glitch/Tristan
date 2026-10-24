from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from typing import Iterable

from .final_fusion import SourceObservation
from .frontier_loop import ActionOutcome
from .ultra_closure import DebtVector


INTENT_REALITY_BOUNDARIES = (
    "Recovered != Accomplished",
    "Accomplished != Verified",
    "Verified != ExternallyValidated",
    "RecordedAt != ValidAt",
    "IntentInference != UserInstruction",
    "Lineage != Truth",
    "EventLog != ScientificEvidence",
    "UnassessedEvidenceDebt != ZeroDebt",
    "Capability != Authority",
    "NO_ACTION is admissible",
)

SURFACE_STATES = frozenset({
    "realized",
    "partial",
    "abandoned",
    "superseded",
    "failed",
    "pending",
    "proposed",
    "questioned",
    "implicit",
})

LINEAGE_RELATIONS = frozenset({
    "PRECEDES",
    "REFINES",
    "SPLITS",
    "MERGES",
    "SUPERSEDES",
    "ABSORBS",
    "CONTRADICTS",
    "FULFILLS",
    "FAILS",
    "ABANDONS",
    "REACTIVATES",
    "DEPENDS_ON",
})


def _parse_time(value: str) -> datetime:
    if not value.strip():
        raise ValueError("timestamp required")
    candidate = value.strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(candidate)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class ObjectRef:
    object_type: str
    object_id: str
    role: str = "related"

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.object_type.strip():
            errors.append("object_type required")
        if not self.object_id.strip():
            errors.append("object_id required")
        if not self.role.strip():
            errors.append("role required")
        return errors

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class IntentAxisPatch:
    recovered: bool | None = None
    accomplished: bool | None = None
    verified: bool | None = None
    externally_validated: bool | None = None
    closed: bool | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class IntentLineageEdge:
    relation: str
    source_intent_id: str
    target_intent_id: str

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.relation not in LINEAGE_RELATIONS:
            errors.append(f"unsupported lineage relation: {self.relation}")
        if not self.source_intent_id.strip():
            errors.append("source_intent_id required")
        if not self.target_intent_id.strip():
            errors.append("target_intent_id required")
        return errors

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class IntentEvidenceDebt:
    source_completeness: float = 0.0
    semantic_certainty: float = 0.0
    execution_proof: float = 0.0
    freshness: float = 0.0
    independence: float = 0.0
    reality_level: float = 0.0
    authority: float = 0.0
    reproducibility: float = 0.0

    def validate(self) -> list[str]:
        errors: list[str] = []
        for name, value in asdict(self).items():
            if value < 0:
                errors.append(f"{name} debt must be non-negative")
        return errors

    @property
    def total(self) -> float:
        return sum(asdict(self).values())

    def to_r9_debt(self) -> DebtVector:
        evidence = (
            self.source_completeness
            + self.semantic_certainty
            + self.execution_proof
            + self.independence
            + self.reproducibility
        )
        return DebtVector(
            evidence=evidence,
            freshness=self.freshness,
            reality=self.reality_level,
            authority=self.authority,
        )

    def to_dict(self) -> dict:
        data = asdict(self)
        data["total"] = self.total
        return data


@dataclass(frozen=True)
class IntentEvent:
    event_id: str
    intent_id: str
    valid_at: str
    recorded_at: str
    source_id: str
    event_kind: str
    surface_state: str | None = None
    axis_patch: IntentAxisPatch = field(default_factory=IntentAxisPatch)
    object_refs: tuple[ObjectRef, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    lineage: tuple[IntentLineageEdge, ...] = ()
    implicit_confidence: float | None = None
    note: str = ""

    def validate(self) -> list[str]:
        errors: list[str] = []
        for name, value in (
            ("event_id", self.event_id),
            ("intent_id", self.intent_id),
            ("source_id", self.source_id),
            ("event_kind", self.event_kind),
        ):
            if not value.strip():
                errors.append(f"{name} required")
        try:
            _parse_time(self.valid_at)
        except Exception:
            errors.append("valid_at must be ISO-8601 compatible")
        try:
            _parse_time(self.recorded_at)
        except Exception:
            errors.append("recorded_at must be ISO-8601 compatible")
        if self.surface_state is not None and self.surface_state not in SURFACE_STATES:
            errors.append(f"unsupported surface_state: {self.surface_state}")
        if self.implicit_confidence is not None and not 0.0 <= self.implicit_confidence <= 1.0:
            errors.append("implicit_confidence must be between 0 and 1")
        if self.surface_state == "implicit" and self.implicit_confidence is None:
            errors.append("implicit surface state requires implicit_confidence")
        if not self.object_refs:
            errors.append("object_refs required")
        elif not any(
            ref.object_type == "intent" and ref.object_id == self.intent_id
            for ref in self.object_refs
        ):
            errors.append("object_refs must include the event intent")
        for ref in self.object_refs:
            errors.extend(ref.validate())
        for edge in self.lineage:
            errors.extend(edge.validate())
        if any(not ref.strip() for ref in self.evidence_refs):
            errors.append("evidence_refs must be non-empty")
        return errors

    def to_dict(self) -> dict:
        return {
            **asdict(self),
            "axis_patch": self.axis_patch.to_dict(),
            "object_refs": tuple(ref.to_dict() for ref in self.object_refs),
            "lineage": tuple(edge.to_dict() for edge in self.lineage),
        }


def _canonical_digest(value: object) -> str:
    blob = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def deduplicate_intent_events(
    events: Iterable[IntentEvent],
) -> tuple[IntentEvent, ...]:
    by_id: dict[str, IntentEvent] = {}
    fingerprints: dict[str, str] = {}
    for event in events:
        errors = event.validate()
        if errors:
            raise ValueError("; ".join(errors))
        fingerprint = _canonical_digest(event.to_dict())
        previous = fingerprints.get(event.event_id)
        if previous is not None and previous != fingerprint:
            raise ValueError(
                f"event_id collision with different payload: {event.event_id}"
            )
        by_id[event.event_id] = event
        fingerprints[event.event_id] = fingerprint
    return tuple(sorted(by_id.values(), key=_event_sort_key))


@dataclass(frozen=True)
class IntentState:
    intent_id: str
    surface_state: str
    recovered: bool
    accomplished: bool
    verified: bool
    externally_validated: bool
    closed: bool
    latest_valid_at: str
    latest_recorded_at: str
    evidence_refs: tuple[str, ...]
    object_refs: tuple[dict, ...]
    lineage: tuple[dict, ...]
    event_ids: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class IntentStateDelta:
    intent_id: str
    surface_transition: tuple[str, str] | None
    axis_changes: tuple[str, ...]
    regressions: tuple[str, ...]
    evidence_added: tuple[str, ...]
    evidence_removed: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class IntentRealityReceipt:
    schema_version: str
    state: dict
    evidence_debt: dict
    evidence_debt_assessed: bool
    r9_debt: dict
    event_count: int
    event_digest: str
    scientific_pass: bool
    authority_granted: bool
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def _event_sort_key(event: IntentEvent) -> tuple[datetime, str]:
    return (_parse_time(event.recorded_at), event.event_id)


def project_intent_state(
    events: Iterable[IntentEvent],
    *,
    as_known_at: str | None = None,
    valid_at: str | None = None,
) -> IntentState | None:
    rows = deduplicate_intent_events(events)
    if not rows:
        return None
    intent_ids = {event.intent_id for event in rows}
    if len(intent_ids) != 1:
        raise ValueError("all events must target one intent")

    known_cutoff = _parse_time(as_known_at) if as_known_at else None
    valid_cutoff = _parse_time(valid_at) if valid_at else None
    filtered = tuple(
        event for event in rows
        if (known_cutoff is None or _parse_time(event.recorded_at) <= known_cutoff)
        and (valid_cutoff is None or _parse_time(event.valid_at) <= valid_cutoff)
    )
    if not filtered:
        return None

    ordered = tuple(sorted(filtered, key=_event_sort_key))
    surface_state = "proposed"
    axes = {
        "recovered": False,
        "accomplished": False,
        "verified": False,
        "externally_validated": False,
        "closed": False,
    }
    evidence: set[str] = set()
    objects: dict[tuple[str, str, str], ObjectRef] = {}
    lineage: dict[tuple[str, str, str], IntentLineageEdge] = {}

    for event in ordered:
        if event.surface_state is not None:
            surface_state = event.surface_state
        patch = event.axis_patch.to_dict()
        for name, value in patch.items():
            if value is not None:
                axes[name] = value
        evidence.update(event.evidence_refs)
        for ref in event.object_refs:
            objects[(ref.object_type, ref.object_id, ref.role)] = ref
        for edge in event.lineage:
            lineage[(edge.relation, edge.source_intent_id, edge.target_intent_id)] = edge

    latest_valid = max(filtered, key=lambda e: (_parse_time(e.valid_at), e.event_id))
    latest_recorded = ordered[-1]
    return IntentState(
        intent_id=ordered[0].intent_id,
        surface_state=surface_state,
        recovered=axes["recovered"],
        accomplished=axes["accomplished"],
        verified=axes["verified"],
        externally_validated=axes["externally_validated"],
        closed=axes["closed"],
        latest_valid_at=latest_valid.valid_at,
        latest_recorded_at=latest_recorded.recorded_at,
        evidence_refs=tuple(sorted(evidence)),
        object_refs=tuple(
            ref.to_dict()
            for _, ref in sorted(objects.items(), key=lambda item: item[0])
        ),
        lineage=tuple(
            edge.to_dict()
            for _, edge in sorted(lineage.items(), key=lambda item: item[0])
        ),
        event_ids=tuple(event.event_id for event in ordered),
    )


def compare_intent_states(before: IntentState, after: IntentState) -> IntentStateDelta:
    if before.intent_id != after.intent_id:
        raise ValueError("intent_id mismatch")
    axis_names = (
        "recovered",
        "accomplished",
        "verified",
        "externally_validated",
        "closed",
    )
    changes: list[str] = []
    regressions: list[str] = []
    for name in axis_names:
        old = bool(getattr(before, name))
        new = bool(getattr(after, name))
        if old != new:
            changes.append(f"{name}:{old}->{new}")
            if old and not new:
                regressions.append(name)
    before_evidence = set(before.evidence_refs)
    after_evidence = set(after.evidence_refs)
    return IntentStateDelta(
        intent_id=before.intent_id,
        surface_transition=(
            (before.surface_state, after.surface_state)
            if before.surface_state != after.surface_state
            else None
        ),
        axis_changes=tuple(changes),
        regressions=tuple(regressions),
        evidence_added=tuple(sorted(after_evidence - before_evidence)),
        evidence_removed=tuple(sorted(before_evidence - after_evidence)),
    )


def source_observation_to_event(
    observation: SourceObservation,
    *,
    intent_id: str,
    event_id: str,
    recorded_at: str,
    surface_state: str | None = None,
) -> IntentEvent:
    evidence_refs = tuple(
        ref for ref in (
            observation.content_hash,
            observation.version_ref,
        )
        if ref
    )
    event = IntentEvent(
        event_id=event_id,
        intent_id=intent_id,
        valid_at=observation.observed_at,
        recorded_at=recorded_at,
        source_id=observation.source_id,
        event_kind="SOURCE_RECOVERED",
        surface_state=surface_state,
        axis_patch=IntentAxisPatch(recovered=True),
        object_refs=(
            ObjectRef("intent", intent_id, "subject"),
            ObjectRef("source", observation.source_id, "provenance"),
        ),
        evidence_refs=evidence_refs,
        note=observation.note,
    )
    errors = event.validate()
    if errors:
        raise ValueError("; ".join(errors))
    return event


def action_outcome_to_event(
    outcome: ActionOutcome,
    *,
    intent_id: str,
    event_id: str,
    valid_at: str,
    recorded_at: str,
    source_id: str = "jarvis-frontier-r2",
) -> IntentEvent:
    errors = outcome.validate()
    if errors:
        raise ValueError("; ".join(errors))
    accomplished = bool(outcome.success)
    verified = bool(outcome.success and outcome.verified_gain > 0)
    note_parts = [
        f"verified_gain={outcome.verified_gain}",
        f"rollback_used={outcome.rollback_used}",
    ]
    if outcome.residuals:
        note_parts.append("residuals=" + ",".join(outcome.residuals))
    if outcome.notes:
        note_parts.extend(outcome.notes)
    event = IntentEvent(
        event_id=event_id,
        intent_id=intent_id,
        valid_at=valid_at,
        recorded_at=recorded_at,
        source_id=source_id,
        event_kind="ACTION_OUTCOME",
        surface_state="realized" if outcome.success else "failed",
        axis_patch=IntentAxisPatch(
            accomplished=accomplished,
            verified=verified,
        ),
        object_refs=(
            ObjectRef("intent", intent_id, "subject"),
            ObjectRef("action", outcome.action_id, "outcome_of"),
        ),
        evidence_refs=tuple(outcome.evidence_refs),
        note="; ".join(note_parts),
    )
    errors = event.validate()
    if errors:
        raise ValueError("; ".join(errors))
    return event


def receipt_to_event(
    receipt: dict,
    *,
    intent_id: str,
    event_id: str,
    source_id: str,
    event_kind: str,
    valid_at: str,
    recorded_at: str,
    axis_patch: IntentAxisPatch,
    surface_state: str | None = None,
    object_refs: tuple[ObjectRef, ...] = (),
    evidence_refs: tuple[str, ...] = (),
    note: str = "",
) -> IntentEvent:
    if not isinstance(receipt, dict) or not receipt:
        raise ValueError("non-empty receipt dict required")
    receipt_digest = _canonical_digest(receipt)
    receipt_ref = f"sha256:{receipt_digest}"
    event = IntentEvent(
        event_id=event_id,
        intent_id=intent_id,
        valid_at=valid_at,
        recorded_at=recorded_at,
        source_id=source_id,
        event_kind=event_kind,
        surface_state=surface_state,
        axis_patch=axis_patch,
        object_refs=(
            ObjectRef("intent", intent_id, "subject"),
            ObjectRef("receipt", receipt_ref, "evidence"),
            *object_refs,
        ),
        evidence_refs=tuple(dict.fromkeys((*evidence_refs, receipt_ref))),
        note=note,
    )
    errors = event.validate()
    if errors:
        raise ValueError("; ".join(errors))
    return event


def _event_digest(events: tuple[IntentEvent, ...]) -> str:
    ordered = sorted(events, key=_event_sort_key)
    payload = [event.to_dict() for event in ordered]
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def compile_intent_reality(
    events: Iterable[IntentEvent],
    *,
    evidence_debt: IntentEvidenceDebt | None = None,
    as_known_at: str | None = None,
    valid_at: str | None = None,
) -> IntentRealityReceipt:
    rows = deduplicate_intent_events(events)
    if not rows:
        raise ValueError("events required")
    state = project_intent_state(
        rows,
        as_known_at=as_known_at,
        valid_at=valid_at,
    )
    if state is None:
        raise ValueError("no events visible under requested temporal cutoffs")
    evidence_debt_assessed = evidence_debt is not None
    debt = evidence_debt or IntentEvidenceDebt()
    errors = debt.validate()
    if errors:
        raise ValueError("; ".join(errors))
    r9 = debt.to_r9_debt()
    return IntentRealityReceipt(
        schema_version="jarvis-intent-reality-r12",
        state=state.to_dict(),
        evidence_debt=debt.to_dict(),
        evidence_debt_assessed=evidence_debt_assessed,
        r9_debt=r9.to_dict(),
        event_count=len(state.event_ids),
        event_digest=_event_digest(tuple(
            event for event in rows if event.event_id in set(state.event_ids)
        )),
        scientific_pass=False,
        authority_granted=False,
        boundaries=INTENT_REALITY_BOUNDARIES,
    )
