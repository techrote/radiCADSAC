#!/usr/bin/env python3
"""Exact phase-aware physical point/jet composition at a true original knot.

Research-only bounded theorem, not an open-span root solver. No floats, sampling,
timeout truth, synthetic source authority or MC-B gate promotion.
"""
from __future__ import annotations

from fractions import Fraction as Q
import copy
import hashlib
import json

SCHEMA = "radicadsac-pb00701-physical-knot-cyclotomic/1.0"
GRAMMAR = "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE"
SOURCE = {
    "grammar": GRAMMAR, "source_parameter_id": "source-time-t",
    "parameter_lo": "0", "parameter_hi": "2",
    "phase_turn_offset": "0", "phase_turn_rate": "1/4",
    "cos_splines": {
        "0": {"degree": 0, "knots": ["0", "1", "2"],
              "controls": ["0", "1/2"]},
        "1": {"degree": 0, "knots": ["0", "1", "2"],
              "controls": ["1", "0"]},
        "2": {"degree": 0, "knots": ["0", "1", "2"],
              "controls": ["0", "1/2"]},
    },
    "sin_splines": {},
}
SOURCE_SHA256 = "f6f10c779a6837b61fb1276b664f45930958fe7dec80aa484d502592940ccd97"

class Refusal(ValueError):
    pass

class ResourceRefusal(Refusal):
    pass

def need(test, reason):
    if not test:
        raise Refusal(reason)

def budget(test, reason):
    if not test:
        raise ResourceRefusal(reason)

def canonical(obj):
    try:
        return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False).encode("ascii")
    except (TypeError, ValueError, OverflowError) as exc:
        raise Refusal("NONCANONICAL_JSON") from exc

def sha(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()

def rat(token):
    need(type(token) is str and 0 < len(token) <= 128,
         "NONCANONICAL_RATIONAL")
    try:
        x = Q(token)
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise Refusal("NONCANONICAL_RATIONAL") from exc
    need(str(x) == token, "NONCANONICAL_RATIONAL")
    budget(max(abs(x.numerator).bit_length(), x.denominator.bit_length()) <= 160,
           "RATIONAL_BIT_RESOURCE_LIMIT")
    return x

def parse(spec):
    need(type(spec) is dict and set(spec) == {
        "grammar", "source_parameter_id", "parameter_lo", "parameter_hi",
        "phase_turn_offset", "phase_turn_rate", "cos_splines", "sin_splines"
    }, "ORIGINAL_SOURCE_FIELDS_REQUIRED")
    budget(len(canonical(spec)) <= 16384, "SOURCE_BYTE_RESOURCE_LIMIT")
    need(spec["grammar"] == GRAMMAR and
         spec["source_parameter_id"] == "source-time-t",
         "ORIGINAL_GRAMMAR_OR_PARAMETER_MISMATCH")
    need(tuple(rat(spec[k]) for k in ("parameter_lo", "parameter_hi",
                                     "phase_turn_offset", "phase_turn_rate"))
         == (Q(0), Q(2), Q(0), Q(1, 4)),
         "UNSUPPORTED_SOURCE_INTERVAL_OR_PHASE")
    left, right = {}, {}
    for field, is_sine in (("cos_splines", False), ("sin_splines", True)):
        channels = spec[field]
        need(type(channels) is dict and len(channels) <= 5,
             "CHANNEL_MAP_INVALID_OR_RESOURCE_LIMIT")
        for key, spline in channels.items():
            need(type(key) is str and key in ("0", "1", "2", "3", "4"),
                 "HARMONIC_NOT_ADMITTED")
            h = int(key)
            need(not (is_sine and h == 0), "SINE_H0_UNDEFINED")
            need(type(spline) is dict and set(spline) ==
                 {"degree", "knots", "controls"},
                 "ORIGINAL_BSPLINE_FIELDS_REQUIRED")
            need(type(spline["degree"]) is int and spline["degree"] == 0,
                 "NOT_DEGREE_ZERO")
            need(type(spline["knots"]) is list and
                 [rat(x) for x in spline["knots"]] == [Q(0), Q(1), Q(2)],
                 "ORIGINAL_KNOTS_MISMATCH")
            need(type(spline["controls"]) is list and
                 len(spline["controls"]) == 2, "ORIGINAL_CONTROL_COUNT")
            vals = [rat(x) for x in spline["controls"]]
            for i, mapping in enumerate((left, right)):
                old = mapping.get(h, (Q(0), Q(0)))
                mapping[h] = (old[0], vals[i]) if is_sine else (vals[i], old[1])
    return left, right

def quarter_cos(n):
    return (1, 0, -1, 0)[n % 4]

def quarter_sin(n):
    return (0, 1, 0, -1)[n % 4]

def point_jet(channels):
    """d^n F(1)/dt^n divided by (pi/2)^n; exact rational.

    If k positive frequencies are active, plus optionally H0, D=2k+e
    distinct exponentials span the function. First D jets all zero => identity
    by Vandermonde invertibility. Thus first nonzero order is <=D-1.
    This is a mathematically terminating degree-aware bound, NOT a time budget.
    """
    active = {h: (c, s) for h, (c, s) in channels.items() if c or s}
    d = 2 * sum(h > 0 for h in active) + int(0 in active)
    budget(d <= 9, "DERIVATIVE_DEGREE_RESOURCE_LIMIT")
    scaled = []
    for n in range(d):
        value = sum((Q(h**n) *
                     (c * quarter_cos(h+n) + s * quarter_sin(h+n))
                     for h, (c, s) in active.items()), Q(0))
        scaled.append(value)
    indices = [i for i, value in enumerate(scaled) if value]
    if not indices:
        # Whole analytic piece identity, not a finite isolated root list.
        return {"status": "IDENTITY_ZERO", "point_value": "0",
                "first_nonzero_order": None, "first_nonzero_scaled": None,
                "derivatives_scaled_by_pi_over_2": [str(x) for x in scaled],
                "finite_vandermonde_dimension": d, "germ_sign_left": 0,
                "germ_sign_right": 0}
    order = indices[0]
    nonzero = scaled[order]
    sign = (nonzero > 0) - (nonzero < 0)
    # Taylor leading coefficient = nonzero*(pi/2)^order/order!:
    # positive dimensional factor, so only parity flips sign on left.
    return {"status": "EXACT_POINT_JET",
            "point_value": str(scaled[0]),
            "first_nonzero_order": order,
            "first_nonzero_scaled": str(nonzero),
            "derivatives_scaled_by_pi_over_2": [str(x) for x in scaled],
            "finite_vandermonde_dimension": d,
            "germ_sign_left": sign * (-1)**order,
            "germ_sign_right": sign}

def analyze(spec):
    a, b = parse(spec)
    left, right = point_jet(a), point_jet(b)
    continuity = left["point_value"] == right["point_value"]
    harmonics = sorted(set(a) | set(b))
    equal_coeffs = all(a.get(h, (Q(0), Q(0))) ==
                       b.get(h, (Q(0), Q(0))) for h in harmonics)
    return {
        "schema": SCHEMA, "status": "EXACT_PHASE_AWARE_ORIGINAL_KNOT_POINT_JETS",
        "source_sha256": sha(spec), "evidence_class": "DETERMINISTIC_MODEL",
        "original_parameter": "source-time-t", "source_interval": ["0", "2"],
        "true_original_knot": "1", "phase_turn_at_knot": "1/4",
        "point_policy": "RIGHT_CONTINUOUS_INTERNAL_WITH_TERMINAL_CLAMP",
        "left_analytic": left, "right_analytic": right,
        "fourier_channels_coefficientwise_equal": equal_coeffs,
        "physical_knot_continuous": continuity,
        "actual_knot_value": right["point_value"],
        "actual_knot_zero": right["point_value"] == "0",
        "left_adjacent_sign": left["germ_sign_left"],
        "right_adjacent_sign": right["germ_sign_right"],
        "left_one_sided_zero_order": (
            left["first_nonzero_order"]
            if left["point_value"] == "0" else None),
        "right_one_sided_zero_order": (
            right["first_nonzero_order"]
            if right["point_value"] == "0" else None),
        "physical_zero_set_outside_knot_determined": False,
        "global_smooth_knot_multiplicity_claimed": False,
        "historical_v54_admitted": False, "pb00701_certified": False,
        "mc_b_established": False, "mc1_established": False,
        "native_step_qualified": False, "production_authorized": False,
    }

def nontruth(reason, resource=False):
    return {"schema": SCHEMA,
            "status": "RESOURCE_REFUSAL" if resource else "BLOCKED",
            "reason": reason, "is_truth_value": False,
            "pb00701_certified": False, "mc_b_established": False,
            "mc1_established": False, "production_authorized": False}

def attempt(spec):
    try:
        return analyze(spec)
    except ResourceRefusal as exc:
        return nontruth(str(exc), True)
    except (Refusal, ValueError, TypeError, KeyError, IndexError,
            ZeroDivisionError) as exc:
        return nontruth(str(exc))
    except (MemoryError, RecursionError, OverflowError) as exc:
        return nontruth(type(exc).__name__, True)

def validate_report(spec, submitted):
    try:
        raw = canonical(submitted)
        budget(len(raw) <= 65536, "SUBMITTED_REPORT_RESOURCE_LIMIT")
        result = attempt(spec)
        need(result.get("status") == "EXACT_PHASE_AWARE_ORIGINAL_KNOT_POINT_JETS",
             "SOURCE_KNOT_POINT_PROOF_MISSING")
        need(raw == canonical(result), "FORGED_PHASE_AWARE_KNOT_REPORT")
        return result
    except ResourceRefusal as exc:
        return nontruth(str(exc), True)
    except (Refusal, TypeError, ValueError) as exc:
        return nontruth(str(exc))

def negative_c():
    need(sha(SOURCE) == SOURCE_SHA256, "PRIMARY_ORIGINAL_SOURCE_SHA_DRIFT")
    r = analyze(SOURCE)
    need(r["physical_knot_continuous"] is True and
         r["fourier_channels_coefficientwise_equal"] is False and
         r["actual_knot_zero"] is True and
         (r["left_one_sided_zero_order"],
          r["right_one_sided_zero_order"]) == (1, 2) and
         (r["left_adjacent_sign"], r["right_adjacent_sign"]) == (1, 1),
         "EXACT_KNOT_CONTINUITY_COUNTEREXAMPLE_FAILED")
    return {
        "schema": SCHEMA, "status": "EXACT_SOURCE_BOUND_NEGATIVE_C",
        "claim": "C_FOURIER_COEFFICIENT_MATCH_NOT_NECESSARY_FOR_PHYSICAL_KNOT_CONTINUITY",
        "evidence_class": "DETERMINISTIC_MODEL",
        "primary_original_source_sha256": SOURCE_SHA256,
        "source_bound_knot_certificate": r,
        "complete_original_source_zero_set": ["1"],
        "complete_original_source_zero_set_justification":
            "cos(pi*t/2) strictly positive on [0,1); "
            "cos^2(pi*t/2) positive on (1,2], exactly zero at 1",
        "left_original_piece_identity": "cos(pi*t/2)",
        "right_original_piece_identity": "(1+cos(pi*t))/2=cos^2(pi*t/2)",
        "historical_corpus_denominator_before_after": [121, 121],
        "historical_route_refusals_before_after": [20, 20],
        "historical_missing_ordered_premises_before_after": [30, 30],
        "qualified_source_specific_before_after": [50, 50],
        "new_historical_ids_resolved": [],
        "general_analytic_event_decision_established": False,
        "no_general_solver_impossibility_claim": True,
        "pb00701_certified": False, "mc_b_established": False,
        "mc1_established": False, "production_authorized": False,
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    options = parser.parse_args()
    if not options.contract:
        parser.error("specify --contract")
    print(json.dumps(negative_c(), sort_keys=True))
