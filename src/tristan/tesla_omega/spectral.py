from __future__ import annotations

import math

from .physics import resonant_frequency_hz
from .topology import Topology


def adjacency_matrix(topology: Topology) -> list[list[float]]:
    index = {node: i for i, node in enumerate(topology.nodes)}
    n = len(topology.nodes)
    matrix = [[0.0 for _ in range(n)] for _ in range(n)]
    for a, b in topology.edges:
        i, j = index[a], index[b]
        matrix[i][j] = 1.0
        matrix[j][i] = 1.0
    return matrix


def symmetric_eigenvalues_jacobi(
    matrix: list[list[float]],
    tol: float = 1e-12,
    max_sweeps: int = 100,
) -> tuple[float, ...]:
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("matrix must be square")
    a = [row[:] for row in matrix]
    for _ in range(max_sweeps * max(n, 1)):
        p = q = -1
        largest = 0.0
        for i in range(n):
            for j in range(i + 1, n):
                value = abs(a[i][j])
                if value > largest:
                    largest = value
                    p, q = i, j
        if largest < tol:
            break
        app, aqq, apq = a[p][p], a[q][q], a[p][q]
        phi = 0.5 * math.atan2(2.0 * apq, aqq - app)
        c, s = math.cos(phi), math.sin(phi)
        for r in range(n):
            if r in (p, q):
                continue
            arp, arq = a[r][p], a[r][q]
            a[r][p] = a[p][r] = c * arp - s * arq
            a[r][q] = a[q][r] = s * arp + c * arq
        a[p][p] = c * c * app - 2.0 * s * c * apq + s * s * aqq
        a[q][q] = s * s * app + 2.0 * s * c * apq + c * c * aqq
        a[p][q] = a[q][p] = 0.0
    return tuple(sorted(a[i][i] for i in range(n)))


def adjacency_eigenvalues(topology: Topology) -> tuple[float, ...]:
    return symmetric_eigenvalues_jacobi(adjacency_matrix(topology))


def coupled_mode_frequencies_hz(
    topology: Topology,
    inductance_h: float,
    capacitance_f: float,
    k: float,
) -> tuple[float, ...]:
    """Ideal equal-resonator magnetic-coupling surrogate.

    L_matrix = L * (I + k A), C_matrix = C * I.
    This is a screening model, not a field solver.
    """
    f0 = resonant_frequency_hz(inductance_h, capacitance_f)
    eigenvalues = adjacency_eigenvalues(topology)
    denominators = [1.0 + k * value for value in eigenvalues]
    if min(denominators) <= 0.0:
        raise ValueError("coupling matrix is not positive definite for this topology/k")
    return tuple(sorted(f0 / math.sqrt(value) for value in denominators))


def modal_metrics(frequencies_hz: tuple[float, ...]) -> dict[str, float]:
    if len(frequencies_hz) < 2:
        raise ValueError("at least two modes are required")
    frequencies = tuple(sorted(frequencies_hz))
    span = frequencies[-1] - frequencies[0]
    spacings = [b - a for a, b in zip(frequencies, frequencies[1:])]
    mean_spacing = sum(spacings) / len(spacings)
    variance = sum((x - mean_spacing) ** 2 for x in spacings) / len(spacings)
    cv = math.sqrt(variance) / mean_spacing if mean_spacing else 0.0
    return {
        "f_min_hz": frequencies[0],
        "f_max_hz": frequencies[-1],
        "modal_span_hz": span,
        "spacing_cv": cv,
        "mode_count": float(len(frequencies)),
    }
