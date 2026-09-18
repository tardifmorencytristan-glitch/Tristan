from __future__ import annotations

from dataclasses import asdict, dataclass

from .atlas_federation import compile_atlas_federation
from .closure import compile_closure_plan
from .domain_cases_r4 import compile_r4_cases
from .evidence_foundry import blank_evidence_receipt, compile_evidence_contract
from .final_fusion import compile_final_fusion
from .jarvis import compile_jarvis_plan
from .r3 import compile_r3_status
from .registry import Registry
from .scientific_connectors import build_source_plan
from .ultra_closure import DebtVector, compile_ultra_closure


DOMAIN_KEYWORDS = {
    "tfuga": ("tfuga", "transformation", "formalize", "formalisation", "axiom"),
    "prime": ("prime", "primal", "factor", "factorization", "factorisation", "pnfm", "pdm"),
    "lc_fractal": ("lc", "circuit", "fractal", "impedance", "resonance", "resonator", "tesla"),
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
    scientific_source_plan: dict
    evidence_contract: dict | None
    atlas_federation: dict
    final_fusion: dict
    ultra_closure: dict
    domino_engine: dict
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


def _compile_evidence_layer(intent: str) -> tuple[dict, dict | None]:
    source_plan = build_source_plan(intent)
    selected_sources = tuple(source_plan["selected_sources"])
    if not selected_sources:
        return source_plan, None

    contract = compile_evidence_contract(
        claim_id="JARVIS-R6-INTENT-CLAIM",
        datasets=selected_sources,
        observables=("explicit-observable-required-before-analysis",),
    )
    receipt = blank_evidence_receipt(contract)
    return source_plan, receipt.to_dict()


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
    scientific_source_plan, evidence_contract = _compile_evidence_layer(intent)
    atlas_federation = compile_atlas_federation(intent, registry)
    final_fusion = compile_final_fusion(intent, registry)
    ultra_closure = compile_ultra_closure(
        intent=intent,
        mission_id="JARVIS-R9-INTENT",
        residuals=core.residuals,
        context_ids=core.selected_context,
        debt=DebtVector(
            evidence=float(len(core.residuals)),
            reality=1.0 if selected_domains else 0.0,
        ),
    )

    status = "PROVISIONAL_JARVIS_RUNTIME"
    if r3.status == "HOLD" or any(case["errors"] for case in selected_cases.values()):
        status = "HOLD"

    return JarvisRuntimeReceipt(
        schema_version="jarvis-tristan-unified-runtime-r9",
        intent=intent,
        selected_context=core.selected_context,
        selected_domains=selected_domains,
        core_plan=core.to_dict(),
        closure_plan=closure.to_dict(),
        r3_capabilities=r3.to_dict(),
        domain_cases=selected_cases,
        scientific_source_plan=scientific_source_plan,
        evidence_contract=evidence_contract,
        atlas_federation=atlas_federation.to_dict(),
        final_fusion=final_fusion.to_dict(),
        ultra_closure=ultra_closure.to_dict(),
        domino_engine={
            "status": "AVAILABLE_NOT_EXECUTED",
            "protocol": "JARVIS-DOMINO-ENGINE-R1",
            "propagation_kinds": ("support", "falsification", "uncertainty", "prediction"),
            "firewall": (
                "causal-quality",
                "provenance-quality",
                "confidence",
                "minimum-propagation-threshold",
                "bounded-depth",
                "cycle-rejection",
            ),
            "boundaries": (
                "Correlation != Causality",
                "LocalEvidence != GlobalTheoryValidation",
                "Propagation != NewEvidence",
                "PredictionGenerated != PredictionConfirmed",
            ),
        },
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
            "SourceSelection != DataRetrieved",
            "DataRetrieved != CorrectAnalysis",
            "AtlasProjection != ScientificRanking",
            "AutonomyPreview != Execution",
            "StateTransitionRequiresEvidence",
            "MissionGenome != Execution",
            "GenerationThrottle != Truth",
            "PrivateSource != PublicPayload",
            "Propagation != NewEvidence",
            "LocalEvidence != GlobalTheoryValidation",
            "NO_ACTION is admissible",
        ),
    )
