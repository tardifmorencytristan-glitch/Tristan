from __future__ import annotations

import math
from dataclasses import dataclass

from .topology import Topology


@dataclass(frozen=True)
class Point3D:
    x: float
    y: float
    z: float


def distance(a: Point3D, b: Point3D) -> float:
    d = math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2 + (a.z-b.z)**2)
    if d <= 0:
        raise ValueError("coincident resonator centers are not allowed")
    return d


def line_geometry(n: int, spacing_m: float = 0.10) -> tuple[Point3D, ...]:
    if n < 2 or spacing_m <= 0:
        raise ValueError("invalid line geometry")
    return tuple(Point3D(i * spacing_m, 0.0, 0.0) for i in range(n))


def hex_bridge_geometry() -> tuple[Point3D, ...]:
    """Six fixed positions with Tx=0 and Rx=5 separated by 0.50 m."""
    return (
        Point3D(0.00, 0.00, 0.00),
        Point3D(0.10, 0.08, 0.00),
        Point3D(0.20,-0.08, 0.00),
        Point3D(0.30, 0.08, 0.00),
        Point3D(0.40,-0.08, 0.00),
        Point3D(0.50, 0.00, 0.00),
    )


def geometric_couplings(
    topology: Topology,
    positions: tuple[Point3D, ...],
    reference_distance_m: float = 0.10,
    reference_k: float = 0.08,
    exponent: float = 3.0,
    k_cap: float = 0.35,
) -> dict[tuple[int, int], float]:
    if len(positions) != len(topology.nodes):
        raise ValueError("positions must match topology node count")
    if reference_distance_m <= 0 or reference_k < 0 or exponent <= 0:
        raise ValueError("invalid geometric coupling parameters")
    index = {node: i for i, node in enumerate(topology.nodes)}
    out: dict[tuple[int, int], float] = {}
    for a,b in topology.edges:
        r = distance(positions[index[a]], positions[index[b]])
        k = reference_k * (reference_distance_m / r) ** exponent
        out[tuple(sorted((a,b)))] = min(k, k_cap)
    return out


def conductor_length_proxy(topology: Topology, positions: tuple[Point3D, ...]) -> float:
    index = {node: i for i, node in enumerate(topology.nodes)}
    return sum(
        distance(positions[index[a]], positions[index[b]])
        for a,b in topology.edges
    )
