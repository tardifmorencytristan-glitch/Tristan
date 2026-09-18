# Autonomy R1 - Bounded Decision Authority

Autonomy R1 changes the Tristan kernel from recommendation-only behavior to bounded decision authority.

Jarvis may now autonomously choose and authorize an action only when all of the following are true:

- the action is internal;
- the action is reversible;
- a rollback is declared;
- evidence references exist;
- confidence is at least the configured threshold;
- expected verified gain exceeds cost and risk;
- the action is not a scientific promotion, physical action, financial commitment, credential/secret change, external publication, or external deployment.

A passing action receives an authorized reversible-only `ExecutionLease`.

External, irreversible, physical, financial, credential, publication, deployment, and scientific-promotion decisions remain `REQUIRE_AUTHORIZATION`.

The governing rule is:

`Decide autonomously when failure is bounded and reversible; escalate when consequences cross the system boundary.`
