from __future__ import annotations

REVIEWERS = (
    "EPISTEMIC","DOMAIN","MATHEMATICAL","STATISTICS","CITATION","PRIOR_ART",
    "REPRODUCIBILITY","ADVERSARIAL","CLARITY","STYLE","COMPRESSION","ACCESSIBILITY","AUTHORITY"
)


def review(doc: dict) -> dict:
    findings = []
    for claim in doc.get("claims", []):
        cid = claim.get("id","<unknown>")
        status = claim.get("status","PROPOSED")
        text = (claim.get("statement") or "").lower()
        if any(w in text for w in ("universal","always","optimal","first","novel")) and not claim.get("prior_art_closed"):
            findings.append({"reviewer":"PRIOR_ART","severity":"HOLD","code":"STRONG_LANGUAGE_PRIOR_ART_OPEN","object":cid})
        if any(w in text for w in ("causes","caused","leads to","due to")) and not claim.get("causal_identification"):
            findings.append({"reviewer":"EPISTEMIC","severity":"HOLD","code":"CAUSAL_LANGUAGE_UNSUPPORTED","object":cid})
        if status in {"MEASURED","REPLICATED","INDEPENDENTLY_VERIFIED"} and not claim.get("evidence_ids"):
            findings.append({"reviewer":"EPISTEMIC","severity":"HOLD","code":"STATUS_WITHOUT_EVIDENCE","object":cid})
    verdict = "PASS" if not findings else "HOLD"
    return {"verdict":verdict,"reviewers":list(REVIEWERS),"findings":findings}
