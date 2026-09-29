from __future__ import annotations
import hashlib, json
from dataclasses import dataclass
from typing import Mapping, Sequence

SCHEMA="tristan.matched-experiment.r206"

def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

@dataclass(frozen=True)
class ExperimentNeed:
    residual_id: str
    metric: str
    direction: str
    minimum_effect: float
    intervention: str
    baseline: str
    allowed_context: str = "local_bounded"

def compile_matched_experiment(
    need: ExperimentNeed,
    *,
    available_controls: Sequence[Mapping[str,object]],
    candidate_confounds: Sequence[str],
    budget: Mapping[str,object],
) -> dict:
    max_runs=int(budget.get("max_runs",0) or 0)
    max_seconds=float(budget.get("max_seconds",0) or 0)
    if max_runs < 2 or max_seconds <= 0:
        return {
            "schema":SCHEMA,
            "residual_id":need.residual_id,
            "status":"HOLD_INSUFFICIENT_BUDGET",
        }
    controls=[
        c for c in available_controls
        if c.get("independent") is True
        and c.get("comparable") is True
    ]
    if not controls:
        return {
            "schema":SCHEMA,
            "residual_id":need.residual_id,
            "status":"HOLD_NO_MATCHED_CONTROL",
        }
    control=sorted(
        controls,
        key=lambda c:(float(c.get("distance",999999.0)),str(c.get("control_id",""))),
    )[0]
    plan={
        "schema":SCHEMA,
        "residual_id":need.residual_id,
        "status":"EXPERIMENT_COMPILED",
        "claim_scope":"bounded matched experiment only",
        "metric":need.metric,
        "direction":need.direction,
        "minimum_effect":need.minimum_effect,
        "intervention":need.intervention,
        "baseline":need.baseline,
        "control_id":control.get("control_id"),
        "control_distance":float(control.get("distance",0.0)),
        "candidate_confounds":sorted(set(candidate_confounds)),
        "runs":{
            "intervention":max(1,max_runs//2),
            "control":max(1,max_runs-max(1,max_runs//2)),
        },
        "max_seconds":max_seconds,
        "randomization":"deterministic_alternating_order",
        "blinding":"analysis_order_hidden_until_measurements_frozen",
        "stop_rules":[
            "stop_on_budget_exhaustion",
            "stop_on_safety_or_authority_boundary",
            "do_not_promote_on_missing_control",
            "do_not_promote_on_unresolved_confound",
        ],
        "authority_granted":False,
        "external_side_effects":False,
    }
    plan["digest"]=digest(plan)
    return plan

def analyze_matched_experiment(plan:Mapping[str,object], measurements:Sequence[Mapping[str,object]])->dict:
    if plan.get("status")!="EXPERIMENT_COMPILED":
        return {"schema":SCHEMA,"status":"HOLD_BAD_PLAN"}
    intervention=[
        float(m["value"]) for m in measurements
        if m.get("arm")=="intervention" and m.get("valid") is True
    ]
    control=[
        float(m["value"]) for m in measurements
        if m.get("arm")=="control" and m.get("valid") is True
    ]
    if not intervention or not control:
        return {"schema":SCHEMA,"status":"HOLD_INCOMPLETE_MEASUREMENTS"}
    i_mean=sum(intervention)/len(intervention)
    c_mean=sum(control)/len(control)
    raw_delta=i_mean-c_mean
    direction=plan.get("direction")
    effect=(-raw_delta) if direction=="decrease" else raw_delta
    threshold=float(plan.get("minimum_effect",0.0))
    confounds=[
        str(m.get("confound"))
        for m in measurements
        if m.get("confound")
    ]
    pass_effect=effect>=threshold
    clean=len(confounds)==0
    out={
        "schema":SCHEMA,
        "status":"MATCHED_EFFECT_SUPPORTED" if pass_effect and clean else "HOLD_MATCHED_EFFECT",
        "intervention_mean":i_mean,
        "control_mean":c_mean,
        "raw_delta":raw_delta,
        "effect_in_requested_direction":effect,
        "minimum_effect":threshold,
        "unresolved_confounds":sorted(set(confounds)),
        "supports_intervention":bool(pass_effect and clean),
        "independent":True,
    }
    out["digest"]=digest(out)
    return out
