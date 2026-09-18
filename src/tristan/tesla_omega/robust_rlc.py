from __future__ import annotations

import math
import random

from .rlc import default_couplings, frequency_sweep, terminal_pair, transfer_at_frequency
from .search import unique_unlabeled_trees
from .physics import resonant_frequency_hz


def _perturb(value: float, frac: float, rng: random.Random) -> float:
    return value * (1.0 + rng.uniform(-frac, frac))


def monte_carlo_topology(
    topology,
    samples: int = 48,
    seed: int = 0,
    inductance_h: float = 10e-6,
    capacitance_f: float = 100e-9,
    coil_resistance_ohm: float = 0.2,
    coupling_k: float = 0.08,
    source_resistance_ohm: float = 0.5,
    load_resistance_ohm: float = 10.0,
    component_tolerance: float = 0.05,
    coupling_tolerance: float = 0.10,
    sweep_points: int = 61,
) -> dict[str, object]:
    if samples < 1:
        raise ValueError("samples must be positive")
    rng = random.Random(seed)
    n = len(topology.nodes)
    f0 = resonant_frequency_hz(inductance_h, capacitance_f)
    efficiencies: list[float] = []
    peak_frequencies: list[float] = []
    for _ in range(samples):
        ls = tuple(_perturb(inductance_h, component_tolerance, rng) for _ in range(n))
        cs = tuple(_perturb(capacitance_f, component_tolerance, rng) for _ in range(n))
        rs = tuple(_perturb(coil_resistance_ohm, component_tolerance, rng) for _ in range(n))
        couplings = {
            edge: _perturb(k, coupling_tolerance, rng)
            for edge, k in default_couplings(topology, coupling_k).items()
        }
        best_eta = -1.0
        best_f = 0.0
        for i in range(sweep_points):
            alpha = i / (sweep_points - 1)
            f = f0 * (0.75 + 0.50 * alpha)
            row = transfer_at_frequency(
                topology, f, ls, cs, rs, couplings,
                source_resistance_ohm, load_resistance_ohm,
            )
            if row["efficiency"] > best_eta:
                best_eta = row["efficiency"]
                best_f = f
        efficiencies.append(best_eta)
        peak_frequencies.append(best_f)
    mean = sum(efficiencies) / len(efficiencies)
    variance = sum((x - mean) ** 2 for x in efficiencies) / len(efficiencies)
    std = math.sqrt(variance)
    ordered = sorted(efficiencies)
    p10 = ordered[max(0, int(0.10 * (len(ordered) - 1)))]
    return {
        "seed": seed,
        "samples": samples,
        "source_receiver": terminal_pair(topology),
        "mean_peak_efficiency": mean,
        "std_peak_efficiency": std,
        "p10_peak_efficiency": p10,
        "worst_peak_efficiency": ordered[0],
        "best_peak_efficiency": ordered[-1],
        "robust_score": mean - std,
        "mean_peak_frequency_hz": sum(peak_frequencies) / len(peak_frequencies),
    }


def search_robust_rlc_trees(
    n: int = 6,
    samples: int = 48,
    seed: int = 0,
    **kwargs,
) -> tuple[dict[str, object], ...]:
    rows = []
    for index, topology in enumerate(unique_unlabeled_trees(n)):
        metrics = monte_carlo_topology(
            topology, samples=samples, seed=seed + 1000 * index, **kwargs
        )
        rows.append({
            "degree_sequence": topology.degree_sequence(),
            "edges": topology.edges,
            "metrics": metrics,
        })
    rows.sort(
        key=lambda row: (
            -row["metrics"]["robust_score"],
            -row["metrics"]["p10_peak_efficiency"],
            row["degree_sequence"],
        )
    )
    return tuple(rows)
