#!/usr/bin/env python3
"""Restricted genuinely different affine-H1 true-knot physical event/sign theorem.

Research-only DETERMINISTIC_MODEL. Never infer an MC, PB, STEP or native gate.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "pb00701-finite-owner-corpus-v54.json"
V2 = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
PREFIX = "composite:DELEGATED_V6_CONSTANT_MODULATION:"
ANCHORS = {
    "tail0": ("9eb6f08a44882adffa919529247c40190c70e8d7599ee2b1a0f7978ef2569eb1",
              "145ac5ce5b533c447c7356e8dc721dbfa5a44562cdc3a37422278fd7bd0199fc"),
    "tail100": ("f6a0eb06c66af415fbb8abdfe62f9b36a2a2bf154e535d83307a80228e044ad5",
                "0801317d3452c77733a129148d58eaac2f06aa9cd26396a44892e82c524e1db2")
}
MAX_BYTES = 400000
MAX_BITS = 512
MAX_MACHIN_PAIRS = 128


class Refusal(ValueError):
    """NONTRUTH: unsupported grammar or insufficient bounded certification."""


def check(cond, reason):
    if not cond:
        raise Refusal(reason)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def guarded_json(path, blob):
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    check(len(raw) <= MAX_BYTES, "CORPUS_BYTE_BUDGET")
    # Bound the JSON nesting depth before the built-in parser allocates trees.
    depth = 0
    in_string = False
    escaped = False
    for ch in raw:
        if in_string:
            if escaped:
                escaped = False
            elif ch == 92:
                escaped = True
            elif ch == 34:
                in_string = False
        elif ch == 34:
            in_string = True
        elif ch in (91, 123):
            depth += 1
            check(depth <= 32, "JSON_DEPTH_BUDGET")
        elif ch in (93, 125):
            depth -= 1
            check(depth >= 0, "JSON_NESTING_MALFORMED")
    check(depth == 0 and not in_string, "JSON_NESTING_MALFORMED")
    check(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
          == blob, "FROZEN_GIT_BLOB_DRIFT")
    def unique(pairs):
        d = {}
        for k, v in pairs:
            check(k not in d, "JSON_DUPLICATE_KEY")
            d[k] = v
        return d
    def integer(s):
        check(len(s) <= 12, "JSON_INTEGER_BUDGET")
        return int(s)
    def reject(_):
        raise Refusal("JSON_NONINTEGER_NUMBER")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                          parse_int=integer, parse_float=reject,
                          parse_constant=reject)
    except (ValueError, UnicodeError, RecursionError) as ex:
        raise Refusal("CORPUS_JSON_INVALID") from ex


def rational(raw):
    check(type(raw) is str and 0 < len(raw) <= 320 and
          all(c in "0123456789-/" for c in raw), "RATIONAL_TOKEN")
    try:
        x = Q(raw)
    except (ValueError, ZeroDivisionError) as ex:
        raise Refusal("INVALID_RATIONAL") from ex
    check(str(x) == raw, "NONCANONICAL_RATIONAL")
    check(max(abs(x.numerator).bit_length(), x.denominator.bit_length())
          <= MAX_BITS, "RATIONAL_BIT_BUDGET")
    return x


def atan_bounds_reciprocal(k, pairs):
    """Exact alternating arctan bracket: even terms lower, next term upper."""
    check(k in (5, 239) and 1 <= pairs <= MAX_MACHIN_PAIRS, "MACHIN_BUDGET")
    x = Q(1, k)
    lower = sum(((-1)**j * x**(2*j+1) / (2*j+1)
                 for j in range(2*pairs)), Q(0))
    upper = lower + x**(4*pairs+1) / (4*pairs+1)
    return lower, upper


def halfpi_bounds(pairs):
    """Machin: pi/2 = 8 atan(1/5) - 2 atan(1/239), rigorous rationals."""
    a, b = atan_bounds_reciprocal(5, pairs)
    c, d = atan_bounds_reciprocal(239, pairs)
    lower, upper = 8*a - 2*d, 8*b - 2*c
    check(Q(3, 2) < lower < upper < Q(2), "MACHIN_INTERVAL_INVALID")
    return lower, upper


def compare_halfpi(m):
    """Returns -1 for m<pi/2, +1 for m>pi/2, else NONTRUTH cap refusal.

    Rational m cannot equal pi/2 by the classical irrationality of pi.
    Shrinking rational bounds therefore separate every rational m eventually.
    """
    if m <= 1:
        return -1
    if m >= 2:
        return 1
    for n in range(1, MAX_MACHIN_PAIRS + 1):
        a, b = halfpi_bounds(n)
        if m < a:
            return -1
        if m > b:
            return 1
    raise Refusal("PI_COMPARISON_BUDGET_NONTRUTH")



def certify_affine_h1(m_text, *, phase="t/4", right_cos_slope="-1/2",
                      right_sin_slope="-1/2", claim_frozen_original=False):
    """Exact physical events for a two-span C0-continuous prospective H1 law.

    Left: H0=0,C=1,S=0; right x=t-1: H0=m*x,C=1-x/2,S=-x/2.
    Each amplitude has a genuine degree-2 B-spline representation with
    knots (0,0,0,1,1,2,2,2); t=1 is a true repeated source knot.
    """
    check(phase == "t/4" and right_cos_slope == "-1/2" and
          right_sin_slope == "-1/2", "UNSUPPORTED_H1_OR_PHASE")
    check(claim_frozen_original is False, "PROSPECTIVE_NOT_FROZEN_ORIGINAL")
    m = rational(m_text)
    half = Q(1, 2)
    # For x in (0,1], F_right=x*(m-Q(x)), where
    # Q(x)=sin(a*x)/x-(sin(a*x)-cos(a*x))/2, a=pi/2.
    # Q'(x)=R'(x)-a*(cos(a*x)+sin(a*x))/2 < 0.
    # Exact limits Q(0+)=pi/2+1/2, Q(1)=1/2.
    events = [{"exact_source_time": "1", "true_source_knot": True,
               "left_sided_order": 1, "right_sided_order": 1,
               "global_smooth_multiplicity": None}]
    exterior = None
    if m < half:
        state = "BELOW_RIGHT_ENDPOINT_THRESHOLD"
        kind = "KNOT_CROSSING"
        signs = ["POSITIVE", "NEGATIVE"]
    elif m == half:
        state = "AT_RIGHT_ENDPOINT_THRESHOLD"
        kind = "KNOT_CROSSING"
        signs = ["POSITIVE", "NEGATIVE"]
        exterior = {"exact_source_time": "2", "left_sided_order": 1,
                    "kind": "EXTERIOR_SIMPLE_ZERO"}
    elif compare_halfpi(m-half) < 0:
        state = "INTERIOR_ROOT_BETWEEN_THRESHOLDS"
        kind = "KNOT_CROSSING"
        signs = ["POSITIVE", "NEGATIVE", "POSITIVE"]
        # Q(1/2)=sqrt(2) exactly. Since m is rational and sqrt(2)
        # irrational, their order is certified by comparing m*m to 2.
        # If m<sqrt(2), unique root x>1/2; otherwise x<1/2.
        if m*m < 2:
            bracket = ["3/2", "2"]
        else:
            bracket = ["1", "3/2"]
        events.append({"kind": "SIMPLE_CROSSING",
                       "strict_open_rational_bracket": bracket,
                       "uniqueness_proof":
                           "STRICTLY_DECREASING_AFFINE_H1_PHASE_RATIO",
                       "left_sided_order": 1, "right_sided_order": 1,
                       "true_source_knot": False,
                       "exact_source_time": None})
    else:
        state = "ABOVE_KNOT_THRESHOLD"
        kind = "KNOT_SIDED_TOUCH"
        signs = ["POSITIVE", "POSITIVE"]
    events[0]["kind"] = kind
    check(len(signs) == len(events) + 1, "SIGN_PARTITION_MISMATCH")
    return {
        "status": "COMPLETE_RESTRICTED_PROSPECTIVE_AFFINE_H1_KNOT",
        "evidence_class": "DETERMINISTIC_MODEL",
        "original_source_case": None,
        "source_parameter": "source-time-t",
        "source_interval": ["0", "2"],
        "source_true_double_knot": "1",
        "source_phase_turns": "t/4",
        "spline_degree": 2,
        "spline_knots": ["0", "0", "0", "1", "1", "2", "2", "2"],
        "proposed_h0_controls": ["0", "0", "0", str(m/2), str(m)],
        "proposed_h1_cos_controls": ["1", "1", "1", "3/4", "1/2"],
        "proposed_h1_sin_controls": ["0", "0", "0", "-1/4", "-1/2"],
        "compared_to_thresholds": state,
        "ordered_interior_events": events,
        "right_exterior_zero": exterior,
        "ordered_signed_open_components": signs,
        "physical_zero_count_including_exterior": len(events) +
            int(exterior is not None),
        "not_an_existing_frozen_source": True,
        "new_historical_closures": [],
        "required_pb_po_discharges": 0,
        "pb00701_established": False,
        "mc_b_established": False, "mc1_established": False,
        "production_authorized": False
    }


def original_census_and_anchors():
    corpus = guarded_json(CORPUS, CORPUS_BLOB)["cases"]
    v2 = guarded_json(V2, V2_BLOB)["source_cases"]
    ids = [r["id"] for r in corpus]
    check(len(ids) == len(set(ids)) == 121, "FROZEN_ORIGINAL_DENOMINATOR")
    blocked = [r for r in corpus if
               r["expected"]["v54_disposition"] == "BLOCKED"]
    missing = [r for r in corpus if
               r["expected"]["v54_disposition"] ==
               "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"]
    check(len(blocked) == 20 and len(missing) == 30, "V54_FAILURE_CENSUS")
    v2_map = {r["case_id"]: r for r in v2}
    check(len(v2_map) == len(v2) == 50 and
          set(v2_map) == {r["id"] for r in blocked + missing},
          "V2_WITNESS_IDENTITY_SET")
    by_id = {r["id"]: r for r in corpus}
    for cid, witness in v2_map.items():
        row = by_id[cid]
        check(witness["source_sha256"] ==
              hashlib.sha256(canonical(row["spec"])).hexdigest()
              and witness["original_row_sha256"] ==
              hashlib.sha256(canonical(row)).hexdigest()
              and witness["registered_evidence_level"] ==
              "COMPLETE_SOURCE_SPECIFIC", "V2_SOURCE_PROVENANCE")
    proofs = {}
    for tail, (spec_sha, row_sha) in ANCHORS.items():
        cid = PREFIX + tail
        row, witness = by_id[cid], v2_map[cid]
        spec = row["spec"]
        check(hashlib.sha256(canonical(spec)).hexdigest() == spec_sha and
              hashlib.sha256(canonical(row)).hexdigest() == row_sha and
              witness["source_sha256"] == spec_sha and
              witness["original_row_sha256"] == row_sha and
              spec["source_parameter_id"] == "source-time-t" and
              (spec["parameter_lo"], spec["parameter_hi"]) == ("0", "2") and
              (spec["phase_turn_offset"], spec["phase_turn_rate"]) ==
              ("0", "1/4") and not spec["sin_splines"],
              "ORIGINAL_SOURCE_ANCHOR")
        h1 = spec["cos_splines"]["1"]
        check(h1 == {"degree": 0, "knots": ["0", "1", "2"],
                     "controls": ["1", "1"]}, "ORIGINAL_H1_KNOT_IDENTITY")
        h0 = spec["cos_splines"]["0"]
        expected_h0 = ({"degree": 0, "knots": ["0", "1", "2"],
                        "controls": ["0", "0"]} if tail == "tail0" else
                       {"degree": 1, "knots": ["0", "0", "1", "1", "2", "2"],
                        "controls": ["0", "0", "0", "100"]})
        check(h0 == expected_h0, "ORIGINAL_H0_BSPLINE_IDENTITY")
        check(row["expected"]["v54_disposition"] == "BLOCKED" and
              witness["registered_evidence_level"] ==
              "COMPLETE_SOURCE_SPECIFIC", "ORIGINAL_ROUTE_PROVENANCE")
        proofs[cid] = {"source_sha256": spec_sha, "row_sha256": row_sha,
                       "original_v54_disposition": "BLOCKED",
                       "preexisting_v2_complete": True,
                       "provenance_reference_only": True,
                       "prospective_h1_is_not_this_original": True}
    census = {"original_sources": 121, "uncertified_routes": 20,
              "missing_ordered_premises": 30, "existing_complete_v2": 50,
              "required_pb_po_discharges": 0}
    return {
        "schema": "mc038-v6-affine-h1-knot-research/1.0",
        "frozen_v54_blob": CORPUS_BLOB, "frozen_v2_blob": V2_BLOB,
        "historical_before": census, "historical_after": dict(census),
        "historical_delta": {k: 0 for k in census},
        "unchanged_historically_unresolved_ids": sorted(v2_map),
        "newly_resolved_historical_case_ids": [],
        "original_source_witnesses": proofs,
        "different_h1_laws_are_prospective": True,
        "prospective_certificates": {m: certify_affine_h1(m)
                                      for m in ("0", "1/2", "1", "3/2", "100")},
        "required_pb_po_discharges": 0,
        "evidence_class": "DETERMINISTIC_MODEL"
    }



class Tests(unittest.TestCase):
    def test_frozen_source_pins_as_provenance_only_and_unchanged_census(self):
        evidence = original_census_and_anchors()
        self.assertEqual(len(evidence["unchanged_historically_unresolved_ids"]), 50)
        self.assertEqual(evidence["historical_before"], evidence["historical_after"])
        self.assertTrue(all(v["provenance_reference_only"]
                            for v in evidence["original_source_witnesses"].values()))
        self.assertTrue(evidence["prospective_certificates"]["1"]["not_an_existing_frozen_source"])

    def test_actual_degree_two_control_laws_and_knot_continuity(self):
        a = certify_affine_h1("3/2")
        self.assertEqual(a["spline_knots"],
                         ["0","0","0","1","1","2","2","2"])
        self.assertEqual(a["proposed_h1_cos_controls"],
                         ["1","1","1","3/4","1/2"])
        self.assertEqual(a["proposed_h1_sin_controls"],
                         ["0","0","0","-1/4","-1/2"])
        self.assertEqual(a["proposed_h0_controls"],
                         ["0","0","0","3/4","3/2"])

    def test_crossing_for_negative_and_small_m(self):
        for m in ("-100", "0", "1/4"):
            a = certify_affine_h1(m)
            self.assertEqual(a["physical_zero_count_including_exterior"], 1)
            self.assertEqual(a["ordered_signed_open_components"],
                             ["POSITIVE", "NEGATIVE"])
            self.assertEqual(a["ordered_interior_events"][0]["kind"],
                             "KNOT_CROSSING")

    def test_exact_exterior_zero_at_m_half(self):
        a = certify_affine_h1("1/2")
        self.assertEqual(a["physical_zero_count_including_exterior"], 2)
        self.assertEqual(a["right_exterior_zero"]["exact_source_time"], "2")
        self.assertEqual(a["ordered_signed_open_components"],
                         ["POSITIVE","NEGATIVE"])

    def test_interior_root_to_right_of_exact_sqrt_two_midpoint(self):
        a = certify_affine_h1("1")
        self.assertEqual(a["physical_zero_count_including_exterior"], 2)
        self.assertEqual(a["ordered_interior_events"][1]
                         ["strict_open_rational_bracket"], ["3/2","2"])
        self.assertEqual(a["ordered_signed_open_components"],
                         ["POSITIVE","NEGATIVE","POSITIVE"])

    def test_interior_root_to_left_of_midpoint(self):
        a = certify_affine_h1("3/2")
        self.assertEqual(a["ordered_interior_events"][1]
                         ["strict_open_rational_bracket"], ["1","3/2"])
        self.assertEqual(a["ordered_signed_open_components"],
                         ["POSITIVE","NEGATIVE","POSITIVE"])

    def test_sided_touch_and_not_false_smooth_double_root(self):
        for m in ("3", "100"):
            a = certify_affine_h1(m)
            self.assertEqual(a["ordered_interior_events"][0]["kind"],
                             "KNOT_SIDED_TOUCH")
            self.assertEqual(a["ordered_signed_open_components"],
                             ["POSITIVE", "POSITIVE"])
            self.assertIsNone(a["ordered_interior_events"][0]
                              ["global_smooth_multiplicity"])
            self.assertEqual(a["physical_zero_count_including_exterior"], 1)

    def test_pi_threshold_enclosures_both_sides(self):
        low, high = halfpi_bounds(8)
        scale = 2**160
        below = Q((low.numerator*scale)//low.denominator,scale)
        above = Q((high.numerator*scale)//high.denominator+1,scale)
        self.assertTrue(below < low < high < above)
        a = certify_affine_h1(str(Q(1,2)+below))
        b = certify_affine_h1(str(Q(1,2)+above))
        self.assertEqual(a["physical_zero_count_including_exterior"], 2)
        self.assertEqual(b["physical_zero_count_including_exterior"], 1)

    def test_extremely_near_real_knot_extra_root_proof_inequality(self):
        # Let d=2^-100. Q(0+)-Q(d)>=sin(a*d)/2>3d/8.
        # Machin encloses a. Choose rational m just below a+1/2,
        # with a+1/2-m<d/4. Then unique root has 0<x<d.
        low, high = halfpi_bounds(60)
        scale = 2**240
        q = Q((low.numerator*scale)//low.denominator,scale)
        d = Q(1, 2**100)
        self.assertTrue(high-q<d/4)
        a = certify_affine_h1(str(Q(1,2)+q))
        self.assertEqual(a["physical_zero_count_including_exterior"],2)
        self.assertEqual(a["ordered_interior_events"][1]
                         ["strict_open_rational_bracket"], ["1","3/2"])

    def test_extremely_near_right_exterior_additional_root(self):
        # For x in [1/2,1], -Q'(x)>3/8 by -sine derivative term.
        # With d=2^-100 and eps=2^-300, Q(1-d)>1/2+3d/8>m.
        # Thus for m=1/2+eps the additional root is in (2-d,2).
        eps=Q(1,2**300)
        d=Q(1,2**100)
        self.assertTrue(eps<3*d/8)
        a=certify_affine_h1(str(Q(1,2)+eps))
        self.assertEqual(a["physical_zero_count_including_exterior"],2)
        self.assertEqual(a["ordered_interior_events"][1]
                         ["strict_open_rational_bracket"], ["3/2","2"])

    def test_sqrt_two_comparison_rational_arbitrary_nearness(self):
        # Exact comparator via integer-square order, no floats.
        from math import isqrt
        n=2**200
        lower=Q(isqrt(2*n*n),n)
        upper=lower+Q(1,n)
        self.assertLess(lower*lower, 2)
        self.assertGreater(upper*upper, 2)
        # Both are inside (1/2,pi/2+1/2).
        self.assertEqual(certify_affine_h1(str(lower))
                         ["ordered_interior_events"][1]
                         ["strict_open_rational_bracket"],["3/2","2"])
        self.assertEqual(certify_affine_h1(str(upper))
                         ["ordered_interior_events"][1]
                         ["strict_open_rational_bracket"],["1","3/2"])

    def test_refuse_unstated_h1_phase_and_historical_identification(self):
        for kw in ({"phase":"t/8"}, {"right_cos_slope":"0"},
                   {"right_sin_slope":"0"}, {"claim_frozen_original":True}):
            with self.assertRaises(Refusal):
                certify_affine_h1("1", **kw)

    def test_refuse_oversized_or_noncanonical_rational(self):
        for m in ("1/1", "0/0", "1e3", "1/2/3", "1/"+str(2**600)):
            with self.assertRaises(Refusal):
                certify_affine_h1(m)

    def test_finite_pi_compare_budget_is_typed_nontruth(self):
        from unittest.mock import patch
        low,high=halfpi_bounds(1)
        mid=(low+high)/2
        with patch.dict(certify_affine_h1.__globals__,
                        {"MAX_MACHIN_PAIRS": 1}):
            with self.assertRaisesRegex(Refusal,
                                        "PI_COMPARISON_BUDGET_NONTRUTH"):
                certify_affine_h1(str(mid+Q(1,2)))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--contract", action="store_true")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.contract:
        print(json.dumps(original_census_and_anchors(), sort_keys=True))
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            raise SystemExit(1)
    if not (args.contract or args.self_test):
        p.error("run with --contract and/or --self-test")


if __name__ == "__main__":
    main()
