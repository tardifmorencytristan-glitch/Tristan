from __future__ import annotations

from dataclasses import asdict, dataclass

from .closure import compile_closure_plan
from .domain_cases_r4 import compile_r4_cases
from .jarvis import compile_jarvis_plan
from .r3 import compile_r3_status
from .registry import Registry


DOMAIN_KEYWORDS = {
    "tfuga": ("tfuga", "transformation", "formalize", "formalisation", "axiom"),
    "prime": ("prime", "primal", "factor", "factorization", "factorisation", "pnfm", "pdm"),
    "lc_fractal": ("lc", "circuit", "fractal", "impedance", "resonance"),
    "gaia": ("gaia", "climate", "climat", "energy", "energie", "water", "eau", "carbon", "co2"),
}


@dataclass(frozen=True)
class JarvisRuntimeReceipt:
    schema_version: str
    intent: str
    selected_context: tuple[str, ...]
    selected_domains: tuple[str, ...]
    core_plan: dict
    closure_plan: dict
    r3_capabilities: dict
    domain_cases: dict[str, dict]
    next_mission_id: str
    epistemic_status: str
    scientific_pass: bool
    authority_granted: bool
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def select_domains(intent: str) -> tuple[str, ...]:
    words = intent.lower()
    selected = [
        domain
        for domain, keywords in DOMAIN_KEYWORDS.items()
        if any(keyword in words for keyword in keywords)
    ]
    return tuple(sorted(set(selected)))


def compile_jarvis_runtime(
    intent: str,
    registry: Registry,
    limit: int = 8,
) -> JarvisRuntimeReceipt:
    core = compile_jarvis_plan(intent, registry, limit=limit)
    closure = compile_closure_plan(intent, registry, limit=limit)
    r3 = compile_r3_status(registry)
    all_cases = compile_r4_cases()
    selected_domains = select_domains(intent)
    selected_cases = {name: all_cases[name] for name in selected_domains}

    status = "PROVISIONAL_JARVIS_RUNTIME"
    if r3.status == "HOLD" or any(case["errors"] for case in selected_cases.values()):
        status = "HOLD"

    return JarvisRuntimeReceipt(
        schema_version="jarvis-tristan-unified-runtime-r5",
        intent=intent,
        selected_context=core.selected_context,
        selected_domains=selected_domains,
        core_plan=core.to_dict(),
        closure_plan=closure.to_dict(),
        r3_capabilities=r3.to_dict(),
        domain_cases=selected_cases,
        next_mission_id=closure.next_mission_id,
        epistemic_status=status,
        scientific_pass=False,
        authority_granted=False,
        boundaries=(
            "UnifiedRuntime != ScientificPASS",
            "Plan != Authorization",
            "DomainCase != TheoryValidation",
            "Simulation != Measurement",
            "Consensus != Evidence",
            "EngineeringCrystal != ScientificPASS",
            "NO_ACTION is admissible",
        ),
    )
