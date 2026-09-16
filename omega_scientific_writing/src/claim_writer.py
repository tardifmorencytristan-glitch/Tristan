from __future__ import annotations

STRENGTH = {"PROPOSED":0,"SIMULATED":1,"OBSERVED":2,"MEASURED":3,"REPLICATED":4,"INDEPENDENTLY_VERIFIED":5,"FORMALLY_PROVEN":5}


def max_language(status: str) -> str:
    return {
        0:"proposed",
        1:"suggested by simulation",
        2:"observed in the evaluated setting",
        3:"measured under the stated protocol",
        4:"replicated under the stated replication scope",
        5:"verified within the stated evidence and assumptions",
    }.get(STRENGTH.get(status,-1), "not established")


def bounded_claim(claim: dict) -> dict:
    status = claim.get("status","PROPOSED")
    scope = claim.get("scope") or "the stated scope"
    statement = (claim.get("statement") or "").strip()
    if not statement:
        raise ValueError("claim statement required")
    return {
        "claim_id":claim.get("id"),
        "status":status,
        "scope":scope,
        "language_ceiling":max_language(status),
        "text":f"Within {scope}, {statement.rstrip('.')} is {max_language(status)}.",
        "no_globalization": status not in {"INDEPENDENTLY_VERIFIED","FORMALLY_PROVEN"},
    }
