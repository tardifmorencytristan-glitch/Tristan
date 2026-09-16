from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EvidenceNode:
    node_id: str
    kind: str
    status: str
    source: str = ""
    note: str = ""


@dataclass(frozen=True)
class EvidenceLink:
    source_id: str
    relation: str
    target_id: str


@dataclass
class EvidenceGraph:
    nodes: dict[str, EvidenceNode] = field(default_factory=dict)
    links: list[EvidenceLink] = field(default_factory=list)

    def add_node(self, node: EvidenceNode) -> None:
        self.nodes[node.node_id] = node

    def link(self, source_id: str, relation: str, target_id: str) -> None:
        if source_id not in self.nodes or target_id not in self.nodes:
            raise KeyError("both evidence nodes must exist before linking")
        self.links.append(EvidenceLink(source_id, relation, target_id))

    def evidence_for(self, target_id: str) -> list[EvidenceNode]:
        ids = [x.source_id for x in self.links if x.target_id == target_id and x.relation in {"SUPPORTS", "PROVES", "BOUNDS"}]
        return [self.nodes[i] for i in ids]

    def contradictions_for(self, target_id: str) -> list[EvidenceNode]:
        ids = [x.source_id for x in self.links if x.target_id == target_id and x.relation == "CONTRADICTS"]
        return [self.nodes[i] for i in ids]

    def support_status(self, target_id: str) -> str:
        if self.contradictions_for(target_id):
            return "CONTESTED"
        evidence = self.evidence_for(target_id)
        if not evidence:
            return "UNKNOWN"
        if any(e.status in {"VERIFIED", "MEASURED", "FORMALLY_PROVEN", "EXTERNALLY_REPLICATED"} for e in evidence):
            return "SUPPORTED"
        return "PARTIAL"
