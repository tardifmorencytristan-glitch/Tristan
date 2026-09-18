from __future__ import annotations

from .robust_rlc import search_robust_rlc_trees


def compile_tesla_omega_r03(
    n: int = 6,
    samples: int = 48,
    seed: int = 20260918,
) -> dict[str, object]:
    candidates = search_robust_rlc_trees(n=n, samples=samples, seed=seed)
    return {
        "schema_version": "tesla-omega-r0.3",
        "status": "ROBUST_RLC_COMPUTATIONAL_SCREENING_ONLY",
        "authority_granted": False,
        "physical_validation_claimed": False,
        "novelty_claimed": False,
        "model": {
            "family": "series-RLC magnetically coupled loop network",
            "nodes": n,
            "edges": n - 1,
            "L_h": 10e-6,
            "C_f": 100e-9,
            "coil_R_ohm": 0.2,
            "source_R_ohm": 0.5,
            "load_R_ohm": 10.0,
            "nominal_k": 0.08,
            "component_tolerance_fraction": 0.05,
            "coupling_tolerance_fraction": 0.10,
            "frequency_window_f0": (0.75, 1.25),
        },
        "candidates": candidates,
        "boundaries": (
            "RLCNetworkModel != MaxwellFieldSolution",
            "PeakEfficiencyInModel != MeasuredEfficiency",
            "MonteCarloRobustness != ManufacturingValidation",
            "BestInBoundedTreeCourt != Novelty",
            "Simulation != Measurement",
        ),
    }
