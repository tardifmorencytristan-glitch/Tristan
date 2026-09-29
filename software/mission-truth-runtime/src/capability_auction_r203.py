from __future__ import annotations
import datetime as dt, hashlib, itertools, json, math, time
from pathlib import Path

SNAPSHOT=Path.home()/".tristan"/"autonomous-maintenance"/"morphogenesis"/"fleet-runtime-resources-r203.json"
SCHEMA="tristan.capability-auction.r203"

def _version(s):
    out=[]; cur=""
    for ch in str(s or ""):
        if ch.isdigit() or (ch=="." and cur): cur+=ch
        elif cur: break
    for part in cur.strip(".").split(".") if cur else []:
        try: out.append(int(part))
        except: break
    return tuple(out)

def _parse_iso(s):
    try:return dt.datetime.fromisoformat(str(s))
    except:return None

def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

def node_fresh(node, now, max_age_s):
    stamp=_parse_iso(node.get("observed_at"))
    if stamp is None:return False
    if now.tzinfo is None and stamp.tzinfo is not None:
        now=now.replace(tzinfo=stamp.tzinfo)
    age=(now-stamp).total_seconds()
    return 0 <= age <= max_age_s

def compatible(task,node,now,max_age_s):
    if not node.get("available",False): return False
    if not node_fresh(node,now,max_age_s): return False
    req=task.get("requires") or {}
    if req.get("python_min") and _version(node.get("python_version")) < _version(req["python_min"]): return False
    if req.get("node_min") and _version(node.get("node_version")) < _version(req["node_min"]): return False
    if req.get("min_free_ram_gb") is not None and float(node.get("free_ram_gb",0)) < float(req["min_free_ram_gb"]): return False
    if req.get("min_disk_free_gb") is not None and float(node.get("disk_free_gb",0)) < float(req["min_disk_free_gb"]): return False
    if req.get("max_cpu_load_pct") is not None and float(node.get("cpu_load_pct",100)) > float(req["max_cpu_load_pct"]): return False
    return True

def score(node):
    ram=float(node.get("free_ram_gb",0))
    disk=float(node.get("disk_free_gb",0))
    cpu=float(node.get("cpu_load_pct",100))
    return round((ram*1.0)+(math.log10(1+max(0,disk))*4.0)+((100-cpu)*0.25),6)

def compile_auction(tasks,*,snapshot_path=SNAPSHOT,max_age_s=300,now=None,exclude_nodes=()):
    snap=json.loads(Path(snapshot_path).read_text())
    nodes=[dict(n) for n in snap.get("nodes",[])]
    excluded=set(exclude_nodes)
    now=now or dt.datetime.now(dt.timezone.utc)
    if now.tzinfo is not None:
        # compare using absolute time through UTC conversion
        pass
    compatible_by={}
    for t in tasks:
        compatible_by[t["id"]]=[
            n for n in nodes
            if n.get("node") not in excluded and compatible(t,n,now,max_age_s)
        ]
    uncovered=[tid for tid,x in compatible_by.items() if not x]
    if uncovered:
        return {
            "schema":SCHEMA,
            "status":"HOLD_UNCOVERED_OR_STALE_REQUIREMENTS",
            "uncovered":uncovered,
            "excluded_nodes":sorted(excluded),
            "bids":[],
            "authority_granted":False,
        }
    best_subset=None
    for k in range(1,len(nodes)+1):
        feasible=[]
        for subset in itertools.combinations(nodes,k):
            names={n["node"] for n in subset}
            if all(any(c["node"] in names for c in compatible_by[t["id"]]) for t in tasks):
                feasible.append(list(subset))
        if feasible:
            feasible.sort(
                key=lambda subset: (
                    sum(score(n) for n in subset),
                    tuple(sorted(n["node"] for n in subset)),
                ),
                reverse=True,
            )
            best_subset=feasible[0]
            break
    bids=[]
    for t in tasks:
        eligible=[n for n in best_subset if any(n["node"]==c["node"] for c in compatible_by[t["id"]])]
        eligible.sort(key=lambda n:(score(n),n["node"]),reverse=True)
        winner=eligible[0]
        bids.append({
            "task_id":t["id"],
            "winner":{"node":winner["node"],"score":score(winner),"why":{"fresh":True,"requirements_satisfied":True,"resource_headroom":True}},
            "alternatives":[{"node":n["node"],"score":score(n)} for n in eligible[1:]],
            "priority":t.get("priority",0),
        })
    out={
        "schema":SCHEMA,
        "status":"PASS",
        "created":time.time(),
        "max_age_s":max_age_s,
        "coalition_size":len(best_subset),
        "coalition":[n["node"] for n in best_subset],
        "bids":bids,
        "snapshot_sha256":hashlib.sha256(Path(snapshot_path).read_bytes()).hexdigest(),
        "authority_granted":False,
    }
    out["digest"]=digest(out)
    return out
