from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Failure:
    id: str
    hypothesis: str
    conditions: str
    prediction: str
    observed: str
    residual: str
    reusable_constraint: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


class FailureMemory:
    def __init__(self, failures: list[Failure] | None = None) -> None:
        self._failures = list(failures or [])

    def add(self, failure: Failure) -> None:
        if any(existing.id == failure.id for existing in self._failures):
            raise ValueError(f"duplicate failure id: {failure.id}")
        self._failures.append(failure)

    def all(self) -> tuple[Failure, ...]:
        return tuple(self._failures)

    def constraints(self) -> tuple[str, ...]:
        return tuple(f.reusable_constraint for f in self._failures if f.reusable_constraint)
