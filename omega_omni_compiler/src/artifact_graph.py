from __future__ import annotations

from dataclasses import dataclass, field, asdict
from hashlib import sha256
import json
from typing import Any


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ArtifactIdentity:
    id: str
    artifact_type: str
    source: str
    version: str = ""
    content_hash: str = ""
    status: str = "PROVISIONAL"
    authority: str = ""

    def validate(self) -> list[str]:
        errors = []
        for name in ("id", "artifact_type", "source"):
            if not getattr(self, name):
                errors.append(f"ArtifactIdentity.{name} required")
        if self.content_hash and len(self.content_hash) != 64:
            errors.append("ArtifactIdentity.content_hash must be SHA-256 hex")
        return errors


@dataclass
class ArtifactNode:
    identity: ArtifactIdentity
    metadata: dict[str, Any] = field(default_factory=dict)
    parent_ids: list[str] = field(default_factory=list)
    receipt_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "identity": asdict(self.identity),
            "metadata": dict(self.metadata),
            "parent_ids": list(self.parent_ids),
            "receipt_ids": list(self.receipt_ids),
        }


class ArtifactGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, ArtifactNode] = {}
        self.children: dict[str, set[str]] = {}

    def add(self, node: ArtifactNode) -> None:
        errors = node.identity.validate()
        if errors:
            raise ValueError(errors)
        aid = node.identity.id
        if aid in self.nodes:
            raise ValueError(f"duplicate artifact id: {aid}")
        self.nodes[aid] = node
        self.children.setdefault(aid, set())
        for parent in node.parent_ids:
            self.children.setdefault(parent, set()).add(aid)

    def descendants(self, artifact_id: str) -> list[str]:
        seen: set[str] = set()
        stack = list(self.children.get(artifact_id, set()))
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            stack.extend(self.children.get(current, set()))
        return sorted(seen)

    def lineage(self, artifact_id: str) -> list[str]:
        seen: set[str] = set()
        stack = [artifact_id]
        while stack:
            current = stack.pop()
            node = self.nodes.get(current)
            if not node:
                continue
            for parent in node.parent_ids:
                if parent not in seen:
                    seen.add(parent)
                    stack.append(parent)
        return sorted(seen)
