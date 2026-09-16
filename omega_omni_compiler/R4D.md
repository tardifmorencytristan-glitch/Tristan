# Ω Multidirectional Omni Compiler — R4D Real Parser Court

Status: PROVISIONAL / BOUNDED REAL PARSER EXECUTION

R4D crosses the R4B boundary from parser-independent observations to actual parser execution on PDF bytes.

## Two bounded parser adapters

- `PyPDFAdapter` uses pinned `pypdf==5.9.0` and emits one page-envelope text observation per selected page. The envelope is explicitly **not** represented as a true text bounding box.
- `PopplerBBoxAdapter` uses `pdftotext -bbox-layout`/`pdfinfo`, emits Poppler-reported block geometry and records the observed Poppler version.

Both adapters bind every observation to the SHA-256 of the exact input PDF bytes.

## CI court

A frozen one-page PDF byte fixture is stored in Git with SHA-256
`cc45d6d9511f68640442c736d05ccd625f34b634cd64115d34c3cf514d4890a4`.

The dedicated R4D workflow installs the pinned pypdf dependency plus Poppler, verifies the fixture hash, executes both parsers, checks selected invariants and geometry semantics, and tests the disagreement path.

The ordinary Omni workflow may skip this optional-dependency court when the parser dependencies are absent; the dedicated R4D workflow is the promotion gate for parser execution.

## Real R3 source court observed before PR materialization

The existing user-owned R4 Living Delta source was materialized from Drive and verified byte-equal to the prior R3 source identity:

- bytes: `1811904`
- SHA-256: `ac4c774094bbecc7f52bf5fb9d1e035595e7a79e483685ed0bea29db7aaee68a`
- pages: `466`
- bounded pages parsed: `1–2`
- pypdf: `5.9.0`
- Poppler `pdftotext`: `25.06.0`

On pages 1–2 the two local parser outputs were not normalized-text identical. Sequence similarity was `0.9737017310252996`, while token-set Jaccard was `1.0`. All eight previously selected R3 semantic anchors were present in both outputs. This is persisted as bounded disagreement evidence, not as adjudication that one parser is more correct.

## Disagreement semantics

Parser disagreement is compiled to `LossTensor` as `UNKNOWN`, not silently relabelled `LOST`. Severity is the measured `1 - sequence_similarity` heuristic; recoverability remains zero until an independent adjudicator is actually implemented.

## Hard boundaries

- `ParserExecution != ParserCorrectness`.
- `ParserAgreement != Truth`.
- `ParserDisagreement != EitherParserWrong`.
- `TokenSetEquality != ReadingOrderEquality`.
- `PopplerBBox != GroundTruthBBox`.
- `PyPDFPageEnvelope != TextBBox`.
- `Pages1To2 != Full466PageBenchmark`.
- `LocalRealPDFCourtPASS != ExactHeadCIPASS`.
- A synthetic frozen CI fixture is not a replacement for external real-world document benchmarks.

## Next gates

1. exact-head dedicated R4D CI;
2. post-merge replay/readback;
3. R4E independent disagreement/reconciliation court;
4. add external parser adapters only through RightToLose tournaments;
5. expand from text/layout to equations, tables and citations.
