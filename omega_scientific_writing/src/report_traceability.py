from __future__ import annotations

from .report_ir import ReportGraphIR


def build_traceability_index(graph: ReportGraphIR, claims: list[dict]) -> dict:
    upstream: dict[str, set[str]] = {}
    downstream: dict[str, set[str]] = {}
    known: set[str] = set()

    def register(oid: str) -> None:
        if oid:
            known.add(oid)
            upstream.setdefault(oid, set())
            downstream.setdefault(oid, set())

    def edge(source: str, target: str) -> None:
        if not source or not target:
            return
        upstream.setdefault(target, set()).add(source)
        downstream.setdefault(source, set()).add(target)

    for collection in (
        graph.objectives, graph.requirements, graph.constraints, graph.assumptions,
        graph.concepts, graph.methods, graph.results, graph.figures,
        graph.interpretations, graph.conclusions, graph.residuals, graph.contradictions,
    ):
        for obj in collection:
            register(obj.meta.id)

    for claim in claims:
        cid = claim.get("id")
        if not cid:
            continue
        register(cid)
        for eid in claim.get("evidence_ids", []):
            register(eid)
            edge(eid, cid)

    for result in graph.results:
        for eid in result.evidence_ids:
            register(eid)
            edge(eid, result.meta.id)
        for oid in result.objective_ids:
            edge(oid, result.meta.id)

    for interpretation in graph.interpretations:
        for rid in interpretation.result_ids:
            edge(rid, interpretation.meta.id)
        for cid in interpretation.claim_ids:
            edge(cid, interpretation.meta.id)

    for conclusion in graph.conclusions:
        for rid in conclusion.result_ids:
            edge(rid, conclusion.meta.id)
        for cid in conclusion.claim_ids:
            edge(cid, conclusion.meta.id)
        for req in conclusion.requirement_ids:
            edge(req, conclusion.meta.id)
        for oid in conclusion.objective_ids:
            edge(oid, conclusion.meta.id)

    all_ids = set(known) | set(upstream) | set(downstream)
    return {
        "upstream": {key: tuple(sorted(upstream.get(key, ()))) for key in sorted(all_ids)},
        "downstream": {key: tuple(sorted(downstream.get(key, ()))) for key in sorted(all_ids)},
        "known_ids": tuple(sorted(known)),
    }


def proof_cone(target_id: str, index: dict) -> dict:
    known = set(index.get("known_ids", ()))
    upstream = index.get("upstream", {})
    reachable: set[str] = set()
    missing: set[str] = set()
    stack = list(upstream.get(target_id, ()))
    while stack:
        current = stack.pop()
        if current in reachable:
            continue
        reachable.add(current)
        if current not in known:
            missing.add(current)
            continue
        stack.extend(upstream.get(current, ()))
    return {
        "target_id": target_id,
        "reachable_ids": sorted(reachable),
        "missing_ids": sorted(missing),
    }


def audit_traceability(graph: ReportGraphIR, claims: list[dict]) -> list[dict]:
    findings: list[dict] = []
    index = build_traceability_index(graph, claims)
    known = set(index["known_ids"])

    for target, sources in index["upstream"].items():
        for source in sources:
            if source not in known:
                findings.append({"severity": "ERROR", "code": "TRACE_DANGLING_REFERENCE", "object": target, "detail": source})

    for result in graph.results:
        if not result.evidence_ids:
            findings.append({"severity": "HOLD", "code": "RESULT_WITHOUT_EVIDENCE", "object": result.meta.id})

    for conclusion in graph.conclusions:
        if not conclusion.claim_ids and not conclusion.result_ids:
            findings.append({"severity": "HOLD", "code": "CONCLUSION_UNSUPPORTED", "object": conclusion.meta.id})

    answered = {
        oid
        for result in graph.results for oid in result.objective_ids
    } | {
        oid
        for conclusion in graph.conclusions for oid in conclusion.objective_ids
    }
    for objective in graph.objectives:
        if objective.meta.id not in answered:
            findings.append({"severity": "HOLD", "code": "OBJECTIVE_UNANSWERED", "object": objective.meta.id})
    return findings
