# Intelligence Omega R0.4

R0.4 adds robust adaptive competition and transfer without increasing autonomous
authority.

## Loop

Mission
-> CURRENT / SHADOW / COUNTER / EXTERNAL / NO_ACTION
-> contextual court
-> OOD mission court
-> TransferGate
-> proof-carrying capability lease
-> external ExecutionLease
-> execution
-> independent RealityReceipt
-> outcome readback
-> M+ / M- / M? / M-delta

## Shadow / Counter court

Every promotion-grade comparison must include:
- current architecture
- shadow architecture
- counter architecture
- external baseline
- NO_ACTION

Origin never contributes to utility.

## OOD court

A mission is OOD only when its signature is not present in the training signature
set. Overlap produces HOLD. Transfer evidence is contextual and never universal.

## Transfer gate

A mechanism can only transfer when:
1. its MemoryRecord explicitly declares the target inside transfer_scope;
2. the OOD court produced transfer evidence;
3. no training overlap was detected.

Even then the result is only ELIGIBLE_FOR_CONTEXTUAL_RETEST.

## Proof-carrying capability lease

A coalition may claim a capability only with evidence IDs and an explicit scope.
This object proves bounded capability evidence, not execution permission.

## Outcome readback

Independent RealityReceipt outcomes are converted into contextual epistemic
memory:
- PASS -> M+
- RESIDUAL -> M-
- unresolved -> M?

This closes the learning loop while preserving authority separation.

## Hard invariants

ContextualWinner != UniversalWinner
Winner != PromotionAuthority
TransferEvidence != TransferAuthority
EligibleForRetest != Promoted
CapabilityProof != ExecutionAuthority
RealityReceipt != PromotionAuthority
OriginBonus = 0
NO_ACTION remains mandatory
