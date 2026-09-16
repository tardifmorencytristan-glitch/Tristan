from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .provenance import BoundingBox, ProvenanceAnchor
from .representation_ir import (
    ConfidenceVector,
    REPRESENTATION_KINDS,
    RepresentationGraph,
    RepresentationNode,
    RepresentationRelation,
)


BLOCK_KINDS = REPRESENTATION_KINDS - {"DOCUMENT", "PAGE"}


@dataclass(frozen=True)
class PDFBlockObservation:
    id: str
    kind: str
    bbox: BoundingBox
    content: Any = None
    reading_order: int = 0
    confidence: ConfidenceVector = field(default_factory=ConfidenceVector)
    source_locator: str = ""
    metadata: tuple[tuple[str, str], ...] = ()

    def validate(self, page_width: float, page_height: float) -> list[str]:
        errors: list[str] = []
        if not self.id:
            errors.append("PDFBlockObservation.id required")
        if self.kind not in BLOCK_KINDS:
            errors.append(f"unsupported PDF block kind: {self.kind}")
        if self.reading_order < 0:
            errors.append("PDFBlockObservation.reading_order must be >= 0")
        errors.extend(self.bbox.validate())
        if self.bbox.x0 < 0 or self.bbox.y0 < 0:
            errors.append("PDFBlockObservation bbox must be within page origin")
        if self.bbox.x1 > page_width or self.bbox.y1 > page_height:
            errors.append("PDFBlockObservation bbox exceeds page bounds")
        errors.extend(self.confidence.validate())
        return errors


@dataclass(frozen=True)
class PDFPageObservation:
    number: int
    width: float
    height: float
    blocks: tuple[PDFBlockObservation, ...] = ()
    rotation: int = 0

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.number < 1:
            errors.append("PDFPageObservation.number must be >= 1")
        if self.width <= 0 or self.height <= 0:
            errors.append("PDFPageObservation width/height must be positive")
        if self.rotation % 90 != 0:
            errors.append("PDFPageObservation.rotation must be a multiple of 90")
        ids = [b.id for b in self.blocks]
        if len(ids) != len(set(ids)):
            errors.append("PDFPageObservation block ids must be unique within page")
        orders = [b.reading_order for b in self.blocks]
        if len(orders) != len(set(orders)):
            errors.append("PDFPageObservation reading_order must be unique within page")
        for block in self.blocks:
            errors.extend(block.validate(self.width, self.height))
        return errors


@dataclass(frozen=True)
class PDFDocumentObservation:
    source_artifact_id: str
    source_sha256: str
    parser: str
    parser_version: str
    pages: tuple[PDFPageObservation, ...]
    observation_status: str = "OBSERVED"

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.source_artifact_id:
            errors.append("PDFDocumentObservation.source_artifact_id required")
        if not self.parser:
            errors.append("PDFDocumentObservation.parser required")
        if not self.parser_version:
            errors.append("PDFDocumentObservation.parser_version required")
        if not self.pages:
            errors.append("PDFDocumentObservation.pages required")
        page_numbers = [p.number for p in self.pages]
        if len(page_numbers) != len(set(page_numbers)):
            errors.append("PDFDocumentObservation page numbers must be unique")
        for page in self.pages:
            errors.extend(page.validate())
        # Reuse the provenance contract as the canonical SHA-256 validator.
        probe = ProvenanceAnchor(
            source_artifact_id=self.source_artifact_id,
            source_content_hash=self.source_sha256,
            extractor=self.parser,
            extractor_version=self.parser_version,
        )
        errors.extend(probe.validate())
        return errors


@dataclass
class PDFIR:
    source_artifact_id: str
    source_sha256: str
    parser: str
    parser_version: str
    observation_status: str
    page_count: int
    graph: RepresentationGraph

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_artifact_id": self.source_artifact_id,
            "source_sha256": self.source_sha256,
            "parser": self.parser,
            "parser_version": self.parser_version,
            "observation_status": self.observation_status,
            "page_count": self.page_count,
            "graph": self.graph.to_dict(),
        }


def _anchor_confidence(vector: ConfidenceVector) -> float:
    observed = vector.observed_axes()
    return min(observed.values()) if observed else 1.0


def compile_pdf_observation(observation: PDFDocumentObservation) -> PDFIR:
    errors = observation.validate()
    if errors:
        raise ValueError(errors)

    graph = RepresentationGraph()
    doc_id = f"{observation.source_artifact_id}:document"
    graph.add_node(
        RepresentationNode(
            id=doc_id,
            kind="DOCUMENT",
            content={"format": "PDF", "page_count": len(observation.pages)},
            provenance=[
                ProvenanceAnchor(
                    source_artifact_id=observation.source_artifact_id,
                    source_content_hash=observation.source_sha256,
                    extractor=observation.parser,
                    extractor_version=observation.parser_version,
                )
            ],
            confidence=ConfidenceVector(provenance=1.0),
            metadata={"observation_status": observation.observation_status},
        )
    )

    page_ids: list[str] = []
    for page in sorted(observation.pages, key=lambda p: p.number):
        page_id = f"{observation.source_artifact_id}:page:{page.number}"
        page_ids.append(page_id)
        page_bbox = BoundingBox(0.0, 0.0, page.width, page.height)
        graph.add_node(
            RepresentationNode(
                id=page_id,
                kind="PAGE",
                content={"number": page.number, "width": page.width, "height": page.height, "rotation": page.rotation},
                provenance=[
                    ProvenanceAnchor(
                        source_artifact_id=observation.source_artifact_id,
                        source_content_hash=observation.source_sha256,
                        extractor=observation.parser,
                        extractor_version=observation.parser_version,
                        page=page.number,
                        bbox=page_bbox,
                        source_locator=f"page:{page.number}",
                    )
                ],
                confidence=ConfidenceVector(layout=1.0, provenance=1.0),
                parent_ids=[doc_id],
            )
        )

        block_ids: list[str] = []
        for block in sorted(page.blocks, key=lambda b: b.reading_order):
            block_id = f"{observation.source_artifact_id}:page:{page.number}:block:{block.id}"
            block_ids.append(block_id)
            locator = block.source_locator or f"page:{page.number}/block:{block.id}"
            graph.add_node(
                RepresentationNode(
                    id=block_id,
                    kind=block.kind,
                    content=block.content,
                    provenance=[
                        ProvenanceAnchor(
                            source_artifact_id=observation.source_artifact_id,
                            source_content_hash=observation.source_sha256,
                            extractor=observation.parser,
                            extractor_version=observation.parser_version,
                            page=page.number,
                            bbox=block.bbox,
                            source_locator=locator,
                            confidence=_anchor_confidence(block.confidence),
                        )
                    ],
                    confidence=block.confidence,
                    parent_ids=[page_id],
                    metadata={"reading_order": block.reading_order, **dict(block.metadata)},
                )
            )

        if block_ids:
            graph.add_relation(
                RepresentationRelation(
                    id=f"contains:{page_id}",
                    kind="CONTAINS",
                    source_ids=(page_id,),
                    target_ids=tuple(block_ids),
                )
            )

    graph.add_relation(
        RepresentationRelation(
            id=f"contains:{doc_id}",
            kind="CONTAINS",
            source_ids=(doc_id,),
            target_ids=tuple(page_ids),
        )
    )

    return PDFIR(
        source_artifact_id=observation.source_artifact_id,
        source_sha256=observation.source_sha256,
        parser=observation.parser,
        parser_version=observation.parser_version,
        observation_status=observation.observation_status,
        page_count=len(observation.pages),
        graph=graph,
    )
