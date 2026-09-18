from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable


R11_BOUNDARIES = (
    "WorkflowSuccess != ScientificPASS",
    "Mergeable != MergeAuthority",
    "ExactHeadQualification != TimelessQualification",
    "StaleBase -> HOLD",
    "HeadMove -> Requalify",
    "PortfolioDecision != MergeAuthority",
    "NO_ACTION is admissible",
)


@dataclass(frozen=True)
class WorkflowObservation:
    name: str
    status: str
    conclusion: str | None = None

    @property
    def successful(self) -> bool:
        return self.status == "completed" and self.conclusion == "success"

    def to_dict(self) -> dict:
        data = asdict(self)
        data["successful"] = self.successful
        return data


@dataclass(frozen=True)
class PullRequestObservation:
    number: int
    title: str
    base_sha: str
    head_sha: str
    mergeable: bool | None
    draft: bool
    required_workflows: tuple[str, ...]
    workflows: tuple[WorkflowObservation, ...]
    blocking_review_threads: int = 0

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.number < 1:
            errors.append("number must be >= 1")
        if not self.title.strip():
            errors.append("title required")
        if len(self.base_sha) != 40:
            errors.append("base_sha must be sha40")
        if len(self.head_sha) != 40:
            errors.append("head_sha must be sha40")
        if self.blocking_review_threads < 0:
            errors.append("blocking_review_threads must be non-negative")
        return errors

    def workflow_map(self) -> dict[str, WorkflowObservation]:
        return {row.name: row for row in self.workflows}

    def to_dict(self) -> dict:
        return {
            **asdict(self),
            "workflows": tuple(row.to_dict() for row in self.workflows),
        }


@dataclass(frozen=True)
class QualificationReceipt:
    pr_number: int
    observed_main_sha: str
    observed_head_sha: str
    decision: str
    blockers: tuple[str, ...]
    exact_head_qualified: bool
    merge_authority_granted: bool
    scientific_pass: bool
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def qualify_pr(
    observation: PullRequestObservation,
    *,
    current_main_sha: str,
) -> QualificationReceipt:
    errors = observation.validate()
    if len(current_main_sha) != 40:
        errors.append("current_main_sha must be sha40")
    if errors:
        raise ValueError("; ".join(errors))

    blockers: list[str] = []
    if observation.draft:
        blockers.append("DRAFT")
    if observation.mergeable is False:
        blockers.append("MERGE_CONFLICT")
    elif observation.mergeable is None:
        blockers.append("MERGEABILITY_UNKNOWN")

    if observation.base_sha != current_main_sha:
        blockers.append("STALE_BASE")

    if observation.blocking_review_threads:
        blockers.append("BLOCKING_REVIEW_THREADS")

    workflow_map = observation.workflow_map()
    for required in observation.required_workflows:
        observed = workflow_map.get(required)
        if observed is None:
            blockers.append(f"MISSING_WORKFLOW:{required}")
        elif not observed.successful:
            blockers.append(f"WORKFLOW_NOT_GREEN:{required}")

    if not blockers:
        decision = "QUALIFIED_EXACT_HEAD"
    elif "MERGE_CONFLICT" in blockers:
        decision = "HOLD_REBASE_OR_RESOLVE"
    elif "STALE_BASE" in blockers:
        decision = "HOLD_REPLAY_ON_CURRENT_MAIN"
    elif any(item.startswith("WORKFLOW_") or item.startswith("MISSING_WORKFLOW") for item in blockers):
        decision = "HOLD_CI"
    elif "DRAFT" in blockers:
        decision = "HOLD_DRAFT"
    elif "BLOCKING_REVIEW_THREADS" in blockers:
        decision = "HOLD_REVIEW"
    else:
        decision = "HOLD"

    return QualificationReceipt(
        pr_number=observation.number,
        observed_main_sha=current_main_sha,
        observed_head_sha=observation.head_sha,
        decision=decision,
        blockers=tuple(blockers),
        exact_head_qualified=not blockers,
        merge_authority_granted=False,
        scientific_pass=False,
        boundaries=R11_BOUNDARIES,
    )


def qualify_portfolio(
    observations: Iterable[PullRequestObservation],
    *,
    current_main_sha: str,
) -> tuple[QualificationReceipt, ...]:
    receipts = tuple(
        qualify_pr(observation, current_main_sha=current_main_sha)
        for observation in observations
    )
    return tuple(sorted(receipts, key=lambda row: (row.decision, row.pr_number)))
