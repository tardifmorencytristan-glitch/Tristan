from __future__ import annotations

from dataclasses import asdict, dataclass


EVIDENCE_STATUSES = {
    "NOT_TESTABLE",
    "NO_SENSITIVITY",
    "INCONCLUSIVE",
    "CONSISTENT",
    "SUPPORTED_WITHIN_DOMAIN",
    "TENSION",
    "EXCLUDED_REGION",
    "FALSIFIED",
    "REPLICATION_REQUIRED",
}


@dataclass(frozen=True)
class EvidenceContract:
    claim_id: str
    reference_model: str
    candidate_model: str
    observables: tuple[str, ...]
    datasets: tuple[str, ...]
    forward_model: str
    selection_function: str
    uncertainty_model: str
    statistical_tests: tuple[str, ...]
    falsification_criteria: tuple[str, ...]
    preregistered: bool = False
    multiplicity_control: str = "required"
    holdout_required: bool = True
    replication_required: bool = True

    def validate(self) -> list[str]:
        errors: list[str] = []
        for name, value in (
            ("claim_id", self.claim_id),
            ("reference_model", self.reference_model),
            ("candidate_model", self.candidate_model),
            ("forward_model", self.forward_model),
            ("selection_function", self.selection_function),
            ("uncertainty_model", self.uncertainty_model),
        ):
            if not value.strip():
                errors.append(f"{name} required")
        if not self.observables:
            errors.append("observables required")
        if not self.datasets:
            errors.append("datasets required")
        if not self.statistical_tests:
            errors.append("statistical_tests required")
        if not self.falsification_criteria:
            errors.append("falsification_criteria required")
        if self.multiplicity_control not in {"required", "not_applicable"}:
            errors.append("multiplicity_control must be required or not_applicable")
        return errors

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class EvidenceReceipt:
    contract: EvidenceContract
    status: str
    result_summary: str
    uncertainty_summary: str
    provenance: tuple[str, ...]
    independent_replication_count: int = 0
    data_retrieved: bool = False
    analysis_executed: bool = False

    def validate(self) -> list[str]:
        errors = self.contract.validate()
        if self.status not in EVIDENCE_STATUSES:
            errors.append(f"unsupported evidence status: {self.status}")
        if not self.result_summary.strip():
            errors.append("result_summary required")
        if not self.uncertainty_summary.strip():
            errors.append("uncertainty_summary required")
        if not self.provenance:
            errors.append("provenance required")
        if self.independent_replication_count < 0:
            errors.append("independent_replication_count must be non-negative")
        return errors

    def to_dict(self) -> dict:
        return asdict(self)


def compile_evidence_contract(
    *,
    claim_id: str,
    datasets: tuple[str, ...],
    observables: tuple[str, ...],
    reference_model: str = "DECLARED_REFERENCE_MODEL",
    candidate_model: str = "DECLARED_CANDIDATE_MODEL",
) -> EvidenceContract:
    return EvidenceContract(
        claim_id=claim_id,
        reference_model=reference_model,
        candidate_model=candidate_model,
        observables=observables,
        datasets=datasets,
        forward_model="instrument-response-and-calibration-required",
        selection_function="explicit-selection-function-required",
        uncertainty_model="statistical-plus-systematic-nuisance-model-required",
        statistical_tests=(
            "likelihood-or-equivalent-goodness-of-fit",
            "posterior-or-bootstrap-predictive-check",
            "holdout-or-independent-dataset-check",
        ),
        falsification_criteria=(
            "predeclared-observable-mismatch-outside-uncertainty",
            "parameter-region-exclusion-with-calibrated-error-control",
            "failure-to-replicate-when-replication-is-required",
        ),
        preregistered=False,
        multiplicity_control="required",
        holdout_required=True,
        replication_required=True,
    )


def blank_evidence_receipt(contract: EvidenceContract) -> EvidenceReceipt:
    return EvidenceReceipt(
        contract=contract,
        status="INCONCLUSIVE",
        result_summary="No data analysis executed by this planning layer.",
        uncertainty_summary="Uncertainty remains unquantified until a bounded analysis is executed.",
        provenance=("jarvis-r6-planning-layer",),
        independent_replication_count=0,
        data_retrieved=False,
        analysis_executed=False,
    )
