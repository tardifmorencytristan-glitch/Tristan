# Jarvis R11 - Portfolio Qualification Court

Status: PROVISIONAL ENGINEERING IMPLEMENTATION.

R11 closes a concrete gap observed after R10: repository work can have successful historical CI while still being unsafe to promote because the PR head moved, the base is stale, mergeability changed, a required workflow is queued or missing, or review debt remains.

## Canonical flow

`PR observation -> exact main/head binding -> required-workflow court -> mergeability/review court -> qualification receipt`

The court never merges by itself. It emits a bounded qualification state that another authorized GitHub action may use.

## Decisions

- `QUALIFIED_EXACT_HEAD`
- `HOLD_CI`
- `HOLD_REPLAY_ON_CURRENT_MAIN`
- `HOLD_REBASE_OR_RESOLVE`
- `HOLD_DRAFT`
- `HOLD_REVIEW`
- `HOLD`

## Exact-head rule

A green workflow attached to an older head is not inherited by a moved head. Likewise a PR whose `base_sha` is not the currently observed `main` receives `STALE_BASE`.

This turns the repository invariant into executable logic:

`HeadMove -> Requalify`

## Boundaries

- WorkflowSuccess != ScientificPASS
- Mergeable != MergeAuthority
- ExactHeadQualification != TimelessQualification
- StaleBase -> HOLD
- HeadMove -> Requalify
- PortfolioDecision != MergeAuthority
- NO_ACTION is admissible
