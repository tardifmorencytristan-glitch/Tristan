from __future__ import annotations

from dataclasses import dataclass, asdict, field
from hashlib import sha256
import json
from typing import Any


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class TransformationReceipt:
    transform_id: str
    input_ids: list[str]
    output_ids: list[str]
    input_hashes: list[str] = field(default_factory=list)
    output_hashes: list[str] = field(default_factory=list)
    preserved_invariants: list[str] = field(default_factory=list)
    losses: list[str] = field(default_factory=list)
    verifier: str = ""
    operator_version: str = ""
    authority: str = ""
    cost: float = 0.0
    risk: float = 0.0
    status: str = "PROVISIONAL"
    parent_receipts: list[str] = field(default_factory=list)

    def canonical_payload(self) -> dict[str, Any]:
        return asdict(self)

    def digest(self) -> str:
        return canonical_hash(self.canonical_payload())

    def validate(self) -> list[str]:
        errors = []
        if not self.transform_id:
            errors.append("transform_id required")
        if len(self.input_ids) != len(self.input_hashes):
            errors.append("input_ids/input_hashes length mismatch")
        if len(self.output_ids) != len(self.output_hashes):
            errors.append("output_ids/output_hashes length mismatch")
        for digest in self.input_hashes + self.output_hashes:
            if len(digest) != 64:
                errors.append("artifact hash must be SHA-256 hex")
        return errors


def receipt_from_transition(transform_id: str, inputs: list[dict], outputs: list[dict], *, preserved=None, losses=None, verifier="", operator_version="", authority="", cost=0.0, risk=0.0) -> TransformationReceipt:
    return TransformationReceipt(
        transform_id=transform_id,
        input_ids=[x["id"] for x in inputs],
        output_ids=[x["id"] for x in outputs],
        input_hashes=[canonical_hash(x) for x in inputs],
        output_hashes=[canonical_hash(x) for x in outputs],
        preserved_invariants=list(preserved or []),
        losses=list(losses or []),
        verifier=verifier,
        operator_version=operator_version,
        authority=authority,
        cost=float(cost),
        risk=float(risk),
    )
