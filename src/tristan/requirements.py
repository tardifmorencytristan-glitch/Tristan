from __future__ import annotations

import re
from dataclasses import dataclass

from .demand_ir import RequirementIR


@dataclass(frozen=True)
class ExtractedRequirement:
    requirement: RequirementIR
    category: str
    source_text: str
    confidence: str


_MODAL = re.compile(r"\b(shall|must|required|requires?|mandatory|will provide|is to provide)\b", re.I)
_OPTIONAL = re.compile(r"\b(should|may|optional|desirable|preferred)\b", re.I)
_EVIDENCE = re.compile(r"\b(evidence|demonstrate|proof|certif|audit|traceab|validation|verification)\w*\b", re.I)
_CATEGORIES = (
    ("ELIGIBILITY", re.compile(r"\b(eligible|eligibility|supplier|vendor|incorporated|citizen|security clearance)\b", re.I)),
    ("SECURITY", re.compile(r"\b(security|privacy|confidential|air[- ]?gap|encryption|protected)\b", re.I)),
    ("DELIVERABLE", re.compile(r"\b(deliverable|report|prototype|software|documentation|training)\b", re.I)),
    ("DEADLINE", re.compile(r"\b(deadline|closing date|due date|submit by)\b", re.I)),
    ("TECHNICAL", re.compile(r"\b(model|validation|automation|api|data|algorithm|system|platform)\b", re.I)),
)


def _category(text: str) -> str:
    for name, pattern in _CATEGORIES:
        if pattern.search(text):
            return name
    return "OTHER"


def extract_requirements(text: str) -> list[ExtractedRequirement]:
    """Conservative rule-based extraction. Silence beats guessing."""
    rows: list[ExtractedRequirement] = []
    chunks = [x.strip(" -\t") for x in re.split(r"[\n\r]+|(?<=[.;])\s+", text) if x.strip()]
    for i, chunk in enumerate(chunks):
        mandatory = bool(_MODAL.search(chunk))
        optional = bool(_OPTIONAL.search(chunk))
        if not mandatory and not optional:
            continue
        key = re.sub(r"[^a-z0-9]+", "_", chunk.lower()).strip("_")[:72] or f"requirement_{i}"
        req = RequirementIR(key=key, description=chunk, mandatory=mandatory, evidence_required=bool(_EVIDENCE.search(chunk)))
        rows.append(ExtractedRequirement(req, _category(chunk), chunk, "RULE_EXPLICIT_MODAL"))
    return rows
