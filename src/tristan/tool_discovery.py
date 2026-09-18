from __future__ import annotations

from dataclasses import asdict, dataclass

from .capability_registry import CapabilityRecord


@dataclass(frozen=True)
class ToolCandidate:
    tool_id: str
    capabilities: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    reliability: float
    uncertainty: float
    cost: float
    origin: str = "unknown"

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.tool_id.strip():
            errors.append("tool_id required")
        if not self.capabilities:
            errors.append("capabilities required")
        if not self.evidence_ids:
            errors.append("evidence_ids required")
        if not 0.0 <= self.reliability <= 1.0:
            errors.append("reliability must be in [0,1]")
        if not 0.0 <= self.uncertainty <= 1.0:
            errors.append("uncertainty must be in [0,1]")
        if self.cost < 0:
            errors.append("cost must be non-negative")
        return errors


@dataclass(frozen=True)
class ToolDiscoveryReceipt:
    required_capabilities: tuple[str, ...]
    eligible_tools: tuple[str, ...]
    selected_tool: str | None
    status: str
    authority_granted: bool
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def select_tool(
    required_capabilities: tuple[str, ...],
    candidates: tuple[ToolCandidate, ...],
) -> ToolDiscoveryReceipt:
    if not required_capabilities:
        raise ValueError("required_capabilities required")
    required = set(required_capabilities)
    eligible: list[ToolCandidate] = []
    for candidate in candidates:
        errors = candidate.validate()
        if errors:
            raise ValueError("; ".join(errors))
        if required <= set(candidate.capabilities):
            eligible.append(candidate)

    if not eligible:
        return ToolDiscoveryReceipt(
            required_capabilities=required_capabilities,
            eligible_tools=(),
            selected_tool=None,
            status="NO_TOOL_FOUND",
            authority_granted=False,
            boundaries=(
                "ToolDiscovery != ToolInstallation",
                "CapabilityClaimRequiresEvidence",
                "OriginBonus = 0",
                "NO_ACTION is admissible",
            ),
        )

    def utility(tool: ToolCandidate) -> tuple[float, str]:
        score = tool.reliability - tool.uncertainty - 0.01 * tool.cost
        return score, tool.tool_id

    ordered = sorted(eligible, key=utility, reverse=True)
    return ToolDiscoveryReceipt(
        required_capabilities=required_capabilities,
        eligible_tools=tuple(tool.tool_id for tool in ordered),
        selected_tool=ordered[0].tool_id,
        status="TOOL_CANDIDATE_SELECTED",
        authority_granted=False,
        boundaries=(
            "ToolSelected != ToolAuthorized",
            "ToolSelected != Installed",
            "OriginBonus = 0",
            "EvidenceScopeApplies",
        ),
    )


def registry_as_tool_candidates(records: tuple[CapabilityRecord, ...]) -> tuple[ToolCandidate, ...]:
    candidates: list[ToolCandidate] = []
    for record in records:
        confidence = 0.8 if "VERIFIED" in record.status else 0.5
        candidates.append(
            ToolCandidate(
                tool_id=record.capability.capability_id,
                capabilities=tuple(record.capability.functions),
                evidence_ids=record.evidence_receipts,
                reliability=confidence,
                uncertainty=1.0 - confidence,
                cost=0.0,
                origin="registry",
            )
        )
    return tuple(candidates)
