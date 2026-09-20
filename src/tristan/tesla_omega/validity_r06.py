from __future__ import annotations

from .architecture_r05 import coils_from_radii, equal_copper_symmetric_search, evaluate_radius_schedule
from .coil_physics import CoilSpec
from .full_coupling import full_impedance_matrix, tuned_capacitances_f
from .independent_solver import max_solution_delta, solve_lu_partial_pivot
from .rlc import _solve_complex


def dipole_separation_ratio(a: CoilSpec,b: CoilSpec) -> float:
    r=(b.center-a.center).norm()
    return r/max(a.radius_m,b.radius_m)


def minimum_pair_separation_ratio(coils: tuple[CoilSpec,...]) -> float:
    return min(
        dipole_separation_ratio(coils[i],coils[j])
        for i in range(len(coils))
        for j in range(i+1,len(coils))
    )


def independent_solver_check(
    radii_m: tuple[float,...],
    frequency_hz: float,
    source_voltage_rms: float=1.0,
) -> dict[str,float]:
    coils=coils_from_radii(radii_m)
    caps=tuned_capacitances_f(coils,159154.94309189534)
    z=full_impedance_matrix(coils,frequency_hz,caps,0,5,0.5,10.0)
    rhs=[0j for _ in coils]
    rhs[0]=complex(source_voltage_rms,0.0)
    x1=_solve_complex(z,rhs)
    x2=solve_lu_partial_pivot(z,rhs)
    return {
        "max_current_solution_delta_a": max_solution_delta(x1,x2),
        "max_current_magnitude_a": max(abs(x) for x in x1),
    }


def compile_validated_candidates(
    min_separation_ratio: float=3.0,
) -> tuple[dict[str,object],...]:
    rows=[]
    for candidate in equal_copper_symmetric_search():
        coils=coils_from_radii(candidate["radii_m"])
        ratio=minimum_pair_separation_ratio(coils)
        peak_frequency=candidate["best"]["frequency_hz"]
        solver_check=independent_solver_check(candidate["radii_m"],peak_frequency)
        rows.append({
            **candidate,
            "model_validity":{
                "min_center_distance_over_max_radius":ratio,
                "threshold":min_separation_ratio,
                "passes_far_field_screen":ratio>=min_separation_ratio,
            },
            "independent_solver":solver_check,
        })
    rows.sort(key=lambda r:(
        not r["model_validity"]["passes_far_field_screen"],
        -r["best"]["efficiency"],
        r["radii_m"],
    ))
    return tuple(rows)
