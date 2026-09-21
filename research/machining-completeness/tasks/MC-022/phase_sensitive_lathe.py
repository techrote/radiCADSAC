#!/usr/bin/env python3
"""Exact-rational bounded phase-sensitive lathe model for MC-022.

This is deterministic research/model evidence. It constructs finite symbolic
timed sweeps while preserving one shared time/path/spindle-phase chronology.
It deliberately fails closed for general transcendental event queries owned by
PB-007-01/PB-007-02 rather than replacing them with angle sampling or epsilon.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

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
    raise TypeError(f"unsupported exact value: {type(value).__name__}")


def floor_q(x: Fraction) -> int:
    return x.numerator // x.denominator


def ceil_q(x: Fraction) -> int:
    return -floor_q(-x)


def normalize_turn(x: int | str | Fraction) -> Fraction:
    p = q(x)
    return p - floor_q(p)


@dataclass(frozen=True)
class TimedState:
    t: Fraction
    r: Fraction
    z: Fraction
    phase_turns_unwrapped: Fraction


@dataclass(frozen=True)
class TimedSegment:
    """Affine exact source law over one closed semantic time interval."""

    t0: Fraction
    t1: Fraction
    r0: Fraction
    r1: Fraction
    z0: Fraction
    z1: Fraction
    phase0: Fraction
    phase1: Fraction

    def __post_init__(self) -> None:
        vals = (self.t0,self.t1,self.r0,self.r1,self.z0,self.z1,self.phase0,self.phase1)
        if any(not isinstance(v, Fraction) for v in vals):
            raise TypeError("TimedSegment fields must be Fraction")
        if not self.t0 < self.t1:
            raise ValueError("semantic time interval must have positive duration")

    def sample(self, t: int | str | Fraction) -> TimedState:
        tt = q(t)
        if not self.t0 <= tt <= self.t1:
            raise ValueError("sample outside closed source interval")
        u = (tt - self.t0) / (self.t1 - self.t0)
        return TimedState(
            tt,
            self.r0 + u * (self.r1 - self.r0),
            self.z0 + u * (self.z1 - self.z0),
            self.phase0 + u * (self.phase1 - self.phase0),
        )

    def lead_per_turn(self) -> Fraction:
        dphase = self.phase1 - self.phase0
        if dphase == 0:
            raise ValueError("zero spindle phase advance")
        return (self.z1 - self.z0) / dphase

    def phase_at(self, t: int | str | Fraction) -> Fraction:
        return self.sample(t).phase_turns_unwrapped


@dataclass(frozen=True)
class TimedProgram:
    """Finite ordered composition preserving every semantic boundary."""

    segments: tuple[TimedSegment, ...]

    def __post_init__(self) -> None:
        if not self.segments:
            raise ValueError("program requires at least one timed segment")
        for a, b in zip(self.segments, self.segments[1:]):
            if a.t1 > b.t0:
                raise ValueError("source segments may not overlap in time")

    def sample(self, t: int | str | Fraction) -> TimedState:
        tt = q(t)
        matches = [s for s in self.segments if s.t0 <= tt <= s.t1]
        if not matches:
            raise ValueError("time not covered by source program")
        if len(matches) == 2:
            left, right = matches
            a, b = left.sample(tt), right.sample(tt)
            if (a.r,a.z,a.phase_turns_unwrapped) != (b.r,b.z,b.phase_turns_unwrapped):
                raise ValueError("discontinuous shared semantic boundary")
            return a
        return matches[0].sample(tt)


def alignment_times(segment: TimedSegment, body_theta_turns: int | str | Fraction) -> tuple[Fraction, ...]:
    """Exact isolated times where a body-fixed azimuth meets machine angle zero.

    Alignment requires phase(t) + body_theta to be an integer number of turns.
    The unwrapped phase interval is retained, so a nonzero affine phase advance
    yields a finite ordered set of exact times rather than modulo-phase chronology
    loss. A continuously aligned zero-advance interval is rejected here instead
    of being misrepresented by its endpoints; downstream interval handling must
    preserve the whole source interval.
    """
    theta = q(body_theta_turns)
    dp = segment.phase1 - segment.phase0
    if dp == 0:
        if normalize_turn(segment.phase0 + theta) != 0:
            return ()
        raise ValueError("stationary aligned phase is an interval, not isolated alignment times")
    lo, hi = sorted((segment.phase0, segment.phase1))
    n0 = ceil_q(lo + theta)
    n1 = floor_q(hi + theta)
    out = []
    for n in range(n0, n1 + 1):
        target_phase = Fraction(n, 1) - theta
        u = (target_phase - segment.phase0) / dp
        if 0 <= u <= 1:
            out.append(segment.t0 + u * (segment.t1 - segment.t0))
    return tuple(sorted(set(out)))


def synchronized_band_removes(
    segment: TimedSegment,
    body_theta_turns: int | str | Fraction,
    z: int | str | Fraction,
    radius: int | str | Fraction,
    axial_half_width: int | str | Fraction,
    final_radius: int | str | Fraction,
) -> bool:
    """Exact bounded phase/feed-correlated radial-turning membership control.

    The point can be removed only at an actual common source time at which its
    body-fixed azimuth aligns with the machine tool. Feed position is evaluated
    at that same time; independent phase×feed coverage is impossible.
    """
    zz, rr = q(z), q(radius)
    width, fr = q(axial_half_width), q(final_radius)
    if width < 0 or fr < 0:
        raise ValueError("negative cutter width/radius")
    if rr <= fr:
        return False
    for t in alignment_times(segment, body_theta_turns):
        if abs(zz - segment.sample(t).z) <= width:
            return True
    return False


_CARDINAL = {
    Fraction(0): lambda x,y: (x,y),
    Fraction(1,4): lambda x,y: (-y,x),
    Fraction(1,2): lambda x,y: (-x,-y),
    Fraction(3,4): lambda x,y: (y,-x),
}


def rotate_xy_cardinal(x: int | str | Fraction, y: int | str | Fraction, phase_turns: int | str | Fraction) -> tuple[Fraction,Fraction]:
    """Exact control rotation for quarter-turn phases only.

    General phase remains symbolic; decimal trig evaluation is not predicate
    authority for the programme.
    """
    p = normalize_turn(phase_turns)
    fn = _CARDINAL.get(p)
    if fn is None:
        raise ValueError("non-cardinal phase requires symbolic/certified analytic route")
    return fn(q(x), q(y))


@dataclass(frozen=True)
class EccentricLaw:
    base_x: Fraction
    base_y: Fraction
    offset_x: Fraction
    offset_y: Fraction
    timed: TimedSegment

    def symbolic_center(self, t: int | str | Fraction) -> dict[str, object]:
        s = self.timed.sample(t)
        return {
            "base_x": self.base_x,
            "base_y": self.base_y,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
            "phase_turns_unwrapped": s.phase_turns_unwrapped,
            "semantics": "base + R(2*pi*phase)*offset",
        }

    def cardinal_center(self, t: int | str | Fraction) -> tuple[Fraction,Fraction]:
        s = self.timed.sample(t)
        dx, dy = rotate_xy_cardinal(self.offset_x, self.offset_y, s.phase_turns_unwrapped)
        return self.base_x + dx, self.base_y + dy


def classify_certified_event(
    value_lo: int | str | Fraction,
    value_hi: int | str | Fraction,
    deriv_lo: int | str | Fraction,
    deriv_hi: int | str | Fraction,
) -> str:
    """Finite MC-007 fail-closed event classifier for one certified leaf."""
    vlo, vhi, dlo, dhi = map(q, (value_lo,value_hi,deriv_lo,deriv_hi))
    if vlo > vhi or dlo > dhi:
        raise ValueError("invalid directed interval")
    if vhi < 0 or vlo > 0:
        return "SEPARATED"
    if dhi < 0 or dlo > 0:
        return "TRANSVERSAL"
    return "TRANSCENDENTAL_EVENT_BLOCKER"


def actual_sweep_error_bound(
    inherited: int | str | Fraction,
    translation: int | str | Fraction,
    support_radius: int | str | Fraction,
    rotation_radians: int | str | Fraction,
    tool: int | str | Fraction,
) -> Fraction:
    """MC-058 conservative finite-cutter sweep transfer, exact rational bound."""
    ei, et, rho, er, e_tool = map(q,(inherited,translation,support_radius,rotation_radians,tool))
    if min(ei,et,rho,er,e_tool) < 0:
        raise ValueError("error/support bounds must be non-negative")
    return ei + et + rho * er + e_tool
