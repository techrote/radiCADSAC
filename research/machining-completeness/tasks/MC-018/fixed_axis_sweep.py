#!/usr/bin/env python3
"""Exact/bounded fixed-axis milling sweep construction for MC-018.

The exact path covers stationary/line/polyline translations of finite flat and
corner-radius end mills with rational source coordinates.  Nonlinear source
motion is consumed through MC-058-certified polyline leaves with an explicit
Euclidean translation enclosure; those leaves produce a conservative
INSIDE/OUTSIDE/UNCERTIFIED sweep sandwich rather than guessed equality.

Binary floating-point values are rejected from authority inputs.
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
    return (q(values[0]), q(values[1]), q(values[2]))


@dataclass(frozen=True)
class FlatEndMill:
    radius: Fraction
    length: Fraction

    @classmethod
    def make(cls, radius, length) -> "FlatEndMill":
        r, l = q(radius), q(length)
        if r <= 0 or l <= 0:
            raise ValueError("flat cutter radius/length must be positive")
        return cls(r, l)

    @property
    def core_radius(self) -> Fraction:
        return self.radius


@dataclass(frozen=True)
class CornerRadiusEndMill:
    radius: Fraction
    corner_radius: Fraction
    length: Fraction

    @classmethod
    def make(cls, radius, corner_radius, length) -> "CornerRadiusEndMill":
        r, c, l = q(radius), q(corner_radius), q(length)
        if r <= 0 or c <= 0 or l <= 0:
            raise ValueError("corner cutter dimensions must be positive")
        if not c < r:
            raise ValueError("corner radius must be strictly smaller than cutter radius; ball/round is MC-019")
        if c > l:
            raise ValueError("corner radius must not exceed finite cutter length")
        return cls(r, c, l)

    @property
    def core_radius(self) -> Fraction:
        return self.radius - self.corner_radius


Tool = FlatEndMill | CornerRadiusEndMill


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
        iv = (q(source_interval[0]), q(source_interval[1]))
        if iv[0] > iv[1]:
            raise ValueError("source interval must be ordered")
        if not source_class:
            raise ValueError("source class is required")
        return cls(v3(p0), v3(p1), e, source_class, iv, bool(engagement_bound))


@dataclass(frozen=True)
class Cylinder:
    radius: Fraction
    z_min: Fraction
    z_max: Fraction

    def __post_init__(self) -> None:
        if self.radius < 0 or self.z_min > self.z_max:
            raise ValueError("invalid cylinder envelope")


def _trim(p: Sequence[Fraction]) -> tuple[Fraction, ...]:
    out = list(p)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return tuple(out or [Fraction(0)])


def _poly_add(a, b):
    n = max(len(a), len(b)); out = [Fraction(0)] * n
    for i in range(n):
        out[i] = (a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
    return _trim(out)


def _poly_sub(a, b):
    n = max(len(a), len(b)); out = [Fraction(0)] * n
    for i in range(n):
        out[i] = (a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)
    return _trim(out)


def _poly_mul(a, b):
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x * y
    return _trim(out)


def _poly_scale(a, k):
    return _trim([q(k) * x for x in a])


def _poly_eval(p, x: Fraction) -> Fraction:
    acc = Fraction(0)
    for c in reversed(p):
        acc = acc * x + c
    return acc


def _poly_deriv(p):
    if len(p) <= 1:
        return (Fraction(0),)
    return _trim([i * p[i] for i in range(1, len(p))])


def _poly_divmod(a, b):
    a = list(_trim(a)); b = _trim(b)
    if b == (0,):
        raise ZeroDivisionError
    if len(a) < len(b):
        return (Fraction(0),), tuple(a)
    qout = [Fraction(0)] * (len(a) - len(b) + 1)
    while len(a) >= len(b) and any(a):
        k = len(a) - len(b)
        c = a[-1] / b[-1]
        qout[k] = c
        for i in range(len(b)):
            a[i+k] -= c * b[i]
        a = list(_trim(a))
    return _trim(qout), _trim(a)


def _poly_monic(p):
    p = _trim(p)
    if p == (0,): return p
    return _poly_scale(p, Fraction(1, 1) / p[-1])


def _poly_gcd(a, b):
    a, b = _trim(a), _trim(b)
    while b != (0,):
        _, r = _poly_divmod(a, b)
        a, b = b, r
    return _poly_monic(a)


def _poly_squarefree(p):
    p = _trim(p)
    if len(p) <= 1:
        return p
    g = _poly_gcd(p, _poly_deriv(p))
    qout, rem = _poly_divmod(p, g)
    assert rem == (0,)
    return _poly_monic(qout)


def _sturm(p):
    p = _poly_squarefree(p)
    if len(p) <= 1:
        return (p,)
    seq = [p, _poly_deriv(p)]
    while seq[-1] != (0,):
        _, r = _poly_divmod(seq[-2], seq[-1])
        if r == (0,):
            break
        seq.append(_poly_scale(r, -1))
    return tuple(seq)


def _variations(seq, x: Fraction) -> int:
    signs = []
    for p in seq:
        y = _poly_eval(p, x)
        if y > 0: signs.append(1)
        elif y < 0: signs.append(-1)
    return sum(a != b for a, b in zip(signs, signs[1:]))


def _root_count(seq, lo: Fraction, hi: Fraction) -> int:
    if lo >= hi: return 0
    return _variations(seq, lo) - _variations(seq, hi)


def _isolate_roots(p, lo: Fraction, hi: Fraction, depth: int = 96):
    p = _poly_squarefree(p)
    if len(p) <= 1:
        return []
    seq = _sturm(p)
    out: list[tuple[Fraction, Fraction]] = []

    def rec(a: Fraction, b: Fraction, count: int, remaining: int) -> None:
        if count <= 0: return
        if count == 1:
            aa, bb = a, b
            for _ in range(12):
                m = (aa + bb) / 2
                left = _root_count(seq, aa, m)
                if left == 1:
                    bb = m
                else:
                    aa = m
            out.append((aa, bb)); return
        if remaining <= 0:
            raise RuntimeError("Sturm isolation depth exhausted")
        m = (a + b) / 2
        left = _root_count(seq, a, m)
        rec(a, m, left, remaining - 1)
        rec(m, b, count - left, remaining - 1)

    rec(lo, hi, _root_count(seq, lo, hi), depth)
    return sorted(out)


def _sign(x: Fraction) -> int:
    return -1 if x < 0 else 1 if x > 0 else 0


def _factor_sign_at_root(factor, interval, combined) -> int:
    a, b = interval
    fseq = _sturm(_poly_squarefree(factor)) if len(_trim(factor)) > 1 else None
    if fseq is not None and _root_count(fseq, a, b) > 0:
        return 0
    for x in ((a+b)/2, (3*a+b)/4, (a+3*b)/4, a, b):
        val = _poly_eval(factor, x)
        if val != 0:
            return _sign(val)
    g = _poly_gcd(factor, combined)
    if len(g) > 1 and _root_count(_sturm(_poly_squarefree(g)), a, b) > 0:
        return 0
    raise RuntimeError("unable to sign polynomial at isolated root")


def _exists_f_le_zero_g_ge_zero(f, g, lo: Fraction, hi: Fraction) -> bool:
    """Decide exists t in [lo,hi] with f(t)<=0 and g(t)>=0 exactly."""
    if lo > hi: return False
    for x in (lo, hi):
        if _poly_eval(f, x) <= 0 and _poly_eval(g, x) >= 0:
            return True
    if lo == hi: return False
    h = _poly_squarefree(_poly_mul(f, g))
    if len(h) <= 1:
        mid = (lo + hi) / 2
        return _poly_eval(f, mid) <= 0 and _poly_eval(g, mid) >= 0
    roots = _isolate_roots(h, lo, hi)
    points = [lo]
    for a, b in roots:
        if points[-1] < a:
            points.append((points[-1] + a) / 2)
        points.append(b)
    if points[-1] < hi:
        points.append((points[-1] + hi) / 2)
    for x in points:
        if lo <= x <= hi and _poly_eval(h, x) != 0:
            if _poly_eval(f, x) <= 0 and _poly_eval(g, x) >= 0:
                return True
    for iv in roots:
        sf = _factor_sign_at_root(f, iv, h)
        sg = _factor_sign_at_root(g, iv, h)
        if sf <= 0 and sg >= 0:
            return True
    return False


def _linear_band_interval(a: Fraction, b: Fraction, lo: Fraction, hi: Fraction):
    """Closed t interval in [0,1] where lo <= a+b*t <= hi."""
    if lo > hi:
        raise ValueError("invalid band")
    if b == 0:
        return (Fraction(0), Fraction(1)) if lo <= a <= hi else None
    t0 = (lo - a) / b; t1 = (hi - a) / b
    l, h = min(t0, t1), max(t0, t1)
    l = max(l, Fraction(0)); h = min(h, Fraction(1))
    return None if l > h else (l, h)


def _radial_poly(point, p0, p1):
    qx, qy, _ = point; x0, y0, _ = p0; x1, y1, _ = p1
    ux, uy = qx - x0, qy - y0
    dx, dy = x1 - x0, y1 - y0
    return _trim((ux*ux + uy*uy, -2*(ux*dx + uy*dy), dx*dx + dy*dy))


def _quadratic_min(poly, iv):
    lo, hi = iv; vals = [_poly_eval(poly, lo), _poly_eval(poly, hi)]
    if len(poly) >= 3 and poly[2] > 0:
        t = -poly[1] / (2 * poly[2])
        if lo <= t <= hi: vals.append(_poly_eval(poly, t))
    return min(vals)


def cylinder_segment_contains(point, cyl: Cylinder, p0, p1) -> bool:
    point, p0, p1 = v3(point), v3(p0), v3(p1)
    z_a = point[2] - p0[2]; z_b = -(p1[2] - p0[2])
    iv = _linear_band_interval(z_a, z_b, cyl.z_min, cyl.z_max)
    if iv is None: return False
    return _quadratic_min(_radial_poly(point, p0, p1), iv) <= cyl.radius * cyl.radius


def flat_segment_contains(point, tool: FlatEndMill, p0, p1) -> bool:
    return cylinder_segment_contains(point, Cylinder(tool.radius, Fraction(0), tool.length), p0, p1)


def corner_segment_contains(point, tool: CornerRadiusEndMill, p0, p1) -> bool:
    """Exact membership in a translated corner-radius cutter sweep over one line."""
    point, p0, p1 = v3(point), v3(p0), v3(p1)
    r, c, a, L = tool.radius, tool.corner_radius, tool.core_radius, tool.length
    s = _radial_poly(point, p0, p1)
    z0 = point[2] - p0[2]; zb = -(p1[2] - p0[2])

    upper = _linear_band_interval(z0, zb, c, L)
    if upper is not None and _quadratic_min(s, upper) <= r*r:
        return True

    lower = _linear_band_interval(z0, zb, Fraction(0), c)
    if lower is None:
        return False
    if _quadratic_min(s, lower) <= a*a:
        return True

    zc = (z0 - c, zb)
    zc2 = _poly_mul(zc, zc)
    h = _poly_add(s, (a*a - c*c,))
    h = _poly_add(h, zc2)
    f = _poly_sub(_poly_mul(h, h), _poly_scale(s, 4*a*a))
    g = _poly_sub(s, (a*a,))
    return _exists_f_le_zero_g_ge_zero(f, g, lower[0], lower[1])


def exact_sweep_contains(point, tool: Tool, leaves: Iterable[Leaf]) -> bool:
    for leaf in leaves:
        if leaf.translation_error != 0:
            raise ValueError("exact sweep requires zero-error leaves")
        if not leaf.engagement_bound:
            raise ValueError("leaf must be bound to an engaged source interval")
        if isinstance(tool, FlatEndMill):
            hit = flat_segment_contains(point, tool, leaf.p0, leaf.p1)
        else:
            hit = corner_segment_contains(point, tool, leaf.p0, leaf.p1)
        if hit: return True
    return False


def certified_classify(point, tool: Tool, leaves: Iterable[Leaf]) -> str:
    """Sound fixed-axis classification from MC-058-certified translation leaves."""
    leaves = tuple(leaves)
    if not leaves:
        return "OUTSIDE"
    exact_hits = []
    for leaf in leaves:
        if not leaf.engagement_bound:
            raise ValueError("unbound engagement leaf")
        if leaf.translation_error == 0:
            hit = flat_segment_contains(point, tool, leaf.p0, leaf.p1) if isinstance(tool, FlatEndMill) else corner_segment_contains(point, tool, leaf.p0, leaf.p1)
            exact_hits.append(hit)
            if hit: return "INSIDE"
    outer_hit = False
    inner_hit = False
    for leaf in leaves:
        e = leaf.translation_error
        if e == 0: continue
        outer = Cylinder(tool.radius + e, -e, tool.length + e)
        if cylinder_segment_contains(point, outer, leaf.p0, leaf.p1):
            outer_hit = True
        core = tool.core_radius - e
        zlo, zhi = e, tool.length - e
        if core >= 0 and zlo <= zhi:
            inner = Cylinder(core, zlo, zhi)
            if cylinder_segment_contains(point, inner, leaf.p0, leaf.p1):
                inner_hit = True
    if inner_hit: return "INSIDE"
    if not outer_hit and not any(exact_hits): return "OUTSIDE"
    return "UNCERTIFIED"


def swept_path(leaves: Sequence[Leaf]) -> tuple[Leaf, ...]:
    """Validate finite ordered source coverage without deleting retraces."""
    if not leaves:
        raise ValueError("at least one engaged leaf is required")
    out = tuple(leaves)
    for i, leaf in enumerate(out):
        if not leaf.engagement_bound:
            raise ValueError("engagement binding is mandatory")
        if i and out[i-1].p1 != leaf.p0:
            raise ValueError("engaged path must be continuous; teleportation is invalid")
    return out
