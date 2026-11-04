#!/usr/bin/env python3
"""Exact source-bound falsifier for a proposed moving-phase knot composition shortcut.

DETERMINISTIC_MODEL negative research, NOT a general PB-007 proof route.
Every zero/order claim below follows from exact original B-spline polynomial
identities and the elementary, full-interval zeros of sine and cosine.
"""
from __future__ import annotations

import copy
import hashlib
import json
from fractions import Fraction as Q

SCHEMA = "radicadsac-pb00701-moving-phase-knot-falsifier/1.0"
GRAMMAR = "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE"
MAX_BYTES = 16384
MAX_BITS = 96
KNOTS = ["-1", "-1", "-1", "0", "0", "1", "1", "1"]
SOURCE = {
    "grammar": GRAMMAR,
    "source_parameter_id": "source-time-t",
    "parameter_lo": "-1",
    "parameter_hi": "1",
    "phase_turn_offset": "0",
    "phase_turn_rate": "1",
    "cos_splines": {
        "0": {"degree": 2, "knots": KNOTS,
              "controls": ["1/2", "0", "0", "0", "1/2"]},
        "1": {"degree": 2, "knots": KNOTS,
              "controls": ["1/2", "0", "0", "0", "-1/2"]},
    },
    "sin_splines": {},
}


class Refusal(ValueError):
    pass


class ResourceRefusal(Refusal):
    pass


def need(condition, reason):
    if not condition:
        raise Refusal(reason)


def canonical(value):
    try:
        return json.dumps(value, ensure_ascii=True, allow_nan=False,
                          sort_keys=True, separators=(",", ":")).encode("ascii")
    except (TypeError, ValueError, OverflowError) as exc:
        raise Refusal("NONCANONICAL_JSON") from exc


def bounded(value):
    raw = canonical(value)
    if len(raw) > MAX_BYTES:
        raise ResourceRefusal("SOURCE_OR_REPORT_SIZE_LIMIT")
    return raw


def rational(raw):
    need(type(raw) is str and 0 < len(raw) <= 128, "RATIONAL_TOKEN_INVALID")
    try:
        x = Q(raw)
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise Refusal("RATIONAL_TOKEN_INVALID") from exc
    need(str(x) == raw, "NONCANONICAL_RATIONAL")
    if max(abs(x.numerator).bit_length(), x.denominator.bit_length()) > MAX_BITS:
        raise ResourceRefusal("RATIONAL_BIT_LIMIT")
    return x


def source_binding(spec):
    raw = bounded(spec)
    need(type(spec) is dict and set(spec) == set(SOURCE),
         "ORIGINAL_SOURCE_FIELD_SET_CHANGED")
    need(spec["grammar"] == GRAMMAR and
         spec["source_parameter_id"] == "source-time-t",
         "ORIGINAL_SOURCE_IDENTITY_CHANGED")
    need(rational(spec["parameter_lo"]) == -1 and
         rational(spec["parameter_hi"]) == 1 and
         rational(spec["phase_turn_offset"]) == 0 and
         rational(spec["phase_turn_rate"]) == 1,
         "ORIGINAL_SOURCE_INTERVAL_OR_PHASE_CHANGED")
    need(type(spec["sin_splines"]) is dict and not spec["sin_splines"],
         "ORIGINAL_SOURCE_SINE_CHANNELS_CHANGED")
    need(type(spec["cos_splines"]) is dict and set(spec["cos_splines"]) == {"0", "1"},
         "ORIGINAL_SOURCE_HARMONICS_CHANGED")
    for harmonic in ("0", "1"):
        data = spec["cos_splines"][harmonic]
        need(type(data) is dict and set(data) == {"degree", "knots", "controls"}
             and type(data["degree"]) is int and data["degree"] == 2,
             "ORIGINAL_SPLINE_FORM_CHANGED")
        need(type(data["knots"]) is list and len(data["knots"]) == 8 and
             type(data["controls"]) is list and len(data["controls"]) == 5,
             "ORIGINAL_SPLINE_CARDINALITY_CHANGED")
        need([rational(x) for x in data["knots"]] ==
             [-1, -1, -1, 0, 0, 1, 1, 1],
             "ORIGINAL_SOURCE_KNOTS_CHANGED")
        expected = [Q(x) for x in SOURCE["cos_splines"][harmonic]["controls"]]
        need([rational(x) for x in data["controls"]] == expected,
             "ORIGINAL_SOURCE_COEFFICIENTS_CHANGED")
    need(raw == bounded(SOURCE), "ORIGINAL_SOURCE_CANONICAL_BYTES_CHANGED")
    return hashlib.sha256(raw).hexdigest()


def poly_add(a, b):
    return tuple((a[i] if i < len(a) else Q(0)) +
                 (b[i] if i < len(b) else Q(0))
                 for i in range(max(len(a), len(b))))


def poly_mul(a, b):
    out = [Q(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return tuple(out)


def poly_eval(p, t):
    total = Q(0)
    for a in reversed(p):
        total = total * t + a
    return total


def piece_poly(controls, lo, hi):
    """Exact global-t polynomial, not a sampled approximation."""
    width = hi - lo
    need(width > 0, "BAD_SPAN_WIDTH")
    s = (Q(-lo, 1) / width, Q(1) / width)
    one_minus_s = poly_add((Q(1),), tuple(-x for x in s))
    basis = (
        poly_mul(one_minus_s, one_minus_s),
        tuple(2*x for x in poly_mul(s, one_minus_s)),
        poly_mul(s, s)
    )
    poly = (Q(0), Q(0), Q(0))
    for c, b in zip(controls, basis):
        poly = poly_add(poly, tuple(c*x for x in b))
    return poly


def cox_de_boor(knots, controls, t):
    """Independent rational original-spline evaluation at interior checkpoints."""
    base = [Q(int(knots[i] <= t < knots[i+1])) for i in range(7)]
    for degree in (1, 2):
        next_base = []
        for i in range(7-degree):
            a = knots[i+degree] - knots[i]
            b = knots[i+degree+1] - knots[i+1]
            left = (t-knots[i])*base[i]/a if a else Q(0)
            right = (knots[i+degree+1]-t)*base[i+1]/b if b else Q(0)
            next_base.append(left + right)
        base = next_base
    need(len(base) == 5 and sum(base) == 1, "COX_DE_BOOR_PARTITION_FAILED")
    return sum((c*w for c, w in zip(controls, base)), Q(0))


def exact_source_coefficients(spec):
    source_sha = source_binding(spec)
    lowered = {}
    for harmonic in ("0", "1"):
        data = spec["cos_splines"][harmonic]
        controls = [rational(x) for x in data["controls"]]
        knots = [rational(x) for x in data["knots"]]
        left = piece_poly(controls[:3], Q(-1), Q(0))
        right = piece_poly(controls[2:], Q(0), Q(1))
        for t in (Q(-3,4), Q(-1,2), Q(-1,4), Q(1,4), Q(1,2), Q(3,4)):
            expected = poly_eval(left if t < 0 else right, t)
            need(cox_de_boor(knots, controls, t) == expected,
                 "ORIGINAL_COX_DE_BOOR_LOWERING_DISAGREES")
        need(poly_eval(left, Q(0)) == poly_eval(right, Q(0)),
             "ORIGINAL_SOURCE_KNOT_DISCONTINUITY")
        lowered[harmonic] = (left, right)
    expected_base = (Q(0), Q(0), Q(1,2))
    need(lowered["0"] == (expected_base, expected_base),
         "ORIGINAL_C0_POLYNOMIAL_IDENTITY_FAILED")
    need(lowered["1"] == (expected_base, tuple(-x for x in expected_base)),
         "ORIGINAL_C1_POLYNOMIAL_IDENTITY_FAILED")
    return source_sha, lowered


def analyze(spec):
    source_sha, lowered = exact_source_coefficients(spec)
    # Coefficient identities hold as polynomials on the *entire* open span.
    # cos(2x) = 2*cos(x)^2-1 and 1-cos(2x) = 2*sin(x)^2.
    # Hence moving phase beta=t yields F_L=t^2*cos(pi*t)^2 and
    # F_R=t^2*sin(pi*t)^2. On [-1,0], cos(pi*t)=0 exactly
    # at t=-1/2; on [0,1], sin(pi*t)=0 exactly at 0 and 1.
    # At t=-1/2 cosine has a simple zero; t^2 is nonzero: order 2.
    # At t=0, left cosine is nonzero: left order 2; right sine
    # has a simple zero *and* t^2 vanishes: right order 4.
    # At t=1, t^2 is nonzero and sine has a simple zero: order 2.
    # Squared factors are positive between these exact zero positions.
    # No float evaluation, approximate root-search or timeout is used.
    report = {
        "schema": SCHEMA,
        "status": "EXACT_SOURCE_BOUND_COUNTEREXAMPLE",
        "evidence_class": "DETERMINISTIC_MODEL",
        "source_sha256": source_sha,
        "source_parameter_id": spec["source_parameter_id"],
        "source_interval": ["-1", "1"],
        "original_true_knots": ["0"],
        "global_phase_turn_law": {"offset": "0", "rate": "1"},
        "source_coefficient_polynomials_global_t": {
            "harmonic_0": [["0", "0", "1/2"], ["0", "0", "1/2"]],
            "harmonic_1": [["0", "0", "1/2"], ["0", "0", "-1/2"]],
        },
        "moving_physical_pieces": [
            {"interval": ["-1", "0"], "identity": "t^2*cos(pi*t)^2"},
            {"interval": ["0", "1"], "identity": "t^2*sin(pi*t)^2"},
        ],
        "moving_zero_set_kind": "FINITE_DISTINCT_CLOSED_SOURCE_ROOTS",
        "moving_distinct_zero_coordinates": ["-1/2", "0", "1"],
        "moving_distinct_root_count": 3,
        "moving_positive_components": [
            {"lo": "-1", "hi": "-1/2", "left_closed": True, "right_closed": False},
            {"lo": "-1/2", "hi": "0", "left_closed": False, "right_closed": False},
            {"lo": "0", "hi": "1", "left_closed": False, "right_closed": False},
        ],
        "moving_events": [
            {"source_t": "-1/2", "kind": "TOUCHING",
             "position": "STRICT_LEFT_SPAN_INTERIOR",
             "order": 2, "left_sign": 1, "right_sign": 1},
            {"source_t": "0", "kind": "SOURCE_KNOT_TOUCHING",
             "position": "TRUE_ORIGINAL_SOURCE_KNOT",
             "left_one_sided_order": 2, "right_one_sided_order": 4,
             "left_sign": 1, "right_sign": 1,
             "global_smooth_multiplicity": None},
            {"source_t": "1", "kind": "RIGHT_EXTERIOR_ZERO",
             "position": "ORIGINAL_RIGHT_EXTERIOR",
             "right_inward_order": 2, "inward_sign": 1},
        ],
        "stationary_counterfactual": {
            "source_mutation": "ONLY_PHASE_TURN_RATE_1_TO_0",
            "phase_turn_offset": "0", "phase_turn_rate": "0",
            "left_piece": "t^2", "right_piece": "0",
            "zero_set_kind": "CLOSED_ZERO_CONTINUUM",
            "closed_zero_components": [["0", "1"]],
            "isolated_root_count": 0, "finite_total_root_count": None,
            "positive_components": [["-1", "0"]],
        },
        "falsified_transfer_rules": [
            "STATIONARY_ZERO_COMPONENTS_ARE_PHASE_INVARIANT",
            "TRUE_ORIGINAL_KNOT_REQUIRES_ONE_GLOBAL_SMOOTH_MULTIPLICITY",
            "ALL_MOVING_SQUARED_AMPLITUDE_KNOT_ZEROS_HAVE_ORDER_TWO",
        ],
        "general_impossibility_claimed": False,
        "frozen_v54_corpus_modified": False,
        "historical_121_source_denominator": 121,
        "historical_route_refusals": 20,
        "historical_missing_ordered_premises": 30,
        "before_complete_fifty_source_supplemental_proofs": 50,
        "after_complete_fifty_source_supplemental_proofs": 50,
        "historical_source_closure_delta": 0,
        "named_original_historical_source_case_ids_added": [],
        "pb00701_certified": False,
        "pb00702_certified": False,
        "pb00703_certified": False,
        "pb00704_certified": False,
        "mc_b_established": False,
        "mc1_established": False,
        "native_brep_or_step_qualified": False,
        "production_authorized": False,
    }
    need([str(x) for x in lowered["0"][0]] == ["0", "0", "1/2"],
         "ORIGINAL_REPLAY_INCONSISTENT")
    return report


def refusal(reason, resource=False):
    return {"schema": SCHEMA, "status": "RESOURCE_REFUSAL" if resource else "BLOCKED",
            "reason": str(reason)[:300], "is_truth_value": False,
            "pb00701_certified": False, "mc_b_established": False,
            "mc1_established": False, "production_authorized": False}


def attempt(spec):
    try:
        return analyze(spec)
    except ResourceRefusal as exc:
        return refusal(exc, True)
    except (Refusal, TypeError, ValueError, KeyError, ZeroDivisionError, OverflowError) as exc:
        return refusal(exc)
    except (MemoryError, RecursionError) as exc:
        return refusal(type(exc).__name__, True)


def validate_report(spec, candidate):
    try:
        fresh = attempt(spec)
        need(fresh.get("status") == "EXACT_SOURCE_BOUND_COUNTEREXAMPLE",
             "FRESH_SOURCE_PROOF_NOT_ESTABLISHED")
        need(bounded(candidate) == bounded(fresh),
             "FORGED_OR_STALE_COUNTEREXAMPLE_REPORT")
        return fresh
    except ResourceRefusal as exc:
        return refusal(exc, True)
    except (Refusal, ValueError, TypeError, KeyError) as exc:
        return refusal(exc)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.json):
        parser.error("select --contract and/or --json")
    result = analyze(SOURCE)
    if args.contract:
        assert validate_report(SOURCE, result) == result
        assert result["historical_source_closure_delta"] == 0
        assert result["moving_events"][1]["left_one_sided_order"] == 2
        assert result["moving_events"][1]["right_one_sided_order"] == 4
        print("PASS: exact original moving-phase two-span (2,4) knot falsifier")
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
