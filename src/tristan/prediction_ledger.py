from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json


@dataclass(frozen=True)
class PredictionRecord:
    claim_id: str
    prediction: str
    scope: tuple[str, ...]
    created_at: str
    previous_hash: str
    record_hash: str

    def to_dict(self) -> dict:
        return asdict(self)


def _canonical_payload(
    claim_id: str,
    prediction: str,
    scope: tuple[str, ...],
    created_at: str,
    previous_hash: str,
) -> str:
    return json.dumps(
        {
            "claim_id": claim_id,
            "prediction": prediction,
            "scope": list(scope),
            "created_at": created_at,
            "previous_hash": previous_hash,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def _hash_payload(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class PredictionLedger:
    """Append-only hash-chained preregistration ledger.

    The ledger freezes a prediction before retrieval/analysis.  It is evidence
    of preregistration integrity, not evidence that the prediction is true.
    """

    def __init__(self) -> None:
        self._records: list[PredictionRecord] = []

    def freeze(
        self,
        claim_id: str,
        prediction: str,
        scope: tuple[str, ...],
        *,
        created_at: str | None = None,
    ) -> PredictionRecord:
        if not claim_id.strip():
            raise ValueError("claim_id required")
        if not prediction.strip():
            raise ValueError("prediction required")
        if not scope:
            raise ValueError("scope required")

        timestamp = created_at or datetime.now(timezone.utc).isoformat()
        previous_hash = self._records[-1].record_hash if self._records else "GENESIS"
        payload = _canonical_payload(
            claim_id,
            prediction,
            tuple(scope),
            timestamp,
            previous_hash,
        )
        record = PredictionRecord(
            claim_id=claim_id,
            prediction=prediction,
            scope=tuple(scope),
            created_at=timestamp,
            previous_hash=previous_hash,
            record_hash=_hash_payload(payload),
        )
        self._records.append(record)
        return record

    def records(self) -> tuple[PredictionRecord, ...]:
        return tuple(self._records)

    def verify(self) -> bool:
        previous_hash = "GENESIS"
        for record in self._records:
            if record.previous_hash != previous_hash:
                return False
            payload = _canonical_payload(
                record.claim_id,
                record.prediction,
                record.scope,
                record.created_at,
                record.previous_hash,
            )
            if _hash_payload(payload) != record.record_hash:
                return False
            previous_hash = record.record_hash
        return True
