from receipt_integrity import strict_equal
"""A1 research: exact germ at a certified irrational algebraic time (not a global isolator)."""
from fractions import Fraction as Q
from hashlib import sha256
from math import gcd
import json

CHANNELS = ("H0", "C1", "S1", "C2", "S2")
PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31)

class Refusal(ValueError):
    """Insufficient contract, malformed source or resource refusal; NOT a zero decision."""

def need(condition, reason):
    if not condition:
        raise Refusal(reason)

def qread(s, bits=128):
    need(type(s) is str and len(s) <= 120 and len(s) > 0, "RATIONAL_TOKEN")
    try:
        q = Q(s)
    except (ValueError, ZeroDivisionError) as exc:
        raise Refusal("RATIONAL_TOKEN") from exc
    need(s == f"{q.numerator}/{q.denominator}", "NONCANONICAL_RATIONAL")
    need(max(abs(q.numerator).bit_length(), q.denominator.bit_length()) <= bits, "RATIONAL_BITS")
    return q

def admitted(doc):
    need(type(doc) is dict and set(doc) == {"a", "b", *CHANNELS}, "SOURCE_FIELDS")
    a, b = qread(doc["a"]), qread(doc["b"])
    need(b != 0, "ZERO_RATE_UNSUPPORTED")
    channels = []
    for key in CHANNELS:
        values = doc[key]
        need(type(values) is list and 1 <= len(values) <= 17, "POLYNOMIAL_SHAPE")
        coeffs = tuple(qread(v) for v in values)
        need(len(coeffs) == 1 or coeffs[-1] != 0, "NONCANONICAL_POLYNOMIAL")
        channels.append(coeffs)
    source_hash = sha256(json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()
    return (a, b), channels, source_hash

def trim(a):
    a = list(a)
    while a and a[-1] == 0:
        a.pop()
    return tuple(a)

def divide(a, b):
    a, b = trim(a), trim(b)
    need(bool(b), "DIVIDE_ZERO")
    r = list(a)
    quot = [Q(0)] * max(0, len(a)-len(b)+1)
    while len(r) >= len(b):
        j = len(r)-len(b)
        c = r[-1] / b[-1]
        quot[j] = c
        for i, value in enumerate(b):
            r[j+i] -= c*value
        r = list(trim(r))
    return trim(quot), trim(r)

def evaluate(p, x):
    v = Q(0)
    for c in reversed(p):
        v = v*x+c
    return v

def ftrim(v, p):
    v = [x % p for x in v]
    while v and v[-1] == 0:
        v.pop()
    return tuple(v)

def fdivrem(a, b, p):
    a, b = ftrim(a,p), ftrim(b,p)
    need(bool(b), "MOD_POLY_DIVIDE_ZERO")
    r = list(a)
    while len(r) >= len(b):
        j = len(r)-len(b)
        c = r[-1]*pow(b[-1],-1,p) % p
        for i,v in enumerate(b):
            r[j+i] = (r[j+i]-c*v)%p
        r = list(ftrim(r,p))
    return tuple(r)

def fmul(a,b,p,mod):
    v = [0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            v[i+j] = (v[i+j]+x*y)%p
    return fdivrem(v,mod,p)

def fpow_x(exponent,p,mod):
    acc = (1,)
    base = fdivrem((0,1),mod,p)
    while exponent:
        if exponent & 1:
            acc = fmul(acc,base,p,mod)
        exponent >>= 1
        if exponent:
            base = fmul(base,base,p,mod)
    return acc

def fgcd(a,b,p):
    while b:
        a,b = b,fdivrem(a,b,p)
    return tuple((x*pow(a[-1],-1,p))%p for x in a) if a else ()

def prime_factors(n):
    result = []
    d = 2
    while d*d <= n:
        if n % d == 0:
            result.append(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        result.append(n)
    return result

def irreducible_mod_prime(m, p):
    need(type(p) is int and p in PRIMES, "PRIME_BUDGET")
    n = len(m)-1
    f = ftrim(m,p)
    need(len(f) == n+1, "LEADING_COEFF_MOD_P")
    f = tuple(c*pow(f[-1],-1,p)%p for c in f)
    x = (0,1)
    for factor in prime_factors(n):
        h = fpow_x(p**(n//factor),p,f)
        difference = ftrim(tuple((h[i] if i<len(h) else 0)-(x[i] if i<len(x) else 0) for i in range(max(len(h),2))),p)
        need(fgcd(f,difference,p) == (1,), "NOT_IRREDUCIBLE_MOD_P")
    h = fpow_x(p**n,p,f)
    difference = ftrim(tuple((h[i] if i<len(h) else 0)-(x[i] if i<len(x) else 0) for i in range(max(len(h),2))),p)
    need(not difference, "NOT_IRREDUCIBLE_MOD_P")

def unique_root(m, lo, hi):
    need(lo < hi and -1024 <= lo < hi <= 1024, "ISOLATION_DOMAIN")
    f = tuple(Q(c) for c in m)
    need(evaluate(f,lo) != 0 and evaluate(f,hi) != 0, "ROOT_ON_BRACKET_BOUNDARY")
    seq = [f,trim(tuple(i*f[i] for i in range(1,len(f))))]
    while seq[-1]:
        _, rem = divide(seq[-2],seq[-1])
        if not rem:
            break
        seq.append(tuple(-v for v in rem))
    def variation(x):
        values = [evaluate(s,x) for s in seq]
        signs = [1 if v>0 else -1 for v in values if v != 0]
        return sum(a!=b for a,b in zip(signs,signs[1:]))
    need(variation(lo)-variation(hi)==1, "NOT_ONE_REAL_ROOT")

def certify(doc, minimal, prime, bracket):
    _, channels, source_hash = admitted(doc)
    need(type(minimal) in (tuple,list) and 3 <= len(minimal) <= 9, "MINIMAL_DEGREE")
    need(all(type(x) is int and abs(x).bit_length() <= 48 for x in minimal), "MINIMAL_COEFFICIENTS")
    m = tuple(minimal)
    need(m[-1] > 0 and gcd(*m) == 1, "MINIMAL_PRIMITIVE")
    irreducible_mod_prime(m,prime)
    need(type(bracket) in (tuple,list) and len(bracket)==2, "BRACKET_SHAPE")
    lo,hi = (qread(x,64) for x in bracket)
    unique_root(m,lo,hi)
    orders=[]
    for poly in channels:
        poly = trim(poly)
        if not poly:
            continue
        val = 0
        while len(poly) >= len(m):
            quotient, remainder = divide(poly,tuple(Q(c) for c in m))
            if remainder:
                break
            val += 1
            poly = quotient
        orders.append(val)
    order = min(orders) if orders else None
    return {"schema":"a1-algebraic-degree-germ/1", "source_sha256":source_hash,
            "minimal_polynomial":list(m), "irreducibility_prime":prime,
            "root_bracket":[f"{lo.numerator}/{lo.denominator}",f"{hi.numerator}/{hi.denominator}"], "root_count":1,
            "result":"IDENTICAL_ZERO_PIECE" if order is None else "EXACT_ZERO" if order else "EXACT_NONZERO",
            "multiplicity":order if order else None,
            "crossing_parity":bool(order%2) if order else None,
            "sign":"UNDETERMINED", "physical_source_authentication":"UNVERIFIED"}

def verify(doc, receipt):
    try:
        return type(receipt) is dict and strict_equal(certify(doc, receipt["minimal_polynomial"],
           receipt["irreducibility_prime"], receipt["root_bracket"]), receipt)
    except (KeyError, TypeError, ValueError, ZeroDivisionError, OverflowError):
        return False
