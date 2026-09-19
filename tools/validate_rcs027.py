#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
errors=[]

def fail(msg): errors.append(msg)
def load(rel):
    p=ROOT/rel
    try: return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e: fail(f"{rel}: {e}"); return {}

REQUIRED_DOCS=[f"docs/{n}" for n in [
"26-INTEGRATED-SEMANTIC-CONTRACT-VERTICAL-SLICE.md",
"27-CANONICALIZER-CONFORMANCE.md","28-REALISTIC-LATHE-TOOL-ENVELOPE-RESEARCH.md",
"29-MANUAL-FREEHAND-MILL-ORACLE-FALLBACK-RESEARCH.md",
"30-STEP-LAYER-D-INTEROPERABILITY-QUALIFICATION.md",
"31-PROPAGATED-UNCERTAINTY-ERROR-BUDGET-ALGEBRA.md",
"32-OCCT-CURRENT-DIFFERENTIAL.md","33-PROVIDER-HANDOFF-RECONCILIATION-STRESS.md",
"34-WINDOWS-LINUX-SCALE-SOAK-FAULT-RECOVERY.md","35-GENESIS-V2-SYNTHESIS-AND-GATE5.md"]]
OM_FILES=["README.md","00-FOUNDING-SPEC.md","01-IMPLEMENTATION-ROADMAP.md","02-INITIAL-ISSUE-GRAPH.md",
"03-UNRESOLVED-RESEARCH-REGISTER.md","04-CLEAN-REPO-BOOTSTRAP-CHECKLIST.md","handoff-v2.json"]
MS_FILES=["README.md","00-FOUNDING-SPEC.md","01-IMPLEMENTATION-ROADMAP.md","02-INITIAL-ISSUE-GRAPH.md",
"03-INTEGRATION-ESCAPE-ROUTES.md","04-CLEAN-REPO-BOOTSTRAP-CHECKLIST.md","handoff-v2.json"]

def static():
    for rel in REQUIRED_DOCS:
        if not (ROOT/rel).is_file(): fail(f"missing {rel}")
    for f in OM_FILES:
        if not (ROOT/"handoffs/v2/opensimachinist"/f).is_file(): fail(f"missing OpenSimachinist v2 {f}")
    for f in MS_FILES:
        if not (ROOT/"handoffs/v2/msac"/f).is_file(): fail(f"missing MSAC v2 {f}")
    for rel in ["handoffs/genesis-release-v1.json","handoffs/genesis-release-v2.json",
                "research/rcs-027/evidence-matrix-v1.json","research/rcs-027/decision-delta-v1.json",
                "research/rcs-027/windows-step-qualification-v1.json"]:
        if not (ROOT/rel).is_file(): fail(f"missing {rel}")

    # V1 freeze identity must not be reinterpreted.
    v1=load("handoffs/genesis-release-v1.json")
    if v1.get("packages",{}).get("opensimachinist",{}).get("package_tree_sha")!="d4793b03f31bd9fd58efcea94afba2f69fa3f7f3":
        fail("Genesis-v1 OpenSimachinist tree identity changed")
    if v1.get("packages",{}).get("msac",{}).get("package_tree_sha")!="e04d53756dd83089d367d756253482bebe791f32":
        fail("Genesis-v1 MSAC tree identity changed")

    ev=load("research/rcs-027/evidence-matrix-v1.json")
    ids=[x.get("id") for x in ev.get("items",[])]
    if ids != [f"RCS-{i:03d}" for i in range(18,27)]:
        fail(f"evidence matrix must contain RCS-018..RCS-026 exactly, got {ids}")
    r22=next((x for x in ev.get("items",[]) if x.get("id")=="RCS-022"),{})
    if r22.get("qualification_status")!="interoperability_unqualified":
        fail("RCS-022 Layer-D truth was weakened")
    delta=load("research/rcs-027/decision-delta-v1.json")
    decisions=[x.get("decision") for x in delta.get("decisions",[])]
    required=[f"DR-{i:04d}" for i in range(1,24)]
    if decisions != required: fail("decision delta must classify DR-0001..DR-0023 exactly")
    protected=set(delta.get("protected_semantics",[]))
    for x in ["source/audio identity","provenance","durable material-body identity and explicit transitions"]:
        if x not in protected: fail(f"missing protected semantic: {x}")

    rel=load("handoffs/genesis-release-v2.json")
    if rel.get("schema")!="radicadsac-genesis-freeze/2.0": fail("unexpected v2 release schema")
    if rel.get("production_repository_creation_authorized") is not False: fail("RCS-027 must not authorize production repo creation")
    if rel.get("shared_contracts",{}).get("journal_schema")!="msac-journal/1.0": fail("journal schema drift")
    if rel.get("shared_contracts",{}).get("step_layer_d_status")!="interoperability_unqualified": fail("STEP status drift")
    if rel.get("shared_contracts",{}).get("occt_version")!="8.0.1": fail("OCCT baseline drift")
    tags=rel.get("tag_plan",{}).get("names",[])
    if tags!=["radiCADSAC-genesis-v2","opensimachinist-handoff-v2","msac-handoff-v2"]: fail("tag plan drift")

    # Both handoffs must agree on critical shared contract values.
    om=load("handoffs/v2/opensimachinist/handoff-v2.json")
    ms=load("handoffs/v2/msac/handoff-v2.json")
    for key in ["journal_schema","backend_architecture","step_profile","step_layer_d_status","occt_version"]:
        if om.get("shared_contracts",{}).get(key)!=ms.get("shared_contracts",{}).get(key):
            fail(f"handoff shared contract mismatch: {key}")
    for doc in [ROOT/"handoffs/v2/opensimachinist/00-FOUNDING-SPEC.md",ROOT/"handoffs/v2/msac/00-FOUNDING-SPEC.md"]:
        text=doc.read_text(encoding="utf-8")
        for phrase in ["source/audio identity","interoperability_unqualified","accepted_pending","all committed material bodies"]:
            if phrase not in text: fail(f"{doc.relative_to(ROOT)} missing protected phrase {phrase!r}")

    # Every issue graph must contain autonomous lifecycle and source references.
    for relp in ["handoffs/v2/opensimachinist/02-INITIAL-ISSUE-GRAPH.md","handoffs/v2/msac/02-INITIAL-ISSUE-GRAPH.md"]:
        t=(ROOT/relp).read_text(encoding="utf-8")
        for phrase in ["dedicated branch","open a PR","automated checks","verify the merge landed on `main`"]:
            if phrase not in t: fail(f"{relp} missing autonomous lifecycle phrase {phrase!r}")
        if len(re.findall(r"^## [A-Z]+-\d{3}",t,flags=re.M))<6: fail(f"{relp} needs at least six concrete bootstrap issues")

    wr=load("research/rcs-027/windows-step-qualification-v1.json")
    if wr.get("status")=="accepted":
        if not wr.get("gate5_closure"): fail("accepted Windows evidence must close Gate5 blocker")
        if wr.get("qualification_status")!="interoperability_unqualified": fail("accepted Windows evidence must preserve Layer-D negative truth")
        if wr.get("occt_commit")!="b8f597c677811d1f9f4d8a97f5ae2825c0353a42": fail("Windows evidence OCCT pin drift")
        if wr.get("live_repetitions")!=3: fail("Windows evidence requires exactly 3 repetitions")
        if wr.get("negative_controls_passed")!=7: fail("Windows evidence requires 7 adversarial controls")
        if ev.get("gate5_status")!="accepted": fail("accepted Windows evidence requires accepted evidence matrix")
        if rel.get("gate5_status")!="accepted": fail("accepted Windows evidence requires accepted release")
    elif wr.get("status")!="pending_ci":
        fail("Windows STEP result must be pending_ci or accepted")

def validate_live(path: Path):
    try: d=json.loads(path.read_text(encoding="utf-8"))
    except Exception as e: fail(f"live Windows result: {e}"); return
    if d.get("schema")!="rcs-027-windows-step-live/1.0": fail("bad live Windows schema")
    if d.get("status")!="pass" or d.get("gate5_windows_step_blocker")!="cleared": fail("live Windows STEP did not clear blocker")
    if d.get("occt_commit")!="b8f597c677811d1f9f4d8a97f5ae2825c0353a42": fail("live Windows OCCT pin mismatch")
    if d.get("live_repetitions")!=3: fail("live Windows repetitions != 3")
    if d.get("qualification_status")!="interoperability_unqualified": fail("live Windows Layer-D truth changed")
    if d.get("positive_case_count")!=11 or d.get("negative_controls_passed")!=7: fail("live Windows fixture cardinality mismatch")
    tc=d.get("toolchain",{})
    if tc.get("compiler_id")!="MSVC" or int(tc.get("compiler_version_numeric",-1))!=1951: fail("live Windows MSVC pin mismatch")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--windows-live",type=Path)
    a=ap.parse_args()
    static()
    if a.windows_live: validate_live(a.windows_live)
    if errors:
        print("\n".join("ERROR: "+x for x in errors),file=sys.stderr); return 1
    print("RCS-027 validation passed")
    return 0
if __name__=="__main__": raise SystemExit(main())
