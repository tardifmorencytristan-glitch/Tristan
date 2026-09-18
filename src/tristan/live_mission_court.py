from __future__ import annotations

from dataclasses import asdict, dataclass

from .scientific_connectors import build_source_plan


@dataclass(frozen=True)
class MissionDecision:
    mission_id: str
    decision: str
    evidence_refs: tuple[str, ...]
    authority_granted: bool = False
    scientific_pass: bool = False
    reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return asdict(self)


def decide_drive_reuse(
    *,
    mission_id: str,
    matching_artifact_ids: tuple[str, ...],
) -> MissionDecision:
    if matching_artifact_ids:
        return MissionDecision(
            mission_id=mission_id,
            decision="REUSE_EXISTING",
            evidence_refs=matching_artifact_ids,
            reasons=("existing relevant artifacts observed",),
        )
    return MissionDecision(
        mission_id=mission_id,
        decision="CREATE_CANDIDATE",
        evidence_refs=(),
        reasons=("no relevant existing artifact observed",),
    )


def qualify_exact_head(
    *,
    mission_id: str,
    candidate_head: str,
    observed_head: str,
    required_workflows: tuple[tuple[str, str, str], ...],
) -> MissionDecision:
    refs = tuple(run_id for _, _, run_id in required_workflows)
    if candidate_head != observed_head:
        return MissionDecision(
            mission_id=mission_id,
            decision="HOLD_HEAD_MISMATCH",
            evidence_refs=refs,
            reasons=("observed head differs from candidate head",),
        )
    failed = [
        name
        for name, conclusion, _ in required_workflows
        if conclusion != "success"
    ]
    if failed:
        return MissionDecision(
            mission_id=mission_id,
            decision="HOLD_WORKFLOW_FAILURE",
            evidence_refs=refs,
            reasons=("non-success workflows: " + ", ".join(sorted(failed)),),
        )
    return MissionDecision(
        mission_id=mission_id,
        decision="EXACT_HEAD_SOFTWARE_PASS",
        evidence_refs=refs,
        reasons=("candidate head matches observed head", "all required workflows succeeded"),
    )


def assess_render_staging(
    *,
    mission_id: str,
    candidate_repo: str,
    candidate_branch: str,
    service_repo: str,
    service_branch: str,
    service_id: str,
) -> MissionDecision:
    refs = (service_id,)
    if candidate_repo != service_repo:
        return MissionDecision(
            mission_id=mission_id,
            decision="NO_DEPLOY_REPO_MISMATCH",
            evidence_refs=refs,
            reasons=("candidate repository differs from Render service repository",),
        )
    if candidate_branch != service_branch:
        return MissionDecision(
            mission_id=mission_id,
            decision="NO_DEPLOY_BRANCH_MISMATCH",
            evidence_refs=refs,
            reasons=("candidate branch differs from Render service branch",),
        )
    return MissionDecision(
        mission_id=mission_id,
        decision="STAGING_ELIGIBLE_NOT_AUTHORIZED",
        evidence_refs=refs,
        reasons=("repository and branch match",),
    )


def compile_scientific_source_mission(
    *,
    mission_id: str,
    intent: str,
) -> MissionDecision:
    plan = build_source_plan(intent)
    source_ids = tuple(plan["selected_sources"])
    if not source_ids:
        return MissionDecision(
            mission_id=mission_id,
            decision="HOLD_NO_SOURCE_SELECTED",
            evidence_refs=(),
            reasons=("no scientific source matched the intent",),
        )
    return MissionDecision(
        mission_id=mission_id,
        decision="SOURCE_PLAN_ONLY",
        evidence_refs=source_ids,
        reasons=(
            "scientific sources selected",
            "network retrieval not executed by source planning",
        ),
    )
