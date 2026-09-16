from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Callable


@dataclass(frozen=True)
class RoundTripReceipt:
    source_type: str
    intermediate_type: str
    source_invariants: dict[str, Any]
    recovered_invariants: dict[str, Any]
    mismatches: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.mismatches

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["passed"] = self.passed
        return d


def compare_invariants(before: dict[str, Any], after: dict[str, Any], keys: list[str]) -> tuple[str, ...]:
    return tuple(k for k in keys if before.get(k) != after.get(k))


def verify_round_trip(
    source: dict[str, Any],
    forward: Callable[[dict[str, Any]], dict[str, Any]],
    reverse: Callable[[dict[str, Any]], dict[str, Any]],
    invariant_keys: list[str],
    source_type: str,
    intermediate_type: str,
) -> RoundTripReceipt:
    mid = forward(source)
    recovered = reverse(mid)
    before = {k: source.get(k) for k in invariant_keys}
    after = {k: recovered.get(k) for k in invariant_keys}
    return RoundTripReceipt(
        source_type=source_type,
        intermediate_type=intermediate_type,
        source_invariants=before,
        recovered_invariants=after,
        mismatches=compare_invariants(before, after, invariant_keys),
    )
