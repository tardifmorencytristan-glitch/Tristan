from __future__ import annotations

import json
import sys
from pathlib import Path


def _ids(items):
    return {x.get("id") for x in items if isinstance(x, dict) and x.get("id")}


def lint(doc: dict) -> list[dict]:
    findings: list[dict] = []
    claims = doc.get("claims", [])
    evidence = doc.get("evidence", [])
    equations = doc.get("equations", [])
    figures = doc.get("figures", [])
    citations = doc.get("citations", [])
    results = doc.get("results", [])

    evid_ids = _ids(evidence)
    claim_ids = _ids(claims)
    cite_ids = _ids(citations)

    for c in claims:
        cid = c.get("id", "<unknown>")
        linked = c.get("evidence_ids", [])
        missing = [x for x in linked if x not in evid_ids]
        if missing:
            findings.append({"severity": "ERROR", "code": "CLAIM_MISSING_EVIDENCE", "object": cid, "detail": missing})
        if not linked and c.get("status") not in {"IDEA", "HYPOTHESIS", "UNKNOWN"}:
            findings.append({"severity": "ERROR", "code": "SUPPORTED_STATUS_WITHOUT_EVIDENCE", "object": cid})
        for ref in c.get("citation_ids", []):
            if ref not in cite_ids:
                findings.append({"severity": "ERROR", "code": "CLAIM_MISSING_CITATION_OBJECT", "object": cid, "detail": ref})
        if not c.get("scope"):
            findings.append({"severity": "ERROR", "code": "CLAIM_SCOPE_MISSING", "object": cid})
        if not c.get("uncertainty"):
            findings.append({"severity": "ERROR", "code": "CLAIM_UNCERTAINTY_MISSING", "object": cid})

    seen_symbol_meanings: dict[str, set[str]] = {}
    for eq in equations:
        for symbol in eq.get("symbols", []):
            s = symbol.get("symbol")
            meaning = symbol.get("meaning")
            if not s or not meaning:
                findings.append({"severity": "ERROR", "code": "SYMBOL_DEFINITION_INCOMPLETE", "object": eq.get("id", "<unknown>")})
                continue
            seen_symbol_meanings.setdefault(s, set()).add(meaning)
            if not symbol.get("dimension") and not symbol.get("unit"):
                findings.append({"severity": "WARN", "code": "SYMBOL_NO_DIMENSION_OR_UNIT", "object": eq.get("id"), "detail": s})
    for symbol, meanings in seen_symbol_meanings.items():
        if len(meanings) > 1:
            findings.append({"severity": "WARN", "code": "SYMBOL_COLLISION", "object": symbol, "detail": sorted(meanings)})

    for fig in figures:
        fid = fig.get("id", "<unknown>")
        missing_claims = [x for x in fig.get("claim_ids", []) if x not in claim_ids]
        if missing_claims:
            findings.append({"severity": "ERROR", "code": "FIGURE_UNKNOWN_CLAIM", "object": fid, "detail": missing_claims})
        if not fig.get("script"):
            findings.append({"severity": "WARN", "code": "FIGURE_NO_GENERATION_SCRIPT", "object": fid})
        if not fig.get("uncertainty_declared", False):
            findings.append({"severity": "WARN", "code": "FIGURE_UNCERTAINTY_NOT_DECLARED", "object": fid})

    for r in results:
        rid = r.get("id", "<unknown>")
        missing = [x for x in r.get("evidence_ids", []) if x not in evid_ids]
        if missing:
            findings.append({"severity": "ERROR", "code": "RESULT_MISSING_EVIDENCE", "object": rid, "detail": missing})

    return findings


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: scientific_lint.py <scientific_ir.json>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    doc = json.loads(path.read_text(encoding="utf-8"))
    findings = lint(doc)
    print(json.dumps({"findings": findings}, indent=2, ensure_ascii=False))
    return 1 if any(x["severity"] == "ERROR" for x in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
