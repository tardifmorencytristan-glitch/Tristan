# R12 vs Weekly Snapshot+Diff — Current-Head Discriminating Court

Status: **TO_TEST / HOLD** until exact-head CI and readback complete.

Base at court creation: `f26c368aeecfb7830e834b5eb2cea0d9b826e1a9`.
R12 source candidate imported exactly from PR #78 head `7cec53b3690d083af8405d45b09c17cec93294b3`.

## Question

Does Jarvis R12 provide a distinct required capability over the lower-complexity weekly snapshot+diff challenger?

## Frozen criteria

Hard gates:

1. current-main compatibility;
2. Recovered != Accomplished;
3. unassessed evidence debt != zero-debt claim;
4. collision-safe event identity fails closed;
5. historical terminal lineage remains queryable;
6. no raw private receipt payload in event storage;
7. Capability != Authority.

Discriminating cases:

- ordinary same-week snapshot delta;
- late-arriving evidence where `valid_at != recorded_at`;
- event-ID collision with altered payload;
- supersession followed by reactivation.

## RightToSimplify rule

Use SIMPLE snapshot+diff whenever current-week state transition is sufficient.
R12 earns only the region that actually requires bitemporal replay, immutable event lineage, or collision-safe identity.

## Falsifier

If SIMPLE reproduces every decision-relevant result without adding bitemporal/event-log machinery, R12 should not be promoted.

If SIMPLE must acquire those mechanisms to answer a real late-evidence/history query correctly, it has reconstructed the R12 capability and R12 has a bounded regional advantage.

Generated != Verified. RepositoryPASS != ScientificPASS. Candidate != Canonical. NO_ACTION remains admissible.
