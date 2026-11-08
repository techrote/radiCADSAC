#!/usr/bin/env python3
"""Finite exact quarter-turn boundary zeros for the generic H0/H1/H2 certifier.

Research-only, bounded DETERMINISTIC_MODEL. This deliberately builds on the
independently qualified but unmerged generic interval certifier in PR #453.
An unsupported exact-zero argument or exhausted interval budget is NONTRUTH.
"""
from __future__ import annotations

import argparse
import copy
import json
import unittest
from fractions import Fraction as Q

import pb00701_generic_interval_events_20261108 as core

Nontruth = core.Nontruth
need = core.need
MAX_GUARD_DIVISOR = 256
MAX_BOUNDARIES = core.MAX_PIECES + 1


def authenticate_source(source):
    """Rebuild the grammar and identity; a hand-forged Source is not a proof."""
    need(type(source) is core.Source, "SOURCE_TYPE")
    document = {
        "phase_offset_pi": str(source.phase_offset),
        "phase_slope_pi": str(source.phase_slope),
        "pieces": [{
            "lo": str(p.lo), "hi": str(p.hi),
            **{key: [str(c) for c in coeff]
               for key, coeff in zip(core.KEYS, p.polys)}
        } for p in source.pieces]
    }
    need(core.parse_source(document) == source,
         "SOURCE_IDENTITY_OR_CONTINUITY_DRIFT")
    return True


def physical_boundary_sign(source, index):
    """Exact zero/sign only at quarter-turns; otherwise enclose nonzero sign."""
    t = source.pieces[0].lo if index == 0 else source.pieces[index-1].hi
    piece = source.pieces[min(index, len(source.pieces)-1)]
    k = source.phase_offset + source.phase_slope*t
    if (2*k).denominator == 1:
        m = int(2*k)
        c1, s1 = ((1, 0), (0, 1), (-1, 0), (0, -1))[m % 4]
        c2 = 1 if m % 2 == 0 else -1
        polys = piece.polys
        value = (core.poly_at(polys[0], t)
                 + c1*core.poly_at(polys[1], t)
                 + s1*core.poly_at(polys[2], t)
                 + c2*core.poly_at(polys[3], t))
        return (1 if value > 0 else -1 if value < 0 else 0), t
    sign = core.point_sign(source, piece, t)
    need(sign != 0, "NON_QUARTER_TURN_BOUNDARY_UNPROVED")
    return sign, t


def guard(source, piece, t, side):
    """Prove a punctured one-sided neighborhood contains no other zero.

    F(t)=0 has already been proved *exactly*, not inferred by a grid.
    F' has one strict sign on the entire closed guard interval, so the
    far endpoint sign and sided absence are consequences of MVT.
    """
    need(side in ("left", "right"), "UNKNOWN_SIDE")
    span = piece.hi-piece.lo
    for divisor in (8, 16, 32, 64, 128, MAX_GUARD_DIVISOR):
        delta = span/divisor
        a, b = ((t-delta, t) if side == "left" else (t, t+delta))
        need(piece.lo <= a < b <= piece.hi, "INVALID_GUARD_DOMAIN")
        for precision in core.PRECISIONS:
            derivative = core.bounds(source, piece, a, b, precision)[1]
            ds = core.strict_sign(derivative)
            if not ds:
                continue
            far = core.point_sign(source, piece, a if side == "left" else b)
            if far != (-ds if side == "left" else ds):
                continue
            return {"lo": str(a), "hi": str(b),
                    "precision": precision, "derivative_sign": ds,
                    "far_sign": far}
    raise Nontruth("ZERO_KNOT_SIDED_DERIVATIVE_NONTRUTH")


def one_piece(source, piece, lo, hi):
    """Only the certified knot-free interior; preserve original identity."""
    need(piece.lo <= lo < hi <= piece.hi, "INTERIOR_EMPTY_OR_OUTSIDE")
    return core.Source(source.phase_offset, source.phase_slope,
                       (core.Piece(lo, hi, piece.polys),), source.identity)


def _produce(source, bits):
    authenticate_source(source)
    need(type(bits) is int and 1 <= bits <= core.MAX_BITS, "BITS_BUDGET")
    need(1 <= len(source.pieces) <= core.MAX_PIECES, "PIECE_BUDGET")
    states = [physical_boundary_sign(source, i)[0]
              for i in range(len(source.pieces)+1)]
    interiors = []
    for i, piece in enumerate(source.pieces):
        left = guard(source, piece, piece.lo, "right") if states[i] == 0 else None
        right = guard(source, piece, piece.hi, "left") if states[i+1] == 0 else None
        a = core.fraction(left["hi"]) if left else piece.lo
        b = core.fraction(right["lo"]) if right else piece.hi
        interior = one_piece(source, piece, a, b)
        certificate = core.classify(interior, bits=bits)
        interiors.append({"piece": i, "lo": str(a), "hi": str(b),
                          "left_guard": left, "right_guard": right,
                          "certificate": certificate})
    events = []
    for i, state in enumerate(states):
        if state:
            continue
        t = physical_boundary_sign(source, i)[1]
        left = interiors[i-1]["right_guard"]["far_sign"] if i else None
        right = interiors[i]["left_guard"]["far_sign"] if i < len(source.pieces) else None
        if left is None or right is None:
            kind = "EXTERIOR_ENDPOINT_ZERO"
        elif left == right:
            kind = "KNOT_TOUCH"
        else:
            kind = "KNOT_CROSSING"
        events.append({"boundary": i, "t": str(t), "kind": kind,
                       "left_sign": left, "right_sign": right})
    return {
        "status": "COMPLETE_RESTRICTED_EXACT_ZERO_BOUNDARIES",
        "evidence_class": "DETERMINISTIC_MODEL",
        "source_sha256": source.identity,
        "target_binary_bits": bits,
        "boundary_events": events,
        "interior_certificates": interiors,
        "physical_root_count": len(events) + sum(
            x["certificate"]["physical_root_count"] for x in interiors),
        "new_historical_closures": [],
        "required_pb_po_discharges": 0,
        "pb00701_established": False,
        "mc_b_established": False,
        "mc1_established": False,
        "production_authorized": False
    }


def verify_extended(source, receipt):
    """Recheck full original coverage, sided derivative signs and child proofs.

    Strict canonical replay also makes type substitution, orphan guards,
    fabricated zero events and undisclosed modified partitions unacceptable.
    """
    authenticate_source(source)
    need(type(receipt) is dict and set(receipt) == {
        "status", "evidence_class", "source_sha256",
        "target_binary_bits", "boundary_events",
        "interior_certificates", "physical_root_count",
        "new_historical_closures", "required_pb_po_discharges",
        "pb00701_established", "mc_b_established",
        "mc1_established", "production_authorized"}, "EXTENDED_RECEIPT_FIELDS")
    bits = receipt["target_binary_bits"]
    need(type(bits) is int and 1 <= bits <= core.MAX_BITS, "RECEIPT_BITS")
    need(type(receipt["boundary_events"]) is list
         and len(receipt["boundary_events"]) <= MAX_BOUNDARIES
         and type(receipt["interior_certificates"]) is list
         and len(receipt["interior_certificates"]) == len(source.pieces),
         "EXTENDED_RECEIPT_BUDGET")
    for index, row in enumerate(receipt["interior_certificates"]):
        need(type(row) is dict and row.get("piece") == index
             and type(row.get("piece")) is int, "INTERIOR_INDEX")
        p = source.pieces[index]
        a, b = core.fraction(row["lo"]), core.fraction(row["hi"])
        child = one_piece(source, p, a, b)
        core.verify_certificate(child, row["certificate"])
    # A second construction pass checks every *original* knot/exterior
    # exact-zero identity, every certified sided derivative over its full
    # guard, every source-time gap, and the signed-event classification.
    expected = _produce(source, bits)
    need(core.canonical(receipt) == core.canonical(expected),
         "EXTENDED_RECEIPT_REPLAY_DRIFT")
    return True


def certify(source, bits=10):
    receipt = _produce(source, bits)
    verify_extended(source, receipt)
    return receipt


def piece(lo, hi, h0, c1=("1",), s1=("0",), c2=("0",), s2=("0",)):
    return {"lo": lo, "hi": hi, "H0": list(h0), "C1": list(c1),
            "S1": list(s1), "C2": list(c2), "S2": list(s2)}


MOVING_KNOT = {
    "phase_offset_pi": "0", "phase_slope_pi": "1/2",
    "pieces": [
        piece("0", "1", ("1/8",), c2=("1/8",)),
        piece("1", "2", ("3/16", "-1/8", "1/16"), c2=("1/8",))
    ]
}
TOUCH_KNOT = {
    "phase_offset_pi": "-1/2", "phase_slope_pi": "1/2",
    "pieces": [
        piece("0", "1", ("-21/10", "1"), c2=("1/10",)),
        piece("1", "2", ("-1/10", "-1"), c2=("1/10",))
    ]
}
ENDPOINT_SINE = {
    "phase_offset_pi": "0", "phase_slope_pi": "1/2",
    "pieces": [piece("0", "1", ("0",), c1=("0",), s1=("1",))]
}
BOTH_ENDPOINTS = {
    "phase_offset_pi": "0", "phase_slope_pi": "1",
    "pieces": [piece("0", "1", ("0",), c1=("0",), s1=("1",))]
}


class Tests(unittest.TestCase):
    def test_moving_true_knot_h1_h2_crossing(self):
        src = core.parse_source(MOVING_KNOT)
        result = certify(src)
        self.assertEqual(result["physical_root_count"], 1)
        self.assertEqual(result["boundary_events"], [
            {"boundary": 1, "t": "1", "kind": "KNOT_CROSSING",
             "left_sign": 1, "right_sign": -1}
        ])
        self.assertEqual(sum(row["certificate"]["physical_root_count"]
                             for row in result["interior_certificates"]), 0)

    def test_knot_touch_different_sided_derivatives(self):
        src = core.parse_source(TOUCH_KNOT)
        result = certify(src)
        self.assertEqual(result["physical_root_count"], 1)
        self.assertEqual(result["boundary_events"][0]["kind"], "KNOT_TOUCH")
        self.assertEqual((result["boundary_events"][0]["left_sign"],
                          result["boundary_events"][0]["right_sign"]), (-1, -1))
        self.assertEqual(result["interior_certificates"][0]
                         ["right_guard"]["derivative_sign"], 1)
        self.assertEqual(result["interior_certificates"][1]
                         ["left_guard"]["derivative_sign"], -1)

    def test_actual_exterior_root_and_both_endpoints(self):
        for doc, expected in ((ENDPOINT_SINE, 1), (BOTH_ENDPOINTS, 2)):
            with self.subTest(expected=expected):
                result = certify(core.parse_source(doc))
                self.assertEqual(result["physical_root_count"], expected)
                self.assertEqual(len(result["boundary_events"]), expected)
                self.assertTrue(all(e["kind"] == "EXTERIOR_ENDPOINT_ZERO"
                                    for e in result["boundary_events"]))

    def test_interior_root_plus_exact_knot_root(self):
        doc = copy.deepcopy(MOVING_KNOT)
        doc["pieces"][1]["H0"] = ["17/8", "-4", "2"]
        result = certify(core.parse_source(doc), bits=8)
        self.assertEqual(result["physical_root_count"], 2)
        self.assertEqual(len(result["boundary_events"]), 1)
        self.assertEqual(result["interior_certificates"][1]
                         ["certificate"]["physical_root_count"], 1)

    def test_non_quarter_turn_exact_zero_refuses(self):
        doc = {"phase_offset_pi": "1/3", "phase_slope_pi": "1/2",
               "pieces": [piece("0", "1", ("-1", "1"), c1=("0",))]}
        with self.assertRaisesRegex(Nontruth, "NON_QUARTER_TURN"):
            certify(core.parse_source(doc))

    def test_flat_derivative_tangency_refuses(self):
        doc = {"phase_offset_pi": "0", "phase_slope_pi": "1/2",
               "pieces": [piece("0", "1", ("0", "0", "1"), c1=("0",))]}
        with self.assertRaises(Nontruth):
            certify(core.parse_source(doc))

    def test_discontinuous_knot_refuses(self):
        doc = copy.deepcopy(MOVING_KNOT)
        doc["pieces"][1]["H0"][0] = "1/8"
        with self.assertRaisesRegex(Nontruth, "KNOT_COEFFICIENT_DISCONTINUITY"):
            core.parse_source(doc)

    def test_hand_forged_source_identity_and_continuity_refuse(self):
        source = core.parse_source(MOVING_KNOT)
        fake = core.Source(source.phase_offset, source.phase_slope,
                           source.pieces, "0"*64)
        with self.assertRaisesRegex(Nontruth, "SOURCE_IDENTITY"):
            certify(fake)
        changed = list(source.pieces)
        right = changed[1]
        polys = list(right.polys)
        polys[0] = (Q(1),)
        changed[1] = core.Piece(right.lo, right.hi, tuple(polys))
        fake = core.Source(source.phase_offset, source.phase_slope,
                           tuple(changed), source.identity)
        with self.assertRaises(Nontruth):
            certify(fake)

    def test_hostile_receipt_substitution_refuses(self):
        src = core.parse_source(TOUCH_KNOT)
        correct = certify(src)
        bad = []
        def mutant():
            return copy.deepcopy(correct)
        x = mutant(); x["physical_root_count"] += 1; bad.append(x)
        x = mutant(); x["boundary_events"][0]["kind"] = "KNOT_CROSSING"; bad.append(x)
        x = mutant(); x["boundary_events"][0]["left_sign"] = True; bad.append(x)
        x = mutant(); x["boundary_events"].clear(); bad.append(x)
        x = mutant(); x["interior_certificates"][0]["right_guard"]["derivative_sign"] *= -1; bad.append(x)
        x = mutant(); x["interior_certificates"][0]["certificate"]["physical_root_count"] = 1; bad.append(x)
        x = mutant(); x["mc_b_established"] = True; bad.append(x)
        x = mutant(); x["new_historical_closures"] = ["invented"]; bad.append(x)
        x = mutant(); x["required_pb_po_discharges"] = True; bad.append(x)
        for index, value in enumerate(bad):
            with self.subTest(index=index), self.assertRaises(Nontruth):
                verify_extended(src, value)

    def test_existing_generic_and_frozen_v44_nonpromotion(self):
        authenticated = core.verify_authenticated_v44()
        self.assertEqual(authenticated["new_historical_closures"], [])
        self.assertEqual(authenticated["required_pb_po_discharges"], 0)
        src = core.parse_source(core.SAMPLES["v44_shape"])
        self.assertEqual(core.classify(src, bits=9)["physical_root_count"], 1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.contract:
        # Read the immutable source and verify the original #453 admission.
        authenticated = core.verify_authenticated_v44()
        results = {}
        for name, doc in (("moving_h1h2_knot", MOVING_KNOT),
                          ("touch_knot", TOUCH_KNOT),
                          ("endpoint", ENDPOINT_SINE),
                          ("both_endpoints", BOTH_ENDPOINTS)):
            cert = certify(core.parse_source(doc))
            results[name] = {"status": cert["status"],
                             "root_count": cert["physical_root_count"],
                             "boundary_events": cert["boundary_events"],
                             "new_historical_closures": []}
        print(json.dumps({"evidence_class": "DETERMINISTIC_MODEL",
                          "frozen_v44_authenticated": authenticated["case_id"],
                          "results": results, "pb00701_established": False,
                          "mc_b_established": False, "mc1_established": False},
                         sort_keys=True))
    if args.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
        if not result.wasSuccessful():
            raise SystemExit(1)
    if not (args.contract or args.self_test):
        parser.error("use --contract and/or --self-test")


if __name__ == "__main__":
    main()
