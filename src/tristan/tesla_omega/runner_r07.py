from __future__ import annotations

from .architecture_r05 import BASE_RADIUS_M, coils_from_radii
from .full_coupling_neumann import evaluate_neumann_schedule
from .neumann import neumann_convergence
from .validity_r06 import compile_validated_candidates


def compile_tesla_omega_r07(top_candidates: int=5) -> dict[str,object]:
    baseline_radii=(BASE_RADIUS_M,)*6
    baseline_coils=coils_from_radii(baseline_radii)
    baseline=evaluate_neumann_schedule(baseline_coils,segments=64)
    r06=compile_validated_candidates(3.0)
    survivors=[c for c in r06 if c["model_validity"]["passes_far_field_screen"]][:top_candidates]
    rows=[]
    for c in survivors:
        coils=coils_from_radii(c["radii_m"])
        neumann=evaluate_neumann_schedule(coils,segments=64)
        rows.append({
            "radii_m":c["radii_m"],
            "dipole_efficiency":c["best"]["efficiency"],
            "neumann":neumann,
        })
    rows.sort(key=lambda r:-r["neumann"]["best"]["efficiency"])
    best=rows[0] if rows else None
    pair_conv=neumann_convergence(baseline_coils[0],baseline_coils[1])
    return {
        "schema_version":"tesla-omega-r0.7",
        "status":"NEUMANN_FILAMENT_SCREENING_ONLY",
        "authority_granted":False,
        "physical_validation_claimed":False,
        "novelty_claimed":False,
        "baseline":baseline,
        "candidate_count":len(rows),
        "candidates":tuple(rows),
        "best_candidate":best,
        "adjacent_pair_neumann_convergence":pair_conv,
        "verification":{
            "best_solver_delta_a":None if best is None else best["neumann"]["best"]["solver_delta_a"],
            "best_power_closure_error_w":None if best is None else best["neumann"]["best"]["power_closure_error_w"],
        },
        "boundaries":(
            "FilamentNeumann != FiniteWireFieldSolution",
            "ThinLoopSelfInductance != ExactSelfInductance",
            "NoProximityEffect != FullACLossModel",
            "NumericalConvergence != ExperimentalValidation",
            "Simulation != Measurement",
        ),
    }
