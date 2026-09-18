from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Book0Seed:
    seed_id: str
    critical_invariants: tuple[str, ...]
    dependencies: tuple[str, ...]
    tests: tuple[str, ...]
    failure_refs: tuple[str, ...] = ()
    regenerator: str = ""

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.seed_id.strip():
            errors.append("seed_id required")
        if not self.critical_invariants:
            errors.append("critical invariants required")
        if not self.tests:
            errors.append("tests required")
        if not self.regenerator.strip():
            errors.append("regenerator required")
        return errors

    def semantic_payload(self) -> dict:
        return {
            "seed_id": self.seed_id,
            "critical_invariants": sorted(self.critical_invariants),
            "dependencies": sorted(self.dependencies),
            "tests": sorted(self.tests),
            "failure_refs": sorted(self.failure_refs),
            "regenerator": self.regenerator,
        }

    def digest(self) -> str:
        raw = json.dumps(self.semantic_payload(), sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class RegenerationCheck:
    expected_digest: str
    observed_digest: str

    @property
    def valid(self) -> bool:
        return self.expected_digest == self.observed_digest


def compare_seeds(expected: Book0Seed, observed: Book0Seed) -> RegenerationCheck:
    return RegenerationCheck(expected.digest(), observed.digest())
