from receipt_integrity import strict_equal
"""A1 research-only exact rational irreducibility fallback and algebraic-time germ.

Classical Kronecker factor enumeration, finite but resource capped. Not a
complete trigonometric-root isolator, B-spline adapter, or production proof.
"""
from fractions import Fraction as Q
from itertools import product
from math import gcd
from hashlib import sha256
import json

CHANNELS = ("H0", "C1", "S1", "C2", "S2")

class Refusal(ValueError):
    pass

def need(condition, code):
    if not condition:
        raise Refusal(code)

def qread(value, bits=128):
    need(type(value) is str and 0 < len(value) <= 120, "RATIONAL_TOKEN")
    try:
        q = Q(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise Refusal("RATIONAL_TOKEN") from exc
    need(value == f"{q.numerator}/{q.denominator}", "NONCANONICAL_RATIONAL")
    need(max(abs(q.numerator).bit_length(), q.denominator.bit_length()) <= bits, "RATIONAL_BITS")
    return q

def admitted(doc):
    # Capture one bounded owned primitive source BEFORE parsing or digesting.
    # Without this, a caller's nested list could change between the parsed
    # coefficient tuple and json.dumps(doc), authenticating a different germ.
    need(type(doc) is dict and all(type(k) is str for k in doc)
         and set(doc) == {"a", "b", *CHANNELS}, "SOURCE_FIELDS")
    captured = {"a": doc["a"], "b": doc["b"]}
    for key in CHANNELS:
        values = doc[key]
        need(type(values) is list and 1 <= len(values) <= 17, "POLYNOMIAL_SHAPE")
        captured[key] = list(values)
    a, b = qread(captured["a"]), qread(captured["b"])
    need(b != 0, "ZERO_RATE_UNSUPPORTED")
    channels = []
    for key in CHANNELS:
        values = captured[key]
        coeffs = tuple(qread(v) for v in values)
        need(len(coeffs) == 1 or coeffs[-1] != 0, "NONCANONICAL_POLYNOMIAL")
        channels.append(coeffs)
    source_hash = sha256(json.dumps(captured, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()
    return (a, b), channels, source_hash

def trim(seq):
    seq = list(seq)
    while seq and seq[-1] == 0:
        seq.pop()
    return tuple(seq)

def divide(a, b):
    a, b = trim(a), trim(b)
    need(bool(b), "DIVIDE_ZERO")
    r = list(a)
    quotient = [Q(0)] * max(0, len(a) - len(b) + 1)
    while len(r) >= len(b):
        shift = len(r) - len(b)
        scale = r[-1] / b[-1]
        quotient[shift] = scale
        for i, coeff in enumerate(b):
            r[shift + i] -= scale * coeff
        r = list(trim(r))
    return trim(quotient), trim(r)

def evaluate(poly, x):
    out = Q(0)
    for coeff in reversed(poly):
        out = out * x + coeff
    return out

def unique_root(m, lo, hi):
    need(lo < hi and -1024 <= lo < hi <= 1024, "ISOLATION_DOMAIN")
    f = tuple(Q(c) for c in m)
    need(evaluate(f, lo) != 0 and evaluate(f, hi) != 0, "ROOT_ON_BRACKET_BOUNDARY")
    seq = [f, trim(tuple(i*f[i] for i in range(1, len(f))))]
    while seq[-1]:
        _, remainder = divide(seq[-2], seq[-1])
        if not remainder:
            break
        seq.append(tuple(-x for x in remainder))
    def variation(x):
        signs = [1 if v > 0 else -1 for v in (evaluate(p, x) for p in seq) if v]
        return sum(a != b for a, b in zip(signs, signs[1:]))
    need(variation(lo) - variation(hi) == 1, "NOT_ONE_REAL_ROOT")


MAX_TRIAL_DIVISIONS = 20_000
MAX_SIGNED_DIVISORS = 2048
MAX_TUPLES = 5_000
MAX_POINTS = 24


def _integer_divisors(value, counters):
    """All signed nonzero divisors; exact and bounded, never partial."""
    n = abs(value)
    need(n != 0, "EVALUATION_ZERO")
    factors = []
    p = 2
    while p * p <= n:
        counters["trial_divisions"] += 1
        need(counters["trial_divisions"] <= MAX_TRIAL_DIVISIONS,
             "TRIAL_DIVISION_BUDGET")
        if n % p == 0:
            k = 0
            while n % p == 0:
                n //= p
                k += 1
            factors.append((p, k))
        p = 3 if p == 2 else p + 2
    if n > 1:
        factors.append((n, 1))
    positives = [1]
    for prime, exponent in factors:
        mult = 1
        old = tuple(positives)
        for _ in range(exponent):
            mult *= prime
            positives.extend(x * mult for x in old)
            need(2 * len(positives) <= MAX_SIGNED_DIVISORS,
                 "DIVISOR_ENUMERATION_BUDGET")
    return tuple(sorted([d for d in positives] + [-d for d in positives]))


def _pmul(a, b):
    out = [Q(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def _interpolate(xs, ys):
    """Unique rational polynomial of degree < len(xs) at distinct points."""
    answer = [Q(0)] * len(xs)
    for i, (x, y) in enumerate(zip(xs, ys)):
        term = [Q(1)]
        denom = Q(1)
        for j, other in enumerate(xs):
            if j != i:
                term = _pmul(term, [-Q(other), Q(1)])
                denom *= Q(x - other)
        for k, coeff in enumerate(term):
            answer[k] += Q(y) * coeff / denom
    return trim(answer)


def irreducible_by_kronecker(m):
    """Decide Q-irreducibility if exhaustive bounded search finishes.

    On reducible input raise RATIONAL_FACTOR; on cap exhaustion raise a typed
    refusal; never infer irreducibility from a truncated enumeration.
    """
    need(type(m) in (tuple, list) and 3 <= len(m) <= 9, "MINIMAL_DEGREE")
    need(all(type(c) is int and abs(c).bit_length() <= 48 for c in m),
         "MINIMAL_COEFFICIENTS")
    m = tuple(m)
    need(m[-1] > 0 and gcd(*m) == 1, "MINIMAL_PRIMITIVE")
    n = len(m) - 1
    counters = {"trial_divisions": 0, "tested_tuples": 0,
                "interpolated_integer_polynomials": 0}
    for degree in range(1, n // 2 + 1):
        xs = []
        k = 0
        while len(xs) <= degree and k < MAX_POINTS:
            x = 0 if k == 0 else (k + 1) // 2 * (1 if k % 2 else -1)
            if evaluate(m, Q(x)) != 0:
                xs.append(x)
            k += 1
        need(len(xs) == degree + 1, "EVALUATION_POINTS_BUDGET")
        choices = [_integer_divisors(int(evaluate(m, Q(x))), counters) for x in xs]
        tuple_count = 1
        for ds in choices:
            tuple_count *= len(ds)
            need(tuple_count + counters["tested_tuples"] <= MAX_TUPLES,
                 "FACTOR_CANDIDATES_BUDGET")
        for ys in product(*choices):
            counters["tested_tuples"] += 1
            g = _interpolate(xs, ys)
            if len(g) != degree + 1 or any(x.denominator != 1 for x in g):
                continue
            counters["interpolated_integer_polynomials"] += 1
            g = tuple(int(x) for x in g)
            if g[-1] < 0:
                g = tuple(-x for x in g)
            if gcd(*g) != 1:
                continue
            _, remainder = divide(tuple(Q(x) for x in m), tuple(Q(x) for x in g))
            need(bool(remainder), "RATIONAL_FACTOR")
    return counters


def certify(doc, minimal, bracket):
    """Produce source-bound exact algebraic-time order, not global event set."""
    _, channels, source_hash = admitted(doc)
    stats = irreducible_by_kronecker(minimal)
    need(type(bracket) in (tuple, list) and len(bracket) == 2, "BRACKET_SHAPE")
    lo, hi = (qread(x, 64) for x in bracket)
    m = tuple(minimal)
    unique_root(m, lo, hi)
    orders = []
    for poly in channels:
        poly = trim(poly)
        if not poly:
            continue
        v = 0
        while len(poly) >= len(m):
            quotient, remainder = divide(poly, tuple(Q(c) for c in m))
            if remainder:
                break
            poly = quotient
            v += 1
        orders.append(v)
    order = min(orders) if orders else None
    return {"schema": "a1-kronecker-algebraic-germ/1",
            "source_sha256": source_hash,
            "minimal_polynomial": list(m),
            "irreducibility_procedure": "EXHAUSTIVE_KRONECKER_V1",
            "factor_search_counts": stats,
            "root_bracket": [f"{lo.numerator}/{lo.denominator}",
                             f"{hi.numerator}/{hi.denominator}"],
            "root_count": 1,
            "result": "IDENTICAL_ZERO_PIECE" if order is None else
                      "EXACT_ZERO" if order else "EXACT_NONZERO",
            "multiplicity": order if order else None,
            "crossing_parity": bool(order % 2) if order else None,
            "sign": "UNDETERMINED",
            "physical_source_authentication": "UNVERIFIED"}


def verify(doc, receipt):
    try:
        return type(receipt) is dict and strict_equal(certify(
            doc, receipt["minimal_polynomial"], receipt["root_bracket"]), receipt)
    except (KeyError, TypeError, ValueError, ZeroDivisionError, OverflowError):
        return False
