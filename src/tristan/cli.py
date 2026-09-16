from __future__ import annotations

import argparse
import json
from pathlib import Path
from .context import compile_context
from .pipeline import run_intent
from .registry import Registry
from .verify import verify_repository


def _root() -> Path:
    return Path.cwd()


def _registry(root: Path) -> Registry:
    return Registry.load(root / "registry/objects.jsonl")


def _print(payload) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tristan")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("verify")
    sub.add_parser("status")

    query = sub.add_parser("query")
    query.add_argument("text")
    query.add_argument("--limit", type=int, default=8)

    run = sub.add_parser("run")
    run.add_argument("intent")
    run.add_argument("--limit", type=int, default=8)

    regen = sub.add_parser("regenerate")
    regen.add_argument("--check", action="store_true", default=True)

    args = parser.parse_args(argv)
    root = _root()

    if args.command == "verify":
        result = verify_repository(root)
        _print(result)
        return 0 if result["status"] == "PASS" else 1

    if args.command == "status":
        reg = _registry(root)
        statuses = {}
        for obj in reg.all():
            statuses[obj.status] = statuses.get(obj.status, 0) + 1
        _print({"objects": len(reg.all()), "by_status": statuses, "authority_granted": False})
        return 0

    if args.command == "query":
        _print(compile_context(args.text, _registry(root), args.limit).to_dict())
        return 0

    if args.command == "run":
        _print(run_intent(args.intent, _registry(root), args.limit).to_dict())
        return 0

    if args.command == "regenerate":
        result = verify_repository(root)
        _print({
            "status": result["status"],
            "mode": "clean_contract_check",
            "rebuild_claimed": False,
            "note": "R0.1 checks that the minimum regeneration seed is structurally complete; it does not rebuild external federated sources.",
            "verify": result,
        })
        return 0 if result["status"] == "PASS" else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
