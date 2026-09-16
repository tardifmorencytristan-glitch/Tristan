from __future__ import annotations

from dataclasses import dataclass, field

from .capability_registry import CapabilityRecord
from .demand_ir import OpportunityIR, RequirementIR


@dataclass(frozen=True)
class ComplianceRow:
    requirement_key: str
    description: str
    mandatory: bool
    capability_name: str | None
    capability_status: str | None
    evidence_receipts: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    result: str = "UNKNOWN"


@dataclass
class ComplianceMatrix:
    opportunity: OpportunityIR
    rows: list[ComplianceRow] = field(default_factory=list)

    @property
    def blockers(self) -> list[ComplianceRow]:
        return [r for r in self.rows if r.mandatory and r.result != "SUPPORTED"]

    @property
    def status(self) -> str:
        if not self.opportunity.requirements:
            return "REQUIREMENTS_UNKNOWN"
        if self.blockers:
            return "HOLD"
        return "SUPPORTED_FOR_DRAFT"


def build_compliance_matrix(opportunity: OpportunityIR, registry: tuple[CapabilityRecord, ...]) -> ComplianceMatrix:
    rows: list[ComplianceRow] = []
    for req in opportunity.requirements:
        matches = [r for r in registry if req.key in r.capability.covers]
        if not matches:
            rows.append(ComplianceRow(req.key, req.description, req.mandatory, None, None, result="GAP"))
            continue
        best = matches[0]
        result = "SUPPORTED" if best.evidence_receipts and not best.status.startswith("PARTIAL") else "PARTIAL"
        rows.append(ComplianceRow(
            req.key,
            req.description,
            req.mandatory,
            best.capability.name,
            best.status,
            best.evidence_receipts,
            best.limitations,
            result,
        ))
    return ComplianceMatrix(opportunity, rows)
