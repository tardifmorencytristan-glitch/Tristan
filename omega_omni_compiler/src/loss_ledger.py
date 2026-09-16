from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class LossEntry:
    transform_id: str
    item: str
    state: str  # PRESERVED | LOST | INFERRED | RECONSTRUCTED | UNKNOWN
    detail: str = ""


VALID_STATES = {"PRESERVED", "LOST", "INFERRED", "RECONSTRUCTED", "UNKNOWN"}


def validate_loss_entries(entries: list[LossEntry]) -> list[str]:
    errors = []
    for e in entries:
        if e.state not in VALID_STATES:
            errors.append(f"{e.transform_id}:{e.item}: invalid state {e.state}")
        if not e.transform_id or not e.item:
            errors.append("transform_id and item required")
    return errors


def summarize(entries: list[LossEntry]) -> dict:
    errors = validate_loss_entries(entries)
    if errors:
        raise ValueError(errors)
    counts = {s: 0 for s in VALID_STATES}
    for e in entries:
        counts[e.state] += 1
    return {"counts": counts, "entries": [asdict(e) for e in entries]}
