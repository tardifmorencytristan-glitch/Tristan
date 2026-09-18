from __future__ import annotations

import math
from dataclasses import dataclass

MU0 = 4.0e-7 * math.pi
COPPER_RESISTIVITY_OHM_M = 1.724e-8
COPPER_CONDUCTIVITY_S_M = 1.0 / COPPER_RESISTIVITY_OHM_M


@dataclass(frozen=True)
class Vec3:
    x: float
    y: float
    z: float

    def dot(self, other: "Vec3") -> float:
        return self.x*other.x + self.y*other.y + self.z*other.z

    def norm(self) -> float:
        return math.sqrt(self.dot(self))

    def unit(self) -> "Vec3":
        n=self.norm()
        if n<=0:
            raise ValueError("zero vector")
        return Vec3(self.x/n,self.y/n,self.z/n)

    def __sub__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x-other.x,self.y-other.y,self.z-other.z)


@dataclass(frozen=True)
class CoilSpec:
    center: Vec3
    normal: Vec3
    radius_m: float
    wire_radius_m: float = 0.0005
    turns: int = 1

    def __post_init__(self):
        if self.radius_m<=0 or self.wire_radius_m<=0 or self.turns<1:
            raise ValueError("invalid coil geometry")
        if self.wire_radius_m >= self.radius_m:
            raise ValueError("wire radius must be smaller than coil radius")
        self.normal.unit()

    @property
    def area_m2(self) -> float:
        return math.pi*self.radius_m**2

    @property
    def wire_length_m(self) -> float:
        return 2.0*math.pi*self.radius_m*self.turns


def skin_depth_m(
    frequency_hz: float,
    conductivity_s_m: float = COPPER_CONDUCTIVITY_S_M,
    permeability_h_m: float = MU0,
) -> float:
    if frequency_hz<=0 or conductivity_s_m<=0 or permeability_h_m<=0:
        raise ValueError("invalid skin-depth parameters")
    return 1.0/math.sqrt(math.pi*frequency_hz*permeability_h_m*conductivity_s_m)


def ac_resistance_skin_approx(
    coil: CoilSpec,
    frequency_hz: float,
    resistivity_ohm_m: float = COPPER_RESISTIVITY_OHM_M,
) -> float:
    if resistivity_ohm_m<=0:
        raise ValueError("resistivity must be positive")
    delta=skin_depth_m(frequency_hz,1.0/resistivity_ohm_m)
    a=coil.wire_radius_m
    inner=max(0.0,a-delta)
    effective_area=math.pi*(a*a-inner*inner)
    return resistivity_ohm_m*coil.wire_length_m/effective_area


def self_inductance_thin_loop_h(coil: CoilSpec) -> float:
    # High-frequency external-inductance approximation for thin circular wire.
    ratio=8.0*coil.radius_m/coil.wire_radius_m
    value=MU0*coil.radius_m*(math.log(ratio)-2.0)*(coil.turns**2)
    if value<=0:
        raise ValueError("coil too thick for thin-loop approximation")
    return value


def dipole_mutual_inductance_h(a: CoilSpec, b: CoilSpec) -> float:
    # Far-field magnetic-dipole approximation. Signed by orientation.
    rvec=b.center-a.center
    r=rvec.norm()
    if r<=max(a.radius_m,b.radius_m):
        raise ValueError("dipole approximation requires separation exceeding coil radius")
    rhat=rvec.unit()
    n1=a.normal.unit()
    n2=b.normal.unit()
    orientation=3.0*n1.dot(rhat)*n2.dot(rhat)-n1.dot(n2)
    return (
        MU0
        * a.turns*b.turns
        * a.area_m2*b.area_m2
        * orientation
        / (4.0*math.pi*r**3)
    )


def total_wire_length_m(coils: tuple[CoilSpec,...]) -> float:
    return sum(c.wire_length_m for c in coils)
