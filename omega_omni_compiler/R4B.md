# Ω Multidirectional Omni Compiler — R4B Generalized Bounded PDFIR

Status: PROVISIONAL / ENGINEERING ADAPTER

R4B compiles a parser-independent `PDFDocumentObservation` into the merged R4A representation graph.

## Separation of responsibilities

`PDF parser -> PDFDocumentObservation -> PDFIR -> RepresentationGraph`

R4B intentionally does **not** claim that arbitrary PDF bytes are already parsed automatically. External/native parser adapters remain a later gate. This prevents one parser implementation from becoming the PDFIR definition.

## Implemented

- page observations with dimensions and rotation;
- typed block observations with geometry, reading order, content and multi-axis confidence;
- page-bound geometry validation;
- unique page/block/read-order gates;
- exact SHA-256 provenance binding on document, page and block nodes;
- document/page/block containment compiled into `RepresentationGraph`;
- conservative provenance confidence derived from the weakest observed confidence axis;
- serialization-ready `PDFIR` wrapper.

## Real lineage bridge

A focused fixture binds the previously observed R3 source PDF SHA-256
`ac4c774094bbecc7f52bf5fb9d1e035595e7a79e483685ed0bea29db7aaee68a`
while explicitly marking the observation as persisted-readback-derived rather than automatic extraction.

## Hard boundaries

- `PDFObservation != PDFBytesParsed`.
- `ReadbackDerivedObservation != AutomaticExtraction`.
- `BoundingBoxValid != LayoutCorrect`.
- `ReadingOrderDeclared != ReadingOrderTrue`.
- `ParserConfidence != Correctness`.
- `PDFIR != OriginalPDF`.

## Next gate

R4C: extend the existing LossLedger into a typed multidimensional LossTensor with severity/recoverability and transform attribution. Then R4D can populate `PDFDocumentObservation` through competing real parser adapters.
