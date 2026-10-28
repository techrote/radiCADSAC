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
import tempfile

HERE = Path(__file__).resolve().parent
V7 = HERE / 'pb00701_coupled_bspline_model.py'
PINNED_SOURCE_BLOBS = {
    'pb00701_coupled_bspline_model.py': 'a086b625e1a6dea8bd202699d161167bb69cc9e7',
    'pb00701_rational_turn_model.py': 'a1316ff0f71b2d7aa80807843a74fd8280779cb2',
    'pb00701_event_model.py': '104c0e7a459cd7da5025853b246faff244a5948e',
    '../MC-032/event_engine.py': '789a709c5141479a343035d1b7055dd4e53534e1',
}
SCHEMA = 'radicadsac-pb00701-affine-identity-research/1.0'
MAX_STATIONARY_CYCLOTOMIC_ORDER = 256


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def verify_pinned_sources(*, root=HERE):
    """Fail closed on any historical source/transitive rational-parser drift."""
    for relative, expected in PINNED_SOURCE_BLOBS.items():
        if git_blob((root / relative).read_bytes()) != expected:
            raise ValueError(f'historical source dependency blob mismatch: {relative}')
    return True


def original_lowerer():
    verify_pinned_sources()
    sys.path.insert(0, str(HERE))
    import pb00701_coupled_bspline_model as v7
    # Reject a preloaded same-named module from a different source path.
    modules = (
        (v7, 'pb00701_coupled_bspline_model.py'),
        (v7.v6, 'pb00701_rational_turn_model.py'),
        (v7.v6.base, 'pb00701_event_model.py'),
        (v7.v6.base.EE, '../MC-032/event_engine.py'),
    )
    for module, relative in modules:
        if Path(module.__file__).resolve() != (HERE / relative).resolve():
            raise ValueError(f'historical source dependency import mismatch: {relative}')
    verify_pinned_sources()
    return v7


def q_exact(raw):
    if isinstance(raw, bool) or not isinstance(raw, (str, int, Q)):
        raise ValueError('only exact rational scalars admitted')
    return Q(raw)



def hash_exact_source_record(spec):
    """Hash raw exact source forms without silently aliasing typed Python values.

    JSON-only records retain their original canonical JSON hash. In-process
    Fraction scalars and non-string harmonic keys require explicit type tags.
    Preserve typed-mapping insertion order: legacy V7 accepts both integer
    and string harmonic keys, and duplicate-alias precedence matters.
    This is input-record identity, not independent source-codec equivalence.
    """
    def encode(value):
        if isinstance(value, Q):
            return {'__radicadsac_fraction__': [str(value.numerator), str(value.denominator)]}
        if isinstance(value, list):
            return [encode(part) for part in value]
        if isinstance(value, dict):
            if all(isinstance(key, str) for key in value):
                return {key: encode(part) for key, part in value.items()}
            return {'__radicadsac_typed_mapping__': [
                [type(key).__name__, str(key), encode(part)]
                for key, part in value.items()
            ]}
        return value

    packed = json.dumps(encode(spec), sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(packed.encode()).hexdigest()


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


def independent_de_boor(raw_spline, u):
    """Test-only exact de Boor value; no V7 normalization/basis/codec helpers.

    This samples a source spline in its original u coordinate, independently
    of the proposed local power-basis identity implementation. It is a finite
    falsifier, not a general source-codec refinement proof.
    """
    degree = raw_spline['degree']
    knots = [Q(value) for value in raw_spline['knots']]
    controls = [Q(value) for value in raw_spline['controls']]
    u = Q(u)
    span = next((k for k in range(degree, len(controls))
                 if knots[k] <= u < knots[k + 1]), None)
    if span is None:
        raise AssertionError('independent de Boor sample outside source support')
    work = [controls[span - degree + j] for j in range(degree + 1)]
    for level in range(1, degree + 1):
        for j in range(degree, level - 1, -1):
            i = span - degree + j
            denominator = knots[i + degree - level + 1] - knots[i]
            if denominator <= 0:
                raise AssertionError('invalid de Boor interior denominator')
            weight = (u - knots[i]) / denominator
            work[j] = (1 - weight) * work[j - 1] + weight * work[j]
    return work[degree]


def independent_power_value(coefficients, local_s):
    """Test-only direct power sum, independent of V7 polynomial evaluation."""
    return sum((Q(c) * local_s**i for i, c in enumerate(coefficients)), Q(0))


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
        source_digest = hash_exact_source_record(spec)
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
    except (MemoryError, OverflowError, RecursionError) as exc:
        return {'status': 'RESOURCE_REFUSAL', 'reason': 'AFFINE_IDENTITY_RESOURCE_EXHAUSTED',
                'exception_type': type(exc).__name__, 'is_truth_value': False}
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
        return {'status': 'SEMANTIC_BLOCKER', 'reason': 'INVALID_EXACT_ORIGINAL_SOURCE', 'detail': str(exc)}
    if any(p['identity_status'] == 'RESOURCE_REFUSAL' for p in pieces):
        status = 'RESOURCE_REFUSAL'
    else:
        status = 'IDENTITY_ZERO_ON_ALL_OPEN_SPANS' if all(p['identity_status'] == 'IDENTITY_ZERO' for p in pieces) else 'NOT_IDENTITY_ON_SOME_OPEN_SPAN'
    result = {'schema': SCHEMA, 'status': status, 'source_sha256': source_digest,
              'source_parameter_id': source_id, 'spans': pieces,
              'scope': 'ANALYTIC_IDENTITY_ONLY_NO_ORDERED_ROOT_OR_PHYSICAL_KNOT_CONSTRUCTION',
              'event_root_count_claimed': False, 'mc_b_or_native_claimed': False}
    if status == 'RESOURCE_REFUSAL':
        result['is_truth_value'] = False
    return result


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
    # At 1/12 turn, sin(theta) == cos(2*theta) == 1/2 exactly.
    # Moving the same source destroys the stationary cross-harmonic identity.
    expect(fixture(cos={'2': spline(-1)}, sin={'1': one},
                   offset='1/12', rate='0'), 'IDENTITY_ZERO_ON_ALL_OPEN_SPANS')
    expect(fixture(cos={'2': spline(-1)}, sin={'1': one},
                   offset='1/12', rate='1/7'), 'NOT_IDENTITY_ON_SOME_OPEN_SPAN')
    # Exact affine reparametrization under a negative global phase slope.
    reversed_phase = expect(fixture(cos={'1': spline(1, 2, knots=[2, 2, 4, 4])},
                                    lo='2', hi='4', offset='1/6', rate='-1/3'),
                            'NOT_IDENTITY_ON_SOME_OPEN_SPAN')
    assert reversed_phase['spans'][0]['phase_turn_offset'] == '-1/2'
    assert reversed_phase['spans'][0]['phase_turn_rate'] == '-2/3'
    expect(fixture(cos={'1': zero}, offset='1/12', rate='-5/7'),
           'IDENTITY_ZERO_ON_ALL_OPEN_SPANS')
    cap = expect(fixture(cos={'0': one}, offset='1/257', rate='0'), 'RESOURCE_REFUSAL')
    assert cap['is_truth_value'] is False
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
    # V7's original parser admits Fraction-valued in-process exact source
    # records; standard JSON hashing must not misclassify them as invalid.
    fraction_source = fixture(cos={'1': spline('1/2')}, offset=Q(1, 8), rate=Q(0))
    fraction_source['cos_splines']['1']['controls'][0] = Q(1, 2)
    fraction_result = expect(fraction_source, 'NOT_IDENTITY_ON_SOME_OPEN_SPAN')
    string_result = expect(fixture(cos={'1': spline('1/2')}, offset='1/8', rate='0'),
                           'NOT_IDENTITY_ON_SOME_OPEN_SPAN')
    assert fraction_result['source_sha256'] != string_result['source_sha256']
    # Numeric and string harmonic keys are separately admitted by V7.
    mixed_source = expect(fixture(cos={0: one, '1': one},
                                  offset='1/4', rate='0'),
                          'NOT_IDENTITY_ON_SOME_OPEN_SPAN')
    string_source = expect(fixture(cos={'0': one, '1': one},
                                   offset='1/4', rate='0'),
                           'NOT_IDENTITY_ON_SOME_OPEN_SPAN')
    assert mixed_source['source_sha256'] != string_source['source_sha256']
    # V7 resolves same-number int/string aliases by last assignment. Preserve
    # raw input identity and insertion order; do not fabricate codec equivalence.
    alias_forward = expect(fixture(cos={1: zero, '1': one}),
                           'NOT_IDENTITY_ON_SOME_OPEN_SPAN')
    alias_reverse = expect(fixture(cos={'1': one, 1: zero}),
                           'IDENTITY_ZERO_ON_ALL_OPEN_SPANS')
    assert alias_forward['source_sha256'] != alias_reverse['source_sha256']
    print('PASS: Fraction input, mixed harmonic keys and alias-order provenance falsifiers')
    # A prime-5 rational stationary phase has a nonquadratic field relation:
    # 1 + 2*cos(2*pi/5) + 2*cos(4*pi/5) == 0. This is NOT a
    # componentwise-zero expression; the same polynomials with moving phase
    # are linearly independent exponential polynomials.
    fifth = fixture(cos={'0': spline(1), '1': spline(2), '2': spline(2)},
                    offset='1/5', rate='0')
    fifth_result = expect(fifth, 'IDENTITY_ZERO_ON_ALL_OPEN_SPANS')
    assert fifth_result['spans'][0]['cyclotomic_order'] == 20
    expect(dict(fifth, phase_turn_rate='1/9'), 'NOT_IDENTITY_ON_SOME_OPEN_SPAN')
    # For prime 7, the sum of all six nontrivial seventh roots is -1,
    # giving 1 + 2*sum_{h=1..3} cos(2*pi*h/7) == 0.
    seventh = fixture(cos={'0': spline(1), '1': spline(2), '2': spline(2),
                           '3': spline(2)}, offset='1/7', rate='0')
    seventh_result = expect(seventh, 'IDENTITY_ZERO_ON_ALL_OPEN_SPANS')
    assert seventh_result['spans'][0]['cyclotomic_order'] == 28
    # Stationary phase aliases harmonics separated by five, but this alias
    # is not a moving-phase identity. Preserve both original owner channels.
    harmonic_alias = fixture(cos={'1': spline(1, 2), '6': spline(-1, -2)},
                             offset='1/5', rate='0')
    expect(harmonic_alias, 'IDENTITY_ZERO_ON_ALL_OPEN_SPANS')
    expect(dict(harmonic_alias, phase_turn_rate='1/9'),
           'NOT_IDENTITY_ON_SOME_OPEN_SPAN')
    # Distinct degree/knot encodings describe the same affine amplitude
    # 1+u versus -(1+u), so cos(pi/4)==sin(pi/4) cancels across both
    # original knot-free spans. No knot may disappear through lowering.
    affine_cancel = fixture(
        cos={'1': spline(1, 2, 3, degree=2, knots=[0, 0, 0, 2, 2, 2])},
        sin={'1': spline(-1, -2, -3, degree=1, knots=[0, 0, 1, 2, 2])},
        lo='0', hi='2', offset='1/8', rate='0')
    cancelled = expect(affine_cancel, 'IDENTITY_ZERO_ON_ALL_OPEN_SPANS')
    assert [p['source_interval'] for p in cancelled['spans']] == [
        ['0', '1'], ['1', '2']]
    expect(dict(affine_cancel, phase_turn_rate='1/8'),
           'NOT_IDENTITY_ON_SOME_OPEN_SPAN')
    perturbed = fixture(
        cos=affine_cancel['cos_splines'],
        sin={'1': spline(-1, '-7/3', -3, degree=1,
                         knots=[0, 0, 1, 2, 2])},
        lo='0', hi='2', offset='1/8', rate='0')
    expect(perturbed, 'NOT_IDENTITY_ON_SOME_OPEN_SPAN')
    # A nonidentical analytic expression can still have an isolated
    # interior root: cos(pi*u) vanishes at u=1/2.
    rooted_nonidentity = expect(
        fixture(cos={'1': one}, offset='0', rate='1/2'),
        'NOT_IDENTITY_ON_SOME_OPEN_SPAN')
    assert rooted_nonidentity['event_root_count_claimed'] is False
    # A cap exactly below an admissible stationary cyclotomic order is
    # typed nontruth refusal, not proof of zero or nonzero.
    seventh_cap = expect(seventh, 'RESOURCE_REFUSAL', max_order=27)
    assert seventh_cap['is_truth_value'] is False
    print('PASS: prime-5/7 cyclotomic identities, harmonic alias, mixed-degree source cancellation, nonidentity root and typed cap falsifiers')
    # Known cyclotomic minimal polynomials independently checked against definitions.
    assert cyclotomic(4) == [1, 0, 1]
    assert cyclotomic(6) == [1, -1, 1]
    assert cyclotomic(8) == [1, 0, 0, 0, 1]
    assert cyclotomic(12) == [1, 0, -1, 0, 1]
    # Independent source-space oracle: nonconstant degree 3/2/1 controls,
    # nonuniform knots, a repeated interior knot, and merged channel cuts.
    # The reference evaluates raw source control points by exact de Boor,
    # never calling V7's basis/lowering/polynomial-evaluation helpers.
    source_probe = fixture(
        cos={'0': spline(2, -1, 3, 1, 4, degree=3,
                         knots=[0, 0, 0, 0, 1, 2, 2, 2, 2]),
             '1': spline(1, 2, -3, 2, degree=2,
                         knots=[0, 0, 0, 1, 2, 2, 2])},
        sin={'2': spline(3, -2, 5, 1, degree=1,
                         knots=[0, 0, '1/2', '1/2', 2, 2])},
        lo='0', hi='2', offset='1/7', rate='-2/9')
    probe_report = expect(source_probe, 'NOT_IDENTITY_ON_SOME_OPEN_SPAN')
    assert [p['source_interval'] for p in probe_report['spans']] == [
        ['0', '1/2'], ['1/2', '1'], ['1', '2']]
    exact_samples = 0
    affine_checks = 0
    for piece in probe_report['spans']:
        left, right = map(Q, piece['source_interval'])
        assert Q(piece['phase_turn_offset']) == Q('1/7') - Q('2/9') * left
        assert Q(piece['phase_turn_rate']) == -Q('2/9') * (right - left)
        affine_checks += 1
        for channel in ('cos_splines', 'sin_splines'):
            for harmonic, raw_spline in source_probe[channel].items():
                normal = v7._normalise_bspline(raw_spline)
                coefficients = v7._piece_from_normal(normal, left, right)['coefficients']
                for local_s in (Q(1, 7), Q(1, 2), Q(5, 6)):
                    global_u = left + (right - left) * local_s
                    observed = independent_power_value(coefficients, local_s)
                    oracle = independent_de_boor(raw_spline, global_u)
                    assert observed == oracle, (
                        channel, harmonic, left, right, local_s, observed, oracle)
                    exact_samples += 1
    assert exact_samples == 27 and affine_checks == 3
    raw = source_probe['cos_splines']['0']
    normal = v7._normalise_bspline(raw)
    corrupted = list(v7._piece_from_normal(normal, Q(0), Q('1/2'))['coefficients'])
    corrupted[0] += Q(1, 17)
    assert independent_power_value(corrupted, Q(1, 7)) != independent_de_boor(raw, Q(1, 14))
    print('PASS: 27 independent rational de Boor samples, 3 affine maps, and a coefficient-corruption falsifier')
    # Isolated scratch-copy mutation controls: historical source remains immutable.
    with tempfile.TemporaryDirectory(prefix='pb00701-affine-pin-') as scratch:
        copied_root = Path(scratch) / 'MC-038'
        for relative in PINNED_SOURCE_BLOBS:
            target = copied_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((HERE / relative).read_bytes())
        assert verify_pinned_sources(root=copied_root)
        for relative in PINNED_SOURCE_BLOBS:
            target = copied_root / relative
            pristine = target.read_bytes()
            target.write_bytes(pristine + b'\n# adversarial dependency drift\n')
            try:
                verify_pinned_sources(root=copied_root)
            except ValueError as exc:
                assert 'blob mismatch' in str(exc), (relative, str(exc))
            else:
                raise AssertionError(f'dependency drift not refused: {relative}')
            target.write_bytes(pristine)
        assert verify_pinned_sources(root=copied_root)
    # Simulate arithmetic limits without substituting refusal for mathematical truth.
    class ExhaustingLowerer:
        def __init__(self, error):
            self.error = error
        def _normalise_harmonic_splines(self, *_):
            raise self.error('synthetic computation limit')
    for error in (MemoryError, OverflowError, RecursionError):
        refused = inspect_original_source(fixture(cos={'0': one}), lowerer=ExhaustingLowerer(error))
        assert refused['status'] == 'RESOURCE_REFUSAL', refused
        assert refused['exception_type'] == error.__name__
        assert refused['is_truth_value'] is False
    print('PASS: 36 original-source status controls + 4 cyclotomic + 3 synthetic exhaustion + 4 dependency-drift controls')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contract', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.contract:
        original_lowerer()
        print('PASS: pinned four-module original-source/parser chain; no route selection invoked')
    if args.self_test:
        self_test()
    if not args.contract and not args.self_test:
        parser.error('choose --contract and/or --self-test')


if __name__ == '__main__':
    main()
