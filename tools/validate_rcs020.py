#!/usr/bin/env python3
"""Validate RCS-020 realistic lathe tool-envelope research contracts/results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "research/rcs-020/experiment-plan-v1.json"
GENERATOR = ROOT / "research/rcs-020/tool_envelope.py"
RUNNER = ROOT / "research/rcs-020/run_campaign.py"
README = ROOT / "research/rcs-020/README.md"
REPORT = ROOT / "docs/28-REALISTIC-LATHE-TOOL-ENVELOPE-RESEARCH.md"
DECISION = ROOT / "docs/decisions/DR-0017-realistic-lathe-tool-envelope-capability.md"

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{path.relative_to(ROOT)}: cannot parse JSON: {exc}")
        return None


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def validate_static() -> dict[str, Any] | None:
    for path in (PLAN, GENERATOR, RUNNER, README, REPORT, DECISION):
        require(path.exists(), f"missing required RCS-020 file: {path.relative_to(ROOT)}")
    plan = load_json(PLAN)
    if not isinstance(plan, dict):
        return None

    require(plan.get("schema") == "rcs-020-lathe-tool-envelope-plan/1.0", "unexpected RCS-020 plan schema")
    require(plan.get("issue") == "RCS-020", "plan must identify RCS-020")
    backend = plan.get("baseline", {}).get("occt", {})
    require(backend.get("version") == "8.0.1", "RCS-020 control must pin OCCT 8.0.1")
    require(backend.get("commit") == "b8f597c677811d1f9f4d8a97f5ae2825c0353a42", "RCS-020 OCCT commit pin drifted")

    sources = plan.get("sources", [])
    require(isinstance(sources, list) and len(sources) >= 3, "RCS-020 must record primary tool-geometry sources")
    if isinstance(sources, list):
        require(all(isinstance(s, dict) and str(s.get("url", "")).startswith("https://") and s.get("fact_used") for s in sources), "every RCS-020 source must have URL and fact_used")
        require(any("sandvik" in str(s.get("url", "")).lower() for s in sources), "tool-geometry plan must cite a primary manufacturer source")

    hypotheses = plan.get("hypotheses", [])
    require(isinstance(hypotheses, list) and len(hypotheses) >= 3, "RCS-020 requires explicit hypotheses")
    require(len(plan.get("falsification", [])) >= 4, "RCS-020 requires falsification criteria")

    policies = plan.get("policies", {})
    for key in (
        "profile_chord_tolerance_mm", "profile_sampling_step_mm", "max_material_profile_volume_delta_mm3",
        "max_occt_strategy_volume_delta_mm3", "max_occt_bbox_delta_mm", "max_step_volume_delta_mm3", "max_step_bbox_delta_mm",
    ):
        require(isinstance(policies.get(key), (int, float)) and float(policies[key]) > 0.0, f"missing/invalid positive policy {key}")
    require("not qualification" in str(policies.get("analytic_nose_surface_policy", "")), "analytic nose retention must remain explicitly unqualified by the polygon adapter")

    tools = plan.get("tools", {})
    require(isinstance(tools, dict) and len(tools) >= 4, "RCS-020 requires external, internal and groove/parting tool definitions")
    classes = {t.get("class") for t in tools.values() if isinstance(t, dict)}
    require({"external_turning", "internal_boring", "groove_parting"}.issubset(classes), "missing required RCS-020 tool class")
    nose_radii = [float(t.get("nose_radius_mm", 0.0)) for t in tools.values() if isinstance(t, dict) and "nose_radius_mm" in t]
    require(any(r > 0.0 for r in nose_radii), "at least one non-zero insert nose radius is required")
    approaches = {float(t["approach_angle_deg"]) for t in tools.values() if isinstance(t, dict) and "approach_angle_deg" in t}
    require(len(approaches) >= 2, "RCS-020 must exercise multiple tool approach angles")

    cases = plan.get("cases", [])
    require(isinstance(cases, list) and len(cases) == 10, "RCS-020 plan must contain exactly ten bounded cases")
    if not isinstance(cases, list):
        return plan
    ids = [case.get("id") for case in cases if isinstance(case, dict)]
    require(len(ids) == len(set(ids)), "RCS-020 case IDs must be unique")
    required_ids = {
        "od-roundnose-95", "face-roundnose-95", "shoulder-roundnose-95", "taper-roundnose-45",
        "exact-retrace-roundnose-20", "through-bore-roundnose", "blind-bore-roundnose",
        "partial-groove-r02", "complete-parting-r02", "undercut-holder-collision",
    }
    require(set(ids) == required_ids, "RCS-020 required case coverage drifted")
    kinds = {case.get("kind") for case in cases if isinstance(case, dict)}
    require({"round_nose_external", "facing_external", "round_nose_internal", "groove", "parting", "reachability_refusal"}.issubset(kinds), "missing process class in RCS-020 cases")
    by_id = {case["id"]: case for case in cases if isinstance(case, dict) and "id" in case}
    require(by_id.get("exact-retrace-roundnose-20", {}).get("journal_events") == 20, "retrace fixture must retain 20 journal events")
    require(by_id.get("complete-parting-r02", {}).get("expected", {}).get("body_count") == 2, "parting fixture must require two material bodies")
    require(by_id.get("undercut-holder-collision", {}).get("expected", {}).get("classification") == "refused_unsupported", "undercut reachability fixture must fail closed")
    require(by_id.get("face-roundnose-95", {}).get("expected", {}).get("result_front_z_mm") == 1.0, "facing fixture must declare tool-derived front plane")

    for path in (GENERATOR, RUNNER):
        if path.exists():
            text = path.read_text(encoding="utf-8")
            compile(text, str(path), "exec")
    if GENERATOR.exists():
        text = GENERATOR.read_text(encoding="utf-8")
        for marker in ("_capsule_polygon", "_oracle_segment_vertical_bounds", "oracle_round_nose_volume", "derive_groove_profile", "groove_oracle_volume", "holder_clearance_collision"):
            require(marker in text, f"tool-envelope implementation missing {marker}")
    if RUNNER.exists():
        text = RUNNER.read_text(encoding="utf-8")
        for marker in ("facing_case", "connectivity_step_control", "analytic_nose_surface_exactly_qualified", "refused_unsupported"):
            require(marker in text, f"RCS-020 runner missing {marker}")

    for path, markers in (
        (README, ("RCS-020", "Reproduction", "independent")),
        (REPORT, ("RCS-020", "Hypotheses", "Capability", "STEP", "Unresolved")),
        (DECISION, ("Status:", "## Context", "## Decision", "## Alternatives considered", "## Evidence", "## Consequences", "## Reversibility")),
    ):
        if path.exists():
            text = path.read_text(encoding="utf-8")
            for marker in markers:
                require(marker in text, f"{path.name} missing marker {marker!r}")
    return plan


def validate_results(plan: dict[str, Any], results_dir: Path) -> None:
    campaign_path = results_dir / "campaign-results.json"
    require(campaign_path.exists(), "RCS-020 measured campaign-results.json missing")
    campaign = load_json(campaign_path)
    if not isinstance(campaign, dict):
        return
    require(campaign.get("schema") == "rcs-020-campaign-results/1.0", "unexpected RCS-020 result schema")
    require(campaign.get("plan_schema") == plan.get("schema"), "RCS-020 result/plan schema mismatch")
    cases = campaign.get("cases", [])
    require(isinstance(cases, list) and len(cases) == 10, "measured RCS-020 campaign must contain ten cases")
    if not isinstance(cases, list):
        return
    by_id = {case.get("case_id"): case for case in cases if isinstance(case, dict)}
    require(len(by_id) == 10, "measured RCS-020 case IDs must be unique")

    qualified = [
        "od-roundnose-95", "face-roundnose-95", "shoulder-roundnose-95", "taper-roundnose-45",
        "exact-retrace-roundnose-20", "through-bore-roundnose", "blind-bore-roundnose", "partial-groove-r02",
    ]
    for case_id in qualified:
        case = by_id.get(case_id)
        require(isinstance(case, dict), f"missing measured case {case_id}")
        if not isinstance(case, dict):
            continue
        require(case.get("material_profile_within_budget") is True, f"{case_id}: tool-derived material profile exceeded oracle budget")
        if case_id != "face-roundnose-95":
            require(case.get("oracle_convergence_within_budget") is True, f"{case_id}: independent oracle did not converge inside budget")
        if case_id in {"od-roundnose-95", "shoulder-roundnose-95", "taper-roundnose-45", "exact-retrace-roundnose-20"}:
            require(case.get("reachability_pass") is True, f"{case_id}: holder reachability unexpectedly failed")
        if case_id == "face-roundnose-95":
            require(case.get("front_plane_matches_expected") is True, "facing tool-derived front plane mismatch")
        evaluation = case.get("occt_evaluation")
        require(isinstance(evaluation, dict), f"{case_id}: missing OCCT/RCS-010 evaluation")
        if isinstance(evaluation, dict):
            require(evaluation.get("all_required_checks_pass") is True, f"{case_id}: OCCT/STEP comparison failed")
            require(evaluation.get("analytic_nose_surface_exactly_qualified") is False, f"{case_id}: bounded polygon adapter must not claim exact nose analytic retention")
        worker = case.get("occt")
        require(isinstance(worker, dict) and worker.get("backend", {}).get("version") == "8.0.1", f"{case_id}: wrong/missing pinned OCCT worker")

    retrace = by_id.get("exact-retrace-roundnose-20", {})
    if isinstance(retrace, dict):
        worker = retrace.get("occt", {})
        require(worker.get("event_count") == 20, "retrace worker must preserve 20 events")
        strategies = worker.get("strategies", {})
        require(strategies.get("repeated_3d", {}).get("material_boolean_operations") == 20, "retrace repeated baseline must execute 20 material Booleans")
        require(strategies.get("batched_3d", {}).get("material_boolean_operations") == 1, "retrace batch must use one material Boolean")
        require(strategies.get("axisymmetric_2d", {}).get("material_boolean_operations") == 0, "retrace axisymmetric material provider must use zero material Booleans")

    od = by_id.get("od-roundnose-95", {})
    if isinstance(od, dict) and isinstance(retrace, dict):
        require(abs(float(od.get("generator", {}).get("volume_mm3", 0.0)) - float(retrace.get("generator", {}).get("volume_mm3", 1.0))) <= 1.0e-9, "exact retrace must preserve the same derived material profile as the first OD pass")

    parting = by_id.get("complete-parting-r02", {})
    require(isinstance(parting, dict) and parting.get("body_count_pass") is True, "parting material model must expose two disconnected bodies")
    if isinstance(parting, dict):
        require(parting.get("material_profile_within_budget") is True, "parting rounded-corner profile exceeded oracle budget")
        control = parting.get("connectivity_step_control")
        require(isinstance(control, dict) and control.get("passed") is True, "parting multi-body OCCT/STEP control failed")
        if isinstance(control, dict):
            require("not rounded-corner envelope equivalence" in str(control.get("scope", "")), "parting control scope must not overclaim rounded-corner equivalence")

    undercut = by_id.get("undercut-holder-collision", {})
    require(isinstance(undercut, dict) and undercut.get("pass") is True, "undercut/reachability refusal was not demonstrated")
    if isinstance(undercut, dict):
        require(undercut.get("classification") == "refused_unsupported", "undercut must classify as refused_unsupported")
        require(undercut.get("reachability", {}).get("collision") is True, "undercut refusal must be backed by measured holder collision")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path)
    args = parser.parse_args()
    plan = validate_static()
    if args.results_dir is not None and isinstance(plan, dict):
        validate_results(plan, args.results_dir)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    suffix = " + measured results" if args.results_dir is not None else ""
    print(f"RCS-020 validation passed{suffix}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
