from __future__ import annotations

from dataclasses import asdict, dataclass

from .epistemic_memory import MemoryRecord
from .ood_court import OODCourtReceipt


@dataclass(frozen=True)
class TransferReceipt:
    record_id: str
    source_context: tuple[str, ...]
    target_context: tuple[str, ...]
    status: str
    eligible: bool
    authority_granted: bool
    reasons: tuple[str, ...]
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def evaluate_transfer(
    record: MemoryRecord,
    target_context: tuple[str, ...],
    ood_receipt: OODCourtReceipt,
) -> TransferReceipt:
    errors = record.validate()
    if errors:
        raise ValueError("; ".join(errors))
    if not target_context:
        raise ValueError("target_context required")

    reasons: list[str] = []
    target = set(target_context)
    declared_scope = set(record.transfer_scope)

    if not declared_scope or not target <= declared_scope:
        reasons.append("target outside declared transfer_scope")
    if not ood_receipt.transfer_evidence:
        reasons.append("OOD court did not produce transfer evidence")
    if ood_receipt.overlap_detected:
        reasons.append("training overlap detected")

    eligible = not reasons
    return TransferReceipt(
        record_id=record.record_id,
        source_context=record.context_tags,
        target_context=target_context,
        status="ELIGIBLE_FOR_CONTEXTUAL_RETEST" if eligible else "HOLD_TRANSFER",
        eligible=eligible,
        authority_granted=False,
        reasons=tuple(reasons),
        boundaries=(
            "EligibleForRetest != Promoted",
            "LocalMechanism != GlobalMechanism",
            "TransferEvidence != ScientificTruth",
            "TransferGate != ExecutionAuthority",
        ),
    )
