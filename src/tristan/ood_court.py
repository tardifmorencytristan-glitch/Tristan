from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class OODMission:
    mission_id: str
    domain: str
    signature: str
    required_capabilities: tuple[str, ...]

    def validate(self) -> list[str]:
        errors: list[str] = []
        for name, value in (
            ("mission_id", self.mission_id),
            ("domain", self.domain),
            ("signature", self.signature),
        ):
            if not value.strip():
                errors.append(f"{name} required")
        if not self.required_capabilities:
            errors.append("required_capabilities required")
        return errors


@dataclass(frozen=True)
class OODResult:
    candidate_id: str
    mission_id: str
    score: float
    success: bool
    uncertainty: float = 0.0

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.candidate_id.strip():
            errors.append("candidate_id required")
        if not self.mission_id.strip():
            errors.append("mission_id required")
        if not 0.0 <= self.uncertainty <= 1.0:
            errors.append("uncertainty must be in [0,1]")
        return errors


@dataclass(frozen=True)
class OODCourtReceipt:
    candidate_id: str
    mission_count: int
    success_rate: float
    mean_score: float
    mean_uncertainty: float
    overlap_detected: bool
    status: str
    transfer_evidence: bool
    promotion_authority: bool
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def evaluate_ood_candidate(
    candidate_id: str,
    missions: tuple[OODMission, ...],
    results: tuple[OODResult, ...],
    *,
    training_signatures: tuple[str, ...] = (),
    min_success_rate: float = 0.8,
    max_mean_uncertainty: float = 0.25,
) -> OODCourtReceipt:
    if not candidate_id.strip():
        raise ValueError("candidate_id required")
    if not missions:
        raise ValueError("OOD missions required")
    if not 0.0 <= min_success_rate <= 1.0:
        raise ValueError("min_success_rate must be in [0,1]")

    for mission in missions:
        errors = mission.validate()
        if errors:
            raise ValueError("; ".join(errors))

    mission_ids = {mission.mission_id for mission in missions}
    candidate_rows = [
        result
        for result in results
        if result.candidate_id == candidate_id and result.mission_id in mission_ids
    ]
    for result in candidate_rows:
        errors = result.validate()
        if errors:
            raise ValueError("; ".join(errors))

    overlap = bool({mission.signature for mission in missions} & set(training_signatures))
    if overlap:
        return OODCourtReceipt(
            candidate_id=candidate_id,
            mission_count=len(missions),
            success_rate=0.0,
            mean_score=0.0,
            mean_uncertainty=1.0,
            overlap_detected=True,
            status="HOLD_TRAINING_OVERLAP",
            transfer_evidence=False,
            promotion_authority=False,
            boundaries=("TrainingOverlap != OOD", "OODReceipt != PromotionAuthority"),
        )

    if {row.mission_id for row in candidate_rows} != mission_ids:
        return OODCourtReceipt(
            candidate_id=candidate_id,
            mission_count=len(missions),
            success_rate=0.0,
            mean_score=0.0,
            mean_uncertainty=1.0,
            overlap_detected=False,
            status="HOLD_INCOMPLETE_OOD_RESULTS",
            transfer_evidence=False,
            promotion_authority=False,
            boundaries=("IncompleteOOD != TransferEvidence",),
        )

    n = len(candidate_rows)
    success_rate = sum(1 for row in candidate_rows if row.success) / n
    mean_score = sum(row.score for row in candidate_rows) / n
    mean_uncertainty = sum(row.uncertainty for row in candidate_rows) / n
    eligible = success_rate >= min_success_rate and mean_uncertainty <= max_mean_uncertainty

    return OODCourtReceipt(
        candidate_id=candidate_id,
        mission_count=n,
        success_rate=success_rate,
        mean_score=mean_score,
        mean_uncertainty=mean_uncertainty,
        overlap_detected=False,
        status="OOD_TRANSFER_EVIDENCE" if eligible else "OOD_RESIDUAL",
        transfer_evidence=eligible,
        promotion_authority=False,
        boundaries=(
            "OODSuccess != UniversalGeneralization",
            "TransferEvidence != TransferAuthority",
            "OODReceipt != ScientificPASS",
        ),
    )
