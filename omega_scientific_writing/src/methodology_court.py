from __future__ import annotations

from .report_ir import MethodIR


def audit_method(method: MethodIR) -> list[dict]:
    findings: list[dict] = []
    mid = method.meta.id or "<unknown>"
    if not method.objective.strip():
        findings.append({"severity": "ERROR", "code": "METHOD_OBJECTIVE_MISSING", "object": mid})
    if not method.input_ids:
        findings.append({"severity": "HOLD", "code": "METHOD_INPUTS_MISSING", "object": mid})
    if not method.steps:
        findings.append({"severity": "ERROR", "code": "METHOD_STEPS_MISSING", "object": mid})
    if not method.output_ids:
        findings.append({"severity": "HOLD", "code": "METHOD_OUTPUTS_MISSING", "object": mid})
    if not method.validation_methods:
        findings.append({"severity": "HOLD", "code": "METHOD_VALIDATION_MISSING", "object": mid})
    return findings
