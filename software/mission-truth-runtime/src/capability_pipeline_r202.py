from __future__ import annotations
import json
from pathlib import Path
from typing import Mapping, Sequence

from capability_auction_r201 import compile_auction, digest as auction_digest
from tristan_connector_os.jarvis_mission_truth_executor_r01 import run_cycle, digest

SCHEMA="tristan.capability-pipeline.r202"

def compile_dag(mission_id:str,tasks:Sequence[Mapping[str,object]],signals:Mapping[str,object]|None=None)->dict:
    body={
        "schema":"jarvis-mission-dag-r0.1",
        "mission_id":mission_id,
        "signals":dict(signals or {}),
        "tasks":[dict(t) for t in tasks],
        "authority_granted":False,
        "external_side_effects":False,
    }
    body["digest"]=digest(body)
    return body

def compile_pipeline(
    mission_id:str,
    tasks:Sequence[Mapping[str,object]],
    signals:Mapping[str,object]|None=None,
    *,
    fleet_path=None,
)->dict:
    dag=compile_dag(mission_id,tasks,signals)
    auction=compile_auction(list(tasks)) if fleet_path is None else compile_auction(list(tasks), fleet_path=fleet_path)
    if auction.get("status")!="PASS":
        return {
            "schema":SCHEMA,
            "status":"HOLD_CAPABILITY_AUCTION",
            "mission_id":mission_id,
            "auction":auction,
            "authority_granted":False,
            "external_side_effects":False,
        }
    auction_body={
        "schema":"jarvis-mission-auction-r0.1",
        "mission_id":mission_id,
        "bids":auction["bids"],
        "authority_granted":False,
        "capability_snapshot_sha256":auction.get("capability_snapshot_sha256"),
        "coalition":auction.get("coalition",[]),
        "coalition_size":auction.get("coalition_size"),
    }
    auction_body["digest"]=digest(auction_body)
    return {
        "schema":SCHEMA,
        "status":"READY",
        "mission_id":mission_id,
        "dag":dag,
        "auction":auction_body,
        "authority_granted":False,
        "external_side_effects":False,
    }

def execute_pipeline(compiled:Mapping[str,object],root:Path,max_tasks_per_node:int=8)->dict:
    if compiled.get("status")!="READY":
        return dict(compiled)
    root.mkdir(parents=True,exist_ok=True)
    dag_path=root/"dag.json"
    auction_path=root/"auction.json"
    dag_path.write_text(json.dumps(compiled["dag"],indent=2),encoding="utf-8")
    auction_path.write_text(json.dumps(compiled["auction"],indent=2),encoding="utf-8")
    nodes=[str(x) for x in compiled["auction"].get("coalition",[]) if x]
    results=[]
    for node in nodes:
        result=run_cycle(
            dag_path=dag_path,
            auction_path=auction_path,
            node=node,
            state_root=root/node,
            shared_root=root/"shared",
            max_tasks=max_tasks_per_node,
        )
        results.append(result)
    verified=sum(int(r.get("verified",0) or 0) for r in results)
    selected=sum(int(r.get("selected",0) or 0) for r in results)
    status="PASS" if results and all(r.get("status")=="PASS" for r in results) else "HOLD"
    out={
        "schema":SCHEMA,
        "status":status,
        "mission_id":compiled["mission_id"],
        "coalition":nodes,
        "selected":selected,
        "verified":verified,
        "results":results,
        "authority_granted":False,
        "external_side_effects":False,
    }
    out["digest"]=digest(out)
    (root/"latest-r202.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
    return out
