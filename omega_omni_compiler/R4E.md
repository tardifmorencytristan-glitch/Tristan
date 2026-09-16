# Ω Multidirectional Omni Compiler — R4E Independent Reconciliation Court

Status: PROVISIONAL / FAIL-CLOSED RECONCILIATION KERNEL

R4E separates parser generation from adjudication. It does not elect a parser from self-consensus, confidence or popularity.

## Decision states

- `CONSENSUS_TEXT`: all parser outputs are exactly equal after the bounded normalization and required invariants are present. This is agreement evidence, not truth.
- `HOLD_DISAGREEMENT`: outputs differ and no independent adjudication is available.
- `HOLD_MISSING_INVARIANT`: at least one required invariant is absent from at least one parser output.
- `HOLD_SOURCE_MISMATCH`: parser runs are not bound to the same source SHA-256.
- `ADJUDICATED_EXTERNAL`: an explicit bounded adjudication supplies accepted parser ids together with provenance, authority and scope.

## Independent adjudication contract

External adjudication must carry:
- an id;
- parser ids that actually exist in the court;
- provenance;
- explicit authority;
- bounded scope.

The reconciliation kernel does not infer authority and does not convert parser agreement into authority.

## LossTensor bridge

- exact text consensus projects to `PRESERVED` semantic state;
- unresolved disagreement/missing invariant projects to `UNKNOWN`;
- source mismatch projects to `UNKNOWN` provenance state;
- externally adjudicated recovery projects to `RECONSTRUCTED`, preserving the adjudication evidence id.

`RECONSTRUCTED != ORIGINAL` remains binding.

## Real R4D readback

The persisted R4D real-PDF court is executable input to R4E. Because pypdf and Poppler differed on normalized sequence while all selected invariants were present, and because no independent adjudicator exists yet, R4E must return `HOLD_DISAGREEMENT`. It is prohibited from choosing either parser from the R4D metrics alone.

## Hard boundaries

- `Consensus != Truth`.
- `Majority != Authority`.
- `Confidence != Correctness`.
- `Similarity != Adjudication`.
- `TokenSetEquality != SemanticEquivalence`.
- `ExternalAdjudication != UniversalParserSuperiority`.
- `ADJUDICATED_EXTERNAL` is bounded to its declared scope.
- `RECONSTRUCTED != ORIGINAL`.

## Next gates

1. qualify R4E exact-head CI;
2. external RightToLose parser tournament with frozen ground truth or independent human/source court;
3. add typed equation/table/citation extraction and reconciliation;
4. route high-impact disagreements by value-of-reparse rather than uniform compute.
