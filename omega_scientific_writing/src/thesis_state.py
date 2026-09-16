from __future__ import annotations

import json
from pathlib import Path


def compile_r4_manifest(manifest: dict) -> dict:
    source = manifest["source"]
    provenance = f"drive:{source['drive_file_id']}@{source['snapshot_time']}"

    claims = []
    evidence = []
    for item in manifest.get("crystallizations", []):
        cid = f"R4-{item['id']}"
        eid = f"EV-{item['id']}"
        evidence.append({
            "id": eid,
            "kind": "literature",
            "provenance": provenance,
            "reproducibility": "unknown",
            "reported_commit": item.get("commit"),
            "reported_status": item.get("status"),
            "evidence_boundary": "Snapshot evidence only; underlying tests/receipts are not independently re-read by this compiler.",
        })
        claims.append({
            "id": cid,
            "statement": f"R4 reports {item['title']} with status {item.get('status', 'UNKNOWN')} at commit {item.get('commit', 'UNKNOWN')}.",
            "status": "OBSERVATION",
            "evidence_ids": [eid],
            "citation_ids": [],
            "assumptions": ["The R4 snapshot text is parsed faithfully."],
            "scope": "R4 Living Delta snapshot only",
            "uncertainty": "Underlying engineering/scientific evidence has not been independently revalidated in this compilation step.",
            "falsifier": "A readback of the cited commit/receipt contradicts the R4 snapshot record.",
            "source_object": item["id"],
        })

    residuals = [
        {"id": f"RES-{i+1}", "statement": text, "status": "OPEN"}
        for i, text in enumerate(manifest.get("open_frontiers", []))
    ]

    return {
        "schema_version": "thesis-state-r2",
        "project": {
            "id": manifest["benchmark_id"],
            "title": source["title"],
            "document_type": "report",
            "language": "fr",
        },
        "parent_anchor": source.get("r3_anchor"),
        "frozen_head": source.get("r4_frozen_head"),
        "epistemic_status": source.get("epistemic_status"),
        "invariants": manifest.get("invariants", []),
        "claims": claims,
        "evidence": evidence,
        "supersessions": [],
        "residuals": residuals,
        "requested_capabilities": manifest.get("r5_requested_capabilities", []),
    }


def load_and_compile(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return compile_r4_manifest(data)
