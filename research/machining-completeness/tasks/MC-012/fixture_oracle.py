#!/usr/bin/env python3
"""Exact, candidate-independent witness oracle for MC-012 F05-F08.

This oracle is intentionally narrow.  It proves only the preregistered rational
boundary/membership witnesses used by MC-012; it is not a native geometry
candidate, a universal machining oracle, or a STEP checker.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Sequence

Q = Fraction


def q(value: int | str | Fraction) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError("authority-path rationals must not be bool/float")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, str):
        return Fraction(value)
    raise TypeError(f"unsupported exact value: {type(value).__name__}")


def vec3(raw: Sequence[int | str | Fraction]) -> tuple[Fraction, Fraction, Fraction]:
    if len(raw) != 3:
        raise ValueError("point/vector requires three coordinates")
    return q(raw[0]), q(raw[1]), q(raw[2])


def point_in_box(
    point: Sequence[int | str | Fraction],
    box: Sequence[Sequence[int | str | Fraction]],
) -> bool:
    if len(box) != 3 or any(len(pair) != 2 for pair in box):
        raise ValueError("box must contain three [lo,hi] pairs")
    p = vec3(point)
    return all(q(pair[0]) <= coord <= q(pair[1]) for coord, pair in zip(p, box))


def finite_cylinder_contains(
    point: Sequence[int | str | Fraction],
    axis: str,
    center: Sequence[int | str | Fraction],
    axial_interval: Sequence[int | str | Fraction],
    radius: int | str | Fraction,
) -> bool:
    """Exact point membership in a finite axis-aligned cylinder."""
    p = vec3(point)
    if len(center) != 2 or len(axial_interval) != 2:
        raise ValueError("cylinder center/interval arity mismatch")
    lo, hi = q(axial_interval[0]), q(axial_interval[1])
    if lo > hi:
        lo, hi = hi, lo
    r2 = q(radius) ** 2
    if q(radius) < 0:
        raise ValueError("negative radius")
    if axis == "x":
        axial = p[0]
        u, v = p[1], p[2]
    elif axis == "y":
        axial = p[1]
        u, v = p[0], p[2]
    elif axis == "z":
        axial = p[2]
        u, v = p[0], p[1]
    else:
        raise ValueError("axis must be x, y or z")
    cu, cv = q(center[0]), q(center[1])
    return lo <= axial <= hi and (u - cu) ** 2 + (v - cv) ** 2 <= r2


def distance2_point_segment_2d(
    point: Sequence[int | str | Fraction],
    a: Sequence[int | str | Fraction],
    b: Sequence[int | str | Fraction],
) -> Fraction:
    if len(point) != 2 or len(a) != 2 or len(b) != 2:
        raise ValueError("2-D segment predicate requires pairs")
    p = (q(point[0]), q(point[1]))
    p0 = (q(a[0]), q(a[1]))
    p1 = (q(b[0]), q(b[1]))
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    wx, wy = p[0] - p0[0], p[1] - p0[1]
    den = dx * dx + dy * dy
    if den == 0:
        return wx * wx + wy * wy
    t = (wx * dx + wy * dy) / den
    t = max(Fraction(0), min(Fraction(1), t))
    rx, ry = wx - t * dx, wy - t * dy
    return rx * rx + ry * ry


def lathe_nose_sweep_removes(
    radius: int | str | Fraction,
    z: int | str | Fraction,
    center_radius: int | str | Fraction,
    z_interval: Sequence[int | str | Fraction],
    nose_radius: int | str | Fraction,
) -> bool:
    """Exact meridional witness for a constant-radius turning pass."""
    if len(z_interval) != 2:
        raise ValueError("lathe z interval needs two endpoints")
    nr = q(nose_radius)
    if nr < 0:
        raise ValueError("negative nose radius")
    p = (q(z), q(radius))
    a = (q(z_interval[0]), q(center_radius))
    b = (q(z_interval[1]), q(center_radius))
    return distance2_point_segment_2d(p, a, b) <= nr * nr


def parting_component_count(remaining_core_radius: int | str | Fraction) -> int:
    """Topological boundary control for a radial parting cut."""
    core = q(remaining_core_radius)
    if core < 0:
        raise ValueError("remaining core radius cannot be negative")
    return 2 if core == 0 else 1


def lathe_od_removes(
    point: Sequence[int | str | Fraction],
    final_radius: int | str | Fraction,
    z_interval: Sequence[int | str | Fraction],
) -> bool:
    """Exact axisymmetric OD-shell witness around common +Z."""
    p = vec3(point)
    lo, hi = q(z_interval[0]), q(z_interval[1])
    if lo > hi:
        lo, hi = hi, lo
    if not (lo <= p[2] <= hi):
        return False
    rr = q(final_radius)
    if rr < 0:
        raise ValueError("negative final radius")
    return p[0] * p[0] + p[1] * p[1] > rr * rr


def t_slot_sweep_removes(
    point: Sequence[int | str | Fraction],
    path_xy: Sequence[Sequence[int | str | Fraction]],
    head_radius: int | str | Fraction,
    head_z: Sequence[int | str | Fraction],
    neck_radius: int | str | Fraction,
    neck_z: Sequence[int | str | Fraction],
) -> bool:
    """Exact witness for a T-slot/form cutter swept in XY at fixed orientation."""
    if len(path_xy) < 2:
        raise ValueError("T-slot path needs at least two points")
    p = vec3(point)
    head_r, neck_r = q(head_radius), q(neck_radius)
    if head_r <= 0 or neck_r <= 0 or head_r <= neck_r:
        raise ValueError("T-slot head must be strictly wider than positive neck")
    def in_interval(zv, interval):
        lo, hi = q(interval[0]), q(interval[1])
        if lo > hi:
            lo, hi = hi, lo
        return lo <= zv <= hi
    d2 = min(
        distance2_point_segment_2d((p[0], p[1]), a, b)
        for a, b in zip(path_xy, path_xy[1:])
    )
    return (
        (in_interval(p[2], head_z) and d2 <= head_r * head_r)
        or (in_interval(p[2], neck_z) and d2 <= neck_r * neck_r)
    )


def t_slot_accessible(
    access_radius: int | str | Fraction,
    head_radius: int | str | Fraction,
    neck_radius: int | str | Fraction,
) -> bool:
    """The head must enter through the prepared access and remain wider than its neck."""
    ar, hr, nr = q(access_radius), q(head_radius), q(neck_radius)
    return nr > 0 and hr > nr and ar >= hr


def _dot(a: Sequence[Fraction], b: Sequence[Fraction]) -> Fraction:
    return sum((x * y for x, y in zip(a, b)), Fraction(0))


def determinant3(matrix: Sequence[Sequence[int | str | Fraction]]) -> Fraction:
    if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
        raise ValueError("matrix must be 3x3")
    m = tuple(tuple(q(v) for v in row) for row in matrix)
    return (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )


def is_rotation_matrix(matrix: Sequence[Sequence[int | str | Fraction]]) -> bool:
    if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
        return False
    m = tuple(tuple(q(v) for v in row) for row in matrix)
    cols = [(m[0][j], m[1][j], m[2][j]) for j in range(3)]
    return (
        all(_dot(c, c) == 1 for c in cols)
        and all(_dot(cols[i], cols[j]) == 0 for i in range(3) for j in range(i + 1, 3))
        and determinant3(m) == 1
    )


def matrix_vec(
    matrix: Sequence[Sequence[int | str | Fraction]],
    vector: Sequence[int | str | Fraction],
) -> tuple[Fraction, Fraction, Fraction]:
    if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
        raise ValueError("matrix must be 3x3")
    m = tuple(tuple(q(v) for v in row) for row in matrix)
    x = vec3(vector)
    return tuple(_dot(row, x) for row in m)  # type: ignore[return-value]
