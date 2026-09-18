from __future__ import annotations

from .architecture_r05 import BASE_RADIUS_M
from .robust_neumann_r08 import paired_robustness


BEST_R07=(0.04,0.035,0.015,0.015,0.035,0.04)


def compile_tesla_omega_r08(
    samples: int=24,
    seed: int=20260918,
    segments: int=32,
) -> dict[str,object]:
    result=paired_robustness(
        (BASE_RADIUS_M,)*6,
        BEST_R07,
        samples=samples,
        seed=seed,
        segments=segments,
    )
    return {
        "schema_version":"tesla-omega-r0.8",
        "status":"PAIRED_GEOMETRIC_ROBUSTNESS_SCREENING_ONLY",
        "authority_granted":False,
        "physical_validation_claimed":False,
        "novelty_claimed":False,
        "perturbations":{
            "intermediate_position_jitter_m":0.005,
            "tilt_deg":5.0,
            "radius_tolerance_fraction":0.02,
            "tx_rx_centers_fixed":True,
            "paired_random_seeds":True,
        },
        "result":result,
        "boundaries":(
            "MonteCarloRobustness != ManufacturingValidation",
            "FilamentNeumann != FiniteWireFieldSolution",
            "RadiusToleranceModel != FullFabricationTolerance",
            "TiltModel != MechanicalAssemblyModel",
            "Simulation != Measurement",
        ),
    }
