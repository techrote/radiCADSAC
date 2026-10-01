#!/usr/bin/env python3
"""V47 rational Sturm polynomials at exact Q(alpha) interval boundaries.

The polynomial stays in the lowered parent coordinate. Field evaluation is
Horner evaluation at the selected boundary, NOT reduction at alpha unless that
boundary actually is alpha. Zero sequence members use exact one-sided jets.
"""
from fractions import Fraction as Q
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_algebraic_child_map_model as a

q, require, engine = a.q, a.require, a.engine


def same(x, y):
    return a._json(x) == a._json(y)


def evaluate(poly, point):
    out = point.field.element(0)
    for c in reversed(a.trim(poly)):
        out = out * point + c
    return out


def side_jet(poly, point, side):
    require(side in ('left', 'right'), 'invalid one-sided direction')
    p, order = a.trim(poly), 0
    while p != [0]:
        value = evaluate(p, point)
        sign = value.sign()
        if sign:
            return {'order': order, 'value': value.record(),
                    'sign': -sign if side == 'left' and order % 2 else sign}
        order += 1
        p = engine.deriv(p)
    return {'order': None, 'value': ['0'], 'sign': 0}


def _variations(signs):
    nonzero = [s for s in signs if s]
    return sum(x != y for x, y in zip(nonzero, nonzero[1:]))


def polynomial_certificate(poly, left, right):
    require(left.field == right.field, 'mixed real embeddings')
    require((right - left).sign() == 1, 'nonpositive algebraic interval width')
    p = a.trim(poly)
    header = {'polynomial': [str(c) for c in p], 'field': left.field.record(),
              'interval': [left.record(), right.record()]}
    if p == [0]:
        return {**header, 'identity_zero': True, 'distinct_roots_open': None,
                'strict_positive': False, 'weak_sign': 0}
    sequence = engine.sturm_sequence(p)
    lsigns = [side_jet(s, left, 'right') for s in sequence]
    rsigns = [side_jet(s, right, 'left') for s in sequence]
    lv = _variations([x['sign'] for x in lsigns])
    rv = _variations([x['sign'] for x in rsigns])
    count = lv - rv
    require(0 <= count <= engine.degree(p), 'invalid exact Sturm count')
    le, re = evaluate(p, left).sign(), evaluate(p, right).sign()
    lj, rj = side_jet(p, left, 'right'), side_jet(p, right, 'left')
    # No interior roots plus continuity fixes one sign throughout the open
    # interval. Endpoint zeros are permitted only by the weak predicate.
    weak = lj['sign'] if count == 0 and lj['sign'] == rj['sign'] else None
    require(weak is None or (le in (0, weak) and re in (0, weak)), 'endpoint/sign inconsistency')
    return {**header, 'identity_zero': False,
            'sturm_sequence': [[str(c) for c in s] for s in sequence],
            'left_inward_jets': lsigns, 'right_inward_jets': rsigns,
            'variations': [lv, rv], 'distinct_roots_open': count,
            'endpoint_signs': [le, re],
            'endpoint_multiplicities': [lj['order'], rj['order']],
            'strict_positive': le == re == 1 and count == 0,
            'weak_sign': weak}


def validate_polynomial_certificate(candidate, poly, left, right):
    # Finite Sturm/jet regeneration. No search for a cut or a monotone route.
    expected = polynomial_certificate(poly, left, right)
    require(same(candidate, expected), 'algebraic interval polynomial proof mismatch')
    return True


def phase_cell(left, right, offset, rate, harmonic):
    """Lift the preserved diagonal cell to a single algebraic bisection.

At least one boundary is rational. It uniquely selects the possible cell;
all containment comparisons are performed in the selected real field.
    """
    require(left.field == right.field and (right - left).sign() == 1, 'invalid phase interval')
    require(type(harmonic) is int and harmonic > 0, 'invalid harmonic')
    offset, rate = q(offset), q(rate)
    require(rate != 0, 'zero phase belongs to predecessor')
    field = left.field
    t0, t1 = (field.element(offset) + x * rate for x in (left, right))
    t0, t1 = t0 * harmonic, t1 * harmonic
    lo, hi = (t0, t1) if rate > 0 else (t1, t0)
    rational = next((x.coefficients[0] for x in (t0, t1) if len(x.coefficients) == 1), None)
    require(rational is not None, 'multi-generator or two-algebraic-boundary cell not owned by v47')
    value = 2 * (rational + Q(3, 16))
    k = value.numerator // value.denominator
    lower, upper = Q(-3, 16) + Q(k, 2), Q(-1, 16) + Q(k, 2)
    signs = [(lo - lower).sign(), (field.element(upper) - hi).sign()]
    return {'status': 'CERTIFIED' if min(signs) >= 0 else 'BLOCKED',
            'reason': 'EXACT_DIAGONAL_PHASE_CONTAINMENT',
            'harmonic': harmonic, 'cell_index': k,
            'bounds': [str(lower), str(upper)],
            'harmonic_phase_endpoints': [t0.record(), t1.record()],
            'closed_containment_signs': signs,
            'diagonal_sign': -1 if k % 2 else 1,
            'field': field.record(), 'interval': [left.record(), right.record()],
            'parent_phase_rate': str(rate)}
