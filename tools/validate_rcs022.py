#!/usr/bin/env python3
"""Validate static and measured RCS-022 contracts without inventing success."""
from __future__ import annotations
import argparse, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "research/rcs-022/fixture-plan-v1.json"
PROFILE = ROOT / "research/rcs-022/profile-v1.json"
REQUIRED = {
    "metric-block","inch-equivalent","analytic-cylinder","analytic-cone","through-hole","blind-hole",
    "two-body-parting","mill-cut-through","lathe-accepted-r020","healed-same-domain","trimmed-curved"
}
NEGATIVE = {
    "wrong_unit_scale","omitted_body","invalid_open_non_solid","analytic_degradation",
    "excessive_dimension_volume_deviation","parser_schema_failure","downstream_import_failure"
}

def fail(msg: str) -> None:
    raise SystemExit(f"RCS-022 validation failed: {msg}")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary")
    args = ap.parse_args()
    plan = json.loads(PLAN.read_text())
    profile = json.loads(PROFILE.read_text())
    if plan.get("schema") != "rcs-022-fixture-plan/1.0": fail("fixture schema")
    ids = {x["id"] for x in plan.get("cases", [])}
    if ids != REQUIRED: fail(f"fixture matrix mismatch: {sorted(ids ^ REQUIRED)}")
    if set(plan.get("negative_cases", [])) != NEGATIVE: fail("negative matrix mismatch")
    if profile.get("exporter", {}).get("version") != "8.0.1": fail("OCCT version not pinned")
    if profile["exporter"].get("source_commit") != "b8f597c677811d1f9f4d8a97f5ae2825c0353a42": fail("OCCT commit not pinned")
    if profile["exporter"].get("schema_mode") != "AP242DIS": fail("schema mode")
    if profile["exporter"].get("tessellated") is not False: fail("tessellated substitution must be off")
    if profile["layer_d"]["parser"].get("product") != "step-io" or profile["layer_d"]["parser"].get("version") != "0.2.4": fail("independent parser pin")
    if profile["layer_d"]["solid_consumer"].get("product") != "vcad-kernel-step" or profile["layer_d"]["solid_consumer"].get("version") != "0.10.0": fail("independent consumer pin")
    if "no OCCT dependency" not in profile["layer_d"]["parser"].get("implementation", ""): fail("parser independence must be explicit")
    if "no OCCT dependency" not in profile["layer_d"]["solid_consumer"].get("implementation", ""): fail("consumer independence must be explicit")
    if args.summary:
        s = json.loads(Path(args.summary).read_text())
        if s.get("schema") != "rcs-022-measured-summary/1.0": fail("summary schema")
        if s.get("qualification_status") not in {"interoperability_qualified","interoperability_unqualified"}: fail("verdict")
        got = {x["case"]["id"] for x in s.get("positive_cases", [])}
        if got != REQUIRED: fail("summary positive matrix incomplete")
        ngot = {x["id"] for x in s.get("negative_cases", [])}
        if ngot != NEGATIVE: fail("summary negative matrix incomplete")
        if not s.get("all_negative_controls_pass"): fail("adversarial controls did not all detect their faults")
        all_pos = all(x.get("qualified") for x in s["positive_cases"])
        if (s["qualification_status"] == "interoperability_qualified") != all_pos:
            fail("verdict does not match positive evidence")
        if s["qualification_status"] == "interoperability_unqualified" and not s.get("blockers"):
            fail("unqualified verdict must retain exact blockers")
        for case in s["positive_cases"]:
            if case["exporter"].get("status") == "exported" and not case.get("step_sha256"):
                fail(f"missing STEP digest for {case['case']['id']}")
            if case.get("qualified") and not all(case.get("checks", {}).values()):
                fail(f"false qualified case {case['case']['id']}")
    print("RCS-022 validation passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
