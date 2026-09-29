from __future__ import annotations
import hashlib,json,pathlib,socket,time
HOME=pathlib.Path.home(); ROOT=HOME/".tristan"/"residual-operator-map"; ROOT.mkdir(parents=True,exist_ok=True)
EVENTS=HOME/".tristan"/"event-morphogenesis"/"events.jsonl"; MAP=ROOT/"map.json"; STATE=ROOT/"state.json"
def load(p):
    try:return json.loads(pathlib.Path(p).read_text(encoding="utf-8-sig"))
    except:return {}
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding="utf-8")
def signature(evt):
    before=evt.get("before_residuals") or []
    payload={"changed":sorted(evt.get("changed") or []),
      "residuals":[(x.get("kind"),round(float(x.get("priority",0) or 0),2)) for x in before]}
    return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()[:16],payload
def path_of(evt):return ">".join(x.get("action") for x in (evt.get("actions") or []) if x.get("action"))
def classify(evt):
    a=evt.get("actions") or []; operational=all(bool((x.get("result") or {}).get("ok")) for x in a) if a else False
    d=float(evt.get("residual_delta",0) or 0)
    if not operational:return "FAIL"
    if d>0:return "IMPROVED"
    if d<0:return "WORSENED"
    return "NEUTRAL"
def recommendation(path,st):
    attempts=int(st.get("attempts",0)); imp=int(st.get("improved",0)); neu=int(st.get("neutral",0))
    wor=int(st.get("worsened",0)); fail=int(st.get("failed",0)); gain=float(st.get("residual_gain",0) or 0)
    score=float(st.get("evidence_score",0) or 0)
    if attempts>=3 and imp>=1 and score>0 and gain>0:
        return {"decision":"RUN_PATH","path":path,"evidence_score":score,"attempts":attempts,"residual_gain":gain,"eligible_to_influence":True}
    if attempts>=3 and imp==0 and wor==0 and fail==0 and neu>=3 and gain==0:
        return {"decision":"NO_ACTION_COOLDOWN","path":path,"evidence_score":score,"attempts":attempts,"residual_gain":gain,"cooldown_seconds":600,"eligible_to_influence":True}
    return {"decision":"SHADOW","path":path,"evidence_score":score,"attempts":attempts,"residual_gain":gain,"eligible_to_influence":False}
def refresh_entry(e):
    if not e.get("paths"):return
    best=max(e["paths"].items(),key=lambda kv:(kv[1].get("evidence_score",-999),kv[1].get("attempts",0)))
    e["recommendation"]=recommendation(best[0],best[1])
def ingest(evt,db):
    pth=path_of(evt)
    if not pth:return
    key,payload=signature(evt);cls=classify(evt);e=db.setdefault(key,{"signature":payload,"paths":{},"episodes":0})
    p=e["paths"].setdefault(pth,{"attempts":0,"improved":0,"neutral":0,"worsened":0,"failed":0,"residual_gain":0.0})
    p["attempts"]+=1
    p[{"IMPROVED":"improved","NEUTRAL":"neutral","WORSENED":"worsened","FAIL":"failed"}[cls]]+=1
    p["residual_gain"]=round(float(p.get("residual_gain",0))+float(evt.get("residual_delta",0) or 0),4)
    p["evidence_score"]=round((2*p["improved"]+0.25*p["neutral"]-2*p["worsened"]-2*p["failed"])/max(1,p["attempts"]),4)
    p["last_ts"]=evt.get("ts");e["episodes"]+=1;refresh_entry(e)
def main():
    db=load(MAP)
    for e in db.values():refresh_entry(e)
    save(MAP,db)
    st=load(STATE);offset=min(int(st.get("line_offset",0) or 0),len(EVENTS.read_text(encoding="utf-8-sig").splitlines()) if EVENTS.exists() else 0)
    while True:
        lines=EVENTS.read_text(encoding="utf-8-sig").splitlines() if EVENTS.exists() else []
        for line in lines[offset:]:
            try:ingest(json.loads(line),db)
            except Exception as ex:
                with open(ROOT/"ingest-errors.jsonl","a",encoding="utf-8") as f:f.write(json.dumps({"ts":time.time(),"error":repr(ex)})+"\n")
        if len(lines)>offset:offset=len(lines);save(MAP,db)
        recs=[(x.get("recommendation") or {}) for x in db.values()]
        save(STATE,{"schema":"tristan.residual_operator_map.r3","ts":time.time(),"node":socket.gethostname(),
          "line_offset":offset,"signatures":len(db),"eligible_recommendations":sum(bool(r.get("eligible_to_influence")) for r in recs),
          "no_action_recommendations":sum(r.get("decision")=="NO_ACTION_COOLDOWN" for r in recs),"mode":"CAUSAL_SHADOW_WITH_NO_ACTION"})
        time.sleep(2)
if __name__=="__main__":main()
