from __future__ import annotations

from dataclasses import replace

from .models import OAKVector, Status


_ORDER = {
    Status.UNKNOWN: 0,
    Status.DOCUMENTED: 1,
    Status.FORMALIZED: 2,
    Status.SIMULATED: 3,
    Status.REPRODUCED: 4,
    Status.MEASURED: 5,
    Status.CERTIFIED: 6,
}


def can_promote(current: Status, target: Status) -> bool:
    if current == Status.CONTRADICTED:
        return False
    if target == Status.CONTRADICTED:
        return True
    return _ORDER.get(target, -1) == _ORDER.get(current, -1) + 1


def promote(vector: OAKVector, domain: str, target: Status) -> OAKVector:
    if domain not in {"documentary", "mathematical", "computational", "experimental"}:
        raise ValueError(f"unknown OAK domain: {domain}")
    current = getattr(vector, domain)
    if not can_promote(current, target):
        raise ValueError(f"illegal promotion {domain}: {current.value} -> {target.value}")
    return replace(vector, **{domain: target})
