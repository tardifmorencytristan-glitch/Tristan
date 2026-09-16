from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any

from .provenance import ProvenanceAnchor


REPRESENTATION_KINDS = {
    "DOCUMENT", "PAGE", "REGION", "TEXT", "SPAN", "HEADING", "PARAGRAPH", "LIST",
    "FIGURE", "CAPTION", "TABLE", "CELL", "EQUATION", "SYMBOL", "CITATION", "REFERENCE",
    "FOOTNOTE", "CODE", "FORM", "METADATA"
}

RELATION_KINDS = {
    "CONTAINS", "CONTINUES", "REFERENCES", "DEFINES", "CAPTION_OF", "EQUIVALENT_TO",
    "DERIVED_FROM", "SUPPORTS", "CONTRADICTS", "UNIT_OF", "VALUE_OF", "SYMBOL_OF",
    "CITATION_FOR", "RENDERED_AS"
}


@dataclass(frozen=True)
class ConfidenceVector:
    text: float | None = None
    structure: float | None = None
    math: float | None = None
    numeric: float | None = None
    layout: float | None = None
    provenance: float | None = None

    def validate(self) -> list[str]:
        errors: list[str] = []
        for name, value in asdict(self).items():
            if value is not None and not 0.0 <= value <= 1.0:
                errors.append(f"ConfidenceVector.{name} must be within [0,1]")
        return errors

    def observed_axes(self) -> dict[str, float]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class RepresentationNode:
    id: str
    kind: str
    content: Any = None
    provenance: list[ProvenanceAnchor] = field(default_factory=list)
    confidence: ConfidenceVector = field(default_factory=ConfidenceVector)
    parent_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.id:
            errors.append("RepresentationNode.id required")
        if self.kind not in REPRESENTATION_KINDS:
            errors.append(f"unknown representation kind: {self.kind}")
        if not self.provenance:
            errors.append("RepresentationNode.provenance required")
        for anchor in self.provenance:
            errors.extend(anchor.validate())
        errors.extend(self.confidence.validate())
        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "content": self.content,
            "provenance": [p.to_dict() for p in self.provenance],
            "confidence": asdict(self.confidence),
            "parent_ids": list(self.parent_ids),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class RepresentationRelation:
    id: str
    kind: str
    source_ids: tuple[str, ...]
    target_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...] = ()
    metadata: tuple[tuple[str, str], ...] = ()

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.id:
            errors.append("RepresentationRelation.id required")
        if self.kind not in RELATION_KINDS:
            errors.append(f"unknown relation kind: {self.kind}")
        if not self.source_ids:
            errors.append("RepresentationRelation.source_ids required")
        if not self.target_ids:
            errors.append("RepresentationRelation.target_ids required")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "source_ids": list(self.source_ids),
            "target_ids": list(self.target_ids),
            "evidence_ids": list(self.evidence_ids),
            "metadata": dict(self.metadata),
        }


class RepresentationGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, RepresentationNode] = {}
        self.relations: dict[str, RepresentationRelation] = {}
        self.outgoing: dict[str, set[str]] = {}
        self.incoming: dict[str, set[str]] = {}

    def add_node(self, node: RepresentationNode) -> None:
        errors = node.validate()
        if errors:
            raise ValueError(errors)
        if node.id in self.nodes:
            raise ValueError(f"duplicate representation node: {node.id}")
        self.nodes[node.id] = node
        self.outgoing.setdefault(node.id, set())
        self.incoming.setdefault(node.id, set())

    def add_relation(self, relation: RepresentationRelation) -> None:
        errors = relation.validate()
        if errors:
            raise ValueError(errors)
        if relation.id in self.relations:
            raise ValueError(f"duplicate representation relation: {relation.id}")
        referenced = set(relation.source_ids) | set(relation.target_ids)
        missing = sorted(referenced - self.nodes.keys())
        if missing:
            raise ValueError(f"relation references missing nodes: {missing}")
        self.relations[relation.id] = relation
        for source in relation.source_ids:
            self.outgoing.setdefault(source, set()).update(relation.target_ids)
        for target in relation.target_ids:
            self.incoming.setdefault(target, set()).update(relation.source_ids)

    def descendants(self, node_id: str) -> list[str]:
        seen: set[str] = set()
        stack = list(self.outgoing.get(node_id, set()))
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            stack.extend(self.outgoing.get(current, set()))
        return sorted(seen)

    def ancestors(self, node_id: str) -> list[str]:
        seen: set[str] = set()
        stack = list(self.incoming.get(node_id, set()))
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            stack.extend(self.incoming.get(current, set()))
        return sorted(seen)

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [self.nodes[k].to_dict() for k in sorted(self.nodes)],
            "relations": [self.relations[k].to_dict() for k in sorted(self.relations)],
        }
