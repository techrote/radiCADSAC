#!/usr/bin/env python3
"""Validate RCS-012 alternative/hybrid geometry research artifacts and runtime evidence."""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    ROOT / "docs/19-ALTERNATIVE-HYBRID-GEOMETRY-REPRESENTATIONS.md",
    ROOT / "research/rcs-012/README.md",
    ROOT / "research/rcs-012/experiment-plan-v1.json",
    ROOT / "research/rcs-012/measured-summary-v1.json",
    ROOT / "research/rcs-012/harness/run_campaign.py",
)

REQUIRED_EXPERIMENT_CANDIDATES = {
    "exact-orthogonal-cell-deferred-csg",
    "sparse-voxel-center-0p5mm",
}

REQUIRED_SOURCE_REVIEWS = {
    "cgal-epeck": ("CGAL 6.2.1", "v6.2.1", "Kernel_23: LGPL v3 or later"),
    "cgal-nef3": ("CGAL 6.2.1", "v6.2.1", "Nef_3: GPL v3 or later"),
    "manifold": ("Manifold 3.5.3", "v3.5.3", "Apache-2.0"),
    "openvdb": ("OpenVDB 13.1.0", "v13.1.0", "Apache-2.0"),
}

REQUIRED_SOURCE_FAMILIES = {
    "mill-lower-dimensional-touch",
    "mill-sub-tolerance-plunge",
    "mill-repeated-identical-slot",
    "mill-overlapping-slots-pockets",
    "mill-cut-through-separation",
    "mill-tiny-cusp",
    "mill-very-high-segment-count",
    "mill-tangent-corner-entry-exit",
}

EXPECTED_REFERENCE = {
    "exact-orthogonal-cell-deferred-csg": {
        "cases": 8,
        "attempts": 16,
        "oracle_volume_exact_attempts": 16,
        "oracle_body_exact_attempts": 16,
        "nondeterministic_case_groups": 0,
        "max_volume_error_mm3": Decimal("0"),
    },
    "sparse-voxel-center-0p5mm": {
        "cases": 8,
        "attempts": 16,
        "oracle_volume_exact_attempts": 12,
        "oracle_body_exact_attempts": 14,
        "nondeterministic_case_groups": 0,
        "max_volume_error_mm3": Decimal("0.2"),
    },
}

errors: list[str] = []


def error(message: str) -> None:
    errors.append(message)


def load_object(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        error(f"missing required file: {path.relative_to(ROOT)}")
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        error(f"{label} is not valid JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        error(f"{label} root must be an object")
        return {}
    return value


def decimal(value: Any, where: str) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception:
        error(f"{where}: expected decimal-compatible value, got {value!r}")
        return Decimal("NaN")


for path in REQUIRED_FILES:
    if not path.is_file():
        error(f"missing required file: {path.relative_to(ROOT)}")

plan_path = ROOT / "research/rcs-012/experiment-plan-v1.json"
plan = load_object(plan_path, "experiment plan")
if plan:
    if plan.get("schema") != "rcs-012-plan/1.0":
        error("experiment plan schema must be rcs-012-plan/1.0")
    if plan.get("campaign") != "alternative-hybrid-geometry":
        error("unexpected RCS-012 campaign id")

    fixture_policy = plan.get("shared_fixture_policy")
    if not isinstance(fixture_policy, dict):
        error("shared_fixture_policy must be an object")
    else:
        if fixture_policy.get("units") != "mm":
            error("RCS-012 shared fixtures must use mm")
        if fixture_policy.get("frame") != "right-handed-z-up-workpiece-v1":
            error("RCS-012 shared fixture frame must match the accepted corpus")
        if fixture_policy.get("source") != "research/rcs-003/corpus-v1.json":
            error("RCS-012 shared fixture source must point to the accepted RCS-003 corpus")

    candidates = plan.get("candidates")
    experiment_ids: set[str] = set()
    if not isinstance(candidates, list):
        error("candidates must be a list")
    else:
        for index, candidate in enumerate(candidates):
            if not isinstance(candidate, dict):
                error(f"candidates[{index}] must be an object")
                continue
            candidate_id = candidate.get("id")
            if candidate.get("kind") == "experiment" and isinstance(candidate_id, str):
                experiment_ids.add(candidate_id)
            for field in ("id", "kind", "implementation", "analytic_semantics", "step_reconciliation"):
                if not isinstance(candidate.get(field), str) or not candidate[field].strip():
                    error(f"candidates[{index}].{field} must be a non-empty string")
        missing_experiments = REQUIRED_EXPERIMENT_CANDIDATES - experiment_ids
        if missing_experiments:
            error(f"missing executable non-OCCT candidates: {sorted(missing_experiments)}")
        if len(experiment_ids) < 2:
            error("RCS-012 must exercise at least two non-OCCT candidates")

    source_review = plan.get("source_review")
    observed_reviews: dict[str, dict[str, Any]] = {}
    if not isinstance(source_review, list):
        error("source_review must be a list")
    else:
        for index, item in enumerate(source_review):
            if not isinstance(item, dict):
                error(f"source_review[{index}] must be an object")
                continue
            item_id = item.get("id")
            if isinstance(item_id, str):
                observed_reviews[item_id] = item
        for source_id, (version, release, license_text) in REQUIRED_SOURCE_REVIEWS.items():
            item = observed_reviews.get(source_id)
            if item is None:
                error(f"missing source review {source_id}")
                continue
            if item.get("version") != version:
                error(f"{source_id}: expected version {version!r}")
            if item.get("release") != release:
                error(f"{source_id}: expected release {release!r}")
            if item.get("license") != license_text:
                error(f"{source_id}: expected license {license_text!r}")

    cases = plan.get("cases")
    family_ids: set[str] = set()
    case_ids: set[str] = set()
    if not isinstance(cases, list):
        error("cases must be a list")
    else:
        if len(cases) < 8:
            error("experiment plan must retain at least eight representative shared cases")
        for index, case in enumerate(cases):
            if not isinstance(case, dict):
                error(f"cases[{index}] must be an object")
                continue
            case_id = case.get("id")
            family = case.get("source_family")
            if not isinstance(case_id, str) or not case_id:
                error(f"cases[{index}].id must be non-empty")
            elif case_id in case_ids:
                error(f"duplicate case id {case_id}")
            else:
                case_ids.add(case_id)
            if isinstance(family, str):
                family_ids.add(family)
            else:
                error(f"cases[{index}].source_family must be a string")
            for field in ("stock", "removals", "expected"):
                if field not in case:
                    error(f"cases[{index}] missing {field}")
        missing_families = REQUIRED_SOURCE_FAMILIES - family_ids
        if missing_families:
            error(f"missing required shared fixture families: {sorted(missing_families)}")

measured_path = ROOT / "research/rcs-012/measured-summary-v1.json"
measured = load_object(measured_path, "measured summary")
if measured:
    if measured.get("schema") != "rcs-012-measured-summary/1.0":
        error("unexpected measured-summary schema")
    if measured.get("campaign") != "alternative-hybrid-geometry":
        error("measured summary campaign mismatch")
    result_summary = measured.get("result_summary")
    if not isinstance(result_summary, dict):
        error("measured summary result_summary must be an object")
    else:
        if result_summary.get("schema") != "rcs-012-summary/1.0":
            error("measured result summary schema mismatch")
        if result_summary.get("case_count") != 8:
            error("reference measurement must cover eight cases")
        if result_summary.get("candidate_count") != 2:
            error("reference measurement must cover two candidates")
        candidate_metrics = result_summary.get("candidates")
        if not isinstance(candidate_metrics, dict):
            error("reference candidate metrics must be an object")
        else:
            for candidate_id, expected in EXPECTED_REFERENCE.items():
                actual = candidate_metrics.get(candidate_id)
                if not isinstance(actual, dict):
                    error(f"reference measurement missing candidate {candidate_id}")
                    continue
                for key, expected_value in expected.items():
                    actual_value = actual.get(key)
                    if isinstance(expected_value, Decimal):
                        if decimal(actual_value, f"{candidate_id}.{key}") != expected_value:
                            error(f"{candidate_id}.{key} reference result changed unexpectedly")
                    elif actual_value != expected_value:
                        error(
                            f"{candidate_id}.{key}: expected {expected_value!r}, got {actual_value!r}"
                        )

    decisive = measured.get("decisive_cases")
    if not isinstance(decisive, dict):
        error("measured summary must record decisive_cases")
    else:
        plunge = decisive.get("tiny-plunge-1um", {})
        cusp = decisive.get("tiny-cusp-1um", {})
        if not isinstance(plunge, dict) or decimal(
            plunge.get("voxel_0p5", {}).get("volume_error_mm3"), "tiny-plunge voxel error"
        ) != Decimal("0.1"):
            error("reference evidence must retain the 0.1 mm^3 voxel plunge miss")
        if not isinstance(cusp, dict) or decimal(
            cusp.get("voxel_0p5", {}).get("volume_error_mm3"), "tiny-cusp voxel error"
        ) != Decimal("0.2"):
            error("reference evidence must retain the 0.2 mm^3 voxel cusp loss")
        if isinstance(cusp, dict) and cusp.get("voxel_0p5", {}).get("body_count") != 0:
            error("reference evidence must retain the voxel cusp body-loss counterexample")

report_path = ROOT / "docs/19-ALTERNATIVE-HYBRID-GEOMETRY-REPRESENTATIONS.md"
if report_path.is_file():
    report = report_path.read_text(encoding="utf-8")
    required_terms = (
        "## Hypotheses and falsification criteria",
        "## Measured results",
        "## Candidate-family trade study",
        "## Primary-source review",
        "## Analytic geometry and STEP reconciliation",
        "## Provenance and semantic identity",
        "## Negative results and rejected interpretations",
        "## Recommendation to RCS-013",
        "## Remaining open questions",
        "CGAL 6.2.1",
        "Manifold 3.5.3",
        "OpenVDB 13.1.0",
        "GPL-3+",
        "Apache-2.0",
        "RCS-005",
        "RCS-008",
        "hybrid representation architecture",
    )
    for term in required_terms:
        if term not in report:
            error(f"trade-study report missing required term/section {term!r}")

parser = argparse.ArgumentParser()
parser.add_argument("--results-dir", type=Path)
args = parser.parse_args()

if args.results_dir is not None:
    summary_path = args.results_dir / "summary.json"
    results_path = args.results_dir / "results.jsonl"
    if not summary_path.is_file():
        error(f"runtime results missing {summary_path}")
    if not results_path.is_file():
        error(f"runtime results missing {results_path}")

    runtime_summary: dict[str, Any] = {}
    if summary_path.is_file():
        try:
            loaded = json.loads(summary_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                runtime_summary = loaded
            else:
                error("runtime summary root must be an object")
        except json.JSONDecodeError as exc:
            error(f"runtime summary is not valid JSON: {exc}")

    runtime_rows: list[dict[str, Any]] = []
    if results_path.is_file():
        for line_no, line in enumerate(results_path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                error(f"results.jsonl line {line_no}: invalid JSON: {exc}")
                continue
            if not isinstance(item, dict):
                error(f"results.jsonl line {line_no}: record must be an object")
                continue
            runtime_rows.append(item)

    if runtime_summary:
        if runtime_summary.get("schema") != "rcs-012-summary/1.0":
            error("runtime summary schema mismatch")
        if runtime_summary.get("case_count") != 8 or runtime_summary.get("candidate_count") != 2:
            error("runtime summary must cover eight cases and two candidates")
        metrics = runtime_summary.get("candidates")
        if not isinstance(metrics, dict):
            error("runtime candidate metrics must be an object")
        else:
            for candidate_id, expected in EXPECTED_REFERENCE.items():
                actual = metrics.get(candidate_id)
                if not isinstance(actual, dict):
                    error(f"runtime summary missing {candidate_id}")
                    continue
                for key, expected_value in expected.items():
                    actual_value = actual.get(key)
                    if isinstance(expected_value, Decimal):
                        if decimal(actual_value, f"runtime {candidate_id}.{key}") != expected_value:
                            error(f"runtime {candidate_id}.{key} does not match reference evidence")
                    elif actual_value != expected_value:
                        error(
                            f"runtime {candidate_id}.{key}: expected {expected_value!r}, got {actual_value!r}"
                        )

    if len(runtime_rows) != 32:
        error(f"runtime campaign must produce 32 attempt records, got {len(runtime_rows)}")
    else:
        seen_groups: set[tuple[str, str, int]] = set()
        for index, row in enumerate(runtime_rows):
            where = f"runtime row {index}"
            if row.get("schema") != "rcs-012-result/1.0":
                error(f"{where}: result schema mismatch")
            candidate_id = row.get("candidate")
            case_id = row.get("case_id")
            attempt = row.get("attempt")
            if candidate_id not in REQUIRED_EXPERIMENT_CANDIDATES:
                error(f"{where}: unknown candidate {candidate_id!r}")
            if not isinstance(case_id, str) or not case_id:
                error(f"{where}: missing case id")
            if attempt not in (1, 2):
                error(f"{where}: attempts must be exactly 1 or 2")
            else:
                key = (str(candidate_id), str(case_id), int(attempt))
                if key in seen_groups:
                    error(f"{where}: duplicate attempt key {key}")
                seen_groups.add(key)
            if row.get("deterministic_engineering_signature") is not True:
                error(f"{where}: engineering signature is not deterministic")
            runtime_ms = row.get("runtime_ms")
            if not isinstance(runtime_ms, (int, float)) or runtime_ms < 0:
                error(f"{where}: runtime_ms must be non-negative")
            if not isinstance(row.get("engineering_signature"), str) or len(row["engineering_signature"]) != 64:
                error(f"{where}: engineering signature must be SHA-256 hex")

        def matching(candidate_id: str, case_id: str) -> list[dict[str, Any]]:
            return [
                row
                for row in runtime_rows
                if row.get("candidate") == candidate_id and row.get("case_id") == case_id
            ]

        for row in matching("exact-orthogonal-cell-deferred-csg", "tiny-plunge-1um"):
            if decimal(row.get("observation", {}).get("volume_error_mm3"), "runtime exact plunge error") != 0:
                error("exact-cell runtime candidate must preserve the tiny plunge exactly")
        for row in matching("sparse-voxel-center-0p5mm", "tiny-plunge-1um"):
            if decimal(row.get("observation", {}).get("volume_error_mm3"), "runtime voxel plunge error") != Decimal("0.1"):
                error("voxel runtime candidate must reproduce the measured tiny-plunge miss")
        for row in matching("exact-orthogonal-cell-deferred-csg", "tiny-cusp-1um"):
            if decimal(row.get("observation", {}).get("volume_error_mm3"), "runtime exact cusp error") != 0:
                error("exact-cell runtime candidate must preserve the tiny cusp exactly")
        for row in matching("sparse-voxel-center-0p5mm", "tiny-cusp-1um"):
            observation = row.get("observation", {})
            if decimal(observation.get("volume_error_mm3"), "runtime voxel cusp error") != Decimal("0.2"):
                error("voxel runtime candidate must reproduce the measured cusp loss")
            if observation.get("body_count") != 0:
                error("voxel runtime candidate must reproduce the measured cusp body loss")

if errors:
    print("RCS-012 validation failed:")
    for item in errors:
        print(f" - {item}")
    sys.exit(1)

print("RCS-012 validation passed (2 executable alternatives, 8 shared cases, pinned source trade study)")
