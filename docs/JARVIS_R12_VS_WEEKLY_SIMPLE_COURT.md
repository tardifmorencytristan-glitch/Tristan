# R12 vs Weekly Snapshot+Diff — Current-Head Discriminating Court

Status: **PASS_CURRENT_MAIN_FRESH_PORT / REGIONAL_R12_ADVANTAGE / SIMPLE_DEFAULT / HOLD_NO_AUTO_MERGE**.

Base at court creation: `f26c368aeecfb7830e834b5eb2cea0d9b826e1a9`.
R12 source candidate imported exactly from PR #78 head `7cec53b3690d083af8405d45b09c17cec93294b3`.
Qualified code/test head: `2fb411a93f1f1cd6523b356f347a203549c2a8fc`.
Court PR: #79.

## Result

The lower-complexity weekly snapshot+diff challenger is sufficient and preferred for ordinary weekly current-state reporting.

R12 demonstrates a bounded distinct capability for cases that require:

- late-arriving evidence with `valid_at != recorded_at`;
- historical `as_known_at` reconstruction;
- fail-closed event-ID collision handling;
- preservation of supersession/reactivation lineage.

This is a regional engineering win only. It is not universal superiority and does not itself authorize merge.

## Frozen court

Hard gates:

1. current-main compatibility;
2. Recovered != Accomplished;
3. unassessed evidence debt != zero-debt claim;
4. collision-safe event identity fails closed;
5. historical terminal lineage remains queryable;
6. no raw private receipt payload in event storage;
7. Capability != Authority.

Discriminating cases:

1. ordinary same-week snapshot delta;
2. late-arriving evidence where `valid_at != recorded_at`;
3. event-ID collision with altered payload;
4. supersession followed by reactivation;
5. lower-complexity preference when history is not required.

## Evidence

Fresh FORGE clone of PR #79:

- R12 + discriminating court: **17/17 PASS**.
- R8/R9 focused after corrected test-module invocation: **9/9 PASS**.
- full public suite: **191/191 PASS**.
- GitHub hosted `jarvis-r6-evidence-domino`: **SUCCESS** on qualified code/test head.
- GitHub hosted `kernel-ci`: **SUCCESS** on qualified code/test head.

Negative memory retained:

- initial R8/R9 invocation referenced non-existent module names and produced two ImportError errors; classified PRE_RUN_CLI, not code failures;
- an earlier PowerShell requalification attempt blocked with no interpretable output and was terminated.

## RightToSimplify decision

`SIMPLE snapshot+diff` remains the default projection when the query only needs current weekly state and delta.

`R12` is justified only for the region where bitemporal knowledge history, immutable event identity, or historical lineage changes the answer.

Therefore the selected composition is:

```
ordinary weekly report -> SIMPLE
historical/bitemporal query -> R12 projection
closure/debt -> existing R9 owner
source observation -> existing R8 owner
```

No new Atlas, evidence court, debt owner, scheduler, memory owner, or autonomy layer is created.

## Promotion state

**HOLD / REVIEW / NO AUTO-MERGE.**

A regional benchmark win is not merge authority. PR #78 remains historical candidate lineage; PR #79 is a fresh-main qualification court, not an automatic replacement owner.

Generated != Verified.
RepositoryPASS != ScientificPASS.
RegionalWin != UniversalWin.
Candidate != Canonical.
Capability != Authority.
NO_ACTION remains admissible.
