from __future__ import annotations

from .spectral import coupled_mode_frequencies_hz, modal_metrics
from .topology import Topology


def coupling_sweep(
    topology: Topology,
    inductance_h: float,
    capacitance_f: float,
    couplings: tuple[float, ...] = (0.02, 0.05, 0.08, 0.10),
) -> dict[str, object]:
    rows: list[dict[str, float]] = []
    for k in couplings:
        metrics = modal_metrics(
            coupled_mode_frequencies_hz(
                topology, inductance_h, capacitance_f, k
            )
        )
        rows.append({"k": k, **metrics})
    spans = [row["modal_span_hz"] for row in rows]
    mean = sum(spans) / len(spans)
    worst = min(spans)
    best = max(spans)
    return {
        "rows": tuple(rows),
        "mean_modal_span_hz": mean,
        "worst_modal_span_hz": worst,
        "best_modal_span_hz": best,
        "span_ratio_worst_to_best": worst / best if best else 0.0,
    }
