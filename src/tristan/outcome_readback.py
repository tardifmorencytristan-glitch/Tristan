from __future__ import annotations

from .epistemic_memory import MemoryKind, MemoryRecord
from .reality_loop import RealityReceipt


def memory_from_reality(
    *,
    record_id: str,
    context_tags: tuple[str, ...],
    mechanism: str,
    reality: RealityReceipt,
    evidence_ids: tuple[str, ...],
    provenance: tuple[str, ...],
    transfer_scope: tuple[str, ...] = (),
) -> MemoryRecord:
    if not evidence_ids:
        raise ValueError("evidence_ids required for outcome readback")
    if not provenance:
        raise ValueError("provenance required for outcome readback")

    if reality.status == "PASS" and reality.reality_gap == 0:
        kind = MemoryKind.POSITIVE
        confidence = 1.0
        outcome = "reality_pass"
    elif reality.status == "RESIDUAL":
        kind = MemoryKind.NEGATIVE
        confidence = max(0.0, min(1.0, reality.reality_gap))
        outcome = f"reality_residual={reality.reality_gap:.12g}"
    else:
        kind = MemoryKind.UNKNOWN
        confidence = 0.0
        outcome = f"unresolved_status={reality.status}"

    return MemoryRecord(
        record_id=record_id,
        kind=kind,
        context_tags=context_tags,
        mechanism=mechanism,
        outcome=outcome,
        confidence=confidence,
        evidence_ids=evidence_ids,
        provenance=provenance,
        transfer_scope=transfer_scope,
    )
