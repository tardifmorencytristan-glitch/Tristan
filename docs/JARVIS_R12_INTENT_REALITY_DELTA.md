# Jarvis R12 - Intent Reality Delta

Status: PROVISIONAL ENGINEERING CANDIDATE.

R12 is a thin adapter over the existing Jarvis R8 Live Atlas and R9 Ultra Closure. It does not create another Atlas, memory authority, mission owner, evidence court, scheduler, or autonomy layer.

## Residual closed by this candidate

R8 records source-centric immutable Live Atlas snapshots and intent-aware mission projections. R9 owns MissionGenome, multidimensional debt, closure/regeneration control, generation throttling, and capability crystallization. The historical unmerged R11 Portfolio Qualification court owns exact-head PR qualification logic but is stale relative to current public main and remains historical lineage evidence.

The remaining bounded gap is temporal intent reconstruction:

- a source recovered today may describe an intention that was valid months ago;
- recovered work must not become accomplished work by implication;
- one event can concern an intent, capability, artifact, evidence object, failure, worker, and source simultaneously;
- superseded/failed/abandoned lineage must remain queryable;
- weekly reconstruction should be a delta over event state rather than a fresh narrative rewrite.

## Canonical composition

```
R8 SourceObservation
  -> R12 IntentEvent(valid_at, recorded_at, object_refs)
  -> IntentState
  -> IntentStateDelta
  -> R12 IntentEvidenceDebt
  -> R9 DebtVector
  -> R9 MissionGenome / closure machinery
```

R12 therefore extends existing owners instead of replacing them.

## Contracts

### ObjectRef

An event may reference multiple typed objects with qualified roles. This supports an object-centric event without requiring the public kernel to become a full graph database.

### IntentEvent

The event separates:

- `valid_at`: when the observation/event belongs in the modeled work history;
- `recorded_at`: when the reconstruction system learned or recorded it;
- source identity;
- surface state;
- independent state-axis patches;
- typed object references;
- evidence references;
- lineage edges;
- optional confidence for implicit intentions.

### Independent axes

The projection keeps these booleans independent:

- RECOVERED
- ACCOMPLISHED
- VERIFIED
- EXTERNALLY_VALIDATED
- CLOSED

In particular, recovery does not imply accomplishment.

### Lineage

The bounded relation vocabulary is:

`PRECEDES | REFINES | SPLITS | MERGES | SUPERSEDES | ABSORBS | CONTRADICTS | FULFILLS | FAILS | ABANDONS | REACTIVATES | DEPENDS_ON`.

### Evidence debt

R12 adds intent-specific evidence-debt dimensions:

`source_completeness, semantic_certainty, execution_proof, freshness, independence, reality_level, authority, reproducibility`.

The adapter projects those dimensions into the existing R9 `DebtVector`; it does not create a competing portfolio-debt owner.

## Bitemporal query behavior

`project_intent_state(..., as_known_at=..., valid_at=...)` supports a bounded historical question such as:

> What intent evidence was valid by time V using only knowledge recorded by time K?

This is event-state reconstruction, not proof that an inferred intention was the user's actual private mental state.

## Weekly IntentAtlas use

A weekly report should consume R12 deltas and emit:

- newly recovered intentions;
- accomplishments and verification transitions;
- regressions;
- supersessions/reactivations;
- evidence gained or lost;
- closure-state transitions;
- unresolved evidence debt.

The report remains a human-readable view. The event history is the reconstruction substrate.

## Historical R11 relationship

The existing R11 Portfolio Qualification branches are not renamed or erased. Their exact-head qualification mechanism remains historical lineage and should be replayed on current main before any future merge. R12 does not grant merge authority.

## External challengers / interoperability

R12 should remain export-compatible in spirit with standard provenance, trace-context, and object-centric event-log mechanisms when doing so reduces future integration cost. External mechanisms receive no automatic priority; they must beat simpler internal representations for the actual workload.

## Hard boundaries

- Recovered != Accomplished
- Accomplished != Verified
- Verified != ExternallyValidated
- RecordedAt != ValidAt
- IntentInference != UserInstruction
- Lineage != Truth
- EventLog != ScientificEvidence
- Capability != Authority
- R12 != NewMissionOwner
- R12 != R8Replacement
- R12 != R9Replacement
- NO_ACTION is admissible

## Candidate exit gate

Promote only after:

1. focused R12 tests pass;
2. unchanged R8 and R9 focused suites still pass;
3. exact candidate head is rebound after all candidate edits;
4. applicable repository CI executes successfully;
5. no claim upgrades beyond engineering scope;
6. Anti-Ego confirms that a simpler weekly-only representation does not provide equivalent required capability at lower persistent complexity.
