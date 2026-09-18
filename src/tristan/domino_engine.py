from __future__ import annotations

from dataclasses import asdict, dataclass
from collections import defaultdict, deque


DOMINO_KINDS = {"support", "falsification", "uncertainty", "prediction"}


@dataclass(frozen=True)
class DominoNode:
    node_id: str
    kind: str
    label: str
    status: str = "ACTIVE"

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.node_id.strip():
            errors.append("node_id required")
        if not self.kind.strip():
            errors.append("kind required")
        if not self.label.strip():
            errors.append("label required")
        return errors


@dataclass(frozen=True)
class DominoEdge:
    source_id: str
    target_id: str
    relation: str
    weight: float
    confidence: float
    provenance_quality: float
    causal_quality: float

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.source_id.strip() or not self.target_id.strip():
            errors.append("source_id and target_id required")
        if not self.relation.strip():
            errors.append("relation required")
        for name, value in (
            ("weight", self.weight),
            ("confidence", self.confidence),
            ("provenance_quality", self.provenance_quality),
            ("causal_quality", self.causal_quality),
        ):
            if not -1.0 <= value <= 1.0:
                errors.append(f"{name} must be in [-1, 1]")
        if self.confidence < 0 or self.provenance_quality < 0 or self.causal_quality < 0:
            errors.append("confidence/provenance/causal quality must be non-negative")
        return errors

    @property
    def gate_score(self) -> float:
        return abs(self.weight) * self.confidence * self.provenance_quality * self.causal_quality


@dataclass(frozen=True)
class DominoEvent:
    origin_id: str
    kind: str
    magnitude: float
    reason: str

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.kind not in DOMINO_KINDS:
            errors.append("unsupported domino kind")
        if not -1.0 <= self.magnitude <= 1.0:
            errors.append("magnitude must be in [-1, 1]")
        if not self.origin_id.strip():
            errors.append("origin_id required")
        if not self.reason.strip():
            errors.append("reason required")
        return errors


@dataclass(frozen=True)
class DominoImpact:
    node_id: str
    kind: str
    delta: float
    depth: int
    path: tuple[str, ...]
    gate_score: float

    def to_dict(self) -> dict:
        return asdict(self)


def propagation_cone(
    nodes: tuple[DominoNode, ...],
    edges: tuple[DominoEdge, ...],
    event: DominoEvent,
    *,
    threshold: float = 0.15,
    max_depth: int = 8,
) -> tuple[DominoImpact, ...]:
    errors = event.validate()
    for node in nodes:
        errors.extend(node.validate())
    for edge in edges:
        errors.extend(edge.validate())
    if errors:
        raise ValueError("; ".join(errors))

    node_ids = {node.node_id for node in nodes}
    if event.origin_id not in node_ids:
        raise ValueError("event origin must exist in nodes")

    outgoing: dict[str, list[DominoEdge]] = defaultdict(list)
    for edge in edges:
        if edge.source_id not in node_ids or edge.target_id not in node_ids:
            raise ValueError("all domino edges must reference declared nodes")
        outgoing[edge.source_id].append(edge)

    queue = deque([(event.origin_id, event.magnitude, 0, (event.origin_id,))])
    best: dict[str, float] = {event.origin_id: abs(event.magnitude)}
    impacts: list[DominoImpact] = []

    while queue:
        current, delta, depth, path = queue.popleft()
        if depth >= max_depth:
            continue
        for edge in outgoing.get(current, []):
            gate = edge.gate_score
            if gate < threshold:
                continue
            next_delta = delta * edge.weight * edge.confidence * edge.provenance_quality * edge.causal_quality
            if abs(next_delta) < threshold:
                continue
            if edge.target_id in path:
                continue
            prior = best.get(edge.target_id, 0.0)
            if abs(next_delta) <= prior:
                continue
            best[edge.target_id] = abs(next_delta)
            next_path = path + (edge.target_id,)
            impacts.append(DominoImpact(
                node_id=edge.target_id,
                kind=event.kind,
                delta=next_delta,
                depth=depth + 1,
                path=next_path,
                gate_score=gate,
            ))
            queue.append((edge.target_id, next_delta, depth + 1, next_path))

    return tuple(sorted(impacts, key=lambda x: (x.depth, -abs(x.delta), x.node_id)))


def critical_test_priority(
    *,
    expected_information_gain: float,
    independence: float,
    reproducibility: float,
    cost: float,
) -> float:
    if min(expected_information_gain, independence, reproducibility, cost) < 0:
        raise ValueError("critical-test inputs must be non-negative")
    return expected_information_gain * independence * reproducibility / max(cost, 1e-9)
