"""R16 VERIFIER: independent scalar multi-front court and exact dual map."""
from pathlib import Path
import itertools,hashlib,json,datetime
xy=list(itertools.product(range(-8,9),repeat=2))
valid=[i for i,(x,y) in enumerate(xy) if x*x+y*y<=80]
parameters=((4,-4,2,1,0),(-4,4,1,-1,4),(2,2,1,1,-4))
objectives={"01":(0,1),"02":(0,2),"12":(1,2),"012":(0,1,2)}
def scores(p,s,d,o,i):
    a,b=xy[i]
    if o==0:
        if d:a,b=abs(a),abs(b)
        if s:a,b=2*(a//2),2*(b//2)
    else:
        if s:a,b=2*(a//2),2*(b//2)
        if d:a,b=abs(a),abs(b)
    target_x,target_y,coupling,sign,offset=parameters[p]
    return ((a-target_x)**2+(b-target_y)**2+coupling*(a-sign*b)**2,
           a*a+b*b,
           (a+b-offset)**2+(p+1)*(a-b)**2)
def dominates(a,b,j):
    le=True;strict=False
    for k in j:
        if a[k]>b[k]:return False
        if a[k]<b[k]:strict=True
    return strict
FR={}
S={}
for p,s,d,o in itertools.product(range(3),range(2),range(2),range(2)):
    data=[scores(p,s,d,o,i) for i in range(len(xy))]
    S[(p,s,d,o)]=data
    for key,J in objectives.items():
        winners=[]
        for i in valid:
            if not any(dominates(data[j],data[i],J) for j in valid if j!=i):
                winners.append(i)
        FR[f"P{p}/S{s}/D{d}/O{o}/J{key}"]=winners
assert len(FR)==96
sha=hashlib.sha256(json.dumps(FR,sort_keys=True,separators=(",",":")).encode()).hexdigest()
assert sha=="06e9ee5d6bb0a561e28738cdb43143f6520ff21c818ccc589c9fcbe1d8ed183f",sha
prior={}
for p,s,d in itertools.product(range(3),range(2),range(2)):
    for j in objectives:
        prior[f"P{p}/S{s}/D{d}/J{j}"]=FR[f"P{p}/S{s}/D{d}/O0/J{j}"]
sha15=hashlib.sha256(json.dumps(prior,sort_keys=True,separators=(",",":")).encode()).hexdigest()
assert sha15=="12bf5ebe0e1be9ea15b3057f9e111db50a94af714668f67d04c027cffeb7cdff"
added=removed=addedges=removeedges=0;witnesses=[]
for p,s,d,o in itertools.product(range(3),range(2),range(2),range(2)):
    val=S[(p,s,d,o)]
    big=set(FR[f"P{p}/S{s}/D{d}/O{o}/J012"])
    for subset in ("01","02","12"):
        small=set(FR[f"P{p}/S{s}/D{d}/O{o}/J{subset}"])
        grow=big-small;shrink=small-big
        added+=len(grow);removed+=len(shrink)
        addedges+=int(bool(grow));removeedges+=int(bool(shrink))
        j=objectives[subset]
        for x in shrink:
            y=next((y for y in valid if y!=x and dominates(val[y],val[x],(0,1,2))),None)
            assert y is not None
            assert all(val[y][k]==val[x][k] for k in j),("unexpected lost subset",p,s,d,o,subset,x,y)
            if len(witnesses)<8:witnesses.append({"context":f"P{p}/S{s}/D{d}/O{o}/J{subset}","removed":x,"dominator":y})
assert (added,removed,addedges,removeedges)==(275,58,42,12)
changed_order=0
for p,s,d,j in itertools.product(range(3),range(2),range(2),objectives):
    A=set(FR[f"P{p}/S{s}/D{d}/O0/J{j}"])
    B=set(FR[f"P{p}/S{s}/D{d}/O1/J{j}"])
    changed_order+=int(A!=B)
    if not(s and d):assert A==B
assert changed_order==12
inverse={str(i):[] for i in valid}
for key,f in FR.items():
    for i in f:inverse[str(i)].append(key)
assert sum(map(len,inverse.values()))==1171
assert len(inverse[str(xy.index((0,0)))])==88
# Pareto invariant under positive affine componentwise changes of reference objectives.
example=S[(1,0,0,0)]
transformed=[(3*q[0]+9,5*q[1]+12,7*q[2]+1) for q in example]
subset=(0,1,2)
test=[]
for i in valid:
    if not any(dominates(transformed[j],transformed[i],subset) for j in valid if j!=i):test.append(i)
assert test==FR["P1/S0/D0/O0/J012"]
out={"schema":"omega.multitristan.r16.scalar_verification","status":"INDEPENDENT_EXACT_SHA_MATCH","role":"VERIFIER","utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"method":"Pure Python scalar loops, independent of NumPy broadcasting and FORGE code",
"fronts":len(FR),"feasible_candidates":len(valid),"front_digest":sha,"R15_digest":sha15,
"added_memberships":added,"removed_memberships":removed,"transitions_with_added":addedges,"transitions_with_removed":removeedges,"changed_operator_order_fronts":changed_order,
"candidate_front_incidence":sum(map(len,inverse.values())),"candidate_origin_memberships":len(inverse[str(xy.index((0,0)))]),
"removed_tie_witnesses":witnesses,"positive_affine_invariance":True,
"source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
"limits":"Independent local synthetic reproduction, not scientific experimental confirmation."}
Path(__file__).with_name("RECEIPT_VERIFIER_R16.json").write_text(json.dumps(out,indent=2),encoding="utf8")
print(json.dumps({k:v for k,v in out.items() if k in ("status","front_digest","fronts","added_memberships","removed_memberships","changed_operator_order_fronts","candidate_front_incidence","candidate_origin_memberships")}))
