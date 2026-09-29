from __future__ import annotations
import argparse, ctypes, json, os, pathlib, secrets, socket, subprocess, sys, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
HOME=pathlib.Path.home()
ROOT=pathlib.Path(__file__).resolve().parent
STATIC=ROOT/"static"; RECEIPTS=ROOT/"receipts"; RECEIPTS.mkdir(parents=True,exist_ok=True)
TOKEN_FILE=ROOT/".session-token"
if not TOKEN_FILE.exists(): TOKEN_FILE.write_text(secrets.token_urlsafe(32),encoding="utf-8")
TOKEN=TOKEN_FILE.read_text(encoding="utf-8").strip()
def loadj(p):
    try:return json.loads(pathlib.Path(p).read_text(encoding="utf-8-sig"))
    except:return {}
def tail_jsonl(p,n=12):
    try:
        lines=pathlib.Path(p).read_text(encoding="utf-8-sig").splitlines()[-n:]
        return [json.loads(x) for x in lines if x.strip()]
    except:return []
def mem():
    class M(ctypes.Structure):
        _fields_=[("dwLength",ctypes.c_ulong),("dwMemoryLoad",ctypes.c_ulong),
        ("ullTotalPhys",ctypes.c_ulonglong),("ullAvailPhys",ctypes.c_ulonglong),
        ("ullTotalPageFile",ctypes.c_ulonglong),("ullAvailPageFile",ctypes.c_ulonglong),
        ("ullTotalVirtual",ctypes.c_ulonglong),("ullAvailVirtual",ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual",ctypes.c_ulonglong)]
    m=M();m.dwLength=ctypes.sizeof(M);ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return {"load_pct":int(m.dwMemoryLoad),"total_gb":round(m.ullTotalPhys/2**30,1),"avail_gb":round(m.ullAvailPhys/2**30,1)}
def gpu():
    try:
        cp=subprocess.run(["nvidia-smi","--query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total",
          "--format=csv,noheader,nounits"],capture_output=True,text=True,timeout=3)
        if cp.returncode:return None
        a=[x.strip() for x in cp.stdout.splitlines()[0].split(",")]
        return {"name":a[0],"temp_c":int(float(a[1])),"util_pct":int(float(a[2])),
                "mem_used_mb":int(float(a[3])),"mem_total_mb":int(float(a[4]))}
    except:return None
def latest_feed(role):
    day=time.strftime("%Y-%m-%d")
    p=HOME/"TristanRepos"/"Tristan"/"reports"/"append-only"/role/f"{day}.jsonl"
    return tail_jsonl(p,16)
def report_meta():
    root=HOME/"TristanRepos"/"Tristan"/"reports"/"mutable"
    out={}
    for name in ("NOW.md","OPERATING_STATE.md","GRAND_STATE.md"):
        f=root/name
        if f.exists():
            st=f.stat(); out[name]={"bytes":st.st_size,"mtime":st.st_mtime}
    return out

def fleet_projection(fleet):
    roles={"DESKTOP-SHA9IHL":"FORGE","DESKTOP-2G1SSMT":"OAK","LAPTOP-AIU36QN6":"HERITAGE"}
    rows=[]
    for x in fleet.get("nodes") or []:
        rows.append({"node":x.get("nodeID"),"role":roles.get(x.get("nodeID"),"NODE"),
                     "input":(x.get("inputHash") or "")[:12],"result":(x.get("resultHash") or "")[:12]})
    return rows

def acceleration_score(hyper,git,weak):
    gs=git.get("summary") or {}
    current=sum(int(v) for k,v in gs.items() if k in ("CURRENT","CLONED","UPDATED"))
    holds=sum(int(v) for k,v in gs.items() if str(k).startswith("HOLD"))
    pressure=float((weak[0].get("priority",0) if weak else 0) or 0)
    boost=1.0 if hyper.get("status")=="ACTIVE" else 0.0
    raw=boost*35 + min(35,current) + min(20,pressure*10) - min(20,holds)
    return max(0,min(100,round(raw,1)))

def operator_learning_state():
    root=HOME/".tristan"/"residual-operator-map"
    state=loadj(root/"state.json")
    mp=loadj(root/"map.json")
    rows=[]
    for key,val in mp.items():
        rec=(val or {}).get("recommendation") or {}
        if rec:
            rows.append({"signature":key,"path":rec.get("path"),
                         "evidence_score":rec.get("evidence_score"),
                         "attempts":rec.get("attempts"),
                         "residual_gain":rec.get("residual_gain"),
                         "eligible":bool(rec.get("eligible_to_influence"))})
    rows=sorted(rows,key=lambda x:((x.get("eligible") is True),x.get("evidence_score") or -999,x.get("attempts") or 0),reverse=True)
    return {"state":state,"recommendations":rows[:12]}

def go_sigma_state():
    repo=HOME/"TristanRepos"/"Tristan"
    contract=loadj(repo/"schemas"/"go_sigma_execution_contract_r1.json")
    mission=loadj(repo/"data"/"GO_SIGMA_CONTINUOUS_MISSION_R1.json")
    return {"contract_schema":contract.get("schema"),"mission_schema":mission.get("schema"),
            "mission_id":mission.get("mission_id"),"modes":mission.get("mode") or [],
            "invariants":contract.get("invariants") or [],"stop_rule":contract.get("stop_rule")}

def collect():
    host=socket.gethostname()
    role="FORGE" if "SHA9IHL" in host else "OAK" if "2G1SSMT" in host else "HERITAGE"
    hyper=loadj(HOME/".tristan"/"hyperloop"/"boost-state.json") or loadj(HOME/".tristan"/"hyperloop"/"state.json")
    git=loadj(HOME/".tristan"/"git-autosync"/"state-latest.json")
    old=loadj(HOME/"JarvisTristan"/"cockpit_runtime"/"state.json")
    morph=loadj(HOME/".tristan"/"autonomous-maintenance"/"morphogenesis"/"state-latest.json")
    worker=loadj(HOME/".tristan"/"autonomous-maintenance"/"morphogenesis"/"worker-truth-latest.json")
    event=loadj(HOME/".tristan"/"event-morphogenesis"/"state.json")
    fleet=loadj(HOME/".tristan"/"autonomous-maintenance"/"morphogenesis"/"fleet-worker-truth-wave-a.json")
    weak=morph.get("weakness_atlas") or []
    return {"schema":"tristan.cockpit.next.state.r5","ts":time.time(),"node":host,"role":role,
      "system":{"memory":mem(),"gpu":gpu()},"hyperloop":hyper,"git":git,"legacy_cockpit":old,
      "morphogenesis":morph,"worker_truth":worker,"fleet_truth":fleet,
      "capabilities":morph.get("capability_graph") or {},"weaknesses":weak,
      "feed":latest_feed(role),"reports":report_meta(),"fleet_projection":fleet_projection(fleet),
      "acceleration_score":acceleration_score(hyper,git,weak),"event_engine":event,"go_sigma":go_sigma_state(),"operator_learning":operator_learning_state()}
def launch(action):
    py=HOME/"AppData"/"Local"/"Programs"/"Python"/"Python313"/"python.exe"
    if action=="git_sync":
        p=HOME/".tristan"/"git-autosync"/"git_autosync.pyw";args=[str(py),str(p),"--once","--max-new","45"]
    elif action=="morph_refresh":
        p=HOME/".tristan"/"autonomous-maintenance"/"morphogenesis"/"compile_state.py";args=[str(py),str(p)]
    elif action=="workertruth_refresh":
        p=HOME/".tristan"/"autonomous-maintenance"/"morphogenesis"/"compile_worker_truth.py";args=[str(py),str(p)]
    else:return False
    if not p.exists():return False
    subprocess.Popen(args,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0x08000000))
    return True
class H(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def sendj(self,obj,code=200):
        b=json.dumps(obj,ensure_ascii=False).encode();self.send_response(code)
        self.send_header("Content-Type","application/json; charset=utf-8");self.send_header("Cache-Control","no-store")
        self.end_headers();self.wfile.write(b)
    def do_GET(self):
        p=urlparse(self.path).path
        if p=="/api/state": return self.sendj(collect())
        if p=="/api/health": return self.sendj({"status":"PASS","node":socket.gethostname(),"ts":time.time()})
        if p=="/api/token": return self.sendj({"token":TOKEN})
        f="index.html" if p=="/" else p.lstrip("/")
        fp=STATIC/f
        if not fp.exists(): self.send_error(404);return
        c="text/html" if fp.suffix==".html" else "text/css" if fp.suffix==".css" else "application/javascript"
        b=fp.read_bytes();self.send_response(200);self.send_header("Content-Type",c+"; charset=utf-8");self.end_headers();self.wfile.write(b)
    def do_POST(self):
        if self.path!="/api/action": return self.sendj({"ok":False},404)
        if self.headers.get("X-Tristan-Token")!=TOKEN:return self.sendj({"ok":False,"error":"forbidden"},403)
        try:n=int(self.headers.get("Content-Length","0"));o=json.loads(self.rfile.read(n) or b"{}")
        except:return self.sendj({"ok":False,"error":"bad-json"},400)
        ok=launch(o.get("action",""));self.sendj({"ok":ok,"action":o.get("action")},200 if ok else 400)
def selftest():
    req=[STATIC/"index.html",STATIC/"app.js",STATIC/"styles.css"]
    missing=[str(x) for x in req if not x.exists()]
    try:s=collect();ok=(not missing and s.get("node")==socket.gethostname())
    except Exception as e:s={"error":repr(e)};ok=False
    out={"status":"PASS" if ok else "FAIL","schema":"tristan-cockpit-next-selftest","node":socket.gethostname(),
         "missing":missing,"state_keys":sorted(s.keys()) if isinstance(s,dict) else []}
    print(json.dumps(out));return 0 if ok else 1
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--self-test",action="store_true");ap.add_argument("--port",type=int,default=8795)
    a=ap.parse_args()
    if a.self_test:raise SystemExit(selftest())
    srv=ThreadingHTTPServer(("127.0.0.1",a.port),H)
    receipt={"schema":"tristan.cockpit.next.launch.r1","node":socket.gethostname(),"port":a.port,"ts":time.time(),"status":"RUNNING"}
    (RECEIPTS/"launch-latest.json").write_text(json.dumps(receipt,indent=2),encoding="utf-8")
    srv.serve_forever()
if __name__=="__main__":main()

