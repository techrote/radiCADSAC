#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from math import comb
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_source_laurent_factor_model as v18  # noqa: E402
import pb00701_rational_turn_model as v6  # noqa: E402

EE = v18.EE
q = v18.q

V19_ROUTE = "EXACT_MULTI_HARMONIC_MONOTONE_ANCHOR_DERIVATIVE_DOMINANCE"
PI_UPPER = Fraction(22, 7)
TWO_PI_UPPER = Fraction(44, 7)


class MonotoneAnchorRefusal(RuntimeError):
    """Bounded exact-resource refusal. Never a truth value."""


def _trim(poly):
    return v18._trim([q(value) for value in poly])


def _peval(poly, value):
    value = q(value)
    total = Fraction(0)
    for coefficient in reversed(_trim(poly)):
        total = total * value + coefficient
    return total


def _deriv(poly):
    poly = _trim(poly)
    if len(poly) <= 1:
        return [Fraction(0)]
    return _trim([index * poly[index] for index in range(1, len(poly))])


def _bernstein_coefficients(poly):
    """Exact power->Bernstein conversion on [0,1]."""
    poly = _trim(poly)
    degree = len(poly) - 1
    if degree == 0:
        return [poly[0]]
    out = []
    for k in range(degree + 1):
        value = Fraction(0)
        for j in range(k + 1):
            if j < len(poly):
                value += poly[j] * Fraction(comb(k, j), comb(degree, j))
        out.append(value)
    return out


def _bernstein_abs_bound(poly):
    coefficients = _bernstein_coefficients(poly)
    return max(abs(value) for value in coefficients)


def _derivative_dominance_certificate(cos_polys, sin_polys, phase_rate):
    """Certify a fixed source-derivative sign by an exact rational bound.

    For h>0,
      |d(C_h cos(2*pi*h*phi)+S_h sin(2*pi*h*phi))/ds|
      <= ||C'_h|| + ||S'_h||
         + 2*pi*|h*phi'| (||C_h|| + ||S_h||).

    We replace 2*pi only by the rigorous rational upper bound 44/7.
    Bernstein convex-hull bounds on [0,1] make every remaining quantity exact.
    """
    rate = q(phase_rate)
    anchor = _trim(cos_polys.get(0, [0]))
    anchor_derivative = _deriv(anchor)
    if anchor == [0] or anchor_derivative == [0]:
        return None

    anchor_bernstein = _bernstein_coefficients(anchor_derivative)
    lower = min(anchor_bernstein)
    upper = max(anchor_bernstein)

    terms = []
    total_bound = Fraction(0)
    positive_harmonics = sorted(
        h for h in (set(cos_polys) | set(sin_polys))
        if int(h) > 0 and (
            _trim(cos_polys.get(h, [0])) != [0]
            or _trim(sin_polys.get(h, [0])) != [0]
        )
    )
    for harmonic in positive_harmonics:
        c = _trim(cos_polys.get(harmonic, [0]))
        s = _trim(sin_polys.get(harmonic, [0]))
        c_prime = _deriv(c)
        s_prime = _deriv(s)
        c_bound = _bernstein_abs_bound(c)
        s_bound = _bernstein_abs_bound(s)
        c_prime_bound = _bernstein_abs_bound(c_prime)
        s_prime_bound = _bernstein_abs_bound(s_prime)
        phase_bound = TWO_PI_UPPER * abs(Fraction(int(harmonic)) * rate) * (c_bound + s_bound)
        term_bound = c_prime_bound + s_prime_bound + phase_bound
        total_bound += term_bound
        terms.append({
            "harmonic": int(harmonic),
            "C_bernstein_abs_bound": str(c_bound),
            "S_bernstein_abs_bound": str(s_bound),
            "C_prime_bernstein_abs_bound": str(c_prime_bound),
            "S_prime_bernstein_abs_bound": str(s_prime_bound),
            "phase_derivative_bound": str(phase_bound),
            "total_derivative_bound": str(term_bound),
        })

    if lower > total_bound:
        direction = "INCREASING"
        margin = lower - total_bound
    elif upper < -total_bound:
        direction = "DECREASING"
        margin = -total_bound - upper
    else:
        return {
            "status": "BLOCKED",
            "reason": "MONOTONE_ANCHOR_DERIVATIVE_DOMINANCE_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "anchor_derivative_bernstein": [str(value) for value in anchor_bernstein],
            "anchor_derivative_lower": str(lower),
            "anchor_derivative_upper": str(upper),
            "oscillatory_derivative_bound": str(total_bound),
            "pi_upper_theorem": "pi < 22/7",
            "strict_margin": "0",
            "terms": terms,
        }

    return {
        "status": "CERTIFIED",
        "relation": "EXACT_BERNSTEIN_DERIVATIVE_DOMINANCE",
        "direction": direction,
        "anchor_polynomial": [str(value) for value in anchor],
        "anchor_derivative": [str(value) for value in anchor_derivative],
        "anchor_derivative_bernstein": [str(value) for value in anchor_bernstein],
        "anchor_derivative_lower": str(lower),
        "anchor_derivative_upper": str(upper),
        "oscillatory_derivative_bound": str(total_bound),
        "strict_margin": str(margin),
        "pi_upper_theorem": "pi < 22/7",
        "two_pi_rational_upper_bound": "44/7",
        "terms": terms,
        "binary_float_used": False,
        "epsilon_used": False,
        "sampling_used": False,
        "caller_certificate_trusted": False,
    }


def _endpoint_coefficients(cos_polys, sin_polys, source_value):
    source_value = q(source_value)
    cos_coefficients = {}
    sin_coefficients = {}
    for harmonic, poly in cos_polys.items():
        value = _peval(poly, source_value)
        if value:
            cos_coefficients[int(harmonic)] = value
    for harmonic, poly in sin_polys.items():
        value = _peval(poly, source_value)
        if value:
            sin_coefficients[int(harmonic)] = value
    return cos_coefficients, sin_coefficients


def _shift_half_turn_if_needed(turn, cos_coefficients, sin_coefficients):
    """Move a tangent-half pole endpoint by exactly half a turn.

    For every integer harmonic h,
      cos(2*pi*h*(t-1/2)) = (-1)^h cos(2*pi*h*t)
      sin(2*pi*h*(t-1/2)) = (-1)^h sin(2*pi*h*t).
    Therefore multiplying each coefficient by (-1)^h preserves the original
    endpoint value while moving tan(pi*t) away from its half-turn pole.
    """
    turn = q(turn)
    if v6._principal_turn(turn) != Fraction(1, 2):
        return turn, dict(cos_coefficients), dict(sin_coefficients), False
    shifted_turn = turn - Fraction(1, 2)
    shifted_cos = {
        int(h): value * (Fraction(-1) if int(h) % 2 else Fraction(1))
        for h, value in cos_coefficients.items()
    }
    shifted_sin = {
        int(h): value * (Fraction(-1) if int(h) % 2 else Fraction(1))
        for h, value in sin_coefficients.items()
    }
    return shifted_turn, shifted_cos, shifted_sin, True


def _endpoint_relation(cos_polys, sin_polys, source_value, turn):
    try:
        cos_coefficients, sin_coefficients = _endpoint_coefficients(
            cos_polys, sin_polys, source_value
        )
        shifted_turn, cos_coefficients, sin_coefficients, shifted = _shift_half_turn_if_needed(
            turn, cos_coefficients, sin_coefficients
        )
        reduction = v6.base.trig_polynomial_to_tan_half(
            cos_coefficients=cos_coefficients,
            sin_coefficients=sin_coefficients,
        )
        numerator = reduction["numerator"]
        if numerator == [0]:
            sign = 0
            endpoint_description = {"kind": "IDENTITY_ZERO_AT_FIXED_SOURCE_ENDPOINT"}
        else:
            endpoint = v6.rational_turn_endpoint(shifted_turn)
            sign, endpoint = v6._sign_at_endpoint(numerator, endpoint)
            endpoint_description = v6._endpoint_description(endpoint)
        relation = "ZERO" if sign == 0 else "POSITIVE" if sign > 0 else "NEGATIVE"
        return {
            "status": "DECIDED",
            "relation": relation,
            "source_value": str(q(source_value)),
            "original_turn": str(q(turn)),
            "evaluation_turn": str(shifted_turn),
            "half_turn_parity_shift": shifted,
            "tan_half_endpoint": endpoint_description,
            "numerator_coefficients": [str(value) for value in numerator],
            "denominator_power": reduction["denominator_power"],
            "binary_float_used": False,
            "epsilon_used": False,
        }
    except v6.EndpointIsolationRefusal as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": str(exc),
            "is_truth_value": False,
        }
    except (ArithmeticError, MemoryError, RecursionError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V19_ENDPOINT_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _relation_number(relation):
    return {"NEGATIVE": -1, "ZERO": 0, "POSITIVE": 1}[relation]


def _root_summary(direction, left_event, right_event):
    left = _relation_number(left_event["relation"])
    right = _relation_number(right_event["relation"])
    if direction == "INCREASING" and left > right:
        return {"status": "SEMANTIC_BLOCKER", "reason": "ENDPOINT_ORDER_CONTRADICTS_CERTIFIED_MONOTONICITY"}
    if direction == "DECREASING" and left < right:
        return {"status": "SEMANTIC_BLOCKER", "reason": "ENDPOINT_ORDER_CONTRADICTS_CERTIFIED_MONOTONICITY"}
    if left == 0 and right == 0:
        return {"status": "SEMANTIC_BLOCKER", "reason": "DISTINCT_ENDPOINT_ZEROS_CONTRADICT_STRICT_MONOTONICITY"}
    open_roots = 1 if left * right < 0 else 0
    left_root = left == 0
    right_root = right == 0
    return {
        "status": "CERTIFIED",
        "distinct_roots_open": open_roots,
        "left_endpoint_root": left_root,
        "right_endpoint_root": right_root,
        "total_distinct_roots_closed": open_roots + int(left_root) + int(right_root),
        "multiple_roots_open": 0,
        "all_roots_simple": True,
        "endpoint_root_multiplicity": (
            {"left": 1} if left_root else {"right": 1} if right_root else {}
        ),
    }


def _monotone_anchor_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    rate = q(rate)
    anchor = _trim(cos_polys.get(0, [0]))
    positive_harmonics = sorted(
        h for h in (set(cos_polys) | set(sin_polys))
        if int(h) > 0 and (
            _trim(cos_polys.get(h, [0])) != [0]
            or _trim(sin_polys.get(h, [0])) != [0]
        )
    )
    if rate == 0 or anchor == [0] or EE.degree(anchor) <= 0 or len(positive_harmonics) < 2:
        return None

    derivative = _derivative_dominance_certificate(cos_polys, sin_polys, rate)
    if derivative is None:
        return None
    if derivative.get("status") != "CERTIFIED":
        return derivative

    left_event = _endpoint_relation(cos_polys, sin_polys, Fraction(0), q(offset))
    if left_event.get("status") == "RESOURCE_REFUSAL":
        return left_event
    right_event = _endpoint_relation(cos_polys, sin_polys, Fraction(1), q(offset) + rate)
    if right_event.get("status") == "RESOURCE_REFUSAL":
        return right_event
    root_summary = _root_summary(derivative["direction"], left_event, right_event)
    if root_summary.get("status") != "CERTIFIED":
        return {
            **root_summary,
            "blocker": "PB-007-01",
            "derivative_certificate": derivative,
            "left_event": left_event,
            "right_event": right_event,
        }

    return {
        "status": "CERTIFIED",
        "relation": V19_ROUTE,
        "source_parameter_id": source_parameter_id,
        "active_positive_harmonics": positive_harmonics,
        "phase_turn_law_local": {"offset": str(q(offset)), "rate": str(rate)},
        "derivative_certificate": derivative,
        "left_event": left_event,
        "right_event": right_event,
        **root_summary,
        "multiplicity_proof": (
            "the exact derivative certificate has a strictly positive rational margin from zero on the closed span; "
            "therefore every admitted source root, including an endpoint root, has multiplicity one"
        ),
        "caller_certificate_trusted": False,
        "sampling_used": False,
        "epsilon_used": False,
        "numerical_trigonometry_used": False,
    }


def analyze_multiharmonic_monotone_anchor_event(spec):
    baseline = v18.classify_required_analytic_event(spec)
    if not isinstance(baseline, dict) or baseline.get("status") == "CERTIFIED":
        return baseline
    if baseline.get("relation") != "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER":
        return baseline

    phase = baseline.get("phase_turn_law", {})
    rate = q(phase.get("rate", "0"))
    offset_global = q(phase.get("offset", "0"))
    upgraded = []
    unresolved = False
    for original_span in baseline.get("spans", []):
        span = dict(original_span)
        if span.get("route", {}).get("status") != "CERTIFIED" and "cos_polynomials" in span and "sin_polynomials" in span:
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
            replacement = _monotone_anchor_route(
                cos_polys,
                sin_polys,
                local_offset,
                local_rate,
                baseline["source_parameter_id"],
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V19_EXACT_MULTI_HARMONIC_MONOTONE_ANCHOR"
                span["route"] = replacement
                span["local_phase_turn_law"] = {
                    "offset": str(local_offset),
                    "rate": str(local_rate),
                    "local_parameter": "s=(u-lo)/(hi-lo)",
                    "shared_parameter": baseline["source_parameter_id"],
                }
        if span.get("route", {}).get("status") != "CERTIFIED":
            unresolved = True
        upgraded.append(span)

    statuses = [span.get("route", {}).get("status") for span in upgraded]
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
        "FINITE_EXACT_PIECEWISE_MULTI_HARMONIC_MONOTONE_ANCHOR_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v19_multiharmonic_monotone_anchor_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict):
        source_spec = dict(spec)
        for key in (
            "anchor_derivative", "bernstein_certificate", "bernstein_bounds",
            "derivative_bound", "derivative_certificate", "monotonicity",
            "endpoint_signs", "endpoint_certificate", "root_count", "root_certificate",
            "pi_upper_bound", "strict_margin",
        ):
            source_spec.pop(key, None)
        if source_spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
            return analyze_multiharmonic_monotone_anchor_event(source_spec)
        return v18.classify_required_analytic_event(source_spec)
    return v18.classify_required_analytic_event(spec)


def resource_refusal(reason="PB00701_V19_MONOTONE_ANCHOR_BUDGET_EXHAUSTED"):
    return {"status": "RESOURCE_REFUSAL", "reason": reason, "is_truth_value": False}
