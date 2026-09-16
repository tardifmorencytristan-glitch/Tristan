from __future__ import annotations

from dataclasses import dataclass

from .compliance import ComplianceMatrix


@dataclass(frozen=True)
class BidDraft:
    status: str
    title: str
    summary: str
    evidence_appendix: tuple[str, ...]
    blockers: tuple[str, ...]


def compile_bid_draft(matrix: ComplianceMatrix) -> BidDraft:
    if matrix.status != "SUPPORTED_FOR_DRAFT":
        blockers = tuple(f"{r.requirement_key}:{r.result}" for r in matrix.blockers)
        return BidDraft(
            "HOLD",
            matrix.opportunity.title,
            "Draft withheld because mandatory requirements are unresolved or insufficiently evidenced.",
            (),
            blockers or (matrix.status,),
        )
    receipts: list[str] = []
    lines: list[str] = []
    for row in matrix.rows:
        if row.capability_name:
            lines.append(f"{row.description} -> {row.capability_name} [{row.capability_status}]")
            receipts.extend(row.evidence_receipts)
    return BidDraft(
        "DRAFT_ONLY",
        matrix.opportunity.title,
        "\n".join(lines),
        tuple(dict.fromkeys(receipts)),
        (),
    )
