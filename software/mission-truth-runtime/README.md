# Mission Truth Runtime Crystal R204

This crystal packages the bounded runtime lineage R200-R204 into a regenerable repository surface.

## Pipeline

Mission/DAG -> measured runtime requirements -> capability auction -> minimal qualified coalition -> WorkerTruth execution -> artifact + receipt -> effect ledger -> independent peer integrity -> effect verification -> external outcome gate.

## Current evidence

- R202 live canary: selected=1, verified=1, authority=false, external_side_effects=false.
- R203: two independent peer nodes recomputed the complete receipt digest and byte-exact artifact SHA-256 with INDEPENDENT_INTEGRITY_PASS.
- R203: resource-aware auction selects DESKTOP-SHA9IHL for high-headroom work and re-auctions a general task to DESKTOP-2G1SSMT when SHA9IHL is excluded.
- R204: local effect is verified while mission outcome remains HOLD without fresh independent external outcome evidence.

## Epistemic boundary

Execution evidence, artifact integrity, peer quorum, and local effect evidence do not establish external mission success. Capability does not grant authority.

## Qualification

Run:

python -m unittest discover -s tests -v

The focused crystal court currently passes 5/5 tests.
