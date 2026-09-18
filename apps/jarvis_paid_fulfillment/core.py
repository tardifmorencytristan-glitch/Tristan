"""Public, secret-free core for Jarvis paid fulfillment R1."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import hmac
import html
import json
import re
import time
from typing import Mapping, Sequence
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

AUDIT_PAYMENT_LINK_ID = "plink_1U8GS0EBGsbM207Ty2xac9pI"
MAX_FILES = 40
MAX_FILE_BYTES = 200_000
MAX_TOTAL_BYTES = 1_500_000
ALLOWED_SUFFIXES = (
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".rb", ".php",
    ".java", ".c", ".cc", ".cpp", ".h", ".hpp", ".toml", ".yaml", ".yml",
    ".json", ".md", ".txt", ".ini", ".cfg", ".sh", ".ps1",
)
ROOT_HIGH_SIGNAL = {
    "README.md", "LICENSE", "LICENSE.md", "pyproject.toml", "requirements.txt",
    "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
    "Pipfile.lock", "poetry.lock", "uv.lock", "Dockerfile", "docker-compose.yml",
}
SECRET_PATTERNS = {
    "OPENAI_KEY_LIKE": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{16,}\b"),
    "GITHUB_TOKEN_LIKE": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "AWS_ACCESS_KEY_LIKE": re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
    "PRIVATE_KEY_BLOCK": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}
RISK_PATTERNS = {
    "SHELL_TRUE": re.compile(r"\bshell\s*=\s*True\b"),
    "OS_SYSTEM": re.compile(r"\bos\.system\s*\("),
    "EVAL_CALL": re.compile(r"(?<![\w.])eval\s*\("),
    "EXEC_CALL": re.compile(r"(?<![\w.])exec\s*\("),
    "TLS_VERIFY_FALSE": re.compile(r"\bverify\s*=\s*False\b"),
    "CURL_PIPE_SHELL": re.compile(r"\bcurl\b[^\n|]{0,300}\|\s*(?:sh|bash)\b"),
    "WORKFLOW_WRITE_ALL": re.compile(r"permissions\s*:\s*write-all", re.I),
    "PULL_REQUEST_TARGET": re.compile(r"\bpull_request_target\s*:"),
}

def _digest(obj: object) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return sha256(raw.encode("utf-8")).hexdigest()

def verify_stripe_signature(payload: bytes, signature_header: str, secret: str, *, tolerance_seconds: int = 300, now: int | None = None) -> bool:
    if not payload or not signature_header or not secret:
        return False
    parts: dict[str, list[str]] = {}
    for item in signature_header.split(","):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        parts.setdefault(key.strip(), []).append(value.strip())
    try:
        timestamp = int(parts.get("t", [""])[0])
    except ValueError:
        return False
    current = int(time.time()) if now is None else int(now)
    if abs(current - timestamp) > tolerance_seconds:
        return False
    signed = str(timestamp).encode("ascii") + b"." + payload
    expected = hmac.new(secret.encode("utf-8"), signed, "sha256").hexdigest()
    return any(hmac.compare_digest(expected, value) for value in parts.get("v1", []))

def extract_custom_fields(session: Mapping[str, object]) -> dict[str, str]:
    out: dict[str, str] = {}
    rows = session.get("custom_fields", ())
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)):
        return out
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        key = str(row.get("key", "")).strip()
        if not key:
            continue
        value = ""
        for kind in ("text", "numeric", "dropdown"):
            node = row.get(kind)
            if isinstance(node, Mapping) and node.get("value") is not None:
                value = str(node.get("value")).strip()
                break
        out[key] = value
    return out

@dataclass(frozen=True)
class PaidAuditIntake:
    session_id: str
    project: str
    problem: str
    scope: str
    customer_email: str
    payment_link: str
    offer: str
    digest: str = ""

    def with_digest(self) -> "PaidAuditIntake":
        payload = asdict(self)
        payload.pop("digest", None)
        return PaidAuditIntake(**payload, digest=_digest(payload))

def intake_from_checkout_session(session: Mapping[str, object]) -> PaidAuditIntake:
    payment_status = str(session.get("payment_status", "")).strip().lower()
    payment_link = str(session.get("payment_link", "")).strip()
    metadata = session.get("metadata", {})
    metadata = metadata if isinstance(metadata, Mapping) else {}
    offer = str(metadata.get("offer", "")).strip()
    fulfillment = str(metadata.get("fulfillment", "")).strip()
    if payment_status != "paid":
        raise ValueError("checkout session is not paid")
    if payment_link != AUDIT_PAYMENT_LINK_ID and not (offer == "audit_express_99" and fulfillment == "auto_oak_audit_v1"):
        raise ValueError("checkout session is not the bounded audit offer")
    fields = extract_custom_fields(session)
    project = fields.get("project", "").strip()
    problem = fields.get("problem", "").strip()
    scope = fields.get("scope", "").strip()
    if not project or len(problem) < 5 or len(scope) < 10:
        raise ValueError("required audit intake fields are missing")
    details = session.get("customer_details", {})
    details = details if isinstance(details, Mapping) else {}
    return PaidAuditIntake(
        session_id=str(session.get("id", "")).strip(),
        project=project,
        problem=problem,
        scope=scope,
        customer_email=str(details.get("email", "")).strip(),
        payment_link=payment_link,
        offer=offer or "audit_express_99",
    ).with_digest()

def parse_public_github_repo(project: str) -> tuple[str, str]:
    raw = project.strip()
    if "://" not in raw and raw.count("/") == 1:
        raw = "https://github.com/" + raw
    parsed = urlparse(raw)
    if parsed.scheme != "https" or (parsed.hostname or "").lower() != "github.com":
        raise ValueError("R1 supports public github.com repositories only")
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        raise ValueError("GitHub repository URL requires owner/repo")
    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    valid = re.compile(r"^[A-Za-z0-9_.-]+$")
    if not valid.fullmatch(owner) or not valid.fullmatch(repo):
        raise ValueError("invalid GitHub owner/repository")
    return owner, repo

def _get_json(url: str, timeout: float = 15.0) -> Mapping[str, object]:
    req = Request(url, headers={"User-Agent": "Jarvis-Tristan-Paid-Fulfillment-R1", "Accept": "application/vnd.github+json"})
    with urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))

def _get_text(url: str, timeout: float = 15.0, max_bytes: int = MAX_FILE_BYTES) -> str:
    req = Request(url, headers={"User-Agent": "Jarvis-Tristan-Paid-Fulfillment-R1"})
    with urlopen(req, timeout=timeout) as response:
        data = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError("file exceeds bounded read limit")
    return data.decode("utf-8", errors="replace")

def _path_priority(path: str) -> tuple[int, int, str]:
    base = path.rsplit("/", 1)[-1]
    if path in ROOT_HIGH_SIGNAL or base in ROOT_HIGH_SIGNAL:
        return (0, len(path), path)
    if path.startswith(".github/workflows/"):
        return (1, len(path), path)
    if "/test" in path.lower() or path.lower().startswith("test"):
        return (2, len(path), path)
    if path.lower().startswith(("src/", "app/", "lib/")):
        return (3, len(path), path)
    return (4, len(path), path)

def select_tree_files(tree_entries: Sequence[Mapping[str, object]]) -> tuple[str, ...]:
    candidates: list[str] = []
    for row in tree_entries:
        if str(row.get("type", "")) != "blob":
            continue
        path = str(row.get("path", ""))
        size = int(row.get("size") or 0)
        if not path or size > MAX_FILE_BYTES:
            continue
        if path in ROOT_HIGH_SIGNAL or path.rsplit("/", 1)[-1] in ROOT_HIGH_SIGNAL or path.lower().endswith(ALLOWED_SUFFIXES):
            candidates.append(path)
    return tuple(sorted(set(candidates), key=_path_priority)[:MAX_FILES])

def fetch_public_repo_snapshot(owner: str, repo: str) -> tuple[Mapping[str, object], tuple[Mapping[str, object], ...], dict[str, str]]:
    meta = _get_json(f"https://api.github.com/repos/{quote(owner)}/{quote(repo)}")
    if bool(meta.get("private", False)):
        raise ValueError("private repositories are outside R1 public scope")
    branch = str(meta.get("default_branch", "main"))
    tree = _get_json(f"https://api.github.com/repos/{quote(owner)}/{quote(repo)}/git/trees/{quote(branch)}?recursive=1")
    rows = tree.get("tree", ())
    if not isinstance(rows, Sequence):
        raise ValueError("GitHub tree payload malformed")
    entries = tuple(row for row in rows if isinstance(row, Mapping))
    selected = select_tree_files(entries)
    files: dict[str, str] = {}
    budget = 0
    for path in selected:
        size = next((int(row.get("size") or 0) for row in entries if row.get("path") == path), 0)
        if budget + size > MAX_TOTAL_BYTES:
            continue
        raw = f"https://raw.githubusercontent.com/{quote(owner)}/{quote(repo)}/{quote(branch)}/{quote(path, safe='/')}"
        try:
            files[path] = _get_text(raw)
            budget += len(files[path].encode("utf-8"))
        except Exception:
            continue
    return meta, entries, files

def _finding(code: str, severity: str, path: str, rationale: str) -> dict[str, str]:
    return {"code": code, "severity": severity, "path": path, "rationale": rationale}

def audit_repo_snapshot(repo_meta: Mapping[str, object], tree_entries: Sequence[Mapping[str, object]], files: Mapping[str, str], *, problem: str, scope: str) -> dict[str, object]:
    paths = {str(row.get("path", "")) for row in tree_entries if str(row.get("path", ""))}
    has_ci = any(path.startswith(".github/workflows/") for path in paths)
    has_tests = any("/test" in path.lower() or path.lower().startswith(("test", "tests/")) for path in paths)
    has_license = any(path.lower().rsplit("/", 1)[-1].startswith("license") for path in paths)
    manifests = {path for path in paths if path.rsplit("/", 1)[-1] in {"requirements.txt", "pyproject.toml", "package.json", "Pipfile"}}
    locks = {path for path in paths if path.rsplit("/", 1)[-1] in {"poetry.lock", "uv.lock", "Pipfile.lock", "package-lock.json", "pnpm-lock.yaml", "yarn.lock"}}
    findings: list[dict[str, str]] = []
    if not has_ci:
        findings.append(_finding("CI_MISSING", "medium", "repository", "No .github/workflows CI workflow was observed in the bounded tree."))
    if not has_tests:
        findings.append(_finding("TESTS_MISSING", "high", "repository", "No conventional test path was observed in the bounded tree."))
    if not has_license:
        findings.append(_finding("LICENSE_MISSING", "low", "repository", "No conventional LICENSE file was observed."))
    if manifests and not locks:
        findings.append(_finding("LOCKFILE_MISSING", "medium", "repository", "Dependency manifest observed without a conventional lockfile."))
    for path, content in files.items():
        for code, pattern in SECRET_PATTERNS.items():
            if pattern.search(content):
                findings.append(_finding(code, "critical", path, "Secret-like material pattern observed; value intentionally redacted."))
        for code, pattern in RISK_PATTERNS.items():
            if pattern.search(content):
                severity = "high" if code in {"TLS_VERIFY_FALSE", "CURL_PIPE_SHELL", "WORKFLOW_WRITE_ALL"} else "medium"
                findings.append(_finding(code, severity, path, "Static risk pattern observed; requires human/context review before remediation."))
        if path.endswith("requirements.txt"):
            lines = [line.strip() for line in content.splitlines() if line.strip() and not line.lstrip().startswith("#")]
            unpinned = [line for line in lines if not re.search(r"(==|~=|===|@\s*https?://)", line)]
            if unpinned:
                findings.append(_finding("UNPINNED_REQUIREMENTS", "medium", path, f"{len(unpinned)} requirement line(s) are not exact/direct pins."))
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings = sorted(findings, key=lambda row: (order.get(row["severity"], 9), row["code"], row["path"]))
    counts = {severity: sum(1 for row in findings if row["severity"] == severity) for severity in ("critical", "high", "medium", "low")}
    status = "ACTION_REQUIRED" if counts["critical"] or counts["high"] else ("REVIEW" if findings else "NO_FLAG_IN_BOUNDED_SCAN")
    report = {
        "schema": "jarvis-paid-audit-report-r1",
        "status": status,
        "repository": {
            "full_name": str(repo_meta.get("full_name", "")),
            "default_branch": str(repo_meta.get("default_branch", "")),
            "archived": bool(repo_meta.get("archived", False)),
            "fork": bool(repo_meta.get("fork", False)),
        },
        "intake": {"problem": problem[:200], "scope": scope[:200]},
        "coverage": {
            "tree_entries": len(tree_entries),
            "files_selected": len(select_tree_files(tree_entries)),
            "files_scanned": len(files),
            "bounded_max_files": MAX_FILES,
            "bounded_max_total_bytes": MAX_TOTAL_BYTES,
        },
        "signals": {
            "ci_observed": has_ci,
            "tests_observed": has_tests,
            "license_observed": has_license,
            "lockfile_observed": bool(locks),
        },
        "finding_counts": counts,
        "findings": findings,
        "boundaries": [
            "Audit != Certification",
            "StaticPattern != Exploitability",
            "NoFlag != Safe",
            "PublicRead != MutationAuthority",
            "GeneratedReport != IndependentPenetrationTest",
        ],
        "authority_granted": False,
    }
    report["digest"] = _digest(report)
    return report

def run_public_github_audit(project: str, problem: str, scope: str) -> dict[str, object]:
    owner, repo = parse_public_github_repo(project)
    meta, tree, files = fetch_public_repo_snapshot(owner, repo)
    return audit_repo_snapshot(meta, tree, files, problem=problem, scope=scope)

def render_report_html(report: Mapping[str, object]) -> str:
    esc = html.escape
    repo = report.get("repository", {})
    repo = repo if isinstance(repo, Mapping) else {}
    findings = report.get("findings", ())
    rows: list[str] = []
    if isinstance(findings, Sequence):
        for finding in findings:
            if isinstance(finding, Mapping):
                rows.append(
                    "<tr><td>" + esc(str(finding.get("severity", ""))) + "</td><td>" +
                    esc(str(finding.get("code", ""))) + "</td><td>" + esc(str(finding.get("path", ""))) +
                    "</td><td>" + esc(str(finding.get("rationale", ""))) + "</td></tr>"
                )
    if not rows:
        rows = ["<tr><td colspan='4'>No flagged pattern in the bounded scan.</td></tr>"]
    return (
        "<!doctype html><html><head><meta charset='utf-8'><title>Jarvis Audit Receipt</title>"
        "<style>body{font-family:system-ui;max-width:1100px;margin:40px auto;padding:0 18px;color:#111}"
        "table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:8px;text-align:left}"
        "code{word-break:break-all}.muted{color:#555}</style></head><body>"
        "<h1>Jarvis bounded technical audit</h1><p><b>Status:</b> " + esc(str(report.get("status", ""))) +
        "</p><p><b>Repository:</b> " + esc(str(repo.get("full_name", ""))) +
        "</p><p><b>Receipt digest:</b> <code>" + esc(str(report.get("digest", ""))) + "</code></p>"
        "<table><thead><tr><th>Severity</th><th>Code</th><th>Path</th><th>Rationale</th></tr></thead><tbody>" +
        "".join(rows) + "</tbody></table><h2>Boundaries</h2><ul>" +
        "".join("<li>" + esc(str(item)) + "</li>" for item in report.get("boundaries", ())) +
        "</ul><p class='muted'>Generated report is advisory and bounded to public read-only evidence.</p></body></html>"
    )
