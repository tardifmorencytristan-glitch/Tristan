from __future__ import annotations

from dataclasses import asdict, dataclass

from .pipeline import run_intent
from .registry import Registry
from .router import ActionCandidate, choose_next_action


JARVIS_BOUNDARIES = (
    "Generated != Verified",
    "Simulation != Measurement",
    "Prototype != Production",
    "Consensus != Evidence",
    "Capability != Authority",
    "NO_ACTION is admissible",
)


@dataclass(frozen=True)
class JarvisPlan:
    schema_version: str
    intent: str
    selected_context: tuple[str, ...]
    residuals: tuple[str, ...]
    next_action: str
    next_transformation: str
    next_action_score: float | None
    epistemic_status: str
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def _candidate_actions(residuals: tuple[str, ...], has_context: bool) -> list[ActionCandidate]:
    candidates: list[ActionCandidate] = []
    if "NO_RELEVANT_REGISTERED_OBJECT" in residuals:
        candidates.append(ActionCandidate(
            "SEARCH_PRIOR_ART",
            "research",
            evidence_gain=3.0,
            capability_gain=1.0,
            debt_reduction=2.0,
            cost=1.0,
            risk=0.1,
            complexity=0.5,
        ))
    if "NO_SELECTED_EVIDENCE_URL" in residuals:
        candidates.append(ActionCandidate(
            "RETRIEVE_EVIDENCE",
            "evidence",
            evidence_gain=4.0,
            debt_reduction=3.0,
            cost=1.0,
            risk=0.1,
            complexity=0.5,
        ))
    if "SELECTED_CONTEXT_CONTAINS_UNPROMOTED_OBJECTS" in residuals:
        candidates.append(ActionCandidate(
            "CLOSE_EVIDENCE_DEBT",
            "validate",
            evidence_gain=3.0,
            debt_reduction=4.0,
            cost=1.2,
            risk=0.2,
            complexity=0.5,
        ))
    if has_context:
        candidates.append(ActionCandidate(
            "ADVERSARIAL_CHALLENGE",
            "attack",
            evidence_gain=1.5,
            capability_gain=0.5,
            cost=0.8,
            risk=0.1,
            complexity=0.4,
        ))
    if not residuals and has_context:
        candidates.append(ActionCandidate(
            "REUSE_VERIFIED_CONTEXT",
            "reuse",
            capability_gain=3.0,
            utility_gain=2.0,
            cost=0.5,
            risk=0.1,
            complexity=0.2,
        ))
    return candidates


def compile_jarvis_plan(intent: str, registry: Registry, limit: int = 8) -> JarvisPlan:
    receipt = run_intent(intent, registry, limit=limit)
    selected = tuple(receipt.context.get("selected_ids", ()))
    action = choose_next_action(_candidate_actions(receipt.residuals, bool(selected)))
    if action is None:
        next_action = "NO_ACTION"
        next_transformation = "none"
        score = None
    else:
        next_action = action.action_id
        next_transformation = action.transformation_id
        score = action.score
    return JarvisPlan(
        schema_version="jarvis-omega-core-r1",
        intent=intent,
        selected_context=selected,
        residuals=receipt.residuals,
        next_action=next_action,
        next_transformation=next_transformation,
        next_action_score=score,
        epistemic_status="PROVISIONAL_ENGINEERING_PLAN",
        boundaries=JARVIS_BOUNDARIES,
    )
