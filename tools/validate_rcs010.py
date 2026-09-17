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
    "od-finish", "facing", "shoulder", "taper", "id-bore-through", "id-bore-blind",
    "repeated-finish-20", "exact-retrace-100", "noisy-feed-canonicalized",
}
EXPECTED_CATEGORIES = {
    "od_turning", "facing", "shoulder", "taper_chamfer", "id_boring",
    "repeated_finishing", "exact_retrace", "canonicalized_analogue_feed",
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
    except Exception as exc:
        error(f"profile_solver.py cannot import: {exc}")
        return None
    return module


for path in REQUIRED_FILES:
    if not path.is_file():
        error(f"missing required file: {path.relative_to(ROOT)}")

plan = load_object(ROOT / "research/rcs-010/experiment-plan-v1.json")
corpus = load_object(ROOT / "research/rcs-003/corpus-v1.json")
if plan:
    if plan.get("schema") != "rcs-010-lathe-plan/1.0":
        error("unexpected RCS-010 plan schema")
    baseline = plan.get("baseline", {})
    if baseline.get("commit") != EXPECTED_OCCT_COMMIT:
        error("RCS-010 plan must pin the accepted OCCT commit")
    if baseline.get("build_profile") != "release-shared-cxx17-worker-only-headless-v4":
        error("RCS-010 plan must pin the accepted RCS-006 build profile")

    cases = plan.get("cases", [])
    if not isinstance(cases, list) or not cases:
        error("RCS-010 plan must contain cases")
        cases = []
    ids = {x.get("id") for x in cases if isinstance(x, dict)}
    categories = {x.get("category") for x in cases if isinstance(x, dict)}
    if not EXPECTED_CATEGORIES.issubset(categories):
        error(f"RCS-010 categories missing: {sorted(EXPECTED_CATEGORIES - categories)}")
    profiles = plan.get("profiles", {})
    smoke = set(profiles.get("smoke", [])) if isinstance(profiles, dict) else set()
    if smoke != EXPECTED_SMOKE:
        error(f"RCS-010 smoke profile mismatch: {sorted(smoke)}")
    if not smoke.issubset(ids):
        error("RCS-010 smoke profile references unknown cases")

    corpus_ids = {x.get("id") for x in corpus.get("fixture_families", []) if isinstance(x, dict)}
    missing = sorted({x.get("source_family_id") for x in cases if isinstance(x, dict)} - corpus_ids)
    if missing:
        error(f"RCS-010 plan references missing RCS-003 families: {missing}")

    for index, item in enumerate(cases):
        if not isinstance(item, dict):
            error(f"cases[{index}] must be an object")
            continue
        for field in ("id", "category", "source_family_id", "stock", "operations", "expected", "step"):
            if field not in item:
                error(f"cases[{index}] missing {field}")
        if not isinstance(item.get("operations"), list) or not item["operations"]:
            error(f"cases[{index}].operations must be a non-empty list")
        if item.get("expected", {}).get("body_count") != 1:
            error(f"cases[{index}] founding fixed-axis set must preserve one material body")

    contracts = plan.get("source_contracts", {})
    for key in ("journal", "corpus", "baseline_harness", "step", "tolerance", "provenance", "regularization"):
        value = contracts.get(key) if isinstance(contracts, dict) else None
        if not isinstance(value, str) or not (ROOT / value).is_file():
            error(f"RCS-010 source contract {key!r} does not resolve")

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
                    error(f"{item['id']}: solver volume is not positive/finite")
                if not isinstance(points, list) or len(points) < 5 or points[0] != points[-1]:
                    error(f"{item['id']}: solver section is not an adequate closed polygon")
            except Exception as exc:
                error(f"{item.get('id')}: deterministic profile solve failed: {exc}")

report = (ROOT / "docs/18-LATHE-MATERIAL-DOMAIN-RESEARCH.md").read_text(encoding="utf-8")
for term in (
    "## Hypotheses and falsification criteria", "## Competing strategies",
    "## Material-domain definition", "## Tool-envelope scope",
    "## Reconciliation and handoff boundaries", "## Explicit supported domain",
    "## Explicit exclusions and fallback requirements", "## Metrics and acceptance oracle",
    "## Relationship to accepted RCS-007/RCS-008/RCS-009 results",
    "## Architecture recommendation pending evidence", "nose radius", "STEP", EXPECTED_OCCT_COMMIT,
):
    if term not in report:
        error(f"RCS-010 report missing {term!r}")

decision = (ROOT / "docs/decisions/DR-0013-axisymmetric-lathe-material-domain.md").read_text(encoding="utf-8")
for term in (
    "Status: proposed pending RCS-010 measured evidence", "## Proposed decision",
    "## Alternatives considered", "## Evidence", "first-class process provider",
    "canonical manufacturing journal", "batched 3D", "nose-radius",
):
    if term not in decision:
        error(f"DR-0013 missing {term!r}")

worker = (ROOT / "research/rcs-010/harness/lathe_worker.cpp").read_text(encoding="utf-8")
for term in (
    "rcs-010-worker/1.0", "BRepPrimAPI_MakeRevol", "BRepAlgoAPI_Cut",
    "repeated_3d", "batched_3d", "axisymmetric_2d", "STEPControl_Writer",
    "WriteMode_StepSchema_AP242DIS", EXPECTED_OCCT_COMMIT,
):
    if term not in worker:
        error(f"RCS-010 worker missing {term!r}")

runner = (ROOT / "research/rcs-010/harness/run_lathe_campaign.py").read_text(encoding="utf-8")
for term in (
    "rcs-010-campaign/1.0", "expected_volume", "axisymmetric_no_bspline_surface",
    "provenance_noop_events", "canonical_geometry_events", "step_roundtrip",
    "repeated_boolean_operations", "batched_boolean_operations",
):
    if term not in runner:
        error(f"RCS-010 campaign runner missing {term!r}")

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
        if results.get("backend", {}).get("commit") != EXPECTED_OCCT_COMMIT:
            error("runtime evidence does not report exact OCCT commit")
        records = results.get("results", [])
        if not isinstance(records, list):
            error("runtime results must be a list")
            records = []
        ids = {x.get("case_id") for x in records if isinstance(x, dict)}
        if results.get("profile") == "smoke" and ids != EXPECTED_SMOKE:
            error(f"runtime smoke coverage mismatch: {sorted(ids)}")
        for index, item in enumerate(records):
            if not isinstance(item, dict):
                error(f"runtime results[{index}] must be an object")
                continue
            w = item.get("worker", {})
            if w.get("status") != "measured":
                error(f"runtime results[{index}] worker did not complete")
                continue
            if w.get("payload", {}).get("schema") != "rcs-010-worker/1.0":
                error(f"runtime results[{index}] worker payload schema invalid")
            if item.get("failures"):
                error(f"runtime results[{index}] acceptance failures: {item.get('failures')}")

        s = results.get("summary", {})
        if not isinstance(s, dict):
            error("runtime summary must be an object")
        else:
            if results.get("profile") == "smoke" and s.get("cases") != len(EXPECTED_SMOKE):
                error("smoke summary case count mismatch")
            if s.get("failed_cases") != 0:
                error("runtime campaign has failed cases")
            attempts = s.get("step_strategy_attempts")
            if not isinstance(attempts, int) or attempts < 3 or s.get("step_strategy_passes") != attempts:
                error("required STEP strategy round-trips did not all pass")
            if int(s.get("provenance_noop_events", 0)) < 99:
                error("smoke evidence lacks exact-retrace no-op coverage")
            if int(s.get("raw_samples", 0)) < 9:
                error("smoke evidence lacks bounded analogue-feed canonicalization coverage")
            repeated = int(s.get("repeated_boolean_operations", 0))
            batched = int(s.get("batched_boolean_operations", 0))
            axis = int(s.get("axisymmetric_boolean_operations", -1))
            if not (repeated > batched > axis == 0):
                error("runtime evidence does not distinguish strategy update counts")

if errors:
    print("RCS-010 validation failed:")
    for item in errors:
        print(f" - {item}")
    sys.exit(1)
print("RCS-010 validation passed")
