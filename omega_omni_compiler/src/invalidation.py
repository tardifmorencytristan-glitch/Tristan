from __future__ import annotations

from dataclasses import dataclass, field

from .artifact_graph import ArtifactGraph


@dataclass
class InvalidationReceipt:
    root_id: str
    invalidated_ids: list[str] = field(default_factory=list)
    reason: str = ""
    status: str = "INVALIDATED"


def affected_closure(graph: ArtifactGraph, changed_artifact_id: str) -> list[str]:
    return [changed_artifact_id] + graph.descendants(changed_artifact_id)


def invalidate(graph: ArtifactGraph, changed_artifact_id: str, reason: str) -> InvalidationReceipt:
    if changed_artifact_id not in graph.nodes:
        raise KeyError(changed_artifact_id)
    return InvalidationReceipt(
        root_id=changed_artifact_id,
        invalidated_ids=affected_closure(graph, changed_artifact_id),
        reason=reason,
    )
