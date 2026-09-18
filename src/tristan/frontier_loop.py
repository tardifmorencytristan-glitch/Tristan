from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Callable

from .autonomous_decision import (
    ActionProposal,
    AutonomousDecision,
    select_autonomous_action,
)


@dataclass(frozen=True)
class FrontierPolicy:
    max_steps_per_checkpoint: int = 64
    max_same_action_repeats: int = 2
    max_stagnant_steps: int = 2
    minimum_verified_gain: float = 0.0

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.max_steps_per_checkpoint < 1:
            errors.append("max_steps_per_checkpoint must be >= 1")
        if self.max_same_action_repeats < 1:
            errors.append("max_same_action_repeats must be >= 1")
        if self.max_stagnant_steps < 1:
            errors.append("max_stagnant_steps must be >= 1")
        if self.minimum_verified_gain < 0:
            errors.append("minimum_verified_gain must be non-negative")
        return errors


@dataclass(frozen=True)
class FrontierContext:
    seed: dict
    step_index: int = 0
    completed_action_ids: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    cumulative_verified_gain: float = 0.0
    residuals: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ActionOutcome:
    action_id: str
    success: bool
    verified_gain: float
    evidence_refs: tuple[str, ...]
    residuals: tuple[str, ...] = ()
    rollback_used: bool = False
    notes: tuple[str, ...] = ()

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.action_id.strip():
            errors.append("action_id required")
        if self.verified_gain < 0:
            errors.append("verified_gain must be non-negative")
        if self.success and not self.evidence_refs:
            errors.append("successful outcome requires evidence_refs")
        return errors

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class FrontierStep:
    step_index: int
    decision: dict
    outcome: dict | None
    residuals_after: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class FrontierReceipt:
    schema_version: str
    status: str
    stop_reason: str
    context: dict
    steps: tuple[dict, ...]
    resume_required: bool
    authority_granted: bool
    scientific_pass: bool
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


Proposer = Callable[[FrontierContext], tuple[ActionProposal, ...]]
Executor = Callable[[ActionProposal, AutonomousDecision, FrontierContext], ActionOutcome]


def _find_proposal(
    proposals: tuple[ActionProposal, ...],
    action_id: str,
) -> ActionProposal:
    for proposal in proposals:
        if proposal.action_id == action_id:
            return proposal
    raise ValueError("selected action_id not found in proposals")


def run_frontier_loop(
    *,
    seed: dict,
    propose: Proposer,
    execute: Executor,
    policy: FrontierPolicy | None = None,
    executor_id: str = "jarvis-frontier-r2",
) -> FrontierReceipt:
    policy = policy or FrontierPolicy()
    errors = policy.validate()
    if errors:
        raise ValueError("; ".join(errors))
    if not isinstance(seed, dict) or not seed:
        raise ValueError("non-empty seed required")

    context = FrontierContext(seed=dict(seed))
    steps: list[dict] = []
    repeat_counts: dict[str, int] = {}
    stagnant_steps = 0

    boundaries = (
        "Continuation != InfinitePermission",
        "EveryStepRequiresFreshDecision",
        "EverySuccessRequiresEvidence",
        "ExternalOrIrreversibleAction -> REQUIRE_AUTHORIZATION",
        "ScientificPromotion -> REQUIRE_AUTHORIZATION",
        "RepeatedNoGain -> P0",
        "Checkpoint != Completion",
        "NO_ACTION is admissible",
    )

    for step_index in range(policy.max_steps_per_checkpoint):
        proposals = propose(context)
        decision = select_autonomous_action(
            proposals,
            executor_id=executor_id,
        )

        if decision.decision != "EXECUTE_AUTONOMOUSLY":
            status = {
                "REQUIRE_AUTHORIZATION": "HOLD_AUTHORITY_BOUNDARY",
                "NO_ACTION": "P0",
            }.get(decision.decision, "HOLD")
            return FrontierReceipt(
                schema_version="tristan-frontier-loop-r2",
                status=status,
                stop_reason=decision.decision,
                context=context.to_dict(),
                steps=tuple(steps),
                resume_required=False,
                authority_granted=False,
                scientific_pass=False,
                boundaries=boundaries,
            )

        repeat_counts[decision.action_id] = repeat_counts.get(decision.action_id, 0) + 1
        if repeat_counts[decision.action_id] > policy.max_same_action_repeats:
            return FrontierReceipt(
                schema_version="tristan-frontier-loop-r2",
                status="HOLD_REPEAT_LOOP",
                stop_reason="same action repeated beyond bounded limit",
                context=context.to_dict(),
                steps=tuple(steps),
                resume_required=False,
                authority_granted=False,
                scientific_pass=False,
                boundaries=boundaries,
            )

        proposal = _find_proposal(proposals, decision.action_id)
        outcome = execute(proposal, decision, context)
        outcome_errors = outcome.validate()
        if outcome_errors:
            raise ValueError("; ".join(outcome_errors))
        if outcome.action_id != decision.action_id:
            raise ValueError("outcome action_id must match selected action")

        next_evidence = tuple(dict.fromkeys(context.evidence_refs + outcome.evidence_refs))
        next_residuals = tuple(dict.fromkeys(outcome.residuals))
        next_context = FrontierContext(
            seed=context.seed,
            step_index=step_index + 1,
            completed_action_ids=context.completed_action_ids + (outcome.action_id,),
            evidence_refs=next_evidence,
            cumulative_verified_gain=context.cumulative_verified_gain + outcome.verified_gain,
            residuals=next_residuals,
        )
        steps.append(
            FrontierStep(
                step_index=step_index,
                decision=decision.to_dict(),
                outcome=outcome.to_dict(),
                residuals_after=next_residuals,
            ).to_dict()
        )

        if not outcome.success:
            return FrontierReceipt(
                schema_version="tristan-frontier-loop-r2",
                status="HOLD_EXECUTION_FAILURE",
                stop_reason="selected action failed",
                context=next_context.to_dict(),
                steps=tuple(steps),
                resume_required=False,
                authority_granted=False,
                scientific_pass=False,
                boundaries=boundaries,
            )

        if outcome.verified_gain <= policy.minimum_verified_gain:
            stagnant_steps += 1
        else:
            stagnant_steps = 0

        context = next_context

        if stagnant_steps >= policy.max_stagnant_steps:
            return FrontierReceipt(
                schema_version="tristan-frontier-loop-r2",
                status="P0",
                stop_reason="no further verified gain observed",
                context=context.to_dict(),
                steps=tuple(steps),
                resume_required=False,
                authority_granted=False,
                scientific_pass=False,
                boundaries=boundaries,
            )

    return FrontierReceipt(
        schema_version="tristan-frontier-loop-r2",
        status="CHECKPOINT",
        stop_reason="bounded checkpoint reached; regenerate proposals and resume",
        context=context.to_dict(),
        steps=tuple(steps),
        resume_required=True,
        authority_granted=False,
        scientific_pass=False,
        boundaries=boundaries,
    )
