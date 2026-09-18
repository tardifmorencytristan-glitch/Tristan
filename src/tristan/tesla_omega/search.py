from __future__ import annotations

from itertools import permutations, product

from .spectral import coupled_mode_frequencies_hz, modal_metrics
from .topology import Topology


def tree_from_prufer(sequence: tuple[int, ...]) -> Topology:
    n = len(sequence) + 2
    if any(x < 0 or x >= n for x in sequence):
        raise ValueError("invalid Prufer sequence")
    degree = [1] * n
    for x in sequence:
        degree[x] += 1
    edges: list[tuple[int, int]] = []
    for x in sequence:
        leaf = min(i for i, d in enumerate(degree) if d == 1)
        edges.append((leaf, x))
        degree[leaf] -= 1
        degree[x] -= 1
    leaves = [i for i, d in enumerate(degree) if d == 1]
    edges.append((leaves[0], leaves[1]))
    normalized = tuple(sorted(tuple(sorted(edge)) for edge in edges))
    return Topology("prufer_tree", tuple(range(n)), normalized)


def unique_labeled_trees(n: int) -> tuple[Topology, ...]:
    if n < 2:
        raise ValueError("n must be >= 2")
    if n > 6:
        raise ValueError("bounded R0.2 search supports n <= 6")
    seen: dict[tuple[tuple[int, int], ...], Topology] = {}
    for seq in product(range(n), repeat=n - 2):
        tree = tree_from_prufer(tuple(seq))
        seen.setdefault(tree.edges, tree)
    return tuple(seen[key] for key in sorted(seen))


def canonical_unlabeled_signature(topology: Topology) -> str:
    """Exact brute-force graph-isomorphism signature for n<=6."""
    n = len(topology.nodes)
    if n > 6:
        raise ValueError("bounded R0.2 canonicalizer supports n <= 6")
    edge_set = {tuple(sorted(e)) for e in topology.edges}
    best: str | None = None
    for perm in permutations(range(n)):
        bits: list[str] = []
        for i in range(n):
            for j in range(i + 1, n):
                a, b = perm[i], perm[j]
                bits.append("1" if tuple(sorted((a, b))) in edge_set else "0")
        code = "".join(bits)
        if best is None or code < best:
            best = code
    return best or ""


def unique_unlabeled_trees(n: int) -> tuple[Topology, ...]:
    classes: dict[str, Topology] = {}
    for tree in unique_labeled_trees(n):
        key = canonical_unlabeled_signature(tree)
        classes.setdefault(key, tree)
    return tuple(classes[key] for key in sorted(classes))


def search_tree_topologies(
    n: int,
    inductance_h: float,
    capacitance_f: float,
    k: float,
    limit: int = 8,
) -> tuple[dict[str, object], ...]:
    scored: list[dict[str, object]] = []
    for topology in unique_unlabeled_trees(n):
        frequencies = coupled_mode_frequencies_hz(
            topology, inductance_h, capacitance_f, k
        )
        metrics = modal_metrics(frequencies)
        scored.append({
            "edges": topology.edges,
            "degree_sequence": topology.degree_sequence(),
            "unlabeled_signature": canonical_unlabeled_signature(topology),
            "frequencies_hz": frequencies,
            "metrics": metrics,
            "screening_score": metrics["modal_span_hz"],
        })
    scored.sort(
        key=lambda x: (-float(x["screening_score"]), x["unlabeled_signature"])
    )
    return tuple(scored[:limit])
