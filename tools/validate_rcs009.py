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
EXPECTED_RUN = 35212264059
EXPECTED_JOB = 105172585743
EXPECTED_ARTIFACT = 10491869655
EXPECTED_DIGEST = "sha256:3b1c761b3cbf60dd6451ba6f6b25fc0970acc5ba5b484ce6f7f0133f1bdf9def"
EXPECTED_CATEGORIES = {
    "lower_dimensional_contact", "tangent_entry_exit", "sliver",
    "repeated_pass", "overlapping_removal", "connectivity_split",
}
EXPECTED_SMOKE = {
    "face-contact-zero", "tangent-contact-zero", "tangent-overlap-1um",
    "thin-skim-0.1um", "repeated-slot-20", "repeated-slot-200",
    "overlapping-slots", "mill-cut-through",
}
REQUIRED_FILES = (
    ROOT / "docs/17-REGULARIZED-DEFERRED-TOPOLOGY.md",
    ROOT / "docs/decisions/DR-0012-regularized-material-and-bounded-deferred-topology.md",
    ROOT / "research/rcs-009/README.md",
    ROOT / "research/rcs-009/experiment-plan-v1.json",
    ROOT / "research/rcs-009/measured-summary-v1.json",
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


def validate_summary(summary: Any, where: str) -> None:
    if not isinstance(summary, dict):
        error(f"{where}: summary must be an object")
        return
    required = {
        "cases", "candidate_failures", "baseline_measured_cases", "candidate_measured_cases",
        "baseline_physical_oracle_passes", "candidate_physical_oracle_passes",
        "baseline_candidate_volume_equivalent_cases", "baseline_candidate_bbox_equivalent_cases",
        "deferred_zero_measure_contacts", "deduplicated_events", "baseline_boolean_operations",
        "candidate_boolean_operations", "cells_builder_probes", "cells_builder_measured",
        "cells_builder_equivalent", "step_attempts", "step_passes",
    }
    if not required.issubset(summary):
        error(f"{where}: summary missing fields {sorted(required - set(summary))}")
        return
    exact = {
        "cases": 8,
        "candidate_failures": 0,
        "baseline_measured_cases": 8,
        "candidate_measured_cases": 8,
        "baseline_physical_oracle_passes": 8,
        "candidate_physical_oracle_passes": 8,
        "baseline_candidate_volume_equivalent_cases": 8,
        "baseline_candidate_bbox_equivalent_cases": 8,
        "deferred_zero_measure_contacts": 2,
        "deduplicated_events": 218,
        "baseline_boolean_operations": 227,
        "candidate_boolean_operations": 6,
        "cells_builder_probes": 2,
        "cells_builder_measured": 2,
        "cells_builder_equivalent": 2,
        "step_attempts": 1,
        "step_passes": 1,
    }
    for key, expected in exact.items():
        if summary.get(key) != expected:
            error(f"{where}: {key}={summary.get(key)!r}, expected pinned measured value {expected!r}")


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
    profiles = plan.get("profiles")
    smoke = set(profiles.get("smoke", [])) if isinstance(profiles, dict) else set()
    if smoke != EXPECTED_SMOKE:
        error(f"RCS-009 smoke profile must contain exactly the founding smoke set; observed {sorted(smoke)}")
    if not smoke.issubset(case_ids):
        error("smoke profile references missing cases")
    if not any(isinstance(item, dict) and item.get("probe_cells_builder") for item in cases):
        error("experiment plan must include CellsBuilder probes")
    if not any(isinstance(item, dict) and item.get("step", {}).get("enabled") for item in cases):
        error("experiment plan must include reconciled STEP round-trip coverage")
    for index, item in enumerate(cases):
        if not isinstance(item, dict):
            error(f"cases[{index}] must be an object")
            continue
        for field in (
            "id", "category", "source_baseline_case", "source_family_id", "worker_case",
            "expected_material_change", "expected_body_count", "expected_candidate_boolean_operations",
            "expected_deferred_zero_measure_contacts", "expected_deduplicated_events",
        ):
            if field not in item:
                error(f"cases[{index}] missing {field}")

measured_path = ROOT / "research/rcs-009/measured-summary-v1.json"
measured = load_object(measured_path) if measured_path.is_file() else {}
if measured:
    if measured.get("schema") != "rcs-009-measured-summary/1.0":
        error("unexpected RCS-009 measured-summary schema")
    source = measured.get("source")
    if not isinstance(source, dict):
        error("measured-summary source must be an object")
    else:
        expected_source = {
            "workflow_run_id": EXPECTED_RUN,
            "job_id": EXPECTED_JOB,
            "artifact_id": EXPECTED_ARTIFACT,
            "artifact_digest": EXPECTED_DIGEST,
        }
        for key, expected in expected_source.items():
            if source.get(key) != expected:
                error(f"measured-summary source {key} mismatch")
    backend = measured.get("backend")
    if not isinstance(backend, dict) or backend.get("commit") != EXPECTED_OCCT_COMMIT:
        error("measured-summary backend does not pin exact OCCT commit")
    validate_summary(measured.get("summary"), "measured-summary")
    reps = measured.get("representative_measurements")
    if not isinstance(reps, dict):
        error("measured-summary representative_measurements missing")
    else:
        cut = reps.get("mill_cut_through", {})
        if cut.get("expected_and_candidate_solids") != 2 or not cut.get("step_roundtrip_passed"):
            error("measured-summary must preserve two-body cut-through STEP evidence")
        skim = reps.get("thin_skim_0_1um", {})
        if skim.get("candidate_boolean_operations") != 1 or skim.get("volume_abs_delta_mm3") != 0.0:
            error("measured-summary must preserve positive-volume thin-skim evidence")

report_path = ROOT / "docs/17-REGULARIZED-DEFERRED-TOPOLOGY.md"
if report_path.is_file():
    report = report_path.read_text(encoding="utf-8")
    for term in (
        "Status: accepted RCS-009 research result",
        "## Hypotheses and falsification criteria",
        "## Precise programme definition — regularized material solid", "cl(int(A \\ B))",
        "## Precise programme definition — deferred topology",
        "## Lower-dimensional debris versus meaningful contact",
        "## Interaction with RCS-007 tolerance/uncertainty",
        "## Interaction with RCS-008 provenance and identity",
        "## Reconciliation boundaries", "## Measured RCS-009 results",
        "## OCCT General Fuse / CellsBuilder interpretation", "## STEP reconciliation contract",
        "## Failure modes from deferring too much", "## Architecture recommendation",
        "## Open questions carried forward", "BOPAlgo_CellsBuilder", "MEASURED (RCS-007)",
        "MEASURED (RCS-008)", str(EXPECTED_RUN), str(EXPECTED_ARTIFACT), EXPECTED_OCCT_COMMIT,
    ):
        if term not in report:
            error(f"RCS-009 report missing required section/term {term!r}")

decision_path = ROOT / "docs/decisions/DR-0012-regularized-material-and-bounded-deferred-topology.md"
if decision_path.is_file():
    decision = decision_path.read_text(encoding="utf-8")
    for term in ("Status: accepted", "## Decision", "## Evidence", str(EXPECTED_RUN), EXPECTED_DIGEST):
        if term not in decision:
            error(f"DR-0012 missing accepted measured evidence term {term!r}")

worker_path = ROOT / "research/rcs-009/harness/deferred_worker.cpp"
if worker_path.is_file():
    worker = worker_path.read_text(encoding="utf-8")
    for term in (
        "rcs-009-deferred-worker/1.0", "BOPAlgo_CellsBuilder", "SetTools",
        "deferred_zero_measure_contacts", "deduplicated_events", "connectivity_checkpoint",
        "STEPControl_Writer", EXPECTED_OCCT_COMMIT,
    ):
        if term not in worker:
            error(f"RCS-009 worker missing required concept {term!r}")

runner_path = ROOT / "research/rcs-009/harness/run_deferred_campaign.py"
if runner_path.is_file():
    runner = runner_path.read_text(encoding="utf-8")
    for term in (
        "rcs-009-results/1.0", "candidate_material_oracle", "baseline_physical_oracle",
        "cells_builder_probe_equivalent", "step_automated_roundtrip", "candidate_failures",
        "decode_worker_stdout",
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
        validate_summary(results.get("summary"), "runtime-results")

if errors:
    print("RCS-009 validation failed:")
    for item in errors:
        print(f" - {item}")
    sys.exit(1)

print("RCS-009 validation passed")
