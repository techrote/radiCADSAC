#!/usr/bin/env python3
"""V48 mixed rational/irrational root producer; historical v44 is unchanged.

Only the isolation workspace is deflated. Every certificate and multiplicity
is bound to the FULL original source. Finite root separation supplies termination.
"""
from fractions import Fraction as Q
from functools import cmp_to_key
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_algebraic_child_map_model as a
import pb00701_algebraic_orientation_cut_model as old

E, q, require = a.engine, a.q, a.require
RESOURCE_ERRORS = (MemoryError, OverflowError, RecursionError)
RELATION = 'EXACT_MIXED_ORIENTATION_ROOTS_WITH_FULL_SOURCE_ISOLATION'


def refusal(stage):
    return {'status': 'RESOURCE_REFUSAL', 'reason': 'PB00701_V48_EXACT_RESOURCE_REFUSAL',
            'stage': stage, 'is_truth_value': False}


def deflate(p, root):
    work, count = a.trim(p), 0
    require(work != [0], 'cannot deflate an identity')
    while E.degree(work) > 0 and E.peval(work, root) == 0:
        work, remainder = E.pdivmod(work, [-q(root), 1])
        require(remainder == [0], 'nonexact rational factor removal')
        count += 1
    return work, count


def full_source_interval(irrational_part, full_square_free, lo, hi):
    """Refine the existing unique irrational root until FULL-source unique.

The irrational workspace has no rational roots in (0,1). Its bisection cannot
hit the target. Every distinct full-source root is separated from that target,
so both full-source endpoint nonzeros and uniqueness eventually hold.
    """
    while (E.peval(full_square_free, lo) == 0 or E.peval(full_square_free, hi) == 0
           or E.distinct_roots_open(full_square_free, lo, hi) != 1):
        lo, hi = old._refine_unique_interval(irrational_part, lo, hi)
    return lo, hi


def exact_orientation_roots(poly, label):
    try:
        original = a.trim(poly)
        if original == [0]:
            return {'status': 'BLOCKED', 'reason': 'IDENTICALLY_ZERO_ORIENTATION', 'blocker': 'PB-007-01'}
        sf = E.square_free(original)
        rational = old._rational_roots_open(sf)
        workspace = sf
        # Both endpoint factors and every interior rational factor are removed
        # ONLY here, never from original amplitude/source polynomials.
        for root in (Q(0), Q(1), *rational):
            workspace, _ = deflate(workspace, root)
        intervals = old._isolate_irrational_roots(workspace) if E.degree(workspace) > 0 else []
        certificates = []
        for index, (lo, hi) in enumerate(intervals):
            lo, hi = full_source_interval(workspace, sf, lo, hi)
            cert = {
                'root_type': 'REAL_ALGEBRAIC_IRRATIONAL', 'label': label,
                'defining_square_free_polynomial': list(a.primitive(sf)),
                'source_polynomial_primitive': list(a.primitive(original)),
                'source_binding': 'EXACT_PRIMITIVE_SOURCE_POLYNOMIAL_TO_SQUARE_FREE_DEFINING_POLYNOMIAL',
                'isolating_interval': [str(lo), str(hi)],
                'unique_root_proof': {'method': 'EXACT_STURM_OPEN_INTERVAL_COUNT',
                                     'sturm_open_root_count': 1, 'rational_endpoints_are_not_roots': True},
                'multiplicity': old._multiplicity_at_isolated_root(original, lo, hi),
                'source_endpoint_order': '0 < alpha < 1', 'order_index_within_polynomial': index,
                'binary_float_used': False, 'epsilon_used': False,
                'sampling_used': False, 'approximate_root_used': False,
            }
            # Regenerated minimal-factor authority proves this is irrational,
            # not merely a caller label attached to an arbitrary isolated root.
            a.RealField.from_source_certificate(original, cert)
            old.validate_algebraic_root_certificate(cert, original)
            certificates.append(cert)
        endpoint_records = [{'source': str(x), 'multiplicity': deflate(original, x)[1]}
                            for x in (Q(0), Q(1)) if E.peval(original, x) == 0]
        rational_records = [{'source': str(x), 'multiplicity': deflate(original, x)[1]} for x in rational]
        count = E.distinct_roots_open(original, Q(0), Q(1))
        require(len(rational) + len(certificates) == count, 'incomplete exact source root accounting')
        return {
            'status': 'CERTIFIED', 'relation': RELATION, 'label': label,
            'source_polynomial': [str(x) for x in original],
            'isolation_workspace': [str(x) for x in workspace],
            'endpoint_roots': endpoint_records, 'rational_open_roots': rational_records,
            'irrational_open_roots': certificates,
            'distinct_roots_open': count, 'distinct_roots_closed': count + len(endpoint_records),
            'all_roots_accounted_exactly': True, 'physical_source_deflated': False,
        }
    except RESOURCE_ERRORS as exc:
        return refusal('root:' + type(exc).__name__)


def validate_orientation_roots(candidate, poly, label):
    expected = exact_orientation_roots(poly, label)
    if expected['status'] == 'RESOURCE_REFUSAL':
        return expected
    require(expected['status'] == 'CERTIFIED', 'no exact root enumeration')
    require(a._json(candidate) == a._json(expected), 'root/source/count certificate mismatch')
    return True


def exact_orientation_cuts(cos_polys, sin_polys):
    try:
        material = a._material(cos_polys, sin_polys, 'root-validation', ('0', '1'), '0', '1')
        cos, sin = ({int(h): a.trim(p) for h, p in material[k].items()}
                    for k in ('cos_polynomials', 'sin_polynomials'))
        groups, records = [], []
        for h in sorted((set(cos) | set(sin)) - {0}):
            c, s = cos.get(h, [Q(0)]), sin.get(h, [Q(0)])
            if c == [0] or s == [0]:
                continue
            for name, p in (('A', a.pscale(a.padd(c, s), Q(1, 2))),
                            ('B', a.pscale(a.padd(c, a.pscale(s, -1)), Q(1, 2)))):
                result = exact_orientation_roots(p, f'H{h}_{name}')
                if result['status'] != 'CERTIFIED':
                    return result
                records.append({'harmonic': h, 'coordinate': name, 'roots': result})
                for cert in result['irrational_open_roots']:
                    owner = {'harmonic': h, 'coordinate': name, 'multiplicity': cert['multiplicity']}
                    group = next((g for g in groups if old.compare_exact_algebraic_roots(cert, g['certificate']) == 0), None)
                    if group is None:
                        groups.append({'certificate': cert, 'ownership': [owner]})
                    else:
                        group['ownership'].append(owner)
        groups.sort(key=cmp_to_key(lambda x, y: old.compare_exact_algebraic_roots(x['certificate'], y['certificate'])))
        for index, group in enumerate(groups):
            group['order_index'] = index
            group['ownership'].sort(key=lambda x: (x['harmonic'], x['coordinate'], x['multiplicity']))
        orders = []
        for i in range(len(groups) - 1):
            require(old.compare_exact_algebraic_roots(groups[i]['certificate'], groups[i+1]['certificate']) == -1,
                    'unordered or duplicate algebraic cuts')
            orders.append({'lower_order_index': i, 'higher_order_index': i+1, 'relation': 'STRICTLY_LESS'})
        return {'status': 'CERTIFIED', 'relation': RELATION,
                'canonical_irrational_cuts': groups, 'source_root_records': records,
                'pairwise_exact_order': orders, 'endpoint_roots_are_internal_cuts': False,
                'physical_source_deflated': False}
    except RESOURCE_ERRORS as exc:
        return refusal('cuts:' + type(exc).__name__)


def build_child_maps(*source_args):
    try:
        material = a._material(*source_args)
        cuts = exact_orientation_cuts(source_args[0], source_args[1])
        if cuts['status'] != 'CERTIFIED':
            return cuts
        splits = [a._bisection(material, c) for c in cuts['canonical_irrational_cuts']]
        return {'status': 'REPRESENTATION_CERTIFIED' if splits else 'NOT_APPLICABLE',
                'source_material': material, 'root_certificate': cuts,
                'independent_single_cut_bisections': splits, 'analytic_cut_consumed': False}
    except RESOURCE_ERRORS as exc:
        return refusal('maps:' + type(exc).__name__)
