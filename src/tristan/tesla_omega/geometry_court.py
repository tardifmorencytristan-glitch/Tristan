from __future__ import annotations

from itertools import permutations

from .geometry import conductor_length_proxy, geometric_couplings, hex_bridge_geometry
from .physics import resonant_frequency_hz
from .rlc import transfer_at_frequency
from .search import unique_unlabeled_trees
from .topology import Topology


def relabel(topology: Topology, mapping: tuple[int, ...]) -> Topology:
    if len(mapping) != len(topology.nodes):
        raise ValueError("mapping length mismatch")
    edges = tuple(sorted(tuple(sorted((mapping[a], mapping[b]))) for a,b in topology.edges))
    return Topology(topology.name, topology.nodes, edges)


def best_geometric_embedding(
    topology: Topology,
    positions=None,
    source_node: int = 0,
    receiver_node: int = 5,
    inductance_h: float = 10e-6,
    capacitance_f: float = 100e-9,
    coil_resistance_ohm: float = 0.2,
    source_resistance_ohm: float = 0.5,
    load_resistance_ohm: float = 10.0,
    points: int = 61,
) -> dict[str, object]:
    positions = positions or hex_bridge_geometry()
    if len(topology.nodes) != 6:
        raise ValueError("R0.4 embedding court currently supports n=6")
    f0 = resonant_frequency_hz(inductance_h, capacitance_f)
    best: dict[str, object] | None = None
    fixed_middle = [1,2,3,4]
    for perm_mid in permutations(fixed_middle):
        mapping = (source_node,) + perm_mid + (receiver_node,)
        candidate = relabel(topology, mapping)
        couplings = geometric_couplings(candidate, positions)
        n = len(candidate.nodes)
        ls = (inductance_h,) * n
        cs = (capacitance_f,) * n
        rs = (coil_resistance_ohm,) * n
        peak = None
        for i in range(points):
            alpha = i/(points-1)
            f = f0 * (0.75 + 0.50*alpha)
            row = transfer_at_frequency(
                candidate,f,ls,cs,rs,couplings,
                source_resistance_ohm,load_resistance_ohm,
                source_node=source_node,receiver_node=receiver_node,
            )
            if peak is None or row["efficiency"] > peak["efficiency"]:
                peak = row
        result = {
            "mapping": mapping,
            "edges": candidate.edges,
            "couplings": tuple(sorted((f"{a}-{b}",k) for (a,b),k in couplings.items())),
            "conductor_length_proxy_m": conductor_length_proxy(candidate, positions),
            "peak": peak,
        }
        if best is None or result["peak"]["efficiency"] > best["peak"]["efficiency"]:
            best = result
    return best


def geometry_matched_tree_court() -> tuple[dict[str, object], ...]:
    rows=[]
    positions=hex_bridge_geometry()
    for topology in unique_unlabeled_trees(6):
        best=best_geometric_embedding(topology, positions=positions)
        rows.append({
            "degree_sequence": topology.degree_sequence(),
            "best_embedding": best,
        })
    rows.sort(key=lambda r:(-r["best_embedding"]["peak"]["efficiency"], r["degree_sequence"]))
    return tuple(rows)
