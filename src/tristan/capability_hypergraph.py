from __future__ import annotations

from dataclasses import dataclass, field

from .capability_registry import CapabilityRecord


@dataclass(frozen=True)
class CapabilityComposition:
    name: str
    members: tuple[str, ...]
    covers: tuple[str, ...]
    evidence_receipts: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    cost_hint: float = 1.0


@dataclass
class CapabilityHypergraph:
    records: dict[str, CapabilityRecord]
    compositions: list[CapabilityComposition] = field(default_factory=list)

    @classmethod
    def from_registry(cls, registry: tuple[CapabilityRecord, ...]) -> "CapabilityHypergraph":
        return cls({r.capability.name: r for r in registry})

    def add_composition(self, composition: CapabilityComposition) -> None:
        missing = [m for m in composition.members if m not in self.records]
        if missing:
            raise KeyError(f"unknown capability members: {missing}")
        self.compositions.append(composition)

    def alternatives_for(self, requirement_key: str) -> list[CapabilityComposition]:
        out: list[CapabilityComposition] = []
        for rec in self.records.values():
            if requirement_key in rec.capability.covers:
                out.append(CapabilityComposition(
                    rec.capability.name,
                    (rec.capability.name,),
                    rec.capability.covers,
                    rec.evidence_receipts,
                    rec.limitations,
                    1.0,
                ))
        out.extend(c for c in self.compositions if requirement_key in c.covers)
        return out

    def minimal_cover(self, requirements: set[str]) -> list[CapabilityComposition]:
        remaining = set(requirements)
        chosen: list[CapabilityComposition] = []
        candidates = list(self.compositions)
        candidates.extend(
            CapabilityComposition(r.capability.name, (r.capability.name,), r.capability.covers,
                                  r.evidence_receipts, r.limitations, 1.0)
            for r in self.records.values()
        )
        while remaining:
            best = max(
                candidates,
                key=lambda c: (len(remaining.intersection(c.covers)) / max(c.cost_hint, 1e-9)),
                default=None,
            )
            if best is None:
                break
            gain = remaining.intersection(best.covers)
            if not gain:
                break
            chosen.append(best)
            remaining -= gain
            candidates = [c for c in candidates if c.name != best.name]
        return chosen
