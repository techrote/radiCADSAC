#!/usr/bin/env python3
"""Exact, candidate-independent witness oracle for MC-013 F09-F12.

This oracle proves only the preregistered rational phase, connectivity,
singular-boundary and scale/precision witnesses used by MC-013. It is not a
native geometry candidate, a universal machining oracle, or a STEP checker.
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


def normalize_turn(value: int | str | Fraction) -> Fraction:
    """Normalize an exact turn fraction to [0,1)."""
    x = q(value)
    return x - (x.numerator // x.denominator)


def body_alignment_phase(body_theta_turns: int | str | Fraction) -> Fraction:
    """Spindle phase at which a body-fixed azimuth meets machine angle zero."""
    return normalize_turn(-q(body_theta_turns))


def phase_window_contains(
    phase_turns: int | str | Fraction,
    start_turns: int | str | Fraction,
    end_turns: int | str | Fraction,
) -> bool:
    """Closed exact phase gate, including a gate that wraps through turn zero."""
    p = normalize_turn(phase_turns)
    lo = normalize_turn(start_turns)
    hi = normalize_turn(end_turns)
    if lo <= hi:
        return lo <= p <= hi
    return p >= lo or p <= hi


def phase_indexed_removes(
    body_theta_turns: int | str | Fraction,
    start_turns: int | str | Fraction,
    end_turns: int | str | Fraction,
) -> bool:
    return phase_window_contains(body_alignment_phase(body_theta_turns), start_turns, end_turns)


def synchronized_turning_removes(
    body_theta_turns: int | str | Fraction,
    z: int | str | Fraction,
    radius: int | str | Fraction,
    phase_start: int | str | Fraction,
    phase_end: int | str | Fraction,
    z_start: int | str | Fraction,
    z_end: int | str | Fraction,
    axial_half_width: int | str | Fraction,
    final_radius: int | str | Fraction,
) -> bool:
    """Exact body-phase/feed-correlated turning witness for a non-wrapping gate."""
    phase = body_alignment_phase(body_theta_turns)
    lo, hi = normalize_turn(phase_start), normalize_turn(phase_end)
    if not lo < hi:
        raise ValueError("synchronized witness requires a non-wrapping positive phase interval")
    if not (lo <= phase <= hi):
        return False
    width = q(axial_half_width)
    if width < 0:
        raise ValueError("negative axial half-width")
    fr = q(final_radius)
    if fr < 0:
        raise ValueError("negative final radius")
    alpha = (phase - lo) / (hi - lo)
    zc = q(z_start) + alpha * (q(z_end) - q(z_start))
    return abs(q(z) - zc) <= width and q(radius) > fr


def cross_slot_component_count(slot_count: int, remaining_web: int | str | Fraction) -> int:
    """Count components after N complete cross-stock separators.

    A strictly positive residual web preserves one material component. At exact
    zero or overtravel, every separator is through and yields N+1 components.
    """
    if isinstance(slot_count, bool) or slot_count < 0:
        raise ValueError("slot_count must be a non-negative integer")
    return 1 if q(remaining_web) > 0 else slot_count + 1


def retained_slab_widths(
    stock_lo: int | str | Fraction,
    stock_hi: int | str | Fraction,
    slots: Sequence[Sequence[int | str | Fraction]],
) -> tuple[Fraction, ...]:
    """Exact 1-D retained intervals induced by ordered disjoint through-slots."""
    lo, hi = q(stock_lo), q(stock_hi)
    if lo >= hi:
        raise ValueError("stock interval must be positive")
    cursor = lo
    widths = []
    for raw in slots:
        if len(raw) != 2:
            raise ValueError("slot requires [lo,hi]")
        a, b = q(raw[0]), q(raw[1])
        if not (cursor < a < b < hi):
            raise ValueError("slots must be ordered, disjoint and internal")
        widths.append(a - cursor)
        cursor = b
    widths.append(hi - cursor)
    if any(width <= 0 for width in widths):
        raise ValueError("all retained slabs must have positive width")
    return tuple(widths)


def squared_distance_2d(
    point: Sequence[int | str | Fraction],
    center: Sequence[int | str | Fraction],
) -> Fraction:
    if len(point) != 2 or len(center) != 2:
        raise ValueError("2-D points require two coordinates")
    dx = q(point[0]) - q(center[0])
    dy = q(point[1]) - q(center[1])
    return dx * dx + dy * dy


def signed_circle_clearance2(
    point: Sequence[int | str | Fraction],
    center: Sequence[int | str | Fraction],
    radius: int | str | Fraction,
) -> Fraction:
    r = q(radius)
    if r < 0:
        raise ValueError("negative radius")
    return squared_distance_2d(point, center) - r * r


def signed_pair_clearance2(
    center_a: Sequence[int | str | Fraction],
    radius_a: int | str | Fraction,
    center_b: Sequence[int | str | Fraction],
    radius_b: int | str | Fraction,
) -> Fraction:
    ra, rb = q(radius_a), q(radius_b)
    if ra < 0 or rb < 0:
        raise ValueError("negative radius")
    return squared_distance_2d(center_a, center_b) - (ra + rb) ** 2


def classify_signed(value: int | str | Fraction) -> str:
    x = q(value)
    if x < 0:
        return "PENETRATING"
    if x > 0:
        return "SEPARATED"
    return "TANGENT"


def retained_web(
    left_cut_end: int | str | Fraction,
    right_cut_start: int | str | Fraction,
) -> Fraction:
    return q(right_cut_start) - q(left_cut_end)


def web_connectivity(
    left_cut_end: int | str | Fraction,
    right_cut_start: int | str | Fraction,
) -> str:
    width = retained_web(left_cut_end, right_cut_start)
    if width > 0:
        return "CONNECTED_POSITIVE_WEB"
    if width == 0:
        return "ZERO_WIDTH_LIMIT"
    return "OVERLAP_NO_WEB"


def translated_gap(
    local_left_end: int | str | Fraction,
    local_right_start: int | str | Fraction,
    translation: int | str | Fraction,
) -> Fraction:
    t = q(translation)
    return retained_web(q(local_left_end) + t, q(local_right_start) + t)


def rotate90_xy(
    point: Sequence[int | str | Fraction],
) -> tuple[Fraction, Fraction, Fraction]:
    if len(point) != 3:
        raise ValueError("3-D point requires three coordinates")
    x, y, z = q(point[0]), q(point[1]), q(point[2])
    return -y, x, z
