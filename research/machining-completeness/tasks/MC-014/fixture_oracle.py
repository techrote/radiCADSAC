#!/usr/bin/env python3
"""Exact, candidate-independent witness oracle for MC-014 F13-F16.

This oracle proves only preregistered rational growth, retrace, partition and
exhaustion witnesses. It is not a native geometry candidate, a universal
machining oracle, or a STEP checker.
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


def interval_length(interval: Sequence[int | str | Fraction]) -> Fraction:
    if len(interval) != 2:
        raise ValueError("interval requires [lo,hi]")
    lo, hi = q(interval[0]), q(interval[1])
    if hi < lo:
        raise ValueError("reversed interval")
    return hi - lo


def box_volume(box: Sequence[Sequence[int | str | Fraction]]) -> Fraction:
    if len(box) != 3:
        raise ValueError("3-D box requires three intervals")
    volume = Q(1)
    for interval in box:
        length = interval_length(interval)
        if length <= 0:
            raise ValueError("box must have positive volume")
        volume *= length
    return volume


def disjoint_box_volume(boxes: Iterable[Sequence[Sequence[int | str | Fraction]]]) -> Fraction:
    """Sum exact volumes of pairwise disjoint boxes.

    MC-014 fixtures preregister disjoint boxes and verify disjointness
    structurally in the task verifier; this helper deliberately does not claim a
    general box-union algorithm.
    """
    return sum((box_volume(box) for box in boxes), Q(0))


def geometric_tier_counts(tiers: int) -> tuple[int, ...]:
    if isinstance(tiers, bool) or tiers < 1:
        raise ValueError("tiers must be a positive integer")
    return tuple(1 << i for i in range(tiers))


def first_occurrence_change_flags(history: Sequence[str]) -> tuple[bool, ...]:
    seen: set[str] = set()
    flags = []
    for ident in history:
        if not isinstance(ident, str) or not ident:
            raise ValueError("history identifiers must be non-empty strings")
        flags.append(ident not in seen)
        seen.add(ident)
    return tuple(flags)


def unique_history_volume(history: Sequence[str], cut_volumes: dict[str, int | str | Fraction]) -> Fraction:
    seen: set[str] = set()
    total = Q(0)
    for ident in history:
        if ident not in cut_volumes:
            raise KeyError(f"unknown cut id {ident}")
        if ident not in seen:
            volume = q(cut_volumes[ident])
            if volume <= 0:
                raise ValueError("unique material-changing cut volume must be positive")
            total += volume
            seen.add(ident)
    return total


def partition_interval(
    start: int | str | Fraction,
    end: int | str | Fraction,
    planes: Sequence[int | str | Fraction],
) -> tuple[tuple[Fraction, Fraction], ...]:
    lo, hi = q(start), q(end)
    if not lo < hi:
        raise ValueError("partition interval must be positive")
    cuts = [q(p) for p in planes]
    if cuts != sorted(cuts) or len(set(cuts)) != len(cuts):
        raise ValueError("partition planes must be unique and ordered")
    if any(not lo < p < hi for p in cuts):
        raise ValueError("partition plane outside open interval")
    pts = [lo, *cuts, hi]
    return tuple((a, b) for a, b in zip(pts, pts[1:]))


def partition_is_exact_cover(
    start: int | str | Fraction,
    end: int | str | Fraction,
    segments: Sequence[Sequence[int | str | Fraction]],
) -> bool:
    lo, hi = q(start), q(end)
    if not segments:
        return False
    cursor = lo
    for seg in segments:
        if len(seg) != 2:
            return False
        a, b = q(seg[0]), q(seg[1])
        if a != cursor or not a < b:
            return False
        cursor = b
    return cursor == hi


def signed_interface_delta(
    left_end: int | str | Fraction,
    right_start: int | str | Fraction,
) -> Fraction:
    """Positive is a gap, zero is exact continuity, negative is overlap."""
    return q(right_start) - q(left_end)


def classify_interface(delta: int | str | Fraction) -> str:
    value = q(delta)
    if value > 0:
        return "GAP"
    if value < 0:
        return "OVERLAP"
    return "EXACT"


def remaining_slab_volume(
    x_interval: Sequence[int | str | Fraction],
    y_interval: Sequence[int | str | Fraction],
    thickness: int | str | Fraction,
) -> Fraction:
    t = q(thickness)
    if t <= 0:
        return Q(0)
    return interval_length(x_interval) * interval_length(y_interval) * t


def exhaustion_state(thickness: int | str | Fraction) -> str:
    t = q(thickness)
    if t > 0:
        return "POSITIVE_MATERIAL"
    if t == 0:
        return "EXACT_EMPTY"
    return "OVERTRAVEL_EMPTY"
