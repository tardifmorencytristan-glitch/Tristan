from __future__ import annotations

from dataclasses import dataclass

from .compliance import ComplianceMatrix


@dataclass(frozen=True)
class ResearchResidual:
    requirement_key: str
    reason: str
    priority_hint: str


def research_residuals(matrix: ComplianceMatrix) -> list[ResearchResidual]:
    residuals: list[ResearchResidual] = []
    if matrix.status == "REQUIREMENTS_UNKNOWN":
        return [ResearchResidual("requirements", "Detailed requirements unavailable", "RETRIEVE_SOURCE")]
    for row in matrix.blockers:
        if row.result == "GAP":
            residuals.append(ResearchResidual(row.requirement_key, "Capability missing", "BUILD_OR_REUSE"))
        elif row.result == "PARTIAL":
            residuals.append(ResearchResidual(row.requirement_key, "Capability evidence insufficient", "VALIDATE"))
        else:
            residuals.append(ResearchResidual(row.requirement_key, "Requirement unresolved", "INVESTIGATE"))
    return residuals
