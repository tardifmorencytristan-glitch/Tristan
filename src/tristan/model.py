from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

ALLOWED_STATUSES = {
    "IDEA", "PROVISIONAL", "HOLD", "SUPPORTED", "MEASURED",
    "VERIFIED_ENGINEERING", "CLOSED", "REJECTED", "SUPERSEDED",
    "RESIDUAL", "UNAVAILABLE",
}


@dataclass(frozen=True)
class TristanObject:
    id: str
    kind: str
    title: str
    status: str
    summary: str
    tags: tuple[str, ...] = ()
    canonical_url: str | None = None
    exact_url: str | None = None
    version_hash: str | None = None
    evidence_urls: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    failures: tuple[str, ...] = ()
    frontiers: tuple[str, ...] = ()
    authority: dict[str, bool] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TristanObject":
        validate_object_dict(data)
        cooked = dict(data)
        for name in {"tags", "evidence_urls", "dependencies", "failures", "frontiers"}:
            cooked[name] = tuple(cooked.get(name, ()))
        cooked.setdefault("authority", {})
        cooked.setdefault("metadata", {})
        for name in {"canonical_url", "exact_url", "version_hash"}:
            cooked.setdefault(name, None)
        return cls(**cooked)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "title": self.title,
            "status": self.status,
            "summary": self.summary,
            "tags": list(self.tags),
            "canonical_url": self.canonical_url,
            "exact_url": self.exact_url,
            "version_hash": self.version_hash,
            "evidence_urls": list(self.evidence_urls),
            "dependencies": list(self.dependencies),
            "failures": list(self.failures),
            "frontiers": list(self.frontiers),
            "authority": dict(self.authority),
            "metadata": dict(self.metadata),
        }


def validate_object_dict(data: dict[str, Any]) -> None:
    required = ("id", "kind", "title", "status", "summary")
    missing = [key for key in required if not data.get(key)]
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")
    if data["status"] not in ALLOWED_STATUSES:
        raise ValueError(f"unsupported status: {data['status']}")
    for name in ("tags", "evidence_urls", "dependencies", "failures", "frontiers"):
        value = data.get(name, [])
        if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
            raise ValueError(f"{name} must be a list of strings")
    authority = data.get("authority", {})
    if not isinstance(authority, dict) or not all(
        isinstance(k, str) and isinstance(v, bool) for k, v in authority.items()
    ):
        raise ValueError("authority must map strings to booleans")
