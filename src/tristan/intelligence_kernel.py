from __future__ import annotations

from dataclasses import asdict, dataclass, replace

from .jarvis_ir import ClaimIR, ExperimentIR
from .model_tournament import ModelCandidate
from .prediction_ledger import PredictionLedger
from .scientific_connectors import build_source_plan


@dataclass(frozen=True)
class CompiledIntelligenceMission:
    schema_version: str
    intent: str
    claim: dict
    prediction_record: dict
    experiment: dict
    model_candidates: tuple[dict, ...]
    scientific_source_plan: dict
    adversarial_roles: tuple[str, ...]
    status: str
    scientific_pass: bool
    authority_granted: bool
    errors: tuple[str, ...]
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def _prediction_text(claim: ClaimIR) -> str:
    observables = ", ".join(claim.predicted_observables)
    return f"{claim.statement} | predicted_observables=[{observables}]"


def compile_intelligence_mission(
    claim: ClaimIR,
    intent: str,
    ledger: PredictionLedger,
) -> CompiledIntelligenceMission:
    errors = list(claim.validate())
    if not claim.predicted_observables:
        errors.append("predicted_observables required before scientific retrieval")

    prediction_record = None
    compiled_claim = claim
    if not errors:
        prediction_record = ledger.freeze(
            claim.claim_id,
            _prediction_text(claim),
            tuple(claim.predicted_observables),
        )
        compiled_claim = replace(
            claim,
            witness=f"prediction-ledger:{prediction_record.record_hash}",
            status="TESTABLE",
        )

    candidates = [ModelCandidate("NULL", "Null or matched-control model", is_null=True)]
    for model_id in claim.competing_models:
        candidates.append(ModelCandidate(model_id, f"Competing model {model_id}"))

    experiment = ExperimentIR(
        experiment_id=f"EXP-{claim.claim_id}",
        hypothesis_claim_id=claim.claim_id,
        alternative_claim_ids=tuple(model.model_id for model in candidates),
        controls=("matched-null-or-baseline",),
        observables=tuple(claim.predicted_observables),
        success_criteria=("predeclared metric separates at least one model from null",),
        failure_criteria=("claim prediction is not distinguishable under preregistered test",),
        stop_rules=("stop on invalid provenance, missing uncertainty, or scope mismatch",),
    )
    errors.extend(experiment.validate())

    source_plan = build_source_plan(intent)
    status = "READY_FOR_ADVERSARIAL_EXECUTION" if not errors else "HOLD"

    return CompiledIntelligenceMission(
        schema_version="tristan-intelligence-omega-v1",
        intent=intent,
        claim=compiled_claim.to_dict(),
        prediction_record=prediction_record.to_dict() if prediction_record else {},
        experiment=experiment.to_dict(),
        model_candidates=tuple(asdict(candidate) for candidate in candidates),
        scientific_source_plan=source_plan,
        adversarial_roles=("DEFENDER", "FALSIFIER", "INDEPENDENT_REPLICATOR"),
        status=status,
        scientific_pass=False,
        authority_granted=False,
        errors=tuple(errors),
        boundaries=(
            "PredictionFrozen != PredictionConfirmed",
            "SourceSelection != DataRetrieved",
            "DataRetrieved != CorrectAnalysis",
            "Simulation != Measurement",
            "Consensus != Evidence",
            "ModelOrdering != ScientificTruth",
            "MissionCompiled != Authorization",
            "NO_ACTION is admissible",
        ),
    )
