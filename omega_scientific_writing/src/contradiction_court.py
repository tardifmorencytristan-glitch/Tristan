from __future__ import annotations

from .report_ir import ReportGraphIR


def audit_contradictions(graph: ReportGraphIR) -> list[dict]:
    findings: list[dict] = []
    for contradiction in graph.contradictions:
        state = contradiction.adjudication_state
        cid = contradiction.meta.id
        if state == "RESOLVED":
            continue
        if state == "UNRESOLVED":
            findings.append({"severity": "HOLD", "code": "CONTRADICTION_UNRESOLVED", "object": cid})
        elif state == "CONTEXTUAL":
            findings.append({"severity": "WARN", "code": "CONTRADICTION_CONTEXTUAL", "object": cid})
        elif state == "TEMPORAL":
            findings.append({"severity": "WARN", "code": "CONTRADICTION_TEMPORAL", "object": cid})
        elif state == "TERMINOLOGICAL":
            findings.append({"severity": "HOLD", "code": "CONTRADICTION_TERMINOLOGICAL", "object": cid})
        else:
            findings.append({"severity": "HOLD", "code": "CONTRADICTION_STATE_UNKNOWN", "object": cid, "detail": state})
    return findings
