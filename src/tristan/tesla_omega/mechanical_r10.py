from __future__ import annotations

import math
import random

from .architecture_r05 import BASE_RADIUS_M
from .coil_physics import CoilSpec
from .full_coupling_neumann import evaluate_neumann_schedule
from .robust_neumann_r08 import perturb_coils
from .runner_r08 import BEST_R07


def center_distance(a: CoilSpec,b: CoilSpec) -> float:
    return (b.center-a.center).norm()


def conservative_clearance_margin_m(
    a: CoilSpec,
    b: CoilSpec,
    clearance_m: float=0.005,
) -> float:
    # Conservative bounding-sphere screen. Passing is sufficient, not necessary.
    return center_distance(a,b)-(a.radius_m+b.radius_m+clearance_m)


def minimum_clearance_margin_m(
    coils: tuple[CoilSpec,...],
    clearance_m: float=0.005,
) -> float:
    return min(
        conservative_clearance_margin_m(coils[i],coils[j],clearance_m)
        for i in range(len(coils))
        for j in range(i+1,len(coils))
    )


def mechanically_valid(
    coils: tuple[CoilSpec,...],
    clearance_m: float=0.005,
) -> bool:
    return minimum_clearance_margin_m(coils,clearance_m)>=0.0


def paired_mechanical_robustness(
    samples: int=48,
    seed: int=20260918,
    segments: int=24,
    clearance_m: float=0.005,
    position_jitter_m: float=0.020,
    tilt_deg: float=20.0,
    radius_tolerance: float=0.10,
) -> dict[str,object]:
    accepted=0
    rejected_mechanical=0
    wins=0
    losses=0
    ratios=[]
    base_margins=[]
    cand_margins=[]

    for sample in range(samples):
        s=seed+sample
        base=perturb_coils(
            (BASE_RADIUS_M,)*6,random.Random(s),
            position_jitter_m=position_jitter_m,
            tilt_deg=tilt_deg,
            radius_tolerance=radius_tolerance,
        )
        cand=perturb_coils(
            BEST_R07,random.Random(s),
            position_jitter_m=position_jitter_m,
            tilt_deg=tilt_deg,
            radius_tolerance=radius_tolerance,
        )
        mb=minimum_clearance_margin_m(base,clearance_m)
        mc=minimum_clearance_margin_m(cand,clearance_m)
        base_margins.append(mb)
        cand_margins.append(mc)
        if mb<0 or mc<0:
            rejected_mechanical+=1
            continue

        b=evaluate_neumann_schedule(base,segments=segments,points=25)["best"]["efficiency"]
        c=evaluate_neumann_schedule(cand,segments=segments,points=25)["best"]["efficiency"]
        accepted+=1
        if c>b:
            wins+=1
        else:
            losses+=1
        ratios.append(c/b if b>0 else float("inf"))

    if ratios:
        ordered=sorted(ratios)
        ratio_stats={
            "min":ordered[0],
            "p10":ordered[max(0,int(0.10*(len(ordered)-1)))],
            "median":ordered[len(ordered)//2],
            "max":ordered[-1],
            "mean":sum(ratios)/len(ratios),
        }
    else:
        ratio_stats=None

    return {
        "samples":samples,
        "accepted":accepted,
        "rejected_mechanical":rejected_mechanical,
        "rejection_fraction":rejected_mechanical/samples,
        "wins":wins,
        "losses":losses,
        "candidate_win_fraction_on_valid":wins/accepted if accepted else None,
        "paired_ratio_on_valid":ratio_stats,
        "minimum_baseline_margin_m":min(base_margins),
        "minimum_candidate_margin_m":min(cand_margins),
        "clearance_m":clearance_m,
    }
