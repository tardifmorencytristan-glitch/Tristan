from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class RequirementIR:
    key: str
    description: str
    mandatory: bool = True
    evidence_required: bool = False


@dataclass(frozen=True)
class OpportunityIR:
    source_url: str
    issuer: str
    title: str
    opportunity_type: str
    deadline: str | None = None
    budget: str | None = None
    eligibility: tuple[str, ...] = ()
    requirements: tuple[RequirementIR, ...] = ()


@dataclass(frozen=True)
class CapabilityIR:
    name: str
    covers: tuple[str, ...]
    evidence_ids: tuple[str, ...] = ()
    automation_level: str = "MANUAL"
    authority_required: bool = False


@dataclass(frozen=True)
class EvidenceEdge:
    requirement_key: str
    capability_name: str
    evidence_ids: tuple[str, ...] = ()


@dataclass
class OpportunityAssessment:
    opportunity: OpportunityIR
    covered: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    evidence_gaps: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    edges: list[EvidenceEdge] = field(default_factory=list)

    @property
    def mandatory_coverage(self) -> float:
        mandatory = [r.key for r in self.opportunity.requirements if r.mandatory]
        if not mandatory:
            return 1.0
        return len([k for k in mandatory if k in self.covered]) / len(mandatory)

    @property
    def actionable(self) -> bool:
        return self.mandatory_coverage == 1.0 and not self.blockers and not self.evidence_gaps


def assess_opportunity(
    opportunity: OpportunityIR,
    capabilities: Iterable[CapabilityIR],
    eligibility_facts: Iterable[str] = (),
) -> OpportunityAssessment:
    caps = list(capabilities)
    eligibility = set(eligibility_facts)
    out = OpportunityAssessment(opportunity=opportunity)

    for requirement in opportunity.requirements:
        matches = [c for c in caps if requirement.key in c.covers]
        if not matches:
            if requirement.mandatory:
                out.gaps.append(requirement.key)
            continue
        out.covered.append(requirement.key)
        for cap in matches:
            out.edges.append(EvidenceEdge(requirement.key, cap.name, cap.evidence_ids))
        if requirement.evidence_required and not any(c.evidence_ids for c in matches):
            out.evidence_gaps.append(requirement.key)

    for rule in opportunity.eligibility:
        if rule not in eligibility:
            out.blockers.append(rule)
    return out


def smallest_capability_cover(opportunity: OpportunityIR, capabilities: Iterable[CapabilityIR]) -> list[str]:
    mandatory = {r.key for r in opportunity.requirements if r.mandatory}
    remaining = set(mandatory)
    chosen: list[str] = []
    pool = list(capabilities)
    while remaining:
        best = max(pool, key=lambda c: len(remaining.intersection(c.covers)), default=None)
        if best is None:
            break
        gain = remaining.intersection(best.covers)
        if not gain:
            break
        chosen.append(best.name)
        remaining -= gain
        pool = [c for c in pool if c.name != best.name]
    return chosen


def no_action_reason(assessment: OpportunityAssessment) -> str | None:
    if assessment.blockers:
        return "ELIGIBILITY_BLOCKED"
    if assessment.gaps:
        return "CAPABILITY_GAP"
    if assessment.evidence_gaps:
        return "EVIDENCE_GAP"
    return None
