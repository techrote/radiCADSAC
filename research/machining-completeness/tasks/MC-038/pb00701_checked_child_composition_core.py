#!/usr/bin/env python3
"""MC-038 conditional exact composition core for *fully split rational polynomials*.

This is deliberately NOT an adapter for historic V27/V41, whose trigonometric
child certificates do not establish the required full ordered root witnesses.
The checker reconstructs complete roots directly from exactly verified factor
identities. Count-only, opaque child assertions and unsupported functions cannot
be promoted to truth. All coordinates, comparisons and signs are rational.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as Q

SCHEMA = 'radicadsac-mc038-checked-rational-child-composition/1.0'
SOURCE_KIND = 'FULLY_SPLIT_RATIONAL_POLYNOMIAL_IN_GLOBAL_SOURCE_PARAMETER'
MAX_DEGREE = 24
MAX_SPANS = 32
MAX_CUTS = 128


class InvalidWitness(ValueError):
    """Malformed or contradicted evidence; never a certification."""


def need(predicate, reason):
    if not predicate:
        raise InvalidWitness(reason)


def rational(value):
    # Python bool is an int: reject it explicitly, along with float and NaN.
    need(type(value) is str, 'rational must be a string; floats and booleans are forbidden')
    need(value and len(value) <= 128, 'missing or overlong rational')
    try:
        q = Q(value)
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise InvalidWitness('invalid exact rational') from exc
    need(str(q) == value, 'rational is not canonical (e.g. 2/4, +1, or 1.0)')
    return q


def fields(obj, required, optional=()):
    need(type(obj) is dict and set(required) <= set(obj) <= set(required) | set(optional),
         'missing or unsupported certificate keys')


def trim(poly):
    result = list(poly)
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def multiply(a, b):
    c = [Q(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i + j] += x * y
    return trim(c)


def at(coeffs, x):
    result = Q(0)
    for c in reversed(coeffs):
        result = result * x + c
    return result


def refuse(reason):
    return {'status': 'RESOURCE_REFUSAL', 'reason': reason,
            'is_truth_value': False, 'certification_authorized': False}


def blocked(reason):
    return {'status': 'BLOCKED', 'reason': reason,
            'is_truth_value': False, 'certification_authorized': False}


def parse_source(spec):
    fields(spec, ('schema', 'source_kind', 'source_parameter_id', 'source_spans', 'cuts'))
    need(spec['schema'] == SCHEMA and spec['source_kind'] == SOURCE_KIND,
         'unsupported source kind/schema; no trigonometric/adaptor authority')
    need(type(spec['source_parameter_id']) is str and 0 < len(spec['source_parameter_id']) <= 128,
         'source parameter identity required')
    spans = spec['source_spans']
    need(type(spans) is list and spans, 'no physical source spans')
    if len(spans) > MAX_SPANS:
        return refuse('SPAN_BUDGET_EXCEEDED')
    parsed = []
    for row in spans:
        fields(row, ('interval', 'coefficients', 'factor_witness'))
        interval = row['interval']
        need(type(interval) is list and len(interval) == 2, 'invalid source interval')
        lo, hi = map(rational, interval)
        need(lo < hi, 'source span must have positive width')
        coefficients = row['coefficients']
        need(type(coefficients) is list and coefficients, 'missing coefficients')
        if len(coefficients) - 1 > MAX_DEGREE:
            return refuse('EXACT_FACTOR_DEGREE_BUDGET_EXCEEDED')
        coefficients = [rational(x) for x in coefficients]
        need(trim(coefficients) == coefficients, 'noncanonical polynomial coefficients')
        if coefficients == [0]:
            return blocked('IDENTICALLY_ZERO_PHYSICAL_INTERVAL_NOT_DISCRETE_ROOTS')
        witness = row['factor_witness']
        fields(witness, ('scale', 'linear_factors'))
        scale = rational(witness['scale'])
        need(scale != 0, 'zero scale is not a complete factor witness')
        factors = witness['linear_factors']
        need(type(factors) is list, 'missing complete rational factor list')
        if len(factors) > MAX_DEGREE:
            return refuse('EXACT_FACTOR_COUNT_BUDGET_EXCEEDED')
        polynomial = [scale]
        roots = {}
        for factor in factors:
            fields(factor, ('root', 'multiplicity'))
            root = rational(factor['root'])
            mult = factor['multiplicity']
            need(type(mult) is int and 1 <= mult <= MAX_DEGREE,
                 'multiplicity must be an exact positive integer')
            need(root not in roots, 'duplicate linear factor; group multiplicities exactly')
            roots[root] = mult
            if sum(roots.values()) > MAX_DEGREE:
                return refuse('EXACT_FACTOR_DEGREE_BUDGET_EXCEEDED')
            for _ in range(mult):
                polynomial = multiply(polynomial, [-root, Q(1)])
        # This exact identity is the completeness premise, not a caller root count.
        need(polynomial == coefficients, 'factor witness does not equal the complete source polynomial')
        if parsed:
            need(parsed[-1]['hi'] == lo, 'original source knots have gap/overlap')
            need(at(parsed[-1]['poly'], lo) == at(coefficients, lo),
                 'source discontinuity at original knot')
        parsed.append({'lo': lo, 'hi': hi, 'poly': coefficients, 'roots': roots})
    cuts = spec['cuts']
    need(type(cuts) is list, 'proof cuts are not a list')
    if len(cuts) > MAX_CUTS:
        return refuse('CERTIFICATE_CUT_BUDGET_EXCEEDED')
    cut_values = [rational(x) for x in cuts]
    need(all(parsed[0]['lo'] < x < parsed[-1]['hi'] for x in cut_values),
         'cut outside source interior, including zero-width exterior cut')
    # Caller cut order, duplicates, and coincident real source knots carry no truth.
    return parsed, sorted(set(cut_values))


def nonzero_sign(value):
    need(value != 0, 'inferred nonzero cell contains an unaccounted zero')
    return 1 if value > 0 else -1


def span_for_open_point(spans, x):
    matches = [row for row in spans if row['lo'] < x < row['hi']]
    need(len(matches) == 1, 'cell sample is not in exactly one physical source span')
    return matches[0]


def one_sided_sign(row, x, direction):
    """Exact leading jet from complete rational polynomial factorization."""
    mult = row['roots'].get(x, 0)
    if not mult:
        return nonzero_sign(at(row['poly'], x)), 0
    remaining = Q(row['poly'][-1])
    for root, order in row['roots'].items():
        if root != x:
            remaining *= (x - root) ** order
    need(remaining != 0, 'factor witness lost a multiplicity')
    sign = nonzero_sign(remaining)
    return sign * (direction ** mult), mult


def compose(spec):
    """Prove a conditional subset's complete physical ordering, or fail closed.

    Never consumes a historical owner, root count, child route label, or caller
    assertion of a physical event. All roots are re-derived from exact source
    polynomials and their algebraically checked complete factor witnesses.
    """
    parsed = parse_source(spec)
    if type(parsed) is dict:  # typed non-truth resource/blocker result
        return parsed
    spans, cuts = parsed
    left, right = spans[0]['lo'], spans[-1]['hi']
    roots = sorted({r for row in spans for r in row['roots'] if row['lo'] <= r <= row['hi']})
    knots = [row['hi'] for row in spans[:-1]]
    all_partition_points = sorted(set([left, right] + knots + cuts + roots))
    cells = []
    for a, b in zip(all_partition_points, all_partition_points[1:]):
        mid = (a + b) / 2
        row = span_for_open_point(spans, mid)
        need(not any(a < x < b for x in row['roots']), 'incomplete physical interval partition')
        cells.append({'left': str(a), 'right': str(b),
                      'sign': 'POSITIVE' if nonzero_sign(at(row['poly'], mid)) == 1 else 'NEGATIVE',
                      'has_open_root': False})
    events = []
    for x in roots:
        left_rows = [row for row in spans if row['lo'] < x <= row['hi']]
        right_rows = [row for row in spans if row['lo'] <= x < row['hi']]
        lr = left_rows[0] if left_rows else None
        rr = right_rows[0] if right_rows else None
        left_info = one_sided_sign(lr, x, -1) if lr is not None else None
        right_info = one_sided_sign(rr, x, +1) if rr is not None else None
        need((lr is None or left_info[1] > 0) and (rr is None or right_info[1] > 0),
             'a source boundary zero has an inconsistent factor witness')
        knot = x in knots
        if knot:
            need(lr is not rr and left_info and right_info,
                 'source knot has no two independent one-sided jets')
            label = 'SOURCE_KNOT_SIGN_CHANGE' if left_info[0] != right_info[0] else 'SOURCE_KNOT_TOUCH'
            smooth_order = None  # absolutely no fictitious global differentiability
        elif left_info and right_info:
            need(lr is rr and left_info[1] == right_info[1],
                 'a smooth proof cut has incompatible multiplicity')
            smooth_order = left_info[1]
            need((left_info[0] != right_info[0]) == bool(smooth_order % 2),
                 'smooth crossing parity contradicts exact factor order')
            label = 'CROSSING' if smooth_order % 2 else 'TANGENCY'
        else:
            smooth_order = (left_info or right_info)[1]
            label = 'SOURCE_ENDPOINT_ZERO'
        events.append({'position': str(x), 'kind': label, 'source_knot': knot,
                       'on_proof_cut': x in cuts,
                       'left_order': left_info[1] if left_info else None,
                       'right_order': right_info[1] if right_info else None,
                       'smooth_physical_multiplicity': smooth_order,
                       'left_sign': left_info[0] if left_info else None,
                       'right_sign': right_info[0] if right_info else None})
    event_positions = sorted(set([left, right] + roots))
    maximal_cells = []
    for a, b in zip(event_positions, event_positions[1:]):
        in_range = [c for c in cells if Q(c['left']) >= a and Q(c['right']) <= b]
        need(in_range and Q(in_range[0]['left']) == a and Q(in_range[-1]['right']) == b,
             'physical interval not completely covered')
        signs = set(c['sign'] for c in in_range)
        need(len(signs) == 1, 'source discontinuity or missing physical root across proof cut')
        maximal_cells.append({'left': str(a), 'right': str(b),
                              'sign': in_range[0]['sign'], 'open': True})
    interior = [e for e in events if left < Q(e['position']) < right]
    output = {'status': 'CONDITIONAL_EXACT_RATIONAL_SUBSET_COMPOSED',
              'schema': SCHEMA, 'source_kind': SOURCE_KIND,
              'source_parameter_id': spec['source_parameter_id'],
              'source_binding_sha256': hashlib.sha256(json.dumps(
                  {'source_parameter_id': spec['source_parameter_id'],
                   'spans': [{'interval': [str(row['lo']), str(row['hi'])],
                              'coefficients': list(map(str, row['poly']))} for row in spans]},
                  sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
              'proof_cuts': list(map(str, cuts)), 'source_knots': list(map(str, knots)),
              'events': events, 'maximal_open_sign_cells': maximal_cells,
              'split_proof_cells': cells,
              'summary': {'distinct_roots_open': len(interior),
                          'distinct_roots_closed': len(events),
                          'smooth_crossings_open': sum(e['kind'] == 'CROSSING' for e in interior),
                          'smooth_tangencies_open': sum(e['kind'] == 'TANGENCY' for e in interior),
                          'source_knot_zeros_open': sum(e['source_knot'] for e in interior)},
              'historical_v54_dispositions_unchanged': True,
              'v27_v41_trigonometric_children_certified': False,
              'pb00701_certified': False, 'mc_b_established': False,
              'mc1_established': False, 'production_authorized': False}
    return output
