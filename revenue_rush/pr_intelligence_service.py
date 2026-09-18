from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import time
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse

APP_ID = "omega-pr-intelligence-rush-r1"
STORE_PATH = Path(os.getenv("REPORT_STORE", "/tmp/omega_pr_intelligence_store.json"))
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
GITHUB_API = "https://api.github.com"
PR_URL_RE = re.compile(r"^https://github\.com/([^/]+)/([^/]+)/pull/(\d+)(?:/.*)?$")

app = FastAPI(title="Omega PR Intelligence Rush R1", version="1.0")


def _load_store() -> dict[str, Any]:
    try:
        return json.loads(STORE_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"events": {}, "reports": {}}
    except Exception:
        return {"events": {}, "reports": {}}


def _save_store(store: dict[str, Any]) -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STORE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(store, sort_keys=True), encoding="utf-8")
    tmp.replace(STORE_PATH)


def verify_stripe_signature(payload: bytes, header: str, secret: str, tolerance: int = 300) -> bool:
    if not secret or not header:
        return False
    parts: dict[str, list[str]] = {}
    for item in header.split(","):
        if "=" not in item:
            continue
        k, v = item.split("=", 1)
        parts.setdefault(k.strip(), []).append(v.strip())
    try:
        timestamp = int(parts["t"][0])
    except Exception:
        return False
    if abs(int(time.time()) - timestamp) > tolerance:
        return False
    signed = str(timestamp).encode() + b"." + payload
    expected = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return any(hmac.compare_digest(expected, sig) for sig in parts.get("v1", []))


def _custom_fields(session: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for field in session.get("custom_fields") or []:
        key = field.get("key")
        typ = field.get("type")
        if key and typ and isinstance(field.get(typ), dict):
            value = field[typ].get("value")
            if value is not None:
                out[str(key)] = str(value)
    return out


def _classify_paths(paths: list[str]) -> dict[str, list[str]]:
    groups = {
        "tests": [], "docs": [], "ci": [], "dependencies": [],
        "migrations": [], "auth_security": [], "billing": [], "source": []
    }
    for p in paths:
        q = p.lower()
        if any(x in q for x in ("test", "spec")):
            groups["tests"].append(p)
        if any(x in q for x in ("readme", "docs/", ".md")):
            groups["docs"].append(p)
        if ".github/workflows/" in q or "ci/" in q or "pipeline" in q:
            groups["ci"].append(p)
        if any(x in q for x in ("requirements", "pyproject", "package.json", "package-lock", "pnpm-lock", "yarn.lock", "poetry.lock")):
            groups["dependencies"].append(p)
        if "migration" in q or "/migrations/" in q:
            groups["migrations"].append(p)
        if any(x in q for x in ("auth", "oauth", "permission", "secret", "security", "crypto")):
            groups["auth_security"].append(p)
        if any(x in q for x in ("billing", "stripe", "payment", "invoice", "checkout")):
            groups["billing"].append(p)
        if p not in groups["tests"] and p not in groups["docs"]:
            groups["source"].append(p)
    return groups


def build_report(pr: dict[str, Any], files: list[dict[str, Any]], focus: str = "") -> dict[str, Any]:
    paths = [str(f.get("filename", "")) for f in files if f.get("filename")]
    groups = _classify_paths(paths)
    additions = int(pr.get("additions") or sum(int(f.get("additions") or 0) for f in files))
    deletions = int(pr.get("deletions") or sum(int(f.get("deletions") or 0) for f in files))
    changed = int(pr.get("changed_files") or len(files))
    churn = additions + deletions

    signals: list[dict[str, Any]] = []
    def add(code: str, level: str, evidence: Any) -> None:
        signals.append({"code": code, "attention": level, "evidence": evidence})

    if churn >= 1500 or changed >= 40:
        add("LARGE_CHANGESET", "HIGH", {"churn": churn, "changed_files": changed})
    elif churn >= 500 or changed >= 15:
        add("MEDIUM_CHANGESET", "MEDIUM", {"churn": churn, "changed_files": changed})

    source_changed = len(groups["source"]) > 0
    if source_changed and not groups["tests"]:
        add("SOURCE_WITHOUT_TEST_FILE_CHANGE", "MEDIUM", {"source_files": len(groups["source"])})
    if groups["ci"]:
        add("CI_OR_WORKFLOW_CHANGED", "MEDIUM", groups["ci"][:20])
    if groups["dependencies"]:
        add("DEPENDENCY_SURFACE_CHANGED", "MEDIUM", groups["dependencies"][:20])
    if groups["migrations"]:
        add("MIGRATION_SURFACE_CHANGED", "HIGH", groups["migrations"][:20])
    if groups["auth_security"]:
        add("AUTH_OR_SECURITY_SURFACE_CHANGED", "HIGH", groups["auth_security"][:20])
    if groups["billing"]:
        add("BILLING_OR_PAYMENT_SURFACE_CHANGED", "HIGH", groups["billing"][:20])
    if paths and len(groups["docs"]) == len(paths):
        add("DOCS_ONLY_CHANGE", "LOW", {"files": len(paths)})
    if paths and len(groups["tests"]) == len(paths):
        add("TEST_ONLY_CHANGE", "LOW", {"files": len(paths)})

    rank = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
    max_level = max((rank[s["attention"]] for s in signals), default=1)
    band = {1: "LOW", 2: "MEDIUM", 3: "HIGH"}[max_level]

    return {
        "schema_version": "omega-pr-intelligence-r1",
        "status": "READ_ONLY_ADVISORY_REPORT",
        "pr": {
            "url": pr.get("html_url"),
            "title": pr.get("title"),
            "state": pr.get("state"),
            "draft": bool(pr.get("draft")),
            "base": (pr.get("base") or {}).get("ref"),
            "head": (pr.get("head") or {}).get("ref"),
            "changed_files": changed,
            "additions": additions,
            "deletions": deletions,
            "churn": churn,
        },
        "focus": focus,
        "attention_band": band,
        "signals": signals,
        "path_groups": {k: v[:50] for k, v in groups.items()},
        "limitations": [
            "Read-only deterministic heuristics; not a security audit or guarantee of correctness.",
            "No private-repository access in R1.",
            "No code execution, merge, comment, approval, or repository mutation.",
            "No claim that a flagged surface contains a defect; flags indicate review attention only.",
            "GitHub API data can be incomplete for PRs with more than 100 changed files in this R1."
        ],
        "generated_by": APP_ID,
    }


async def analyze_public_pr(url: str, focus: str = "") -> dict[str, Any]:
    m = PR_URL_RE.match(url.strip())
    if not m:
        raise ValueError("Expected a public GitHub pull request URL")
    owner, repo, number = m.group(1), m.group(2), int(m.group(3))
    headers = {"Accept": "application/vnd.github+json", "User-Agent": APP_ID}
    async with httpx.AsyncClient(timeout=12.0, headers=headers) as client:
        pr_r = await client.get(f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{number}")
        if pr_r.status_code == 404:
            raise ValueError("PR not found or not publicly accessible")
        pr_r.raise_for_status()
        files_r = await client.get(f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{number}/files", params={"per_page": 100})
        files_r.raise_for_status()
    return build_report(pr_r.json(), files_r.json(), focus=focus)


@app.get("/health")
def health() -> dict[str, Any]:
    return {"ok": True, "service": APP_ID, "webhook_configured": bool(WEBHOOK_SECRET)}


@app.post("/stripe/webhook")
async def stripe_webhook(request: Request) -> dict[str, Any]:
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")
    if not verify_stripe_signature(payload, signature, WEBHOOK_SECRET):
        raise HTTPException(status_code=400, detail="invalid signature")
    event = json.loads(payload)
    event_id = str(event.get("id", ""))
    store = _load_store()
    if event_id and event_id in store["events"]:
        return {"ok": True, "duplicate": True}

    if event.get("type") not in {"checkout.session.completed", "checkout.session.async_payment_succeeded"}:
        if event_id:
            store["events"][event_id] = {"ignored": True, "type": event.get("type")}
            _save_store(store)
        return {"ok": True, "ignored": True}

    session = (event.get("data") or {}).get("object") or {}
    metadata = session.get("metadata") or {}
    if metadata.get("product_family") != "omega_pr_intelligence":
        if event_id:
            store["events"][event_id] = {"ignored": True, "reason": "other product"}
            _save_store(store)
        return {"ok": True, "ignored": True}

    if session.get("payment_status") != "paid":
        raise HTTPException(status_code=409, detail="payment not paid")

    fields = _custom_fields(session)
    pr_url = fields.get("github_pr_url", "")
    focus = fields.get("focus", "")
    session_id = str(session.get("id", ""))
    if not session_id or not pr_url:
        raise HTTPException(status_code=422, detail="missing checkout session or PR URL")

    try:
        report = await analyze_public_pr(pr_url, focus)
        report["checkout_session_id"] = session_id
        report["payment_verified"] = True
        report["customer_email_present"] = bool((session.get("customer_details") or {}).get("email"))
        store["reports"][session_id] = report
        if event_id:
            store["events"][event_id] = {"fulfilled": True, "session": session_id}
        _save_store(store)
    except Exception as exc:
        if event_id:
            store["events"][event_id] = {"fulfilled": False, "session": session_id, "error": str(exc)[:300]}
            _save_store(store)
        raise HTTPException(status_code=422, detail="fulfillment failed") from exc

    return {"ok": True, "fulfilled": True, "session_id": session_id}


@app.get("/report/{session_id}", response_class=HTMLResponse)
def report_page(session_id: str) -> str:
    report = _load_store().get("reports", {}).get(session_id)
    if not report:
        return """<html><body><h1>Omega PR Intelligence</h1><p>Report pending or unavailable. Refresh shortly. If it remains unavailable, the submitted PR may not be public or accessible.</p></body></html>"""
    body = json.dumps(report, indent=2, ensure_ascii=False)
    safe = body.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"""<html><body><h1>Omega PR Intelligence</h1><p>Paid read-only advisory report.</p><pre>{safe}</pre></body></html>"""
