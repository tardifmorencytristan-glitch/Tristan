# TESLA-OMEGA Frontier R0.11

R0.11 attacks the filament-wire idealization.

Each circular conductor is replaced, for mutual-inductance screening, by four equal-weight filament loops sampling the finite circular wire cross-section:

- radius minus d and radius plus d;
- center shifted minus d and plus d along the coil normal;
- d = wire_radius / sqrt(2).

Every pairwise coil mutual inductance is the mean over all 16 filament-pair Neumann integrals.

This is a small quadrature model for finite conductor cross-section. It is stronger than a single center filament but is not an exact field solution.

AC resistance still uses the skin-depth annulus approximation. Proximity-effect losses are deliberately not invented here and remain the next missing physics gate.
