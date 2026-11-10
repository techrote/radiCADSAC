"""A1 research-only exact square lift of an H1 trigonometric germ.

Finite *admitted* family: F(t)=P(t)R(t-k)^2(sin(pi*t)-t*cos(pi*t))^2
on [k,k+1], k integer >=3, with a C0 two-piece rational polynomial P.
Exact proof rules and oracle limitations are in SQUARE-LIFT.md. No native codec.
"""
from __future__ import annotations
from receipt_integrity import strict_equal

from dataclasses import dataclass
from fractions import Fraction as Q
from hashlib import sha256
from math import comb
import json

MAX_K = 10000
MAX_DEGREE_P = 3
MAX_DEGREE_R = 3
MAX_BITS = 128
ZERO = (Q(0),)
HALF = Q(1, 2)


class Refusal(ValueError):
    """NONTRUTH: unsupported source, proof condition, or resource budget."""


def rational(x):
    if type(x) is int:
        x = Q(x)
    if type(x) is not Q or max(abs(x.numerator).bit_length(), x.denominator.bit_length()) > MAX_BITS:
        raise Refusal("unsupported rational or coefficient budget")
    return x


def poly(values, maxdegree):
    if type(values) not in (list, tuple) or not 1 <= len(values) <= maxdegree + 1:
        raise Refusal("coefficient vector must be a bounded list/tuple")
    v = tuple(rational(x) for x in values)
    if len(v) > 1 and v[-1] == 0:
        raise Refusal("noncanonical trailing zero")
    return v


def add(a, b):
    c = [Q(0)] * max(len(a), len(b))
    for j, x in enumerate(a): c[j] += x
    for j, x in enumerate(b): c[j] += x
    while len(c) > 1 and not c[-1]: c.pop()
    return tuple(c)


def mul(a, b):
    c = [Q(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b): c[i+j] += x*y
    while len(c) > 1 and not c[-1]: c.pop()
    return tuple(c)


def scale(a, factor):
    return tuple(x * factor for x in a)


def evaluate(a, u):
    v = Q(0)
    for x in reversed(a): v = v*u + x
    return v


def derivative(a):
    return tuple(i*a[i] for i in range(1, len(a))) or ZERO


def bernstein_coefficients(a, lo, hi):
    """Exact Bernstein coefficients of p(lo+(hi-lo)v), v in [0,1]."""
    if not lo < hi: raise Refusal("invalid ordered cell")
    # Translate power basis to v, then v^i = sum_{j>=i} C(j,i)/C(n,i) B_j^n(v).
    powers = [Q(0)] * len(a)
    for i, ai in enumerate(a):
        for j in range(i+1):
            powers[j] += ai*comb(i,j)*lo**(i-j)*(hi-lo)**j
    n = len(a)-1
    return tuple(sum((powers[i]*Q(comb(j,i),comb(n,i)) for i in range(j+1)), Q(0))
                 for j in range(n+1))


def positive(a, lo, hi):
    """Sufficient exact condition; not a general polynomial positivity decider."""
    b = bernstein_coefficients(a, lo, hi)
    if not all(x > 0 for x in b):
        raise Refusal("Bernstein positivity not certified")
    return b


@dataclass(frozen=True)
class Spec:
    k: int
    left_p: tuple
    right_p: tuple
    r: tuple

    def __post_init__(self):
        validate(self)


def validate(s):
    if type(s) is not Spec or type(s.k) is not int or not 3 <= s.k <= MAX_K:
        raise Refusal("integer k outside admitted range")
    left = poly(s.left_p, MAX_DEGREE_P)
    right = poly(s.right_p, MAX_DEGREE_P)
    r = poly(s.r, MAX_DEGREE_R)
    if type(s.left_p) is not tuple or type(s.right_p) is not tuple or type(s.r) is not tuple:
        raise Refusal("source vectors must be immutable tuples")
    if (left, right, r) != (s.left_p, s.right_p, s.r) or any(
        type(v) is not Q for vec in (s.left_p, s.right_p, s.r) for v in vec
    ):
        raise Refusal("noncanonical source")
    if evaluate(left, HALF) != evaluate(right, HALF):
        raise Refusal("C0 seam mismatch")
    positive(left, Q(0), HALF)
    positive(right, HALF, Q(1))
    if r != ZERO:
        positive(r, Q(0), Q(1))
    return s


def make_spec(k, left_p=(Q(7,4), Q(1,2)), right_p=(Q(3,2), Q(1)), r=(Q(1),)):
    # Validate bounded container length BEFORE conversion, including rejecting generators.
    left_p = poly(left_p, MAX_DEGREE_P)
    right_p = poly(right_p, MAX_DEGREE_P)
    r = poly(r, MAX_DEGREE_R)
    return Spec(k, left_p, right_p, r)


def channels(s, p):
    """Formal H0/H1/H2 coefficients in u=t-k, phase exactly pi*t."""
    t = (Q(s.k), Q(1))
    t2 = mul(t,t)
    q = mul(p, mul(s.r, s.r))
    c0 = scale(mul(q, add(t2, (Q(1),))), HALF)
    c2 = scale(mul(q, add(t2, (Q(-1),))), HALF)
    s2 = scale(mul(q, t), Q(-1))
    return {"c0": [str(x) for x in c0], "c1": ["0"], "s1": ["0"],
            "c2": [str(x) for x in c2], "s2": [str(x) for x in s2]}


def payload(s):
    validate(s)
    return {"grammar": "A1-H2-SQUARE-LIFT-1", "phase_basis": "PI_TURNS",
            "phase_offset": "0", "phase_rate": "1", "domain": [str(s.k), str(s.k+1)],
            "coordinate": "u=t-k", "k": s.k,
            "left_p": [str(x) for x in s.left_p],
            "right_p": [str(x) for x in s.right_p],
            "r": [str(x) for x in s.r],
            "left_h": channels(s, s.left_p), "right_h": channels(s, s.right_p)}


def source_hash(s):
    b = json.dumps(payload(s), sort_keys=True, separators=(",", ":")).encode("ascii")
    return sha256(b).hexdigest()


def issue(s):
    """Replay a finite exact theorem schema, not a general event solver."""
    validate(s)
    k = s.k
    seam = evaluate(s.left_p, HALF)
    base = {"schema": "a1-square-lift-receipt-v1", "source_sha256": source_hash(s),
            "phase_basis": "PI_TURNS", "proof_rule": "SQUARE_OF_MONOTONE_TAN_MINUS_ID",
            "interval": [str(k), str(k+1)], "knot": str(Q(2*k+1,2)),
            "seam_value": str(seam * evaluate(s.r, HALF)**2),
            "left_end_value": str(evaluate(s.left_p, Q(0))*evaluate(s.r,Q(0))**2*k*k),
            "right_end_value": str(evaluate(s.right_p,Q(1))*evaluate(s.r,Q(1))**2*(k+1)**2)}
    if s.r == ZERO:
        return {**base, "classification": "IDENTICAL_ZERO_CONTINUUM",
                "zero_set": [str(k), str(k+1)], "genuine_physical_kink": False,
                "knot_right_minus_left_derivative": "0", "strict_exterior_sign": "NONE"}
    jump = (evaluate(derivative(s.right_p),HALF)-evaluate(derivative(s.left_p),HALF))*evaluate(s.r,HALF)**2
    lo = Q(2*k+1,2) - Q(1,3*k)
    return {**base, "classification": "ONE_TRANSCENDENTAL_ORDER_2_TOUCH",
            "root_bracket_open": [str(lo),str(Q(2*k+1,2))],
            "root_count_total": 1, "root_order": 2, "crosses": False,
            "strict_exterior_sign": "POSITIVE", "genuine_physical_kink": jump != 0,
            "knot_right_minus_left_derivative": str(jump)}


def verify(s, receipt):
    try:
        return type(receipt) is dict and strict_equal(issue(s), receipt)
    except (Refusal, OverflowError, TypeError, ValueError, AttributeError):
        return False


if __name__ == "__main__":
    import unittest
    from test_square_lift import SquareLiftTests
    unittest.main(module="test_square_lift", verbosity=2)
