# Adaptive Intelligence R0.3

This layer makes Intelligence Omega more capable without granting it more
authority.

## Added

1. **Epistemic memory**
   - M+ positive mechanisms
   - M- failures
   - M? unresolved contexts
   - M-delta measured changes
   - transfer is opt-in, never automatic

2. **Adaptive capability routing**
   - choose the smallest coalition that covers mission capabilities
   - origin-blind utility
   - reliability, uncertainty, cost, latency and coalition complexity
   - HOLD when coverage is incomplete
   - selection never grants execution authority

3. **Calibration**
   - empirical accuracy vs stated confidence
   - Brier score
   - confidence gap
   - future policy can downgrade overconfident agents

4. **Causal-credit ablations**
   - remove one component at a time
   - measure local performance delta
   - keep the receipt explicitly weaker than causal proof

## Next residual

- ShadowJarvis / CounterJarvis paired planning
- OOD mission court
- proof-carrying capability leases
- outcome readback into M+/M-/M?/M-delta
- contextual transfer tests
- automated regeneration drills

## Invariants

Generated != Verified
Capability != Authority
Selected != Authorized
AblationContribution != CausalProof
LocalCredit != GlobalTransfer
Confidence != Accuracy
NO_ACTION remains admissible
