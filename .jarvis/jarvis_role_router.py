from __future__ import annotations

from hashlib import sha256
import argparse
import json
from pathlib import Path
import sys


PROTOCOL = "ULTIMATE-JARVIS-TRISTAN-LOCAL-ROLE-MESH-R1"
ROLE_ORDER = ("CODE", "TESTS", "DOCS", "RESEARCH", "CI", "SECURITY", "ARCHITECTURE", "OAK")
ROLE_SIGNALS = {
    "CODE": {
        "python", "javascript", "typescript", "rust", "go", "java", "kotlin",
        "c", "cpp", "csharp", "ruby", "php", "swift", "scala", "shell",
        "powershell", "r", "julia", "lua", "sql",
    },
    "TESTS": {"tests-observed"},
    "DOCS": {"documentation-observed", "markdown", "latex"},
    "RESEARCH": {"surface:research", "surface:data", "surface:benchmarks", "surface:examples", "latex"},
    "CI": {"github-actions-observed"},
    "SECURITY": {
        "python-dependencies", "node-package", "rust-package", "go-module",
        "maven-project", "gradle-project", "container-build", "container-compose",
        "surface:infra", "surface:infrastructure",
    },
    "ARCHITECTURE": {
        "surface:src", "surface:lib", "surface:app", "surface:apps",
        "surface:packages", "surface:services", "surface:service",
        "surface:infra", "surface:infrastructure", "surface:tools",
    },
    "OAK": set(),
}
MISSION_KEYWORDS = {
    "CODE": ("code", "implement", "implementation", "refactor", "fix", "bug", "feature", "function", "class", "module", "api", "runtime"),
    "TESTS": ("test", "tests", "testing", "regression", "benchmark", "verify", "validation"),
    "DOCS": ("doc", "docs", "documentation", "readme", "write", "draft", "explain", "paper"),
    "RESEARCH": ("research", "evidence", "experiment", "scientific", "science", "dataset", "data", "prior art", "hypothesis", "paper", "benchmark"),
    "CI": ("ci", "workflow", "github actions", "pipeline", "build", "deploy", "release"),
    "SECURITY": ("security", "secret", "dependency", "dependencies", "vulnerability", "supply chain", "permission", "authority", "credential"),
    "ARCHITECTURE": ("architecture", "design", "system", "dependency graph", "structure", "integration", "repository", "repo"),
}


def _digest(value: object) -> str:
    body = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return "sha256:" + sha256(body.encode("utf-8")).hexdigest()


def _signals(context: dict) -> set[str]:
    found = set(str(x) for x in context.get("capabilities", []))
    found.update(str(x) for x in context.get("primary_languages", []))
    found.update(
        "surface:" + str(x)
        for x in context.get("evidence", {}).get("architecture_surfaces", [])
    )
    return found


def compile_role_profile(context: dict) -> dict:
    source_digest = str(context.get("digest", ""))
    if not source_digest:
        raise ValueError("local context digest required")
    signals = _signals(context)
    roles = []
    for role in ROLE_ORDER:
        observed = sorted(signals.intersection(ROLE_SIGNALS[role]))
        available = role == "OAK" or bool(observed)
        roles.append({
            "role": role,
            "available": available,
            "observed_signals": observed,
            "producer": role not in {"OAK", "TESTS"},
            "verifier": role in {"TESTS", "OAK"},
            "promotion_authority": False,
        })
    profile = {
        "protocol": PROTOCOL,
        "source_context_digest": source_digest,
        "available_roles": [x["role"] for x in roles if x["available"]],
        "unavailable_roles": [x["role"] for x in roles if not x["available"]],
        "roles": roles,
        "authority_granted": False,
    }
    profile["digest"] = _digest(profile)
    return profile


def requested_roles(intent: str) -> list[str]:
    normalized = " ".join(str(intent).lower().split())
    requested = set()
    for role, terms in MISSION_KEYWORDS.items():
        if any(term in normalized for term in terms):
            requested.add(role)
    if not requested:
        requested.add("ARCHITECTURE")
    if "CODE" in requested:
        requested.add("TESTS")
    requested.add("OAK")
    return [role for role in ROLE_ORDER if role in requested]


def route(intent: str, profile: dict) -> dict:
    requested = requested_roles(intent)
    available = set(profile.get("available_roles", []))
    selected = [role for role in requested if role in available]
    missing = [role for role in requested if role not in available]
    receipt = {
        "protocol": PROTOCOL,
        "intent": intent,
        "requested_roles": requested,
        "selected_roles": selected,
        "missing_roles": missing,
        "status": "ROUTED" if not missing else "HOLD_CAPABILITY_GAP",
        "no_action_available": True,
        "execution_authority_granted": False,
        "promotion_authority_granted": False,
        "boundaries": [
            "ObservedRole != ExecutedRole",
            "RoleSelection != ExecutionAuthority",
            "Generator != Verifier != PromotionAuthority",
            "OAK != Producer",
            "Coalition != Authority",
        ],
    }
    receipt["digest"] = _digest(receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", default=".jarvis/JARVIS_LOCAL_CONTEXT.json")
    parser.add_argument("--profile-output", default=".jarvis/JARVIS_ROLE_PROFILE.json")
    parser.add_argument("--intent", default="")
    parser.add_argument("--route-output", default=".jarvis/JARVIS_MISSION_ROUTE.json")
    args = parser.parse_args()

    context = json.loads(Path(args.context).read_text(encoding="utf-8"))
    profile = compile_role_profile(context)
    Path(args.profile_output).write_text(
        json.dumps(profile, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(profile, indent=2, sort_keys=True))

    if args.intent:
        mission = route(args.intent, profile)
        Path(args.route_output).write_text(
            json.dumps(mission, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(mission, indent=2, sort_keys=True))
        return 0 if mission["status"] == "ROUTED" else 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
