from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CrystalCandidate:
    crystal_id: str
    spec_ref: str
    implementation_ref: str
    tests: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    failure_ids: tuple[str, ...]
    book0_digest: str
    interfaces: tuple[str, ...]
    benchmarks: tuple[str, ...] = ()
    oak_status: str = "UNKNOWN"

    def readiness_errors(self) -> list[str]:
        errors: list[str] = []
        if not self.crystal_id.strip():
            errors.append("crystal_id required")
        if not self.spec_ref.strip():
            errors.append("spec_ref required")
        if not self.implementation_ref.strip():
            errors.append("implementation_ref required")
        if not self.tests:
            errors.append("tests required")
        if not self.evidence_ids:
            errors.append("evidence required")
        if not self.book0_digest.strip():
            errors.append("BOOK0 digest required")
        if not self.interfaces:
            errors.append("interfaces required")
        if self.oak_status in {"UNKNOWN", "ACTIVE"}:
            errors.append("OAK status too immature for engineering crystal")
        return errors


@dataclass(frozen=True)
class CrystalReceipt:
    crystal_id: str
    status: str
    errors: tuple[str, ...]
    oak_status: str
    scientific_pass: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


def compile_crystal(candidate: CrystalCandidate) -> CrystalReceipt:
    errors = tuple(candidate.readiness_errors())
    return CrystalReceipt(
        crystal_id=candidate.crystal_id,
        status="ENGINEERING_CRYSTAL_READY" if not errors else "HOLD",
        errors=errors,
        oak_status=candidate.oak_status,
        scientific_pass=False,
    )
