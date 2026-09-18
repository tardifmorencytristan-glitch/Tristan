from __future__ import annotations

"""Proof-bounded compiler for paid open-source opportunities.

AdvertisedReward != Revenue.
PriorityScore != ExpectedValue.
Actionable != Authorized.
AIAllowed != ContributionAccepted.
NO_ACTION is admissible.
"""

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
from typing import Iterable, Sequence

PROTOCOL = "TRISTAN-OPPORTUNITY-COMPILER-R1"
AI_POLICIES = {"ALLOWED", "RESTRICTED", "UNKNOWN", "PROHIBITED"}


def _finite_nonnegative(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and non-negative")
    return value


def _unit(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{name} must be finite and in [0,1]")
    return value


def _clean(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(str(v).strip() for v in values if str(v).strip())


def _digest(payload: object) -> str:
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(body.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class OpportunityObservation:
    opportunity_id: str
    source: str
    source_url: str
    repository: str = ""
    reward_amount: float = 0.0
    currency: str = ""
    is_open: bool = False
    open_verified: bool = False
    reward_current_verified: bool = False
    payout_path_verified: bool = False
    claim_rules_verified: bool = False
    claim_before_work: bool = False
    claim_available: bool = True
    license_verified: bool = False
    license_id: str = ""
    ai_policy: str = "UNKNOWN"
    agent_execution_planned: bool = True
    expected_hours: float = 1.0
    human_minutes: float = 0.0
    competition_score: float = 0.0
    risk: float = 0.0
    evidence_quality: float = 0.0
    reuse_potential: float = 0.0
    capability_gain: float = 0.0
    deadline_urgent: bool = False
    requires_hardware: bool = False
    hardware_available: bool = False
    requires_real_funds: bool = False
    likely_files: tuple[str, ...] = ()
    requirements: tuple[str, ...] = ()
    test_plan: tuple[str, ...] = ()
    implementation_steps: tuple[str, ...] = ()
    claim_steps: tuple[str, ...] = ()
    submission_steps: tuple[str, ...] = ()
    reusable_components: tuple[str, ...] = ()
    no_action_conditions: tuple[str, ...] = ()

    def normalized(self) -> "OpportunityObservation":
        oid = self.opportunity_id.strip()
        source = self.source.strip()
        url = self.source_url.strip()
        if not oid or not source or not url:
            raise ValueError("opportunity_id, source and source_url are required")
        ai_policy = self.ai_policy.strip().upper()
        if ai_policy not in AI_POLICIES:
            raise ValueError(f"unsupported ai_policy: {ai_policy}")
        expected_hours = _finite_nonnegative(self.expected_hours, "expected_hours")
        if expected_hours <= 0:
            raise ValueError("expected_hours must be greater than zero")
        return OpportunityObservation(
            opportunity_id=oid,
            source=source,
            source_url=url,
            repository=self.repository.strip(),
            reward_amount=_finite_nonnegative(self.reward_amount, "reward_amount"),
            currency=self.currency.strip().upper(),
            is_open=bool(self.is_open),
            open_verified=bool(self.open_verified),
            reward_current_verified=bool(self.reward_current_verified),
            payout_path_verified=bool(self.payout_path_verified),
            claim_rules_verified=bool(self.claim_rules_verified),
            claim_before_work=bool(self.claim_before_work),
            claim_available=bool(self.claim_available),
            license_verified=bool(self.license_verified),
            license_id=self.license_id.strip(),
            ai_policy=ai_policy,
            agent_execution_planned=bool(self.agent_execution_planned),
            expected_hours=expected_hours,
            human_minutes=_finite_nonnegative(self.human_minutes, "human_minutes"),
            competition_score=_unit(self.competition_score, "competition_score"),
            risk=_unit(self.risk, "risk"),
            evidence_quality=_unit(self.evidence_quality, "evidence_quality"),
            reuse_potential=_unit(self.reuse_potential, "reuse_potential"),
            capability_gain=_unit(self.capability_gain, "capability_gain"),
            deadline_urgent=bool(self.deadline_urgent),
            requires_hardware=bool(self.requires_hardware),
            hardware_available=bool(self.hardware_available),
            requires_real_funds=bool(self.requires_real_funds),
            likely_files=_clean(self.likely_files),
            requirements=_clean(self.requirements),
            test_plan=_clean(self.test_plan),
            implementation_steps=_clean(self.implementation_steps),
            claim_steps=_clean(self.claim_steps),
            submission_steps=_clean(self.submission_steps),
            reusable_components=_clean(self.reusable_components),
            no_action_conditions=_clean(self.no_action_conditions),
        )


@dataclass(frozen=True)
class OpportunityDecision:
    opportunity_id: str
    repository: str
    state: str
    priority_score: float
    reward_per_hour: float
    blockers: tuple[str, ...]
    claim_before_work: bool
    claim_steps: tuple[str, ...]
    likely_files: tuple[str, ...]
    requirements: tuple[str, ...]
    test_plan: tuple[str, ...]
    implementation_steps: tuple[str, ...]
    submission_steps: tuple[str, ...]
    reusable_components: tuple[str, ...]
    no_action_conditions: tuple[str, ...]
    advertised_reward_is_revenue: bool
    authority_granted: bool

    def to_dict(self) -> dict:
        return asdict(self)


def priority_score(observation: OpportunityObservation) -> float:
    """Non-probabilistic routing heuristic, not expected monetary value."""
    o = observation.normalized()
    reward_per_hour = o.reward_amount / o.expected_hours
    regenerative = 1.0 + 0.45 * o.reuse_potential + 0.45 * o.capability_gain
    urgency = 1.12 if o.deadline_urgent else 1.0
    evidence = 0.30 + 0.70 * o.evidence_quality
    human_burden = 1.0 + o.human_minutes / max(60.0 * o.expected_hours, 1.0)
    competition_burden = 1.0 + 3.0 * o.competition_score
    risk_burden = 1.0 + 2.0 * o.risk
    score = reward_per_hour * regenerative * urgency * evidence
    score /= human_burden * competition_burden * risk_burden
    return round(max(0.0, score), 6)


def evaluate_opportunity(observation: OpportunityObservation) -> OpportunityDecision:
    o = observation.normalized()
    blockers: list[str] = []
    state = "ACTIONABLE"

    if o.open_verified and not o.is_open:
        state = "NO_ACTION_CLOSED"
        blockers.append("SOURCE_VERIFIED_CLOSED")
    elif not o.open_verified:
        state = "HOLD_OPEN_STATE"
        blockers.append("OPEN_STATE_NOT_VERIFIED")
    elif o.reward_amount <= 0 or not o.reward_current_verified:
        state = "HOLD_REWARD"
        blockers.append("CURRENT_REWARD_NOT_VERIFIED")
    elif not o.currency:
        state = "HOLD_PAYOUT"
        blockers.append("PAYOUT_CURRENCY_UNKNOWN")
    elif not o.payout_path_verified:
        state = "HOLD_PAYOUT"
        blockers.append("PAYOUT_PATH_NOT_VERIFIED")
    elif not o.claim_rules_verified:
        state = "HOLD_CLAIM_RULES"
        blockers.append("CLAIM_RULES_NOT_VERIFIED")
    elif o.claim_before_work and not o.claim_available:
        state = "NO_ACTION_CLAIM_UNAVAILABLE"
        blockers.append("CLAIM_REQUIRED_BEFORE_WORK_BUT_UNAVAILABLE")
    elif not o.license_verified:
        state = "HOLD_LICENSE"
        blockers.append("LICENSE_NOT_VERIFIED")
    elif not o.requirements or not o.test_plan or not o.implementation_steps or not o.submission_steps:
        state = "HOLD_SCOPE"
        blockers.append("EXECUTION_PACKET_INCOMPLETE")
    elif o.agent_execution_planned and o.ai_policy == "PROHIBITED":
        state = "NO_ACTION_AI_PROHIBITED"
        blockers.append("AI_AGENT_CONTRIBUTION_PROHIBITED")
    elif o.agent_execution_planned and o.ai_policy == "UNKNOWN":
        state = "HOLD_AI_POLICY"
        blockers.append("AI_AGENT_POLICY_NOT_VERIFIED")
    elif o.agent_execution_planned and o.ai_policy == "RESTRICTED":
        state = "HOLD_AI_RESTRICTION"
        blockers.append("AI_AGENT_RESTRICTIONS_REQUIRE_MANUAL_REVIEW")
    elif o.requires_real_funds:
        state = "NO_ACTION_RESOURCE_RISK"
        blockers.append("REAL_FUNDS_REQUIRED_FOR_VALIDATION")
    elif o.requires_hardware and not o.hardware_available:
        state = "HOLD_HARDWARE"
        blockers.append("REQUIRED_HARDWARE_NOT_AVAILABLE")
    elif o.competition_score >= 0.85 or o.expected_hours >= 32:
        state = "CANARY_ONLY"
        blockers.append("HIGH_BURDEN_REQUIRES_DIFFERENTIAL_CANARY")

    generated_no_action = (
        "source closes or reward is withdrawn",
        "claim slot becomes unavailable",
        "licensing or contribution terms become incompatible",
        "AI-agent use is prohibited for the planned execution mode",
        "a competing implementation eliminates the distinct residual",
        "required tests cannot be reproduced without unavailable hardware or unsafe real-fund exposure",
        "measured effort/value falls below the current portfolio frontier",
    )

    return OpportunityDecision(
        opportunity_id=o.opportunity_id,
        repository=o.repository,
        state=state,
        priority_score=priority_score(o),
        reward_per_hour=round(o.reward_amount / o.expected_hours, 6),
        blockers=tuple(blockers),
        claim_before_work=o.claim_before_work,
        claim_steps=o.claim_steps,
        likely_files=o.likely_files,
        requirements=o.requirements,
        test_plan=o.test_plan,
        implementation_steps=o.implementation_steps,
        submission_steps=o.submission_steps,
        reusable_components=o.reusable_components,
        no_action_conditions=tuple(dict.fromkeys(o.no_action_conditions + generated_no_action)),
        advertised_reward_is_revenue=False,
        authority_granted=False,
    )


@dataclass(frozen=True)
class OpportunityPortfolio:
    protocol: str
    decisions: tuple[OpportunityDecision, ...]
    actionable_ids: tuple[str, ...]
    canary_ids: tuple[str, ...]
    hold_ids: tuple[str, ...]
    no_action_ids: tuple[str, ...]
    advertised_reward_total: float
    realized_revenue_total: float
    authority_self_granted: bool
    receipt_sha256: str

    def to_dict(self) -> dict:
        data = asdict(self)
        data["decisions"] = [d.to_dict() for d in self.decisions]
        return data


def compile_portfolio(observations: Sequence[OpportunityObservation]) -> OpportunityPortfolio:
    normalized = tuple(o.normalized() for o in observations)
    decisions = tuple(
        sorted(
            (evaluate_opportunity(o) for o in normalized),
            key=lambda d: (
                0 if d.state == "ACTIONABLE" else 1 if d.state == "CANARY_ONLY" else 2,
                -d.priority_score,
                d.opportunity_id,
            ),
        )
    )
    actionable = tuple(d.opportunity_id for d in decisions if d.state == "ACTIONABLE")
    canary = tuple(d.opportunity_id for d in decisions if d.state == "CANARY_ONLY")
    holds = tuple(d.opportunity_id for d in decisions if d.state.startswith("HOLD_"))
    no_action = tuple(d.opportunity_id for d in decisions if d.state.startswith("NO_ACTION_"))
    advertised = sum(o.reward_amount for o in normalized if o.reward_current_verified and o.is_open)
    payload = {
        "protocol": PROTOCOL,
        "decisions": [d.to_dict() for d in decisions],
        "actionable_ids": actionable,
        "canary_ids": canary,
        "hold_ids": holds,
        "no_action_ids": no_action,
        "advertised_reward_total": advertised,
        "realized_revenue_total": 0.0,
        "authority_self_granted": False,
    }
    return OpportunityPortfolio(
        protocol=PROTOCOL,
        decisions=decisions,
        actionable_ids=actionable,
        canary_ids=canary,
        hold_ids=holds,
        no_action_ids=no_action,
        advertised_reward_total=round(advertised, 6),
        realized_revenue_total=0.0,
        authority_self_granted=False,
        receipt_sha256=_digest(payload),
    )
