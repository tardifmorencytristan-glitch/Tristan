from __future__ import annotations

from .architecture_r05 import BASE_RADIUS_M
from .robust_neumann_r08 import paired_robustness
from .runner_r08 import BEST_R07


SCENARIOS=(
    {"name":"S1_mild","position_jitter_m":0.002,"tilt_deg":2.0,"radius_tolerance":0.01},
    {"name":"S2_nominal","position_jitter_m":0.005,"tilt_deg":5.0,"radius_tolerance":0.02},
    {"name":"S3_strong","position_jitter_m":0.010,"tilt_deg":10.0,"radius_tolerance":0.05},
    {"name":"S4_extreme","position_jitter_m":0.020,"tilt_deg":20.0,"radius_tolerance":0.10},
)


def compile_stress_ladder(
    samples: int=16,
    seed: int=20260918,
    segments: int=24,
) -> tuple[dict[str,object],...]:
    from .robust_neumann_r08 import perturb_coils
    from .full_coupling_neumann import evaluate_neumann_schedule
    import random, math

    rows=[]
    for scenario_index,scenario in enumerate(SCENARIOS):
        ratios=[]
        wins=0
        base_values=[]
        cand_values=[]
        for sample in range(samples):
            s=seed+10000*scenario_index+sample
            rb=random.Random(s)
            rc=random.Random(s)
            base=perturb_coils(
                (BASE_RADIUS_M,)*6,rb,
                position_jitter_m=scenario["position_jitter_m"],
                tilt_deg=scenario["tilt_deg"],
                radius_tolerance=scenario["radius_tolerance"],
            )
            cand=perturb_coils(
                BEST_R07,rc,
                position_jitter_m=scenario["position_jitter_m"],
                tilt_deg=scenario["tilt_deg"],
                radius_tolerance=scenario["radius_tolerance"],
            )
            b=evaluate_neumann_schedule(base,segments=segments,points=25)["best"]["efficiency"]
            c=evaluate_neumann_schedule(cand,segments=segments,points=25)["best"]["efficiency"]
            base_values.append(b); cand_values.append(c)
            ratios.append(c/b if b>0 else float("inf"))
            if c>b: wins+=1

        ordered=sorted(ratios)
        mean=sum(ratios)/len(ratios)
        var=sum((x-mean)**2 for x in ratios)/len(ratios)
        rows.append({
            **scenario,
            "samples":samples,
            "candidate_win_fraction":wins/samples,
            "ratio_mean":mean,
            "ratio_std":math.sqrt(var),
            "ratio_min":ordered[0],
            "ratio_p10":ordered[max(0,int(0.10*(len(ordered)-1)))],
            "ratio_median":ordered[len(ordered)//2],
            "ratio_max":ordered[-1],
            "baseline_mean_efficiency":sum(base_values)/len(base_values),
            "candidate_mean_efficiency":sum(cand_values)/len(cand_values),
        })
    return tuple(rows)
