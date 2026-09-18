from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CalibrationSample:
    confidence: float
    correct: bool
    domain: str = "general"

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not 0.0 <= self.confidence <= 1.0:
            errors.append("confidence must be in [0,1]")
        if not self.domain.strip():
            errors.append("domain required")
        return errors


@dataclass(frozen=True)
class CalibrationReport:
    sample_count: int
    brier_score: float
    mean_confidence: float
    empirical_accuracy: float
    calibration_gap: float
    status: str

    def to_dict(self) -> dict:
        return asdict(self)


def calibration_report(samples: tuple[CalibrationSample, ...]) -> CalibrationReport:
    if not samples:
        raise ValueError("samples required")
    for sample in samples:
        errors = sample.validate()
        if errors:
            raise ValueError("; ".join(errors))

    n = len(samples)
    brier = sum(
        (sample.confidence - (1.0 if sample.correct else 0.0)) ** 2
        for sample in samples
    ) / n
    mean_confidence = sum(sample.confidence for sample in samples) / n
    accuracy = sum(1 for sample in samples if sample.correct) / n
    gap = abs(mean_confidence - accuracy)

    return CalibrationReport(
        sample_count=n,
        brier_score=brier,
        mean_confidence=mean_confidence,
        empirical_accuracy=accuracy,
        calibration_gap=gap,
        status="CALIBRATION_MEASURED",
    )
