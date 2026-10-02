from __future__ import annotations
import hashlib, json
from dataclasses import dataclass
from typing import Mapping, Sequence

SCHEMA="tristan.causal-effect.r205"

def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

@dataclass(frozen=True)
class OutcomeContract:
    outcome_id: str
    metric: str
    direction: str
    minimum_delta: float
    baseline_ref: str
    observation_ref: str
    freshness_required: bool = True
    independence_required: bool = True

def verify_outcome_contract(contract: OutcomeContract, evidence: Mapping[str,object]) -> dict:
    baseline=float(evidence.get("baseline",0.0))
    observed=float(evidence.get("observed",0.0))
    fresh=bool(evidence.get("fresh",False))
    independent=bool(evidence.get("independent",False))
    delta=observed-baseline
    if contract.direction=="increase":
        metric_pass=delta >= contract.minimum_delta
    elif contract.direction=="decrease":
        metric_pass=(-delta) >= contract.minimum_delta
    else:
        return {"schema":SCHEMA,"status":"HOLD_BAD_DIRECTION","outcome_id":contract.outcome_id}
    freshness_pass=(not contract.freshness_required) or fresh
    independence_pass=(not contract.independence_required) or independent
    observed_pass=bool(evidence.get("outcome_observed",False))
    ok=metric_pass and freshness_pass and independence_pass and observed_pass
    out={
        "schema":SCHEMA,
        "outcome_id":contract.outcome_id,
        "metric":contract.metric,
        "baseline":baseline,
        "observed":observed,
        "delta":delta,
        "metric_pass":metric_pass,
        "freshness_pass":freshness_pass,
        "independence_pass":independence_pass,
        "outcome_observed":observed_pass,
        "status":"OUTCOME_CONTRACT_PASS" if ok else "HOLD_OUTCOME_CONTRACT",
    }
    out["digest"]=digest(out)
    return out

def causal_attribution(
    *,
    execution_verified: bool,
    local_effect_verified: bool,
    outcome_contract: Mapping[str,object],
    controls: Sequence[Mapping[str,object]] = (),
    confounds: Sequence[str] = (),
) -> dict:
    outcome_pass=outcome_contract.get("status")=="OUTCOME_CONTRACT_PASS"
    control_support=sum(
        1 for c in controls
        if c.get("independent") is True
        and c.get("supports_intervention") is True
    )
    no_unresolved_confounds=len(tuple(confounds))==0
    causal_supported=(
        execution_verified
        and local_effect_verified
        and outcome_pass
        and control_support >= 1
        and no_unresolved_confounds
    )
    out={
        "schema":SCHEMA,
        "execution_verified":bool(execution_verified),
        "local_effect_verified":bool(local_effect_verified),
        "outcome_contract_pass":bool(outcome_pass),
        "independent_control_support":control_support,
        "unresolved_confounds":list(confounds),
        "causal_effect_supported":causal_supported,
        "status":"CAUSAL_EFFECT_SUPPORTED" if causal_supported else "HOLD_CAUSAL_ATTRIBUTION",
        "claim_scope":"supports bounded causal attribution only; not universal mechanism proof",
    }
    out["digest"]=digest(out)
    return out

def feedback_decision(
    *,
    causal_receipt: Mapping[str,object],
    current_node: str,
    candidate_nodes: Sequence[Mapping[str,object]],
    required_capabilities: Sequence[str],
) -> dict:
    if causal_receipt.get("causal_effect_supported") is not True:
        return {
            "schema":SCHEMA,
            "status":"NO_ACTION_UNVERIFIED_CAUSAL_GAIN",
            "current_node":current_node,
            "next_node":current_node,
        }
    eligible=[]
    need=set(required_capabilities)
    for n in candidate_nodes:
        caps=set(n.get("capabilities",()))
        if not need.issubset(caps):
            continue
        score=float(n.get("verified_gain_per_cost",0.0))
        eligible.append((score,str(n.get("node"))))
    if not eligible:
        return {
            "schema":SCHEMA,
            "status":"HOLD_NO_ELIGIBLE_NODE",
            "current_node":current_node,
            "next_node":None,
        }
    eligible.sort(reverse=True)
    next_node=eligible[0][1]
    return {
        "schema":SCHEMA,
        "status":"KEEP_CURRENT" if next_node==current_node else "REAUCTION",
        "current_node":current_node,
        "next_node":next_node,
        "winner_score":eligible[0][0],
    }
