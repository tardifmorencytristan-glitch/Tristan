from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Iterable


ROOT_REPOSITORY = "tardifmorencytristan-glitch/Tristan-Tardif-Morency"
LOCAL_REPOSITORY = "tardifmorencytristan-glitch/Tristan"
TARGET_VISIBILITY = "PUBLIC_SAFE"
ALLOWED_REPOSITORIES = frozenset({ROOT_REPOSITORY, LOCAL_REPOSITORY})
ALLOWED_SOURCE_VISIBILITY = frozenset({"PUBLIC_SAFE"})


def _digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return "sha256:" + sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class PublicSafeSource:
    repository: str
    path: str
    commit: str
    locator: str
    visibility: str = "PUBLIC_SAFE"


@dataclass(frozen=True)
class PublicSafeClaim:
    claim_id: str
    text: str
    sources: tuple[PublicSafeSource, ...]
    weight: float = 1.0
    substantive: bool = True


@dataclass(frozen=True)
class PublicSafeDraftReceipt:
    status: str
    substantive_claims: int
    supported_claims: int
    weighted_grounding_coverage: float
    unsupported_claim_ids: tuple[str, ...]
    source_scope_violation_claim_ids: tuple[str, ...]
    visibility_violation_claim_ids: tuple[str, ...]
    authority_granted: bool
    scientific_pass: bool
    digest: str


def load_profile(root: Path) -> dict:
    return json.loads((root / ".jarvis" / "JARVIS_REPO_PROFILE.json").read_text(encoding="utf-8"))


def audit_public_safe_draft(claims: Iterable[PublicSafeClaim]) -> PublicSafeDraftReceipt:
    claims = tuple(claim for claim in claims if claim.substantive)
    unsupported: list[str] = []
    scope: list[str] = []
    visibility: list[str] = []
    supported: list[PublicSafeClaim] = []

    for claim in claims:
        if not claim.sources:
            unsupported.append(claim.claim_id)
            continue
        bad_scope = any(source.repository not in ALLOWED_REPOSITORIES for source in claim.sources)
        bad_visibility = any(source.visibility not in ALLOWED_SOURCE_VISIBILITY for source in claim.sources)
        if bad_scope:
            scope.append(claim.claim_id)
        if bad_visibility:
            visibility.append(claim.claim_id)
        if not bad_scope and not bad_visibility:
            supported.append(claim)

    total = sum(claim.weight for claim in claims)
    covered = sum(claim.weight for claim in supported)
    coverage = covered / total if total else 0.0

    if not claims:
        status = "HOLD_EMPTY_DRAFT"
    elif unsupported:
        status = "HOLD_UNSOURCED"
    elif scope:
        status = "HOLD_SOURCE_SCOPE"
    elif visibility:
        status = "HOLD_VISIBILITY"
    elif coverage == 1.0:
        status = "PASS_GROUNDED"
    else:
        status = "HOLD_GROUNDING_GAP"

    payload = {
        "status": status,
        "substantive_claims": len(claims),
        "supported_claims": len(supported),
        "weighted_grounding_coverage": coverage,
        "unsupported_claim_ids": tuple(sorted(unsupported)),
        "source_scope_violation_claim_ids": tuple(sorted(scope)),
        "visibility_violation_claim_ids": tuple(sorted(visibility)),
        "authority_granted": False,
        "scientific_pass": False,
    }
    return PublicSafeDraftReceipt(**payload, digest=_digest(payload))
