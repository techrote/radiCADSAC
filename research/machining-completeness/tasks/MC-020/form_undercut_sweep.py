#!/usr/bin/env python3
"""Exact/bounded form and accessible-undercut sweep construction for MC-020.

This deterministic research model covers finite exact-rational box-union cutting
regions. It deliberately does not claim that every admitted arbitrary form or
undercut cutter has this codec; PB-007-03 remains open for that source-language
gap. Fixed-axis stationary/line/polyline milling is exact. MC-058 nonlinear
source leaves are consumed through conservative translation-error sandwiches.

Access witnesses are checked independently of sweep membership by testing the
complete cutting plus non-cutting holder body against finite rational obstacle
boxes along an explicit unengaged approach path.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Sequence

Q = Fraction


def q(value: int | str | Fraction) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError("authority rationals must not be bool/float")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, str):
        return Fraction(value)
    raise TypeError(f"unsupported rational type: {type(value).__name__}")


def v3(values: Sequence[int | str | Fraction]) -> tuple[Fraction, Fraction, Fraction]:
    if len(values) != 3:
        raise ValueError("expected a 3-vector")
    return q(values[0]), q(values[1]), q(values[2])


@dataclass(frozen=True)
class Box:
    x0: Fraction
    x1: Fraction
    y0: Fraction
    y1: Fraction
    z0: Fraction
    z1: Fraction

    @classmethod
    def make(cls, x0, x1, y0, y1, z0, z1) -> "Box":
        box = cls(q(x0), q(x1), q(y0), q(y1), q(z0), q(z1))
        if not (box.x0 < box.x1 and box.y0 < box.y1 and box.z0 < box.z1):
            raise ValueError("tool boxes must have strictly positive volume")
        return box

    def inflate(self, distance: int | str | Fraction) -> "Box":
        e = q(distance)
        if e < 0:
            raise ValueError("inflation distance must be non-negative")
        return Box(self.x0 - e, self.x1 + e, self.y0 - e, self.y1 + e, self.z0 - e, self.z1 + e)

    def erode(self, distance: int | str | Fraction) -> "Box | None":
        e = q(distance)
        if e < 0:
            raise ValueError("erosion distance must be non-negative")
        x0, x1 = self.x0 + e, self.x1 - e
        y0, y1 = self.y0 + e, self.y1 - e
        z0, z1 = self.z0 + e, self.z1 - e
        if not (x0 < x1 and y0 < y1 and z0 < z1):
            return None
        return Box(x0, x1, y0, y1, z0, z1)

    def contains_local(self, point: Sequence[int | str | Fraction]) -> bool:
        x, y, z = v3(point)
        return self.x0 <= x <= self.x1 and self.y0 <= y <= self.y1 and self.z0 <= z <= self.z1


TOOL_KINDS = {"mill_form", "mill_accessible_undercut", "lathe_form_tool"}
EXACT_SOURCE_CLASSES = {"stationary", "line", "polyline"}
BOUNDED_SOURCE_CLASSES = {"circular_arc", "helical_arc", "spline", "piecewise_motion", "timed_phase_motion"}
ALLOWED_SOURCE_CLASSES = EXACT_SOURCE_CLASSES | BOUNDED_SOURCE_CLASSES


@dataclass(frozen=True)
class Tool:
    kind: str
    cutting: tuple[Box, ...]
    holder: tuple[Box, ...] = ()
    codec: str = "exact_rational_box_union_v1"

    @classmethod
    def make(cls, kind: str, cutting: Iterable[Box], holder: Iterable[Box] = ()) -> "Tool":
        if kind not in TOOL_KINDS:
            raise ValueError("unsupported MC-020 cutter family")
        cut = tuple(cutting)
        hold = tuple(holder)
        if not cut:
            raise ValueError("effective cutting region must be non-empty")
        if not all(isinstance(b, Box) for b in cut + hold):
            raise TypeError("cutting and holder regions must be exact Box objects")
        return cls(kind, cut, hold)

    @property
    def complete_body(self) -> tuple[Box, ...]:
        return self.cutting + self.holder


@dataclass(frozen=True)
class Leaf:
    p0: tuple[Fraction, Fraction, Fraction]
    p1: tuple[Fraction, Fraction, Fraction]
    translation_error: Fraction = Fraction(0)
    source_class: str = "line"
    source_interval: tuple[Fraction, Fraction] = (Fraction(0), Fraction(1))
    engagement_bound: bool = True

    @classmethod
    def make(
        cls,
        p0: Sequence[int | str | Fraction],
        p1: Sequence[int | str | Fraction],
        *,
        translation_error: int | str | Fraction = 0,
        source_class: str = "line",
        source_interval: Sequence[int | str | Fraction] = (0, 1),
        engagement_bound: bool = True,
    ) -> "Leaf":
        e = q(translation_error)
        if e < 0:
            raise ValueError("translation enclosure must be non-negative")
        if source_class not in ALLOWED_SOURCE_CLASSES:
            raise ValueError("source class is not admitted by MC-020/MC-058")
        if len(source_interval) != 2:
            raise ValueError("source interval must have two endpoints")
        iv = q(source_interval[0]), q(source_interval[1])
        if iv[0] > iv[1]:
            raise ValueError("source interval must be ordered")
        return cls(v3(p0), v3(p1), e, source_class, iv, bool(engagement_bound))


def _linear_band_interval(a: Fraction, b: Fraction, lo: Fraction, hi: Fraction):
    """t in [0,1] such that lo <= a+b*t <= hi."""
    if lo > hi:
        raise ValueError("invalid band")
    if b == 0:
        return (Fraction(0), Fraction(1)) if lo <= a <= hi else None
    t0, t1 = (lo - a) / b, (hi - a) / b
    left = max(min(t0, t1), Fraction(0))
    right = min(max(t0, t1), Fraction(1))
    return None if left > right else (left, right)


def _intersect_intervals(a, b):
    if a is None or b is None:
        return None
    left, right = max(a[0], b[0]), min(a[1], b[1])
    return None if left > right else (left, right)


def box_segment_contains(point, box: Box, p0, p1) -> bool:
    """Exact membership in one translated box sweep along one shared line parameter."""
    x = v3(point)
    a = v3(p0)
    b = v3(p1)
    lows = (box.x0, box.y0, box.z0)
    highs = (box.x1, box.y1, box.z1)
    iv = (Fraction(0), Fraction(1))
    for i in range(3):
        # box.lo <= x_i - (a_i + t*(b_i-a_i)) <= box.hi
        band = _linear_band_interval(x[i] - a[i], -(b[i] - a[i]), lows[i], highs[i])
        iv = _intersect_intervals(iv, band)
        if iv is None:
            return False
    return True


def tool_segment_contains(point, tool: Tool, p0, p1) -> bool:
    return any(box_segment_contains(point, box, p0, p1) for box in tool.cutting)


def exact_sweep_contains(point, tool: Tool, leaves: Iterable[Leaf]) -> bool:
    for leaf in leaves:
        if leaf.translation_error != 0:
            raise ValueError("exact sweep requires zero-error leaves")
        if leaf.source_class not in EXACT_SOURCE_CLASSES:
            raise ValueError("exact sweep only accepts stationary/line/polyline source leaves")
        if not leaf.engagement_bound:
            raise ValueError("leaf must be bound to an engaged source interval")
        if tool_segment_contains(point, tool, leaf.p0, leaf.p1):
            return True
    return False


def certified_classify(point, tool: Tool, leaves: Iterable[Leaf]) -> str:
    """Conservative fixed-axis classification from source-bound MC-058 leaves."""
    leaves = tuple(leaves)
    if not leaves:
        return "OUTSIDE"
    outer_hit = False
    for leaf in leaves:
        if not leaf.engagement_bound:
            raise ValueError("unbound engagement leaf")
        if leaf.source_class not in ALLOWED_SOURCE_CLASSES:
            raise ValueError("unrecognized source class")
        if leaf.translation_error == 0 and leaf.source_class in EXACT_SOURCE_CLASSES:
            if tool_segment_contains(point, tool, leaf.p0, leaf.p1):
                return "INSIDE"
            continue

        e = leaf.translation_error
        for box in tool.cutting:
            # Euclidean translation error <= e implies each coordinate error <= e.
            if box_segment_contains(point, box.inflate(e), leaf.p0, leaf.p1):
                outer_hit = True
            inner = box.erode(e)
            if inner is not None and box_segment_contains(point, inner, leaf.p0, leaf.p1):
                return "INSIDE"
    if not outer_hit:
        return "OUTSIDE"
    return "UNCERTIFIED"


def swept_path(leaves: Sequence[Leaf]) -> tuple[Leaf, ...]:
    """Validate finite ordered source coverage without deleting retraces."""
    if not leaves:
        raise ValueError("at least one engaged leaf is required")
    out = tuple(leaves)
    for i, leaf in enumerate(out):
        if not leaf.engagement_bound:
            raise ValueError("engagement binding is mandatory")
        if i and out[i - 1].p1 != leaf.p0:
            raise ValueError("engaged path must be continuous; teleportation is invalid")
    return out


def _translated_box_intersects_obstacle(moving: Box, obstacle: Box, p0, p1) -> bool:
    """Closed-set collision for a translated box and a stationary obstacle box."""
    a = v3(p0)
    b = v3(p1)
    moving_lows = (moving.x0, moving.y0, moving.z0)
    moving_highs = (moving.x1, moving.y1, moving.z1)
    obstacle_lows = (obstacle.x0, obstacle.y0, obstacle.z0)
    obstacle_highs = (obstacle.x1, obstacle.y1, obstacle.z1)
    iv = (Fraction(0), Fraction(1))
    for i in range(3):
        # [mlo+p, mhi+p] intersects [olo,ohi] iff
        # p is in [olo-mhi, ohi-mlo].
        band = _linear_band_interval(
            a[i], b[i] - a[i], obstacle_lows[i] - moving_highs[i], obstacle_highs[i] - moving_lows[i]
        )
        iv = _intersect_intervals(iv, band)
        if iv is None:
            return False
    return True


def access_is_clear(
    tool: Tool,
    approach_points: Sequence[Sequence[int | str | Fraction]],
    obstacles: Iterable[Box],
) -> bool:
    """Check an explicit unengaged access path for complete tool/holder clearance.

    Obstacles denote retained material/fixture that the complete body must not
    contact. Target material intentionally engaged by the later cutting interval
    is not encoded as an obstacle here.
    """
    if len(approach_points) < 2:
        raise ValueError("access witness requires an explicit approach path")
    points = tuple(v3(p) for p in approach_points)
    obs = tuple(obstacles)
    for i in range(len(points) - 1):
        for body_box in tool.complete_body:
            for obstacle in obs:
                if _translated_box_intersects_obstacle(body_box, obstacle, points[i], points[i + 1]):
                    return False
    return True
