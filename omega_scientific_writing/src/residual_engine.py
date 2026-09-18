from __future__ import annotations

from .methodology_court import audit_method
from .report_ir import ReportGraphIR, ReportMeta, ResidualIR

SEVERITY = {
    "MISSING_EVIDENCE": "CRITICAL",
    "MISSING_SOURCE": "HIGH",
    "MISSING_UNIT": "HIGH",
    "MISSING_UNCERTAINTY": "HIGH",
    "MISSING_VALIDATION": "CRITICAL",
    "MISSING_DEFINITION": "MEDIUM",
    "UNRESOLVED_CONTRADICTION": "CRITICAL",
    "UNANSWERED_OBJECTIVE": "CRITICAL",
    "UNSUPPORTED_CONCLUSION": "CRITICAL",
    "ORPHAN_FIGURE": "HIGH",
    "ORPHAN_TABLE": "HIGH",
    "DUPLICATE_CONCEPT": "HIGH",
    "AMBIGUOUS_TERMINOLOGY": "CRITICAL",
    "NON_REPRODUCIBLE_METHOD": "CRITICAL",
    "UNRESOLVED_CITATION_SUPPORT": "CRITICAL",
    "RENDER_READBACK_FAILURE": "CRITICAL",
}

_FINDING_TO_RESIDUAL = {
    "METHOD_VALIDATION_MISSING": "NON_REPRODUCIBLE_METHOD",
    "CONTRADICTION_UNRESOLVED": "UNRESOLVED_CONTRADICTION",
    "OBJECTIVE_UNANSWERED": "UNANSWERED_OBJECTIVE",
    "CONCLUSION_UNSUPPORTED": "UNSUPPORTED_CONCLUSION",
    "TERM_AMBIGUOUS": "AMBIGUOUS_TERMINOLOGY",
    "RESULT_WITHOUT_EVIDENCE": "MISSING_EVIDENCE",
    "CITATION_DOES_NOT_ENTAIL": "UNRESOLVED_CITATION_SUPPORT",
}


def _residual(kind: str, target: str, description: str) -> ResidualIR:
    return ResidualIR(
        meta=ReportMeta(f"RES:{kind}:{target}", status="RESIDUAL"),
        residual_type=kind,
        target_id=target,
        severity=SEVERITY[kind],
        description=description,
    )


def derive_residuals(graph: ReportGraphIR, external_findings=()) -> tuple[ResidualIR, ...]:
    collected: dict[str, ResidualIR] = {r.meta.id: r for r in graph.residuals}
    if graph.objectives and not graph.results and not graph.conclusions:
        for objective in graph.objectives:
            item = _residual("UNANSWERED_OBJECTIVE", objective.meta.id, "Objective has no declared result or conclusion")
            collected[item.meta.id] = item
    for method in graph.methods:
        codes = {finding["code"] for finding in audit_method(method)}
        if "METHOD_VALIDATION_MISSING" in codes:
            item = _residual("NON_REPRODUCIBLE_METHOD", method.meta.id, "Method has no declared validation method")
            collected[item.meta.id] = item
    for finding in external_findings:
        kind = _FINDING_TO_RESIDUAL.get(finding.get("code"))
        if not kind:
            continue
        target = str(finding.get("object", "<unknown>"))
        item = _residual(kind, target, str(finding.get("detail") or finding.get("code")))
        collected[item.meta.id] = item
    return tuple(collected[key] for key in sorted(collected))


def blocking_residuals(residuals: tuple[ResidualIR, ...]) -> tuple[ResidualIR, ...]:
    return tuple(r for r in residuals if r.severity == "CRITICAL" and r.resolution_state != "RESOLVED")
