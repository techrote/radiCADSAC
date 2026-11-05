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
    # Only None requests a disk load: explicit empty registries are invalid.
    graph=load(MC/"task-graph-v1.json") if graph is None else graph
    programme=load(MC/"programme-v1.json") if programme is None else programme
    outcomes=load(MC/"outcomes-v1.json") if outcomes is None else outcomes
    ghmap=load(MC/"github-map-v1.json") if ghmap is None else ghmap
    posdoc=load(MC/"proof-obligations-v1.json") if posdoc is None else posdoc
    for name, value, keys in (
        ("task graph", graph, ("tasks", "packages")),
        ("programme", programme, ("gates",)),
        ("outcomes", outcomes, ("tasks",)),
        ("GitHub map", ghmap, ("tasks",)),
        ("proof obligations", posdoc, ("obligations",)),
    ):
        if not isinstance(value, dict) or any(key not in value for key in keys):
            fail(f"{name} registry malformed")
    # Check nested JSON shapes before IDs, dependencies or registry rows are
    # dereferenced. Malformed supplied evidence must be a controlled refusal,
    # not an uncontrolled Python exception or an implicit default.
    if (not isinstance(graph["tasks"],list)
            or any(not isinstance(t,dict) or not isinstance(t.get("id"),str)
                   for t in graph["tasks"])):
        fail("task inventory malformed")
    if (not isinstance(graph["packages"],list)
            or any(not isinstance(p,dict) or not isinstance(p.get("id"),str)
                   or not isinstance(p.get("tasks"),list)
                   or any(not isinstance(i,str) for i in p["tasks"])
                   for p in graph["packages"])):
        fail("package inventory malformed")
    if (not isinstance(outcomes["tasks"],dict)
            or any(not isinstance(v,dict) for v in outcomes["tasks"].values())
            or not isinstance(ghmap["tasks"],dict)
            or any(not isinstance(v,dict) for v in ghmap["tasks"].values())):
        fail("task outcome/GitHub registry malformed")
    if (not isinstance(posdoc["obligations"],list)
            or any(not isinstance(v,dict) or not isinstance(v.get("id"),str)
                   for v in posdoc["obligations"])):
        fail("proof obligation inventory malformed")
    tasks=graph["tasks"]; ids=[t["id"] for t in tasks]; idset=set(ids)
    expected={f"MC-{i:03d}" for i in range(1,59)}
    if len(tasks)!=58 or idset!=expected or len(ids)!=len(idset): fail("MC task ID/count mismatch")
    for t in tasks:
        if (not isinstance(t.get("dependencies"),list)
                or any(not isinstance(d,dict) or not isinstance(d.get("task"),str)
                       or not isinstance(d.get("type"),str)
                       for d in t["dependencies"])):
            fail(f"{t['id']} dependencies malformed")
        for k in ("package","title","objective","scope","non_goals","acceptance","verification","artifacts","blockers","locks"):
            if k not in t: fail(f"{t['id']} missing {k}")
        # Each executable task contract is a list of nonempty strings; locks may
        # be empty but cannot be replaced by a truthy scalar or mapping.
        for k in ("acceptance","verification","artifacts","locks"):
            entries=t[k]
            if (not isinstance(entries,list)
                    or any(not isinstance(entry,str) or not entry.strip()
                           for entry in entries)):
                fail(f"{t['id']} malformed {k}")
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
    # MC-038 pre-gate repair: producing MG-07 tasks must not depend on the gate they help establish.
    tmap={t["id"]:t for t in tasks}
    for tid in ("MC-031","MC-032","MC-033"):
        deps={(d["task"],d["type"]) for d in tmap[tid]["dependencies"]}
        if ("MC-038","capability") in deps: fail(f"{tid} reintroduced circular MC-038 capability dependency")
        if ("MC-005","capability") not in deps: fail(f"{tid} missing accepted MC-A pre-gate authority")
    for tid in ("MC-034","MC-035","MC-036","MC-037"):
        deps={(d["task"],d["type"]) for d in tmap[tid]["dependencies"]}
        if ("MC-038","capability") not in deps: fail(f"{tid} lost legitimate post-gate MC-038 dependency")

    pids=[p["id"] for p in graph["packages"]]
    if pids!=[f"MG-{i:02d}" for i in range(14)]: fail("package hierarchy mismatch")
    members=[x for p in graph["packages"] for x in p["tasks"]]
    if sorted(members)!=sorted(ids) or len(members)!=len(set(members)): fail("package membership mismatch")
    # A task's self-declared package must agree with its unique package owner.
    # Otherwise a corrupt nested task record could pass the package membership
    # check while claiming a different recognized MG package.
    for package in graph["packages"]:
        for task_id in package["tasks"]:
            if tmap[task_id].get("package") != package["id"]:
                fail(f"{task_id} task package binding mismatch")

    gate_owners={"MC-A":"MC-005","MC-B":"MC-038","MC-C":"MC-016","MC-D":"MC-041","MC-E":"MC-044","MC-F":"MC-048","MC-1":"MC-052"}
    gate_states={"MC-A":"ACCEPTED","MC-B":"NOT_ESTABLISHED","MC-C":"NOT_ESTABLISHED","MC-D":"NOT_ESTABLISHED","MC-E":"NOT_ESTABLISHED","MC-F":"NOT_ESTABLISHED","MC-1":"NOT_ESTABLISHED"}
    listed_gates=programme["gates"]
    if (not isinstance(listed_gates,list) or len(listed_gates)!=len(gate_owners)
            or any(not isinstance(g,dict) or not isinstance(g.get("id"),str)
                   for g in listed_gates)):
        fail("gate inventory malformed")
    gates={g["id"]:g for g in listed_gates}
    if len(gates)!=len(listed_gates) or set(gates)!=set(gate_owners):
        fail("gate inventory mismatch")
    for g,o in gate_owners.items():
        if gates.get(g,{}).get("owner")!=o or gates[g].get("state")!=gate_states[g]: fail(f"{g} current state/owner mismatch")
    if programme.get("capability_status")!="NOT_ESTABLISHED": fail("MC-1 capability advanced before final gate")
    if programme.get("production_authorized") is not False or programme.get("expensive_execution_authorized") is not False: fail("MC-A must not authorize production/native spend")

    if set(outcomes["tasks"])!=idset or set(ghmap["tasks"])!=idset: fail("task registry set mismatch")
    if outcomes["tasks"]["MC-005"].get("state")!="CAPABILITY_ACCEPTED": fail("MC-005 outcome registry mismatch")
    if outcomes["tasks"]["MC-005"].get("blockers")!=[]: fail("accepted MC-005 may not retain blockers")
    nums=[]
    for i in ids:
        n=ghmap["tasks"][i].get("issue")
        if type(n) is not int or n<=0: fail(f"{i} missing issue")
        # The outcomes and GitHub routing ledgers must identify the *same*
        # task-specific issue. Validating each register in isolation would
        # admit a stale or silently misdirected acceptance record.
        row=outcomes["tasks"][i]
        if type(row.get("issue")) is not int or row["issue"]!=n:
            fail(f"{i} outcome/GitHub issue binding mismatch")
        if row.get("state") not in {
            "NOT_STARTED","COMPLETED_RESEARCH","NEGATIVE_RESULT","CAPABILITY_ACCEPTED"
        }:
            fail(f"{i} unknown outcome state")
        # A task-local outcome must not unilaterally grant a capability while
        # the programme and proof gates still say NOT_ESTABLISHED.
        if row["state"]=="CAPABILITY_ACCEPTED" and i!="MC-005":
            fail(f"{i} capability acceptance contradicts current programme gates")
        if (not isinstance(row.get("accepted_artifacts"),list)
                or any(not isinstance(p,str) or not p.strip()
                       for p in row["accepted_artifacts"])
                or not isinstance(row.get("blockers"),list)
                or any(not isinstance(b,dict) for b in row["blockers"])):
            fail(f"{i} outcome evidence/blocker fields malformed")
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
    bad=copy.deepcopy(g); tm={t["id"]:t for t in bad["tasks"]}; tm["MC-031"]["dependencies"][0]={"task":"MC-038","type":"capability"}
    try: validate(bad,p,o,m,pos)
    except AssertionError: pass
    else: fail("self-test failed to reject reintroduced MC-038 pre-gate cycle")
    bad=copy.deepcopy(g); tm={t["id"]:t for t in bad["tasks"]}; tm["MC-034"]["dependencies"]=[d for d in tm["MC-034"]["dependencies"] if d!={"task":"MC-038","type":"capability"}]
    try: validate(bad,p,o,m,pos)
    except AssertionError: pass
    else: fail("self-test failed to reject removed post-gate MC-038 dependency")
    # Adversarial contract probes: malformed inputs must not be substituted,
    # silently shadow a gate, or masquerade as validated authority.
    try: validate({},p,o,m,pos)
    except AssertionError: pass
    else: fail("self-test accepted explicitly empty injected graph")
    for change, label in (
        (lambda x: x["gates"].append(copy.deepcopy(x["gates"][0])), "duplicate gate"),
        (lambda x: x["gates"][-1].__setitem__("id","MC-Z"), "unknown gate"),
        (lambda x: x.__setitem__("production_authorized",0), "non-boolean production permission"),
        (lambda x: x.__setitem__("expensive_execution_authorized",0), "non-boolean native permission"),
    ):
        badp=copy.deepcopy(p); change(badp)
        try: validate(g,badp,o,m,pos)
        except AssertionError: pass
        else: fail(f"self-test accepted {label}")
    badm=copy.deepcopy(m); badm["tasks"]["MC-001"]["issue"]=True
    try: validate(g,p,o,badm,pos)
    except AssertionError: pass
    else: fail("self-test accepted boolean GitHub issue number")
    # Adversarial cross-register custody: valid-looking individual ledgers
    # must fail if their shared issue key drifts or gate acceptance is forged.
    for change, label in (
        (lambda x: x["tasks"]["MC-038"].__setitem__("issue",101), "misrouted issue"),
        (lambda x: x["tasks"]["MC-038"].__setitem__("issue",True), "boolean outcome issue"),
        (lambda x: x["tasks"]["MC-038"].__setitem__("state","CAPABILITY_ACCEPTED"), "premature MC-B outcome"),
        (lambda x: x["tasks"]["MC-052"].__setitem__("state","CAPABILITY_ACCEPTED"), "premature MC-1 outcome"),
        (lambda x: x["tasks"]["MC-038"].__setitem__("state","CLOSED"), "unknown outcome state"),
        (lambda x: x["tasks"]["MC-038"].__setitem__("accepted_artifacts",None), "null accepted artifacts"),
        (lambda x: x["tasks"]["MC-038"].__setitem__("blockers",None), "null blockers"),
    ):
        bado=copy.deepcopy(o); change(bado)
        try: validate(g,p,bado,m,pos)
        except AssertionError: pass
        else: fail(f"self-test accepted {label}")
    # These mutations previously raised TypeError/KeyError/AttributeError
    # before reaching a conservative registry refusal.
    for target, change, label in (
        (0, lambda x: x.__setitem__("tasks",None), "null task inventory"),
        (0, lambda x: x["tasks"].__setitem__(0,None), "null task record"),
        (0, lambda x: x["tasks"][0].__setitem__("id",[]), "unhashable task ID"),
        (0, lambda x: x["tasks"][0].__setitem__("dependencies",None), "null dependencies"),
        (0, lambda x: x["tasks"][0].pop("dependencies"), "missing dependencies"),
        (0, lambda x: x["tasks"][0].__setitem__("package","MG-13"), "cross-package task declaration"),
        (0, lambda x: x["tasks"][0].__setitem__("acceptance",True), "boolean acceptance contract"),
        (0, lambda x: x["tasks"][0].__setitem__("verification","not a list"), "scalar verification contract"),
        (0, lambda x: x["tasks"][0].__setitem__("artifacts",{"item":1}), "mapping artifacts contract"),
        (0, lambda x: x["tasks"][0].__setitem__("locks",{"programme-registry":True}), "mapping locks"),
        (0, lambda x: x["tasks"][0]["acceptance"].__setitem__(0,None), "null acceptance entry"),
        (0, lambda x: x["tasks"][0].__setitem__("locks",[None]), "null lock entry"),
        (0, lambda x: x["tasks"][0].__setitem__("artifacts",["  "]), "blank artifact entry"),
        (0, lambda x: next(t for t in x["tasks"] if t["dependencies"])["dependencies"].__setitem__(0,None), "null dependency"),
        (0, lambda x: x.__setitem__("packages",None), "null package inventory"),
        (0, lambda x: x["packages"].__setitem__(0,None), "null package record"),
        (0, lambda x: x["packages"][0].__setitem__("tasks",None), "null package membership"),
        (0, lambda x: x["packages"][0]["tasks"].__setitem__(0,{}), "unhashable package member"),
        (2, lambda x: x.__setitem__("tasks",None), "null outcome registry"),
        (2, lambda x: x["tasks"].__setitem__("MC-005",None), "null outcome row"),
        (3, lambda x: x.__setitem__("tasks",None), "null GitHub registry"),
        (3, lambda x: x["tasks"].__setitem__("MC-001",None), "null GitHub row"),
        (4, lambda x: x.__setitem__("obligations",None), "null obligation inventory"),
        (4, lambda x: x["obligations"].__setitem__(0,None), "null obligation row"),
    ):
        inputs=[copy.deepcopy(g),copy.deepcopy(p),copy.deepcopy(o),copy.deepcopy(m),copy.deepcopy(pos)]
        change(inputs[target])
        try: validate(*inputs)
        except AssertionError: pass
        except (TypeError,KeyError,AttributeError,ValueError) as exc:
            fail(f"self-test {label} raised uncontrolled {type(exc).__name__}: {exc}")
        else: fail(f"self-test accepted {label}")
    print("MC-1 validator self-test passed")
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--self-test",action="store_true"); a=ap.parse_args()
    validate()
    self_test() if a.self_test else print("MC-1 static validation passed")
