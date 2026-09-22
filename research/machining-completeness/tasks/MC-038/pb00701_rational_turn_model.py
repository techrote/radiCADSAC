#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from math import comb
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_event_model as base  # noqa: E402

EE = base.EE
q = base.q


class EndpointIsolationRefusal(RuntimeError):
    """Bounded resource refusal. Never a truth value."""


def _trim(poly):
    out = [q(value) for value in poly]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out or [Fraction(0)]


def _pscale(poly, scalar):
    scalar = q(scalar)
    return _trim([scalar * q(value) for value in poly])


def _fraction_floor(value: Fraction) -> int:
    return value.numerator // value.denominator


def _fraction_ceil(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def _principal_turn(turn: Fraction) -> Fraction:
    """Reduce tangent-periodic turn to (-1/2, 1/2], with +1/2 the pole."""
    turn = q(turn)
    reduced = turn - _fraction_floor(turn)
    if reduced > Fraction(1, 2):
        reduced -= 1
    return reduced


def _pole_in_closed_turn_interval(lo: Fraction, hi: Fraction) -> bool:
    # tan(pi * turn) has poles at turn = k + 1/2.
    first_k = _fraction_ceil(lo - Fraction(1, 2))
    last_k = _fraction_floor(hi - Fraction(1, 2))
    return first_k <= last_k


def tangent_polynomial(denominator: int):
    """Integer polynomial whose real roots are tan(k*pi/q).

    Im((1 + i*x)^q) = sum_{j odd} C(q,j) (-1)^((j-1)/2) x^j.
    """
    if isinstance(denominator, bool) or not isinstance(denominator, int) or denominator <= 0:
        raise TypeError("denominator must be a positive integer")
    poly = [Fraction(0)] * (denominator + 1)
    for degree in range(1, denominator + 1, 2):
        poly[degree] = Fraction(comb(denominator, degree) * (-1) ** ((degree - 1) // 2))
    return _trim(poly)


def _root_bound(poly) -> Fraction:
    poly = _trim(poly)
    if EE.degree(poly) <= 0:
        return Fraction(1)
    lead = abs(poly[-1])
    ratio = max((abs(value) / lead for value in poly[:-1]), default=Fraction(0))
    return Fraction(1 + _fraction_ceil(ratio))


def _root_at_rational(poly, value: Fraction) -> bool:
    return EE.peval(poly, value) == 0


def _isolate_positive_root(poly, root_rank: int, *, max_bisections: int = 512):
    if root_rank <= 0:
        raise ValueError("root rank must be positive")
    bound = _root_bound(poly)
    lo = Fraction(0)
    hi = bound
    total = EE.distinct_roots_open(poly, lo, hi)
    if root_rank > total:
        raise ValueError("requested tangent root does not exist")
    rank = root_rank
    for _ in range(max_bisections):
        mid = (lo + hi) / 2
        left = EE.distinct_roots_open(poly, lo, mid)
        if _root_at_rational(poly, mid):
            if rank == left + 1:
                return {"kind": "RATIONAL", "value": mid}
            if rank <= left:
                hi = mid
            else:
                lo = mid
                rank -= left + 1
            continue
        if rank <= left:
            hi = mid
        else:
            lo = mid
            rank -= left
        if EE.distinct_roots_open(poly, lo, hi) == 1:
            return {"kind": "ALGEBRAIC", "lo": lo, "hi": hi}
    raise EndpointIsolationRefusal("RATIONAL_TURN_ENDPOINT_ISOLATION_BUDGET_EXHAUSTED")


def rational_turn_endpoint(turn, *, max_bisections: int = 512):
    """Exact algebraic representation of tan(pi*turn) for a finite rational turn."""
    original = q(turn)
    principal = _principal_turn(original)
    if principal == Fraction(1, 2):
        raise ValueError("TAN_HALF_POLE")
    if principal == 0:
        return {
            "kind": "RATIONAL",
            "turn": original,
            "principal_turn": principal,
            "value": Fraction(0),
        }
    if principal == Fraction(1, 4):
        return {
            "kind": "RATIONAL",
            "turn": original,
            "principal_turn": principal,
            "value": Fraction(1),
        }
    if principal == Fraction(-1, 4):
        return {
            "kind": "RATIONAL",
            "turn": original,
            "principal_turn": principal,
            "value": Fraction(-1),
        }

    denominator = principal.denominator
    numerator = principal.numerator
    poly = tangent_polynomial(denominator)
    isolated = _isolate_positive_root(poly, abs(numerator), max_bisections=max_bisections)
    if isolated["kind"] == "RATIONAL":
        value = isolated["value"] if numerator > 0 else -isolated["value"]
        return {
            "kind": "RATIONAL",
            "turn": original,
            "principal_turn": principal,
            "value": value,
        }
    lo, hi = isolated["lo"], isolated["hi"]
    if numerator < 0:
        lo, hi = -hi, -lo
    return {
        "kind": "ALGEBRAIC_TAN_RATIONAL_TURN",
        "turn": original,
        "principal_turn": principal,
        "defining_polynomial": poly,
        "lo": lo,
        "hi": hi,
        "root_rank_abs": abs(numerator),
        "denominator": denominator,
    }


def _refine_endpoint(endpoint):
    if endpoint["kind"] == "RATIONAL":
        return endpoint
    poly = endpoint["defining_polynomial"]
    lo, hi = endpoint["lo"], endpoint["hi"]
    mid = (lo + hi) / 2
    if _root_at_rational(poly, mid):
        refined = dict(endpoint)
        refined.clear()
        refined.update({
            "kind": "RATIONAL",
            "turn": endpoint["turn"],
            "principal_turn": endpoint["principal_turn"],
            "value": mid,
        })
        return refined
    left = EE.distinct_roots_open(poly, lo, mid)
    refined = dict(endpoint)
    if left == 1:
        refined["hi"] = mid
    elif left == 0:
        refined["lo"] = mid
    else:
        raise AssertionError("endpoint interval ceased to isolate one root")
    return refined


def _sign_at_endpoint(poly, endpoint, *, max_refinements: int = 1024):
    poly = _trim(poly)
    if endpoint["kind"] == "RATIONAL":
        return EE.sign(EE.peval(poly, endpoint["value"])), endpoint
    defining = endpoint["defining_polynomial"]
    common = EE.pgcd(poly, defining)
    if EE.degree(common) > 0 and EE.distinct_roots_open(common, endpoint["lo"], endpoint["hi"]) == 1:
        return 0, endpoint
    current = endpoint
    for _ in range(max_refinements):
        left_value = EE.peval(poly, current["lo"])
        right_value = EE.peval(poly, current["hi"])
        if left_value and right_value and EE.sign(left_value) == EE.sign(right_value):
            if EE.distinct_roots_open(poly, current["lo"], current["hi"]) == 0:
                return EE.sign(left_value), current
        current = _refine_endpoint(current)
        if current["kind"] == "RATIONAL":
            return EE.sign(EE.peval(poly, current["value"])), current
    raise EndpointIsolationRefusal("ALGEBRAIC_ENDPOINT_SIGN_BUDGET_EXHAUSTED")


def _event_at_endpoint(poly, endpoint):
    poly = _trim(poly)
    if endpoint["kind"] == "RATIONAL":
        return base._event_summary(EE.exact_event(poly, endpoint["value"]))
    current = endpoint
    sign, current = _sign_at_endpoint(poly, current)
    if sign:
        return {
            "status": "DECIDED",
            "relation": "POSITIVE" if sign > 0 else "NEGATIVE",
            "multiplicity": 0,
        }
    multiplicity = 0
    derivative = poly
    while derivative != [0]:
        derivative = EE.deriv(derivative)
        multiplicity += 1
        derivative_sign, current = _sign_at_endpoint(derivative, current)
        if derivative_sign:
            return {
                "status": "DECIDED",
                "relation": "ZERO",
                "multiplicity": multiplicity,
                "singular": multiplicity > 1,
                "event_kind": (
                    "SIMPLE_CROSSING" if multiplicity == 1
                    else "MULTIPLE_CROSSING" if multiplicity % 2
                    else "MULTIPLE_TANGENCY"
                ),
                "sign_change": bool(multiplicity % 2),
            }
    return {"status": "BLOCKED", "reason": "DEGENERATE_IDENTITY_ZERO", "blocker": "PB-007-01"}


def _one_sided_sign_at_endpoint(poly, endpoint, side: str):
    if side not in {"left", "right"}:
        raise ValueError("side must be left or right")
    current = endpoint
    derivative = _trim(poly)
    order = 0
    while derivative != [0]:
        endpoint_sign, current = _sign_at_endpoint(derivative, current)
        if endpoint_sign:
            return endpoint_sign if side == "right" or order % 2 == 0 else -endpoint_sign
        derivative = EE.deriv(derivative)
        order += 1
    return 0


def _variations(signs):
    nonzero = [value for value in signs if value]
    return sum(left != right for left, right in zip(nonzero, nonzero[1:]))


def _distinct_roots_open(poly, left_endpoint, right_endpoint):
    sequence = EE.sturm_sequence(poly)
    left_variations = _variations([
        _one_sided_sign_at_endpoint(item, left_endpoint, "right") for item in sequence
    ])
    right_variations = _variations([
        _one_sided_sign_at_endpoint(item, right_endpoint, "left") for item in sequence
    ])
    return left_variations - right_variations


def _endpoint_description(endpoint):
    description = {
        "kind": endpoint["kind"],
        "turn": str(endpoint["turn"]),
        "principal_turn": str(endpoint["principal_turn"]),
    }
    if endpoint["kind"] == "RATIONAL":
        description["tan_half"] = str(endpoint["value"])
    else:
        description.update({
            "defining_polynomial": [str(value) for value in endpoint["defining_polynomial"]],
            "isolating_interval": [str(endpoint["lo"]), str(endpoint["hi"])],
            "root_rank_abs": endpoint["root_rank_abs"],
            "denominator": endpoint["denominator"],
        })
    return description


def analyze_rational_turn_window(
    *,
    cos_coefficients=None,
    sin_coefficients=None,
    turn_lo,
    turn_hi,
    source_parameter_id,
    parameter_projection=None,
    witness_turn=None,
):
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
        left_endpoint = rational_turn_endpoint(lo)
        right_endpoint = rational_turn_endpoint(hi)
        reduction = base.trig_polynomial_to_tan_half(cos_coefficients, sin_coefficients)
    except EndpointIsolationRefusal as exc:
        return {"status": "RESOURCE_REFUSAL", "reason": str(exc), "is_truth_value": False}
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        return {"status": "SEMANTIC_BLOCKER", "reason": "INVALID_EXACT_ANALYTIC_EVENT_SPEC", "detail": str(exc)}

    numerator = reduction["numerator"]
    if numerator == [0]:
        return {
            "status": "BLOCKED",
            "reason": "TRIGONOMETRIC_IDENTITY_ZERO_REQUIRES_SEPARATE_SEMANTIC_HANDLING",
            "blocker": "PB-007-01",
        }
    try:
        distinct_open = _distinct_roots_open(numerator, left_endpoint, right_endpoint)
        repeated_factor = EE.pgcd(numerator, EE.deriv(numerator))
        multiple_open = 0 if EE.degree(repeated_factor) <= 0 else _distinct_roots_open(
            repeated_factor, left_endpoint, right_endpoint
        )
        result = {
            "status": "CERTIFIED",
            "relation": "EXACT_TRIGONOMETRIC_ROOT_COUNT_RATIONAL_TURN",
            "source_parameter_id": source_parameter_id,
            "turn_interval": [str(lo), str(hi)],
            "left_endpoint": _endpoint_description(left_endpoint),
            "right_endpoint": _endpoint_description(right_endpoint),
            "left_event": _event_at_endpoint(numerator, left_endpoint),
            "right_event": _event_at_endpoint(numerator, right_endpoint),
            "numerator_coefficients": [str(value) for value in numerator],
            "denominator_power": reduction["denominator_power"],
            "distinct_roots_open": distinct_open,
            "multiple_roots_open": multiple_open,
            "all_open_roots_simple": multiple_open == 0,
        }
        if witness_turn is not None:
            witness = q(witness_turn)
            if not lo <= witness <= hi:
                return {"status": "SEMANTIC_BLOCKER", "reason": "EVENT_WITNESS_OUTSIDE_SOURCE_WINDOW"}
            witness_endpoint = rational_turn_endpoint(witness)
            result["witness_turn"] = str(witness)
            result["witness_endpoint"] = _endpoint_description(witness_endpoint)
            result["witness_event"] = _event_at_endpoint(numerator, witness_endpoint)
        return result
    except EndpointIsolationRefusal as exc:
        return {"status": "RESOURCE_REFUSAL", "reason": str(exc), "is_truth_value": False}


def classify_required_analytic_event(spec):
    if not isinstance(spec, dict):
        return {"status": "UNCERTIFIED", "reason": "MISSING_ANALYTIC_EVENT_SPEC"}
    grammar = spec.get("grammar")
    if grammar == "RATIONAL_TRIG_POLYNOMIAL_RATIONAL_TURN_WINDOW":
        allowed = {
            "grammar", "cos_coefficients", "sin_coefficients", "turn_lo", "turn_hi",
            "source_parameter_id", "parameter_projection", "witness_turn",
        }
        if set(spec) - allowed:
            return {"status": "SEMANTIC_BLOCKER", "reason": "UNREVIEWED_EVENT_AUTHORITY_FIELD"}
        return analyze_rational_turn_window(
            cos_coefficients=spec.get("cos_coefficients"),
            sin_coefficients=spec.get("sin_coefficients"),
            turn_lo=spec.get("turn_lo"),
            turn_hi=spec.get("turn_hi"),
            source_parameter_id=spec.get("source_parameter_id"),
            parameter_projection=spec.get("parameter_projection"),
            witness_turn=spec.get("witness_turn"),
        )
    if grammar == "RATIONAL_TRIG_POLYNOMIAL_CARDINAL_WINDOW":
        return base.classify_required_analytic_event(spec)
    if grammar in {
        "POLYNOMIAL_MODULATED_TRIGONOMETRIC",
        "GENERAL_COUPLED_EXPONENTIAL_POLYNOMIAL",
        "GENERAL_TANGENTIAL_MULTIPLE_SINGULAR_TRANSCENDENTAL",
    }:
        return {
            "status": "BLOCKED",
            "reason": "FULL_REQUIRED_ANALYTIC_DECISION_ROUTE_NOT_ESTABLISHED",
            "blocker": "PB-007-01",
        }
    return {"status": "BLOCKED", "reason": "UNSUPPORTED_ANALYTIC_GRAMMAR", "blocker": "PB-007-01"}


def resource_refusal(reason="PB00701_RATIONAL_TURN_BUDGET_EXHAUSTED"):
    return {"status": "RESOURCE_REFUSAL", "reason": reason, "is_truth_value": False}
