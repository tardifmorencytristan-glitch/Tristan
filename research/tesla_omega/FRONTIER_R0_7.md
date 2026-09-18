# TESLA-OMEGA Frontier R0.7

R0.7 replaces the far-field magnetic-dipole mutual-inductance approximation for promoted candidates with a numerical Neumann filament integral.

For two circular filament loops:

M = mu0/(4 pi) double_integral (dl1 dot dl2)/|r1-r2|.

Each circular loop is discretized into straight segments. Mutual inductance is evaluated by midpoint quadrature over segment pairs.

R0.7 checks convergence at multiple segment counts and preserves all-pairs coupling. It also retains two independent linear-system solvers and real-power closure.

This is materially stronger than the dipole model for nearby loops, but it is still not a full electromagnetic field model. Finite conductor cross-section, proximity effect, radiation, dielectric environment, nearby materials and thermal behavior remain absent.

Only the top model-valid R0.6 candidates are escalated to the more expensive Neumann court. This is the multi-fidelity funnel in executable form.
