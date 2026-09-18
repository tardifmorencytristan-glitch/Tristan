# TESLA-OMEGA Frontier R0.10

R0.10 adds an explicit mechanical-admissibility gate before interpreting robustness samples.

For every coil pair, a conservative bounding-sphere clearance condition is checked:

center_distance >= radius_i + radius_j + clearance

with a default 5 mm clearance.

This is intentionally conservative for tilted circular loops. Passing means the pair is certainly separated under the sphere approximation. Failing does not prove that the real finite wires intersect, so rejected samples are labeled MECHANICAL_REJECT rather than physical impossibilities.

The R0.9 extreme stress envelope is re-evaluated. Every sample is now classified into:

- mechanically rejected;
- mechanically valid and candidate wins;
- mechanically valid and candidate loses.

Mechanical rejection is never counted as a performance loss.

The next stronger gate is detailed finite-wire geometry rather than further increasing random stress amplitudes.
