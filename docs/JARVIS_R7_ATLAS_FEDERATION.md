# Jarvis Tristan R7 - Atlas Federation

Status: PROVISIONAL ENGINEERING IMPLEMENTATION.

R7 adds a fail-closed Atlas federation projection to the canonical Jarvis runtime. It federates the current public kernel, the historical Git source family, a private Git source descriptor, and observed Drive document families without copying private payloads into the public repository.

## Purpose

The Atlas is a routing and residual surface, not a truth engine.

It converts source-state gaps into bounded missions such as:

- materialize a bounded source;
- bind an exact version;
- canonicalize duplicate document families;
- preserve private/public federation boundaries.

Those missions are ranked by the existing MissionQueue. R7 does not introduce a competing priority engine.

## Top projections

R7 exposes Top16, Top64 and Top256 as bounded projections of eligible Atlas missions.

These lists are operational attention views only.

Hard boundaries:

- AtlasProjection != ScientificRanking
- TopK != Truth
- MissionPriority != ScientificImportance
- FederatedPointer != LoadedEvidence
- SourceAvailability != ScientificSupport
- DuplicateName != DuplicateContent
- PrivateSource != PublicPayload
- NO_ACTION is admissible

## Privacy and provenance

Private Git and Drive sources are represented in the public layer by safe descriptors only. The public module intentionally omits private URLs, IDs and document payloads.

Exact snapshots must be bound per task before a federated source can be treated as reproducible evidence.

## Runtime integration

The canonical `tristan jarvis` receipt now includes:

- R1 core plan;
- R2 closure MissionQueue;
- R3 capabilities;
- R4 public domain cases;
- R6 scientific source/evidence and Domino planning;
- R7 Atlas federation projection.

The closure queue remains the owner of `next_mission_id`. Atlas Top projections do not silently override it.
