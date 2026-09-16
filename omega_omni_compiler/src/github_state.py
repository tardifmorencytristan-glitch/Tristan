from __future__ import annotations

from typing import Any

from .domain_ir import GitIR


def gitir_from_branch_payload(repository: str, payload: dict[str, Any], provenance: str) -> GitIR:
    name = payload.get("name")
    commit = payload.get("commit") or {}
    sha = commit.get("sha")
    if not name or not sha:
        raise ValueError("branch payload requires name and commit.sha")
    return GitIR(
        id=f"git:{repository}:{name}:{sha}",
        repository=repository,
        branch=name,
        head_sha=sha,
        commits=[sha],
        checks=[],
        provenance=provenance,
    )


def attach_check_runs(git: GitIR, check_payload: dict[str, Any]) -> GitIR:
    runs = check_payload.get("check_runs", [])
    normalized = []
    for run in runs:
        head = run.get("head_sha")
        if head and head != git.head_sha:
            continue
        normalized.append({
            "name": run.get("name"),
            "status": run.get("status"),
            "conclusion": run.get("conclusion"),
            "head_sha": head,
        })
    git.checks = normalized
    return git


def exact_head_checks_pass(git: GitIR) -> bool:
    if not git.checks:
        return False
    return all(
        c.get("head_sha") == git.head_sha
        and c.get("status") == "completed"
        and c.get("conclusion") == "success"
        for c in git.checks
    )
