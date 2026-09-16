from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from .context import compile_context
from .registry import Registry


@dataclass(frozen=True)
class RunReceipt:
    schema_version: str
    intent: str
    intent_sha256: str
    context: dict
    residuals: tuple[str, ...]
    decision: str
    epistemic_status: str
    generated_at: str

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "intent": self.intent,
            "intent_sha256": self.intent_sha256,
            "context": self.context,
            "residuals": list(self.residuals),
            "decision": self.decision,
            "epistemic_status": self.epistemic_status,
            "generated_at": self.generated_at,
        }


def run_intent(intent: str, registry: Registry, limit: int = 8) -> RunReceipt:
    if not intent.strip():
        raise ValueError("intent must not be empty")
    context = compile_context(intent, registry, limit=limit)
    residuals = []
    if not context.selected_ids:
        residuals.append("NO_RELEVANT_REGISTERED_OBJECT")
    else:
        selected = [registry.require(object_id) for object_id in context.selected_ids]
        if not any(obj.evidence_urls for obj in selected):
            residuals.append("NO_SELECTED_EVIDENCE_URL")
        if any(obj.status in {"IDEA", "PROVISIONAL", "HOLD", "RESIDUAL"} for obj in selected):
            residuals.append("SELECTED_CONTEXT_CONTAINS_UNPROMOTED_OBJECTS")

    decision = "SEARCH_OR_CREATE_BOUNDED_CANDIDATE" if residuals else "REUSE_SELECTED_CONTEXT"
    digest = hashlib.sha256(intent.encode("utf-8")).hexdigest()
    return RunReceipt(
        schema_version="0.1",
        intent=intent,
        intent_sha256=digest,
        context=context.to_dict(),
        residuals=tuple(residuals),
        decision=decision,
        epistemic_status="PROVISIONAL_ENGINEERING_RECEIPT",
        generated_at=datetime.now(timezone.utc).isoformat(),
    )


def stable_receipt_bytes(receipt: RunReceipt) -> bytes:
    payload = receipt.to_dict().copy()
    payload["generated_at"] = "<runtime>"
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
