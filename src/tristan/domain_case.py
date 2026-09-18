from __future__ import annotations

from dataclasses import asdict, dataclass

from .anti_corpus import AlternativeCandidate, anti_corpus_decision
from .mission_queue import Mission, next_mission, rank_missions


@dataclass(frozen=True)
class DomainClaimTemplate:
    claim_id: str
    statement: str
    status: str
    witness: str
    evidence_required: tuple[str, ...]
    assumptions: tuple[str, ...] = ()
    validity_domain: str = ""

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.claim_id.strip():
            errors.append("claim_id required")
        if not self.statement.strip():
            errors.append("statement required")
        if not self.witness.strip():
            errors.append("witness required")
        if not self.evidence_required:
            errors.append("evidence_required required")
        if self.status not in {"UNKNOWN", "ACTIVE", "FORMALIZED", "TESTABLE"}:
            errors.append("public domain template may not self-promote beyond TESTABLE")
        return errors


@dataclass(frozen=True)
class DomainCase:
    domain: str
    scope: str
    claims: tuple[DomainClaimTemplate, ...]
    challengers: tuple[AlternativeCandidate, ...]
    missions: tuple[Mission, ...]
    boundaries: tuple[str, ...]

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.domain.strip():
            errors.append("domain required")
        if not self.scope.strip():
            errors.append("scope required")
        if not self.claims:
            errors.append("claims required")
        for claim in self.claims:
            errors.extend(f"{claim.claim_id}: {e}" for e in claim.validate())
        for challenger in self.challengers:
            errors.extend(f"{challenger.candidate_id}: {e}" for e in challenger.validate())
        for mission in self.missions:
            errors.extend(f"{mission.mission_id}: {e}" for e in mission.validate())
        if not self.boundaries:
            errors.append("boundaries required")
        return errors

    def compile(self) -> dict:
        errors = self.validate()
        anti = anti_corpus_decision(list(self.challengers))
        ranked = rank_missions(list(self.missions))
        decision = next_mission(list(self.missions))
        return {
            "domain": self.domain,
            "scope": self.scope,
            "status": "HOLD_INVALID_DOMAIN_CASE" if errors else "PROVISIONAL_DOMAIN_CASE",
            "errors": errors,
            "claims": [asdict(c) for c in self.claims],
            "anti_corpus": anti,
            "missions": [m.to_dict() for m in ranked],
            "next_mission_id": decision.next_mission_id,
            "boundaries": list(self.boundaries),
            "scientific_pass": False,
        }
