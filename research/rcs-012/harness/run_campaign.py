#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import resource
import time
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 40
SCHEMA = "rcs-012-result/1.0"
VOXEL_H = Decimal("0.5")


def D(value: object) -> Decimal:
    return Decimal(str(value))


def box_key(box: dict[str, object]) -> tuple[str, ...]:
    return tuple(str(box[key]) for key in ("x0", "x1", "y0", "y1", "z0", "z1"))


def unique_removals(case: dict[str, object]) -> tuple[list[dict[str, object]], int]:
    seen: dict[tuple[str, ...], dict[str, object]] = {}
    raw_count = 0
    for item in case["removals"]:
        raw_count += int(item.get("repeat", 1))
        key = box_key(item)
        if key not in seen:
            seen[key] = {axis: item[axis] for axis in ("x0", "x1", "y0", "y1", "z0", "z1")}
    return list(seen.values()), raw_count


def contains(box: dict[str, object], x: Decimal, y: Decimal, z: Decimal) -> bool:
    return (
        D(box["x0"]) <= x < D(box["x1"])
        and D(box["y0"]) <= y < D(box["y1"])
        and D(box["z0"]) <= z < D(box["z1"])
    )


def components(occupied: set[tuple[int, int, int]]) -> int:
    seen: set[tuple[int, int, int]] = set()
    count = 0
    for start in occupied:
        if start in seen:
            continue
        count += 1
        seen.add(start)
        stack = [start]
        while stack:
            i, j, k = stack.pop()
            for neighbor in (
                (i + 1, j, k),
                (i - 1, j, k),
                (i, j + 1, k),
                (i, j - 1, k),
                (i, j, k + 1),
                (i, j, k - 1),
            ):
                if neighbor in occupied and neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
    return count


def exact_cell(case: dict[str, object]) -> dict[str, object]:
    stock = case["stock"]
    removals, raw_count = unique_removals(case)
    xs = sorted({D(stock["x0"]), D(stock["x1"])} | {D(box[key]) for box in removals for key in ("x0", "x1")})
    ys = sorted({D(stock["y0"]), D(stock["y1"])} | {D(box[key]) for box in removals for key in ("y0", "y1")})
    zs = sorted({D(stock["z0"]), D(stock["z1"])} | {D(box[key]) for box in removals for key in ("z0", "z1")})

    occupied: set[tuple[int, int, int]] = set()
    volume = D(0)
    tested = 0
    for i in range(len(xs) - 1):
        x = (xs[i] + xs[i + 1]) / 2
        for j in range(len(ys) - 1):
            y = (ys[j] + ys[j + 1]) / 2
            for k in range(len(zs) - 1):
                z = (zs[k] + zs[k + 1]) / 2
                tested += 1
                if contains(stock, x, y, z) and not any(contains(box, x, y, z) for box in removals):
                    occupied.add((i, j, k))
                    volume += (xs[i + 1] - xs[i]) * (ys[j + 1] - ys[j]) * (zs[k + 1] - zs[k])

    return {
        "material_volume_mm3": str(volume.normalize()),
        "body_count": components(occupied),
        "occupied_cells": len(occupied),
        "tested_cells": tested,
        "raw_operation_count": raw_count,
        "unique_envelope_count": len(removals),
        "analytic_semantics_retained": True,
        "surface_error_bound_mm": "0",
        "step_reconciliation": "exact-planar-constructive-within-bounded-subset",
    }


def voxel(case: dict[str, object]) -> dict[str, object]:
    stock = case["stock"]
    removals, raw_count = unique_removals(case)
    h = VOXEL_H
    x0, x1 = D(stock["x0"]), D(stock["x1"])
    y0, y1 = D(stock["y0"]), D(stock["y1"])
    z0, z1 = D(stock["z0"]), D(stock["z1"])
    nx, ny, nz = int((x1 - x0) / h), int((y1 - y0) / h), int((z1 - z0) / h)
    if D(nx) * h != x1 - x0 or D(ny) * h != y1 - y0 or D(nz) * h != z1 - z0:
        raise ValueError(f"{case['id']}: stock dimensions must align to voxel size {h}")

    occupied: set[tuple[int, int, int]] = set()
    for i in range(nx):
        x = x0 + (D(i) + D("0.5")) * h
        for j in range(ny):
            y = y0 + (D(j) + D("0.5")) * h
            for k in range(nz):
                z = z0 + (D(k) + D("0.5")) * h
                if not any(contains(box, x, y, z) for box in removals):
                    occupied.add((i, j, k))

    volume = D(len(occupied)) * (h**3)
    return {
        "material_volume_mm3": str(volume.normalize()),
        "body_count": components(occupied),
        "occupied_cells": len(occupied),
        "tested_cells": nx * ny * nz,
        "raw_operation_count": raw_count,
        "unique_envelope_count": len(removals),
        "analytic_semantics_retained": False,
        "surface_error_bound_mm": str((D(str(math.sqrt(3))) * h / D(2)).normalize()),
        "step_reconciliation": "surface-extraction-plus-recognition-required",
    }


def signature(observation: dict[str, object]) -> str:
    durable = {
        key: observation[key]
        for key in (
            "material_volume_mm3",
            "body_count",
            "occupied_cells",
            "raw_operation_count",
            "unique_envelope_count",
            "analytic_semantics_retained",
            "surface_error_bound_mm",
            "step_reconciliation",
        )
    }
    payload = json.dumps(durable, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def run(plan: dict[str, object], repeats: int) -> list[dict[str, object]]:
    adapters = [
        ("exact-orthogonal-cell-deferred-csg", exact_cell),
        ("sparse-voxel-center-0p5mm", voxel),
    ]
    rows: list[dict[str, object]] = []
    for case in plan["cases"]:
        expected = case["expected"]
        for candidate, adapter in adapters:
            group_start = len(rows)
            signatures: list[str] = []
            for attempt in range(1, repeats + 1):
                started = time.perf_counter()
                observation = adapter(case)
                elapsed_ms = (time.perf_counter() - started) * 1000.0
                expected_volume = D(expected["material_volume_mm3"])
                observed_volume = D(observation["material_volume_mm3"])
                absolute_error = abs(observed_volume - expected_volume)
                observation["volume_error_mm3"] = str(absolute_error.normalize())
                observation["volume_error_relative"] = str(
                    (absolute_error / expected_volume if expected_volume != 0 else D(0)).normalize()
                )
                observation["body_count_matches_oracle"] = observation["body_count"] == int(expected["body_count"])
                engineering_signature = signature(observation)
                signatures.append(engineering_signature)
                rows.append(
                    {
                        "schema": SCHEMA,
                        "case_id": case["id"],
                        "source_family": case["source_family"],
                        "candidate": candidate,
                        "attempt": attempt,
                        "runtime_ms": round(elapsed_ms, 6),
                        "peak_rss_kib": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
                        "oracle": expected,
                        "observation": observation,
                        "engineering_signature": engineering_signature,
                    }
                )
            stable = len(set(signatures)) == 1
            for row in rows[group_start:]:
                row["deterministic_engineering_signature"] = stable
    return rows


def summarize(plan: dict[str, object], rows: list[dict[str, object]]) -> dict[str, object]:
    by_candidate: dict[str, dict[str, object]] = {}
    for row in rows:
        bucket = by_candidate.setdefault(
            row["candidate"],
            {
                "attempts": 0,
                "oracle_volume_exact": 0,
                "oracle_body_exact": 0,
                "max_volume_error_mm3": D(0),
                "cases": set(),
            },
        )
        bucket["attempts"] += 1
        bucket["cases"].add(row["case_id"])
        if D(row["observation"]["volume_error_mm3"]) == 0:
            bucket["oracle_volume_exact"] += 1
        if row["observation"]["body_count_matches_oracle"]:
            bucket["oracle_body_exact"] += 1
        bucket["max_volume_error_mm3"] = max(
            bucket["max_volume_error_mm3"], D(row["observation"]["volume_error_mm3"])
        )

    summary = {
        "schema": "rcs-012-summary/1.0",
        "campaign": plan["campaign"],
        "case_count": len(plan["cases"]),
        "candidate_count": len(plan["candidates"]),
        "candidates": {},
    }
    for candidate, bucket in by_candidate.items():
        nondeterministic_groups = 0
        for case in plan["cases"]:
            group = [
                row
                for row in rows
                if row["candidate"] == candidate and row["case_id"] == case["id"]
            ]
            if group and not group[0]["deterministic_engineering_signature"]:
                nondeterministic_groups += 1
        summary["candidates"][candidate] = {
            "cases": len(bucket["cases"]),
            "attempts": bucket["attempts"],
            "oracle_volume_exact_attempts": bucket["oracle_volume_exact"],
            "oracle_body_exact_attempts": bucket["oracle_body_exact"],
            "nondeterministic_case_groups": nondeterministic_groups,
            "max_volume_error_mm3": str(bucket["max_volume_error_mm3"].normalize()),
        }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    root = Path(__file__).resolve().parents[1]
    parser.add_argument("--plan", type=Path, default=root / "experiment-plan-v1.json")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=2)
    args = parser.parse_args()

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows = run(plan, args.repeats)
    summary = summarize(plan, rows)

    (args.out_dir / "results.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8"
    )
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    lines = [
        "# RCS-012 runtime summary",
        "",
        f"Cases: {summary['case_count']} · candidates: {summary['candidate_count']}",
        "",
        "| Candidate | Attempts | exact volume | body oracle | max volume error mm³ | nondeterministic groups |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for candidate, metrics in summary["candidates"].items():
        lines.append(
            f"| `{candidate}` | {metrics['attempts']} | {metrics['oracle_volume_exact_attempts']} | "
            f"{metrics['oracle_body_exact_attempts']} | {metrics['max_volume_error_mm3']} | "
            f"{metrics['nondeterministic_case_groups']} |"
        )
    (args.out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
