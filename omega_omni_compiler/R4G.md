# Ω Multidirectional Omni Compiler — R4G/H Scientific Renderer Absorption + CI PDF Readback

Status: PROVISIONAL / EXACT-BLOB REUSE + CI-NATIVE PDF ARTIFACT GATE

R4G/H absorbs the useful Scientific Writing R4.2 rendering capability from stale PR #21 into the Omni transformation fabric without merging that stale lineage wholesale.

## Exact reused blobs from PR #21

The following previously observed blobs are reused byte-for-byte on the fresh Omni branch:

- `omega_scientific_writing/src/latex_renderer.py` — blob `a525a318d01ceb81a140c0c0438afcfe7bcad22a`
- `omega_scientific_writing/fixtures/battery_r4_2_packet.json` — blob `9d0ac114f522a9ceab8920220f1b827fd463c4e5`
- `omega_scientific_writing/artifacts/r4_2/BATTERY_R4_2_EVIDENCE_BOUNDED.tex` — blob `296e889d5685e3a94180a2af556412c1943f404e`
- `omega_scientific_writing/tests/test_r4_2_latex_renderer.py` — blob `64f5819c8393ab7608679e6a3d65e229ec6903d1`
- historical local PDF/readback receipt — blob `7ee1b518c553a119cc81993e6dfc2cda3b1586a3`

The stale PR is therefore a capability/evidence source, not a branch to merge.

## Omni adapter

`ScientificRenderArtifact` binds:
- exact renderer identity/version;
- generated `.tex` SHA-256;
- source evidence anchor;
- required semantic readback token contract;
- non-promoted status `GENERATED_NOT_PDF_VERIFIED`.

The adapter verifies exact source-anchor presence and the inherited semantic token contract before any PDF build.

## Renderer parity

The Omni adapter output must be byte-identical to the persisted R4.2 `.tex` artifact and retain SHA-256:

`6f024984f9b1dac291f1c64243f2758783917712e2bbfd04abea76651d1a03f8`

This tests capability absorption without silently changing the scientific projection.

## CI-native PDF gate

A dedicated GitHub Actions lane now performs on the exact PR head:

1. install pdfTeX/LaTeX packages + Poppler;
2. execute the original R4.2 renderer tests and the Omni adapter tests;
3. render the packet through the Omni adapter;
4. verify exact `.tex` SHA-256 and byte parity with the historical artifact;
5. run pdfTeX twice;
6. reject any `Overfull \\hbox` regression;
7. require a real non-empty two-page PDF;
8. run `pdfinfo` structural readback;
9. run `pdftotext` and require bounded semantic tokens;
10. render both PDF pages to non-empty PNG images with `pdftoppm`;
11. emit an exact-head runtime receipt with output hashes;
12. upload `.tex`, `.pdf`, text readback, PDF metadata, PNG renders and receipts as a CI artifact.

## FailureGenome inheritance

The historical R4.2 provenance-overflow failure remains part of the lineage. CI now operationalizes one regression condition by failing on an `Overfull \\hbox`, while preserving the `xurl`/breakable URL correction.

This automated check is not equivalent to human visual inspection.

## Hard boundaries

- `GeneratedPDF != IndependentEvidence`.
- `CIRenderReadbackPASS != ScientificPASS`.
- `PNGRenderNonempty != HumanVisualInspectionPASS`.
- `TextReadbackPASS != CitationCourtPASS`.
- `RendererParity != WritingSuperiority`.
- `HistoricalLocalPDFPASS != CurrentExactHeadCIPASS`.
- Runtime PDF SHA may differ from the historical local PDF due to build-environment metadata; semantic/structural/readback gates remain separately measured.

## Next gates

1. exact-head R4G/H CI and artifact receipt;
2. post-merge readback of the reused blobs and workflow;
3. close stale PR #21 as superseded-by-composition only after this fresh lane succeeds;
4. generalize from the Battery-specific renderer to a DocumentIR renderer contract without weakening evidence/scope gates;
5. add accessibility/citation courts and multi-document generation from shared IR.
