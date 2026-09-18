from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchQuestion:
    id: str
    question: str
    required_evidence: tuple[str, ...]
    stop_condition: str


QUESTIONS = (
    ResearchQuestion(
        "Q001",
        "Does a cost-matched hierarchical tree of identical LC resonators produce a reproducibly different modal spectrum than chain and star controls?",
        ("analytic surrogate", "independent numerical solver", "matched node/edge/component budget"),
        "No stable spectral difference after perturbation and independent recomputation.",
    ),
    ResearchQuestion(
        "Q002",
        "Does any spectral advantage survive component tolerances and coupling perturbations?",
        ("deterministic perturbation sweep", "uncertainty interval", "matched controls"),
        "Candidate advantage overlaps control uncertainty interval.",
    ),
    ResearchQuestion(
        "Q003",
        "Does a circuit-level advantage survive a field-level model?",
        ("SPICE or equivalent network model", "field solver", "loss model"),
        "Network-level advantage disappears under field/loss model.",
    ),
)


def frontier_queue() -> tuple[dict[str, object], ...]:
    return tuple({
        "id": q.id,
        "question": q.question,
        "required_evidence": q.required_evidence,
        "stop_condition": q.stop_condition,
        "status": "UNKNOWN",
    } for q in QUESTIONS)
