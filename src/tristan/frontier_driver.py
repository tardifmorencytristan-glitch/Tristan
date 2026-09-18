from __future__ import annotations

from pathlib import Path

from .autonomous_decision import ActionProposal
from .frontier_worker import WorkerOutcome, WorkerState
from .verify import verify_repository


def repository_proposals(state: WorkerState) -> tuple[ActionProposal, ...]:
    if state.last_status in {"NEW", "DORMANT_SCAN", "FAILURE_ANALYSIS", "HOLD_NO_HANDLER"}:
        return (
            ActionProposal(
                action_id=f"verify-repository-g{state.generation + 1}",
                action_kind="verify_repository",
                plan={"operation": "verify_repository", "generation": state.generation + 1},
                reversible=True,
                external_side_effect=False,
                rollback="discard verification receipt",
                evidence_refs=tuple(state.evidence_refs) or ("repository-state",),
                confidence=1.0,
                expected_verified_gain=1.0,
                cost=0.05,
                risk=0.0,
            ),
        )
    return ()


def verify_repository_handler(root: str | Path):
    root = Path(root)

    def _handler(proposal: ActionProposal, state: WorkerState) -> WorkerOutcome:
        result = verify_repository(root)
        status = result["status"]
        evidence = (f"verify:{state.cycle_count}:{status}",)
        if status == "PASS":
            return WorkerOutcome(
                success=True,
                verified_gain=1.0,
                evidence_refs=evidence,
                residuals=("scan-for-new-work",),
                note="repository verification passed",
            )
        return WorkerOutcome(
            success=False,
            verified_gain=0.0,
            evidence_refs=evidence,
            residuals=tuple(result.get("errors", ())),
            note="repository verification failed",
        )

    return _handler
