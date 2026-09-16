from __future__ import annotations

import re
from dataclasses import dataclass

from .demand_ir import RequirementIR


@dataclass(frozen=True)
class RequirementR2:
    requirement: RequirementIR
    category: str
    source_span: str
    condition: str | None = None
    deadline: str | None = None
    acceptance_test: str | None = None
    confidence: str = "RULE_EXPLICIT"


_MANDATORY = re.compile(r"\b(shall|must|required|mandatory|is required to|will provide)\b", re.I)
_OPTIONAL = re.compile(r"\b(should|may|optional|preferred|desirable)\b", re.I)
_DEADLINE = re.compile(r"\b(?:by|before|no later than)\s+([A-Z][a-z]+\s+\d{1,2},?\s+\d{4}|\d{4}-\d{2}-\d{2})", re.I)
_ACCEPT = re.compile(r"\b(acceptance|accepted when|pass if|demonstrate|verify|validation|evidence)\b", re.I)
_CONDITION = re.compile(r"\b(if|when|provided that|subject to|unless)\b(.+)$", re.I)


def _category(text: str) -> str:
    patterns = {
        "ELIGIBILITY": r"\b(eligible|eligibility|supplier|vendor|clearance|incorporated|citizen)\b",
        "SECURITY": r"\b(security|privacy|confidential|air[- ]?gap|encryption|protected)\b",
        "DELIVERABLE": r"\b(deliverable|report|prototype|software|documentation|training)\b",
        "DEADLINE": r"\b(deadline|closing date|due date|submit by|no later than)\b",
        "TECHNICAL": r"\b(model|validation|automation|api|data|algorithm|system|platform|traceability)\b",
    }
    for name, pattern in patterns.items():
        if re.search(pattern, text, re.I):
            return name
    return "OTHER"


def extract_requirements_r2(text: str) -> list[RequirementR2]:
    """Conservative clause compiler. It extracts only explicit obligations/preferences."""
    chunks = [x.strip(" -\t") for x in re.split(r"[\n\r]+|(?<=[.;])\s+", text) if x.strip()]
    out: list[RequirementR2] = []
    for i, chunk in enumerate(chunks):
        mandatory = bool(_MANDATORY.search(chunk))
        optional = bool(_OPTIONAL.search(chunk))
        if not mandatory and not optional:
            continue
        key = re.sub(r"[^a-z0-9]+", "_", chunk.lower()).strip("_")[:72] or f"requirement_{i}"
        deadline_match = _DEADLINE.search(chunk)
        condition_match = _CONDITION.search(chunk)
        out.append(RequirementR2(
            requirement=RequirementIR(key, chunk, mandatory=mandatory, evidence_required=bool(_ACCEPT.search(chunk))),
            category=_category(chunk),
            source_span=chunk,
            condition=condition_match.group(0) if condition_match else None,
            deadline=deadline_match.group(1) if deadline_match else None,
            acceptance_test=chunk if _ACCEPT.search(chunk) else None,
        ))
    return out
