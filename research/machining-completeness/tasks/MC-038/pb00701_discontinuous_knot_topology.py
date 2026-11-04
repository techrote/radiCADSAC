#!/usr/bin/env python3
"""Exact bounded degree-zero original-source knot zero topology; research only.

Both affine phase endpoints must be strictly within the positive cosine sector.
The source's original piece limits do NOT imply a value at a discontinuous knot.
"""
from __future__ import annotations

from fractions import Fraction as Q
import copy
import hashlib
import json

SCHEMA = "radicadsac-mc038-discontinuous-knot-topology/1.0"
GRAMMAR = "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE"
RIGHT = "RIGHT_CONTINUOUS_INTERNAL_WITH_TERMINAL_CLAMP"
LEFT = "LEFT_CONTINUOUS_INTERNAL_COUNTERFACTUAL"
SOURCE = {
    "grammar": GRAMMAR, "source_parameter_id": "source-time-t",
    "parameter_lo": "0", "parameter_hi": "2",
    "phase_turn_offset": "0", "phase_turn_rate": "1/16",
    "cos_splines": {"1": {"degree": 0, "knots": ["0", "1", "2"],
                           "controls": ["0", "1"]}},
    "sin_splines": {},
}
SOURCE_SHA = "4860a921cea8332762d2db3f5aaeafa286593b230299f44d07ffc3a9bbcbd136"


class Refusal(ValueError):
    pass


class ResourceRefusal(Refusal):
    pass


def need(ok, reason):
    if not ok:
        raise Refusal(reason)


def budget(ok, reason):
    if not ok:
        raise ResourceRefusal(reason)


def canonical(obj):
    try:
        return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False).encode("ascii")
    except (TypeError, ValueError, OverflowError) as e:
        raise Refusal("NONCANONICAL_JSON") from e


def sha(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def rational(token):
    need(type(token) is str and 0 < len(token) <= 128, "NONCANONICAL_RATIONAL")
    try:
        value = Q(token)
    except (ValueError, ZeroDivisionError, OverflowError) as e:
        raise Refusal("NONCANONICAL_RATIONAL") from e
    need(str(value) == token, "NONCANONICAL_RATIONAL")
    budget(max(abs(value.numerator).bit_length(), value.denominator.bit_length()) <= 160,
           "RATIONAL_BIT_RESOURCE_LIMIT")
    return value


def parse(spec):
    need(type(spec) is dict and set(spec) == {
        "grammar", "source_parameter_id", "parameter_lo", "parameter_hi",
        "phase_turn_offset", "phase_turn_rate", "cos_splines", "sin_splines",
    }, "ORIGINAL_SOURCE_FIELDS_REQUIRED")
    budget(len(canonical(spec)) <= 16384, "SOURCE_BYTE_RESOURCE_LIMIT")
    need(spec["grammar"] == GRAMMAR and
         spec["source_parameter_id"] == "source-time-t",
         "SOURCE_GRAMMAR_OR_PARAMETER_MISMATCH")
    lo, hi = rational(spec["parameter_lo"]), rational(spec["parameter_hi"])
    need(lo < hi, "INVALID_ORIGINAL_INTERVAL")
    need(type(spec["sin_splines"]) is dict and not spec["sin_splines"] and
         type(spec["cos_splines"]) is dict and set(spec["cos_splines"]) == {"1"},
         "SINGLE_H1_COSINE_ONLY")
    spline = spec["cos_splines"]["1"]
    need(type(spline) is dict and set(spline) == {"degree", "knots", "controls"},
         "ORIGINAL_SPLINE_FIELDS_REQUIRED")
    need(type(spline["degree"]) is int and spline["degree"] == 0 and
         type(spline["knots"]) is list and len(spline["knots"]) == 3 and
         type(spline["controls"]) is list and len(spline["controls"]) == 2,
         "DEGREE_ZERO_TWO_SPANS_ONLY")
    knots = tuple(rational(x) for x in spline["knots"])
    need(knots[0] == lo and lo < knots[1] < hi and knots[2] == hi,
         "ORIGINAL_KNOTS_MISMATCH")
    controls = tuple(rational(x) for x in spline["controls"])
    offset = rational(spec["phase_turn_offset"])
    rate = rational(spec["phase_turn_rate"])
    ends = (offset + rate * lo, offset + rate * hi)
    budget(all(max(abs(x.numerator).bit_length(), x.denominator.bit_length()) <= 512
               for x in ends), "DERIVED_PHASE_RESOURCE_LIMIT")
    # Exact affine interpolation gives the entire source turn range.
    # If -1/4 < turn < 1/4, cos(2*pi*turn) is strictly positive.
    need(all(-Q(1, 4) < x < Q(1, 4) for x in ends),
         "POSITIVE_COSINE_SECTOR_NOT_ESTABLISHED")
    return lo, knots[1], hi, controls, offset, rate


def component(lo, hi, left_closed, right_closed, relation):
    return dict(lo=str(lo), hi=str(hi), left_closed=left_closed,
                right_closed=right_closed, relation=relation)


def analyze(spec, policy=RIGHT):
    need(policy in (RIGHT, LEFT), "UNBOUND_KNOT_POINT_POLICY")
    lo, knot, hi, (a, b), offset, rate = parse(spec)
    # The two original degree-zero basis functions are nonoverlapping on
    # [lo,knot) and [knot,hi); the final endpoint is explicitly clamped.
    # LEFT is a counterfactual choice only, not an asserted source convention.
    lk = policy == LEFT
    rk = not lk
    sa = (a > 0) - (a < 0)
    sb = (b > 0) - (b < 0)
    if not sa and not sb:
        zeros = [component(lo, hi, True, True, "ZERO")]
    elif not sa:
        zeros = [component(lo, knot, True, lk, "ZERO")]
    elif not sb:
        zeros = [component(knot, hi, rk, True, "ZERO")]
    else:
        zeros = []
    if sa and sa == sb:
        signs = [component(lo, hi, True, True,
                           "POSITIVE" if sa > 0 else "NEGATIVE")]
    else:
        signs = []
        if sa:
            signs.append(component(lo, knot, True, lk,
                                   "POSITIVE" if sa > 0 else "NEGATIVE"))
        if sb:
            signs.append(component(knot, hi, rk, True,
                                   "POSITIVE" if sb > 0 else "NEGATIVE"))
    point = a if lk else b
    closed = all(c["left_closed"] and c["right_closed"] for c in zeros)
    return {
        "schema": SCHEMA, "status": "EXACT_BOUNDED_ORIGINAL_SOURCE_KNOT_TOPOLOGY_RESEARCH",
        "evidence_class": "DETERMINISTIC_MODEL", "source_sha256": sha(spec),
        "source_parameter_id": "source-time-t",
        "original_interval": [str(lo), str(hi)], "true_original_knot": str(knot),
        "phase_turn_law": {"offset": str(offset), "rate": str(rate)},
        "phase_turn_endpoints": [str(offset+rate*lo), str(offset+rate*hi)],
        "phase_sector": "STRICTLY_POSITIVE_COSINE",
        "original_degree_zero_controls": [str(a), str(b)],
        "knot_point_policy": policy,
        "original_open_piece_zero_relations":
            ["IDENTITY_ZERO" if not sa else "NONZERO",
             "IDENTITY_ZERO" if not sb else "NONZERO"],
        "left_one_sided_sign": sa, "right_one_sided_sign": sb,
        "actual_knot_point_sign": (point > 0) - (point < 0),
        "actual_knot_point_zero": point == 0,
        "physical_continuity_at_knot": a == b,
        "maximal_zero_components": zeros,
        "maximal_constant_sign_components": signs,
        "zero_set_relatively_closed": closed,
        "closed_components_only_complete": closed,
        "isolated_finite_root_list_complete": not bool(zeros),
        "global_smooth_knot_multiplicity_claimed": False,
        "historical_v54_admitted": False, "pb00701_certified": False,
        "mc_b_established": False, "mc1_established": False,
        "native_step_qualified": False, "production_authorized": False,
    }


def nontruth(reason, resource=False):
    return {"schema": SCHEMA, "status": "RESOURCE_REFUSAL" if resource else "BLOCKED",
            "reason": reason, "is_truth_value": False,
            "pb00701_certified": False, "mc_b_established": False,
            "mc1_established": False, "production_authorized": False}


def attempt(spec, policy=RIGHT):
    try:
        return analyze(spec, policy)
    except ResourceRefusal as e:
        return nontruth(str(e), True)
    except (Refusal, ValueError, TypeError, KeyError, IndexError, ZeroDivisionError) as e:
        return nontruth(str(e))
    except (MemoryError, RecursionError, OverflowError) as e:
        return nontruth(type(e).__name__, True)


def validate_report(spec, policy, submitted):
    try:
        raw = canonical(submitted)
        budget(len(raw) <= 65536, "SUBMITTED_REPORT_RESOURCE_LIMIT")
        checked = attempt(spec, policy)
        need(checked.get("status") ==
             "EXACT_BOUNDED_ORIGINAL_SOURCE_KNOT_TOPOLOGY_RESEARCH",
             "SOURCE_PROOF_NOT_ESTABLISHED")
        need(raw == canonical(checked), "FORGED_SOURCE_KNOT_REPORT")
        return checked
    except ResourceRefusal as e:
        return nontruth(str(e), True)
    except (Refusal, ValueError, TypeError) as e:
        return nontruth(str(e))


def negative_c():
    need(sha(SOURCE) == SOURCE_SHA, "PRIMARY_SOURCE_SHA_DRIFT")
    right = analyze(SOURCE, RIGHT)
    left = analyze(SOURCE, LEFT)
    need(right["original_open_piece_zero_relations"] ==
         left["original_open_piece_zero_relations"], "OPEN_SOURCE_PIECES_DIFFER")
    need(right["maximal_zero_components"] ==
         [component(Q(0), Q(1), True, False, "ZERO")],
         "RIGHT_KNOT_POLICY_COUNTEREXAMPLE_FAILED")
    need(left["maximal_zero_components"] ==
         [component(Q(0), Q(1), True, True, "ZERO")],
         "LEFT_POLICY_CONTROL_FAILED")
    flip = copy.deepcopy(SOURCE)
    flip["cos_splines"]["1"]["controls"] = ["1", "-1"]
    jump = analyze(flip)
    need(not jump["maximal_zero_components"] and
         (jump["left_one_sided_sign"], jump["right_one_sided_sign"],
          jump["actual_knot_point_sign"]) == (1, -1, -1),
         "SIGN_JUMP_WITHOUT_ROOT_COUNTEREXAMPLE_FAILED")
    return {
        "schema": SCHEMA, "status": "EXACT_SOURCE_BOUND_NEGATIVE_C_RESEARCH",
        "claim": "C_DISCONTINUOUS_KNOT_CLOSED_ONLY_AND_ZERO_SET_ONLY_TRANSFER_FALSIFIED",
        "evidence_class": "DETERMINISTIC_MODEL",
        "primary_source_sha256": SOURCE_SHA,
        "right_internal_original_source": right,
        "left_internal_counterfactual_same_open_pieces": left,
        "sign_jump_source_sha256": jump["source_sha256"],
        "sign_jump_no_zero_control": jump,
        "finite_union_of_closed_sets_cannot_equal_half_open": True,
        "point_policy_must_be_bound_to_actual_original_source": True,
        "no_general_analytic_solver_impossibility_claim": True,
        "historical_source_denominator_before_after": [121, 121],
        "historical_route_refusals_before_after": [20, 20],
        "historical_missing_premises_before_after": [30, 30],
        "complete_source_specific_before_after": [50, 50],
        "new_historical_case_ids_closed": [],
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
