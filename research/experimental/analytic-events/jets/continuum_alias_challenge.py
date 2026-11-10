#!/usr/bin/env python3
"""A2 research: sided continuum germ versus complete physical zero-set.

Standard-library exact Fraction oracle. Optional source-pinned A2 replay:
    python continuum_alias_challenge.py --a2-module path/to/cyclotomic_moments.py
Research only. No original-source, MC-B, native or STEP qualification.
"""
import argparse
import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from math import comb

A2_GIT_BLOB = '649b6dc6d5f74766ae285115dfd7600f2b6f6036'


def polynomial_to_bernstein(coeffs, degree):
    assert len(coeffs) <= degree + 1
    return tuple(sum(coeffs[k] * Q(comb(i, k), comb(degree, k))
                     for k in range(min(i, len(coeffs) - 1) + 1))
                 for i in range(degree + 1))


def bernstein_to_polynomial(controls):
    p = len(controls) - 1
    coefficients = [Q(0)] * (p + 1)
    for i, c in enumerate(controls):
        for j in range(p - i + 1):
            coefficients[i + j] += c * comb(p, i) * comb(p - i, j) * (-1) ** j
    return tuple(coefficients)


def source_fixture(p, q, lam):
    """F=0 on [0,1], F=u**q*(1-lam*u)*(1-sin(pi*t/2)) on [1,2]."""
    assert 1 <= q <= p <= 3 and (lam == 0 or q < p)
    poly = [Q(0)] * (p + 1)
    poly[q] = Q(1)
    if lam:
        poly[q + 1] = -Q(lam)
    right = polynomial_to_bernstein(poly, p)
    left = (Q(0),) * (p + 1)
    cp = left + right[1:]
    assert len(cp) == 2 * p + 1 and cp[p] == right[0] == 0
    knots = (Q(0),) * (p + 1) + (Q(1),) * p + (Q(2),) * (p + 1)
    controls = {0: (cp, (Q(0),) * len(cp)),
                1: ((Q(0),) * len(cp), tuple(-x for x in cp))}
    return p, knots, controls, Q(0), Q(1, 4)


def source_digest(fixture):
    p, knots, controls, offset, rate = fixture
    doc = {'degree': p, 'knots': [str(k) for k in knots],
           'phase': [str(offset), str(rate)],
           'controls': {str(h): [[str(v) for v in pair[0]],
                                  [str(v) for v in pair[1]]]
                        for h, pair in controls.items()}}
    return hashlib.sha256(json.dumps(doc, sort_keys=True,
                     separators=(',', ':')).encode('ascii')).hexdigest()


def check_fixture(p, q, lam):
    f = source_fixture(p, q, lam)
    cp = f[2][0][0]
    lhs = bernstein_to_polynomial(cp[:p + 1])
    rhs = bernstein_to_polynomial(cp[p:])
    expected = tuple(Q(1) if k == q else -Q(lam) if k == q + 1 else Q(0)
                     for k in range(p + 1))
    assert lhs == (Q(0),) * (p + 1)
    assert rhs == expected
    assert f[2][1][1] == tuple(-v for v in cp)
    assert all(rhs[k] == 0 for k in range(q)) and rhs[q] == 1
    # Analytic carrier at knot: 1-cos(pi*u/2) has exact order 2,
    # with positive leading coefficient pi^2/8. Hence right order q+2.
    zeros = ['[0,1]']
    if lam > 0 and Q(1, lam) <= 1:
        zeros.append(str(1 + Q(1, lam)))
    return {'p': p, 'q': q, 'lambda': str(lam),
            'left_status': 'IDENTITY_ZERO_ON_ANALYTIC_SPAN',
            'right_order': q + 2, 'right_sign': 1,
            'knot_status': 'CONTINUUM_ADJACENT_ZERO_KNOT',
            'isolated_knot_count': 0, 'zero_components': zeros,
            'source_sha256': source_digest(f)}


def formal_carrier_controls():
    # Exact coefficient of z^(2m) in (1-cos z)^m is 2^-m,
    # z=pi*(t-1)/2, for every integer m>=1.
    for m in range(1, 9):
        series = [Q(0)] * (2 * m + 1)
        series[0] = Q(1)
        carrier = [Q(0)] * (2 * m + 1)
        for k in range(1, m + 1):
            carrier[2*k] = Q((-1)**(k + 1), __import__('math').factorial(2*k))
        for _ in range(m):
            new = [Q(0)] * (2*m + 1)
            for i, a in enumerate(series):
                for j, b in enumerate(carrier[:2*m + 1 - i]):
                    new[i + j] += a*b
            series = new
        assert all(x == 0 for x in series[:2*m])
        assert series[2*m] == Q(1, 2**m)


def replay_a2(path):
    raw = open(path, 'rb').read()
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    assert blob == A2_GIT_BLOB, 'A2_SOURCE_BLOB_MISMATCH: ' + blob
    spec = importlib.util.spec_from_file_location('a2_pinned_moments', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    count = 0
    for p, q in ((2, 1), (3, 1), (3, 2)):
        for lam in (0, 2, 3, -1):
            f = source_fixture(p, q, lam)
            got = module.knot_germ(*f)
            assert got['status'] == 'CONTINUUM_ADJACENT_ZERO_KNOT'
            assert got['left']['status'] == 'IDENTITY_ZERO_ON_ANALYTIC_SPAN'
            assert got['right']['order'] == q + 2
            assert got['right']['right_sign'] == 1
            assert got['physical_zero_count'] == 0
            assert got['spline_sha256'] == source_digest(f)
            assert module.verify_knot_receipt(*f, got) is True
            flipped = module.reversed_spline(*f)
            rev = module.knot_germ(*flipped)
            assert rev['status'] == got['status']
            assert rev['right']['status'] == 'IDENTITY_ZERO_ON_ANALYTIC_SPAN'
            assert rev['left']['order'] == q + 2
            assert rev['left']['left_sign'] == 1
            assert module.verify_knot_receipt(*flipped, rev) is True
            count += 1
        base = source_fixture(p, q, 0)
        changed = source_fixture(p, q, 2)
        original = module.knot_germ(*base)
        assert original['right']['order'] == module.knot_germ(*changed)['right']['order']
        assert original['spline_sha256'] != module.knot_germ(*changed)['spline_sha256']
        assert module.attempt(module.verify_knot_receipt, *changed, original)['status'] == 'RESOURCE_REFUSAL_OR_BLOCKED'
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--a2-module', help='Exact source-pinned full A2 module replay')
    args = parser.parse_args()
    formal_carrier_controls()
    result = []
    for p, q in ((2, 1), (3, 1), (3, 2)):
        for lam in (0, 2, 3, -1):
            result.append(check_fixture(p, q, lam))
        base = next(x for x in result if x['p'] == p and x['q'] == q and x['lambda'] == '0')
        altered = next(x for x in result if x['p'] == p and x['q'] == q and x['lambda'] == '2')
        assert (base['left_status'], base['right_order'], base['right_sign']) == (altered['left_status'], altered['right_order'], altered['right_sign'])
        assert base['source_sha256'] != altered['source_sha256']
        assert base['zero_components'] != altered['zero_components']
    print(json.dumps({'oracle_case_count': len(result), 'carrier_series_controls': 8,
                      'extra_root_cases': sum(len(x['zero_components']) > 1 for x in result),
                      'source_binding_separations': 3,
                      'a2_exact_module_cases': replay_a2(args.a2_module) if args.a2_module else 'NOT_RUN',
                      'evidence_class': 'DETERMINISTIC_MODEL',
                      'gate': 'NOT_ESTABLISHED'}, sort_keys=True))


if __name__ == '__main__':
    main()
