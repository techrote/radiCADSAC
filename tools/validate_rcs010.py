#!/usr/bin/env python3
"""Validate RCS-010 lathe material-domain research and runtime evidence."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_OCCT_COMMIT = "b8f597c677811d1f9f4d8a97f5ae2825c0353a42"
EXPECTED_SMOKE = {
    "od-finish", "facing", "shoulder", "taper", "id-bore-through",
    "repeated-finish-20", "exact-retrace-100",
}
EXPECTED_CATEGORIES = {
    "od_turning", "facing", "shoulder", "taper_chamfer", "id_boring",
    "repeated_finishing", "exact_retrace",
}
REQUIRED_FILES = (
    ROOT / "docs/18-LATHE-MATERIAL-DOMAIN-RESEARCH.md",
    ROOT / "docs/decisions/DR-0013-axisymmetric-lathe-material-domain.md",
    ROOT / "research/rcs-010/README.md",
    ROOT / "research/rcs-010/experiment-plan-v1.json",
    ROOT / "research/rcs-010/harness/profile_solver.py",
    ROOT / "research/rcs-010/harness/CMakeLists.txt",
    ROOT / "research/rcs-010/harness/lathe_worker.cpp",
    ROOT / "research/rcs-010/harness/run_lathe_campaign.py",
)

errors: list[str] = []


def error(message: str) -> None:
    errors.append(message)


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        error(f"{path.relative_to(ROOT)}: cannot load JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        error(f"{path.relative_to(ROOT)}: JSON root must be an object")
        return {}
    return value


def load_profile_solver() -> Any:
    path = ROOT / "research/rcs-010/harness/profile_solver.py"
    spec = importlib.util.spec_from_file_location("rcs010_profile_solver", path)
    if spec is None or spec.loader is None:
        error("cannot create import spec for profile_solver.py")
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # validator should report a concise structural failure
        error(f"profile_solver.py cannot import: {exc}")
        return None
    return module


for path in REQUIRED_FILES:
    if not path.is_file():
        error(f"missing required file: {path.relative_to(ROOT)}")

plan_path = ROOT / "research/rcs-010/experiment-plan-v1.json"
plan = load_object(plan_path) if plan_path.is_file() else {}
corpus_path = ROOT / "research/rcs-003/corpus-v1.json"
corpus = load_object(corpus_path) if corpus_path.is_file() else {}

if plan:
    if plan.get("schema") != "rcs-010-lathe-plan/1.0":
        error("unexpected RCS-010 plan schema")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict) or baseline.get("commit") != EXPECTED_OCCT_COMMIT:
        error("RCS-010 plan must pin the accepted OCCT commit")
    if not isinstance(baseline, dict) or baseline.get("build_profile") != "release-shared-cxx17-worker-only-headless-v4":
        error("RCS-010 plan must pin the accepted RCS-006 OCCT build profile")

    cases = plan.get("cases")
    if not isinstance(cases, list) or not cases:
        error("RCS-010 plan must contain cases")
        cases = []
    case_ids = {item.get("id") for item in cases if isinstance(item, dict)}
    categories = {item.get("category") for item in cases if isinstance(item, dict)}
    if not EXPECTED_CATEGORIES.issubset(categories):
        error(f"RCS-010 required categories missing: {sorted(EXPECTED_CATEGORIES - categories)}")

    profiles = plan.get("profiles")
    smoke = set(profiles.get("smoke", [])) if isinstance(profiles, dict) else set()
    if smoke != EXPECTED_SMOKE:
        error(f"RCS-010 smoke profile mismatch: {sorted(smoke)}")
    if not smoke.issubset(case_ids):
        error("RCS-010 smoke profile references unknown cases")

    corpus_ids = {
        item.get("id") for item in corpus.get("fixture_families", []) if isinstance(item, dict)
    } if corpus else set()
    missing_families = sorted({
        item.get("source_family_id") for item in cases if isinstance(item, dict)
    } - corpus_ids)
    if missing_families:
        error(f"RCS-010 plan references missing RCS-003 families: {missing_families}")

    required_case_fields = {"id", "category", "source_family_id", "stock", "operations", "expected", "step"}
    for index, item in enumerate(cases):
        if not isinstance(item, dict):
            error(f"cases[{index}] must be an object")
            continue
        missing = required_case_fields - set(item)
        if missing:
            error(f"cases[{index}] missing fields {sorted(missing)}")
        stock = item.get("stock")
        if not isinstance(stock, dict):
            error(f"cases[{index}].stock must be an object")
        operations = item.get("operations")
        if not isinstance(operations, list) or not operations:
            error(f"cases[{index}].operations must be a non-empty list")
        expected = item.get("expected")
        if not isinstance(expected, dict) or expected.get("body_count") != 1:
            error(f"cases[{index}] founding fixed-axis set must preserve one material body")

    source_contracts = plan.get("source_contracts")
    if not isinstance(source_contracts, dict):
        error("RCS-010 source_contracts must be an object")
    else:
        for key in ("journal", "corpus", "baseline_harness", "step", "tolerance", "provenance", "regularization"):
            value = source_contracts.get(key)
            if not isinstance(value, str) or not (ROOT / value).is_file():
                error(f"RCS-010 source contract {key!r} does not resolve to a repository file")

    solver = load_profile_solver()
    if solver is not None:
        for item in cases:
            if not isinstance(item, dict):
                continue
            try:
                solved = solver.apply_case(item)
                volume = float(solved["result"]["volume_mm3"])
                points = solved["result"]["polygon_points"]
                if not math.isfinite(volume) or volume <= 0:
                    error(f"{item.get('id')}: profile solver produced non-positive/non-finite volume")
                if not isinstance(points, list) or len(points) < 5:
                    error(f"{item.get('id')}: profile solver produced an inadequate closed section")
                if points and points[0] != points[-1]:
                    error(f"{item.get('id')}: profile section is not closed")
            except Exception as exc:
                error(f"{item.get('id')}: profile solver failed deterministic plan case: {exc}")

report_path = ROOT / "docs/18-LATHE-MATERIAL-DOMAIN-RESEARCH.md"
if report_path.is_file():
    report = report_path.read_text(encoding="utf-8")
    for term in (
        "## Hypotheses and falsification criteria", "## Competing strategies",
        "## Material-domain definition", "## Operation semantics tested",
        "## Tool-envelope scope", "## Reconciliation and handoff boundaries",
        "## Explicit supported domain", "## Explicit exclusions and fallback requirements",
        "## Metrics and acceptance oracle", "## Relationship to accepted RCS-007/RCS-008/RCS-009 results",
        "## Architecture recommendation pending evidence", "piecewise", "axisymmetric",
        "nose radius", "STEP", EXPECTED_OCCT_COMMIT,
    ):
        if term not in report:
            error(f"RCS-010 report missing required term/section {term!r}")

decision_path = ROOT / "docs/decisions/DR-0013-axisymmetric-lathe-material-domain.md"
if decision_path.is_file():
    decision = decision_path.read_text(encoding="utf-8")
    for term in (
        "Status: proposed pending RCS-010 measured evidence", "## Proposed decision",
        "## Alternatives considered", "## Evidence", "first-class process provider",
        "canonical manufacturing journal", "batched 3D", "nose-radius",
    ):
        if term not in decision:
            error(f"DR-0013 missing required term {term!r}")

worker_path = ROOT / "research/rcs-010/harness/lathe_worker.cpp"
if worker_path.is_file():
    worker = worker_path.read_text(encoding="utf-8")
    for term in (
        "rcs-010-worker/1.0", "BRepPrimAPI_MakeRevol", "BRepAlgoAPI_Cut",
        "repeated_3d", "batched_3d", "axisymmetric_2d", "STEPControl_Writer",
        "WriteMode_StepSchema_AP242DIS", EXPECTED_OCCT_COMMIT,
    ):
        if term not in worker:
            error(f"RCS-010 worker missing required concept {term!r}")

runner_path = ROOT / "research/rcs-010/harness/run_lathe_campaign.py"
if runner_path.is_file():
    runner = runner_path.read_text(encoding="utf-8")
    for term in (
        "rcs-010-campaign/1.0", "analytic material volume", "axisymmetric_no_bspline_surface",
        "provenance_noop_events", "canonical_geometry_events", "step_roundtrip",
        "repeated_boolean_operations", "batched_boolean_operations",
    ):
        if term not in runner:
            error(f"RCS-010 campaign runner missing required concept {term!r}")

parser = argparse.ArgumentParser()
parser.add_argument("--results-dir", type=Path)
args = parser.parse_args()

if args.results_dir is not None:
    results_path = args.results_dir / "results.json"
    summary_path = args.results_dir / "summary.md"
    if not results_path.is_file():
        error(f"runtime results missing: {results_path}")
    if not summary_path.is_file():
        error(f"runtime summary missing: {summary_path}")
    results = load_object(results_path) if results_path.is_file() else {}
    if results:
        if results.get("schema") != "rcs-010-campaign/1.0":
            error("unexpected RCS-010 runtime result schema")
        backend = results.get("backend")
        if not isinstance(backend, dict) or backend.get("commit") != EXPECTED_OCCT_COMMIT:
            error("RCS-010 runtime evidence does not report exact OCCT commit")
        records = results.get("results")
        if not isinstance(records, list):
            error("RCS-010 runtime results must be a list")
            records = []
        ids = {item.get("case_id") for item in records if isinstance(item, dict)}
        if results.get("profile") == "smoke" and ids != EXPECTED_SMOKE:
            error(f"RCS-010 runtime smoke coverage mismatch: {sorted(ids)}")
        for index, item in enumerate(records):
            if not isinstance(item, dict):
                error(f"runtime results[{index}] must be an object")
                continue
            worker = item.get("worker")
            if not isinstance(worker, dict) or worker.get("status") != "measured":
                error(f"runtime results[{index}] worker did not complete")
                continue
            payload = worker.get("payload")
            if not isinstance(payload, dict) or payload.get("schema") != "rcs-010-worker/1.0":
                error(f"runtime results[{index}] worker payload schema invalid")
            if item.get("failures"):
                error(f"runtime results[{index}] reports acceptance failures: {item.get('failures')}")

        summary = results.get("summary")
        if not isinstance(summary, dict):
            error("RCS-010 runtime summary must be an object")
        else:
            if summary.get("cases") != len(EXPECTED_SMOKE) and results.get("profile") == "smoke":
                error("RCS-010 smoke summary case count mismatch")
            if summary.get("failed_cases") != 0:
                error("RCS-010 runtime campaign has failed cases")
            attempts = summary.get("step_strategy_attempts")
            passes = summary.get("step_strategy_passes")
            if not isinstance(attempts, int) or attempts < 3 or passes != attempts:
                error("RCS-010 required STEP strategy round-trips did not all pass")
            if int(summary.get("provenance_noop_events", 0)) < 99:
                error("RCS-010 smoke evidence lacks exact-retrace provenance no-op coverage")
            repeated = int(summary.get("repeated_boolean_operations", 0))
            batched = int(summary.get("batched_boolean_operations", 0))
            axis = int(summary.get("axisymmetric_boolean_operations", -1))
            if not (repeated > batched > axis == 0):
                error("RCS-010 runtime evidence does not distinguish the three strategy update counts")

if errors:
    print("RCS-010 validation failed:")
    for item in errors:
        print(f" - {item}")
    sys.exit(1)

print("RCS-010 validation passed")
