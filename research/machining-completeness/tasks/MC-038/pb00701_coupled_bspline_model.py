#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pb00701_rational_turn_model as v6  # noqa: E402

EE = v6.EE
q = v6.q


class CoupledAnalyticRefusal(RuntimeError):
    """Bounded resource refusal. Never a truth value."""


def _trim(poly):
    out = [q(value) for value in poly]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out or [Fraction(0)]


def _padd(a, b):
    a = _trim(a)
    b = _trim(b)
    out = [Fraction(0)] * max(len(a), len(b))
    for i, value in enumerate(a):
        out[i] += value
    for i, value in enumerate(b):
        out[i] += value
    return _trim(out)


def _pscale(poly, scalar):
    scalar = q(scalar)
    return _trim([scalar * value for value in _trim(poly)])


def _pmul(a, b):
    a = _trim(a)
    b = _trim(b)
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, left in enumerate(a):
        for j, right in enumerate(b):
            out[i + j] += left * right
    return _trim(out)


def _peval(poly, value):
    value = q(value)
    total = Fraction(0)
    for coefficient in reversed(_trim(poly)):
        total = total * value + coefficient
    return total


def _is_constant(poly):
    return len(_trim(poly)) == 1


def _normalise_bspline(spec):
    if not isinstance(spec, dict):
        raise TypeError("B-spline spec must be an object")
    if set(spec) != {"degree", "knots", "controls"}:
        raise ValueError("B-spline spec must contain exactly degree, knots and controls")
    degree = spec["degree"]
    if isinstance(degree, bool) or not isinstance(degree, int) or degree < 0:
        raise TypeError("B-spline degree must be a non-negative integer")
    raw_knots = spec["knots"]
    raw_controls = spec["controls"]
    if not isinstance(raw_knots, list) or not isinstance(raw_controls, list):
        raise TypeError("B-spline knots and controls must be finite lists")
    if not raw_controls:
        raise ValueError("B-spline requires at least one control value")
    knots = [q(value) for value in raw_knots]
    controls = [q(value) for value in raw_controls]
    if len(knots) != len(controls) + degree + 1:
        raise ValueError("B-spline knot/control cardinality mismatch")
    if any(left > right for left, right in zip(knots, knots[1:])):
        raise ValueError("B-spline knots must be nondecreasing exactly")
    max_multiplicity = 1
    run = 1
    for left, right in zip(knots, knots[1:]):
        if left == right:
            run += 1
            max_multiplicity = max(max_multiplicity, run)
        else:
            run = 1
    if max_multiplicity > degree + 1:
        raise ValueError("B-spline knot multiplicity exceeds degree+1")
    domain_lo = knots[degree]
    domain_hi = knots[len(controls)]
    if not domain_lo < domain_hi:
        raise ValueError("B-spline source domain is empty")
    return {
        "degree": degree,
        "knots": knots,
        "controls": controls,
        "domain": (domain_lo, domain_hi),
    }


def _basis_piece(knots, degree, index, span_lo, span_hi, memo):
    key = (index, degree)
    if key in memo:
        return memo[key]
    if degree == 0:
        midpoint = (span_lo + span_hi) / 2
        value = Fraction(1) if knots[index] <= midpoint < knots[index + 1] else Fraction(0)
        memo[key] = [value]
        return memo[key]

    width = span_hi - span_lo
    left = [Fraction(0)]
    left_den = knots[index + degree] - knots[index]
    if left_den:
        left_factor = [
            (span_lo - knots[index]) / left_den,
            width / left_den,
        ]
        left = _pmul(
            left_factor,
            _basis_piece(knots, degree - 1, index, span_lo, span_hi, memo),
        )

    right = [Fraction(0)]
    right_den = knots[index + degree + 1] - knots[index + 1]
    if right_den:
        right_factor = [
            (knots[index + degree + 1] - span_lo) / right_den,
            -width / right_den,
        ]
        right = _pmul(
            right_factor,
            _basis_piece(knots, degree - 1, index + 1, span_lo, span_hi, memo),
        )

    memo[key] = _padd(left, right)
    return memo[key]


def bspline_piece(spec, span_lo, span_hi):
    """Return exact local-s power coefficients on one knot-free open source span.

    The local coordinate is s=(u-span_lo)/(span_hi-span_lo), s in (0,1).
    Exact one-sided endpoint limits are returned separately. Repeated source
    knots remain semantic boundaries; no epsilon is used to merge them.
    """
    normal = _normalise_bspline(spec)
    lo = q(span_lo)
    hi = q(span_hi)
    domain_lo, domain_hi = normal["domain"]
    if not (domain_lo <= lo < hi <= domain_hi):
        raise ValueError("requested span lies outside B-spline source domain")
    if any(lo < knot < hi for knot in normal["knots"]):
        raise ValueError("requested span crosses a source knot")

    memo = {}
    poly = [Fraction(0)]
    for index, control in enumerate(normal["controls"]):
        basis = _basis_piece(
            normal["knots"], normal["degree"], index, lo, hi, memo
        )
        poly = _padd(poly, _pscale(basis, control))
    poly = _trim(poly)
    return {
        "source_interval": (lo, hi),
        "local_coordinate": "s=(u-lo)/(hi-lo)",
        "coefficients": poly,
        "left_limit": _peval(poly, 0),
        "right_limit": _peval(poly, 1),
    }


def lower_bspline(spec, interval_lo=None, interval_hi=None):
    normal = _normalise_bspline(spec)
    lo = normal["domain"][0] if interval_lo is None else q(interval_lo)
    hi = normal["domain"][1] if interval_hi is None else q(interval_hi)
    if not (normal["domain"][0] <= lo < hi <= normal["domain"][1]):
        raise ValueError("requested lowering interval lies outside B-spline source domain")
    boundaries = {lo, hi}
    boundaries.update(k for k in normal["knots"] if lo < k < hi)
    ordered = sorted(boundaries)
    return [
        bspline_piece(spec, left, right)
        for left, right in zip(ordered, ordered[1:])
        if left < right
    ]


def _normalise_harmonic_splines(mapping, name):
    if mapping is None:
        return {}
    if not isinstance(mapping, dict):
        raise TypeError(f"{name} must be a harmonic->B-spline mapping")
    out = {}
    for raw_harmonic, spline in mapping.items():
        if isinstance(raw_harmonic, bool):
            raise TypeError("harmonic index must not be bool")
        try:
            harmonic = int(raw_harmonic)
        except (TypeError, ValueError) as exc:
            raise TypeError("harmonic index must be an integer") from exc
        if str(harmonic) != str(raw_harmonic) and not isinstance(raw_harmonic, int):
            raise TypeError("harmonic index must use canonical integer encoding")
        if harmonic < 0:
            raise ValueError("negative harmonics are not separate real-series indices")
        if name == "sin_splines" and harmonic == 0:
            raise ValueError("sin(0*theta) modulation is invalid")
        out[harmonic] = _normalise_bspline(spline)
    return out


def _canonical_bspline_spec(normal):
    return {
        "degree": normal["degree"],
        "knots": [str(value) for value in normal["knots"]],
        "controls": [str(value) for value in normal["controls"]],
    }


def _master_boundaries(normals, interval_lo, interval_hi):
    boundaries = {interval_lo, interval_hi}
    for normal in normals:
        domain_lo, domain_hi = normal["domain"]
        if not (domain_lo <= interval_lo < interval_hi <= domain_hi):
            raise ValueError("all modulation channels must cover the requested source interval")
        boundaries.update(k for k in normal["knots"] if interval_lo < k < interval_hi)
    return sorted(boundaries)


def _piece_from_normal(normal, left, right):
    return bspline_piece(_canonical_bspline_spec(normal), left, right)


def _quarter_turn_index(turn):
    turn = q(turn)
    quarter = turn * 4
    if quarter.denominator != 1:
        return None
    return quarter.numerator % 4


def _cardinal_cos_sin(harmonic, turn):
    index = _quarter_turn_index(q(turn) * harmonic)
    if index is None:
        return None
    table = {
        0: (Fraction(1), Fraction(0)),
        1: (Fraction(0), Fraction(1)),
        2: (Fraction(-1), Fraction(0)),
        3: (Fraction(0), Fraction(-1)),
    }
    return table[index]


def _event_summary(event):
    return {
        key: event[key]
        for key in ("status", "relation", "multiplicity", "singular", "event_kind", "sign_change")
        if key in event
    }


def _stationary_cardinal_result(cos_polys, sin_polys, phase_turn):
    total = [Fraction(0)]
    harmonics = sorted(set(cos_polys) | set(sin_polys))
    for harmonic in harmonics:
        trig = _cardinal_cos_sin(harmonic, phase_turn)
        if trig is None:
            return {
                "status": "BLOCKED",
                "reason": "STATIONARY_NONCARDINAL_PHASE_ALGEBRAIC_COEFFICIENT_ROUTE_NOT_ESTABLISHED",
                "blocker": "PB-007-01",
            }
        cosine, sine = trig
        if harmonic in cos_polys:
            total = _padd(total, _pscale(cos_polys[harmonic], cosine))
        if harmonic in sin_polys:
            total = _padd(total, _pscale(sin_polys[harmonic], sine))
    total = _trim(total)
    if total == [0]:
        return {
            "status": "BLOCKED",
            "reason": "IDENTITY_ZERO_REQUIRES_SEPARATE_EVENT_SEMANTICS",
            "blocker": "PB-007-01",
        }
    repeated = EE.pgcd(total, EE.deriv(total))
    return {
        "status": "CERTIFIED",
        "relation": "EXACT_STATIONARY_CARDINAL_POLYNOMIAL_EVENT",
        "polynomial_coefficients": [str(value) for value in total],
        "left_event": _event_summary(EE.exact_event(total, Fraction(0))),
        "right_event": _event_summary(EE.exact_event(total, Fraction(1))),
        "distinct_roots_open": EE.distinct_roots_open(total, Fraction(0), Fraction(1)),
        "multiple_roots_open": (
            0 if EE.degree(repeated) <= 0
            else EE.distinct_roots_open(repeated, Fraction(0), Fraction(1))
        ),
    }


def _dominance_certificate(cos_polys, sin_polys):
    base = _trim(cos_polys.get(0, [Fraction(0)]))
    base_constant = base[0]
    base_variation = sum(abs(value) for value in base[1:])
    oscillatory = Fraction(0)
    for harmonic, poly in cos_polys.items():
        if harmonic == 0:
            continue
        oscillatory += sum(abs(value) for value in _trim(poly))
    for poly in sin_polys.values():
        oscillatory += sum(abs(value) for value in _trim(poly))
    margin = abs(base_constant) - base_variation - oscillatory
    if margin <= 0:
        return None
    return {
        "status": "CERTIFIED",
        "relation": "SEPARATED_BY_EXACT_RATIONAL_AMPLITUDE_DOMINANCE",
        "sign": "POSITIVE" if base_constant > 0 else "NEGATIVE",
        "margin": str(margin),
        "bound_rule": "|a0|-sum(|nonconstant harmonic-0 coefficients|)-sum(|oscillatory coefficients|)>0",
        "distinct_roots_open": 0,
        "multiple_roots_open": 0,
    }


def _constant_modulation_result(cos_polys, sin_polys, turn_left, turn_right, source_parameter_id):
    cos_coefficients = {
        str(h): str(_trim(poly)[0])
        for h, poly in cos_polys.items()
        if _trim(poly)[0] != 0
    }
    sin_coefficients = {
        str(h): str(_trim(poly)[0])
        for h, poly in sin_polys.items()
        if _trim(poly)[0] != 0
    }
    lo = min(turn_left, turn_right)
    hi = max(turn_left, turn_right)
    result = v6.analyze_rational_turn_window(
        cos_coefficients=cos_coefficients,
        sin_coefficients=sin_coefficients,
        turn_lo=lo,
        turn_hi=hi,
        source_parameter_id=source_parameter_id,
        parameter_projection=source_parameter_id,
    )
    result = dict(result)
    result["delegated_route"] = "PB00701_V6_CONSTANT_COEFFICIENT_RATIONAL_TURN"
    return result


def analyze_coupled_bspline_event(
    *,
    cos_splines=None,
    sin_splines=None,
    parameter_lo,
    parameter_hi,
    phase_turn_offset,
    phase_turn_rate,
    source_parameter_id,
    parameter_projection=None,
):
    if not source_parameter_id or not isinstance(source_parameter_id, str):
        return {"status": "SEMANTIC_BLOCKER", "reason": "MISSING_SHARED_SOURCE_PARAMETER"}
    if parameter_projection not in (None, source_parameter_id):
        return {"status": "SEMANTIC_BLOCKER", "reason": "INDEPENDENT_PARAMETER_PROJECTION_FORBIDDEN"}

    try:
        lo = q(parameter_lo)
        hi = q(parameter_hi)
        offset = q(phase_turn_offset)
        rate = q(phase_turn_rate)
        if not lo < hi:
            return {"status": "SEMANTIC_BLOCKER", "reason": "INVERTED_OR_EMPTY_SOURCE_INTERVAL"}
        cos_norm = _normalise_harmonic_splines(cos_splines, "cos_splines")
        sin_norm = _normalise_harmonic_splines(sin_splines, "sin_splines")
        if not cos_norm and not sin_norm:
            return {"status": "SEMANTIC_BLOCKER", "reason": "EMPTY_EVENT_EXPRESSION"}
        all_normals = list(cos_norm.values()) + list(sin_norm.values())
        boundaries = _master_boundaries(all_normals, lo, hi)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        return {
            "status": "SEMANTIC_BLOCKER",
            "reason": "INVALID_EXACT_COUPLED_BSPLINE_EVENT_SPEC",
            "detail": str(exc),
        }

    spans = []
    unresolved = False
    for left, right in zip(boundaries, boundaries[1:]):
        if not left < right:
            continue
        cos_polys = {
            harmonic: _piece_from_normal(normal, left, right)["coefficients"]
            for harmonic, normal in cos_norm.items()
        }
        sin_polys = {
            harmonic: _piece_from_normal(normal, left, right)["coefficients"]
            for harmonic, normal in sin_norm.items()
        }
        turn_left = offset + rate * left
        turn_right = offset + rate * right

        route = _dominance_certificate(cos_polys, sin_polys)
        if route is not None:
            route_kind = "EXACT_RATIONAL_AMPLITUDE_DOMINANCE"
        elif rate == 0:
            route = _stationary_cardinal_result(cos_polys, sin_polys, offset)
            route_kind = "EXACT_STATIONARY_PHASE_POLYNOMIAL"
        elif all(_is_constant(poly) for poly in list(cos_polys.values()) + list(sin_polys.values())):
            route = _constant_modulation_result(
                cos_polys, sin_polys, turn_left, turn_right, source_parameter_id
            )
            route_kind = "DELEGATED_V6_CONSTANT_MODULATION"
        else:
            unresolved = True
            route = {
                "status": "BLOCKED",
                "reason": "NONCONSTANT_POLYNOMIAL_MODULATION_WITH_NONZERO_PHASE_REQUIRES_UNESTABLISHED_EXACT_ZERO_ROUTE",
                "blocker": "PB-007-01",
                "theorem_boundary": "BOUNDED_POLYNOMIAL_TRIGONOMETRIC_EXPONENTIAL_ZERO_PROBLEM",
                "sampling_or_timeout_is_truth": False,
                "satisfying_unproved_conjecture_assumed": False,
            }
            route_kind = "PB00701_GENERAL_COUPLED_THEOREM_BOUNDARY"

        if route.get("status") != "CERTIFIED":
            unresolved = True

        spans.append({
            "source_interval": [str(left), str(right)],
            "phase_turn_interval": [str(turn_left), str(turn_right)],
            "cos_polynomials": {
                str(h): [str(value) for value in poly]
                for h, poly in sorted(cos_polys.items())
            },
            "sin_polynomials": {
                str(h): [str(value) for value in poly]
                for h, poly in sorted(sin_polys.items())
            },
            "route_kind": route_kind,
            "route": route,
        })

    route_statuses = [span["route"].get("status") for span in spans]
    if "RESOURCE_REFUSAL" in route_statuses:
        aggregate_status = "RESOURCE_REFUSAL"
    elif "SEMANTIC_BLOCKER" in route_statuses:
        aggregate_status = "SEMANTIC_BLOCKER"
    elif unresolved:
        aggregate_status = "BLOCKED"
    else:
        aggregate_status = "CERTIFIED"

    return {
        "status": aggregate_status,
        "relation": (
            "FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER"
            if unresolved
            else "FINITE_EXACT_PIECEWISE_COUPLED_EVENT_DECISION"
        ),
        "source_parameter_id": source_parameter_id,
        "source_interval": [str(lo), str(hi)],
        "phase_turn_law": {
            "offset": str(offset),
            "rate": str(rate),
            "shared_parameter": source_parameter_id,
        },
        "spans": spans,
        "blocker": "PB-007-01" if unresolved else None,
    }


def classify_required_analytic_event(spec):
    if not isinstance(spec, dict):
        return {"status": "UNCERTIFIED", "reason": "MISSING_ANALYTIC_EVENT_SPEC"}
    grammar = spec.get("grammar")
    if grammar == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
        allowed = {
            "grammar", "cos_splines", "sin_splines", "parameter_lo", "parameter_hi",
            "phase_turn_offset", "phase_turn_rate", "source_parameter_id",
            "parameter_projection",
        }
        if set(spec) - allowed:
            return {"status": "SEMANTIC_BLOCKER", "reason": "UNREVIEWED_EVENT_AUTHORITY_FIELD"}
        return analyze_coupled_bspline_event(
            cos_splines=spec.get("cos_splines"),
            sin_splines=spec.get("sin_splines"),
            parameter_lo=spec.get("parameter_lo"),
            parameter_hi=spec.get("parameter_hi"),
            phase_turn_offset=spec.get("phase_turn_offset"),
            phase_turn_rate=spec.get("phase_turn_rate"),
            source_parameter_id=spec.get("source_parameter_id"),
            parameter_projection=spec.get("parameter_projection"),
        )
    if grammar in {
        "RATIONAL_TRIG_POLYNOMIAL_RATIONAL_TURN_WINDOW",
        "RATIONAL_TRIG_POLYNOMIAL_CARDINAL_WINDOW",
    }:
        return v6.classify_required_analytic_event(spec)
    if grammar in {
        "GENERAL_COUPLED_EXPONENTIAL_POLYNOMIAL",
        "GENERAL_TANGENTIAL_MULTIPLE_SINGULAR_TRANSCENDENTAL",
    }:
        return {
            "status": "BLOCKED",
            "reason": "FULL_REQUIRED_ANALYTIC_DECISION_ROUTE_NOT_ESTABLISHED",
            "blocker": "PB-007-01",
        }
    return {"status": "BLOCKED", "reason": "UNSUPPORTED_ANALYTIC_GRAMMAR", "blocker": "PB-007-01"}


def resource_refusal(reason="PB00701_COUPLED_BSPLINE_BUDGET_EXHAUSTED"):
    return {"status": "RESOURCE_REFUSAL", "reason": reason, "is_truth_value": False}
