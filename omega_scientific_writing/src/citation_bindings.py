from __future__ import annotations

VALID_SUPPORT = {"DIRECT","PARTIAL","BACKGROUND","METHOD","PRIOR_ART","CONTRADICTOR","BASELINE","NOT_ENTAILING"}


def validate_bindings(claims: list[dict], sources: list[dict], bindings: list[dict]) -> list[dict]:
    claim_ids = {c.get("id") for c in claims}
    source_ids = {s.get("id") for s in sources}
    findings = []
    used = set()
    for i, b in enumerate(bindings):
        obj = b.get("id") or f"binding-{i}"
        if b.get("claim_id") not in claim_ids:
            findings.append({"severity":"ERROR","code":"CITATION_UNKNOWN_CLAIM","object":obj})
        if b.get("source_id") not in source_ids:
            findings.append({"severity":"ERROR","code":"CITATION_UNKNOWN_SOURCE","object":obj})
        st = b.get("support_type")
        if st not in VALID_SUPPORT:
            findings.append({"severity":"ERROR","code":"CITATION_SUPPORT_TYPE_UNKNOWN","object":obj,"detail":str(st)})
        if st == "NOT_ENTAILING":
            findings.append({"severity":"ERROR","code":"CITATION_DOES_NOT_ENTAIL","object":obj})
        if b.get("source_id"):
            used.add(b["source_id"])
    for sid in source_ids - used:
        findings.append({"severity":"WARN","code":"BIBLIOGRAPHY_ENTRY_UNUSED","object":sid})
    return findings
