from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class WeeklyIntentSnapshot:
    intent_id: str
    surface_state: str
    recovered: bool = False
    accomplished: bool = False
    verified: bool = False
    externally_validated: bool = False
    closed: bool = False
    evidence_refs: tuple[str, ...] = ()
    lineage: tuple[tuple[str, str, str], ...] = ()
    evidence_debt_assessed: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class WeeklyIntentDelta:
    intent_id: str
    surface_transition: tuple[str, str] | None
    axis_changes: tuple[str, ...]
    regressions: tuple[str, ...]
    evidence_added: tuple[str, ...]
    evidence_removed: tuple[str, ...]
    lineage_added: tuple[tuple[str, str, str], ...]
    lineage_removed: tuple[tuple[str, str, str], ...]

    def to_dict(self) -> dict:
        return asdict(self)


def diff_snapshots(before: WeeklyIntentSnapshot, after: WeeklyIntentSnapshot) -> WeeklyIntentDelta:
    if before.intent_id != after.intent_id:
        raise ValueError("intent_id mismatch")
    axes = ("recovered", "accomplished", "verified", "externally_validated", "closed")
    changes = []
    regressions = []
    for name in axes:
        old = bool(getattr(before, name))
        new = bool(getattr(after, name))
        if old != new:
            changes.append(f"{name}:{old}->{new}")
            if old and not new:
                regressions.append(name)
    b_e = set(before.evidence_refs)
    a_e = set(after.evidence_refs)
    b_l = set(before.lineage)
    a_l = set(after.lineage)
    return WeeklyIntentDelta(
        intent_id=before.intent_id,
        surface_transition=(before.surface_state, after.surface_state)
        if before.surface_state != after.surface_state else None,
        axis_changes=tuple(changes),
        regressions=tuple(regressions),
        evidence_added=tuple(sorted(a_e-b_e)),
        evidence_removed=tuple(sorted(b_e-a_e)),
        lineage_added=tuple(sorted(a_l-b_l)),
        lineage_removed=tuple(sorted(b_l-a_l)),
    )


def supports_bitemporal_history() -> bool:
    return False


def supports_collision_safe_event_identity() -> bool:
    return False
