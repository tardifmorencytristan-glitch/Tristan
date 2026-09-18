# Ω Scientific Report Compiler — R5A

**Status:** PROVISIONAL / EXACT-HEAD-CI-TARGET

R5A implements the first bounded scientific-report graph and diagnostic courts on top of the existing Ω Scientific Writing Compiler.

## Implemented

- typed report-domain IR;
- deterministic validation and strict packet loading;
- terminology consistency court;
- methodology completeness/reproducibility court;
- typed residual derivation and blocking residuals;
- objective/result/claim/conclusion traceability and proof cones;
- explicit contradiction court;
- integrated conservative report court;
- valid and deliberately invalid end-to-end fixtures;
- CLI verdict with PASS=0 and HOLD=1.

## Hard invariants

- `Generated != Verified`
- `CompilationPASS != ScientificPASS`
- `Simulation != Measurement`
- `Formatting != Evidence`
- `ParserAgreement != Truth`
- `Artifact != Knowledge`
- `ReverseCompiled != OriginalSource`
- `Capability != Authority`
- `ReceiptClaim != ArtifactBytes`
- `OriginBonus = 0`
- `NO_ACTION` and `HOLD` remain admissible outcomes.

## Boundaries

R5A validates declared structure, traceability, terminology, methodology completeness, contradictions, and declared evidence relationships. It does not establish scientific truth, peer-review acceptance, experimental validity beyond supplied evidence, rendering qualification, reverse compilation correctness, or publication authority.

R5A contains no Drive synchronization or external publication logic.

## Next gate

R5B: general report compiler, renderer contract, LaTeX/PDF generation, exact-head PDF readback, and immutable Report Crystal qualification without weakening R5A epistemic boundaries.
