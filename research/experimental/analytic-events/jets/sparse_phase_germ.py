#!/usr/bin/env python3
"""A2-SPARSE-001: exact local difference germ for two rational-phase H0/H1/H2 sources.

Deterministic research model; not a B-spline source authenticator or event isolator.
No floating-point tests are used.  Execute: python3 -m unittest -v test_sparse_phase_germ.py
"""
from fractions import Fraction as F
from math import comb, factorial
from hashlib import sha256
import json

SCHEMA = 'radicadsac-a2-sparse-phase-germ/1'

class Refusal(ValueError):
    pass

def check(ok, why):
    if not ok:
        raise Refusal(why)

def rat(x):
    check(type(x) in (int, F), 'NONEXACT_RATIONAL')
    x = F(x)
    check(max(x.numerator.bit_length(), x.denominator.bit_length()) <= 160,
          'INPUT_BIT_BUDGET')
    return x

def polynomial(seq):
    check(type(seq) in (tuple, list) and 1 <= len(seq) <= 4, 'POLY_SHAPE')
    p = tuple(rat(v) for v in seq)
    while len(p) > 1 and p[-1] == 0:
        p = p[:-1]
    return p

def admit(raw):
    check(type(raw) is dict and set(raw) == {'interval', 'phase', 'terms'}, 'SOURCE_SHAPE')
    interval, phase, terms = raw['interval'], raw['phase'], raw['terms']
    check(type(interval) in (tuple, list) and len(interval) == 2, 'INTERVAL_SHAPE')
    check(type(phase) in (tuple, list) and len(phase) == 2, 'PHASE_SHAPE')
    l, r = (rat(x) for x in interval)
    a, b = (rat(x) for x in phase)
    check(l < r and b != 0, 'INVALID_DOMAIN_OR_RATE')
    check(type(terms) is dict and 1 <= len(terms) <= 3, 'TERMS_SHAPE')
    parsed = {}
    for h, pair in terms.items():
        check(type(h) is int and 0 <= h <= 2, 'HARMONIC_GRAMMAR')
        check(type(pair) in (tuple, list) and len(pair) == 2, 'HARMONIC_PAIR')
        p, q = polynomial(pair[0]), polynomial(pair[1])
        check(h != 0 or q == (F(0),), 'ZERO_HARMONIC_SINE')
        parsed[h] = (p, q)
    return (l, r), (a, b), dict(sorted(parsed.items()))

def canonical(src):
    (l, r), (a, b), terms = admit(src)
    return {'interval': [str(l), str(r)], 'phase': [str(a), str(b)],
            'terms': [[h, [str(x) for x in p], [str(x) for x in q]]
                      for h, (p, q) in terms.items()]}

def fingerprint(src):
    return sha256(json.dumps(canonical(src), sort_keys=True, separators=(',', ':'))
                  .encode('ascii')).hexdigest()

def shift(p, t):
    return tuple(sum(p[i] * comb(i, j) * t**(i-j)
                     for i in range(j, len(p))) for j in range(len(p)))

def budget(x):
    check(max(x.numerator.bit_length(), x.denominator.bit_length()) <= 4096,
          'INTERMEDIATE_BIT_BUDGET')
    return x

def formal_difference(left, right, t0):
    """Amplitude-degree -> sparse abs-frequency -> [cos amplitude, sin amplitude]."""
    t0 = rat(t0)
    groups = {}
    for raw, direction in ((left, -1), (right, 1)):
        (l, r), (a, b), terms = admit(raw)
        check(l <= t0 <= r, 'POINT_OUTSIDE_SOURCE')
        for h, (p, q) in terms.items():
            if not any(p) and not any(q):
                continue
            turns = h * (a + b*t0)
            check((4*turns).denominator == 1, 'NON_QUARTER_LOCAL_PHASE')
            c, s = ((1, 0), (0, 1), (-1, 0), (0, -1))[int(4*turns) % 4]
            freq = abs(2*h*b)
            ps, qs = shift(p, t0), shift(q, t0)
            for j in range(max(len(ps), len(qs))):
                x = ps[j] if j < len(ps) else 0
                y = qs[j] if j < len(qs) else 0
                cosine = direction * (x*c + y*s)
                sine = direction * (y*c - x*s) * (1 if b > 0 else -1)
                if h == 0:
                    sine = 0
                old = groups.setdefault(j, {}).setdefault(freq, [F(0), F(0)])
                old[0] = budget(old[0] + cosine)
                old[1] = budget(old[1] + sine)
    return {j: {f: (c, s) for f, (c, s) in frequencies.items() if c or s}
            for j, frequencies in groups.items()}

def moment(frequencies, k):
    coeff = F(0)
    for f, (c, s) in frequencies.items():
        if k % 2 == 0:
            coeff += c * (-1)**(k//2) * f**k / factorial(k)
        else:
            coeff += s * (-1)**((k-1)//2) * f**k / factorial(k)
        budget(coeff)
    return coeff

def atan_interval(x, n):
    val = sum(F((-1)**k, (2*k+1)*x**(2*k+1)) for k in range(n))
    tail = F((-1)**n, (2*n+1)*x**(2*n+1))
    return (min(val, val+tail), max(val, val+tail))

def pi_interval(n):
    a, b = atan_interval(5, n), atan_interval(239, n)
    return 16*a[0]-4*b[1], 16*a[1]-4*b[0]

def sign_pi_poly(terms):
    """Rigorous rational interval sign for sum coeff*pi**k, or typed refusal."""
    for n in (2, 4, 8, 16, 32, 64):
        lo, hi = pi_interval(n)
        lower = upper = F(0)
        for k, c in terms:
            x, y = c*lo**k, c*hi**k
            lower += min(x, y)
            upper += max(x, y)
        if lower > 0:
            return 1, n
        if upper < 0:
            return -1, n
    raise Refusal('SIGN_INTERVAL_BUDGET')

def analyze(left, right, t0):
    """Full replay receipt for analytic difference right-left at rational t0."""
    t0 = rat(t0)
    groups = formal_difference(left, right, t0)
    first = []
    for j, freqs in sorted(groups.items()):
        if not freqs:
            continue
        m = sum(f > 0 for f in freqs)
        bound = 2*m + (1 if F(0) in freqs else 0)
        check(bound > 0, 'IMPOSSIBLE_EMPTY_BASIS')
        for k in range(bound):
            c = moment(freqs, k)
            if c:
                first.append((j+k, j, k, c, bound))
                break
        else:
            raise Refusal('ANNIHILATOR_INVARIANT_FAILURE')
    head = {'schema': SCHEMA, 'left_sha256': fingerprint(left),
            'right_sha256': fingerprint(right), 'time': str(t0),
            'source_kind': 'EXPRESSION_ONLY_NOT_PHYSICAL_KNOT',
            'complete_event_partition': False, 'mc_b_established': False,
            'production_authorized': False}
    if not first:
        return {**head, 'status': 'ANALYTICALLY_IDENTICAL',
                'first_mismatch_order': None, 'left_sign': None,
                'right_sign': None, 'moment_terms': []}
    order = min(v[0] for v in first)
    lead = sorted([(k, c) for n, j, k, c, bound in first if n == order])
    sign, effort = sign_pi_poly(lead)
    return {**head, 'status': 'EXACT_LOCAL_DIFFERENCE',
            'first_mismatch_order': order,
            'continuous_derivatives_through': order - 1,
            'left_sign': -sign if order % 2 else sign,
            'right_sign': sign,
            'moment_terms': [[k, str(c)] for k, c in lead],
            'sign_interval_terms': effort,
            'max_active_frequency': str(max((f for x in groups.values() for f in x), default=F(0))),
            'local_annihilator_ceiling': max((j+2*sum(f>0 for f in fs)+(F(0) in fs)-1
                                             for j, fs in groups.items() if fs), default=0)}

def verify(left, right, t0, claimed):
    check(type(claimed) is dict and analyze(left, right, t0) == claimed,
          'FORGED_OR_STALE_RECEIPT')
    return True

def attempt(left, right, t0):
    try:
        return analyze(left, right, t0)
    except (Refusal, MemoryError, OverflowError, RecursionError) as exc:
        return {'schema': SCHEMA, 'status': 'RESOURCE_REFUSAL_OR_BLOCKED',
                'reason': str(exc), 'is_truth_value': False,
                'mc_b_established': False, 'production_authorized': False}
