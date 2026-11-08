#!/usr/bin/env python3
"""Exact rational isolating brackets for the unchanged frozen V44 H1+H2 root.

Research only. Every asserted physical sign follows from rational interval
arithmetic, never float/root-scanning or an H1-only substituted coordinate.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
from functools import lru_cache
from math import factorial
import json
import unittest

from pb00701_v44_h2_root_coordinate_20261107 import (
    CASE_ID, SPEC_SHA, ROW_SHA, CORPUS_BLOB, V2_BLOB, EPSILON,
    Refusal, require, parse_rational, verify_original, classify,
)

# Explicitly bounded research implementation, not a universal root solver.
MAX_TARGET_BITS = 64
PRECISIONS = (2, 4, 8, 12, 16, 24, 32, 48, 64)


@lru_cache(maxsize=20)
def pi_bracket(n):
    """Machin and alternating arctan: wholly rational pi enclosure."""
    require(type(n) is int and n in PRECISIONS, "PI_PRECISION_BUDGET")

    def atan_reciprocal(k):
        x = Q(1, k)
        lower = sum(((-1)**j * x**(2*j+1) / (2*j+1)
                     for j in range(2*n)), Q(0))
        upper = lower + x**(4*n+1) / (4*n+1)
        return lower, upper

    a, b = atan_reciprocal(5)
    c, d = atan_reciprocal(239)
    low, high = 16*a - 4*d, 16*b - 4*c
    require(Q(3) < low < high < Q(22, 7), "PI_ENCLOSURE_FAILURE")
    return low, high


def trig_bounds(k, n):
    """Intervals for sin(pi*k),cos(pi*k), using rigorous rational remainders.

    Taylor bounds are about the rational midpoint of a Machin pi enclosure.
    Since |d(sin)/dx| and |d(cos)/dx| <= 1, expanding the argument by the
    pi uncertainty radius preserves both enclosures without assumptions
    about monotonicity of sin or cos across a cell.
    """
    require(type(k) is Q and -Q(1, 2) <= k <= Q(1, 2),
            "TRIG_ARGUMENT_OUT_OF_V44_RANGE")
    pl, pu = pi_bracket(n)
    a, b = sorted((k*pl, k*pu))
    z, radius = (a+b)/2, (b-a)/2
    require(abs(z) < 2, "TRIG_TAYLOR_RANGE")
    sin_t = sum(((-1)**j * z**(2*j+1)/factorial(2*j+1)
                 for j in range(n+1)), Q(0))
    cos_t = sum(((-1)**j * z**(2*j)/factorial(2*j)
                 for j in range(n+1)), Q(0))
    sin_error = abs(z)**(2*n+3)/factorial(2*n+3) + radius
    cos_error = abs(z)**(2*n+2)/factorial(2*n+2) + radius
    return ((sin_t-sin_error, sin_t+sin_error),
            (cos_t-cos_error, cos_t+cos_error))


def scale(k, interval):
    a, b = k*interval[0], k*interval[1]
    return min(a, b), max(a, b)


def sum_intervals(*intervals):
    return (sum((x[0] for x in intervals), Q(0)),
            sum((x[1] for x in intervals), Q(0)))


def full_interval(t, epsilon, n):
    """Rigorous physical F_epsilon(t) bounds in original V44 source time."""
    require(type(t) is Q and Q(0) <= t <= Q(1), "SOURCE_TIME_BOUNDS")
    c, s = -Q(3,2)+t+2*t*t, -Q(1,2)-t+2*t*t
    phase_pi = -Q(1,4)+t/8
    sin_1, cos_1 = trig_bounds(phase_pi, n)
    _, cos_2 = trig_bounds(2*phase_pi, n)
    return sum_intervals(scale(c, cos_1), scale(s, sin_1),
                         scale(epsilon, cos_2))


def certified_sign(t, epsilon, *, max_terms=64):
    """Returns only a strictly proven sign; an ambiguous enclosure refuses."""
    require(type(max_terms) is int and max_terms in PRECISIONS,
            "SIGN_PRECISION_BUDGET")
    for n in PRECISIONS:
        if n > max_terms:
            break
        low, high = full_interval(t, epsilon, n)
        if low > 0:
            return 1
        if high < 0:
            return -1
    raise Refusal("SIGN_UNDECIDED_WITHIN_RATIONAL_BUDGET")


def isolate(bits, epsilon_text="1/100000000", *, max_terms=64):
    """Conservative bisection; both endpoints have strictly certified signs."""
    require(type(bits) is int and 1 <= bits <= MAX_TARGET_BITS,
            "TARGET_BIT_BUDGET")
    epsilon = parse_rational(epsilon_text)
    classify(epsilon_text)  # Exact derivative/uniqueness proof from #448.
    require(certified_sign(Q(0), epsilon, max_terms=max_terms) == -1 and
            certified_sign(Q(1), epsilon, max_terms=max_terms) == 1,
            "ENDPOINT_SIGN_PROOF_FAILED")
    lo, hi = Q(0), Q(1)
    target = Q(1, 2**bits)
    for _ in range(4*bits+16):
        if hi-lo <= target:
            break
        # Avoid a single zero/near-zero midpoint stalling the process.
        pivots = ((lo+hi)/2, (3*lo+hi)/4, (lo+3*hi)/4)
        for pivot in pivots:
            try:
                sign = certified_sign(pivot, epsilon, max_terms=max_terms)
                break
            except Refusal as exc:
                if str(exc) != "SIGN_UNDECIDED_WITHIN_RATIONAL_BUDGET":
                    raise
        else:
            raise Refusal("ALL_RATIONAL_PIVOTS_UNDECIDED")
        if sign < 0:
            lo = pivot
        else:
            hi = pivot
    require(hi-lo <= target, "BRACKET_REFINEMENT_BUDGET")
    require(certified_sign(lo, epsilon, max_terms=max_terms) == -1 and
            certified_sign(hi, epsilon, max_terms=max_terms) == 1,
            "FINAL_BRACKET_SIGN_PROOF_FAILED")
    return lo, hi


def certificate(bits=40):
    # Source identity and historical census established by the independent
    # #448 parent: no arbitrary source may masquerade as frozen V44.
    original = verify_original()
    require(original["row"]["id"] == CASE_ID, "V44_CASE_MISMATCH")
    full_lo, full_hi = isolate(bits, str(EPSILON))
    h1_lo, h1_hi = isolate(bits, "0")
    require(full_hi < h1_lo, "ROOT_ORDER_UNRESOLVED_AT_REQUESTED_BITS")
    return {
        "schema": "mc038-v44-h2-exact-isolation/1.0",
        "evidence_class": "DETERMINISTIC_MODEL",
        "original_case_id": CASE_ID,
        "original_source_sha256": SPEC_SHA, "original_row_sha256": ROW_SHA,
        "frozen_v54_blob": CORPUS_BLOB, "frozen_v2_blob": V2_BLOB,
        "original_parameter": "pb00701-v44-algebraic-orientation",
        "original_h2_epsilon": str(EPSILON),
        "requested_binary_precision": bits,
        "full_h1_h2_root_bracket": [str(full_lo), str(full_hi)],
        "h1_only_control_root_bracket": [str(h1_lo), str(h1_hi)],
        "strict_full_before_h1": True,
        "certified_sign_at_each_lower_endpoint": "NEGATIVE",
        "certified_sign_at_each_upper_endpoint": "POSITIVE",
        "root_count_for_each_equation": 1,
        "both_simple_by_parent_analytic_theorem": True,
        "physical_h2_preserved_in_full_equation": True,
        "newly_resolved_historical_case_ids": [],
        "historical_counts_unchanged": [121, 20, 30, 50],
        "required_pb_po_discharges": 0,
        "pb00701_established": False, "mc_b_established": False,
        "mc1_established": False, "production_authorized": False,
    }


class Tests(unittest.TestCase):
    def test_authenticated_original_and_parent_theorem(self):
        self.assertEqual(verify_original()["row"]["id"], CASE_ID)
        self.assertEqual(classify(str(EPSILON))["exact_root_order"],
                         "FULL_ROOT_STRICTLY_BEFORE_H1_ROOT")

    def test_exact_pi_and_trigonometric_bounds(self):
        for n in (2, 8, 16):
            lo, hi = pi_bracket(n)
            self.assertTrue(Q(3) < lo < hi < Q(22,7))
            (slo, shi), (clo, chi) = trig_bounds(-Q(1,4), n)
            self.assertLess(slo, 0)
            self.assertGreater(shi, -1)
            self.assertGreater(clo, 0)
            self.assertLess(chi, 1)

    def test_certified_source_endpoint_signs(self):
        for epsilon in (Q(0), EPSILON, -EPSILON):
            self.assertEqual(certified_sign(Q(0), epsilon), -1)
            self.assertEqual(certified_sign(Q(1), epsilon), 1)

    def test_finite_exact_nested_brackets(self):
        a, b = isolate(12)
        c, d = isolate(24)
        self.assertTrue(a <= c < d <= b)
        self.assertLessEqual(d-c, Q(1,2**24))

    def test_full_original_and_h1_root_are_disjoint(self):
        result = certificate(40)
        self.assertTrue(result["strict_full_before_h1"])
        self.assertEqual(result["requested_binary_precision"], 40)
        self.assertEqual(result["required_pb_po_discharges"], 0)

    def test_h2_sign_reverse_moves_root_other_way(self):
        zero_lo, zero_hi = isolate(40, "0")
        negative_lo, _ = isolate(40, "-1/100000000")
        self.assertLess(zero_hi, negative_lo)

    def test_every_reported_endpoint_is_strictly_proved(self):
        for eps in ("0", "1/100000000", "-1/100000000"):
            lo, hi = isolate(20, eps)
            self.assertEqual(certified_sign(lo, Q(eps)), -1)
            self.assertEqual(certified_sign(hi, Q(eps)), 1)

    def test_typed_resource_and_grammar_refusals(self):
        for bits in (0, 65, True, "40"):
            with self.assertRaises(Refusal):
                isolate(bits)
        for e in ("1/1", "11/1000", "1e-8", "1/0"):
            with self.assertRaises(Refusal):
                isolate(10, e)
        with self.assertRaises(Refusal):
            full_interval(Q(-1,8), EPSILON, 8)
        with self.assertRaises(Refusal):
            certified_sign(Q(1,2), EPSILON, max_terms=3)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--contract", action="store_true")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--bits", type=int, default=40)
    args = p.parse_args()
    if args.contract:
        print(json.dumps(certificate(args.bits), sort_keys=True))
    if args.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
        if not result.wasSuccessful():
            raise SystemExit(1)
    if not (args.contract or args.self_test):
        p.error("use --contract and/or --self-test")


if __name__ == "__main__":
    main()
