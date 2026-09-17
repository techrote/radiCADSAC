#!/usr/bin/env python3
"""Run the RCS-020 realistic lathe tool-envelope campaign."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from tool_envelope import (  # noqa: E402
    derive_groove_profile,
    derive_round_nose_profile,
    encode_worker_profile,
    groove_oracle_volume,
    holder_clearance_collision,
    oracle_round_nose_volume,
)

SCHEMA = "rcs-020-campaign-results/1.0"


def run_json_process(command: list[str], timeout_s: int = 120) -> dict[str, Any]:
    started = time.perf_counter()
    proc = subprocess.run(command, text=True, capture_output=True, timeout=timeout_s)
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    if proc.returncode != 0:
        raise RuntimeError(
            f"process failed rc={proc.returncode}: {' '.join(command)}\n"
            f"stdout={proc.stdout}\nstderr={proc.stderr}"
        )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"process did not emit JSON: {exc}\nstdout={proc.stdout}") from exc
    payload["_supervisor_elapsed_ms"] = elapsed_ms
    return payload


def abs_bbox_delta(a: dict[str, Any], b: dict[str, Any]) -> float:
    keys = ("xmin", "ymin", "zmin", "xmax", "ymax", "zmax")
    return max(abs(float(a[k]) - float(b[k])) for k in keys)


def evaluate_worker(
    worker: dict[str, Any], *, generated_volume: float, expected_body_count: int,
    policies: dict[str, Any], step_required: bool,
) -> dict[str, Any]:
    strategies = worker["strategies"]
    axis = strategies["axisymmetric_2d"]
    axis_metrics = axis["metrics"]
    checks: dict[str, bool] = {
        "axis_status": axis["status"] == "measured",
        "axis_valid_brep": bool(axis_metrics["valid_brep"]),
        "axis_body_count": int(axis_metrics["topology"]["solids"]) == expected_body_count,
        "profile_to_axis_volume": abs(float(axis_metrics["volume_mm3"]) - generated_volume)
        <= float(policies["max_occt_strategy_volume_delta_mm3"]),
    }

    for name in ("repeated_3d", "batched_3d"):
        strategy = strategies[name]
        metrics = strategy["metrics"]
        checks[f"{name}_status"] = strategy["status"] == "measured"
        checks[f"{name}_valid_brep"] = bool(metrics["valid_brep"])
        checks[f"{name}_body_count"] = int(metrics["topology"]["solids"]) == expected_body_count
        checks[f"{name}_volume_match"] = (
            abs(float(metrics["volume_mm3"]) - float(axis_metrics["volume_mm3"]))
            <= float(policies["max_occt_strategy_volume_delta_mm3"])
        )
        checks[f"{name}_bbox_match"] = (
            abs_bbox_delta(metrics["bbox_mm"], axis_metrics["bbox_mm"])
            <= float(policies["max_occt_bbox_delta_mm"])
        )

    step_summary: dict[str, Any] = {"required": step_required, "strategies": {}}
    if step_required:
        for name in ("repeated_3d", "batched_3d", "axisymmetric_2d"):
            step = strategies[name]["step"]
            readback = step["readback_metrics"]
            ok = bool(
                step["attempted"]
                and step["transfer_status"] == "done"
                and step["write_status"] == "done"
                and step["read_status"] == "done"
                and step["readback_transferred"]
                and readback["valid_brep"]
                and int(readback["topology"]["solids"]) == expected_body_count
                and float(step["volume_abs_delta_mm3"]) <= float(policies["max_step_volume_delta_mm3"])
                and float(step["bbox_max_abs_delta_mm"]) <= float(policies["max_step_bbox_delta_mm"])
            )
            checks[f"{name}_step_roundtrip"] = ok
            step_summary["strategies"][name] = {
                "passed_geometry_roundtrip": ok,
                "analytic_surfaces": readback["analytic_surfaces"],
                "volume_abs_delta_mm3": float(step["volume_abs_delta_mm3"]),
                "bbox_max_abs_delta_mm": float(step["bbox_max_abs_delta_mm"]),
            }

    return {
        "checks": checks,
        "all_required_checks_pass": all(checks.values()),
        "axis_metrics": axis_metrics,
        "step": step_summary,
        "analytic_nose_surface_exactly_qualified": False,
        "analytic_note": (
            "The RCS-010 comparator consumes a bounded polygonized material profile. "
            "Layer A-C geometry/read-back success does not qualify exact circular-nose/torus "
            "surface retention; that remains an explicit capability boundary."
        ),
    }


def invoke_lathe_worker(
    case: dict[str, Any], stock: dict[str, Any], profile_encoded: str, generated_volume: float,
    policies: dict[str, Any], lathe_worker: Path | None, out_dir: Path,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if lathe_worker is None:
        return None, None
    step_dir = out_dir / "step" / case["id"]
    step_dir.mkdir(parents=True, exist_ok=True)
    worker = run_json_process([
        str(lathe_worker), "--case-id", case["id"], "--profile", profile_encoded,
        "--stock-z0", str(stock["z0_mm"]), "--stock-z1", str(stock["z1_mm"]),
        "--stock-radius", str(stock["outer_radius_mm"]),
        "--event-count", str(case.get("journal_events", 1)), "--step-dir", str(step_dir),
    ], timeout_s=180)
    evaluation = evaluate_worker(
        worker, generated_volume=generated_volume,
        expected_body_count=int(case["expected"]["body_count"]), policies=policies,
        step_required=bool(case["expected"].get("step", False)),
    )
    return worker, evaluation


def round_nose_case(case: dict[str, Any], tool: dict[str, Any], policies: dict[str, Any], lathe_worker: Path | None, out_dir: Path) -> dict[str, Any]:
    stock = case["stock"]
    mode = "external" if case["kind"] == "round_nose_external" else "internal"
    path = [tuple(map(float, p)) for p in case["tool_path_zr_mm"]]
    profile = derive_round_nose_profile(
        path_zr_mm=path, nose_radius_mm=float(tool["nose_radius_mm"]),
        stock_z0_mm=float(stock["z0_mm"]), stock_z1_mm=float(stock["z1_mm"]),
        stock_outer_radius_mm=float(stock["outer_radius_mm"]), mode=mode,
        chord_tolerance_mm=float(policies["profile_chord_tolerance_mm"]),
        sampling_step_mm=float(policies["profile_sampling_step_mm"]),
    )
    oracle = oracle_round_nose_volume(
        path_zr_mm=path, nose_radius_mm=float(tool["nose_radius_mm"]),
        stock_z0_mm=float(stock["z0_mm"]), stock_z1_mm=float(stock["z1_mm"]),
        stock_outer_radius_mm=float(stock["outer_radius_mm"]), mode=mode, integration_step_mm=0.0002,
    )
    profile_volume = profile.volume_mm3()
    delta = abs(profile_volume - float(oracle["volume_mm3"]))
    reachability = None
    if tool["class"] == "external_turning":
        reachability = holder_clearance_collision(
            path_zr_mm=path,
            stock_outer_sections=[{"z0_mm": stock["z0_mm"], "z1_mm": stock["z1_mm"], "outer_radius_mm": stock["outer_radius_mm"]}],
            approach_angle_deg=float(tool["approach_angle_deg"]),
            holder_setback_mm=float(tool["holder_setback_mm"]), holder_length_mm=float(tool["holder_length_mm"]),
        )

    result: dict[str, Any] = {
        "case_id": case["id"], "kind": case["kind"], "tool_id": case["tool"], "tool_geometry": tool,
        "tool_path_zr_mm": case["tool_path_zr_mm"],
        "generator": {"profile_points": len(profile.boundary), "volume_mm3": profile_volume, "boundary": [[z, r] for z, r in profile.boundary], "polygon_points": len(profile.polygon_radius_z()), "declared_chord_tolerance_mm": policies["profile_chord_tolerance_mm"]},
        "oracle": oracle, "material_profile_volume_abs_delta_mm3": delta,
        "material_profile_within_budget": delta <= float(policies["max_material_profile_volume_delta_mm3"]),
        "oracle_convergence_within_budget": float(oracle["convergence_delta_mm3"]) <= float(policies["max_material_profile_volume_delta_mm3"]),
        "reachability": reachability, "expected": case["expected"],
    }
    if reachability is not None:
        result["reachability_pass"] = not reachability["collision"]
    worker, evaluation = invoke_lathe_worker(case, stock, encode_worker_profile(profile), profile_volume, policies, lathe_worker, out_dir)
    if worker is not None:
        result["occt"], result["occt_evaluation"] = worker, evaluation
    return result


def facing_case(case: dict[str, Any], tool: dict[str, Any], policies: dict[str, Any], lathe_worker: Path | None, out_dir: Path) -> dict[str, Any]:
    """Derive a faced front plane from the leftmost extent of a radiused nose radial sweep."""
    stock = case["stock"]
    path = [tuple(map(float, p)) for p in case["tool_path_zr_mm"]]
    nose = float(tool["nose_radius_mm"])
    if max(z for z, _ in path) - min(z for z, _ in path) > 1.0e-12:
        raise ValueError("facing research path must remain at one axial centre coordinate")
    radial_min = min(r for _, r in path) - nose
    radial_max = max(r for _, r in path) + nose
    if radial_min > 1.0e-9 or radial_max < float(stock["outer_radius_mm"]) - 1.0e-9:
        raise ValueError("facing path does not sweep from the spindle axis through the stock OD")
    face_z = path[0][0] - nose
    if not (float(stock["z0_mm"]) < face_z < float(stock["z1_mm"])):
        raise ValueError("derived face lies outside stock")

    radius = float(stock["outer_radius_mm"])
    generated_volume = math.pi * radius * radius * (float(stock["z1_mm"]) - face_z)
    profile_encoded = ";".join([
        f"0,{face_z:.17g}", f"{radius:.17g},{face_z:.17g}",
        f"{radius:.17g},{float(stock['z1_mm']):.17g}", f"0,{float(stock['z1_mm']):.17g}",
    ])
    oracle_face_z = min(z for z, _ in path) - math.hypot(nose, 0.0)
    oracle_volume = math.pi * radius * radius * (float(stock["z1_mm"]) - oracle_face_z)
    result: dict[str, Any] = {
        "case_id": case["id"], "kind": case["kind"], "tool_id": case["tool"], "tool_geometry": tool,
        "tool_path_zr_mm": case["tool_path_zr_mm"],
        "generator": {"result_front_z_mm": face_z, "volume_mm3": generated_volume, "radial_coverage_mm": [radial_min, radial_max]},
        "oracle": {"result_front_z_mm": oracle_face_z, "volume_mm3": oracle_volume, "method": "closed-form exact circular-nose axial support"},
        "material_profile_volume_abs_delta_mm3": abs(generated_volume - oracle_volume),
        "material_profile_within_budget": abs(generated_volume - oracle_volume) <= float(policies["max_material_profile_volume_delta_mm3"]),
        "front_plane_matches_expected": abs(face_z - float(case["expected"]["result_front_z_mm"])) <= 1.0e-12,
        "expected": case["expected"],
    }
    worker, evaluation = invoke_lathe_worker(case, stock, profile_encoded, generated_volume, policies, lathe_worker, out_dir)
    if worker is not None:
        result["occt"], result["occt_evaluation"] = worker, evaluation
    return result


def groove_case(case: dict[str, Any], tool: dict[str, Any], policies: dict[str, Any], lathe_worker: Path | None, out_dir: Path) -> dict[str, Any]:
    stock = case["stock"]
    corner = max(float(tool["left_corner_radius_mm"]), float(tool["right_corner_radius_mm"]))
    profile = derive_groove_profile(
        stock_z0_mm=float(stock["z0_mm"]), stock_z1_mm=float(stock["z1_mm"]),
        stock_outer_radius_mm=float(stock["outer_radius_mm"]), center_z_mm=float(case["groove_center_z_mm"]),
        cutting_width_mm=float(tool["cutting_width_mm"]), corner_radius_mm=corner,
        bottom_radius_mm=float(case["bottom_radius_mm"]), chord_tolerance_mm=float(policies["profile_chord_tolerance_mm"]),
    )
    oracle = groove_oracle_volume(
        stock_z0_mm=float(stock["z0_mm"]), stock_z1_mm=float(stock["z1_mm"]),
        stock_outer_radius_mm=float(stock["outer_radius_mm"]), center_z_mm=float(case["groove_center_z_mm"]),
        cutting_width_mm=float(tool["cutting_width_mm"]), corner_radius_mm=corner,
        bottom_radius_mm=float(case["bottom_radius_mm"]),
    )
    volume = profile.volume_mm3()
    delta = abs(volume - float(oracle["volume_mm3"]))
    result: dict[str, Any] = {
        "case_id": case["id"], "kind": case["kind"], "tool_id": case["tool"], "tool_geometry": tool,
        "generator": {"profile_points": len(profile.boundary), "volume_mm3": volume, "boundary": [[z, r] for z, r in profile.boundary]},
        "oracle": oracle, "material_profile_volume_abs_delta_mm3": delta,
        "material_profile_within_budget": delta <= float(policies["max_material_profile_volume_delta_mm3"]),
        "oracle_convergence_within_budget": float(oracle["convergence_delta_mm3"]) <= float(policies["max_material_profile_volume_delta_mm3"]),
        "expected": case["expected"],
    }
    worker, evaluation = invoke_lathe_worker(case, stock, encode_worker_profile(profile), volume, policies, lathe_worker, out_dir)
    if worker is not None:
        result["occt"], result["occt_evaluation"] = worker, evaluation
    return result


def parting_case(case: dict[str, Any], tool: dict[str, Any], policies: dict[str, Any], baseline_worker: Path | None, out_dir: Path) -> dict[str, Any]:
    stock = case["stock"]
    corner = max(float(tool["left_corner_radius_mm"]), float(tool["right_corner_radius_mm"]))
    profile = derive_groove_profile(
        stock_z0_mm=float(stock["z0_mm"]), stock_z1_mm=float(stock["z1_mm"]), stock_outer_radius_mm=float(stock["outer_radius_mm"]),
        center_z_mm=float(case["groove_center_z_mm"]), cutting_width_mm=float(tool["cutting_width_mm"]),
        corner_radius_mm=corner, bottom_radius_mm=float(case["bottom_radius_mm"]), chord_tolerance_mm=float(policies["profile_chord_tolerance_mm"]),
    )
    oracle = groove_oracle_volume(
        stock_z0_mm=float(stock["z0_mm"]), stock_z1_mm=float(stock["z1_mm"]), stock_outer_radius_mm=float(stock["outer_radius_mm"]),
        center_z_mm=float(case["groove_center_z_mm"]), cutting_width_mm=float(tool["cutting_width_mm"]),
        corner_radius_mm=corner, bottom_radius_mm=float(case["bottom_radius_mm"]),
    )
    effective_zero_gap = max(0.0, float(tool["cutting_width_mm"]) - 2.0 * corner)
    body_count = 2 if effective_zero_gap > 0.0 and float(case["bottom_radius_mm"]) <= 0.0 else 1
    result: dict[str, Any] = {
        "case_id": case["id"], "kind": case["kind"], "tool_id": case["tool"], "tool_geometry": tool,
        "generator": {"volume_mm3": profile.volume_mm3(), "boundary": [[z, r] for z, r in profile.boundary], "effective_zero_material_gap_mm": effective_zero_gap, "body_count": body_count},
        "oracle": oracle, "material_profile_volume_abs_delta_mm3": abs(profile.volume_mm3() - float(oracle["volume_mm3"])),
        "material_profile_within_budget": abs(profile.volume_mm3() - float(oracle["volume_mm3"])) <= float(policies["max_material_profile_volume_delta_mm3"]),
        "body_count_pass": body_count == int(case["expected"]["body_count"]), "expected": case["expected"],
    }
    if baseline_worker is not None:
        step_file = out_dir / "step" / f"{case['id']}-connectivity-control.step"
        step_file.parent.mkdir(parents=True, exist_ok=True)
        worker = run_json_process([
            str(baseline_worker), "--case", "lathe_parting", "--param", f"tool_width_mm={effective_zero_gap}",
            "--param", "fuzzy_mm=0", "--step-file", str(step_file), "--unit", "millimeter",
        ], timeout_s=120)
        metrics, step = worker["result_metrics"], worker["step"]
        connectivity_ok = bool(
            metrics["valid_brep"] and int(metrics["topology"]["solids"]) == int(case["expected"]["body_count"])
            and step["attempted"] and step["transfer_status"] == "done" and step["write_status"] == "done"
            and step["read_status"] == "done" and step["readback_transferred"] and step["readback_metrics"]["valid_brep"]
            and int(step["readback_metrics"]["topology"]["solids"]) == int(case["expected"]["body_count"])
        )
        result["connectivity_step_control"] = {
            "worker": worker, "control_gap_mm": effective_zero_gap, "passed": connectivity_ok,
            "scope": "body-connectivity and all-bodies STEP control; not rounded-corner envelope equivalence",
        }
    return result


def reachability_case(case: dict[str, Any], tool: dict[str, Any]) -> dict[str, Any]:
    probe = holder_clearance_collision(
        path_zr_mm=[tuple(map(float, p)) for p in case["tool_path_zr_mm"]], stock_outer_sections=case["stock_outer_sections"],
        approach_angle_deg=float(tool["approach_angle_deg"]), holder_setback_mm=float(tool["holder_setback_mm"]),
        holder_length_mm=float(tool["holder_length_mm"]),
    )
    classification = "refused_unsupported" if probe["collision"] else "unexpectedly_reachable"
    return {
        "case_id": case["id"], "kind": case["kind"], "tool_id": case["tool"], "tool_geometry": tool,
        "reachability": probe, "classification": classification, "expected": case["expected"],
        "pass": bool(probe["collision"]) and classification == case["expected"]["classification"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=HERE / "experiment-plan-v1.json")
    parser.add_argument("--lathe-worker", type=Path)
    parser.add_argument("--baseline-worker", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    policies = plan["policies"]
    results: list[dict[str, Any]] = []
    for case in plan["cases"]:
        tool = plan["tools"][case["tool"]]
        if case["kind"] in {"round_nose_external", "round_nose_internal"}:
            result = round_nose_case(case, tool, policies, args.lathe_worker, args.out_dir)
        elif case["kind"] == "facing_external":
            result = facing_case(case, tool, policies, args.lathe_worker, args.out_dir)
        elif case["kind"] == "groove":
            result = groove_case(case, tool, policies, args.lathe_worker, args.out_dir)
        elif case["kind"] == "parting":
            result = parting_case(case, tool, policies, args.baseline_worker, args.out_dir)
        elif case["kind"] == "reachability_refusal":
            result = reachability_case(case, tool)
        else:
            raise ValueError(f"unsupported case kind {case['kind']}")
        results.append(result)
        (args.out_dir / f"{case['id']}.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    aggregate = {
        "schema": SCHEMA, "plan_schema": plan["schema"], "case_count": len(results), "cases": results,
        "workers": {"lathe_worker": str(args.lathe_worker) if args.lathe_worker else None, "baseline_worker": str(args.baseline_worker) if args.baseline_worker else None},
    }
    (args.out_dir / "campaign-results.json").write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"schema": SCHEMA, "case_count": len(results), "out_dir": str(args.out_dir)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
