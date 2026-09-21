#!/usr/bin/env python3
"""Fixture-specific exact witness oracle for MC-011 F01-F04.

The oracle is intentionally narrow: exact rational point/sweep predicates and
rigid transforms only.  It is not a candidate implementation or a universal
material oracle.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Iterable, Sequence

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


def _sub(a: Sequence[Fraction], b: Sequence[Fraction]) -> tuple[Fraction, ...]:
    return tuple(x - y for x, y in zip(a, b))


def _dot(a: Sequence[Fraction], b: Sequence[Fraction]) -> Fraction:
    return sum((x * y for x, y in zip(a, b)), Fraction(0, 1))


def distance2_point_segment(
    point: Sequence[int | str | Fraction],
    a: Sequence[int | str | Fraction],
    b: Sequence[int | str | Fraction],
) -> Fraction:
    """Exact squared Euclidean distance to a finite 3-D segment."""
    p, p0, p1 = vec3(point), vec3(a), vec3(b)
    d = _sub(p1, p0)
    w = _sub(p, p0)
    den = _dot(d, d)
    if den == 0:
        return _dot(w, w)
    t = _dot(w, d) / den
    t = max(Fraction(0, 1), min(Fraction(1, 1), t))
    residual = tuple(wi - t * di for wi, di in zip(w, d))
    return _dot(residual, residual)


def _plane_axes(axis: str) -> tuple[int, int]:
    if axis == "x":
        return 1, 2
    if axis == "y":
        return 0, 2
    if axis == "z":
        return 0, 1
    raise ValueError("axis must be x, y or z")


def distance2_point_segment_in_plane(
    point: Sequence[int | str | Fraction],
    a: Sequence[int | str | Fraction],
    b: Sequence[int | str | Fraction],
    axis: str,
) -> Fraction:
    """Squared distance after projection perpendicular to the cutter axis."""
    p, p0, p1 = vec3(point), vec3(a), vec3(b)
    i, j = _plane_axes(axis)
    pp = (p[i], p[j], Fraction(0, 1))
    aa = (p0[i], p0[j], Fraction(0, 1))
    bb = (p1[i], p1[j], Fraction(0, 1))
    return distance2_point_segment(pp, aa, bb)


def flat_axis_sweep_removes(
    point: Sequence[int | str | Fraction],
    path: Iterable[Sequence[int | str | Fraction]],
    radius: int | str | Fraction,
    axis: str,
    axial_interval: Sequence[int | str | Fraction],
) -> bool:
    """Exact point membership in a fixed-axis finite cylindrical cutter sweep.

    The path translates the cylinder perpendicular to its fixed axis.  This is
    sufficient for the deliberately bounded F01/F02/F04 witness predicates.
    """
    pts = [vec3(p) for p in path]
    if len(pts) < 2:
        raise ValueError("sweep path needs at least two points")
    if len(axial_interval) != 2:
        raise ValueError("axial interval needs two endpoints")
    lo, hi = q(axial_interval[0]), q(axial_interval[1])
    if lo > hi:
        lo, hi = hi, lo
    p = vec3(point)
    ai = {"x": 0, "y": 1, "z": 2}.get(axis)
    if ai is None:
        raise ValueError("axis must be x, y or z")
    if not (lo <= p[ai] <= hi):
        return False
    r2 = q(radius) ** 2
    return any(
        distance2_point_segment_in_plane(p, a, b, axis) <= r2
        for a, b in zip(pts, pts[1:])
    )


def ball_polyline_sweep_removes(
    point: Sequence[int | str | Fraction],
    path: Iterable[Sequence[int | str | Fraction]],
    radius: int | str | Fraction,
) -> bool:
    """Exact point membership in a spherical cutter swept along a 3-D polyline."""
    pts = [vec3(p) for p in path]
    if len(pts) < 2:
        raise ValueError("sweep path needs at least two points")
    r2 = q(radius) ** 2
    return any(distance2_point_segment(point, a, b) <= r2 for a, b in zip(pts, pts[1:]))


def matrix_vec(
    matrix: Sequence[Sequence[int | str | Fraction]],
    vector: Sequence[int | str | Fraction],
) -> tuple[Fraction, Fraction, Fraction]:
    if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
        raise ValueError("matrix must be 3x3")
    m = tuple(tuple(q(v) for v in row) for row in matrix)
    x = vec3(vector)
    return tuple(_dot(row, x) for row in m)  # type: ignore[return-value]


def rigid_transform(
    matrix: Sequence[Sequence[int | str | Fraction]],
    translation: Sequence[int | str | Fraction],
    point: Sequence[int | str | Fraction],
) -> tuple[Fraction, Fraction, Fraction]:
    y = matrix_vec(matrix, point)
    t = vec3(translation)
    return y[0] + t[0], y[1] + t[1], y[2] + t[2]


def determinant3(matrix: Sequence[Sequence[int | str | Fraction]]) -> Fraction:
    m = tuple(tuple(q(v) for v in row) for row in matrix)
    if len(m) != 3 or any(len(row) != 3 for row in m):
        raise ValueError("matrix must be 3x3")
    return (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )


def is_rotation_matrix(matrix: Sequence[Sequence[int | str | Fraction]]) -> bool:
    """Exact SO(3) check for rational matrices."""
    cols = []
    m = tuple(tuple(q(v) for v in row) for row in matrix)
    if len(m) != 3 or any(len(row) != 3 for row in m):
        return False
    for j in range(3):
        cols.append((m[0][j], m[1][j], m[2][j]))
    return (
        all(_dot(c, c) == 1 for c in cols)
        and all(_dot(cols[i], cols[j]) == 0 for i in range(3) for j in range(i + 1, 3))
        and determinant3(m) == 1
    )


def canonical_undirected_segments(
    path: Iterable[Sequence[int | str | Fraction]],
) -> frozenset[tuple[tuple[Fraction, Fraction, Fraction], tuple[Fraction, Fraction, Fraction]]]:
    pts = [vec3(p) for p in path]
    if len(pts) < 2:
        raise ValueError("path needs at least two points")
    edges = []
    for a, b in zip(pts, pts[1:]):
        edges.append((a, b) if a <= b else (b, a))
    return frozenset(edges)
