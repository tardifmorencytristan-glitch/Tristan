# TESLA-OMEGA Frontier R0.3

R0.3 replaces the lossless modal-only court with a passive series-RLC coupled-loop surrogate.

For each topology:

- every node has identical nominal L, C, and coil resistance;
- graph edges carry mutual inductance M_ij = k_ij sqrt(L_i L_j);
- one endpoint receives a source resistance;
- the farthest endpoint receives a resistive load;
- the impedance matrix is solved directly in the frequency domain;
- load power and source real power produce a model efficiency;
- deterministic Monte Carlo perturbs L, C, R and coupling.

The court remains bounded to the six unlabeled trees at n=6, all with five edges.

Promotion rule:

A topology that wins the ideal spectral-span court can lose in the RLC robustness court. That loss is desirable information and is recorded rather than hidden.

R0.3 is still a network model. It does not include 3D coil geometry, radiation, skin/proximity effects, dielectric loss, field coupling to the environment, thermal constraints, or experimental measurement.
