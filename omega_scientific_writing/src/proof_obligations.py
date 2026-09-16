from __future__ import annotations


OBLIGATIONS = {
    "ENGINEERING": [
        "declared_scope",
        "software_or_system_evidence",
        "failure_boundary",
        "reproducible_environment_or_receipt",
    ],
    "NUMERICAL": [
        "model_or_equations",
        "numerical_method",
        "parameter_domain",
        "convergence_or_stability_check",
        "baseline_or_reference",
    ],
    "EMPIRICAL": [
        "measurement_or_experiment",
        "uncertainty",
        "sample_or_acquisition_protocol",
        "controls_or_baseline",
        "limitations",
    ],
    "PHYSICAL": [
        "physical_model",
        "units_or_dimensions",
        "domain_of_validity",
        "empirical_or_independent_anchor",
        "alternative_explanations",
        "falsifier",
    ],
    "MATHEMATICAL": [
        "formal_statement",
        "assumptions",
        "proof_or_derivation",
        "dependency_chain",
        "counterexample_when_assumptions_relaxed",
    ],
    "METHODOLOGICAL": [
        "baseline",
        "matched_budget_comparison",
        "metric",
        "robustness_check",
        "failure_regime",
    ],
    "LITERATURE": [
        "search_scope",
        "source_provenance",
        "contradictory_sources_checked",
        "primary_sources_when_available",
    ],
    "COMPLIANCE": [
        "authority_source",
        "version_or_date",
        "rule_scope",
        "explicit_not_checked_state",
    ],
}


def required_obligations(claim: dict) -> list[str]:
    return list(OBLIGATIONS.get(claim.get("claim_type"), []))


def missing_obligations(claim: dict) -> list[str]:
    declared = set(claim.get("obligations_satisfied", []))
    return [x for x in required_obligations(claim) if x not in declared]


def evaluate_obligations(doc: dict) -> list[dict]:
    findings = []
    for claim in doc.get("claims", []):
        cid = claim.get("id", "<unknown>")
        ctype = claim.get("claim_type")
        if ctype not in OBLIGATIONS:
            continue
        missing = missing_obligations(claim)
        if missing:
            findings.append({
                "severity": "WARN",
                "code": "PROOF_OBLIGATIONS_OPEN",
                "object": cid,
                "detail": missing,
            })
    return findings
