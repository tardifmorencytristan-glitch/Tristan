from __future__ import annotations


def _by_id(items: list[dict]) -> dict[str, dict]:
    return {x.get("id"): x for x in items if isinstance(x, dict) and x.get("id")}


def diff_states(before: dict, after: dict) -> dict:
    b = _by_id(before.get("claims", []))
    a = _by_id(after.get("claims", []))

    added = sorted(set(a) - set(b))
    removed = sorted(set(b) - set(a))
    status_changes = []
    evidence_changes = []
    scope_changes = []

    for cid in sorted(set(a) & set(b)):
        if b[cid].get("status") != a[cid].get("status"):
            status_changes.append({"id": cid, "before": b[cid].get("status"), "after": a[cid].get("status")})
        if set(b[cid].get("evidence_ids", [])) != set(a[cid].get("evidence_ids", [])):
            evidence_changes.append({
                "id": cid,
                "before": sorted(b[cid].get("evidence_ids", [])),
                "after": sorted(a[cid].get("evidence_ids", [])),
            })
        if b[cid].get("scope") != a[cid].get("scope"):
            scope_changes.append({"id": cid, "before": b[cid].get("scope"), "after": a[cid].get("scope")})

    return {
        "claims_added": added,
        "claims_removed": removed,
        "status_changes": status_changes,
        "evidence_changes": evidence_changes,
        "scope_changes": scope_changes,
    }


def promotion_events(diff: dict) -> list[dict]:
    order = {
        "IDEA": 0,
        "HYPOTHESIS": 1,
        "DERIVATION": 2,
        "SIMULATION": 3,
        "OBSERVATION": 4,
        "MEASUREMENT": 5,
        "REPLICATION": 6,
        "INDEPENDENT_VERIFICATION": 7,
        "FORMAL_PROOF": 7,
        "UNKNOWN": -1,
    }
    return [
        item for item in diff.get("status_changes", [])
        if order.get(item["after"], -1) > order.get(item["before"], -1)
    ]
