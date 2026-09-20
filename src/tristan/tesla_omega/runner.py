from __future__ import annotations

from .extract import compile_extraction_queue
from .frontier import frontier_queue
from .pipeline import compile_tesla_omega_status
from .robustness import coupling_sweep
from .search import search_tree_topologies
from .topology import chain, star


def compile_tesla_omega_r02(
    n: int = 6,
    inductance_h: float = 10e-6,
    capacitance_f: float = 100e-9,
    k: float = 0.08,
) -> dict[str, object]:
    if not 3 <= n <= 6:
        raise ValueError("R0.2 bounded search requires 3 <= n <= 6")
    baseline = compile_tesla_omega_status()
    candidates = search_tree_topologies(
        n, inductance_h, capacitance_f, k, limit=8
    )
    controls = []
    for topology in (chain(n), star(n)):
        controls.append({
            "name": topology.name,
            "signature": topology.signature(),
            "coupling_sweep": coupling_sweep(
                topology, inductance_h, capacitance_f
            ),
        })
    return {
        "schema_version": "tesla-omega-r0.2",
        "status": "COMPUTATIONAL_SCREENING_ONLY",
        "authority_granted": False,
        "physical_validation_claimed": False,
        "novelty_claimed": False,
        "base": baseline,
        "model": {
            "kind": "ideal_equal_resonator_magnetic_coupling_surrogate",
            "nodes": n,
            "edges": n - 1,
            "inductance_h": inductance_h,
            "capacitance_f": capacitance_f,
            "coupling_k": k,
            "field_solver": False,
            "loss_model": False,
        },
        "controls": tuple(controls),
        "candidate_classes": candidates,
        "extraction_queue": compile_extraction_queue(),
        "frontier_queue": frontier_queue(),
        "boundaries": (
            "SpectralScreening != WPTPerformance",
            "NetworkSurrogate != MaxwellFieldSolution",
            "PatentDocumentation != ExperimentalProof",
            "TopologicalDifference != UsefulAdvantage",
            "BestInBoundedSearch != Novelty",
            "Simulation != Measurement",
        ),
    }
