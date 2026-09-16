from __future__ import annotations

from .universal_ir import UniversalIRObject


def scientific_ir_to_universal(doc: dict) -> UniversalIRObject:
    project = doc.get("project", {})
    claims = doc.get("claims", [])
    return UniversalIRObject(
        id=f"SCI-{project.get('id', 'unknown')}",
        type="SCIENTIFIC",
        status="PROVISIONAL",
        provenance=[f"scientific-ir:{project.get('id', 'unknown')}"] ,
        version=project.get("version"),
        scope=project.get("title", ""),
        assumptions=[],
        uncertainty="ScientificIR bridge preserves structure but does not independently validate truth.",
        evidence_ids=[e.get("id") for e in doc.get("evidence", []) if e.get("id")],
        payload={
            "project": project,
            "claims": claims,
            "evidence": doc.get("evidence", []),
            "equations": doc.get("equations", []),
            "figures": doc.get("figures", []),
            "citations": doc.get("citations", []),
            "results": doc.get("results", []),
        },
    )


def universal_to_scientific_ir(obj: UniversalIRObject) -> dict:
    if obj.type != "SCIENTIFIC":
        raise ValueError("UniversalIR object must be SCIENTIFIC")
    payload = obj.payload
    return {
        "project": payload.get("project", {}),
        "claims": payload.get("claims", []),
        "evidence": payload.get("evidence", []),
        "equations": payload.get("equations", []),
        "figures": payload.get("figures", []),
        "citations": payload.get("citations", []),
        "results": payload.get("results", []),
    }
