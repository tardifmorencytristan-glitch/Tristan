# Ω Scientific Writing Compiler R0 — Receipt

Status: PROVISIONAL / CI-PENDING

Branch: `feat/omega-scientific-writing-r0`

Initial exact head at receipt creation: `f733a6d9a451d931359639eebd828a588aa0488d`

## Materialized

- ScientificIR JSON schema.
- Deterministic ScientificLint.
- Polytechnique Montréal profile (partial / provisional).
- IEEE article profile.
- Positive ScientificIR fixture.
- Negative ScientificIR fixture.
- Unit tests and CI workflow.

## Verified source facts encoded

- Polytechnique Montréal requires use of an official Word or LaTeX template for theses/dissertations and points students to the current presentation guide and submission checklist.
- IEEE Author Center describes an abstract up to 250 words, self-contained, and methodology detailed enough for replication; it also asks authors to acknowledge limitations and avoid exaggerating results.
- Current LaTeX Tagged PDF guidance recommends a current LaTeX release and prefers LuaLaTeX for new documents.

## OAK boundary

No claim is made that R0 currently validates full Polytechnique formatting, journal acceptance, experimental truth, novelty, statistical validity, or formal proof. Those remain residuals.

## Required promotion gates

1. CI positive fixture PASS.
2. CI negative fixture rejected as intended.
3. Full official Polytechnique guide/template parity extraction.
4. LaTeX build adapter and PDF readback.
5. R4/R5 thesis ingestion benchmark.
