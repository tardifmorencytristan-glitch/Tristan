from __future__ import annotations

import math

from .coil_physics import CoilSpec, ac_resistance_skin_approx, self_inductance_thin_loop_h
from .full_coupling import tuned_capacitances_f
from .independent_solver import solve_lu_partial_pivot
from .neumann import neumann_mutual_inductance_h
from .rlc import _solve_complex


def mutual_matrix_h(coils: tuple[CoilSpec,...],segments: int=64) -> tuple[tuple[float,...],...]:
    n=len(coils)
    m=[[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n):
            value=neumann_mutual_inductance_h(coils[i],coils[j],segments)
            m[i][j]=value
            m[j][i]=value
    return tuple(tuple(row) for row in m)


def solve_neumann_network(
    coils: tuple[CoilSpec,...],
    frequency_hz: float,
    capacitances_f: tuple[float,...],
    mutual_h: tuple[tuple[float,...],...],
    source_node: int=0,
    receiver_node: int=5,
    source_resistance_ohm: float=0.5,
    load_resistance_ohm: float=10.0,
) -> dict[str,object]:
    n=len(coils)
    w=2.0*math.pi*frequency_hz
    z=[[0j]*n for _ in range(n)]
    for i,c in enumerate(coils):
        l=self_inductance_thin_loop_h(c)
        r=ac_resistance_skin_approx(c,frequency_hz)
        extra=(source_resistance_ohm if i==source_node else 0.0)+(load_resistance_ohm if i==receiver_node else 0.0)
        z[i][i]=complex(r+extra,w*l-1.0/(w*capacitances_f[i]))
    for i in range(n):
        for j in range(i+1,n):
            z[i][j]=z[j][i]=complex(0.0,w*mutual_h[i][j])
    rhs=[0j]*n
    rhs[source_node]=1+0j
    x1=_solve_complex(z,rhs)
    x2=solve_lu_partial_pivot(z,rhs)
    source_power=(complex(1.0,0.0)*x1[source_node].conjugate()).real
    load_power=abs(x1[receiver_node])**2*load_resistance_ohm
    copper_loss=sum(abs(x1[i])**2*ac_resistance_skin_approx(coils[i],frequency_hz) for i in range(n))
    source_loss=abs(x1[source_node])**2*source_resistance_ohm
    return {
        "efficiency":load_power/source_power if source_power>0 else 0.0,
        "source_power_w":source_power,
        "load_power_w":load_power,
        "copper_loss_w":copper_loss,
        "source_loss_w":source_loss,
        "power_closure_error_w":abs(source_power-(load_power+copper_loss+source_loss)),
        "solver_delta_a":max(abs(a-b) for a,b in zip(x1,x2)),
    }


def evaluate_neumann_schedule(
    coils: tuple[CoilSpec,...],
    target_frequency_hz: float=159154.94309189534,
    segments: int=64,
    points: int=41,
) -> dict[str,object]:
    caps=tuned_capacitances_f(coils,target_frequency_hz)
    mutual=mutual_matrix_h(coils,segments)
    best=None
    for i in range(points):
        alpha=i/(points-1)
        f=target_frequency_hz*(0.80+0.40*alpha)
        row=solve_neumann_network(coils,f,caps,mutual)
        if best is None or row["efficiency"]>best["efficiency"]:
            best={"frequency_hz":f,**row}
    return {"best":best,"mutual_h":mutual,"segments":segments}
