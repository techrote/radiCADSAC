#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MC=ROOT/"research"/"machining-completeness"
DOC=ROOT/"docs"/"machining-completeness"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def fail(m): raise AssertionError(m)
def validate(graph=None,programme=None,outcomes=None,ghmap=None,posdoc=None):
    required=[ROOT/"handoffs/current-authority.json", DOC/"00-PROGRAMME.md", DOC/"01-DOMAIN-AND-SEMANTICS.md", DOC/"02-COMPLETENESS-ARGUMENT.md", DOC/"03-ORACLE-AND-CORPUS.md", DOC/"04-REPRESENTATION-AND-RECONSTRUCTION.md", DOC/"05-QUALIFICATION.md", DOC/"06-MC1-DECISION.md", DOC/"07-EXECUTION-PROTOCOL.md", DOC/"08-SOURCES-AND-EVIDENCE.md", DOC/"09-REVIEW-AND-CHANGELOG.md", DOC/"10-RAG-INDEX.md", DOC/"11-FORMAT-CONTRACTS.md", DOC/"12-ROADMAP.md", MC/"programme-v1.json", MC/"task-graph-v1.json", MC/"proof-obligations-v1.json", MC/"fixture-families-v1.json", MC/"evidence-ledger-v1.json", MC/"outcomes-v1.json", MC/"authority-map-v1.json", MC/"github-map-v1.json"]
    for p in required:
        if not p.exists(): fail(f"missing {p.relative_to(ROOT)}")
    graph=graph or load(MC/"task-graph-v1.json"); programme=programme or load(MC/"programme-v1.json"); outcomes=outcomes or load(MC/"outcomes-v1.json"); ghmap=ghmap or load(MC/"github-map-v1.json"); posdoc=posdoc or load(MC/"proof-obligations-v1.json")
    tasks=graph["tasks"]; ids=[t["id"] for t in tasks]; idset=set(ids)
    expected={f"MC-{i:03d}" for i in range(1,59)}
    if len(tasks)!=58 or idset!=expected or len(ids)!=len(idset): fail("MC task ID/count mismatch")
    for t in tasks:
        for k in ("package","title","objective","scope","non_goals","acceptance","verification","artifacts","blockers","locks"):
            if k not in t: fail(f"{t['id']} missing {k}")
        if not t["acceptance"] or not t["verification"] or not t["artifacts"]: fail(f"{t['id']} missing executable contract")
        for d in t["dependencies"]:
            if d["task"] not in idset or d["type"] not in {"artifact","capability"}: fail(f"{t['id']} bad dependency")
    indeg={i:0 for i in idset}; rev={i:[] for i in idset}
    for t in tasks:
        for d in t["dependencies"]: indeg[t["id"]]+=1; rev[d["task"]].append(t["id"])
    q=sorted(i for i,n in indeg.items() if n==0); seen=[]
    while q:
        x=q.pop(0); seen.append(x)
        for y in rev[x]:
            indeg[y]-=1
            if indeg[y]==0: q.append(y); q.sort()
    if len(seen)!=58: fail("dependency cycle")
    pids=[p["id"] for p in graph["packages"]]
    if pids!=[f"MG-{i:02d}" for i in range(14)]: fail("package hierarchy mismatch")
    members=[x for p in graph["packages"] for x in p["tasks"]]
    if sorted(members)!=sorted(ids) or len(members)!=len(set(members)): fail("package membership mismatch")

    gate_owners={"MC-A":"MC-005","MC-B":"MC-038","MC-C":"MC-016","MC-D":"MC-041","MC-E":"MC-044","MC-F":"MC-048","MC-1":"MC-052"}
    gate_states={"MC-A":"ACCEPTED","MC-B":"NOT_ESTABLISHED","MC-C":"NOT_ESTABLISHED","MC-D":"NOT_ESTABLISHED","MC-E":"NOT_ESTABLISHED","MC-F":"NOT_ESTABLISHED","MC-1":"NOT_ESTABLISHED"}
    gates={g["id"]:g for g in programme["gates"]}
    for g,o in gate_owners.items():
        if gates.get(g,{}).get("owner")!=o or gates[g].get("state")!=gate_states[g]: fail(f"{g} current state/owner mismatch")
    if programme.get("capability_status")!="NOT_ESTABLISHED": fail("MC-1 capability advanced before final gate")
    if programme.get("production_authorized") or programme.get("expensive_execution_authorized"): fail("MC-A must not authorize production/native spend")

    if set(outcomes["tasks"])!=idset or set(ghmap["tasks"])!=idset: fail("task registry set mismatch")
    if outcomes["tasks"]["MC-005"].get("state")!="CAPABILITY_ACCEPTED": fail("MC-005 outcome registry mismatch")
    if outcomes["tasks"]["MC-005"].get("blockers")!=[]: fail("accepted MC-005 may not retain blockers")
    nums=[]
    for i in ids:
        n=ghmap["tasks"][i].get("issue")
        if not isinstance(n,int) or n<=0: fail(f"{i} missing issue")
        nums.append(n)
    if len(nums)!=len(set(nums)) or ghmap.get("programme_issue")!=62: fail("GitHub map mismatch")

    if posdoc.get("status")!="PARTIALLY_ESTABLISHED": fail("PO register aggregate state mismatch")
    pos=posdoc["obligations"]
    if [p["id"] for p in pos]!=[f"PO-{i:02d}" for i in range(1,13)]: fail("PO register mismatch")
    for i,p in enumerate(pos,1):
        expected_state="ACCEPTED" if i==1 else "OPEN"
        if p.get("state")!=expected_state: fail(f"PO-{i:02d} current state mismatch")
    if "research/machining-completeness/tasks/MC-005/domain-lock-review-v1.json" not in pos[0].get("accepted_evidence",[]): fail("PO-01 MC-005 evidence binding missing")
    if any(p.get("accepted_evidence") for p in pos[1:]): fail("unaccepted PO has accepted evidence")

    fam=load(MC/"fixture-families-v1.json")["families"]
    if [f["id"] for f in fam]!=[f"F{i:02d}" for i in range(1,17)]: fail("fixture register mismatch")
    allowed_fixture_states={"UNBUILT","BUILT"}
    for f in fam:
        state=f.get("state"); owner=f.get("owner")
        if state not in allowed_fixture_states or f.get("mandatory") is not True: fail(f"fixture state/mandatory mismatch for {f.get('id')}")
        if owner not in outcomes["tasks"]: fail(f"fixture owner mismatch for {f.get('id')}")
        if state=="BUILT" and outcomes["tasks"][owner].get("state")=="NOT_STARTED": fail(f"built fixture has no completed producing owner: {f.get('id')}")
    auth=load(ROOT/"handoffs/current-authority.json")
    if auth.get("programme")!="MC-1" or auth.get("production_authorized") is not False: fail("current authority mismatch")
    for p in (ROOT/"README.md",ROOT/"AGENTS.md",ROOT/"handoffs/README.md"):
        s=p.read_text(encoding="utf-8")
        if "MC-1" not in s or "current-authority.json" not in s: fail(f"{p.name} lacks MC-1 current routing")
    protected=[ROOT/"research/rcs-021/measured-summary-v1.json",ROOT/"research/rcs-021/material_oracle.py",ROOT/"research/rcs-021/manifold_fallback.py",ROOT/"research/rcs-021/field.py",ROOT/"handoffs/genesis-release-v2.json",ROOT/"handoffs/evidence-dependencies-v2.1.json"]
    for p in protected:
        if not p.exists(): fail(f"protected historical input missing: {p.relative_to(ROOT)}")
    return True

def self_test():
    g=load(MC/"task-graph-v1.json"); p=load(MC/"programme-v1.json"); o=load(MC/"outcomes-v1.json"); m=load(MC/"github-map-v1.json"); pos=load(MC/"proof-obligations-v1.json")
    validate(g,p,o,m,pos)
    bad=copy.deepcopy(g); bad["tasks"][0]["dependencies"].append({"task":"MC-001","type":"artifact"})
    try: validate(bad,p,o,m,pos)
    except AssertionError: pass
    else: fail("self-test failed to reject cycle")
    badp=copy.deepcopy(p); next(x for x in badp["gates"] if x["id"]=="MC-B")["state"]="ACCEPTED"
    try: validate(g,badp,o,m,pos)
    except AssertionError: pass
    else: fail("self-test failed to reject premature later gate")
    badp=copy.deepcopy(p); next(x for x in badp["gates"] if x["id"]=="MC-A")["state"]="NOT_ESTABLISHED"
    try: validate(g,badp,o,m,pos)
    except AssertionError: pass
    else: fail("self-test failed to reject MC-A regression")
    badpos=copy.deepcopy(pos); badpos["obligations"][1]["state"]="ACCEPTED"
    try: validate(g,p,o,m,badpos)
    except AssertionError: pass
    else: fail("self-test failed to reject premature proof obligation")
    bado=copy.deepcopy(o); bado["tasks"]["MC-005"]["state"]="COMPLETED_RESEARCH"
    try: validate(g,p,bado,m,pos)
    except AssertionError: pass
    else: fail("self-test failed to reject MC-005 gate/outcome mismatch")
    print("MC-1 validator self-test passed")
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--self-test",action="store_true"); a=ap.parse_args()
    validate()
    self_test() if a.self_test else print("MC-1 static validation passed")
