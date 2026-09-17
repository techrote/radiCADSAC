#!/usr/bin/env python3
"""Validate RCS-007 virtual-tolerance research contracts and optional runtime artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_OCCT_COMMIT = "b8f597c677811d1f9f4d8a97f5ae2825c0353a42"
EXPECTED_CHANNELS = {
    "input_sampling_resolution",
    "machine_control_resolution",
    "manufacturing_tolerance",
    "numerical_uncertainty",
    "topological_equivalence",
    "contact_classification",
    "preview_tolerance",
    "export_tolerance",
    "validation_tolerance",
}
EXPECTED_MODELS = {
    "occt_global_fuzzy",
    "operation_local_interval",
    "semantic_replay_collapse",
    "anchored_quantization",
    "controlled_perturbation",
}

REQUIRED_FILES = (
    ROOT / "docs/15-VIRTUAL-TOLERANCE-RESEARCH.md",
    ROOT / "research/rcs-007/README.md",
    ROOT / "research/rcs-007/experiment-plan-v1.json",
    ROOT / "research/rcs-007/harness/CMakeLists.txt",
    ROOT / "research/rcs-007/harness/repeated_finish_worker.cpp",
    ROOT / "research/rcs-007/harness/run_tolerance_campaign.py",
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

plan_path = ROOT / "research/rcs-007/experiment-plan-v1.json"
plan = load_object(plan_path) if plan_path.is_file() else {}
if plan:
    if plan.get("experiment_plan_schema") != "rcs-007-experiment-plan/1.0":
        error("unexpected RCS-007 experiment plan schema")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        error("plan baseline must be an object")
    else:
        if baseline.get("version") != "8.0.1":
            error("RCS-007 baseline must pin OCCT 8.0.1")
        if baseline.get("commit") != EXPECTED_OCCT_COMMIT:
            error("RCS-007 baseline commit does not match accepted OCCT pin")
    channels = plan.get("policy_channels")
    if not isinstance(channels, list) or set(channels) != EXPECTED_CHANNELS:
        error("policy_channels must contain the nine distinct RCS-007 channels")
    models = plan.get("candidate_models")
    model_ids = {
        item.get("id")
        for item in models
        if isinstance(models, list) and isinstance(item, dict)
    } if isinstance(models, list) else set()
    if not EXPECTED_MODELS.issubset(model_ids):
        error(f"candidate models missing: {sorted(EXPECTED_MODELS - model_ids)}")
    profiles = plan.get("profiles")
    if not isinstance(profiles, dict) or not {"smoke", "baseline"}.issubset(profiles):
        error("plan must define smoke and baseline profiles")
    sweeps = plan.get("backend_sweeps")
    families = {
        item.get("family")
        for item in sweeps
        if isinstance(sweeps, list) and isinstance(item, dict)
    } if isinstance(sweeps, list) else set()
    required_families = {"coincidence", "tangency", "sub_tolerance_skim"}
    if not required_families.issubset(families):
        error(f"backend sweeps missing: {sorted(required_families - families)}")
    if not isinstance(plan.get("repeated_finish"), dict):
        error("plan missing repeated_finish experiment")
    if not isinstance(plan.get("accumulation_chain"), dict):
        error("plan missing accumulation_chain experiment")

report_path = ROOT / "docs/15-VIRTUAL-TOLERANCE-RESEARCH.md"
if report_path.is_file():
    report = report_path.read_text(encoding="utf-8")
    required_terms = (
        "## Hypotheses and falsification criteria",
        "## Policy channels are not one epsilon",
        "## Candidate model A — OCCT global fuzzy Boolean",
        "## Candidate model B — operation-local interval classification",
        "## Candidate model C — semantic replay collapse",
        "## Anchored quantization",
        "## Controlled perturbation",
        "## Algebraic properties and failure modes",
        "## Export and STEP reconciliation",
        "## Provisional architecture recommendation",
        "RCS-008",
        "RCS-009",
        EXPECTED_OCCT_COMMIT,
    )
    for term in required_terms:
        if term not in report:
            error(f"research report missing required section/term {term!r}")

runner_path = ROOT / "research/rcs-007/harness/run_tolerance_campaign.py"
if runner_path.is_file():
    runner = runner_path.read_text(encoding="utf-8")
    for term in (
        "operation_local_interval",
        "semantic_replay_collapse",
        "controlled_perturbation",
        "accumulation_chains",
        "rcs-007-results/1.0",
    ):
        if term not in runner:
            error(f"campaign runner missing required concept {term!r}")

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
        if results.get("results_schema") != "rcs-007-results/1.0":
            error("unexpected runtime result schema")
        backend = results.get("backend")
        if not isinstance(backend, dict) or backend.get("commit") != EXPECTED_OCCT_COMMIT:
            error("runtime results do not report the exact OCCT commit")
        channels = results.get("policy_channels")
        if not isinstance(channels, list) or set(channels) != EXPECTED_CHANNELS:
            error("runtime results lost tolerance policy channels")
        sweeps = results.get("backend_sweeps")
        if not isinstance(sweeps, list) or len(sweeps) < 10:
            error("runtime backend sweeps are unexpectedly small")
        else:
            families = {item.get("family") for item in sweeps if isinstance(item, dict)}
            if not {"coincidence", "tangency", "sub_tolerance_skim"}.issubset(families):
                error("runtime backend sweeps lack required fixture families")
            measured = [
                item for item in sweeps
                if isinstance(item, dict)
                and isinstance(item.get("worker"), dict)
                and isinstance(item["worker"].get("payload"), dict)
            ]
            if len(measured) != len(sweeps):
                error("one or more runtime backend sweep attempts did not produce worker payloads")
        repeated = results.get("repeated_finishing")
        if not isinstance(repeated, list) or not any(
            isinstance(item, dict) and int(item.get("repeat_count", 0)) > 1
            for item in repeated
        ):
            error("runtime results lack repeated finishing passes")
        chains = results.get("accumulation_chains")
        if not isinstance(chains, list) or not chains:
            error("runtime results lack tolerance accumulation chains")
        else:
            for item in chains:
                if not isinstance(item, dict):
                    continue
                orders = item.get("orders")
                if not isinstance(orders, dict) or not {"ascending", "descending"}.issubset(orders):
                    error("accumulation chain does not contain both operation orders")
                    break
        perturb = results.get("controlled_perturbation")
        if not isinstance(perturb, list) or not perturb:
            error("runtime results lack controlled perturbation pairs")
        algebraic = results.get("algebraic")
        if not isinstance(algebraic, dict):
            error("runtime results lack algebraic consistency evidence")
        summary = results.get("summary")
        if not isinstance(summary, dict):
            error("runtime results lack aggregate summary")

if errors:
    print("RCS-007 validation failed:")
    for item in errors:
        print(f" - {item}")
    sys.exit(1)

print("RCS-007 validation passed")
