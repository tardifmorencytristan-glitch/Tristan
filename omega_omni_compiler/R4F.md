# Ω Multidirectional Omni Compiler — R4F Scientific Specialized IRs

Status: PROVISIONAL / CONSERVATIVE TYPED SCIENTIFIC KERNEL

R4F adds scientific structures without claiming that general PDF recognition of those structures is solved.

## QuantityIR + numeric integrity

`QuantityIR` preserves:
- label;
- original decimal lexeme;
- exact `Decimal` interpretation;
- unit string;
- source representation node;
- provenance ids;
- bounded observation status.

A conservative explicit assignment extractor recognizes forms such as `Vmax = 4.20 V`. It does not infer implicit quantities or convert units automatically.

`NumericCourtDecision` compares parser-observed quantities for the same explicit label:
- `CONSISTENT`
- `HOLD_MISSING_QUANTITY`
- `HOLD_UNIT_DISAGREEMENT`
- `HOLD_VALUE_DISAGREEMENT`

Unit disagreement is never silently converted, and numeric disagreement is projected into LossTensor as `UNKNOWN`.

## EquationIR

R4F introduces an intentionally bounded `EquationIR` candidate carrying raw text, lhs/rhs, lexical symbol candidates, source node and provenance. The initial constructor requires exactly one equality sign.

It does **not** claim symbolic equivalence, dimensional validity, algebraic correctness, LaTeX recovery or AST correctness. Its default state is `CANDIDATE_UNVERIFIED`.

## TableIR

`TableIR` / `TableCellIR` provide typed row/column coordinates, spans, header flag and source-node linkage. Duplicate coordinates and invalid spans fail closed.

No general table detector is claimed by R4F.

## CitationIR

`CitationIR` separates:
- citation marker presence;
- target text;
- source resolution;
- support/contradiction status.

Resolving a citation does not promote it to `SUPPORTS`. A support/contradiction claim requires a resolved source id.

## Hard boundaries

- `QuantityParsed != QuantityCorrect`.
- `DecimalEquality != PhysicalEquivalence`.
- `UnitStringEquality != DimensionalProof`.
- `UnitDisagreement != ConvertibleWithoutPolicy`.
- `EquationCandidate != SymbolicAST`.
- `EquationCandidate != MathematicalTruth`.
- `TableIR != TableDetectionPASS`.
- `CitationResolved != ClaimSupported`.
- `NumericConsensus != SourceTruth`.

## Next gates

1. exact-head CI;
2. bind QuantityIR to real R4D parser runs and independent source regions;
3. add unit/dimension registry and explicit conversion policies;
4. add specialist equation/table/citation parser adapters through RightToLose tournaments;
5. absorb the stale Scientific Writing R4.2 renderer as a DocumentIR/ScientificIR renderer adapter, then make generated PDF rendering/readback CI-native.
