# Context Retrieval Court R0.2

## Purpose

This court tests whether the R0.1 token-overlap context scorer should be replaced, supplemented, or left unchanged. It is a bounded engineering benchmark over the current public registry, not a semantic-truth benchmark and not a claim about the user's full corpus.

## Reuse first

The court reuses the historical BM25 mechanism already present in `Tristan-Tardif-Morency/tools/context_real_archive_replay_r01.py` and the RightToLose doctrine in `docs/OMEGA_TRISTAN_CONTEXT_RECONSTRUCTION_R2.md`. The BM25 mechanism is prior Tristan work, not a new invention of this repository.

## Frozen arms

- `CURRENT_R0_1`: existing `score_object()` runtime scorer.
- `BM25_CORE`: BM25 over the same title/tags/summary surface.
- `BM25_FULL`: BM25 over the bounded public object fields including declared failures/frontiers/dependencies/metadata.
- `TFIDF_FULL_NORMALIZED`: dependency-free TF-IDF cosine over the same full public fields with underscore/camel-case normalization.
- `SQLITE_FTS5_FULL`: SQLite FTS5/BM25 over the full public fields when FTS5 is available.
- `NO_ACTION`: keep the R0.1 runtime unchanged.

No embedding API or external vector dependency is added in R0.2. That complexity remains a future challenger only if a larger court justifies it.

## Frozen fixture

`benchmarks/context_retrieval_r0_2.json` contains 16 labeled queries: 8 development and 8 holdout queries over the seven public registry objects available when the fixture was created.

The labels are self-authored and therefore weak evidence. Holdout is used to reduce direct tuning leakage, but it is not independent external ground truth.

## Metrics

The court records:

- hit@1;
- mean reciprocal rank (MRR);
- recall@3.

Runtime promotion is intentionally disabled in this court. A candidate may become a shadow challenger, but the current runtime is not mutated solely from this small fixture.

## Tie rule

A metric tie does not fabricate a winner. When multiple arms share best holdout MRR, the decision is `TIE_KEEP_RUNTIME_UNCHANGED_SHADOW_CHALLENGERS`.

## Execution

```bash
PYTHONPATH=src python -m tristan.retrieval_court
```

CI executes the same court after compile, unit tests, and kernel verification.

## Hard boundaries

- `SelfAuthoredLabels != SemanticTruth`.
- `SevenObjects != RepresentativeCorpus`.
- `DevelopmentSplit != HeldOutEvidence`.
- `WinnerOnFixture != RuntimePromotion`.
- `Tie != Winner`.
- `BM25PriorArtReused != NewTristanInvention`.
- `SQLiteFTSAvailableHere != AvailableEverywhere`.
- `BenchmarkVictory != UniversalRetrievalSuperiority`.
- `NoRuntimeMutationWithoutLargerIndependentCourt`.

## Next gate

If a lexical/full-field challenger beats the current scorer on this small court, freeze a materially larger independently labeled corpus/query set drawn from authorized real Tristan objects. Compare current lexical, BM25/FTS5, TF-IDF, semantic/embedding, graph/hybrid, and NO_ACTION under matched budgets before changing the runtime router.
