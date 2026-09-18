# TESLA-OMEGA Frontier R0.5

R0.5 removes the artificial edge-only coupling graph from the physical court.

Every pair of physical coils couples. The first all-pairs model uses a signed magnetic-dipole approximation based on coil areas, normals, and center-to-center displacement.

All six coils use the same wire radius and one turn. The symmetric radius schedule [a,b,c,c,b,a] is searched under the exact constraint a+b+c = 0.09 m, so total circular conductor length is identical to the six-coil baseline radius of 0.03 m.

Each coil self-inductance is approximated by the high-frequency thin-loop expression, each resonator is individually tuned to the common target frequency, and copper AC resistance is approximated from skin depth and the conducting annulus.

The model adds two internal closure gates:

- max |Z I - V| for the solved complex linear system;
- real-power closure between source input, source resistance, copper loss, and load.

These are computational consistency checks, not experimental validation.

The major conceptual change is that physical architecture is now represented by geometry and resonator parameters. A graph edge no longer gets to turn electromagnetic coupling on or off by declaration.
