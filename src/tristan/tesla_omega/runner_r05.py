from __future__ import annotations

from .architecture_r05 import BASE_RADIUS_M, equal_copper_symmetric_search, evaluate_radius_schedule


def compile_tesla_omega_r05() -> dict[str,object]:
    baseline=evaluate_radius_schedule((BASE_RADIUS_M,)*6)
    candidates=equal_copper_symmetric_search()
    best=candidates[0]
    return {
        "schema_version":"tesla-omega-r0.5",
        "status":"ALL_PAIRS_EQUAL_COPPER_SCREENING_ONLY",
        "authority_granted":False,
        "physical_validation_claimed":False,
        "novelty_claimed":False,
        "model":{
            "coupling":"all-pairs magnetic dipole approximation",
            "self_inductance":"thin circular loop high-frequency approximation",
            "resistance":"copper skin-depth annulus approximation",
            "individual_tuning":"each resonator tuned to common target frequency",
            "source_receiver":"fixed nodes 0 and 5 at 0.50 m",
            "topology_edges_used":False,
        },
        "baseline":baseline,
        "best_equal_copper_candidate":best,
        "candidate_count":len(candidates),
        "baseline_to_best_ratio":best["best"]["efficiency"]/baseline["best"]["efficiency"] if baseline["best"]["efficiency"]>0 else None,
        "verification":{
            "best_max_linear_residual":best["best"]["max_linear_residual"],
            "best_power_closure_error_w":best["best"]["power_closure_error_w"],
        },
        "boundaries":(
            "DipoleApproximation != FullMutualInductance",
            "EqualCopperLength != EqualMassIncludingCapacitors",
            "SkinDepthApproximation != ProximityEffectModel",
            "AllPairsNetwork != MaxwellFieldSolution",
            "OptimizedInSurrogate != Novelty",
            "Simulation != Measurement",
        ),
    }
