# TESLA-OMEGA Frontier R0.6

R0.6 attacks the validity of R0.5 rather than trusting its 24.8x relative gain.

The all-pairs mutual-inductance model is a magnetic-dipole far-field approximation. R0.6 therefore records the minimum center-to-center separation divided by the larger radius for every coil pair.

A conservative screening threshold of 3.0 is used only as an engineering gate for this surrogate. It is not asserted to be a universal electromagnetic validity theorem.

Candidates below the threshold are not called invalid physics. They are marked outside the trusted screening region of this approximation and must move to a stronger mutual-inductance model.

R0.6 also solves the same complex impedance system with two independently implemented algorithms:

1. Gauss-Jordan elimination already used by R0.5.
2. LU elimination with partial pivoting.

Agreement is a software/numerical consistency check only.

The objective is now to distinguish three things:
- apparent gain inside the model;
- numerical reproducibility of that gain;
- whether the model itself is being used in a defensible regime.
