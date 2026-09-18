from __future__ import annotations

from dataclasses import asdict, dataclass

from .reality_loop import ExecutionLease, plan_digest


BLOCKING_KINDS = {
    "physical_action",
    "financial_commitment",
    "credential_or_secret_change",
    "scientific_promotion",
    "external_publication",
    "external_deployment",
}


@dataclass(frozen=True)
class ActionProposal:
    action_id: str
    action_kind: str
    plan: dict
    reversible: bool
    external_side_effect: bool
    rollback: str
    evidence_refs: tuple[str, ...] = ()
    confidence: float = 0.0
    expected_verified_gain: float = 0.0
    cost: float = 0.0
    risk: float = 0.0

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.action_id.strip():
            errors.append("action_id required")
        if not self.action_kind.strip():
            errors.append("action_kind required")
        if not isinstance(self.plan, dict) or not self.plan:
            errors.append("plan required")
        if not 0.0 <= self.confidence <= 1.0:
            errors.append("confidence must be in [0,1]")
        for name, value in (
            ("expected_verified_gain", self.expected_verified_gain),
            ("cost", self.cost),
            ("risk", self.risk),
        ):
            if value < 0:
                errors.append(f"{name} must be non-negative")
        if self.reversible and not self.rollback.strip():
            errors.append("rollback required for reversible autonomous action")
        return errors

    @property
    def utility(self) -> float:
        return self.expected_verified_gain - self.cost - self.risk


@dataclass(frozen=True)
class AutonomousDecision:
    action_id: str
    decision: str
    reason: str
    authority_granted: bool
    execution_lease: dict | None
    utility: float
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def decide_action(
    proposal: ActionProposal,
    *,
    executor_id: str = "jarvis-autonomy-r1",
    minimum_confidence: float = 0.80,
    minimum_utility: float = 0.0,
) -> AutonomousDecision:
    errors = proposal.validate()
    boundaries = (
        "AutonomousDecision != ScientificTruth",
        "ReversibleInternalActionOnly",
        "ExternalSideEffect -> REQUIRE_AUTHORIZATION",
        "IrreversibleAction -> REQUIRE_AUTHORIZATION",
        "ScientificPromotion -> REQUIRE_AUTHORIZATION",
        "NO_ACTION is admissible",
    )

    if errors:
        return AutonomousDecision(
            proposal.action_id, "HOLD_INVALID", "; ".join(errors), False, None,
            proposal.utility, boundaries,
        )

    if (
        proposal.action_kind in BLOCKING_KINDS
        or proposal.external_side_effect
        or not proposal.reversible
    ):
        return AutonomousDecision(
            proposal.action_id,
            "REQUIRE_AUTHORIZATION",
            "action exceeds bounded autonomous mandate",
            False,
            None,
            proposal.utility,
            boundaries,
        )

    if proposal.confidence < minimum_confidence:
        return AutonomousDecision(
            proposal.action_id,
            "HOLD_LOW_CONFIDENCE",
            "confidence below autonomous threshold",
            False,
            None,
            proposal.utility,
            boundaries,
        )

    if not proposal.evidence_refs:
        return AutonomousDecision(
            proposal.action_id,
            "HOLD_NO_EVIDENCE",
            "at least one evidence reference is required",
            False,
            None,
            proposal.utility,
            boundaries,
        )

    if proposal.utility <= minimum_utility:
        return AutonomousDecision(
            proposal.action_id,
            "NO_ACTION",
            "expected verified gain does not exceed bounded burden",
            False,
            None,
            proposal.utility,
            boundaries,
        )

    digest = plan_digest(proposal.plan)
    lease = ExecutionLease(
        plan_digest=digest,
        executor_id=executor_id,
        allowed_actions=(proposal.action_kind,),
        authorized=True,
        reversible_only=True,
    )
    return AutonomousDecision(
        proposal.action_id,
        "EXECUTE_AUTONOMOUSLY",
        "bounded reversible internal action passed evidence, confidence and utility gates",
        True,
        lease.to_dict(),
        proposal.utility,
        boundaries,
    )


def select_autonomous_action(
    proposals: tuple[ActionProposal, ...],
    *,
    executor_id: str = "jarvis-autonomy-r1",
) -> AutonomousDecision:
    decisions = [decide_action(p, executor_id=executor_id) for p in proposals]
    executable = [d for d in decisions if d.decision == "EXECUTE_AUTONOMOUSLY"]
    if executable:
        return max(executable, key=lambda d: (d.utility, d.action_id))

    authorization = [d for d in decisions if d.decision == "REQUIRE_AUTHORIZATION"]
    if authorization:
        return max(authorization, key=lambda d: (d.utility, d.action_id))

    if decisions:
        return max(decisions, key=lambda d: (d.utility, d.action_id))

    return AutonomousDecision(
        "NO_ACTION",
        "NO_ACTION",
        "no proposals supplied",
        False,
        None,
        0.0,
        (
            "AutonomousDecision != ScientificTruth",
            "NO_ACTION is admissible",
        ),
    )
