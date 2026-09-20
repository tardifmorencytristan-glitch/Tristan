from __future__ import annotations

import math

from .coil_physics import CoilSpec, ac_resistance_skin_approx, dipole_mutual_inductance_h, self_inductance_thin_loop_h
from .rlc import _solve_complex


def tuned_capacitances_f(coils: tuple[CoilSpec,...], target_frequency_hz: float) -> tuple[float,...]:
    if target_frequency_hz<=0:
        raise ValueError("target frequency must be positive")
    w=2.0*math.pi*target_frequency_hz
    return tuple(1.0/(w*w*self_inductance_thin_loop_h(c)) for c in coils)


def full_impedance_matrix(
    coils: tuple[CoilSpec,...],
    frequency_hz: float,
    capacitances_f: tuple[float,...],
    source_node: int,
    receiver_node: int,
    source_resistance_ohm: float,
    load_resistance_ohm: float,
) -> list[list[complex]]:
    n=len(coils)
    if len(capacitances_f)!=n:
        raise ValueError("capacitance count mismatch")
    w=2.0*math.pi*frequency_hz
    z=[[0j for _ in range(n)] for _ in range(n)]
    for i,coil in enumerate(coils):
        l=self_inductance_thin_loop_h(coil)
        r=ac_resistance_skin_approx(coil,frequency_hz)
        extra=(source_resistance_ohm if i==source_node else 0.0)+(load_resistance_ohm if i==receiver_node else 0.0)
        z[i][i]=complex(r+extra,w*l-1.0/(w*capacitances_f[i]))
    for i in range(n):
        for j in range(i+1,n):
            m=dipole_mutual_inductance_h(coils[i],coils[j])
            zij=complex(0.0,w*m)
            z[i][j]=zij
            z[j][i]=zij
    return z


def solve_full_coupling(
    coils: tuple[CoilSpec,...],
    frequency_hz: float,
    capacitances_f: tuple[float,...],
    source_node: int=0,
    receiver_node: int=5,
    source_resistance_ohm: float=0.5,
    load_resistance_ohm: float=10.0,
    source_voltage_rms: float=1.0,
) -> dict[str,object]:
    z=full_impedance_matrix(
        coils,frequency_hz,capacitances_f,source_node,receiver_node,
        source_resistance_ohm,load_resistance_ohm,
    )
    rhs=[0j for _ in coils]
    rhs[source_node]=complex(source_voltage_rms,0.0)
    currents=_solve_complex(z,rhs)
    source_current=currents[source_node]
    load_power=abs(currents[receiver_node])**2*load_resistance_ohm
    source_power=(complex(source_voltage_rms,0.0)*source_current.conjugate()).real
    copper_loss=sum(abs(currents[i])**2*ac_resistance_skin_approx(coils[i],frequency_hz) for i in range(len(coils)))
    source_loss=abs(source_current)**2*source_resistance_ohm
    residual=[]
    for i,row in enumerate(z):
        reconstructed=sum(row[j]*currents[j] for j in range(len(coils)))
        residual.append(abs(reconstructed-rhs[i]))
    accounted=load_power+copper_loss+source_loss
    return {
        "efficiency": load_power/source_power if source_power>0 else 0.0,
        "source_power_w": source_power,
        "load_power_w": load_power,
        "copper_loss_w": copper_loss,
        "source_loss_w": source_loss,
        "power_closure_error_w": abs(source_power-accounted),
        "max_linear_residual": max(residual),
        "currents_abs_a": tuple(abs(i) for i in currents),
    }
