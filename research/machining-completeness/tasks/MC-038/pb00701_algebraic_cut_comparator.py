#!/usr/bin/env python3
"""Exact, bounded comparison of separately isolated real-algebraic cuts.

No floating point, primitive element, compositum, transcendental phase-zero
oracle, physical root isolation, or generalized machining admission is claimed.
"""
from __future__ import annotations
from fractions import Fraction as Q
from math import gcd
import json

SCHEMA = "radicadsac-pb00701-algebraic-cut-comparison/1.0"
MAX_DEGREE = 6
MAX_COEFF_BITS = 96
MAX_ENDPOINT_BITS = 256
MAX_WORK_BITS = 8192
MAX_ROUNDS = 64
MAX_CERT_BYTES = 65536

class Refusal(ValueError):
    pass

class ResourceRefusal(RuntimeError):
    pass

def require(condition, reason):
    if not condition:
        raise Refusal(reason)

def bounded(q, max_bits=MAX_WORK_BITS):
    if max(q.numerator.bit_length(), q.denominator.bit_length()) > max_bits:
        raise ResourceRefusal("EXACT_RATIONAL_WORK_BUDGET")
    return q

def trim(p):
    p = list(p)
    while p and p[-1] == 0:
        p.pop()
    return tuple(p)

def derivative(p):
    return trim(tuple(bounded(i*c) for i, c in enumerate(p) if i != 0))

def evaluate(p, x):
    v = Q(0)
    for c in reversed(p):
        v = bounded(v*x + c)
    return v

def remainder(a, b):
    require(bool(b), "ZERO_POLYNOMIAL_DIVISOR")
    r = trim(a)
    while len(r) >= len(b):
        factor = bounded(r[-1]/b[-1])
        offset = len(r)-len(b)
        v = list(r)
        for i, c in enumerate(b):
            v[offset+i] = bounded(v[offset+i] - factor*c)
        r = trim(v)
    return r

def polynomial_gcd(a, b):
    while b:
        a, b = b, remainder(a, b)
    require(bool(a), "UNDEFINED_POLYNOMIAL_GCD")
    return tuple(bounded(x/a[-1]) for x in a)

def sturm(p):
    require(len(p) >= 2, "NONLINEAR_POLYNOMIAL_REQUIRED")
    a = trim(p)
    b = derivative(a)
    seq = [a, b]
    while True:
        r = trim(tuple(-x for x in remainder(a, b)))
        if not r:
            break
        seq.append(r)
        a, b = b, r
    return tuple(seq)

def variations(seq, x):
    signs = []
    for p in seq:
        v = evaluate(p, x)
        if v:
            signs.append(1 if v > 0 else -1)
    return sum(a != b for a,b in zip(signs, signs[1:]))

def root_count(seq, lo, hi):
    require(lo < hi, "INVALID_OPEN_INTERVAL")
    require(evaluate(seq[0], lo) != 0 and evaluate(seq[0], hi) != 0,
            "POLYNOMIAL_ROOT_AT_OPEN_INTERVAL_BOUNDARY")
    count = variations(seq, lo)-variations(seq, hi)
    require(0 <= count <= len(seq[0])-1, "INVALID_STURM_VARIATION")
    return count

def canonical_integer_coefficients(raw):
    require(type(raw) is list and 2 <= len(raw) <= MAX_DEGREE+1,
            "POLYNOMIAL_DEGREE_BUDGET")
    require(all(type(c) is str and 1 <= len(c) <= 32 for c in raw),
            "POLYNOMIAL_COEFFICIENT_SHAPE")
    try:
        ints = tuple(int(c) for c in raw)
    except ValueError as ex:
        raise Refusal("INVALID_POLYNOMIAL_COEFFICIENT") from ex
    require(all(str(n) == c for n,c in zip(ints, raw)), "NONCANONICAL_POLYNOMIAL_COEFFICIENT")
    if any(abs(n).bit_length() > MAX_COEFF_BITS for n in ints):
        raise ResourceRefusal("POLYNOMIAL_COEFFICIENT_BIT_BUDGET")
    require(ints[-1] > 0 and gcd(*ints) == 1,
            "POLYNOMIAL_NOT_POSITIVE_PRIMITIVE")
    return tuple(Q(n) for n in ints)

def rational_from_record(raw):
    require(type(raw) is str and 1 <= len(raw) <= 160,
            "RATIONAL_ENDPOINT_RECORD_SHAPE")
    try:
        q = Q(raw)
    except (ValueError, ZeroDivisionError) as ex:
        raise Refusal("INVALID_RATIONAL_ENDPOINT") from ex
    require(str(q) == raw, "NONCANONICAL_RATIONAL_ENDPOINT")
    if max(q.numerator.bit_length(),q.denominator.bit_length()) > MAX_ENDPOINT_BITS:
        raise ResourceRefusal("RATIONAL_ENDPOINT_BIT_BUDGET")
    return q

def parse_cut(raw):
    require(type(raw) is dict and set(raw) == {"polynomial", "lower", "upper"},
            "INVALID_ALGEBRAIC_CUT_RECORD")
    p = canonical_integer_coefficients(raw["polynomial"])
    lo,hi = rational_from_record(raw["lower"]), rational_from_record(raw["upper"])
    require(lo < hi, "EMPTY_ROOT_ISOLATOR")
    if len(polynomial_gcd(p,derivative(p))) != 1:
        raise Refusal("NON_SQUAREFREE_POLYNOMIAL")
    seq=sturm(p)
    require(root_count(seq,lo,hi)==1, "ISOLATOR_MUST_HAVE_EXACTLY_ONE_OPEN_ROOT")
    return p,lo,hi,seq

def relation_to_rational(cut, q):
    p,lo,hi,seq = cut
    if q <= lo:
        return 1
    if q >= hi:
        return -1
    if evaluate(p,q) == 0:
        return 0
    n=root_count(seq,lo,q)
    require(n in (0,1), "ROOT_SIDE_INCONSISTENT")
    return -1 if n == 1 else 1

def compare(raw_a,raw_b):
    """Proof by Sturm/gcd equality or finitely many exact separating cuts."""
    a,b=parse_cut(raw_a),parse_cut(raw_b)
    p,lo_a,hi_a,sa=a
    h,lo_b,hi_b,sb=b
    common=polynomial_gcd(p,h)
    overlap_lo=max(lo_a,lo_b)
    overlap_hi=min(hi_a,hi_b)
    if overlap_lo < overlap_hi and len(common) > 1:
        shared_count=root_count(sturm(common),overlap_lo,overlap_hi)
        require(shared_count in (0,1), "COMMON_ROOT_ISOLATOR_INCONSISTENT")
        if shared_count == 1:
            return {"schema": SCHEMA,"status":"CERTIFIED", "relation":0,
                    "method":"COMMON_ROOT_GCD", "rounds":0,
                    "gcd":[str(c) for c in common]}
    for rounds in range(MAX_ROUNDS+1):
        if hi_a <= lo_b or hi_b <= lo_a:
            return {"schema":SCHEMA,"status":"CERTIFIED",
                    "relation":-1 if hi_a <= lo_b else 1,
                    "method":"STRICT_RATIONAL_SEPARATION", "rounds":rounds,
                    "gcd":[str(c) for c in common]}
        if rounds == MAX_ROUNDS:
            break
        q = bounded((max(lo_a,lo_b)+min(hi_a,hi_b))/2)
        ra = relation_to_rational((p,lo_a,hi_a,sa),q)
        rb = relation_to_rational((h,lo_b,hi_b,sb),q)
        if ra != rb:
            return {"schema":SCHEMA,"status":"CERTIFIED",
                    "relation": -1 if ra < rb else 1,
                    "method":"STRICT_RATIONAL_SEPARATION", "rounds":rounds+1,
                    "gcd":[str(c) for c in common]}
        require(ra != 0, "UNCERTIFIED_DOUBLE_RATIONAL_ROOT")
        if ra < 0:
            hi_a,hi_b = q,q
        else:
            lo_a,lo_b = q,q
        for endpoint in (lo_a,hi_a,lo_b,hi_b):
            bounded(endpoint,MAX_WORK_BITS)
    raise ResourceRefusal("ALGEBRAIC_ROOT_SEPARATION_ROUND_BUDGET")

def verify_comparison(raw_a,raw_b,submitted):
    try:
        require(type(submitted) is dict, "INVALID_SUBMITTED_CERTIFICATE")
        try:
            blob=json.dumps(submitted, sort_keys=True, separators=(",", ":"))
        except (TypeError,ValueError,RecursionError) as ex:
            raise Refusal("INVALID_CERTIFICATE_ENCODING") from ex
        if len(blob.encode("utf-8")) > MAX_CERT_BYTES:
            raise ResourceRefusal("CERTIFICATE_SIZE_BUDGET")
        expected=compare(raw_a,raw_b)
        require(submitted==expected, "FORGED_COMPARISON_CERTIFICATE")
        return {"status":"CERTIFIED","relation":expected["relation"]}
    except ResourceRefusal as ex:
        return {"status":"RESOURCE_REFUSAL","reason":str(ex),"is_truth_value":False}
    except (Refusal,TypeError,ValueError,KeyError,OverflowError,RecursionError) as ex:
        return {"status":"BLOCKED","reason":str(ex),"is_truth_value":False}
