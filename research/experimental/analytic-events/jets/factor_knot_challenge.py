#!/usr/bin/env python3
"""A2 research: independently challenge knot-local product multiplicity.

Run `python3 factor_knot_challenge.py --oracle-only` without A2 sources.
Run `python3 factor_knot_challenge.py` from the A2 research directory to
replay the source-authenticated candidate module as well. Not production code.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction as Q
from math import comb, factorial


def check(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def multiply(a, b, limit):
    out = [Q(0)] * (limit + 1)
    for i, u in enumerate(a):
        for j, v in enumerate(b):
            if i + j <= limit:
                out[i + j] += u * v
    return out


def oracle_only():
    """Exact rational formal-series controls, not finite-sampling proof."""
    count = 0
    for m in range(1, 9):
        for q in range(9):
            limit = q + 2 * m
            # 1-cos(z): sin(pi/2+z)=cos(z).
            base = [Q(0)] * (limit + 1)
            for k in range(1, limit // 2 + 1):
                base[2 * k] = Q((-1) ** (k + 1), factorial(2 * k))
            power = [Q(1)]
            for _ in range(m):
                power = multiply(power, base, limit)
            series = [Q(0)] * q + power
            check(series[:limit], [Q(0)] * limit, f"vanishing q={q}, m={m}")
            check(series[limit], Q(1, 2**m), f"leading q={q}, m={m}")
            count += 1
    # Both vectors have nonnegative nonzero Bernstein coefficients; each
    # endpoint coefficient at the common knot is zero. POS != CLOSED_POSITIVE.
    left, right = [Q(1), Q(0), Q(0)], [Q(0), Q(1, 2), Q(1)]
    assert all(c >= 0 for c in left + right) and any(left) and any(right)
    check(left[-1], Q(0), "left closed endpoint")
    check(right[0], Q(0), "right closed endpoint")
    return count


def polynomial_power(q, scale):
    return [Q(scale) * comb(q, i) * (-1) ** (q - i)
            for i in range(q + 1)]


def source_terms(q, m, scale):
    p = polynomial_power(q, scale)
    if m == 1:
        return {0: (p, [0]), 1: ([0], [-v for v in p])}
    if m == 2:
        return {0: ([Q(3, 2) * v for v in p], [0]),
                1: ([0], [-2 * v for v in p]),
                2: ([-Q(1, 2) * v for v in p], [0])}
    raise AssertionError("A2 executable control only admits m=1,2")


def a2_replay():
    import cyclotomic_moments as a2  # exact same research directory

    cases = 0
    for m in (1, 2):
        for q in range(4):
            for scale in (Q(1), Q(-3, 2)):
                src = a2.source(0, 2, 0, Q(1, 4), source_terms(q, m, scale))
                receipt = a2.point_germ(src, 1)
                check(receipt["order"], q + 2 * m, "product order")
                sign = 1 if scale > 0 else -1
                check(receipt["right_sign"], sign, "product right sign")
                check(receipt["left_sign"], sign * (-1) ** q,
                      "product left sign")
                check(receipt["event_kind"],
                      "TANGENCY" if q % 2 == 0 else "CROSSING",
                      "product parity")
                assert a2.verify_receipt(src, 1, receipt)
                forged = dict(receipt)
                forged["order"] += 1
                try:
                    a2.verify_receipt(src, 1, forged)
                except a2.Refusal:
                    pass
                else:
                    raise AssertionError("forged local order accepted")
                cases += 1

    knots = [Q(0)] * 3 + [Q(1)] * 2 + [Q(2)] * 3
    factor = [Q(1), Q(0), Q(0), Q(1, 2), Q(1)]
    zeros = [Q(0)] * 5
    # Genuine degree-2 C0 spline: factor left=(1-t)^2,
    # factor right=(t-1); multiply by (1-sin(pi*t/2)).
    controls = {0: (factor, zeros),
                1: (zeros, [-v for v in factor])}
    receipt = a2.knot_germ(2, knots, controls, 0, Q(1, 4))
    check(receipt["status"], "SINGLE_PHYSICAL_ZERO_KNOT", "knot type")
    check(receipt["physical_zero_count"], 1, "one physical knot event")
    check((receipt["left"]["order"], receipt["right"]["order"]),
          (4, 3), "asymmetric one-sided product orders")
    check((receipt["left"]["left_sign"], receipt["right"]["right_sign"]),
          (1, 1), "outer physical signs")
    assert a2.verify_knot_receipt(2, knots, controls, 0, Q(1, 4), receipt)
    rev = a2.reversed_spline(2, knots, controls, 0, Q(1, 4), 2)
    reversed_receipt = a2.knot_germ(*rev)
    check((reversed_receipt["left"]["order"],
           reversed_receipt["right"]["order"]), (3, 4), "reversed orders")
    check((reversed_receipt["left"]["left_sign"],
           reversed_receipt["right"]["right_sign"]), (1, 1), "reversed signs")
    tampered = deepcopy(controls)
    tampered[0][0][0] = Q(2)  # same knot value, different complete source
    try:
        a2.verify_knot_receipt(2, knots, tampered, 0, Q(1, 4), receipt)
    except a2.Refusal:
        pass
    else:
        raise AssertionError("modified complete spline source reused receipt")

    # Nonzero C0 knot with unequal side derivatives and nontrivial
    # cyclotomic phase. Neither a zero nor a sided zero-order claim.
    nonzero = {0: ([3, 3, 3, 4, 6], zeros),
               1: ([0, 1, 2, 3, 2], [1, 0, 0, 2, 3])}
    nz = a2.knot_germ(2, knots, nonzero, Q(1, 8), Q(1, 4))
    check(nz["status"], "NONZERO_KNOT", "nonzero asymmetric C0 knot")
    check((nz["left"]["order"], nz["right"]["order"]),
          (0, 0), "nonzero orders")
    check((nz["left"]["right_sign"], nz["right"]["right_sign"]),
          (1, 1), "shared nonzero knot sign")
    nrev = a2.knot_germ(*a2.reversed_spline(
        2, knots, nonzero, Q(1, 8), Q(1, 4), 2))
    check(nrev["status"], "NONZERO_KNOT", "reversed nonzero knot")
    check((nrev["left"]["right_sign"], nrev["right"]["right_sign"]),
          (1, 1), "reversed nonzero signs")
    return cases + 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oracle-only", action="store_true")
    args = parser.parse_args()
    total = oracle_only()
    print(f"PASS: {total} exact rational formal-series and Bernstein controls")
    if args.oracle_only:
        print("A2 published module replay: NOT EXECUTED (--oracle-only)")
        return
    replay = a2_replay()
    print(f"PASS: {replay} source-authenticated A2 cases incl. C0 knots")


if __name__ == "__main__":
    main()
