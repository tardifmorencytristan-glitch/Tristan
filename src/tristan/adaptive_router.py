from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import combinations
from typing import Mapping


@dataclass(frozen=True)
class CapabilityCandidate:
    candidate_id: str
    capabilities: tuple[str, ...]
    reliability: float
    uncertainty: float
    cost: float
    latency: float
    evidence_status: str = "UNKNOWN"

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.candidate_id.strip():
            errors.append("candidate_id required")
        if not self.capabilities:
            errors.append("capabilities required")
        for name, value in (
            ("reliability", self.reliability),
            ("uncertainty", self.uncertainty),
        ):
            if not 0.0 <= value <= 1.0:
                errors.append(f"{name} must be in [0,1]")
        for name, value in (("cost", self.cost), ("latency", self.latency)):
            if value < 0:
                errors.append(f"{name} must be non-negative")
        return errors


@dataclass(frozen=True)
class CoalitionReceipt:
    required_capabilities: tuple[str, ...]
    selected_candidates: tuple[str, ...]
    covered_capabilities: tuple[str, ...]
    utility: float | None
    status: str
    authority_granted: bool
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def _utility(coalition: tuple[CapabilityCandidate, ...]) -> float:
    reliability = min(candidate.reliability for candidate in coalition)
    uncertainty = max(candidate.uncertainty for candidate in coalition)
    cost = sum(candidate.cost for candidate in coalition)
    latency = max(candidate.latency for candidate in coalition)
    complexity = 0.05 * max(0, len(coalition) - 1)
    return reliability - uncertainty - 0.01 * cost - 0.001 * latency - complexity


def select_minimal_coalition(
    required_capabilities: tuple[str, ...],
    candidates: tuple[CapabilityCandidate, ...],
    *,
    max_coalition_size: int = 4,
) -> CoalitionReceipt:
    if not required_capabilities:
        raise ValueError("required_capabilities required")
    if max_coalition_size < 1:
        raise ValueError("max_coalition_size must be >= 1")
    for candidate in candidates:
        errors = candidate.validate()
        if errors:
            raise ValueError("; ".join(errors))

    required = set(required_capabilities)
    feasible: list[tuple[float, tuple[CapabilityCandidate, ...]]] = []
    max_size = min(max_coalition_size, len(candidates))
    for size in range(1, max_size + 1):
        for coalition in combinations(candidates, size):
            covered = set().union(*(set(c.capabilities) for c in coalition))
            if required <= covered:
                feasible.append((_utility(coalition), coalition))
        if feasible:
            break

    if not feasible:
        return CoalitionReceipt(
            required_capabilities=required_capabilities,
            selected_candidates=(),
            covered_capabilities=(),
            utility=None,
            status="HOLD_NO_CAPABILITY_COVERAGE",
            authority_granted=False,
            boundaries=(
                "CapabilityCoverage != Authority",
                "NoCoverage -> HOLD",
                "OriginBonus = 0",
                "NO_ACTION is admissible",
            ),
        )

    utility, coalition = max(feasible, key=lambda item: (item[0], tuple(c.candidate_id for c in item[1])))
    covered = sorted(set().union(*(set(c.capabilities) for c in coalition)))
    return CoalitionReceipt(
        required_capabilities=required_capabilities,
        selected_candidates=tuple(c.candidate_id for c in coalition),
        covered_capabilities=tuple(covered),
        utility=utility,
        status="COALITION_SELECTED",
        authority_granted=False,
        boundaries=(
            "CapabilityCoverage != Authority",
            "Selection != Execution",
            "Utility != UniversalSuperiority",
            "OriginBonus = 0",
            "NO_ACTION is admissible",
        ),
    )


@dataclass(frozen=True)
class RuntimeNode:
    candidate_id: str
    python_version: str | None
    node_version: str | None
    reliability: float = 1.0
    uncertainty: float = 0.0
    cost: float = 0.0
    latency: float = 0.0
    evidence_status: str = "UNKNOWN"


def _version_tuple(value: object) -> tuple[int, ...]:
    text = str(value or "")
    current = ""
    for ch in text:
        if ch.isdigit() or (ch == "." and current):
            current += ch
        elif current:
            break
    if not current:
        return ()
    return tuple(int(part) for part in current.strip(".").split(".") if part.isdigit())


def runtime_requirements_satisfied(
    requirements: Mapping[str, object],
    node: RuntimeNode,
) -> bool:
    if node.evidence_status != "MEASURED":
        return False
    python_min = requirements.get("python_min")
    node_min = requirements.get("node_min")
    if python_min and _version_tuple(node.python_version) < _version_tuple(python_min):
        return False
    if node_min and _version_tuple(node.node_version) < _version_tuple(node_min):
        return False
    return True


def select_runtime_coalition(
    task_requirements: Mapping[str, Mapping[str, object]],
    nodes: tuple[RuntimeNode, ...],
    *,
    max_coalition_size: int = 4,
) -> CoalitionReceipt:
    if not task_requirements:
        raise ValueError("task_requirements required")

    candidates: list[CapabilityCandidate] = []
    for node in nodes:
        covered_tasks = tuple(
            task_id
            for task_id, requirements in task_requirements.items()
            if runtime_requirements_satisfied(requirements, node)
        )
        if not covered_tasks:
            continue
        candidates.append(
            CapabilityCandidate(
                candidate_id=node.candidate_id,
                capabilities=covered_tasks,
                reliability=node.reliability,
                uncertainty=node.uncertainty,
                cost=node.cost,
                latency=node.latency,
                evidence_status=node.evidence_status,
            )
        )

    return select_minimal_coalition(
        tuple(task_requirements),
        tuple(candidates),
        max_coalition_size=max_coalition_size,
    )
