from __future__ import annotations

from dataclasses import asdict, dataclass

from .domain_adapters import default_domain_adapters
from .registry import Registry


@dataclass(frozen=True)
class R3Status:
    schema_version: str
    registry_objects: int
    domain_adapters: tuple[str, ...]
    regeneration_mode: str
    failure_diagnosis_mode: str
    status: str
    scientific_pass: bool
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def compile_r3_status(registry: Registry) -> R3Status:
    adapters = default_domain_adapters()
    invalid = {name: adapter.validate() for name, adapter in adapters.items() if adapter.validate()}
    status = "HOLD" if invalid else "PROVISIONAL_ENGINEERING_R3"
    return R3Status(
        schema_version="jarvis-r3",
        registry_objects=len(registry.all()),
        domain_adapters=tuple(sorted(adapters)),
        regeneration_mode="DIFFERENTIAL_AFFECTED_SUBGRAPH_ONLY",
        failure_diagnosis_mode="CAUSE_HYPOTHESES_PLUS_DISCRIMINATING_TEST",
        status=status,
        scientific_pass=False,
        boundaries=(
            "DifferentialRebuild != ScientificValidation",
            "CausalFailureGraph != ProvenCause",
            "RegenerableEngineeringCrystal != ScientificPASS",
            "DomainAdapter != DomainTheoryValidation",
        ),
    )
