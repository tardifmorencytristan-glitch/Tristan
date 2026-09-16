from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any


@dataclass
class PDFRoundTripEvidence:
    source_pdf_sha256: str
    output_pdf_sha256: str
    source_pages: list[int]
    expected_invariants: list[str] = field(default_factory=list)
    preserved_invariants: list[str] = field(default_factory=list)
    losses: list[str] = field(default_factory=list)
    boundaries: list[str] = field(default_factory=list)
    latex_engine: str = ""
    source_bytes: int = 0
    output_pages: int = 0

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["semantic_roundtrip_pass"] = self.semantic_roundtrip_pass()
        return payload

    def semantic_roundtrip_pass(self) -> bool:
        return set(self.expected_invariants) <= set(self.preserved_invariants)

    def validate(self) -> list[str]:
        errors: list[str] = []
        for name, digest in (("source_pdf_sha256", self.source_pdf_sha256), ("output_pdf_sha256", self.output_pdf_sha256)):
            if len(digest) != 64:
                errors.append(f"{name} must be SHA-256 hex")
        if not self.source_pages:
            errors.append("source_pages required")
        if not self.latex_engine:
            errors.append("latex_engine required")
        if self.source_bytes <= 0:
            errors.append("source_bytes must be positive")
        if self.output_pages <= 0:
            errors.append("output_pages must be positive")
        if not self.losses:
            errors.append("bounded roundtrip must declare losses")
        return errors


def semantic_readback(expected: list[str], readback_text: str) -> dict[str, bool]:
    return {item: item in readback_text for item in expected}


def preserved_from_checks(checks: dict[str, bool]) -> list[str]:
    return [item for item, ok in checks.items() if ok]
