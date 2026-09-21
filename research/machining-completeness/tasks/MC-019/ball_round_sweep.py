#!/usr/bin/env python3
"""Exact/bounded fixed-axis ball/round milling sweep construction for MC-019.

The exact path covers stationary/line/polyline translations of a finite ball-end
cutting solid with rational source coordinates. Nonlinear source motion is
consumed through MC-058-certified line leaves with an explicit Euclidean
translation enclosure; those leaves produce INSIDE/OUTSIDE/UNCERTIFIED rather
than guessed equality.

Authority values reject binary floating point.
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
class BallRoundEndMill:
    radius: Fraction
    length: Fraction

    @classmethod
    def make(cls, radius, length) -> "BallRoundEndMill":
        r, l = q(radius), q(length)
        if r <= 0 or l <= 0:
            raise ValueError("ball/round cutter radius and finite length must be positive")
        if l < r:
            raise ValueError("finite cutter length must reach the ball-centre/seam plane")
        return cls(r, l)

    @property
    def inner_radius(self) -> Fraction:
        """Radius of a simple exact inscribed cylinder used for bounded leaves."""
        return self.radius / 2

    @property
    def inner_z_min(self) -> Fraction:
        return self.radius / 2


EXACT_SOURCE_CLASSES = {"stationary", "line", "polyline"}
BOUNDED_SOURCE_CLASSES = {"circular_arc", "helical_arc", "spline", "piecewise_motion", "timed_phase_motion"}
ALLOWED_SOURCE_CLASSES = EXACT_SOURCE_CLASSES | BOUNDED_SOURCE_CLASSES


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
        if len(source_interval) != 2:
            raise ValueError("source interval must have two endpoints")
        iv = q(source_interval[0]), q(source_interval[1])
        if iv[0] > iv[1]:
            raise ValueError("source interval must be ordered")
        if source_class not in ALLOWED_SOURCE_CLASSES:
            raise ValueError("source class is not admitted by MC-019/MC-058")
        return cls(v3(p0), v3(p1), e, source_class, iv, bool(engagement_bound))


@dataclass(frozen=True)
class Cylinder:
    radius: Fraction
    z_min: Fraction
    z_max: Fraction

    def __post_init__(self) -> None:
        if self.radius < 0 or self.z_min > self.z_max:
            raise ValueError("invalid cylinder")


def _linear_band_interval(a: Fraction, b: Fraction, lo: Fraction, hi: Fraction):
    if lo > hi:
        raise ValueError("invalid band")
    if b == 0:
        return (Fraction(0), Fraction(1)) if lo <= a <= hi else None
    t0, t1 = (lo - a) / b, (hi - a) / b
    l, h = max(min(t0, t1), Fraction(0)), min(max(t0, t1), Fraction(1))
    return None if l > h else (l, h)


def _quadratic_min(c0: Fraction, c1: Fraction, c2: Fraction, iv) -> Fraction:
    lo, hi = iv
    vals = [c0 + c1 * lo + c2 * lo * lo, c0 + c1 * hi + c2 * hi * hi]
    if c2 > 0:
        t = -c1 / (2 * c2)
        if lo <= t <= hi:
            vals.append(c0 + c1 * t + c2 * t * t)
    return min(vals)


def _distance2_poly(point, p0, p1, offset=(Fraction(0), Fraction(0), Fraction(0))):
    qx, qy, qz = v3(point)
    x0, y0, z0 = v3(p0)
    x1, y1, z1 = v3(p1)
    ox, oy, oz = offset
    ux, uy, uz = qx - x0 - ox, qy - y0 - oy, qz - z0 - oz
    dx, dy, dz = x1 - x0, y1 - y0, z1 - z0
    c0 = ux * ux + uy * uy + uz * uz
    c1 = -2 * (ux * dx + uy * dy + uz * dz)
    c2 = dx * dx + dy * dy + dz * dz
    return c0, c1, c2


def _radial2_poly(point, p0, p1):
    qx, qy, _ = v3(point)
    x0, y0, _ = v3(p0)
    x1, y1, _ = v3(p1)
    ux, uy = qx - x0, qy - y0
    dx, dy = x1 - x0, y1 - y0
    return ux * ux + uy * uy, -2 * (ux * dx + uy * dy), dx * dx + dy * dy


def cylinder_segment_contains(point, cyl: Cylinder, p0, p1) -> bool:
    point, p0, p1 = v3(point), v3(p0), v3(p1)
    z0 = point[2] - p0[2]
    dz = -(p1[2] - p0[2])
    iv = _linear_band_interval(z0, dz, cyl.z_min, cyl.z_max)
    if iv is None:
        return False
    return _quadratic_min(*_radial2_poly(point, p0, p1), iv) <= cyl.radius * cyl.radius


def ball_round_segment_contains(point, tool: BallRoundEndMill, p0, p1) -> bool:
    """Exact membership in one translated finite ball/round cutter line sweep."""
    point, p0, p1 = v3(point), v3(p0), v3(p1)
    r, L = tool.radius, tool.length
    z0 = point[2] - p0[2]
    dz = -(p1[2] - p0[2])

    # Cylindrical region from the ball-centre/seam plane to finite cutter top.
    upper = _linear_band_interval(z0, dz, r, L)
    if upper is not None and _quadratic_min(*_radial2_poly(point, p0, p1), upper) <= r * r:
        return True

    # Lower hemispherical nose. The moving sphere centre is p(t)+(0,0,r),
    # but only source parameters whose local z lies in [0,r] are admitted.
    lower = _linear_band_interval(z0, dz, Fraction(0), r)
    if lower is None:
        return False
    sphere = _distance2_poly(point, p0, p1, (Fraction(0), Fraction(0), r))
    return _quadratic_min(*sphere, lower) <= r * r


def exact_sweep_contains(point, tool: BallRoundEndMill, leaves: Iterable[Leaf]) -> bool:
    for leaf in leaves:
        if leaf.translation_error != 0:
            raise ValueError("exact sweep requires zero-error leaves")
        if leaf.source_class not in EXACT_SOURCE_CLASSES:
            raise ValueError("exact sweep only accepts stationary/line/polyline source leaves")
        if not leaf.engagement_bound:
            raise ValueError("leaf must be bound to an engaged source interval")
        if ball_round_segment_contains(point, tool, leaf.p0, leaf.p1):
            return True
    return False


def certified_classify(point, tool: BallRoundEndMill, leaves: Iterable[Leaf]) -> str:
    """Sound fixed-axis classification from source-bound MC-058 translation leaves."""
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
            if ball_round_segment_contains(point, tool, leaf.p0, leaf.p1):
                return "INSIDE"
            continue

        e = leaf.translation_error
        # Complete cutter lies inside radius-R, z=[0,L] cylinder.
        outer = Cylinder(tool.radius + e, -e, tool.length + e)
        if cylinder_segment_contains(point, outer, leaf.p0, leaf.p1):
            outer_hit = True

        # Exact cutter contains radius-R/2 cylinder on z=[R/2,L].
        # Erode it by e so every point remains inside under any translation
        # displacement bounded by e.
        inner_r = tool.inner_radius - e
        inner_lo = tool.inner_z_min + e
        inner_hi = tool.length - e
        if inner_r >= 0 and inner_lo <= inner_hi:
            inner = Cylinder(inner_r, inner_lo, inner_hi)
            if cylinder_segment_contains(point, inner, leaf.p0, leaf.p1):
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
