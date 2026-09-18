from __future__ import annotations

from dataclasses import dataclass

from .jarvis_ir import ClaimIR


OAK_STATUSES = {
    "UNKNOWN",
    "ACTIVE",
    "FORMALIZED",
    "TESTABLE",
    "COMPUTATIONALLY_VERIFIED",
    "SIMULATED",
    "PROTOTYPED",
    "MEASURED",
    "REPLICATED",
    "CERTIFIED_MATH",
    "CERTIFIED_SOFTWARE",
    "CERTIFIED_PHYSICS",
    "M-",
    "P0",
}

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "UNKNOWN": {"ACTIVE", "M-", "P0"},
    "ACTIVE": {"FORMALIZED", "TESTABLE", "M-", "P0"},
    "FORMALIZED": {"TESTABLE", "CERTIFIED_MATH", "M-", "P0"},
    "TESTABLE": {"COMPUTATIONALLY_VERIFIED", "SIMULATED", "PROTOTYPED", "M-", "P0"},
    "COMPUTATIONALLY_VERIFIED": {"CERTIFIED_SOFTWARE", "M-", "P0"},
    "SIMULATED": {"PROTOTYPED", "M-", "P0"},
    "PROTOTYPED": {"MEASURED", "M-", "P0"},
    "MEASURED": {"REPLICATED", "M-", "P0"},
    "REPLICATED": {"CERTIFIED_PHYSICS", "M-", "P0"},
    "CERTIFIED_MATH": {"P0"},
    "CERTIFIED_SOFTWARE": {"P0"},
    "CERTIFIED_PHYSICS": {"P0"},
    "M-": {"P0"},
    "P0": set(),
}


@dataclass(frozen=True)
class EvidenceVector:
    formal: bool = False
    computational: bool = False
    simulation: bool = False
    experimental: bool = False
    replication: bool = False
    external: bool = False


def promotion_errors(
    current: str,
    target: str,
    claim: ClaimIR,
    evidence: EvidenceVector,
) -> list[str]:
    errors: list[str] = []
    if current not in OAK_STATUSES:
        errors.append(f"unknown current OAK status: {current}")
        return errors
    if target not in OAK_STATUSES:
        errors.append(f"unknown target OAK status: {target}")
        return errors
    if current == target:
        return errors
    if target not in ALLOWED_TRANSITIONS[current]:
        errors.append(f"disallowed OAK transition: {current} -> {target}")
        return errors

    witness_required = {
        "TESTABLE",
        "COMPUTATIONALLY_VERIFIED",
        "SIMULATED",
        "PROTOTYPED",
        "MEASURED",
        "REPLICATED",
        "CERTIFIED_MATH",
        "CERTIFIED_SOFTWARE",
        "CERTIFIED_PHYSICS",
    }
    if target in witness_required and not (claim.witness or "").strip():
        errors.append("witness required before promotion")

    if target == "CERTIFIED_MATH" and not evidence.formal:
        errors.append("formal evidence required for CERTIFIED_MATH")
    if target in {"COMPUTATIONALLY_VERIFIED", "CERTIFIED_SOFTWARE"} and not evidence.computational:
        errors.append("computational evidence required")
    if target == "SIMULATED" and not evidence.simulation:
        errors.append("simulation evidence required")
    if target == "MEASURED" and not evidence.experimental:
        errors.append("experimental evidence required")
    if target == "REPLICATED" and not (evidence.experimental and evidence.replication):
        errors.append("experimental and replication evidence required")
    if target == "CERTIFIED_PHYSICS" and not (evidence.experimental and evidence.replication):
        errors.append("replicated experimental evidence required for CERTIFIED_PHYSICS")
    return errors


def promote(current: str, target: str, claim: ClaimIR, evidence: EvidenceVector) -> str:
    errors = promotion_errors(current, target, claim, evidence)
    if errors:
        raise ValueError("; ".join(errors))
    return target
