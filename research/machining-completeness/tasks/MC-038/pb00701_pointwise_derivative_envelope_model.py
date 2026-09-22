#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_multiharmonic_monotone_anchor_model as v19  # noqa: E402

EE = v19.EE
q = v19.q
TWO_PI_UPPER = v19.TWO_PI_UPPER
V20_ROUTE = "EXACT_MULTI_HARMONIC_POINTWISE_POLYNOMIAL_DERIVATIVE_ENVELOPE"


class PointwiseEnvelopeRefusal(RuntimeError):
    """Bounded exact-resource refusal. Never a truth value."""


def _trim(poly):
    return v19._trim([q(value) for value in poly])


def _padd(left, right):
    left = _trim(left)
    right = _trim(right)
    out = [Fraction(0)] * max(len(left), len(right))
    for index, value in enumerate(left):
        out[index] += value
    for index, value in enumerate(right):
        out[index] += value
    return _trim(out)


def _pscale(poly, scalar):
    scalar = q(scalar)
    return _trim([scalar * value for value in _trim(poly)])


def _pmul(left, right):
    left = _trim(left)
    right = _trim(right)
    out = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] += a * b
    return _trim(out)


def _strict_sign_certificate(poly, label):
    """Prove a rational polynomial has one strict sign on closed [0,1]."""
    try:
        poly = _trim(poly)
        left = EE.exact_event(poly, Fraction(0))
        right = EE.exact_event(poly, Fraction(1))
        left_relation = left.get("relation")
        right_relation = right.get("relation")
        if left_relation == "ZERO" or right_relation == "ZERO":
            return {
                "status": "BLOCKED",
                "reason": f"{label}_ENDPOINT_ZERO",
                "blocker": "PB-007-01",
                "left_event": left,
                "right_event": right,
            }
        roots = int(EE.distinct_roots_open(poly, Fraction(0), Fraction(1)))
        if roots:
            return {
                "status": "BLOCKED",
                "reason": f"{label}_INTERIOR_ROOT",
                "blocker": "PB-007-01",
                "distinct_roots_open": roots,
                "left_event": left,
                "right_event": right,
            }
        if left_relation not in {"POSITIVE", "NEGATIVE"} or right_relation != left_relation:
            return {
                "status": "BLOCKED",
                "reason": f"{label}_SIGN_NOT_CERTIFIED",
                "blocker": "PB-007-01",
                "left_event": left,
                "right_event": right,
            }
        return {
            "status": "CERTIFIED",
            "relation": "EXACT_RATIONAL_CLOSED_INTERVAL_STURM_STRICT_SIGN",
            "sign": left_relation,
            "polynomial": [str(value) for value in poly],
            "left_event": left,
            "right_event": right,
            "distinct_roots_open": 0,
            "source": "MC-032_EXACT_RATIONAL_STURM_AUTHORITY",
            "caller_certificate_trusted": False,
            "binary_float_used": False,
            "epsilon_used": False,
            "sampling_used": False,
        }
    except (ArithmeticError, MemoryError, RecursionError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V20_{label}_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _strict_positive_certificate(poly, label):
    """Prove a rational polynomial is strictly positive on closed [0,1]."""
    try:
        poly = _trim(poly)
        left = EE.exact_event(poly, Fraction(0))
        right = EE.exact_event(poly, Fraction(1))
        if left.get("relation") != "POSITIVE" or right.get("relation") != "POSITIVE":
            return {
                "status": "BLOCKED",
                "reason": f"{label}_ENDPOINT_NOT_POSITIVE",
                "blocker": "PB-007-01",
                "left_event": left,
                "right_event": right,
            }
        roots = int(EE.distinct_roots_open(poly, Fraction(0), Fraction(1)))
        if roots:
            return {
                "status": "BLOCKED",
                "reason": f"{label}_INTERIOR_ROOT",
                "blocker": "PB-007-01",
                "distinct_roots_open": roots,
                "left_event": left,
                "right_event": right,
            }
        return {
            "status": "CERTIFIED",
            "relation": "EXACT_RATIONAL_CLOSED_INTERVAL_STURM_STRICT_POSITIVITY",
            "polynomial": [str(value) for value in poly],
            "left_event": left,
            "right_event": right,
            "distinct_roots_open": 0,
            "source": "MC-032_EXACT_RATIONAL_STURM_AUTHORITY",
            "caller_certificate_trusted": False,
            "binary_float_used": False,
            "epsilon_used": False,
            "sampling_used": False,
        }
    except (ArithmeticError, MemoryError, RecursionError) as exc:
        return {
            "status": "RESOURCE_REFUSAL",
            "reason": f"PB00701_V20_{label}_RESOURCE_REFUSAL:{type(exc).__name__}",
            "is_truth_value": False,
        }


def _pointwise_derivative_envelope_certificate(cos_polys, sin_polys, phase_rate):
    """Exact pointwise L2 envelope for the oscillatory source derivative.

    For every active positive harmonic, the derivative contribution is bounded
    pointwise by the sum of the absolute values of the exact rational
    polynomials C'_h, S'_h, K_h C_h, K_h S_h, where
    K_h=(44/7)|h*phase_rate| > 2*pi*|h*phase_rate|.

    If these nonzero polynomials are f_1..f_N, Cauchy-Schwarz gives
       sum_i |f_i| <= sqrt(N * sum_i f_i^2).
    Thus a fixed sign for P' and strict positivity of
       Q=P'^2-N*sum_i f_i^2
    prove that the complete event derivative has the sign of P'.
    """
    rate = q(phase_rate)
    anchor = _trim(cos_polys.get(0, [0]))
    anchor_derivative = v19._deriv(anchor)
    if anchor == [0] or anchor_derivative == [0] or rate == 0:
        return None

    positive_harmonics = sorted(
        int(h) for h in (set(cos_polys) | set(sin_polys))
        if int(h) > 0 and (
            _trim(cos_polys.get(h, [0])) != [0]
            or _trim(sin_polys.get(h, [0])) != [0]
        )
    )
    if len(positive_harmonics) < 2:
        return None

    terms = []
    term_polynomials = []
    for harmonic in positive_harmonics:
        c = _trim(cos_polys.get(harmonic, [0]))
        s = _trim(sin_polys.get(harmonic, [0]))
        scale = TWO_PI_UPPER * abs(Fraction(harmonic) * rate)
        candidates = (
            ("C_prime", v19._deriv(c)),
            ("S_prime", v19._deriv(s)),
            ("phase_C", _pscale(c, scale)),
            ("phase_S", _pscale(s, scale)),
        )
        for kind, poly in candidates:
            poly = _trim(poly)
            if poly == [0]:
                continue
            term_polynomials.append(poly)
            terms.append({
                "harmonic": harmonic,
                "kind": kind,
                "polynomial": [str(value) for value in poly],
            })

    if not term_polynomials:
        return None

    sum_squares = [Fraction(0)]
    for poly in term_polynomials:
        sum_squares = _padd(sum_squares, _pmul(poly, poly))
    term_count = len(term_polynomials)
    q_poly = _padd(
        _pmul(anchor_derivative, anchor_derivative),
        _pscale(sum_squares, -term_count),
    )

    anchor_sign = _strict_sign_certificate(anchor_derivative, "ANCHOR_DERIVATIVE")
    if anchor_sign.get("status") == "RESOURCE_REFUSAL":
        return anchor_sign
    if anchor_sign.get("status") != "CERTIFIED":
        return {
            "status": "BLOCKED",
            "reason": "POINTWISE_ENVELOPE_ANCHOR_SIGN_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "anchor_sign_certificate": anchor_sign,
            "q_polynomial": [str(value) for value in q_poly],
        }

    q_positive = _strict_positive_certificate(q_poly, "POINTWISE_ENVELOPE_Q")
    if q_positive.get("status") == "RESOURCE_REFUSAL":
        return q_positive
    if q_positive.get("status") != "CERTIFIED":
        return {
            "status": "BLOCKED",
            "reason": "POINTWISE_ENVELOPE_STRICT_DOMINANCE_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "anchor_sign_certificate": anchor_sign,
            "q_positivity_certificate": q_positive,
            "term_count": term_count,
            "sum_squares_polynomial": [str(value) for value in sum_squares],
            "q_polynomial": [str(value) for value in q_poly],
            "terms": terms,
        }

    direction = "INCREASING" if anchor_sign["sign"] == "POSITIVE" else "DECREASING"
    return {
        "status": "CERTIFIED",
        "relation": "EXACT_POINTWISE_POLYNOMIAL_L2_DERIVATIVE_DOMINANCE",
        "direction": direction,
        "anchor_polynomial": [str(value) for value in anchor],
        "anchor_derivative": [str(value) for value in anchor_derivative],
        "active_positive_harmonics": positive_harmonics,
        "term_count": term_count,
        "terms": terms,
        "sum_squares_polynomial": [str(value) for value in sum_squares],
        "q_polynomial": [str(value) for value in q_poly],
        "anchor_sign_certificate": anchor_sign,
        "q_positivity_certificate": q_positive,
        "pointwise_inequality": "sum_i |f_i(s)| <= sqrt(N * sum_i f_i(s)^2) < |P'(s)|",
        "pi_upper_theorem": "pi < 22/7",
        "two_pi_rational_upper_bound": "44/7",
        "finite_termination": "two exact closed-interval rational-polynomial Sturm decisions",
        "caller_certificate_trusted": False,
        "binary_float_used": False,
        "epsilon_used": False,
        "sampling_used": False,
        "arbitrary_subdivision_cap_used": False,
    }


def _pointwise_envelope_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    rate = q(rate)
    anchor = _trim(cos_polys.get(0, [0]))
    positive_harmonics = sorted(
        int(h) for h in (set(cos_polys) | set(sin_polys))
        if int(h) > 0 and (
            _trim(cos_polys.get(h, [0])) != [0]
            or _trim(sin_polys.get(h, [0])) != [0]
        )
    )
    if rate == 0 or anchor == [0] or EE.degree(anchor) <= 0 or len(positive_harmonics) < 2:
        return None

    derivative = _pointwise_derivative_envelope_certificate(cos_polys, sin_polys, rate)
    if derivative is None:
        return None
    if derivative.get("status") != "CERTIFIED":
        return derivative

    left_event = v19._endpoint_relation(cos_polys, sin_polys, Fraction(0), q(offset))
    if left_event.get("status") == "RESOURCE_REFUSAL":
        return left_event
    right_event = v19._endpoint_relation(cos_polys, sin_polys, Fraction(1), q(offset) + rate)
    if right_event.get("status") == "RESOURCE_REFUSAL":
        return right_event
    root_summary = v19._root_summary(derivative["direction"], left_event, right_event)
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
        "relation": V20_ROUTE,
        "source_parameter_id": source_parameter_id,
        "active_positive_harmonics": positive_harmonics,
        "phase_turn_law_local": {"offset": str(q(offset)), "rate": str(rate)},
        "derivative_certificate": derivative,
        "left_event": left_event,
        "right_event": right_event,
        **root_summary,
        "multiplicity_proof": (
            "exact fixed-sign P' plus exact Q>0 proves the complete source derivative is strictly nonzero "
            "throughout the closed span; every admitted open or endpoint root therefore has multiplicity one"
        ),
        "caller_certificate_trusted": False,
        "sampling_used": False,
        "epsilon_used": False,
        "numerical_trigonometry_used": False,
        "arbitrary_subdivision_cap_used": False,
    }


def analyze_pointwise_derivative_envelope_event(spec):
    baseline = v19.classify_required_analytic_event(spec)
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
        old_route = span.get("route", {})
        eligible = (
            old_route.get("status") == "BLOCKED"
            and old_route.get("reason") == "MONOTONE_ANCHOR_DERIVATIVE_DOMINANCE_NOT_CERTIFIED"
            and "cos_polynomials" in span
            and "sin_polynomials" in span
        )
        if eligible:
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
            replacement = _pointwise_envelope_route(
                cos_polys,
                sin_polys,
                local_offset,
                local_rate,
                baseline["source_parameter_id"],
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V20_EXACT_POINTWISE_DERIVATIVE_ENVELOPE"
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
        "FINITE_EXACT_PIECEWISE_MULTI_HARMONIC_POINTWISE_ENVELOPE_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v20_pointwise_derivative_envelope_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict):
        source_spec = dict(spec)
        for key in (
            "pointwise_envelope", "pointwise_envelope_certificate", "envelope_terms",
            "sum_squares", "sum_squares_polynomial", "q_polynomial", "Q",
            "sturm_certificate", "sturm_root_count", "anchor_sign", "term_count",
            "derivative_certificate", "root_count", "root_certificate",
        ):
            source_spec.pop(key, None)
        if source_spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
            return analyze_pointwise_derivative_envelope_event(source_spec)
        return v19.classify_required_analytic_event(source_spec)
    return v19.classify_required_analytic_event(spec)


def resource_refusal(reason="PB00701_V20_POINTWISE_ENVELOPE_BUDGET_EXHAUSTED"):
    return {"status": "RESOURCE_REFUSAL", "reason": reason, "is_truth_value": False}
