# Intelligence Omega R0.5

R0.5 extends the verified R0.4 adaptive loop with bounded meta-learning,
world-model prediction, active experiment selection, evidence-bound tool
discovery and reversible architecture mutation.

## Core chain

Observed outcomes
-> contextual MetaLearning
-> WorldState + TransitionHypothesis
-> predicted residuals
-> ExperimentDesigner
-> ToolDiscovery
-> candidate ArchitectureMutation
-> frozen retest
-> Shadow/OOD/Transfer courts
-> external authority only
-> RealityReceipt
-> epistemic memory

## Meta-learning

Strategy preferences are learned only from context-matching outcomes.
Insufficient contextual samples produce HOLD.
The conservative utility penalizes standard error and stated uncertainty.

## World model

The world-model layer is deliberately small:
- typed state variables
- explicit transition hypothesis
- explicit assumptions
- uncertainty
- prediction receipt
- observed residual

It is not a claim that the internal state equals the world.

## Active experiment design

Candidate experiments are ranked by evidence utility:

expected_information_gain * reproducibility * falsification_power
----------------------------------------------------------------
                    cost + risk + time

Low-utility fronts yield NO_ACTION.

## Tool discovery

Tools are only eligible when they:
- cover all required capabilities
- carry evidence IDs
- expose reliability and uncertainty
- survive origin-blind comparison

Selection does not install or authorize a tool.

## Architecture mutation

A mutation must have:
- explicit TransformationIR
- rollback
- frozen retests
- reversibility
- positive expected net gain after risk, evidence debt and complexity

Otherwise the correct result is NO_ACTION.

CandidateMutation != ExecutedMutation
ExecutedMutation != PromotedMutation
SelfModification != SelfApproval

## Hard invariants

PastPerformance != FutureGuarantee
ModelPrediction != Observation
ExpectedInformationGain != ObservedInformationGain
ToolSelected != ToolAuthorized
NoMeasuredGain -> NO_ACTION
FrozenRetestRequired
RollbackRequired
OriginBonus = 0
NO_ACTION remains admissible
