from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class CodeIR:
    id: str
    language: str
    modules: list[str] = field(default_factory=list)
    interfaces: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)
    benchmarks: list[str] = field(default_factory=list)
    provenance: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GitIR:
    id: str
    repository: str
    branch: str
    head_sha: str
    commits: list[str] = field(default_factory=list)
    checks: list[dict[str, Any]] = field(default_factory=list)
    provenance: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DocumentIR:
    id: str
    title: str
    document_type: str
    claim_ids: list[str] = field(default_factory=list)
    sections: list[dict[str, Any]] = field(default_factory=list)
    provenance: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SpecIR:
    id: str
    title: str
    constraints: list[dict[str, Any]] = field(default_factory=list)
    revision: str = ""
    provenance: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_domain_ir(obj: Any) -> list[str]:
    errors: list[str] = []
    for key in ("id", "provenance"):
        if not getattr(obj, key, None):
            errors.append(f"{obj.__class__.__name__}.{key} required")
    if isinstance(obj, GitIR):
        if not obj.repository or not obj.branch or not obj.head_sha:
            errors.append("GitIR repository/branch/head_sha required")
    if isinstance(obj, DocumentIR) and not obj.title:
        errors.append("DocumentIR.title required")
    if isinstance(obj, SpecIR) and not obj.title:
        errors.append("SpecIR.title required")
    if isinstance(obj, CodeIR) and not obj.language:
        errors.append("CodeIR.language required")
    return errors
