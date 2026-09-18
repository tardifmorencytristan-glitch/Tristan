from __future__ import annotations

from dataclasses import asdict, dataclass

from .jarvis import compile_jarvis_plan
from .mission_queue import Mission, next_mission, rank_missions
from .registry import Registry


@dataclass(frozen=True)
class ClosurePlan:
    schema_version: str
    intent: str
    selected_context: tuple[str, ...]
    residuals: tuple[str, ...]
    missions: tuple[dict, ...]
    next_mission_id: str
    status: str
    scientific_pass: bool
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def _missions_from_plan(intent: str, selected: tuple[str, ...], residuals: tuple[str, ...]) -> list[Mission]:
    target = selected[0] if selected else "unresolved-intent"
    missions: list[Mission] = []

    if "NO_RELEVANT_REGISTERED_OBJECT" in residuals:
        missions.append(Mission(
            "M-RESEARCH", target, "SEARCH_PRIOR_ART", "source-and-provenance-court",
            expected_verified_gain=3.0, debt_reduction=2.0, reuse_potential=1.0,
            cost=1.0, risk=0.1, dependency_depth=0.0,
        ))
    if "NO_SELECTED_EVIDENCE_URL" in residuals:
        missions.append(Mission(
            "M-EVIDENCE", target, "RETRIEVE_EVIDENCE", "evidence-capsule-court",
            expected_verified_gain=4.0, debt_reduction=4.0, reuse_potential=1.0,
            cost=1.0, risk=0.1, dependency_depth=0.0,
        ))
    if "SELECTED_CONTEXT_CONTAINS_UNPROMOTED_OBJECTS" in residuals:
        missions.append(Mission(
            "M-VALIDATE", target, "CLOSE_EVIDENCE_DEBT", "oak-promotion-court",
            expected_verified_gain=3.0, debt_reduction=5.0, reuse_potential=1.0,
            cost=1.2, risk=0.2, dependency_depth=0.0,
        ))
    if selected:
        missions.append(Mission(
            "M-ANTI", target, "ADVERSARIAL_CHALLENGE", "anti-corpus-pareto-court",
            expected_verified_gain=1.5, debt_reduction=1.0, reuse_potential=1.0,
            cost=0.8, risk=0.1, dependency_depth=0.0,
        ))
    if selected and not residuals:
        missions.append(Mission(
            "M-CRYSTAL", target, "CRYSTAL_READINESS_CHECK", "crystal-compiler-court",
            expected_verified_gain=1.0, debt_reduction=1.0, reuse_potential=3.0,
            cost=0.5, risk=0.1, dependency_depth=0.0,
        ))
    return missions


def compile_closure_plan(intent: str, registry: Registry, limit: int = 8) -> ClosurePlan:
    jarvis = compile_jarvis_plan(intent, registry, limit=limit)
    missions = _missions_from_plan(intent, jarvis.selected_context, jarvis.residuals)
    ranked = rank_missions(missions)
    decision = next_mission(missions)
    return ClosurePlan(
        schema_version="jarvis-closure-r2",
        intent=intent,
        selected_context=jarvis.selected_context,
        residuals=jarvis.residuals,
        missions=tuple(m.to_dict() for m in ranked),
        next_mission_id=decision.next_mission_id,
        status="PROVISIONAL_ENGINEERING_CLOSURE_PLAN",
        scientific_pass=False,
        boundaries=(
            "MissionPriority != ScientificImportance",
            "EngineeringCrystal != ScientificPASS",
            "ParetoSurvival != Truth",
            "FailureMemory != AutomaticRepairAuthority",
            "NO_ACTION is admissible",
        ),
    )
