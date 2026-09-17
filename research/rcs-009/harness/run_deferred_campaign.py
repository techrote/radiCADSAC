#!/usr/bin/env python3
"""Compare the RCS-006 immediate B-rep baseline with the RCS-009 deferred candidate."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
PLAN_PATH = ROOT / "research/rcs-009/experiment-plan-v1.json"
BASELINE_PLAN_PATH = ROOT / "research/rcs-006/benchmark-plan-v1.json"
EXPECTED_COMMIT = "b8f597c677811d1f9f4d8a97f5ae2825c0353a42"
MATERIAL_CHANGE_EPSILON_MM3 = 1.0e-9


def decode_worker_stdout(stdout: str) -> tuple[dict[str, Any] | None, str]:
    """Decode worker JSON while preserving OCCT exchange diagnostics emitted on stdout."""
    stripped = stdout.strip()
    if not stripped:
        return None, "worker produced empty stdout"
    try:
        value = json.loads(stripped)
        return value if isinstance(value, dict) else None, ""
    except json.JSONDecodeError:
        pass

    # OCCT STEPControl_Writer emits human-readable transfer statistics before
    # the worker's final one-line JSON record. Recover only a complete final
    # JSON object; all preceding text remains diagnostic evidence.
    for line in reversed(stripped.splitlines()):
        candidate = line.strip()
        if not (candidate.startswith("{") and candidate.endswith("}")):
            continue
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value, ""
    return None, "no complete JSON object found in worker stdout"


def run_worker(worker: Path, case: dict[str, Any], timeout_s: float, step_file: Path | None = None) -> dict[str, Any]:
    command = [str(worker), "--case", case["worker_case"]]
    for key, value in sorted(case.get("parameters", {}).items()):
        command.extend(["--param", f"{key}={value}"])
    if step_file is not None:
        command.extend(["--step-file", str(step_file), "--unit", case["step"]["unit"]])

    try:
        completed = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "timeout",
            "exit_code": None,
            "stderr": (exc.stderr or "") if isinstance(exc.stderr, str) else "",
            "command": command,
        }

    record: dict[str, Any] = {
        "exit_code": completed.returncode,
        "stderr": completed.stderr.strip(),
        "command": command,
    }
    if completed.returncode != 0:
        record.update(status="worker_error", stdout=completed.stdout.strip())
        return record

    payload, error = decode_worker_stdout(completed.stdout)
    if payload is None:
        record.update(status="protocol_error", stdout=completed.stdout.strip(), error=error)
        return record
    record["payload"] = payload
    diagnostics = completed.stdout[: completed.stdout.rfind(json.dumps(payload, separators=(",", ":")))] if False else ""
    # The exact prefix is intentionally not reconstructed; raw STEP diagnostics
    # are only needed when parsing fails and are then retained in `stdout`.
    record["status"] = "measured"
    return record


def bbox_max_delta(a: dict[str, Any], b: dict[str, Any]) -> float:
    return max(abs(float(a[key]) - float(b[key])) for key in ("xmin", "ymin", "zmin", "xmax", "ymax", "zmax"))


def material_oracle(payload: dict[str, Any], expected_change: bool) -> bool:
    removed = float(payload.get("material_volume_removed_mm3", 0.0))
    return removed > MATERIAL_CHANGE_EPSILON_MM3 if expected_change else abs(removed) <= MATERIAL_CHANGE_EPSILON_MM3


def step_pass(payload: dict[str, Any], volume_tol: float, bbox_tol: float, body_count: int) -> tuple[bool, list[str]]:
    failures: list[str] = []
    step = payload.get("step", {})
    if not step.get("attempted"):
        failures.append("STEP was not attempted")
    for field in ("transfer_status", "write_status", "read_status"):
        if step.get(field) != "done":
            failures.append(f"{field}={step.get(field)!r}")
    if not step.get("readback_transferred"):
        failures.append("readback roots were not transferred")
    readback = step.get("readback_metrics", {})
    if not readback.get("valid_brep"):
        failures.append("readback B-rep is invalid")
    if readback.get("topology", {}).get("solids") != body_count:
        failures.append("readback material-body count changed")
    if float(step.get("volume_abs_delta_mm3", math.inf)) > volume_tol:
        failures.append("STEP volume delta exceeds campaign tolerance")
    if float(step.get("bbox_max_abs_delta_mm", math.inf)) > bbox_tol:
        failures.append("STEP bounding-box delta exceeds campaign tolerance")
    if not step.get("serialized_mentions_ap242"):
        failures.append("serialized file did not expose AP242 marker")
    if step.get("unit") == "millimeter" and not step.get("serialized_mentions_millimeter"):
        failures.append("serialized file did not expose millimetre unit marker")
    return not failures, failures


def cells_probe_equivalent(payload: dict[str, Any], volume_tol: float) -> tuple[bool | None, str]:
    probe = payload.get("cells_builder_probe", {})
    if not probe.get("attempted"):
        return None, "not_attempted"
    status = str(probe.get("status"))
    if status not in {"measured", "measured_with_warning"}:
        return False, status
    equivalent = (
        float(probe.get("volume_abs_delta_mm3", math.inf)) <= volume_tol
        and int(probe.get("solid_count_delta", 999999)) == 0
        and bool(probe.get("metrics", {}).get("valid_brep"))
    )
    return equivalent, status


def evaluate_case(case: dict[str, Any], baseline: dict[str, Any], candidate: dict[str, Any], volume_tol: float, bbox_tol: float) -> dict[str, Any]:
    result: dict[str, Any] = {
        "case_id": case["id"],
        "category": case["category"],
        "source_baseline_case": case["source_baseline_case"],
        "source_family_id": case["source_family_id"],
        "expected_material_change": case["expected_material_change"],
        "expected_body_count": case["expected_body_count"],
        "baseline": baseline,
        "candidate": candidate,
        "checks": {},
        "failures": [],
    }

    if baseline.get("status") == "measured":
        base = baseline["payload"]
        result["checks"]["baseline_worker_measured"] = True
        result["checks"]["baseline_physical_oracle"] = (
            material_oracle(base, case["expected_material_change"])
            and base.get("result_metrics", {}).get("topology", {}).get("solids") == case["expected_body_count"]
        )
        result["baseline_boolean_operations"] = int(base.get("boolean_operations", 0))
        result["baseline_geometry_ms"] = float(base.get("timing", {}).get("geometry_ms", 0.0))
    else:
        result["checks"]["baseline_worker_measured"] = False

    if candidate.get("status") != "measured":
        result["checks"]["candidate_worker_measured"] = False
        result["failures"].append("candidate worker did not return a measured record")
        return result

    result["checks"]["candidate_worker_measured"] = True
    cand = candidate["payload"]
    metrics = cand.get("result_metrics", {})
    semantics = cand.get("semantics", {})

    checks: list[tuple[str, bool, str]] = [
        (
            "candidate_material_oracle",
            material_oracle(cand, case["expected_material_change"]),
            "candidate violated physical material-change oracle",
        ),
        ("candidate_valid_brep", bool(metrics.get("valid_brep")), "candidate result is not a valid B-rep"),
        (
            "candidate_body_count",
            metrics.get("topology", {}).get("solids") == case["expected_body_count"],
            "candidate material-body count differs from physical oracle",
        ),
        (
            "candidate_materialization_count",
            int(semantics.get("materialized_boolean_operations", -1)) == case["expected_candidate_boolean_operations"],
            "candidate topology materialization count differs from plan",
        ),
        (
            "zero_measure_contact_policy",
            int(semantics.get("deferred_zero_measure_contacts", -1)) == case["expected_deferred_zero_measure_contacts"],
            "candidate zero-measure contact policy differs from plan",
        ),
        (
            "provenance_retrace_collapse",
            int(semantics.get("deduplicated_events", -1)) == case["expected_deduplicated_events"],
            "candidate provenance-backed retrace collapse differs from plan",
        ),
    ]
    for name, passed, message in checks:
        result["checks"][name] = passed
        if not passed:
            result["failures"].append(message)

    result["candidate_boolean_operations"] = int(semantics.get("materialized_boolean_operations", 0))
    result["deferred_zero_measure_contacts"] = int(semantics.get("deferred_zero_measure_contacts", 0))
    result["deduplicated_events"] = int(semantics.get("deduplicated_events", 0))
    result["candidate_geometry_ms"] = float(cand.get("timing", {}).get("geometry_ms", 0.0))

    if case.get("expected_connectivity_checkpoint"):
        passed = bool(semantics.get("connectivity_checkpoint"))
        result["checks"]["connectivity_checkpoint"] = passed
        if not passed:
            result["failures"].append("body-separating case did not force connectivity checkpoint")

    if baseline.get("status") == "measured":
        base_metrics = baseline["payload"].get("result_metrics", {})
        volume_delta = abs(float(base_metrics.get("volume_mm3", math.inf)) - float(metrics.get("volume_mm3", -math.inf)))
        bbox_delta = bbox_max_delta(base_metrics.get("bbox_mm", {}), metrics.get("bbox_mm", {}))
        result["baseline_candidate_volume_abs_delta_mm3"] = volume_delta
        result["baseline_candidate_bbox_max_abs_delta_mm"] = bbox_delta
        result["checks"]["final_volume_equivalent_to_baseline"] = volume_delta <= volume_tol
        result["checks"]["final_bbox_equivalent_to_baseline"] = bbox_delta <= bbox_tol
        # Baseline divergence is retained as evidence rather than making the
        # candidate pass/fail dependent on a possibly defective baseline.

    cells_equivalent, cells_status = cells_probe_equivalent(cand, volume_tol)
    result["cells_builder_probe_equivalent"] = cells_equivalent
    result["cells_builder_probe_status"] = cells_status

    if case.get("step", {}).get("enabled"):
        passed, failures = step_pass(cand, volume_tol, bbox_tol, case["expected_body_count"])
        result["checks"]["step_automated_roundtrip"] = passed
        result["step_failures"] = failures
        if not passed:
            result["failures"].extend(f"STEP: {message}" for message in failures)

    return result


def summary_markdown(results: dict[str, Any]) -> str:
    s = results["summary"]
    return "\n".join([
        "# RCS-009 deferred-topology smoke summary",
        "",
        f"- Cases: {s['cases']}",
        f"- Candidate structural/oracle failures: {s['candidate_failures']}",
        f"- Baseline physical-oracle passes: {s['baseline_physical_oracle_passes']}/{s['baseline_measured_cases']}",
        f"- Candidate physical-oracle passes: {s['candidate_physical_oracle_passes']}/{s['candidate_measured_cases']}",
        f"- Baseline/candidate final-volume equivalent cases: {s['baseline_candidate_volume_equivalent_cases']}",
        f"- Deferred zero-measure contacts: {s['deferred_zero_measure_contacts']}",
        f"- Provenance-backed geometry recomputations elided: {s['deduplicated_events']}",
        f"- Baseline materialized Booleans: {s['baseline_boolean_operations']}",
        f"- Candidate materialized Booleans: {s['candidate_boolean_operations']}",
        f"- CellsBuilder probes measured/equivalent: {s['cells_builder_measured']}/{s['cells_builder_equivalent']}",
        f"- STEP automated round-trip passes: {s['step_passes']}/{s['step_attempts']}",
        "",
        "Baseline defects and CellsBuilder negative results remain evidence; candidate physical/structural/STEP failures fail the campaign.",
        "",
    ])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-worker", type=Path, required=True)
    parser.add_argument("--candidate-worker", type=Path, required=True)
    parser.add_argument("--profile", choices=("smoke", "baseline"), default="smoke")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=float, default=60.0)
    args = parser.parse_args()

    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    baseline_plan = json.loads(BASELINE_PLAN_PATH.read_text(encoding="utf-8"))
    baseline_ids = {item["id"] for item in baseline_plan["cases"]}
    selected_ids = set(plan["profiles"][args.profile])
    cases = [item for item in plan["cases"] if item["id"] in selected_ids]
    missing_baseline = sorted({item["source_baseline_case"] for item in cases} - baseline_ids)
    if missing_baseline:
        raise SystemExit(f"RCS-009 plan references missing RCS-006 cases: {missing_baseline}")

    volume_tol = float(plan["comparison_tolerances"]["volume_abs_mm3"])
    bbox_tol = float(plan["comparison_tolerances"]["bbox_abs_mm"])
    args.out_dir.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="rcs009-") as temporary:
        temporary_path = Path(temporary)
        for case in cases:
            baseline = run_worker(args.baseline_worker.resolve(), case, args.timeout_seconds)
            step_path = temporary_path / f"{case['id']}.step" if case.get("step", {}).get("enabled") else None
            candidate = run_worker(args.candidate_worker.resolve(), case, args.timeout_seconds, step_path)
            records.append(evaluate_case(case, baseline, candidate, volume_tol, bbox_tol))

    baseline_measured = [item for item in records if item["baseline"].get("status") == "measured"]
    candidate_measured = [item for item in records if item["candidate"].get("status") == "measured"]
    cells_records = [item for item in records if item.get("cells_builder_probe_equivalent") is not None]
    step_records = [item for item in records if "step_automated_roundtrip" in item["checks"]]

    summary = {
        "cases": len(records),
        "candidate_failures": sum(bool(item["failures"]) for item in records),
        "baseline_measured_cases": len(baseline_measured),
        "candidate_measured_cases": len(candidate_measured),
        "baseline_physical_oracle_passes": sum(item["checks"].get("baseline_physical_oracle") is True for item in records),
        "candidate_physical_oracle_passes": sum(
            item["checks"].get("candidate_material_oracle") is True
            and item["checks"].get("candidate_body_count") is True
            for item in records
        ),
        "baseline_candidate_volume_equivalent_cases": sum(
            item["checks"].get("final_volume_equivalent_to_baseline") is True for item in records
        ),
        "baseline_candidate_bbox_equivalent_cases": sum(
            item["checks"].get("final_bbox_equivalent_to_baseline") is True for item in records
        ),
        "deferred_zero_measure_contacts": sum(item.get("deferred_zero_measure_contacts", 0) for item in records),
        "deduplicated_events": sum(item.get("deduplicated_events", 0) for item in records),
        "baseline_boolean_operations": sum(item.get("baseline_boolean_operations", 0) for item in records),
        "candidate_boolean_operations": sum(item.get("candidate_boolean_operations", 0) for item in records),
        "cells_builder_probes": len(cells_records),
        "cells_builder_measured": sum(item.get("cells_builder_probe_status") in {"measured", "measured_with_warning"} for item in cells_records),
        "cells_builder_equivalent": sum(item.get("cells_builder_probe_equivalent") is True for item in cells_records),
        "step_attempts": len(step_records),
        "step_passes": sum(item["checks"].get("step_automated_roundtrip") is True for item in step_records),
    }

    output = {
        "results_schema": "rcs-009-results/1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "profile": args.profile,
        "backend": {"id": "occt", "version": "8.0.1", "tag": "V8_0_1", "commit": EXPECTED_COMMIT},
        "candidate_model": plan["candidate"],
        "comparison_tolerances": plan["comparison_tolerances"],
        "records": records,
        "summary": summary,
    }
    (args.out_dir / "results.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.out_dir / "summary.md").write_text(summary_markdown(output), encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 3 if summary["candidate_failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
