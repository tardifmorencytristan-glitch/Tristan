from __future__ import annotations

from hashlib import sha256
import argparse
import json
from pathlib import Path
import sys


PROTOCOL = "ULTIMATE-JARVIS-TRISTAN-LOCAL-SPECIALIZATION-R1"
IGNORE_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", ".jarvis", "node_modules",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "dist", "build", "target", "vendor",
}
LANGUAGE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".rs": "rust",
    ".go": "go",
    ".java": "java",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".c": "c",
    ".h": "c-cpp-header",
    ".cc": "cpp",
    ".cpp": "cpp",
    ".cxx": "cpp",
    ".hpp": "c-cpp-header",
    ".cs": "csharp",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".scala": "scala",
    ".sh": "shell",
    ".ps1": "powershell",
    ".r": "r",
    ".R": "r",
    ".jl": "julia",
    ".lua": "lua",
    ".sql": "sql",
    ".tex": "latex",
    ".md": "markdown",
}
MANIFEST_CAPABILITIES = {
    "pyproject.toml": ("python-packaging", "python"),
    "requirements.txt": ("python-dependencies", "python"),
    "setup.py": ("python-packaging", "python"),
    "package.json": ("node-package", "javascript-typescript"),
    "package-lock.json": ("node-lockfile", "javascript-typescript"),
    "pnpm-lock.yaml": ("pnpm-lockfile", "javascript-typescript"),
    "yarn.lock": ("yarn-lockfile", "javascript-typescript"),
    "Cargo.toml": ("rust-package", "rust"),
    "Cargo.lock": ("rust-lockfile", "rust"),
    "go.mod": ("go-module", "go"),
    "go.sum": ("go-lockfile", "go"),
    "pom.xml": ("maven-project", "java"),
    "build.gradle": ("gradle-project", "java-kotlin"),
    "build.gradle.kts": ("gradle-project", "java-kotlin"),
    "CMakeLists.txt": ("cmake-project", "c-cpp"),
    "Dockerfile": ("container-build", "container"),
    "docker-compose.yml": ("container-compose", "container"),
    "compose.yml": ("container-compose", "container"),
}
ARCHITECTURE_DIRS = (
    "src", "lib", "app", "apps", "packages", "services", "service",
    "infra", "infrastructure", "scripts", "tools", "docs", "tests",
    "test", "examples", "benchmarks", "research", "data",
)


def _digest(value: object) -> str:
    body = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return "sha256:" + sha256(body.encode("utf-8")).hexdigest()


def _walk(root: Path, max_files: int) -> list[Path]:
    found = []
    for path in root.rglob("*"):
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        if any(part in IGNORE_DIRS for part in rel.parts):
            continue
        if path.is_file():
            found.append(rel)
            if len(found) >= max_files:
                break
    return sorted(found, key=lambda p: p.as_posix())


def _is_test_path(path: Path) -> bool:
    name = path.name.lower()
    parts = {part.lower() for part in path.parts}
    return (
        "tests" in parts
        or "test" in parts
        or name.startswith("test_")
        or name.endswith("_test.py")
        or name.endswith("_test.go")
        or ".test." in name
        or ".spec." in name
    )


def scan_repository(root: Path, *, max_files: int = 20000) -> dict:
    files = _walk(root, max_files)
    paths = [path.as_posix() for path in files]
    path_set = set(paths)

    language_counts = {}
    for path in files:
        language = LANGUAGE_EXTENSIONS.get(path.suffix)
        if language:
            language_counts[language] = language_counts.get(language, 0) + 1

    manifests = []
    capabilities = set()
    for filename, implied in MANIFEST_CAPABILITIES.items():
        matches = [path for path in paths if path == filename or path.endswith("/" + filename)]
        if matches:
            manifests.extend(matches)
            capabilities.update(implied)

    test_files = [path for path in paths if _is_test_path(Path(path))]
    if test_files:
        capabilities.add("tests-observed")

    docs = [
        path for path in paths
        if Path(path).name.lower().startswith("readme")
        or path.startswith("docs/")
        or path.endswith(".md")
    ]
    if docs:
        capabilities.add("documentation-observed")

    workflows = [
        path for path in paths
        if path.startswith(".github/workflows/")
        and (path.endswith(".yml") or path.endswith(".yaml"))
    ]
    if workflows:
        capabilities.add("github-actions-observed")

    architecture = [
        name for name in ARCHITECTURE_DIRS
        if any(path == name or path.startswith(name + "/") for path in paths)
    ]
    capabilities.update("surface:" + name for name in architecture)

    dependency_surfaces = sorted(set(manifests))
    primary_languages = sorted(
        language_counts,
        key=lambda name: (-language_counts[name], name),
    )

    evidence = {
        "manifests": sorted(set(manifests)),
        "test_files": test_files[:256],
        "documentation_files": docs[:256],
        "workflow_files": workflows[:128],
        "architecture_surfaces": architecture,
    }

    payload = {
        "protocol": PROTOCOL,
        "status": "OBSERVED",
        "file_count_observed": len(files),
        "scan_truncated": len(files) >= max_files,
        "primary_languages": primary_languages,
        "language_file_counts": {
            key: language_counts[key] for key in sorted(language_counts)
        },
        "dependency_surfaces": dependency_surfaces,
        "capabilities": sorted(capabilities),
        "evidence": evidence,
        "recommended_mode": (
            "SPECIALIZED"
            if primary_languages or manifests or test_files or workflows
            else "GENERIC"
        ),
        "authority_granted": False,
        "scientific_pass": False,
        "execution_verified": False,
    }
    payload["digest"] = _digest(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default=".jarvis/JARVIS_LOCAL_CONTEXT.json")
    parser.add_argument("--max-files", type=int, default=20000)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    receipt = scan_repository(root, max_files=args.max_files)
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
