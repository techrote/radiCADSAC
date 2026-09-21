#!/usr/bin/env python3
"""Bounded exact-rational rotational-reduction model for MC-021.

This is deterministic research/model evidence.  It deliberately implements only
an exact axisymmetric quotient subtype; phase-sensitive/eccentric histories are
rejected rather than approximated.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isqrt
from typing import Iterable, Mapping, Sequence

F = Fraction


@dataclass(frozen=True, order=True)
class MeridianRect:
    """Closed meridian rectangle [r0,r1] x [z0,z1], r >= 0.

    Positive width in both directions is required for material/cutter regions.
    Boundaries are retained exactly; regularized subtraction treats zero-area
    intersections as no positive-volume removal.
    """

    r0: F
    r1: F
    z0: F
    z1: F

    def __post_init__(self) -> None:
        if self.r0 < 0 or not (self.r0 < self.r1 and self.z0 < self.z1):
            raise ValueError("meridian rectangles require r>=0 and positive area")

    def contains(self, r: F, z: F) -> bool:
        return self.r0 <= r <= self.r1 and self.z0 <= z <= self.z1

    def pi_volume_coeff(self) -> F:
        """Return c such that the exact solid-of-revolution volume is c*pi."""
        return (self.r1 * self.r1 - self.r0 * self.r0) * (self.z1 - self.z0)


@dataclass(frozen=True)
class Line2:
    dr0: F
    dz0: F
    dr1: F
    dz1: F


def _affine_t_interval(a0: F, a1: F, lo: F, hi: F) -> tuple[F, F] | None:
    """t in [0,1] for which lo <= a0 + t*(a1-a0) <= hi."""
    if lo > hi:
        return None
    d = a1 - a0
    if d == 0:
        return (F(0), F(1)) if lo <= a0 <= hi else None
    t0 = (lo - a0) / d
    t1 = (hi - a0) / d
    if t0 > t1:
        t0, t1 = t1, t0
    t0 = max(F(0), t0)
    t1 = min(F(1), t1)
    return (t0, t1) if t0 <= t1 else None


def swept_rect_contains(rect: MeridianRect, motion: Line2, r: F, z: F) -> bool:
    """Exact membership in a translated rectangle sweep along one shared t.

    The same source parameter must satisfy radial and axial bands.  This is the
    quotient-space analogue of the MC-020 shared-parameter fixed-axis check.
    """
    ri = _affine_t_interval(motion.dr0, motion.dr1, r - rect.r1, r - rect.r0)
    zi = _affine_t_interval(motion.dz0, motion.dz1, z - rect.z1, z - rect.z0)
    if ri is None or zi is None:
        return False
    return max(ri[0], zi[0]) <= min(ri[1], zi[1])


def union_sweep_contains(rects: Sequence[MeridianRect], motion: Line2, r: F, z: F) -> bool:
    return any(swept_rect_contains(rect, motion, r, z) for rect in rects)


def _sqrt_fraction_exact(q: F) -> F:
    if q < 0:
        raise ValueError("negative squared radius")
    n = isqrt(q.numerator)
    d = isqrt(q.denominator)
    if n * n != q.numerator or d * d != q.denominator:
        raise ValueError("radius is not exactly rational")
    return F(n, d)


def rational_radius(x: F, y: F) -> F:
    """Exact rational radius for controls whose squared radius is a rational square."""
    return _sqrt_fraction_exact(x * x + y * y)


def revolved_rect_contains_cartesian(rect: MeridianRect, x: F, y: F, z: F) -> bool:
    """Independent Cartesian membership using squared radius only.

    No trigonometric sampling, floating point or angular epsilon is involved.
    """
    s = x * x + y * y
    return rect.r0 * rect.r0 <= s <= rect.r1 * rect.r1 and rect.z0 <= z <= rect.z1


def swept_rect_contains_cartesian_rational_radius(
    rect: MeridianRect, motion: Line2, x: F, y: F, z: F
) -> bool:
    return swept_rect_contains(rect, motion, rational_radius(x, y), z)


def _positive_intersection(a: MeridianRect, b: MeridianRect) -> MeridianRect | None:
    r0, r1 = max(a.r0, b.r0), min(a.r1, b.r1)
    z0, z1 = max(a.z0, b.z0), min(a.z1, b.z1)
    if r0 >= r1 or z0 >= z1:
        return None
    return MeridianRect(r0, r1, z0, z1)


def subtract_rect(material: MeridianRect, cutter: MeridianRect) -> list[MeridianRect]:
    """Regularized exact subtraction for one meridian rectangle.

    The result is a disjoint rectangular partition of the positive-area
    quotient material.  Zero-area contact removes no positive volume.
    """
    i = _positive_intersection(material, cutter)
    if i is None:
        return [material]
    out: list[MeridianRect] = []
    if material.r0 < i.r0:
        out.append(MeridianRect(material.r0, i.r0, material.z0, material.z1))
    if i.r1 < material.r1:
        out.append(MeridianRect(i.r1, material.r1, material.z0, material.z1))
    if material.z0 < i.z0:
        out.append(MeridianRect(i.r0, i.r1, material.z0, i.z0))
    if i.z1 < material.z1:
        out.append(MeridianRect(i.r0, i.r1, i.z1, material.z1))
    return out


def exact_pi_volume_coeff(rects: Iterable[MeridianRect]) -> F:
    return sum((r.pi_volume_coeff() for r in rects), F(0))


REQUIRED_TRUE = (
    "target_axisymmetry_certificate",
    "certificate_bound_to_target_body",
    "certificate_bound_to_setup_revision",
    "coaxial_spindle_and_material_axis",
    "rigid_setup_transform_exact",
    "phase_independent_meridian_placement",
    "engagement_factors_as_meridian_times_full_turn",
    "full_phase_orbit_for_every_meridian_state",
    "saved_operation_immutable",
    "engagement_boundaries_authoritative",
    "cutting_and_noncutting_regions_distinct",
    "physical_access_witness_present",
    "holder_clearance_witness_present",
    "durable_body_identity_preserved",
)
REQUIRED_FALSE = (
    "eccentric_setup",
    "phase_synchronization",
    "timed_phase_motion_required_for_geometry",
    "partial_phase_engagement",
    "compound_live_tool_kinematics",
    "sampled_angle_authority",
    "global_epsilon_authority",
)


def admission_failures(meta: Mapping[str, object]) -> list[str]:
    """Return exact reasons the axisymmetric quotient fast path is inadmissible."""
    failures: list[str] = []
    for key in REQUIRED_TRUE:
        if meta.get(key) is not True:
            failures.append(f"{key}:required_true")
    for key in REQUIRED_FALSE:
        if meta.get(key) is not False:
            failures.append(f"{key}:required_false")
    if meta.get("phase_domain") != "FULL_S1_FOR_EACH_MERIDIAN_STATE":
        failures.append("phase_domain:not_full_product")
    if meta.get("fallback_owner") != "MC-022":
        failures.append("fallback_owner:not_MC-022")
    if meta.get("material_representation") != "EXACT_AXISYMMETRIC_MERIDIAN":
        failures.append("material_representation:not_exact_axisymmetric_meridian")
    return failures


def admissible(meta: Mapping[str, object]) -> bool:
    return not admission_failures(meta)
