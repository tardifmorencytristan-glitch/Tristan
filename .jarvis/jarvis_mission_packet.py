from __future__ import annotations

from hashlib import sha256
import argparse
import json
from pathlib import PurePosixPath, Path
import sys


PROTOCOL = "ULTIMATE-JARVIS-TRISTAN-LOCAL-MISSION-PACKET-R1"
ROOT_ROLE_ANCHORS = {
    "CODE": ["skills/MASTER_CONNECTOR_OS_R1.md", "src/tristan_connector_os/ultra_mission_compiler_r1.py"],
    "TESTS": ["src/tristan_connector_os/github_copilot_capability_os.py", ".github/skills/tristan-proof-carrying-pr/SKILL.md"],
    "DOCS": ["docs/ULTIMATE_JARVIS_TRISTAN_REPOSITORY_MESH_R1.md", "skills/OMEGA_CONVERSATION_TO_PROOF_CARRYING_PR_R1.md"],
    "RESEARCH": ["skills/MASTER_CONNECTOR_OS_R1.md", "skills/OMEGA_REVOLUTIONARY_IDEA_GENESIS_R1.md"],
    "CI": [".github/skills/tristan-proof-carrying-pr/SKILL.md", "tools/auto_pr_factory.py"],
    "SECURITY": ["skills/MASTER_CONNECTOR_OS_R1.md", "src/tristan_connector_os/github_copilot_capability_os.py"],
    "ARCHITECTURE": ["README.md", "skills/MASTER_CONNECTOR_OS_R1.md"],
    "OAK": ["governance/JARVIS_TRISTAN_COMMITTEES_R1.json", "AGENTS.md"],
}
ROLE_LOCAL_KINDS = {
    "CODE": {"source"},
    "TESTS": {"test"},
    "DOCS": {"docs"},
    "RESEARCH": {"research", "data", "benchmark", "example"},
    "CI": {"workflow"},
    "SECURITY": {"manifest", "infra"},
    "ARCHITECTURE": {"source", "infra", "docs"},
    "OAK": set(),
}


def _digest(value: object) -> str:
    body = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return "sha256:" + sha256(body.encode("utf-8")).hexdigest()


def _kind(path: str) -> str:
    p = PurePosixPath(path)
    text = path.lower()
    name = p.name.lower()
    parts = {x.lower() for x in p.parts}
    if text.startswith(".github/workflows/"):
        return "workflow"
    if "tests" in parts or "test" in parts or name.startswith("test_") or ".test." in name or ".spec." in name:
        return "test"
    if name.startswith("readme") or text.startswith("docs/") or p.suffix.lower() in {".md", ".rst", ".tex"}:
        return "docs"
    if text.startswith("research/"):
        return "research"
    if text.startswith("data/"):
        return "data"
    if text.startswith("benchmarks/"):
        return "benchmark"
    if text.startswith("examples/"):
        return "example"
    if text.startswith("infra/") or text.startswith("infrastructure/"):
        return "infra"
    if name in {
        "pyproject.toml", "requirements.txt", "setup.py", "package.json",
        "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "cargo.toml",
        "cargo.lock", "go.mod", "go.sum", "pom.xml", "build.gradle",
        "build.gradle.kts", "cmakelists.txt", "dockerfile",
        "docker-compose.yml", "compose.yml",
    }:
        return "manifest"
    return "source"


def _candidate_paths(context: dict) -> list[str]:
    evidence = context.get("evidence", {})
    paths = set()
    for bucket in ("manifests", "test_files", "documentation_files", "workflow_files"):
        paths.update(str(x) for x in evidence.get(bucket, []) or [])
    return sorted(paths)


def compile_packet(intent: str, role_profile: dict, context: dict) -> dict:
    role_router_path = Path(__file__).with_name("jarvis_role_router.py")
    namespace = {}
    exec(role_router_path.read_text(encoding="utf-8"), namespace)
    route = namespace["route"](intent, role_profile)

    selected = list(route["selected_roles"])
    candidates = _candidate_paths(context)
    local_sources = []
    role_packets = []

    for role in selected:
        kinds = ROLE_LOCAL_KINDS.get(role, set())
        role_sources = [path for path in candidates if _kind(path) in kinds]
        local_sources.extend(role_sources)
        role_packets.append({
            "role": role,
            "local_sources": role_sources,
            "root_anchors": ROOT_ROLE_ANCHORS[role],
            "authority_granted": False,
        })

    packet = {
        "protocol": PROTOCOL,
        "intent": intent,
        "route_status": route["status"],
        "selected_roles": selected,
        "missing_roles": route["missing_roles"],
        "local_sources": sorted(set(local_sources)),
        "root_anchors": sorted({
            anchor for role in selected for anchor in ROOT_ROLE_ANCHORS[role]
        }),
        "role_packets": role_packets,
        "grounding_required": 1.0,
        "no_action_available": True,
        "execution_authority_granted": False,
        "promotion_authority_granted": False,
        "generated_is_verified": False,
        "boundaries": [
            "LocalSourceSelection != SourceTruth",
            "ROOTAnchor != LoadedPrivateContent",
            "RoleSelection != ExecutionAuthority",
            "Generated != Verified",
        ],
    }
    packet["digest"] = _digest(packet)
    return packet


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--intent", required=True)
    parser.add_argument("--context", default=".jarvis/JARVIS_LOCAL_CONTEXT.json")
    parser.add_argument("--roles", default=".jarvis/JARVIS_ROLE_PROFILE.json")
    parser.add_argument("--output", default=".jarvis/JARVIS_MISSION_PACKET.json")
    args = parser.parse_args()

    context = json.loads(Path(args.context).read_text(encoding="utf-8"))
    roles = json.loads(Path(args.roles).read_text(encoding="utf-8"))
    packet = compile_packet(args.intent, roles, context)
    Path(args.output).write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0 if packet["route_status"] == "ROUTED" else 2


if __name__ == "__main__":
    sys.exit(main())
