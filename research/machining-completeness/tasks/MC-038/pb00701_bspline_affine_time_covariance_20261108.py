#!/usr/bin/env python3
"""Exact rational B-spline affine source-time covariance and H0/H1/H2 events.

DETERMINISTIC_MODEL research; this is not physical machining time reversal,
frozen original-corpus authentication, STEP, or production qualification.
"""
from __future__ import annotations
import argparse
import copy
import math
import random
import unittest
from fractions import Fraction as Q
import pb00701_generic_interval_events_20261108 as core
import pb00701_genuine_bspline_knot_bridge_20261108 as bridge

Nontruth = core.Nontruth
need = core.need


def parse_map(offset, slope):
    need(type(offset) is str and type(slope) is str, "AFFINE_MAP_ENCODING")
    a, b = core.fraction(offset), core.fraction(slope)
    need(offset == str(a) and slope == str(b), "AFFINE_MAP_NONCANONICAL")
    need(abs(a) <= 8 and 0 < abs(b) <= 8, "AFFINE_MAP_BUDGET")
    return a, b


def remap(spec, offset, slope):
    """Old time = a+b*new time. Reverse BOTH knot and control order if b<0."""
    old_doc, old, old_knots = bridge.source_to_pieces(spec)
    a, b = parse_map(offset, slope)
    new_spec = copy.deepcopy(spec)
    new_spec["phase_offset_pi"] = str(old.phase_offset + old.phase_slope*a)
    new_spec["phase_slope_pi"] = str(old.phase_slope*b)
    for key in core.KEYS:
        p, knots, controls, _ = bridge.spline_parse(spec["splines"][key])
        uu = knots if b > 0 else tuple(reversed(knots))
        cc = controls if b > 0 else tuple(reversed(controls))
        new_spec["splines"][key] = {
            "degree": p, "knots": [str((u-a)/b) for u in uu],
            "controls": [str(c) for c in cc]}
    new_doc, new, new_knots = bridge.source_to_pieces(new_spec)
    need(len(old.pieces) == len(new.pieces), "AFFINE_PIECE_COUNT_DRIFT")
    return new_spec, (old_doc, old, old_knots), (new_doc, new, new_knots)


def compose(poly, a, b):
    """Exact power basis of P(a+b*t), not an interpolating approximation."""
    out = [Q(0)]*len(poly)
    for j, c in enumerate(poly):
        for i in range(j+1):
            out[i] += c*math.comb(j, i)*a**(j-i)*b**i
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return tuple(out)


def coefficient_witness(old, new, a, b):
    need(new.phase_offset == old.phase_offset + old.phase_slope*a and
         new.phase_slope == old.phase_slope*b, "AFFINE_PHASE_DRIFT")
    witness = []
    for i, piece in enumerate(new.pieces):
        endpoints = (a+b*piece.lo, a+b*piece.hi)
        l, r = min(endpoints), max(endpoints)
        covering = [(j, prior) for j, prior in enumerate(old.pieces)
                    if prior.lo <= l and r <= prior.hi]
        need(len(covering) == 1, "AFFINE_OLD_SPAN_NONUNIQUE")
        j, ancestor = covering[0]
        need(tuple(compose(p, a, b) for p in ancestor.polys) == piece.polys,
             "AFFINE_COEFFICIENT_DRIFT")
        witness.append({"new_piece_index": i, "old_piece_index": j,
                        "new_lo": str(piece.lo), "new_hi": str(piece.hi),
                        "old_lo": str(l), "old_hi": str(r)})
    return witness


def structural_witness(original, transformed, a, b):
    expected = sorted(({
        "t": str((core.fraction(k["t"])-a)/b),
        "field_multiplicities": k["field_multiplicities"]
    } for k in original), key=lambda row: core.fraction(row["t"]))
    need(expected == transformed, "AFFINE_GENUINE_KNOT_DRIFT")
    return expected


def boundary_witness(before, after, a, b):
    """Exactly transfer event coordinates and swap sided order/sign if reversed."""
    source_events = before["physical_events"]["boundary_events"]
    target_events = after["physical_events"]["boundary_events"]
    n = len(before["derived_piece_source"]["pieces"])
    need(n == len(after["derived_piece_source"]["pieces"]),
         "AFFINE_BOUNDARY_SPAN_DRIFT")
    rows = []
    for x in source_events:
        reverse = b < 0
        rows.append({
            "boundary": n-x["boundary"] if reverse else x["boundary"],
            "t": str((core.fraction(x["t"])-a)/b),
            "kind": x["kind"],
            "left_sign": x["right_sign"] if reverse else x["left_sign"],
            "right_sign": x["left_sign"] if reverse else x["right_sign"],
            "left_order": x["right_order"] if reverse else x["left_order"],
            "right_order": x["left_order"] if reverse else x["right_order"],
        })
    rows.sort(key=lambda x: x["boundary"])
    need(rows == target_events, "AFFINE_BOUNDARY_EVENT_DRIFT")
    need(before["physical_events"]["physical_root_count"] ==
         after["physical_events"]["physical_root_count"],
         "AFFINE_ROOT_COUNT_DRIFT")
    return rows


def produce(spec, offset, slope, bits=10):
    need(type(bits) is int and 1 <= bits <= core.MAX_BITS, "AFFINE_BITS_BUDGET")
    a, b = parse_map(offset, slope)
    other, (_, old, knots), (_, new, new_knots) = remap(spec, offset, slope)
    coeff = coefficient_witness(old, new, a, b)
    structural = structural_witness(knots, new_knots, a, b)
    before = bridge.certify(spec, bits=bits)
    after = bridge.certify(other, bits=bits)
    boundary = boundary_witness(before, after, a, b)
    return {
        "status": "COMPLETE_RESTRICTED_AFFINE_BSPLINE_TIME_COVARIANCE",
        "evidence_class": "DETERMINISTIC_MODEL",
        "time_map": {"old_t_offset": str(a), "old_t_slope": str(b),
                     "orientation": "FORWARD" if b > 0 else "REVERSED"},
        "bits": bits, "original_supplied_sha256": bridge.source_hash(spec),
        "transformed_supplied_sha256": bridge.source_hash(other),
        "original_derived_sha256": old.identity,
        "transformed_derived_sha256": new.identity,
        "transformed_source": other,
        "exact_polynomial_correspondence": coeff,
        "structural_knot_correspondence": structural,
        "physical_boundary_correspondence": boundary,
        "original_complete_events": before,
        "transformed_complete_events": after,
        "historical_corpus_membership_claimed": False,
        "new_historical_closures": [], "required_pb_po_discharges": 0,
        "pb00701_established": False, "mc_b_established": False,
        "mc1_established": False, "production_authorized": False,
    }


def verify(spec, receipt):
    """Replay source algebra and both independently certified physical proofs."""
    need(type(receipt) is dict and set(receipt) == {
        "status", "evidence_class", "time_map", "bits",
        "original_supplied_sha256", "transformed_supplied_sha256",
        "original_derived_sha256", "transformed_derived_sha256",
        "transformed_source", "exact_polynomial_correspondence",
        "structural_knot_correspondence", "physical_boundary_correspondence",
        "original_complete_events", "transformed_complete_events",
        "historical_corpus_membership_claimed", "new_historical_closures",
        "required_pb_po_discharges", "pb00701_established",
        "mc_b_established", "mc1_established", "production_authorized"
    }, "AFFINE_RECEIPT_FIELDS")
    m = receipt["time_map"]
    need(type(m) is dict and set(m) ==
         {"old_t_offset", "old_t_slope", "orientation"},
         "AFFINE_MAP_RECEIPT_FIELDS")
    a, b = parse_map(m["old_t_offset"], m["old_t_slope"])
    bits = receipt["bits"]
    need(type(bits) is int and 1 <= bits <= core.MAX_BITS, "AFFINE_BITS_BUDGET")
    other, (_, old, knots), (_, new, new_knots) = remap(spec, str(a), str(b))
    coeff = coefficient_witness(old, new, a, b)
    structural = structural_witness(knots, new_knots, a, b)
    expected = {
        "status": "COMPLETE_RESTRICTED_AFFINE_BSPLINE_TIME_COVARIANCE",
        "evidence_class": "DETERMINISTIC_MODEL",
        "time_map": {"old_t_offset": str(a), "old_t_slope": str(b),
                     "orientation": "FORWARD" if b > 0 else "REVERSED"},
        "bits": bits, "original_supplied_sha256": bridge.source_hash(spec),
        "transformed_supplied_sha256": bridge.source_hash(other),
        "original_derived_sha256": old.identity,
        "transformed_derived_sha256": new.identity,
        "transformed_source": other, "exact_polynomial_correspondence": coeff,
        "structural_knot_correspondence": structural,
        "historical_corpus_membership_claimed": False,
        "new_historical_closures": [], "required_pb_po_discharges": 0,
        "pb00701_established": False, "mc_b_established": False,
        "mc1_established": False, "production_authorized": False,
    }
    for key, value in expected.items():
        try:
            equal = core.canonical(receipt[key]) == core.canonical(value)
        except (TypeError, ValueError, OverflowError, RecursionError) as exc:
            raise Nontruth("AFFINE_RECEIPT_MALFORMED") from exc
        need(equal, "AFFINE_RECEIPT_REPLAY_DRIFT:" + key)
    before, after = receipt["original_complete_events"], receipt["transformed_complete_events"]
    bridge.verify(spec, before)
    bridge.verify(other, after)
    need(before["physical_events"]["target_binary_bits"] == bits and
         after["physical_events"]["target_binary_bits"] == bits,
         "AFFINE_EVENT_BITS_DRIFT")
    expected_events = boundary_witness(before, after, a, b)
    need(core.canonical(receipt["physical_boundary_correspondence"]) ==
         core.canonical(expected_events), "AFFINE_BOUNDARY_RECEIPT_DRIFT")
    return True


def certify(spec, offset, slope, bits=10):
    result = produce(spec, offset, slope, bits)
    verify(spec, result)
    return result


def crossing_source():
    return bridge.model(["5/8", "3/4", "7/8", "1", "9/8"])


def all_five_source():
    s = copy.deepcopy(bridge.POSITIVE_TANGENCY)
    s["splines"]["H0"]["controls"] = ["3"]*5
    for k, value in (("C1", "1/3"), ("S1", "1/5"),
                     ("C2", "1/9"), ("S2", "1/13")):
        s["splines"][k]["controls"] = [value]
    return s


class Tests(unittest.TestCase):
    def test_nontrivial_reverse_double_knot_tangency(self):
        r = certify(bridge.POSITIVE_TANGENCY, "3/2", "-1/2")
        self.assertEqual(r["time_map"]["orientation"], "REVERSED")
        self.assertEqual(r["structural_knot_correspondence"],
                         [{"t": "1", "field_multiplicities": {"H0": 2}}])
        event = r["physical_boundary_correspondence"][0]
        self.assertEqual((event["kind"], event["left_order"], event["right_order"]),
                         ("KNOT_TOUCH", 2, 2))

    def test_reverse_swaps_mixed_sided_orders(self):
        r = certify(bridge.MIXED_TANGENCY, "2", "-1")
        event = r["physical_boundary_correspondence"][0]
        self.assertEqual((event["left_order"], event["right_order"]), (1, 2))
        self.assertEqual(r["transformed_complete_events"]["physical_events"]
                         ["physical_root_count"], 1)

    def test_reverse_swaps_crossing_signs(self):
        r = certify(crossing_source(), "2", "-1")
        event = r["physical_boundary_correspondence"][0]
        self.assertEqual(event["kind"], "KNOT_CROSSING")
        self.assertEqual((event["left_sign"], event["right_sign"]), (1, -1))

    def test_positive_rational_scale(self):
        r = certify(bridge.POSITIVE_TANGENCY, "0", "1/2")
        self.assertEqual([k["t"] for k in
                          r["structural_knot_correspondence"]], ["2"])
        self.assertEqual([w["old_piece_index"] for w in
                          r["exact_polynomial_correspondence"]], [0, 1])

    def test_all_five_nonzero_coefficients(self):
        r = certify(all_five_source(), "3/2", "-1/2")
        self.assertEqual(r["original_complete_events"]["physical_events"]
                         ["physical_root_count"], 0)

    def test_adversarial_receipt_mutations(self):
        r = certify(bridge.POSITIVE_TANGENCY, "3/2", "-1/2")
        for field, value in (
            ("historical_corpus_membership_claimed", True),
            ("new_historical_closures", ["fake"]),
            ("required_pb_po_discharges", True),
            ("original_supplied_sha256", "0"*64),
            ("exact_polynomial_correspondence", []),
            ("structural_knot_correspondence", []),
            ("physical_boundary_correspondence", []), ("bits", 9)):
            with self.subTest(field=field):
                wrong = copy.deepcopy(r)
                wrong[field] = value
                with self.assertRaises(Nontruth):
                    verify(bridge.POSITIVE_TANGENCY, wrong)
        wrong = copy.deepcopy(r)
        wrong["time_map"]["orientation"] = "FORWARD"
        with self.assertRaises(Nontruth):
            verify(bridge.POSITIVE_TANGENCY, wrong)
        wrong = copy.deepcopy(r)
        wrong["transformed_complete_events"]["physical_events"]["physical_root_count"] = 5
        with self.assertRaises(Nontruth):
            verify(bridge.POSITIVE_TANGENCY, wrong)
        other = copy.deepcopy(bridge.POSITIVE_TANGENCY)
        other["splines"]["H0"]["controls"][0] = "2"
        with self.assertRaises(Nontruth):
            verify(other, r)

    def test_nontruth_invalid_maps(self):
        for a, b in (("0", "0"), ("0", "-0"), ("0", "9"),
                     ("9", "1"), ("0", "1/0"), ("0.0", "1"),
                     ("0", "2/4"), ("0", "1/8")):
            with self.subTest(a=a, b=b), self.assertRaises(Nontruth):
                produce(bridge.POSITIVE_TANGENCY, a, b)
        for a, b in ((0, "1"), ("0", True)):
            with self.assertRaises(Nontruth):
                produce(bridge.POSITIVE_TANGENCY, a, b)
        with self.assertRaises(Nontruth):
            produce(bridge.POSITIVE_TANGENCY, "0", "1", bits=True)

    def test_random_exact_basis_covariance(self):
        rng = random.Random(20261108)
        count = 0
        for p in range(4):
            for _ in range(40):
                interior = sorted(rng.sample(
                    [Q(i, 4) for i in range(1, 8)], rng.randrange(0, 4)))
                knots = [Q(0)]*(p+1) + interior + [Q(2)]*(p+1)
                controls = [Q(rng.randint(-5, 5), rng.randint(1, 9))
                            for _ in range(len(knots)-p-1)]
                if p == 0:
                    controls = [controls[0]]*len(controls)
                old = bridge.spline_parse({
                    "degree": p, "knots": [str(u) for u in knots],
                    "controls": [str(c) for c in controls]})
                a = rng.choice([Q(0), Q(1), Q(3, 2), Q(2)])
                b = rng.choice([Q(1, 2), Q(1), Q(-1), Q(-1, 2)])
                uu = knots if b > 0 else list(reversed(knots))
                cc = controls if b > 0 else list(reversed(controls))
                new = bridge.spline_parse({
                    "degree": p, "knots": [str((u-a)/b) for u in uu],
                    "controls": [str(c) for c in cc]})
                for i in range(25):
                    t = new[1][0] + (new[1][-1]-new[1][0])*Q(i, 24)
                    self.assertEqual(bridge.spline_value(old, a+b*t),
                                     bridge.spline_value(new, t))
                    count += 1
        self.assertEqual(count, 4000)


def contract():
    bridge.contract()
    r = certify(bridge.POSITIVE_TANGENCY, "3/2", "-1/2")
    need(r["original_complete_events"]["physical_events"]["physical_root_count"] == 1 and
         r["transformed_complete_events"]["physical_events"]["physical_root_count"] == 1 and
         not r["historical_corpus_membership_claimed"] and
         r["required_pb_po_discharges"] == 0, "AFFINE_CONTRACT_DRIFT")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.contract:
        contract()
        print("EXACT_BSPLINE_AFFINE_TIME_COVARIANCE_CONTRACT_PASS")
    if args.self_test:
        unittest.main(argv=["unittest"], exit=False)
