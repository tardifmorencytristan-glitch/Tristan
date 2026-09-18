from __future__ import annotations

import math


def resonant_frequency_hz(inductance_h: float, capacitance_f: float) -> float:
    if inductance_h <= 0 or capacitance_f <= 0:
        raise ValueError("L and C must be positive")
    return 1.0 / (2.0 * math.pi * math.sqrt(inductance_h * capacitance_f))


def coupling_coefficient(mutual_h: float, l1_h: float, l2_h: float) -> float:
    if l1_h <= 0 or l2_h <= 0:
        raise ValueError("inductances must be positive")
    k = mutual_h / math.sqrt(l1_h * l2_h)
    if abs(k) >= 1.0:
        raise ValueError("passive two-coil model requires |k| < 1")
    return k


def coupled_two_resonator_frequencies_hz(
    inductance_h: float,
    capacitance_f: float,
    k: float,
) -> tuple[float, float]:
    """Ideal identical magnetically coupled resonators."""
    if not -1.0 < k < 1.0:
        raise ValueError("k must satisfy -1 < k < 1")
    f0 = resonant_frequency_hz(inductance_h, capacitance_f)
    values = (f0 / math.sqrt(1.0 + k), f0 / math.sqrt(1.0 - k))
    return tuple(sorted(values))


def quality_factor_series_r_l(inductance_h: float, resistance_ohm: float, frequency_hz: float) -> float:
    if inductance_h <= 0 or resistance_ohm <= 0 or frequency_hz <= 0:
        raise ValueError("L, R, and f must be positive")
    return 2.0 * math.pi * frequency_hz * inductance_h / resistance_ohm
