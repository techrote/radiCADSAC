#!/usr/bin/env python3
"""A2-PHASE-001: exact quarter-turn phase-gauge normalization probe.

Standalone research algebra, no MC-038 authority, native solver, or complete
B-spline-source provenance.  All arithmetic is fractions.Fraction.
"""
from fractions import Fraction as F
from functools import reduce
from hashlib import sha256
from math import gcd
import json


class Refusal(ValueError):
    pass


def check(ok, reason):
    if not ok:
        raise Refusal(reason)


def poly(seq):
    check(type(seq) in (tuple, list) and 1 <= len(seq) <= 9, "POLY_SHAPE")
    out = []
    for v in seq:
        check(type(v) in (int, F), "POLY_COEFFICIENT")
        q = F(v)
        check(q.numerator.bit_length() <= 160 and q.denominator.bit_length() <= 160,
              "POLY_BUDGET")
        out.append(q)
    while len(out) > 1 and not out[-1]:
        out.pop()
    return tuple(out)


def plus(a, b):
    return tuple((a[i] if i < len(a) else 0) +
                 (b[i] if i < len(b) else 0)
                 for i in range(max(len(a), len(b))))


def scale(a, k):
    return tuple(k*x for x in a)


def negate(a):
    return scale(a, -1)


def clean(a):
    return poly(a)


def admitted(src):
    """One bounded piece; offset is integral quarter turns, rate rational."""
    check(type(src) is dict and set(src) == {"offset", "rate", "terms"}, "SOURCE_SHAPE")
    a, b = src["offset"], src["rate"]
    check(type(a) in (int, F) and type(b) in (int, F), "PHASE_TYPE")
    a, b = F(a), F(b)
    check(max(a.numerator.bit_length(), a.denominator.bit_length(),
              b.numerator.bit_length(), b.denominator.bit_length()) <= 160,
          "PHASE_BIT_BUDGET")
    check(4*a == int(4*a), "OFFSET_NOT_QUARTER_TURN")
    check(b != 0 and abs(b) <= 4 and b.denominator <= 32, "RATE_BUDGET")
    terms = src["terms"]
    check(type(terms) is dict and len(terms) <= 9, "HARMONIC_SHAPE")
    parsed = {}
    for h, pair in terms.items():
        check(type(h) is int and 0 <= h <= 8, "HARMONIC_BUDGET")
        check(type(pair) in (tuple, list) and len(pair) == 2, "PAIR_SHAPE")
        p, q = poly(pair[0]), poly(pair[1])
        check(h != 0 or not any(q), "ZERO_FREQUENCY_SINE")
        parsed[h] = (p, q)
    return a, b, parsed


def gcd_rationals(freqs):
    den = 1
    for x in freqs:
        den = den * x.denominator // gcd(den, x.denominator)
    integers = [int(x * den) for x in freqs]
    return F(reduce(gcd, integers), den)


def quarter(h, a):
    r = int(4*a*h) % 4
    return ((1, 0), (0, 1), (-1, 0), (0, -1))[r]


def normalize(sources):
    """Return common rational base frequency g and canonical Fourier terms."""
    check(type(sources) in (list, tuple) and 1 <= len(sources) <= 2, "SOURCE_COUNT")
    parsed = [admitted(s) for s in sources]
    freqs = [abs(h*b) for _, b, terms in parsed for h, (p, q) in terms.items()
             if h and (any(p) or any(q))]
    g = gcd_rationals(freqs) if freqs else F(1)
    result = []
    for a, b, terms in parsed:
        out = {0: ((F(0),), (F(0),))}
        for h, (p, q) in terms.items():
            if h == 0:
                oldp, _ = out[0]
                out[0] = (plus(oldp, p), (F(0),))
                continue
            k = h*abs(b)/g
            check(k.denominator == 1, "FREQUENCY_GRID")
            k = int(k)
            c, s = quarter(h, a)
            cp = plus(scale(p, c), scale(q, s))
            sq = plus(scale(p, -s), scale(q, c))
            if b < 0:
                sq = negate(sq)
            oldp, oldq = out.get(k, ((F(0),), (F(0),)))
            out[k] = (plus(oldp, cp), plus(oldq, sq))
        result.append({h: (clean(p), clean(q)) for h, (p, q) in sorted(out.items())
                       if any(p) or any(q)})
    return g, result


def gauss_laurent_source(src, g):
    """INDEPENDENT oracle: rotate complex exponential coefficients, not cos/sin pairs."""
    a, b, terms = admitted(src)
    out = {}
    def add(k, real, imag):
        r, i = out.get(k, ((F(0),), (F(0),)))
        out[k] = (plus(r, real), plus(i, imag))
    for h, (p, q) in terms.items():
        if not h:
            add(0, p, (F(0),))
            continue
        k = int(h*abs(b)/g)
        c, s = quarter(h, a)
        # Coefficient of exp(i*2*pi*h*b*t) is ((P-iQ)/2)*(c+is).
        real = scale(plus(scale(p, c), scale(q, s)), F(1, 2))
        imag = scale(plus(scale(p, s), scale(q, -c)), F(1, 2))
        if b < 0:
            imag = negate(imag)
        add(k, real, imag)
        add(-k, real, negate(imag))
    return {k: (clean(r), clean(i)) for k, (r, i) in out.items()
            if any(r) or any(i)}


def gauss_laurent_normalized(terms):
    out = {}
    for k, (p, q) in terms.items():
        if k == 0:
            out[0] = (p, (F(0),))
        else:
            out[k] = (clean(scale(p, F(1, 2))), clean(scale(q, F(-1, 2))))
            out[-k] = (clean(scale(p, F(1, 2))), clean(scale(q, F(1, 2))))
    return out


def identity(a, b):
    g, pair = normalize((a, b))
    ks = sorted(set(pair[0]) | set(pair[1]))
    equal = all(pair[0].get(k, ((0,), (0,))) == pair[1].get(k, ((0,), (0,))) for k in ks)
    return g, pair, equal


def source_hash(src):
    a, b, terms = admitted(src)
    obj = (str(a), str(b), [(h, [str(x) for x in p], [str(x) for x in q])
                              for h, (p, q) in sorted(terms.items())])
    return sha256(json.dumps(obj, separators=(',', ':')).encode()).hexdigest()


def shifted_carrier(p):
    from math import comb
    return tuple(F(comb(p, i) * (-1)**(p-i)) for i in range(p+1))


def formal_cos_defect_power(m, cutoff=8):
    """Independent exact Taylor oracle in formal z=pi*(t-1)/2."""
    from math import factorial
    one_minus_cos = [F(0)] * (cutoff+1)
    for j in range(1, cutoff//2+1):
        one_minus_cos[2*j] = F((-1)**(j+1), factorial(2*j))
    out = [F(1)] + [F(0)] * cutoff
    for _ in range(m):
        out = [sum(out[i]*one_minus_cos[n-i] for i in range(n+1))
               for n in range(cutoff+1)]
    return out


def run():
    # Fixed finite control of an INFINITE rational-frequency/phase polynomial class.
    trials = 0
    for den in (2, 3, 4, 5):
        for numer in (1, 2, -1):
            for offset in (0, F(1, 4), F(1, 2), F(3, 4)):
                for p in range(4):
                    source = {"offset": offset, "rate": F(numer, den),
                              "terms": {0: ((1, 2), (0,)),
                                        1: ((1, -2, 3), (0, 1)),
                                        2: (shifted_carrier(p), (2, -1))}}
                    g, out = normalize([source])
                    assert gauss_laurent_source(source, g) == gauss_laurent_normalized(out[0])
                    trials += 1
    # Two dissimilar encodings of the SAME nonzero analytic source sin(pi*t/2).
    left = {"offset": F(0), "rate": F(1, 4), "terms": {1: ((0,), (1,))}}
    right = {"offset": F(1, 4), "rate": F(-1, 4), "terms": {1: ((1,), (0,))}}
    g, _, same = identity(left, right)
    assert g == F(1, 4) and same and source_hash(left) != source_hash(right)
    assert gauss_laurent_source(left, g) == gauss_laurent_source(right, g)
    # H0/H1/H2 signed mismatch families: D=c*(t-1)^p*(1-sin(pi*t/2))^m.
    family = 0
    for p in range(9):
        for m in range(3):
            for c in (F(1), F(-3, 5)):
                carrier = scale(shifted_carrier(p), c)
                terms = {1: ((1,), (0,))}
                if m == 0:
                    terms[0] = (carrier, (0,))
                elif m == 1:
                    terms[0] = (carrier, (0,))
                    terms[1] = (plus((F(1),), negate(carrier)), (0,))
                else:
                    terms[0] = (scale(carrier, F(3, 2)), (0,))
                    terms[1] = (plus((F(1),), scale(carrier, -2)), (0,))
                    terms[2] = (scale(carrier, F(1, 2)), (0,))
                rhs = {"offset": F(1, 4), "rate": F(-1, 4), "terms": terms}
                grid, (a, b), equal = identity(left, rhs)
                assert not equal
                assert gauss_laurent_source(rhs, grid) == gauss_laurent_normalized(b)
                # Independently expand the claimed *difference* in original
                # left phase, and compare its full Gaussian-Laurent signature.
                if m == 0:
                    target_terms = {0: (carrier, (0,))}
                elif m == 1:
                    target_terms = {0: (carrier, (0,)),
                                    1: ((0,), negate(carrier))}
                else:
                    target_terms = {0: (scale(carrier, F(3, 2)), (0,)),
                                    1: ((0,), scale(carrier, -2)),
                                    2: (scale(carrier, F(-1, 2)), (0,))}
                target = {"offset": F(0), "rate": F(1, 4), "terms": target_terms}
                grid2, (_, target_c) = normalize([left, target])
                assert grid == grid2
                for k in set(a) | set(b) | set(target_c):
                    r0, i0 = a.get(k, ((F(0),), (F(0),)))
                    r1, i1 = b.get(k, ((F(0),), (F(0),)))
                    rt, it = target_c.get(k, ((F(0),), (F(0),)))
                    assert clean(plus(r1, negate(r0))) == rt
                    assert clean(plus(i1, negate(i0))) == it
                # Independent exact formal Taylor series: lower 2*m vanish.
                coeff = formal_cos_defect_power(m)
                assert all(coeff[i] == 0 for i in range(2*m))
                assert coeff[2*m] == F(1, 2**m)
                # carrier=(t-1)^p*c; first mismatch n=p+2m.
                family += 1
    bad = 0
    for invalid in (
        {"offset": F(1, 8), "rate": F(1, 4), "terms": {1: ((1,), (0,))}},
        {"offset": 0, "rate": 0, "terms": {1: ((1,), (0,))}},
        {"offset": 0, "rate": 1, "terms": {0: ((1,), (1,))}},
        {"offset": 0, "rate": 1, "terms": {9: ((1,), (0,))}},
        {"offset": 0, "rate": 1, "terms": {1: ((1,)*10, (0,))}},
        {"offset": 0, "rate": F(1, 33), "terms": {1: ((1,), (0,))}},
    ):
        try:
            normalize([invalid])
        except Refusal:
            bad += 1
        else:
            raise AssertionError('invalid source admitted')
    assert bad == 6
    print(f"PASS: {trials} exact Gaussian-Laurent source controls; "
          f"{family} mismatched H0/H1/H2 pairs; {bad} typed refusals; "
          "same-function/different-source negative control")


if __name__ == '__main__':
    run()
