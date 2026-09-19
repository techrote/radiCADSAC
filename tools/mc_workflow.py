#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, re, subprocess, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MC=ROOT/"research"/"machining-completeness"
REPO="techrote/radiCADSAC"
BASE_URL="https://github.com/techrote/radiCADSAC/blob/main/"
def load(n): return json.loads((MC/n).read_text(encoding="utf-8"))
def ready():
    g=load("task-graph-v1.json"); o=load("outcomes-v1.json")["tasks"]
    def ok(d):
        s=o[d["task"]]["state"]
        return s=="CAPABILITY_ACCEPTED" if d["type"]=="capability" else s in {"COMPLETED_RESEARCH","NEGATIVE_RESULT","CAPABILITY_ACCEPTED"}
    xs=[t["id"] for t in g["tasks"] if o[t["id"]]["state"]=="NOT_STARTED" and all(ok(d) for d in t["dependencies"])]
    print("\n".join(xs) if xs else "No task is currently evidence-ready.")
    return 0
def verify(task):
    ids={t["id"] for t in load("task-graph-v1.json")["tasks"]}
    if task not in ids: raise SystemExit("unknown task")
    d=MC/"tasks"/task
    for p in (d/"report.md",d/"outcome.json"):
        if not p.exists(): raise SystemExit(f"missing {p.relative_to(ROOT)}")
    obj=json.loads((d/"outcome.json").read_text(encoding="utf-8"))
    if obj.get("task")!=task or obj.get("result_kind") not in {"COMPLETED_RESEARCH","NEGATIVE_RESULT","BLOCKED","CAPABILITY_ACCEPTED"}:
        raise SystemExit("invalid task outcome")
    v=d/"verify.py"
    if v.exists(): subprocess.run([sys.executable,str(v),"--contract"],check=True)
    print(f"{task} contract verification passed")
    return 0
def gh(method,path,body=None):
    tok=os.environ.get("GITHUB_TOKEN")
    if not tok: raise SystemExit("GITHUB_TOKEN required for sync")
    data=None if body is None else json.dumps(body).encode()
    req=urllib.request.Request("https://api.github.com/repos/"+REPO+"/"+path,data=data,method=method,
        headers={"Authorization":"Bearer "+tok,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=30) as r:
        return json.load(r) if r.status!=204 else None
def all_issues():
    out=[]; page=1
    while True:
        part=gh("GET",f"issues?state=all&per_page=100&page={page}")
        if not isinstance(part,list): raise SystemExit("GitHub issue listing failed")
        out.extend(x for x in part if "pull_request" not in x)
        if len(part)<100: return out
        page+=1
def managed(t):
    deps="\n".join(f"- \`{d['task']}\` — **{d['type']}** dependency" for d in t["dependencies"]) or "- None."
    locks=", ".join(f"\`{x}\`" for x in t["locks"]) or "isolated task paths only"
    acc="\n".join("- [ ] "+x for x in t["acceptance"])
    ver="\n".join("- "+x for x in t["verification"])
    arts="\n".join("- "+x for x in t["artifacts"])
    gate=(f"\n- [ ] Gate **{t['gate']}** changes only if its full evidence contract is genuinely satisfied; otherwise it remains \`NOT_ESTABLISHED\`." if t.get("gate") else "")
    return f"""<!-- MC:MANAGED:START {t['id']} -->
## Objective
{t['objective']}

## Scope and non-goals
**Scope:** {t['scope']}

**Non-goals:** {t['non_goals']}

## Dependencies and concurrency
{deps}

Coordination/locks: {locks}. Artifact dependencies allow only provisional research with open assumptions propagated; capability dependencies require actual evidence acceptance. Issue existence never authorizes paid/native execution or production bootstrap.

## Canonical context
Read the [MC-1 programme]({BASE_URL}docs/machining-completeness/00-PROGRAMME.md), [execution protocol]({BASE_URL}docs/machining-completeness/07-EXECUTION-PROTOCOL.md), [roadmap]({BASE_URL}docs/machining-completeness/12-ROADMAP.md), [task graph]({BASE_URL}research/machining-completeness/task-graph-v1.json), the package-relevant MC specification, and every dependency's accepted output. Historical Genesis-v2.1 evidence remains scoped through [DR-0026]({BASE_URL}docs/decisions/DR-0026-machining-completeness-programme.md). Do not depend on chat context.

## Implementation prompt for the future agent
Reconcile live \`main\`, every existing branch/PR containing \`{t['id']}\`, and dependency outcomes before changing anything. Resume the existing owner rather than restarting. State the hypothesis/falsification criterion, exact base/head, owned paths, required locks, blockers and next bounded action, then execute only this task. Preserve negative evidence and producing identities. Do not narrow the machining domain, weaken tests, inflate tolerances, drop bodies, guess lineage, promote model evidence to native geometry, use mesh-wrapped STEP as engineering success, or convert timeout/resource refusal into a solved case. Use branch → PR → applicable exact-head checks → verified merge.

## Acceptance criteria
{acc}{gate}

## Verification
{ver}
- Run \`python3 tools/validate_machining_completeness.py\`.
- Run \`python3 tools/mc_workflow.py verify {t['id']}\` when outcome artifacts exist.
- Re-run only native evidence actually invalidated by this task, under an explicit bounded permit.

## Expected artifacts
{arts}
- \`research/machining-completeness/tasks/{t['id']}/report.md\`
- \`research/machining-completeness/tasks/{t['id']}/outcome.json\`
- \`research/machining-completeness/tasks/{t['id']}/verify.py\` when executable work is claimed

## Blocking and stopping conditions
{t['blockers']}
Record blockers, affected descendants and independent work that can continue. A negative research result may complete an investigation but does not pass a capability gate by itself.
<!-- MC:MANAGED:END {t['id']} -->"""
def reconcile_body(body,t):
    marker=f"<!-- MC:TASK:{t['id']} -->"
    if marker not in body: raise ValueError("stable task marker missing")
    block=managed(t)
    start=f"<!-- MC:MANAGED:START {t['id']} -->"; end=f"<!-- MC:MANAGED:END {t['id']} -->"
    if start in body and end in body:
        a=body.index(start); b=body.index(end,a)+len(end)
        return body[:a]+block+body[b:]
    return body.rstrip()+"\n\n"+block+"\n"
def sync(apply=False):
    graph=load("task-graph-v1.json"); mapping=load("github-map-v1.json")["tasks"]; issues=all_issues()
    markers={}
    for issue in issues:
        for tid in re.findall(r"MC:TASK:(MC-\d{3})",issue.get("body") or ""):
            markers.setdefault(tid,[]).append(issue)
    duplicates={k:v for k,v in markers.items() if len(v)>1}
    if duplicates:
        for k,v in sorted(duplicates.items()): print("duplicate",k,[x["number"] for x in v])
        return 3
    drift=[]
    for t in graph["tasks"]:
        n=mapping[t["id"]]["issue"]; issue=next((x for x in issues if x["number"]==n),None)
        if issue is None: drift.append((t["id"],n,"missing bound issue")); continue
        if not (issue.get("body") or "").find(f"MC:TASK:{t['id']}")>=0: drift.append((t["id"],n,"marker/binding mismatch")); continue
        title=f"[{t['package']}] {t['id']} — {t['title']}"
        try: body=reconcile_body(issue.get("body") or "",t)
        except ValueError as e: drift.append((t["id"],n,str(e))); continue
        changed=(issue.get("title")!=title or (issue.get("body") or "")!=body)
        if changed:
            drift.append((t["id"],n,"managed drift"))
            if apply: gh("PATCH",f"issues/{n}",{"title":title,"body":body})
    if drift and not apply:
        for d in drift: print(*d)
        return 2
    if apply:
        print(f"Applied {len(drift)} managed issue update(s).")
        return 0
    print("MC GitHub managed task issues are in zero-drift state.")
    return 0
if __name__=="__main__":
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest="cmd",required=True)
    sp.add_parser("ready")
    v=sp.add_parser("verify"); v.add_argument("task")
    s=sp.add_parser("sync"); mx=s.add_mutually_exclusive_group(); mx.add_argument("--check",action="store_true"); mx.add_argument("--apply",action="store_true")
    a=ap.parse_args()
    raise SystemExit(ready() if a.cmd=="ready" else verify(a.task) if a.cmd=="verify" else sync(a.apply))
