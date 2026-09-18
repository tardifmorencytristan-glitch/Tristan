from __future__ import annotations

import math

from .physics import resonant_frequency_hz
from .topology import Topology


def _solve_complex(matrix: list[list[complex]], rhs: list[complex]) -> tuple[complex, ...]:
    n = len(matrix)
    if n == 0 or len(rhs) != n or any(len(row) != n for row in matrix):
        raise ValueError("invalid linear system")
    a = [list(row) + [rhs[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) < 1e-18:
            raise ValueError("singular impedance matrix")
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]
        p = a[col][col]
        a[col] = [x / p for x in a[col]]
        for row in range(n):
            if row == col:
                continue
            factor = a[row][col]
            if factor == 0:
                continue
            a[row] = [x - factor * y for x, y in zip(a[row], a[col])]
    return tuple(a[i][-1] for i in range(n))


def graph_distances(topology: Topology, start: int) -> dict[int, int]:
    neighbors = {node: [] for node in topology.nodes}
    for a, b in topology.edges:
        neighbors[a].append(b)
        neighbors[b].append(a)
    dist = {start: 0}
    queue = [start]
    for node in queue:
        for nxt in neighbors[node]:
            if nxt not in dist:
                dist[nxt] = dist[node] + 1
                queue.append(nxt)
    return dist


def terminal_pair(topology: Topology) -> tuple[int, int]:
    best: tuple[int, int, int] | None = None
    pair = (topology.nodes[0], topology.nodes[-1])
    for a in topology.nodes:
        dist = graph_distances(topology, a)
        for b in topology.nodes:
            if a >= b:
                continue
            candidate = (dist[b], -a, -b)
            if best is None or candidate > best:
                best = candidate
                pair = (a, b)
    return pair


def impedance_matrix(
    topology: Topology,
    omega: float,
    inductances_h: tuple[float, ...],
    capacitances_f: tuple[float, ...],
    coil_resistances_ohm: tuple[float, ...],
    coupling_by_edge: dict[tuple[int, int], float],
    source_node: int,
    receiver_node: int,
    source_resistance_ohm: float,
    load_resistance_ohm: float,
) -> list[list[complex]]:
    n = len(topology.nodes)
    if not (len(inductances_h) == len(capacitances_f) == len(coil_resistances_ohm) == n):
        raise ValueError("component vectors must match topology size")
    index = {node: i for i, node in enumerate(topology.nodes)}
    z = [[0j for _ in range(n)] for _ in range(n)]
    for node in topology.nodes:
        i = index[node]
        l = inductances_h[i]
        c = capacitances_f[i]
        r = coil_resistances_ohm[i]
        if l <= 0 or c <= 0 or r < 0:
            raise ValueError("invalid passive component")
        extra = 0.0
        if node == source_node:
            extra += source_resistance_ohm
        if node == receiver_node:
            extra += load_resistance_ohm
        z[i][i] = complex(r + extra, omega * l - 1.0 / (omega * c))
    for a, b in topology.edges:
        key = tuple(sorted((a, b)))
        k = coupling_by_edge[key]
        ia, ib = index[a], index[b]
        m = k * math.sqrt(inductances_h[ia] * inductances_h[ib])
        zij = complex(0.0, omega * m)
        z[ia][ib] = zij
        z[ib][ia] = zij
    return z


def transfer_at_frequency(
    topology: Topology,
    frequency_hz: float,
    inductances_h: tuple[float, ...],
    capacitances_f: tuple[float, ...],
    coil_resistances_ohm: tuple[float, ...],
    coupling_by_edge: dict[tuple[int, int], float],
    source_resistance_ohm: float = 0.5,
    load_resistance_ohm: float = 10.0,
    source_voltage_rms: float = 1.0,
    source_node: int | None = None,
    receiver_node: int | None = None,
) -> dict[str, float]:
    if frequency_hz <= 0 or source_resistance_ohm < 0 or load_resistance_ohm <= 0:
        raise ValueError("invalid transfer parameters")
    if (source_node is None) != (receiver_node is None):
        raise ValueError("source_node and receiver_node must be provided together")
    if source_node is None:
        source_node, receiver_node = terminal_pair(topology)
    if source_node not in topology.nodes or receiver_node not in topology.nodes:
        raise ValueError("source/receiver must be topology nodes")
    omega = 2.0 * math.pi * frequency_hz
    z = impedance_matrix(
        topology, omega, inductances_h, capacitances_f, coil_resistances_ohm,
        coupling_by_edge, source_node, receiver_node,
        source_resistance_ohm, load_resistance_ohm,
    )
    index = {node: i for i, node in enumerate(topology.nodes)}
    rhs = [0j for _ in topology.nodes]
    rhs[index[source_node]] = complex(source_voltage_rms, 0.0)
    currents = _solve_complex(z, rhs)
    source_current = currents[index[source_node]]
    receiver_current = currents[index[receiver_node]]
    source_power = (complex(source_voltage_rms, 0.0) * source_current.conjugate()).real
    load_power = abs(receiver_current) ** 2 * load_resistance_ohm
    coil_loss = sum(abs(currents[i]) ** 2 * coil_resistances_ohm[i] for i in range(len(currents)))
    source_loss = abs(source_current) ** 2 * source_resistance_ohm
    eta = load_power / source_power if source_power > 0 else 0.0
    return {
        "frequency_hz": frequency_hz,
        "source_power_w": source_power,
        "load_power_w": load_power,
        "coil_loss_w": coil_loss,
        "source_loss_w": source_loss,
        "efficiency": eta,
    }


def default_couplings(topology: Topology, k: float) -> dict[tuple[int, int], float]:
    if not 0 <= k < 1:
        raise ValueError("k must satisfy 0 <= k < 1")
    return {tuple(sorted(edge)): k for edge in topology.edges}


def frequency_sweep(
    topology: Topology,
    inductance_h: float = 10e-6,
    capacitance_f: float = 100e-9,
    coil_resistance_ohm: float = 0.2,
    coupling_k: float = 0.08,
    source_resistance_ohm: float = 0.5,
    load_resistance_ohm: float = 10.0,
    points: int = 81,
    span: tuple[float, float] = (0.70, 1.30),
    source_node: int | None = None,
    receiver_node: int | None = None,
) -> dict[str, object]:
    if points < 3:
        raise ValueError("points must be >= 3")
    f0 = resonant_frequency_hz(inductance_h, capacitance_f)
    n = len(topology.nodes)
    ls = (inductance_h,) * n
    cs = (capacitance_f,) * n
    rs = (coil_resistance_ohm,) * n
    couplings = default_couplings(topology, coupling_k)
    rows = []
    for i in range(points):
        alpha = i / (points - 1)
        f = f0 * (span[0] + alpha * (span[1] - span[0]))
        rows.append(transfer_at_frequency(
            topology, f, ls, cs, rs, couplings,
            source_resistance_ohm, load_resistance_ohm,
            source_node=source_node, receiver_node=receiver_node,
        ))
    best = max(rows, key=lambda row: row["efficiency"])
    terminals = (
        (source_node, receiver_node)
        if source_node is not None
        else terminal_pair(topology)
    )
    return {
        "f0_hz": f0,
        "source_receiver": terminals,
        "best": best,
        "rows": tuple(rows),
    }
