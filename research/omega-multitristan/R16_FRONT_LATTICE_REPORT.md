# Ω-MULTI-TRISTAN R16 — Objective-subset lattices, operator noncommutation and inverse front incidence

**Evidence status:** FINITE SYNTHETIC MATHEMATICS; dual-machine independent enumeration, adversarial counterexample. **Not** a new historically established optimization theorem, physical experiment, real-world superiority claim, CI certification, or autonomous deployment.

## 1. Relation to prior research and existing system

R16 extends the finite R15 experiment without replacing its result. Recovered original R15 front-map SHA256 is:
`12bf5ebe0e1be9ea15b3057f9e111db50a94af714668f67d04c027cffeb7cdff`.

The existing Ω-M4OPT R0.2 RightToLose work already rejects M4OPT as a universal optimizer: five frozen cases, zero strict wins, two ties and three quality losses. Its candidate value is **routing and guarding against loss of information**, not superseding direct specialists. Refer to `docs/OMEGA_M4OPT_R0_2_RIGHTTOLOSE.md` in the `Tristan-Tardif-Morency` repository. `NO_M4OPT`, `KEEP_SEPARATE` and `NO_ACTION` are admissible.

The conventional Pareto order, efficient decision points, Pareto objective vectors and objective reduction have extensive prior literature. Relevant references include:
- Michael T. M. Emmerich and André H. Deutz (2018), *A tutorial on multiobjective optimization: fundamentals and evolutionary methods*, Natural Computing, https://doi.org/10.1007/s11047-018-9685-y
- *Objective Reduction in Many-Objective Optimization: Evolutionary Multiobjective Approaches and Comprehensive Analysis*, IEEE Transactions on Evolutionary Computation (2018), https://doi.org/10.1109/TEVC.2017.2672668

**Terminology:** Our JSON maps a context to its **set of non-dominated candidate IDs in decision space**. Because lossy transformations create tied objective values, the number of such IDs can exceed the number of unique objective vectors on the Pareto front. We deliberately preserve candidate IDs for provenance and inverse incidence.

## 2. Finite typed tensor

Three synthetic problems, two scales, two representations, **two operator orders**, 289 integer design candidates and three objectives:

```text
T[problem:3, scale:2, representation:2, order:2, candidate:289, objective:3]
```

A feasible candidate `(a,b)` satisfies `a²+b² <= 80`, giving **249** feasible of 289 total candidates in `[-8,8]^2`. Problem definitions and cost functions remain exactly those of R15:
- P0: `(tx,ty,coupling,sign,offset)=(4,-4,2,1,0)`
- P1: `(-4,4,1,-1,4)`
- P2: `(2,2,1,1,-4)`

Objectives are minimized:
```text
fit = (a-tx)^2+(b-ty)^2+coupling*(a-sign*b)^2
size = a*a+b*b
residual = (a+b-offset)^2+(p+1)*(a-b)^2
```

Objective-subset views are `J01, J02, J12, J012`; together they create **96** separate candidate-ID front contexts.

Order O0 is the R15 definition: `D(x)=abs(x)` then `S(x)=2*floor(x/2)`, each applied only if enabled. O1 is `S` then `D`. Both transformations are generally information-losing; when one is disabled, order is irrelevant.

## 3. Reproduced computational results

FORGE used NumPy integer arrays and broadcasting; VERIFIER independently regenerated all results via standard-library scalar loops. Independent methods agreed on:
- **96** candidate-ID non-dominated sets.
- **1,171** candidate/context memberships.
- R15 48-context digest exactly reproduced under O0.
- Full R16 sorted compact JSON SHA256 **`06e9ee5d6bb0a561e28738cdb43143f6520ff21c818ccc589c9fcbe1d8ed183f`**.
- **72** directed transitions from a two-objective subset to the three-objective set (24 scenario contexts × 3 subsets).
- Across these transitions, **275** new memberships and **58** removed memberships; 42 transitions with additions and 12 with removals. These are membership counts with repeat context accounting, not 333 distinct discoveries.
- Across all 48 pairwise O0-vs-O1 front comparisons (3 problems × 2 scales × 2 representations × 4 subsets), **12** differ; only settings where both lossy operations were enabled differ.
- Candidate `(0,0)` appears in **88 of 96** contexts and three problems, *not* a universal optimizer.

VERIFIER also checked that componentwise positive affine rescalings preserve nondominated candidate IDs in a reference context, and checked exact dual candidate↔context incidence.

## 4. Exact theorem concerning objective addition and ties

Fix a **common set of candidate IDs** `C`, objective maps `f_i:C->R`, two sets of objectives `J subset K`, and Pareto domination defined as componentwise no worse with at least one strict improvement. Let `E_J` be the nondominated **candidate IDs** under `J`.

If `x in E_J` but `x not in E_K`, then there is a `y` that dominates `x` on K, and **must tie x on every old objective in J**. Otherwise the same y would strictly dominate x on J, contradicting x in E_J. Therefore the only way for a nondominated candidate to disappear when adding objectives is a tied old-objective projection broken by a newly considered objective. This is a direct elementary fact about the standard Pareto definition, *not* an unprecedented mathematical discovery.

Minimal removal example: two candidates with vectors `A=(0,0), B=(0,1)`. Under first objective only they tie and both belong to `E_{0}`; with both objectives A dominates B. Minimal addition example: `A=(0,1),B=(1,0)`. Under first objective A dominates B; with both objectives neither dominates the other. Consequently, naive unconditional inclusion `E_J subset E_K` is **false for candidate-ID Pareto sets** when equal old-objective vectors occur.

FORGE and VERIFIER checked tie witnesses for each of the 58 removed memberships in this frozen fixture.

## 5. Operator commutation obstruction and information loss

```text
D(x) = |x|
S(x) = 2*floor(x/2)
S(D(-1)) = 0
D(S(-1)) = 2
```

OAK independently verified that **105 / 249** feasible input configurations have different transformed coordinates under O0 and O1. Max L1 discrepancy across the two transformed coordinate vectors on this sample is 4. **All twelve** comparisons of candidate-ID Pareto sets at settings `scale=1, direction=1` give different sets.

This is a precisely typed noncommutation / information-loss phenomenon. It is **not** proof of emergence, physical gauge fields, or a novel causal mechanism. Lossy compressed objective vectors must never erase historical IDs, input signs or source provenance in a scientific or Git evidence registry.

OAK also built both minimal Pareto counterexamples in scalar Python and evaluated lossy mapping duplicates. Its independent result is `EXACT_FALSIFICATION_AND_LOSS_DIAGNOSIS`.

## 6. Reproduce (in an isolated environment)

- [Pure Python R16 independent scalar implementation](r16_front_lattice_reference.py): runs without third-party packages and writes its JSON receipt in the current script directory; asserts the full front digest and prior R15 digest.
- [OAK R16 counterexample and loss guard](r16_adversarial_guard.py): reproduces both minimal Pareto examples, the `D∘S != S∘D` witness, transformed-state collisions and the 12 changed fronts.

No downloading and executing arbitrary Web code is required: these are human-readable public source files; use reviewed local copies and verify the exact commit SHA and source digest before any execution.

## 7. Status of public use and autonomous channels

- Safe public *research reference use* is appropriate: an independently reproduced synthetic benchmark, definitions and falsifiable assertions.
- Claims of science, physical superiority, external datasets validated, real-world performance or universal optimizer efficacy have **not** been demonstrated.
- Publishing uses the already connected authenticated GitHub connector. Direct unattended credentialed writes from each PC, a persistent publisher, inbound access, continuous agents or controlled external deployments were **not** established in this iteration.
- Any GitHub merge or CI promotion requires separate live-branch, test and authority gates; public research files may be copied permanently.
- Preserve `GENERATED != EXECUTED != READBACK != INDEPENDENT_VERIFIED != PUBLISHED != MERGED != DEPLOYED`.

Next exploratory questions: typed transformations of *objective subsets*, information-preserving lifts of sign and scale, history-aware equivalence of candidate IDs, and the inverse map from question families to viable solution families. Compare against established objective-reduction methods and specialist solvers. Preserve TdT and TdNT as distinct provenance families.
