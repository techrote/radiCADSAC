#!/usr/bin/env python3
"""RCS-020 research-only lathe tool-envelope derivation.

The programme authority remains the canonical journal. This module derives a
bounded axisymmetric material profile from explicit tool geometry and canonical
tool-centre paths. The generator and oracle intentionally use different
algorithms so one implementation does not define its own truth.

Coordinates are (z, r) in millimetres.
"""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
import math
from typing import Sequence

Point = tuple[float, float]
EPS = 1.0e-12


@dataclass(frozen=True)
class MaterialProfile:
    mode: str
    stock_z0_mm: float
    stock_z1_mm: float
    stock_outer_radius_mm: float
    boundary: tuple[Point, ...]

    def volume_mm3(self) -> float:
        total = 0.0
        for (z0, v0), (z1, v1) in zip(self.boundary, self.boundary[1:]):
            length = z1 - z0
            if length < -EPS:
                raise ValueError("profile z order reversed")
            if length <= EPS:
                continue
            if self.mode == "external":
                outer0, outer1 = v0, v1
                inner0 = inner1 = 0.0
            elif self.mode == "internal":
                outer0 = outer1 = self.stock_outer_radius_mm
                inner0, inner1 = v0, v1
            else:
                raise ValueError(f"unsupported profile mode {self.mode}")
            total += (
                math.pi
                * length
                * (
                    outer0 * outer0 + outer0 * outer1 + outer1 * outer1
                    - inner0 * inner0 - inner0 * inner1 - inner1 * inner1
                )
                / 3.0
            )
        return total

    def polygon_radius_z(self) -> list[tuple[float, float]]:
        """Return the closed (radius,z) polygon consumed by RCS-010 worker."""
        if self.mode == "external":
            points: list[tuple[float, float]] = [(0.0, self.stock_z0_mm)]
            points.extend((radius, z) for z, radius in self.boundary)
            points.append((0.0, self.stock_z1_mm))
            points.append((0.0, self.stock_z0_mm))
            return _dedupe(points)

        points = [(self.boundary[0][1], self.stock_z0_mm)]
        points.append((self.stock_outer_radius_mm, self.stock_z0_mm))
        points.append((self.stock_outer_radius_mm, self.stock_z1_mm))
        points.append((self.boundary[-1][1], self.stock_z1_mm))
        for z, radius in reversed(self.boundary[:-1]):
            points.append((radius, z))
        points.append((self.boundary[0][1], self.stock_z0_mm))
        return _dedupe(points)


def _dedupe(points: Sequence[tuple[float, float]]) -> list[tuple[float, float]]:
    out: list[tuple[float, float]] = []
    for point in points:
        if not out or abs(point[0] - out[-1][0]) > EPS or abs(point[1] - out[-1][1]) > EPS:
            out.append(point)
    return out


def _arc_points(center: Point, radius: float, a0: float, a1: float, chord_tol: float) -> list[Point]:
    if radius <= 0.0:
        raise ValueError("nose radius must be positive")
    if chord_tol <= 0.0:
        raise ValueError("chord tolerance must be positive")
    if chord_tol >= 2.0 * radius:
        max_step = math.pi
    else:
        max_step = 2.0 * math.acos(max(-1.0, min(1.0, 1.0 - chord_tol / radius)))
    count = max(1, math.ceil(abs(a1 - a0) / max_step))
    return [
        (
            center[0] + radius * math.cos(a0 + (a1 - a0) * i / count),
            center[1] + radius * math.sin(a0 + (a1 - a0) * i / count),
        )
        for i in range(count + 1)
    ]


def _capsule_polygon(p0: Point, p1: Point, radius: float, chord_tol: float) -> list[Point]:
    """Polygonized Minkowski sum of a line segment and circular nose."""
    dz = p1[0] - p0[0]
    dr = p1[1] - p0[1]
    length = math.hypot(dz, dr)
    if length <= EPS:
        circle = _arc_points(p0, radius, 0.0, 2.0 * math.pi, chord_tol)
        if circle[-1] != circle[0]:
            circle.append(circle[0])
        return circle

    tz, tr = dz / length, dr / length
    nz, nr = -tr, tz
    normal_angle = math.atan2(nr, nz)

    a = (p0[0] + radius * nz, p0[1] + radius * nr)
    b = (p1[0] + radius * nz, p1[1] + radius * nr)
    d = (p0[0] - radius * nz, p0[1] - radius * nr)

    points: list[Point] = [a, b]
    end_arc = _arc_points(p1, radius, normal_angle, normal_angle - math.pi, chord_tol)
    points.extend(end_arc[1:])
    points.append(d)
    start_arc = _arc_points(p0, radius, normal_angle - math.pi, normal_angle - 2.0 * math.pi, chord_tol)
    points.extend(start_arc[1:])
    if points[-1] != points[0]:
        points.append(points[0])
    return points


def _vertical_bounds(poly: Sequence[Point], z: float) -> tuple[float, float] | None:
    values: list[float] = []
    for (z0, r0), (z1, r1) in zip(poly, poly[1:]):
        if abs(z1 - z0) <= EPS:
            if abs(z - z0) <= 1.0e-10:
                values.extend((r0, r1))
            continue
        if min(z0, z1) - 1.0e-10 <= z <= max(z0, z1) + 1.0e-10:
            t = (z - z0) / (z1 - z0)
            if -1.0e-9 <= t <= 1.0 + 1.0e-9:
                values.append(r0 + t * (r1 - r0))
    if not values:
        return None
    return min(values), max(values)


def _polygon_generator_bound(polys: Sequence[Sequence[Point]], z: float, mode: str) -> float | None:
    lows: list[float] = []
    highs: list[float] = []
    for poly in polys:
        bounds = _vertical_bounds(poly, z)
        if bounds is not None:
            lows.append(bounds[0])
            highs.append(bounds[1])
    if not lows:
        return None
    return min(lows) if mode == "external" else max(highs)


def _compress_profile(points: Sequence[Point], tolerance: float = 1.0e-11) -> tuple[Point, ...]:
    out: list[Point] = []
    for point in points:
        if out and abs(point[0] - out[-1][0]) <= EPS and abs(point[1] - out[-1][1]) <= EPS:
            continue
        out.append(point)
        while len(out) >= 3:
            a, b, c = out[-3:]
            if abs(a[0] - b[0]) <= EPS or abs(b[0] - c[0]) <= EPS or abs(c[0] - a[0]) <= EPS:
                break
            predicted = a[1] + (c[1] - a[1]) * (b[0] - a[0]) / (c[0] - a[0])
            if abs(b[1] - predicted) <= tolerance:
                out.pop(-2)
            else:
                break
    return tuple(out)


def derive_round_nose_profile(
    *,
    path_zr_mm: Sequence[Point],
    nose_radius_mm: float,
    stock_z0_mm: float,
    stock_z1_mm: float,
    stock_outer_radius_mm: float,
    mode: str,
    chord_tolerance_mm: float,
    sampling_step_mm: float,
) -> MaterialProfile:
    """Derive a bounded profile using polygonized swept circular-nose capsules."""
    if mode not in {"external", "internal"}:
        raise ValueError("mode must be external or internal")
    if len(path_zr_mm) < 2:
        raise ValueError("path must contain at least two points")
    if sampling_step_mm <= 0.0:
        raise ValueError("sampling step must be positive")

    polys = [
        _capsule_polygon(tuple(a), tuple(b), nose_radius_mm, chord_tolerance_mm)
        for a, b in zip(path_zr_mm, path_zr_mm[1:])
    ]
    span = stock_z1_mm - stock_z0_mm
    if span <= 0.0:
        raise ValueError("stock z span must be positive")
    count = max(1, math.ceil(span / sampling_step_mm))
    z_nodes = {stock_z0_mm + span * i / count for i in range(count + 1)}
    support_edges: set[float] = set()

    for poly in polys:
        for z, _ in poly:
            if stock_z0_mm <= z <= stock_z1_mm:
                z_nodes.add(z)
        min_z = min(p[0] for p in poly)
        max_z = max(p[0] for p in poly)
        if stock_z0_mm <= min_z <= stock_z1_mm:
            support_edges.add(min_z)
        if stock_z0_mm <= max_z <= stock_z1_mm:
            support_edges.add(max_z)

    baseline = stock_outer_radius_mm if mode == "external" else 0.0

    def material_value(z: float) -> float:
        bound = _polygon_generator_bound(polys, z, mode)
        if bound is None:
            return baseline
        if mode == "external":
            return min(stock_outer_radius_mm, max(0.0, bound))
        return max(0.0, min(stock_outer_radius_mm, bound))

    out: list[Point] = []
    epsilon = min(1.0e-7, sampling_step_mm * 1.0e-3)
    for z in sorted(z_nodes | support_edges):
        value = material_value(z)
        if z in support_edges:
            left = _polygon_generator_bound(polys, max(stock_z0_mm, z - epsilon), mode) if z > stock_z0_mm else None
            right = _polygon_generator_bound(polys, min(stock_z1_mm, z + epsilon), mode) if z < stock_z1_mm else None
            if (left is None) != (right is None):
                if left is None:
                    out.extend(((z, baseline), (z, value)))
                    continue
                out.extend(((z, value), (z, baseline)))
                continue
        out.append((z, value))

    profile = MaterialProfile(
        mode=mode,
        stock_z0_mm=stock_z0_mm,
        stock_z1_mm=stock_z1_mm,
        stock_outer_radius_mm=stock_outer_radius_mm,
        boundary=_compress_profile(out),
    )
    for _, radius in profile.boundary:
        if radius < -EPS or radius > stock_outer_radius_mm + EPS:
            raise ValueError("derived profile lies outside stock radial domain")
    return profile


# ---------------- independent exact oracle ----------------

def _oracle_segment_vertical_bounds(p0: Point, p1: Point, z: float, radius: float) -> tuple[float, float] | None:
    """Closed-form capsule intersection with a vertical z=constant line."""
    candidates: list[float] = []

    for endpoint_z, endpoint_r in (p0, p1):
        dz = z - endpoint_z
        if abs(dz) <= radius + EPS:
            root = math.sqrt(max(0.0, radius * radius - dz * dz))
            candidates.extend((endpoint_r - root, endpoint_r + root))

    dz_segment = p1[0] - p0[0]
    dr_segment = p1[1] - p0[1]
    length = math.hypot(dz_segment, dr_segment)
    if length > EPS:
        nz = -dr_segment / length
        nr = dz_segment / length
        for sign in (-1.0, 1.0):
            az0 = p0[0] + sign * radius * nz
            ar0 = p0[1] + sign * radius * nr
            az1 = p1[0] + sign * radius * nz
            ar1 = p1[1] + sign * radius * nr
            if abs(az1 - az0) <= EPS:
                if abs(z - az0) <= 1.0e-10:
                    candidates.extend((ar0, ar1))
            else:
                t = (z - az0) / (az1 - az0)
                if -1.0e-10 <= t <= 1.0 + 1.0e-10:
                    candidates.append(ar0 + t * (ar1 - ar0))

    if not candidates:
        return None
    return min(candidates), max(candidates)


def oracle_round_nose_material_value(path_zr_mm: Sequence[Point], nose_radius_mm: float, z: float, stock_outer_radius_mm: float, mode: str) -> float:
    lows: list[float] = []
    highs: list[float] = []
    for p0, p1 in zip(path_zr_mm, path_zr_mm[1:]):
        bounds = _oracle_segment_vertical_bounds(tuple(p0), tuple(p1), z, nose_radius_mm)
        if bounds is not None:
            lows.append(bounds[0])
            highs.append(bounds[1])
    if mode == "external":
        return stock_outer_radius_mm if not lows else min(stock_outer_radius_mm, max(0.0, min(lows)))
    if mode == "internal":
        return 0.0 if not highs else max(0.0, min(stock_outer_radius_mm, max(highs)))
    raise ValueError("invalid mode")


def oracle_round_nose_volume(
    *,
    path_zr_mm: Sequence[Point],
    nose_radius_mm: float,
    stock_z0_mm: float,
    stock_z1_mm: float,
    stock_outer_radius_mm: float,
    mode: str,
    integration_step_mm: float = 0.0002,
) -> dict[str, float]:
    """Independent high-resolution material volume with a convergence estimate."""
    def integrate(step: float) -> float:
        span = stock_z1_mm - stock_z0_mm
        count = max(1, math.ceil(span / step))
        h = span / count
        values: list[float] = []
        for i in range(count + 1):
            z = stock_z0_mm + i * h
            radius = oracle_round_nose_material_value(path_zr_mm, nose_radius_mm, z, stock_outer_radius_mm, mode)
            area = math.pi * radius * radius if mode == "external" else math.pi * (stock_outer_radius_mm * stock_outer_radius_mm - radius * radius)
            values.append(area)
        return h * (sum(values) - 0.5 * (values[0] + values[-1]))

    coarse = integrate(integration_step_mm * 2.0)
    fine = integrate(integration_step_mm)
    return {
        "volume_mm3": fine,
        "coarse_volume_mm3": coarse,
        "convergence_delta_mm3": abs(fine - coarse),
        "integration_step_mm": integration_step_mm,
    }


def profile_value_at(profile: MaterialProfile, z: float) -> float:
    boundary = profile.boundary
    if z <= boundary[0][0] + EPS:
        return boundary[0][1]
    if z >= boundary[-1][0] - EPS:
        return boundary[-1][1]
    zs = [point[0] for point in boundary]
    index = bisect_right(zs, z) - 1
    index = max(0, min(index, len(boundary) - 2))
    z0, r0 = boundary[index]
    z1, r1 = boundary[index + 1]
    if abs(z1 - z0) <= EPS:
        return r1
    t = (z - z0) / (z1 - z0)
    return r0 + t * (r1 - r0)


def derive_groove_profile(
    *,
    stock_z0_mm: float,
    stock_z1_mm: float,
    stock_outer_radius_mm: float,
    center_z_mm: float,
    cutting_width_mm: float,
    corner_radius_mm: float,
    bottom_radius_mm: float,
    chord_tolerance_mm: float,
) -> MaterialProfile:
    """Groove profile from cutting width, corner radius, pose and plunge depth."""
    if not (0.0 <= bottom_radius_mm < stock_outer_radius_mm):
        raise ValueError("invalid groove bottom radius")
    if cutting_width_mm <= 0.0:
        raise ValueError("cutting width must be positive")
    if not (0.0 <= corner_radius_mm <= cutting_width_mm / 2.0):
        raise ValueError("corner radius out of range")

    half = cutting_width_mm / 2.0
    flat_half = half - corner_radius_mm
    left_edge = center_z_mm - half
    right_edge = center_z_mm + half
    left_flat = center_z_mm - flat_half
    right_flat = center_z_mm + flat_half

    points: list[Point] = [(stock_z0_mm, stock_outer_radius_mm)]
    if left_edge > stock_z0_mm:
        points.append((left_edge, stock_outer_radius_mm))
    points.append((left_edge, bottom_radius_mm + corner_radius_mm))

    if corner_radius_mm > 0.0:
        center_left = (left_flat, bottom_radius_mm + corner_radius_mm)
        left_arc = _arc_points(center_left, corner_radius_mm, math.pi, 1.5 * math.pi, chord_tolerance_mm)
        points.extend(left_arc[1:])
    else:
        points.append((left_flat, bottom_radius_mm))

    if right_flat > left_flat + EPS:
        points.append((right_flat, bottom_radius_mm))

    if corner_radius_mm > 0.0:
        center_right = (right_flat, bottom_radius_mm + corner_radius_mm)
        right_arc = _arc_points(center_right, corner_radius_mm, 1.5 * math.pi, 2.0 * math.pi, chord_tolerance_mm)
        points.extend(right_arc[1:])
    points.append((right_edge, stock_outer_radius_mm))
    if right_edge < stock_z1_mm:
        points.append((stock_z1_mm, stock_outer_radius_mm))

    return MaterialProfile(
        mode="external",
        stock_z0_mm=stock_z0_mm,
        stock_z1_mm=stock_z1_mm,
        stock_outer_radius_mm=stock_outer_radius_mm,
        boundary=_compress_profile(points),
    )


def groove_oracle_volume(
    *,
    stock_z0_mm: float,
    stock_z1_mm: float,
    stock_outer_radius_mm: float,
    center_z_mm: float,
    cutting_width_mm: float,
    corner_radius_mm: float,
    bottom_radius_mm: float,
    integration_step_mm: float = 0.00025,
) -> dict[str, float]:
    half = cutting_width_mm / 2.0
    flat_half = half - corner_radius_mm

    def radius_at(z: float) -> float:
        x = abs(z - center_z_mm)
        if x > half:
            return stock_outer_radius_mm
        if corner_radius_mm <= EPS or x <= flat_half:
            return bottom_radius_mm
        dx = x - flat_half
        return bottom_radius_mm + corner_radius_mm - math.sqrt(max(0.0, corner_radius_mm * corner_radius_mm - dx * dx))

    def integrate(step: float) -> float:
        span = stock_z1_mm - stock_z0_mm
        count = max(1, math.ceil(span / step))
        h = span / count
        areas = [math.pi * radius_at(stock_z0_mm + i * h) ** 2 for i in range(count + 1)]
        return h * (sum(areas) - 0.5 * (areas[0] + areas[-1]))

    fine = integrate(integration_step_mm)
    coarse = integrate(integration_step_mm * 2.0)
    return {
        "volume_mm3": fine,
        "coarse_volume_mm3": coarse,
        "convergence_delta_mm3": abs(fine - coarse),
        "integration_step_mm": integration_step_mm,
    }


def stock_outer_at(sections: Sequence[dict], z: float) -> float | None:
    for section in sections:
        if float(section["z0_mm"]) - EPS <= z <= float(section["z1_mm"]) + EPS:
            return float(section["outer_radius_mm"])
    return None


def holder_clearance_collision(
    *,
    path_zr_mm: Sequence[Point],
    stock_outer_sections: Sequence[dict],
    approach_angle_deg: float,
    holder_setback_mm: float,
    holder_length_mm: float,
    sample_step_mm: float = 0.05,
) -> dict:
    """Conservative holder-ray collision probe for capability/refusal research."""
    angle = math.radians(approach_angle_deg)
    dz = math.cos(angle)
    dr = math.sin(angle)
    samples = 0

    for nose_z, nose_r in path_zr_mm:
        distance = holder_setback_mm
        while distance <= holder_length_mm + EPS:
            z = nose_z + distance * dz
            r = nose_r + distance * dr
            outer = stock_outer_at(stock_outer_sections, z)
            samples += 1
            if outer is not None and r < outer - 1.0e-9:
                return {
                    "collision": True,
                    "samples": samples,
                    "first_collision": {
                        "nose_z_mm": nose_z,
                        "nose_r_mm": nose_r,
                        "holder_distance_mm": distance,
                        "probe_z_mm": z,
                        "probe_r_mm": r,
                        "stock_outer_radius_mm": outer,
                    },
                }
            distance += sample_step_mm

    return {"collision": False, "samples": samples, "first_collision": None}


def encode_worker_profile(profile: MaterialProfile) -> str:
    return ";".join(f"{radius:.17g},{z:.17g}" for radius, z in profile.polygon_radius_z())
