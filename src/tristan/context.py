from __future__ import annotations

import re
from dataclasses import dataclass
from .model import TristanObject
from .registry import Registry

TOKEN_RE = re.compile(r"[a-z0-9_+\-]+", re.IGNORECASE)

STATUS_WEIGHT = {
    "VERIFIED_ENGINEERING": 6.0,
    "MEASURED": 5.5,
    "SUPPORTED": 5.0,
    "CLOSED": 4.0,
    "PROVISIONAL": 3.0,
    "HOLD": 2.0,
    "RESIDUAL": 1.5,
    "IDEA": 1.0,
    "SUPERSEDED": 0.5,
    "REJECTED": 0.0,
    "UNAVAILABLE": 0.0,
}


def _tokens(text: str) -> set[str]:
    return {m.group(0).lower() for m in TOKEN_RE.finditer(text) if len(m.group(0)) >= 2}


def score_object(query: str, obj: TristanObject) -> float:
    q = _tokens(query)
    if not q:
        return 0.0
    title_tags = _tokens(obj.title + " " + " ".join(obj.tags))
    summary = _tokens(obj.summary)
    overlap = 3.0 * len(q & title_tags) + 1.0 * len(q & summary)
    if overlap == 0:
        return 0.0
    evidence_bonus = min(2.0, 0.5 * len(obj.evidence_urls))
    return overlap + 0.15 * STATUS_WEIGHT.get(obj.status, 0.0) + evidence_bonus


@dataclass(frozen=True)
class ContextReceipt:
    query: str
    selected_ids: tuple[str, ...]
    scores: tuple[float, ...]
    omitted_count: int
    invariant: str = "minimum_sufficient_bounded_context_not_truth"

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "selected_ids": list(self.selected_ids),
            "scores": list(self.scores),
            "omitted_count": self.omitted_count,
            "invariant": self.invariant,
        }


def compile_context(query: str, registry: Registry, limit: int = 8) -> ContextReceipt:
    if limit < 1:
        raise ValueError("limit must be >= 1")
    ranked = []
    for obj in registry.all():
        score = score_object(query, obj)
        if score > 0:
            ranked.append((score, obj.id))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    selected = ranked[:limit]
    return ContextReceipt(
        query=query,
        selected_ids=tuple(object_id for _, object_id in selected),
        scores=tuple(round(score, 6) for score, _ in selected),
        omitted_count=max(0, len(ranked) - len(selected)),
    )
