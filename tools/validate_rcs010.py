#!/usr/bin/env python3
"""Validate accepted RCS-010 lathe material-domain research and runtime evidence."""
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
EXPECTED_RUN = 35214872300
EXPECTED_JOB = 105180888767
EXPECTED_ARTIFACT = 10493944652
EXPECTED_DIGEST = "sha256:7a2511d30fbcdf4dc04b9e8a969b2a3387a84d90226d1f2784249899ca81096c"
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
    ROOT / "research/rcs-010/measured-summary-v1.json",
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


def validate_summary(summary: Any, where: str) -> None:
    if not isinstance(summary, dict):
        error(f"{where}: summary must be an object")
        return
    exact = {
        "cases": 9,
        "failed_cases": 0,
        "step_strategy_attempts": 21,
        "step_strategy_passes": 21,
        "journal_events": 135,
        "provenance_noop_events": 118,
        "raw_samples": 9,
        "repeated_boolean_operations": 127,
        "batched_boolean_operations": 9,
        "axisymmetric_boolean_operations": 0,
    }
    for key, expected in exact.items():
        if summary.get(key) != expected:
            error(f"{where}: {key}={summary.get(key)!r}, expected {expected!r}")
    for key in ("repeated_total_ms", "batched_total_ms", "axisymmetric_total_ms"):
        if not isinstance(summary.get(key), (int, float)) or float(summary[key]) <= 0:
            error(f"{where}: {key} must be a positive measured value")


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
        error("RCS-010 plan must pin accepted OCCT commit")
    if baseline.get("build_profile") != "release-shared-cxx17-worker-only-headless-v4":
        error("RCS-010 plan must pin accepted RCS-006 build profile")
    cases = plan.get("cases", [])
    if not isinstance(cases, list) or not cases:
        error("RCS-010 plan must contain cases")
        cases = []
    ids = {x.get("id") for x in cases if isinstance(x, dict)}
    categories = {x.get("category") for x in cases if isinstance(x, dict)}
    if not EXPECTED_CATEGORIES.issubset(categories):
        error(f"RCS-010 categories missing: {sorted(EXPECTED_CATEGORIES - categories)}")
    smoke = set(plan.get("profiles", {}).get("smoke", []))
    if smoke != EXPECTED_SMOKE or not smoke.issubset(ids):
        error(f"RCS-010 accepted smoke set mismatch: {sorted(smoke)}")
    corpus_ids = {x.get("id") for x in corpus.get("fixture_families", []) if isinstance(x, dict)}
    missing = sorted({x.get("source_family_id") for x in cases if isinstance(x, dict)} - corpus_ids)
    if missing:
        error(f"RCS-010 references missing RCS-003 families: {missing}")
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
                    error(f"{item.get('id')}: solver volume is not positive/finite")
                if not isinstance(points, list) or len(points) < 5 or points[0] != points[-1]:
                    error(f"{item.get('id')}: solver section is not an adequate closed polygon")
            except Exception as exc:
                error(f"{item.get('id')}: deterministic profile solve failed: {exc}")

measured = load_object(ROOT / "research/rcs-010/measured-summary-v1.json")
if measured:
    if measured.get("schema") != "rcs-010-measured-summary/1.0" or measured.get("status") != "accepted":
        error("RCS-010 measured summary must be accepted schema 1.0")
    source = measured.get("source", {})
    expected_source = {
        "workflow_run_id": EXPECTED_RUN,
        "job_id": EXPECTED_JOB,
        "artifact_id": EXPECTED_ARTIFACT,
        "artifact_digest": EXPECTED_DIGEST,
    }
    for key, expected in expected_source.items():
        if source.get(key) != expected:
            error(f"RCS-010 measured source {key} mismatch")
    if measured.get("backend", {}).get("commit") != EXPECTED_OCCT_COMMIT:
        error("RCS-010 measured summary backend commit mismatch")
    validate_summary(measured.get("summary"), "measured-summary")
    summary = measured.get("summary", {})
    if float(summary.get("max_strategy_axis_volume_abs_delta_mm3", math.inf)) > 1e-5:
        error("measured cross-strategy volume delta exceeds accepted budget")
    if float(summary.get("max_strategy_axis_bbox_abs_delta_mm", math.inf)) > 1e-6:
        error("measured cross-strategy bbox delta exceeds accepted budget")
    if float(summary.get("max_step_volume_abs_delta_mm3", math.inf)) > 1e-5:
        error("measured STEP volume delta exceeds accepted budget")
    reps = measured.get("representative_measurements", {})
    taper = reps.get("taper", {})
    if taper.get("axisymmetric_analytic_surfaces", {}).get("cone") != 1 or not taper.get("axisymmetric_step_roundtrip_passed"):
        error("measured summary must preserve analytic taper/STEP evidence")
    blind = reps.get("blind_bore", {})
    if blind.get("axisymmetric_faces") != 6 or blind.get("repeated_faces") != 5 or not blind.get("axisymmetric_step_roundtrip_passed"):
        error("measured summary must preserve blind-bore topology-regeneration evidence")
    retrace = reps.get("exact_retrace_100", {})
    if retrace.get("journal_events") != 100 or retrace.get("provenance_noop_events") != 99:
        error("measured summary must preserve 100-pass retrace provenance evidence")
    noisy = reps.get("noisy_feed", {})
    if noisy.get("raw_samples") != 9 or noisy.get("canonical_geometry_events") != 1:
        error("measured summary must preserve analogue canonicalization evidence")

report = (ROOT / "docs/18-LATHE-MATERIAL-DOMAIN-RESEARCH.md").read_text(encoding="utf-8")
for term in (
    "Status: accepted RCS-010 research result", "## Hypotheses and falsification criteria",
    "## Competing strategies", "## Material-domain definition", "## Tool-envelope scope",
    "## Reconciliation and handoff boundaries", "## Explicit supported domain",
    "## Explicit exclusions and fallback requirements", "## Metrics and acceptance oracle",
    "## Measured RCS-010 results", "## Relationship to accepted RCS-007/RCS-008/RCS-009 results",
    "## Architecture recommendation", str(EXPECTED_RUN), str(EXPECTED_ARTIFACT), EXPECTED_DIGEST,
    "21/21", "nose radius", "STEP", EXPECTED_OCCT_COMMIT,
):
    if term not in report:
        error(f"RCS-010 report missing {term!r}")

decision = (ROOT / "docs/decisions/DR-0013-axisymmetric-lathe-material-domain.md").read_text(encoding="utf-8")
for term in (
    "Status: accepted", "## Decision", "## Alternatives considered", "## Evidence",
    "first-class process provider", "canonical manufacturing journal", "batched 3D",
    "nose-radius", str(EXPECTED_RUN), EXPECTED_DIGEST,
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
            error("unexpected RCS-010 runtime schema")
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
        validate_summary(results.get("summary"), "runtime-summary")

if errors:
    print("RCS-010 validation failed:")
    for item in errors:
        print(f" - {item}")
    sys.exit(1)
print("RCS-010 validation passed")
