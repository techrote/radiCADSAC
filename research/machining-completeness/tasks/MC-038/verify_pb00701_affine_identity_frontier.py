#!/usr/bin/env python3
"""MC-038: narrowly scoped exact analytic-identity experiment, not a root solver.

Reads only the original V7 source-lowering primitives; neither historical route
selection nor a finite-owner certificate is invoked or changed. The bounded
stationary cyclotomic arithmetic refuses rather than guessing on resource caps.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction as Q
from math import gcd
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
V7 = HERE / 'pb00701_coupled_bspline_model.py'
V7_BLOB = 'a086b625e1a6dea8bd202699d161167bb69cc9e7'
SCHEMA = 'radicadsac-pb00701-affine-identity-research/1.0'
MAX_STATIONARY_CYCLOTOMIC_ORDER = 256


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def original_lowerer():
    if git_blob(V7.read_bytes()) != V7_BLOB:
        raise ValueError('historical V7 original-source lowering drifted')
    sys.path.insert(0, str(HERE))
    import pb00701_coupled_bspline_model as v7
    return v7


def q_exact(raw):
    if isinstance(raw, bool) or not isinstance(raw, (str, int, Q)):
        raise ValueError('only exact rational scalars admitted')
    return Q(raw)


def trimmed(poly):
    result = list(poly)
    while len(result) > 1 and not result[-1]:
        result.pop()
    return result or [Q(0)]


def divisors(n):
    return [k for k in range(1, n + 1) if n % k == 0]


def poly_exact_div(numerator, monic):
    """Integer monic division; all remainders must be exactly zero."""
    p = list(numerator)
    deg = len(monic) - 1
    out = [0] * max(1, len(p) - deg)
    for k in range(len(p) - 1, deg - 1, -1):
        factor = p[k]
        out[k - deg] = factor
        if factor:
            for j, value in enumerate(monic):
                p[k - deg + j] -= factor * value
    if any(p[:deg]):
        raise AssertionError('cyclotomic integer division remainder nonzero')
    return out


def cyclotomic(n):
    if n < 1:
        raise ValueError('cyclotomic order must be positive')
    known = {}
    for d in divisors(n):
        poly = [-1] + [0] * (d - 1) + [1]
        for lower in divisors(d):
            if lower < d:
                poly = poly_exact_div(poly, known[lower])
        known[d] = poly
    return known[n]


def pow_zeta(k, phi, order):
    """Reduce a power of primitive zeta_N in Q[X]/Phi_N."""
    k %= order
    poly = [0] * (k + 1)
    poly[k] = 1
    deg = len(phi) - 1
    for at in range(len(poly) - 1, deg - 1, -1):
        factor = poly[at]
        if factor:
            for j, coeff in enumerate(phi):
                poly[at - deg + j] -= factor * coeff
    return [Q(v) for v in (poly[:deg] + [0] * deg)[:deg]]


def stationary_identity(cos_polys, sin_polys, offset, max_order):
    """Compare rational power coefficients exactly in the cyclotomic field."""
    n = offset.denominator * 4 // gcd(offset.denominator, 4)
    if n > max_order:
        return None, n
    phi = cyclotomic(n)
    degree = len(phi) - 1
    max_degree = max(len(p) for p in list(cos_polys.values()) + list(sin_polys.values()))
    accum = [[Q(0) for _ in range(degree)] for _ in range(max_degree)]
    cache = {}

    def z(k):
        key = k % n
        if key not in cache:
            cache[key] = pow_zeta(key, phi, n)
        return cache[key]

    for mapping, channel in ((cos_polys, 'cos'), (sin_polys, 'sin')):
        for h, poly in mapping.items():
            k = h * offset.numerator * (n // offset.denominator)
            if channel == 'cos':
                left, right, right_sign = z(k), z(-k), 1
            else:
                # 1/i = -i; i=zeta_N^(N/4), N multiple of 4.
                left, right, right_sign = z(k + n // 4), z(-k + n // 4), -1
            direction = 1 if channel == 'cos' else -1
            basis = [Q(direction, 2) * (a + right_sign * b)
                     for a, b in zip(left, right)]
            for j, coefficient in enumerate(poly):
                for col, unit in enumerate(basis):
                    accum[j][col] += coefficient * unit
    return not any(any(v for v in row) for row in accum), n


def span_identity(cos_polys, sin_polys, alpha, beta, max_order):
    if beta:
        # Independence of {s^j exp(2*pi*i*k*beta*s)} for distinct integer k.
        # Fixed phase alpha only rotates each (+h,-h) coefficient pair.
        return not any(any(poly) for poly in list(cos_polys.values()) +
                       list(sin_polys.values())), None
    return stationary_identity(cos_polys, sin_polys, alpha, max_order)


def inspect_original_source(spec, *, max_order=MAX_STATIONARY_CYCLOTOMIC_ORDER, lowerer=None):
    if lowerer is None:
        lowerer = original_lowerer()
    allowed = {'grammar', 'cos_splines', 'sin_splines', 'parameter_lo', 'parameter_hi',
               'phase_turn_offset', 'phase_turn_rate', 'source_parameter_id', 'parameter_projection'}
    if not isinstance(spec, dict) or set(spec) - allowed or spec.get('grammar') != 'RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE':
        return {'status': 'SEMANTIC_BLOCKER', 'reason': 'NOT_ADMITTED_ORIGINAL_SOURCE_GRAMMAR'}
    source_id = spec.get('source_parameter_id')
    if not isinstance(source_id, str) or not source_id or spec.get('parameter_projection') not in (None, source_id):
        return {'status': 'SEMANTIC_BLOCKER', 'reason': 'INVALID_SHARED_SOURCE_PARAMETER'}
    try:
        lo, hi = q_exact(spec['parameter_lo']), q_exact(spec['parameter_hi'])
        offset, rate = q_exact(spec['phase_turn_offset']), q_exact(spec['phase_turn_rate'])
        if lo >= hi or max_order < 4:
            raise ValueError('invalid interval or phase order limit')
        cos_norm = lowerer._normalise_harmonic_splines(spec.get('cos_splines'), 'cos_splines')
        sin_norm = lowerer._normalise_harmonic_splines(spec.get('sin_splines'), 'sin_splines')
        if not cos_norm and not sin_norm:
            raise ValueError('empty original expression')
        boundaries = lowerer._master_boundaries(list(cos_norm.values()) + list(sin_norm.values()), lo, hi)
        source_digest = hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        pieces = []
        for left, right in zip(boundaries, boundaries[1:]):
            cos_poly = {h: trimmed(lowerer._piece_from_normal(normal, left, right)['coefficients']) for h, normal in cos_norm.items()}
            sin_poly = {h: trimmed(lowerer._piece_from_normal(normal, left, right)['coefficients']) for h, normal in sin_norm.items()}
            identical, order = span_identity(cos_poly, sin_poly, offset + rate * left, rate * (right - left), max_order)
            pieces.append({'source_interval': [str(left), str(right)],
                           'local_coordinate': 's=(u-left)/(right-left)',
                           'phase_turn_offset': str(offset + rate * left),
                           'phase_turn_rate': str(rate * (right - left)),
                           'identity_status': 'RESOURCE_REFUSAL' if identical is None else 'IDENTITY_ZERO' if identical else 'NOT_IDENTITY',
                           'cyclotomic_order': order})
    except (KeyError, TypeError, ValueError, ZeroDivisionError, OverflowError) as exc:
        return {'status': 'SEMANTIC_BLOCKER', 'reason': 'INVALID_EXACT_ORIGINAL_SOURCE', 'detail': str(exc)}
    if any(p['identity_status'] == 'RESOURCE_REFUSAL' for p in pieces):
        status = 'RESOURCE_REFUSAL'
    else:
        status = 'IDENTITY_ZERO_ON_ALL_OPEN_SPANS' if all(p['identity_status'] == 'IDENTITY_ZERO' for p in pieces) else 'NOT_IDENTITY_ON_SOME_OPEN_SPAN'
    return {'schema': SCHEMA, 'status': status, 'source_sha256': source_digest,
            'source_parameter_id': source_id, 'spans': pieces,
            'scope': 'ANALYTIC_IDENTITY_ONLY_NO_ORDERED_ROOT_OR_PHYSICAL_KNOT_CONSTRUCTION',
            'event_root_count_claimed': False, 'mc_b_or_native_claimed': False}


def spline(*controls, degree=None, knots=None):
    if degree is None:
        degree = len(controls) - 1
    if knots is None:
        knots = [0] * (degree + 1) + [1] * (degree + 1)
    return {'degree': degree, 'knots': [str(k) for k in knots],
            'controls': [str(v) for v in controls]}


def fixture(*, cos=None, sin=None, offset='0', rate='1/4', lo='0', hi='1'):
    return {'grammar': 'RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE',
            'cos_splines': cos or {}, 'sin_splines': sin or {},
            'parameter_lo': lo, 'parameter_hi': hi,
            'phase_turn_offset': offset, 'phase_turn_rate': rate,
            'source_parameter_id': 'proof-fixture-u'}


def self_test():
    v7 = original_lowerer()
    def expect(spec, expected, *, max_order=256):
        observed = inspect_original_source(spec, max_order=max_order, lowerer=v7)
        assert observed['status'] == expected, (expected, observed)
        if observed['status'] not in ('RESOURCE_REFUSAL', 'SEMANTIC_BLOCKER'):
            assert not observed['event_root_count_claimed']
            assert not observed['mc_b_or_native_claimed']
        return observed

    zero = spline(0, 0)
    one = spline(1)
    linear = spline(1, 2)
    neg_linear = spline(-1, -2)
    expect(fixture(cos={'1': zero}), 'IDENTITY_ZERO_ON_ALL_OPEN_SPANS')
    expect(fixture(cos={'1': linear}), 'NOT_IDENTITY_ON_SOME_OPEN_SPAN')
    expect(fixture(cos={'0': zero, '1': zero}), 'IDENTITY_ZERO_ON_ALL_OPEN_SPANS')
    expect(fixture(cos={'1': one}, offset='1/4', rate='0'), 'IDENTITY_ZERO_ON_ALL_OPEN_SPANS')
    expect(fixture(cos={'1': linear}, sin={'1': neg_linear}, offset='1/8', rate='0'), 'IDENTITY_ZERO_ON_ALL_OPEN_SPANS')
    expect(fixture(cos={'1': one, '2': spline(-1)}, offset='1/3', rate='0'), 'IDENTITY_ZERO_ON_ALL_OPEN_SPANS')
    expect(fixture(cos={'1': one}, offset='1/6', rate='0'), 'NOT_IDENTITY_ON_SOME_OPEN_SPAN')
    expect(fixture(sin={'1': one}, offset='1/4', rate='0'), 'NOT_IDENTITY_ON_SOME_OPEN_SPAN')
    expect(fixture(sin={'1': one}, offset='1/2', rate='0'), 'IDENTITY_ZERO_ON_ALL_OPEN_SPANS')
    expect(fixture(cos={'0': one}, offset='1/257', rate='0'), 'RESOURCE_REFUSAL')
    expect(fixture(cos={'0': one}, offset='1/257', rate='1/9'), 'NOT_IDENTITY_ON_SOME_OPEN_SPAN')
    discontinuous = fixture(cos={'0': spline(0, 1, degree=0, knots=[0, 1, 2])}, lo='0', hi='2', rate='0')
    result = expect(discontinuous, 'NOT_IDENTITY_ON_SOME_OPEN_SPAN')
    assert [p['identity_status'] for p in result['spans']] == ['IDENTITY_ZERO', 'NOT_IDENTITY']
    altered = dict(discontinuous, parameter_projection='unrelated-u')
    expect(altered, 'SEMANTIC_BLOCKER')
    altered = dict(discontinuous, unreviewed_authority=True)
    expect(altered, 'SEMANTIC_BLOCKER')
    altered = dict(discontinuous, phase_turn_rate=0.25)
    expect(altered, 'SEMANTIC_BLOCKER')
    altered = fixture(cos={'0': one}, sin={'0': one})
    expect(altered, 'SEMANTIC_BLOCKER')
    # Known cyclotomic minimal polynomials independently checked against definitions.
    assert cyclotomic(4) == [1, 0, 1]
    assert cyclotomic(6) == [1, -1, 1]
    assert cyclotomic(8) == [1, 0, 0, 0, 1]
    assert cyclotomic(12) == [1, 0, -1, 0, 1]
    print('PASS: 16 exact original-source statuses + 4 cyclotomic polynomial controls')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contract', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.contract:
        original_lowerer()
        print('PASS: pinned exact V7 original-source lowerer; no route selection invoked')
    if args.self_test:
        self_test()
    if not args.contract and not args.self_test:
        parser.error('choose --contract and/or --self-test')


if __name__ == '__main__':
    main()
