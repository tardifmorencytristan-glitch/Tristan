from __future__ import annotations

from .coil_physics import CoilSpec, Vec3, total_wire_length_m
from .full_coupling import solve_full_coupling, tuned_capacitances_f
from .geometry import hex_bridge_geometry


TARGET_FREQUENCY_HZ=159154.94309189534
BASE_RADIUS_M=0.03
WIRE_RADIUS_M=0.0005


def coils_from_radii(radii_m: tuple[float,...]) -> tuple[CoilSpec,...]:
    pts=hex_bridge_geometry()
    if len(radii_m)!=len(pts):
        raise ValueError("radius count mismatch")
    return tuple(
        CoilSpec(
            center=Vec3(p.x,p.y,p.z),
            normal=Vec3(0.0,0.0,1.0),
            radius_m=r,
            wire_radius_m=WIRE_RADIUS_M,
            turns=1,
        )
        for p,r in zip(pts,radii_m)
    )


def evaluate_radius_schedule(
    radii_m: tuple[float,...],
    frequency_points: int=61,
) -> dict[str,object]:
    coils=coils_from_radii(radii_m)
    caps=tuned_capacitances_f(coils,TARGET_FREQUENCY_HZ)
    best=None
    for i in range(frequency_points):
        alpha=i/(frequency_points-1)
        f=TARGET_FREQUENCY_HZ*(0.80+0.40*alpha)
        row=solve_full_coupling(coils,f,caps)
        if best is None or row["efficiency"]>best["efficiency"]:
            best={"frequency_hz":f,**row}
    return {
        "radii_m":radii_m,
        "wire_length_m":total_wire_length_m(coils),
        "capacitances_f":caps,
        "best":best,
    }


def equal_copper_symmetric_search(step_m: float=0.005) -> tuple[dict[str,object],...]:
    # Symmetric schedule [a,b,c,c,b,a], with a+b+c fixed to preserve total copper.
    target_triplet_sum=3.0*BASE_RADIUS_M
    values=[]
    x=0.015
    while x<=0.0450000001:
        values.append(round(x,6))
        x+=step_m
    rows=[]
    for a in values:
        for b in values:
            c=target_triplet_sum-a-b
            if c<0.015-1e-12 or c>0.045+1e-12:
                continue
            radii=(a,b,c,c,b,a)
            result=evaluate_radius_schedule(radii)
            result["family"]="symmetric_equal_copper"
            rows.append(result)
    rows.sort(key=lambda r:(-r["best"]["efficiency"],r["radii_m"]))
    return tuple(rows)
