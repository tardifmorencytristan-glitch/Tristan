from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

from .contradiction_court import audit_contradictions
from .methodology_court import audit_method
from .proof_obligations import evaluate_obligations
from .report_ir import ReportGraphIR, report_graph_from_dict, validate_report_graph
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
    findings.extend(audit_traceability(graph, claims))
    findings.extend(audit_contradictions(graph))
    findings.extend(audit_terminology(doc.get("terminology_usages", []), graph.concepts))

    residuals = derive_residuals(graph, findings)
    blockers = blocking_residuals(residuals)
    hard = any(f.get("severity") in {"ERROR", "HOLD"} for f in findings)
    verdict = "HOLD" if hard or blockers else "PASS"

    return {
        "verdict": verdict,
        "scientific_status": "NOT_ESTABLISHED_BY_REPORT_COURT",
        "findings": sorted(findings, key=_finding_key),
        "residuals": [asdict(r) for r in residuals],
        "blocking_residuals": [asdict(r) for r in blockers],
        "traceability": build_traceability_index(graph, claims),
        "invariants": list(INVARIANTS),
    }


def load_report_packet(path: str | Path) -> tuple[dict, ReportGraphIR]:
    packet = json.loads(Path(path).read_text(encoding="utf-8"))
    if set(packet) != {"scientific_ir", "report_graph"}:
        raise ValueError("report packet requires exactly scientific_ir and report_graph")
    if not isinstance(packet["scientific_ir"], dict) or not isinstance(packet["report_graph"], dict):
        raise ValueError("report packet sections must be objects")
    return packet["scientific_ir"], report_graph_from_dict(packet["report_graph"])


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("usage: python -m omega_scientific_writing.src.report_court <packet.json>", file=sys.stderr)
        return 2
    doc, graph = load_report_packet(args[0])
    result = evaluate_report(doc, graph)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
