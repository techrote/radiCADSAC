#!/usr/bin/env python3
"""Validate RCS-011 mill strategy research artifacts and optional runtime evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COMMIT = "b8f597c677811d1f9f4d8a97f5ae2825c0353a42"
EXPECTED_STRATEGIES = {
    "explicit_analytic",
    "segment_sweep",
    "canonical_batch",
    "freehand_batch",
    "sampled_fallback",
}
EXPECTED_CASES = {
    "drill-explicit",
    "slot-clean",
    "overlapping-slots",
    "face-skim-zero",
    "face-skim-positive",
    "plunge-1um",
    "self-cross",
    "retrace-exact",
    "retrace-jitter",
    "tangent-zero",
    "tangent-overlap",
    "stationary-engaged",
    "ball-path",
    "cut-through",
    "high-segment-line",
}
EXPECTED_SOURCES = {
    "mill-sub-tolerance-plunge",
    "mill-repeated-identical-slot",
    "mill-overlapping-slots-pockets",
    "mill-coplanar-face-skim",
    "mill-self-crossing-freehand",
    "mill-retraced-jittery-path",
    "mill-tangent-corner-entry-exit",
    "mill-cut-through-separation",
    "mill-very-high-segment-count",
}
REQUIRED_FILES = (
    ROOT / "docs/19-MILL-CUTTER-SWEEP-RESEARCH.md",
    ROOT / "research/rcs-011/README.md",
    ROOT / "research/rcs-011/experiment-plan-v1.json",
    ROOT / "research/rcs-011/harness/CMakeLists.txt",
    ROOT / "research/rcs-011/harness/mill_worker.cpp",
    ROOT / "research/rcs-011/harness/run_mill_campaign.py",
    ROOT / ".github/workflows/rcs011.yml",
)

errors: list[str] = []


def error(message: str) -> None:
    errors.append(message)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        error(f"cannot parse {path.relative_to(ROOT)}: {exc}")
        return None


def check_static() -> None:
    for path in REQUIRED_FILES:
        if not path.is_file():
            error(f"missing required file: {path.relative_to(ROOT)}")

    plan_path = ROOT / "research/rcs-011/experiment-plan-v1.json"
    plan = load_json(plan_path) if plan_path.is_file() else None
    if not isinstance(plan, dict):
        return
    if plan.get("schema") != "rcs-011-mill-experiment-plan/1.0":
        error("unexpected RCS-011 plan schema")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict) or baseline.get("commit") != EXPECTED_COMMIT:
        error("RCS-011 plan must pin the accepted OCCT commit")
    if not isinstance(baseline, dict) or baseline.get("version") != "8.0.1":
        error("RCS-011 plan must pin OCCT 8.0.1")

    strategies = plan.get("strategies")
    observed_strategies: set[str] = set()
    levels: set[int] = set()
    if not isinstance(strategies, list):
        error("strategies must be a list")
    else:
        for idx, strategy in enumerate(strategies):
            if not isinstance(strategy, dict):
                error(f"strategies[{idx}] must be an object")
                continue
            sid = strategy.get("id")
            if isinstance(sid, str):
                observed_strategies.add(sid)
            level = strategy.get("hierarchy_level")
            if isinstance(level, int):
                levels.add(level)
        if observed_strategies != EXPECTED_STRATEGIES:
            error(f"strategy set mismatch: {sorted(observed_strategies)}")
        if levels != {1, 2, 3, 4, 5}:
            error(f"hierarchy levels must be exactly 1..5, got {sorted(levels)}")

    cases = plan.get("cases")
    case_ids: set[str] = set()
    source_ids: set[str] = set()
    tools: set[str] = set()
    step_cases = 0
    two_body = False
    diagnostic = False
    if not isinstance(cases, list):
        error("cases must be a list")
    else:
        for idx, case in enumerate(cases):
            if not isinstance(case, dict):
                error(f"cases[{idx}] must be an object")
                continue
            cid = case.get("id")
            source = case.get("source_family")
            tool = case.get("tool")
            if isinstance(cid, str):
                if cid in case_ids:
                    error(f"duplicate case id {cid}")
                case_ids.add(cid)
            if isinstance(source, str):
                source_ids.add(source)
            if isinstance(tool, str):
                tools.add(tool)
            case_strategies = case.get("strategies")
            if not isinstance(case_strategies, list) or not case_strategies:
                error(f"case {cid!r} has no strategies")
            elif not set(case_strategies).issubset(EXPECTED_STRATEGIES):
                error(f"case {cid!r} names unknown strategy")
            if case.get("reference_strategy") not in (case_strategies or []):
                error(f"case {cid!r} reference strategy is not exercised")
            if case.get("step"):
                step_cases += 1
            if case.get("expected_body_count") == 2:
                two_body = True
            if cid == "plunge-1um" and case.get("required") is False:
                diagnostic = True
        missing = EXPECTED_CASES - case_ids
        if missing:
            error(f"missing required RCS-011 cases: {sorted(missing)}")
        if not EXPECTED_SOURCES.issubset(source_ids):
            error(f"missing RCS-003 source-family coverage: {sorted(EXPECTED_SOURCES - source_ids)}")
        if not {"flat_end_mill", "drill", "ball_end"}.issubset(tools):
            error("fixture set must cover flat end mill, drill, and ball-end envelope")
        if step_cases < 4:
            error("at least four RCS-011 cases must exercise STEP read-back")
        if not two_body:
            error("fixture set must include a two-body cut-through case")
        if not diagnostic:
            error("1 um plunge must remain explicit diagnostic evidence rather than a hidden pass requirement")

    profiles = plan.get("profiles")
    if not isinstance(profiles, dict) or not isinstance(profiles.get("smoke"), list):
        error("smoke profile missing")
    elif not EXPECTED_CASES.issubset(set(profiles["smoke"])):
        error("smoke profile does not cover all founding RCS-011 cases")

    recognizers = plan.get("recognition_samples")
    if not isinstance(recognizers, list) or len(recognizers) < 5:
        error("recognition guard requires positive and negative samples")
    else:
        expected_values = {r.get("expected") for r in recognizers if isinstance(r, dict)}
        if "unrecognized" not in expected_values or "strict_linear_slot" not in expected_values or "explicit_drill" not in expected_values:
            error("recognition samples must test explicit tag, strict recognition, and false-positive rejection")

    report_path = ROOT / "docs/19-MILL-CUTTER-SWEEP-RESEARCH.md"
    if report_path.is_file():
        report = report_path.read_text(encoding="utf-8")
        terms = (
            "## Hypotheses and falsification criteria",
            "## Strategy hierarchy under test",
            "## Recognition policy",
            "## Stationary and near-stationary engaged motion",
            "## Topology and reconciliation boundaries",
            "sampled fallback",
            "five-axis",
            EXPECTED_COMMIT,
            "regularized volumetric",
        )
        for term in terms:
            if term not in report:
                error(f"RCS-011 report missing required term {term!r}")

    worker_path = ROOT / "research/rcs-011/harness/mill_worker.cpp"
    if worker_path.is_file():
        worker = worker_path.read_text(encoding="utf-8")
        for term in (
            "BRepAlgoAPI_Cut",
            "BRepCheck_Analyzer",
            "STEPControl_Writer",
            "STEPControl_Reader",
            "SetRunParallel(false)",
            "SetFuzzyValue(0.0)",
            "sampled_fallback",
            "canonical_batch",
            "freehand_batch",
            EXPECTED_COMMIT,
        ):
            if term not in worker:
                error(f"RCS-011 worker missing required marker {term!r}")

    runner_path = ROOT / "research/rcs-011/harness/run_mill_campaign.py"
    if runner_path.is_file():
        runner = runner_path.read_text(encoding="utf-8")
        for term in ("subprocess.run", "timeout=timeout_s", "strict_recognize", "nondeterministic result", "sampled fallback exceeded"):
            if term not in runner:
                error(f"RCS-011 runner missing required marker {term!r}")

    workflow_path = ROOT / ".github/workflows/rcs011.yml"
    if workflow_path.is_file():
        workflow = workflow_path.read_text(encoding="utf-8")
        for term in ("verify_occt_install.sh", "run_mill_campaign.py", "validate_rcs011.py --results-dir", "actions/upload-artifact@v4"):
            if term not in workflow:
                error(f"RCS-011 workflow missing required marker {term!r}")


def check_runtime(results_dir: Path) -> None:
    campaign_path = results_dir / "campaign.json"
    results_path = results_dir / "results.jsonl"
    summary_path = results_dir / "measured-summary.json"
    for path in (campaign_path, results_path, summary_path):
        if not path.is_file():
            error(f"runtime evidence missing {path}")
    if errors:
        return

    campaign = load_json(campaign_path)
    summary = load_json(summary_path)
    if not isinstance(campaign, dict) or not isinstance(summary, dict):
        return
    if campaign.get("schema") != "rcs-011-campaign/1.0":
        error("unexpected campaign schema")
    backend = campaign.get("backend")
    if not isinstance(backend, dict) or backend.get("commit") != EXPECTED_COMMIT:
        error("campaign did not measure the pinned OCCT commit")
    if campaign.get("structural_failure_count") != 0:
        error(f"campaign structural failures: {campaign.get('structural_failure_count')}")
    if campaign.get("required_acceptance_failure_count") != 0:
        error(f"campaign required acceptance failures: {campaign.get('required_acceptance_failure_count')}")

    if summary.get("schema") != "rcs-011-measured-summary/1.0":
        error("unexpected measured-summary schema")
    if summary.get("structural_failure_count") != 0 or summary.get("required_acceptance_failure_count") != 0:
        error("measured summary reports structural/required acceptance failures")
    recognition = summary.get("recognition_results")
    if not isinstance(recognition, list) or not recognition:
        error("measured summary lacks recognition evidence")
    else:
        mismatches = [r for r in recognition if isinstance(r, dict) and r.get("observed") != r.get("expected")]
        if mismatches:
            error(f"recognition guard mismatches: {mismatches}")

    records: list[dict[str, Any]] = []
    try:
        for lineno, line in enumerate(results_path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            if not isinstance(record, dict):
                error(f"results line {lineno} is not an object")
                continue
            records.append(record)
    except (OSError, json.JSONDecodeError) as exc:
        error(f"cannot parse runtime results: {exc}")
        return

    observed_cases = {r.get("case_id") for r in records}
    if not EXPECTED_CASES.issubset(observed_cases):
        error(f"runtime results missing cases: {sorted(EXPECTED_CASES - observed_cases)}")
    observed_strategies = {r.get("strategy") for r in records}
    if not EXPECTED_STRATEGIES.issubset(observed_strategies):
        error(f"runtime results missing strategies: {sorted(EXPECTED_STRATEGIES - observed_strategies)}")

    exact_required_failures = [
        r for r in records
        if r.get("required") and r.get("strategy") != "sampled_fallback" and r.get("classification") != "success"
    ]
    if exact_required_failures:
        error(f"required exact-strategy attempts failed: {[(r.get('case_id'), r.get('strategy'), r.get('classification')) for r in exact_required_failures[:10]]}")

    success_records = [r for r in records if r.get("classification") == "success" and isinstance(r.get("worker"), dict)]
    if not success_records:
        error("no successful measured attempts")
    for record in success_records:
        geom = record["worker"].get("geometry")
        if not isinstance(geom, dict) or not geom.get("valid_brep"):
            error(f"successful record lacks valid B-rep: {record.get('case_id')} {record.get('strategy')}")
            break

    batching_wins = 0
    by_case_attempt: dict[tuple[str, int], dict[str, dict[str, Any]]] = {}
    for record in records:
        key = (str(record.get("case_id")), int(record.get("attempt", 0)))
        by_case_attempt.setdefault(key, {})[str(record.get("strategy"))] = record
    for strategies in by_case_attempt.values():
        segment = strategies.get("segment_sweep")
        for name in ("canonical_batch", "freehand_batch"):
            candidate = strategies.get(name)
            if not segment or not candidate:
                continue
            sw = segment.get("worker")
            cw = candidate.get("worker")
            if isinstance(sw, dict) and isinstance(cw, dict) and int(cw.get("material_booleans", 999999)) < int(sw.get("material_booleans", -1)):
                batching_wins += 1
    if batching_wins < 2:
        error(f"expected at least two measured material-Boolean batching wins, observed {batching_wins}")

    successful_step = 0
    for record in success_records:
        step = record["worker"].get("step")
        if isinstance(step, dict) and step.get("attempted") and step.get("write_status") == "done" and step.get("read_status") == "done" and step.get("readback_transferred"):
            successful_step += 1
    if successful_step < 4:
        error(f"expected at least four successful STEP attempts, observed {successful_step}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path)
    args = parser.parse_args()
    check_static()
    if args.results_dir is not None:
        check_runtime(args.results_dir)
    if errors:
        print("RCS-011 validation failed:")
        for item in errors:
            print(f" - {item}")
        return 1
    print("RCS-011 validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
