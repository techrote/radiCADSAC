#!/usr/bin/env python3
"""Exact second-order sided zeros for bounded moving H0/H1/H2 physical sources.

Research-only DETERMINISTIC_MODEL. Stacks on #455/#453. A COMPLETE receipt
requires strict enclosures; unsupported or exhausted cases raise NONTRUTH.
A declared polynomial piece interface is NOT proof of an original spline knot.
"""
from __future__ import annotations

import argparse
import copy
import json
import unittest
from fractions import Fraction as Q

import pb00701_generic_interval_events_20261108 as core
import pb00701_generic_zero_knot_extension_20261108 as prior

Nontruth = core.Nontruth
need = core.need
DIVISORS = (8, 16, 32, 64, 128, 256)


def derivative_zero_exactly(source, piece, t):
    """Prove F'(t)=A+pi*B=0 with separately exact rational A=B=0.

    A phase quarter-turn fixes all harmonic sine/cosine values rationally.
    An approximate zero or cancellation of a nonzero rational plus pi
    is deliberately NOT interpreted as exact zero.
    """
    k = source.phase_offset + source.phase_slope*t
    need((2*k).denominator == 1, "DERIVATIVE_ZERO_PHASE_UNSUPPORTED")
    m = int(2*k)
    c1, s1 = ((1, 0), (0, 1), (-1, 0), (0, -1))[m % 4]
    c2 = 1 if m % 2 == 0 else -1
    p = piece.polys
    d = [core.poly_at(core.derivative(poly), t) for poly in p]
    v = [core.poly_at(poly, t) for poly in p]
    rational = d[0] + c1*d[1] + s1*d[2] + c2*d[3]
    pi_coefficient = source.phase_slope * (
        c1*v[2] - s1*v[1] + 2*c2*v[4])
    return rational == 0 and pi_coefficient == 0


def second_bounds(source, piece, lo, hi, precision):
    """Inclusion-isotonic rational enclosure for the complete F''.

    omega_h = pi*h*phase_slope.  Each harmonic contributes
      C'' cos + S'' sin + 2 omega(-C' sin + S' cos)
                        - omega^2(C cos + S sin).
    The product enclosure for omega^2 is intentionally conservative.
    """
    need(piece.lo <= lo <= hi <= piece.hi, "SECOND_DERIVATIVE_OUTSIDE")
    polys = piece.polys
    values = [core.poly_interval(poly, lo, hi) for poly in polys]
    first = [core.poly_interval(core.derivative(poly), lo, hi)
             for poly in polys]
    second = [core.poly_interval(core.derivative(core.derivative(poly)),
                                 lo, hi) for poly in polys]
    total = second[0]
    minus = core.point(Q(-1))
    for harmonic, ci, si in ((1, 1, 2), (2, 3, 4)):
        if not (any(polys[ci]) or any(polys[si])):
            continue
        sin, cos = core.trig_cell(source, harmonic, lo, hi, precision)
        omega = core.mul(core.point(Q(harmonic)*source.phase_slope),
                         core.pi_interval(precision))
        wave = core.add(core.mul(values[ci], cos),
                        core.mul(values[si], sin))
        rotation = core.add(core.mul(first[si], cos),
                            core.mul(minus, core.mul(first[ci], sin)))
        curvature = core.add(core.mul(second[ci], cos),
                             core.mul(second[si], sin))
        total = core.add(total, curvature,
                         core.mul(core.point(Q(2)), core.mul(omega, rotation)),
                         core.mul(minus, core.mul(core.mul(omega, omega), wave)))
    return total


def second_guard(source, piece, t, side):
    """Strict F'' and exact F(t)=F'(t)=0 prove one-sided quadratic sign.

    Taylor's theorem gives F(t+h)=h^2 F''(xi)/2 on either side.
    This proves an isolated zero and each one-sided order 2, without
    asserting a global multiplicity across different source pieces.
    """
    need(side in ("left", "right"), "UNKNOWN_SIDE")
    need(derivative_zero_exactly(source, piece, t),
         "FIRST_DERIVATIVE_NOT_EXACT_ZERO")
    span = piece.hi-piece.lo
    for divisor in DIVISORS:
        delta = span/divisor
        a, b = ((t-delta, t) if side == "left" else (t, t+delta))
        need(piece.lo <= a < b <= piece.hi, "SECOND_GUARD_OUTSIDE")
        for precision in core.PRECISIONS:
            signed_second = core.strict_sign(
                second_bounds(source, piece, a, b, precision))
            if not signed_second:
                continue
            far = core.point_sign(source, piece,
                                  a if side == "left" else b)
            if far != signed_second:
                continue
            return {"lo": str(a), "hi": str(b),
                    "precision": precision, "order": 2,
                    "first_derivative_exact_zero": True,
                    "second_derivative_sign": signed_second,
                    "far_sign": far}
    raise Nontruth("SECOND_ORDER_SIDED_NONTRUTH")


def sided_guard(source, piece, t, side):
    # Exact F(t)=0 is separately established before this call.
    if derivative_zero_exactly(source, piece, t):
        return second_guard(source, piece, t, side)
    first = prior.guard(source, piece, t, side)
    return {"lo": first["lo"], "hi": first["hi"],
            "precision": first["precision"], "order": 1,
            "derivative_sign": first["derivative_sign"],
            "far_sign": first["far_sign"]}


def _produce(source, bits):
    prior.authenticate_source(source)
    need(type(bits) is int and 1 <= bits <= core.MAX_BITS, "BITS_BUDGET")
    states = [prior.physical_boundary_sign(source, i)[0]
              for i in range(len(source.pieces)+1)]
    interiors = []
    for i, piece in enumerate(source.pieces):
        left = sided_guard(source, piece, piece.lo, "right") if states[i] == 0 else None
        right = sided_guard(source, piece, piece.hi, "left") if states[i+1] == 0 else None
        a = core.fraction(left["hi"]) if left else piece.lo
        b = core.fraction(right["lo"]) if right else piece.hi
        child = prior.one_piece(source, piece, a, b)
        cert = core.classify(child, bits=bits)
        interiors.append({"piece": i, "lo": str(a), "hi": str(b),
                          "left_guard": left, "right_guard": right,
                          "child_source_sha256": child.identity,
                          "certificate": cert})
    events = []
    for i, sign in enumerate(states):
        if sign:
            continue
        t = prior.physical_boundary_sign(source, i)[1]
        left_guard = interiors[i-1]["right_guard"] if i else None
        right_guard = interiors[i]["left_guard"] if i < len(source.pieces) else None
        left = left_guard["far_sign"] if left_guard else None
        right = right_guard["far_sign"] if right_guard else None
        kind = ("EXTERIOR_ENDPOINT_ZERO" if left is None or right is None
                else "KNOT_TOUCH" if left == right else "KNOT_CROSSING")
        events.append({"boundary": i, "t": str(t), "kind": kind,
                       "left_sign": left, "right_sign": right,
                       "left_order": left_guard["order"] if left_guard else None,
                       "right_order": right_guard["order"] if right_guard else None})
    return {
        "status": "COMPLETE_RESTRICTED_FIRST_SECOND_BOUNDARY_EVENTS",
        "evidence_class": "DETERMINISTIC_MODEL",
        "source_sha256": source.identity,
        "target_binary_bits": bits,
        "boundary_events": events,
        "interior_certificates": interiors,
        "physical_root_count": len(events) + sum(
            row["certificate"]["physical_root_count"] for row in interiors),
        "new_historical_closures": [],
        "required_pb_po_discharges": 0,
        "pb00701_established": False,
        "mc_b_established": False,
        "mc1_established": False,
        "production_authorized": False,
    }


def verify_extended(source, receipt):
    """Recompute every guard and source-bound child, then compare exact bytes."""
    prior.authenticate_source(source)
    need(type(receipt) is dict and set(receipt) == {
        "status", "evidence_class", "source_sha256", "target_binary_bits",
        "boundary_events", "interior_certificates", "physical_root_count",
        "new_historical_closures", "required_pb_po_discharges",
        "pb00701_established", "mc_b_established", "mc1_established",
        "production_authorized"}, "SECOND_RECEIPT_FIELDS")
    bits = receipt["target_binary_bits"]
    need(type(bits) is int and 1 <= bits <= core.MAX_BITS, "SECOND_RECEIPT_BITS")
    rows = receipt["interior_certificates"]
    need(type(rows) is list and len(rows) == len(source.pieces) and
         type(receipt["boundary_events"]) is list and
         len(receipt["boundary_events"]) <= len(source.pieces)+1,
         "SECOND_RECEIPT_SIZE")
    for i, row in enumerate(rows):
        need(type(row) is dict and set(row) == {
            "piece", "lo", "hi", "left_guard", "right_guard",
            "child_source_sha256", "certificate"} and
             type(row["piece"]) is int and row["piece"] == i,
             "SECOND_CHILD_FIELDS")
        p = source.pieces[i]
        child = prior.one_piece(source, p, core.fraction(row["lo"]),
                                core.fraction(row["hi"]))
        need(type(row["child_source_sha256"]) is str and
             row["child_source_sha256"] == child.identity,
             "SECOND_CHILD_IDENTITY")
        try:
            core.verify_certificate(child, row["certificate"])
        except (KeyError, TypeError, IndexError, AttributeError,
                OverflowError, RecursionError) as exc:
            raise Nontruth("SECOND_CHILD_MALFORMED") from exc
    expected = _produce(source, bits)
    try:
        valid = core.canonical(receipt) == core.canonical(expected)
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise Nontruth("SECOND_RECEIPT_NONCANONICAL") from exc
    need(valid, "SECOND_RECEIPT_REPLAY_DRIFT")
    return True


def certify(source, bits=10):
    result = _produce(source, bits)
    verify_extended(source, result)
    return result


def piece(lo, hi, h0, c1=("1",), s1=("0",), c2=("1/8",), s2=("0",)):
    return {"lo": lo, "hi": hi, "H0": list(h0), "C1": list(c1),
            "S1": list(s1), "C2": list(c2), "S2": list(s2)}


POSITIVE_BOTH_HARMONICS = {
    "phase_offset_pi": "0", "phase_slope_pi": "1",
    "pieces": [
        piece("0", "1", ("7/8",)),
        piece("1", "2", ("7/8",))
    ]
}
MIXED_ORDER = {
    "phase_offset_pi": "0", "phase_slope_pi": "1",
    "pieces": [
        piece("0", "1", ("7/8",)),
        piece("1", "2", ("5/8", "1/4"))
    ]
}
NEGATIVE_BOTH_HARMONICS = {
    "phase_offset_pi": "0", "phase_slope_pi": "1",
    "pieces": [
        piece("3/4", "1", ("1/2",), c2=("1/2",)),
        piece("1", "5/4", ("1/2",), c2=("1/2",))
    ]
}
EXTERIOR_QUADRATIC = {
    "phase_offset_pi": "0", "phase_slope_pi": "1",
    "pieces": [
        piece("0", "1/2", ("-1/4", "0", "4"),
              c1=("1/4",), c2=("0",))
    ]
}
CUBIC_REFUSAL = {
    "phase_offset_pi": "0", "phase_slope_pi": "1",
    "pieces": [
        piece("1", "2", ("-1", "3", "-3", "1"),
              c1=("0",), c2=("0",))
    ]
}


class Tests(unittest.TestCase):
    def test_h1h2_quadratic_touch_true_moving_phase(self):
        src = core.parse_source(POSITIVE_BOTH_HARMONICS)
        rec = certify(src)
        self.assertEqual(rec["physical_root_count"], 1)
        self.assertEqual(rec["boundary_events"], [
            {"boundary": 1, "t": "1", "kind": "KNOT_TOUCH",
             "left_sign": 1, "right_sign": 1,
             "left_order": 2, "right_order": 2}
        ])
        self.assertTrue(verify_extended(src, rec))

    def test_mixed_first_and_second_sided_order(self):
        rec = certify(core.parse_source(MIXED_ORDER))
        self.assertEqual(rec["physical_root_count"], 1)
        self.assertEqual((rec["boundary_events"][0]["left_order"],
                          rec["boundary_events"][0]["right_order"]), (2, 1))
        self.assertEqual((rec["boundary_events"][0]["left_sign"],
                          rec["boundary_events"][0]["right_sign"]), (1, 1))

    def test_negative_quadratic_touch(self):
        rec = certify(core.parse_source(NEGATIVE_BOTH_HARMONICS))
        self.assertEqual(rec["physical_root_count"], 1)
        event = rec["boundary_events"][0]
        self.assertEqual((event["left_sign"], event["right_sign"]), (-1, -1))
        self.assertEqual((event["left_order"], event["right_order"]), (2, 2))

    def test_exterior_order_two_zero(self):
        rec = certify(core.parse_source(EXTERIOR_QUADRATIC))
        self.assertEqual(rec["physical_root_count"], 1)
        event = rec["boundary_events"][0]
        self.assertEqual((event["left_order"], event["right_order"]), (None, 2))
        self.assertEqual(event["kind"], "EXTERIOR_ENDPOINT_ZERO")

    def test_exact_zero_requires_rational_and_pi_coefficients_zero(self):
        doc = copy.deepcopy(POSITIVE_BOTH_HARMONICS)
        src = core.parse_source(doc)
        self.assertTrue(derivative_zero_exactly(src, src.pieces[0], Q(1)))
        doc["pieces"][0]["S1"] = ["1/4"]
        doc["pieces"][1]["S1"] = ["1/4"]
        src = core.parse_source(doc)
        self.assertFalse(derivative_zero_exactly(src, src.pieces[0], Q(1)))

    def test_exact_cubic_flat_contact_refuses(self):
        with self.assertRaises(Nontruth):
            certify(core.parse_source(CUBIC_REFUSAL))

    def test_prior_first_derivative_contract_retained(self):
        src = core.parse_source(prior.MOVING_KNOT)
        rec = certify(src)
        self.assertEqual(rec["physical_root_count"], 1)
        self.assertEqual((rec["boundary_events"][0]["left_order"],
                          rec["boundary_events"][0]["right_order"]), (1, 1))
        self.assertEqual((rec["boundary_events"][0]["left_sign"],
                          rec["boundary_events"][0]["right_sign"]), (1, -1))

    def test_unproved_nonquarterturn_boundary_refuses(self):
        doc = {"phase_offset_pi": "1/3", "phase_slope_pi": "1/2",
               "pieces": [piece("0", "1", ("-1", "1"),
                                c1=("0",), c2=("0",))]}
        with self.assertRaisesRegex(Nontruth, "NON_QUARTER_TURN"):
            certify(core.parse_source(doc))

    def test_certificate_substitution_and_promotion_refuse(self):
        src = core.parse_source(POSITIVE_BOTH_HARMONICS)
        original = certify(src)
        bad = []
        x = copy.deepcopy(original); x["boundary_events"][0]["left_order"] = 1; bad.append(x)
        x = copy.deepcopy(original); x["boundary_events"][0]["kind"] = "KNOT_CROSSING"; bad.append(x)
        x = copy.deepcopy(original); x["physical_root_count"] = 2; bad.append(x)
        x = copy.deepcopy(original); x["mc1_established"] = True; bad.append(x)
        x = copy.deepcopy(original); x["required_pb_po_discharges"] = True; bad.append(x)
        x = copy.deepcopy(original); x["interior_certificates"][0]["child_source_sha256"] = src.identity; bad.append(x)
        x = copy.deepcopy(original); x["interior_certificates"][0]["certificate"]["signed_partition"] = 4; bad.append(x)
        x = copy.deepcopy(original); x["boundary_events"] = [object()]; bad.append(x)
        for index, wrong in enumerate(bad):
            with self.subTest(index=index), self.assertRaises(Nontruth):
                verify_extended(src, wrong)

    def test_second_bounds_exact_polynomial_and_harmonic_challenges(self):
        src = core.parse_source(POSITIVE_BOTH_HARMONICS)
        self.assertTrue(core.strict_sign(
            second_bounds(src, src.pieces[0], Q(7, 8), Q(1), 24)))
        for item in src.pieces:
            self.assertTrue(derivative_zero_exactly(src, item, Q(1)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.contract:
        original = core.verify_authenticated_v44()
        records = {}
        for name, source in (("positive_h1h2", POSITIVE_BOTH_HARMONICS),
                             ("mixed_order", MIXED_ORDER),
                             ("negative_h1h2", NEGATIVE_BOTH_HARMONICS),
                             ("exterior", EXTERIOR_QUADRATIC),
                             ("prior_first_order", prior.MOVING_KNOT)):
            cert = certify(core.parse_source(source))
            records[name] = {"root_count": cert["physical_root_count"],
                             "events": cert["boundary_events"]}
        print(json.dumps({"evidence_class": "DETERMINISTIC_MODEL",
                          "frozen_v44_authenticated": original["case_id"],
                          "cases": records, "new_historical_closures": [],
                          "required_pb_po_discharges": 0,
                          "pb00701_established": False,
                          "mc_b_established": False,
                          "mc1_established": False}, sort_keys=True))
    if args.self_test:
        outcome = unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
        if not outcome.wasSuccessful():
            raise SystemExit(1)
    if not (args.contract or args.self_test):
        parser.error("use --contract and/or --self-test")


if __name__ == "__main__":
    main()
