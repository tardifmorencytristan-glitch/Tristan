from __future__ import annotations

from dataclasses import dataclass


CLAIM_TYPES = {
    "ENGINEERING",
    "NUMERICAL",
    "EMPIRICAL",
    "PHYSICAL",
    "MATHEMATICAL",
    "METHODOLOGICAL",
    "LITERATURE",
    "COMPLIANCE",
}

EVIDENCE_KINDS = {
    "software_test",
    "simulation",
    "measurement",
    "experiment",
    "dataset",
    "formal_proof",
    "derivation",
    "literature",
    "institutional_rule",
    "other",
}

ALLOWED_EVIDENCE = {
    "ENGINEERING": {"software_test", "experiment", "dataset", "other"},
    "NUMERICAL": {"simulation", "software_test", "dataset", "derivation", "other"},
    "EMPIRICAL": {"measurement", "experiment", "dataset", "literature", "other"},
    "PHYSICAL": {"measurement", "experiment", "simulation", "derivation", "literature", "other"},
    "MATHEMATICAL": {"formal_proof", "derivation", "literature", "other"},
    "METHODOLOGICAL": {"experiment", "dataset", "software_test", "literature", "other"},
    "LITERATURE": {"literature", "other"},
    "COMPLIANCE": {"institutional_rule", "other"},
}


@dataclass(frozen=True)
class TypeFinding:
    severity: str
    code: str
    object: str
    detail: str = ""


def validate_claim_types(doc: dict) -> list[dict]:
    findings: list[TypeFinding] = []
    evidence = {e.get("id"): e for e in doc.get("evidence", []) if e.get("id")}

    for claim in doc.get("claims", []):
        cid = claim.get("id", "<unknown>")
        ctype = claim.get("claim_type")
        if ctype is None:
            findings.append(TypeFinding("WARN", "CLAIM_TYPE_MISSING", cid))
            continue
        if ctype not in CLAIM_TYPES:
            findings.append(TypeFinding("ERROR", "CLAIM_TYPE_UNKNOWN", cid, str(ctype)))
            continue

        for eid in claim.get("evidence_ids", []):
            ev = evidence.get(eid)
            if not ev:
                continue
            kind = ev.get("kind")
            if kind not in EVIDENCE_KINDS:
                findings.append(TypeFinding("ERROR", "EVIDENCE_KIND_UNKNOWN", eid, str(kind)))
                continue
            if kind not in ALLOWED_EVIDENCE[ctype]:
                findings.append(TypeFinding(
                    "ERROR",
                    "EVIDENCE_TYPE_MISMATCH",
                    cid,
                    f"{ctype} claim linked to {kind} evidence {eid}",
                ))

        if ctype == "PHYSICAL":
            kinds = {evidence[eid].get("kind") for eid in claim.get("evidence_ids", []) if eid in evidence}
            if kinds and kinds <= {"software_test"}:
                findings.append(TypeFinding(
                    "ERROR", "ENGINEERING_TO_PHYSICAL_PROMOTION", cid,
                    "software tests alone cannot support a physical claim",
                ))

    return [f.__dict__ for f in findings]
