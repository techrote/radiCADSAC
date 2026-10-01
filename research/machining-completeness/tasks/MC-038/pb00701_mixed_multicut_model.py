#!/usr/bin/env python3
"""V49 finite mixed-root partition and complete monotone event composition.

V48 regenerates all root records; V45 bisections remain endpoint evidence only.
The actual children are original-parent-coordinate boundary pairs, not maps in
an invented common algebraic field. Source grammar and predecessor ownership
are unchanged. No resource budget, precision or sampling result is truth.
"""
from functools import cmp_to_key
from fractions import Fraction as Q
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_mixed_boundary_model as b

a, E, q, require = b.a, b.E, b.q, b.require
RELATION = 'EXACT_MIXED_BOUNDARY_MULTICUT_MONOTONE_COMPOSITION'
PARTITION = 'FINITE_SOURCE_ORIENTATION_AND_DIAGONAL_CERTIFICATE_PARTITION'
PHASE_FAMILY = 'V34_DIAGONAL_BOUNDARIES_MINUS_3_16_MINUS_1_16_PLUS_K_OVER_2'


def finite_phase_cuts(material):
    """The complete finite crossing set of an explicitly fixed old cell family."""
    offset, rate = b.local_phase(material)
    if not rate:
        return []
    cos, sin = b.maps(material)
    harmonics = sorted(h for h in set(cos) | set(sin) if h > 0 and
                       (cos.get(h, [0]) != [0] or sin.get(h, [0]) != [0]))
    cuts = []
    for h in harmonics:
        tlo, thi = sorted((h * offset, h * (offset + rate)))
        for base in (Q(-3, 16), Q(-1, 16)):
            kl, kh = 2 * (tlo - base), 2 * (thi - base)
            first = -((-kl.numerator) // kl.denominator)
            last = kh.numerator // kh.denominator
            for k in range(first, last + 1):
                boundary = base + Q(k, 2)
                t = (boundary / h - offset) / rate
                require(0 <= t <= 1, 'phase crossing escaped exact parent range')
                cuts.append({'source': str(t), 'kind': 'DIAGONAL_CERTIFICATE_BOUNDARY',
                             'harmonic': h, 'cell_index': k, 'base': str(base),
                             'harmonic_phase': str(boundary)})
    return cuts


def _source_orientation(material, certificate, owners):
    for owner in owners:
        polynomial = a._orientation(material, owner['harmonic'], owner['coordinate'])
        if a.primitive(polynomial) == a.primitive(certificate['source_polynomial_primitive']):
            return polynomial
    raise ValueError('irrational cut has no source orientation owner')


def _partition(*source_args):
    """Return (serial proof, runtime boundaries), regenerated from source only."""
    import pb00701_mixed_orientation_roots_model as roots
    material = a._material(*source_args)
    cos, sin = b.maps(material)
    root_certificate = roots.exact_orientation_cuts(cos, sin)
    if root_certificate['status'] != 'CERTIFIED':
        return root_certificate, []
    items = [dict(point=b.Boundary.at(i), causes=[{'kind': 'PARENT_ENDPOINT', 'side': name}], split=None)
             for i, name in ((0, 'left'), (1, 'right'))]
    for record in root_certificate['source_root_records']:
        h, coordinate = record['harmonic'], record['coordinate']
        polynomial = a._orientation(material, h, coordinate)
        for location, kind in (('endpoint_roots', 'ENDPOINT_ORIENTATION_ROOT'),
                               ('rational_open_roots', 'RATIONAL_ORIENTATION_ROOT')):
            for root in record['roots'][location]:
                t, m = q(root['source']), root['multiplicity']
                require(type(m) is int and m > 0 and E.multiplicity_at(polynomial, t) == m,
                        'rational root is not bound to its source multiplicity')
                require(0 <= t <= 1 and (kind != 'RATIONAL_ORIENTATION_ROOT' or 0 < t < 1),
                        'wrong rational root domain')
                items.append(dict(point=b.Boundary.at(t), split=None, causes=[
                    {'kind': kind, 'harmonic': h, 'coordinate': coordinate, 'multiplicity': m}]))
    for cut in root_certificate['canonical_irrational_cuts']:
        certificate, owners = cut['certificate'], cut['ownership']
        polynomial = _source_orientation(material, certificate, owners)
        point = b.Boundary.from_source(polynomial, certificate)
        split = a._bisection(material, cut)
        require(b.same(point.field.record(), split['field']), 'root/bisection real embedding mismatch')
        items.append(dict(point=point, split=split, causes=[
            {'kind': 'IRRATIONAL_ORIENTATION_ROOT', **owner} for owner in owners]))
    phase_cuts = finite_phase_cuts(material)
    for cut in phase_cuts:
        items.append(dict(point=b.Boundary.at(cut['source']), split=None, causes=[cut]))
    items.sort(key=cmp_to_key(lambda x, y: b.order_certificate(x['point'], y['point'])['comparison']))
    unique = []
    for item in items:
        if unique and b.order_certificate(unique[-1]['point'], item['point'])['comparison'] == 0:
            previous = unique[-1]
            previous['causes'].extend(item['causes'])
            if item['split'] is not None:
                require(previous['split'] is None or b.same(previous['split'], item['split']),
                        'incompatible independently bound copies of the same root')
                previous['split'] = item['split']
        else:
            unique.append(item)
    for item in unique:
        item['causes'] = [value for _, value in sorted({a._json(v): v for v in item['causes']}.items())]
    points = [item['point'] for item in unique]
    require(points[0] == b.Boundary.at(0) and points[-1] == b.Boundary.at(1), 'partition lost parent endpoints')
    order_proofs = [b.order_certificate(lo, hi) for lo, hi in zip(points, points[1:])]
    require(all(x['comparison'] == -1 for x in order_proofs), 'partition has duplicate or reversed cuts')
    boundary_records = [{'index': i, 'point': item['point'].record(), 'causes': item['causes'],
                         'endpoint_bisection': item['split']} for i, item in enumerate(unique)]
    parent_lo, parent_hi = map(q, material['parent_source_interval'])
    phase_offset, phase_rate = b.local_phase(material)
    cells = []
    for i, (lo, hi) in enumerate(zip(points, points[1:])):
        cells.append({'index': i, 'boundary_indices': [i, i + 1],
                      'representation': 'UNCHANGED_PARENT_COORDINATE_BOUNDARY_PAIR',
                      'parent_local_interval': [lo.record(), hi.record()],
                      'global_source_endpoints': [b.value_record(x.affine(parent_lo, parent_hi - parent_lo)) for x in (lo, hi)],
                      'phase_endpoints': [b.value_record(x.affine(phase_offset, phase_rate)) for x in (lo, hi)],
                      'source_parameter_id': material['source_parameter_id'],
                      'source_binding_sha256': b.digest(material),
                      'positive_width_proof': order_proofs[i], 'normalized_child_map': None})
    proof = {'status': 'PARTITION_CERTIFIED', 'method': PARTITION,
             'source_material': material, 'source_binding_sha256': b.digest(material),
             'root_certificate': root_certificate, 'phase_cut_family': PHASE_FAMILY,
             'phase_cuts': phase_cuts, 'boundaries': boundary_records, 'cells': cells,
             'cell_count': len(cells), 'coverage': 'EXACT_ORDERED_PARENT_COVER_NO_GAPS_OR_OVERLAPS',
             'compositum_claimed': False, 'normalized_mixed_field_maps_claimed': False,
             'proof_cuts_are_physical_roots': False}
    return proof, points


def build_partition(*source_args):
    try:
        return _partition(*source_args)[0]
    except b.RESOURCE_ERRORS as exc:
        return b.refusal('partition:' + type(exc).__name__)


def validate_partition(candidate, *source_args):
    regenerated = build_partition(*source_args)
    if regenerated['status'] == 'RESOURCE_REFUSAL':
        return regenerated
    require(regenerated['status'] == 'PARTITION_CERTIFIED', 'no source-derived partition')
    require(b.same(candidate, regenerated), 'partition/source/ownership/order/coverage mismatch')
    return True


def _rational_endpoint(material, point):
    import pb00701_multiharmonic_monotone_anchor_model as v19
    require(point.rational is not None, 'rational endpoint cannot accept an algebraic boundary')
    cos, sin = b.maps(material)
    offset, rate = b.local_phase(material)
    return v19._endpoint_relation(cos, sin, point.rational, offset + rate * point.rational)


def _endpoint(material, point, boundary_record):
    if point.rational is not None:
        return _rational_endpoint(material, point)
    import pb00701_algebraic_endpoint_model as v46
    import pb00701_algebraic_endpoint_certificate as epcheck
    split = boundary_record['endpoint_bisection']
    require(split is not None and b.same(point.field.record(), split['field']), 'missing bound irrational endpoint')
    result = v46._decide_endpoint(material, split)
    if result['status'] == 'ENDPOINT_CERTIFIED':
        epcheck._validate_endpoint(result, material, split)
    return result


def _assemble(partition, derivatives, endpoints):
    """Internal semantic composition. The outer checker binds all witnesses."""
    import pb00701_algebraic_monotone_cut_model as v47
    import pb00701_phase_sector_partition_model as v27
    cells, boundaries = partition['cells'], partition['boundaries']
    require(len(derivatives) == len(cells) and len(endpoints) == len(boundaries), 'multi-cut cardinality mismatch')
    require(len(cells) >= 3, 'v49 multi-cut consumption needs at least three cells')
    require(any(x['point']['kind'] == 'ALGEBRAIC_IRRATIONAL' for x in boundaries), 'v49 requires an irrational boundary')
    children = []
    for i, cell in enumerate(cells):
        summary = v47.child_summary(derivatives[i], endpoints[i], endpoints[i + 1])
        if summary['status'] != 'CERTIFIED':
            return summary
        children.append({'parent_local_interval': cell['parent_local_interval'],
                         'source_parameter_id': partition['source_material']['source_parameter_id'],
                         'cell': cell, 'derivative_certificate': derivatives[i], 'summary': summary})
    directions = [c['summary']['derivative_sign'] for c in children]
    if any(type(sign) is not int or sign not in (-1, 1) for sign in directions):
        return {'status': 'SEMANTIC_BLOCKER', 'reason': 'INVALID_STRICT_DERIVATIVE_DIRECTION'}
    if len(set(directions)) != 1:
        return {'status': 'SEMANTIC_BLOCKER', 'reason': 'INCOMPATIBLE_STRICT_CLOSED_DERIVATIVES_AT_SMOOTH_CUT'}
    # _compose_child_summaries copies exact boundary records as opaque source
    # positions; it never subtracts them or rationalizes algebraic numbers.
    composition = v27._compose_child_summaries(children)
    if composition['status'] != 'CERTIFIED':
        return composition
    return {**composition, 'relation': RELATION,
            'source_parameter_id': partition['source_material']['source_parameter_id'],
            'partition': partition, 'children': children, 'endpoint_evidence': endpoints,
            'child_count': len(children), 'analytic_multicut_consumed': True,
            'general_nonmonotone_root_solver_claimed': False, 'compositum_claimed': False}


def build_multicut_event(*source_args):
    stage = 'partition'
    try:
        partition, points = _partition(*source_args)
        if partition['status'] != 'PARTITION_CERTIFIED':
            return partition
        if len(points) < 4 or not any(p.field is not None for p in points):
            return b.blocked('NO_MIXED_MULTICUT_PARTITION')
        material = partition['source_material']
        if not q(material['phase_turn_law']['rate']):
            return b.blocked('ZERO_PHASE_PREDECESSOR_OWNERSHIP')
        derivatives = []
        for i, (lo, hi) in enumerate(zip(points, points[1:])):
            stage = 'closed-child:' + str(i)
            result = b.certify_derivative(material, lo, hi)
            if result['status'] != 'CERTIFIED':
                return {**result, 'failed_child_index': i, 'partition': partition}
            derivatives.append(result)
        endpoints = []
        for i, (point, record) in enumerate(zip(points, partition['boundaries'])):
            stage = 'endpoint:' + str(i)
            result = _endpoint(material, point, record)
            if result.get('status') in ('RESOURCE_REFUSAL', 'SEMANTIC_BLOCKER'):
                return result
            if result.get('status') not in ('DECIDED', 'ENDPOINT_CERTIFIED'):
                return b.blocked('PHYSICAL_ENDPOINT_NOT_DECIDED', boundary_index=i, endpoint=result)
            endpoints.append(result)
        stage = 'composition'
        return _assemble(partition, derivatives, endpoints)
    except b.RESOURCE_ERRORS as exc:
        return b.refusal(stage + ':' + type(exc).__name__)


def classify_required_analytic_event(spec):
    """Complete v48 validation/precedence first; never swallow source exceptions."""
    import pb00701_mixed_orientation_consumer as v48
    try:
        baseline = v48.classify_required_analytic_event(spec)
        if not isinstance(baseline, dict) or baseline.get('status') != 'BLOCKED':
            return baseline
        if baseline.get('relation') != 'FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER':
            return baseline
        spans, changed = [], False
        for original in baseline.get('spans', []):
            span = dict(original)
            if span.get('route', {}).get('status') == 'BLOCKED' and all(k in span for k in ('cos_polynomials', 'sin_polynomials')):
                phase = baseline['phase_turn_law']
                result = build_multicut_event(
                    {int(h): p for h, p in span['cos_polynomials'].items()},
                    {int(h): p for h, p in span['sin_polynomials'].items()},
                    baseline['source_parameter_id'], span['source_interval'], phase['offset'], phase['rate'])
                if result.get('status') in ('CERTIFIED', 'RESOURCE_REFUSAL', 'SEMANTIC_BLOCKER'):
                    span['route_kind'], span['route'] = 'PB00701_V49_MIXED_BOUNDARY_MULTICUT', result
                    changed = True
            spans.append(span)
        if not changed:
            return baseline
        statuses = {s.get('route', {}).get('status') for s in spans}
        status = ('RESOURCE_REFUSAL' if 'RESOURCE_REFUSAL' in statuses else
                  'SEMANTIC_BLOCKER' if 'SEMANTIC_BLOCKER' in statuses else
                  'CERTIFIED' if statuses == {'CERTIFIED'} else 'BLOCKED')
        return {**baseline, 'status': status, 'spans': spans,
                'relation': 'FINITE_EXACT_PIECEWISE_MIXED_BOUNDARY_MULTICUT_EVENT_DECISION' if status == 'CERTIFIED' else baseline['relation'],
                'blocker': None if status == 'CERTIFIED' else 'PB-007-01',
                'v49_mixed_boundary_multicut_extension': True,
                **({'is_truth_value': False} if status == 'RESOURCE_REFUSAL' else {})}
    except b.RESOURCE_ERRORS as exc:
        return b.refusal('source:' + type(exc).__name__)
