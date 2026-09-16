# Ω Multidirectional Omni Compiler — R4A Representation Kernel

Status: PROVISIONAL / ENGINEERING KERNEL

R4A extends the existing Omni Compiler rather than creating a parallel document engine.

## Added primitives

- `BoundingBox` for source geometry.
- `ProvenanceAnchor` bound to an exact SHA-256 source artifact, extractor/version, optional page/bbox/locator and bounded confidence.
- `ConfidenceVector` with independent text/structure/math/numeric/layout/provenance axes.
- `RepresentationNode` for document/page/region/text/table/equation/citation and related representation objects.
- `RepresentationRelation` for typed n-ary semantic/structural links.
- `RepresentationGraph` with ancestor/descendant closure inside one representation.

## Ownership boundary

- `ArtifactGraph` remains the inter-artifact lineage/invalidation owner.
- `UniversalIRObject` remains the cross-domain IR owner.
- R4A owns only intra-artifact representation structure and atomic provenance.

## Hard invariants

- `URL != Loaded`.
- `HashEquality != SemanticTruth`.
- `ParserConfidence != Correctness`.
- `ExtractedNode != SourceArtifact`.
- `RepresentationGraph != ArtifactGraph`.
- Missing provenance fails closed for representation nodes.

## Next gate

R4B: materialize a generalized bounded `PDFIR` adapter that produces page/block nodes with source geometry/provenance, without claiming OCR/layout generality that has not been benchmarked.
