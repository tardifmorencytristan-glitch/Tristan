"""R16 OAK: adversarial tie, commutator and lossy duplicate court."""
from pathlib import Path
from itertools import product
from hashlib import sha256
import json,datetime
coords=list(product(range(-8,9),repeat=2))
valid=[k for k,(a,b) in enumerate(coords) if a*a+b*b<=80]
params=((4,-4,2,1,0),(-4,4,1,-1,4),(2,2,1,1,-4))
sets={"01":(0,1),"02":(0,2),"12":(1,2),"012":(0,1,2)}
def modify(x,y,order):
    if order=="DS":
        x,y=abs(x),abs(y)
        return ((x//2)*2,(y//2)*2)
    return (abs((x//2)*2),abs((y//2)*2))
def score(p,a,b):
    u,v,c,sgn,off=params[p]
    return ((a-u)**2+(b-v)**2+c*(a-sgn*b)**2,a*a+b*b,(a+b-off)**2+(p+1)*(a-b)**2)
def dominates(a,b,J):return all(a[k]<=b[k] for k in J) and any(a[k]<b[k] for k in J)
def front(scores,J):
    result=set()
    for i in valid:
        if not any(dominates(scores[j],scores[i],J) for j in valid if i!=j):result.add(i)
    return result
# The Pareto subset-lattice monotonicity hypothesis is false with tied objectives.
minimal_shrink=[(0,0),(0,1)]
assert set(range(2))=={i for i in range(2) if not any(dominates(minimal_shrink[j],minimal_shrink[i],(0,)) for j in range(2) if j!=i)}
assert {0}=={i for i in range(2) if not any(dominates(minimal_shrink[j],minimal_shrink[i],(0,1)) for j in range(2) if j!=i)}
minimal_growth=[(0,1),(1,0)]
assert {0}=={i for i in range(2) if not any(dominates(minimal_growth[j],minimal_growth[i],(0,)) for j in range(2) if j!=i)}
assert {0,1}=={i for i in range(2) if not any(dominates(minimal_growth[j],minimal_growth[i],(0,1)) for j in range(2) if j!=i)}
a=modify(-1,0,"DS");b=modify(-1,0,"SD")
assert a==(0,0) and b==(2,0)
changed=[i for i in valid if modify(*coords[i],"DS")!=modify(*coords[i],"SD")]
assert changed
worst=max(sum(abs(x-y) for x,y in zip(modify(*coords[i],"DS"),modify(*coords[i],"SD"))) for i in changed)
by_problem=[]
for p in range(3):
    reference=[score(p,*coords[i]) for i in range(len(coords))]
    ds=[score(p,*modify(*coords[i],"DS")) for i in range(len(coords))]
    sd=[score(p,*modify(*coords[i],"SD")) for i in range(len(coords))]
    uniqDS=len(set(modify(*coords[i],"DS") for i in valid))
    uniqSD=len(set(modify(*coords[i],"SD") for i in valid))
    for name,J in sets.items():
        R=front(reference,J);A=front(ds,J);B=front(sd,J)
        assert A!=B
        by_problem.append({"problem":p,"objectives":name,"DS_front":len(A),"SD_front":len(B),
          "order_symmetric_difference":len(A^B),
          "DS_false_memberships_vs_fine_signed":len(A-R),
          "SD_false_memberships_vs_fine_signed":len(B-R),
          "distinct_DS_designs":uniqDS,"distinct_SD_designs":uniqSD,
          "DS_unique_score_vectors":len(set(ds[i] for i in A)),"SD_unique_score_vectors":len(set(sd[i] for i in B))})
assert len(by_problem)==12
# TTM remembers candidate IDs as distinct traces even where transformed states coincide.
report={"schema":"omega.multitristan.r16.adversarial_guard","role":"OAK","status":"EXACT_FALSIFICATION_AND_LOSS_DIAGNOSIS","utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"candidate_feasible":len(valid),
"operator_order":"DS=abs then even-floor; SD=even-floor then abs","one_dimensional_counterexample":{"initial":-1,"DS":a[0],"SD":b[0]},
"noncommuting_input_candidates":len(changed),"max_l1_operator_residual":worst,
"proof_counterexample_shrink":{"points":minimal_shrink,"front_one_obj":[0,1],"front_two_obj":[0]},
"proof_counterexample_growth":{"points":minimal_growth,"front_one_obj":[0],"front_two_obj":[0,1]},
"order_contexts_different":len(by_problem),"context_details":by_problem,
"hard_guard":"REJECT automatic replacement of fine signed model by lossy transform; keep original candidate IDs and provenance.",
"evidence_status":"synthetic exact finite arithmetic, not external scientific validation",
"source_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
"next_questions":["How to represent tied candidates while preserving historical identity?","How to distinguish an objective change from a representation change?","Which reversible embeddings can retain original signed values?"]}
Path(__file__).with_name("RECEIPT_OAK_R16.json").write_text(json.dumps(report,indent=2),encoding="utf8")
print(json.dumps({k:v for k,v in report.items() if k in ("status","candidate_feasible","noncommuting_input_candidates","max_l1_operator_residual","order_contexts_different","one_dimensional_counterexample")}))
