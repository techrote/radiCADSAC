#!/usr/bin/env python3
"""PB-007-01 bounded C: original V9 phasor norm does not determine physical events.

A read-only, source-pinned checker for one *proposed* information-losing method.
The exact analytic argument (not a numerical scan) is in the adjacent RAG note.
Never interpret this script as PB-007, MC-B, native geometry or STEP acceptance.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
V54 = HERE / "pb00701-finite-owner-corpus-v54.json"
V2 = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
RECEIPT = HERE / "pb00701-v9-phasor-norm-obstruction-20261106.json"
V54_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
CASE = "composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail0"
SOURCE_SHA = "4d1ef1cbecceeb4a43b4e30fd37327fa204164cc9ce25dfe4f1744a052cebcc2"
ROW_SHA = "406ec73609a8213051afd3361478416e496c782b2b89ae2a857b772146059279"
SCHEMA = "radicadsac-mc038-v9-phasor-norm-obstruction/1.0"


class Refusal(ValueError):
    """No mathematical truth or acceptance from an unmatched source."""


def need(test, why):
    if not test:
        raise Refusal(why)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False)


def digest(obj):
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def read_pinned(path, blob, cap=512 * 1024):
    need(path.is_file(), "required frozen source missing")
    # Read at most cap+1 bytes before SHA-1 and JSON parsing. Cap is custody,
    # not a truth criterion for any analytic source.
    with path.open("rb") as f:
        raw = f.read(cap + 1)
    need(len(raw) <= cap, "refusal: frozen input byte budget exceeded")
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    need(actual == blob, "frozen git blob provenance mismatch")
    def distinct(pairs):
        out = {}
        for key, value in pairs:
            need(key not in out, "duplicate JSON key")
            out[key] = value
        return out
    def nonfinite(_):
        raise Refusal("nonfinite JSON token")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=distinct, parse_constant=nonfinite)


def original_spec():
    corpus = read_pinned(V54, V54_BLOB)
    v2 = read_pinned(V2, V2_BLOB)
    rows = corpus["cases"]
    ids = [r["id"] for r in rows]
    need(len(rows) == len(set(ids)) == 121, "frozen original population/IDs changed")
    c = Counter(r["expected"]["v54_disposition"] for r in rows)
    need(c["BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"] == 30,
         "historical 30 ordered-premise population changed")
    need(sum(v for k, v in c.items() if k.startswith("BLOCKED:") and
             k != "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE") == 20,
         "historical 20 route-refusal population changed")
    v2rows = v2["source_cases"]
    need(len(v2rows) == 50 and len({r["case_id"] for r in v2rows}) == 50,
         "V2 complete-source population changed")
    need(all(r["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC" for r in v2rows),
         "V2 contains incomplete witnesses")
    need(v2["summary"]["complete_finite_sources"] == 49 and
         v2["summary"]["complete_continuum_sources"] == 1,
         "V2 finite/continuum kinds changed")
    need({r["case_id"] for r in v2rows} ==
         {r["id"] for r in rows if r["expected"]["v54_disposition"].startswith("BLOCKED:")},
         "V54/V2 unresolved case identity mismatch")
    row = next(r for r in rows if r["id"] == CASE)
    registry = next(r for r in v2rows if r["case_id"] == CASE)
    need(digest(row) == ROW_SHA, "original V54 case row identity mismatch")
    spec = row["spec"]
    need(digest(spec) == SOURCE_SHA, "original rational B-spline source identity mismatch")
    need(registry["source_sha256"] == SOURCE_SHA and
         registry["original_row_sha256"] == ROW_SHA and
         registry["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC" and
         registry["evidence"]["complete_original_source_zero_set"] is True,
         "prior complete V2 proof was not preserved")
    need(registry["historical_v54_disposition"] ==
         "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE" and
         row["expected"]["v54_disposition"] == registry["historical_v54_disposition"],
         "historical V54 label changed")
    need(registry["phase_turn_law"] == {"offset":"0","rate":"1/8"} and
         registry["original_source_piece_edges"] == ["0","1","2"] and
         registry["source_interval"] == ["0","2"],
         "prior V2 original source/phase/knot identity changed")
    return spec


def source_coefficients(spec):
    """Independently lower the exact two-piece clamped B-spline controls."""
    need(set(spec) == {"grammar", "source_parameter_id", "parameter_lo", "parameter_hi",
                       "phase_turn_offset", "phase_turn_rate", "cos_splines", "sin_splines"},
         "source grammar keys changed")
    need(spec["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE" and
         spec["source_parameter_id"] == "source-time-t" and
         [spec["parameter_lo"], spec["parameter_hi"]] == ["0","2"] and
         [spec["phase_turn_offset"], spec["phase_turn_rate"]] == ["0","1/8"],
         "source time/phase not admitted")
    cs, ss = spec["cos_splines"], spec["sin_splines"]
    need(set(cs) == {"0","1"} and set(ss) == {"1"}, "not pure H0/H1 phasor grammar")
    c0, c1, s1 = cs["0"], cs["1"], ss["1"]
    need(c0 == {"degree":0, "knots":["0","1","2"], "controls":["0","0"]},
         "H0 not identically zero")
    need(c1["degree"] == 1 and c1["knots"] == ["0","0","1","1","2","2"] and
         s1["degree"] == 0 and s1["knots"] == ["0","1","2"],
         "true piecewise B-spline knots/degrees changed")
    c = [Q(v) for v in c1["controls"]]
    s = [Q(v) for v in s1["controls"]]
    need(len(c) == 4 and len(s) == 2, "control population mismatch")
    # Degree-one Bezier on [0,1] is c0*(1-t)+c1*t;
    # the second span, with local u=t-1, is c2*(1-u)+c3*u.
    need(c == [Q(-1,2),Q(1,2),Q(1,2),Q(1,2)] and s == [Q(1),Q(1)],
         "not the exact frozen original V9 coefficients")
    left_cos = (c[0], c[1]-c[0])          # -1/2 + t
    right_cos = (c[2], c[3]-c[2])        # 1/2 + 0*(t-1)
    need(c[1] == c[2] and s[0] == s[1], "source discontinuity")
    return (left_cos, right_cos, s)


def polynomial_square(poly):
    ans = [Q(0)] * (2 * len(poly) - 1)
    for i, a in enumerate(poly):
        for j, b in enumerate(poly):
            ans[i+j] += a*b
    return tuple(ans)


def add_poly(a, b):
    return tuple((a[i] if i < len(a) else Q(0)) +
                 (b[i] if i < len(b) else Q(0))
                 for i in range(max(len(a),len(b))))


def norm_square(c, s):
    return add_poly(polynomial_square(c), polynomial_square(s))


def check_source(spec):
    (left, right, original_s) = source_coefficients(spec)
    # Construct adversarial *synthetic companion*: only the sign of S1 is
    # reversed. The original frozen source is never replaced/relabelled.
    companion = deepcopy(spec)
    companion["sin_splines"]["1"]["controls"] = ["-1","-1"]
    need(companion["cos_splines"] == spec["cos_splines"] and
         companion["phase_turn_rate"] == spec["phase_turn_rate"] and
         companion["phase_turn_offset"] == spec["phase_turn_offset"] and
         companion["sin_splines"]["1"]["knots"] == spec["sin_splines"]["1"]["knots"],
         "adversarial comparison changed source semantics")
    neg_s = [-q for q in original_s]
    norm_a_left = norm_square(left, [original_s[0]])
    norm_b_left = norm_square(left, [neg_s[0]])
    norm_a_right = norm_square(right, [original_s[1]])
    norm_b_right = norm_square(right, [neg_s[1]])
    need(norm_a_left == norm_b_left == (Q(5,4),-Q(1),Q(1)) and
         norm_a_right == norm_b_right == (Q(5,4),),
         "projected phasor norm not identical on both original time spans")
    return companion


def expected_receipt():
    return {
        "schema": SCHEMA,
        "task": "MC-038",
        "obligation": "PB-007-01 / PO-05 / PO-08",
        "falsified_candidate": "COMMON_H1_PHASOR_NORM_ONLY_ZERO_DECISION",
        "claim_type": "BOUNDED_NEGATIVE_C",
        "evidence_class": "DETERMINISTIC_MODEL",
        "frozen_v54_git_blob": V54_BLOB,
        "accepted_v2_git_blob": V2_BLOB,
        "original_case_id": CASE,
        "original_source_sha256": SOURCE_SHA,
        "original_row_sha256": ROW_SHA,
        "source_parameter": "source-time-t",
        "source_interval": ["0","2"],
        "source_knot": "1",
        "phase_turns": "t/8",
        "original_h1_cos": ["t-1/2","1/2"],
        "original_h1_sin": ["1","1"],
        "synthetic_companion_h1_sin": ["-1","-1"],
        "both_amplitude_squared": ["t^2-t+5/4","5/4"],
        "original_physical_event": {
            "zero_set": "one simple r in (0,1/2)",
            "multiplicity": 1,
            "parity": "odd",
            "maximal_open_sign_cells": ["NEGATIVE","POSITIVE"]
        },
        "synthetic_companion_physical_event": {
            "zero_set": "empty on [0,2]",
            "maximal_open_sign_cells": ["NEGATIVE"]
        },
        "historical_before": {"sources":121,"uncertified_routes":20,
                              "missing_ordered_premises":30,"complete_v2_sources":50},
        "historical_after": {"sources":121,"uncertified_routes":20,
                             "missing_ordered_premises":30,"complete_v2_sources":50},
        "new_historical_closed_cases": [],
        "required_pb_po_discharges": 0,
        "general_analytic_event_theorem_proved": False,
        "mc_b_established": False,
        "mc1_established": False,
        "native_geometry_qualified": False,
        "engineering_step_qualified": False,
        "production_authorized": False
    }


def verify_receipt(receipt):
    need(canonical(receipt) == canonical(expected_receipt()),
         "machine receipt falsely changes the bounded mathematical claim")


def contract():
    spec = original_spec()
    companion = check_source(spec)
    need(companion["sin_splines"]["1"]["controls"] == ["-1","-1"],
         "phasor orientation retained instead of reversed")
    need(RECEIPT.is_file(), "machine receipt missing")
    with RECEIPT.open("rb") as f:
        raw = f.read(64 * 1024 + 1)
    need(len(raw) <= 64 * 1024, "machine receipt byte budget exceeded")
    receipt = json.loads(raw.decode("utf-8"))
    verify_receipt(receipt)
    return receipt


class Adversarial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = original_spec()

    def test_original_and_exact_norm_identity(self):
        self.assertEqual(check_source(self.spec)["sin_splines"]["1"]["controls"],
                         ["-1","-1"])

    def refuse(self, mutation):
        s = deepcopy(self.spec)
        mutation(s)
        with self.assertRaises(Refusal):
            check_source(s)

    def test_phase_substitution_refuses(self):
        self.refuse(lambda s: s.__setitem__("phase_turn_rate", "1/12"))

    def test_true_knot_substitution_refuses(self):
        self.refuse(lambda s: s["cos_splines"]["1"]["knots"].__setitem__(2,"3/4"))

    def test_harmonic_substitution_refuses(self):
        self.refuse(lambda s: s["sin_splines"].__setitem__("2",s["sin_splines"].pop("1")))

    def test_original_control_mutation_refuses(self):
        self.refuse(lambda s: s["cos_splines"]["1"]["controls"].__setitem__(1,"3/4"))

    def test_sine_orientation_change_refuses_original_identity(self):
        self.refuse(lambda s: s["sin_splines"]["1"]["controls"].__setitem__(0,"-1"))

    def test_knot_discontinuity_refuses(self):
        self.refuse(lambda s: s["cos_splines"]["1"]["controls"].__setitem__(2,"1/4"))

    def test_type_coercion_refuses(self):
        self.refuse(lambda s: s["cos_splines"]["1"].__setitem__("degree",True))

    def test_false_novelty_boolean_refuses(self):
        r = expected_receipt()
        r["required_pb_po_discharges"] = True
        with self.assertRaises(Refusal):
            verify_receipt(r)

    def test_silent_case_closure_refuses(self):
        r = expected_receipt()
        r["new_historical_closed_cases"] = [CASE]
        with self.assertRaises(Refusal):
            verify_receipt(r)

    def test_synthetic_identity_zero_nonzero_norm(self):
        # At phase=0, C=0,S=1 is identically zero but norm=1;
        # C=1,S=0 is root-free while sharing norm=1. Not original-source evidence.
        self.assertEqual(norm_square([Q(0)],[Q(1)]),
                         norm_square([Q(1)],[Q(0)]))
        self.assertEqual(norm_square([Q(1)],[Q(0)]),(Q(1),))

    def test_synthetic_tangency_and_sign_loss(self):
        # At phase=0, C=(t-1/2)^2; C and -C have the same squared
        # amplitude and an exact order-two tangency, opposite cell signs.
        p = [Q(1,4),-Q(1),Q(1)]
        self.assertEqual(norm_square(p,[Q(0)]),
                         norm_square([-x for x in p],[Q(0)]))

    def test_synthetic_close_roots_and_endpoint(self):
        # Distinct exact rationals separated by 2^-120, no scanning/rounding.
        a, b = Q(1,2), Q(1,2) + Q(1,2**120)
        p = [a*b,-(a+b),Q(1)]
        self.assertEqual(norm_square(p,[Q(0)]),
                         norm_square([-x for x in p],[Q(0)]))
        self.assertEqual(b-a,Q(1,2**120))
        self.assertEqual(norm_square([Q(0),Q(1)],[Q(0)]),
                         norm_square([Q(0),-Q(1)],[Q(0)]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract",action="store_true")
    parser.add_argument("--self-test",action="store_true")
    args = parser.parse_args()
    if args.self_test:
        unittest.main(argv=[__file__],exit=False,verbosity=2)
    if args.contract or not args.self_test:
        result = contract()
        print(canonical({"status":"BOUNDED_NEGATIVE_C","source_case_id":CASE,
                         "source_sha256":SOURCE_SHA,"new_historical_closed_cases":0,
                         "required_pb_discharge":False,"receipt_sha256":digest(result)}))
