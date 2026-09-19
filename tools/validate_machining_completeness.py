#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MC=ROOT/"research"/"machining-completeness"
DOC=ROOT/"docs"/"machining-completeness"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def fail(m): raise AssertionError(m)
def validate(graph=None,programme=None,outcomes=None,ghmap=None):
    required=[ROOT/"handoffs/current-authority.json", DOC/"00-PROGRAMME.md", DOC/"01-DOMAIN-AND-SEMANTICS.md", DOC/"02-COMPLETENESS-ARGUMENT.md", DOC/"03-ORACLE-AND-CORPUS.md", DOC/"04-REPRESENTATION-AND-RECONSTRUCTION.md", DOC/"05-QUALIFICATION.md", DOC/"06-MC1-DECISION.md", DOC/"07-EXECUTION-PROTOCOL.md", DOC/"08-SOURCES-AND-EVIDENCE.md", DOC/"09-REVIEW-AND-CHANGELOG.md", DOC/"10-RAG-INDEX.md", DOC/"11-FORMAT-CONTRACTS.md", DOC/"12-ROADMAP.md", MC/"programme-v1.json", MC/"task-graph-v1.json", MC/"proof-obligations-v1.json", MC/"fixture-families-v1.json", MC/"evidence-ledger-v1.json", MC/"outcomes-v1.json", MC/"authority-map-v1.json", MC/"github-map-v1.json"]
    for p in required:
        if not p.exists(): fail(f"missing {p.relative_to(ROOT)}")
    graph=graph or load(MC/"task-graph-v1.json"); programme=programme or load(MC/"programme-v1.json"); outcomes=outcomes or load(MC/"outcomes-v1.json"); ghmap=ghmap or load(MC/"github-map-v1.json")
    tasks=graph["tasks"]; ids=[t["id"] for t in tasks]; idset=set(ids)
    expected={f"MC-{i:03d}" for i in range(1,58)}
    if len(tasks)!=57 or idset!=expected or len(ids)!=len(idset): fail("MC task ID/count mismatch")
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
    if len(seen)!=57: fail("dependency cycle")
    pids=[p["id"] for p in graph["packages"]]
    if pids!=[f"MG-{i:02d}" for i in range(14)]: fail("package hierarchy mismatch")
    members=[x for p in graph["packages"] for x in p["tasks"]]
    if sorted(members)!=sorted(ids) or len(members)!=len(set(members)): fail("package membership mismatch")
    go={"MC-A":"MC-005","MC-B":"MC-038","MC-C":"MC-016","MC-D":"MC-041","MC-E":"MC-044","MC-F":"MC-048","MC-1":"MC-052"}
    gates={g["id"]:g for g in programme["gates"]}
    for g,o in go.items():
        if gates.get(g,{}).get("owner")!=o or gates[g]["state"]!="NOT_ESTABLISHED": fail(f"{g} adoption state/owner mismatch")
    if programme.get("production_authorized") or programme.get("expensive_execution_authorized"): fail("adoption must not authorize production/native spend")
    if set(outcomes["tasks"])!=idset or set(ghmap["tasks"])!=idset: fail("task registry set mismatch")
    nums=[]
    for i in ids:
        n=ghmap["tasks"][i].get("issue")
        if not isinstance(n,int) or n<=0: fail(f"{i} missing issue")
        nums.append(n)
    if len(nums)!=len(set(nums)) or ghmap.get("programme_issue")!=62: fail("GitHub map mismatch")
    pos=load(MC/"proof-obligations-v1.json")["obligations"]
    if [p["id"] for p in pos]!=[f"PO-{i:02d}" for i in range(1,13)] or any(p["state"]!="OPEN" for p in pos): fail("PO register mismatch")
    fam=load(MC/"fixture-families-v1.json")["families"]
    if [f["id"] for f in fam]!=[f"F{i:02d}" for i in range(1,17)] or any(f["state"]!="UNBUILT" for f in fam): fail("fixture register mismatch")
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
    g=load(MC/"task-graph-v1.json"); p=load(MC/"programme-v1.json"); o=load(MC/"outcomes-v1.json"); m=load(MC/"github-map-v1.json")
    validate(g,p,o,m)
    bad=copy.deepcopy(g); bad["tasks"][0]["dependencies"].append({"task":"MC-001","type":"artifact"})
    try: validate(bad,p,o,m)
    except AssertionError: pass
    else: fail("self-test failed to reject cycle")
    badp=copy.deepcopy(p); badp["gates"][0]["state"]="ACCEPTED"
    try: validate(g,badp,o,m)
    except AssertionError: pass
    else: fail("self-test failed to reject premature gate")
    print("MC-1 validator self-test passed")
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--self-test",action="store_true"); a=ap.parse_args()
    validate()
    self_test() if a.self_test else print("MC-1 static validation passed")
