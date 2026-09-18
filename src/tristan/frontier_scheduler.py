from __future__ import annotations

from dataclasses import asdict, dataclass

from .frontier_loop import FrontierReceipt


@dataclass(frozen=True)
class ContinuationDirective:
    mode: str
    reason: str
    wake_condition: str
    preserve_context: bool
    autonomous: bool
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def next_continuation_directive(receipt: FrontierReceipt) -> ContinuationDirective:
    boundaries = (
        "Dormant != Terminated",
        "Continuation != InfinitePermission",
        "BlockedPath != BlockedSearch",
        "NewEvidenceMayWakeP0",
        "AuthorityBoundaryMustNotBeBypassed",
    )

    if receipt.status == "CHECKPOINT":
        return ContinuationDirective(
            mode="RESUME_FRONTIER",
            reason="bounded work quantum completed",
            wake_condition="immediate",
            preserve_context=True,
            autonomous=True,
            boundaries=boundaries,
        )

    if receipt.status == "P0":
        return ContinuationDirective(
            mode="DORMANT_SCAN",
            reason="no currently admissible verified-gain action",
            wake_condition="new evidence, changed dependency, new candidate, or changed constraint",
            preserve_context=True,
            autonomous=True,
            boundaries=boundaries,
        )

    if receipt.status == "HOLD_REPEAT_LOOP":
        return ContinuationDirective(
            mode="DIVERSIFY_SEARCH",
            reason="repetition firewall fired",
            wake_condition="generate a structurally different candidate set before resuming",
            preserve_context=True,
            autonomous=True,
            boundaries=boundaries,
        )

    if receipt.status == "HOLD_EXECUTION_FAILURE":
        return ContinuationDirective(
            mode="FAILURE_ANALYSIS",
            reason="last selected action failed",
            wake_condition="record failure evidence and generate a bounded alternative",
            preserve_context=True,
            autonomous=True,
            boundaries=boundaries,
        )

    if receipt.status == "HOLD_AUTHORITY_BOUNDARY":
        return ContinuationDirective(
            mode="SEARCH_WITHIN_AUTHORITY",
            reason="best observed path crossed an authority boundary",
            wake_condition="find an internal reversible alternative or receive explicit authorization",
            preserve_context=True,
            autonomous=True,
            boundaries=boundaries,
        )

    return ContinuationDirective(
        mode="REASSESS",
        reason=f"unclassified frontier state: {receipt.status}",
        wake_condition="new evidence or policy change",
        preserve_context=True,
        autonomous=True,
        boundaries=boundaries,
    )
