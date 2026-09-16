from __future__ import annotations

ALLOWED_ROLES = {"CONTEXT","PROBLEM","GAP","QUESTION","HYPOTHESIS","METHOD","EVIDENCE","RESULT","INTERPRETATION","ALTERNATIVE","LIMITATION","RESIDUAL"}


def build_argument_graph(nodes: list[dict], edges: list[dict]) -> dict:
    by_id = {n["id"]: dict(n) for n in nodes if n.get("id")}
    findings = []
    for nid, node in by_id.items():
        role = node.get("role")
        if role not in ALLOWED_ROLES:
            findings.append({"severity":"ERROR","code":"ARGUMENT_ROLE_UNKNOWN","object":nid,"detail":str(role)})
    clean_edges = []
    for e in edges:
        s, t = e.get("source"), e.get("target")
        if s not in by_id or t not in by_id:
            findings.append({"severity":"ERROR","code":"ARGUMENT_EDGE_DANGLING","object":f"{s}->{t}"})
        else:
            clean_edges.append({"source":s,"target":t,"relation":e.get("relation","SUPPORTS")})
    incoming = {k:0 for k in by_id}
    for e in clean_edges:
        incoming[e["target"]] += 1
    for nid, node in by_id.items():
        if node.get("role") in {"RESULT","INTERPRETATION"} and incoming[nid] == 0:
            findings.append({"severity":"WARN","code":"ARGUMENT_UNSUPPORTED","object":nid})
    return {"nodes":list(by_id.values()),"edges":clean_edges,"findings":findings}
