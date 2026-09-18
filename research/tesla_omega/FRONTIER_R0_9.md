# TESLA-OMEGA Frontier R0.9

R0.9 searches for the first perturbation regime that breaks the R0.7 candidate's paired advantage.

Four deterministic stress levels are evaluated:

- S1 mild: +/-2 mm, +/-2 deg, +/-1% radius.
- S2 nominal: +/-5 mm, +/-5 deg, +/-2% radius.
- S3 strong: +/-10 mm, +/-10 deg, +/-5% radius.
- S4 extreme: +/-20 mm, +/-20 deg, +/-10% radius.

The baseline and candidate receive exactly the same random seed at every sample and scenario.

A scenario is considered to have broken the current candidate if candidate win fraction drops below 1.0 or the p10 paired ratio falls to 1.0 or lower.

This criterion is deliberately severe for screening and does not constitute a worst-case mathematical proof.
