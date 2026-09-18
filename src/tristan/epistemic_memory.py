from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum


class MemoryKind(str, Enum):
    POSITIVE = "M+"
    NEGATIVE = "M-"
    UNKNOWN = "M?"
    DELTA = "M-delta"


@dataclass(frozen=True)
class MemoryRecord:
    record_id: str
    kind: MemoryKind
    context_tags: tuple[str, ...]
    mechanism: str
    outcome: str
    confidence: float
    evidence_ids: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()
    transfer_scope: tuple[str, ...] = ()

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.record_id.strip():
            errors.append("record_id required")
        if not self.mechanism.strip():
            errors.append("mechanism required")
        if not self.outcome.strip():
            errors.append("outcome required")
        if not 0.0 <= self.confidence <= 1.0:
            errors.append("confidence must be in [0,1]")
        if not self.provenance:
            errors.append("provenance required")
        return errors

    def to_dict(self) -> dict:
        data = asdict(self)
        data["kind"] = self.kind.value
        return data


class EpistemicMemory:
    """Context-bound memory with explicit non-transfer by default."""

    def __init__(self) -> None:
        self._records: list[MemoryRecord] = []

    def append(self, record: MemoryRecord) -> None:
        errors = record.validate()
        if errors:
            raise ValueError("; ".join(errors))
        if any(existing.record_id == record.record_id for existing in self._records):
            raise ValueError("duplicate record_id")
        self._records.append(record)

    def records(self) -> tuple[MemoryRecord, ...]:
        return tuple(self._records)

    def query(self, context_tags: tuple[str, ...]) -> tuple[MemoryRecord, ...]:
        requested = set(context_tags)
        matches: list[MemoryRecord] = []
        for record in self._records:
            local = set(record.context_tags)
            transferable = set(record.transfer_scope)
            if requested <= local or (transferable and requested <= transferable):
                matches.append(record)
        return tuple(matches)

    def unresolved_for(self, context_tags: tuple[str, ...]) -> bool:
        return len(self.query(context_tags)) == 0


def delta_record(
    *,
    record_id: str,
    context_tags: tuple[str, ...],
    mechanism: str,
    before: float,
    after: float,
    metric: str,
    provenance: tuple[str, ...],
) -> MemoryRecord:
    delta = after - before
    return MemoryRecord(
        record_id=record_id,
        kind=MemoryKind.DELTA,
        context_tags=context_tags,
        mechanism=mechanism,
        outcome=f"{metric}_delta={delta:+.12g}",
        confidence=1.0,
        provenance=provenance,
    )
