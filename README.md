# Tristan

**Status: BOOTSTRAP / PROVISIONAL ENGINEERING KERNEL**

`Tristan` is a small public, regenerable kernel for routing intentions into the minimum sufficient set of sources, capabilities, evidence, failures, tests, and frontiers.

It does **not** claim to contain the entire Tristan corpus, nor to make scientific claims true by compilation.

## Scientific Consistency demand canary

A public browser-only canary tests one concrete problem: **does scientific code remain consistent with the equations it is supposed to implement?**

Live canary:

https://raw.githack.com/tardifmorencytristan-glitch/Tristan/main/index.html

Properties:

- runs locally in the browser;
- accepts bounded mathematical expressions, not arbitrary source code;
- compares two expressions on deterministic numerical samples;
- reports a residual and PASS/HOLD-style result;
- explicitly does **not** claim formal proof.

A bounded synthetic benchmark currently reports **8/8 correct** across four equivalence cases and four controlled mismatch families. This is a small engineering check, not evidence of general scientific-paper/code performance. See `receipts/SCIENTIFIC_CONSISTENCY_BENCH_R0_1.json`.

If the canary creates real value, the current deeper-report experiment points to Stripe Checkout:

https://buy.stripe.com/5kQ3cvfda08yfEH6He83C04

The economic experiment remains unvalidated until attributable external usage and payment evidence exist.

## Core invariants

- Generated != Verified
- Simulation != Measurement
- Prototype != Production
- Capability != Authority
- OriginBonus = 0
- LocalWinner != UniversalWinner
- EveryComponentHasRightToLose
- NO_ACTION is admissible

## Architecture

`INTENT -> CONTEXT* -> RESIDUAL -> SEARCH -> REPRESENT -> GENERATE -> TEST -> ATTACK -> COMPETE -> REALITY -> CRYSTALLIZE -> REGENERATE`

The initial public kernel deliberately federates existing sources instead of copying them blindly.

## Quick start

```bash
python -m pip install -e .
tristan verify
tristan status
tristan query "context regeneration evidence"
tristan run "Build a minimum sufficient context compiler"
```

## Current canonical source federation

The bootstrap registry points to:

- the historical Git repository `tardifmorencytristan-glitch/Tristan-Tardif-Morency`;
- the machine-readable `context/TRISTAN_MEMORY_REGISTRY.json`;
- the Google Drive `TRISTAN Ω-CONTEXT BOOTSTRAP`.

Pointers are not proof that their contents were loaded or verified. Every operation must preserve provenance and evidence scope.

## Maturity

This first kernel is intentionally dependency-light and deterministic. It provides:

1. a typed `TristanObject`;
2. a JSONL registry;
3. bounded `Context*(Q)` compilation;
4. a deterministic `run` receipt;
5. regeneration/status commands;
6. schema and repository invariant checks;
7. a CI workflow.

Future modules must earn their complexity through measured, scoped gains.
