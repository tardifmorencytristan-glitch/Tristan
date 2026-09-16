from __future__ import annotations

from .contradiction_court import audit_contradictions
from .methodology_court import audit_method
from .proof_obligations import evaluate_obligations
from .report_ir import ReportGraphIR, report_graph_to_dict, validate_report_graph
from .report_traceability import audit_traceability, build_traceability_index
from .residual_engine import blocking_residuals, derive_residuals
from .scientific_lint import lint
from .scientific_types import validate_claim_types
from .terminology_court import audit_terminology

INVARIANTS = [
    "Generated != Verified",
    "CompilationPASS != ScientificPASS",
    "Simulation != Measurement",
    "Formatting != Evidence",
    "Capability != Authority",
]


def _finding_key(finding: dict) -> tuple[str, str, str, str]:
    return (
        str(finding.get("severity", "")),
        str(finding.get("code", "")),
        str(finding.get("object", "")),
        repr(finding.get("detail")),
    )


def evaluate_report(doc: dict, graph: ReportGraphIR) -> dict:
    claims = doc.get("claims", [])
    findings: list[dict] = []
    findings.extend(validate_report_graph(graph))
    findings.extend(lint(doc))
    findings.extend(validate_claim_types(doc))
    findings.extend(evaluate_obligations(doc))
    for method in graph.methods:
        findings.extend(audit_method(method))
    traceability_findings = audit_traceability(graph, claims)
    findings.extend(traceability_findings)
    findings.extend(audit_contradictions(graph))
    findings.extend(audit_terminology(doc.get("terminology_usages", []), graph.concepts))

    residuals = derive_residuals(graph, findings)
    blockers = blocking_residuals(residuals)
    hard = any(f.get("severity") in {"ERROR", "HOLD"} for f in findings)
    verdict = "HOLD" if hard or blockers else "PASS"

    traceability = build_traceability_index(graph, claims)
    return {
        "verdict": verdict,
        "scientific_status": "NOT_ESTABLISHED_BY_REPORT_COURT",
        "findings": sorted(findings, key=_finding_key),
        "residuals": [report_graph_to_dict(ReportGraphIR(project_id=graph.project_id, residuals=(r,)))["residuals"][0] for r in residuals],
        "blocking_residuals": [report_graph_to_dict(ReportGraphIR(project_id=graph.project_id, residuals=(r,)))["residuals"][0] for r in blockers],
        "traceability": traceability,
        "invariants": list(INVARIANTS),
    }
