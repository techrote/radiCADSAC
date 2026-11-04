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
    # A cheap task verifier is not a gate authority. It must nevertheless
    # refuse an artifact that promotes its own status or changes its issue
    # binding relative to the accepted outcome and GitHub registries.
    outcomes=load("outcomes-v1.json"); mapping=load("github-map-v1.json")
    registered=(outcomes.get("tasks",{}).get(task)
                if isinstance(outcomes,dict) and isinstance(outcomes.get("tasks"),dict)
                else None)
    mapped=(mapping.get("tasks",{}).get(task)
            if isinstance(mapping,dict) and isinstance(mapping.get("tasks"),dict)
            else None)
    if (not isinstance(obj,dict)
            or obj.get("schema")!="radicadsac-mc-task-outcome/1.0"
            or obj.get("task")!=task
            or type(obj.get("result_kind")) is not str
            or obj.get("result_kind") not in {"COMPLETED_RESEARCH","NEGATIVE_RESULT","BLOCKED","CAPABILITY_ACCEPTED"}
            or not isinstance(registered,dict) or not isinstance(mapped,dict)
            # A BLOCKED provisional report may precede registry acceptance:
            # MC-038 deliberately remains NOT_STARTED in the authoritative map.
            or (obj.get("result_kind")!=registered.get("state")
                and not (registered.get("state")=="NOT_STARTED"
                         and obj.get("result_kind")=="BLOCKED"))
            or type(obj.get("issue")) is not int
            or type(registered.get("issue")) is not int
            or type(mapped.get("issue")) is not int
            or obj["issue"]!=registered["issue"] or obj["issue"]!=mapped["issue"]):
        raise SystemExit("invalid or unregistered task outcome")
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
    deps="\n".join(f"- `{d['task']}` — **{d['type']}** dependency" for d in t["dependencies"]) or "- None."
    locks=", ".join(f"`{x}`" for x in t["locks"]) or "isolated task paths only"
    acc="\n".join("- [ ] "+x for x in t["acceptance"])
    ver="\n".join("- "+x for x in t["verification"])
    arts="\n".join("- "+x for x in t["artifacts"])
    gate=(f"\n- [ ] Gate **{t['gate']}** changes only if its full evidence contract is genuinely satisfied; otherwise it remains `NOT_ESTABLISHED`." if t.get("gate") else "")
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
Reconcile live `main`, every existing branch/PR containing `{t['id']}`, and dependency outcomes before changing anything. Resume the existing owner rather than restarting. State the hypothesis/falsification criterion, exact base/head, owned paths, required locks, blockers and next bounded action, then execute only this task. Preserve negative evidence and producing identities. Do not narrow the machining domain, weaken tests, inflate tolerances, drop bodies, guess lineage, promote model evidence to native geometry, use mesh-wrapped STEP as engineering success, or convert timeout/resource refusal into a solved case. Use branch → PR → applicable exact-head checks → verified merge.

## Acceptance criteria
{acc}{gate}

## Verification
{ver}
- Run `python3 tools/validate_machining_completeness.py`.
- Run `python3 tools/mc_workflow.py verify {t['id']}` when outcome artifacts exist.
- Re-run only native evidence actually invalidated by this task, under an explicit bounded permit.

## Expected artifacts
{arts}
- `research/machining-completeness/tasks/{t['id']}/report.md`
- `research/machining-completeness/tasks/{t['id']}/outcome.json`
- `research/machining-completeness/tasks/{t['id']}/verify.py` when executable work is claimed

## Blocking and stopping conditions
{t['blockers']}
Record blockers, affected descendants and independent work that can continue. A negative research result may complete an investigation but does not pass a capability gate by itself.
<!-- MC:MANAGED:END {t['id']} -->"""
def reconcile_body(body,t):
    marker=f"<!-- MC:TASK:{t['id']} -->"
    if body.count(marker)!=1: raise ValueError("expected exactly one stable task marker")
    block=managed(t)
    start=f"<!-- MC:MANAGED:START {t['id']} -->"; end=f"<!-- MC:MANAGED:END {t['id']} -->"
    opens=body.count(start); closes=body.count(end)
    if opens!=closes or opens>1:
        raise ValueError("incomplete or duplicate managed block delimiters")
    if opens:
        a=body.index(start); b=body.index(end)
        if b<a: raise ValueError("managed block end precedes start")
        b+=len(end)
        if a<=body.index(marker)<b:
            raise ValueError("stable task marker lies inside replaceable managed block")
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

    # Plan every mutation before issuing a PATCH: missing bindings, malformed
    # managed blocks and marker conflicts must not leave a partial sync behind.
    drift=[]; conflicts=[]; changes=[]
    by_number={issue["number"]:issue for issue in issues}
    bound_numbers={}
    for t in graph["tasks"]:
        n=mapping[t["id"]]["issue"]
        if n in bound_numbers:
            conflicts.append((t["id"],n,f"issue also bound to {bound_numbers[n]}"))
            continue
        bound_numbers[n]=t["id"]
        issue=by_number.get(n)
        if issue is None:
            conflicts.append((t["id"],n,"missing bound issue"))
            continue
        if f"MC:TASK:{t['id']}" not in (issue.get("body") or ""):
            conflicts.append((t["id"],n,"marker/binding mismatch"))
            continue
        title=f"[{t['package']}] {t['id']} — {t['title']}"
        try: body=reconcile_body(issue.get("body") or "",t)
        except ValueError as e:
            conflicts.append((t["id"],n,str(e)))
            continue
        if issue.get("title")!=title or (issue.get("body") or "")!=body:
            drift.append((t["id"],n,"managed drift"))
            changes.append((n,title,body,issue.get("title"),issue.get("body") or ""))
    if conflicts:
        for d in conflicts: print("conflict",*d)
        for d in drift: print("pending",*d)
        return 3
    if drift and not apply:
        for d in drift: print(*d)
        return 2
    if apply:
        # Refresh the complete proposed write set before mutation. There is no
        # issue-body compare-and-swap in this API; this detects stale plans
        # without silently overwriting edits observed since enumeration.
        for n,title,body,old_title,old_body in changes:
            observed=gh("GET",f"issues/{n}")
            if observed.get("title")!=old_title or (observed.get("body") or "")!=old_body:
                print("pre-write conflict",n)
                return 4
        for n,title,body,_,_ in changes:
            gh("PATCH",f"issues/{n}",{"title":title,"body":body})
            observed=gh("GET",f"issues/{n}")
            if observed.get("title")!=title or (observed.get("body") or "")!=body:
                print("post-write mismatch",n)
                return 4
        print(f"Applied {len(changes)} managed issue update(s); verified read-back.")
        return 0
    print("MC GitHub managed task issues are in zero-drift state.")
    return 0

def self_test_verify():
    """Fail closed on self-promoted status, forged issue bindings and bad shapes."""
    from tempfile import TemporaryDirectory
    from unittest.mock import patch
    with TemporaryDirectory() as td:
        root=Path(td); d=root/"tasks"/"MC-038"; d.mkdir(parents=True)
        (d/"report.md").write_text("synthetic contract",encoding="utf-8")
        (d/"verify.py").write_text("# mocked verifier",encoding="utf-8")
        canonical={"schema":"radicadsac-mc-task-outcome/1.0",
                   "task":"MC-038","result_kind":"BLOCKED","issue":100}
        fixtures={
            "task-graph-v1.json":{"tasks":[{"id":"MC-038"}]},
            "outcomes-v1.json":{"tasks":{"MC-038":{"state":"NOT_STARTED","issue":100}}},
            "github-map-v1.json":{"tasks":{"MC-038":{"issue":100}}},
        }
        def fake_load(name):
            return fixtures[name]
        bad=[
            dict(canonical,result_kind="CAPABILITY_ACCEPTED"),
            dict(canonical,issue=101),
            dict(canonical,issue=True),
            dict(canonical,schema="unknown-schema"),
            dict(canonical,task="MC-005"),
            None,
            ["not an outcome object"],
            dict(canonical,result_kind=[]),
            dict(canonical,result_kind={}),
        ]
        with (patch.dict(globals(),{"MC":root}),
              patch(__name__+".load",side_effect=fake_load),
              patch(__name__+".subprocess.run") as runner):
            (d/"outcome.json").write_text(json.dumps(canonical),encoding="utf-8")
            assert verify("MC-038")==0
            assert runner.call_count==1, "valid contract verifier not invoked"
            for sample in bad:
                (d/"outcome.json").write_text(json.dumps(sample),encoding="utf-8")
                try: verify("MC-038")
                except SystemExit as exc:
                    assert str(exc)=="invalid or unregistered task outcome", (
                        f"unexpected refusal for {sample}: {exc}")
                else: raise AssertionError(f"accepted forged task outcome: {sample}")
            assert runner.call_count==1, "forged task outcome reached verifier"
            # Corrupted authoritative mappings must also refuse an otherwise
            # well-formed source artifact instead of silently accepting it.
            (d/"outcome.json").write_text(json.dumps(canonical),encoding="utf-8")
            fixtures["outcomes-v1.json"]["tasks"]["MC-038"]["state"]="CAPABILITY_ACCEPTED"
            try: verify("MC-038")
            except SystemExit: pass
            else: raise AssertionError("accepted inconsistent registered state")
            fixtures["outcomes-v1.json"]["tasks"]["MC-038"]["state"]="NOT_STARTED"
            fixtures["github-map-v1.json"]["tasks"]["MC-038"]["issue"]=101
            try: verify("MC-038")
            except SystemExit: pass
            else: raise AssertionError("accepted inconsistent GitHub issue map")
            assert runner.call_count==1, "inconsistent registry reached verifier"
    print("MC task outcome authority-binding adversarial self-test passed")


def self_test():
    """Offline adversarial coverage of zero-write conflicts and exact read-back."""
    from unittest.mock import patch

    task={"id":"MC-999","package":"MG-99","title":"Test task",
          "objective":"Current objective","scope":"Scoped","non_goals":"No production",
          "dependencies":[],"locks":[],"acceptance":["A"],"verification":["V"],
          "artifacts":["R"],"blockers":"None"}
    graph={"tasks":[task]}
    mapping={"tasks":{"MC-999":{"issue":991}}}
    marker="<!-- MC:TASK:MC-999 -->"
    good=marker+"\n\nHuman-owned notes\n\n"+managed(task)+"\n\nHuman-owned tail\n"
    stale=good.replace("Current objective","Stale objective",1)
    issues=[{"number":991,"title":"Old title","body":stale}]
    calls=[]

    def fake_load(name):
        return {"task-graph-v1.json":graph,"github-map-v1.json":mapping}[name]
    def fake_issues():
        return [dict(issue) for issue in issues]
    def fake_gh(method,path,body=None):
        n=int(path.rsplit("/",1)[1])
        calls.append((method,n))
        if method=="PATCH":
            issue=next(issue for issue in issues if issue["number"]==n)
            issue.update(body)
            return dict(issue)
        if method=="GET":
            return dict(next(issue for issue in issues if issue["number"]==n))
        raise AssertionError("unexpected GitHub method")

    def reject(body):
        try: reconcile_body(body,task)
        except ValueError: return
        raise AssertionError("accepted a corrupt managed-body marker/delimiter")

    reject(good.replace("<!-- MC:MANAGED:END MC-999 -->",""))
    reject(good.replace("<!-- MC:MANAGED:START MC-999 -->",""))
    reject(good+"\n<!-- MC:MANAGED:START MC-999 -->")
    reject(good.replace(marker,marker+"\n"+marker))
    reject(marker+"\n<!-- MC:MANAGED:END MC-999 -->\n<!-- MC:MANAGED:START MC-999 -->")
    reject("<!-- MC:MANAGED:START MC-999 -->\n"+marker+"\n<!-- MC:MANAGED:END MC-999 -->")
    with (patch(__name__+".load",side_effect=fake_load),
          patch(__name__+".all_issues",side_effect=fake_issues),
          patch(__name__+".gh",side_effect=fake_gh)):
        assert sync(False)==2 and not calls, "check mode mutated the issue"
        assert sync(True)==0 and calls==[("GET",991),("PATCH",991),("GET",991)], "apply failed to verify mutation"
        assert issues[0]["body"]==good, "managed update modified human-owned text"
        calls.clear()
        assert sync(True)==0 and not calls, "unchanged apply caused a write"
        assert sync(False)==0, "corrected issue was still in drift"

        # A missing issue or marker cannot be silently reported as applied.
        issues.clear()
        assert sync(True)==3 and not calls, "missing mapped issue did not block"
        issues.append({"number":991,"title":"Old title","body":"No stable marker"})
        assert sync(True)==3 and not calls, "missing marker did not block"
        issues[0]={"number":991,"title":"Old title","body":marker+"\n<!-- MC:MANAGED:START MC-999 -->"}
        assert sync(True)==3 and not calls, "malformed managed block did not block"

        # A late hard conflict must abort the entire batch, not write the
        # earlier, otherwise applicable update.
        issues[0]={"number":991,"title":"Old title","body":stale}
        task2=dict(task,id="MC-998")
        graph["tasks"].append(task2)
        mapping["tasks"]["MC-998"]={"issue":992}
        assert sync(True)==3 and not calls, "partial write preceded a later conflict"
        graph["tasks"].pop()
        del mapping["tasks"]["MC-998"]

        # Two distinct tasks mapped to one issue would overwrite each other's
        # reconciliations even if both have valid stable markers.
        issues[0]={"number":991,"title":"Old title",
                   "body":stale+"\n<!-- MC:TASK:MC-998 -->\n"+managed(task2)}
        graph["tasks"].append(task2)
        mapping["tasks"]["MC-998"]={"issue":991}
        calls.clear()
        assert sync(True)==3 and not calls, "duplicate binding overwrote a prior task update"
        graph["tasks"].pop()
        del mapping["tasks"]["MC-998"]
        issues[0]={"number":991,"title":"Old title","body":stale}

        # An intervening human edit must abort before the first PATCH.
        def changed_preflight(method,path,body=None):
            result=fake_gh(method,path,body)
            return dict(result,body="human edit") if method=="GET" else result
        with patch(__name__+".gh",side_effect=changed_preflight):
            calls.clear()
            assert sync(True)==4 and calls==[("GET",991)], "stale plan overwrote a concurrent edit"

        # A successful preflight does not excuse an incorrect post-write readback.
        reads=[0]
        def bad_readback(method,path,body=None):
            result=fake_gh(method,path,body)
            if method=="GET":
                reads[0]+=1
                if reads[0]==2: return dict(result,body="read-back corrupted")
            return result
        with patch(__name__+".gh",side_effect=bad_readback):
            calls.clear()
            assert sync(True)==4 and calls==[("GET",991),("PATCH",991),("GET",991)], (
                "post-write mismatch falsely reported success")
    self_test_verify()
    print("MC managed issue sync adversarial self-test passed")
    return 0
if __name__=="__main__":
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest="cmd",required=True)
    sp.add_parser("ready")
    v=sp.add_parser("verify"); v.add_argument("task")
    s=sp.add_parser("sync"); mx=s.add_mutually_exclusive_group(); mx.add_argument("--check",action="store_true"); mx.add_argument("--apply",action="store_true")
    sp.add_parser("self-test")
    a=ap.parse_args()
    raise SystemExit(ready() if a.cmd=="ready" else verify(a.task) if a.cmd=="verify" else self_test() if a.cmd=="self-test" else sync(a.apply))
