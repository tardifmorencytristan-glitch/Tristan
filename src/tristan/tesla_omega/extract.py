from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class PatentSeed:
    source_id: str
    patent_number: str
    title: str
    year: int
    device_family: str
    reconstructable_objects: tuple[str, ...]
    explicit_unknowns: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["reconstructable_objects"] = list(self.reconstructable_objects)
        payload["explicit_unknowns"] = list(self.explicit_unknowns)
        return payload


PATENT_SEEDS = (
    PatentSeed(
        "S001",
        "US454622A",
        "System of Electric Lighting",
        1891,
        "high_frequency_lighting",
        ("source", "oscillatory circuit", "transformer/coupling", "load/lighting element"),
        ("complete component values", "distributed parasitics", "measured efficiency"),
    ),
    PatentSeed(
        "S002",
        "US613809A",
        "Method of and apparatus for controlling mechanism of moving vessels or vehicles",
        1898,
        "remote_control",
        ("transmitter", "receiver", "switching/relay logic", "actuator"),
        ("channel transfer function", "noise environment", "measured reliability"),
    ),
    PatentSeed(
        "S003",
        "US645576A",
        "System of transmission of electrical energy",
        1900,
        "energy_transmission",
        ("source", "elevated terminal", "resonant transformer", "receiver concept"),
        ("full equivalent circuit", "ground/return impedance", "measured end-to-end efficiency"),
    ),
)


def compile_extraction_queue() -> tuple[dict[str, object], ...]:
    queue: list[dict[str, object]] = []
    for seed in PATENT_SEEDS:
        for unknown in seed.explicit_unknowns:
            queue.append({
                "source_id": seed.source_id,
                "patent_number": seed.patent_number,
                "missing": unknown,
                "action": "SEARCH_PRIMARY_OR_REPLICATION_SOURCE",
                "promotion_blocked": True,
            })
    return tuple(queue)
