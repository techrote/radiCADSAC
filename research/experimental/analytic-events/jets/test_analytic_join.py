#!/usr/bin/env python3
"""A2-JOIN-001 prospective exact controls and adversarial receipt tests."""
import importlib.util
import unittest
from fractions import Fraction as Q
from math import comb
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "a2_analytic_join", Path(__file__).with_name("analytic_join.py"))
join = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(join)


def controls_for_join(p, c_left, c_right, harmonic=False, bias=0):
    """Genuine clamped C0 degree-p spline for bias+c_side*(t-1)^p.

    For harmonic=True, multiply the polynomial by 1-sin(pi*t/2);
    all supplied channels use the same complete knot/control source.
    """
    cp = [Q(bias + (-1)**p * c_left)] + [Q(bias)] * (2*p-1) + [
        Q(bias + c_right)]
    zero = [Q(0)] * (2*p+1)
    data = {0: (cp, zero)}
    if harmonic:
        data[1] = (zero, [-v for v in cp])
    return data


def knots_for(p):
    return [0] * (p+1) + [1] * p + [2] * (p+1)


def bernstein_evaluate(cp, u):
    p = len(cp) - 1
    return sum(cp[i] * comb(p, i) * u**i * (1-u)**(p-i)
               for i in range(p+1))


class AnalyticJoinControls(unittest.TestCase):
    def test_independent_bernstein_source_identity(self):
        # Degree-p polynomial identity established by p+1 exact points per
        # side, NOT floating samples or an assumed synthetic two-span input.
        for p in range(1, 4):
            for c_left, c_right, bias in ((1, 2, 0), (-3, 4, 7),
                                          (2, 2, 0), (0, 0, 9)):
                cp = controls_for_join(p, c_left, c_right, bias=bias)[0][0]
                for i in range(p+1):
                    u = Q(i, p)
                    with self.subTest(p=p, side="left", u=u):
                        self.assertEqual(bernstein_evaluate(cp[:p+1], u),
                                         Q(bias)+Q(c_left)*(u-1)**p)
                    with self.subTest(p=p, side="right", u=u):
                        self.assertEqual(bernstein_evaluate(cp[p:], u),
                                         Q(bias)+Q(c_right)*u**p)

    def test_finite_mismatch_and_signed_reversal(self):
        # For m=0,1, exact knot regularity is p+2m-1, NOT the C0
        # minimum guaranteed by structural multiplicity p.
        for p in range(1, 4):
            for m in (0, 1):
                for c_left, c_right in ((1, 2), (-3, 4)):
                    terms = controls_for_join(p, c_left, c_right,
                                              harmonic=bool(m), bias=0)
                    args = (p, knots_for(p), terms, 0, Q(1, 4))
                    result = join.analytic_join(*args)
                    n = p+2*m
                    with self.subTest(p=p, m=m, left=c_left, right=c_right):
                        self.assertEqual(result["status"],
                                         "FINITE_DERIVATIVE_MISMATCH")
                        self.assertEqual(result["first_mismatched_derivative"], n)
                        self.assertEqual(result["continuous_derivatives_through"],
                                         n-1)
                        self.assertLessEqual(
                            n, result["difference_germ"]["structural_order_bound"])
                        self.assertEqual(
                            result["difference_germ"]["right_sign"], 1)
                        self.assertEqual(
                            result["difference_germ"]["left_sign"], (-1)**n)
                        self.assertTrue(join.verify_join(*args, result))
                        reversed_args = join.a2.reversed_spline(*args)
                        rev = join.analytic_join(*reversed_args)
                        self.assertEqual(rev["first_mismatched_derivative"], n)
                        self.assertEqual(
                            rev["difference_germ"]["right_sign"], (-1)**(n+1))
                        self.assertNotEqual(rev["spline_sha256"],
                                            result["spline_sha256"])

    def test_removable_knot_is_not_physical_zero_classification(self):
        for p in range(1, 4):
            for m in (0, 1):
                for c, bias in ((2, 0), (0, 7)):
                    args = (p, knots_for(p),
                            controls_for_join(p, c, c, bool(m), bias),
                            0, Q(1, 4))
                    report = join.analytic_join(*args)
                    with self.subTest(p=p, m=m, c=c, bias=bias):
                        self.assertEqual(report["status"],
                                         "ANALYTICALLY_REMOVABLE_KNOT")
                        self.assertIsNone(report["first_mismatched_derivative"])
                        self.assertTrue(report["all_derivatives_match"])
                        self.assertEqual(report["difference_germ"]["status"],
                                         "IDENTITY_ZERO_ON_ANALYTIC_SPAN")
                        self.assertFalse(report["complete_zero_set_certified"])
                        self.assertTrue(join.verify_join(*args, report))

    def test_a3_hostile_join_receipts_exact_parent(self):
        """Real source replay refuses attacker-defined equality at any depth."""
        class EqualAlways(str):
            def __eq__(self, other):
                return True
            __hash__ = str.__hash__

        from copy import deepcopy
        p = 3
        args = (p, knots_for(p), controls_for_join(p, 1, 2, True),
                0, Q(1, 4))
        clean = join.analytic_join(*args)
        self.assertTrue(join.verify_join(*args, clean))
        for field in ("status", "first_mismatched_derivative",
                      "spline_sha256", "production_authorized", "knot"):
            with self.subTest(join_field=field):
                forged = dict(clean, **{field: EqualAlways("FORGED")})
                self.assertTrue(forged == clean)
                with self.assertRaisesRegex(
                        join.a2.Refusal, "FORGED_OR_STALE_JOIN_RECEIPT"):
                    join.verify_join(*args, forged)
        forged = deepcopy(clean)
        forged["difference_germ"]["status"] = EqualAlways("FORGED")
        with self.assertRaisesRegex(
                join.a2.Refusal, "FORGED_OR_STALE_JOIN_RECEIPT"):
            join.verify_join(*args, forged)
        forged = dict(clean, production_authorized=0)
        with self.assertRaisesRegex(
                join.a2.Refusal, "FORGED_OR_STALE_JOIN_RECEIPT"):
            join.verify_join(*args, forged)

    def test_source_binding_and_refusals(self):
        p = 3
        args = (p, knots_for(p), controls_for_join(p, 1, 2, True),
                0, Q(1, 4))
        result = join.analytic_join(*args)
        # Both sources can have the same first mismatch order and even the
        # same DIFFERENCE polynomial while being distinct physical sources.
        altered = (p, knots_for(p), controls_for_join(p, 3, 4, True),
                   0, Q(1, 4))
        other = join.analytic_join(*altered)
        self.assertEqual(result["first_mismatched_derivative"],
                         other["first_mismatched_derivative"])
        self.assertNotEqual(result["spline_sha256"], other["spline_sha256"])
        with self.assertRaises(join.a2.Refusal):
            join.verify_join(*altered, result)
        forged = dict(result, first_mismatched_derivative=0)
        with self.assertRaises(join.a2.Refusal):
            join.verify_join(*args, forged)
        wrong_knots = [0]*4 + [1]*2 + [2]*5
        with self.assertRaises(join.a2.Refusal):
            join.analytic_join(p, wrong_knots, args[2], 0, Q(1, 4))
        invalid_phase = join.a2.attempt(
            join.analytic_join, p, knots_for(p), args[2], 0, 0)
        self.assertEqual(invalid_phase["status"],
                         "RESOURCE_REFUSAL_OR_BLOCKED")
        self.assertFalse(invalid_phase["is_truth_value"])


if __name__ == "__main__":
    unittest.main()
