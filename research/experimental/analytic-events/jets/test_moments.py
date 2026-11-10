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
        self.assertTrue(m.verify_knot_receipt(3, knots, controls, 0, Q(1, 4),
                                              receipt))
        with self.assertRaises(m.Refusal):
            m.verify_knot_receipt(3, knots, controls, 0, Q(1, 4),
                                  dict(receipt, physical_zero_count=3))
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

    def test_preparse_rational_budget_and_malformed_spline_controls(self):
        # Entire canonical 160-bit numerator/denominator pair remains admitted.
        top, bottom = (1 << 159) - 1, (1 << 159) - 3
        canonical = f"{top}/{bottom}"
        self.assertLessEqual(len(canonical), m.MAX_RATIONAL_LITERAL_CHARS)
        self.assertEqual(m.rational(canonical), Q(top, bottom))

        # Pre-parse length refusal must precede Fraction construction, even
        # when a huge leading-zero input would normalize to a tiny rational.
        oversized = "0" * 100_000 + "1/2"
        for invalid in (oversized, "1/" + "0" * 100_000 + "3",
                        " " * 200 + "1/2"):
            with self.subTest(length=len(invalid)):
                with self.assertRaisesRegex(
                        m.Refusal, "RATIONAL_LITERAL_RESOURCE_LIMIT"):
                    m.rational(invalid)
                result = m.attempt(m.rational, invalid)
                self.assertEqual(result["status"], "RESOURCE_REFUSAL_OR_BLOCKED")
                self.assertFalse(result["is_truth_value"])

        for invalid in (True, 3.5, None, {}, b"1/2"):
            with self.subTest(type=type(invalid).__name__):
                with self.assertRaisesRegex(m.Refusal, "NONEXACT_RATIONAL"):
                    m.rational(invalid)

        with self.assertRaisesRegex(m.Refusal, "RATIONAL_LITERAL_RESOURCE_LIMIT"):
            m.source(0, 2, 0, Q(1, 4), {1: ([oversized], [0])})

        knots = [0] * 4 + [1] * 3 + [2] * 4
        for malformed in (None, 7, "0000000"):
            with self.subTest(control=repr(malformed)):
                with self.assertRaisesRegex(m.Refusal, "INVALID_SPLINE_CONTROL_COUNT"):
                    m.clamped_two_span_bezier(
                        3, knots, {0: (malformed, [0] * 7)}, 0, Q(1, 4))

    def test_knot_count_checked_before_element_conversion(self):
        # A3 #5833649987: only fixed-length built-in knot containers are
        # admissible. No length-100000 conversion and no iterator consumption.
        class BombIterator:
            def __init__(self):
                self.pulls = 0

            def __iter__(self):
                self.pulls += 1
                raise AssertionError("UNBOUNDED_KNOT_ITERATOR_CONSUMED")

        knots = [0] * 4 + [1] * 3 + [2] * 4
        controls = {0: ([[0] * 7, [0] * 7])}
        for malformed in ([0] * 100_000, tuple([0] * 12),
                          "0" * 11, None, (x for x in knots)):
            with self.subTest(kind=type(malformed).__name__):
                with self.assertRaisesRegex(
                        m.Refusal, "INVALID_BSPLINE_KNOT_COUNT"):
                    m.clamped_two_span_bezier(
                        3, malformed, controls, 0, Q(1, 4))
                with self.assertRaisesRegex(
                        m.Refusal, "INVALID_BSPLINE_KNOT_COUNT"):
                    m.reversed_spline(3, malformed, controls, 0, Q(1, 4))

        bomb = BombIterator()
        with self.assertRaisesRegex(
                m.Refusal, "INVALID_BSPLINE_KNOT_COUNT"):
            m.clamped_two_span_bezier(3, bomb, controls, 0, Q(1, 4))
        self.assertEqual(bomb.pulls, 0)
        with self.assertRaisesRegex(
                m.Refusal, "INVALID_BSPLINE_KNOT_COUNT"):
            m.reversed_spline(3, bomb, controls, 0, Q(1, 4))
        self.assertEqual(bomb.pulls, 0)

        # Real fixed-length tuples remain admissible. No refusal is a zero
        # certificate; absence of an iterator is an explicit source grammar.
        a, b, knot, binding = m.clamped_two_span_bezier(
            3, tuple(knots), controls, 0, Q(1, 4))
        self.assertEqual(knot, Q(1))
        self.assertEqual(len(binding), 64)
        refusal = m.attempt(m.clamped_two_span_bezier, 3, bomb,
                            controls, 0, Q(1, 4))
        self.assertFalse(refusal["is_truth_value"])
        self.assertEqual(refusal["status"], "RESOURCE_REFUSAL_OR_BLOCKED")

    def test_signed_reversal_preflight_rejects_unbounded_controls(self):
        # A3 exact-head review #5834336109: oversized control arrays used
        # to be copied and returned by the public helper without refusal.
        knots = [0] * 4 + [1] * 3 + [2] * 4
        legal = {0: ([0] * 7, [0] * 7)}

        class Bomb:
            pulls = 0

            def __iter__(self):
                self.pulls += 1
                raise AssertionError("CONTROL_ITERATOR_WAS_CONSUMED")

            def __reversed__(self):
                self.pulls += 1
                raise AssertionError("CONTROL_ITERATOR_WAS_REVERSED")

        bomb = Bomb()
        malformed = (
            ({0: ([0] * 100_000, [0] * 7)}, "INVALID_SPLINE_CONTROL_COUNT"),
            ({0: ([0] * 7, [0] * 100_000)}, "INVALID_SPLINE_CONTROL_COUNT"),
            ({0: (bomb, [0] * 7)}, "INVALID_SPLINE_CONTROL_COUNT"),
            ({0: ([0] * 7, (x for x in range(7)))},
             "INVALID_SPLINE_CONTROL_COUNT"),
            ({0: None}, "INVALID_SPLINE_HARMONIC"),
            ({0: ([0] * 7,)}, "INVALID_SPLINE_HARMONIC"),
            ({0: ([0] * 7, [0] * 7), 1: ([0] * 100_000, [0] * 7)},
             "INVALID_SPLINE_CONTROL_COUNT"),
            ({9: ([0] * 7, [0] * 7)}, "INVALID_SPLINE_HARMONIC"),
            ({True: ([0] * 7, [0] * 7)}, "INVALID_SPLINE_HARMONIC"),
            ({}, "INVALID_SPLINE_CHANNELS"),
            (None, "INVALID_SPLINE_CHANNELS"),
        )
        for controls, reason in malformed:
            with self.subTest(kind=reason, shape=type(controls).__name__):
                with self.assertRaisesRegex(m.Refusal, reason):
                    m.reversed_spline(3, knots, controls, 0, Q(1, 4))
        self.assertEqual(bomb.pulls, 0)

        # Correct shape is insufficient: refuse noncanonical source content
        # and transformations that violate the emitted source budget.
        with self.assertRaisesRegex(m.Refusal, "INVALID_RATIONAL"):
            m.reversed_spline(
                3, knots, {0: ([0] * 6 + ["not-a-rational"], [0] * 7)},
                0, Q(1, 4))
        with self.assertRaisesRegex(
                m.Refusal, "NONCANONICAL_ZERO_HARMONIC_SINE"):
            m.reversed_spline(3, knots, {0: ([0] * 7, [1] * 7)},
                              0, Q(1, 4))
        with self.assertRaisesRegex(m.Refusal, "UNSUPPORTED_SPLINE_KNOT_PATTERN"):
            m.reversed_spline(3, [0] * 4 + [1] * 2 + [2] * 5,
                              legal, 0, Q(1, 4))
        with self.assertRaisesRegex(m.Refusal, "SOURCE_DOMAIN_RESOURCE_LIMIT"):
            m.reversed_spline(3, knots, legal, 0, Q(1, 4), A=10)

        # Each admitted degree roundtrips complete original source data;
        # a true C0 knot remains a structural knot after negative reversal.
        for p in (1, 2, 3):
            source = (p, [0] * (p + 1) + [1] * p + [2] * (p + 1),
                      {0: ([0] * (2 * p + 1), [0] * (2 * p + 1))},
                      0, Q(1, 4))
            once = m.reversed_spline(*source)
            twice = m.reversed_spline(*once)
            self.assertEqual(
                m.clamped_two_span_bezier(*source)[3],
                m.clamped_two_span_bezier(*twice)[3])
            self.assertEqual(
                m.knot_germ(*once)["status"], "CONTINUUM_BOTH_SIDES")

    def test_refusal_is_not_a_truth_value(self):
        refused = m.attempt(m.source, 0, 2, 0, 0, {1: ([0], [1])})
        self.assertFalse(refused["is_truth_value"])
        self.assertEqual(refused["status"], "RESOURCE_REFUSAL_OR_BLOCKED")
        s = m.source(0, 2, 0, Q(1, 4), {1: ([0], [1])})
        with self.assertRaises(m.Refusal):
            m.point_germ(s, Q(1, 97))


if __name__ == "__main__":
    unittest.main()
