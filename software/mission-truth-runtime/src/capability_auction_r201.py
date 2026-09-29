from __future__ import annotations
import itertools,json,hashlib,time
from pathlib import Path
FLEET=Path.home()/".tristan"/"autonomous-maintenance"/"morphogenesis"/"fleet-runtime-capabilities-r195.json"
def v(s):
    out=[]
    cur=""
    for ch in str(s or ""):
        if ch.isdigit() or (ch=="." and cur): cur+=ch
        elif cur: break
    for p in cur.strip(".").split(".") if cur else []:
        try: out.append(int(p))
        except: break
    return tuple(out)
def compatible(task,node):
    r=task.get("requires") or {}
    if r.get("python_min") and v(node.get("python_version"))<v(r["python_min"]): return False
    if r.get("node_min") and v(node.get("node_version"))<v(r["node_min"]): return False
    return True
def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def compile_auction(tasks):
    fleet=json.loads(FLEET.read_text())
    nodes=fleet["nodes"]
    compatible_by_task={t["id"]:[n for n in nodes if compatible(t,n)] for t in tasks}
    impossible=[tid for tid,x in compatible_by_task.items() if not x]
    if impossible:
        return {"schema":"tristan.capability-auction.r201","status":"HOLD_UNCOVERED_REQUIREMENTS","uncovered":impossible,"bids":[]}
    best=None
    for k in range(1,len(nodes)+1):
        for subset in itertools.combinations(nodes,k):
            if all(any(n["node"]==c["node"] for n in subset for c in compatible_by_task[t["id"]]) for t in tasks):
                best=list(subset); break
        if best: break
    bids=[]
    for t in tasks:
        eligible=[n for n in best if any(n["node"]==c["node"] for c in compatible_by_task[t["id"]])]
        eligible.sort(key=lambda n:(v(n.get("python_version")),v(n.get("node_version")),n["node"]),reverse=True)
        winner=eligible[0]
        bids.append({"task_id":t["id"],"winner":{"node":winner["node"],"score":1.0,"why":{"runtime_requirements_satisfied":True,"measured_capability":True}},"alternatives":[{"node":n["node"]} for n in eligible[1:]],"priority":t.get("priority",0)})
    out={"schema":"tristan.capability-auction.r201","status":"PASS","created":time.time(),"coalition_size":len(best),"coalition":[n["node"] for n in best],"bids":bids,"capability_snapshot_sha256":hashlib.sha256(FLEET.read_bytes()).hexdigest(),"authority_granted":False}
    out["digest"]=digest(out)
    return out
if __name__=="__main__":
    tasks=[
      {"id":"py313","requires":{"python_min":"3.13"},"priority":1.0},
      {"id":"py38","requires":{"python_min":"3.8"},"priority":0.9},
      {"id":"node24","requires":{"node_min":"24.0"},"priority":0.8}
    ]
    print(json.dumps(compile_auction(tasks),indent=2))
