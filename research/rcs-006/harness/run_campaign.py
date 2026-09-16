#!/usr/bin/env python3
"""Process-isolated RCS-006 baseline campaign orchestrator."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PLAN = ROOT / "research/rcs-006/benchmark-plan-v1.json"
CORPUS_PATH = ROOT / "research/rcs-003/corpus-v1.json"
STEP_FIXTURES_PATH = ROOT / "research/rcs-005/fixtures-v1.json"
CONFORMANCE_PATH = ROOT / "research/rcs-005/conformance-v1.json"
EXPECTED_OCCT_COMMIT = "b8f597c677811d1f9f4d8a97f5ae2825c0353a42"
RESULT_SCHEMA = "rcs-006-result/1.0"

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


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_head() -> str | None:
    if os.environ.get("GITHUB_SHA"):
        return os.environ["GITHUB_SHA"]
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def round_floats(value: Any, places: int = 9) -> Any:
    if isinstance(value, float):
        return round(value, places)
    if isinstance(value, dict):
        return {key: round_floats(child, places) for key, child in value.items()}
    if isinstance(value, list):
        return [round_floats(child, places) for child in value]
    return value


def stable_signature(worker: dict[str, Any]) -> str:
    stable = {
        "case_id": worker.get("case_id"),
        "parameters": worker.get("parameters"),
        "backend": worker.get("backend"),
        "boolean_operations": worker.get("boolean_operations"),
        "input_metrics": worker.get("input_metrics"),
        "result_metrics": worker.get("result_metrics"),
        "material_volume_removed_mm3": worker.get("material_volume_removed_mm3"),
        "step": {
            key: value
            for key, value in (worker.get("step") or {}).items()
            if key not in {"file_digest_fnv1a64"}
        },
    }
    encoded = json.dumps(round_floats(stable), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def analytic_count(metrics: dict[str, Any], name: str) -> int:
    surfaces = metrics.get("analytic_surfaces") or {}
    curves = metrics.get("analytic_curves") or {}
    return int(surfaces.get(name, 0)) + int(curves.get(name, 0))


def evaluate_success(
    case: dict[str, Any],
    worker: dict[str, Any],
    step_fixture: dict[str, Any] | None,
    default_accuracy: dict[str, Any],
) -> tuple[str, list[str]]:
    notes: list[str] = []
    result_metrics = worker.get("result_metrics") or {}
    input_metrics = worker.get("input_metrics") or {}

    if not result_metrics.get("valid_brep", False):
        return "invalid topology", ["OCCT BRepCheck_Analyzer rejected the result"]

    actual_bodies = int((result_metrics.get("topology") or {}).get("solids", -1))
    expected_bodies = int(case["expected_body_count"])
    if actual_bodies != expected_bodies:
        return "valid topology but wrong geometry", [
            f"body count {actual_bodies} != expected {expected_bodies}"
        ]

    input_volume = float(input_metrics.get("volume_mm3", 0.0))
    result_volume = float(result_metrics.get("volume_mm3", 0.0))
    removed = input_volume - result_volume
    volume_epsilon = max(abs(input_volume) * 1.0e-12, 1.0e-9)
    if case.get("expect_volume_change"):
        if removed <= volume_epsilon:
            return "valid topology but wrong geometry", [
                f"expected positive removal; observed {removed:.12g} mm^3"
            ]
    elif abs(removed) > volume_epsilon:
        return "valid topology but wrong geometry", [
            f"expected no material change; observed {removed:.12g} mm^3"
        ]

    step = worker.get("step") or {}
    if not step.get("attempted"):
        return "success", notes

    if step.get("transfer_status") != "done" or step.get("write_status") != "done":
        return "STEP writer failure", [
            f"transfer={step.get('transfer_status')} write={step.get('write_status')}"
        ]
    if step.get("read_status") != "done" or not step.get("readback_transferred"):
        return "STEP round-trip failure", [
            f"read={step.get('read_status')} transferred={step.get('readback_transferred')}"
        ]

    rb = step.get("readback_metrics") or {}
    if not rb.get("valid_brep", False):
        return "STEP round-trip failure", ["read-back B-rep is invalid"]
    rb_bodies = int((rb.get("topology") or {}).get("solids", -1))
    if rb_bodies != expected_bodies:
        return "STEP round-trip failure", [
            f"read-back body count {rb_bodies} != expected {expected_bodies}"
        ]

    accuracy = dict(default_accuracy)
    if step_fixture and isinstance(step_fixture.get("accuracy"), dict):
        accuracy.update(step_fixture["accuracy"])
    dimension_error_nm = float(step.get("bbox_max_abs_delta_mm", 0.0)) * 1_000_000.0
    if dimension_error_nm > float(accuracy["max_dimension_error_nm"]):
        return "geometric tolerance breach", [
            f"bbox delta {dimension_error_nm:.6g} nm exceeds {accuracy['max_dimension_error_nm']} nm"
        ]
    if float(step.get("volume_abs_delta_mm3", 0.0)) > float(accuracy["max_volume_error_abs_mm3"]):
        return "geometric tolerance breach", ["absolute volume round-trip budget exceeded"]
    if float(step.get("volume_rel_delta", 0.0)) > float(accuracy["max_volume_error_rel"]):
        return "geometric tolerance breach", ["relative volume round-trip budget exceeded"]

    unit = str((case.get("step") or {}).get("unit", "millimeter"))
    if unit == "inch" and not step.get("serialized_mentions_inch"):
        return "STEP writer failure", ["serialized file did not expose expected inch unit marker"]
    if unit == "millimeter" and not step.get("serialized_mentions_millimeter"):
        return "STEP writer failure", ["serialized file did not expose expected millimetre SI marker"]

    if step_fixture:
        for required in step_fixture.get("required_analytic_classes", []):
            if analytic_count(rb, required) <= 0:
                return "geometric tolerance breach", [
                    f"required analytic class lost on read-back: {required}"
                ]

    return "success", notes


def validate_plan(plan: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if plan.get("benchmark_plan_schema") != "rcs-006-benchmark-plan/1.0":
        raise ValueError("unexpected benchmark plan schema")
    backend = plan.get("backend") or {}
    if backend.get("commit") != EXPECTED_OCCT_COMMIT:
        raise ValueError("benchmark plan is not pinned to the accepted OCCT commit")

    corpus = load_json(CORPUS_PATH)
    family_ids = {item["id"] for item in corpus.get("fixture_families", [])}
    step_matrix = load_json(STEP_FIXTURES_PATH)
    step_fixtures = {item["fixture_id"]: item for item in step_matrix.get("fixtures", [])}
    conformance = load_json(CONFORMANCE_PATH)

    case_ids: set[str] = set()
    for case in plan.get("cases", []):
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            raise ValueError("every case requires an id")
        if case_id in case_ids:
            raise ValueError(f"duplicate case id: {case_id}")
        case_ids.add(case_id)
        if case.get("source_family_id") not in family_ids:
            raise ValueError(f"{case_id}: unknown RCS-003 source family {case.get('source_family_id')!r}")
        step_fixture_id = case.get("step_fixture_id")
        if step_fixture_id and step_fixture_id not in step_fixtures:
            raise ValueError(f"{case_id}: unknown RCS-005 STEP fixture {step_fixture_id!r}")

    for profile_name, members in (plan.get("profiles") or {}).items():
        missing = sorted(set(members) - case_ids)
        if missing:
            raise ValueError(f"profile {profile_name} references unknown cases: {missing}")

    return step_fixtures, step_matrix, conformance


def run_worker(
    worker: Path,
    case: dict[str, Any],
    attempt: int,
    timeout_seconds: int,
    out_dir: Path,
) -> dict[str, Any]:
    command = [str(worker), "--case", str(case["worker_case"])]
    for key, value in sorted((case.get("parameters") or {}).items()):
        command.extend(["--param", f"{key}={value}"])

    step_path: Path | None = None
    step_config = case.get("step") or {}
    if step_config.get("enabled"):
        step_path = out_dir / "step" / f"{case['id']}-attempt-{attempt}.stp"
        command.extend(["--step-file", str(step_path), "--unit", str(step_config.get("unit", "millimeter"))])

    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "classification": "hang/timeout",
            "notes": [f"worker exceeded {timeout_seconds}s timeout"],
            "exit_code": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "wall_ms": (time.monotonic() - started) * 1000.0,
            "worker": None,
            "step_file": str(step_path) if step_path else None,
        }

    wall_ms = (time.monotonic() - started) * 1000.0
    if completed.returncode != 0:
        classification = "crash" if completed.returncode < 0 else "algorithm returned error/status"
        return {
            "classification": classification,
            "notes": [f"worker exit code {completed.returncode}"],
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "wall_ms": wall_ms,
            "worker": None,
            "step_file": str(step_path) if step_path else None,
        }

    try:
        worker_result = json.loads(completed.stdout.strip())
    except json.JSONDecodeError as exc:
        return {
            "classification": "algorithm returned error/status",
            "notes": [f"worker stdout was not valid JSON: {exc}"],
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "wall_ms": wall_ms,
            "worker": None,
            "step_file": str(step_path) if step_path else None,
        }

    return {
        "classification": "success",
        "notes": [],
        "exit_code": completed.returncode,
        "stdout": "",
        "stderr": completed.stderr,
        "wall_ms": wall_ms,
        "worker": worker_result,
        "step_file": str(step_path) if step_path else None,
    }


def write_summary(records: list[dict[str, Any]], path: Path, campaign: dict[str, Any]) -> None:
    lines = [
        "# RCS-006 campaign summary",
        "",
        f"Plan: `{campaign['plan_id']}`  ",
        f"Profile: `{campaign['profile']}`  ",
        f"OCCT: `{campaign['backend']['version']}` / `{campaign['backend']['commit']}`  ",
        f"Attempts: {len(records)}  ",
        "",
        "| Case | Attempt | Classification | Valid | Bodies | Volume mm3 | Geometry ms | STEP |",
        "|---|---:|---|---|---:|---:|---:|---|",
    ]
    for record in records:
        worker = record.get("worker") or {}
        metrics = worker.get("result_metrics") or {}
        topology = metrics.get("topology") or {}
        timing = worker.get("timing") or {}
        step = worker.get("step") or {}
        step_text = "-"
        if step.get("attempted"):
            step_text = f"{step.get('write_status')}/{step.get('read_status')}"
        lines.append(
            "| {case} | {attempt} | {classification} | {valid} | {bodies} | {volume:.9g} | {ms:.3f} | {step} |".format(
                case=record["case_id"],
                attempt=record["attempt"],
                classification=record["classification"],
                valid=metrics.get("valid_brep", "-"),
                bodies=topology.get("solids", "-"),
                volume=float(metrics.get("volume_mm3", 0.0)),
                ms=float(timing.get("geometry_ms", 0.0)),
                step=step_text,
            )
        )
    lines.extend(["", "## Counts", ""])
    for key, count in sorted((campaign.get("classification_counts") or {}).items()):
        lines.append(f"- `{key}`: {count}")
    if campaign.get("nondeterministic_case_ids"):
        lines.extend(["", "Nondeterministic cases: " + ", ".join(campaign["nondeterministic_case_ids"])])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", required=True, type=Path)
    parser.add_argument("--plan", default=DEFAULT_PLAN, type=Path)
    parser.add_argument("--profile", default="smoke")
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--repeats", type=int)
    parser.add_argument("--timeout-seconds", type=int)
    args = parser.parse_args()

    worker = args.worker.resolve()
    if not worker.is_file():
        raise SystemExit(f"worker does not exist: {worker}")
    plan = load_json(args.plan)
    step_fixtures, step_matrix, _conformance = validate_plan(plan)
    cases_by_id = {case["id"]: case for case in plan["cases"]}
    if args.profile not in plan["profiles"]:
        raise SystemExit(f"unknown profile: {args.profile}")

    repeats = args.repeats if args.repeats is not None else int(plan.get("default_repeats", 2))
    timeout_seconds = (
        args.timeout_seconds
        if args.timeout_seconds is not None
        else int(plan.get("worker_timeout_seconds", 60))
    )
    if repeats < 1:
        raise SystemExit("repeats must be >= 1")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    signatures: dict[str, list[str]] = defaultdict(list)
    run_started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    for case_id in plan["profiles"][args.profile]:
        case = cases_by_id[case_id]
        step_fixture = step_fixtures.get(case.get("step_fixture_id"))
        for attempt in range(1, repeats + 1):
            result = run_worker(worker, case, attempt, timeout_seconds, args.out_dir)
            if result["classification"] == "success" and result["worker"]:
                classification, notes = evaluate_success(
                    case,
                    result["worker"],
                    step_fixture,
                    step_matrix["default_accuracy"],
                )
                result["classification"] = classification
                result["notes"].extend(notes)
                signatures[case_id].append(stable_signature(result["worker"]))

            record = {
                "result_schema": RESULT_SCHEMA,
                "run_started_utc": run_started_utc,
                "plan_id": plan["plan_id"],
                "profile": args.profile,
                "case_id": case_id,
                "source_family_id": case["source_family_id"],
                "step_fixture_id": case.get("step_fixture_id"),
                "attempt": attempt,
                "classification": result["classification"],
                "notes": result["notes"],
                "exit_code": result["exit_code"],
                "wall_ms": result["wall_ms"],
                "stderr": result["stderr"],
                "worker": result["worker"],
                "step_file": result["step_file"],
            }
            if record["classification"] not in FAILURE_TAXONOMY:
                raise RuntimeError(f"internal invalid classification: {record['classification']}")
            records.append(record)
            print(json.dumps(record, sort_keys=True), flush=True)

    nondeterministic: list[str] = []
    for case_id, case_signatures in signatures.items():
        if len(case_signatures) >= 2 and len(set(case_signatures)) != 1:
            nondeterministic.append(case_id)
            for record in records:
                if record["case_id"] == case_id and record["classification"] == "success":
                    record["classification"] = "nondeterministic result"
                    record["notes"].append("stable result signature differed across repeated attempts")

    results_path = args.out_dir / "results.jsonl"
    with results_path.open("w", encoding="utf-8") as stream:
        for record in records:
            stream.write(json.dumps(record, sort_keys=True) + "\n")

    counts = Counter(record["classification"] for record in records)
    campaign = {
        "campaign_schema": "rcs-006-campaign/1.0",
        "run_started_utc": run_started_utc,
        "plan_id": plan["plan_id"],
        "profile": args.profile,
        "backend": plan["backend"],
        "source_commit": git_head(),
        "worker_sha256": sha256_file(worker),
        "plan_sha256": sha256_file(args.plan),
        "host": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "repeats": repeats,
        "timeout_seconds": timeout_seconds,
        "record_count": len(records),
        "classification_counts": dict(sorted(counts.items())),
        "nondeterministic_case_ids": sorted(nondeterministic),
    }
    (args.out_dir / "campaign.json").write_text(
        json.dumps(campaign, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_summary(records, args.out_dir / "summary.md", campaign)

    failures = sum(count for key, count in counts.items() if key != "success")
    print("RCS006_CAMPAIGN_SUMMARY=" + json.dumps(campaign, sort_keys=True), flush=True)
    print((args.out_dir / "summary.md").read_text(encoding="utf-8"), flush=True)
    return 0 if failures == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
