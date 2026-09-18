from __future__ import annotations

import math

from .coil_physics import MU0, CoilSpec, Vec3


def _cross(a: Vec3,b: Vec3) -> Vec3:
    return Vec3(a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x)


def _scale(a: Vec3,s: float) -> Vec3:
    return Vec3(a.x*s,a.y*s,a.z*s)


def _add(a: Vec3,b: Vec3) -> Vec3:
    return Vec3(a.x+b.x,a.y+b.y,a.z+b.z)


def _basis_from_normal(normal: Vec3) -> tuple[Vec3,Vec3]:
    n=normal.unit()
    ref=Vec3(1.0,0.0,0.0) if abs(n.x)<0.9 else Vec3(0.0,1.0,0.0)
    u=_cross(n,ref).unit()
    v=_cross(n,u).unit()
    return u,v


def circle_segments(coil: CoilSpec, segments: int=64) -> tuple[tuple[Vec3,Vec3],...]:
    if segments<8:
        raise ValueError("segments must be >= 8")
    u,v=_basis_from_normal(coil.normal)
    out=[]
    for i in range(segments):
        t0=2.0*math.pi*i/segments
        t1=2.0*math.pi*(i+1)/segments
        p0=_add(coil.center,_add(_scale(u,coil.radius_m*math.cos(t0)),_scale(v,coil.radius_m*math.sin(t0))))
        p1=_add(coil.center,_add(_scale(u,coil.radius_m*math.cos(t1)),_scale(v,coil.radius_m*math.sin(t1))))
        midpoint=_scale(_add(p0,p1),0.5)
        dl=p1-p0
        out.append((midpoint,dl))
    return tuple(out)


def neumann_mutual_inductance_h(a: CoilSpec,b: CoilSpec,segments: int=64) -> float:
    sa=circle_segments(a,segments)
    sb=circle_segments(b,segments)
    total=0.0
    min_r=float("inf")
    for pa,dla in sa:
        for pb,dlb in sb:
            rvec=pb-pa
            r=rvec.norm()
            min_r=min(min_r,r)
            if r<=0:
                raise ValueError("intersecting filament segments")
            total += dla.dot(dlb)/r
    return MU0/(4.0*math.pi)*total*a.turns*b.turns


def neumann_convergence(
    a: CoilSpec,b: CoilSpec,levels: tuple[int,...]=(32,64,128)
) -> dict[str,object]:
    values=tuple((n,neumann_mutual_inductance_h(a,b,n)) for n in levels)
    last=values[-1][1]
    prev=values[-2][1]
    scale=max(abs(last),1e-30)
    return {
        "levels":values,
        "relative_last_change":abs(last-prev)/scale,
        "value_h":last,
    }
