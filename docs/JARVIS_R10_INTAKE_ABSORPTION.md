# Jarvis R10 - Intake Absorption

Status: PROVISIONAL ENGINEERING IMPLEMENTATION.

R10 absorbs the reusable mechanisms from the historical Problem Foundry and Ultimate Jarvis repository-node branches into one canonical owner: `src/tristan/intake_guard.py`.

It does not preserve those branches as parallel runtimes.

## Absorbed capabilities

From Problem Foundry:
- source-specific ingestion/publication profiles;
- domain-specific verification contracts for code, math, physics, engineering and data;
- fail-closed publication behavior.

From the repository-local Ultimate Jarvis branch:
- exact repository/path/commit/locator grounding;
- visibility gates;
- role-scope gates;
- weighted grounding coverage;
- PUBLIC_SAFE fail-closed behavior.

## Canonical flow

`IntakeRequest -> PolicyProfile -> VerificationContract -> GroundingCourt -> MissionGenome`

The output is a MissionGenome-compatible internal plan, not publication authority.

## Important boundaries

- ProblemIntake != PublicationAuthority
- GroundingPASS != ScientificTruth
- RepositorySource != ScientificEvidence
- PrivateSource -> PublicOutput = FORBIDDEN
- NoSource -> NoSubstantiveClaim
- PolicyProfile != TimelessExternalPolicy
- MissionGenome != Execution

R10 intentionally keeps external-policy profiles as local bounded configuration. They must be refreshed when a real action materially depends on current platform policy.
