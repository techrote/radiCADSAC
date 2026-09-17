#!/usr/bin/env python3
"""Run RCS-007 tolerance/equivalence experiments against the RCS-006 OCCT worker."""

from __future__ import annotations

import argparse
import json
import math
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
PLAN_PATH = ROOT / "research/rcs-007/experiment-plan-v1.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise RuntimeError(f"{path}: expected JSON object")
    return value


def parse_final_json(stdout: str) -> tuple[dict[str, Any], list[str]]:
    diagnostics: list[str] = []
    for raw in reversed(stdout.splitlines()):
        line = raw.strip()
        if not line:
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            diagnostics.append(line)
            continue
        if isinstance(value, dict):
            diagnostics.reverse()
            return value, diagnostics
    raise RuntimeError("worker stdout contained no JSON object")


def run_worker(command: list[str], timeout_seconds: float = 60.0) -> dict[str, Any]:
    started = time.perf_counter()
    proc = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )
    wall_ms = (time.perf_counter() - started) * 1000.0
    record: dict[str, Any] = {
        "command": command,
        "returncode": proc.returncode,
        "wall_ms": wall_ms,
        "stderr": proc.stderr,
        "stdout_diagnostics": [],
        "payload": None,
    }
    if proc.returncode == 0:
        payload, diagnostics = parse_final_json(proc.stdout)
        record["payload"] = payload
        record["stdout_diagnostics"] = diagnostics
    else:
        record["stdout"] = proc.stdout
    return record


def decimal_text(value: float) -> str:
    return format(value, ".17g")


def bool_change(payload: dict[str, Any], threshold: float) -> bool:
    removed = float(payload.get("material_volume_removed_mm3", 0.0))
    return removed > threshold


def signed_expected_change(offset_mm: float) -> bool:
    return offset_mm < 0.0


def interval_decision(offset_mm: float, half_width_mm: float) -> str:
    if offset_mm < -half_width_mm:
        return "execute_material_change"
    if offset_mm > half_width_mm:
        return "clearance_noop"
    return "defer_uncertain_contact"


def interval_predicted_change(offset_mm: float, half_width_mm: float) -> bool:
    return offset_mm < -half_width_mm


def anchored_quantized(value_mm: float, quantum_mm: float) -> float:
    return round(value_mm / quantum_mm) * quantum_mm


def quantized_signed_predicted_change(offset_mm: float, quantum_mm: float) -> bool:
    return anchored_quantized(offset_mm, quantum_mm) < 0.0


def quantized_positive_predicted_change(depth_mm: float, quantum_mm: float) -> bool:
    return anchored_quantized(depth_mm, quantum_mm) > 0.0


def finish_signature(payload: dict[str, Any]) -> tuple[Any, ...]:
    return (
        bool(payload.get("valid_brep")),
        int(payload.get("solids", -1)),
        int(payload.get("faces", -1)),
        int(payload.get("edges", -1)),
    )


def local_model_for_skim(depth_mm: float) -> dict[str, Any]:
    # RCS-003 states that every strictly positive commanded skim is material-removal intent.
    # Numerical uncertainty may make a result unqualified but must not silently rewrite the intent.
    return {
        "decision": "execute_positive_removal" if depth_mm > 0.0 else "noop",
        "predicted_material_change": depth_mm > 0.0,
    }


def run_contact_sweeps(
    worker: Path,
    plan: dict[str, Any],
    profile: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    constants = plan["constants"]
    threshold = float(constants["volume_change_threshold_mm3"])
    interval_u = float(constants["local_interval_half_width_mm"])
    quantum = float(constants["anchored_quantum_mm"])
    results: list[dict[str, Any]] = []
    perturbation_candidates: dict[tuple[str, float, float], dict[str, Any]] = {}

    for sweep in plan["backend_sweeps"]:
        family = str(sweep["family"])
        case = str(sweep["worker_case"])
        parameter = str(sweep["parameter"])
        values = (
            profile["skim_depths_mm"]
            if family == "sub_tolerance_skim"
            else profile["contact_offsets_mm"]
        )
        for value in values:
            value = float(value)
            for fuzzy in profile["fuzzy_values_mm"]:
                fuzzy = float(fuzzy)
                command = [
                    str(worker),
                    "--case",
                    case,
                    "--param",
                    f"{parameter}={decimal_text(value)}",
                    "--param",
                    f"fuzzy_mm={decimal_text(fuzzy)}",
                ]
                executed = run_worker(command)
                record: dict[str, Any] = {
                    "family": family,
                    "worker_case": case,
                    "parameter": parameter,
                    "value_mm": value,
                    "fuzzy_mm": fuzzy,
                    "worker": executed,
                }
                payload = executed.get("payload")
                if isinstance(payload, dict):
                    actual_change = bool_change(payload, threshold)
                    if family == "sub_tolerance_skim":
                        expected_change = value > 0.0
                        local = local_model_for_skim(value)
                        quantized_change = quantized_positive_predicted_change(value, quantum)
                    else:
                        expected_change = signed_expected_change(value)
                        local = {
                            "decision": interval_decision(value, interval_u),
                            "predicted_material_change": interval_predicted_change(value, interval_u),
                        }
                        quantized_change = quantized_signed_predicted_change(value, quantum)

                    record.update(
                        {
                            "expected_material_change": expected_change,
                            "occt_material_change": actual_change,
                            "occt_matches_physical_oracle": actual_change == expected_change,
                            "operation_local_interval": {
                                **local,
                                "matches_physical_oracle": bool(local["predicted_material_change"])
                                == expected_change,
                            },
                            "anchored_quantization": {
                                "quantized_value_mm": anchored_quantized(value, quantum),
                                "predicted_material_change": quantized_change,
                                "matches_physical_oracle": quantized_change == expected_change,
                            },
                        }
                    )
                    perturbation_candidates[(family, value, fuzzy)] = record
                results.append(record)

    perturbations: list[dict[str, Any]] = []
    delta = float(plan["perturbation"]["delta_mm"])
    for family in plan["perturbation"]["families"]:
        for fuzzy in profile["fuzzy_values_mm"]:
            neg = perturbation_candidates.get((family, -delta, float(fuzzy)))
            pos = perturbation_candidates.get((family, delta, float(fuzzy)))
            zero = perturbation_candidates.get((family, 0.0, float(fuzzy)))
            if neg and pos and zero:
                perturbations.append(
                    {
                        "family": family,
                        "fuzzy_mm": float(fuzzy),
                        "delta_mm": delta,
                        "negative_material_change": neg.get("occt_material_change"),
                        "zero_material_change": zero.get("occt_material_change"),
                        "positive_material_change": pos.get("occt_material_change"),
                        "direction_changes_physical_result": (
                            neg.get("occt_material_change") != pos.get("occt_material_change")
                        ),
                    }
                )
    return results, perturbations


def run_repeated_finish(
    finish_worker: Path,
    plan: dict[str, Any],
    profile: dict[str, Any],
) -> list[dict[str, Any]]:
    depth = float(plan["repeated_finish"]["depth_mm"])
    volume_tol = float(plan["constants"]["geometry_equivalence_volume_mm3"])
    results: list[dict[str, Any]] = []
    for fuzzy in profile["fuzzy_values_mm"]:
        fuzzy = float(fuzzy)
        collapsed = run_worker(
            [
                str(finish_worker),
                "--mode",
                "repeated",
                "--repeat-count",
                "1",
                "--depth-mm",
                decimal_text(depth),
                "--fuzzy-mm",
                decimal_text(fuzzy),
            ]
        )
        collapsed_payload = collapsed.get("payload")
        for count in profile["repeat_counts"]:
            count = int(count)
            baseline = run_worker(
                [
                    str(finish_worker),
                    "--mode",
                    "repeated",
                    "--repeat-count",
                    str(count),
                    "--depth-mm",
                    decimal_text(depth),
                    "--fuzzy-mm",
                    decimal_text(fuzzy),
                ]
            )
            base_payload = baseline.get("payload")
            equivalent = False
            volume_delta = None
            speedup = None
            if isinstance(base_payload, dict) and isinstance(collapsed_payload, dict):
                volume_delta = abs(
                    float(base_payload["volume_mm3"]) - float(collapsed_payload["volume_mm3"])
                )
                equivalent = (
                    volume_delta <= volume_tol
                    and finish_signature(base_payload) == finish_signature(collapsed_payload)
                )
                collapsed_ms = max(float(collapsed_payload.get("geometry_ms", 0.0)), 1.0e-12)
                speedup = float(base_payload.get("geometry_ms", 0.0)) / collapsed_ms
            results.append(
                {
                    "repeat_count": count,
                    "depth_mm": depth,
                    "fuzzy_mm": fuzzy,
                    "baseline": baseline,
                    "semantic_replay_collapse_reference": collapsed,
                    "collapse_equivalent": equivalent,
                    "volume_delta_mm3": volume_delta,
                    "geometry_time_ratio_baseline_over_collapsed": speedup,
                }
            )
    return results


def run_accumulation_chains(
    finish_worker: Path,
    plan: dict[str, Any],
    profile: dict[str, Any],
) -> list[dict[str, Any]]:
    per_op_u = float(plan["constants"]["per_operation_numerical_uncertainty_mm"])
    volume_tol = float(plan["constants"]["geometry_equivalence_volume_mm3"])
    increment = float(profile["chain_increment_mm"])
    results: list[dict[str, Any]] = []

    for count in profile["chain_counts"]:
        count = int(count)
        for fuzzy in profile["fuzzy_values_mm"]:
            fuzzy = float(fuzzy)
            by_order: dict[str, dict[str, Any]] = {}
            for order in plan["accumulation_chain"]["orders"]:
                by_order[str(order)] = run_worker(
                    [
                        str(finish_worker),
                        "--mode",
                        "chain",
                        "--repeat-count",
                        str(count),
                        "--increment-mm",
                        decimal_text(increment),
                        "--order",
                        str(order),
                        "--fuzzy-mm",
                        decimal_text(fuzzy),
                    ]
                )
            asc_payload = by_order["ascending"].get("payload")
            desc_payload = by_order["descending"].get("payload")
            equivalent = False
            volume_delta = None
            topology_equal = False
            if isinstance(asc_payload, dict) and isinstance(desc_payload, dict):
                volume_delta = abs(
                    float(asc_payload["volume_mm3"]) - float(desc_payload["volume_mm3"])
                )
                topology_equal = finish_signature(asc_payload) == finish_signature(desc_payload)
                equivalent = volume_delta <= volume_tol and topology_equal
            results.append(
                {
                    "count": count,
                    "increment_mm": increment,
                    "fuzzy_mm": fuzzy,
                    "orders": by_order,
                    "order_equivalent": equivalent,
                    "order_volume_delta_mm3": volume_delta,
                    "order_topology_equal": topology_equal,
                    "uncertainty_bounds_mm": {
                        "conservative_linear": count * per_op_u,
                        "uncorrelated_rss": math.sqrt(count) * per_op_u,
                    },
                }
            )
    return results


def algebraic_results(plan: dict[str, Any]) -> dict[str, Any]:
    u = float(plan["constants"]["local_interval_half_width_mm"])
    q = float(plan["constants"]["anchored_quantum_mm"])
    a, b, c = 0.0, 0.75 * u, 1.5 * u
    close = lambda x, y: abs(x - y) <= u
    x, y = 0.49 * q, 0.51 * q
    return {
        "operation_local_interval_relation": {
            "definition": "abs(a-b) <= local_interval_half_width_mm",
            "reflexive": close(a, a),
            "symmetric_example": close(a, b) == close(b, a),
            "transitive_counterexample": {
                "a_mm": a,
                "b_mm": b,
                "c_mm": c,
                "a_related_b": close(a, b),
                "b_related_c": close(b, c),
                "a_related_c": close(a, c),
            },
            "conclusion": "compatibility relation is reflexive and symmetric but not transitive; do not use its transitive closure as global topology identity",
        },
        "anchored_quantization_relation": {
            "definition": "round(x/q) bucket equality",
            "is_equivalence_relation": True,
            "boundary_counterexample": {
                "x_mm": x,
                "y_mm": y,
                "distance_mm": abs(x - y),
                "x_bucket_mm": anchored_quantized(x, q),
                "y_bucket_mm": anchored_quantized(y, q),
                "same_bucket": anchored_quantized(x, q) == anchored_quantized(y, q),
            },
            "conclusion": "transitivity is purchased with grid-boundary discontinuities and coordinate relocation",
        },
    }


def summarize(
    contact: list[dict[str, Any]],
    perturbations: list[dict[str, Any]],
    repeated: list[dict[str, Any]],
    chains: list[dict[str, Any]],
) -> dict[str, Any]:
    measured = [r for r in contact if isinstance(r.get("worker", {}).get("payload"), dict)]
    occt_mismatch = sum(not bool(r.get("occt_matches_physical_oracle")) for r in measured)
    local_mismatch = sum(
        not bool(r.get("operation_local_interval", {}).get("matches_physical_oracle"))
        for r in measured
    )
    quant_mismatch = sum(
        not bool(r.get("anchored_quantization", {}).get("matches_physical_oracle"))
        for r in measured
    )
    worker_failures = sum(r.get("worker", {}).get("returncode") != 0 for r in contact)
    collapse_non_equiv = sum(
        int(r["repeat_count"]) > 1 and not bool(r["collapse_equivalent"]) for r in repeated
    )
    order_divergence = sum(not bool(r["order_equivalent"]) for r in chains)
    perturb_directional = sum(bool(r["direction_changes_physical_result"]) for r in perturbations)
    return {
        "backend_sweep_attempts": len(contact),
        "backend_sweep_worker_failures": worker_failures,
        "occt_global_fuzzy_oracle_mismatches": occt_mismatch,
        "operation_local_interval_oracle_mismatches": local_mismatch,
        "anchored_quantization_oracle_mismatches": quant_mismatch,
        "semantic_replay_collapse_non_equivalent_cases": collapse_non_equiv,
        "accumulation_order_divergent_cases": order_divergence,
        "controlled_perturbation_direction_sensitive_pairs": perturb_directional,
    }


def write_summary(path: Path, result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# RCS-007 experiment summary",
        "",
        f"Profile: `{result['profile']}`  ",
        f"OCCT: `{result['backend']['version']}` @ `{result['backend']['commit']}`",
        "",
        "## Aggregate observations",
        "",
        f"- Backend sweep attempts: {summary['backend_sweep_attempts']}.",
        f"- Worker failures: {summary['backend_sweep_worker_failures']}.",
        f"- OCCT global-fuzzy oracle mismatches: {summary['occt_global_fuzzy_oracle_mismatches']}.",
        f"- Operation-local interval oracle mismatches: {summary['operation_local_interval_oracle_mismatches']}.",
        f"- Anchored-quantization oracle mismatches: {summary['anchored_quantization_oracle_mismatches']}.",
        f"- Non-equivalent semantic replay-collapse cases: {summary['semantic_replay_collapse_non_equivalent_cases']}.",
        f"- Accumulation order-divergent cases: {summary['accumulation_order_divergent_cases']}.",
        f"- Direction-sensitive controlled-perturbation pairs: {summary['controlled_perturbation_direction_sensitive_pairs']}.",
        "",
        "The aggregate counts are evidence indices, not architecture decisions. Inspect `results.json` for the signed parameter/fuzzy-value records.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", required=True, type=Path)
    parser.add_argument("--finish-worker", required=True, type=Path)
    parser.add_argument("--profile", default="smoke", choices=("smoke", "baseline"))
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()

    plan = load_json(PLAN_PATH)
    profile = plan["profiles"][args.profile]
    args.out_dir.mkdir(parents=True, exist_ok=True)

    contact, perturbations = run_contact_sweeps(args.worker, plan, profile)
    repeated = run_repeated_finish(args.finish_worker, plan, profile)
    chains = run_accumulation_chains(args.finish_worker, plan, profile)

    result = {
        "results_schema": "rcs-007-results/1.0",
        "plan_id": plan["plan_id"],
        "profile": args.profile,
        "backend": plan["baseline"],
        "environment": {
            "platform": platform.platform(),
            "python": sys.version.split()[0],
        },
        "policy_channels": plan["policy_channels"],
        "candidate_models": plan["candidate_models"],
        "algebraic": algebraic_results(plan),
        "backend_sweeps": contact,
        "controlled_perturbation": perturbations,
        "repeated_finishing": repeated,
        "accumulation_chains": chains,
    }
    result["summary"] = summarize(contact, perturbations, repeated, chains)

    result_path = args.out_dir / "results.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_summary(args.out_dir / "summary.md", result)
    print(json.dumps(result["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
