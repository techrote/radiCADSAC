#!/usr/bin/env python3
"""Run the RCS-021 manual/freehand material-oracle and fallback campaign."""
from __future__ import annotations

import argparse
import json
import math
import platform
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))

from field import STOCK, load_plan, profile_cases, segment_count
import material_oracle
import tridexel
import manifold_fallback

STOCK_VOLUME=STOCK[0]*STOCK[1]*STOCK[2]

def _dump(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

def _overlap(a0: float,a1: float,b0: float,b1: float) -> bool:
    return max(a0,b0) <= min(a1,b1) + 1e-9

def _run_rcs011(worker: Path, case_id: str, strategy: str, timeout_s: float) -> dict[str, Any]:
    started=time.perf_counter()
    cmd=[str(worker),"--case",case_id,"--strategy",strategy]
    try:
        cp=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=timeout_s,check=False)
    except subprocess.TimeoutExpired:
        return {"case_id":case_id,"strategy":strategy,"classification":"hang/timeout","timeout_s":timeout_s,"runtime_ms":(time.perf_counter()-started)*1000.0}
    lines=cp.stdout.strip().splitlines()
    if not lines:
        return {"case_id":case_id,"strategy":strategy,"classification":"worker_error","returncode":cp.returncode,"stderr":cp.stderr.strip(),"runtime_ms":(time.perf_counter()-started)*1000.0}
    try:
        payload=json.loads(lines[-1])
    except json.JSONDecodeError as exc:
        return {"case_id":case_id,"strategy":strategy,"classification":"worker_protocol_error","error":str(exc),"stdout":cp.stdout[-2000:],"runtime_ms":(time.perf_counter()-started)*1000.0}
    geom=payload.get("geometry",{}) if isinstance(payload,dict) else {}
    return {
        "case_id":case_id,
        "strategy":strategy,
        "classification":"success" if cp.returncode==0 and payload.get("success") else "algorithm_error",
        "returncode":cp.returncode,
        "volume_mm3":geom.get("volume_mm3"),
        "body_count":geom.get("topology",{}).get("solids"),
        "valid_brep":geom.get("valid_brep"),
        "material_booleans":payload.get("material_booleans"),
        "envelope_primitives":payload.get("envelope_primitives"),
        "worker_runtime_ms":payload.get("runtime_ms"),
        "wall_runtime_ms":(time.perf_counter()-started)*1000.0,
        "error":payload.get("error") or cp.stderr.strip(),
    }

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--profile",choices=("ci","baseline"),default="ci")
    ap.add_argument("--out-dir",type=Path,required=True)
    ap.add_argument("--rcs011-worker",type=Path)
    ap.add_argument("--repeats",type=int,default=2)
    ap.add_argument("--oracle-depth",type=int)
    ap.add_argument("--skip-external",action="store_true")
    args=ap.parse_args()
    plan=load_plan()
    policies=plan["policies"]
    depth=args.oracle_depth or int(policies["oracle_max_depth_ci" if args.profile=="ci" else "oracle_max_depth_baseline"])
    pitch=float(policies["tridexel_pitch_ci_mm"])
    args.out_dir.mkdir(parents=True,exist_ok=True)
    cases=profile_cases(plan,args.profile)
    records=[]
    structural=[]
    external_success=0
    deterministic=True
    closed_form_ok=True

    for case in cases:
        oracle=material_oracle.evaluate(case,depth,float(policies["oracle_field_numeric_error_mm"]),pitch)
        cv=oracle.get("closed_form_validation")
        if cv and not cv.get("contained_by_material_interval"):
            closed_form_ok=False
            structural.append(f"{case['id']}: closed-form truth outside independent oracle interval")
        tri_runs=[tridexel.evaluate(case,pitch) for _ in range(max(1,args.repeats))]
        sigs={r["engineering_signature"] for r in tri_runs}
        repeat_ok=len(sigs)==1
        deterministic = deterministic and repeat_ok
        tri=tri_runs[0]
        interval_overlap=_overlap(
            float(oracle["material_volume_lower_mm3"]),float(oracle["material_volume_upper_mm3"]),
            float(tri["volume_lower_mm3"]),float(tri["volume_upper_mm3"]),
        )
        expected_bodies=int(case.get("expected_body_count",1))
        body_ok=int(tri["body_count"])==expected_bodies and int(oracle["body_count_xy_grid"])==expected_bodies
        feature=case.get("minimum_positive_feature_mm")
        positive_removal=True
        if feature is not None:
            positive_removal=(STOCK_VOLUME-float(tri["volume_estimate_mm3"])) > 0.0
        bounded=(
            interval_overlap and body_ok and repeat_ok and positive_removal and
            float(tri["volume_interval_width_mm3"]) <= float(policies["qualification_max_volume_interval_mm3"]) and
            float(tri["spatial_support_radius_xy_mm"]) <= float(policies["qualification_max_spatial_support_radius_mm"])
        )
        if bounded:
            tri_class="bounded_candidate_pass"
        elif interval_overlap and body_ok and repeat_ok and positive_removal:
            tri_class="accepted_pending_refinement"
        else:
            tri_class="refused_unresolved_ambiguity"
        if not interval_overlap:
            structural.append(f"{case['id']}: dexel and independent oracle material intervals do not overlap")
        if not repeat_ok:
            structural.append(f"{case['id']}: dexel engineering signature changed across repeats")
        if not body_ok:
            structural.append(f"{case['id']}: required body count {expected_bodies} was not preserved")
        if not positive_removal:
            structural.append(f"{case['id']}: positive sub-tolerance removal was erased")

        external=None
        if not args.skip_external:
            external=manifold_fallback.evaluate(
                case,
                float(policies["manifold_edge_length_mm"]),
                float(policies["manifold_root_tolerance_mm"]),
                float(policies["manifold_authoritative_min_feature_mm"]),
            )
            if external.get("classification") != "external_candidate_error":
                external_success+=1
            if external.get("volume_mm3") is not None:
                external["volume_inside_oracle_interval"]=(
                    float(oracle["material_volume_lower_mm3"]) - 1e-9 <= float(external["volume_mm3"]) <= float(oracle["material_volume_upper_mm3"]) + 1e-9
                )
                external["body_count_matches_expected"]=int(external.get("body_count",-1))==expected_bodies

        refinements=[]
        if case["id"] in {"retrace-jitter","simultaneous-xyz","ball-rounded","plunge-1um","cut-through"}:
            for rpitch in policies["tridexel_refinement_pitches_mm"]:
                rp=float(rpitch)
                if abs(rp-pitch) < 1e-12:
                    rr=tri
                else:
                    rr=tridexel.evaluate(case,rp)
                refinements.append({
                    "pitch_mm":rp,
                    "spatial_support_radius_xy_mm":rr["spatial_support_radius_xy_mm"],
                    "volume_estimate_mm3":rr["volume_estimate_mm3"],
                    "volume_interval_width_mm3":rr["volume_interval_width_mm3"],
                    "body_count":rr["body_count"],
                    "runtime_ms":rr["runtime_ms"],
                    "total_interval_count":rr["total_interval_count"],
                })
        records.append({
            "case_id":case["id"],
            "source_family":case["source_family"],
            "tool":case["tool"],
            "segment_count":segment_count(case),
            "expected_body_count":expected_bodies,
            "oracle":oracle,
            "tridexel":tri,
            "tridexel_repeat_signatures":sorted(sigs),
            "tridexel_repeatable":repeat_ok,
            "tridexel_oracle_intervals_overlap":interval_overlap,
            "positive_sub_tolerance_removal_preserved":positive_removal,
            "candidate_classification":tri_class,
            "refinement":refinements,
            "external":external,
        })

    by_id={r["case_id"]:r for r in records}
    rcs011=[]
    if args.rcs011_worker:
        if not args.rcs011_worker.exists():
            structural.append(f"RCS-011 worker does not exist: {args.rcs011_worker}")
        else:
            mapping={"retrace-jitter":"retrace-jitter","slot-clean":"closed-form-horizontal-slot"}
            for control in plan["rcs011_controls"]:
                oracle_record=by_id[mapping[control["case_id"]]]["oracle"]
                for strategy in control["strategies"]:
                    rr=_run_rcs011(args.rcs011_worker,control["case_id"],strategy,float(policies["rcs011_worker_timeout_s"]))
                    if rr.get("volume_mm3") is not None:
                        rr["volume_inside_independent_oracle_interval"]=(
                            float(oracle_record["material_volume_lower_mm3"])-1e-9 <= float(rr["volume_mm3"]) <= float(oracle_record["material_volume_upper_mm3"])+1e-9
                        )
                    rcs011.append(rr)
    retrace_seq=next((r for r in rcs011 if r["case_id"]=="retrace-jitter" and r["strategy"]=="segment_sweep"),None)
    retrace_batch=next((r for r in rcs011 if r["case_id"]=="retrace-jitter" and r["strategy"]=="freehand_batch"),None)
    retrace_detected=None
    if retrace_seq and retrace_batch:
        retrace_detected=(
            retrace_seq.get("volume_inside_independent_oracle_interval") is True and
            retrace_batch.get("volume_inside_independent_oracle_interval") is False and
            retrace_batch.get("valid_brep") is True
        )
        if not retrace_detected:
            structural.append("RCS-011 retrace-jitter live revisit did not reproduce independent valid-but-wrong separation")

    sampled=next((r for r in rcs011 if r["case_id"]=="slot-clean" and r["strategy"]=="sampled_fallback"),None)
    sampled_revisited = sampled is not None and sampled.get("classification") in {"hang/timeout","success","algorithm_error"}
    if args.rcs011_worker and not sampled_revisited:
        structural.append("RCS-011 sampled fallback was not boundedly revisited")

    sub=by_id["plunge-1um"]
    cut=by_id["cut-through"]
    high=by_id["high-segment-freehand"]
    required_checks={
        "closed_form_oracle_validation":closed_form_ok,
        "tridexel_deterministic":deterministic,
        "sub_tolerance_positive_removal_preserved":sub["positive_sub_tolerance_removal_preserved"],
        "cut_through_two_bodies_preserved":cut["tridexel"]["body_count"]==2 and cut["oracle"]["body_count_xy_grid"]==2,
        "high_segment_fixture_exceeds_rcs011_smoke":high["segment_count"]>50,
        "external_candidate_executed":args.skip_external or external_success>0,
        "rcs011_retrace_independently_detected":True if not args.rcs011_worker else retrace_detected is True,
        "rcs011_sampled_fallback_revisited":True if not args.rcs011_worker else sampled_revisited,
    }
    all_pass=all(bool(v) for v in required_checks.values()) and not structural
    campaign={
        "schema":"rcs-021-campaign-results/1.0",
        "plan_schema":plan["schema"],
        "profile":args.profile,
        "environment":{"python":platform.python_version(),"platform":platform.platform()},
        "configuration":{"oracle_max_depth":depth,"tridexel_pitch_mm":pitch,"repeats":args.repeats},
        "case_count":len(records),
        "cases":records,
        "rcs011_revisit":rcs011,
        "rcs011_retrace_detected":retrace_detected,
        "rcs011_sampled_revisit":sampled,
        "external_success_count":external_success,
        "structural_failures":structural,
        "required_checks":required_checks,
        "all_required_checks_pass":all_pass,
    }
    _dump(args.out_dir/"campaign-results.json",campaign)
    with (args.out_dir/"case-records.jsonl").open("w",encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record,sort_keys=True)+"\n")
    print(json.dumps({"schema":campaign["schema"],"case_count":len(records),"all_required_checks_pass":all_pass,"structural_failures":structural},sort_keys=True))
    return 0 if all_pass else 2

if __name__=="__main__":
    raise SystemExit(main())
