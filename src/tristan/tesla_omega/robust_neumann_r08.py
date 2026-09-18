from __future__ import annotations

import math
import random

from .architecture_r05 import coils_from_radii
from .coil_physics import CoilSpec, Vec3
from .full_coupling_neumann import evaluate_neumann_schedule


def _rotate_small(normal: Vec3, tilt_x_rad: float, tilt_y_rad: float) -> Vec3:
    # Small deterministic two-axis rotation, then normalize.
    x,y,z=normal.x,normal.y,normal.z
    cy,sy=math.cos(tilt_y_rad),math.sin(tilt_y_rad)
    x,z=cy*x+sy*z,-sy*x+cy*z
    cx,sx=math.cos(tilt_x_rad),math.sin(tilt_x_rad)
    y,z=cx*y-sx*z,sx*y+cx*z
    return Vec3(x,y,z).unit()


def perturb_coils(
    radii_m: tuple[float,...],
    rng: random.Random,
    position_jitter_m: float=0.005,
    tilt_deg: float=5.0,
    radius_tolerance: float=0.02,
) -> tuple[CoilSpec,...]:
    base=coils_from_radii(radii_m)
    out=[]
    for i,c in enumerate(base):
        if i in (0,len(base)-1):
            center=c.center
        else:
            center=Vec3(
                c.center.x+rng.uniform(-position_jitter_m,position_jitter_m),
                c.center.y+rng.uniform(-position_jitter_m,position_jitter_m),
                c.center.z+rng.uniform(-position_jitter_m,position_jitter_m),
            )
        tilt=math.radians(tilt_deg)
        normal=_rotate_small(
            c.normal,
            rng.uniform(-tilt,tilt),
            rng.uniform(-tilt,tilt),
        )
        radius=c.radius_m*(1.0+rng.uniform(-radius_tolerance,radius_tolerance))
        out.append(CoilSpec(center,normal,radius,c.wire_radius_m,c.turns))
    return tuple(out)


def paired_robustness(
    baseline_radii: tuple[float,...],
    candidate_radii: tuple[float,...],
    samples: int=24,
    seed: int=20260918,
    segments: int=32,
) -> dict[str,object]:
    baseline_eta=[]
    candidate_eta=[]
    ratios=[]
    for sample in range(samples):
        sample_seed=seed+sample
        rb=random.Random(sample_seed)
        rc=random.Random(sample_seed)
        base_coils=perturb_coils(baseline_radii,rb)
        cand_coils=perturb_coils(candidate_radii,rc)
        base=evaluate_neumann_schedule(base_coils,segments=segments,points=31)["best"]["efficiency"]
        cand=evaluate_neumann_schedule(cand_coils,segments=segments,points=31)["best"]["efficiency"]
        baseline_eta.append(base)
        candidate_eta.append(cand)
        ratios.append(cand/base if base>0 else float("inf"))

    def stats(values: list[float]) -> dict[str,float]:
        ordered=sorted(values)
        mean=sum(values)/len(values)
        variance=sum((x-mean)**2 for x in values)/len(values)
        return {
            "mean":mean,
            "std":math.sqrt(variance),
            "min":ordered[0],
            "p10":ordered[max(0,int(0.10*(len(ordered)-1)))],
            "median":ordered[len(ordered)//2],
            "max":ordered[-1],
        }

    wins=sum(1 for c,b in zip(candidate_eta,baseline_eta) if c>b)
    return {
        "samples":samples,
        "seed":seed,
        "segments":segments,
        "baseline":stats(baseline_eta),
        "candidate":stats(candidate_eta),
        "paired_ratio":stats(ratios),
        "candidate_win_fraction":wins/samples,
    }
