#!/usr/bin/env python3
"""Run the RCS-010 lathe strategy comparison against the pinned OCCT adapter."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from profile_solver import apply_case, encode_polygon

ROOT = Path(__file__).resolve().parents[3]
PLAN_PATH = ROOT / "research/rcs-010/experiment-plan-v1.json"
CORPUS_PATH = ROOT / "research/rcs-003/corpus-v1.json"
EXPECTED_COMMIT = "b8f597c677811d1f9f4d8a97f5ae2825c0353a42"


def decode_worker_stdout(stdout: str) -> tuple[dict[str, Any] | None, str]:
    text = stdout.strip()
    if not text:
        return None, "worker produced empty stdout"
    try:
        value = json.loads(text)
        return (value, "") if isinstance(value, dict) else (None, "worker JSON root is not an object")
    except json.JSONDecodeError:
        pass
    for line in reversed(text.splitlines()):
        candidate = line.strip()
        if not (candidate.startswith("{") and candidate.endswith("}")):
            continue
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value, ""
    return None, "no complete final JSON object found in worker stdout"


def bbox_delta(a: dict[str, Any], b: dict[str, Any]) -> float:
    keys = ("xmin", "ymin", "zmin", "xmax", "ymax", "zmax")
    return max(abs(float(a[k]) - float(b[k])) for k in keys)


def strategy_step_pass(step: dict[str, Any], body_count: int, volume_tol: float, bbox_tol: float) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if not step.get("attempted"):
        failures.append("STEP not attempted")
        return False, failures
    for field in ("transfer_status", "write_status", "read_status"):
        if step.get(field) != "done":
            failures.append(f"{field}={step.get(field)!r}")
    if not step.get("readback_transferred"):
        failures.append("STEP roots were not transferred")
    metrics = step.get("readback_metrics", {})
    if not metrics.get("valid_brep"):
        failures.append("STEP read-back B-rep invalid")
    if metrics.get("topology", {}).get("solids") != body_count:
        failures.append("STEP read-back body count changed")
    if float(step.get("volume_abs_delta_mm3", math.inf)) > volume_tol:
        failures.append("STEP volume delta exceeds budget")
    if float(step.get("bbox_max_abs_delta_mm", math.inf)) > bbox_tol:
        failures.append("STEP bounding-box delta exceeds budget")
    if not step.get("serialized_mentions_ap242"):
        failures.append("serialized file lacks AP242 marker")
    if not step.get("serialized_mentions_millimeter"):
        failures.append("serialized file lacks millimetre unit marker")
    if step.get("error"):
        failures.append(f"STEP worker error: {step['error']}")
    return not failures, failures


def run_worker(worker: Path, case: dict[str, Any], solved: dict[str, Any], step_dir: Path | None, timeout: float) -> dict[str, Any]:
    stock = case["stock"]
    if int(solved["raw_samples"]) > 0:
        event_count = max(1, int(solved["canonical_geometry_events"]))
    else:
        event_count = max(1, int(solved["journal_events"]))

    command = [
        str(worker),
        "--case-id", case["id"],
        "--profile", encode_polygon(solved["result"]["polygon_points"]),
        "--stock-z0", str(stock["z0_mm"]),
        "--stock-z1", str(stock["z1_mm"]),
        "--stock-radius", str(stock["outer_radius_mm"]),
        "--event-count", str(event_count),
    ]
    if step_dir is not None:
        command.extend(["--step-dir", str(step_dir)])

    try:
        completed = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "timeout",
            "command": command,
            "stderr": (exc.stderr or "") if isinstance(exc.stderr, str) else "",
        }

    record: dict[str, Any] = {
        "status": "worker_error" if completed.returncode else "measured",
        "exit_code": completed.returncode,
        "command": command,
        "stderr": completed.stderr.strip(),
    }
    if completed.returncode:
        record["stdout"] = completed.stdout.strip()
        return record

    payload, error = decode_worker_stdout(completed.stdout)
    if payload is None:
        record.update(status="protocol_error", stdout=completed.stdout.strip(), error=error)
        return record
    record["payload"] = payload
    return record


def evaluate(case: dict[str, Any], solved: dict[str, Any], worker_record: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "case_id": case["id"],
        "category": case["category"],
        "source_family_id": case["source_family_id"],
        "solver": solved,
        "worker": worker_record,
        "checks": {},
        "failures": [],
    }
    checks = result["checks"]
    failures = result["failures"]

    expected = case["expected"]
    if worker_record.get("status") != "measured":
        checks["worker_measured"] = False
        failures.append(f"worker status={worker_record.get('status')!r}")
        return result
    checks["worker_measured"] = True

    payload = worker_record["payload"]
    checks["backend_commit"] = payload.get("backend", {}).get("commit") == EXPECTED_COMMIT
    if not checks["backend_commit"]:
        failures.append("worker backend commit does not match pinned OCCT baseline")

    volume_tol = float(plan["comparison_tolerances"]["volume_abs_mm3"])
    bbox_tol = float(plan["comparison_tolerances"]["bbox_abs_mm"])
    step_volume_tol = float(plan["comparison_tolerances"]["step_volume_abs_mm3"])
    step_bbox_tol = float(plan["comparison_tolerances"]["step_bbox_abs_mm"])
    expected_volume = float(solved["result"]["volume_mm3"])
    expected_body_count = int(expected["body_count"])

    strategies = payload.get("strategies", {})
    axis_metrics = strategies.get("axisymmetric_2d", {}).get("metrics", {})
    for name in ("repeated_3d", "batched_3d", "axisymmetric_2d"):
        strategy = strategies.get(name, {})
        measured = strategy.get("status") == "measured"
        checks[f"{name}_measured"] = measured
        if not measured:
            failures.append(f"{name} failed: {strategy.get('error')}")
            continue
        metrics = strategy.get("metrics", {})
        valid = bool(metrics.get("valid_brep"))
        body_ok = metrics.get("topology", {}).get("solids") == expected_body_count
        volume_ok = abs(float(metrics.get("volume_mm3", math.inf)) - expected_volume) <= volume_tol
        checks[f"{name}_valid_brep"] = valid
        checks[f"{name}_body_count"] = body_ok
        checks[f"{name}_analytic_volume"] = volume_ok
        if not valid:
            failures.append(f"{name} B-rep invalid")
        if not body_ok:
            failures.append(f"{name} body count differs from oracle")
        if not volume_ok:
            failures.append(f"{name} volume differs from 2D analytic material oracle")

        if name != "axisymmetric_2d" and axis_metrics:
            same_volume = abs(float(metrics.get("volume_mm3", math.inf)) - float(axis_metrics.get("volume_mm3", -math.inf))) <= volume_tol
            same_bbox = bbox_delta(metrics.get("bbox_mm", {}), axis_metrics.get("bbox_mm", {})) <= bbox_tol
            checks[f"{name}_axis_volume_equivalent"] = same_volume
            checks[f"{name}_axis_bbox_equivalent"] = same_bbox
            if not same_volume:
                failures.append(f"{name} final volume differs from axisymmetric reconstruction")
            if not same_bbox:
                failures.append(f"{name} bounds differ from axisymmetric reconstruction")

    expected_events = int(solved["canonical_geometry_events"]) if int(solved["raw_samples"]) else int(solved["journal_events"])
    expected_events = max(1, expected_events)
    operation_expectations = {"repeated_3d": expected_events, "batched_3d": 1, "axisymmetric_2d": 0}
    for name, count in operation_expectations.items():
        actual = strategies.get(name, {}).get("material_boolean_operations")
        passed = actual == count
        checks[f"{name}_boolean_count"] = passed
        if not passed:
            failures.append(f"{name} material Boolean count {actual!r} != {count}")

    axis_surfaces = axis_metrics.get("analytic_surfaces", {})
    expected_classes = set(expected.get("surface_classes", []))
    preserved = all(int(axis_surfaces.get(item, 0)) > 0 for item in expected_classes)
    checks["axisymmetric_expected_analytic_surfaces"] = preserved
    checks["axisymmetric_no_bspline_surface"] = int(axis_surfaces.get("bspline_surface", 0)) == 0
    if not preserved:
        failures.append(f"axisymmetric reconstruction did not preserve expected analytic classes: {sorted(expected_classes)}")
    if not checks["axisymmetric_no_bspline_surface"]:
        failures.append("axisymmetric reconstruction introduced B-spline surfaces")

    if "journal_events" in expected:
        checks["journal_event_count"] = solved["journal_events"] == expected["journal_events"]
        if not checks["journal_event_count"]:
            failures.append("profile solver journal-event count differs from plan")
    if "provenance_noop_events" in expected:
        checks["provenance_noop_events"] = solved["provenance_noop_events"] == expected["provenance_noop_events"]
        if not checks["provenance_noop_events"]:
            failures.append("exact retrace no-op evidence differs from plan")
    if "raw_samples" in expected:
        checks["raw_sample_count"] = solved["raw_samples"] == expected["raw_samples"]
        checks["canonical_geometry_events"] = solved["canonical_geometry_events"] == expected["canonical_geometry_events"]
        if not checks["raw_sample_count"] or not checks["canonical_geometry_events"]:
            failures.append("analogue canonicalization evidence differs from plan")

    if case.get("step"):
        for name in ("repeated_3d", "batched_3d", "axisymmetric_2d"):
            strategy = strategies.get(name, {})
            if strategy.get("status") != "measured":
                continue
            passed, step_failures = strategy_step_pass(
                strategy.get("step", {}), expected_body_count, step_volume_tol, step_bbox_tol
            )
            checks[f"{name}_step_roundtrip"] = passed
            if not passed:
                failures.extend(f"{name} STEP: {message}" for message in step_failures)

    result["observations"] = {
        "event_count_after_canonicalization": expected_events,
        "repeated_boolean_operations": strategies.get("repeated_3d", {}).get("material_boolean_operations"),
        "batched_boolean_operations": strategies.get("batched_3d", {}).get("material_boolean_operations"),
        "axisymmetric_boolean_operations": strategies.get("axisymmetric_2d", {}).get("material_boolean_operations"),
        "repeated_faces": strategies.get("repeated_3d", {}).get("metrics", {}).get("topology", {}).get("faces"),
        "batched_faces": strategies.get("batched_3d", {}).get("metrics", {}).get("topology", {}).get("faces"),
        "axisymmetric_faces": strategies.get("axisymmetric_2d", {}).get("metrics", {}).get("topology", {}).get("faces"),
        "repeated_total_ms": strategies.get("repeated_3d", {}).get("conceptual_total_ms"),
        "batched_total_ms": strategies.get("batched_3d", {}).get("conceptual_total_ms"),
        "axisymmetric_total_ms": strategies.get("axisymmetric_2d", {}).get("conceptual_total_ms"),
    }
    return result


def summary_markdown(campaign: dict[str, Any]) -> str:
    s = campaign["summary"]
    return "\n".join([
        "# RCS-010 lathe material-domain campaign",
        "",
        f"- Cases: {s['cases']}",
        f"- Cases with acceptance failures: {s['failed_cases']}",
        f"- STEP strategy round-trips passed: {s['step_strategy_passes']}/{s['step_strategy_attempts']}",
        f"- Journal events represented: {s['journal_events']}",
        f"- Provenance-equivalent no-op events: {s['provenance_noop_events']}",
        f"- Raw analogue samples canonicalized: {s['raw_samples']}",
        f"- Repeated 3D material Booleans: {s['repeated_boolean_operations']}",
        f"- Batched 3D material Booleans: {s['batched_boolean_operations']}",
        f"- Axisymmetric material Booleans: {s['axisymmetric_boolean_operations']}",
        f"- Repeated 3D conceptual runtime (ms): {s['repeated_total_ms']:.6f}",
        f"- Batched 3D conceptual runtime (ms): {s['batched_total_ms']:.6f}",
        f"- Axisymmetric reconstruction runtime (ms): {s['axisymmetric_total_ms']:.6f}",
        "",
        "Runtime is comparative research evidence, not a production performance guarantee. The 3D envelope is an oracle-derived completed removal-envelope proxy; tool-envelope generation is a separate RCS-010 scope limit.",
        "",
    ])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", type=Path, required=True)
    parser.add_argument("--profile", choices=("smoke", "baseline"), default="smoke")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=float, default=90.0)
    args = parser.parse_args()

    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    corpus_ids = {item["id"] for item in corpus["fixture_families"]}
    missing = sorted({item["source_family_id"] for item in plan["cases"]} - corpus_ids)
    if missing:
        raise SystemExit(f"RCS-010 plan references missing RCS-003 families: {missing}")

    selected = set(plan["profiles"][args.profile])
    cases = [case for case in plan["cases"] if case["id"] in selected]
    if len(cases) != len(selected):
        raise SystemExit("profile references unknown RCS-010 cases")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="rcs010-step-") as tmp:
        tmp_path = Path(tmp)
        for case in cases:
            solved = apply_case(case)
            step_dir = tmp_path / case["id"] if case.get("step") else None
            worker_record = run_worker(args.worker.resolve(), case, solved, step_dir, args.timeout_seconds)
            records.append(evaluate(case, solved, worker_record, plan))

    strategies = ("repeated_3d", "batched_3d", "axisymmetric_2d")
    step_attempts = 0
    step_passes = 0
    repeated_ops = batched_ops = axis_ops = 0
    repeated_ms = batched_ms = axis_ms = 0.0

    for record in records:
        worker = record.get("worker", {}).get("payload", {})
        strategy_map = worker.get("strategies", {})
        repeated_ops += int(strategy_map.get("repeated_3d", {}).get("material_boolean_operations", 0) or 0)
        batched_ops += int(strategy_map.get("batched_3d", {}).get("material_boolean_operations", 0) or 0)
        axis_ops += int(strategy_map.get("axisymmetric_2d", {}).get("material_boolean_operations", 0) or 0)
        repeated_ms += float(strategy_map.get("repeated_3d", {}).get("conceptual_total_ms", 0.0) or 0.0)
        batched_ms += float(strategy_map.get("batched_3d", {}).get("conceptual_total_ms", 0.0) or 0.0)
        axis_ms += float(strategy_map.get("axisymmetric_2d", {}).get("conceptual_total_ms", 0.0) or 0.0)
        for name in strategies:
            key = f"{name}_step_roundtrip"
            if key in record["checks"]:
                step_attempts += 1
                step_passes += int(record["checks"][key] is True)

    summary = {
        "cases": len(records),
        "failed_cases": sum(bool(item["failures"]) for item in records),
        "step_strategy_attempts": step_attempts,
        "step_strategy_passes": step_passes,
        "journal_events": sum(int(item["solver"]["journal_events"]) for item in records),
        "provenance_noop_events": sum(int(item["solver"]["provenance_noop_events"]) for item in records),
        "raw_samples": sum(int(item["solver"]["raw_samples"]) for item in records),
        "repeated_boolean_operations": repeated_ops,
        "batched_boolean_operations": batched_ops,
        "axisymmetric_boolean_operations": axis_ops,
        "repeated_total_ms": repeated_ms,
        "batched_total_ms": batched_ms,
        "axisymmetric_total_ms": axis_ms,
    }
    campaign = {
        "schema": "rcs-010-campaign/1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "profile": args.profile,
        "plan_id": plan["plan_id"],
        "backend": plan["baseline"],
        "summary": summary,
        "results": records,
    }

    (args.out_dir / "results.json").write_text(json.dumps(campaign, indent=2) + "\n", encoding="utf-8")
    (args.out_dir / "summary.md").write_text(summary_markdown(campaign), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["failed_cases"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
