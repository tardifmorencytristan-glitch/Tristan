from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Topology:
    name: str
    nodes: tuple[int, ...]
    edges: tuple[tuple[int, int], ...]

    def degree_sequence(self) -> tuple[int, ...]:
        degree = {node: 0 for node in self.nodes}
        for a, b in self.edges:
            degree[a] += 1
            degree[b] += 1
        return tuple(sorted(degree.values(), reverse=True))

    def signature(self) -> tuple[int, int, tuple[int, ...]]:
        return len(self.nodes), len(self.edges), self.degree_sequence()


def chain(n: int) -> Topology:
    if n < 2:
        raise ValueError("chain requires at least two nodes")
    nodes = tuple(range(n))
    return Topology("chain", nodes, tuple((i, i + 1) for i in range(n - 1)))


def star(n: int) -> Topology:
    if n < 3:
        raise ValueError("star requires at least three nodes")
    nodes = tuple(range(n))
    return Topology("star", nodes, tuple((0, i) for i in range(1, n)))


def binary_tree(levels: int) -> Topology:
    if levels < 1:
        raise ValueError("levels must be >= 1")
    n = 2 ** levels - 1
    nodes = tuple(range(n))
    edges: list[tuple[int, int]] = []
    for parent in range((n - 1) // 2):
        left = 2 * parent + 1
        right = left + 1
        if left < n:
            edges.append((parent, left))
        if right < n:
            edges.append((parent, right))
    return Topology("binary_tree", nodes, tuple(edges))


def mutate_add_leaf(topology: Topology, parent: int) -> Topology:
    if parent not in topology.nodes:
        raise ValueError("parent is not in topology")
    node = max(topology.nodes) + 1
    return Topology(
        f"{topology.name}+leaf",
        topology.nodes + (node,),
        topology.edges + ((parent, node),),
    )
