# Ω Scientific Writing Compiler — R0

Status: PROVISIONAL / EXECUTABLE KERNEL TARGET

Goal: compile structured scientific research objects into institution/journal-adapted manuscripts while preserving claims, evidence, provenance, notation, units, reproducibility, and epistemic status.

Core invariant: `Generated != Verified`; `CompilationPASS != ScientificPASS`; `Simulation != Measurement`; `Formatting != Evidence`.

## R0 scope

- `ScientificIR` schema for claims, evidence, equations, figures, citations and results.
- Machine-readable writing/compliance rules.
- Polytechnique Montréal thesis adapter profile.
- IEEE article adapter profile.
- Deterministic scientific lints for claim/evidence linkage, symbol definitions, units metadata, figures and citations.
- OAK receipt describing validation status and residuals.

## Pipeline

`QUESTION -> LITERATURE -> RESIDUAL -> HYPOTHESIS -> EXPERIMENT/PROOF -> EVIDENCE -> ScientificIR -> LINT -> ADAPTER -> LATEX -> PDF -> READBACK -> RECEIPT`

## Epistemic boundary

This package does not make scientific claims true. It checks declared structure, provenance and selected consistency constraints. Novelty, experimental truth, legal/institutional acceptance and formal proof require independent verification.