#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_dual_ratio_model as v10  # noqa: E402

v9 = v10.v9
v8 = v10.v8
v7 = v10.v7
v6 = v10.v6
EE = v10.EE
q = v10.q


def _strict_positive_closed(poly):
    """Certify an exact rational polynomial is strictly positive on [0,1]."""
    poly = v9._trim(poly)
    if poly == [0]:
        return None
    left = EE.peval(poly, Fraction(0))
    right = EE.peval(poly, Fraction(1))
    if left <= 0 or right <= 0:
        return None
    roots_open = EE.distinct_roots_open(poly, Fraction(0), Fraction(1))
    if roots_open:
        return None
    middle = EE.peval(poly, Fraction(1, 2))
    if middle <= 0:
        raise AssertionError("root-free positive-endpoint polynomial lost positive midpoint")
    return {
        "status": "CERTIFIED",
        "method": "MC032_EXACT_STURM_STRICT_POSITIVITY_ON_CLOSED_SPAN",
        "polynomial": [str(value) for value in poly],
        "left_value": str(left),
        "right_value": str(right),
        "sample_source": "1/2",
        "sample_value": str(middle),
        "distinct_roots_open": 0,
    }


def _phase_dominance_certificate(a_poly, b_poly, u_rate, chart):
    """Prove phase derivative dominates the selected rational ratio derivative.

    D=A*B'-A'*B.  For tangent H'=pi*u'*sec^2-D/B^2; for
    cotangent K'=-pi*u'*csc^2+D/A^2.  pi>3 and

      3*|u'|*den^2 - sign(u')*D > 0

    therefore fixes the exact projective-function derivative direction without
    evaluating pi numerically, even when D changes sign.
    """
    u_rate = q(u_rate)
    if u_rate == 0:
        return None
    d_poly = v9._ratio_derivative_numerator(a_poly, b_poly)
    denominator = b_poly if chart == "TANGENT" else a_poly
    den_sq = v7._pmul(denominator, denominator)
    phase_term = v7._pscale(den_sq, 3 * abs(u_rate))
    signed_d = v7._pscale(d_poly, 1 if u_rate > 0 else -1)
    dominance_poly = v9._psub(phase_term, signed_d)
    positive = _strict_positive_closed(dominance_poly)
    if positive is None:
        return None
    d_roots = EE.distinct_roots_open(d_poly, Fraction(0), Fraction(1)) if d_poly != [0] else 0
    return {
        "status": "CERTIFIED",
        "method": "EXACT_RATIONAL_PHASE_DERIVATIVE_DOMINANCE_USING_PI_GT_3",
        "projective_chart": chart,
        "pi_theorem": "PI_IS_STRICTLY_GREATER_THAN_3",
        "numeric_pi_used": False,
        "sampling_used": False,
        "u_rate": str(u_rate),
        "ratio_derivative_numerator_D": [str(value) for value in d_poly],
        "ratio_derivative_distinct_roots_open": d_roots,
        "dominance_polynomial_definition": "P=3*abs(u')*den^2-sign(u')*D",
        "dominance_polynomial_certificate": positive,
        "strict_projective_function_direction": (
            ("INCREASING" if u_rate > 0 else "DECREASING")
            if chart == "TANGENT"
            else ("DECREASING" if u_rate > 0 else "INCREASING")
        ),
        "derivative_identity": (
            "H'=pi*u'*sec^2(pi*u)-D/B^2"
            if chart == "TANGENT"
            else "K'=-pi*u'*csc^2(pi*u)+D/A^2"
        ),
    }


def _single_harmonic_phase_dominance_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    if q(rate) == 0:
        return None
    cos_nonzero = {h: v9._trim(poly) for h, poly in cos_polys.items() if v9._trim(poly) != [0]}
    sin_nonzero = {h: v9._trim(poly) for h, poly in sin_polys.items() if v9._trim(poly) != [0]}
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

    b_zero_free = v9._poly_zero_free_closed(b_poly)
    a_zero_free = v9._poly_zero_free_closed(a_poly)
    if b_zero_free is not None:
        chart = "TANGENT"
        denominator_certificate = b_zero_free
    elif a_zero_free is not None:
        chart = "COTANGENT"
        denominator_certificate = a_zero_free
    else:
        return {
            "status": "BLOCKED",
            "reason": "NO_ZERO_FREE_PROJECTIVE_COMPONENT_FOR_PHASE_DOMINANCE_ROUTE",
            "blocker": "PB-007-01",
        }

    u_offset = 2 * harmonic * q(offset)
    u_rate = 2 * harmonic * q(rate)
    dominance = _phase_dominance_certificate(a_poly, b_poly, u_rate, chart)
    if dominance is None:
        return {
            "status": "BLOCKED",
            "reason": "EXACT_PHASE_DERIVATIVE_DOMINANCE_NOT_CERTIFIED",
            "blocker": "PB-007-01",
            "projective_chart": chart,
            "ratio_derivative_numerator": [
                str(value) for value in v9._ratio_derivative_numerator(a_poly, b_poly)
            ],
        }

    try:
        if chart == "TANGENT":
            boundaries = v9._phase_pole_boundaries(u_offset, u_rate)
            boundary_fn = lambda source, side: v9._boundary_comparison(  # noqa: E731
                a_poly, b_poly, u_offset, u_rate, source, side
            )
        else:
            boundaries = v10._cot_pole_boundaries(u_offset, u_rate)
            boundary_fn = lambda source, side: v10._cot_boundary_comparison(  # noqa: E731
                a_poly, b_poly, u_offset, u_rate, source, side
            )

        charts = []
        endpoint_events = []
        total_open_roots = 0
        for left, right in zip(boundaries, boundaries[1:]):
            left_cmp = boundary_fn(left, "left")
            right_cmp = boundary_fn(right, "right")
            for comparison in (left_cmp, right_cmp):
                if comparison.get("status") != "DECIDED":
                    return {
                        "status": comparison.get("status", "BLOCKED"),
                        "reason": comparison.get("reason", "PROJECTIVE_ENDPOINT_COMPARISON_NOT_DECIDED"),
                        "blocker": "PB-007-01",
                        "delegate": comparison,
                    }

            if left == 0 and left_cmp.get("sign") == 0:
                endpoint = v10._endpoint_simple_certificate(
                    a_poly, b_poly, u_rate, left, "left", chart
                )
                if endpoint.get("status") != "CERTIFIED":
                    return endpoint
                endpoint_events.append(endpoint)
            if right == 1 and right_cmp.get("sign") == 0:
                endpoint = v10._endpoint_simple_certificate(
                    a_poly, b_poly, u_rate, right, "right", chart
                )
                if endpoint.get("status") != "CERTIFIED":
                    return endpoint
                endpoint_events.append(endpoint)

            increasing = (u_rate > 0) if chart == "TANGENT" else (u_rate < 0)
            has_root = (
                left_cmp["sign"] < 0 and right_cmp["sign"] > 0
                if increasing
                else left_cmp["sign"] > 0 and right_cmp["sign"] < 0
            )
            roots = 1 if has_root else 0
            total_open_roots += roots
            charts.append({
                "source_interval": [str(left), str(right)],
                "left_boundary": left_cmp,
                "right_boundary": right_cmp,
                "projective_function_direction": "STRICTLY_INCREASING" if increasing else "STRICTLY_DECREASING",
                "distinct_roots_open": roots,
                "multiple_roots_open": 0,
                "all_open_roots_simple": True,
            })

        internal_poles = []
        for source in boundaries[1:-1]:
            if chart == "TANGENT":
                boundary = v9._pole_boundary(a_poly, b_poly, u_offset, u_rate, source, "left")
            else:
                boundary = v10._cot_pole_boundary(a_poly, u_offset, u_rate, source, "left")
            internal_poles.append({
                "source": str(source),
                "harmonic_projective_turn": str(u_offset + u_rate * source),
                "original_event_relation": boundary["original_event_relation"],
                "original_event_zero": False,
                "authority": "B_NONZERO_AT_TANGENT_POLE" if chart == "TANGENT" else "A_NONZERO_AT_COTANGENT_POLE",
            })

        return {
            "status": "CERTIFIED",
            "relation": "EXACT_PHASE_DOMINATED_SINGLE_HARMONIC_EVENT_DECISION",
            "source_parameter_id": source_parameter_id,
            "harmonic": harmonic,
            "cos_polynomial": [str(value) for value in a_poly],
            "sin_polynomial": [str(value) for value in b_poly],
            "coprime_proof": {
                "method": "EXACT_RATIONAL_POLYNOMIAL_GCD",
                "gcd_degree": EE.degree(common),
                "gcd_coefficients": [str(value) for value in v9._trim(common)],
            },
            "projective_chart": chart,
            "projective_ratio": "-A(s)/B(s)" if chart == "TANGENT" else "-B(s)/A(s)",
            "ratio_denominator_certificate": denominator_certificate,
            "phase_dominance_certificate": dominance,
            "harmonic_projective_turn_law": {
                "offset": str(u_offset),
                "rate": str(u_rate),
                "definition": "u(s)=2*h*theta_turn(s)",
            },
            "projective_pole_boundaries": [str(value) for value in boundaries],
            "pole_safe_charts": charts,
            "internal_pole_events": internal_poles,
            "endpoint_events": endpoint_events,
            "open_roots": {
                "distinct": total_open_roots,
                "multiplicity_sum": total_open_roots,
                "multiple_distinct": 0,
                "all_simple": True,
            },
            "all_certified_events": {
                "open_distinct": total_open_roots,
                "endpoint_distinct": len(endpoint_events),
                "multiplicity_sum": total_open_roots + len(endpoint_events),
                "all_simple": True,
            },
            "simplicity_proof": {
                "open_roots": "strict projective-function derivative from exact pi>3 phase-dominance certificate",
                "endpoint_roots": "v10 exact endpoint-simple irrational-pi contradiction",
                "numeric_pi_used": False,
                "sampling_used": False,
            },
        }
    except (v10.DualRatioRefusal, v9.MonotoneRatioRefusal) as exc:
        return {"status": "RESOURCE_REFUSAL", "reason": str(exc), "is_truth_value": False}
    except v6.EndpointIsolationRefusal as exc:
        return {"status": "RESOURCE_REFUSAL", "reason": str(exc), "is_truth_value": False}


def analyze_phase_dominance_event(spec):
    baseline = v10.classify_required_analytic_event(spec)
    if not isinstance(baseline, dict):
        return baseline
    if baseline.get("status") == "CERTIFIED":
        return baseline
    if baseline.get("relation") != "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER":
        return baseline

    rate = q(baseline["phase_turn_law"]["rate"])
    offset_global = q(baseline["phase_turn_law"]["offset"])
    unresolved = False
    upgraded = []
    for original_span in baseline["spans"]:
        span = dict(original_span)
        route = span["route"]
        if (
            span.get("route_kind") == "PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO"
            and route.get("status") == "BLOCKED"
            and route.get("reason") == "OPPOSED_DUAL_PROJECTIVE_MONOTONICITY_NOT_CERTIFIED"
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
            replacement = _single_harmonic_phase_dominance_route(
                cos_polys, sin_polys, local_offset, local_rate,
                baseline["source_parameter_id"],
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO"
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
        "FINITE_EXACT_PIECEWISE_PHASE_DOMINATED_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v11_phase_dominance_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict) and spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
        return analyze_phase_dominance_event(spec)
    return v10.classify_required_analytic_event(spec)


def resource_refusal(reason="PB00701_V11_PHASE_DOMINANCE_BUDGET_EXHAUSTED"):
    return {"status": "RESOURCE_REFUSAL", "reason": reason, "is_truth_value": False}
