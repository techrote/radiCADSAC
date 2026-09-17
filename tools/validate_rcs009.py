#!/usr/bin/env python3
"""Validate RCS-009 regularized-material/deferred-topology research."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_OCCT_COMMIT = "b8f597c677811d1f9f4d8a97f5ae2825c0353a42"
EXPECTED_CATEGORIES = {
    "lower_dimensional_contact",
    "tangent_entry_exit",
    "sliver",
    "repeated_pass",
    "overlapping_removal",
    "connectivity_split",
}
EXPECTED_SMOKE = {
    "face-contact-zero",
    "tangent-contact-zero",
    "tangent-overlap-1um",
    "thin-skim-0.1um",
    "repeated-slot-20",
    "repeated-slot-200",
    "overlapping-slots",
    "mill-cut-through",
}

REQUIRED_FILES = (
    ROOT / "docs/17-REGULARIZED-DEFERRED-TOPOLOGY.md",
    ROOT / "docs/decisions/DR-0012-regularized-material-and-bounded-deferred-topology.md",
    ROOT / "research/rcs-009/README.md",
    ROOT / "research/rcs-009/experiment-plan-v1.json",
    ROOT / "research/rcs-009/harness/CMakeLists.txt",
    ROOT / "research/rcs-009/harness/deferred_worker.cpp",
    ROOT / "research/rcs-009/harness/run_deferred_campaign.py",
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
        error(f"{path.relative_to(ROOT)}: root must be an object")
        return {}
    return value


for path in REQUIRED_FILES:
    if not path.is_file():
        error(f"missing required file: {path.relative_to(ROOT)}")

plan_path = ROOT / "research/rcs-009/experiment-plan-v1.json"
plan = load_object(plan_path) if plan_path.is_file() else {}
if plan:
    if plan.get("experiment_plan_schema") != "rcs-009-experiment-plan/1.0":
        error("unexpected RCS-009 experiment plan schema")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict) or baseline.get("commit") != EXPECTED_OCCT_COMMIT:
        error("RCS-009 baseline must pin the accepted OCCT commit")
    candidate = plan.get("candidate")
    if not isinstance(candidate, dict) or "deferred" not in str(candidate.get("strategy", "")).lower():
        error("experiment plan must define the deferred candidate strategy")
    cases = plan.get("cases")
    if not isinstance(cases, list) or not cases:
        error("experiment plan must contain cases")
        cases = []
    categories = {item.get("category") for item in cases if isinstance(item, dict)}
    if not EXPECTED_CATEGORIES.issubset(categories):
        error(f"RCS-009 fixture categories missing: {sorted(EXPECTED_CATEGORIES - categories)}")
    case_ids = {item.get("id") for item in cases if isinstance(item, dict)}
    smoke = set(plan.get("profiles", {}).get("smoke", [])) if isinstance(plan.get("profiles"), dict) else set()
    if smoke != EXPECTED_SMOKE:
        error(f"RCS-009 smoke profile must contain exactly the founding smoke set; observed {sorted(smoke)}")
    if not smoke.issubset(case_ids):
        error("smoke profile references missing cases")
    if not any(isinstance(item, dict) and item.get("probe_cells_builder") for item in cases):
        error("experiment plan must include at least one CellsBuilder probe")
    if not any(isinstance(item, dict) and item.get("step", {}).get("enabled") for item in cases):
        error("experiment plan must include reconciled STEP round-trip coverage")
    for index, item in enumerate(cases):
        if not isinstance(item, dict):
            error(f"cases[{index}] must be an object")
            continue
        for field in (
            "id",
            "category",
            "source_baseline_case",
            "source_family_id",
            "worker_case",
            "expected_material_change",
            "expected_body_count",
            "expected_candidate_boolean_operations",
            "expected_deferred_zero_measure_contacts",
            "expected_deduplicated_events",
        ):
            if field not in item:
                error(f"cases[{index}] missing {field}")

report_path = ROOT / "docs/17-REGULARIZED-DEFERRED-TOPOLOGY.md"
if report_path.is_file():
    report = report_path.read_text(encoding="utf-8")
    required_terms = (
        "## Hypotheses and falsification criteria",
        "## Precise programme definition — regularized material solid",
        "cl(int(A \\ B))",
        "## Precise programme definition — deferred topology",
        "## Lower-dimensional debris versus meaningful contact",
        "## Interaction with RCS-007 tolerance/uncertainty",
        "## Interaction with RCS-008 provenance and identity",
        "## Reconciliation boundaries",
        "## OCCT General Fuse / CellsBuilder interpretation",
        "## STEP reconciliation contract",
        "## Failure modes from deferring too much",
        "## Provisional recommendation",
        "## Open questions carried forward",
        "BOPAlgo_CellsBuilder",
        "MEASURED (RCS-007)",
        "MEASURED (RCS-008)",
        EXPECTED_OCCT_COMMIT,
    )
    for term in required_terms:
        if term not in report:
            error(f"RCS-009 report missing required section/term {term!r}")

worker_path = ROOT / "research/rcs-009/harness/deferred_worker.cpp"
if worker_path.is_file():
    worker = worker_path.read_text(encoding="utf-8")
    for term in (
        "rcs-009-deferred-worker/1.0",
        "BOPAlgo_CellsBuilder",
        "SetTools",
        "deferred_zero_measure_contacts",
        "deduplicated_events",
        "connectivity_checkpoint",
        "STEPControl_Writer",
        EXPECTED_OCCT_COMMIT,
    ):
        if term not in worker:
            error(f"RCS-009 worker missing required concept {term!r}")

runner_path = ROOT / "research/rcs-009/harness/run_deferred_campaign.py"
if runner_path.is_file():
    runner = runner_path.read_text(encoding="utf-8")
    for term in (
        "rcs-009-results/1.0",
        "candidate_material_oracle",
        "baseline_physical_oracle",
        "cells_builder_probe_equivalent",
        "step_automated_roundtrip",
        "candidate_failures",
    ):
        if term not in runner:
            error(f"RCS-009 campaign runner missing required concept {term!r}")

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
        if results.get("results_schema") != "rcs-009-results/1.0":
            error("unexpected RCS-009 runtime result schema")
        backend = results.get("backend")
        if not isinstance(backend, dict) or backend.get("commit") != EXPECTED_OCCT_COMMIT:
            error("runtime results do not report exact OCCT commit")
        records = results.get("records")
        if not isinstance(records, list):
            error("runtime results records must be a list")
            records = []
        record_ids = {item.get("case_id") for item in records if isinstance(item, dict)}
        if results.get("profile") == "smoke" and record_ids != EXPECTED_SMOKE:
            error(f"runtime smoke cases incomplete: {sorted(record_ids)}")
        for index, item in enumerate(records):
            if not isinstance(item, dict):
                error(f"records[{index}] must be an object")
                continue
            candidate_record = item.get("candidate")
            if not isinstance(candidate_record, dict) or candidate_record.get("status") != "measured":
                error(f"records[{index}] candidate worker did not complete")
                continue
            payload = candidate_record.get("payload")
            if not isinstance(payload, dict) or payload.get("worker_schema") != "rcs-009-deferred-worker/1.0":
                error(f"records[{index}] candidate payload schema invalid")
            if item.get("failures"):
                error(f"records[{index}] reports candidate contract failures: {item.get('failures')}")

        summary = results.get("summary")
        required_summary = {
            "cases",
            "candidate_failures",
            "baseline_measured_cases",
            "candidate_measured_cases",
            "baseline_physical_oracle_passes",
            "candidate_physical_oracle_passes",
            "baseline_candidate_volume_equivalent_cases",
            "deferred_zero_measure_contacts",
            "deduplicated_events",
            "baseline_boolean_operations",
            "candidate_boolean_operations",
            "cells_builder_probes",
            "cells_builder_measured",
            "cells_builder_equivalent",
            "step_attempts",
            "step_passes",
        }
        if not isinstance(summary, dict) or not required_summary.issubset(summary):
            error("runtime summary incomplete")
        else:
            if summary.get("candidate_failures") != 0:
                error("runtime summary reports candidate failures")
            if summary.get("candidate_measured_cases") != summary.get("cases"):
                error("not every candidate case was measured")
            if summary.get("candidate_physical_oracle_passes") != summary.get("cases"):
                error("candidate failed one or more physical/body oracles")
            if int(summary.get("deferred_zero_measure_contacts", 0)) < 2:
                error("runtime evidence did not exercise both zero-measure contact deferrals")
            if int(summary.get("deduplicated_events", 0)) < 200:
                error("runtime evidence did not exercise repeated-pass geometry elision")
            if int(summary.get("candidate_boolean_operations", 0)) >= int(summary.get("baseline_boolean_operations", 0)):
                error("candidate did not reduce topology materialization count versus baseline")
            if int(summary.get("cells_builder_probes", 0)) < 2:
                error("runtime evidence lacks required CellsBuilder probes")
            if int(summary.get("step_attempts", 0)) < 1 or summary.get("step_passes") != summary.get("step_attempts"):
                error("reconciled STEP round-trip evidence did not pass")

if errors:
    print("RCS-009 validation failed:")
    for item in errors:
        print(f" - {item}")
    sys.exit(1)

print("RCS-009 validation passed")
