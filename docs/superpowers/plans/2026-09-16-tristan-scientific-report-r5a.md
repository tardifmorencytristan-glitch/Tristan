# Tristan Scientific Report Compiler R5A Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first independently testable R5 release: a conservative typed scientific-report graph with terminology, methodology, residual, contradiction, traceability, and integrated report-court validation.

**Architecture:** R5A extends `omega_scientific_writing` rather than creating a new silo. It preserves the existing dict-based ScientificIR interfaces for claims/evidence while adding focused frozen dataclasses for report-domain objects. Courts return deterministic finding dictionaries and fail closed to `HOLD`; they do not render final reports or promote scientific truth.

**Tech Stack:** Python >=3.11, standard library only, `dataclasses`, `unittest`, existing `omega_scientific_writing` modules, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-16-tristan-scientific-report-compiler-design.md`

## Global Constraints

- Preserve `Generated != Verified` and `CompilationPASS != ScientificPASS`.
- Preserve `Simulation != Measurement`, `Formatting != Evidence`, `ParserAgreement != Truth`, `Artifact != Knowledge`, `Capability != Authority`, and `ReceiptClaim != ArtifactBytes`.
- Do not duplicate or replace `omega_omni_compiler` specialized IRs such as QuantityIR, EquationIR, TableIR, or CitationIR.
- Do not silently promote extracted/AI-generated content to `SUPPORTED`, `MEASURED`, `VERIFIED_ENGINEERING`, or `CRYSTALLIZED`.
- `HOLD` is the required default for unresolved critical ambiguity, contradiction, unsupported conclusions, or critical residuals.
- No destructive deletion, no external publication, and no Drive write logic in R5A.
- Python floor remains `>=3.11`; add no runtime dependencies.
- Tests use the repository's existing `python -m unittest discover -s omega_scientific_writing/tests -v` convention.
- R5A excludes final report rendering, generalized PDF qualification, reverse compilation, DOCX/HTML adapters, and automated Drive synchronization; those remain R5B-R5E.

---

## File Structure

### New source files

- `omega_scientific_writing/src/report_ir.py` — frozen report-domain dataclasses, validation, deterministic serialization.
- `omega_scientific_writing/src/terminology_court.py` — canonical-term/alias/ambiguity checks.
- `omega_scientific_writing/src/methodology_court.py` — completeness/reproducibility diagnostics for `MethodIR`.
- `omega_scientific_writing/src/residual_engine.py` — typed residual generation and crystallization-blocker classification.
- `omega_scientific_writing/src/report_traceability.py` — objective/result/claim/conclusion dependency index and proof-cone traversal.
- `omega_scientific_writing/src/contradiction_court.py` — explicit scoped contradictions and fail-closed unresolved-conflict findings.
- `omega_scientific_writing/src/report_court.py` — composition root combining R5A courts plus existing scientific claim/evidence/proof-obligation checks.

### New tests

- `omega_scientific_writing/tests/test_r5a_report_ir.py`
- `omega_scientific_writing/tests/test_r5a_terminology.py`
- `omega_scientific_writing/tests/test_r5a_methodology_residuals.py`
- `omega_scientific_writing/tests/test_r5a_traceability_contradictions.py`
- `omega_scientific_writing/tests/test_r5a_report_court.py`

### New fixtures/docs/CI

- `omega_scientific_writing/examples/report_r5a_valid.json`
- `omega_scientific_writing/examples/report_r5a_invalid.json`
- `omega_scientific_writing/R5A.md`
- `.github/workflows/omega-scientific-report-r5a.yml`

### Existing files intentionally reused, not rewritten

- `omega_scientific_writing/src/scientific_types.py`
- `omega_scientific_writing/src/proof_obligations.py`
- `omega_scientific_writing/src/scientific_lint.py`
- `omega_scientific_writing/src/argument_graph.py`
- `omega_scientific_writing/src/epistemic_diff.py`
- `omega_omni_compiler/src/scientific_ir.py`

---

### Task 1: Report-domain IR and deterministic validation

**Files:**
- Create: `omega_scientific_writing/src/report_ir.py`
- Test: `omega_scientific_writing/tests/test_r5a_report_ir.py`

**Interfaces:**
- Produces: `ReportMeta`, `ObjectiveIR`, `RequirementIR`, `ConstraintIR`, `AssumptionIR`, `ConceptTermIR`, `MethodIR`, `ResultIR`, `FigureAxisIR`, `FigureIR`, `InterpretationIR`, `ConclusionIR`, `ResidualIR`, `ContradictionIR`, `ReportGraphIR`, `validate_report_graph(graph) -> list[dict]`, `report_graph_to_dict(graph) -> dict`.
- Consumes: no new R5A interfaces.

- [ ] **Step 1: Write failing IR tests**

Create `omega_scientific_writing/tests/test_r5a_report_ir.py` with:

```python
import unittest

from omega_scientific_writing.src.report_ir import (
    ReportMeta, ObjectiveIR, RequirementIR, MethodIR, ResultIR,
    ConclusionIR, ReportGraphIR, validate_report_graph, report_graph_to_dict,
)


class R5AReportIRTests(unittest.TestCase):
    def test_valid_graph_serializes_deterministically(self):
        graph = ReportGraphIR(
            project_id="P1",
            objectives=(ObjectiveIR(ReportMeta("O1"), "Measure thermal compliance"),),
            requirements=(RequirementIR(ReportMeta("RQ1"), "Tmax < 45 C", "max_temperature_c < 45"),),
            methods=(MethodIR(
                meta=ReportMeta("M1"),
                objective="Measure maximum temperature",
                input_ids=("D1",),
                steps=("acquire temperature", "compute maximum"),
                output_ids=("R1",),
                validation_methods=("sensor calibration check",),
            ),),
            results=(ResultIR(ReportMeta("R1"), "Tmax = 42.1 C", evidence_ids=("E1",)),),
            conclusions=(ConclusionIR(
                ReportMeta("C1"),
                "Thermal requirement is satisfied in the stated test scope",
                claim_ids=("CL1",), result_ids=("R1",), requirement_ids=("RQ1",),
            ),),
        )
        self.assertEqual(validate_report_graph(graph), [])
        first = report_graph_to_dict(graph)
        second = report_graph_to_dict(graph)
        self.assertEqual(first, second)
        self.assertEqual(first["project_id"], "P1")

    def test_duplicate_ids_are_rejected(self):
        graph = ReportGraphIR(
            project_id="P1",
            objectives=(ObjectiveIR(ReportMeta("X"), "A"),),
            results=(ResultIR(ReportMeta("X"), "B"),),
        )
        codes = {f["code"] for f in validate_report_graph(graph)}
        self.assertIn("REPORT_DUPLICATE_OBJECT_ID", codes)

    def test_unknown_status_is_rejected(self):
        graph = ReportGraphIR(
            project_id="P1",
            objectives=(ObjectiveIR(ReportMeta("O1", status="MAGIC"), "A"),),
        )
        codes = {f["code"] for f in validate_report_graph(graph)}
        self.assertIn("REPORT_STATUS_UNKNOWN", codes)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify it fails**

Run:

```bash
python -m unittest omega_scientific_writing.tests.test_r5a_report_ir -v
```

Expected: import failure because `omega_scientific_writing.src.report_ir` does not exist.

- [ ] **Step 3: Implement the minimal typed IR**

Create `omega_scientific_writing/src/report_ir.py`. Use `@dataclass(frozen=True)` throughout. Define:

```python
REPORT_STATUSES = {
    "PROVISIONAL", "OBSERVED_CANDIDATE", "SUPPORTED", "MEASURED",
    "VERIFIED_ENGINEERING", "HOLD", "CONTRADICTED", "RESIDUAL",
    "REJECTED", "SUPERSEDED", "CRYSTALLIZED",
}

@dataclass(frozen=True)
class ReportMeta:
    id: str
    status: str = "PROVISIONAL"
    scope: str = ""
    provenance_ids: tuple[str, ...] = ()
    transform_id: str = ""
```

Define the remaining dataclasses with these exact fields:

```python
ObjectiveIR(meta, statement)
RequirementIR(meta, statement, success_criterion)
ConstraintIR(meta, statement)
AssumptionIR(meta, statement, justification="")
ConceptTermIR(meta, canonical_terms, aliases=(), ambiguous_terms=(), forbidden_substitutions=(), definition="", source_ids=())
MethodIR(meta, objective, input_ids=(), assumption_ids=(), constraint_ids=(), steps=(), tool_ids=(), output_ids=(), validation_methods=(), limitations=())
ResultIR(meta, statement, evidence_ids=(), quantity_ids=())
FigureAxisIR(label, unit="")
FigureIR(meta, purpose, source_ids=(), claim_ids=(), axes=(), caption="", orientation="", uncertainty_declared=False)
InterpretationIR(meta, statement, result_ids=(), claim_ids=())
ConclusionIR(meta, statement, claim_ids=(), result_ids=(), requirement_ids=())
ResidualIR(meta, residual_type, target_id, severity, description, resolution_state="OPEN")
ContradictionIR(meta, subject_ids, conflict_type, description, adjudication_state="UNRESOLVED")
ReportGraphIR(project_id, objectives=(), requirements=(), constraints=(), assumptions=(), concepts=(), methods=(), results=(), figures=(), interpretations=(), conclusions=(), residuals=(), contradictions=())
```

Implement `validate_report_graph` to emit deterministic dictionaries with keys `severity`, `code`, `object`, and optional `detail`. It must reject an empty `project_id`, blank object ids, duplicate ids across all collections, and statuses outside `REPORT_STATUSES`.

Implement `report_graph_to_dict` with `dataclasses.asdict`; sort only unordered set-like diagnostics, never reorder declared scientific sequences such as methodology steps.

- [ ] **Step 4: Run the IR tests**

```bash
python -m unittest omega_scientific_writing.tests.test_r5a_report_ir -v
```

Expected: all tests PASS.

- [ ] **Step 5: Run the existing scientific-writing suite for regression**

```bash
python -m unittest discover -s omega_scientific_writing/tests -v
```

Expected: existing tests plus the new IR tests PASS.

- [ ] **Step 6: Commit**

```bash
git add omega_scientific_writing/src/report_ir.py omega_scientific_writing/tests/test_r5a_report_ir.py
git commit -m "feat(scientific-report): add R5A report-domain IR"
```

---

### Task 2: Terminology consistency court

**Files:**
- Create: `omega_scientific_writing/src/terminology_court.py`
- Test: `omega_scientific_writing/tests/test_r5a_terminology.py`

**Interfaces:**
- Consumes: `ConceptTermIR` from Task 1.
- Produces: `normalize_term(text, concepts) -> tuple[str | None, list[dict]]`, `audit_terminology(usages, concepts) -> list[dict]`.

- [ ] **Step 1: Write failing terminology tests**

```python
import unittest
from omega_scientific_writing.src.report_ir import ReportMeta, ConceptTermIR
from omega_scientific_writing.src.terminology_court import audit_terminology


class R5ATerminologyTests(unittest.TestCase):
    def setUp(self):
        self.concepts = (
            ConceptTermIR(
                ReportMeta("TERM1"),
                canonical_terms=(("fr", "débit volumique"), ("en", "volumetric flow rate")),
                aliases=("débit", "volume flow rate"),
                ambiguous_terms=("flux",),
                forbidden_substitutions=("flow",),
                definition="Volume transported per unit time",
                source_ids=("SRC1",),
            ),
        )

    def test_alias_is_detected_without_losing_canonical_identity(self):
        findings = audit_terminology(
            [{"object_id": "P1", "language": "fr", "term": "débit"}], self.concepts
        )
        self.assertTrue(any(f["code"] == "TERM_ALIAS_USED" for f in findings))
        self.assertFalse(any(f["severity"] == "ERROR" for f in findings))

    def test_ambiguous_term_holds(self):
        findings = audit_terminology(
            [{"object_id": "P2", "language": "fr", "term": "flux"}], self.concepts
        )
        self.assertTrue(any(f["code"] == "TERM_AMBIGUOUS" and f["severity"] == "HOLD" for f in findings))

    def test_unknown_ai_term_is_not_auto_accepted(self):
        findings = audit_terminology(
            [{"object_id": "P3", "language": "fr", "term": "hyperflux", "origin": "ai_generated"}], self.concepts
        )
        self.assertTrue(any(f["code"] == "AI_TERM_UNREGISTERED" for f in findings))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify it fails**

```bash
python -m unittest omega_scientific_writing.tests.test_r5a_terminology -v
```

Expected: import failure for `terminology_court`.

- [ ] **Step 3: Implement the terminology court**

Implement exact matching after Unicode-aware `casefold().strip()` normalization. Do not use fuzzy matching in R5A. Required finding codes:

```text
TERM_ALIAS_USED        severity WARN
TERM_AMBIGUOUS         severity HOLD
TERM_FORBIDDEN_SUBSTITUTION severity HOLD
TERM_UNKNOWN           severity WARN
AI_TERM_UNREGISTERED   severity HOLD
TERM_CANONICAL_LANGUAGE_MISSING severity HOLD
```

The court may propose the canonical term in `detail`, but it must not mutate source text.

- [ ] **Step 4: Run terminology and regression tests**

```bash
python -m unittest omega_scientific_writing.tests.test_r5a_terminology -v
python -m unittest discover -s omega_scientific_writing/tests -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add omega_scientific_writing/src/terminology_court.py omega_scientific_writing/tests/test_r5a_terminology.py
git commit -m "feat(scientific-report): add terminology consistency court"
```

---

### Task 3: Methodology diagnostics and residual engine

**Files:**
- Create: `omega_scientific_writing/src/methodology_court.py`
- Create: `omega_scientific_writing/src/residual_engine.py`
- Test: `omega_scientific_writing/tests/test_r5a_methodology_residuals.py`

**Interfaces:**
- Consumes: `MethodIR`, `ReportGraphIR`, `ResidualIR`.
- Produces: `audit_method(method) -> list[dict]`, `derive_residuals(graph, external_findings=()) -> tuple[ResidualIR, ...]`, `blocking_residuals(residuals) -> tuple[ResidualIR, ...]`.

- [ ] **Step 1: Write failing tests**

```python
import unittest
from omega_scientific_writing.src.report_ir import ReportMeta, MethodIR, ObjectiveIR, ReportGraphIR
from omega_scientific_writing.src.methodology_court import audit_method
from omega_scientific_writing.src.residual_engine import derive_residuals, blocking_residuals


class R5AMethodologyResidualTests(unittest.TestCase):
    def test_method_without_validation_is_non_reproducible_residual(self):
        method = MethodIR(
            meta=ReportMeta("M1"), objective="Measure X",
            input_ids=("D1",), steps=("measure X",), output_ids=("R1",),
            validation_methods=(),
        )
        codes = {f["code"] for f in audit_method(method)}
        self.assertIn("METHOD_VALIDATION_MISSING", codes)

    def test_unanswered_objective_becomes_critical_residual(self):
        graph = ReportGraphIR(
            project_id="P1",
            objectives=(ObjectiveIR(ReportMeta("O1"), "Determine X"),),
        )
        residuals = derive_residuals(graph)
        types = {r.residual_type for r in residuals}
        self.assertIn("UNANSWERED_OBJECTIVE", types)
        self.assertEqual(len(blocking_residuals(residuals)), 1)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Verify failure**

```bash
python -m unittest omega_scientific_writing.tests.test_r5a_methodology_residuals -v
```

Expected: missing-module failure.

- [ ] **Step 3: Implement methodology checks**

`audit_method` must emit:

```text
METHOD_OBJECTIVE_MISSING      ERROR
METHOD_INPUTS_MISSING         HOLD
METHOD_STEPS_MISSING          ERROR
METHOD_OUTPUTS_MISSING        HOLD
METHOD_VALIDATION_MISSING     HOLD
METHOD_ASSUMPTION_UNJUSTIFIED WARN (when an attached assumption lacks justification; this cross-object check is added through optional lookup in report_court)
```

Do not infer steps, inputs, outputs, validation, or assumptions.

- [ ] **Step 4: Implement residual derivation**

`derive_residuals` must deterministically generate stable ids of the form `RES:<TYPE>:<TARGET>`. Initial R5A types and blocker policy:

```text
MISSING_EVIDENCE              CRITICAL
MISSING_SOURCE                HIGH
MISSING_UNIT                  HIGH
MISSING_UNCERTAINTY           HIGH
MISSING_VALIDATION            CRITICAL
MISSING_DEFINITION            MEDIUM
UNRESOLVED_CONTRADICTION      CRITICAL
UNANSWERED_OBJECTIVE          CRITICAL
UNSUPPORTED_CONCLUSION        CRITICAL
ORPHAN_FIGURE                 HIGH
ORPHAN_TABLE                  HIGH
DUPLICATE_CONCEPT             HIGH
AMBIGUOUS_TERMINOLOGY         CRITICAL
NON_REPRODUCIBLE_METHOD       CRITICAL
UNRESOLVED_CITATION_SUPPORT   CRITICAL
RENDER_READBACK_FAILURE       CRITICAL
```

`blocking_residuals` returns severity `CRITICAL` residuals whose `resolution_state` is not `RESOLVED`.

- [ ] **Step 5: Run tests**

```bash
python -m unittest omega_scientific_writing.tests.test_r5a_methodology_residuals -v
python -m unittest discover -s omega_scientific_writing/tests -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add omega_scientific_writing/src/methodology_court.py omega_scientific_writing/src/residual_engine.py omega_scientific_writing/tests/test_r5a_methodology_residuals.py
git commit -m "feat(scientific-report): add methodology and residual courts"
```

---

### Task 4: Traceability index, proof cones, and contradiction court

**Files:**
- Create: `omega_scientific_writing/src/report_traceability.py`
- Create: `omega_scientific_writing/src/contradiction_court.py`
- Test: `omega_scientific_writing/tests/test_r5a_traceability_contradictions.py`

**Interfaces:**
- Consumes: `ReportGraphIR`, existing claim dictionaries.
- Produces: `build_traceability_index(graph, claims) -> dict`, `proof_cone(target_id, index) -> dict`, `audit_traceability(graph, claims) -> list[dict]`, `audit_contradictions(graph) -> list[dict]`.

- [ ] **Step 1: Write failing traceability/contradiction tests**

```python
import unittest
from omega_scientific_writing.src.report_ir import (
    ReportMeta, ObjectiveIR, ResultIR, ConclusionIR, ContradictionIR, ReportGraphIR,
)
from omega_scientific_writing.src.report_traceability import build_traceability_index, proof_cone, audit_traceability
from omega_scientific_writing.src.contradiction_court import audit_contradictions


class R5ATraceabilityContradictionTests(unittest.TestCase):
    def test_conclusion_proof_cone_reaches_result_and_claim(self):
        graph = ReportGraphIR(
            project_id="P1",
            objectives=(ObjectiveIR(ReportMeta("O1"), "Determine X"),),
            results=(ResultIR(ReportMeta("R1"), "X=2", evidence_ids=("E1",)),),
            conclusions=(ConclusionIR(ReportMeta("C1"), "X criterion met", claim_ids=("CL1",), result_ids=("R1",)),),
        )
        claims = [{"id": "CL1", "evidence_ids": ["E1"], "scope": "test A"}]
        index = build_traceability_index(graph, claims)
        cone = proof_cone("C1", index)
        self.assertIn("R1", cone["reachable_ids"])
        self.assertIn("CL1", cone["reachable_ids"])
        self.assertIn("E1", cone["reachable_ids"])

    def test_conclusion_without_support_holds(self):
        graph = ReportGraphIR(
            project_id="P1",
            conclusions=(ConclusionIR(ReportMeta("C1"), "unsupported"),),
        )
        codes = {f["code"] for f in audit_traceability(graph, [])}
        self.assertIn("CONCLUSION_UNSUPPORTED", codes)

    def test_unresolved_contradiction_holds(self):
        graph = ReportGraphIR(
            project_id="P1",
            contradictions=(ContradictionIR(
                ReportMeta("X1"), subject_ids=("CL1", "CL2"),
                conflict_type="STATEMENT", description="same scope conflict",
            ),),
        )
        findings = audit_contradictions(graph)
        self.assertTrue(any(f["code"] == "CONTRADICTION_UNRESOLVED" and f["severity"] == "HOLD" for f in findings))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Verify failure**

```bash
python -m unittest omega_scientific_writing.tests.test_r5a_traceability_contradictions -v
```

Expected: missing-module failure.

- [ ] **Step 3: Implement deterministic dependency index**

Represent the index as:

```python
{
    "upstream": {target_id: tuple(source_ids)},
    "downstream": {source_id: tuple(target_ids)},
    "known_ids": tuple(sorted(all_ids)),
}
```

Required relationships:

```text
evidence -> claim
result -> conclusion
claim -> conclusion
requirement -> conclusion
result -> interpretation
claim -> interpretation
```

`proof_cone` traverses upstream only, returns `target_id`, `reachable_ids` sorted deterministically, and `missing_ids` for dangling references. It must never fabricate a missing node.

`audit_traceability` emits at least:

```text
TRACE_DANGLING_REFERENCE ERROR
CONCLUSION_UNSUPPORTED   HOLD
OBJECTIVE_UNANSWERED     HOLD
RESULT_WITHOUT_EVIDENCE  HOLD
```

An objective counts as answered in R5A only when at least one result or conclusion explicitly references its id through a declared link. Add `objective_ids: tuple[str, ...] = ()` to `ResultIR` and `ConclusionIR` in Task 1's module before implementing this check, with backward-compatible defaults.

- [ ] **Step 4: Implement contradiction court**

Required states:

```text
UNRESOLVED -> HOLD
CONTEXTUAL -> WARN
TEMPORAL -> WARN
TERMINOLOGICAL -> HOLD until terminology court resolves it
RESOLVED -> no blocking finding
```

Do not infer that different scopes resolve a contradiction unless the contradiction record explicitly declares `adjudication_state="CONTEXTUAL"`.

- [ ] **Step 5: Run tests and regression suite**

```bash
python -m unittest omega_scientific_writing.tests.test_r5a_traceability_contradictions -v
python -m unittest discover -s omega_scientific_writing/tests -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add omega_scientific_writing/src/report_ir.py omega_scientific_writing/src/report_traceability.py omega_scientific_writing/src/contradiction_court.py omega_scientific_writing/tests/test_r5a_traceability_contradictions.py
git commit -m "feat(scientific-report): add proof cones and contradiction court"
```

---

### Task 5: Integrated R5A report court with existing scientific semantics

**Files:**
- Create: `omega_scientific_writing/src/report_court.py`
- Test: `omega_scientific_writing/tests/test_r5a_report_court.py`

**Interfaces:**
- Consumes: `validate_claim_types`, `evaluate_obligations`, `scientific_lint.lint`, all R5A courts.
- Produces: `evaluate_report(doc: dict, graph: ReportGraphIR) -> dict`.

- [ ] **Step 1: Write failing integration tests**

```python
import unittest
from omega_scientific_writing.src.report_ir import (
    ReportMeta, ObjectiveIR, MethodIR, ResultIR, ConclusionIR, ReportGraphIR,
)
from omega_scientific_writing.src.report_court import evaluate_report


class R5AReportCourtTests(unittest.TestCase):
    def test_clean_bounded_packet_passes_r5a_structure(self):
        doc = {
            "claims": [{
                "id": "CL1", "statement": "temperature remains below limit",
                "claim_type": "EMPIRICAL", "status": "MEASURED", "scope": "test A",
                "uncertainty": "+/-0.4 C", "evidence_ids": ["E1"],
                "obligations_satisfied": [
                    "measurement_or_experiment", "uncertainty", "sample_or_acquisition_protocol",
                    "controls_or_baseline", "limitations",
                ],
            }],
            "evidence": [{"id": "E1", "kind": "measurement"}],
            "equations": [], "figures": [], "citations": [],
            "results": [{"id": "R1", "evidence_ids": ["E1"]}],
        }
        graph = ReportGraphIR(
            project_id="P1",
            objectives=(ObjectiveIR(ReportMeta("O1"), "Verify thermal limit"),),
            methods=(MethodIR(
                ReportMeta("M1"), "Measure maximum temperature",
                input_ids=("D1",), steps=("measure", "compute maximum"),
                output_ids=("R1",), validation_methods=("calibration check",),
            ),),
            results=(ResultIR(ReportMeta("R1"), "42.1 +/- 0.4 C", evidence_ids=("E1",), objective_ids=("O1",)),),
            conclusions=(ConclusionIR(
                ReportMeta("C1"), "limit satisfied in test A",
                claim_ids=("CL1",), result_ids=("R1",), objective_ids=("O1",),
            ),),
        )
        out = evaluate_report(doc, graph)
        self.assertEqual(out["verdict"], "PASS")
        self.assertEqual(out["blocking_residuals"], [])

    def test_unsupported_conclusion_forces_hold(self):
        out = evaluate_report({}, ReportGraphIR(
            project_id="P1",
            conclusions=(ConclusionIR(ReportMeta("C1"), "unsupported"),),
        ))
        self.assertEqual(out["verdict"], "HOLD")
        self.assertTrue(any(f["code"] == "CONCLUSION_UNSUPPORTED" for f in out["findings"]))

    def test_repository_pass_does_not_emit_scientific_pass(self):
        out = evaluate_report({}, ReportGraphIR(project_id="P1"))
        self.assertNotEqual(out.get("scientific_status"), "ScientificPASS")
        self.assertIn("CompilationPASS != ScientificPASS", out["invariants"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Verify failure**

```bash
python -m unittest omega_scientific_writing.tests.test_r5a_report_court -v
```

Expected: missing-module failure.

- [ ] **Step 3: Implement `evaluate_report` composition**

Evaluation order:

```text
1. validate_report_graph
2. existing scientific_lint.lint
3. validate_claim_types
4. evaluate_obligations
5. audit each methodology
6. audit traceability
7. audit contradictions
8. terminology findings supplied from doc["terminology_usages"]
9. derive residuals from graph + findings
10. classify blocking residuals
11. verdict = HOLD if any ERROR/HOLD or blocking residual; else PASS
```

Return exactly:

```python
{
    "verdict": "PASS" or "HOLD",
    "scientific_status": "NOT_ESTABLISHED_BY_REPORT_COURT",
    "findings": [...],
    "residuals": [...],
    "blocking_residuals": [...],
    "traceability": {...},
    "invariants": [
        "Generated != Verified",
        "CompilationPASS != ScientificPASS",
        "Simulation != Measurement",
        "Formatting != Evidence",
        "Capability != Authority",
    ],
}
```

Sort findings by `(severity, code, object, repr(detail))` only at the output boundary for deterministic receipts; do not change scientific sequence order inside objects.

- [ ] **Step 4: Run integration and full tests**

```bash
python -m unittest omega_scientific_writing.tests.test_r5a_report_court -v
python -m unittest discover -s omega_scientific_writing/tests -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add omega_scientific_writing/src/report_court.py omega_scientific_writing/tests/test_r5a_report_court.py
git commit -m "feat(scientific-report): compose conservative R5A report court"
```

---

### Task 6: Real fixtures, CLI court, documentation, and exact-head CI

**Files:**
- Create: `omega_scientific_writing/examples/report_r5a_valid.json`
- Create: `omega_scientific_writing/examples/report_r5a_invalid.json`
- Modify: `omega_scientific_writing/src/report_court.py`
- Create: `omega_scientific_writing/R5A.md`
- Create: `.github/workflows/omega-scientific-report-r5a.yml`
- Test: `omega_scientific_writing/tests/test_r5a_report_court.py`

**Interfaces:**
- Produces CLI `python -m omega_scientific_writing.src.report_court <json>` returning exit 0 for PASS and exit 1 for HOLD.
- Produces exact-head CI qualification for R5A only.

- [ ] **Step 1: Add fixture-loading integration test**

Extend `test_r5a_report_court.py` with a test that loads both fixture files through a public helper `load_report_packet(path) -> tuple[dict, ReportGraphIR]`, then asserts valid fixture PASS and invalid fixture HOLD.

The valid fixture must include one objective, requirement, method, measured result, empirical claim with measurement evidence, conclusion, and canonical term usage.

The invalid fixture must contain all of these deliberate defects:

```text
- one unanswered objective
- one method without validation
- one unsupported conclusion
- one ambiguous terminology use
- one unresolved contradiction
```

Assert the invalid output contains `OBJECTIVE_UNANSWERED`, `METHOD_VALIDATION_MISSING`, `CONCLUSION_UNSUPPORTED`, `TERM_AMBIGUOUS`, and `CONTRADICTION_UNRESOLVED`.

- [ ] **Step 2: Verify fixture test fails before fixtures/helper exist**

```bash
python -m unittest omega_scientific_writing.tests.test_r5a_report_court -v
```

Expected: failure for missing fixture/helper.

- [ ] **Step 3: Implement packet loader and CLI**

The packet JSON top level is:

```json
{
  "scientific_ir": {},
  "report_graph": {
    "project_id": "P1",
    "objectives": [],
    "requirements": [],
    "constraints": [],
    "assumptions": [],
    "concepts": [],
    "methods": [],
    "results": [],
    "figures": [],
    "interpretations": [],
    "conclusions": [],
    "residuals": [],
    "contradictions": []
  }
}
```

Implement explicit dictionary-to-dataclass constructors in `report_ir.py`; do not use unsafe dynamic class lookup. Unknown object fields cause `ValueError` instead of being silently ignored.

CLI behavior:

```bash
python -m omega_scientific_writing.src.report_court omega_scientific_writing/examples/report_r5a_valid.json
# prints JSON verdict and exits 0

python -m omega_scientific_writing.src.report_court omega_scientific_writing/examples/report_r5a_invalid.json
# prints JSON verdict and exits 1
```

- [ ] **Step 4: Write `R5A.md`**

Document:

```text
Status: PROVISIONAL / EXACT-HEAD-CI-TARGET
Implemented: report IR, terminology court, methodology court, residual engine, traceability/proof cones, contradiction court, integrated report court.
Boundaries: structural/declared-evidence validation only; no ScientificPASS; no rendering qualification; no reverse compiler; no Drive sync.
Next gate: R5B report compiler + generalized LaTeX/PDF crystal qualification.
```

Include the exact invariant list from the architecture spec.

- [ ] **Step 5: Add exact-head CI workflow**

Create `.github/workflows/omega-scientific-report-r5a.yml`:

```yaml
name: Omega Scientific Report R5A

on:
  pull_request:
    paths:
      - 'omega_scientific_writing/**'
      - '.github/workflows/omega-scientific-report-r5a.yml'
  push:
    branches: [main]
    paths:
      - 'omega_scientific_writing/**'
      - '.github/workflows/omega-scientific-report-r5a.yml'

permissions:
  contents: read

jobs:
  r5a:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha || github.sha }}
      - name: Assert exact source head
        shell: bash
        run: |
          expected='${{ github.event.pull_request.head.sha || github.sha }}'
          actual="$(git rev-parse HEAD)"
          test "$actual" = "$expected"
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Full scientific writing tests
        run: python -m unittest discover -s omega_scientific_writing/tests -v
      - name: Valid R5A packet must pass
        run: python -m omega_scientific_writing.src.report_court omega_scientific_writing/examples/report_r5a_valid.json
      - name: Invalid R5A packet must hold
        shell: bash
        run: |
          set +e
          python -m omega_scientific_writing.src.report_court omega_scientific_writing/examples/report_r5a_invalid.json
          status=$?
          set -e
          test "$status" -eq 1
```

If GitHub expression evaluation for the mixed PR/push `ref` is rejected in Actions syntax, split the checkout assertion into PR and push conditional steps rather than weakening exact-head verification.

- [ ] **Step 6: Run local qualification**

```bash
python -m unittest discover -s omega_scientific_writing/tests -v
python -m omega_scientific_writing.src.report_court omega_scientific_writing/examples/report_r5a_valid.json
bash -c 'set +e; python -m omega_scientific_writing.src.report_court omega_scientific_writing/examples/report_r5a_invalid.json; s=$?; set -e; test "$s" -eq 1'
```

Expected: unit suite PASS, valid packet exit 0, invalid packet exit 1.

- [ ] **Step 7: Commit**

```bash
git add omega_scientific_writing/examples/report_r5a_valid.json omega_scientific_writing/examples/report_r5a_invalid.json omega_scientific_writing/src/report_court.py omega_scientific_writing/src/report_ir.py omega_scientific_writing/tests/test_r5a_report_court.py omega_scientific_writing/R5A.md .github/workflows/omega-scientific-report-r5a.yml
git commit -m "test(scientific-report): qualify R5A report court"
```

---

### Task 7: Capability registration and qualification receipt after CI evidence exists

**Files:**
- Modify: `src/tristan/capability_registry.py`
- Create: `omega_scientific_writing/receipts/R5A_EXACT_HEAD.md`
- Test: `tests/test_capability_registry.py` if present; otherwise add the assertion to the closest existing capability-registry test file discovered before editing.

**Interfaces:**
- Consumes: successful exact-head R5A GitHub Actions run from Task 6.
- Produces: repository-persisted R5A capability evidence without claiming scientific truth.

- [ ] **Step 1: Verify exact-head CI evidence before editing the registry**

Required evidence before this task proceeds:

```text
Omega Scientific Report R5A workflow = PASS on the exact feature head
Full scientific-writing unit suite = PASS
Valid packet = PASS
Invalid packet = expected HOLD/exit 1
```

If CI is unavailable or reports runner/steps anomalies, stop this task at HOLD; do not register `LOCAL_CI_VERIFIED`.

- [ ] **Step 2: Write a failing capability-registry assertion**

Assert that the registry contains a capability with id `ScientificReportGraph`, status `LOCAL_CI_VERIFIED`, and receipt `omega_scientific_writing/receipts/R5A_EXACT_HEAD.md`.

- [ ] **Step 3: Add the exact-head receipt**

The receipt records:

```text
exact source head SHA
workflow/run identity
observed PASS gates
fixture identities/hashes if available from the run
known boundaries
Generated != Verified
CompilationPASS != ScientificPASS
ReportCourtPASS != ScientificPASS
```

Do not write the receipt before the exact-head run has actually completed.

- [ ] **Step 4: Register the capability**

Add to `default_capability_registry()`:

```python
CapabilityRecord(
    CapabilityIR(
        "ScientificReportGraph",
        ("report_traceability", "terminology_audit", "methodology_audit", "residual_detection", "contradiction_hold"),
        ("omega_scientific_writing/receipts/R5A_EXACT_HEAD.md",),
        "AUTOMATED",
    ),
    "LOCAL_CI_VERIFIED",
    ("omega_scientific_writing/receipts/R5A_EXACT_HEAD.md",),
    ("report-court pass does not establish scientific truth", "R5B-R5E not yet qualified"),
),
```

- [ ] **Step 5: Run the full relevant suites**

```bash
python -m unittest discover -s omega_scientific_writing/tests -v
python -m unittest discover -s tests -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/tristan/capability_registry.py omega_scientific_writing/receipts/R5A_EXACT_HEAD.md tests omega_scientific_writing/tests
git commit -m "docs(scientific-report): bind R5A capability to exact-head evidence"
```

---

## Final R5A Qualification Checklist

Before the R5A implementation PR is marked ready:

- [ ] `python -m unittest discover -s omega_scientific_writing/tests -v` passes.
- [ ] Kernel tests relevant to capability registration pass.
- [ ] Valid fixture exits 0.
- [ ] Invalid fixture exits 1 with all five deliberate defect codes.
- [ ] No finding path automatically upgrades claim epistemic status.
- [ ] No R5A module duplicates Omni `QuantityIR`, `EquationIR`, `TableIR`, or `CitationIR`.
- [ ] Unresolved contradiction produces HOLD.
- [ ] Unsupported conclusion produces HOLD.
- [ ] Method without validation creates a blocking residual.
- [ ] Ambiguous terminology produces HOLD.
- [ ] Proof cone exposes dangling/missing ids instead of inventing nodes.
- [ ] Exact-head GitHub Actions run succeeds before capability registration.
- [ ] Receipt explicitly says `ReportCourtPASS != ScientificPASS`.
- [ ] No Drive publication/sync code was introduced in R5A.

## Self-Review Result

- **Spec coverage:** R5A covers the approved subproject scope: report-domain IR, terminology registry/court, methodology diagnostics, residual engine, contradiction records/court, objective/result/claim/conclusion traceability, and exact-head qualification. Rendering, reverse compilation, additional document adapters, Report Crystal rendering, and Drive synchronization remain correctly deferred to R5B-R5E.
- **Placeholder scan:** No implementation step relies on `TBD`, generic error-handling instructions, or an undefined future helper.
- **Type consistency:** The plan consistently uses `ReportMeta`, `ReportGraphIR`, `ResultIR.objective_ids`, `ConclusionIR.objective_ids`, `evaluate_report`, `derive_residuals`, `blocking_residuals`, `build_traceability_index`, and `proof_cone` with the same signatures across tasks.
