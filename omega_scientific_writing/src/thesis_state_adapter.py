from __future__ import annotations


def to_scientific_ir(thesis_state: dict) -> dict:
    """Project a conservative ThesisState into ScientificIR without changing claim status."""
    project = dict(thesis_state.get("project", {}))
    claims = [dict(c) for c in thesis_state.get("claims", [])]
    evidence = []
    for item in thesis_state.get("evidence", []):
        e = dict(item)
        # R4 snapshot records are provenance objects, not primary scientific literature.
        if e.get("kind") == "literature":
            e["kind"] = "other"
        evidence.append(e)

    return {
        "project": project,
        "claims": claims,
        "evidence": evidence,
        "equations": [],
        "figures": [],
        "citations": [],
        "results": [],
        "thesis_state_metadata": {
            "parent_anchor": thesis_state.get("parent_anchor"),
            "frozen_head": thesis_state.get("frozen_head"),
            "epistemic_status": thesis_state.get("epistemic_status"),
            "supersessions": thesis_state.get("supersessions", []),
            "residuals": thesis_state.get("residuals", []),
        },
    }
