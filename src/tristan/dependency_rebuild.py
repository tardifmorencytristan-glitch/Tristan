from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class RebuildPlan:
    changed_ids: tuple[str, ...]
    affected_ids: tuple[str, ...]
    rebuild_order: tuple[str, ...]
    full_rebuild: bool = False


def affected_subgraph(changed: set[str], dependents: dict[str, set[str]]) -> set[str]:
    seen = set(changed)
    queue = deque(sorted(changed))
    while queue:
        current = queue.popleft()
        for child in sorted(dependents.get(current, ())):
            if child not in seen:
                seen.add(child)
                queue.append(child)
    return seen


def topological_rebuild_order(affected: set[str], dependencies: dict[str, set[str]]) -> tuple[str, ...]:
    indegree = {node: 0 for node in affected}
    children: dict[str, set[str]] = {node: set() for node in affected}
    for node in affected:
        for dep in dependencies.get(node, ()):
            if dep in affected:
                indegree[node] += 1
                children.setdefault(dep, set()).add(node)

    ready = deque(sorted(node for node, degree in indegree.items() if degree == 0))
    order: list[str] = []
    while ready:
        node = ready.popleft()
        order.append(node)
        for child in sorted(children.get(node, ())):
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child)

    if len(order) != len(affected):
        raise ValueError("dependency cycle detected in affected subgraph")
    return tuple(order)


def differential_rebuild_plan(
    changed: set[str],
    dependencies: dict[str, set[str]],
) -> RebuildPlan:
    dependents: dict[str, set[str]] = {}
    for node, deps in dependencies.items():
        for dep in deps:
            dependents.setdefault(dep, set()).add(node)
    affected = affected_subgraph(changed, dependents)
    order = topological_rebuild_order(affected, dependencies)
    return RebuildPlan(
        changed_ids=tuple(sorted(changed)),
        affected_ids=tuple(sorted(affected)),
        rebuild_order=order,
        full_rebuild=False,
    )
