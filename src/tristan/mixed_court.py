from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CourtCase:
    case_id: str
    truth_positive: bool
    predicted_positive: bool
    mechanism_correct: bool | None = None


@dataclass(frozen=True)
class CourtMetrics:
    tp: int
    tn: int
    fp: int
    fn: int
    precision: float | None
    recall: float | None
    fpr: float | None
    fnr: float | None
    mechanism_accuracy: float | None


def evaluate_court(cases: list[CourtCase]) -> CourtMetrics:
    tp = sum(c.truth_positive and c.predicted_positive for c in cases)
    tn = sum((not c.truth_positive) and (not c.predicted_positive) for c in cases)
    fp = sum((not c.truth_positive) and c.predicted_positive for c in cases)
    fn = sum(c.truth_positive and (not c.predicted_positive) for c in cases)
    precision = tp / (tp + fp) if (tp + fp) else None
    recall = tp / (tp + fn) if (tp + fn) else None
    fpr = fp / (fp + tn) if (fp + tn) else None
    fnr = fn / (fn + tp) if (fn + tp) else None
    mechanisms = [c.mechanism_correct for c in cases if c.predicted_positive and c.mechanism_correct is not None]
    mechanism_accuracy = sum(bool(x) for x in mechanisms) / len(mechanisms) if mechanisms else None
    return CourtMetrics(tp, tn, fp, fn, precision, recall, fpr, fnr, mechanism_accuracy)
