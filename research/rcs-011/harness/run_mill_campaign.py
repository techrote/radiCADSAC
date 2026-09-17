#!/usr/bin/env python3
"""Run the RCS-011 fixed-orientation milling strategy campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
PLAN_PATH = ROOT / "research/rcs-011/experiment-plan-v1.json"
STOCK_VOLUME_MM3 = 40.0 * 30.0 * 10.0


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def quantize(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 9)
    if isinstance(value, dict):
        return {k: quantize(v) for k, v in sorted(value.items())}
    if isinstance(value, list):
        return [quantize(v) for v in value]
    return value


def signature(payload: dict[str, Any]) -> str:
    selected = {
        "success": payload.get("success"),
        "geometry": payload.get("geometry"),
        "step": payload.get("step"),
        "material_booleans": payload.get("material_booleans"),
        "envelope_primitives": payload.get("envelope_primitives"),
        "canonical_segments": payload.get("canonical_segments"),
    }
    blob = json.dumps(quantize(selected), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def strict_recognize(sample: dict[str, Any]) -> str:
    tag = sample.get("semantic_tag")
    if tag == "drill":
        return "explicit_drill"
    points = sample.get("points", [])
    if not isinstance(points, list) or len(points) < 2:
        return "unrecognized"

    parsed: list[tuple[float, float, float]] = []
    for p in points:
        if not isinstance(p, list) or len(p) != 3:
            return "unrecognized"
        parsed.append((float(p[0]), float(p[1]), float(p[2])))

    z0 = parsed[0][2]
    if any(abs(p[2] - z0) > 1e-12 for p in parsed):
        return "unrecognized"

    ax, ay, _ = parsed[0]
    bx, by, _ = parsed[-1]
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    if length <= 1e-12:
        return "unrecognized"
    last_t = -math.inf
    for x, y, _ in parsed:
        cross = (x - ax) * dy - (y - ay) * dx
        if abs(cross) > 1e-9 * max(1.0, length):
            return "unrecognized"
        t = ((x - ax) * dx + (y - ay) * dy) / (length * length)
        if t + 1e-12 < last_t:
            return "unrecognized"
        last_t = t
    return "strict_linear_slot"


def run_worker(
    worker: Path,
    case_id: str,
    strategy: str,
    step_path: Path | None,
    timeout_s: float,
) -> tuple[dict[str, Any] | None, str, int | None, float]:
    command = [str(worker), "--case", case_id, "--strategy", strategy]
    if step_path is not None:
        command.extend(["--step", str(step_path)])
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return None, f"timeout after {timeout_s}s: {exc}", None, (time.perf_counter() - started) * 1000.0
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    stdout = completed.stdout.strip().splitlines()
    if not stdout:
        return None, completed.stderr.strip() or "worker produced no stdout", completed.returncode, elapsed_ms
    try:
        payload = json.loads(stdout[-1])
    except json.JSONDecodeError as exc:
        return None, f"worker JSON parse failed: {exc}; stdout={completed.stdout!r}; stderr={completed.stderr!r}", completed.returncode, elapsed_ms
    if not isinstance(payload, dict):
        return None, "worker JSON root is not an object", completed.returncode, elapsed_ms
    if completed.stderr.strip():
        payload.setdefault("stderr", completed.stderr.strip())
    return payload, "", completed.returncode, elapsed_ms


def bbox_delta(a: dict[str, Any], b: dict[str, Any]) -> float:
    aa = a.get("bbox_mm", {})
    bb = b.get("bbox_mm", {})
    keys = ("xmin", "ymin", "zmin", "xmax", "ymax", "zmax")
    try:
        return max(abs(float(aa[k]) - float(bb[k])) for k in keys)
    except (KeyError, TypeError, ValueError):
        return math.inf


def compare_geometry(candidate: dict[str, Any], reference: dict[str, Any]) -> dict[str, Any]:
    cg = candidate.get("geometry", {})
    rg = reference.get("geometry", {})
    try:
        volume_delta = abs(float(cg.get("volume_mm3")) - float(rg.get("volume_mm3")))
    except (TypeError, ValueError):
        volume_delta = math.inf
    ctop = cg.get("topology", {})
    rtop = rg.get("topology", {})
    try:
        face_growth = int(ctop.get("faces", 0)) - int(rtop.get("faces", 0))
        edge_growth = int(ctop.get("edges", 0)) - int(rtop.get("edges", 0))
    except (TypeError, ValueError):
        face_growth = None
        edge_growth = None
    return {
        "volume_delta_mm3": volume_delta,
        "bbox_delta_mm": bbox_delta(cg, rg),
        "face_count_delta": face_growth,
        "edge_count_delta": edge_growth,
    }


def classify_attempt(
    case: dict[str, Any],
    payload: dict[str, Any] | None,
    returncode: int | None,
    worker_error: str,
    policies: dict[str, Any],
) -> tuple[str, list[str]]:
    notes: list[str] = []
    if payload is None:
        if returncode is None:
            return "hang/timeout", [worker_error]
        return "crash", [worker_error]
    if returncode not in (0, None):
        return "algorithm returned error/status", [payload.get("error") or worker_error or f"exit {returncode}"]
    if not payload.get("success", False):
        return "algorithm returned error/status", [str(payload.get("error", "worker reported failure"))]
    geom = payload.get("geometry")
    if not isinstance(geom, dict):
        return "invalid topology", ["missing geometry object"]
    if not geom.get("valid_brep", False):
        return "invalid topology", ["BRepCheck_Analyzer reported invalid result"]

    expected_bodies = int(case["expected_body_count"])
    actual_bodies = int(geom.get("topology", {}).get("solids", -1))
    if actual_bodies != expected_bodies:
        return "valid topology but wrong geometry", [f"expected {expected_bodies} solids, observed {actual_bodies}"]

    if case.get("expected_no_material_change"):
        delta = abs(float(geom.get("volume_mm3", math.nan)) - STOCK_VOLUME_MM3)
        if not math.isfinite(delta) or delta > float(policies["volume_compare_abs_mm3"]):
            return "valid topology but wrong geometry", [f"zero-volume-change oracle breached by {delta} mm^3"]

    step = payload.get("step", {})
    if case.get("step"):
        if not isinstance(step, dict) or not step.get("attempted"):
            return "STEP writer failure", ["STEP-required case did not attempt STEP"]
        if step.get("write_status") != "done":
            return "STEP writer failure", [f"writer status {step.get('write_status')}"]
        if step.get("read_status") != "done" or not step.get("readback_transferred", False):
            return "STEP round-trip failure", [f"reader status {step.get('read_status')}"]
        readback = step.get("readback", {})
        if not isinstance(readback, dict) or not readback.get("valid_brep", False):
            return "STEP round-trip failure", ["read-back B-rep invalid"]
        read_bodies = int(readback.get("topology", {}).get("solids", -1))
        if read_bodies != expected_bodies:
            return "STEP round-trip failure", [f"STEP body count {read_bodies}, expected {expected_bodies}"]
        if abs(float(step.get("volume_delta_mm3", math.inf))) > float(policies["step_volume_abs_mm3"]):
            return "STEP round-trip failure", [f"STEP volume delta {step.get('volume_delta_mm3')} mm^3"]
        if abs(float(step.get("bbox_delta_mm", math.inf))) > float(policies["step_bbox_abs_mm"]):
            return "STEP round-trip failure", [f"STEP bbox delta {step.get('bbox_delta_mm')} mm"]
    return "success", notes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", type=Path, required=True)
    parser.add_argument("--profile", choices=("smoke", "baseline"), default="smoke")
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    plan = load_json(PLAN_PATH)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    step_dir = args.out_dir / "step"
    step_dir.mkdir(exist_ok=True)
    cases_by_id = {case["id"]: case for case in plan["cases"]}
    selected_ids = plan["profiles"][args.profile]
    records: list[dict[str, Any]] = []
    structural_failures = 0
    required_acceptance_failures = 0

    recognition_results: list[dict[str, str]] = []
    for sample in plan.get("recognition_samples", []):
        observed = strict_recognize(sample)
        expected = sample["expected"]
        recognition_results.append({"id": sample["id"], "expected": expected, "observed": observed})
        if observed != expected:
            structural_failures += 1

    for case_id in selected_ids:
        case = cases_by_id[case_id]
        per_strategy: dict[str, list[dict[str, Any]]] = {}
        reference_payload: dict[str, Any] | None = None
        strategies = list(case["strategies"])
        ref_id = case["reference_strategy"]
        strategies.remove(ref_id)
        strategies.insert(0, ref_id)

        for strategy in strategies:
            attempts: list[dict[str, Any]] = []
            for attempt in range(1, args.repeats + 1):
                step_path = step_dir / f"{case_id}--{strategy}--{attempt}.step" if case.get("step") else None
                payload, worker_error, returncode, wall_ms = run_worker(args.worker, case_id, strategy, step_path, args.timeout)
                classification, notes = classify_attempt(case, payload, returncode, worker_error, plan["policies"])
                if strategy == ref_id and case.get("required", True) and classification != "success":
                    required_acceptance_failures += 1
                record: dict[str, Any] = {
                    "schema": "rcs-011-result/1.0",
                    "case_id": case_id,
                    "source_family": case["source_family"],
                    "tool": case["tool"],
                    "strategy": strategy,
                    "reference_strategy": ref_id,
                    "hierarchy_level": next(s["hierarchy_level"] for s in plan["strategies"] if s["id"] == strategy),
                    "attempt": attempt,
                    "classification": classification,
                    "required": bool(case.get("required", True)),
                    "wall_ms": wall_ms,
                    "notes": notes,
                    "worker": payload,
                }
                if payload is not None:
                    record["signature"] = signature(payload)
                attempts.append(record)
                records.append(record)
                if attempt == 1 and strategy == ref_id and classification == "success" and payload is not None:
                    reference_payload = payload
            per_strategy[strategy] = attempts

        if reference_payload is None:
            if case.get("required", True):
                required_acceptance_failures += 1
            continue

        for strategy, attempts in per_strategy.items():
            for record in attempts:
                payload = record.get("worker")
                if not isinstance(payload, dict) or not payload.get("success"):
                    continue
                comparison = compare_geometry(payload, reference_payload)
                record["reference_comparison"] = comparison
                if strategy != ref_id:
                    over_volume = comparison["volume_delta_mm3"] > float(plan["policies"]["volume_compare_abs_mm3"])
                    over_bbox = comparison["bbox_delta_mm"] > float(plan["policies"]["bbox_compare_abs_mm"])
                    if over_volume or over_bbox:
                        record["fidelity_within_reference_budget"] = False
                        record["classification"] = "geometric tolerance breach"
                        if strategy == "sampled_fallback":
                            record["notes"].append("sampled fallback exceeded exact-envelope fidelity budget; retained as negative evidence")
                        else:
                            record["notes"].append("candidate hierarchy strategy disagreed with reference; retained as negative evidence")
                    else:
                        record["fidelity_within_reference_budget"] = True

        for strategy, attempts in per_strategy.items():
            sigs = {a.get("signature") for a in attempts if a.get("signature")}
            if len(sigs) > 1:
                for record in attempts:
                    if record.get("classification") == "success":
                        record["classification"] = "nondeterministic result"
                        record["notes"].append("repeat engineering signature changed")
                if strategy == ref_id and case.get("required", True):
                    required_acceptance_failures += 1

    tolerated_negative_results = sum(
        1
        for record in records
        if record["classification"] != "success"
        and not (
            record.get("required", True)
            and record.get("strategy") == record.get("reference_strategy")
        )
    )

    results_path = args.out_dir / "results.jsonl"
    with results_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    successful = sum(1 for record in records if record["classification"] == "success")
    classifications: dict[str, int] = {}
    for record in records:
        classifications[record["classification"]] = classifications.get(record["classification"], 0) + 1

    measured_summary: dict[str, Any] = {
        "schema": "rcs-011-measured-summary/1.0",
        "profile": args.profile,
        "attempt_count": len(records),
        "successful_attempt_count": successful,
        "classifications": classifications,
        "structural_failure_count": structural_failures,
        "required_acceptance_failure_count": required_acceptance_failures,
        "tolerated_negative_result_count": tolerated_negative_results,
        "recognition_results": recognition_results,
        "backend": plan["baseline"],
        "host": {"platform": platform.platform(), "python": sys.version.split()[0]},
        "strategy_aggregates": {},
    }
    for strategy in [s["id"] for s in plan["strategies"]]:
        subset = [r for r in records if r["strategy"] == strategy and isinstance(r.get("worker"), dict)]
        if not subset:
            continue
        runtimes = [float(r["worker"].get("runtime_ms", 0.0)) for r in subset]
        booleans = [int(r["worker"].get("material_booleans", 0)) for r in subset]
        primitives = [int(r["worker"].get("envelope_primitives", 0)) for r in subset]
        geometry_subset = [r for r in subset if isinstance(r["worker"].get("geometry"), dict)]
        measured_summary["strategy_aggregates"][strategy] = {
            "attempts": len(subset),
            "runtime_ms_total": sum(runtimes),
            "runtime_ms_mean": sum(runtimes) / len(runtimes),
            "material_booleans_total": sum(booleans),
            "envelope_primitives_total": sum(primitives),
            "max_faces": max((int(r["worker"]["geometry"]["topology"]["faces"]) for r in geometry_subset), default=0),
            "max_edges": max((int(r["worker"]["geometry"]["topology"]["edges"]) for r in geometry_subset), default=0),
        }

    (args.out_dir / "measured-summary.json").write_text(
        json.dumps(measured_summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    campaign = {
        "schema": "rcs-011-campaign/1.0",
        "profile": args.profile,
        "plan": str(PLAN_PATH.relative_to(ROOT)),
        "plan_sha256": hashlib.sha256(PLAN_PATH.read_bytes()).hexdigest(),
        "worker": str(args.worker),
        "repeats": args.repeats,
        "timeout_s": args.timeout,
        "backend": plan["baseline"],
        "result_files": ["results.jsonl", "measured-summary.json", "summary.md"],
        "structural_failure_count": structural_failures,
        "required_acceptance_failure_count": required_acceptance_failures,
        "tolerated_negative_result_count": tolerated_negative_results,
    }
    (args.out_dir / "campaign.json").write_text(
        json.dumps(campaign, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# RCS-011 milling campaign summary",
        "",
        f"- Profile: `{args.profile}`",
        f"- Attempts: {len(records)}",
        f"- Successful attempts: {successful}",
        f"- Structural failures: {structural_failures}",
        f"- Required acceptance failures: {required_acceptance_failures}",
        f"- Tolerated negative results: {tolerated_negative_results}",
        "",
        "## Classification counts",
        "",
    ]
    for key in sorted(classifications):
        lines.append(f"- `{key}`: {classifications[key]}")
    lines += ["", "## Recognition guard", ""]
    for item in recognition_results:
        lines.append(f"- `{item['id']}`: expected `{item['expected']}`, observed `{item['observed']}`")
    lines += ["", "## Strategy aggregates", ""]
    for strategy, agg in measured_summary["strategy_aggregates"].items():
        lines.append(
            f"- `{strategy}`: attempts={agg['attempts']}, runtime_total={agg['runtime_ms_total']:.3f} ms, "
            f"material_booleans={agg['material_booleans_total']}, envelope_primitives={agg['envelope_primitives_total']}, "
            f"max_faces={agg['max_faces']}, max_edges={agg['max_edges']}"
        )
    (args.out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    if structural_failures:
        return 3
    if required_acceptance_failures:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
