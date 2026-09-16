from __future__ import annotations

import json
from pathlib import Path
from .context_rehydration import audit_registry_context
from .registry import Registry

REQUIRED_PATHS = (
    "README.md",
    "pyproject.toml",
    "registry/objects.jsonl",
    "schemas/tristan-object.schema.json",
    "src/tristan/model.py",
    "src/tristan/registry.py",
    "src/tristan/context.py",
    "src/tristan/context_rehydration.py",
    "src/tristan/pipeline.py",
)

HARD_INVARIANTS = (
    "Generated != Verified",
    "Capability != Authority",
    "OriginBonus = 0",
    "NO_ACTION is admissible",
)


def verify_repository(root: str | Path) -> dict:
    root = Path(root)
    missing = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    errors = []
    if missing:
        errors.append("missing paths: " + ", ".join(missing))

    registry_path = root / "registry/objects.jsonl"
    registry_count = 0
    context_debt = None
    if registry_path.exists():
        try:
            registry = Registry.load(registry_path)
            registry_count = len(registry.all())
            context_debt = audit_registry_context(registry)
            if context_debt.missing_dependencies:
                errors.append("context debt missing dependencies: " + ", ".join(context_debt.missing_dependencies))
            if context_debt.missing_failures:
                errors.append("context debt missing negative-memory refs: " + ", ".join(context_debt.missing_failures))
            if context_debt.stale_objects:
                errors.append("context debt stale objects: " + ", ".join(context_debt.stale_objects))
        except Exception as exc:
            errors.append(f"registry invalid: {exc}")

    schema_path = root / "schemas/tristan-object.schema.json"
    if schema_path.exists():
        try:
            json.loads(schema_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"schema invalid JSON: {exc}")

    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").exists() else ""
    for invariant in HARD_INVARIANTS:
        if invariant not in readme:
            errors.append(f"README missing invariant: {invariant}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "registry_count": registry_count,
        "context_debt_clean": bool(context_debt.clean) if context_debt is not None else False,
        "scope": "repository_structure_registry_and_context_debt_only",
        "scientific_pass": False,
    }
