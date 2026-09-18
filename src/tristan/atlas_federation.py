from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any

from .mission_queue import Mission, next_mission, rank_missions


ATLAS_FEDERATION_BOUNDARIES = (
    "FederatedPointer != LoadedEvidence",
    "SourceAvailability != ScientificSupport",
    "DuplicateName != DuplicateContent",
    "PrivateSource != PublicPayload",
    "MissionPriority != ScientificImportance",
    "AtlasProjection != ScientificRanking",
    "TopK != Truth",
    "NO_ACTION is admissible",
)


@dataclass(frozen=True)
class FederatedSource:
    source_id: str
    family: str
    kind: str
    visibility: str
    materialized: bool
    exact_version_bound: bool
    duplicate_family_observed: bool = False
    observed_at: str = "2026-09-18"
    note: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class AtlasFederationReceipt:
    schema_version: str
    intent: str
    sources: tuple[dict, ...]
    missions: tuple[dict, ...]
    top16: tuple[str, ...]
    top64: tuple[str, ...]
    top256: tuple[str, ...]
    next_action: str
    epistemic_status: str
    scientific_pass: bool
    authority_granted: bool
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def _slug(value: str) -> str:
    cooked = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return cooked or "source"


def _registry_sources(registry: Any) -> list[FederatedSource]:
    out: list[FederatedSource] = []
    for obj in registry.all():
        tags = {str(tag).lower() for tag in getattr(obj, "tags", ())}
        if "drive" in tags:
            family = "drive-registry"
        elif "git" in tags or "repository" in tags:
            family = "git-registry"
        elif getattr(obj, "kind", "") == "registry":
            family = "context-registry"
        else:
            family = f"registry-{getattr(obj, 'kind', 'object')}"
        out.append(FederatedSource(
            source_id=getattr(obj, "id", _slug(getattr(obj, "title", "registry-object"))),
            family=family,
            kind=getattr(obj, "kind", "object"),
            visibility="public-or-federated",
            materialized=bool(getattr(obj, "evidence_urls", ()))
            or getattr(obj, "status", "") == "VERIFIED_ENGINEERING",
            exact_version_bound=bool(
                getattr(obj, "exact_url", None) or getattr(obj, "version_hash", None)
            ),
            duplicate_family_observed=False,
            note="Derived from the canonical public registry; no external payload copied.",
        ))
    return out


def _observed_connector_sources() -> list[FederatedSource]:
    # Safe descriptors only. They intentionally omit private Drive IDs/URLs and payloads.
    return [
        FederatedSource(
            "github-public-kstar",
            "git-public-kstar",
            "repository",
            "public",
            True,
            True,
            note="Current public Tristan kernel.",
        ),
        FederatedSource(
            "github-historical-root",
            "git-historical",
            "repository",
            "public-or-federated",
            False,
            False,
            note="Historical Tristan repository family; bind exact snapshots per task.",
        ),
        FederatedSource(
            "github-private-root",
            "git-private",
            "repository",
            "private",
            False,
            False,
            note="Private Git source remains federated; never copied to public output by this layer.",
        ),
        FederatedSource(
            "drive-context-bootstrap",
            "drive-bootstrap",
            "document-family",
            "private-or-shared",
            True,
            False,
            note="Context bootstrap observed through the connected Drive.",
        ),
        FederatedSource(
            "drive-atlas-family",
            "drive-atlas",
            "document-family",
            "private-or-shared",
            False,
            False,
            True,
            note="Multiple Atlas documents observed; canonicalization required before treating names as identities.",
        ),
        FederatedSource(
            "drive-tfuga-family",
            "drive-tfuga",
            "document-family",
            "private-or-shared",
            False,
            False,
            True,
            note="TFUGA audit, best-of, archive and intake families observed.",
        ),
        FederatedSource(
            "drive-hgfm-family",
            "drive-hgfm",
            "document-family",
            "private-or-shared",
            False,
            False,
            True,
            note="HGFM BOOK0, morphology and verification-receipt families observed.",
        ),
        FederatedSource(
            "drive-jarvis-family",
            "drive-jarvis",
            "document-family",
            "private-or-shared",
            False,
            False,
            True,
            note="Jarvis runtime, morphogenesis and receipt families observed.",
        ),
        FederatedSource(
            "drive-omega-math-family",
            "drive-omega-math",
            "document-family",
            "private-or-shared",
            False,
            False,
            True,
            note="Omega mathematical representation/compiler families observed.",
        ),
    ]


def _source_missions(source: FederatedSource) -> list[Mission]:
    sid = _slug(source.source_id)
    missions: list[Mission] = []
    if not source.materialized:
        missions.append(Mission(
            f"M-ATLAS-MATERIALIZE-{sid}",
            source.source_id,
            "MATERIALIZE_BOUNDED_SOURCE",
            "source-provenance-court",
            expected_verified_gain=3.0,
            debt_reduction=4.0,
            reuse_potential=2.0,
            cost=1.0,
            risk=0.2,
        ))
    if not source.exact_version_bound:
        missions.append(Mission(
            f"M-ATLAS-PIN-{sid}",
            source.source_id,
            "BIND_EXACT_VERSION",
            "provenance-version-court",
            expected_verified_gain=2.0,
            debt_reduction=3.0,
            reuse_potential=2.0,
            cost=0.6,
            risk=0.1,
        ))
    if source.duplicate_family_observed:
        missions.append(Mission(
            f"M-ATLAS-DEDUP-{_slug(source.family)}",
            source.source_id,
            "CANONICALIZE_DUPLICATE_FAMILY",
            "content-hash-and-lineage-court",
            expected_verified_gain=2.0,
            debt_reduction=4.0,
            reuse_potential=3.0,
            cost=0.8,
            risk=0.1,
        ))
    if source.visibility in {"private", "private-or-shared"}:
        missions.append(Mission(
            f"M-ATLAS-BOUNDARY-{sid}",
            source.source_id,
            "PRESERVE_PRIVATE_FEDERATION_BOUNDARY",
            "privacy-and-provenance-court",
            expected_verified_gain=1.0,
            debt_reduction=2.0,
            reuse_potential=2.0,
            cost=0.4,
            risk=0.1,
        ))
    return missions


def compile_atlas_federation(intent: str, registry: Any) -> AtlasFederationReceipt:
    merged: dict[str, FederatedSource] = {}
    for source in [*_registry_sources(registry), *_observed_connector_sources()]:
        merged[source.source_id] = source
    sources = tuple(sorted(merged.values(), key=lambda s: (s.family, s.source_id)))

    missions: list[Mission] = []
    for source in sources:
        missions.extend(_source_missions(source))
    ranked = rank_missions(missions)
    decision = next_mission(missions)
    ids = tuple(m.mission_id for m in ranked)

    return AtlasFederationReceipt(
        schema_version="jarvis-atlas-federation-r7",
        intent=intent,
        sources=tuple(s.to_dict() for s in sources),
        missions=tuple(m.to_dict() for m in ranked),
        top16=ids[:16],
        top64=ids[:64],
        top256=ids[:256],
        next_action=decision.next_mission_id,
        epistemic_status="PROVISIONAL_FEDERATION_PLAN",
        scientific_pass=False,
        authority_granted=False,
        boundaries=ATLAS_FEDERATION_BOUNDARIES,
    )
