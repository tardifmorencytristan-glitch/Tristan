from __future__ import annotations

from dataclasses import dataclass, asdict
from string import hexdigits
from typing import Any


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(ch in hexdigits for ch in value)


@dataclass(frozen=True)
class BoundingBox:
    x0: float
    y0: float
    x1: float
    y1: float

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.x1 < self.x0:
            errors.append("BoundingBox.x1 must be >= x0")
        if self.y1 < self.y0:
            errors.append("BoundingBox.y1 must be >= y0")
        return errors

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True)
class ProvenanceAnchor:
    source_artifact_id: str
    source_content_hash: str
    extractor: str
    extractor_version: str
    page: int | None = None
    bbox: BoundingBox | None = None
    source_locator: str = ""
    confidence: float = 1.0

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.source_artifact_id:
            errors.append("ProvenanceAnchor.source_artifact_id required")
        if not _is_sha256(self.source_content_hash):
            errors.append("ProvenanceAnchor.source_content_hash must be 64 hex chars")
        if not self.extractor:
            errors.append("ProvenanceAnchor.extractor required")
        if not self.extractor_version:
            errors.append("ProvenanceAnchor.extractor_version required")
        if self.page is not None and self.page < 1:
            errors.append("ProvenanceAnchor.page must be >= 1")
        if not 0.0 <= self.confidence <= 1.0:
            errors.append("ProvenanceAnchor.confidence must be within [0,1]")
        if self.bbox is not None:
            errors.extend(self.bbox.validate())
        return errors

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        return payload
