#!/usr/bin/env python3
"""Validate RCS-021 manual/freehand milling research and measured results."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"research/rcs-021"
PLAN=BASE/"experiment-plan-v1.json"
FILES=[BASE/"field.py",BASE/"material_oracle.py",BASE/"tridexel.py",BASE/"manifold_fallback.py",BASE/"run_campaign.py"]
README=BASE/"README.md"
REPORT=ROOT/"docs/29-MANUAL-FREEHAND-MILL-ORACLE-FALLBACK-RESEARCH.md"
DECISION=ROOT/"docs/decisions/DR-0018-manual-freehand-mill-bounded-directional-fallback.md"
errors:list[str]=[]

def fail(msg:str)->None: errors.append(msg)
def require(cond:bool,msg:str)->None:
    if not cond: fail(msg)
def load(path:Path)->Any:
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc:
        fail(f"{path.relative_to(ROOT)}: cannot parse JSON: {exc}"); return None

def validate_static()->dict[str,Any]|None:
    for path in [PLAN,*FILES,README,REPORT,DECISION]: require(path.exists(),f"missing RCS-021 file: {path.relative_to(ROOT)}")
    plan=load(PLAN)
    if not isinstance(plan,dict): return None
    require(plan.get("schema")=="rcs-021-manual-mill-plan/1.0","unexpected RCS-021 plan schema")
    require(plan.get("issue")=="RCS-021" and plan.get("issue_number")==40,"plan must identify RCS-021/#40")
    base=plan.get("baseline",{})
    require(base.get("units")=="mm" and "z-up" in str(base.get("frame","")),"explicit millimetre/Z-up baseline required")
    occt=base.get("rcs011_occt",{})
    require(occt.get("version")=="8.0.1" and occt.get("commit")=="b8f597c677811d1f9f4d8a97f5ae2825c0353a42","RCS-011 OCCT control pin drifted")
    ext=base.get("external",{})
    require(ext.get("name")=="Manifold" and ext.get("version")=="3.5.3","Manifold 3.5.3 pin required")
    require(ext.get("commit")=="0edd9d54876f3135e431575214dd6d8a72866fee","Manifold source commit pin drifted")
    require(ext.get("license")=="Apache-2.0","Manifold license must be recorded")
    require(len(plan.get("sources",[]))>=6,"RCS-021 requires primary/programme evidence sources")
    require(len(plan.get("hypotheses",[]))>=5,"RCS-021 requires falsifiable hypotheses")
    require(all(isinstance(h,dict) and h.get("statement") and h.get("falsified_by") for h in plan.get("hypotheses",[])),"every hypothesis needs falsification criteria")
    policies=plan.get("policies",{})
    for key in ("oracle_max_depth_ci","oracle_field_numeric_error_mm","tridexel_pitch_ci_mm","manifold_edge_length_mm","manifold_root_tolerance_mm","qualification_max_volume_interval_mm3","qualification_max_spatial_support_radius_mm"):
        require(isinstance(policies.get(key),(int,float)) and float(policies[key])>0.0,f"missing/invalid positive RCS-021 policy {key}")
    require("never snapped to zero" in str(policies.get("sub_tolerance_policy","")),"sub-tolerance policy must forbid silent erasure")
    require("before-STEP" in str(policies.get("step_reconciliation","")),"fallback state must reconcile before STEP")
    cases=plan.get("cases",[])
    require(isinstance(cases,list) and len(cases)>=14,"RCS-021 requires at least fourteen bounded fixtures")
    if not isinstance(cases,list): return plan
    ids={c.get("id") for c in cases if isinstance(c,dict)}
    required={"closed-form-stationary-flat","closed-form-horizontal-slot","self-cross","retrace-exact","retrace-jitter","simultaneous-xyz","ball-rounded","tangent-zero","tangent-overlap","plunge-1um","overlapping-paths","cut-through","high-segment-freehand","stationary-near"}
    require(required.issubset(ids),"RCS-021 pathological fixture coverage drifted")
    by_id={c["id"]:c for c in cases if isinstance(c,dict) and "id" in c}
    require(by_id.get("cut-through",{}).get("expected_body_count")==2,"cut-through must require two material bodies")
    require(float(by_id.get("plunge-1um",{}).get("minimum_positive_feature_mm",0.0))==1e-6,"1 um positive-removal witness required")
    high=by_id.get("high-segment-freehand",{}).get("generated_path",{})
    require(int(high.get("segments",0))>50,"high-segment fixture must exceed RCS-011 smoke")
    require(len(plan.get("rcs011_controls",[]))>=2,"RCS-011 valid-wrong and sampled-timeout revisits required")
    for path in FILES:
        if path.exists(): compile(path.read_text(encoding="utf-8"),str(path),"exec")
    marker_sets={
        BASE/"field.py":("flat_segment_field","rounded_segment_field","removal_field","column_height","known_volume"),
        BASE/"material_oracle.py":("conservative-lipschitz-octree","material_volume_lower_mm3","closed_form_validation"),
        BASE/"tridexel.py":("directional_interval_counts","volume_lower_mm3","engineering_signature","reconciliation_class"),
        BASE/"manifold_fallback.py":("PINNED_VERSION=\"3.5.3\"","Manifold.level_set","authoritative\":False"),
        BASE/"run_campaign.py":("rcs011_retrace_detected","accepted_pending_refinement","refused_unresolved_ambiguity","all_required_checks_pass"),
    }
    for path,markers in marker_sets.items():
        if path.exists():
            text=path.read_text(encoding="utf-8")
            for marker in markers: require(marker in text,f"{path.name} missing contract marker {marker!r}")
    for path,markers in ((README,("Independent oracle","Tri-dexel","Manifold","Reproduction")),(REPORT,("Hypotheses","Independent material oracle","RCS-011","sub-tolerance","STEP")),(DECISION,("## Context","## Decision","## Evidence","## Consequences","## Reversibility"))):
        if path.exists():
            text=path.read_text(encoding="utf-8")
            for marker in markers: require(marker in text,f"{path.name} missing marker {marker!r}")
    return plan

def validate_results(plan:dict[str,Any],results:Path)->None:
    payload=load(results/"campaign-results.json")
    if not isinstance(payload,dict): return
    require(payload.get("schema")=="rcs-021-campaign-results/1.0","unexpected RCS-021 campaign schema")
    require(payload.get("plan_schema")==plan.get("schema"),"RCS-021 plan/result schema mismatch")
    require(payload.get("case_count")>=14,"RCS-021 campaign must cover all pathological cases")
    require(payload.get("all_required_checks_pass") is True,"RCS-021 runtime required checks did not pass")
    require(payload.get("structural_failures")==[],"RCS-021 structural failures must be empty")
    checks=payload.get("required_checks",{})
    for key in ("closed_form_oracle_validation","tridexel_deterministic","sub_tolerance_positive_removal_preserved","cut_through_two_bodies_preserved","high_segment_fixture_exceeds_rcs011_smoke","external_candidate_executed","rcs011_retrace_independently_detected","rcs011_sampled_fallback_revisited"):
        require(checks.get(key) is True,f"RCS-021 required runtime check failed/missing: {key}")
    cases=payload.get("cases",[])
    require(isinstance(cases,list),"RCS-021 cases must be a list")
    if not isinstance(cases,list): return
    by_id={c.get("case_id"):c for c in cases if isinstance(c,dict)}
    for case in cases:
        if not isinstance(case,dict): continue
        cid=case.get("case_id","<unknown>")
        oracle=case.get("oracle",{})
        lo=oracle.get("material_volume_lower_mm3"); hi=oracle.get("material_volume_upper_mm3")
        require(isinstance(lo,(int,float)) and isinstance(hi,(int,float)) and 0.0<=float(lo)<=float(hi)<=12000.000001,f"{cid}: invalid independent material interval")
        require(float(oracle.get("boundary_spatial_half_diagonal_mm",-1.0))>=0.0,f"{cid}: missing independent spatial bound")
        if oracle.get("closed_form_validation") is not None:
            require(oracle["closed_form_validation"].get("contained_by_material_interval") is True,f"{cid}: closed-form oracle is outside independent interval")
        tri=case.get("tridexel",{})
        require(case.get("tridexel_repeatable") is True,f"{cid}: dexel result is nondeterministic")
        require(case.get("tridexel_oracle_intervals_overlap") is True,f"{cid}: dexel/oracle intervals do not overlap")
        require(tri.get("reconciliation_class")=="bounded_directional_material_state_requires_brep_before_step",f"{cid}: reconciliation class missing/drifted")
        require(int(tri.get("body_count",-1))==int(case.get("expected_body_count",-2)),f"{cid}: body count mismatch")
        ext=case.get("external")
        if ext is not None and ext.get("classification")!="external_candidate_error":
            require(ext.get("version")=="3.5.3",f"{cid}: external comparator version drifted")
            require(ext.get("authoritative") is False,f"{cid}: mesh comparator must remain non-authoritative")
    plunge=by_id.get("plunge-1um",{})
    require(plunge.get("positive_sub_tolerance_removal_preserved") is True,"1 um positive removal was silently erased")
    require(float(plunge.get("tridexel",{}).get("volume_estimate_mm3",12000.0))<12000.0,"1 um plunge estimate must remove positive material")
    cut=by_id.get("cut-through",{})
    require(cut.get("tridexel",{}).get("body_count")==2 and cut.get("oracle",{}).get("body_count_xy_grid")==2,"cut-through must preserve two material bodies")
    high=by_id.get("high-segment-freehand",{})
    require(int(high.get("segment_count",0))>50,"measured high-segment fixture must exceed RCS-011 smoke")
    revisit=payload.get("rcs011_revisit",[])
    if revisit:
        seq=next((r for r in revisit if r.get("case_id")=="retrace-jitter" and r.get("strategy")=="segment_sweep"),{})
        batch=next((r for r in revisit if r.get("case_id")=="retrace-jitter" and r.get("strategy")=="freehand_batch"),{})
        sample=next((r for r in revisit if r.get("case_id")=="slot-clean" and r.get("strategy")=="sampled_fallback"),{})
        require(seq.get("volume_inside_independent_oracle_interval") is True,"RCS-011 segment reference must agree with independent oracle")
        require(batch.get("valid_brep") is True and batch.get("volume_inside_independent_oracle_interval") is False,"RCS-011 valid-but-wrong retrace must be independently detected")
        require(sample.get("classification") in {"hang/timeout","success","algorithm_error"},"RCS-011 sampled fallback revisit missing bounded classification")

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--results-dir",type=Path); args=ap.parse_args()
    plan=validate_static()
    if plan is not None and args.results_dir: validate_results(plan,args.results_dir)
    if errors:
        print("RCS-021 validation failed:",file=sys.stderr)
        for e in errors: print(f"- {e}",file=sys.stderr)
        return 1
    print("RCS-021 validation passed")
    return 0
if __name__=="__main__": raise SystemExit(main())
