# Intelligence Omega R0.6 - Live Mission Court

R0.6 changes the optimization target from architecture growth to measured
mission closure.

The first frozen mission court is built from connected-access observations made
on 2026-09-18.

## Frozen missions

1. **Drive reuse**
   Existing Jarvis Morphogenesis / Runtime artifacts were observed.
   Correct action: REUSE_EXISTING.

2. **GitHub exact-head qualification**
   Candidate head:
   `0bfa493c28561370ab8d01645c46bdfd8b8eac06`
   Both required workflows completed with conclusion `success`.
   Correct bounded decision: EXACT_HEAD_SOFTWARE_PASS.

3. **Render staging**
   The connected Render service points at a different repository and main
   branch from the Intelligence Omega candidate.
   Correct action: NO_DEPLOY_REPO_MISMATCH.

4. **Scientific source planning**
   A CERN + JWST mission must select CERN Open Data / HEPData / JWST MAST,
   while retaining SourceSelection != DataRetrieved.
   Correct action: SOURCE_PLAN_ONLY.

## Why this matters

These cases are not claims of general intelligence and are not scientific
validation. They are frozen replayable decisions grounded in states actually
observed through connected services.

The next benchmark layer should add held-out live missions and compare:
- current policy
- adaptive policy
- external/simple baseline
- NO_ACTION

Metrics should include:
- correct terminal decision
- authority violations
- evidence/provenance coverage
- unnecessary actions
- latency/cost
- calibration
- recovery after changed state

## Hard boundaries

FrozenObservation != LiveStateForever
RepositoryPASS != ScientificPASS
CorrectDecisionOn4Missions != GeneralIntelligence
ReplayPASS != ExternalReplication
DeploymentEligibility != DeploymentAuthority
NO_ACTION remains admissible
