from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Any, Iterable

from .loss_tensor import LossObservation, LossTensor
from .parser_adapters import ParserComparison, ParserRun, compare_texts, invariant_presence, normalize_text


RECONCILIATION_STATUSES = {
    "CONSENSUS_TEXT",
    "HOLD_DISAGREEMENT",
    "HOLD_MISSING_INVARIANT",
    "HOLD_SOURCE_MISMATCH",
    "ADJUDICATED_EXTERNAL",
}


@dataclass(frozen=True)
class IndependentAdjudication:
    id: str
    accepted_parser_ids: tuple[str, ...]
    provenance: tuple[str, ...]
    authority: str
    scope: str

    def validate(self, available_parser_ids: set[str]) -> list[str]:
        errors: list[str] = []
        if not self.id:
            errors.append("IndependentAdjudication.id required")
        if not self.accepted_parser_ids:
            errors.append("IndependentAdjudication.accepted_parser_ids required")
        unknown = sorted(set(self.accepted_parser_ids) - available_parser_ids)
        if unknown:
            errors.append(f"IndependentAdjudication references unknown parsers: {unknown}")
        if not self.provenance:
            errors.append("IndependentAdjudication.provenance required")
        if not self.authority:
            errors.append("IndependentAdjudication.authority required")
        if not self.scope:
            errors.append("IndependentAdjudication.scope required")
        return errors


@dataclass(frozen=True)
class ReconciliationDecision:
    status: str
    parser_ids: tuple[str, ...]
    accepted_parser_ids: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    missing_invariants: tuple[str, ...] = ()
    source_sha256: str = ""
    max_pairwise_disagreement: float = 0.0
    adjudication_id: str = ""
    authority: str = ""
    scope: str = ""

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.status not in RECONCILIATION_STATUSES:
            errors.append(f"invalid reconciliation status: {self.status}")
        if len(self.parser_ids) < 2:
            errors.append("at least two parser ids required")
        if self.status == "ADJUDICATED_EXTERNAL":
            if not self.accepted_parser_ids:
                errors.append("external adjudication requires accepted parsers")
            if not self.adjudication_id or not self.authority or not self.scope:
                errors.append("external adjudication requires id, authority and scope")
        elif self.accepted_parser_ids:
            errors.append("non-adjudicated decision cannot select parsers")
        if not 0.0 <= self.max_pairwise_disagreement <= 1.0:
            errors.append("max_pairwise_disagreement must be within [0,1]")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "parser_ids": list(self.parser_ids),
            "accepted_parser_ids": list(self.accepted_parser_ids),
            "reasons": list(self.reasons),
            "missing_invariants": list(self.missing_invariants),
            "source_sha256": self.source_sha256,
            "max_pairwise_disagreement": self.max_pairwise_disagreement,
            "adjudication_id": self.adjudication_id,
            "authority": self.authority,
            "scope": self.scope,
        }

    def to_loss_tensor(self, transform_id: str = "parser_reconciliation") -> LossTensor:
        tensor = LossTensor()
        item = "<->".join(self.parser_ids)
        if self.status in {"CONSENSUS_TEXT", "ADJUDICATED_EXTERNAL"}:
            tensor.add(
                LossObservation(
                    transform_id=transform_id,
                    item_id=item,
                    dimension="SEMANTIC",
                    state="PRESERVED" if self.status == "CONSENSUS_TEXT" else "RECONSTRUCTED",
                    severity=0.0 if self.status == "CONSENSUS_TEXT" else self.max_pairwise_disagreement,
                    recoverability=1.0,
                    cause=(
                        "exact normalized parser consensus"
                        if self.status == "CONSENSUS_TEXT"
                        else "bounded external adjudication supplied"
                    ),
                    evidence_ids=(self.adjudication_id,) if self.adjudication_id else (),
                )
            )
            return tensor

        dimension = "PROVENANCE" if self.status == "HOLD_SOURCE_MISMATCH" else "SEMANTIC"
        severity = 1.0 if self.status in {"HOLD_SOURCE_MISMATCH", "HOLD_MISSING_INVARIANT"} else self.max_pairwise_disagreement
        tensor.add(
            LossObservation(
                transform_id=transform_id,
                item_id=item,
                dimension=dimension,
                state="UNKNOWN",
                severity=severity,
                recoverability=0.0,
                cause="; ".join(self.reasons) or self.status,
            )
        )
        return tensor


def _max_pairwise_disagreement(runs: tuple[ParserRun, ...]) -> float:
    maximum = 0.0
    for left, right in combinations(runs, 2):
        comparison = compare_texts(left.parser, left.text, right.parser, right.text)
        maximum = max(maximum, 1.0 - comparison.sequence_similarity)
    return maximum


def reconcile_runs(
    runs: Iterable[ParserRun],
    required_invariants: tuple[str, ...] = (),
    adjudication: IndependentAdjudication | None = None,
) -> ReconciliationDecision:
    frozen = tuple(runs)
    if len(frozen) < 2:
        raise ValueError("at least two parser runs required")
    parser_ids = tuple(run.parser for run in frozen)
    if len(set(parser_ids)) != len(parser_ids):
        raise ValueError("parser ids must be unique within a reconciliation court")

    source_hashes = {run.observation.source_sha256 for run in frozen}
    if len(source_hashes) != 1:
        return ReconciliationDecision(
            status="HOLD_SOURCE_MISMATCH",
            parser_ids=parser_ids,
            reasons=("parser runs are not bound to the same source SHA-256",),
            max_pairwise_disagreement=_max_pairwise_disagreement(frozen),
        )
    source_hash = next(iter(source_hashes))

    missing: list[str] = []
    for run in frozen:
        presence = invariant_presence(run, required_invariants)
        for invariant, present in presence.items():
            if not present:
                missing.append(f"{run.parser}:{invariant}")
    if missing:
        return ReconciliationDecision(
            status="HOLD_MISSING_INVARIANT",
            parser_ids=parser_ids,
            reasons=("one or more required invariants are absent",),
            missing_invariants=tuple(sorted(missing)),
            source_sha256=source_hash,
            max_pairwise_disagreement=_max_pairwise_disagreement(frozen),
        )

    normalized = {normalize_text(run.text) for run in frozen}
    disagreement = _max_pairwise_disagreement(frozen)
    if len(normalized) == 1:
        return ReconciliationDecision(
            status="CONSENSUS_TEXT",
            parser_ids=parser_ids,
            reasons=("all parser outputs are exactly equal after bounded normalization",),
            source_sha256=source_hash,
            max_pairwise_disagreement=0.0,
        )

    if adjudication is None:
        return ReconciliationDecision(
            status="HOLD_DISAGREEMENT",
            parser_ids=parser_ids,
            reasons=("parser outputs disagree and no independent adjudication is supplied",),
            source_sha256=source_hash,
            max_pairwise_disagreement=disagreement,
        )

    errors = adjudication.validate(set(parser_ids))
    if errors:
        raise ValueError(errors)
    return ReconciliationDecision(
        status="ADJUDICATED_EXTERNAL",
        parser_ids=parser_ids,
        accepted_parser_ids=adjudication.accepted_parser_ids,
        reasons=("bounded external adjudication supplied; no parser selected by self-consensus",),
        source_sha256=source_hash,
        max_pairwise_disagreement=disagreement,
        adjudication_id=adjudication.id,
        authority=adjudication.authority,
        scope=adjudication.scope,
    )


def reconcile_recorded_evidence(payload: dict[str, Any]) -> ReconciliationDecision:
    parsers = tuple(sorted(payload.get("executed_parsers", {}).keys()))
    if len(parsers) < 2:
        raise ValueError("recorded evidence requires at least two executed parsers")
    source_hash = str(payload.get("source", {}).get("sha256", ""))
    missing: list[str] = []
    for invariant, statuses in payload.get("selected_invariants", {}).items():
        if not statuses or not all(bool(v) for v in statuses.values()):
            missing.append(invariant)
    comparison = payload.get("comparison", {})
    exact = bool(comparison.get("normalized_exact_text_equal", False))
    similarity = float(comparison.get("sequence_similarity", 0.0))
    disagreement = max(0.0, min(1.0, 1.0 - similarity))
    if missing:
        return ReconciliationDecision(
            status="HOLD_MISSING_INVARIANT",
            parser_ids=parsers,
            reasons=("recorded court is missing one or more selected invariants",),
            missing_invariants=tuple(sorted(missing)),
            source_sha256=source_hash,
            max_pairwise_disagreement=disagreement,
        )
    if exact:
        return ReconciliationDecision(
            status="CONSENSUS_TEXT",
            parser_ids=parsers,
            reasons=("recorded normalized outputs are exactly equal",),
            source_sha256=source_hash,
            max_pairwise_disagreement=0.0,
        )
    return ReconciliationDecision(
        status="HOLD_DISAGREEMENT",
        parser_ids=parsers,
        reasons=("recorded parser outputs disagree and no independent adjudication is present",),
        source_sha256=source_hash,
        max_pairwise_disagreement=disagreement,
    )
