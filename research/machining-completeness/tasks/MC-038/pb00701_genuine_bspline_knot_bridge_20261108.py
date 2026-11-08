#!/usr/bin/env python3
"""Exact rational B-spline to complete moving H0/H1/H2 event certificates.

Research-only DETERMINISTIC_MODEL. The source vector authenticates *structural*
knots of the supplied B-spline, not membership in the frozen original corpus.
A declared polynomial interface is never accepted as a spline knot by itself.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import unittest
from fractions import Fraction as Q

import pb00701_generic_interval_events_20261108 as core
import pb00701_generic_second_order_boundary_20261108 as events

Nontruth = core.Nontruth
need = core.need
KEYS = core.KEYS
MAX_SOURCE_BYTES = 14000
MAX_CONTROLS = 24
MAX_DEGREE = 3


def source_hash(doc):
    try:
        raw = core.canonical(doc)
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise Nontruth("SPLINE_SOURCE_NONCANONICAL") from exc
    need(len(raw) <= MAX_SOURCE_BYTES, "SPLINE_SOURCE_BYTE_BUDGET")
    return hashlib.sha256(raw).hexdigest()


def spline_parse(raw):
    need(type(raw) is dict and set(raw) == {"degree", "knots", "controls"},
         "SPLINE_FIELDS")
    p = raw["degree"]
    need(type(p) is int and 0 <= p <= MAX_DEGREE, "SPLINE_DEGREE_BUDGET")
    knots, controls = raw["knots"], raw["controls"]
    need(type(knots) is list and type(controls) is list and
         1 <= len(controls) <= MAX_CONTROLS and
         len(knots) == len(controls) + p + 1, "SPLINE_KNOT_CONTROL_COUNT")
    u = tuple(core.fraction(x) for x in knots)
    c = tuple(core.fraction(x) for x in controls)
    need(all(a <= b for a, b in zip(u, u[1:])), "SPLINE_KNOT_ORDER")
    lo, hi = u[0], u[-1]
    need(Q(-8) <= lo < hi <= Q(8), "SPLINE_DOMAIN")
    need(all(x == lo for x in u[:p+1]) and
         all(x == hi for x in u[-(p+1):]) and
         u[p+1] > lo and u[-(p+2)] < hi,
         "SPLINE_NOT_OPEN_CLAMPED")
    multiplicities = {}
    for value in u[p+1:-(p+1)]:
        need(lo < value < hi, "SPLINE_INTERIOR_KNOT_RANGE")
        multiplicities[value] = multiplicities.get(value, 0) + 1
    need(all(m <= max(p, 1) for m in multiplicities.values()),
         "SPLINE_C0_MULTIPLICITY_BUDGET")
    return p, u, c, multiplicities


def spline_value(spline, t):
    """Cox-de Boor rational basis; endpoint uses the open-clamped controls."""
    p, u, c, _ = spline
    need(u[0] <= t <= u[-1], "SPLINE_VALUE_OUTSIDE_DOMAIN")
    if t == u[-1]:
        return c[-1]
    if t == u[0]:
        return c[0]

    def basis(i, degree):
        if degree == 0:
            return Q(int(u[i] <= t < u[i+1]))
        left = Q(0)
        a = u[i+degree] - u[i]
        if a:
            left = (t-u[i])*basis(i, degree-1)/a
        right = Q(0)
        b = u[i+degree+1] - u[i+1]
        if b:
            right = (u[i+degree+1]-t)*basis(i+1, degree-1)/b
        return left + right

    return sum((v*basis(i, p) for i, v in enumerate(c)), Q(0))


def multiply_linear(poly, x):
    result = [Q(0)]*(len(poly)+1)
    for i, a in enumerate(poly):
        result[i] -= a*x
        result[i+1] += a
    return result


def span_polynomial(spline, lo, hi):
    """Exact Newton interpolation, justified by degree-p B-spline span law.

    p+1 distinct interior rational samples determine the full polynomial
    on a knot-free interval. Further non-interpolating probes independently
    check our rational basis and polynomial reconstruction implementation.
    """
    p = spline[0]
    xs = [lo+(hi-lo)*Q(i+1, p+2) for i in range(p+1)]
    divided = [spline_value(spline, t) for t in xs]
    for level in range(1, p+1):
        for j in range(p, level-1, -1):
            divided[j] = (divided[j]-divided[j-1])/(xs[j]-xs[j-level])
    result, term = [Q(0)]*(p+1), [Q(1)]
    for i, a in enumerate(divided):
        for j, value in enumerate(term):
            result[j] += a*value
        term = multiply_linear(term, xs[i])
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    for ratio in (Q(1, 7), Q(2, 7), Q(4, 7), Q(6, 7)):
        t = lo+(hi-lo)*ratio
        need(core.poly_at(tuple(result), t) == spline_value(spline, t),
             "SPLINE_SPAN_RECONSTRUCTION_DRIFT")
    return [str(v) for v in result]


def source_to_pieces(spec):
    """Reconstruct a complete #453 source from *real supplied* knot vectors."""
    source_hash(spec)
    need(type(spec) is dict and set(spec) == {
         "grammar", "phase_offset_pi", "phase_slope_pi", "splines"},
         "SPLINE_SOURCE_FIELDS")
    need(spec["grammar"] == "RATIONAL_BSPLINE_H0H1H2_AFFINE_PHASE/1",
         "SPLINE_SOURCE_GRAMMAR")
    a = core.fraction(spec["phase_offset_pi"])
    b = core.fraction(spec["phase_slope_pi"])
    raw = spec["splines"]
    need(type(raw) is dict and set(raw) == set(KEYS),
         "SPLINE_SOURCE_COEFFICIENTS")
    splines = {key: spline_parse(raw[key]) for key in KEYS}
    bounds = {(v[1][0], v[1][-1]) for v in splines.values()}
    need(len(bounds) == 1, "SPLINE_SOURCE_DOMAIN_MISMATCH")
    lo, hi = next(iter(bounds))
    endpoints = sorted(set(x for _, u, _, _ in splines.values() for x in u))
    need(endpoints[0] == lo and endpoints[-1] == hi and
         len(endpoints)-1 <= core.MAX_PIECES,
         "SPLINE_UNION_SPAN_BUDGET")
    pieces = []
    for l, r in zip(endpoints, endpoints[1:]):
        row = {"lo": str(l), "hi": str(r)}
        for key in KEYS:
            row[key] = span_polynomial(splines[key], l, r)
        pieces.append(row)
    knot_witnesses = [
        {"t": str(t), "field_multiplicities": {
            key: sp[3][t] for key, sp in splines.items() if t in sp[3]}}
        for t in endpoints[1:-1]
    ]
    # This check, in particular, refuses genuinely discontinuous degree-zero
    # coefficient sources rather than inventing a continuous physical law.
    doc = {"phase_offset_pi": str(a), "phase_slope_pi": str(b),
           "pieces": pieces}
    parsed = core.parse_source(doc)
    return doc, parsed, knot_witnesses


def produce(spec, bits=10):
    need(type(bits) is int and 1 <= bits <= core.MAX_BITS, "BITS_BUDGET")
    doc, parsed, knots = source_to_pieces(spec)
    return {
        "status": "COMPLETE_RESTRICTED_BSPLINE_AUTHENTICATED_EVENTS",
        "evidence_class": "DETERMINISTIC_MODEL",
        "supplied_spline_sha256": source_hash(spec),
        "derived_piece_sha256": parsed.identity,
        "genuine_internal_knot_witnesses": knots,
        "derived_piece_source": doc,
        "physical_events": events.certify(parsed, bits=bits),
        "new_historical_closures": [],
        "required_pb_po_discharges": 0,
        "pb00701_established": False,
        "mc_b_established": False,
        "mc1_established": False,
        "production_authorized": False,
    }


def verify(spec, receipt):
    """Bind all prospective claims, knot provenance and parent certificates."""
    need(type(receipt) is dict and set(receipt) == {
        "status", "evidence_class", "supplied_spline_sha256",
        "derived_piece_sha256", "genuine_internal_knot_witnesses",
        "derived_piece_source", "physical_events", "new_historical_closures",
        "required_pb_po_discharges", "pb00701_established",
        "mc_b_established", "mc1_established", "production_authorized"},
         "SPLINE_RECEIPT_FIELDS")
    doc, parsed, knots = source_to_pieces(spec)
    expected = {
        "status": "COMPLETE_RESTRICTED_BSPLINE_AUTHENTICATED_EVENTS",
        "evidence_class": "DETERMINISTIC_MODEL",
        "supplied_spline_sha256": source_hash(spec),
        "derived_piece_sha256": parsed.identity,
        "genuine_internal_knot_witnesses": knots,
        "derived_piece_source": doc,
        "new_historical_closures": [],
        "required_pb_po_discharges": 0,
        "pb00701_established": False,
        "mc_b_established": False,
        "mc1_established": False,
        "production_authorized": False,
    }
    for key, value in expected.items():
        try:
            good = core.canonical(receipt[key]) == core.canonical(value)
        except (TypeError, ValueError, OverflowError, RecursionError) as exc:
            raise Nontruth("SPLINE_RECEIPT_MALFORMED") from exc
        need(good, "SPLINE_RECEIPT_REPLAY_DRIFT:" + key)
    try:
        events.verify_extended(parsed, receipt["physical_events"])
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError,
            RecursionError) as exc:
        raise Nontruth("MALFORMED_PHYSICAL_CERTIFICATE") from exc
    return True


def certify(spec, bits=10):
    receipt = produce(spec, bits)
    verify(spec, receipt)
    return receipt


KNOTS = ["0", "0", "0", "1", "1", "2", "2", "2"]


def spline(degree, knots, controls):
    return {"degree": degree, "knots": knots, "controls": controls}


def model(controls, slope="1"):
    constant = lambda x: spline(0, ["0", "2"], [x])
    return {
        "grammar": "RATIONAL_BSPLINE_H0H1H2_AFFINE_PHASE/1",
        "phase_offset_pi": "0", "phase_slope_pi": slope,
        "splines": {
            "H0": spline(2, list(KNOTS), controls),
            "C1": constant("1"), "S1": constant("0"),
            "C2": constant("1/8"), "S2": constant("0")
        }
    }


# A truly represented double-knot C0 source, with two different quadratic
# H0 laws and a genuine full H1+H2 moving-phase second-order physical zero.
POSITIVE_TANGENCY = model(["9/8", "7/8", "7/8", "7/8", "11/8"])
# Left sided order two, right sided order one at the same true source knot.
MIXED_TANGENCY = model(["7/8", "7/8", "7/8", "1", "9/8"])


def v44_projection():
    """Independent prospective-spline projection matching the frozen V44 law.

    Comparison with #453's frozen-blob-authenticated result is separate from
    this prospective grammar and DOES NOT reassign original proof ownership.
    """
    constant = lambda x: spline(0, ["0", "1"], [x])
    return {
        "grammar": "RATIONAL_BSPLINE_H0H1H2_AFFINE_PHASE/1",
        "phase_offset_pi": "-1/4", "phase_slope_pi": "1/8",
        "splines": {
            "H0": constant("0"),
            "C1": spline(2, ["0", "0", "0", "1", "1", "1"],
                         ["-3/2", "-1", "3/2"]),
            "S1": spline(2, ["0", "0", "0", "1", "1", "1"],
                         ["-1/2", "-1", "1/2"]),
            "C2": constant("1/100000000"), "S2": constant("0")
        }
    }


class Tests(unittest.TestCase):
    def test_true_knot_double_sided_h1_h2_tangency(self):
        rec = certify(POSITIVE_TANGENCY)
        self.assertEqual(rec["genuine_internal_knot_witnesses"],
                         [{"t": "1", "field_multiplicities": {"H0": 2}}])
        self.assertEqual(rec["physical_events"]["physical_root_count"], 1)
        self.assertEqual(rec["physical_events"]["boundary_events"][0]["kind"],
                         "KNOT_TOUCH")
        self.assertEqual([rec["physical_events"]["boundary_events"][0][k]
                          for k in ("left_order", "right_order")], [2, 2])
        self.assertNotEqual(rec["derived_piece_source"]["pieces"][0]["H0"],
                            rec["derived_piece_source"]["pieces"][1]["H0"])

    def test_mixed_true_knot_orders(self):
        rec = certify(MIXED_TANGENCY)
        event = rec["physical_events"]["boundary_events"][0]
        self.assertEqual((event["left_order"], event["right_order"]), (2, 1))
        self.assertEqual((event["left_sign"], event["right_sign"]), (1, 1))

    def test_v44_frozen_shape_comparison(self):
        doc, _, knots = source_to_pieces(v44_projection())
        self.assertEqual(doc, core.SAMPLES["v44_shape"])
        self.assertEqual(knots, [])

    def test_cubic_nonuniform_basis_and_span_polynomials(self):
        data = model(["0", "0", "0", "0", "0"])
        data["splines"]["H0"] = spline(3,
            ["0", "0", "0", "0", "1", "1", "2", "2", "2", "2"],
            ["1/3", "1/2", "1", "2", "3", "5"])
        doc, src, knots = source_to_pieces(data)
        self.assertEqual(knots[0]["field_multiplicities"]["H0"], 2)
        sp = spline_parse(data["splines"]["H0"])
        for t in (Q(1, 7), Q(4, 5), Q(9, 7), Q(13, 7)):
            p = src.pieces[0 if t < 1 else 1]
            self.assertEqual(core.poly_at(p.polys[0], t), spline_value(sp, t))
        self.assertEqual(len(doc["pieces"]), 2)

    def test_degree_and_multiplicity_refusals(self):
        for mutation in (
            lambda x: x["splines"]["H0"].__setitem__("degree", True),
            lambda x: x["splines"]["H0"].__setitem__("degree", 4),
            lambda x: x["splines"]["H0"].__setitem__(
                "knots", ["0", "0", "0", "1", "1", "1", "2", "2", "2"]),
            lambda x: x["splines"]["H0"].__setitem__(
                "knots", ["0", "0", "0", "2", "1", "2", "2", "2"]),
        ):
            doc = copy.deepcopy(POSITIVE_TANGENCY)
            mutation(doc)
            with self.assertRaises(Nontruth):
                source_to_pieces(doc)

    def test_c0_discontinuity_refuses(self):
        doc = copy.deepcopy(POSITIVE_TANGENCY)
        doc["splines"]["H0"] = spline(0, ["0", "1", "2"], ["0", "1"])
        with self.assertRaisesRegex(Nontruth, "KNOT_COEFFICIENT_DISCONTINUITY"):
            source_to_pieces(doc)

    def test_unsupported_source_and_union_span_budget(self):
        doc = copy.deepcopy(POSITIVE_TANGENCY)
        doc["original_source_id"] = "fake"
        with self.assertRaises(Nontruth):
            source_to_pieces(doc)
        doc = copy.deepcopy(POSITIVE_TANGENCY)
        doc["splines"]["H0"] = spline(1,
            ["0", "0", "1/4", "1/2", "3/4", "1", "3/2", "2", "2"],
            ["0"]*7)
        with self.assertRaisesRegex(Nontruth, "SPLINE_UNION_SPAN_BUDGET"):
            source_to_pieces(doc)

    def test_receipt_knot_identity_and_promotion_mutations_refuse(self):
        rec = certify(POSITIVE_TANGENCY)
        for name, changed in (
            ("fake_knot", ("genuine_internal_knot_witnesses",
                           [{"t": "3/2", "field_multiplicities": {"H0": 2}}])),
            ("source", ("derived_piece_sha256", "0"*64)),
            ("promote", ("pb00701_established", True)),
            ("boolean_zero", ("required_pb_po_discharges", False)),
        ):
            with self.subTest(name=name):
                copyrec = copy.deepcopy(rec)
                copyrec[changed[0]] = changed[1]
                with self.assertRaises(Nontruth):
                    verify(POSITIVE_TANGENCY, copyrec)

    def test_event_certificate_mutation_refuses(self):
        rec = certify(POSITIVE_TANGENCY)
        rec["physical_events"]["boundary_events"][0]["left_order"] = 1
        with self.assertRaises(Nontruth):
            verify(POSITIVE_TANGENCY, rec)

    def test_changed_spline_controls_invalidate_original_receipt(self):
        rec = certify(POSITIVE_TANGENCY)
        spec = copy.deepcopy(POSITIVE_TANGENCY)
        spec["splines"]["H0"]["controls"][0] = "13/8"
        with self.assertRaises(Nontruth):
            verify(spec, rec)

    def test_noncanonical_rational_and_domain_refuse(self):
        for raw in ("2/4", "1.0", "9999999999999999999999999999999999999999999999999999"):
            doc = copy.deepcopy(POSITIVE_TANGENCY)
            doc["splines"]["H0"]["controls"][0] = raw
            with self.assertRaises(Nontruth):
                source_to_pieces(doc)


def contract():
    # Re-execute the actual independently pinned frozen source/census check.
    # The shape comparison must be exact; identity is never inherited from a
    # user-supplied prospective source document.
    core.verify_authenticated_v44()
    doc, _, knots = source_to_pieces(v44_projection())
    need(doc == core.SAMPLES["v44_shape"] and knots == [],
         "FROZEN_V44_PROJECTION_DRIFT")
    rec = certify(POSITIVE_TANGENCY)
    need(rec["physical_events"]["physical_root_count"] == 1 and
         len(rec["genuine_internal_knot_witnesses"]) == 1,
         "GENUINE_KNOT_EVENT_CONTRACT_DRIFT")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.contract:
        contract()
        print("GENUINE_BSPLINE_KNOT_BRIDGE_CONTRACT_PASS")
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        need(result.wasSuccessful(), "SELF_TEST_FAILED")
    if not (args.contract or args.self_test):
        parser.error("select --contract or --self-test")
