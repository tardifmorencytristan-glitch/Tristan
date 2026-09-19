# Ω Multidirectional Omni Compiler — R4H Communication Projection Adapter

Status: **LOCAL_BOUNDED_ENGINEERING_PASS / REPOSITORY-GATE-PENDING**

## Mission

R4H adds the smallest missing communication projection layer without creating a new
writer, voice runtime, video system, evidence authority, or mother-system.

Canonical composition:

`Claim/Evidence IR -> RepresentationGraph -> CommunicationProjectionSpec -> TimedProjectionIR -> renderer adapter`

The adapter is intentionally downstream of existing knowledge/evidence owners.

## Reused owners

- structural `ClaimLike` / `EvidenceLike` protocols, with `tristan.jarvis_ir.ClaimIR` and `EvidenceIR` verified by a separate bridge test;
- Omni R4A `RepresentationGraph` + provenance;
- Scientific Writing R4/R4.1 stable claim/evidence lineage;
- existing renderers remain external adapters;
- WebVTT is the first external timed-text export target.

`CommunicationProjection != ScientificWriting2 != Presence2 != VideoOS`.
## Added

- `CommunicationProjectionSpec`: audience/channel/language/time/loss/accessibility/rights/authority references.
- `TimedProjectionSegment`: timed semantic unit bound to representation, claim, evidence and provenance ids.
- `TimedProjectionIR`: deterministic ordered projection object.
- `CommunicationCourtReceipt`: fail-closed structural court.
- deterministic JSON round-trip + digest.
- deterministic WebVTT caption export.
- Battery-T R4.1 integration benchmark using the persisted scientific-writing fixture.

Authority references are references only. The receipt hard-codes `authority_granted=false`.

## Structural gates

The court HOLDS when it observes:

- missing representation/claim/evidence ids;
- a claim whose linked evidence is absent from the same timed segment;
- required captions missing from spoken segments;
- time budget overflow;
- accumulated declared semantic loss above budget;
- invalid ids/timestamps or duplicate segment ids.

The loss value is declared metadata, not measured semantic equivalence.

## Battery-T integration court

Source fixture:
`omega_scientific_writing/fixtures/battery_t_r0_4_writing_court.json`.
The existing R4_BOUNDED candidate is projected into one evidence-bound timed segment.

Observed local result:

- source fixture SHA-256: `89141c9158e5563bb5bc43f94d053f85a86769de4908cab765a5869eb5efc2a3`;
- projection digest: `6a62f1fad38d02e87b80e213672dcbadea46cb1e2a497b4be210ac2d8c900a51`;
- court digest: `e07b6a679eda9bca9bc0f1cf54345081bc507950f4a79f1863fa2b13b2499c32`;
- court result: **PASS_STRUCTURAL**;
- missing representation/claim/evidence refs: 0;
- unsupported claims: 0;
- caption gaps: 0;
- WebVTT semantic content remains explicitly bounded to the source claim.

## Local qualification

Exact construction base: public `main@eff0af246696b862bd871e6c2b761ce01e551233`.

- focused R4H court: **10/10 PASS**;
- Omni protocol + real Jarvis ClaimIR/EvidenceIR bridge: **11/11 PASS**;
- Scientific Writing suite: **50/50 PASS**;
- public root suite: **170/170 PASS**;
- py_compile: PASS;
- Battery-T benchmark: PASS_STRUCTURAL.

Omni candidate suite:
- 71 tests total;
- 69 PASS / 2 FAIL.
Clean baseline clone at the same public main:
- 61 tests total;
- 59 PASS / 2 FAIL;
- the same two failures are the existing R4D fixture SHA mismatch
  (`cbab3b... != cc45d6...`).

Therefore R4H adds 10 passing tests and no new observed Omni failure identity.
This is bounded differential evidence, not RepositoryPASS.

## Anti-Ego / RightToDie

The next court must compare this adapter against:

1. direct/simple script + captions;
2. existing Omni representation without R4H;
3. external timed-text/render tooling;
4. hybrid;
5. NO_ACTION.

If the same fidelity/accessibility/provenance can be achieved with lower persistent
complexity, R4H should be absorbed or deleted.

## Hard boundaries

- `PASS_STRUCTURAL != SemanticEquivalence`
- `DeclaredSemanticLoss != MeasuredSemanticLoss`
- `WebVTTExport != VideoRender`
- `CaptionPresent != HumanComprehension`
- `ProvenanceBound != ClaimTrue`
- `Generated != Verified`
- `Capability != Authority`
- `NO_ACTION admissible`
## Next gates

1. exact-head CI/repository qualification;
2. measured text -> timed projection -> transcript round-trip residual;
3. origin-blind renderer tournament: direct/FFmpeg, Manim, Remotion/browser, hybrid, NO_VIDEO;
4. DAPT/TTML import-export only if a real dubbing/audio-description workflow needs it;
5. C2PA export only if public media provenance needs it;
6. Presence/voice binding only after its phone/STT/TTS authority and measurement gates;
7. human comprehension/transfer court before any communication-superiority claim.

The desired end state is not more media infrastructure. It is the smallest
regenerable bridge that preserves evidence and meaning across necessary projections.
