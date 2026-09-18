# JARVIS Tristan Problem Foundry R1

Problem Foundry turns externally observed problems into bounded, reusable verification work.

## Scientific and community boundary

The foundry is not an auto-answer bot. It separates:

1. problem intake,
2. decomposition into a ProblemGenome,
3. routing into a domain verification contract,
4. solution research and implementation,
5. adversarial checks,
6. OAK promotion,
7. optional human-reviewed public contribution.

Stack Overflow, MathOverflow, and Physics Stack Exchange are configured fail-closed for AI-generated publication as of 2026-09-18. Their adapter mode is manual problem text only. No Stack Exchange scraping or auto-posting is part of R1.

GitHub intake may use an authorized connector, but publication remains disabled until repository-local contribution rules are checked.

## ProblemGenome

A problem records its source, domain, tags/languages, expected utility, generalization potential, verifiability, diversity contribution, unanswered signal, reuse potential, effort, and risk.

The base priority is:

[
S(q)=\frac{2U+2G+2V+1.5D+A+1.5R}{E+\rho}
]

where the symbols correspond to the fields above. The queue then adds a bounded bonus to under-represented domains so the system does not collapse into one easy problem family.

## Verification contracts

Code: minimal reproducer, unit tests, regressions, static/type checks when applicable, and benchmarks for performance claims.

Math: explicit assumptions, counterexample search, exact/symbolic cross-checks, numerical sanity checks where useful, and formal or human proof review for certification.

Physics: dimensional analysis, limiting cases, conservation/symmetry checks, numerical cross-checks, and an explicit literature/measurement boundary.

Engineering and data have their own contracts as well.

## OAK interpretation

A ProblemPlan has status PROVISIONAL_ENGINEERING_PLAN. It is not evidence that a solution is correct. Solvers must still produce domain-specific evidence and pass the existing OAK gates.

The public objective is useful work, not volume: accepted fixes, reproducible demonstrations, verified proofs, measurements, or documentation improvements are stronger signals than raw post count.

## CLI target

R1 exposes a `tristan foundry` command after the CLI integration in this branch. Its JSON output is suitable for downstream mission queues and AI-7 orchestration.
