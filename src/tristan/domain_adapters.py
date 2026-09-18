from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DomainAdapter:
    domain: str
    serializer: str
    generator: str
    evaluator: str
    constraints: tuple[str, ...]
    witnesses: tuple[str, ...]
    maturity: str = "PROVISIONAL"

    def validate(self) -> list[str]:
        errors: list[str] = []
        for name, value in (
            ("domain", self.domain),
            ("serializer", self.serializer),
            ("generator", self.generator),
            ("evaluator", self.evaluator),
        ):
            if not value.strip():
                errors.append(f"{name} required")
        if not self.constraints:
            errors.append("constraints required")
        if not self.witnesses:
            errors.append("witnesses required")
        return errors


def default_domain_adapters() -> dict[str, DomainAdapter]:
    return {
        "tfuga": DomainAdapter(
            domain="TFUGA",
            serializer="ClaimIR+TransformationIR",
            generator="typed-conjecture-and-transformation-generator",
            evaluator="formalization-counterexample-and-evidence-court",
            constraints=(
                "Analogy != FormalOperator",
                "GeneralizationRequiresValidityDomain",
                "PhysicalClaimRequiresIndependentEvidence",
            ),
            witnesses=("formal-proof-or-counterexample", "bounded-prediction"),
        ),
        "prime": DomainAdapter(
            domain="Prime",
            serializer="integer-instance+algorithm-config",
            generator="candidate-factorization-primality-strategy",
            evaluator="exact-correctness-runtime-memory-benchmark",
            constraints=("ExactCorrectnessBeforeSpeed", "BaselineRequired"),
            witnesses=("exact-result", "runtime", "memory", "scaling"),
        ),
        "lc_fractal": DomainAdapter(
            domain="LC-Fractal",
            serializer="netlist+geometry+component-tolerances",
            generator="control-and-fractal-topology-candidate",
            evaluator="analytic-or-spice-bounded-court",
            constraints=(
                "Simulation != Measurement",
                "ControlRequired",
                "ToleranceSweepRequired",
            ),
            witnesses=("delta-Z(omega)", "delta-Q", "delta-resonance-spectrum"),
        ),
        "gaia": DomainAdapter(
            domain="Gaia",
            serializer="impact-vector+assumptions+scenario",
            generator="technology-portfolio-candidate",
            evaluator="pareto-impact-evidence-cost-risk-court",
            constraints=(
                "SimulatedImpact != MeasuredImpact",
                "NoSingleMagicScore",
                "UncertaintyRequired",
            ),
            witnesses=("CO2e", "energy", "water", "materials", "cost", "scale"),
        ),
    }


def validate_default_domain_adapters() -> dict[str, list[str]]:
    return {name: adapter.validate() for name, adapter in default_domain_adapters().items()}
