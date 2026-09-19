#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, subprocess, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; MC=ROOT/"research"/"machining-completeness"
def load(n): return json.loads((MC/n).read_text(encoding="utf-8"))
def ready():
    g=load("task-graph-v1.json"); o=load("outcomes-v1.json")["tasks"]
    def ok(d):
        s=o[d["task"]]["state"]
        return s=="CAPABILITY_ACCEPTED" if d["type"]=="capability" else s in {"COMPLETED_RESEARCH","NEGATIVE_RESULT","CAPABILITY_ACCEPTED"}
    xs=[t["id"] for t in g["tasks"] if o[t["id"]]["state"]=="NOT_STARTED" and all(ok(d) for d in t["dependencies"])]
    print("\n".join(xs) if xs else "No task is currently evidence-ready."); return 0
def verify(task):
    ids={t["id"] for t in load("task-graph-v1.json")["tasks"]}
    if task not in ids: raise SystemExit("unknown task")
    d=MC/"tasks"/task
    for p in (d/"report.md",d/"outcome.json"):
        if not p.exists(): raise SystemExit(f"missing {p.relative_to(ROOT)}")
    obj=json.loads((d/"outcome.json").read_text(encoding="utf-8"))
    if obj.get("task")!=task or obj.get("result_kind") not in {"COMPLETED_RESEARCH","NEGATIVE_RESULT","BLOCKED","CAPABILITY_ACCEPTED"}: raise SystemExit("invalid task outcome")
    v=d/"verify.py"
    if v.exists(): subprocess.run([sys.executable,str(v),"--contract"],check=True)
    print(f"{task} contract verification passed"); return 0
def gh(method,path,body=None):
    tok=os.environ.get("GITHUB_TOKEN")
    if not tok: raise SystemExit("GITHUB_TOKEN required for sync")
    data=None if body is None else json.dumps(body).encode()
    q=urllib.request.Request("https://api.github.com/repos/techrote/radiCADSAC/"+path,data=data,method=method,headers={"Authorization":"Bearer "+tok,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","Content-Type":"application/json"})
    with urllib.request.urlopen(q,timeout=30) as r: return json.load(r) if r.status!=204 else None
def sync(check=True):
    g=load("task-graph-v1.json"); m=load("github-map-v1.json")["tasks"]; drift=[]
    for t in g["tasks"]:
        i=gh("GET",f"issues/{m[t['id']]['issue']}"); body=i.get("body") or ""; marker=f"MC:TASK:{t['id']}"
        if marker not in body: drift.append((t["id"],"missing marker"))
    if drift:
        for d in drift: print(*d)
        return 2
    print("MC GitHub issue bindings are present and unique."); return 0
if __name__=="__main__":
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest="cmd",required=True)
    sp.add_parser("ready"); v=sp.add_parser("verify"); v.add_argument("task"); s=sp.add_parser("sync"); s.add_argument("--check",action="store_true")
    a=ap.parse_args()
    raise SystemExit(ready() if a.cmd=="ready" else verify(a.task) if a.cmd=="verify" else sync(True))
