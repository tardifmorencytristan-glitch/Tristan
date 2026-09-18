from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class Status(str, Enum):
    UNKNOWN = "UNKNOWN"
    DOCUMENTED = "DOCUMENTED"
    FORMALIZED = "FORMALIZED"
    SIMULATED = "SIMULATED"
    REPRODUCED = "REPRODUCED"
    MEASURED = "MEASURED"
    CERTIFIED = "CERTIFIED"
    CONTRADICTED = "CONTRADICTED"


@dataclass(frozen=True)
class OAKVector:
    documentary: Status = Status.UNKNOWN
    mathematical: Status = Status.UNKNOWN
    computational: Status = Status.UNKNOWN
    experimental: Status = Status.UNKNOWN

    def to_dict(self) -> dict[str, str]:
        return {k: v.value for k, v in asdict(self).items()}


@dataclass(frozen=True)
class Evidence:
    id: str
    kind: str
    title: str
    url: str
    year: int | None = None
    primary: bool = False
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Claim:
    id: str
    statement: str
    category: str
    source_ids: tuple[str, ...] = field(default_factory=tuple)
    prediction: str = ""
    observable: str = ""
    falsifier: str = ""
    oak: OAKVector = field(default_factory=OAKVector)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["source_ids"] = list(self.source_ids)
        payload["oak"] = self.oak.to_dict()
        return payload
