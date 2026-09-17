#!/usr/bin/env python3
"""Deterministic research-grade axisymmetric lathe material-domain solver.

The durable authority remains the canonical journal. This module is a disposable
RCS-010 prototype that applies canonical semantic turning operations to a 2D
(z, radius) material section, then emits a closed radial/axial polygon suitable
for exact revolution by the pinned OCCT measurement worker.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, getcontext
from typing import Any, Iterable

getcontext().prec = 34
D = Decimal
EPS = D("1e-18")
PI = D("3.1415926535897932384626433832795028841971693993751")


def dec(value: Any) -> Decimal:
    return value if isinstance(value, Decimal) else D(str(value))


@dataclass
class Section:
    z0: Decimal
    z1: Decimal
    outer0: Decimal
    outer1: Decimal
    inner0: Decimal
    inner1: Decimal

    def interp_outer(self, z: Decimal) -> Decimal:
        if self.z1 == self.z0:
            return self.outer1
        t = (z - self.z0) / (self.z1 - self.z0)
        return self.outer0 + t * (self.outer1 - self.outer0)

    def interp_inner(self, z: Decimal) -> Decimal:
        if self.z1 == self.z0:
            return self.inner1
        t = (z - self.z0) / (self.z1 - self.z0)
        return self.inner0 + t * (self.inner1 - self.inner0)

    def volume_mm3(self) -> Decimal:
        length = self.z1 - self.z0
        outer_term = self.outer0 * self.outer0 + self.outer0 * self.outer1 + self.outer1 * self.outer1
        inner_term = self.inner0 * self.inner0 + self.inner0 * self.inner1 + self.inner1 * self.inner1
        return PI * length * (outer_term - inner_term) / D(3)


class LatheProfile:
    def __init__(self, z0: Decimal, z1: Decimal, outer: Decimal, inner: Decimal = D(0)) -> None:
        if not z1 > z0:
            raise ValueError("stock z1 must be greater than z0")
        if not outer > inner >= 0:
            raise ValueError("stock radii must satisfy outer > inner >= 0")
        self.sections = [Section(z0, z1, outer, outer, inner, inner)]

    @property
    def z0(self) -> Decimal:
        return self.sections[0].z0

    @property
    def z1(self) -> Decimal:
        return self.sections[-1].z1

    def split(self, z: Decimal) -> None:
        for index, section in enumerate(self.sections):
            if section.z0 + EPS < z < section.z1 - EPS:
                outer = section.interp_outer(z)
                inner = section.interp_inner(z)
                self.sections[index:index + 1] = [
                    Section(section.z0, z, section.outer0, outer, section.inner0, inner),
                    Section(z, section.z1, outer, section.outer1, inner, section.inner1),
                ]
                return

    def _prepare_interval(self, z0: Decimal, z1: Decimal) -> list[Section]:
        if z1 <= z0:
            raise ValueError("operation interval must have positive length")
        if z0 < self.z0 - EPS or z1 > self.z1 + EPS:
            raise ValueError("operation interval lies outside current material domain")
        self.split(z0)
        self.split(z1)
        return [s for s in self.sections if s.z0 >= z0 - EPS and s.z1 <= z1 + EPS]

    def trim_front(self, new_z0: Decimal) -> bool:
        if new_z0 <= self.z0 + EPS:
            return False
        if new_z0 >= self.z1 - EPS:
            raise ValueError("facing operation would remove all material")
        self.split(new_z0)
        old = self.sections
        self.sections = [s for s in old if s.z0 >= new_z0 - EPS]
        return True

    def reduce_outer(self, z0: Decimal, z1: Decimal, target: Decimal) -> bool:
        changed = False
        for section in self._prepare_interval(z0, z1):
            n0 = min(section.outer0, target)
            n1 = min(section.outer1, target)
            if n0 <= section.inner0 or n1 <= section.inner1:
                raise ValueError("OD operation would invert/collapse material thickness")
            changed |= abs(n0 - section.outer0) > EPS or abs(n1 - section.outer1) > EPS
            section.outer0, section.outer1 = n0, n1
        return changed

    def taper_outer(self, z0: Decimal, z1: Decimal, radius0: Decimal, radius1: Decimal) -> bool:
        changed = False
        span = z1 - z0
        for section in self._prepare_interval(z0, z1):
            def target(z: Decimal) -> Decimal:
                return radius0 + (z - z0) * (radius1 - radius0) / span
            n0 = min(section.outer0, target(section.z0))
            n1 = min(section.outer1, target(section.z1))
            if n0 <= section.inner0 or n1 <= section.inner1:
                raise ValueError("taper operation would invert/collapse material thickness")
            changed |= abs(n0 - section.outer0) > EPS or abs(n1 - section.outer1) > EPS
            section.outer0, section.outer1 = n0, n1
        return changed

    def enlarge_inner(self, z0: Decimal, z1: Decimal, target: Decimal) -> bool:
        changed = False
        for section in self._prepare_interval(z0, z1):
            n0 = max(section.inner0, target)
            n1 = max(section.inner1, target)
            if n0 >= section.outer0 or n1 >= section.outer1:
                raise ValueError("ID operation would invert/collapse material thickness")
            changed |= abs(n0 - section.inner0) > EPS or abs(n1 - section.inner1) > EPS
            section.inner0, section.inner1 = n0, n1
        return changed

    def volume_mm3(self) -> Decimal:
        return sum((s.volume_mm3() for s in self.sections), D(0))

    def _append_distinct(self, points: list[tuple[Decimal, Decimal]], radius: Decimal, z: Decimal) -> None:
        point = (radius, z)
        if not points or points[-1] != point:
            points.append(point)

    def polygon(self) -> list[tuple[Decimal, Decimal]]:
        """Closed radial/axial section polygon, ordered for face construction."""
        if not self.sections:
            raise ValueError("empty profile")

        points: list[tuple[Decimal, Decimal]] = []
        first = self.sections[0]
        self._append_distinct(points, first.inner0, first.z0)
        self._append_distinct(points, first.outer0, first.z0)

        for index, section in enumerate(self.sections):
            if index and self.sections[index - 1].outer1 != section.outer0:
                self._append_distinct(points, section.outer0, section.z0)
            self._append_distinct(points, section.outer1, section.z1)

        last = self.sections[-1]
        self._append_distinct(points, last.inner1, last.z1)

        for index in range(len(self.sections) - 1, -1, -1):
            section = self.sections[index]
            self._append_distinct(points, section.inner0, section.z0)
            if index and self.sections[index - 1].inner1 != section.inner0:
                self._append_distinct(points, self.sections[index - 1].inner1, section.z0)

        if points[-1] != points[0]:
            points.append(points[0])
        return points

    def as_dict(self) -> dict[str, Any]:
        return {
            "z0_mm": str(self.z0),
            "z1_mm": str(self.z1),
            "sections": [
                {
                    "z0_mm": str(s.z0),
                    "z1_mm": str(s.z1),
                    "outer0_mm": str(s.outer0),
                    "outer1_mm": str(s.outer1),
                    "inner0_mm": str(s.inner0),
                    "inner1_mm": str(s.inner1),
                }
                for s in self.sections
            ],
            "volume_mm3": float(self.volume_mm3()),
            "polygon_points": [[float(r), float(z)] for r, z in self.polygon()],
        }


def apply_case(case: dict[str, Any]) -> dict[str, Any]:
    stock = case["stock"]
    profile = LatheProfile(
        dec(stock["z0_mm"]),
        dec(stock["z1_mm"]),
        dec(stock["outer_radius_mm"]),
        dec(stock.get("inner_radius_mm", "0")),
    )
    stock_volume = profile.volume_mm3()

    journal_events = 0
    geometry_events = 0
    provenance_noop_events = 0
    raw_samples = 0
    canonical_geometry_events = 0
    canonicalization_notes: list[str] = []

    for operation in case["operations"]:
        repeat = int(operation.get("repeat", 1))
        kind = operation["kind"]
        if kind == "noisy_od_trace":
            samples = [dec(v) for v in operation["raw_radius_mm"]]
            raw_samples += len(samples)
            nominal = dec(operation["nominal_radius_mm"])
            bound = dec(operation["max_deviation_mm"])
            worst = max(abs(value - nominal) for value in samples)
            if worst > bound:
                raise ValueError(f"noisy trace exceeds canonicalization bound: {worst} > {bound}")
            journal_events += len(samples)
            changed = profile.reduce_outer(dec(operation["z0_mm"]), dec(operation["z1_mm"]), nominal)
            geometry_events += int(changed)
            canonical_geometry_events += 1
            canonicalization_notes.append(
                f"{len(samples)} raw samples bounded by {bound} mm -> one canonical OD envelope at radius {nominal} mm"
            )
            continue

        for _ in range(repeat):
            journal_events += 1
            if kind == "od_turn":
                changed = profile.reduce_outer(
                    dec(operation["z0_mm"]), dec(operation["z1_mm"]), dec(operation["target_radius_mm"])
                )
            elif kind == "face_front":
                changed = profile.trim_front(dec(operation["new_z0_mm"]))
            elif kind == "taper_outer":
                changed = profile.taper_outer(
                    dec(operation["z0_mm"]),
                    dec(operation["z1_mm"]),
                    dec(operation["radius0_mm"]),
                    dec(operation["radius1_mm"]),
                )
            elif kind == "id_bore":
                changed = profile.enlarge_inner(
                    dec(operation["z0_mm"]),
                    dec(operation["z1_mm"]),
                    dec(operation["target_inner_radius_mm"]),
                )
            else:
                raise ValueError(f"unsupported operation kind: {kind}")
            if changed:
                geometry_events += 1
            else:
                provenance_noop_events += 1

    return {
        "case_id": case["id"],
        "stock_volume_mm3": float(stock_volume),
        "result": profile.as_dict(),
        "journal_events": journal_events,
        "geometry_events": geometry_events,
        "provenance_noop_events": provenance_noop_events,
        "raw_samples": raw_samples,
        "canonical_geometry_events": canonical_geometry_events,
        "canonicalization_notes": canonicalization_notes,
    }


def encode_polygon(points: Iterable[Iterable[float]]) -> str:
    return ";".join(f"{float(radius):.17g},{float(z):.17g}" for radius, z in points)
