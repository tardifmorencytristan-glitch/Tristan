from __future__ import annotations

from .anti_corpus import AlternativeCandidate
from .domain_case import DomainCase, DomainClaimTemplate
from .mission_queue import Mission


def tfuga_case() -> DomainCase:
    claim = DomainClaimTemplate(
        claim_id="TFUGA-PUBLIC-001",
        statement="A TFUGA transformation must be defined as a typed operator with explicit invariants and a bounded validity domain before it can be treated as a formal operator.",
        status="TESTABLE",
        witness="formal operator definition plus counterexample search outside declared validity domain",
        evidence_required=("typed-definition", "invariant-tests", "counterexample-search"),
        assumptions=("public kernel scope only",),
        validity_domain="only explicitly defined transformations represented in the public kernel",
    )
    challengers = (
        AlternativeCandidate("TFUGA-ALT-001", claim.claim_id, "Use ordinary typed transformation pipelines without TFUGA-specific semantics.", evidence_count=1, predictive_hits=1, complexity=1, cost=1),
        AlternativeCandidate("TFUGA-ALT-002", claim.claim_id, "Treat TFUGA language as heuristic notation until a formal operator is specified.", evidence_count=1, predictive_hits=1, complexity=0.5, cost=0.5),
    )
    missions = (
        Mission("TFUGA-M1", "TFUGA-PUBLIC-001", "FORMALIZE_OPERATOR", "formalization-court", expected_verified_gain=4, debt_reduction=4, reuse_potential=3, cost=1.5, risk=0.2),
        Mission("TFUGA-M2", "TFUGA-PUBLIC-001", "SEARCH_COUNTEREXAMPLES", "counterexample-court", expected_verified_gain=3, debt_reduction=3, reuse_potential=2, cost=1, risk=0.1),
    )
    return DomainCase(
        "TFUGA",
        "public formalization obligations only; no private scientific claims imported",
        (claim,), challengers, missions,
        ("Analogy != FormalOperator", "GeneralizationRequiresValidityDomain", "DomainCase != TheoryValidation"),
    )


def prime_case() -> DomainCase:
    claim = DomainClaimTemplate(
        claim_id="PRIME-PUBLIC-001",
        statement="A prime-related algorithm candidate must establish exact correctness before speed or scaling claims are promoted.",
        status="TESTABLE",
        witness="exact outputs on deterministic cases plus matched-baseline runtime and memory measurements",
        evidence_required=("exact-correctness", "baseline", "runtime", "memory"),
        validity_domain="declared integer ranges and benchmark environments only",
    )
    challengers = (
        AlternativeCandidate("PRIME-ALT-001", claim.claim_id, "Baseline deterministic implementation.", evidence_count=2, predictive_hits=2, complexity=1, cost=1),
        AlternativeCandidate("PRIME-ALT-002", claim.claim_id, "NO_ACTION: keep current baseline if candidate lacks measurable gain.", evidence_count=1, predictive_hits=1, complexity=0, cost=0),
    )
    missions = (
        Mission("PRIME-M1", claim.claim_id, "EXACT_CORRECTNESS_COURT", "exact-checker", expected_verified_gain=5, debt_reduction=5, reuse_potential=3, cost=1, risk=0.1),
        Mission("PRIME-M2", claim.claim_id, "MATCHED_BENCHMARK", "runtime-memory-court", expected_verified_gain=3, debt_reduction=2, reuse_potential=2, cost=1.5, risk=0.1, dependencies=("PRIME-M1",)),
    )
    return DomainCase(
        "Prime",
        "algorithmic correctness and benchmark obligations",
        (claim,), challengers, missions,
        ("ExactCorrectnessBeforeSpeed", "LocalBenchmark != UniversalSuperiority", "NO_ACTION is admissible"),
    )


def lc_fractal_case() -> DomainCase:
    claim = DomainClaimTemplate(
        claim_id="LCF-PUBLIC-001",
        statement="Any claimed LC-fractal effect must be stated as a difference against an explicit control under declared component tolerances.",
        status="TESTABLE",
        witness="predeclared delta in impedance, Q, resonance frequency, bandwidth, or spectral density between candidate and control",
        evidence_required=("control", "netlist-or-equations", "tolerance-sweep", "simulation-receipt"),
        assumptions=("simulation-only until independent physical measurements exist",),
        validity_domain="declared circuit topology, parameter ranges, simulator, and frequency range",
    )
    challengers = (
        AlternativeCandidate("LCF-ALT-001", claim.claim_id, "Matched non-fractal control with equal component budget.", evidence_count=2, predictive_hits=2, complexity=1, cost=1),
        AlternativeCandidate("LCF-ALT-002", claim.claim_id, "Observed difference explained by tolerances or parasitics rather than topology.", evidence_count=1, predictive_hits=1, complexity=1, cost=1),
    )
    missions = (
        Mission("LCF-M1", claim.claim_id, "BUILD_MATCHED_CONTROL", "control-court", expected_verified_gain=4, debt_reduction=4, reuse_potential=2, cost=1.5, risk=0.2),
        Mission("LCF-M2", claim.claim_id, "RUN_TOLERANCE_SWEEP", "simulation-court", expected_verified_gain=3, debt_reduction=3, reuse_potential=2, cost=2, risk=0.2, dependencies=("LCF-M1",)),
    )
    return DomainCase(
        "LC-Fractal",
        "simulation and control obligations only; no experimental promotion",
        (claim,), challengers, missions,
        ("Simulation != Measurement", "ControlRequired", "ToleranceSweepRequired", "DomainCase != PhysicalEvidence"),
    )


def gaia_case() -> DomainCase:
    claim = DomainClaimTemplate(
        claim_id="GAIA-PUBLIC-001",
        statement="A Gaia project impact estimate must remain a scenario result until its assumptions, uncertainty, baseline, and measured outcomes are separately established.",
        status="TESTABLE",
        witness="impact vector with baseline, assumptions, uncertainty and later measured outcome fields",
        evidence_required=("baseline", "assumptions", "uncertainty", "scenario-calculation"),
        validity_domain="declared scenario, geography, time horizon, technology assumptions, and data vintage",
    )
    challengers = (
        AlternativeCandidate("GAIA-ALT-001", claim.claim_id, "Simpler baseline scenario with no Tristan-specific intervention.", evidence_count=2, predictive_hits=2, complexity=0.5, cost=0.5),
        AlternativeCandidate("GAIA-ALT-002", claim.claim_id, "Alternative portfolio with lower projected impact but stronger evidence and lower risk.", evidence_count=2, predictive_hits=1, complexity=1, cost=1),
    )
    missions = (
        Mission("GAIA-M1", claim.claim_id, "BOUND_BASELINE_AND_ASSUMPTIONS", "impact-evidence-court", expected_verified_gain=4, debt_reduction=5, reuse_potential=3, gaia_impact=1, cost=1.2, risk=0.2),
        Mission("GAIA-M2", claim.claim_id, "PARETO_SCENARIO_COURT", "multi-criteria-court", expected_verified_gain=3, debt_reduction=2, reuse_potential=3, gaia_impact=2, cost=1.5, risk=0.2, dependencies=("GAIA-M1",)),
    )
    return DomainCase(
        "Gaia",
        "impact-accounting obligations only; no simulated impact promoted to measured impact",
        (claim,), challengers, missions,
        ("SimulatedImpact != MeasuredImpact", "NoSingleMagicScore", "UncertaintyRequired", "DomainCase != ImpactCertification"),
    )


def default_r4_cases() -> dict[str, DomainCase]:
    return {
        "tfuga": tfuga_case(),
        "prime": prime_case(),
        "lc_fractal": lc_fractal_case(),
        "gaia": gaia_case(),
    }


def compile_r4_cases() -> dict[str, dict]:
    return {name: case.compile() for name, case in default_r4_cases().items()}
