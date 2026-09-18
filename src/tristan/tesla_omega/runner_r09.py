from __future__ import annotations

from .stress_r09 import compile_stress_ladder


def compile_tesla_omega_r09(
    samples: int=16,
    seed: int=20260918,
    segments: int=24,
) -> dict[str,object]:
    ladder=compile_stress_ladder(samples=samples,seed=seed,segments=segments)
    first_failure=next(
        (
            row["name"]
            for row in ladder
            if row["candidate_win_fraction"]<1.0 or row["ratio_p10"]<=1.0
        ),
        None,
    )
    return {
        "schema_version":"tesla-omega-r0.9",
        "status":"STRESS_LADDER_SCREENING_ONLY",
        "authority_granted":False,
        "physical_validation_claimed":False,
        "novelty_claimed":False,
        "ladder":ladder,
        "first_failure_scenario":first_failure,
        "survives_all_sampled_scenarios":first_failure is None,
        "boundaries":(
            "StressSurvival != ManufacturingQualification",
            "SampledPerturbations != WorstCaseProof",
            "FilamentNeumann != FiniteWireFieldSolution",
            "Simulation != Measurement",
        ),
    }
