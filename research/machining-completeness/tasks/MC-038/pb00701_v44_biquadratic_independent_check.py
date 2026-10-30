#!/usr/bin/env python3
"""Independent exact-interval and linear-algebra challenge of fixed V44 K arithmetic.

This is an adversarial deterministic-model checker, not an algebraic-child theorem,
a general compositum implementation or a second physical/geometry oracle.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
from itertools import product
from math import isqrt
import unittest

import pb00701_v44_two_quadratic_cut_restriction as owner

SCHEMA = "radicadsac-pb00701-fixed-biquadratic-independent-check/1.0"
PARENT_BLOB = "46b89ccb449bb37f3c07b14d6de5e9fb92c50352"
BITS = (8, 16, 32, 64, 128, 256, 512)
MAX_INPUT_BITS = 1024

class Refusal(ValueError):
    pass

class ResourceRefusal(RuntimeError):
    pass

def coefficients(raw):
    if type(raw) is not tuple or len(raw) != 4 or any(type(x) is not Q for x in raw):
        raise Refusal("FOUR_EXACT_RATIONAL_COEFFICIENTS_REQUIRED")
    if any(max(abs(x.numerator).bit_length(), x.denominator.bit_length()) > MAX_INPUT_BITS for x in raw):
        raise ResourceRefusal("COEFFICIENT_BIT_BUDGET")
    return raw

def sqrt_bounds(n, bits):
    """Strict dyadic enclosure, computed using integer square root alone."""
    scale = 1 << bits
    floor = isqrt(n * scale * scale)
    return Q(floor, scale), Q(floor + 1, scale)

def interval_sign(raw, refinements=BITS):
    """Independent strict sign; never infer zero from interval overlap.

    Independence of 1,sqrt2,sqrt3,sqrt6 supplies the only exact zero test:
    if (a+b√2)+(c+d√2)√3=0 with rational coefficients, then either
    c=d=0, or sqrt3 is in Q(sqrt2). The latter is impossible since
    (x+y√2)^2=3 implies xy=0 and rational squares 3 or 3/2.
    """
    values = coefficients(raw)
    if not any(values):
        return 0
    for bits in refinements:
        if type(bits) is not int or bits < 1 or bits > 1024:
            raise ResourceRefusal("INVALID_REFINEMENT_BUDGET")
        lower = upper = values[0]
        for coeff, n in zip(values[1:], (2, 3, 6)):
            lo, hi = sqrt_bounds(n, bits)
            if coeff >= 0:
                lower += coeff * lo
                upper += coeff * hi
            else:
                lower += coeff * hi
                upper += coeff * lo
        if lower > 0:
            return 1
        if upper < 0:
            return -1
    raise ResourceRefusal("STRICT_INTERVAL_SIGN_UNRESOLVED")

def independent_product(a, b):
    """Independent group-algebra table for basis 1,√2,√3,√6."""
    a, b = coefficients(a), coefficients(b)
    result = [Q(0)] * 4
    for i in range(4):
        for j in range(4):
            result[i ^ j] += a[i] * b[j] * (2 if i & j & 1 else 1) * (3 if i & j & 2 else 1)
    return tuple(result)

def independent_inverse(a):
    """Solve L_a(x)=1 by rational Gaussian elimination, not nested conjugation."""
    a = coefficients(a)
    if not any(a):
        raise Refusal("ZERO_INVERSE")
    basis = [tuple(Q(int(i == j)) for i in range(4)) for j in range(4)]
    columns = [independent_product(a, e) for e in basis]
    rows = [[columns[j][i] for j in range(4)] + [Q(int(i == 0))] for i in range(4)]
    for col in range(4):
        pivot = next((row for row in range(col, 4) if rows[row][col] != 0), None)
        if pivot is None:
            raise Refusal("SINGULAR_MULTIPLICATION_MATRIX")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        factor = rows[col][col]
        rows[col] = [v / factor for v in rows[col]]
        for row in range(4):
            if row != col:
                factor = rows[row][col]
                rows[row] = [x - factor * y for x, y in zip(rows[row], rows[col])]
    result = tuple(row[4] for row in rows)
    if independent_product(a, result) != (Q(1), Q(0), Q(0), Q(0)):
        raise Refusal("INDEPENDENT_INVERSE_ROUNDTRIP_FAILED")
    return result

def challenge():
    # Live source lineage and frozen deterministic-case contract, not a fake CI-only stub.
    if owner.parent.bridge.previous.git_blob(owner.parent.bridge.previous.TASK /
            "pb00701_v44_two_quadratic_cut_restriction.py") != PARENT_BLOB:
        raise Refusal("PINNED_FIELD_OWNER_DRIFT")
    owner.pins()
    record = owner.attempt()
    if (record.get("status") != owner.SUCCESS or
            record.get("source_sha256") != "d3b3a90024ea283dfd96811b8fc2b66ceff621b3b48defc44c77f85557adbba2" or
            record.get("synthetic_open_root_counts") != [1, 0, 0] or
            record.get("historical_v54_admitted") is not False or
            record.get("mc_b_established") is not False or
            record.get("production_authorized") is not False):
        raise Refusal("PINNED_FROZEN_SOURCE_PROOF_NOT_REPLAYED")
    checked = 0
    nonzero = []
    for entries in product(range(-2, 3), repeat=4):
        v = tuple(map(Q, entries))
        expected = interval_sign(v)
        if owner.K(v).sign() != expected:
            raise Refusal("INDEPENDENT_SIGN_DISAGREEMENT:" + repr(entries))
        if any(v):
            nonzero.append(v)
        checked += 1
    unit = (Q(1), Q(0), Q(0), Q(0))
    # Distinct algorithms: 4x4 rational linear solve vs nested-conjugation inverse.
    for v in nonzero[::17]:
        inv = independent_inverse(v)
        if inv != owner.K(v).inverse().v or independent_product(v, inv) != unit:
            raise Refusal("INDEPENDENT_INVERSE_DISAGREEMENT:" + repr(v))
    pairs = 0
    for a, b in zip(nonzero[::19], reversed(nonzero[::23])):
        independent = independent_product(a, b)
        if independent != (owner.K(a) * owner.K(b)).v:
            raise Refusal("INDEPENDENT_PRODUCT_DISAGREEMENT")
        if interval_sign(independent) != interval_sign(a) * interval_sign(b):
            raise Refusal("PRODUCT_SIGN_LAW_DISAGREEMENT")
        pairs += 1
    return dict(schema=SCHEMA, status="FIXED_BIQUADRATIC_CROSSCHECK_PASSED",
        evidence_class="DETERMINISTIC_MODEL", checked_vectors=checked,
        checked_inverses=len(nonzero[::17]), checked_products=pairs,
        interval_bits=list(BITS), original_source_sha256=record["source_sha256"],
        synthetic_cut_is_historical_owner=False, general_field_oracle=False,
        general_irrational_phase_zero_decider=False, historical_v54_admitted=False,
        mc_b_established=False, mc1_established=False, production_authorized=False)

class ArithmeticChallenge(unittest.TestCase):
    def test_strict_interval_refusal_and_zero(self):
        zero = (Q(0),)*4
        self.assertEqual(interval_sign(zero), 0)
        with self.assertRaises(ResourceRefusal):
            interval_sign((Q(-577), Q(408), Q(0), Q(0)), (1,))
        with self.assertRaises(Refusal):
            interval_sign((0, Q(1), Q(0), Q(0)))
        with self.assertRaises(ResourceRefusal):
            interval_sign((Q(1 << 1025), Q(0), Q(0), Q(0)))
        with self.assertRaises(Refusal):
            independent_inverse(zero)
    def test_near_cancellation_both_signs(self):
        v = (Q(-577), Q(408), Q(0), Q(0))
        self.assertEqual(interval_sign(v), -1)
        self.assertEqual(interval_sign(tuple(-x for x in v)), 1)
        # Exact irrational √6 cancellation near two decimal approximants.
        w = (Q(-49), Q(0), Q(0), Q(20))
        self.assertEqual(interval_sign(w), -1)
        self.assertEqual(interval_sign(tuple(-x for x in w)), 1)
    def test_independent_inverse_and_products(self):
        v = (Q(1, 3), Q(-2, 5), Q(7, 11), Q(-3, 13))
        inv = independent_inverse(v)
        self.assertEqual(independent_product(v, inv), (Q(1), Q(0), Q(0), Q(0)))
        self.assertEqual(inv, owner.K(v).inverse().v)
        self.assertEqual(independent_product(v, v), (owner.K(v) * owner.K(v)).v)
    def test_source_bound_full_challenge(self):
        report = challenge()
        self.assertEqual(report["checked_vectors"], 625)
        self.assertFalse(report["mc1_established"])

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--contract", action="store_true")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if not (args.contract or args.self_test):
        p.error("choose at least one check")
    if args.contract:
        import json
        print(json.dumps(challenge(), sort_keys=True))
    if args.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(ArithmeticChallenge))
        raise SystemExit(0 if result.wasSuccessful() else 1)

if __name__ == "__main__":
    main()
