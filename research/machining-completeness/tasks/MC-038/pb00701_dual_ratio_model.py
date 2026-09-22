#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_monotone_ratio_model as v9  # noqa: E402

v8 = v9.v8
v7 = v9.v7
v6 = v9.v6
EE = v9.EE
q = v9.q

MAX_DUAL_CHARTS = v9.MAX_RATIO_CHARTS


class DualRatioRefusal(RuntimeError):
    """Bounded resource refusal. Never a truth value."""


def _fraction_floor(value: Fraction) -> int:
    return value.numerator // value.denominator


def _fraction_ceil(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def _is_integer_turn(value) -> bool:
    value = q(value)
    return value.denominator == 1


def _cot_pole_boundaries(u_offset, u_rate):
    u_offset = q(u_offset)
    u_rate = q(u_rate)
    if u_rate == 0:
        raise ValueError("dual-projective route requires nonzero harmonic phase rate")
    u_end = u_offset + u_rate
    lo = min(u_offset, u_end)
    hi = max(u_offset, u_end)
    first_n = _fraction_ceil(lo)
    last_n = _fraction_floor(hi)
    pole_count = max(0, last_n - first_n + 1)
    if pole_count > MAX_DUAL_CHARTS:
        raise DualRatioRefusal("PB00701_V10_COT_CHART_BUDGET_EXHAUSTED")
    boundaries = {Fraction(0), Fraction(1)}
    for n in range(first_n, last_n + 1):
        source = (Fraction(n) - u_offset) / u_rate
        if 0 < source < 1:
            boundaries.add(source)
    ordered = sorted(boundaries)
    if len(ordered) - 1 > MAX_DUAL_CHARTS:
        raise DualRatioRefusal("PB00701_V10_COT_CHART_BUDGET_EXHAUSTED")
    return ordered


def _finite_cot_comparison(a_poly, b_poly, u_offset, u_rate, source):
    source = q(source)
    a_value = EE.peval(a_poly, source)
    b_value = EE.peval(b_poly, source)
    if a_value == 0:
        raise AssertionError("certified zero-free cotangent denominator vanished")
    ratio = -b_value / a_value
    u_turn = q(u_offset) + q(u_rate) * source
    if _is_integer_turn(u_turn):
        raise ValueError("finite cotangent comparison requested at cotangent pole")
    shifted_turn = Fraction(1, 2) - u_turn
    endpoint = v6.rational_turn_endpoint(shifted_turn)
    event = v6._event_at_endpoint([-ratio, Fraction(1)], endpoint)
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
            "reason": "RATIONAL_TURN_COTANGENT_ENDPOINT_COMPARISON_NOT_DECIDED",
            "delegate": event,
        }
    return {
        "status": "DECIDED",
        "kind": "FINITE_EXACT_RATIONAL_TURN_COTANGENT_COMPARISON",
        "source": str(source),
        "harmonic_projective_turn": str(u_turn),
        "shifted_tangent_turn": str(shifted_turn),
        "ratio": str(ratio),
        "relation": relation,
        "sign": sign,
        "endpoint_kind": endpoint["kind"],
        "comparison_polynomial": [str(-ratio), "1"],
    }


def _cot_pole_boundary(a_poly, u_offset, u_rate, source, side):
    source = q(source)
    u_turn = q(u_offset) + q(u_rate) * source
    if not _is_integer_turn(u_turn):
        raise ValueError("cotangent pole boundary requested at finite cotangent turn")
    rate_sign = 1 if q(u_rate) > 0 else -1
    # side names the boundary position in the chart: a left boundary is
    # approached from the right, while a right boundary is approached from
    # the left. cot(pi*u) is +infinity immediately to the right of an integer
    # and -infinity immediately to its left for increasing u.
    k_sign = rate_sign if side == "left" else -rate_sign
    a_value = EE.peval(a_poly, source)
    if a_value == 0:
        raise AssertionError("certified zero-free cotangent denominator vanished at pole")
    n = int(u_turn)
    cos_sign = 1 if n % 2 == 0 else -1
    f_sign = EE.sign(a_value) * cos_sign
    return {
        "status": "DECIDED",
        "kind": "COTANGENT_POLE_ONE_SIDED",
        "source": str(source),
        "harmonic_projective_turn": str(u_turn),
        "side": side,
        "K_relation": "POSITIVE_INFINITY" if k_sign > 0 else "NEGATIVE_INFINITY",
        "sign": k_sign,
        "original_event_relation": "POSITIVE" if f_sign > 0 else "NEGATIVE",
        "original_event_zero": False,
        "pole_index": n,
    }


def _cot_boundary_comparison(a_poly, b_poly, u_offset, u_rate, source, side):
    u_turn = q(u_offset) + q(u_rate) * q(source)
    if _is_integer_turn(u_turn):
        return _cot_pole_boundary(a_poly, u_offset, u_rate, source, side)
    return _finite_cot_comparison(a_poly, b_poly, u_offset, u_rate, source)


def _endpoint_simple_certificate(a_poly, b_poly, u_rate, source, side, chart):
    source = q(source)
    a_value = EE.peval(a_poly, source)
    b_value = EE.peval(b_poly, source)
    norm2 = a_value * a_value + b_value * b_value
    if norm2 == 0:
        return {
            "status": "BLOCKED",
            "reason": "ENDPOINT_SIMULTANEOUS_MODULATION_ZERO",
            "blocker": "PB-007-01",
        }
    u_rate = q(u_rate)
    if u_rate == 0:
        return {
            "status": "BLOCKED",
            "reason": "ENDPOINT_SIMPLE_THEOREM_REQUIRES_NONZERO_PHASE_RATE",
            "blocker": "PB-007-01",
        }
    derivative_numerator = v9._ratio_derivative_numerator(a_poly, b_poly)
    d_value = EE.peval(derivative_numerator, source)
    denominator = u_rate * norm2
    if denominator == 0:
        raise AssertionError("nonzero phase and modulation norm lost endpoint theorem denominator")
    forced_pi = d_value / denominator
    return {
        "status": "CERTIFIED",
        "kind": "EXACT_SIMPLE_EXTERNAL_ENDPOINT_EVENT",
        "side": side,
        "source": str(source),
        "projective_chart": chart,
        "multiplicity": 1,
        "a_value": str(a_value),
        "b_value": str(b_value),
        "modulation_norm_squared": str(norm2),
        "phase_u_rate": str(u_rate),
        "derivative_numerator_D": str(d_value),
        "multiple_root_consequence": f"pi={forced_pi}",
        "exclusion_theorem": "PI_IS_IRRATIONAL_SO_CANNOT_EQUAL_A_RATIONAL_NUMBER",
        "numeric_pi_used": False,
        "sampling_used": False,
    }


def _dual_monotonicity_certificate(a_poly, b_poly, u_rate, chart):
    certificate = v9._monotonicity_certificate(a_poly, b_poly, u_rate)
    if certificate is None:
        return None
    certificate = dict(certificate)
    certificate["projective_chart"] = chart
    if chart == "TANGENT":
        certificate["projective_function"] = "H=tan(pi*u)-(-A/B)"
        certificate["strict_projective_function_direction"] = (
            "INCREASING" if q(u_rate) > 0 else "DECREASING"
        )
        certificate["derivative_identity"] = (
            "H'=pi*u'*sec^2(pi*u)-r_t', r_t'=(A*B'-A'*B)/B^2"
        )
    else:
        certificate["projective_function"] = "K=cot(pi*u)-(-B/A)"
        certificate["strict_projective_function_direction"] = (
            "DECREASING" if q(u_rate) > 0 else "INCREASING"
        )
        certificate["derivative_identity"] = (
            "K'=-pi*u'*csc^2(pi*u)-r_c', r_c'=-(A*B'-A'*B)/A^2"
        )
    return certificate


def _single_harmonic_dual_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
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
            "reason": "NO_ZERO_FREE_PROJECTIVE_COMPONENT_FOR_DUAL_RATIO_ROUTE",
            "blocker": "PB-007-01",
        }

    u_offset = 2 * harmonic * q(offset)
    u_rate = 2 * harmonic * q(rate)
    monotonicity = _dual_monotonicity_certificate(a_poly, b_poly, u_rate, chart)
    if monotonicity is None:
        return {
            "status": "BLOCKED",
            "reason": "OPPOSED_DUAL_PROJECTIVE_MONOTONICITY_NOT_CERTIFIED",
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
            boundaries = _cot_pole_boundaries(u_offset, u_rate)
            boundary_fn = lambda source, side: _cot_boundary_comparison(  # noqa: E731
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
                endpoint = _endpoint_simple_certificate(
                    a_poly, b_poly, u_rate, left, "left", chart
                )
                if endpoint.get("status") != "CERTIFIED":
                    return endpoint
                endpoint_events.append(endpoint)
            if right == 1 and right_cmp.get("sign") == 0:
                endpoint = _endpoint_simple_certificate(
                    a_poly, b_poly, u_rate, right, "right", chart
                )
                if endpoint.get("status") != "CERTIFIED":
                    return endpoint
                endpoint_events.append(endpoint)

            if chart == "TANGENT":
                increasing = u_rate > 0
            else:
                increasing = u_rate < 0
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
                boundary = v9._pole_boundary(
                    a_poly, b_poly, u_offset, u_rate, source, "left"
                )
            else:
                boundary = _cot_pole_boundary(
                    a_poly, u_offset, u_rate, source, "left"
                )
            internal_poles.append({
                "source": str(source),
                "harmonic_projective_turn": str(u_offset + u_rate * source),
                "original_event_relation": boundary["original_event_relation"],
                "original_event_zero": False,
                "authority": (
                    "B_NONZERO_AT_TANGENT_POLE"
                    if chart == "TANGENT"
                    else "A_NONZERO_AT_COTANGENT_POLE"
                ),
            })

        return {
            "status": "CERTIFIED",
            "relation": "EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_EVENT_DECISION",
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
            "ratio_monotonicity_certificate": monotonicity,
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
                "open_roots": "strict projective-function derivative on each pole-free chart",
                "endpoint_roots": "a multiple endpoint root would force pi to equal an exact rational D/(u'*(A^2+B^2))",
                "requires_numeric_pi_bound": False,
                "sampling_used": False,
            },
        }
    except (DualRatioRefusal, v9.MonotoneRatioRefusal) as exc:
        return {"status": "RESOURCE_REFUSAL", "reason": str(exc), "is_truth_value": False}
    except v6.EndpointIsolationRefusal as exc:
        return {"status": "RESOURCE_REFUSAL", "reason": str(exc), "is_truth_value": False}


def analyze_dual_ratio_event(spec):
    baseline = v9.classify_required_analytic_event(spec)
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
    upgrade_reasons = {
        "RATIO_DENOMINATOR_NONVANISHING_NOT_CERTIFIED",
        "EXTERNAL_ENDPOINT_ZERO_REQUIRES_SEPARATE_COUPLED_MULTIPLICITY_AUTHORITY",
    }
    for original_span in baseline["spans"]:
        span = dict(original_span)
        route = span["route"]
        if route.get("status") == "BLOCKED" and route.get("reason") in upgrade_reasons:
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
            replacement = _single_harmonic_dual_route(
                cos_polys, sin_polys, local_offset, local_rate,
                baseline["source_parameter_id"],
            )
            if replacement is not None:
                span["route_kind"] = "PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO"
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
        "FINITE_EXACT_PIECEWISE_DUAL_PROJECTIVE_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v10_dual_projective_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict) and spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
        return analyze_dual_ratio_event(spec)
    return v9.classify_required_analytic_event(spec)


def resource_refusal(reason="PB00701_V10_DUAL_PROJECTIVE_BUDGET_EXHAUSTED"):
    return {"status": "RESOURCE_REFUSAL", "reason": reason, "is_truth_value": False}
