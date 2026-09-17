#!/usr/bin/env python3
"""Run the RCS-009 immediate-B-rep versus bounded-deferred-topology campaign."""

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


def run_worker(
    worker: Path,
    case: dict[str, Any],
    timeout_s: float,
    step_file: Path | None = None,
) -> dict[str, Any]:
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
        record["status"] = "worker_error"
        record["stdout"] = completed.stdout.strip()
        return record
    try:
        record["payload"] = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        record["status"] = "protocol_error"
        record["stdout"] = completed.stdout.strip()
        record["error"] = str(exc)
        return record
    record["status"] = "measured"
    return record


def bbox_max_delta(a: dict[str, Any], b: dict[str, Any]) -> float:
    keys = ("xmin", "ymin", "zmin", "xmax", "ymax", "zmax")
    return max(abs(float(a[key]) - float(b[key])) for key in keys)


def material_oracle(payload: dict[str, Any], expected_change: bool) -> bool:
    removed = float(payload.get("material_volume_removed_mm3", 0.0))
    if expected_change:
        return removed > MATERIAL_CHANGE_EPSILON_MM3
    return abs(removed) <= MATERIAL_CHANGE_EPSILON_MM3


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
    solids = readback.get("topology", {}).get("solids")
    if solids != body_count:
        failures.append(f"readback solid count {solids!r} != {body_count}")
    if float(step.get("volume_abs_delta_mm3", math.inf)) > volume_tol:
        failures.append("STEP volume delta exceeds campaign tolerance")
    if float(step.get("bbox_max_abs_delta_mm", math.inf)) > bbox_tol:
        failures.append("STEP bounding-box delta exceeds campaign tolerance")
    if not step.get("serialized_mentions_ap242"):
        failures.append("serialized file did not expose AP242 marker")
    if step.get("unit") == "millimeter" and not step.get("serialized_mentions_millimeter"):
        failures.append("serialized file did not expose millimetre unit marker")
    return (not failures, failures)


def cells_probe_equivalent(payload: dict[str, Any], volume_tol: float) -> tuple[bool | None, str]:
    probe = payload.get("cells_builder_probe", {})
    if not probe.get("attempted"):
        return None, "not_attempted"
    if probe.get("status") not in {"measured", "measured_with_warning"}:
        return False, str(probe.get("status"))
    equivalent = (
        float(probe.get("volume_abs_delta_mm3", math.inf)) <= volume_tol
        and int(probe.get("solid_count_delta", 999999)) == 0
        and bool(probe.get("metrics", {}).get("valid_brep"))
    )
    return equivalent, str(probe.get("status"))


def evaluate_case(
    case: dict[str, Any],
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    volume_tol: float,
    bbox_tol: float,
) -> dict[str, Any]:
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

    if baseline.get("status") != "measured":
        result["checks"]["baseline_worker_measured"] = False
    else:
        base_payload = baseline["payload"]
        result["checks"]["baseline_worker_measured"] = True
        result["checks"]["baseline_physical_oracle"] = material_oracle(
            base_payload, case["expected_material_change"]
        ) and base_payload.get("result_metrics", {}).get("topology", {}).get("solids") == case["expected_body_count"]
        result["baseline_boolean_operations"] = int(base_payload.get("boolean_operations", 0))
        result["baseline_geometry_ms"] = float(base_payload.get("timing", {}).get("geometry_ms", 0.0))

    if candidate.get("status") != "measured":
        result["checks"]["candidate_worker_measured"] = False
        result["failures"].append("candidate worker did not return a measured record")
        return result

    result["checks"]["candidate_worker_measured"] = True
    cand = candidate["payload"]
    cand_metrics = cand.get("result_metrics", {})
    semantics = cand.get("semantics", {})

    candidate_oracle = material_oracle(cand, case["expected_material_change"])
    result["checks"]["candidate_material_oracle"] = candidate_oracle
    if not candidate_oracle:
        result["failures"].append("candidate violated physical material-change oracle")

    valid = bool(cand_metrics.get("valid_brep"))
    result["checks"]["candidate_valid_brep"] = valid
    if not valid:
        result["failures"].append("candidate result is not a valid B-rep")

    solid_count = cand_metrics.get("topology", {}).get("solids")
    bodies_ok = solid_count == case["expected_body_count"]
    result["checks"]["candidate_body_count"] = bodies_ok
    if not bodies_ok:
        result["failures"].append(
            f"candidate solid count {solid_count!r} != expected {case['expected_body_count']}"
        )

    expected_ops = case["expected_candidate_boolean_operations"]
    candidate_ops = int(semantics.get("materialized_boolean_operations", -1))
    result["candidate_boolean_operations"] = candidate_ops
    ops_ok = candidate_ops == expected_ops
    result["checks"]["candidate_materialization_count"] = ops_ok
    if not ops_ok:
        result["failures"].append(f"candidate materialized {candidate_ops} Booleans; expected {expected_ops}")

    expected_contacts = case["expected_deferred_zero_measure_contacts"]
    contact_count = int(semantics.get("deferred_zero_measure_contacts", -1))
    result["deferred_zero_measure_contacts"] = contact_count
    contacts_ok = contact_count == expected_contacts
    result["checks"]["zero_measure_contact_policy"] = contacts_ok
    if not contacts_ok:
        result["failures"].append(
            f"candidate deferred {contact_count} zero-measure contacts; expected {expected_contacts}"
        )

    expected_dedup = case["expected_deduplicated_events"]
    dedup = int(semantics.get("deduplicated_events", -1))
    result["deduplicated_events"] = dedup
    dedup_ok = dedup == expected_dedup
    result["checks"]["provenance_retrace_collapse"] = dedup_ok
    if not dedup_ok:
        result["failures"].append(f"candidate deduplicated {dedup} events; expected {expected_dedup}")

    if case.get("expected_connectivity_checkpoint"):
        checkpoint_ok = bool(semantics.get("connectivity_checkpoint"))
        result["checks"]["connectivity_checkpoint"] = checkpoint_ok
        if not checkpoint_ok:
            result["failures"].append("body-separating case did not force connectivity checkpoint")

    result["candidate_geometry_ms"] = float(cand.get("timing", {}).get("geometry_ms", 0.0))

    if baseline.get("status") == "measured":
        base_payload = baseline["payload"]
        base_metrics = base_payload.get("result_metrics", {})
        volume_delta = abs(
            float(base_metrics.get("volume_mm3", math.inf)) - float(cand_metrics.get("volume_mm3", -math.inf))
        )
        bbox_delta = bbox_max_delta(base_metrics.get("bbox_mm", {}), cand_metrics.get("bbox_mm", {}))
        result["baseline_candidate_volume_abs_delta_mm3"] = volume_delta
        result["baseline_candidate_bbox_max_abs_delta_mm"] = bbox_delta
        result["checks"]["final_volume_equivalent_to_baseline"] = volume_delta <= volume_tol
        result["checks"]["final_bbox_equivalent_to_baseline"] = bbox_delta <= bbox_tol
        # Baseline divergence is preserved as evidence and does not by itself invalidate the candidate.

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
    lines = [
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
        "Baseline defects and CellsBuilder negative results are retained as evidence; candidate contract/oracle and required STEP reconciliation failures make the campaign fail.",
        "",
    ]
    return "\n".join(lines)


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
        temp = Path(temporary)
        for case in cases:
            baseline = run_worker(args.baseline_worker.resolve(), case, args.timeout_seconds)
            step_path = temp / f"{case['id']}.step" if case.get("step", {}).get("enabled") else None
            candidate = run_worker(args.candidate_worker.resolve(), case, args.timeout_seconds, step_path)
            records.append(evaluate_case(case, baseline, candidate, volume_tol, bbox_tol))

    baseline_measured = [r for r in records if r["baseline"].get("status") == "measured"]
    candidate_measured = [r for r in records if r["candidate"].get("status") == "measured"]
    candidate_failures = sum(bool(r["failures"]) for r in records)
    cells_records = [r for r in records if r.get("cells_builder_probe_equivalent") is not None]
    step_records = [r for r in records if "step_automated_roundtrip" in r["checks"]]

    summary = {
        "cases": len(records),
        "candidate_failures": candidate_failures,
        "baseline_measured_cases": len(baseline_measured),
        "candidate_measured_cases": len(candidate_measured),
        "baseline_physical_oracle_passes": sum(
            r["checks"].get("baseline_physical_oracle") is True for r in records
        ),
        "candidate_physical_oracle_passes": sum(
            r["checks"].get("candidate_material_oracle") is True
            and r["checks"].get("candidate_body_count") is True
            for r in records
        ),
        "baseline_candidate_volume_equivalent_cases": sum(
            r["checks"].get("final_volume_equivalent_to_baseline") is True for r in records
        ),
        "baseline_candidate_bbox_equivalent_cases": sum(
            r["checks"].get("final_bbox_equivalent_to_baseline") is True for r in records
        ),
        "deferred_zero_measure_contacts": sum(r.get("deferred_zero_measure_contacts", 0) for r in records),
        "deduplicated_events": sum(r.get("deduplicated_events", 0) for r in records),
        "baseline_boolean_operations": sum(r.get("baseline_boolean_operations", 0) for r in records),
        "candidate_boolean_operations": sum(r.get("candidate_boolean_operations", 0) for r in records),
        "cells_builder_probes": len(cells_records),
        "cells_builder_measured": sum(
            r.get("cells_builder_probe_status") in {"measured", "measured_with_warning"} for r in cells_records
        ),
        "cells_builder_equivalent": sum(r.get("cells_builder_probe_equivalent") is True for r in cells_records),
        "step_attempts": len(step_records),
        "step_passes": sum(r["checks"].get("step_automated_roundtrip") is True for r in step_records),
    }

    output = {
        "results_schema": "rcs-009-results/1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "profile": args.profile,
        "backend": {
            "id": "occt",
            "version": "8.0.1",
            "tag": "V8_0_1",
            "commit": EXPECTED_COMMIT,
        },
        "candidate_model": plan["candidate"],
        "comparison_tolerances": plan["comparison_tolerances"],
        "records": records,
        "summary": summary,
    }
    (args.out_dir / "results.json").write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.out_dir / "summary.md").write_text(summary_markdown(output), encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 3 if candidate_failures else 0


if __name__ == "__main__":
    sys.exit(main())
