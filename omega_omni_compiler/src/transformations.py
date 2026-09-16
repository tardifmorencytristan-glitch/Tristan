from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Callable, Any

REVERSIBILITY = {"LOSSLESS", "APPROX_REVERSIBLE", "LOSSY", "NON_INVERTIBLE"}


@dataclass(frozen=True)
class Transformation:
    id: str
    input_types: tuple[str, ...]
    output_types: tuple[str, ...]
    operator: str
    preconditions: tuple[str, ...] = ()
    preserved_invariants: tuple[str, ...] = ()
    known_losses: tuple[str, ...] = ()
    verifier: str = ""
    reversibility: str = "LOSSY"
    cost: float = 1.0
    risk: float = 0.0

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.id:
            errors.append("id required")
        if not self.input_types or not self.output_types:
            errors.append("input_types and output_types required")
        if self.reversibility not in REVERSIBILITY:
            errors.append("invalid reversibility")
        if self.cost < 0 or self.risk < 0:
            errors.append("cost/risk must be non-negative")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class TransformationRegistry:
    def __init__(self) -> None:
        self._items: dict[str, Transformation] = {}

    def register(self, transform: Transformation) -> None:
        errors = transform.validate()
        if errors:
            raise ValueError(errors)
        if transform.id in self._items:
            raise ValueError(f"duplicate transformation: {transform.id}")
        self._items[transform.id] = transform

    def all(self) -> list[Transformation]:
        return list(self._items.values())

    def by_input(self, input_type: str) -> list[Transformation]:
        return [t for t in self._items.values() if input_type in t.input_types]

    def get(self, transform_id: str) -> Transformation:
        return self._items[transform_id]


def default_registry() -> TransformationRegistry:
    r = TransformationRegistry()
    for t in [
        Transformation("scientific_to_document", ("SCIENTIFIC",), ("DOCUMENT",), "scientific_document_adapter", preserved_invariants=("claims", "status", "scope", "uncertainty"), verifier="semantic_checksum", reversibility="APPROX_REVERSIBLE", cost=1.0),
        Transformation("document_to_scientific", ("DOCUMENT",), ("SCIENTIFIC",), "document_reverse_compiler", preserved_invariants=("claims", "citations"), known_losses=("layout",), verifier="claim_set_compare", reversibility="APPROX_REVERSIBLE", cost=2.0),
        Transformation("scientific_to_code", ("SCIENTIFIC",), ("CODE",), "research_code_bridge", preserved_invariants=("equations", "assumptions", "units"), known_losses=("prose_context",), verifier="cross_representation_tests", reversibility="LOSSY", cost=3.0),
        Transformation("code_to_git", ("CODE",), ("GIT",), "git_materializer", preserved_invariants=("tests", "provenance"), verifier="exact_head_ci", reversibility="APPROX_REVERSIBLE", cost=1.5),
        Transformation("git_to_document", ("GIT",), ("DOCUMENT",), "git_document_adapter", preserved_invariants=("commit_sha", "tests", "receipts"), verifier="source_link_check", reversibility="LOSSY", cost=1.0),
        Transformation("document_to_artifact", ("DOCUMENT",), ("ARTIFACT",), "artifact_compiler", preserved_invariants=("claims", "figures", "citations"), verifier="readback", reversibility="LOSSY", cost=1.0),
        Transformation("artifact_to_document", ("ARTIFACT",), ("DOCUMENT",), "artifact_reverse_compiler", preserved_invariants=("visible_text", "structure"), known_losses=("source_semantics",), verifier="loss_ledger", reversibility="LOSSY", cost=2.5),
        Transformation("spec_to_code", ("SPEC",), ("CODE",), "constraint_test_compiler", preserved_invariants=("limits", "units", "conditions"), verifier="constraint_tests", reversibility="LOSSY", cost=2.0),
    ]:
        r.register(t)
    return r
