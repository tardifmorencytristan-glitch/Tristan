from __future__ import annotations

from dataclasses import dataclass, asdict, field
from hashlib import sha256
import json
from typing import Any


@dataclass
class TransformationReceipt:
    transform_id: str
    input_ids: list[str]
    output_ids: list[str]
    preserved_invariants: list[str] = field(default_factory=list)
    losses: list[str] = field(default_factory=list)
    verifier: str = ""
    status: str = "PROVISIONAL"
    parent_receipts: list[str] = field(default_factory=list)

    def canonical_payload(self) -> dict[str, Any]:
        return asdict(self)

    def digest(self) -> str:
        payload = json.dumps(self.canonical_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return sha256(payload.encode("utf-8")).hexdigest()


def receipt_from_transition(transform_id: str, inputs: list[dict], outputs: list[dict], *, preserved=None, losses=None, verifier="") -> TransformationReceipt:
    return TransformationReceipt(
        transform_id=transform_id,
        input_ids=[x["id"] for x in inputs],
        output_ids=[x["id"] for x in outputs],
        preserved_invariants=list(preserved or []),
        losses=list(losses or []),
        verifier=verifier,
    )
