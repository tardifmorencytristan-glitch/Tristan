# Ω Multidirectional Omni Compiler — R4C Typed LossTensor

Status: PROVISIONAL / ENGINEERING ADAPTER

R4C extends the existing `LossLedger` without replacing or invalidating its historical receipts.

## Added model

Each loss observation now carries:
- transform attribution;
- item identity;
- typed dimension;
- existing legacy state (`PRESERVED`, `LOST`, `INFERRED`, `RECONSTRUCTED`, `UNKNOWN`);
- severity in `[0,1]`;
- recoverability in `[0,1]`;
- intentional-loss flag;
- cause/detail/evidence references.

Dimensions include semantic, numeric, units, equations, citations, layout, visual, provenance, relation, uncertainty, reading order, typography and image information.

## Compatibility

`LossTensor.from_legacy(...)` lifts historical `LossEntry` objects into the tensor, and `to_legacy()` projects the compatible core fields back to the legacy representation.

This bridge is intentionally lossy for R4C-only metadata such as dimension/severity/recoverability/intentional/cause/evidence. The legacy ledger remains authoritative for its historical schema.

## Residual-weight heuristic

`severity * (1 - recoverability)` is exposed only as a routing heuristic. It is not a probability, calibrated risk, evidence score or truth metric.

## Hard boundaries

- `LossMeasured != TruthMeasured`.
- `Severity != ProbabilityOfError`.
- `Recoverability != GuaranteedRecovery`.
- `IntentionalLoss != Preserved`.
- `TensorSummary != UniversalQualityScore`.
- Legacy projection may discard R4C-only metadata and must not be treated as an exact tensor roundtrip.

## Next gate

R4D: real parser adapters must produce actual `PDFDocumentObservation` objects from observed PDF bytes, compete on frozen fixtures, and populate LossTensor entries from measured disagreements/failures rather than hard-coded superiority claims.
