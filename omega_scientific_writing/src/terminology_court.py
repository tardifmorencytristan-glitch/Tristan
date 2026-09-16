from __future__ import annotations

from .report_ir import ConceptTermIR


def _norm(text: str) -> str:
    return text.casefold().strip()


def _canonical_for_language(concept: ConceptTermIR, language: str) -> str | None:
    for lang, term in concept.canonical_terms:
        if _norm(lang) == _norm(language):
            return term
    return None


def normalize_term(text: str, concepts: tuple[ConceptTermIR, ...]) -> tuple[str | None, list[dict]]:
    needle = _norm(text)
    findings: list[dict] = []
    for concept in concepts:
        canonical = { _norm(term): term for _, term in concept.canonical_terms }
        if needle in canonical:
            return canonical[needle], findings
        if needle in {_norm(x) for x in concept.aliases}:
            canonical_term = concept.canonical_terms[0][1] if concept.canonical_terms else None
            findings.append({"severity": "WARN", "code": "TERM_ALIAS_USED", "object": concept.meta.id, "detail": canonical_term})
            return canonical_term, findings
        if needle in {_norm(x) for x in concept.ambiguous_terms}:
            findings.append({"severity": "HOLD", "code": "TERM_AMBIGUOUS", "object": concept.meta.id})
            return None, findings
        if needle in {_norm(x) for x in concept.forbidden_substitutions}:
            findings.append({"severity": "HOLD", "code": "TERM_FORBIDDEN_SUBSTITUTION", "object": concept.meta.id})
            return None, findings
    findings.append({"severity": "WARN", "code": "TERM_UNKNOWN", "object": text})
    return None, findings


def audit_terminology(usages: list[dict], concepts: tuple[ConceptTermIR, ...]) -> list[dict]:
    findings: list[dict] = []
    for usage in usages:
        object_id = usage.get("object_id", "<unknown>")
        language = usage.get("language", "")
        term = usage.get("term", "")
        needle = _norm(term)
        matched = False
        for concept in concepts:
            canonical = _canonical_for_language(concept, language)
            all_canonical = {_norm(x) for _, x in concept.canonical_terms}
            if needle in all_canonical:
                matched = True
                if not canonical:
                    findings.append({"severity": "HOLD", "code": "TERM_CANONICAL_LANGUAGE_MISSING", "object": object_id})
                break
            if needle in {_norm(x) for x in concept.aliases}:
                matched = True
                findings.append({"severity": "WARN", "code": "TERM_ALIAS_USED", "object": object_id, "detail": canonical or (concept.canonical_terms[0][1] if concept.canonical_terms else None)})
                break
            if needle in {_norm(x) for x in concept.ambiguous_terms}:
                matched = True
                findings.append({"severity": "HOLD", "code": "TERM_AMBIGUOUS", "object": object_id})
                break
            if needle in {_norm(x) for x in concept.forbidden_substitutions}:
                matched = True
                findings.append({"severity": "HOLD", "code": "TERM_FORBIDDEN_SUBSTITUTION", "object": object_id})
                break
        if not matched:
            if usage.get("origin") == "ai_generated":
                findings.append({"severity": "HOLD", "code": "AI_TERM_UNREGISTERED", "object": object_id, "detail": term})
            else:
                findings.append({"severity": "WARN", "code": "TERM_UNKNOWN", "object": object_id, "detail": term})
    return findings
