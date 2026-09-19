#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE="a68fa92d1128a163b232e2be69d6f731bd56caa5"
errors=[]

def fail(msg): errors.append(msg)
def load(rel):
    try: return json.loads((ROOT/rel).read_text(encoding="utf-8"))
    except Exception as exc: fail(f"{rel}: {exc}"); return {}
def read(rel): return (ROOT/rel).read_text(encoding="utf-8")

def status_errors(rel, om, ms):
    out=[]
    if rel.get("gate5_status")!="accepted": out.append("release Gate5 must remain accepted")
    if rel.get("consistency_revision")!="2.1": out.append("release consistency_revision must be 2.1")
    for name,obj in [("opensimachinist",om),("msac",ms)]:
        if obj.get("consistency_revision")!="2.1": out.append(f"{name} consistency revision drift")
        if obj.get("status")!="gate5_foundation_qualified_bootstrap_consistent": out.append(f"{name} stale/inconsistent status")
        c=obj.get("correction_of",{})
        if c.get("original_status")!="candidate_gate5_pending_windows_step": out.append(f"{name} original status provenance missing")
    return out

def dependency_errors(man, *, resolve=True):
    out=[]
    if man.get("schema")!="radicadsac-bootstrap-evidence-dependencies/2.1": out.append("dependency manifest schema drift")
    if man.get("source_commit")!=BASE: out.append("dependency source commit drift")
    allowed={"SOURCE","INFERENCE","MEASURED_NATIVE_GEOMETRY","MEASURED_INDEPENDENT_ORACLE","MEASURED_DETERMINISTIC_MODEL","MEASURED_PLATFORM_PROCESS"}
    if len(man.get("items",[]))<10: out.append("dependency manifest too small")
    for item in man.get("items",[]):
        path=item.get("path"); claimed=item.get("blob_sha"); classes=set(item.get("claim_class",[]))
        if not path or not claimed: out.append("dependency missing path/blob_sha"); continue
        if not classes or not classes <= allowed: out.append(f"{path}: invalid claim class {classes}")
        if resolve:
            try:
                actual=subprocess.check_output(["git","rev-parse",f"{BASE}:{path}"],cwd=ROOT,text=True).strip()
            except Exception as exc:
                out.append(f"{path}: cannot resolve pinned blob: {exc}"); continue
            if actual!=claimed: out.append(f"{path}: blob mismatch {claimed} != {actual}")
    return out

def static():
    rel=load("handoffs/genesis-release-v2.json")
    om=load("handoffs/v2/opensimachinist/handoff-v2.json")
    ms=load("handoffs/v2/msac/handoff-v2.json")
    for e in status_errors(rel,om,ms): fail(e)

    corr=rel.get("consistency_correction",{})
    if corr.get("original_release_manifest_blob_sha")!="c47beb993a3cd64f28fd35c1d47f1a3630cef92c": fail("original release manifest blob provenance missing")
    pk=corr.get("original_package_tree_shas",{})
    if pk.get("opensimachinist")!="b93e6e7ca28d26753e735f8ffe4acc56c5821676": fail("original OpenSimachinist tree provenance missing")
    if pk.get("msac")!="a38d265aae2fda8e35dcf58e7d127d459e74055a": fail("original MSAC tree provenance missing")

    if rel.get("self_contained") is not False: fail("corrected handoff must not claim standalone self-containment")
    if rel.get("evidence_dependency_manifest")!="handoffs/evidence-dependencies-v2.1.json": fail("release does not route exact evidence manifest")
    deps=load("handoffs/evidence-dependencies-v2.1.json")
    for e in dependency_errors(deps): fail(e)
    dep_paths={x.get("path") for x in deps.get("items",[])}
    for required in ["docs/10-CANONICAL-JOURNAL-CONTRACT.md","docs/13-STEP-CONFORMANCE-CONTRACT.md",
                     "research/rcs-019/vectors-v1.json","research/rcs-022/frozen-result-v1.json",
                     "research/rcs-025/reference-results-v1.json","research/rcs-027/windows-step-qualification-v1.json"]:
        if required not in dep_paths: fail(f"exact dependency manifest missing {required}")
    for obj,name in [(om,"opensimachinist"),(ms,"msac")]:
        if obj.get("evidence_dependency_manifest")!="handoffs/evidence-dependencies-v2.1.json": fail(f"{name} does not route exact evidence dependencies")

    for name,path in [("opensimachinist","handoffs/v2/opensimachinist"),("msac","handoffs/v2/msac")]:
        actual=subprocess.check_output(["git","rev-parse",f"HEAD:{path}"],cwd=ROOT,text=True).strip()
        if rel.get("packages",{}).get(name,{}).get("package_tree_sha")!=actual: fail(f"{name} corrected package tree mismatch")

    readme=read("README.md"); agents=read("AGENTS.md"); hidx=read("handoffs/README.md")
    for phrase in ["Genesis v2 is the current bootstrap authority","evidence-dependencies-v2.1.json"]:
        if phrase not in readme: fail(f"README missing current-route phrase {phrase!r}")
    if "The **current** production bootstrap outputs" not in agents: fail("AGENTS current routing missing")
    if "v1 packages" not in agents: fail("AGENTS historical v1 routing missing")
    if "Current bootstrap route" not in hidx or "Genesis-v1 historical freeze" not in hidx: fail("handoff index routing missing")

    if "pending PR merge" in read("docs/27-CANONICALIZER-CONFORMANCE.md"): fail("stale RCS-019 pending-merge status remains")

    for relp in ["docs/08-TERMINOLOGY.md","docs/10-CANONICAL-JOURNAL-CONTRACT.md",
                 "handoffs/v2/opensimachinist/00-FOUNDING-SPEC.md","handoffs/v2/msac/00-FOUNDING-SPEC.md"]:
        t=read(relp)
        for phrase in ["pending-intent transaction","last committed"]:
            if phrase not in t: fail(f"{relp}: pending durability phrase missing {phrase!r}")
    jt=read("docs/10-CANONICAL-JOURNAL-CONTRACT.md")
    for phrase in ["not yet a committed workpiece revision","provider-private state","save, crash"]:
        if phrase not in jt: fail(f"journal pending boundary missing {phrase!r}")

    term=read("docs/08-TERMINOLOGY.md")
    for phrase in ["closures of connected components of the material interior","Point- or edge-only contact","do **not** silently merge"]:
        if phrase not in term: fail(f"connectivity terminology missing {phrase!r}")

    method=read("docs/06-RESEARCH-METHOD.md")
    for cls in ["MEASURED_NATIVE_GEOMETRY","MEASURED_INDEPENDENT_ORACLE","MEASURED_DETERMINISTIC_MODEL","MEASURED_PLATFORM_PROCESS"]:
        if cls not in method: fail(f"research method missing {cls}")
    if "does **not** execute a new native geometry reconstruction" not in read("docs/33-PROVIDER-HANDOFF-RECONCILIATION-STRESS.md"): fail("RCS-025 model/native boundary missing")
    if "do not execute 100,000 native OCCT material-changing geometry operations" not in read("docs/34-WINDOWS-LINUX-SCALE-SOAK-FAULT-RECOVERY.md"): fail("RCS-026 scale scope boundary missing")
    if "Gate 5 accepts the **foundation and bounded/refusal policies**" not in read("docs/35-GENESIS-V2-SYNTHESIS-AND-GATE5.md"): fail("Gate5 claim boundary missing")

def adversarial():
    rel={"gate5_status":"accepted","consistency_revision":"2.1"}
    good={"consistency_revision":"2.1","status":"gate5_foundation_qualified_bootstrap_consistent",
          "correction_of":{"original_status":"candidate_gate5_pending_windows_step"}}
    bad=copy.deepcopy(good); bad["status"]="candidate_gate5_pending_windows_step"
    if not status_errors(rel,bad,good): fail("adversarial stale package status was accepted")
    badrel=copy.deepcopy(rel); badrel["gate5_status"]="pending"
    if not status_errors(badrel,good,good): fail("adversarial Gate5 downgrade was accepted")

    dep={"schema":"radicadsac-bootstrap-evidence-dependencies/2.1","source_commit":BASE,
         "items":[{"path":"research/rcs-019/vectors-v1.json","blob_sha":"0"*40,
                   "claim_class":["MEASURED_DETERMINISTIC_MODEL"],"required_by":["OSM-002"]} for _ in range(10)]}
    errs=dependency_errors(dep,resolve=True)
    if not any("blob mismatch" in e for e in errs): fail("adversarial evidence blob drift was accepted")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--adversarial-self-test",action="store_true"); args=ap.parse_args()
    static()
    if args.adversarial_self_test: adversarial()
    if errors:
        print("\n".join("ERROR: "+e for e in errors),file=sys.stderr); return 1
    print("Genesis-v2 bootstrap consistency validation passed")
    return 0
if __name__=="__main__": raise SystemExit(main())
