# TESLA-OMEGA Frontier R0.8

R0.8 tests whether the R0.7 equal-copper radius schedule survives paired geometric perturbations.

Baseline and candidate receive the same deterministic random seed for each sample. The court perturbs:

- intermediate resonator centers by up to +/-5 mm in x, y and z;
- coil normals by up to +/-5 degrees on two axes;
- coil radii by +/-2 percent;
- Tx and Rx centers remain fixed.

Each perturbed system is retuned using its perturbed coil self-inductance and evaluated with all-pairs Neumann filament mutual inductance.

The primary metric is paired candidate/baseline efficiency ratio, supplemented by candidate win fraction, p10, minimum and standard deviation.

This is a robustness screen, not a manufacturing or experimental validation.
