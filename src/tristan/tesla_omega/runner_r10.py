from __future__ import annotations

from .architecture_r05 import BASE_RADIUS_M, coils_from_radii
from .mechanical_r10 import minimum_clearance_margin_m, paired_mechanical_robustness
from .runner_r08 import BEST_R07


def compile_tesla_omega_r10(
    samples: int=48,
    seed: int=20260918,
    segments: int=24,
) -> dict[str,object]:
    baseline_margin=minimum_clearance_margin_m(coils_from_radii((BASE_RADIUS_M,)*6))
    candidate_margin=minimum_clearance_margin_m(coils_from_radii(BEST_R07))
    stress=paired_mechanical_robustness(
        samples=samples,seed=seed,segments=segments
    )
    return {
        "schema_version":"tesla-omega-r0.10",
        "status":"MECHANICALLY_GATED_ROBUSTNESS_SCREENING_ONLY",
        "authority_granted":False,
        "physical_validation_claimed":False,
        "novelty_claimed":False,
        "nominal":{
            "baseline_clearance_margin_m":baseline_margin,
            "candidate_clearance_margin_m":candidate_margin,
            "clearance_requirement_m":0.005,
        },
        "stress":stress,
        "interpretation":{
            "mechanical_rejections_are_not_performance_losses":True,
            "bounding_sphere_gate_is_conservative":True,
        },
        "boundaries":(
            "BoundingSpherePass != DetailedCADClearance",
            "BoundingSphereReject != PhysicalImpossibility",
            "MechanicalGate != ManufacturingQualification",
            "FilamentNeumann != FiniteWireFieldSolution",
            "Simulation != Measurement",
        ),
    }
