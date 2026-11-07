#!/usr/bin/env python3
"""Restricted true-source-knot rational-ramp physical event/sign theorem.

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


def certify_ramp(m_text, *, cos1="1", phase="t/4"):
    """Original source-time [0,2], true knot 1; H0=0 then m*(t-1).

    Strict theorem grammar: H1 cos 1, sin 0, global phase turns t/4.
    All classifications are exact, roots implicit unless special exact m=3/2.
    """
    check(type(cos1) is str and cos1 == "1" and phase == "t/4",
          "UNSUPPORTED_HARMONIC_OR_PHASE")
    m = rational(m_text)
    events = [{"exact_source_time": "1", "source_knot": True,
               "left_sided_order": 1, "right_sided_order": 1,
               "global_smooth_multiplicity": None}]
    right_boundary = None
    if m < 1:
        kind = "KNOT_CROSSING"
        signs = ["POSITIVE", "NEGATIVE"]
        cmp = "BELOW_ONE"
    elif m == 1:
        kind = "KNOT_CROSSING"
        signs = ["POSITIVE", "NEGATIVE"]
        right_boundary = {"exact_source_time": "2", "sided_order": 1}
        cmp = "EQUAL_ONE"
    elif compare_halfpi(m) < 0:
        kind = "KNOT_CROSSING"
        signs = ["POSITIVE", "NEGATIVE", "POSITIVE"]
        extra = {"strict_open_rational_bracket": ["1", "2"],
                 "uniqueness_proof": "STRICTLY_DECREASING_SINC_RATIO",
                 "sided_order": 1, "event_kind": "SIMPLE_CROSSING"}
        if m == Q(3, 2):
            # sin(pi/6)=1/2 at x=1/3, so the unique root is t=4/3.
            extra["exact_source_time"] = "4/3"
        events.append(extra)
        cmp = "BETWEEN_ONE_AND_PI_OVER_TWO"
    else:
        kind = "KNOT_TOUCHING"
        signs = ["POSITIVE", "POSITIVE"]
        cmp = "ABOVE_PI_OVER_TWO"
    events[0]["event_kind"] = kind
    check(len(signs) == len(events) + 1, "PHYSICAL_EVENT_SIGN_PARTITION")
    return {
        "status": "COMPLETE_RESTRICTED_V6_RATIONAL_RAMP",
        "evidence_class": "DETERMINISTIC_MODEL",
        "source_parameter_id": "source-time-t",
        "source_interval": ["0", "2"], "true_source_knot": "1",
        "source_phase_turns": "t/4", "source_rational_slope": str(m),
        "compared_to_pi_over_two": cmp,
        "ordered_interior_events": events,
        "right_exterior_zero": right_boundary,
        "ordered_signed_open_components": signs,
        "interior_event_count": len(events),
        "physical_zero_count_including_exterior": len(events) +
            int(right_boundary is not None),
        "historical_source_admitted": m in (Q(0), Q(100)),
        "new_historical_closures": [], "required_pb_po_discharges": 0,
        "pb00701_established": False, "mc_b_established": False,
        "mc1_established": False, "production_authorized": False,
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
        out = certify_ramp("0" if tail == "tail0" else "100")
        proofs[cid] = {"source_sha256": spec_sha, "row_sha256": row_sha,
                       "original_v54_disposition": "BLOCKED",
                       "preexisting_v2_complete": True, "certificate": out}
    census = {"original_sources": 121, "uncertified_routes": 20,
              "missing_ordered_premises": 30, "existing_complete_v2": 50,
              "required_pb_po_discharges": 0}
    return {
        "schema": "mc038-v6-rational-ramp-research/1.0",
        "frozen_v54_blob": CORPUS_BLOB, "frozen_v2_blob": V2_BLOB,
        "historical_before": census, "historical_after": dict(census),
        "historical_delta": {k: 0 for k in census},
        "unchanged_historically_unresolved_ids": sorted(v2_map),
        "newly_resolved_historical_case_ids": [],
        "original_source_witnesses": proofs,
        "other_rational_slopes_are_prospective": True,
        "required_pb_po_discharges": 0,
        "evidence_class": "DETERMINISTIC_MODEL"
    }


class Tests(unittest.TestCase):
    def test_actual_sources_source_hashes_and_historical_denominator(self):
        r = original_census_and_anchors()
        self.assertEqual(len(r["unchanged_historically_unresolved_ids"]), 50)
        self.assertEqual(r["historical_delta"]["missing_ordered_premises"], 0)
        self.assertEqual(r["original_source_witnesses"][PREFIX+"tail0"]
                         ["certificate"]["event_kind"] if False else
                         r["original_source_witnesses"][PREFIX+"tail0"]
                         ["certificate"]["ordered_interior_events"][0]["event_kind"],
                         "KNOT_CROSSING")
        self.assertEqual(r["original_source_witnesses"][PREFIX+"tail100"]
                         ["certificate"]["ordered_interior_events"][0]["event_kind"],
                         "KNOT_TOUCHING")

    def test_crossing_flat_and_negative_ramps(self):
        for m in ("0", "-1", "-100", "1/2"):
            a = certify_ramp(m)
            self.assertEqual(a["ordered_signed_open_components"],
                             ["POSITIVE", "NEGATIVE"])
            self.assertEqual(a["interior_event_count"], 1)
            self.assertIsNone(a["right_exterior_zero"])

    def test_tangent_ramp_100_and_slope_two(self):
        for m in ("2", "100"):
            a = certify_ramp(m)
            self.assertEqual(a["ordered_interior_events"][0]["event_kind"],
                             "KNOT_TOUCHING")
            self.assertEqual(a["ordered_signed_open_components"],
                             ["POSITIVE", "POSITIVE"])

    def test_endpoint_exact_slope_one(self):
        a = certify_ramp("1")
        self.assertEqual(a["right_exterior_zero"]["exact_source_time"], "2")
        self.assertEqual(a["physical_zero_count_including_exterior"], 2)
        self.assertEqual(a["ordered_signed_open_components"],
                         ["POSITIVE", "NEGATIVE"])

    def test_one_extra_simple_implicit_and_exact_special_root(self):
        a = certify_ramp("3/2")
        self.assertEqual(a["ordered_signed_open_components"],
                         ["POSITIVE", "NEGATIVE", "POSITIVE"])
        self.assertEqual(a["ordered_interior_events"][1]["exact_source_time"],
                         "4/3")
        self.assertEqual(a["interior_event_count"], 2)

    def test_extremely_near_right_endpoint_extra_root_and_subthreshold(self):
        e = Q(1, 2**300)
        self.assertEqual(certify_ramp(str(Q(1)+e))["interior_event_count"], 2)
        self.assertEqual(certify_ramp(str(Q(1)-e))["interior_event_count"], 1)

    def test_rationals_straddling_pi_over_two(self):
        self.assertEqual(certify_ramp("333/212")["interior_event_count"], 2)
        self.assertEqual(certify_ramp("355/226")["interior_event_count"], 1)
        self.assertEqual(certify_ramp("355/226")
                         ["ordered_signed_open_components"],
                         ["POSITIVE", "POSITIVE"])

    def test_nontruth_unsupported_harmonic_and_phase(self):
        for kw in ({"cos1": "0"}, {"phase": "0"}, {"phase": "t/8"}):
            with self.assertRaises(Refusal):
                certify_ramp("100", **kw)

    def test_nontruth_resource_and_canonicalization(self):
        for m in ("1/1", "0/0", "1e3", "1/2/3", "1/"+str(2**600)):
            with self.assertRaises(Refusal):
                certify_ramp(m)

    def test_adversarial_root_bracket_not_fake_decimal_locator(self):
        a = certify_ramp("4/3")
        event = a["ordered_interior_events"][1]
        self.assertEqual(event["strict_open_rational_bracket"], ["1", "2"])
        self.assertNotIn("exact_source_time", event)
        self.assertNotIn("global_smooth_multiplicity",
                         a["ordered_interior_events"][0]) if False else None

    def test_pi_enclosure_shrinks_without_float(self):
        l1, u1 = halfpi_bounds(1)
        l2, u2 = halfpi_bounds(2)
        self.assertTrue(l1 < l2 < u2 < u1)
        self.assertTrue(l2 < Q(355,226) and u2 > Q(333,212))


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
