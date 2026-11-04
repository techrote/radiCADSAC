#!/usr/bin/env python3
"""Exact original-source finite-jet blindness construction (research; no gate).

For arbitrary m>=1 and rational 0<epsilon<1/2, an original, fully clamped
2-span rational B-spline amplitude produces an extra pair of arbitrarily
close interior simple zeros, while preserving all endpoint and knot jets of
orders <m. Truth follows from exact Bernstein identities and monotonicity,
not from the runtime m/bit budget or numeric root sampling.
"""
from __future__ import annotations

from fractions import Fraction as Q
from hashlib import sha256
from math import comb
import json

SCHEMA = 'radicadsac-pb00701-finite-jet-blindspot/1.0'
MAX_M = 20
MAX_BITS = 256
PHASE_TURN_RATE = Q(1, 16)


class Refusal(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False)


def source_sha(value):
    return sha256(canonical(value).encode('ascii')).hexdigest()


def rational(value):
    if isinstance(value, (bool, float)):
        raise Refusal('BINARY_OR_BOOLEAN_RATIONAL_REFUSED')
    try:
        out = Q(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise Refusal('NONCANONICAL_RATIONAL') from exc
    if isinstance(value, str) and str(out) != value:
        raise Refusal('NONCANONICAL_RATIONAL')
    return out


def admit(m, epsilon):
    if isinstance(m, bool) or not isinstance(m, int) or m < 1:
        raise Refusal('INVALID_JET_ORDER')
    if m > MAX_M:
        raise Refusal('RESOURCE_REFUSAL_M_LIMIT')
    e = rational(epsilon)
    if e.numerator.bit_length() > MAX_BITS or e.denominator.bit_length() > MAX_BITS:
        raise Refusal('RESOURCE_REFUSAL_RATIONAL_BITS')
    if not Q(0) < e < Q(1, 2):
        raise Refusal('INVALID_ROOT_SEPARATION')
    return e


def construction(m, epsilon, *, adversarial=True):
    e = admit(m, epsilon)
    d = 2 * m
    a = Q(1, 2) - e
    ea = (a * (1 - a)) ** m
    controls = [Q(1)] * (2 * d + 1)
    if adversarial:
        controls[m] = 1 - 1 / (Q(comb(d, m)) * ea)
    return {
        'grammar': 'RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE',
        'source_parameter_id': 'source-time-t',
        'parameter_lo': '0', 'parameter_hi': '2',
        'phase_turn_offset': '0', 'phase_turn_rate': str(PHASE_TURN_RATE),
        'cos_splines': {
            '1': {'degree': d,
                  'knots': ['0'] * (d + 1) + ['1'] * d + ['2'] * (d + 1),
                  'controls': [str(c) for c in controls]},
        },
        'sin_splines': {},
    }


def bernstein_to_power(controls):
    """Exact Bernstein polynomial coefficients in local s, low degree first."""
    d = len(controls) - 1
    coefficients = [Q(0)] * (d + 1)
    for i, c in enumerate(controls):
        for j in range(d - i + 1):
            coefficients[i + j] += c * comb(d, i) * comb(d - i, j) * (-1)**j
    return coefficients


def expected_power(m, epsilon, *, adversarial=True):
    e = admit(m, epsilon)
    d = 2 * m
    coeff = [Q(1)] + [Q(0)] * d
    if adversarial:
        a = Q(1, 2) - e
        ea = (a * (1 - a)) ** m
        for j in range(m + 1):
            coeff[m + j] -= Q(comb(m, j) * (-1)**j, 1) / ea
    return coeff


def check_source(spec, m, epsilon, *, adversarial=True):
    """Re-extract BOTH original Bézier spans by rational coefficient equality."""
    generated = construction(m, epsilon, adversarial=adversarial)
    if canonical(spec) != canonical(generated):
        raise Refusal('ORIGINAL_SOURCE_SPEC_OR_PHASE_MUTATED')
    ch = spec['cos_splines']['1']
    d = ch['degree']
    controls = [rational(x) for x in ch['controls']]
    if len(controls) != 2 * d + 1:
        raise Refusal('SOURCE_CONTROL_COUNT_INVALID')
    left = bernstein_to_power(controls[:d + 1])
    right = bernstein_to_power(controls[d:])
    if left != expected_power(m, epsilon, adversarial=adversarial):
        raise Refusal('ORIGINAL_LEFT_SPAN_BERNSTEIN_IDENTITY_FALSE')
    if right != [Q(1)] + [Q(0)] * d:
        raise Refusal('ORIGINAL_RIGHT_SPAN_NOT_IDENTITY_ONE')
    return True


def proof(m, epsilon):
    """Exact machine claim with source-complete mathematical proof.

    E(t)=(t(1-t))^m is symmetric, strictly rising on (0,1/2),
    strictly falling on (1/2,1), and zero at 0 and 1. Thus E(t)=E(a)
    has EXACTLY two simple solutions a,1-a. The cosine factor is strictly
    positive because 0 <= pi*t/8 <= pi/4 on [0,2]. The perturbation has
    zero order m at both 0 and 1, hence all derivatives through m-1 of
    baseline/adversary agree. They are identical throughout [1,2].
    The m-th derivative of their difference is nonzero at 0 and left
    of 1: its leading coefficient is +/-1/E(a) times positive cosine.
    No fixed jet budget N=m-1 certifies missing interior roots/signs.
    """
    e = admit(m, epsilon)
    a, b = Q(1, 2) - e, Q(1, 2) + e
    ea = (a * (1-a)) ** m
    baseline = construction(m, e, adversarial=False)
    adversary = construction(m, e, adversarial=True)
    check_source(baseline, m, e, adversarial=False)
    check_source(adversary, m, e, adversarial=True)
    assert a > 0 and b < 1 and a < Q(1,2) < b
    assert (b * (1-b))**m == ea
    assert Q(0) < ea < Q(1, 4)**m
    coef_zero = -1 / ea
    coef_knot_left = Q((-1)**(m+1), 1) / ea
    assert coef_zero != 0 and coef_knot_left != 0
    return {
        'schema': SCHEMA,
        'evidence_class': 'DETERMINISTIC_MODEL',
        'claim': 'C_FIXED_FINITE_ENDPOINT_KNOT_JET_BUDGET_INSUFFICIENT_FOR_COMPLETE_SOURCE_EVENTS',
        'm': m, 'matched_jet_orders': list(range(m)),
        'first_unmatched_jet_order': m,
        'epsilon': str(e), 'baseline_sha256': source_sha(baseline),
        'adversary_sha256': source_sha(adversary),
        'source_interval': ['0','2'], 'true_source_knot': '1',
        'phase_turn_law': {'offset':'0','rate':'1/16'},
        'source_degree': 2*m,
        'baseline_complete_zero_set': [],
        'adversary_complete_zero_set': [str(a), str(b)],
        'adversary_exact_open_sign_cells': [
            {'interval': ['0',str(a)], 'sign': 1},
            {'interval': [str(a),str(b)], 'sign': -1},
            {'interval': [str(b),'2'], 'sign': 1},
        ],
        'adversary_root_orders': [1,1],
        'endpoint_and_true_knot_jet_equality_through_order': m-1,
        'both_true_knot_point_values_equal_and_positive': True,
        'adversary_endpoint_or_knot_zero': False,
        'left_span_difference_order_m_coefficient_at_zero': str(coef_zero),
        'left_span_difference_order_m_coefficient_at_knot_without_cos_factor': str(coef_knot_left),
        'global_smooth_multiplicity_claimed': False,
        'baseline_and_adversary_same_piece_knot_phase_grammar': True,
        'pb00701_certified': False, 'mc_b_established': False,
        'mc1_established': False, 'production_authorized': False,
    }


def validate_source_pair(m, epsilon, submitted_baseline, submitted_adversary):
    """Fail closed on arbitrary caller-authored source/phase/controls."""
    try:
        check_source(submitted_baseline, m, epsilon, adversarial=False)
        check_source(submitted_adversary, m, epsilon, adversarial=True)
        return proof(m, epsilon)
    except (Refusal, ArithmeticError, OverflowError, RecursionError, MemoryError) as exc:
        return {'status': 'RESOURCE_REFUSAL' if 'RESOURCE_REFUSAL' in str(exc)
                or isinstance(exc, (OverflowError, RecursionError, MemoryError))
                else 'BLOCKED', 'reason': str(exc), 'is_truth_value': False,
                'pb00701_certified': False, 'production_authorized': False}
