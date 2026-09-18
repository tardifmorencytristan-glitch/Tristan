# Autonomy R2 - Frontier Loop

Autonomy R2 makes continuation a first-class protocol.

The loop is:

`OBSERVE -> RESIDUAL -> PROPOSE -> DECIDE -> LEASE -> EXECUTE -> MEASURE -> EVIDENCE -> RESIDUAL -> ...`

Each new step requires a fresh Autonomy R1 decision. Authority is never inherited merely because the previous step succeeded.

The system continues automatically while a proposal is:

- internal;
- reversible;
- evidence-backed;
- above confidence threshold;
- positive in verified utility;
- inside its execution lease.

Stopping states are meaningful:

- `P0`: no admissible next action or repeated no-gain;
- `HOLD_AUTHORITY_BOUNDARY`: next useful action crosses an external/irreversible/scientific authority boundary;
- `HOLD_EXECUTION_FAILURE`: execution failed;
- `HOLD_REPEAT_LOOP`: anti-loop firewall fired;
- `CHECKPOINT`: bounded work quantum ended and `resume_required=true`.

A checkpoint is not completion. A scheduler or worker may immediately resume from its serialized FrontierContext.

Hard boundaries:

- Continuation != InfinitePermission
- EveryStepRequiresFreshDecision
- EverySuccessRequiresEvidence
- ExternalOrIrreversibleAction -> REQUIRE_AUTHORIZATION
- ScientificPromotion -> REQUIRE_AUTHORIZATION
- RepeatedNoGain -> P0
- Checkpoint != Completion
- NO_ACTION is admissible
