#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_common_factor_model as v8  # noqa: E402

v7 = v8.v7
v6 = v8.v6
EE = v8.EE
q = v8.q

MAX_RATIO_CHARTS = 4096


class MonotoneRatioRefusal(RuntimeError):
    """Bounded resource refusal. Never a truth value."""


def _trim(poly):
    return v8._trim(poly)


def _psub(a, b):
    return v7._padd(a, v7._pscale(b, -1))


def _fraction_floor(value: Fraction) -> int:
    return value.numerator // value.denominator


def _fraction_ceil(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def _is_tangent_pole(turn) -> bool:
    turn = q(turn)
    twice = 2 * turn
    return twice.denominator == 1 and twice.numerator % 2 != 0


def _pole_index(turn) -> int:
    turn = q(turn)
    if not _is_tangent_pole(turn):
        raise ValueError("turn is not a tangent pole")
    value = turn - Fraction(1, 2)
    if value.denominator != 1:
        raise AssertionError("pole index lost integer identity")
    return value.numerator


def _phase_pole_boundaries(u_offset, u_rate):
    u_offset = q(u_offset)
    u_rate = q(u_rate)
    if u_rate == 0:
        raise ValueError("monotone-ratio route requires nonzero harmonic phase rate")
    u_end = u_offset + u_rate
    lo = min(u_offset, u_end)
    hi = max(u_offset, u_end)
    first_n = _fraction_ceil(lo - Fraction(1, 2))
    last_n = _fraction_floor(hi - Fraction(1, 2))
    pole_count = max(0, last_n - first_n + 1)
    if pole_count > MAX_RATIO_CHARTS:
        raise MonotoneRatioRefusal("PB00701_V9_RATIO_CHART_BUDGET_EXHAUSTED")
    boundaries = {Fraction(0), Fraction(1)}
    for n in range(first_n, last_n + 1):
        pole = Fraction(n, 1) + Fraction(1, 2)
        source = (pole - u_offset) / u_rate
        if 0 < source < 1:
            boundaries.add(source)
    ordered = sorted(boundaries)
    if len(ordered) - 1 > MAX_RATIO_CHARTS:
        raise MonotoneRatioRefusal("PB00701_V9_RATIO_CHART_BUDGET_EXHAUSTED")
    return ordered


def _poly_zero_free_closed(poly):
    poly = _trim(poly)
    if poly == [0]:
        return None
    left = EE.peval(poly, Fraction(0))
    right = EE.peval(poly, Fraction(1))
    if left == 0 or right == 0:
        return None
    roots_open = EE.distinct_roots_open(poly, Fraction(0), Fraction(1))
    if roots_open:
        return None
    middle = EE.peval(poly, Fraction(1, 2))
    sign = EE.sign(middle)
    if not sign:
        raise AssertionError("zero-free polynomial vanished at exact midpoint")
    return {
        "method": "MC032_EXACT_STURM_CLOSED_NONVANISHING",
        "left_value": str(left),
        "right_value": str(right),
        "distinct_roots_open": 0,
        "sign": "POSITIVE" if sign > 0 else "NEGATIVE",
    }


def _ratio_derivative_numerator(a_poly, b_poly):
    # r=-A/B, so r'=(A*B' - A'*B)/B^2.
    return _trim(_psub(
        v7._pmul(a_poly, EE.deriv(b_poly)),
        v7._pmul(EE.deriv(a_poly), b_poly),
    ))


def _monotonicity_certificate(a_poly, b_poly, u_rate):
    numerator = _ratio_derivative_numerator(a_poly, b_poly)
    desired = -1 if q(u_rate) > 0 else 1
    if numerator == [0]:
        return {
            "status": "CERTIFIED",
            "method": "EXACT_RATIONAL_POLYNOMIAL_IDENTITY",
            "ratio_derivative_numerator": ["0"],
            "ratio_direction": "CONSTANT",
            "harmonic_phase_direction": "INCREASING" if desired < 0 else "DECREASING",
            "strict_H_direction": "INCREASING" if desired < 0 else "DECREASING",
        }
    roots_open = EE.distinct_roots_open(numerator, Fraction(0), Fraction(1))
    if roots_open:
        return None
    sample = EE.peval(numerator, Fraction(1, 2))
    sign = EE.sign(sample)
    if sign != desired:
        return None
    return {
        "status": "CERTIFIED",
        "method": "MC032_EXACT_STURM_SIGN_WITH_NO_OPEN_ROOTS",
        "ratio_derivative_numerator": [str(value) for value in numerator],
        "distinct_roots_open": 0,
        "sample_source": "1/2",
        "sample_value": str(sample),
        "ratio_direction": "STRICTLY_DECREASING" if sign < 0 else "STRICTLY_INCREASING",
        "harmonic_phase_direction": "INCREASING" if q(u_rate) > 0 else "DECREASING",
        "strict_H_direction": "INCREASING" if q(u_rate) > 0 else "DECREASING",
    }


def _finite_comparison(a_poly, b_poly, u_offset, u_rate, source):
    source = q(source)
    a_value = EE.peval(a_poly, source)
    b_value = EE.peval(b_poly, source)
    if b_value == 0:
        raise AssertionError("certified zero-free ratio denominator vanished")
    ratio = -a_value / b_value
    turn = q(u_offset) + q(u_rate) * source
    if _is_tangent_pole(turn):
        raise ValueError("finite comparison requested at tangent pole")
    endpoint = v6.rational_turn_endpoint(turn)
    event = v6._event_at_endpoint([ -ratio, Fraction(1) ], endpoint)
    relation = event.get("relation")
    if relation == "POSITIVE":
        sign = 1
    elif relation == "NEGATIVE":
        sign = -1
    elif relation == "ZERO":
        sign = 0
    else:
        return {
            "status": "BLOCKED",
            "reason": "RATIONAL_TURN_ENDPOINT_COMPARISON_NOT_DECIDED",
            "delegate": event,
        }
    return {
        "status": "DECIDED",
        "kind": "FINITE_EXACT_RATIONAL_TURN_COMPARISON",
        "source": str(source),
        "harmonic_tangent_turn": str(turn),
        "ratio": str(ratio),
        "relation": relation,
        "sign": sign,
        "endpoint_kind": endpoint["kind"],
        "comparison_polynomial": [str(-ratio), "1"],
    }


def _pole_boundary(a_poly, b_poly, u_offset, u_rate, source, side):
    source = q(source)
    turn = q(u_offset) + q(u_rate) * source
    if not _is_tangent_pole(turn):
        raise ValueError("pole boundary requested at finite tangent turn")
    rate_sign = 1 if q(u_rate) > 0 else -1
    h_sign = -rate_sign if side == "left" else rate_sign
    b_value = EE.peval(b_poly, source)
    if b_value == 0:
        raise AssertionError("certified zero-free ratio denominator vanished at pole")
    n = _pole_index(turn)
    sin_sign = 1 if n % 2 == 0 else -1
    f_sign = EE.sign(b_value) * sin_sign
    return {
        "status": "DECIDED",
        "kind": "TANGENT_POLE_ONE_SIDED",
        "source": str(source),
        "harmonic_tangent_turn": str(turn),
        "side": side,
        "H_relation": "POSITIVE_INFINITY" if h_sign > 0 else "NEGATIVE_INFINITY",
        "sign": h_sign,
        "original_event_relation": "POSITIVE" if f_sign > 0 else "NEGATIVE",
        "original_event_zero": False,
        "pole_index": n,
    }


def _boundary_comparison(a_poly, b_poly, u_offset, u_rate, source, side):
    turn = q(u_offset) + q(u_rate) * q(source)
    if _is_tangent_pole(turn):
        return _pole_boundary(a_poly, b_poly, u_offset, u_rate, source, side)
    return _finite_comparison(a_poly, b_poly, u_offset, u_rate, source)


def _single_harmonic_ratio_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    if q(rate) == 0:
        return None
    cos_nonzero = {h: _trim(poly) for h, poly in cos_polys.items() if _trim(poly) != [0]}
    sin_nonzero = {h: _trim(poly) for h, poly in sin_polys.items() if _trim(poly) != [0]}
    harmonics = set(cos_nonzero) | set(sin_nonzero)
    if len(harmonics) != 1:
        return None
    harmonic = next(iter(harmonics))
    if harmonic <= 0 or harmonic not in cos_nonzero or harmonic not in sin_nonzero:
        return None
    a_poly = cos_nonzero[harmonic]
    b_poly = sin_nonzero[harmonic]

    common = EE.pgcd(a_poly, b_poly)
    if EE.degree(common) > 0:
        return None

    denominator = _poly_zero_free_closed(b_poly)
    if denominator is None:
        return {
            "status": "BLOCKED",
            "reason": "RATIO_DENOMINATOR_NONVANISHING_NOT_CERTIFIED",
            "blocker": "PB-007-01",
        }

    u_offset = 2 * harmonic * q(offset)
    u_rate = 2 * harmonic * q(rate)
    monotonicity = _monotonicity_certificate(a_poly, b_poly, u_rate)
    if monotonicity is None:
        return {
            "status": "BLOCKED",
            "reason": "OPPOSED_RATIO_MONOTONICITY_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "ratio_derivative_numerator": [
                str(value) for value in _ratio_derivative_numerator(a_poly, b_poly)
            ],
        }

    try:
        boundaries = _phase_pole_boundaries(u_offset, u_rate)
        charts = []
        total_roots = 0
        for left, right in zip(boundaries, boundaries[1:]):
            left_cmp = _boundary_comparison(
                a_poly, b_poly, u_offset, u_rate, left, "left"
            )
            right_cmp = _boundary_comparison(
                a_poly, b_poly, u_offset, u_rate, right, "right"
            )
            for comparison in (left_cmp, right_cmp):
                if comparison.get("status") != "DECIDED":
                    return {
                        "status": comparison.get("status", "BLOCKED"),
                        "reason": comparison.get("reason", "ENDPOINT_COMPARISON_NOT_DECIDED"),
                        "blocker": "PB-007-01",
                        "delegate": comparison,
                    }
            if left == 0 and left_cmp.get("sign") == 0:
                return {
                    "status": "BLOCKED",
                    "reason": "EXTERNAL_ENDPOINT_ZERO_REQUIRES_SEPARATE_COUPLED_MULTIPLICITY_AUTHORITY",
                    "blocker": "PB-007-01",
                    "endpoint": "left",
                    "comparison": left_cmp,
                }
            if right == 1 and right_cmp.get("sign") == 0:
                return {
                    "status": "BLOCKED",
                    "reason": "EXTERNAL_ENDPOINT_ZERO_REQUIRES_SEPARATE_COUPLED_MULTIPLICITY_AUTHORITY",
                    "blocker": "PB-007-01",
                    "endpoint": "right",
                    "comparison": right_cmp,
                }
            increasing = u_rate > 0
            has_root = (
                left_cmp["sign"] < 0 and right_cmp["sign"] > 0
                if increasing
                else left_cmp["sign"] > 0 and right_cmp["sign"] < 0
            )
            roots = 1 if has_root else 0
            total_roots += roots
            charts.append({
                "source_interval": [str(left), str(right)],
                "left_boundary": left_cmp,
                "right_boundary": right_cmp,
                "H_direction": "STRICTLY_INCREASING" if increasing else "STRICTLY_DECREASING",
                "distinct_roots_open": roots,
                "multiple_roots_open": 0,
                "all_open_roots_simple": True,
            })

        internal_poles = []
        for source in boundaries[1:-1]:
            turn = u_offset + u_rate * source
            if not _is_tangent_pole(turn):
                raise AssertionError("non-pole appeared as internal ratio chart boundary")
            boundary = _pole_boundary(
                a_poly, b_poly, u_offset, u_rate, source, "left"
            )
            internal_poles.append({
                "source": str(source),
                "harmonic_tangent_turn": str(turn),
                "original_event_relation": boundary["original_event_relation"],
                "original_event_zero": False,
                "authority": "B_NONZERO_AND_EXACT_CARDINAL_SIN_AT_TANGENT_POLE",
            })

        left_source = Fraction(0)
        right_source = Fraction(1)
        left_boundary = _boundary_comparison(
            a_poly, b_poly, u_offset, u_rate, left_source, "left"
        )
        right_boundary = _boundary_comparison(
            a_poly, b_poly, u_offset, u_rate, right_source, "right"
        )
        return {
            "status": "CERTIFIED",
            "relation": "EXACT_MONOTONE_SINGLE_HARMONIC_RATIO_EVENT_DECISION",
            "source_parameter_id": source_parameter_id,
            "harmonic": harmonic,
            "cos_polynomial": [str(value) for value in a_poly],
            "sin_polynomial": [str(value) for value in b_poly],
            "coprime_proof": {
                "method": "EXACT_RATIONAL_POLYNOMIAL_GCD",
                "gcd_degree": EE.degree(common),
                "gcd_coefficients": [str(value) for value in _trim(common)],
            },
            "ratio": "-A(s)/B(s)",
            "ratio_denominator_certificate": denominator,
            "ratio_monotonicity_certificate": monotonicity,
            "harmonic_tangent_turn_law": {
                "offset": str(u_offset),
                "rate": str(u_rate),
                "definition": "u(s)=2*h*theta_turn(s)",
                "tangent": "tan(pi*u(s))",
            },
            "phase_pole_boundaries": [str(value) for value in boundaries],
            "pole_safe_charts": charts,
            "internal_pole_events": internal_poles,
            "left_endpoint_nonzero": left_boundary.get("sign") != 0,
            "right_endpoint_nonzero": right_boundary.get("sign") != 0,
            "open_roots": {
                "distinct": total_roots,
                "multiplicity_sum": total_roots,
                "multiple_distinct": 0,
                "all_simple": True,
            },
            "simplicity_proof": {
                "identity": "H'(s)=pi*u'(s)*sec^2(pi*u(s))-r'(s)",
                "reason": "u' has fixed nonzero sign and r' is certified opposite/nonincreasing or opposite/nondecreasing; therefore H' has the strict u' sign on every pole-free chart",
                "requires_numeric_pi_bound": False,
                "sampling_used": False,
            },
        }
    except MonotoneRatioRefusal as exc:
        return {"status": "RESOURCE_REFUSAL", "reason": str(exc), "is_truth_value": False}
    except v6.EndpointIsolationRefusal as exc:
        return {"status": "RESOURCE_REFUSAL", "reason": str(exc), "is_truth_value": False}


def analyze_monotone_ratio_event(spec):
    baseline = v8.classify_required_analytic_event(spec)
    if not isinstance(baseline, dict) or baseline.get("relation") not in {
        "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER",
        "FINITE_EXACT_PIECEWISE_COUPLED_EVENT_DECISION",
        "FINITE_EXACT_PIECEWISE_COMMON_FACTOR_EVENT_DECISION",
    }:
        return baseline
    if baseline.get("status") == "CERTIFIED":
        return baseline

    rate = q(baseline["phase_turn_law"]["rate"])
    offset_global = q(baseline["phase_turn_law"]["offset"])
    unresolved = False
    upgraded = []
    for original_span in baseline["spans"]:
        span = dict(original_span)
        route = span["route"]
        if route.get("status") == "BLOCKED" and route.get("reason") == (
            "NONCONSTANT_POLYNOMIAL_MODULATION_WITH_NONZERO_PHASE_REQUIRES_UNESTABLISHED_EXACT_ZERO_ROUTE"
        ):
            left = q(span["source_interval"][0])
            right = q(span["source_interval"][1])
            width = right - left
            local_offset = offset_global + rate * left
            local_rate = rate * width
            cos_polys = {
                int(h): [q(value) for value in poly]
                for h, poly in span["cos_polynomials"].items()
            }
            sin_polys = {
                int(h): [q(value) for value in poly]
                for h, poly in span["sin_polynomials"].items()
            }
            replacement = _single_harmonic_ratio_route(
                cos_polys, sin_polys, local_offset, local_rate,
                baseline["source_parameter_id"],
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO"
                span["route"] = replacement
                span["local_phase_turn_law"] = {
                    "offset": str(local_offset),
                    "rate": str(local_rate),
                    "local_parameter": "s=(u-lo)/(hi-lo)",
                    "shared_parameter": baseline["source_parameter_id"],
                }
        if span["route"].get("status") != "CERTIFIED":
            unresolved = True
        upgraded.append(span)

    statuses = [span["route"].get("status") for span in upgraded]
    if "RESOURCE_REFUSAL" in statuses:
        status = "RESOURCE_REFUSAL"
    elif "SEMANTIC_BLOCKER" in statuses:
        status = "SEMANTIC_BLOCKER"
    elif unresolved:
        status = "BLOCKED"
    else:
        status = "CERTIFIED"
    result = dict(baseline)
    result["status"] = status
    result["spans"] = upgraded
    result["relation"] = (
        "FINITE_EXACT_PIECEWISE_MONOTONE_RATIO_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v9_monotone_ratio_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict) and spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
        return analyze_monotone_ratio_event(spec)
    return v8.classify_required_analytic_event(spec)


def resource_refusal(reason="PB00701_V9_MONOTONE_RATIO_BUDGET_EXHAUSTED"):
    return {"status": "RESOURCE_REFUSAL", "reason": reason, "is_truth_value": False}
