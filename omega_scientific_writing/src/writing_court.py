from __future__ import annotations

import hashlib
import re

STRONG_PATTERNS = (
    "universally", "proves", "proven", "causes", "causal", "validated",
    "scientifically validated", "world-first", "novel method", "always superior",
)
LIMITATION_MARKERS = (
    "not a calibrated", "not calibrated", "not a validation", "does not establish",
    "does not demonstrate", "bounded", "within", "evaluated", "roughly",
)


def blind_id(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _contains_number(text: str, expected: str) -> bool:
    # Accept exact decimal prefix as written in the frozen spec.
    return expected in text


def score_text(text: str, spec: dict) -> dict:
    lower = text.lower()
    required_numbers = [str(x) for x in spec.get("required_numbers", [])]
    required_terms = [str(x).lower() for x in spec.get("required_terms", [])]
    scope_terms = [str(x).lower() for x in spec.get("scope_terms", [])]

    numeric_hits = sum(_contains_number(text, x) for x in required_numbers)
    term_hits = sum(x in lower for x in required_terms)
    scope_hits = sum(x in lower for x in scope_terms)
    strong_hits = sum(x in lower for x in STRONG_PATTERNS)
    limitation_hits = sum(x in lower for x in LIMITATION_MARKERS)

    numeric_fidelity = 0.0 if not required_numbers else numeric_hits / len(required_numbers)
    term_fidelity = 0.0 if not required_terms else term_hits / len(required_terms)
    scope_coverage = 0.0 if not scope_terms else scope_hits / len(scope_terms)
    calibration = max(0.0, 1.0 - min(1.0, strong_hits / 2.0))
    limitation_coverage = min(1.0, limitation_hits / max(1, spec.get("limitation_target", 2)))

    words = re.findall(r"\b\w+[\w.-]*\b", text)
    word_count = len(words)
    max_words = int(spec.get("max_words", 90))
    concision = 1.0 if word_count <= max_words else max(0.0, max_words / word_count)

    weights = spec.get("weights", {
        "numeric_fidelity": 3.0,
        "term_fidelity": 2.0,
        "scope_coverage": 2.0,
        "calibration": 4.0,
        "limitation_coverage": 3.0,
        "concision": 1.0,
    })
    components = {
        "numeric_fidelity": numeric_fidelity,
        "term_fidelity": term_fidelity,
        "scope_coverage": scope_coverage,
        "calibration": calibration,
        "limitation_coverage": limitation_coverage,
        "concision": concision,
    }
    total = sum(weights[k] * components[k] for k in components)
    max_total = sum(weights.values())
    return {
        "blind_id": blind_id(text),
        "score": round(total / max_total, 6),
        "components": {k: round(v, 6) for k, v in components.items()},
        "word_count": word_count,
        "strong_language_hits": strong_hits,
    }


def run_court(packet: dict) -> dict:
    spec = packet["frozen_spec"]
    evaluated = []
    origin_map = {}
    for candidate in packet.get("candidates", []):
        result = score_text(candidate["text"], spec)
        result["text_sha256"] = hashlib.sha256(candidate["text"].encode("utf-8")).hexdigest()
        evaluated.append(result)
        origin_map[result["blind_id"]] = candidate["origin"]
    evaluated.sort(key=lambda x: (-x["score"], x["blind_id"]))
    return {
        "status": "DIAGNOSTIC_INTERNAL_COURT",
        "ranking_blind": evaluated,
        "winner_blind_id": evaluated[0]["blind_id"] if evaluated else None,
        "origin_map_audit_only": origin_map,
        "winner_origin_audit_only": origin_map.get(evaluated[0]["blind_id"]) if evaluated else None,
        "boundaries": [
            "InternalDiagnostic != IndependentHumanReview",
            "HeuristicScore != ProseQualityTruth",
            "SameGeneratorCandidates != IndependentBaselines",
            "WinningThisCourt != ScientificPASS",
            "NO_ACTION is admissible",
        ],
    }
