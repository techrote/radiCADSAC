#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from math import gcd, isqrt
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_coupled_bspline_model as v7  # noqa: E402

v6 = v7.v6
EE = v7.EE
q = v7.q

MAX_PHASE_CHARTS = 4096
MAX_RATIONAL_ROOT_CANDIDATES = 20000


class CommonFactorRefusal(RuntimeError):
    """Bounded resource refusal. Never a truth value."""


def _trim(poly):
    out = [q(value) for value in poly]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out or [Fraction(0)]


def _monic(poly):
    poly = _trim(poly)
    if poly == [0]:
        return poly
    lead = poly[-1]
    return _trim([value / lead for value in poly])


def _pdiv_exact(numerator, denominator):
    numerator = _trim(numerator)
    denominator = _trim(denominator)
    if denominator == [0]:
        raise ZeroDivisionError("polynomial division by zero")
    if len(numerator) < len(denominator):
        return [Fraction(0)], numerator
    remainder = list(numerator)
    quotient = [Fraction(0)] * (len(numerator) - len(denominator) + 1)
    while remainder != [0] and len(remainder) >= len(denominator):
        shift = len(remainder) - len(denominator)
        coefficient = remainder[-1] / denominator[-1]
        quotient[shift] += coefficient
        for index, value in enumerate(denominator):
            remainder[index + shift] -= coefficient * value
        remainder = _trim(remainder)
    return _trim(quotient), _trim(remainder)


def _common_factor(polynomials):
    nonzero = [_trim(poly) for poly in polynomials if _trim(poly) != [0]]
    if not nonzero:
        return None
    common = nonzero[0]
    for poly in nonzero[1:]:
        common = EE.pgcd(common, poly)
    common = _monic(common)
    if EE.degree(common) <= 0:
        return None
    quotients = []
    for poly in nonzero:
        quotient, remainder = _pdiv_exact(poly, common)
        if remainder != [0] or EE.degree(quotient) != 0:
            return None
        quotients.append(quotient[0])
    return common, quotients


def _fraction_floor(value: Fraction) -> int:
    return value.numerator // value.denominator


def _fraction_ceil(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def _phase_chart_boundaries(offset, rate):
    offset = q(offset)
    rate = q(rate)
    if rate == 0:
        raise ValueError("common-factor route requires nonzero phase rate")
    turn0 = offset
    turn1 = offset + rate
    lo = min(turn0, turn1)
    hi = max(turn0, turn1)
    boundaries = {Fraction(0), Fraction(1)}
    first_n = _fraction_ceil(2 * lo)
    last_n = _fraction_floor(2 * hi)
    if last_n - first_n + 1 > MAX_PHASE_CHARTS:
        raise CommonFactorRefusal("PB00701_V8_PHASE_CHART_BUDGET_EXHAUSTED")
    for n in range(first_n, last_n + 1):
        turn = Fraction(n, 2)
        source = (turn - offset) / rate
        if 0 < source < 1:
            boundaries.add(source)
    ordered = sorted(boundaries)
    if len(ordered) - 1 > MAX_PHASE_CHARTS:
        raise CommonFactorRefusal("PB00701_V8_PHASE_CHART_BUDGET_EXHAUSTED")
    return ordered


def _chart_shift(turn_a, turn_b):
    midpoint = (q(turn_a) + q(turn_b)) / 2
    cell = _fraction_floor(2 * midpoint)
    return Fraction(2 * cell + 1, 4)


def _shift_trig_coefficients(cos_coefficients, sin_coefficients, shift):
    cos_out = {}
    sin_out = {}
    harmonics = sorted(set(cos_coefficients) | set(sin_coefficients))
    for harmonic in harmonics:
        trig = v7._cardinal_cos_sin(harmonic, shift)
        if trig is None:
            raise AssertionError("quarter-turn chart shift lost exact cardinal authority")
        cosine, sine = trig
        c = q(cos_coefficients.get(harmonic, 0))
        d = q(sin_coefficients.get(harmonic, 0))
        c_new = c * cosine + d * sine
        d_new = -c * sine + d * cosine
        if c_new:
            cos_out[harmonic] = c_new
        if d_new:
            if harmonic == 0:
                raise AssertionError("phase shift manufactured sin(0*theta)")
            sin_out[harmonic] = d_new
    return cos_out, sin_out


def _serial_coefficients(mapping):
    return {str(h): str(value) for h, value in sorted(mapping.items()) if value}


def _trig_event_at_source(cos_coefficients, sin_coefficients, offset, rate, source):
    source = q(source)
    turn = q(offset) + q(rate) * source
    cell = _fraction_floor(2 * turn)
    shift = Fraction(2 * cell + 1, 4)
    shifted_cos, shifted_sin = _shift_trig_coefficients(
        cos_coefficients, sin_coefficients, shift
    )
    reduced = turn - shift
    endpoint = v6.rational_turn_endpoint(reduced)
    numerator = v6.base.trig_polynomial_to_tan_half(
        _serial_coefficients(shifted_cos), _serial_coefficients(shifted_sin)
    )["numerator"]
    event = v6._event_at_endpoint(numerator, endpoint)
    return dict(event, source_parameter=str(source), original_turn=str(turn), chart_shift=str(shift))


def _multiplicity_sum_rational_interval(poly, lo, hi):
    current = _trim(poly)
    total = 0
    while EE.degree(current) > 0:
        total += EE.distinct_roots_open(current, lo, hi)
        current = EE.pgcd(current, EE.deriv(current))
    return total


def _multiple_distinct_rational_interval(poly, lo, hi):
    repeated = EE.pgcd(_trim(poly), EE.deriv(_trim(poly)))
    if EE.degree(repeated) <= 0:
        return 0
    return EE.distinct_roots_open(repeated, lo, hi)


def _multiplicity_sum_v6(poly, left_endpoint, right_endpoint):
    current = _trim(poly)
    total = 0
    while EE.degree(current) > 0:
        total += v6._distinct_roots_open(current, left_endpoint, right_endpoint)
        current = EE.pgcd(current, EE.deriv(current))
    return total


def _multiple_distinct_v6(poly, left_endpoint, right_endpoint):
    repeated = EE.pgcd(_trim(poly), EE.deriv(_trim(poly)))
    if EE.degree(repeated) <= 0:
        return 0
    return v6._distinct_roots_open(repeated, left_endpoint, right_endpoint)


def _divisors(value: int):
    value = abs(value)
    if value == 0:
        return []
    result = set()
    for candidate in range(1, isqrt(value) + 1):
        if value % candidate == 0:
            result.add(candidate)
            result.add(value // candidate)
        if len(result) > MAX_RATIONAL_ROOT_CANDIDATES:
            raise CommonFactorRefusal("PB00701_V8_RATIONAL_ROOT_ENUMERATION_BUDGET_EXHAUSTED")
    return sorted(result)


def _lcm(a: int, b: int) -> int:
    if not a or not b:
        return 0
    return abs(a // gcd(a, b) * b)


def _primitive_integer_poly(poly):
    poly = _trim(poly)
    denominator = 1
    for value in poly:
        denominator = _lcm(denominator, value.denominator)
    ints = [int(value * denominator) for value in poly]
    content = 0
    for value in ints:
        content = gcd(content, abs(value))
    if content:
        ints = [value // content for value in ints]
    if ints and ints[-1] < 0:
        ints = [-value for value in ints]
    return ints


def _rational_roots_open(poly, lo=Fraction(0), hi=Fraction(1)):
    poly = _trim(poly)
    roots = set()
    work = list(poly)
    if work[0] == 0:
        if lo < 0 < hi:
            roots.add(Fraction(0))
        while len(work) > 1 and work[0] == 0:
            work = work[1:]
    work = _trim(work)
    if EE.degree(work) <= 0:
        return sorted(roots)
    ints = _primitive_integer_poly(work)
    constant = abs(ints[0])
    leading = abs(ints[-1])
    numerators = _divisors(constant)
    denominators = _divisors(leading)
    if 2 * len(numerators) * len(denominators) > MAX_RATIONAL_ROOT_CANDIDATES:
        raise CommonFactorRefusal("PB00701_V8_RATIONAL_ROOT_ENUMERATION_BUDGET_EXHAUSTED")
    for numerator in numerators:
        for denominator in denominators:
            for sign in (-1, 1):
                root = Fraction(sign * numerator, denominator)
                if lo < root < hi and EE.peval(poly, root) == 0:
                    roots.add(root)
    return sorted(roots)


def _chart_trig_summary(cos_coefficients, sin_coefficients, offset, rate, left, right, source_parameter_id):
    turn_left = offset + rate * left
    turn_right = offset + rate * right
    shift = _chart_shift(turn_left, turn_right)
    shifted_cos, shifted_sin = _shift_trig_coefficients(cos_coefficients, sin_coefficients, shift)
    reduced_left = turn_left - shift
    reduced_right = turn_right - shift
    lo = min(reduced_left, reduced_right)
    hi = max(reduced_left, reduced_right)
    result = v6.analyze_rational_turn_window(
        cos_coefficients=_serial_coefficients(shifted_cos),
        sin_coefficients=_serial_coefficients(shifted_sin),
        turn_lo=lo,
        turn_hi=hi,
        source_parameter_id=source_parameter_id,
        parameter_projection=source_parameter_id,
    )
    if result.get("status") != "CERTIFIED":
        return {
            "status": result.get("status", "BLOCKED"),
            "reason": result.get("reason", "V6_CHART_DELEGATION_FAILED"),
            "delegate": result,
        }
    numerator = [q(value) for value in result["numerator_coefficients"]]
    left_endpoint = v6.rational_turn_endpoint(lo)
    right_endpoint = v6.rational_turn_endpoint(hi)
    multiplicity_sum = _multiplicity_sum_v6(numerator, left_endpoint, right_endpoint)
    multiple_distinct = _multiple_distinct_v6(numerator, left_endpoint, right_endpoint)
    return {
        "status": "CERTIFIED",
        "source_interval": [str(left), str(right)],
        "phase_turn_interval": [str(turn_left), str(turn_right)],
        "chart_shift": str(shift),
        "reduced_turn_interval": [str(reduced_left), str(reduced_right)],
        "shifted_cos_coefficients": _serial_coefficients(shifted_cos),
        "shifted_sin_coefficients": _serial_coefficients(shifted_sin),
        "distinct_roots_open": result["distinct_roots_open"],
        "open_root_multiplicity_sum": multiplicity_sum,
        "multiple_roots_open": multiple_distinct,
        "delegate": result,
    }


def _factor_route(cos_polys, sin_polys, offset, rate, source_parameter_id):
    if rate == 0:
        return None
    labelled = []
    polynomials = []
    for kind, mapping in (("cos", cos_polys), ("sin", sin_polys)):
        for harmonic, poly in sorted(mapping.items()):
            poly = _trim(poly)
            if poly != [0]:
                labelled.append((kind, harmonic, poly))
                polynomials.append(poly)
    factorization = _common_factor(polynomials)
    if factorization is None:
        return None
    common, quotient_values = factorization
    cos_coefficients = {}
    sin_coefficients = {}
    quotient_proof = []
    for (kind, harmonic, poly), scalar in zip(labelled, quotient_values):
        quotient, remainder = _pdiv_exact(poly, common)
        quotient_proof.append({
            "channel": kind,
            "harmonic": harmonic,
            "polynomial": [str(value) for value in poly],
            "quotient": [str(value) for value in quotient],
            "remainder": [str(value) for value in remainder],
        })
        if remainder != [0] or EE.degree(quotient) != 0:
            return None
        if kind == "cos":
            cos_coefficients[harmonic] = scalar
        else:
            sin_coefficients[harmonic] = scalar

    if not cos_coefficients and not sin_coefficients:
        return {
            "status": "BLOCKED",
            "reason": "ZERO_TRIG_IDENTITY_OR_ZERO_MODULATION",
            "blocker": "PB-007-01",
        }

    try:
        chart_boundaries = _phase_chart_boundaries(offset, rate)
        charts = []
        for left, right in zip(chart_boundaries, chart_boundaries[1:]):
            chart = _chart_trig_summary(
                cos_coefficients, sin_coefficients, offset, rate, left, right, source_parameter_id
            )
            if chart.get("status") != "CERTIFIED":
                return chart
            charts.append(chart)

        internal_events = []
        trig_distinct = sum(chart["distinct_roots_open"] for chart in charts)
        trig_multiplicity_sum = sum(chart["open_root_multiplicity_sum"] for chart in charts)
        trig_multiple_distinct = sum(chart["multiple_roots_open"] for chart in charts)
        for boundary in chart_boundaries[1:-1]:
            event = _trig_event_at_source(
                cos_coefficients, sin_coefficients, offset, rate, boundary
            )
            internal_events.append(event)
            if event.get("relation") == "ZERO":
                trig_distinct += 1
                multiplicity = int(event["multiplicity"])
                trig_multiplicity_sum += multiplicity
                if multiplicity > 1:
                    trig_multiple_distinct += 1

        factor_distinct = EE.distinct_roots_open(common, Fraction(0), Fraction(1))
        factor_multiplicity_sum = _multiplicity_sum_rational_interval(
            common, Fraction(0), Fraction(1)
        )
        factor_multiple_distinct = _multiple_distinct_rational_interval(
            common, Fraction(0), Fraction(1)
        )
        rational_roots = _rational_roots_open(common)
        coincidences = []
        for root in rational_roots:
            factor_event = EE.exact_event(common, root)
            trig_event = _trig_event_at_source(
                cos_coefficients, sin_coefficients, offset, rate, root
            )
            if trig_event.get("relation") == "ZERO":
                coincidences.append({
                    "source": str(root),
                    "factor_multiplicity": int(factor_event["multiplicity"]),
                    "trig_multiplicity": int(trig_event["multiplicity"]),
                    "product_multiplicity": int(factor_event["multiplicity"]) + int(trig_event["multiplicity"]),
                    "checked_exactly": True,
                })

        irrational_factor_roots = factor_distinct - len(rational_roots)
        coincidence_count = len(coincidences)
        both_multiple = sum(
            item["factor_multiplicity"] > 1 and item["trig_multiplicity"] > 1
            for item in coincidences
        )
        both_simple = sum(
            item["factor_multiplicity"] == 1 and item["trig_multiplicity"] == 1
            for item in coincidences
        )
        product_multiple_distinct = (
            factor_multiple_distinct + trig_multiple_distinct - both_multiple + both_simple
        )

        factor_left = EE.exact_event(common, Fraction(0))
        factor_right = EE.exact_event(common, Fraction(1))
        trig_left = _trig_event_at_source(cos_coefficients, sin_coefficients, offset, rate, 0)
        trig_right = _trig_event_at_source(cos_coefficients, sin_coefficients, offset, rate, 1)

        def product_endpoint(factor_event, trig_event):
            fm = int(factor_event.get("multiplicity", 0)) if factor_event.get("relation") == "ZERO" else 0
            tm = int(trig_event.get("multiplicity", 0)) if trig_event.get("relation") == "ZERO" else 0
            multiplicity = fm + tm
            return {
                "relation": "ZERO" if multiplicity else "NONZERO",
                "factor_multiplicity": fm,
                "trig_multiplicity": tm,
                "product_multiplicity": multiplicity,
                "singular": multiplicity > 1,
                "sign_change": bool(multiplicity % 2) if multiplicity else None,
            }

        return {
            "status": "CERTIFIED",
            "relation": "EXACT_COMMON_POLYNOMIAL_FACTOR_TIMES_RATIONAL_TRIG_POLYNOMIAL",
            "common_factor_coefficients": [str(value) for value in common],
            "common_factor_degree": EE.degree(common),
            "factorization_proof": {
                "method": "EXACT_RATIONAL_POLYNOMIAL_GCD_AND_DIVISION",
                "quotients": quotient_proof,
                "all_remainders_zero": True,
                "all_quotients_degree_zero": True,
            },
            "trig_factor": {
                "cos_coefficients": _serial_coefficients(cos_coefficients),
                "sin_coefficients": _serial_coefficients(sin_coefficients),
                "nonzero_identity": True,
            },
            "phase_chart_boundaries": [str(value) for value in chart_boundaries],
            "pole_safe_charts": charts,
            "internal_chart_events": internal_events,
            "factor_open_roots": {
                "distinct": factor_distinct,
                "multiplicity_sum": factor_multiplicity_sum,
                "multiple_distinct": factor_multiple_distinct,
                "rational_roots": [str(value) for value in rational_roots],
                "algebraic_irrational_distinct": irrational_factor_roots,
            },
            "trig_open_roots": {
                "distinct": trig_distinct,
                "multiplicity_sum": trig_multiplicity_sum,
                "multiple_distinct": trig_multiple_distinct,
            },
            "coincidences": coincidences,
            "coincidence_authority": {
                "rational_source_roots_checked_exactly": True,
                "algebraic_irrational_source_roots_disjoint_by": "GELFOND_SCHNEIDER",
                "preconditions": [
                    "common factor has rational coefficients",
                    "phase offset and nonzero phase rate are rational",
                    "trigonometric factor is nonzero with rational coefficients",
                    "one shared algebraic source parameter is used",
                ],
                "generalization_outside_grammar_forbidden": True,
            },
            "product_open_roots": {
                "distinct": factor_distinct + trig_distinct - coincidence_count,
                "multiplicity_sum": factor_multiplicity_sum + trig_multiplicity_sum,
                "multiple_distinct": product_multiple_distinct,
            },
            "left_event": product_endpoint(factor_left, trig_left),
            "right_event": product_endpoint(factor_right, trig_right),
        }
    except CommonFactorRefusal as exc:
        return {"status": "RESOURCE_REFUSAL", "reason": str(exc), "is_truth_value": False}
    except v6.EndpointIsolationRefusal as exc:
        return {"status": "RESOURCE_REFUSAL", "reason": str(exc), "is_truth_value": False}


def analyze_common_factor_event(spec):
    baseline = v7.classify_required_analytic_event(spec)
    if not isinstance(baseline, dict) or baseline.get("relation") not in {
        "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER",
        "FINITE_EXACT_PIECEWISE_COUPLED_EVENT_DECISION",
    }:
        return baseline
    if baseline.get("status") == "CERTIFIED":
        return baseline

    rate = q(baseline["phase_turn_law"]["rate"])
    offset_global = q(baseline["phase_turn_law"]["offset"])
    unresolved = False
    upgraded = []
    for span in baseline["spans"]:
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
            replacement = _factor_route(
                cos_polys, sin_polys, local_offset, local_rate,
                baseline["source_parameter_id"],
            )
            if replacement is not None:
                span = dict(span)
                span["route_kind"] = "PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION"
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
        "FINITE_EXACT_PIECEWISE_COMMON_FACTOR_EVENT_DECISION"
        if status == "CERTIFIED"
        else "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
    )
    result["blocker"] = "PB-007-01" if unresolved else None
    result["v8_common_factor_extension"] = True
    return result


def classify_required_analytic_event(spec):
    if isinstance(spec, dict) and spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
        return analyze_common_factor_event(spec)
    return v7.classify_required_analytic_event(spec)


def resource_refusal(reason="PB00701_V8_COMMON_FACTOR_BUDGET_EXHAUSTED"):
    return {"status": "RESOURCE_REFUSAL", "reason": reason, "is_truth_value": False}
