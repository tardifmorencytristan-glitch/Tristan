from __future__ import annotations
import hashlib,json,pathlib,subprocess,time,socket
HOME=pathlib.Path.home(); ROOT=HOME/".tristan"/"event-morphogenesis"; ROOT.mkdir(parents=True,exist_ok=True)
STATE=ROOT/"state.json"; EVENTS=ROOT/"events.jsonl"; MAP=HOME/".tristan"/"residual-operator-map"/"map.json"
PY=HOME/"AppData"/"Local"/"Programs"/"Python"/"Python313"/"python.exe"
WATCH={"git":HOME/".tristan"/"git-autosync"/"state-latest.json","morph":HOME/".tristan"/"autonomous-maintenance"/"morphogenesis"/"state-latest.json",
"worker":HOME/".tristan"/"autonomous-maintenance"/"morphogenesis"/"worker-truth-latest.json","cockpit":HOME/"JarvisTristan"/"cockpit_runtime_next"/"state.json",
"report":HOME/".tristan"/"report-fabric"/"state.json"}
MORPH=HOME/".tristan"/"autonomous-maintenance"/"morphogenesis"/"compile_state.py"
WAVE=HOME/".tristan"/"autonomous-maintenance"/"morphogenesis"/"wave_a_court.py"
WT=HOME/".tristan"/"autonomous-maintenance"/"morphogenesis"/"compile_worker_truth.py"
def load(p):
    try:return json.loads(pathlib.Path(p).read_text(encoding="utf-8-sig"))
    except:return {}
def mtimes():
    out={}
    for k,p in WATCH.items():
        try:out[k]=p.stat().st_mtime_ns
        except:out[k]=0
    return out
def residual_vector():
    w=load(WATCH["morph"]).get("weakness_atlas") or []
    return [{"kind":x.get("kind"),"priority":float(x.get("priority",0) or 0)} for x in w]
def burden(v):return round(sum(x["priority"] for x in v),4)
def signature(changed,before):
    payload={"changed":sorted(changed),"residuals":[(x.get("kind"),round(float(x.get("priority",0) or 0),2)) for x in before]}
    return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()[:16]
def learned_decision(sig):
    return ((load(MAP).get(sig) or {}).get("recommendation") or {})
def run(script,timeout=120):
    if not script.exists():return {"ok":False,"status":"ABSENT"}
    try:
        cp=subprocess.run([str(PY),str(script)],capture_output=True,text=True,timeout=timeout,
          creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0x08000000))
        return {"ok":cp.returncode==0,"code":cp.returncode,"out":(cp.stdout or "")[-1000:],"err":(cp.stderr or "")[-1000:]}
    except Exception as e:return {"ok":False,"status":"ERROR","err":repr(e)}
def append_event(o):
    with open(EVENTS,"a",encoding="utf-8") as f:f.write(json.dumps(o,ensure_ascii=False)+"\n")
def main():
    host=socket.gethostname();prev=mtimes();last_action={};last_no_action={};level=1;idle=0
    while True:
        cur=mtimes();changed=[k for k,v in cur.items() if v!=prev.get(k)];now=time.time();before=residual_vector()
        sig=signature(changed,before);rec=learned_decision(sig);suppressed=False;actions=[];debounce=max(2,12-level)
        def ready(k):return now-last_action.get(k,0)>=debounce
        noact=rec.get("decision")=="NO_ACTION_COOLDOWN" and rec.get("eligible_to_influence")
        cooldown=int(rec.get("cooldown_seconds",600) or 600)
        if noact and now-last_no_action.get(sig,0)<cooldown:
            suppressed=True
        else:
            if noact:last_no_action[sig]=now
            if "git" in changed and ready("morph"):actions.append(("morph",MORPH))
            if "morph" in changed:
                if ready("wave"):actions.append(("wave",WAVE))
                if ready("worker"):actions.append(("worker",WT))
        if changed:idle=0;level=min(8,level+1)
        else:
            idle+=1
            if idle>=15:level=max(1,level-1);idle=0
        results=[];seen=set()
        for name,script in actions:
            if name in seen:continue
            seen.add(name);r=run(script);last_action[name]=time.time();results.append({"action":name,"result":r})
            if not r.get("ok"):level=max(1,level-2)
        after=residual_vector()
        if results or suppressed:
            evt={"schema":"tristan.event.morphogenesis.episode.r2","ts":time.time(),"node":host,"signature":sig,
                 "changed":changed,"actions":results,"suppressed_by_learning":suppressed,"learned_recommendation":rec,
                 "before_residuals":before,"after_residuals":after,"before_burden":burden(before),"after_burden":burden(after),
                 "residual_delta":round(burden(before)-burden(after),4)}
            append_event(evt)
        STATE.write_text(json.dumps({"schema":"tristan.event.morphogenesis.r4","ts":now,"node":host,"changed":changed,
          "acceleration_level":level,"results":results,"learned_decision":rec,"suppressed_by_learning":suppressed,
          "poll_seconds":max(1,5-level//2)},indent=2),encoding="utf-8")
        prev=cur;time.sleep(max(1,5-level//2))
if __name__=="__main__":main()
