#!/usr/bin/env python3
"""MC-038: conditional COMPLETE single nontransverse root in an exact trig span.

Combine independently existing exact cyclotomic rational-point derivative jets
with a global rational derivative enclosure and a finite rational zero-free
outer partition. Never treat a point jet alone as a whole-span root count.
Research-only, no historical V27/V41 or native/MC-B authority.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as Q
from math import comb
from pathlib import Path

import pb00701_rational_phase_point as point
import pb00701_transverse_trig_interval as interval

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[3]
SCHEMA = "radicadsac-pb00701-jet-guarded-nontransverse/1.0"
SOURCE_SCHEMA = "radicadsac-pb00701-exact-original-trig-span/1.0"
MAX_CERT_BYTES = 16384
PINS = {
    TASK / "pb00701_rational_phase_point.py":
        "9fc344e045fa800fb24d30902a641e534a1e197b",
    TASK / "pb00701_transverse_trig_interval.py":
        "2320f92efe4316d865a89f6d848737e2c000ca4d",
    TASK / "pb00701-finite-owner-corpus-v54.json":
        "5841c331579489b25caef38cd412bdbf286f9134",
    ROOT / "research/machining-completeness/tasks/MC-002/domain-contract-v1.json":
        "23de82f5240a72509f7afe4acd5948b65bc4ff13",
    ROOT / "handoffs/current-authority.json":
        "fa0233323a0804d8a5d3eb7cd892a274a6173fab",
}

class Refusal(ValueError):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason

def require(ok, reason):
    if not ok:
        raise Refusal(reason)

def canonical(obj):
    try:
        return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False)
    except (TypeError, ValueError, OverflowError) as exc:
        raise Refusal("NONJSON_OR_NONFINITE_EVIDENCE") from exc

def pins():
    for path, expected in PINS.items():
        raw = path.read_bytes()
        got = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(got == expected, "ORIGINAL_PRODUCER_OR_FROZEN_SOURCE_DRIFT:" + path.name)

def rat(s):
    require(type(s) is str and 0 < len(s) <= 128,
            "NONCANONICAL_OR_UNBOUNDED_RATIONAL_TYPE")
    try:
        x = interval.formal_rational(s)
    except (interval.Refusal, ValueError, ZeroDivisionError, OverflowError) as exc:
        raise Refusal("INVALID_EXACT_RATIONAL") from exc
    require(str(x) == s, "NONCANONICAL_EXACT_RATIONAL")
    return x

def source_span(source):
    """Use all rational polynomial harmonic channels, no selected-leaf inference."""
    require(type(source) is dict and set(source) == {
        "schema", "source_parameter_id", "source_interval",
        "phase_turns", "harmonics"}, "UNREVIEWED_OR_MISSING_ORIGINAL_SOURCE_FIELD")
    require(len(canonical(source)) <= 8192 and
            source["schema"] == SOURCE_SCHEMA and
            source["source_parameter_id"] == "source-time-t",
            "UNSUPPORTED_ORIGINAL_SOURCE_GRAMMAR_OR_IDENTITY")
    endpoints, phase, harmonics = (source[k] for k in
                                  ("source_interval", "phase_turns", "harmonics"))
    require(type(endpoints) is list and len(endpoints) == 2 and
            type(phase) is list and len(phase) == 2 and
            type(harmonics) is dict and 1 <= len(harmonics) <= 8,
            "UNSUPPORTED_SOURCE_INTERVAL_PHASE_OR_HARMONICS")
    left, right = (rat(x) for x in endpoints)
    offset, rate = (rat(x) for x in phase)
    terms = {}
    for key, term in harmonics.items():
        require(type(key) is str and key.isascii() and key.isdecimal() and
                len(key) <= 2 and str(int(key)) == key and
                type(term) is dict and set(term) == {"cos", "sin"},
                "UNSUPPORTED_HARMONIC_OR_CHANNEL_GRAMMAR")
        h = int(key)
        co, si = term["cos"], term["sin"]
        require(type(co) is list and type(si) is list and
                1 <= len(co) <= 4 and 1 <= len(si) <= 4,
                "UNSUPPORTED_POLYNOMIAL_DEGREE_OR_TYPE")
        terms[h] = (tuple(rat(x) for x in co), tuple(rat(x) for x in si))
        if h == 0:
            require(all(x == 0 for x in terms[h][1]),
                    "ZERO_HARMONIC_SINE_CHANNEL_NOT_CANONICAL")
    try:
        span = interval.Span(left, right, offset, rate, terms)
    except interval.Refusal as exc:
        raise Refusal(str(exc)) from exc
    require(point.span_binding(span) ==
            point.span_binding(interval.Span(left, right, offset, rate, terms)),
            "RELOWERED_ORIGINAL_SOURCE_CHANGED")
    return span

def derivative_limit(span, derivative_order):
    """Prove global |F^(k)| <= M_k by Leibniz, |sin|,|cos|<=1, 2pi<44/7."""
    require(type(derivative_order) is int and
            1 <= derivative_order <= 7, "DERIVATIVE_ORDER_RESOURCE_LIMIT")
    radius = max(Q(1), abs(span.left), abs(span.right))
    result = Q(0)
    for h, (cos, sin) in span.terms.items():
        c, s = cos, sin
        omega = Q(44, 7) * abs(h * span.rate)
        for j in range(derivative_order+1):
            result += comb(derivative_order, j) * omega**(
                derivative_order-j) * (
                    interval.norm_bound(c, radius) + interval.norm_bound(s, radius))
            c, s = interval.derivative(c), interval.derivative(s)
        require(result.numerator.bit_length() <= 8192 and
                result.denominator.bit_length() <= 8192,
                "DERIVATIVE_ENVELOPE_RESOURCE_LIMIT")
    return result

def no_root_cover(span, left, right, sign, m1, budget):
    """Finite exhaustive closed dyadic cell cover, not sampled signs."""
    cells = []
    node_count = 0
    max_seen_depth = 0

    def visit(a, b, depth):
        nonlocal node_count, max_seen_depth
        node_count += 1
        max_seen_depth = max(depth, max_seen_depth)
        if node_count > budget["max_nodes"]:
            raise Refusal("DYADIC_NODE_RESOURCE_LIMIT")
        mid, radius = (a+b)/2, (b-a)/2
        enclosure = interval.widen(span.evaluate(mid), m1*radius)
        tested = interval.strict_sign(enclosure)
        if tested == sign:
            cells.append({
                "source_interval": [str(a), str(b)],
                "complete_value_enclosure": [str(enclosure[0]),str(enclosure[1])],
                "strict_sign": sign,
            })
            return
        if tested and tested != sign:
            raise Refusal("OUTER_ROOT_FREE_COVER_CONTRADICTS_JET_PARITY")
        if depth >= budget["max_depth"]:
            raise Refusal("OUTER_ROOT_FREE_COVER_DEPTH_EXHAUSTED")
        visit(a, mid, depth+1)
        visit(mid, b, depth+1)

    visit(left, right, 0)
    require(cells[0]["source_interval"][0] == str(left) and
            cells[-1]["source_interval"][1] == str(right) and
            all(cells[i]["source_interval"][1] ==
                cells[i+1]["source_interval"][0]
                for i in range(len(cells)-1)),
            "OUTER_SOURCE_INTERVAL_COVER_INCOMPLETE")
    return {
        "source_interval": [str(left), str(right)],
        "strict_sign": sign,
        "cells": len(cells), "nodes": node_count,
        "maximum_depth": max_seen_depth,
        "full_cell_certificate_sha256":
            hashlib.sha256(canonical(cells).encode("ascii")).hexdigest(),
        "first_cell": cells[0], "last_cell": cells[-1],
    }

def prove(source, root, guard, *, max_order=4, max_depth=18, max_nodes=20000):
    pins()
    span = source_span(source)
    root = rat(root)
    require(type(guard) is list and len(guard) == 2, "INVALID_GUARD_TYPE")
    a, b = (rat(v) for v in guard)
    require(span.left < a < root < b < span.right,
            "GUARD_DOES_NOT_COVER_ONE_STRICT_INTERIOR_ROOT")
    require(type(max_order) is int and 2 <= max_order <= 6 and
            type(max_depth) is int and 0 <= max_depth <= 18 and
            type(max_nodes) is int and 1 <= max_nodes <= 20000,
            "INVALID_PROOF_RESOURCE_BUDGET")
    event = point.point(span, root, max_order=max_order)
    require(event["status"] == "EXACT_RATIONAL_POINT_EVENT" and
            event["source_binding_sha256"] == point.span_binding(span) and
            event["coordinate"] == str(root) and
            event["first_nonzero_derivative_order"] >= 2,
            "EXACT_NONTRANSVERSE_RATIONAL_POINT_JET_NOT_ESTABLISHED")
    m, sign = event["one_sided_order"], event["first_nonzero_derivative_sign"]
    require(m <= max_order and sign in (-1, 1) and
            event["exact_vanishing_derivatives"] == list(range(m)),
            "INCOMPLETE_EXACT_DERIVATIVE_JET")
    m1 = derivative_limit(span, 1)
    upper_next = derivative_limit(span, m+1)
    distance = max(root-a, b-root)
    center_enclosure = point.derivative_interval(span, root, m)
    guard_enclosure = interval.widen(center_enclosure, upper_next*distance)
    require(interval.strict_sign(guard_enclosure) == sign,
            "LOCAL_MTH_DERIVATIVE_SIGN_UNDECIDED")
    # Taylor's integral remainder: all derivatives below m vanish at r.
    # With F^(m) sign constant on the WHOLE guard, sign(F(s)) equals
    # sign(F^(m)) * sign(s-r)^m for every s != r in that guard.
    sign_left = sign if m % 2 == 0 else -sign
    sign_right = sign
    require(event["left_sign"] == sign_left and
            event["right_sign"] == sign_right and
            event["event_kind"] == ("TANGENCY" if m % 2 == 0 else "CROSSING"),
            "NONTRANSVERSE_POINT_PARITY_DISAGREES_WITH_TAYLOR_GUARD")
    require(interval.strict_sign(span.evaluate(a)) == sign_left and
            interval.strict_sign(span.evaluate(b)) == sign_right and
            interval.strict_sign(span.evaluate(span.left)) == sign_left and
            interval.strict_sign(span.evaluate(span.right)) == sign_right,
            "SOURCE_OR_GUARD_ENDPOINT_SIGN_UNPROVED")
    budget = {"max_nodes": max_nodes, "max_depth": max_depth}
    left_cover = no_root_cover(span, span.left, a, sign_left, m1, budget)
    right_cover = no_root_cover(span, b, span.right, sign_right, m1, budget)
    require(left_cover["nodes"] + right_cover["nodes"] <= max_nodes,
            "COMBINED_OUTER_COVER_NODE_RESOURCE_LIMIT")
    # Exactly three contiguous regions (left no-root, guarded m-th-order root,
    # right no-root) cover every point of the original closed source span.
    pins()
    return {
        "schema": SCHEMA,
        "status": "COMPLETE_ONE_NONTRANSVERSE_ORIGINAL_SPAN_ROOT_RESEARCH",
        "evidence_class": "DETERMINISTIC_MODEL",
        "source_parameter_id": source["source_parameter_id"],
        "source_record_sha256": hashlib.sha256(
            canonical(source).encode("ascii")).hexdigest(),
        "canonical_source_binding_sha256": point.span_binding(span),
        "source_interval": [str(span.left), str(span.right)],
        "phase_turns": [str(span.offset), str(span.rate)],
        "certified_exact_rational_root": str(root),
        "certified_exact_multiplicity": m,
        "event_kind": event["event_kind"],
        "root_left_sign": sign_left, "root_right_sign": sign_right,
        "original_source_end_signs": [sign_left, sign_right],
        "global_abs_derivative_1_bound": str(m1),
        "global_abs_derivative_m_plus_1_bound": str(upper_next),
        "guard": [str(a), str(b)],
        "guard_mth_derivative_enclosure":
            [str(guard_enclosure[0]), str(guard_enclosure[1])],
        "guard_derivative_strict_sign": sign,
        "point_derivative_jet": event,
        "zero_free_left_cover": left_cover,
        "zero_free_right_cover": right_cover,
        "complete_open_root_count": 1,
        "complete_open_source_signs": [sign_left, sign_right],
        "root_coordinate_is_exact_rational": True,
        "certificate_dispositions_historical_changed": False,
        "frozen_v54_source_admitted": False,
        "general_v27_v41_trig_owner_certified": False,
        "pb00701_certified": False,
        "mc_b_established": False, "mc1_established": False,
        "native_brep_or_step_qualified": False,
        "production_authorized": False,
    }

def nontruth(reason, status="BLOCKED"):
    return {"schema": SCHEMA, "status": status, "reason": reason,
            "is_truth_value": False,
            "historical_child_certified": False, "mc_b_established": False,
            "production_authorized": False}

def attempt(source, root, guard, *, max_order=4, max_depth=18, max_nodes=20000):
    try:
        return prove(source, root, guard, max_order=max_order,
                     max_depth=max_depth, max_nodes=max_nodes)
    except (Refusal, point.Refusal, interval.Refusal, ValueError, KeyError,
            IndexError, TypeError, ZeroDivisionError, OverflowError) as exc:
        reason = str(exc)
        status = ("RESOURCE_REFUSAL" if any(tag in reason for tag in
                  ("RESOURCE", "UNDECIDED", "UNRESOLVED", "EXHAUSTED"))
                  else "BLOCKED")
        return nontruth(reason, status)
    except (MemoryError, RecursionError) as exc:
        return nontruth(type(exc).__name__, "RESOURCE_REFUSAL")

def validate_report(source, root, guard, submitted, **budget):
    try:
        claimed = canonical(submitted)
        if len(claimed) > MAX_CERT_BYTES:
            return nontruth("SUBMITTED_REPORT_RESOURCE_LIMIT", "RESOURCE_REFUSAL")
        checked = attempt(source, root, guard, **budget)
        require(checked.get("status") ==
                "COMPLETE_ONE_NONTRANSVERSE_ORIGINAL_SPAN_ROOT_RESEARCH",
                "EXACT_COMPLETE_SOURCE_PROOF_MISSING")
        require(claimed == canonical(checked),
                "FORGED_NONTRANSVERSE_COMPLETE_ROOT_REPORT")
        return checked
    except (Refusal, ValueError, TypeError, OverflowError) as exc:
        return nontruth(str(exc))
    except (MemoryError, RecursionError) as exc:
        return nontruth(type(exc).__name__, "RESOURCE_REFUSAL")
