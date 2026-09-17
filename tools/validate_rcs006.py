#!/usr/bin/env python3
"""Validate RCS-006 benchmark harness contracts and optional campaign output."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COMMIT = "b8f597c677811d1f9f4d8a97f5ae2825c0353a42"
EXPECTED_VERSION = "8.0.1"

REQUIRED_FILES = (
    ROOT / "docs/14-BASELINE-BENCHMARK-HARNESS.md",
    ROOT / "research/rcs-006/README.md",
    ROOT / "research/rcs-006/benchmark-plan-v1.json",
    ROOT / "research/rcs-006/result.schema.json",
    ROOT / "research/rcs-006/harness/CMakeLists.txt",
    ROOT / "research/rcs-006/harness/bootstrap_occt.sh",
    ROOT / "research/rcs-006/harness/occt_worker.cpp",
    ROOT / "research/rcs-006/harness/run_campaign.py",
)

FAILURE_TAXONOMY = {
    "success",
    "rejected input",
    "algorithm returned error/status",
    "invalid topology",
    "valid topology but wrong geometry",
    "geometric tolerance breach",
    "crash",
    "hang/timeout",
    "excessive runtime",
    "excessive memory",
    "nondeterministic result",
    "STEP writer failure",
    "STEP round-trip failure",
    "downstream consumer failure",
}

REQUIRED_SMOKE_CASES = {
    "coincident-face-zero",
    "tangent-contact-zero",
    "thin-skim-1um",
    "repeated-slot-20",
    "repeated-slot-200",
    "lathe-od-finish",
    "lathe-parting",
    "mill-cut-through",
    "step-cylinder-mm",
    "step-block-inch",
}

errors: list[str] = []


def error(message: str) -> None:
    errors.append(message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        error(f"{path.relative_to(ROOT)}: cannot parse JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        error(f"{path.relative_to(ROOT)}: root must be an object")
        return {}
    return value


def validate_static() -> dict[str, Any]:
    for path in REQUIRED_FILES:
        if not path.is_file():
            error(f"missing required file: {path.relative_to(ROOT)}")

    plan = load_json(ROOT / "research/rcs-006/benchmark-plan-v1.json")
    if plan.get("benchmark_plan_schema") != "rcs-006-benchmark-plan/1.0":
        error("benchmark plan has unexpected schema")
    backend = plan.get("backend") or {}
    if backend.get("id") != "occt" or backend.get("version") != EXPECTED_VERSION:
        error("benchmark plan must identify OCCT 8.0.1 baseline")
    if backend.get("tag") != "V8_0_1" or backend.get("commit") != EXPECTED_COMMIT:
        error("benchmark plan must pin V8_0_1 and accepted commit")
    if backend.get("run_parallel") is not False or backend.get("non_destructive_booleans") is not True:
        error("baseline execution policy must be single-threaded and non-destructive")

    corpus = load_json(ROOT / "research/rcs-003/corpus-v1.json")
    family_ids = {item.get("id") for item in corpus.get("fixture_families", []) if isinstance(item, dict)}
    step_matrix = load_json(ROOT / "research/rcs-005/fixtures-v1.json")
    step_ids = {item.get("fixture_id") for item in step_matrix.get("fixtures", []) if isinstance(item, dict)}

    cases = plan.get("cases")
    case_ids: set[str] = set()
    if not isinstance(cases, list):
        error("benchmark plan cases must be a list")
        cases = []
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            error(f"cases[{index}] must be an object")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            error(f"cases[{index}] missing id")
            continue
        if case_id in case_ids:
            error(f"duplicate benchmark case id {case_id}")
        case_ids.add(case_id)
        if case.get("source_family_id") not in family_ids:
            error(f"{case_id}: source_family_id does not resolve in RCS-003")
        step_fixture = case.get("step_fixture_id")
        if step_fixture is not None and step_fixture not in step_ids:
            error(f"{case_id}: step_fixture_id does not resolve in RCS-005")
        if case.get("expected_classification") not in {
            "no_material_change",
            "regularized_material_change",
            "body_separation_or_merge",
            "ambiguous_or_unsupported",
        }:
            error(f"{case_id}: invalid expected physical classification")
        if not isinstance(case.get("expected_body_count"), int) or case["expected_body_count"] < 1:
            error(f"{case_id}: expected_body_count must be positive integer")

    profiles = plan.get("profiles") or {}
    smoke = set(profiles.get("smoke", []))
    baseline = set(profiles.get("baseline", []))
    if smoke != REQUIRED_SMOKE_CASES:
        error(f"smoke profile must contain exact required coverage set: {sorted(REQUIRED_SMOKE_CASES)}")
    if not smoke.issubset(baseline):
        error("smoke profile must be a subset of baseline profile")
    if not baseline.issubset(case_ids):
        error("baseline profile contains unknown case IDs")

    repeated_200 = next((case for case in cases if case.get("id") == "repeated-slot-200"), None)
    if not repeated_200 or (repeated_200.get("parameters") or {}).get("count") != "200":
        error("high-operation-count smoke member must execute 200 repeated operations")

    separation_step = {"lathe-parting", "mill-cut-through"}
    for case in cases:
        if case.get("id") in separation_step and not (case.get("step") or {}).get("enabled"):
            error(f"{case.get('id')}: multi-body STEP round-trip must be enabled")

    result_schema = load_json(ROOT / "research/rcs-006/result.schema.json")
    classification = ((result_schema.get("properties") or {}).get("classification") or {}).get("enum")
    if not isinstance(classification, list) or set(classification) != FAILURE_TAXONOMY:
        error("result schema classification enum must match research failure taxonomy plus success")

    worker_text = (ROOT / "research/rcs-006/harness/occt_worker.cpp").read_text(encoding="utf-8") if (ROOT / "research/rcs-006/harness/occt_worker.cpp").is_file() else ""
    for required in (
        EXPECTED_COMMIT,
        "OCC_VERSION_COMPLETE",
        "SetRunParallel(false)",
        "SetNonDestructive(true)",
        "BRepCheck_Analyzer",
        "STEPControl_Writer",
        "STEPControl_Reader",
        "DESTEP_Parameters",
        "max_rss_kb",
    ):
        if required not in worker_text:
            error(f"OCCT worker missing required evidence/behavior {required!r}")

    runner_text = (ROOT / "research/rcs-006/harness/run_campaign.py").read_text(encoding="utf-8") if (ROOT / "research/rcs-006/harness/run_campaign.py").is_file() else ""
    for required in ("subprocess.run", "TimeoutExpired", "stable_signature", "results.jsonl", "summary.md"):
        if required not in runner_text:
            error(f"campaign runner missing required isolation/result feature {required!r}")

    bootstrap_text = (ROOT / "research/rcs-006/harness/bootstrap_occt.sh").read_text(encoding="utf-8") if (ROOT / "research/rcs-006/harness/bootstrap_occt.sh").is_file() else ""
    for required in (EXPECTED_COMMIT, "git -C", "checkout --detach", "BUILD_LIBRARY_TYPE=Shared", "BUILD_CPP_STANDARD=C++17"):
        if required not in bootstrap_text:
            error(f"bootstrap script missing pin/build requirement {required!r}")

    doc_text = (ROOT / "docs/14-BASELINE-BENCHMARK-HARNESS.md").read_text(encoding="utf-8") if (ROOT / "docs/14-BASELINE-BENCHMARK-HARNESS.md").is_file() else ""
    for required in (
        "## Process isolation and timeout doctrine",
        "## Result schema",
        "## Failure taxonomy",
        "## Founding experiment set",
        "## STEP integration",
        "## Parameter sweeps",
        "RCS-017",
    ):
        if required not in doc_text:
            error(f"harness report missing required section/term {required!r}")

    return plan


def validate_runtime(results_dir: Path, plan: dict[str, Any]) -> None:
    campaign_path = results_dir / "campaign.json"
    results_path = results_dir / "results.jsonl"
    summary_path = results_dir / "summary.md"
    for path in (campaign_path, results_path, summary_path):
        if not path.is_file():
            error(f"runtime artifact missing: {path}")
    if errors:
        return

    campaign = load_json(campaign_path)
    if campaign.get("campaign_schema") != "rcs-006-campaign/1.0":
        error("runtime campaign has unexpected schema")
    backend = campaign.get("backend") or {}
    if backend.get("commit") != EXPECTED_COMMIT or backend.get("version") != EXPECTED_VERSION:
        error("runtime campaign does not report pinned OCCT baseline")
    if campaign.get("profile") != "smoke":
        error("CI runtime validation expects smoke profile")
    if int(campaign.get("repeats", 0)) < 2:
        error("smoke campaign must repeat cases at least twice for nondeterminism detection")

    records: list[dict[str, Any]] = []
    for lineno, line in enumerate(results_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            error(f"results.jsonl:{lineno}: invalid JSON: {exc}")
            continue
        if not isinstance(record, dict):
            error(f"results.jsonl:{lineno}: result must be object")
            continue
        records.append(record)
        if record.get("result_schema") != "rcs-006-result/1.0":
            error(f"results.jsonl:{lineno}: unexpected result_schema")
        if record.get("classification") not in FAILURE_TAXONOMY:
            error(f"results.jsonl:{lineno}: unknown classification")

    by_case: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        if isinstance(record.get("case_id"), str):
            by_case[record["case_id"]].append(record)
    if set(by_case) != REQUIRED_SMOKE_CASES:
        error(f"runtime smoke coverage mismatch: {sorted(by_case)}")
    for case_id in REQUIRED_SMOKE_CASES:
        if len(by_case.get(case_id, [])) < 2:
            error(f"runtime case {case_id} lacks repeated attempts")

    step_attempts = 0
    for case_id in {"lathe-parting", "mill-cut-through", "step-cylinder-mm", "step-block-inch"}:
        for record in by_case.get(case_id, []):
            worker = record.get("worker")
            if isinstance(worker, dict) and isinstance(worker.get("step"), dict) and worker["step"].get("attempted"):
                step_attempts += 1
    if step_attempts == 0:
        error("runtime smoke campaign produced no STEP attempt metrics")

    if len(records) != int(campaign.get("record_count", -1)):
        error("campaign record_count does not match results.jsonl")
    counts = Counter(record.get("classification") for record in records)
    if dict(sorted(counts.items())) != campaign.get("classification_counts"):
        error("campaign classification_counts do not match results.jsonl")

    summary = summary_path.read_text(encoding="utf-8")
    for case_id in REQUIRED_SMOKE_CASES:
        if case_id not in summary:
            error(f"summary.md missing smoke case {case_id}")


parser = argparse.ArgumentParser()
parser.add_argument("--results-dir", type=Path)
args = parser.parse_args()
plan = validate_static()
if args.results_dir is not None and not errors:
    validate_runtime(args.results_dir, plan)

if errors:
    print("RCS-006 harness validation failed:")
    for item in errors:
        print(f" - {item}")
    sys.exit(1)

if args.results_dir is None:
    print(f"RCS-006 static validation passed ({len(REQUIRED_SMOKE_CASES)} smoke cases)")
else:
    print(f"RCS-006 runtime validation passed ({len(REQUIRED_SMOKE_CASES)} repeated smoke cases)")
