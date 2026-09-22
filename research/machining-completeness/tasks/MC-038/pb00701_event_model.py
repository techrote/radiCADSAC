#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
import importlib.util
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
EVENT_ENGINE_PATH = HERE.parent / "MC-032" / "event_engine.py"


def _load_event_engine():
    spec = importlib.util.spec_from_file_location("radicadsac_mc032_event_engine", EVENT_ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load MC-032 event engine")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EE = _load_event_engine()


def q(value) -> Fraction:
    """Exact rational parser. Binary float/bool are never predicate authority."""
    return EE.q(value)


def _trim(poly):
    out = [q(x) for x in poly]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out or [Fraction(0)]


def _padd(a, b):
    out = [Fraction(0)] * max(len(a), len(b))
    for i, value in enumerate(a):
        out[i] += q(value)
    for i, value in enumerate(b):
        out[i] += q(value)
    return _trim(out)


def _pscale(a, scalar):
    scalar = q(scalar)
    return _trim([scalar * q(value) for value in a])


def _psub(a, b):
    return _padd(a, _pscale(b, -1))


def _pmul(a, b):
    a = _trim(a)
    b = _trim(b)
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, left in enumerate(a):
        for j, right in enumerate(b):
            out[i + j] += left * right
    return _trim(out)


def _ppow(poly, exponent: int):
    if isinstance(exponent, bool) or not isinstance(exponent, int) or exponent < 0:
        raise TypeError("polynomial exponent must be a non-negative integer")
    result = [Fraction(1)]
    base = _trim(poly)
    n = exponent
    while n:
        if n & 1:
            result = _pmul(result, base)
        base = _pmul(base, base)
        n //= 2
    return result


def _normalise_coefficients(values, name):
    if values is None:
        return {}
    if not isinstance(values, dict):
        raise TypeError(f"{name} must be a harmonic->rational mapping")
    out = {}
    for raw_harmonic, raw_value in values.items():
        if isinstance(raw_harmonic, bool):
            raise TypeError("harmonic index must not be bool")
        try:
            harmonic = int(raw_harmonic)
        except (TypeError, ValueError) as exc:
            raise TypeError("harmonic index must be an integer") from exc
        if str(harmonic) != str(raw_harmonic) and not isinstance(raw_harmonic, int):
            raise TypeError("harmonic index must have canonical integer encoding")
        if harmonic < 0:
            raise ValueError("negative harmonics are represented by real cos/sin coefficients, not separate indices")
        value = q(raw_value)
        if value:
            out[harmonic] = value
    if 0 in out and name == "sin_coefficients":
        raise ValueError("sin(0*theta) coefficient must be zero")
    return out


def trig_polynomial_to_tan_half(cos_coefficients=None, sin_coefficients=None):
    """Reduce a rational trigonometric polynomial to a rational polynomial numerator.

    For x = tan(theta/2):
      cos(theta) = (1-x^2)/(1+x^2)
      sin(theta) = 2x/(1+x^2)

    A finite real trigonometric polynomial with rational coefficients therefore becomes
    P(x)/(1+x^2)^n.  The denominator is strictly positive for real finite x, so
    real root multiplicity and sign are exactly those of P.
    """
    cos_coefficients = _normalise_coefficients(cos_coefficients, "cos_coefficients")
    sin_coefficients = _normalise_coefficients(sin_coefficients, "sin_coefficients")
    harmonics = set(cos_coefficients) | set(sin_coefficients)
    degree = max(harmonics or {0})

    denominator_base = [Fraction(1), Fraction(0), Fraction(1)]
    cos_base = [Fraction(1), Fraction(0), Fraction(-1)]
    sin_base = [Fraction(0), Fraction(2)]

    cos_num = [[Fraction(1)]]
    sin_num = [[Fraction(0)]]
    for _ in range(degree):
        previous_cos = cos_num[-1]
        previous_sin = sin_num[-1]
        cos_num.append(_psub(_pmul(previous_cos, cos_base), _pmul(previous_sin, sin_base)))
        sin_num.append(_padd(_pmul(previous_sin, cos_base), _pmul(previous_cos, sin_base)))

    numerator = [Fraction(0)]
    for harmonic in range(degree + 1):
        lift = _ppow(denominator_base, degree - harmonic)
        if harmonic in cos_coefficients:
            numerator = _padd(
                numerator,
                _pscale(_pmul(cos_num[harmonic], lift), cos_coefficients[harmonic]),
            )
        if harmonic in sin_coefficients:
            numerator = _padd(
                numerator,
                _pscale(_pmul(sin_num[harmonic], lift), sin_coefficients[harmonic]),
            )

    return {
        "numerator": _trim(numerator),
        "denominator_power": degree,
    }


def _fraction_floor(value: Fraction) -> int:
    return value.numerator // value.denominator


def _fraction_ceil(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def _pole_in_closed_turn_interval(lo: Fraction, hi: Fraction) -> bool:
    # tan(pi * turn) has poles at turn = k + 1/2.
    first_k = _fraction_ceil(lo - Fraction(1, 2))
    last_k = _fraction_floor(hi - Fraction(1, 2))
    return first_k <= last_k


def _cardinal_tan_half(turn: Fraction):
    # theta = 2*pi*turn, hence tan(theta/2) = tan(pi*turn).
    turn = q(turn)
    unit = turn - _fraction_floor(turn)
    if unit == 0:
        return Fraction(0)
    if unit == Fraction(1, 4):
        return Fraction(1)
    if unit == Fraction(1, 2):
        return None
    if unit == Fraction(3, 4):
        return Fraction(-1)
    raise ValueError("turn endpoint is not a cardinal quarter-turn")


def _event_summary(event):
    return {
        key: event[key]
        for key in ("status", "relation", "multiplicity", "singular", "event_kind", "sign_change")
        if key in event
    }


def analyze_cardinal_window(
    *,
    cos_coefficients=None,
    sin_coefficients=None,
    turn_lo,
    turn_hi,
    source_parameter_id,
    parameter_projection=None,
    witness_half_tan=None,
):
    """Exact bounded subroute for a source-bound cardinal-turn window.

    This is intentionally not a general MC-003 analytic-event solver.  The source
    interval endpoints must be quarter-turn values whose tan-half coordinates are
    rational, and the interval must not cross a tan-half pole.  Unsupported source
    windows fail closed as PB-007-01 rather than being approximated.
    """
    if not source_parameter_id or not isinstance(source_parameter_id, str):
        return {"status": "SEMANTIC_BLOCKER", "reason": "MISSING_SHARED_SOURCE_PARAMETER"}
    if parameter_projection not in (None, source_parameter_id):
        return {"status": "SEMANTIC_BLOCKER", "reason": "INDEPENDENT_PARAMETER_PROJECTION_FORBIDDEN"}

    try:
        lo = q(turn_lo)
        hi = q(turn_hi)
    except (TypeError, ValueError, ZeroDivisionError):
        return {"status": "SEMANTIC_BLOCKER", "reason": "NONEXACT_TURN_ENDPOINT"}
    if not lo < hi:
        return {"status": "SEMANTIC_BLOCKER", "reason": "INVERTED_OR_EMPTY_TURN_INTERVAL"}
    if _pole_in_closed_turn_interval(lo, hi):
        return {
            "status": "BLOCKED",
            "reason": "TAN_HALF_POLE_REQUIRES_EXACT_WINDOW_PARTITION",
            "blocker": "PB-007-01",
        }
    try:
        x_lo = _cardinal_tan_half(lo)
        x_hi = _cardinal_tan_half(hi)
    except ValueError:
        return {
            "status": "BLOCKED",
            "reason": "NONCARDINAL_EXACT_ENDPOINT_NOT_COVERED_BY_BOUNDED_SUBROUTE",
            "blocker": "PB-007-01",
        }
    if x_lo is None or x_hi is None:
        return {
            "status": "BLOCKED",
            "reason": "TAN_HALF_POLE_REQUIRES_EXACT_WINDOW_PARTITION",
            "blocker": "PB-007-01",
        }
    if not x_lo < x_hi:
        return {
            "status": "SEMANTIC_BLOCKER",
            "reason": "CARDINAL_WINDOW_NOT_MONOTONE_IN_TAN_HALF_COORDINATE",
        }

    try:
        reduction = trig_polynomial_to_tan_half(cos_coefficients, sin_coefficients)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        return {
            "status": "SEMANTIC_BLOCKER",
            "reason": "INVALID_EXACT_TRIGONOMETRIC_POLYNOMIAL",
            "detail": str(exc),
        }
    numerator = reduction["numerator"]
    if numerator == [0]:
        return {
            "status": "BLOCKED",
            "reason": "TRIGONOMETRIC_IDENTITY_ZERO_REQUIRES_SEPARATE_SEMANTIC_HANDLING",
            "blocker": "PB-007-01",
        }

    left = EE.exact_event(numerator, x_lo)
    right = EE.exact_event(numerator, x_hi)
    distinct_open = EE.distinct_roots_open(numerator, x_lo, x_hi)
    repeated_factor = EE.pgcd(numerator, EE.deriv(numerator))
    multiple_open = 0 if EE.degree(repeated_factor) <= 0 else EE.distinct_roots_open(repeated_factor, x_lo, x_hi)

    result = {
        "status": "CERTIFIED",
        "relation": "EXACT_TRIGONOMETRIC_ROOT_COUNT",
        "source_parameter_id": source_parameter_id,
        "turn_interval": [str(lo), str(hi)],
        "tan_half_interval": [str(x_lo), str(x_hi)],
        "numerator_coefficients": [str(value) for value in numerator],
        "denominator_power": reduction["denominator_power"],
        "left_endpoint": _event_summary(left),
        "right_endpoint": _event_summary(right),
        "distinct_roots_open": distinct_open,
        "multiple_roots_open": multiple_open,
        "all_open_roots_simple": multiple_open == 0,
    }

    if witness_half_tan is not None:
        try:
            witness = q(witness_half_tan)
        except (TypeError, ValueError, ZeroDivisionError):
            return {"status": "SEMANTIC_BLOCKER", "reason": "NONEXACT_EVENT_WITNESS"}
        if not x_lo <= witness <= x_hi:
            return {"status": "SEMANTIC_BLOCKER", "reason": "EVENT_WITNESS_OUTSIDE_SOURCE_WINDOW"}
        result["witness_half_tan"] = str(witness)
        result["witness_event"] = _event_summary(EE.exact_event(numerator, witness))

    return result


def classify_required_analytic_event(spec):
    """Prospective dispatch boundary for PB-007-01 follow-up evidence."""
    if not isinstance(spec, dict):
        return {"status": "UNCERTIFIED", "reason": "MISSING_ANALYTIC_EVENT_SPEC"}
    grammar = spec.get("grammar")
    if grammar == "RATIONAL_TRIG_POLYNOMIAL_CARDINAL_WINDOW":
        allowed = {
            "grammar", "cos_coefficients", "sin_coefficients", "turn_lo", "turn_hi",
            "source_parameter_id", "parameter_projection", "witness_half_tan",
        }
        unknown = set(spec) - allowed
        if unknown:
            return {"status": "SEMANTIC_BLOCKER", "reason": "UNREVIEWED_EVENT_AUTHORITY_FIELD"}
        return analyze_cardinal_window(
            cos_coefficients=spec.get("cos_coefficients"),
            sin_coefficients=spec.get("sin_coefficients"),
            turn_lo=spec.get("turn_lo"),
            turn_hi=spec.get("turn_hi"),
            source_parameter_id=spec.get("source_parameter_id"),
            parameter_projection=spec.get("parameter_projection"),
            witness_half_tan=spec.get("witness_half_tan"),
        )
    if grammar in {
        "NONCARDINAL_RATIONAL_TURN_WINDOW",
        "POLYNOMIAL_MODULATED_TRIGONOMETRIC",
        "GENERAL_COUPLED_EXPONENTIAL_POLYNOMIAL",
        "GENERAL_TANGENTIAL_MULTIPLE_SINGULAR_TRANSCENDENTAL",
    }:
        return {
            "status": "BLOCKED",
            "reason": "FULL_REQUIRED_ANALYTIC_DECISION_ROUTE_NOT_ESTABLISHED",
            "blocker": "PB-007-01",
        }
    return {
        "status": "BLOCKED",
        "reason": "UNSUPPORTED_ANALYTIC_GRAMMAR",
        "blocker": "PB-007-01",
    }


def resource_refusal(reason="PB00701_EVENT_BUDGET_EXHAUSTED"):
    return {"status": "RESOURCE_REFUSAL", "reason": reason, "is_truth_value": False}
