from __future__ import annotations

from .architecture_r05 import BASE_RADIUS_M, coils_from_radii
from .finite_wire_r11 import evaluate_finite_wire_schedule
from .runner_r08 import BEST_R07


def compile_tesla_omega_r11(segments: int=48) -> dict[str,object]:
    baseline=evaluate_finite_wire_schedule(
        coils_from_radii((BASE_RADIUS_M,)*6),segments=segments
    )
    candidate=evaluate_finite_wire_schedule(
        coils_from_radii(BEST_R07),segments=segments
    )
    ratio=(
        candidate["best"]["efficiency"]/baseline["best"]["efficiency"]
        if baseline["best"]["efficiency"]>0 else None
    )
    return {
        "schema_version":"tesla-omega-r0.11",
        "status":"FINITE_WIRE_QUADRATURE_SCREENING_ONLY",
        "authority_granted":False,
        "physical_validation_claimed":False,
        "novelty_claimed":False,
        "cross_section_model":"4-filament equal-weight quadrature",
        "segments_per_filament":segments,
        "baseline":baseline,
        "candidate":candidate,
        "relative_ratio":ratio,
        "verification":{
            "candidate_solver_delta_a":candidate["best"]["solver_delta_a"],
            "candidate_power_closure_error_w":candidate["best"]["power_closure_error_w"],
        },
        "boundaries":(
            "FourFilamentQuadrature != ExactFiniteConductorField",
            "FiniteWireMutual != ProximityEffectLoss",
            "ThinLoopSelfInductanceStillApproximate",
            "Simulation != Measurement",
        ),
    }
