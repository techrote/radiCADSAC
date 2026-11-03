#!/usr/bin/env python3
"""Prospective exact two-span stationary B-spline zero-component research.

No arbitrary child assertions: the original five controls of each cosine
channel are lowered with exact rational arithmetic. This restricted theorem
handles phase offset=rate=0 and rationally split degree<=2 pieces only.
Irrational roots and moving phases conservatively BLOCK; it is not MC-B proof.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as Q
from math import isqrt

SCHEMA = "radicadsac-mc038-two-span-stationary-mixed-components/1.0"
GRAMMAR = "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE"
MAX_SOURCE_BYTES = 16384
MAX_BITS = 96


class Refusal(ValueError):
    pass


class ResourceRefusal(Refusal):
    pass


def budget(ok, reason):
    if not ok:
        raise ResourceRefusal(reason)


def need(ok, reason):
    if not ok:
        raise Refusal(reason)


def rational(raw):
    need(type(raw) is str and 0 < len(raw) <= 128, "NONCANONICAL_RATIONAL")
    try:
        value = Q(raw)
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise Refusal("NONCANONICAL_RATIONAL") from exc
    need(str(value) == raw, "NONCANONICAL_RATIONAL")
    budget(max(abs(value.numerator).bit_length(), value.denominator.bit_length()) <= MAX_BITS,
           "RATIONAL_BIT_BUDGET_EXCEEDED")
    return value


def encode(record):
    return json.dumps(record, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode()


def source(spec):
    need(type(spec) is dict and set(spec) == {
        "grammar", "source_parameter_id", "parameter_lo", "parameter_hi",
        "phase_turn_offset", "phase_turn_rate", "cos_splines", "sin_splines"
    }, "ORIGINAL_SOURCE_FIELDS_REQUIRED")
    raw = encode(spec)
    budget(len(raw) <= MAX_SOURCE_BYTES, "SOURCE_BYTE_BUDGET_EXCEEDED")
    need(spec["grammar"] == GRAMMAR, "SOURCE_GRAMMAR_MISMATCH")
    name = spec["source_parameter_id"]
    need(type(name) is str and 0 < len(name) <= 128, "SOURCE_PARAMETER_ID_INVALID")
    lo, hi = rational(spec["parameter_lo"]), rational(spec["parameter_hi"])
    need(lo < hi, "SOURCE_INTERVAL_INVALID")
    need(rational(spec["phase_turn_offset"]) == 0 and
         rational(spec["phase_turn_rate"]) == 0,
         "ONLY_STATIONARY_ZERO_PHASE_PROVED")
    need(type(spec["sin_splines"]) is dict and not spec["sin_splines"],
         "SINE_CHANNELS_UNSUPPORTED")
    channels = spec["cos_splines"]
    need(type(channels) is dict and set(channels) == {"0", "1"},
         "TWO_ORIGINAL_COSINE_CHANNELS_REQUIRED")
    extracted = []
    knot = None
    for harmonic in ("0", "1"):
        spline = channels[harmonic]
        need(type(spline) is dict and set(spline) == {"degree", "knots", "controls"},
             "ORIGINAL_SPLINE_FIELDS_REQUIRED")
        need(type(spline["degree"]) is int and spline["degree"] == 2,
             "ORIGINAL_QUADRATIC_DEGREE_REQUIRED")
        need(type(spline["knots"]) is list and len(spline["knots"]) == 8 and
             type(spline["controls"]) is list and len(spline["controls"]) == 5,
             "TWO_SPAN_QUADRATIC_CARDINALITY_REQUIRED")
        xs = [rational(x) for x in spline["knots"]]
        k = xs[3]
        need(lo < k < hi and xs == [lo]*3 + [k]*2 + [hi]*3,
             "ORIGINAL_TWO_SPAN_KNOTS_INVALID")
        need(knot is None or knot == k, "ORIGINAL_CHANNEL_KNOTS_DISAGREE")
        knot = k
        controls = [rational(x) for x in spline["controls"]]
        extracted.append(controls)
    # Cox--de Boor for a degree-2 knot of multiplicity two gives the exact
    # Bernstein triples [c0,c1,c2] and [c2,c3,c4]. Both include the real
    # original shared control c2; no independent piece list is accepted.
    return lo, knot, hi, extracted, hashlib.sha256(raw).hexdigest()


def cox_de_boor(knots, controls, x):
    """Independent degree-2 evaluation of the *unsplit* original B-spline.

    Called only for interior rational samples (half-open knot convention).
    This is not an independently sourced oracle for physical machining.
    """
    base = [Q(int(knots[i] <= x < knots[i+1])) for i in range(7)]
    for degree in (1, 2):
        next_basis = []
        for i in range(7-degree):
            left_width = knots[i+degree]-knots[i]
            right_width = knots[i+degree+1]-knots[i+1]
            value = ((x-knots[i])*base[i]/left_width if left_width else Q(0))
            value += ((knots[i+degree+1]-x)*base[i+1]/right_width
                      if right_width else Q(0))
            next_basis.append(value)
        base = next_basis
    need(len(base) == len(controls) == 5 and sum(base) == 1,
         "ORIGINAL_COX_BASIS_PARTITION_FAILED")
    return sum((weight*control for weight,control in zip(base,controls)), Q(0))


def bernstein_global(triple, lo, hi):
    a, b, c = triple
    width = hi - lo
    need(width > 0, "ZERO_WIDTH_SPAN")
    linear = 2 * (b - a) / width
    quadratic = (a - 2*b + c) / (width*width)
    return [a - linear*lo + quadratic*lo*lo,
            linear - 2*quadratic*lo, quadratic]


def evaluate(poly, x):
    return poly[0] + x*(poly[1] + x*poly[2])


def degree(poly):
    return 2 if poly[2] else (1 if poly[1] else (0 if poly[0] else -1))


def exact_roots(poly):
    d = degree(poly)
    if d == -1:
        return None  # identically zero on the entire original source span
    if d == 0:
        return []
    if d == 1:
        return [-poly[0]/poly[1]]
    a, b, c = poly[2], poly[1], poly[0]
    delta = b*b - 4*a*c
    if delta < 0:
        return []
    num, den = isqrt(delta.numerator), isqrt(delta.denominator)
    need(num*num == delta.numerator and den*den == delta.denominator,
         "UNSPLIT_IRRATIONAL_QUADRATIC_ROOT_UNPROVED")
    root = Q(num, den)
    return sorted(set([(-b-root)/(2*a), (-b+root)/(2*a)]))


def order_at(poly, x):
    if evaluate(poly, x):
        return 0
    if poly[1] + 2*poly[2]*x:
        return 1
    need(poly[2] != 0, "NONZERO_POLYNOMIAL_ORDER_UNDEFINED")
    return 2


def analyze(spec):
    lo, knot, hi, channels, binding = source(spec)
    pieces = []
    for i, (a, b) in enumerate(((lo, knot), (knot, hi))):
        triple0 = channels[0][i*2:i*2+3]
        triple1 = channels[1][i*2:i*2+3]
        coeff0 = bernstein_global(triple0, a, b)
        coeff1 = bernstein_global(triple1, a, b)
        physical = [x+y for x,y in zip(coeff0, coeff1)]
        budget(max(max(abs(v.numerator).bit_length(), v.denominator.bit_length())
                   for v in physical) <= 4*MAX_BITS, "INTERMEDIATE_BIT_BUDGET_EXCEEDED")
        # Exact lower/upper and midpoint tests of the actual Bernstein span.
        for x in (a, (2*a+b)/3, (a+b)/2, (a+2*b)/3, b):
            u = (x-a)/(b-a)
            for triple, coeff in ((triple0, coeff0), (triple1, coeff1)):
                need(evaluate(coeff, x) ==
                     triple[0]*(1-u)**2 + 2*triple[1]*u*(1-u) + triple[2]*u*u,
                     "EXTRACTED_BERNSTEIN_IDENTITY_FALSE")
        knots = [lo]*3+[knot]*2+[hi]*3
        for x in ((2*a+b)/3, (a+b)/2, (a+2*b)/3):
            for original, coeff in ((channels[0], coeff0), (channels[1], coeff1)):
                need(evaluate(coeff,x) == cox_de_boor(knots,original,x),
                     "ORIGINAL_COX_SOURCE_EXTRACTION_FAILED")
        roots = exact_roots(physical)
        pieces.append({"lo": a, "hi": b, "poly": physical,
                       "roots": None if roots is None else [x for x in roots if a <= x <= b]})
    need(evaluate(pieces[0]["poly"], knot) ==
         evaluate(pieces[1]["poly"], knot) == channels[0][2]+channels[1][2],
         "ORIGINAL_SHARED_CONTROL_CONTINUITY_FAILED")
    zero_intervals = [[p["lo"], p["hi"]] for p in pieces if p["roots"] is None]
    if len(zero_intervals) == 2:
        zero_intervals = [[lo, hi]]
    candidate_points = sorted({r for p in pieces if p["roots"] is not None for r in p["roots"]})
    points = [r for r in candidate_points if not any(a <= r <= b for a,b in zero_intervals)]
    events = []
    for x in points:
        left = next((p for p in pieces if p["lo"] < x <= p["hi"]), None)
        right = next((p for p in pieces if p["lo"] <= x < p["hi"]), None)
        need(left is not None or right is not None, "ISOLATED_ROOT_OUTSIDE_SOURCE")
        if left is not None:
            need(left["roots"] is not None and evaluate(left["poly"], x) == 0,
                 "FALSE_LEFT_SIDE_ISOLATED_ROOT")
        if right is not None:
            need(right["roots"] is not None and evaluate(right["poly"], x) == 0,
                 "FALSE_RIGHT_SIDE_ISOLATED_ROOT")
        events.append({"coordinate": str(x), "source_knot": x == knot,
                       "left_order": order_at(left["poly"],x) if left else None,
                       "right_order": order_at(right["poly"],x) if right else None,
                       "global_smooth_knot_multiplicity_claimed": False})
    boundaries = sorted(set([lo, knot, hi] + points + [x for span in zero_intervals for x in span]))
    cells = []
    for a,b in zip(boundaries, boundaries[1:]):
        mid = (a+b)/2
        if any(x <= mid <= y for x,y in zero_intervals):
            continue
        p = next((p for p in pieces if p["lo"] < mid < p["hi"]), None)
        need(p is not None, "CELL_NOT_IN_EXACT_SOURCE_PIECE")
        value = evaluate(p["poly"], mid)
        need(value != 0, "UNACCOUNTED_NONZERO_CELL_ROOT")
        sign = "POSITIVE" if value > 0 else "NEGATIVE"
        if cells and cells[-1][1] == a and a not in points and not any(
                x <= a <= y for x,y in zero_intervals):
            need(cells[-1][2] == sign, "NONZERO_KNOT_SIGN_CONFLICT")
            cells[-1] = (cells[-1][0], b, sign)
        else:
            cells.append((a,b,sign))
    zero_set = lambda x: x in points or any(a <= x <= b for a,b in zero_intervals)
    return {"schema": SCHEMA,
            "status": "EXACT_STATIONARY_ORIGINAL_SOURCE_MIXED_COMPONENTS_RESEARCH",
            "evidence_class": "DETERMINISTIC_MODEL",
            "source_sha256": binding,
            "source_parameter_id": spec["source_parameter_id"],
            "original_source_interval": [str(lo),str(hi)],
            "source_knot": str(knot),
            "original_phase_turn_law": {"offset": "0", "rate": "0"},
            "extracted_physical_polynomials_global_t": [
                list(map(str,p["poly"])) for p in pieces],
            "maximal_closed_zero_intervals": [[str(a),str(b)] for a,b in zero_intervals],
            "isolated_zero_points": events,
            "isolated_point_count": len(events),
            "finite_total_root_cardinality": not bool(zero_intervals),
            "nonzero_sign_cells": [{"left": str(a),"right": str(b),
                                    "left_included": a == lo and not zero_set(a),
                                    "right_included": b == hi and not zero_set(b),
                                    "sign": sign} for a,b,sign in cells],
            "historical_v54_dispositions_changed": False,
            "moving_phase_proved": False, "irrational_roots_proved": False,
            "pb00701_certified": False, "mc_b_established": False,
            "mc1_established": False, "production_authorized": False}


def attempt(spec):
    try:
        return analyze(spec)
    except ResourceRefusal as exc:
        return {"schema": SCHEMA, "status": "RESOURCE_REFUSAL", "reason": str(exc),
                "is_truth_value": False, "pb00701_certified": False,
                "mc_b_established": False, "mc1_established": False,
                "production_authorized": False}
    except (Refusal, ValueError, TypeError, KeyError, OverflowError) as exc:
        return {"schema": SCHEMA, "status": "BLOCKED", "reason": str(exc),
                "is_truth_value": False, "pb00701_certified": False,
                "mc_b_established": False, "mc1_established": False,
                "production_authorized": False}
    except (MemoryError, RecursionError) as exc:
        return {"schema": SCHEMA, "status": "RESOURCE_REFUSAL",
                "reason": type(exc).__name__, "is_truth_value": False,
                "pb00701_certified": False, "mc_b_established": False,
                "mc1_established": False, "production_authorized": False}


def validate_report(spec, report):
    checked = attempt(spec)
    if checked.get("status") != "EXACT_STATIONARY_ORIGINAL_SOURCE_MIXED_COMPONENTS_RESEARCH":
        return checked
    try:
        need(type(report) is dict and encode(report) == encode(checked),
             "FORGED_OR_STALE_SOURCE_COMPONENT_REPORT")
        return checked
    except (Refusal, ValueError, TypeError) as exc:
        return {"schema": SCHEMA, "status": "BLOCKED", "reason": str(exc),
                "is_truth_value": False, "mc_b_established": False,
                "production_authorized": False}
