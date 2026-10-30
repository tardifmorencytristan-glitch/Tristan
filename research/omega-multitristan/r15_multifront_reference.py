"""R15 VERIFIER: independent scalar Pareto dominance, not NumPy broadcasting."""
import itertools,json,hashlib,datetime
from pathlib import Path
coords=list(itertools.product(range(-8,9),repeat=2))
allowed=[i for i,(x,y) in enumerate(coords) if x*x+y*y<=80]
assert len(allowed)==249
params=[(4,-4,2,1,0),(-4,4,1,-1,4),(2,2,1,1,-4)]
groups={"01":(0,1),"02":(0,2),"12":(1,2),"012":(0,1,2)}
def cost(p,s,d,ij):
    a,b=coords[ij]
    if d==1:a,b=abs(a),abs(b)
    if s==1:a,b=(a//2)*2,(b//2)*2
    u,v,c,sgn,off=params[p]
    return ((a-u)**2+(b-v)**2+c*(a-sgn*b)**2,a*a+b*b,(a+b-off)**2+(p+1)*(a-b)**2)
def dominates(z,y,axes):
    better=False
    for k in axes:
        if z[k]>y[k]:return False
        if z[k]<y[k]:better=True
    return better
fronts={}
for p in range(3):
  for s in range(2):
    for d in range(2):
      data={i:cost(p,s,d,i) for i in allowed}
      for k,obj in groups.items():
        front=[]
        for i in allowed:
            v=data[i]
            if not any(dominates(data[j],v,obj) for j in allowed if i!=j):front.append(i)
        fronts[f"P{p}/S{s}/D{d}/J{k}"]=front
assert len(fronts)==48
digest=hashlib.sha256(json.dumps(fronts,sort_keys=True,separators=(",",":")).encode()).hexdigest()
# Dual incidence check: candidate->context is exact transpose of context->candidate.
inv={i:[] for i in allowed}
for key,ids in fronts.items():
    for idx in ids:inv[idx].append(key)
assert sum(map(len,fronts.values()))==sum(map(len,inv.values()))
# Affine positive change of each selected objective leaves Pareto memberships invariant.
key="P1/S0/D0/J012";a0=[cost(1,0,0,i) for i in allowed]
modified={i:(2*v[0]+7,3*v[1]+11,5*v[2]+13) for i,v in zip(allowed,a0)}
orig=fronts[key]
after=[i for i in allowed if not any(dominates(modified[j],modified[i],(0,1,2)) for j in allowed if i!=j)]
assert orig==after
# Nontrivial question distinction: same candidate need not be Pareto in all objective subsets or problems.
assert any(0<len(xs)<len(fronts) for xs in inv.values())
res={"schema":"omega.multitristan.r15.independent_scalar_court","role":"VERIFIER","status":"INDEPENDENT_48_FRONT_EXACT_MATCH_CANDIDATE","utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
"method":"No NumPy; direct independent scalar integer cost evaluation and two-level nondominance enumeration",
"candidate_count":len(coords),"feasible":len(allowed),"front_count":len(fronts),"front_sha256":digest,"front_memberships_total":sum(map(len,fronts.values())),
"affine_positive_rescaling_preserves_front":True,"transpose_incidence_verified":True,
"source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
"limitations":"No external algorithm benchmark, physical test or scientific claim; compare SHA256 with FORGE after both read-backs."}
Path(__file__).with_name("RECEIPT_VERIFIER_R15.json").write_text(json.dumps(res,indent=2),encoding="utf-8")
print(json.dumps(res,ensure_ascii=True))
