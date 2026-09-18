from __future__ import annotations

from .architecture_r05 import BASE_RADIUS_M, evaluate_radius_schedule
from .validity_r06 import compile_validated_candidates, minimum_pair_separation_ratio
from .architecture_r05 import coils_from_radii


def compile_tesla_omega_r06() -> dict[str,object]:
    baseline=evaluate_radius_schedule((BASE_RADIUS_M,)*6)
    baseline_ratio=minimum_pair_separation_ratio(coils_from_radii((BASE_RADIUS_M,)*6))
    candidates=compile_validated_candidates(min_separation_ratio=3.0)
    survivors=tuple(c for c in candidates if c["model_validity"]["passes_far_field_screen"])
    best_survivor=survivors[0] if survivors else None
    return {
        "schema_version":"tesla-omega-r0.6",
        "status":"MODEL_VALIDITY_GATED_SCREENING_ONLY",
        "authority_granted":False,
        "physical_validation_claimed":False,
        "novelty_claimed":False,
        "validity_rule":"min pair center distance / max pair radius >= 3.0",
        "baseline":{
            **baseline,
            "min_separation_ratio":baseline_ratio,
        },
        "candidate_count":len(candidates),
        "survivor_count":len(survivors),
        "best_survivor":best_survivor,
        "discarded_best_unconstrained":next((c for c in candidates if not c["model_validity"]["passes_far_field_screen"]),None),
        "boundaries":(
            "FarFieldScreenPass != ExactMutualInductance",
            "IndependentLinearSolverAgreement != PhysicsValidation",
            "DipoleModel != NearFieldCoilModel",
            "SurrogateGain != MeasuredGain",
            "Simulation != Measurement",
        ),
    }
