from __future__ import annotations

from dataclasses import asdict, dataclass

from .domain_cases_r4 import compile_r4_cases


@dataclass(frozen=True)
class R4Status:
    schema_version: str
    cases: dict[str, dict]
    status: str
    scientific_pass: bool
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def compile_r4_status() -> R4Status:
    cases = compile_r4_cases()
    invalid = [name for name, case in cases.items() if case["errors"]]
    return R4Status(
        schema_version="jarvis-r4-domain-cases",
        cases=cases,
        status="HOLD" if invalid else "PROVISIONAL_ENGINEERING_R4",
        scientific_pass=False,
        boundaries=(
            "PublicDomainCase != PrivateCorpusImport",
            "ClaimTemplate != ScientificTruth",
            "EvidenceObligation != EvidenceObtained",
            "MissionQueue != Authorization",
        ),
    )
