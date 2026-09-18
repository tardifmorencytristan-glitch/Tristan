from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

from .adaptive_router import CapabilityCandidate, select_minimal_coalition


ULTRA_CLOSURE_BOUNDARIES = (
    "Generated != Verified",
    "MissionGenome != Execution",
    "CapabilityCrystal != ScientificPASS",
    "PortfolioDecision != MergeAuthority",
    "RegimeSelection != Permission",
    "GenerationThrottle != Truth",
    "Capability != Authority",
    "NO_ACTION is admissible",
)


@dataclass(frozen=True)
class DebtVector:
    evidence: float = 0.0
    complexity: float = 0.0
    freshness: float = 0.0
    merge: float = 0.0
    maintenance: float = 0.0
    reality: float = 0.0
    authority: float = 0.0

    def validate(self) -> list[str]:
        errors: list[str] = []
        for name, value in asdict(self).items():
            if value < 0:
                errors.append(f"{name} debt must be non-negative")
        return errors

    @property
    def total(self) -> float:
        return sum(asdict(self).values())

    def to_dict(self) -> dict:
        data = asdict(self)
        data["total"] = self.total
        return data


@dataclass(frozen=True)
class MissionGenome:
    mission_id: str
    goal: str
    residuals: tuple[str, ...]
    context_ids: tuple[str, ...]
    required_capabilities: tuple[str, ...]
    constraints: tuple[str, ...]
    authority_scope: tuple[str, ...]
    evidence_contract: tuple[str, ...]
    candidate_origins: tuple[str, ...]
    falsifiers: tuple[str, ...]
    stop_rules: tuple[str, ...]
    rollback: str
    debt: DebtVector

    def validate(self) -> list[str]:
        errors = self.debt.validate()
        for name, value in (
            ("mission_id", self.mission_id),
            ("goal", self.goal),
            ("rollback", self.rollback),
        ):
            if not value.strip():
                errors.append(f"{name} required")
        if not self.required_capabilities:
            errors.append("required_capabilities required")
        if not self.evidence_contract:
            errors.append("evidence_contract required")
        if not self.stop_rules:
            errors.append("stop_rules required")
        if set(self.candidate_origins) != {
            "TRISTAN", "SIMPLE", "EXTERNAL", "HYBRID", "NO_ACTION"
        }:
            errors.append("candidate_origins must implement the five-origin court")
        return errors

    def to_dict(self) -> dict:
        data = asdict(self)
        data["debt"] = self.debt.to_dict()
        return data


@dataclass(frozen=True)
class CapabilityCrystal:
    capability_id: str
    interface: str
    domain: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    dependencies: tuple[str, ...]
    limits: tuple[str, ...]
    falsifiers: tuple[str, ...]
    regeneration_recipe: tuple[str, ...]
    right_to_lose: bool
    provenance: tuple[str, ...]
    version: str
    status: str = "PROVISIONAL_CRYSTAL"

    def validate(self) -> list[str]:
        errors: list[str] = []
        for name, value in (
            ("capability_id", self.capability_id),
            ("interface", self.interface),
            ("version", self.version),
        ):
            if not value.strip():
                errors.append(f"{name} required")
        if not self.domain:
            errors.append("domain required")
        if not self.evidence_ids:
            errors.append("evidence_ids required")
        if not self.limits:
            errors.append("limits required")
        if not self.falsifiers:
            errors.append("falsifiers required")
        if not self.regeneration_recipe:
            errors.append("regeneration_recipe required")
        if not self.provenance:
            errors.append("provenance required")
        if not self.right_to_lose:
            errors.append("right_to_lose must remain true")
        return errors

    @property
    def crystal_ready(self) -> bool:
        return not self.validate()

    def to_dict(self) -> dict:
        data = asdict(self)
        data["crystal_ready"] = self.crystal_ready
        data["scientific_pass"] = False
        return data


@dataclass(frozen=True)
class ProofCarryingResearchObject:
    object_id: str
    claims: tuple[str, ...]
    data_refs: tuple[str, ...]
    code_refs: tuple[str, ...]
    environment_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    negative_results: tuple[str, ...]
    falsifiers: tuple[str, ...]
    provenance: tuple[str, ...]
    limitations: tuple[str, ...]
    replication_state: str

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.object_id.strip():
            errors.append("object_id required")
        if not self.claims:
            errors.append("claims required")
        if not self.provenance:
            errors.append("provenance required")
        if not self.limitations:
            errors.append("limitations required")
        if not self.replication_state.strip():
            errors.append("replication_state required")
        return errors

    def to_dict(self) -> dict:
        data = asdict(self)
        data["scientific_pass"] = False
        return data


@dataclass(frozen=True)
class GenerationThrottleReceipt:
    generation_rate: float
    verification_rate: float
    closure_rate: float
    debt_absorption_rate: float
    generation_budget_multiplier: float
    closure_budget_multiplier: float
    status: str
    reason: str

    def to_dict(self) -> dict:
        return asdict(self)


def generation_throttle(
    *,
    generation_rate: float,
    verification_rate: float,
    closure_rate: float,
    debt_absorption_rate: float,
) -> GenerationThrottleReceipt:
    rates = (
        generation_rate, verification_rate, closure_rate, debt_absorption_rate
    )
    if any(rate < 0 for rate in rates):
        raise ValueError("rates must be non-negative")
    sustainable = verification_rate + closure_rate + debt_absorption_rate
    if generation_rate <= sustainable:
        return GenerationThrottleReceipt(
            generation_rate,
            verification_rate,
            closure_rate,
            debt_absorption_rate,
            1.0,
            1.0,
            "BALANCED",
            "generation does not exceed verification plus closure plus debt absorption",
        )
    overload = generation_rate / max(sustainable, 1e-9)
    return GenerationThrottleReceipt(
        generation_rate,
        verification_rate,
        closure_rate,
        debt_absorption_rate,
        max(0.10, 1.0 / overload),
        min(4.0, overload),
        "THROTTLE_GENERATION",
        "generation exceeds bounded closure capacity",
    )


@dataclass(frozen=True)
class RegimeDecision:
    mode: str
    reason: str
    exploration_budget_multiplier: float
    closure_budget_multiplier: float
    reality_budget_multiplier: float

    def to_dict(self) -> dict:
        return asdict(self)


def select_regime(
    *,
    backlog: float,
    evidence_debt: float,
    reality_debt: float,
    verified_demand: float,
    risk: float,
) -> RegimeDecision:
    values = (backlog, evidence_debt, reality_debt, verified_demand, risk)
    if any(value < 0 for value in values):
        raise ValueError("regime inputs must be non-negative")

    closure_pressure = backlog + evidence_debt
    reality_pressure = reality_debt + verified_demand
    if closure_pressure > 0 and closure_pressure >= reality_pressure:
        return RegimeDecision(
            "CLOSE",
            "backlog and evidence debt dominate current state",
            0.25,
            2.0,
            1.0,
        )
    if reality_pressure > 0:
        return RegimeDecision(
            "REALITY",
            "reality debt or verified demand dominates current state",
            0.35,
            1.25,
            2.0,
        )
    if risk > 0:
        return RegimeDecision(
            "VERIFY",
            "risk remains while no stronger closure or reality pressure exists",
            0.25,
            1.25,
            0.75,
        )
    return RegimeDecision(
        "EXPLORE",
        "no material backlog, debt, demand or risk supplied",
        1.0,
        0.75,
        0.75,
    )


def _required_capabilities(residuals: Iterable[str]) -> tuple[str, ...]:
    required = {"context", "provenance"}
    for residual in residuals:
        upper = residual.upper()
        if "EVIDENCE" in upper or "VALIDATE" in upper:
            required.add("evidence")
        if "RESEARCH" in upper or "PRIOR" in upper:
            required.add("research")
        if "DUP" in upper or "CANON" in upper:
            required.add("identity")
        if "TEST" in upper or "ATTACK" in upper:
            required.add("falsification")
    return tuple(sorted(required))


def compile_mission_genome(
    *,
    mission_id: str,
    goal: str,
    residuals: tuple[str, ...],
    context_ids: tuple[str, ...],
    debt: DebtVector | None = None,
) -> MissionGenome:
    genome = MissionGenome(
        mission_id=mission_id,
        goal=goal,
        residuals=residuals,
        context_ids=context_ids,
        required_capabilities=_required_capabilities(residuals),
        constraints=(
            "minimum-sufficient-context",
            "reversible-first",
            "evidence-bounded",
            "origin-blind-selection",
        ),
        authority_scope=("internal-planning", "reversible-engineering"),
        evidence_contract=(
            "source-provenance",
            "explicit-result",
            "uncertainty-or-limit",
            "receipt",
        ),
        candidate_origins=("TRISTAN", "SIMPLE", "EXTERNAL", "HYBRID", "NO_ACTION"),
        falsifiers=("counterexample", "baseline-loss", "regression", "no-gain"),
        stop_rules=(
            "NO_ACTION",
            "HOLD_AUTHORITY",
            "REPEATED_NO_GAIN",
            "COST_EXCEEDS_VERIFIED_GAIN",
        ),
        rollback="restore previous immutable receipt or snapshot",
        debt=debt or DebtVector(),
    )
    errors = genome.validate()
    if errors:
        raise ValueError("; ".join(errors))
    return genome


def _default_candidates() -> tuple[CapabilityCandidate, ...]:
    return (
        CapabilityCandidate(
            "jarvis-core",
            ("context", "provenance", "research"),
            0.90, 0.10, 1.0, 1.0, "VERIFIED_ENGINEERING",
        ),
        CapabilityCandidate(
            "evidence-foundry",
            ("evidence", "falsification"),
            0.88, 0.12, 1.2, 1.2, "VERIFIED_ENGINEERING",
        ),
        CapabilityCandidate(
            "atlas-r8",
            ("identity", "context", "provenance"),
            0.86, 0.14, 1.0, 1.0, "VERIFIED_ENGINEERING",
        ),
        CapabilityCandidate(
            "simple-no-action-baseline",
            ("context",),
            0.99, 0.01, 0.0, 0.0, "BASELINE",
        ),
    )


@dataclass(frozen=True)
class UltraClosureReceipt:
    schema_version: str
    mission_genome: dict
    coalition: dict
    regime: dict
    throttle: dict
    causal_credit: dict
    pcro_status: str
    capability_crystal_status: str
    portfolio_fronts: tuple[str, ...]
    progress_definition: str
    epistemic_status: str
    scientific_pass: bool
    authority_granted: bool
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def compile_ultra_closure(
    *,
    intent: str,
    mission_id: str,
    residuals: tuple[str, ...],
    context_ids: tuple[str, ...],
    debt: DebtVector | None = None,
) -> UltraClosureReceipt:
    debt = debt or DebtVector()
    genome = compile_mission_genome(
        mission_id=mission_id,
        goal=intent,
        residuals=residuals,
        context_ids=context_ids,
        debt=debt,
    )
    coalition = select_minimal_coalition(
        genome.required_capabilities,
        _default_candidates(),
        max_coalition_size=4,
    )
    regime = select_regime(
        backlog=float(len(residuals)),
        evidence_debt=debt.evidence,
        reality_debt=debt.reality,
        verified_demand=0.0,
        risk=debt.authority,
    )
    throttle = generation_throttle(
        generation_rate=float(max(1, len(residuals))),
        verification_rate=1.0 if "evidence" in genome.required_capabilities else 0.5,
        closure_rate=1.0,
        debt_absorption_rate=1.0 if debt.total > 0 else 0.5,
    )
    return UltraClosureReceipt(
        schema_version="tristan-ultra-closure-r9",
        mission_genome=genome.to_dict(),
        coalition=coalition.to_dict(),
        regime=regime.to_dict(),
        throttle=throttle.to_dict(),
        causal_credit={
            "status": "AVAILABLE_NOT_EXECUTED",
            "owner": "causal_credit.assign_ablation_credit",
            "boundary": "AblationContribution != CausalProof",
        },
        pcro_status="CONTRACT_AVAILABLE_NOT_INSTANTIATED",
        capability_crystal_status="CONTRACT_AVAILABLE_NOT_PROMOTED",
        portfolio_fronts=(
            "PORTFOLIO_CLOSURE",
            "RUNTIME_CLOSURE",
            "MEMORY_CLOSURE",
            "SCIENTIFIC_CLOSURE",
            "REALITY_CLOSURE",
        ),
        progress_definition=(
            "VerifiedCapabilityDelta + RealityDelta + FutureWorkEliminated"
        ),
        epistemic_status="PROVISIONAL_ULTRA_CLOSURE_PLAN",
        scientific_pass=False,
        authority_granted=False,
        boundaries=ULTRA_CLOSURE_BOUNDARIES,
    )
