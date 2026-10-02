# Ω Multidirectional Omni Compiler — R0

Status: PROVISIONAL / EXECUTABLE KERNEL

R0 materializes the smallest shared substrate for bidirectional and multidirectional transformations between research, code, Git, specifications, documents and artifacts.

## Core

- `UniversalIRObject`: typed object with provenance, status, dependencies, scope, assumptions, uncertainty and evidence links.
- `TransformationRegistry`: proof-oriented transformation metadata including preserved invariants, known losses, verifier, reversibility, cost and risk.
- `PathRouter`: chooses a currently lowest `cost + risk + explicit loss` path across registered transformations.
- `LossLedger`: preserves `PRESERVED/LOST/INFERRED/RECONSTRUCTED/UNKNOWN` states.
- `RoundTripVerifier`: compares selected invariants after forward/reverse transformations.
- `ScientificIR bridge`: first real bridge from the existing scientific compiler into UniversalIR and back.

## Current transformation surface

`SCIENTIFIC <-> DOCUMENT <-> ARTIFACT`, `SCIENTIFIC -> CODE -> GIT -> DOCUMENT`, and `SPEC -> CODE`.

These are routing contracts, not claims that every operator is already fully implemented. Operators that are not yet materialized remain interface-level capabilities.

## Invariants

- `Generated != Verified`
- `Artifact != Knowledge`
- `ReverseCompiled != OriginalSource`
- `DigitizedData != OriginalData`
- `Capability != Authority`
- `RoundTripPASS != Truth`
- Losses must remain explicit.

## R1 residuals

1. Materialize real `CodeIR`, `GitIR`, `DocumentIR`, `SpecIR` adapters rather than routing-only contracts.
2. Add PDF reverse compiler using exact file/readback sources.
3. Add bidirectional transformation receipts with hashes and lineage.
4. Add invariant-aware parallax/path-curvature comparison across alternate routes.
5. Connect ScientificTypeSystem/ProofObligations from `omega_scientific_writing`.
6. Add incremental invalidation graph and content-addressed cache.
7. Run one real end-to-end benchmark: external artifact -> IR -> code/Git -> document/PDF -> reverse IR.

## R4H communication projection adapter

R4H reuses `ClaimIR`/`EvidenceIR`, the R4A `RepresentationGraph`, and Scientific Writing lineage to compile bounded timed projections for text/voice/video/slides/web/live surfaces without creating a second writer, Presence runtime, or video OS.

It adds evidence-bound timed segments, fail-closed accessibility/time/loss gates, deterministic JSON round-trip, and a WebVTT export adapter. The Battery-T R4.1 fixture is the first integration court.

See `R4H.md` and `evidence/R4H_COMMUNICATION_PROJECTION_R01.json`.

`PASS_STRUCTURAL != SemanticEquivalence`; `WebVTTExport != VideoRender`; `Capability != Authority`.