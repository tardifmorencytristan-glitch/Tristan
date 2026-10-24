from __future__ import annotations
import hashlib, json
from typing import Mapping, Sequence

SCHEMA="tristan.effect-verifier.r204"

def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

def verify_local_effect(receipt:Mapping[str,object], artifact_sha256:str)->dict:
    execution_ok=receipt.get("execution_status")=="VERIFIED"
    artifact_ok=bool(artifact_sha256) and artifact_sha256==receipt.get("artifact_sha256")
    boundary_ok=(
        receipt.get("authority_granted") is False
        and receipt.get("external_side_effects") is False
        and receipt.get("money_spent")==0
        and receipt.get("public_publish") is False
    )
    local_effect_ok=execution_ok and artifact_ok and boundary_ok
    out={
        "schema":SCHEMA,
        "mission_id":receipt.get("mission_id"),
        "execution_verified":execution_ok,
        "artifact_verified":artifact_ok,
        "boundary_verified":boundary_ok,
        "local_effect_verified":local_effect_ok,
        "mission_outcome_verified":False,
        "status":"EFFECT_LOCAL_VERIFIED_MISSION_OUTCOME_UNVERIFIED" if local_effect_ok else "HOLD_EFFECT",
    }
    out["digest"]=digest(out)
    return out

def verify_peer_quorum(peer_receipts:Sequence[Mapping[str,object]], quorum:int=2)->dict:
    passes=[
        r for r in peer_receipts
        if r.get("status")=="INDEPENDENT_INTEGRITY_PASS"
        and r.get("receipt_digest_match") is True
        and r.get("artifact_hash_match") is True
        and r.get("boundary_ok") is True
    ]
    unique=sorted({str(r.get("verifier_node")) for r in passes if r.get("verifier_node")})
    ok=len(unique)>=quorum
    out={
        "schema":SCHEMA,
        "kind":"PEER_QUORUM",
        "quorum":quorum,
        "verified_nodes":unique,
        "verified_count":len(unique),
        "status":"INTEGRITY_QUORUM_VERIFIED" if ok else "HOLD_QUORUM",
        "mission_outcome_verified":False,
    }
    out["digest"]=digest(out)
    return out

def verify_external_outcome(local_effect:Mapping[str,object], external_evidence:Sequence[Mapping[str,object]])->dict:
    admissible=[
        e for e in external_evidence
        if e.get("independent") is True
        and e.get("fresh") is True
        and e.get("outcome_observed") is True
    ]
    ok=bool(local_effect.get("local_effect_verified")) and bool(admissible)
    out={
        "schema":SCHEMA,
        "kind":"MISSION_OUTCOME",
        "local_effect_verified":bool(local_effect.get("local_effect_verified")),
        "external_evidence_count":len(admissible),
        "mission_outcome_verified":ok,
        "status":"MISSION_OUTCOME_VERIFIED" if ok else "HOLD_EXTERNAL_OUTCOME_EVIDENCE",
    }
    out["digest"]=digest(out)
    return out
