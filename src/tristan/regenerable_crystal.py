from __future__ import annotations

from dataclasses import dataclass

from .book0 import Book0Seed, compare_seeds
from .crystal import CrystalCandidate, compile_crystal


@dataclass(frozen=True)
class RegenerableCrystalReceipt:
    crystal_id: str
    crystal_status: str
    regeneration_valid: bool
    status: str
    scientific_pass: bool = False


def qualify_regenerable_crystal(
    candidate: CrystalCandidate,
    expected_seed: Book0Seed,
    observed_seed: Book0Seed,
) -> RegenerableCrystalReceipt:
    crystal = compile_crystal(candidate)
    regen = compare_seeds(expected_seed, observed_seed)
    ready = crystal.status == "ENGINEERING_CRYSTAL_READY" and regen.valid
    return RegenerableCrystalReceipt(
        crystal_id=candidate.crystal_id,
        crystal_status=crystal.status,
        regeneration_valid=regen.valid,
        status="REGENERABLE_ENGINEERING_CRYSTAL" if ready else "HOLD",
        scientific_pass=False,
    )
