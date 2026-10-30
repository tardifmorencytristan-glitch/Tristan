# Ω-MULTI-TRISTAN R15 — Tensorized multidirectional multi-front laboratory

**Status:** INDEPENDENTLY REPRODUCED SYNTHETIC COMPUTATION. **Not** an optimizer superiority result, physics experiment, scientific certification, production rollout, or automatic merge authorization.

## Motivation

The same problem can admit many non-compensatory Pareto fronts, because the objective subset, observation scale and representation vary. In the inverse direction, one candidate can belong to fronts of several problems. Preserve **both** directions; an apparent universal winner is not established by repeated frontier membership.

## Explicit finite mathematical fixture

Enumerate the 289 integer-coordinate candidates `(a,b) in [-8,8]^2`, where each integer coordinate denotes a quarter unit. A candidate is feasible iff `a*a+b*b <= 80`. There are **249 feasible** candidates.

The experiment comprises:
- 3 explicitly chosen synthetic problems `p=0,1,2`;
- 2 scales: exact integer grid or lossy floor quantization to even coordinates;
- 2 directions: signed inputs or lossy absolute-value folding;
- 289 candidates;
- 3 minimized objectives.

The parameter tuple for each problem is `(tx, ty, coupling, sign, offset)`:

| Problem | Parameters |
|---|---|
| P0 | `(4,-4,2,1,0)` |
| P1 | `(-4,4,1,-1,4)` |
| P2 | `(2,2,1,1,-4)` |

For transformed coordinates `(a,b)`, define:
- `fit=(a-tx)^2+(b-ty)^2+coupling*(a-sign*b)^2`;
- `size=a^2+b^2`;
- `residual=(a+b-offset)^2+(p+1)*(a-b)^2`.

For a feasible candidate `c`, objectives `J` are either `(fit,size)`, `(fit,residual)`, `(size,residual)`, or all three. All are minimized. A candidate dominates another iff no selected objective is worse and at least one is strictly better. Tied objective vectors may correspond to distinct parameter candidates; do not silently erase their provenance.

A vectorized implementation produced `T[p,scale,direction,candidate,objective]` of shape **`(3,2,2,289,3)`**, then computed 48 Pareto fronts (3×2×2×4).

For a front `F[p,s,d,J]`, the inverse incidence `G[c]` is the set of contexts in which candidate `c` is Pareto-nondominated. This is a mathematical transpose of frontier membership, not proof of transferability to an unrelated physical problem.

## Reproduction and independent checks

FORGE: NumPy broadcasting, integer arithmetic and vectorized dominance.
VERIFIER: the separate, standard-library-only source **[`r15_multifront_reference.py`](r15_multifront_reference.py)** calculates integer costs and tests dominance with scalar loops; no NumPy broadcasting or copied dominance routine. It checks positive affine objective rescaling and exact forward/inverse incidence transposition.

Both methods reported:
- **48** frontier contexts;
- **249** feasible parameter candidates;
- **629** candidate/front memberships;
- identical SHA-256 over the canonical, sorted-key, compact JSON map `context -> sorted candidate IDs`:

`12bf5ebe0e1be9ea15b3057f9e111db50a94af714668f67d04c027cffeb7cdff`

Reference signed, fine-scale frontier sizes for objective sets `01,02,12,012`:
- P0: `4,4,1,4`
- P1: `11,10,7,12`
- P2: `5,9,5,9`

The candidate `(0,0)` occurs in **44 of 48 frontier contexts** across all three problems; this does not make it a universally optimal or authorized decision. Other candidates and objective subsets lead to different fronts.

OAK: an adversarial reference-model comparison studied all 12 `problem × scale × direction` contexts for the three-objective frontier. The **nine** lossy representation cases are flagged by the guard; in every one, the transformed Pareto front included candidates not nondominated under the original signed exact reference. The guard result is **do not promote lossy routing as an equivalent solver**. Guard rejection is not itself evidence of a better optimization algorithm.

## Existing theory and external baselines

This complements, rather than supersedes, existing Tristan multi-object / multi-scale / multi-direction / multi-objective routing ideas. Non-compensatory Pareto comparison and algorithm selection are established mathematical and engineering concepts. Do not present them as historically new. Independent specialist algorithms, direct baselines, and `NO_ACTION` remain legitimate winners.

## Publication and execution boundary

- The public artifact is a **self-contained synthetic example only**; there are no private repository contents, passwords, credentials, machine addresses, unreviewed personal data or unpublished physical claims.
- GitHub publication uses an authorized GitHub connector, not authenticated Git CLI on all three PCs. A Web-read-back can validate the published code; it does not grant remote code execution authority.
- Reproduction code creates its receipt beside the script when executed. Never execute arbitrary retrieved Web material based only on a published filename or README.
- `GENERATED != EXECUTED != READ_BACK != INDEPENDENT_REPRODUCED != SCIENTIFIC_VALIDATED != DEPLOYED`.
- Source rights, secrecy, licensing, external publishing permissions, branch requirements and independent tests are mandatory before publishing *other* datasets.
- Public contents can be copied irreversibly; network access must remain scoped and revocable.
- `KEEP_SEPARATE`, `NO_M4OPT` and `NO_ACTION` remain admissible.
