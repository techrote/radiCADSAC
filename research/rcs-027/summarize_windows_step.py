#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any

def load(p: Path) -> dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))

def projection(summary: dict[str, Any]) -> dict[str, Any]:
    positives=[]
    for case in sorted(summary["positive_cases"], key=lambda x:x["case"]["id"]):
        positives.append({
            "id":case["case"]["id"],
            "qualified":case["qualified"],
            "export_status":case["exporter"].get("status"),
            "layer_c_body_count":case["exporter"]["layer_c_readback"]["metrics"].get("body_count"),
            "parser_status":case["parser"].get("status"),
            "parser_solid_count":case["parser"].get("solid_count"),
            "consumer_status":case["consumer"].get("status"),
            "consumer_solid_count":case["consumer"].get("solid_count"),
            "checks":case["checks"],
        })
    negatives=[{"id":x["id"],"passed":x["passed"],"failure_code":x.get("failure_code")}
               for x in sorted(summary["negative_cases"], key=lambda x:x["id"])]
    return {
        "profile_id":summary["profile_id"],
        "qualification_status":summary["qualification_status"],
        "positive_cases":positives,
        "negative_cases":negatives,
        "blockers":sorted(summary.get("blockers",[])),
        "all_positive_qualified":summary["all_positive_qualified"],
        "all_negative_controls_pass":summary["all_negative_controls_pass"],
    }

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,action="append",required=True)
    ap.add_argument("--toolchain",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    if len(a.input)!=3:
        raise SystemExit("RCS-027 Windows STEP closure requires exactly three repetitions")
    runs=[load(p) for p in a.input]
    projections=[projection(x) for x in runs]
    if not all(x==projections[0] for x in projections[1:]):
        raise SystemExit("Windows programme-level STEP result drifted between repetitions")
    first=projections[0]
    if first["qualification_status"]!="interoperability_unqualified":
        raise SystemExit("Layer-D status must remain interoperability_unqualified")
    if len(first["positive_cases"])!=11 or len(first["negative_cases"])!=7:
        raise SystemExit("unexpected RCS-022 fixture/control cardinality")
    if not first["all_negative_controls_pass"]:
        raise SystemExit("an RCS-022 adversarial control failed")
    tool=load(a.toolchain)
    if tool.get("compiler_id")!="MSVC" or int(tool.get("compiler_version_numeric",-1))!=1951:
        raise SystemExit(f"unexpected MSVC toolchain: {tool}")
    out={
        "schema":"rcs-027-windows-step-live/1.0",
        "status":"pass",
        "gate5_windows_step_blocker":"cleared",
        "runner_scope":"windows-2025 / MSVC 19.51 / exact OCCT 8.0.1",
        "occt_version":"8.0.1",
        "occt_commit":"b8f597c677811d1f9f4d8a97f5ae2825c0353a42",
        "profile_id":first["profile_id"],
        "live_repetitions":3,
        "positive_case_count":11,
        "negative_case_count":7,
        "negative_controls_passed":7,
        "qualification_status":first["qualification_status"],
        "programme_projection":first,
        "toolchain":tool,
        "protected_semantics":"unchanged",
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("RCS027_WINDOWS_STEP_SUMMARY="+json.dumps({
        "status":"pass","repetitions":3,"qualification_status":first["qualification_status"],
        "positive_cases":11,"negative_controls_passed":7,
        "compiler":tool["compiler_id"],"compiler_version_numeric":tool["compiler_version_numeric"]
    },sort_keys=True))
    return 0
if __name__=="__main__":
    raise SystemExit(main())
