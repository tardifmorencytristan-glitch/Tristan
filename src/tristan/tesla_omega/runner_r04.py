from __future__ import annotations

from .geometry import hex_bridge_geometry
from .geometry_court import geometry_matched_tree_court


def compile_tesla_omega_r04() -> dict[str, object]:
    positions = hex_bridge_geometry()
    court = geometry_matched_tree_court()
    return {
        "schema_version": "tesla-omega-r0.4",
        "status": "GEOMETRY_MATCHED_COMPUTATIONAL_SCREENING_ONLY",
        "authority_granted": False,
        "physical_validation_claimed": False,
        "novelty_claimed": False,
        "geometry": {
            "positions_m": tuple((p.x,p.y,p.z) for p in positions),
            "source_node": 0,
            "receiver_node": 5,
            "source_receiver_separation_m": 0.50,
            "reference_k_at_0p10m": 0.08,
            "distance_exponent": 3.0,
            "orientation_model": "coaxial-equivalent scalar surrogate",
        },
        "court": court,
        "boundaries": (
            "FixedGeometry != RealCoilGeometry",
            "DistanceDerivedK != MutualInductanceMeasurement",
            "ScalarOrientationModel != FullVectorEM",
            "NetworkSurrogate != MaxwellFieldSolution",
            "Simulation != Measurement",
        ),
    }
