from __future__ import annotations

"""Bounded mission-DAG consumer over Jarvis Worker Truth R0.1.

The executor converts an existing mission DAG + auction into truthful local
execution receipts. It never exposes arbitrary shell execution or external
mutation authority. VERIFIED means the registered local handler executed and
its deterministic output was verified; it does not mean the high-level mission
outcome or external-world objective was achieved.
"""

from dataclasses import asdict
from hashlib import sha256
import ctypes
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import time
from typing import Any, Mapping

try:
    from .jarvis_worker_truth_r01 import (
        FINAL_STATES,
        HandlerSpec,
        VerifiedReceiptStore,
        assert_truthful,
        process_job,
    )
except ImportError:  # pragma: no cover - standalone local materialization
    from jarvis_worker_truth_r01 import (
        FINAL_STATES,
        HandlerSpec,
        VerifiedReceiptStore,
        assert_truthful,
        process_job,
    )

PROTOCOL = "OMEGA-JARVIS-MISSION-TRUTH-EXECUTOR-R0.1"
RUNTIME_CAPABILITY_FILE = Path.home() / ".tristan" / "runtime-capability-r195.json"
EFFECT_LEDGER_NAME = "effect-ledger-r200.jsonl"
ALLOWED_ACTIONS = frozenset(
    {
        "benchmark_and_profile",
        "independent_oak_review",
        "design_zero_spend_canary",
        "recompute_tier_thresholds",
        "source_scout",
    }
)
LOCAL_AUTHORITY = frozenset({"local_pure"})


def digest(value: object) -> str:
    return sha256(
        json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
            default=str,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def verify_embedded_digest(value: Mapping[str, object]) -> bool:
    got = str(value.get("digest", ""))
    body = {k: v for k, v in value.items() if k != "digest"}
    return bool(got) and got == digest(body)


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True)
    tmp = path.with_name(path.name + f".{os.getpid()}.{time.time_ns()}.tmp")
    tmp.write_text(payload, encoding="utf-8")
    os.replace(tmp, path)


def runtime_capability_snapshot() -> Mapping[str, object]:
    cap = load_json(RUNTIME_CAPABILITY_FILE, {})
    if not isinstance(cap, Mapping):
        cap = {}
    raw = RUNTIME_CAPABILITY_FILE.read_bytes() if RUNTIME_CAPABILITY_FILE.exists() else b""
    return {
        "path": str(RUNTIME_CAPABILITY_FILE),
        "exists": RUNTIME_CAPABILITY_FILE.exists(),
        "sha256": sha256(raw).hexdigest() if raw else None,
        "status": cap.get("status"),
        "python_invocation": cap.get("python_invocation"),
        "python_version": cap.get("python_version") or cap.get("py3_version"),
        "node_invocation": cap.get("node_invocation"),
        "node_version": cap.get("node_version"),
    }


def append_effect_ledger(state_root: Path, record: Mapping[str, object]) -> str:
    path = state_root / EFFECT_LEDGER_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
    return str(path)


def _free_ram_gb() -> float | None:
    if os.name != "nt":
        return None

    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    state = MemoryStatus()
    state.dwLength = ctypes.sizeof(MemoryStatus)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(state)):
        return None
    return round(state.ullAvailPhys / (1024**3), 3)


def _gpu_snapshot() -> Mapping[str, object]:
    command = [
        "nvidia-smi",
        "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu",
        "--format=csv,noheader,nounits",
    ]
    try:
        cp = subprocess.run(command, capture_output=True, text=True, timeout=5)
        if cp.returncode != 0:
            return {"status": "UNAVAILABLE"}
        rows = []
        for line in cp.stdout.splitlines():
            parts = [x.strip() for x in line.split(",")]
            if len(parts) == 6:
                rows.append(
                    {
                        "name": parts[0],
                        "memory_total_mb": float(parts[1]),
                        "memory_used_mb": float(parts[2]),
                        "memory_free_mb": float(parts[3]),
                        "utilization_pct": float(parts[4]),
                        "temperature_c": float(parts[5]),
                    }
                )
        return {"status": "PASS", "gpus": rows}
    except Exception as exc:
        return {"status": "UNAVAILABLE", "error_type": type(exc).__name__}


def resource_snapshot(state_root: Path | None = None) -> Mapping[str, object]:
    disk_free_gb = None
    disk_total_gb = None
    if state_root is not None:
        try:
            usage = shutil.disk_usage(state_root)
            disk_free_gb = round(usage.free / (1024**3), 3)
            disk_total_gb = round(usage.total / (1024**3), 3)
        except Exception:
            pass
    return {
        "node": platform.node(),
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "free_ram_gb": _free_ram_gb(),
        "state_disk_free_gb": disk_free_gb,
        "state_disk_total_gb": disk_total_gb,
        "gpu": _gpu_snapshot(),
    }


def benchmark_and_profile(payload: Mapping[str, object]) -> Mapping[str, object]:
    task = dict(payload.get("task", {}))
    target = str(task.get("target", ""))
    resource = dict(payload.get("resource", {}))
    if target in {"swarm", "improve", "embed"}:
        intervention = "serialize_heavy_models_and_measure_before_after"
    else:
        intervention = "stream_chunk_and_cap_concurrency_then_measure"
    return {
        "kind": "RESOURCE_PROFILE_PACKET",
        "target": target,
        "resource": resource,
        "proposed_bounded_intervention": intervention,
        "experiment_required": True,
    }


def independent_oak_review(payload: Mapping[str, object]) -> Mapping[str, object]:
    task = dict(payload.get("task", {}))
    gate = str(task.get("gate", ""))
    checks = {
        "oak_declared": "OAK" in gate,
        "rollback_declared": "rollback" in gate,
        "no_spend_declared": "no_spend" in gate,
        "external_authority_granted": False,
    }
    return {
        "kind": "OAK_CONTRACT_REVIEW",
        "target": task.get("target"),
        "checks": checks,
        "decision": "PASS_CONTRACT_ONLY" if all(checks.values()) is False and all(
            checks[k] for k in ("oak_declared", "rollback_declared", "no_spend_declared")
        ) else "HOLD_CONTRACT",
        "scope": "contract_and_local_evidence_only",
    }


def design_zero_spend_canary(payload: Mapping[str, object]) -> Mapping[str, object]:
    task = dict(payload.get("task", {}))
    target = str(task.get("target", ""))
    return {
        "kind": "ZERO_SPEND_CANARY_DESIGN",
        "target": target,
        "constraints": [
            "no_spend",
            "no_account_creation",
            "no_publication",
            "no_credentials",
            "local_or_read_only_first",
        ],
        "steps": [
            "freeze success and falsification criteria",
            "reuse existing adapter or produce local staging artifact only",
            "run deterministic/local canary",
            "verify output independently",
            "promote only after separate authority gate",
        ],
        "outcome_claimed": False,
    }


def recompute_tier_thresholds(payload: Mapping[str, object]) -> Mapping[str, object]:
    signals = dict(payload.get("signals", {}))
    funnel = dict(signals.get("funnel", {}))
    total = max(1, int(funnel.get("total", 0) or 0))
    counts = {
        "T0": int(funnel.get("T0_metadata_only", 0) or 0),
        "T1": int(funnel.get("T1_enrich_embed", 0) or 0),
        "T2": int(funnel.get("T2_scout", 0) or 0),
        "T3": int(funnel.get("T3_full_swarm", 0) or 0),
    }
    shares = {key: round(value / total, 8) for key, value in counts.items()}
    return {
        "kind": "FUNNEL_THRESHOLD_RECOMPUTE",
        "total": total,
        "counts": counts,
        "shares": shares,
        "decision": "KEEP_CURRENT_T3_OR_NARROW" if shares["T3"] <= 0.01 else "NARROW_T3",
        "widen_t3": False,
    }


def source_scout(payload: Mapping[str, object]) -> Mapping[str, object]:
    task = dict(payload.get("task", {}))
    return {
        "kind": "SOURCE_SCOUT_PACKET",
        "target": task.get("target"),
        "requirements": [
            "rights_cleared",
            "metadata_first",
            "jit_full_text_only_if_needed",
            "source_provenance",
            "independent_oak_before_promotion",
        ],
        "network_mutation": False,
        "acquisition_executed": False,
    }


HANDLERS = {
    "benchmark_and_profile": (
        HandlerSpec("MISSION_PROFILE", "1", "local_pure", "PURE"),
        benchmark_and_profile,
    ),
    "independent_oak_review": (
        HandlerSpec("MISSION_OAK_REVIEW", "1", "local_pure", "PURE"),
        independent_oak_review,
    ),
    "design_zero_spend_canary": (
        HandlerSpec("MISSION_CANARY_DESIGN", "1", "local_pure", "PURE"),
        design_zero_spend_canary,
    ),
    "recompute_tier_thresholds": (
        HandlerSpec("MISSION_FUNNEL_RECOMPUTE", "1", "local_pure", "PURE"),
        recompute_tier_thresholds,
    ),
    "source_scout": (
        HandlerSpec("MISSION_SOURCE_SCOUT", "1", "local_pure", "PURE"),
        source_scout,
    ),
}


def verify_handler_output(
    payload: Mapping[str, object], output: Mapping[str, object]
) -> bool:
    action = str(payload.get("action", ""))
    selected = HANDLERS.get(action)
    if selected is None:
        return False
    _, handler = selected
    return dict(output) == dict(handler(payload))


def _version_tuple(value: object) -> tuple[int, ...]:
    text = str(value or "")
    digits = []
    current = ""
    for ch in text:
        if ch.isdigit() or (ch == "." and current):
            current += ch
        elif current:
            break
    for part in current.strip(".").split(".") if current else []:
        try:
            digits.append(int(part))
        except ValueError:
            break
    return tuple(digits)


def runtime_requirements_satisfied(task: Mapping[str, object], cap: Mapping[str, object]) -> bool:
    req = task.get("requires") or {}
    if not isinstance(req, Mapping):
        return True
    py_min = req.get("python_min")
    node_min = req.get("node_min")
    if py_min:
        got = _version_tuple(cap.get("python_version"))
        need = _version_tuple(py_min)
        if not got or got < need:
            return False
    if node_min:
        got = _version_tuple(cap.get("node_version"))
        need = _version_tuple(node_min)
        if not got or got < need:
            return False
    return True


def auction_winners(auction: Mapping[str, object]) -> Mapping[str, str]:
    winners = {}
    for bid in auction.get("bids", []) or []:
        if not isinstance(bid, Mapping):
            continue
        winner = bid.get("winner")
        if isinstance(winner, Mapping) and winner.get("node"):
            winners[str(bid.get("task_id", ""))] = str(winner["node"])
    return winners


def _receipt_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return [p for p in root.rglob("*.json") if p.is_file()]


def semantic_execution_key(
    task: Mapping[str, object],
    dag: Mapping[str, object],
    assigned_node: str,
) -> str:
    """Stable key that reopens work only when mission-relevant evidence changes."""

    action = str(task.get("action", ""))
    signals = dict(dag.get("signals", {}))
    relevant: Mapping[str, object] | object = {}
    if action == "benchmark_and_profile":
        target = str(task.get("target", ""))
        row = next(
            (
                x
                for x in signals.get("big_t", []) or []
                if isinstance(x, Mapping) and str(x.get("stage", "")) == target
            ),
            {},
        )
        relevant = {
            "stage": row.get("stage"),
            "bottleneck": row.get("bottleneck"),
            "confidence": row.get("confidence"),
        }
    elif action == "recompute_tier_thresholds":
        funnel = dict(signals.get("funnel", {}))
        relevant = {
            k: funnel.get(k)
            for k in (
                "total",
                "T0_metadata_only",
                "T1_enrich_embed",
                "T2_scout",
                "T3_full_swarm",
            )
        }
    elif action == "source_scout":
        relevant = {"genome_digest": signals.get("genome_digest")}

    task_semantic = {
        k: task.get(k)
        for k in (
            "id",
            "kind",
            "target",
            "action",
            "gate",
            "depends_on",
            "model",
        )
    }
    return digest(
        {
            "task": task_semantic,
            "assigned_node": assigned_node,
            "relevant_signal": relevant,
        }
    )


def completed_execution_keys(
    local_root: Path,
    shared_root: Path | None,
) -> set[str]:
    roots = [local_root / "receipts"]
    if shared_root is not None:
        roots.append(shared_root)
    done: set[str] = set()
    for root in roots:
        for path in _receipt_files(root):
            rec = load_json(path, {})
            if (
                isinstance(rec, Mapping)
                and rec.get("protocol") == PROTOCOL
                and rec.get("execution_status") == "VERIFIED"
                and rec.get("execution_key")
            ):
                done.add(str(rec["execution_key"]))
    return done


def select_tasks(
    dag: Mapping[str, object],
    auction: Mapping[str, object],
    *,
    node: str,
    completed: set[str],
    max_tasks: int,
    runtime_capability: Mapping[str, object] | None = None,
) -> list[Mapping[str, object]]:
    winners = auction_winners(auction)
    task_index = {
        str(t.get("id", "")): t
        for t in dag.get("tasks", []) or []
        if isinstance(t, Mapping) and t.get("id")
    }
    selected = []
    for task in task_index.values():
        task_id = str(task.get("id", ""))
        assigned = winners.get(task_id, str(task.get("node", "")))
        deps = [str(x) for x in task.get("depends_on", []) or []]
        key = semantic_execution_key(task, dag, assigned)

        dep_keys = []
        deps_known = True
        for dep in deps:
            dep_task = task_index.get(dep)
            if dep_task is None:
                deps_known = False
                break
            dep_assigned = winners.get(dep, str(dep_task.get("node", "")))
            dep_keys.append(semantic_execution_key(dep_task, dag, dep_assigned))

        if (
            task.get("status") == "READY"
            and task_id
            and assigned == node
            and task.get("action") in ALLOWED_ACTIONS
            and runtime_requirements_satisfied(task, runtime_capability or {})
            and key not in completed
            and deps_known
            and all(dep_key in completed for dep_key in dep_keys)
        ):
            row = dict(task)
            row["_execution_key"] = key
            selected.append(row)
    selected.sort(key=lambda row: float(row.get("priority", 0) or 0), reverse=True)
    return selected[: max(0, int(max_tasks))]

def _materialize(
    root: Path,
    mission_id: str,
    execution_key: str,
    output: Mapping[str, object],
) -> tuple[str, str]:
    path = root / "artifacts" / f"{mission_id}_{execution_key[:12]}.json"
    atomic_json(path, output)
    observed = path.read_bytes()
    return str(path), sha256(observed).hexdigest()


def _mirror(path: Path, shared_root: Path | None, node: str, kind: str) -> str | None:
    if shared_root is None:
        return None
    dest = shared_root / node / kind / path.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".tmp")
    shutil.copy2(path, tmp)
    os.replace(tmp, dest)
    return str(dest)


def verify_peer_receipts(shared_root: Path | None, verifier_node: str) -> list[Mapping[str, object]]:
    if shared_root is None or not shared_root.exists():
        return []
    checks = []
    for peer in [p for p in shared_root.iterdir() if p.is_dir() and p.name != verifier_node and p.name != "verification"]:
        for receipt_path in (peer / "receipts").glob("*.json") if (peer / "receipts").exists() else []:
            rec = load_json(receipt_path, {})
            if not isinstance(rec, Mapping) or rec.get("protocol") != PROTOCOL:
                continue
            expected = str(rec.get("receipt_digest", ""))
            body = {k: v for k, v in rec.items() if k != "receipt_digest"}
            receipt_ok = expected == digest(body)
            artifact_file = str(rec.get("artifact_file", ""))
            artifact = peer / "artifacts" / artifact_file if artifact_file else Path()
            artifact_ok = bool(artifact_file) and artifact.exists() and sha256(artifact.read_bytes()).hexdigest() == rec.get("artifact_sha256")
            boundary_ok = rec.get("authority_granted") is False and rec.get("external_side_effects") is False
            status = "INDEPENDENT_INTEGRITY_PASS" if receipt_ok and artifact_ok and boundary_ok else "HOLD_INTEGRITY"
            row = {
                "schema": "jarvis-mission-peer-verification-r0.1",
                "verifier_node": verifier_node,
                "peer_node": peer.name,
                "mission_id": rec.get("mission_id"),
                "execution_key": rec.get("execution_key"),
                "receipt_ok": receipt_ok,
                "artifact_ok": artifact_ok,
                "boundary_ok": boundary_ok,
                "status": status,
                "verified_at": time.time(),
            }
            row["digest"] = digest({k: v for k, v in row.items() if k != "digest"})
            key_short = str(rec.get("execution_key", ""))[:12]
            out = shared_root / "verification" / verifier_node / f"{peer.name}_{rec.get('mission_id')}_{key_short}.json"
            atomic_json(out, row)
            checks.append(row)
    return checks


def run_cycle(
    *,
    dag_path: Path,
    auction_path: Path,
    node: str,
    state_root: Path,
    shared_root: Path | None = None,
    max_tasks: int = 1,
    min_free_disk_gb: float = 2.0,
) -> Mapping[str, object]:
    state_root.mkdir(parents=True, exist_ok=True)
    if (state_root / "stop.request").exists():
        return {"protocol": PROTOCOL, "status": "NO_ACTION_STOP_REQUEST", "node": node}

    if not dag_path.exists():
        return {"protocol": PROTOCOL, "status": "NO_ACTION_DAG_SOURCE_UNAVAILABLE", "node": node,
                "dag_path": str(dag_path), "authority_granted": False}
    if not auction_path.exists():
        return {"protocol": PROTOCOL, "status": "NO_ACTION_AUCTION_SOURCE_UNAVAILABLE", "node": node,
                "auction_path": str(auction_path), "authority_granted": False}

    dag = load_json(dag_path, {})
    auction = load_json(auction_path, {})
    if not isinstance(dag, Mapping) or not verify_embedded_digest(dag):
        return {"protocol": PROTOCOL, "status": "HOLD_BAD_DAG_DIGEST", "node": node,
                "dag_path": str(dag_path), "authority_granted": False}
    if not isinstance(auction, Mapping) or not verify_embedded_digest(auction):
        return {"protocol": PROTOCOL, "status": "HOLD_BAD_AUCTION_DIGEST", "node": node,
                "auction_path": str(auction_path), "authority_granted": False}

    dag_digest = str(dag["digest"])
    auction_digest = str(auction["digest"])
    runtime_capability = runtime_capability_snapshot()
    if not runtime_capability.get("exists") or runtime_capability.get("status") != "MEASURED":
        return {
            "protocol": PROTOCOL,
            "status": "HOLD_RUNTIME_CAPABILITY_UNVERIFIED",
            "node": node,
            "runtime_capability": runtime_capability,
            "authority_granted": False,
            "external_side_effects": False,
        }
    resource = resource_snapshot(state_root)
    disk_free = resource.get("state_disk_free_gb")
    if disk_free is not None and float(disk_free) < float(min_free_disk_gb):
        return {
            "protocol": PROTOCOL,
            "status": "NO_ACTION_RESOURCE_GUARD",
            "node": node,
            "resource": resource,
            "min_free_disk_gb": float(min_free_disk_gb),
            "authority_granted": False,
            "external_side_effects": False,
        }

    completed = completed_execution_keys(state_root, shared_root)
    tasks = select_tasks(
        dag,
        auction,
        node=node,
        completed=completed,
        max_tasks=max_tasks,
        runtime_capability=runtime_capability,
    )
    results = []

    for task in tasks:
        action = str(task.get("action", ""))
        execution_key = str(task["_execution_key"])
        clean_task = {k: v for k, v in task.items() if not str(k).startswith("_")}
        payload = {
            "action": action,
            "task": clean_task,
            "signals": dict(dag.get("signals", {})),
            "resource": resource,
            "source_dag_digest": dag_digest,
            "source_auction_digest": auction_digest,
        }
        job = {"id": task["id"], "type": action, "payload": payload}
        store = VerifiedReceiptStore({})
        worker = process_job(
            job,
            handlers=HANDLERS,
            authority_scopes=LOCAL_AUTHORITY,
            verifier=verify_handler_output,
            store=store,
        )
        assert_truthful(worker)
        selected = HANDLERS.get(action)
        output = dict(selected[1](payload)) if selected is not None and worker.status == "VERIFIED" else {}
        artifact_path = None
        artifact_sha = None
        if worker.status == "VERIFIED":
            artifact_path, artifact_sha = _materialize(
                state_root,
                str(task["id"]),
                execution_key,
                output,
            )

        invocation_id = digest({"execution_key": execution_key, "node": node, "created_ns": time.time_ns()})
        transport_idempotency_key = digest({"mission_id": task["id"], "execution_key": execution_key, "auction": auction_digest})
        receipt = {
            "protocol": PROTOCOL,
            "mission_id": task["id"],
            "kind": task.get("kind"),
            "action": action,
            "target": task.get("target"),
            "priority": task.get("priority"),
            "selected_node": node,
            "execution_key": execution_key,
            "invocation_id": invocation_id,
            "transport_idempotency_key": transport_idempotency_key,
            "runtime_capability": runtime_capability,
            "source_dag_digest": dag_digest,
            "source_auction_digest": auction_digest,
            "execution_status": worker.status,
            "execution_truth": asdict(worker),
            "outcome_status": "CANDIDATE_OR_MEASUREMENT_ONLY",
            "artifact_path": artifact_path,
            "artifact_file": Path(artifact_path).name if artifact_path else None,
            "artifact_sha256": artifact_sha,
            "authority_granted": False,
            "external_side_effects": False,
            "money_spent": 0,
            "human_contact": False,
            "public_publish": False,
            "main_merge": False,
            "created_at": time.time(),
            "invariants": [
                "ExecutionVerified!=MissionOutcomeVerified",
                "Capability!=Authority",
                "Generated!=Verified",
                "NO_ACTION admissible",
                "RightToLose",
            ],
        }
        receipt["receipt_digest"] = digest(receipt)
        receipt_path = state_root / "receipts" / f"{task['id']}_{execution_key[:12]}.json"
        atomic_json(receipt_path, receipt)
        ledger_record = {
            "schema": "tristan.effect-ledger.r200",
            "mission_id": task["id"],
            "execution_key": execution_key,
            "invocation_id": invocation_id,
            "transport_idempotency_key": transport_idempotency_key,
            "node": node,
            "execution_status": worker.status,
            "external_side_effects": False,
            "artifact_sha256": artifact_sha,
            "receipt_digest": receipt["receipt_digest"],
            "runtime_capability_sha256": runtime_capability.get("sha256"),
            "created_at": receipt["created_at"],
        }
        ledger_record["digest"] = digest(ledger_record)
        append_effect_ledger(state_root, ledger_record)
        _mirror(receipt_path, shared_root, node, "receipts")
        if artifact_path:
            _mirror(Path(artifact_path), shared_root, node, "artifacts")
        results.append(receipt)
        if worker.status == "VERIFIED":
            completed.add(execution_key)

    peer = verify_peer_receipts(shared_root, node)
    status = "PASS" if all(r["execution_status"] in FINAL_STATES for r in results) else "HOLD_EXECUTION"
    out = {
        "protocol": PROTOCOL,
        "status": status,
        "node": node,
        "source_dag_digest": dag_digest,
        "source_auction_digest": auction_digest,
        "selected": len(tasks),
        "verified": sum(1 for r in results if r["execution_status"] == "VERIFIED"),
        "peer_checks": len(peer),
        "peer_integrity_pass": sum(1 for x in peer if x["status"] == "INDEPENDENT_INTEGRITY_PASS"),
        "resource": resource,
        "results": [
            {
                "mission_id": r["mission_id"],
                "action": r["action"],
                "execution_status": r["execution_status"],
                "artifact_sha256": r["artifact_sha256"],
            }
            for r in results
        ],
        "authority_granted": False,
        "external_side_effects": False,
    }
    out["digest"] = digest(out)
    atomic_json(state_root / "latest.json", out)
    return out
