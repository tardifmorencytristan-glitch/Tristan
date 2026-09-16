from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush

from .transformations import Transformation, TransformationRegistry


@dataclass(frozen=True)
class RoutedPath:
    transforms: tuple[str, ...]
    total_cost: float
    total_risk: float
    total_loss_count: int

    @property
    def objective(self) -> float:
        return self.total_cost + self.total_risk + self.total_loss_count


def find_path(registry: TransformationRegistry, source_type: str, target_type: str) -> RoutedPath | None:
    if source_type == target_type:
        return RoutedPath((), 0.0, 0.0, 0)

    heap: list[tuple[float, str, tuple[str, ...], float, float, int]] = []
    heappush(heap, (0.0, source_type, (), 0.0, 0.0, 0))
    best: dict[str, float] = {source_type: 0.0}

    while heap:
        score, node, path, cost, risk, losses = heappop(heap)
        if node == target_type:
            return RoutedPath(path, cost, risk, losses)
        if score > best.get(node, float("inf")):
            continue
        for t in registry.by_input(node):
            for out in t.output_types:
                new_cost = cost + t.cost
                new_risk = risk + t.risk
                new_losses = losses + len(t.known_losses) + (1 if t.reversibility in {"LOSSY", "NON_INVERTIBLE"} else 0)
                new_score = new_cost + new_risk + new_losses
                if new_score < best.get(out, float("inf")):
                    best[out] = new_score
                    heappush(heap, (new_score, out, path + (t.id,), new_cost, new_risk, new_losses))
    return None
