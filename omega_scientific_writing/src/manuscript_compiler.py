from __future__ import annotations

from .argument_graph import build_argument_graph
from .claim_writer import bounded_claim
from .citation_bindings import validate_bindings
from .reviewer_council import review


def compile_manuscript(doc: dict) -> dict:
    claims = doc.get("claims", [])
    sources = doc.get("sources", [])
    bindings = doc.get("citation_bindings", [])
    graph = build_argument_graph(doc.get("argument_nodes", []), doc.get("argument_edges", []))
    paragraphs = [bounded_claim(c) for c in claims]
    citation_findings = validate_bindings(claims, sources, bindings)
    council = review(doc)
    hard = [f for f in graph["findings"] + citation_findings if f.get("severity") == "ERROR"]
    verdict = "HOLD" if hard or council["verdict"] != "PASS" else "PASS"
    return {
        "verdict": verdict,
        "paragraphs": paragraphs,
        "argument_graph": graph,
        "citation_findings": citation_findings,
        "reviewer_council": council,
        "invariants": [
            "Generated != Verified",
            "LinguisticStrength <= EvidenceStrength",
            "CitationPresent != CitationEntailsClaim",
            "ReviewerCouncil != ExternalPeerReview",
        ],
    }
