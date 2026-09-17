#!/usr/bin/env python3
"""Independent Python decision path for RCS-019 canonicalizer conformance."""
from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path
from typing import Any

I64_MIN = -(1 << 63)
I64_MAX = (1 << 63) - 1
MASK64 = (1 << 64) - 1


def round_even(num: int, den: int) -> int:
    if den <= 0:
        raise ValueError("denominator must be positive")
    sign = -1 if num < 0 else 1
    n = abs(num)
    q, r = divmod(n, den)
    twice = 2 * r
    if twice > den or (twice == den and q % 2 == 1):
        q += 1
    return sign * q


def accepted(**kwargs: Any) -> dict[str, Any]:
    return {"status": "accepted", **kwargs}


def refused(code: str) -> dict[str, Any]:
    return {"status": "refused", "code": code}


def as_ints(values: list[str]) -> list[int]:
    return [int(x) for x in values]


def q15_check(q: list[int], policy: dict[str, Any]) -> dict[str, Any]:
    if any(x < I64_MIN or x > I64_MAX for x in q):
        return refused("INTEGER_OVERFLOW")
    if all(x == 0 for x in q):
        return refused("ZERO_QUATERNION")
    scale = int(policy["q15_scale"])
    eps = int(policy["q15_norm_tolerance_tokens"])
    n2 = sum(x * x for x in q)
    if not ((scale - eps) ** 2 <= n2 <= (scale + eps) ** 2):
        return refused("QUATERNION_NORM_OUT_OF_RANGE")
    for x in q:
        if x:
            if x < 0:
                q = [-v for v in q]
            break
    return accepted(q=[str(v) for v in q])


def rotate_exact(q: list[int], p: list[int]) -> list[int]:
    w, x, y, z = q
    n2 = w*w + x*x + y*y + z*z
    if n2 == 0:
        raise ValueError("zero quaternion")
    matrix = (
        (w*w + x*x - y*y - z*z, 2*(x*y - w*z), 2*(x*z + w*y)),
        (2*(x*y + w*z), w*w - x*x + y*y - z*z, 2*(y*z - w*x)),
        (2*(x*z - w*y), 2*(y*z + w*x), w*w - x*x - y*y + z*z),
    )
    out: list[int] = []
    for row in matrix:
        numerator = sum(a*b for a, b in zip(row, p))
        qv, rv = divmod(abs(numerator), n2)
        if rv != 0:
            raise ValueError("test transform does not map exactly to integer nanometres")
        out.append(-qv if numerator < 0 else qv)
    return out


def frame_graph(frames: list[dict[str, Any]]) -> dict[str, Any]:
    ids = [f["id"] for f in frames]
    if len(set(ids)) != len(ids):
        return refused("DUPLICATE_FRAME_ID")
    known = set(ids)
    for frame in frames:
        parent = frame.get("parent")
        if parent is not None and parent not in known:
            return refused("UNKNOWN_PARENT_FRAME")
    remaining = {f["id"]: f.get("parent") for f in frames}
    order: list[str] = []
    while remaining:
        progressed = False
        for fid in ids:
            if fid not in remaining:
                continue
            parent = remaining[fid]
            if parent is None or parent in order:
                order.append(fid)
                del remaining[fid]
                progressed = True
        if not progressed:
            return refused("FRAME_CYCLE")
    return accepted(topological_order=order)


def segment_samples(samples: list[dict[str, Any]]) -> dict[str, Any]:
    quantized: list[str] = []
    segments: list[list[str]] = []
    current: list[str] = []
    prev: tuple[Any, ...] | None = None
    for sample in samples:
        context = (sample["engaged"], sample["tool"], sample["setup"], sample["body"])
        qx = round_even(int(sample["x_num"]), int(sample["x_den"]))
        quantized.append(str(qx))
        if prev is None or context == prev:
            current.append(sample["id"])
        else:
            segments.append(current)
            current = [sample["id"]]
        prev = context
    if current:
        segments.append(current)
    return accepted(segments=segments, quantized_x_nm=quantized)


def compress_collinear(points: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if len(points) <= 2:
        return points[:]
    out = [points[0]]
    for i in range(1, len(points) - 1):
        a = out[-1]
        b = points[i]
        c = points[i + 1]
        abx, aby = b[0] - a[0], b[1] - a[1]
        bcx, bcy = c[0] - b[0], c[1] - b[1]
        if abx * bcy - aby * bcx == 0 and abx * bcx + aby * bcy >= 0:
            continue
        out.append(b)
    out.append(points[-1])
    return out


def interp(a: tuple[int, int], b: tuple[int, int], num: int, den: int) -> tuple[int, int]:
    return (
        a[0] + round_even((b[0] - a[0]) * num, den),
        a[1] + round_even((b[1] - a[1]) * num, den),
    )


def evaluate(vector: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    op = vector["operation"]
    data = vector["input"]
    if op == "round_rational":
        value = round_even(int(data["numerator"]), int(data["denominator"]))
        return accepted(integer=str(value))
    if op == "convert_length":
        scale = {"mm": 1_000_000, "inch": 25_400_000}.get(data["unit"])
        if scale is None:
            return refused("UNKNOWN_UNIT")
        value = round_even(int(data["numerator"]) * scale, int(data["denominator"]))
        if value < I64_MIN or value > I64_MAX:
            return refused("INTEGER_OVERFLOW")
        return accepted(length_nm=str(value))
    if op == "validate_i64":
        value = int(data["value"])
        if value < I64_MIN or value > I64_MAX:
            return refused("INTEGER_OVERFLOW")
        return accepted(value=str(value))
    if op == "canonicalize_q15":
        return q15_check(as_ints(data["q"]), policy)
    if op == "apply_transform_chain":
        p = as_ints(data["point_nm"])
        for transform in data["transforms"]:
            q = as_ints(transform["q"])
            check = q15_check(q[:], policy)
            if check["status"] != "accepted":
                return check
            p = rotate_exact(q, p)
            p = [x + y for x, y in zip(p, as_ints(transform["t_nm"]))]
            if any(x < I64_MIN or x > I64_MAX for x in p):
                return refused("INTEGER_OVERFLOW")
        return accepted(point_nm=[str(v) for v in p])
    if op == "validate_frame_graph":
        return frame_graph(data["frames"])
    if op == "stable_timestamp_order":
        decorated = [(int(s["time_ns"]), i, s["id"]) for i, s in enumerate(data["samples"])]
        decorated.sort(key=lambda x: (x[0], x[1]))
        return accepted(ids=[x[2] for x in decorated])
    if op == "segment_samples":
        return segment_samples(data["samples"])
    if op == "classify_arc":
        sweep = abs(int(data["sweep_nrad"]))
        err = int(data["certified_error_nm"])
        allowed = int(data["allowed_error_nm"])
        full = int(policy["full_circle_nrad"])
        low = int(policy["min_arc_sweep_nrad"])
        guard = int(policy["full_circle_guard_nrad"])
        if sweep < low or abs(full - sweep) < guard:
            return accepted(representation="polyline", reason="ARC_SWEEP_AMBIGUOUS")
        if err > allowed:
            return accepted(representation="polyline", reason="FIT_BOUND_UNCERTIFIED")
        return accepted(representation="arc")
    if op == "choose_fit":
        if int(data["certified_error_nm"]) <= int(data["allowed_error_nm"]):
            return accepted(representation=data["candidate"])
        return accepted(representation="polyline", reason="FIT_BOUND_UNCERTIFIED")
    if op == "equivalent_linear_sampling":
        start = tuple(as_ints(data["start_nm"]))
        end = tuple(as_ints(data["end_nm"]))
        outputs = []
        for count in data["sample_counts"]:
            den = count - 1
            points = [interp(start, end, i, den) for i in range(count)]
            outputs.append(compress_collinear(points))
        identical = all(o == outputs[0] for o in outputs[1:])
        return accepted(all_identical=identical, representation="line" if len(outputs[0]) == 2 else "polyline", max_error_nm="0")
    if op == "equivalent_v_sampling":
        start = tuple(as_ints(data["start_nm"]))
        mid = tuple(as_ints(data["mid_nm"]))
        end = tuple(as_ints(data["end_nm"]))
        outputs = []
        for count in data["sample_counts"]:
            den = count - 1
            half = den // 2
            if den % 2:
                raise ValueError("V-path test count must include midpoint")
            points = [interp(start, mid, i, half) for i in range(half + 1)]
            points += [interp(mid, end, i, half) for i in range(1, half + 1)]
            outputs.append(compress_collinear(points))
        identical = all(o == outputs[0] for o in outputs[1:])
        encoded = [[str(x), str(y)] for x, y in outputs[0]]
        return accepted(all_identical=identical, representation="polyline", points_nm=encoded, max_error_nm="0")
    if op == "noisy_line_trace":
        count = int(data["sample_count"])
        state = int(data["seed"]) & MASK64
        radius = int(data["noise_radius_nm"])
        allowed = int(data["allowed_error_nm"])
        observed = 0
        for i in range(count):
            if i == 0 or i == count - 1:
                y = 0
            else:
                state = (6364136223846793005 * state + 1442695040888963407) & MASK64
                y = int(state % (2 * radius + 1)) - radius
            observed = max(observed, abs(y))
        if observed > allowed:
            return refused("FIT_BOUND_UNCERTIFIED")
        return accepted(representation="line", max_error_nm=str(observed), sample_count=count)
    return refused("UNKNOWN_OPERATION")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("vectors", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    suite = json.loads(args.vectors.read_text(encoding="utf-8"))
    policy = suite["policy"]
    results = []
    failures = []
    for vector in suite["vectors"]:
        actual = evaluate(vector, policy)
        ok = actual == vector["expected"]
        results.append({"id": vector["id"], "family": vector["family"], "actual": actual, "matches_expected": ok})
        if not ok:
            failures.append({"id": vector["id"], "expected": vector["expected"], "actual": actual})
    payload = {
        "schema": "rcs-019-run-result/1.0",
        "implementation": "python-independent-reference/1.0",
        "runtime": {"python": platform.python_version(), "platform": platform.platform()},
        "vector_schema": suite["schema"],
        "result_count": len(results),
        "failure_count": len(failures),
        "results": results,
        "failures": failures,
    }
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
