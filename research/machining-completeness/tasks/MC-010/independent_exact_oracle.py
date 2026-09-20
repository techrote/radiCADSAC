#!/usr/bin/env python3
"""Exact rational cell-set controls for MC-010.

This module is intentionally narrow. It models finite unions of disjoint,
positive-volume axis-aligned rational boxes and exact axis-parallel translational
sweeps. It is a control oracle, not a machining-domain implementation.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Sequence


Q = Fraction


def q(value: int | str | Fraction) -> Fraction:
    """Parse an exact rational. Binary floating input is forbidden."""
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError("exact rational input must not be bool/float")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, str):
        return Fraction(value)
    raise TypeError(f"unsupported rational input type: {type(value).__name__}")


@dataclass(frozen=True, order=True)
class Box:
    x0: Fraction
    x1: Fraction
    y0: Fraction
    y1: Fraction
    z0: Fraction
    z1: Fraction

    @classmethod
    def make(
        cls,
        x0: int | str | Fraction,
        x1: int | str | Fraction,
        y0: int | str | Fraction,
        y1: int | str | Fraction,
        z0: int | str | Fraction,
        z1: int | str | Fraction,
    ) -> "Box":
        box = cls(q(x0), q(x1), q(y0), q(y1), q(z0), q(z1))
        box.require_positive_volume()
        return box

    def require_positive_volume(self) -> None:
        if not (self.x0 < self.x1 and self.y0 < self.y1 and self.z0 < self.z1):
            raise ValueError("box must have strictly positive volume")

    @property
    def volume(self) -> Fraction:
        return (self.x1 - self.x0) * (self.y1 - self.y0) * (self.z1 - self.z0)

    def intersection(self, other: "Box") -> "Box | None":
        lo = (max(self.x0, other.x0), max(self.y0, other.y0), max(self.z0, other.z0))
        hi = (min(self.x1, other.x1), min(self.y1, other.y1), min(self.z1, other.z1))
        if not (lo[0] < hi[0] and lo[1] < hi[1] and lo[2] < hi[2]):
            return None
        return Box(lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])

    def translate_axis(self, axis: str, delta: int | str | Fraction) -> "Box":
        d = q(delta)
        if axis == "x":
            return Box(self.x0 + d, self.x1 + d, self.y0, self.y1, self.z0, self.z1)
        if axis == "y":
            return Box(self.x0, self.x1, self.y0 + d, self.y1 + d, self.z0, self.z1)
        if axis == "z":
            return Box(self.x0, self.x1, self.y0, self.y1, self.z0 + d, self.z1 + d)
        raise ValueError("axis must be x, y or z")


def _append_if_positive(out: list[Box], coords: Sequence[Fraction]) -> None:
    b = Box(*coords)
    if b.x0 < b.x1 and b.y0 < b.y1 and b.z0 < b.z1:
        out.append(b)


def subtract_box(stock: Box, cutter: Box) -> tuple[Box, ...]:
    """Return an exact, disjoint partition of stock minus cutter."""
    hit = stock.intersection(cutter)
    if hit is None:
        return (stock,)

    out: list[Box] = []
    # Slabs left/right of the intersection.
    _append_if_positive(out, (stock.x0, hit.x0, stock.y0, stock.y1, stock.z0, stock.z1))
    _append_if_positive(out, (hit.x1, stock.x1, stock.y0, stock.y1, stock.z0, stock.z1))
    # Within the intersecting x-span, slabs before/after its y-span.
    _append_if_positive(out, (hit.x0, hit.x1, stock.y0, hit.y0, stock.z0, stock.z1))
    _append_if_positive(out, (hit.x0, hit.x1, hit.y1, stock.y1, stock.z0, stock.z1))
    # Within the intersecting x/y prism, slabs below/above its z-span.
    _append_if_positive(out, (hit.x0, hit.x1, hit.y0, hit.y1, stock.z0, hit.z0))
    _append_if_positive(out, (hit.x0, hit.x1, hit.y0, hit.y1, hit.z1, stock.z1))
    return tuple(sorted(out))


def subtract_many(material: Iterable[Box], cutters: Iterable[Box]) -> tuple[Box, ...]:
    cells = tuple(sorted(material))
    for cutter in cutters:
        nxt: list[Box] = []
        for cell in cells:
            nxt.extend(subtract_box(cell, cutter))
        cells = tuple(sorted(nxt))
    return cells


def swept_box_axis_parallel(
    cutter: Box,
    axis: str,
    start_delta: int | str | Fraction,
    end_delta: int | str | Fraction,
) -> Box:
    """Exact swept set for a box translated monotonically along one coordinate axis."""
    a, b = q(start_delta), q(end_delta)
    lo, hi = min(a, b), max(a, b)
    if axis == "x":
        return Box(cutter.x0 + lo, cutter.x1 + hi, cutter.y0, cutter.y1, cutter.z0, cutter.z1)
    if axis == "y":
        return Box(cutter.x0, cutter.x1, cutter.y0 + lo, cutter.y1 + hi, cutter.z0, cutter.z1)
    if axis == "z":
        return Box(cutter.x0, cutter.x1, cutter.y0, cutter.y1, cutter.z0 + lo, cutter.z1 + hi)
    raise ValueError("axis must be x, y or z")


def total_volume(material: Iterable[Box]) -> Fraction:
    return sum((cell.volume for cell in material), Fraction(0, 1))


def _strict_overlap(a0: Fraction, a1: Fraction, b0: Fraction, b1: Fraction) -> bool:
    return max(a0, b0) < min(a1, b1)


def face_connected(a: Box, b: Box) -> bool:
    """True only for positive-area face contact; edge/point contact is disconnected."""
    xface = (a.x1 == b.x0 or b.x1 == a.x0) and _strict_overlap(a.y0, a.y1, b.y0, b.y1) and _strict_overlap(a.z0, a.z1, b.z0, b.z1)
    yface = (a.y1 == b.y0 or b.y1 == a.y0) and _strict_overlap(a.x0, a.x1, b.x0, b.x1) and _strict_overlap(a.z0, a.z1, b.z0, b.z1)
    zface = (a.z1 == b.z0 or b.z1 == a.z0) and _strict_overlap(a.x0, a.x1, b.x0, b.x1) and _strict_overlap(a.y0, a.y1, b.y0, b.y1)
    return xface or yface or zface


def component_count(material: Iterable[Box]) -> int:
    cells = list(material)
    if not cells:
        return 0
    unseen = set(range(len(cells)))
    count = 0
    while unseen:
        count += 1
        seed = unseen.pop()
        stack = [seed]
        while stack:
            i = stack.pop()
            attached = [j for j in tuple(unseen) if face_connected(cells[i], cells[j])]
            for j in attached:
                unseen.remove(j)
                stack.append(j)
    return count


def contains_point(cell: Box, xyz: Sequence[int | str | Fraction]) -> bool:
    x, y, z = (q(v) for v in xyz)
    return cell.x0 <= x <= cell.x1 and cell.y0 <= y <= cell.y1 and cell.z0 <= z <= cell.z1


def material_contains(material: Iterable[Box], xyz: Sequence[int | str | Fraction]) -> bool:
    return any(contains_point(cell, xyz) for cell in material)
