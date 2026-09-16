from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

REPORT_STATUSES = {
    "PROVISIONAL", "OBSERVED_CANDIDATE", "SUPPORTED", "MEASURED",
    "VERIFIED_ENGINEERING", "HOLD", "CONTRADICTED", "RESIDUAL",
    "REJECTED", "SUPERSEDED", "CRYSTALLIZED",
}


@dataclass(frozen=True)
class ReportMeta:
    id: str
    status: str = "PROVISIONAL"
    scope: str = ""
    provenance_ids: tuple[str, ...] = ()
    transform_id: str = ""


@dataclass(frozen=True)
class ObjectiveIR:
    meta: ReportMeta
    statement: str


@dataclass(frozen=True)
class RequirementIR:
    meta: ReportMeta
    statement: str
    success_criterion: str


@dataclass(frozen=True)
class ConstraintIR:
    meta: ReportMeta
    statement: str


@dataclass(frozen=True)
class AssumptionIR:
    meta: ReportMeta
    statement: str
    justification: str = ""


@dataclass(frozen=True)
class ConceptTermIR:
    meta: ReportMeta
    canonical_terms: tuple[tuple[str, str], ...]
    aliases: tuple[str, ...] = ()
    ambiguous_terms: tuple[str, ...] = ()
    forbidden_substitutions: tuple[str, ...] = ()
    definition: str = ""
    source_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class MethodIR:
    meta: ReportMeta
    objective: str
    input_ids: tuple[str, ...] = ()
    assumption_ids: tuple[str, ...] = ()
    constraint_ids: tuple[str, ...] = ()
    steps: tuple[str, ...] = ()
    tool_ids: tuple[str, ...] = ()
    output_ids: tuple[str, ...] = ()
    validation_methods: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResultIR:
    meta: ReportMeta
    statement: str
    evidence_ids: tuple[str, ...] = ()
    quantity_ids: tuple[str, ...] = ()
    objective_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class FigureAxisIR:
    label: str
    unit: str = ""


@dataclass(frozen=True)
class FigureIR:
    meta: ReportMeta
    purpose: str
    source_ids: tuple[str, ...] = ()
    claim_ids: tuple[str, ...] = ()
    axes: tuple[FigureAxisIR, ...] = ()
    caption: str = ""
    orientation: str = ""
    uncertainty_declared: bool = False


@dataclass(frozen=True)
class InterpretationIR:
    meta: ReportMeta
    statement: str
    result_ids: tuple[str, ...] = ()
    claim_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConclusionIR:
    meta: ReportMeta
    statement: str
    claim_ids: tuple[str, ...] = ()
    result_ids: tuple[str, ...] = ()
    requirement_ids: tuple[str, ...] = ()
    objective_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResidualIR:
    meta: ReportMeta
    residual_type: str
    target_id: str
    severity: str
    description: str
    resolution_state: str = "OPEN"


@dataclass(frozen=True)
class ContradictionIR:
    meta: ReportMeta
    subject_ids: tuple[str, ...]
    conflict_type: str
    description: str
    adjudication_state: str = "UNRESOLVED"


@dataclass(frozen=True)
class ReportGraphIR:
    project_id: str
    objectives: tuple[ObjectiveIR, ...] = ()
    requirements: tuple[RequirementIR, ...] = ()
    constraints: tuple[ConstraintIR, ...] = ()
    assumptions: tuple[AssumptionIR, ...] = ()
    concepts: tuple[ConceptTermIR, ...] = ()
    methods: tuple[MethodIR, ...] = ()
    results: tuple[ResultIR, ...] = ()
    figures: tuple[FigureIR, ...] = ()
    interpretations: tuple[InterpretationIR, ...] = ()
    conclusions: tuple[ConclusionIR, ...] = ()
    residuals: tuple[ResidualIR, ...] = ()
    contradictions: tuple[ContradictionIR, ...] = ()


def _objects(graph: ReportGraphIR) -> tuple[Any, ...]:
    return (
        *graph.objectives, *graph.requirements, *graph.constraints,
        *graph.assumptions, *graph.concepts, *graph.methods, *graph.results,
        *graph.figures, *graph.interpretations, *graph.conclusions,
        *graph.residuals, *graph.contradictions,
    )


def validate_report_graph(graph: ReportGraphIR) -> list[dict]:
    findings: list[dict] = []
    if not graph.project_id.strip():
        findings.append({"severity": "ERROR", "code": "REPORT_PROJECT_ID_MISSING", "object": "<report>"})

    seen: set[str] = set()
    duplicates: set[str] = set()
    for obj in _objects(graph):
        oid = obj.meta.id
        if not oid.strip():
            findings.append({"severity": "ERROR", "code": "REPORT_OBJECT_ID_MISSING", "object": "<unknown>"})
        elif oid in seen:
            duplicates.add(oid)
        else:
            seen.add(oid)
        if obj.meta.status not in REPORT_STATUSES:
            findings.append({"severity": "ERROR", "code": "REPORT_STATUS_UNKNOWN", "object": oid or "<unknown>", "detail": obj.meta.status})

    for oid in sorted(duplicates):
        findings.append({"severity": "ERROR", "code": "REPORT_DUPLICATE_OBJECT_ID", "object": oid})
    return findings


def report_graph_to_dict(graph: ReportGraphIR) -> dict:
    return asdict(graph)
