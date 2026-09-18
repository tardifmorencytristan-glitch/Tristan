from __future__ import annotations

from dataclasses import asdict, dataclass

from .jarvis_ir import TransformationIR


@dataclass(frozen=True)
class MutationCandidate:
    mutation_id: str
    transformation: TransformationIR
    frozen_retests: tuple[str, ...]
    baseline_score: float
    expected_score: float
    complexity_delta: float
    evidence_gain: float
    reversible: bool = True

    def validate(self) -> list[str]:
        errors = self.transformation.validate()
        if not self.mutation_id.strip():
            errors.append("mutation_id required")
        if not self.frozen_retests:
            errors.append("frozen_retests required")
        if self.complexity_delta < 0:
            errors.append("complexity_delta must be non-negative")
        if self.evidence_gain < 0:
            errors.append("evidence_gain must be non-negative")
        if not self.reversible:
            errors.append("mutation must be reversible in this layer")
        return errors

    @property
    def expected_net_gain(self) -> float:
        return (
            self.expected_score
            - self.baseline_score
            + self.evidence_gain
            - self.complexity_delta
            - self.transformation.evidence_debt
            - self.transformation.risk
        )


@dataclass(frozen=True)
class MutationReceipt:
    mutation_id: str | None
    expected_net_gain: float
    status: str
    executable: bool
    promotion_authority: bool
    rollback: str | None
    frozen_retests: tuple[str, ...]
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def select_mutation(
    candidates: tuple[MutationCandidate, ...],
    *,
    minimum_net_gain: float = 0.0,
) -> MutationReceipt:
    if minimum_net_gain < 0:
        raise ValueError("minimum_net_gain must be non-negative")
    for candidate in candidates:
        errors = candidate.validate()
        if errors:
            raise ValueError("; ".join(errors))

    viable = [c for c in candidates if c.expected_net_gain > minimum_net_gain]
    if not viable:
        return MutationReceipt(
            mutation_id=None,
            expected_net_gain=0.0,
            status="NO_ACTION",
            executable=False,
            promotion_authority=False,
            rollback=None,
            frozen_retests=(),
            boundaries=(
                "NoMeasuredGain -> NO_ACTION",
                "GeneratedMutation != VerifiedMutation",
                "SelfModification != SelfApproval",
            ),
        )

    best = max(viable, key=lambda c: (c.expected_net_gain, c.mutation_id))
    return MutationReceipt(
        mutation_id=best.mutation_id,
        expected_net_gain=best.expected_net_gain,
        status="CANDIDATE_MUTATION_REQUIRES_RETEST",
        executable=False,
        promotion_authority=False,
        rollback=best.transformation.rollback,
        frozen_retests=best.frozen_retests,
        boundaries=(
            "MutationCandidate != ExecutionAuthority",
            "MutationCandidate != Promotion",
            "FrozenRetestRequired",
            "RollbackRequired",
            "SelfModification != SelfApproval",
        ),
    )
