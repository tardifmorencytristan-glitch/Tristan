from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CapabilityProof:
    capability: str
    evidence_ids: tuple[str, ...]
    scope: tuple[str, ...]

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.capability.strip():
            errors.append("capability required")
        if not self.evidence_ids:
            errors.append("evidence_ids required")
        if not self.scope:
            errors.append("scope required")
        return errors


@dataclass(frozen=True)
class ProofCarryingCapabilityLease:
    plan_digest: str
    holder_id: str
    proofs: tuple[CapabilityProof, ...]
    authority_granted: bool = False

    def validate(
        self,
        *,
        plan_digest: str,
        required_capabilities: tuple[str, ...],
        target_scope: tuple[str, ...],
    ) -> list[str]:
        errors: list[str] = []
        if self.plan_digest != plan_digest:
            errors.append("plan digest mismatch")
        if not self.holder_id.strip():
            errors.append("holder_id required")

        proof_map = {proof.capability: proof for proof in self.proofs}
        for proof in self.proofs:
            errors.extend(proof.validate())

        for capability in required_capabilities:
            proof = proof_map.get(capability)
            if proof is None:
                errors.append(f"missing proof for capability: {capability}")
                continue
            if not set(target_scope) <= set(proof.scope):
                errors.append(f"scope mismatch for capability: {capability}")

        return errors

    def to_dict(self) -> dict:
        return asdict(self)
