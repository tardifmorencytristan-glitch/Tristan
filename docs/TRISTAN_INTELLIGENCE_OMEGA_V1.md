# Tristan Intelligence Omega v1

This layer fuses the existing Jarvis R6 evidence stack with a preregistered,
adversarial intelligence loop. It deliberately reuses existing kernel types,
OAK, scientific connectors, and repository/runtime boundaries.

## Canonical loop

Claim -> Prediction Ledger -> ExperimentIR -> Scientific Source Plan
-> Defender / Falsifier / Independent Replicator -> Model Tournament
-> OAK -> Crystal / Failure Memory

## New primitives

- **PredictionLedger**: append-only SHA-256 chain. It proves preregistration
  integrity only; it does not prove the scientific claim.
- **CompiledIntelligenceMission**: converts a ClaimIR into a testable,
  adversarial mission and freezes the prediction before retrieval.
- **ModelTournament**: compares declared metrics across null/conventional/
  Tristan models without promoting the best-scoring model to scientific truth.

## Hard gates

- PredictionFrozen != PredictionConfirmed
- SourceSelection != DataRetrieved
- DataRetrieved != CorrectAnalysis
- Simulation != Measurement
- Consensus != Evidence
- ModelOrdering != ScientificTruth
- MissionCompiled != Authorization
- NO_ACTION is admissible

## Repository policy

This work is layered on top of the R6 evidence branch and is intended to be
reviewed through exact-head CI in a draft PR. It must not merge itself.
