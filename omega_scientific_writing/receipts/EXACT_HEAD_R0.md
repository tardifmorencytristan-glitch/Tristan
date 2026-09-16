# Exact-head verification

Observed branch head before receipt update: `7a4adf1361ffcaf8c6d6be858ab54b13084379ec`.

Observed GitHub Actions on that exact head:

- `Omega Scientific Writing R0`: PASS.
  - Unit tests: PASS.
  - Positive fixture lint: PASS.
  - Negative fixture rejection: PASS.
- `kernel-ci`: PASS across observed Python 3.11, 3.12, 3.13 and 3.14 jobs.
  - Compile: PASS.
  - Unit tests: PASS.
  - Kernel verify: PASS.
  - Retrieval court R0.2: PASS.

OAK boundary: this receipt proves the software gates above on that exact commit. It does **not** prove full Polytechnique compliance, PDF build/readback, scientific truth, novelty, or experimental validity.

Promotion rule: after this receipt commit, the new exact head must itself pass applicable CI before merge.
