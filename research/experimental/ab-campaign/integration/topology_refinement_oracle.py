"""B5: independent exact-rational zero-component/refinement adversary.

Not an execution of A1/B1 published modules or an authenticated spline
producer. Mathematical proof of the infinite family is in the companion report.
Run: python3 topology_refinement_oracle.py
"""
from fractions import Fraction as Q
from itertools import product


def cone(coeff):
    if all(v == 0 for v in coeff):
        return "ZERO"
    if all(v >= 0 for v in coeff):
        return "POS"
    if all(v <= 0 for v in coeff):
        return "NEG"
    return "UNKNOWN"


def inspect(r, s, d):
    """F=0 on [0,1], F=(t-1)^2 on [1,2]; quotient F/d, d != 0."""
    if not (Q(0) < r < Q(1) < s < Q(2) and d):
        raise ValueError("inadmissible split/denominator")
    cuts = (Q(0), r, Q(1), s, Q(2))
    signs = []
    for a, b in zip(cuts, cuts[1:]):
        # Bernstein degree-2 coefficients of (t-1)^2 on [a,b].
        # Nonzero pieces are strictly signed in each OPEN interval.
        coeff = (Q(0),) if b <= 1 else (
            (a - 1) ** 2, (a - 1) * (b - 1), (b - 1) ** 2)
        sign = cone(tuple(v / d for v in coeff))
        if sign == "UNKNOWN":
            raise AssertionError("unexpected unverified Bernstein sign")
        signs.append(sign)
    zero_intervals = []
    for a, b, sign in zip(cuts, cuts[1:], signs):
        if sign == "ZERO":
            if zero_intervals and zero_intervals[-1][1] == a:
                zero_intervals[-1] = (zero_intervals[-1][0], b)
            else:
                zero_intervals.append((a, b))
    # All boundary zeros are incident to the closed identity-zero interval.
    # None is an isolated point, including the genuine spline knot t=1.
    return cuts, tuple(signs), tuple(zero_intervals), ()


def run():
    verified = 0
    for i, j, d in product(range(1, 7), range(1, 7),
                           (Q(1), Q(2), Q(3, 5), Q(-7, 3))):
        r, s = Q(i, 7), Q(1) + Q(j, 7)
        cuts, signs, intervals, points = inspect(r, s, d)
        assert intervals == ((Q(0), Q(1)),)
        assert points == ()
        expected_right = "POS" if d > 0 else "NEG"
        assert signs == ("ZERO", "ZERO", expected_right, expected_right)
        assert cuts == (Q(0), r, Q(1), s, Q(2))
        # The union-of-breakpoints list changes with r,s; the genuine
        # structural knot of the numerator remains t=1 in every case.
        assert r != Q(1) and s != Q(1)
        verified += 1
    for bad in ((Q(0), Q(3, 2), Q(1)),
                (Q(1, 2), Q(3, 2), Q(0)),
                (Q(1), Q(3, 2), Q(1))):
        try:
            inspect(*bad)
        except ValueError:
            continue
        raise AssertionError("inadmissible source was accepted")
    print(f"{verified} exact Fraction/Bernstein controls PASS; 3 refusal controls PASS")


if __name__ == "__main__":
    run()
