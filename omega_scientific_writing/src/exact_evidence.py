from __future__ import annotations


def evidence_from_exact_commit(record: dict) -> dict:
    required = ["object_id", "commit_sha", "repository", "commit_message", "observed_boundaries"]
    missing = [k for k in required if not record.get(k)]
    if missing:
        raise ValueError(f"missing exact-evidence fields: {missing}")

    return {
        "id": f"EXACT-{record['object_id']}",
        "kind": "software_test" if record.get("evidence_class") == "software" else "other",
        "provenance": f"github:{record['repository']}@{record['commit_sha']}",
        "reproducibility": record.get("reproducibility", "unknown"),
        "exact_commit_read": True,
        "commit_message": record["commit_message"],
        "observed_boundaries": list(record["observed_boundaries"]),
        "receipt_paths": list(record.get("receipt_paths", [])),
    }


def may_promote_snapshot_evidence(record: dict) -> bool:
    return bool(record.get("exact_commit_read") and record.get("independent_receipt_read") and record.get("promotion_authorized"))
