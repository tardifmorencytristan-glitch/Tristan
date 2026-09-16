from __future__ import annotations

from dataclasses import dataclass
from .context import compile_context
from .registry import Registry

MEMORY_STATES = {"M+", "M-", "M?", "MΔ", "M⊥", "M∅"}


@dataclass(frozen=True)
class ConceptIdentity:
    concept_id: str
    canonical_name: str
    aliases: tuple[str, ...] = ()
    supersedes: tuple[str, ...] = ()

    def matches(self, text: str) -> bool:
        t = text.casefold()
        return self.canonical_name.casefold() in t or any(a.casefold() in t for a in self.aliases)


@dataclass(frozen=True)
class ContextDebt:
    missing_dependencies: tuple[str, ...] = ()
    missing_failures: tuple[str, ...] = ()
    stale_objects: tuple[str, ...] = ()
    duplicate_concepts: tuple[str, ...] = ()

    @property
    def clean(self) -> bool:
        return not any((self.missing_dependencies, self.missing_failures, self.stale_objects, self.duplicate_concepts))


@dataclass(frozen=True)
class RehydratedContext:
    query: str
    seed_ids: tuple[str, ...]
    selected_ids: tuple[str, ...]
    memory_ids: tuple[str, ...]
    debt: ContextDebt
    invariant: str = "rehydrated_context_is_projection_not_current_truth"


def resolve_concepts(text: str, identities: tuple[ConceptIdentity, ...]) -> tuple[str, ...]:
    return tuple(i.concept_id for i in identities if i.matches(text))


def _closure(seed_ids: tuple[str, ...], registry: Registry) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    selected = set(seed_ids)
    missing_deps: set[str] = set()
    missing_failures: set[str] = set()
    queue = list(seed_ids)
    while queue:
        oid = queue.pop(0)
        obj = registry.get(oid)
        if obj is None:
            continue
        for dep in obj.dependencies:
            if registry.get(dep) is None:
                missing_deps.add(dep)
            elif dep not in selected:
                selected.add(dep); queue.append(dep)
        for failure in obj.failures:
            if registry.get(failure) is None:
                missing_failures.add(failure)
            elif failure not in selected:
                selected.add(failure); queue.append(failure)
    return tuple(sorted(selected)), tuple(sorted(missing_deps)), tuple(sorted(missing_failures))


def audit_registry_context(registry: Registry) -> ContextDebt:
    missing_deps: set[str] = set()
    missing_failures: set[str] = set()
    stale: set[str] = set()
    for obj in registry.all():
        missing_deps.update(dep for dep in obj.dependencies if registry.get(dep) is None)
        missing_failures.update(f for f in obj.failures if registry.get(f) is None)
        if bool(obj.metadata.get("stale", False)):
            stale.add(obj.id)
    return ContextDebt(tuple(sorted(missing_deps)), tuple(sorted(missing_failures)), tuple(sorted(stale)), ())


def rehydrate_context(query: str, registry: Registry, limit: int = 8) -> RehydratedContext:
    receipt = compile_context(query, registry, limit=limit)
    selected, missing_deps, missing_failures = _closure(receipt.selected_ids, registry)
    memory_ids = tuple(sorted(
        oid for oid in selected
        if str(registry.require(oid).metadata.get("memory_state", "")) in MEMORY_STATES
    ))
    stale = tuple(sorted(
        oid for oid in selected
        if bool(registry.require(oid).metadata.get("stale", False))
    ))
    debt = ContextDebt(missing_deps, missing_failures, stale, ())
    return RehydratedContext(query, receipt.selected_ids, selected, memory_ids, debt)


def context_ci(ctx: RehydratedContext) -> tuple[str, ...]:
    failures: list[str] = []
    if not ctx.seed_ids:
        failures.append("EMPTY_CONTEXT")
    if ctx.debt.missing_dependencies:
        failures.append("MISSING_DEPENDENCY")
    if ctx.debt.missing_failures:
        failures.append("MISSING_NEGATIVE_MEMORY")
    if ctx.debt.stale_objects:
        failures.append("STALE_CONTEXT")
    return tuple(failures)
