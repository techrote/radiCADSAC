#!/usr/bin/env python3
"""Representation-neutral material field for RCS-021."""
from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = ROOT / "research/rcs-021/experiment-plan-v1.json"
STOCK = (40.0, 30.0, 10.0)
EPS = 1.0e-12

@dataclass(frozen=True)
class P:
    x: float
    y: float
    z: float

def load_plan() -> dict[str, Any]:
    return json.loads(PLAN_PATH.read_text(encoding="utf-8"))

def expand_case(raw: dict[str, Any]) -> dict[str, Any]:
    case = json.loads(json.dumps(raw))
    spec = case.pop("generated_path", None)
    if spec:
        n = int(spec["segments"])
        pts = []
        for i in range(n + 1):
            u = i / n
            phase = 2.0 * math.pi * float(spec["cycles"]) * u
            pts.append([
                float(spec["x0"]) + (float(spec["x1"]) - float(spec["x0"])) * u,
                float(spec["y_center"]) + float(spec["y_amplitude"]) * math.sin(phase),
                float(spec["z_center"]) + float(spec["z_amplitude"]) * math.sin(phase * 0.5),
            ])
        case["paths"] = [pts]
        case["generated_segment_count"] = n
    return case

def profile_cases(plan: dict[str, Any], profile: str) -> list[dict[str, Any]]:
    by_id = {x["id"]: x for x in plan["cases"]}
    return [expand_case(by_id[x]) for x in plan["profiles"][profile]]

def points(case: dict[str, Any]) -> list[list[P]]:
    return [[P(*map(float, q)) for q in path] for path in case["paths"]]

def segments(case: dict[str, Any]) -> Iterator[tuple[P, P]]:
    for path in points(case):
        if len(path) == 1:
            yield path[0], path[0]
        else:
            yield from zip(path, path[1:])

def segment_count(case: dict[str, Any]) -> int:
    return sum(max(1, len(path) - 1) for path in points(case))

def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))

def xy_distance(x: float, y: float, a: P, b: P) -> tuple[float, float]:
    dx, dy = b.x - a.x, b.y - a.y
    den = dx * dx + dy * dy
    if den <= EPS:
        return math.hypot(x - a.x, y - a.y), 0.0
    t = clamp(((x - a.x) * dx + (y - a.y) * dy) / den, 0.0, 1.0)
    return math.hypot(x - a.x - dx * t, y - a.y - dy * t), t

def xy_interval(x: float, y: float, a: P, b: P, radius: float) -> tuple[float, float] | None:
    dx, dy = b.x - a.x, b.y - a.y
    fx, fy = a.x - x, a.y - y
    aa = dx * dx + dy * dy
    cc = fx * fx + fy * fy - radius * radius
    if aa <= EPS:
        return (0.0, 1.0) if cc <= EPS else None
    bb = 2.0 * (fx * dx + fy * dy)
    disc = bb * bb - 4.0 * aa * cc
    if disc < -EPS:
        return None
    root = math.sqrt(max(0.0, disc))
    lo = max(0.0, (-bb - root) / (2.0 * aa))
    hi = min(1.0, (-bb + root) / (2.0 * aa))
    return None if hi + EPS < lo else (lo, hi)

def z_interval(limit: float, a: P, b: P) -> tuple[float, float] | None:
    dz = b.z - a.z
    if abs(dz) <= EPS:
        return (0.0, 1.0) if a.z <= limit + EPS else None
    t = (limit - a.z) / dz
    lo, hi = ((0.0, min(1.0, t)) if dz > 0.0 else (max(0.0, t), 1.0))
    return None if hi + EPS < lo else (max(0.0, lo), min(1.0, hi))

def flat_segment_field(p: P, a: P, b: P, radius: float) -> float:
    dx, dy, dz = b.x - a.x, b.y - a.y, b.z - a.z
    if dx * dx + dy * dy <= EPS:
        return min(radius - math.hypot(p.x - a.x, p.y - a.y), p.z - min(a.z, b.z))
    if abs(dz) <= EPS:
        d, _ = xy_distance(p.x, p.y, a, b)
        return min(radius - d, p.z - a.z)
    def at(t: float) -> float:
        qx, qy, qz = a.x + dx*t, a.y + dy*t, a.z + dz*t
        return min(radius - math.hypot(p.x-qx, p.y-qy), p.z-qz)
    low = max(at(0.0), at(1.0))
    high = min(radius, p.z - min(a.z, b.z))
    def feasible(level: float) -> bool:
        rr = radius - level
        if rr < 0.0:
            return False
        xi = xy_interval(p.x, p.y, a, b, rr)
        zi = z_interval(p.z - level, a, b)
        return xi is not None and zi is not None and max(xi[0], zi[0]) <= min(xi[1], zi[1]) + EPS
    for _ in range(64):
        mid = (low + high) * 0.5
        if feasible(mid): low = mid
        else: high = mid
    return (low + high) * 0.5

def rounded_segment_field(p: P, a: P, b: P, radius: float) -> float:
    if abs(a.z - b.z) > 1.0e-12:
        raise ValueError("rounded RCS-021 path must be constant-Z")
    dxy, _ = xy_distance(p.x, p.y, a, b)
    distance = dxy if p.z >= a.z else math.hypot(dxy, p.z - a.z)
    return radius - distance

def removal_field(case: dict[str, Any], p: P) -> float:
    tool = case["tool"]
    radius = float(tool["radius_mm"])
    values = []
    for a, b in segments(case):
        if tool["kind"] == "flat": values.append(flat_segment_field(p, a, b, radius))
        elif tool["kind"] == "ball": values.append(rounded_segment_field(p, a, b, radius))
        else: raise ValueError(f"unsupported tool kind {tool['kind']!r}")
    return max(values)

def stock_field(p: P) -> float:
    sx, sy, sz = STOCK
    return min(p.x, sx-p.x, p.y, sy-p.y, p.z, sz-p.z)

def final_field(case: dict[str, Any], p: P) -> float:
    return min(stock_field(p), -removal_field(case, p))

def column_height(case: dict[str, Any], x: float, y: float) -> float:
    height = STOCK[2]
    radius = float(case["tool"]["radius_mm"])
    for a, b in segments(case):
        interval = xy_interval(x, y, a, b, radius)
        if interval is None: continue
        lo, hi = interval
        if case["tool"]["kind"] == "flat":
            za = a.z + (b.z-a.z)*lo
            zb = a.z + (b.z-a.z)*hi
            floor = min(za, zb)
        else:
            d, _ = xy_distance(x, y, a, b)
            floor = a.z - math.sqrt(max(0.0, radius*radius-d*d))
        height = min(height, clamp(floor, 0.0, STOCK[2]))
    return clamp(height, 0.0, STOCK[2])
def known_volume(case: dict[str, Any]) -> tuple[float, int] | None:
    tag = case.get("known_oracle")
    if not tag: return None
    volume = STOCK[0]*STOCK[1]*STOCK[2]
    r = float(case["tool"]["radius_mm"])
    ps = points(case)
    if tag == "stationary_flat_cylinder":
        return volume - math.pi*r*r*clamp(STOCK[2]-ps[0][0].z, 0.0, STOCK[2]), 1
    if tag == "flat_stadium_slot":
        a,b = ps[0][0], ps[0][-1]
        length = math.hypot(b.x-a.x, b.y-a.y)
        depth = clamp(STOCK[2]-min(a.z,b.z), 0.0, STOCK[2])
        return volume - (2*r*length + math.pi*r*r)*depth, 1
    if tag == "no_positive_volume_contact": return volume, 1
    if tag == "pure_plunge":
        zmin = min(q.z for q in ps[0])
        return volume - math.pi*r*r*clamp(STOCK[2]-zmin,0.0,STOCK[2]), 1
    if tag == "through_strip_two_bodies":
        return (STOCK[0]-2*r)*STOCK[1]*STOCK[2], 2
    raise ValueError(f"unknown known oracle {tag!r}")
