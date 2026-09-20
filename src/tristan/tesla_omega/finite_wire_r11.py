from __future__ import annotations

import math

from .coil_physics import CoilSpec, Vec3
from .full_coupling import tuned_capacitances_f
from .full_coupling_neumann import solve_neumann_network
from .neumann import neumann_mutual_inductance_h


def _shift(v: Vec3, direction: Vec3, amount: float) -> Vec3:
    return Vec3(v.x+direction.x*amount,v.y+direction.y*amount,v.z+direction.z*amount)


def cross_section_filaments(coil: CoilSpec) -> tuple[CoilSpec,...]:
    # Four-point cross-section quadrature: +/- radial radius and +/- normal center.
    d=coil.wire_radius_m/math.sqrt(2.0)
    n=coil.normal.unit()
    radii=(coil.radius_m-d,coil.radius_m+d)
    if radii[0]<=coil.wire_radius_m:
        raise ValueError("wire too thick for finite-wire quadrature")
    return (
        CoilSpec(_shift(coil.center,n,-d),coil.normal,radii[0],coil.wire_radius_m,coil.turns),
        CoilSpec(_shift(coil.center,n,-d),coil.normal,radii[1],coil.wire_radius_m,coil.turns),
        CoilSpec(_shift(coil.center,n, d),coil.normal,radii[0],coil.wire_radius_m,coil.turns),
        CoilSpec(_shift(coil.center,n, d),coil.normal,radii[1],coil.wire_radius_m,coil.turns),
    )


def finite_wire_mutual_inductance_h(
    a: CoilSpec,b: CoilSpec,segments: int=48
) -> float:
    fa=cross_section_filaments(a)
    fb=cross_section_filaments(b)
    values=[
        neumann_mutual_inductance_h(x,y,segments)
        for x in fa
        for y in fb
    ]
    return sum(values)/len(values)


def finite_wire_mutual_matrix_h(
    coils: tuple[CoilSpec,...],segments: int=48
) -> tuple[tuple[float,...],...]:
    n=len(coils)
    m=[[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n):
            value=finite_wire_mutual_inductance_h(coils[i],coils[j],segments)
            m[i][j]=m[j][i]=value
    return tuple(tuple(row) for row in m)


def evaluate_finite_wire_schedule(
    coils: tuple[CoilSpec,...],
    target_frequency_hz: float=159154.94309189534,
    segments: int=48,
    points: int=41,
) -> dict[str,object]:
    caps=tuned_capacitances_f(coils,target_frequency_hz)
    mutual=finite_wire_mutual_matrix_h(coils,segments)
    best=None
    for i in range(points):
        alpha=i/(points-1)
        f=target_frequency_hz*(0.80+0.40*alpha)
        row=solve_neumann_network(coils,f,caps,mutual)
        if best is None or row["efficiency"]>best["efficiency"]:
            best={"frequency_hz":f,**row}
    return {"best":best,"mutual_h":mutual,"segments":segments}
