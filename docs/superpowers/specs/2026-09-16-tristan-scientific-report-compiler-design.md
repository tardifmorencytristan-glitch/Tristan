# Tristan Scientific Report Compiler R5 — Architecture Design

**Status:** DESIGN / IMPLEMENTATION NOT YET AUTHORIZED BY WRITTEN-SPEC REVIEW

**Date:** 2026-09-16

**Repository baseline:** `tardifmorencytristan-glitch/Tristan` at `7c5c22cb3187eeaf07c66dd1eb2f11d51909166a`

**Purpose:** Turn the existing Tristan scientific-writing, Omni transformation, provenance, parser-court, loss, evidence, and renderer capabilities into one conservative bidirectional scientific-report system that can ingest existing technical reports, represent their scientific content as typed objects, diagnose residuals and contradictions, regenerate publication artifacts, and preserve exact provenance and epistemic boundaries.

---

## 1. Design decision

The scientific-report system is **not** a new isolated project. It is a specialized application layer over the existing Tristan kernel and its already-implemented scientific/Omni components.

The canonical architecture is:

```text
TRISTAN KERNEL
  -> representation/provenance substrate
  -> Omni multidirectional transforms
  -> ScientificIR + evidence/proof obligations
  -> scientific-report graph
  -> validators/courts
  -> report compiler
  -> renderers
  -> PDF/readback qualification
  -> immutable receipts/crystals
  -> bounded Drive family mirror
```

The generated DOCX/PDF/Markdown/LaTeX/HTML artifacts are views of the scientific state. They are not the canonical source of truth.

### Hard epistemic invariants

- `Generated != Verified`
- `CompilationPASS != ScientificPASS`
- `Simulation != Measurement`
- `Formatting != Evidence`
- `ParserAgreement != Truth`
- `RoundTripPASS != Truth`
- `Artifact != Knowledge`
- `ReverseCompiled != OriginalSource`
- `Capability != Authority`
- `ReceiptClaim != ArtifactBytes`
- `OriginBonus = 0`
- `NO_ACTION` and `HOLD` remain admissible outcomes.

No validator may silently promote an extracted or AI-generated statement into scientific truth.

---

## 2. Existing baseline to preserve and reuse

R5 must compose existing capabilities rather than duplicate them.

### 2.1 Tristan kernel

Reuse `src/tristan/model.py` and the existing registry/context mechanisms for top-level capability/source registration and repository-wide provenance routing.

`TristanObject` remains the lightweight cross-system registry object. R5 does **not** overload it with every scientific field. Rich scientific objects remain in dedicated IRs and are referenced from `TristanObject` metadata/evidence links.

### 2.2 Ω Scientific Writing Compiler

Reuse `omega_scientific_writing` for:

- typed scientific claims;
- evidence-kind compatibility;
- proof obligations;
- epistemic diff;
- exact-evidence adapters;
- existing scientific lint semantics;
- LaTeX scientific rendering where already qualified.

The existing boundary that software evidence alone cannot establish a physical claim is preserved.

### 2.3 Ω Multidirectional Omni Compiler

Reuse `omega_omni_compiler` for:

- UniversalIR routing;
- representation nodes and atomic provenance;
- PDFIR and real parser courts;
- loss accounting / LossTensor;
- QuantityIR, EquationIR, TableIR and CitationIR;
- reconciliation/HOLD semantics;
- exact renderer absorption and CI-native PDF readback.

R5 extends this substrate with report-specific objects and validators; it does not replace the Omni transformation fabric.

### 2.4 Exact-head qualification

The system inherits the repository's exact-head discipline. Generated artifacts and receipts are bound to exact source commits, exact inputs and exact hashes. Historical receipts with identity inconsistencies remain negative evidence rather than being silently rewritten.

---

## 3. Target capabilities

R5 must support two principal directions.

### 3.1 Knowledge -> report

```text
Research objects
  -> scientific-report graph
  -> validation courts
  -> report plan
  -> section compiler
  -> figure/table compiler
  -> renderer
  -> PDF/DOCX/Markdown/LaTeX/HTML
  -> readback
  -> receipt
```

### 3.2 Report -> knowledge

```text
PDF/DOCX/Markdown/LaTeX
  -> exact artifact identity
  -> parser tournament
  -> representation graph
  -> scientific object candidates
  -> reconciliation courts
  -> report graph
  -> residual/contradiction analysis
  -> human/authorized adjudication where required
```

Reverse compilation never claims to reconstruct the unique original source or author intent.

---

## 4. Canonical scientific-report object model

Create a report-domain IR that references existing Omni/Scientific objects instead of copying them.

### 4.1 Core objects

- `ReportProjectIR`
- `RequirementIR`
- `ConstraintIR`
- `AssumptionIR`
- `ConceptTermIR`
- `MethodIR`
- `DatasetRefIR`
- `ExperimentRefIR`
- `ResultIR`
- `ClaimRefIR`
- `EvidenceRefIR`
- `FigureIR`
- `ReportTableIR`
- `InterpretationIR`
- `ConclusionIR`
- `ResidualIR`
- `ContradictionIR`
- `ReportSectionIR`
- `ReportManifestIR`
- `ReportCrystalReceipt`

`ClaimRefIR` and `EvidenceRefIR` point to the scientific-writing/evidence objects. Numeric/equation/table/citation primitives point to existing Omni specialized IRs.

### 4.2 Shared minimum metadata

Every report-domain object carries:

```text
id
kind
status
scope
source/provenance ids
created_from transform id
confidence axes where meaningful
validation findings
supersedes/superseded_by where meaningful
```

The design avoids a single vague scalar confidence score when the underlying system can preserve separate extraction, identity, support and validation dimensions.

### 4.3 Status model

Use conservative states compatible with the existing kernel and scientific pipeline:

- `PROVISIONAL`
- `OBSERVED_CANDIDATE`
- `SUPPORTED`
- `MEASURED`
- `VERIFIED_ENGINEERING`
- `HOLD`
- `CONTRADICTED`
- `RESIDUAL`
- `REJECTED`
- `SUPERSEDED`
- `CRYSTALLIZED`

`CRYSTALLIZED` means the report state and its receipt were frozen reproducibly. It does **not** mean the scientific claims are universally true.

---

## 5. Claim/evidence/proof-cone graph

The report compiler treats the paragraph as presentation, not the primary reasoning unit.

Canonical dependency flow:

```text
Source/Artifact
  -> Dataset/Observation
  -> Method/Experiment
  -> Result
  -> Claim
  -> Interpretation
  -> Conclusion
  -> Requirement satisfaction / recommendation
```

A `ProofCone` query reconstructs all upstream evidence and transformation lineage for any claim or conclusion.

If an upstream object is invalidated or superseded, downstream dependents become candidates for revalidation. R5 reports the impact; it does not silently rewrite conclusions.

---

## 6. Methodology compiler

Methodology becomes a first-class structured object.

`MethodIR` must encode, where applicable:

- objective;
- inputs;
- assumptions;
- constraints;
- ordered steps;
- instruments/tools;
- calculations/transforms;
- outputs;
- validation method;
- uncertainty/limitations;
- source and version identity.

The Methodology Compiler produces:

- reproducible prose;
- a process diagram specification;
- input/constraint/assumption tables;
- a validation checklist;
- residuals for missing methodological fields.

A method with missing critical validation information may compile as a draft but cannot receive a clean scientific-report qualification.

---

## 7. Terminology registry and consistency court

Create `ConceptTermIR` with:

- canonical term per language;
- explicit aliases;
- ambiguous terms;
- forbidden substitutions where domain-specific precision would be lost;
- definition/source;
- optional unit/dimension association.

The terminology court identifies:

- one concept referred to by inconsistent terminology;
- one ambiguous term mapped to multiple concepts;
- AI-generated wording not present in the accepted terminology registry;
- unauthorized terminology normalization.

The court proposes changes but preserves the original wording and provenance. Accepted normalization is emitted as an explicit transformation receipt.

---

## 8. Redundancy and semantic-duplication court

The report system must distinguish legitimate repeated context from accidental duplication.

Output classes:

- `EXACT_DUPLICATE`
- `NEAR_DUPLICATE`
- `SAME_CLAIM_DIFFERENT_WORDING`
- `LEGITIMATE_RECAP`
- `UNRESOLVED_SIMILARITY`

Deletion is never automatic. The compiler may render one canonical explanation and cross-reference it from other sections when the adjudication state allows it.

---

## 9. Figure and diagram court

`FigureIR` must carry:

- scientific question/purpose;
- source dataset/result ids;
- axes;
- units;
- legend metadata;
- uncertainty representation where applicable;
- caption;
- rendering provenance;
- orientation convention;
- claims supported/illustrated;
- accessibility metadata where available.

The court checks at minimum:

- missing axis labels;
- missing units;
- missing/inconsistent legends;
- missing source/result linkage;
- orientation inconsistency;
- untraceable figure inputs;
- unsupported scientific interpretation;
- rendering/readback failures.

### Orientation invariant

Default conventions:

- temporal/causal horizontal diagrams: left -> right;
- process/hierarchy vertical diagrams: top -> bottom.

Exceptions require explicit metadata and do not silently redefine the project convention.

---

## 10. Units and numeric integrity

Reuse existing `QuantityIR` and the numeric integrity court. Extend through a versioned unit/dimension registry instead of ad hoc string comparison.

R5 must preserve original numeric lexemes and original units in provenance even when a normalized view is produced.

No implicit unit conversion may be used as scientific evidence. Conversion is an explicit transformation with:

- source quantity;
- source unit;
- target unit;
- conversion rule/version;
- output quantity;
- receipt.

Uncertainty propagation is a separate bounded capability and must declare its method.

---

## 11. Residual engine

Residuals are first-class work items, not generic warnings.

Initial residual classes:

- `MISSING_EVIDENCE`
- `MISSING_SOURCE`
- `MISSING_UNIT`
- `MISSING_UNCERTAINTY`
- `MISSING_VALIDATION`
- `MISSING_DEFINITION`
- `UNRESOLVED_CONTRADICTION`
- `UNANSWERED_OBJECTIVE`
- `UNSUPPORTED_CONCLUSION`
- `ORPHAN_FIGURE`
- `ORPHAN_TABLE`
- `DUPLICATE_CONCEPT`
- `AMBIGUOUS_TERMINOLOGY`
- `NON_REPRODUCIBLE_METHOD`
- `UNRESOLVED_CITATION_SUPPORT`
- `RENDER_READBACK_FAILURE`

Residual severity is explicit. Critical residuals block crystallization. Noncritical residuals remain listed in the final receipt.

The metric `ResidualCount -> 0` is a work target, not proof of scientific truth.

---

## 12. Contradiction engine

A contradiction record contains:

- subject ids;
- conflicting statements/values;
- scope/condition comparison;
- provenance;
- whether the conflict is genuine, contextual, temporal, terminological or unresolved;
- adjudication status.

The system must prefer `HOLD` over inventing a reconciliation.

Contradiction search operates on the declared corpus. Absence of a detected contradiction is not evidence that no contradiction exists outside that corpus.

---

## 13. Report compiler

The report compiler consumes a validated `ReportManifestIR` and creates a deterministic report plan.

Default engineering/scientific structure:

1. Executive summary / abstract
2. Context and problem statement
3. Objectives
4. Requirements and success criteria
5. Inputs/data sources
6. Constraints
7. Assumptions
8. Methodology
9. Results
10. Analysis
11. Discussion
12. Uncertainty and limitations
13. Recommendation/decision where applicable
14. Conclusion
15. Future work
16. References
17. Appendices

Adapters may map the same canonical scientific state to institutional/journal templates without changing the underlying evidence graph.

### Canonical mapping checks

- every declared objective must map to at least one result or explicit unresolved residual;
- every conclusion must map to supporting claims/results;
- every figure/table must map to a purpose and source;
- every claim requiring evidence must satisfy its proof obligations or remain HOLD;
- every critical terminology conflict must be adjudicated before crystallization.

---

## 14. Renderer strategy

### 14.1 First-class qualified route

LaTeX -> PDF remains the first deeply qualified route because an exact renderer and CI-native PDF/readback lane already exist.

R5 generalizes the Battery-specific rendering capability into a report renderer contract without weakening current exact-source and readback gates.

### 14.2 Additional outputs

Add adapters in this order:

1. Markdown — deterministic review/debug view;
2. HTML — portable structured view;
3. DOCX — practical collaboration/export view;
4. additional institutional LaTeX templates.

A DOCX export being generated successfully does not inherit PDF qualification automatically. Each output adapter receives its own structural/readback court.

---

## 15. Reverse-ingest strategy

### 15.1 PDF

Reuse the existing two-parser PDF court, reconciliation logic, PDFIR and representation graph.

Extraction stages:

```text
exact bytes/hash
  -> independent parser observations
  -> representation graph
  -> specialized scientific candidate extraction
  -> cross-parser reconciliation
  -> candidate report objects
  -> validators
```

### 15.2 DOCX/Markdown/LaTeX

Implement adapters behind the same representation interface. They must preserve source ranges/locations and exact artifact identity whenever the format permits it.

### 15.3 AI assistance

AI extraction/generation may propose candidates, summaries, terminology mappings and rewrites. AI output receives explicit provenance and cannot self-authorize promotion to `SUPPORTED`, `MEASURED`, `VERIFIED_ENGINEERING` or `CRYSTALLIZED`.

---

## 16. Event, supersession and non-destruction model

R5 does not introduce an opaque mutable database as the only history source.

Every semantically meaningful change produces a versioned receipt/event containing:

- event id;
- object id/type;
- previous identity/version where applicable;
- new identity/version;
- reason;
- actor/agent class;
- evidence/input ids;
- exact code/source head;
- timestamp;
- transformation id;
- hashes of materialized artifacts when applicable.

Merge, normalization and supersession are explicit events. Rejected and superseded objects remain addressable for audit and rollback.

---

## 17. Report Crystal

A successful report crystallization emits a `ReportCrystalReceipt` containing at minimum:

- project/report id;
- exact repository source head;
- input artifact hashes;
- report-manifest hash;
- scientific object-set identity;
- unresolved residuals and their severities;
- unresolved contradictions;
- renderer identity/version;
- generated artifact hashes;
- readback results;
- validation court results;
- qualification boundaries;
- environment/toolchain identity sufficient for reproducibility.

A crystal is immutable. A subsequent correction produces a new crystal that supersedes the previous one; it does not rewrite historical receipts.

---

## 18. Family Drive mirror

### 18.1 Canonical responsibility split

- **GitHub repository:** canonical code, schemas, tests, machine-readable receipts and versioned architecture/specification.
- **Google Drive family repository:** human-readable project mirror, family decision material, selected generated reports and release receipts.

Drive must not become an alternate source of code truth.

### 18.2 Family-safe publication policy

The family mirror receives only artifacts explicitly classified for family visibility. Raw datasets, credentials, private research material, unpublished sensitive content and secrets are excluded by default.

Automatic external publication remains forbidden. Drive synchronization is a bounded authorized write into the designated family repository only.

### 18.3 Mirror layout

Under the designated family folder:

```text
Tristan Scientific Report Compiler/
  00 - README - Family View
  01 - Architecture and Design
  02 - Current Status and Residuals
  03 - Qualified Releases
  04 - Report Crystals
  05 - Decision Packets
```

Git commit ids and crystal/receipt hashes are embedded in family-facing documents so a Drive artifact can be traced back to the exact Git state.

---

## 19. Error handling and fail-closed behavior

Any of the following defaults to `HOLD` rather than silent repair:

- parser disagreement on a critical value;
- source/hash mismatch;
- unsupported claim/evidence pairing;
- unresolved unit disagreement;
- contradictory conclusions under the same scope;
- missing exact source anchor required by a renderer;
- failed readback gate;
- ambiguous terminology that changes scientific meaning;
- missing authority for publication/promotion.

Noncritical presentation errors may produce a draft artifact, but its receipt must record the failure and cannot claim clean qualification.

---

## 20. Testing strategy

R5 uses TDD and exact deterministic fixtures where possible.

### 20.1 Unit tests

Cover each IR validation rule and court independently.

### 20.2 Negative fixtures

Every critical validator must have fixtures that are expected to fail/HOLD, including:

- missing units;
- unsupported conclusion;
- repeated terminology drift;
- contradictory claims;
- orphan figures;
- non-reproducible methods;
- source/hash mismatch;
- parser disagreement;
- AI-generated unsupported claim.

### 20.3 Round-trip tests

For bounded fixtures:

```text
Scientific/report IR -> document -> reverse ingest -> compared invariants
```

A round-trip pass means selected invariants were preserved, not that prose identity or scientific truth was preserved.

### 20.4 Exact-head CI

Required lanes:

- existing kernel CI;
- existing Omni CI;
- existing Scientific Writing CI;
- report IR + validators;
- report compile fixtures;
- PDF build/readback;
- reverse-ingest regression;
- family-mirror manifest generation in dry-run mode.

Drive writes are not required for ordinary CI. The CI lane generates the exact mirror manifest that an authorized sync action would publish.

---

## 21. Security and authority boundaries

- No credentials or tokens are stored in report artifacts or receipts.
- No deletion of external Drive content is performed by the report compiler.
- No automatic public release is performed.
- Family Drive sync is additive/versioned unless an explicit authorized replacement policy is invoked.
- Scientific status promotion and external publication remain separate authorities.
- Code capability never implies permission to publish, delete or disclose.

---

## 22. Subproject decomposition

This architecture is intentionally larger than one implementation plan. It is decomposed into independently reviewable releases.

### R5A — Report Graph + Core Validators

Deliverables:

- report-domain IR;
- terminology registry;
- methodology object/compiler diagnostics;
- residual engine;
- contradiction records;
- claim/objective/conclusion traceability;
- unit tests and negative fixtures.

This is the first implementation plan after the design is approved.

### R5B — General Report Compiler + LaTeX/PDF Qualification

Deliverables:

- ReportManifest compiler;
- deterministic section plan;
- generalized scientific renderer contract;
- LaTeX output;
- exact-head PDF build/readback;
- ReportCrystalReceipt.

### R5C — Reverse Report Compiler

Deliverables:

- PDFIR -> report-domain candidate extraction;
- specialized quantity/equation/table/citation integration;
- reconciliation and contradiction feed;
- bounded round-trip court.

### R5D — Markdown/HTML/DOCX Adapters

Deliverables:

- deterministic Markdown;
- structured HTML;
- DOCX export/readback court;
- format-specific qualification receipts.

### R5E — Family Drive Mirror

Deliverables:

- family-safe mirror manifest;
- release/crystal summary generator;
- bounded Drive sync adapter;
- Git<->Drive traceability receipts;
- no-delete policy tests/dry runs.

---

## 23. Acceptance criteria for the architecture

The architecture is considered implemented only when all of the following are demonstrated on at least one bounded real report fixture:

1. Exact artifact/source identity is recorded.
2. The report is represented by typed report/scientific objects.
3. Objective -> result -> claim -> conclusion traceability is queryable.
4. A terminology inconsistency is detected by a regression fixture.
5. A duplicate/near-duplicate passage is surfaced without destructive deletion.
6. A missing figure unit/label or orphan figure is detected.
7. A methodological omission produces an explicit residual.
8. An unsupported or contradictory conclusion enters HOLD.
9. A report is deterministically compiled to LaTeX and qualified through PDF/readback CI.
10. The exact generated artifact hashes appear in a ReportCrystalReceipt.
11. Reverse ingest reconstructs bounded candidate invariants from the generated PDF.
12. Round-trip comparison reports preserved/lost/unknown invariants explicitly.
13. A family-safe mirror manifest is produced and traceable to the Git head/crystal.
14. No test or receipt claims `ScientificPASS` merely because formatting, parsing, compilation, CI or readback passed.

---

## 24. Explicit non-goals for R5

R5 does not attempt to:

- prove arbitrary scientific claims automatically;
- replace peer review;
- infer missing experimental evidence;
- automatically publish externally;
- automatically delete or overwrite family Drive content;
- build a general ontology of all science;
- make every historical Tristan artifact canonical in one migration;
- guarantee semantic equivalence across every document format;
- treat AI wording as authoritative terminology.

These boundaries are deliberate complexity controls, not missing features.

---

## 25. Implementation order

After written-spec review, implementation proceeds:

```text
R5A
 -> exact-head qualification
 -> R5B
 -> exact-head qualification + first Report Crystal
 -> R5C
 -> round-trip qualification
 -> R5D
 -> adapter-specific qualification
 -> R5E
 -> bounded family Drive sync
```

Each release must be independently testable and may remain HOLD without weakening the preceding qualified capabilities.

---

## 26. Final design invariant

The system's purpose is not to make reports sound more convincing. It is to make the path from **source -> method -> result -> claim -> conclusion -> artifact** more explicit, reproducible, challengeable and recoverable.

A polished report with weak evidence must remain visibly weak. A parser disagreement must remain visible. A contradictory result must remain visible. A historical failure remains evidence. A Drive mirror remains a mirror. Git/source identity and scientific provenance remain separable but traceable.
