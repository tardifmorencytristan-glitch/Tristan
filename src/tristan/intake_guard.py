from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Iterable

from .ultra_closure import DebtVector, MissionGenome, compile_mission_genome


PUBLIC_SAFE = "PUBLIC_SAFE"
PRIVATE = "PRIVATE"
SECRET = "SECRET"
VISIBILITY_RANK = {PUBLIC_SAFE: 0, PRIVATE: 1, SECRET: 2}

SOURCE_POLICIES = {
    "stackoverflow": {
        "ingestion_mode": "MANUAL_PROBLEM_TEXT_ONLY",
        "automated_publication": False,
        "policy_status": "AI_GENERATED_PUBLICATION_BLOCKED_BY_LOCAL_PROFILE",
    },
    "mathoverflow": {
        "ingestion_mode": "MANUAL_PROBLEM_TEXT_ONLY",
        "automated_publication": False,
        "policy_status": "AI_GENERATED_PUBLICATION_BLOCKED_BY_LOCAL_PROFILE",
    },
    "physics-stackexchange": {
        "ingestion_mode": "MANUAL_PROBLEM_TEXT_ONLY",
        "automated_publication": False,
        "policy_status": "AI_GENERATED_PUBLICATION_BLOCKED_BY_LOCAL_PROFILE",
    },
    "github": {
        "ingestion_mode": "AUTHORIZED_CONNECTOR_ONLY",
        "automated_publication": False,
        "policy_status": "REPOSITORY_RULES_REQUIRED",
    },
}

DOMAIN_VERIFICATION = {
    "code": (
        "minimal_reproducer",
        "unit_tests",
        "regression_tests",
        "static_or_type_checks_when_applicable",
        "benchmark_when_performance_is_claimed",
    ),
    "math": (
        "explicit_assumptions",
        "counterexample_search",
        "symbolic_or_exact_cross_check",
        "numerical_sanity_check_when_applicable",
        "formal_or_human_proof_review_for_certification",
    ),
    "physics": (
        "dimensional_analysis",
        "limiting_cases",
        "conservation_or_symmetry_checks",
        "numerical_cross_check",
        "literature_and_measurement_boundary",
    ),
    "engineering": (
        "requirements",
        "failure_modes",
        "simulation_or_model_check",
        "test_plan",
        "safety_and_operating_limits",
    ),
    "data": (
        "dataset_provenance",
        "schema_validation",
        "statistical_sanity_checks",
        "leakage_and_bias_checks",
        "reproducible_analysis",
    ),
}


def _digest(value: object) -> str:
    blob = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _valid_sha40(value: str) -> bool:
    value = value.strip().lower()
    return len(value) == 40 and all(ch in "0123456789abcdef" for ch in value)


@dataclass(frozen=True)
class GroundedSource:
    repository: str
    path: str
    commit: str
    locator: str
    visibility: str = PUBLIC_SAFE

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.repository.strip():
            errors.append("repository required")
        if not self.path.strip():
            errors.append("path required")
        if not _valid_sha40(self.commit):
            errors.append("commit must be sha40")
        if not self.locator.strip():
            errors.append("locator required")
        if self.visibility not in VISIBILITY_RANK:
            errors.append("unknown visibility")
        return errors

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class GroundedClaim:
    claim_id: str
    text: str
    role: str
    sources: tuple[GroundedSource, ...]
    weight: float = 1.0
    substantive: bool = True

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.claim_id.strip():
            errors.append("claim_id required")
        if not self.text.strip():
            errors.append("text required")
        if not self.role.strip():
            errors.append("role required")
        if self.weight < 0:
            errors.append("weight must be non-negative")
        for source in self.sources:
            errors.extend(source.validate())
        return errors


@dataclass(frozen=True)
class IntakeRequest:
    request_id: str
    source: str
    domain: str
    title: str
    body: str
    tags: tuple[str, ...] = ()
    requested_publication: bool = False

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.request_id.strip():
            errors.append("request_id required")
        if not self.title.strip():
            errors.append("title required")
        if self.source not in SOURCE_POLICIES:
            errors.append(f"unknown source policy: {self.source}")
        if self.domain not in DOMAIN_VERIFICATION:
            errors.append(f"unknown domain: {self.domain}")
        return errors


@dataclass(frozen=True)
class GroundingReceipt:
    status: str
    substantive_claims: int
    supported_claims: int
    weighted_grounding_coverage: float
    unsupported_claim_ids: tuple[str, ...]
    scope_violation_claim_ids: tuple[str, ...]
    path_violation_claim_ids: tuple[str, ...]
    commit_violation_claim_ids: tuple[str, ...]
    visibility_violation_claim_ids: tuple[str, ...]
    role_violation_claim_ids: tuple[str, ...]
    authority_granted: bool
    scientific_pass: bool
    digest: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class IntakePlan:
    schema_version: str
    request: dict
    source_policy: dict
    verification_contract: tuple[str, ...]
    publication_allowed: bool
    publication_blockers: tuple[str, ...]
    mission_genome: dict
    grounding: dict | None
    status: str
    authority_granted: bool
    scientific_pass: bool
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def audit_grounded_claims(
    claims: Iterable[GroundedClaim],
    *,
    allowed_repositories: tuple[str, ...],
    allowed_paths: tuple[str, ...],
    exact_commits: dict[str, str],
    allowed_roles: tuple[str, ...],
    target_visibility: str = PUBLIC_SAFE,
) -> GroundingReceipt:
    if target_visibility not in VISIBILITY_RANK:
        raise ValueError("unknown target_visibility")

    allowed_repo_set = set(allowed_repositories)
    allowed_path_set = set(allowed_paths)
    allowed_role_set = set(allowed_roles)
    target_rank = VISIBILITY_RANK[target_visibility]

    claims = tuple(claims)
    unsupported: list[str] = []
    bad_scope: list[str] = []
    bad_path: list[str] = []
    bad_commit: list[str] = []
    bad_visibility: list[str] = []
    bad_role: list[str] = []
    supported_ids: set[str] = set()

    for claim in claims:
        errors = claim.validate()
        if errors:
            raise ValueError(f"{claim.claim_id}: {'; '.join(errors)}")
        if not claim.substantive:
            continue
        failed = False
        if claim.role not in allowed_role_set:
            bad_role.append(claim.claim_id)
            failed = True
        if not claim.sources:
            unsupported.append(claim.claim_id)
            failed = True
        for source in claim.sources:
            if source.repository not in allowed_repo_set:
                bad_scope.append(claim.claim_id)
                failed = True
                continue
            if source.path not in allowed_path_set:
                bad_path.append(claim.claim_id)
                failed = True
            expected = exact_commits.get(source.repository)
            if expected is None or source.commit != expected:
                bad_commit.append(claim.claim_id)
                failed = True
            if VISIBILITY_RANK[source.visibility] > target_rank:
                bad_visibility.append(claim.claim_id)
                failed = True
        if not failed:
            supported_ids.add(claim.claim_id)

    substantive = [claim for claim in claims if claim.substantive]
    total_weight = sum(claim.weight for claim in substantive)
    supported_weight = sum(
        claim.weight for claim in substantive if claim.claim_id in supported_ids
    )
    coverage = supported_weight / total_weight if total_weight else 0.0

    if not substantive:
        status = "HOLD_EMPTY_ARTIFACT"
    elif unsupported:
        status = "HOLD_UNSOURCED"
    elif bad_scope:
        status = "HOLD_SOURCE_SCOPE"
    elif bad_path:
        status = "HOLD_SOURCE_PATH"
    elif bad_commit:
        status = "HOLD_COMMIT_MISMATCH"
    elif bad_visibility:
        status = "HOLD_VISIBILITY"
    elif bad_role:
        status = "HOLD_ROLE_SCOPE"
    elif coverage == 1.0:
        status = "PASS_GROUNDED"
    else:
        status = "HOLD_GROUNDING_GAP"

    payload = {
        "status": status,
        "substantive_claims": len(substantive),
        "supported_claims": len(supported_ids),
        "weighted_grounding_coverage": coverage,
        "unsupported_claim_ids": tuple(sorted(set(unsupported))),
        "scope_violation_claim_ids": tuple(sorted(set(bad_scope))),
        "path_violation_claim_ids": tuple(sorted(set(bad_path))),
        "commit_violation_claim_ids": tuple(sorted(set(bad_commit))),
        "visibility_violation_claim_ids": tuple(sorted(set(bad_visibility))),
        "role_violation_claim_ids": tuple(sorted(set(bad_role))),
        "authority_granted": False,
        "scientific_pass": False,
    }
    return GroundingReceipt(**payload, digest=_digest(payload))


def compile_intake_plan(
    request: IntakeRequest,
    *,
    context_ids: tuple[str, ...],
    residuals: tuple[str, ...] = (),
    debt: DebtVector | None = None,
    grounding: GroundingReceipt | None = None,
) -> IntakePlan:
    errors = request.validate()
    if errors:
        raise ValueError("; ".join(errors))

    policy = SOURCE_POLICIES[request.source]
    blockers: list[str] = []
    if not policy["automated_publication"]:
        blockers.append("AUTOMATED_PUBLICATION_DISABLED")
    if policy["policy_status"] == "REPOSITORY_RULES_REQUIRED":
        blockers.append("REPOSITORY_RULES_NOT_YET_VERIFIED")
    if request.requested_publication:
        blockers.append("PUBLICATION_REQUIRES_EXPLICIT_AUTHORITY")
    if grounding is not None and grounding.status != "PASS_GROUNDED":
        blockers.append("GROUNDING_NOT_PASS")

    augmented_residuals = tuple(dict.fromkeys(
        residuals
        + (f"VERIFY_DOMAIN_{request.domain.upper()}",)
        + (() if grounding is None or grounding.status == "PASS_GROUNDED"
           else ("GROUNDING_GAP",))
    ))
    genome = compile_mission_genome(
        mission_id=f"INTAKE-{request.request_id}",
        goal=request.title,
        residuals=augmented_residuals,
        context_ids=context_ids,
        debt=debt or DebtVector(),
    )

    status = "READY_INTERNAL" if not blockers else "HOLD"
    return IntakePlan(
        schema_version="tristan-intake-guard-r10",
        request=asdict(request),
        source_policy=dict(policy),
        verification_contract=DOMAIN_VERIFICATION[request.domain],
        publication_allowed=False,
        publication_blockers=tuple(blockers),
        mission_genome=genome.to_dict(),
        grounding=grounding.to_dict() if grounding is not None else None,
        status=status,
        authority_granted=False,
        scientific_pass=False,
        boundaries=(
            "ProblemIntake != PublicationAuthority",
            "GroundingPASS != ScientificTruth",
            "RepositorySource != ScientificEvidence",
            "PrivateSource -> PublicOutput = FORBIDDEN",
            "NoSource -> NoSubstantiveClaim",
            "PolicyProfile != TimelessExternalPolicy",
            "MissionGenome != Execution",
        ),
    )
