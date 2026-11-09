#!/usr/bin/env python3
"""Adversarial exact tests: infinite parameter families, source knots and replay."""
import importlib.util
import unittest
from fractions import Fraction as Q
from math import comb
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "moments", Path(__file__).with_name("cyclotomic_moments.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def gmul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def trig_power(n):
    """Independent Laurent polynomial expansion of (1-sin(theta))**n."""
    state = {0: (Q(1), Q(0))}
    factor = {0: (Q(1), Q(0)), 1: (Q(0), Q(1, 2)),
              -1: (Q(0), Q(-1, 2))}
    for _ in range(n):
        new = {}
        for h, z in state.items():
            for hh, w in factor.items():
                k = h+hh
                v = gmul(z, w)
                old = new.get(k, (Q(0), Q(0)))
                new[k] = old[0]+v[0], old[1]+v[1]
        state = new
    terms = {}
    for h in range(n+1):
        re, im = state[h]
        if h == 0:
            assert im == 0
            terms[h] = ([re], [Q(0)])
        else:
            terms[h] = ([2*re], [-2*im])
    return terms


def times_xminus1_degree(terms, degree):
    p = [Q(comb(degree, k)*(-1)**(degree-k))
         for k in range(degree+1)]
    return {h: ([c*a[0] for c in p], [c*b[0] for c in p])
            for h, (a, b) in terms.items()}


class ResearchControls(unittest.TestCase):
    def test_roots_of_unity(self):
        for n in (4, 8, 12, 16, 24, 48, 60, 64):
            f = m.Field(n)
            c, si = f.trig(Q(1, 4))
            self.assertEqual(c, f.zero)
            self.assertEqual(si, f.one)
            self.assertEqual(f.mult(si, si), f.one)

    def test_sharp_order_family_and_polynomial_amplitude(self):
        # 28 independent constructive Laurent expansions; each parameter
        # (harmonic count, amplitude degree) belongs to an infinite family.
        for harmonic_count in range(1, 8):
            for degree in range(4):
                with self.subTest(harmonics=harmonic_count, degree=degree):
                    terms = times_xminus1_degree(trig_power(harmonic_count), degree)
                    source = m.source(0, 2, 0, Q(1, 4), terms)
                    receipt = m.point_germ(source, 1)
                    self.assertEqual(receipt["status"], "EXACT_POINT_ZERO")
                    self.assertEqual(receipt["order"], 2*harmonic_count+degree)
                    self.assertEqual(receipt["right_sign"], 1)
                    self.assertEqual(receipt["event_kind"],
                                     "TANGENCY" if degree%2 == 0 else "CROSSING")
                    self.assertTrue(m.verify_receipt(source, 1, receipt))
                    self.assertLessEqual(receipt["order"],
                                         receipt["structural_order_bound"])

    def test_jet_cap_falsifier(self):
        s = m.source(0, 2, 0, Q(1, 4), trig_power(6))
        self.assertEqual(m.point_germ(s, 1)["order"], 12)

    def test_identity_zero_and_exact_nonroot(self):
        self.assertEqual(m.point_germ(m.source(0, 2, 0, Q(1, 4),
                                                {0: ([0], [0])}), 1)["status"],
                         "IDENTITY_ZERO_ON_ANALYTIC_SPAN")
        self.assertEqual(m.point_germ(m.source(0, 2, Q(1, 8), Q(1, 4),
                                                {1: ([0], [1])}), 1)["status"],
                         "EXACT_POINT_NONZERO")

    def test_actual_clamped_c0_bspline_sided_orders(self):
        knots = [0]*4 + [1]*3 + [2]*4
        controls = {0: ([[1, Q(1, 3), 0, 0, 0, 0, -1], [0]*7])}
        receipt = m.knot_germ(3, knots, controls, 0, Q(1, 4))
        self.assertEqual(receipt["status"], "SINGLE_PHYSICAL_ZERO_KNOT")
        self.assertEqual(receipt["physical_zero_count"], 1)
        self.assertEqual((receipt["left"]["order"], receipt["right"]["order"]),
                         (2, 3))
        self.assertEqual((receipt["left"]["left_sign"], receipt["right"]["right_sign"]),
                         (1, -1))
        # A signed source-time reversal swaps physical sides, not knot identity.
        params = m.reversed_spline(3, knots, controls, 0, Q(1, 4))
        reversed_receipt = m.knot_germ(*params)
        self.assertEqual((reversed_receipt["left"]["order"],
                          reversed_receipt["right"]["order"]), (3, 2))
        self.assertEqual((reversed_receipt["left"]["left_sign"],
                          reversed_receipt["right"]["right_sign"]), (-1, 1))
        self.assertNotEqual(receipt["spline_sha256"],
                            reversed_receipt["spline_sha256"])

    def test_zero_interval_not_misclassified_as_point(self):
        knots = [0]*4 + [1]*3 + [2]*4
        # Left span identically zero; right span is -(t-1)^3.
        controls = {0: ([[0, 0, 0, 0, 0, 0, -1], [0]*7])}
        receipt = m.knot_germ(3, knots, controls, 0, Q(1, 4))
        self.assertEqual(receipt["status"], "CONTINUUM_ADJACENT_ZERO_KNOT")
        self.assertEqual(receipt["physical_zero_count"], 0)

    def test_forged_receipts_and_malformed_knots(self):
        s = m.source(0, 2, 0, Q(1, 4), trig_power(3))
        receipt = m.point_germ(s, 1)
        with self.assertRaises(m.Refusal):
            m.verify_receipt(s, 1, dict(receipt, order=1))
        with self.assertRaises(m.Refusal):
            m.verify_receipt(m.source(0, 2, 0, Q(1, 4),
                                      {1: ([0], [1])}), 1, receipt)
        with self.assertRaises(m.Refusal):
            m.knot_germ(3, [0]*4+[1]*2+[2]*5,
                        {0: ([[0]*7, [0]*7])}, 0, Q(1, 4))

    def test_refusal_is_not_a_truth_value(self):
        refused = m.attempt(m.source, 0, 2, 0, 0, {1: ([0], [1])})
        self.assertFalse(refused["is_truth_value"])
        self.assertEqual(refused["status"], "RESOURCE_REFUSAL_OR_BLOCKED")
        s = m.source(0, 2, 0, Q(1, 4), {1: ([0], [1])})
        with self.assertRaises(m.Refusal):
            m.point_germ(s, Q(1, 97))


if __name__ == "__main__":
    unittest.main()
