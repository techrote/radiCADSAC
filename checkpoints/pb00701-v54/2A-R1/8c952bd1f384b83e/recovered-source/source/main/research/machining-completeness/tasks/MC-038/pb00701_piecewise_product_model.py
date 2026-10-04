#!/usr/bin/env python3
"""V52 full-source continuous knot composition, preserving V51 span authority.

A shared knot has two one-sided analytic orders, NOT their sum or an assumed
single analytic multiplicity. Physical continuity is exact value equality, not
matching signs. Only source knots with proved nonzero values coalesce sign cells.
"""
from fractions import Fraction as Q
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_algebraic_child_map_model as a
import pb00701_mixed_boundary_model as b

E, q, require = a.engine, a.q, a.require
RESOURCE_ERRORS = b.RESOURCE_ERRORS
RELATION = 'EXACT_CONTINUOUS_PIECEWISE_PRODUCT_ROOTS_AND_SIGN_CELLS'
GRAMMAR = 'RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE'
ALLOWED = {'grammar', 'cos_splines', 'sin_splines', 'parameter_lo', 'parameter_hi',
           'phase_turn_offset', 'phase_turn_rate', 'source_parameter_id', 'parameter_projection'}
SIGNS = {'NEGATIVE': -1, 'ZERO': 0, 'POSITIVE': 1}


def refusal(stage):
    return {'status': 'RESOURCE_REFUSAL', 'reason': 'PB00701_V52_EXACT_RESOURCE_REFUSAL',
            'stage': stage, 'is_truth_value': False}


def lower_source(spec):
    """Regenerate all original source knots and powers via preserved V7, no route search."""
    import pb00701_coupled_bspline_model as v7
    require(isinstance(spec, dict) and spec.get('grammar') == GRAMMAR, 'unsupported piecewise source grammar')
    require(not (set(spec) - ALLOWED), 'unknown full-source authority field')
    ident = spec['source_parameter_id']
    require(isinstance(ident, str) and bool(ident), 'missing original source identity')
    require(spec.get('parameter_projection') in (None, ident), 'independent source projection')
    lo, hi = q(spec['parameter_lo']), q(spec['parameter_hi'])
    require(lo < hi, 'empty or reversed original source interval')
    offset, rate = q(spec['phase_turn_offset']), q(spec['phase_turn_rate'])
    normals = [v7._normalise_harmonic_splines(spec.get(key), key)
               for key in ('cos_splines', 'sin_splines')]
    all_normals = [normal for mapping in normals for normal in mapping.values()]
    require(bool(all_normals), 'empty physical source')
    boundaries = v7._master_boundaries(all_normals, lo, hi)
    canonical = {'grammar': GRAMMAR, 'source_parameter_id': ident,
                 'parameter_projection': spec.get('parameter_projection'),
                 'parameter_lo': str(lo), 'parameter_hi': str(hi),
                 'phase_turn_offset': str(offset), 'phase_turn_rate': str(rate)}
    for key, mapping in zip(('cos_splines', 'sin_splines'), normals):
        canonical[key] = {str(h): v7._canonical_bspline_spec(n) for h, n in sorted(mapping.items())}
    spans = []
    for i, (left, right) in enumerate(zip(boundaries, boundaries[1:])):
        require(left < right, 'zero-width source span')
        pieces = [{h: v7._piece_from_normal(n, left, right) for h, n in sorted(mapping.items())}
                  for mapping in normals]
        maps = [{h: piece['coefficients'] for h, piece in mapping.items()} for mapping in pieces]
        material = a._material(*maps, ident, (left, right), offset, rate)
        limits = []
        for side in ('left_limit', 'right_limit'):
            limits.append({kind: {str(h): str(piece[side]) for h, piece in mapping.items()}
                           for kind, mapping in zip(('COS', 'SIN'), pieces)})
        spans.append({'span_index': i, 'source_interval': [str(left), str(right)],
                      'material': material, 'material_binding_sha256': b.digest(material),
                      'one_sided_amplitude_limits': limits,
                      'parent_map': {'offset': str(left), 'positive_scale': str(right-left)}})
    return {'status': 'SOURCE_LOWERING_CERTIFIED', 'source_spec': canonical,
            'source_binding_sha256': b.digest(canonical), 'source_parameter_id': ident,
            'source_interval': [str(lo), str(hi)], 'phase_turn_law': {'offset': str(offset), 'rate': str(rate)},
            'source_boundaries': [str(x) for x in boundaries], 'spans': spans,
            'partition_authority': 'EXACT_UNION_OF_ORIGINAL_SOURCE_KNOTS_AND_REQUESTED_EXTERIORS',
            'caller_lowering_trusted': False, 'source_knots_are_physical_roots_by_default': False}


def source_args(row):
    mat = row['material']
    return ({int(h): p for h, p in mat['cos_polynomials'].items()},
            {int(h): p for h, p in mat['sin_polynomials'].items()},
            mat['source_parameter_id'], mat['parent_source_interval'],
            mat['phase_turn_law']['offset'], mat['phase_turn_law']['rate'])


def check_spans(lowering, proofs):
    import pb00701_ordered_product_certificate as checker
    require(isinstance(proofs, list) and len(proofs) == len(lowering['spans']), 'omitted or extra source-span witness')
    require(len(proofs) >= 2, 'V52 needs more than one original source span')
    for row, proof in zip(lowering['spans'], proofs):
        checked = checker.validate_ordered_product_event(proof, *source_args(row))
        if checked is not True:
            return checked
    return True


def knot_continuity(left, right, left_proof, right_proof):
    """Exact physical difference at the common rational source knot; no sampled signs."""
    import pb00701_multiharmonic_monotone_anchor_model as v19
    knot = left['source_interval'][1]
    require(knot == right['source_interval'][0], 'source-knot gap or overlap')
    lm, rm = left['material'], right['material']
    require(lm['source_parameter_id'] == rm['source_parameter_id']
            and b.same(lm['phase_turn_law'], rm['phase_turn_law']), 'source identity or phase discontinuity')
    turn = q(lm['phase_turn_law']['offset']) + q(lm['phase_turn_law']['rate']) * q(knot)
    lvalues, rvalues = left['one_sided_amplitude_limits'][1], right['one_sided_amplitude_limits'][0]
    differences = []
    for kind in ('COS', 'SIN'):
        keys = sorted(set(lvalues[kind]) | set(rvalues[kind]), key=int)
        differences.append({int(h): [q(rvalues[kind].get(h, '0'))-q(lvalues[kind].get(h, '0'))] for h in keys})
    difference = v19._endpoint_relation(*differences, Q(0), turn)
    if difference.get('status') in ('RESOURCE_REFUSAL', 'SEMANTIC_BLOCKER'):
        return difference
    require(difference.get('status') == 'DECIDED' and difference['relation'] in SIGNS,
            'unresolved physical source-knot equality')
    common = {'knot': knot, 'phase_turn': str(turn), 'source_parameter_id': lm['source_parameter_id'],
              'span_indices': [left['span_index'], right['span_index']],
              'source_material_bindings': [b.digest(lm), b.digest(rm)],
              'one_sided_amplitude_values': [lvalues, rvalues],
              'difference_is_right_minus_left': True, 'physical_difference_evidence': difference}
    if difference['relation'] != 'ZERO':
        return b.blocked('PHYSICAL_SOURCE_KNOT_DISCONTINUITY', **common,
                         valid_manufacturing_source_rejected_as_invalid=False)
    lb, rb = left_proof['ordered_boundaries'][-1], right_proof['ordered_boundaries'][0]
    global_knot = {'kind': 'RATIONAL', 'value': knot}
    require(b.same(lb['global_position'], global_knot) and b.same(rb['global_position'], global_knot),
            'span endpoint is not this exact source knot')
    require(lb['physical_relation'] == rb['physical_relation'], 'equal physical values have inconsistent relations')
    relation = lb['physical_relation']
    signs = [lb['inward_sign'], rb['inward_sign']]
    require(all(type(x) is int and x in (-1, 1) for x in signs), 'missing exact one-sided neighborhood sign')
    orders = [lb['physical_multiplicity'], rb['physical_multiplicity']]
    require(all(type(x) is int and x >= 0 for x in orders), 'invalid one-sided analytic orders')
    if relation == 'ZERO':
        require(all(x > 0 for x in orders), 'zero source knot lacks both one-sided orders')
        kind = 'CROSSING' if signs[0] != signs[1] else 'TANGENCY'
    else:
        require(orders == [0, 0] and signs == [SIGNS[relation]]*2, 'nonzero continuous knot cannot change sign')
        kind = 'NONZERO'
    widths = [q(row['source_interval'][1])-q(row['source_interval'][0]) for row in (left, right)]
    return {**common, 'status': 'KNOT_CONTINUITY_CERTIFIED', 'physical_relation': relation,
            'one_sided_orders': orders, 'one_sided_signs': signs, 'event_kind': kind,
            'global_derivative_scales': [str(Q(1)/width**order) for width, order in zip(widths, orders)],
            'analytic_multiplicity': None, 'one_sided_orders_are_added': False,
            'left_endpoint_witness_binding_sha256': b.digest(lb),
            'right_endpoint_witness_binding_sha256': b.digest(rb),
            'physical_value_equals_both_source_limits': True}


def build_joins(lowering, proofs):
    joins = []
    for i in range(len(proofs)-1):
        join = knot_continuity(lowering['spans'][i], lowering['spans'][i+1], proofs[i], proofs[i+1])
        if join.get('status') != 'KNOT_CONTINUITY_CERTIFIED':
            return join
        joins.append(join)
    return joins


def assemble(lowering, proofs, joins):
    """Compose already checked exact span evidence; checker regenerates this formula."""
    n = len(proofs)
    require(n == len(lowering['spans']) and n >= 2 and len(joins) == n-1, 'piecewise cardinality mismatch')
    roots, cells, boundaries, id_maps = [], [], [], []
    for i, proof in enumerate(proofs):
        local = proof['ordered_boundaries']
        require(len(local) >= 2, 'empty span boundary decomposition')
        mapping = {}
        for j, point in enumerate(local):
            if j == 0 and i > 0:
                mapping[point['id']] = 'knot:' + str(i-1)
                continue  # The same knot already owns the preceding endpoint.
            ident = ('knot:' + str(i) if j == len(local)-1 and i < n-1 else
                     'exterior:left' if i == 0 and j == 0 else
                     'exterior:right' if i == n-1 and j == len(local)-1 else
                     'span:' + str(i) + '/' + point['id'])
            mapping[point['id']] = ident
            if ident.startswith('knot:'):
                join = joins[i]
                row = {'id': ident, 'kind': 'SOURCE_KNOT', 'global_position': point['global_position'],
                       'span_references': [[i, point['id']], [i+1, proofs[i+1]['ordered_boundaries'][0]['id']]],
                       'physical_relation': join['physical_relation'], 'event_kind': join['event_kind'],
                       'analytic_multiplicity': None, 'one_sided_orders': join['one_sided_orders'],
                       'neighborhood_signs': join['one_sided_signs'], 'continuity_binding_sha256': b.digest(join)}
            else:
                row = {'id': ident, 'kind': 'SOURCE_EXTERIOR' if ident.startswith('exterior:') else 'SPAN_ROOT',
                       'global_position': point['global_position'], 'span_references': [[i, point['id']]],
                       'physical_relation': point['physical_relation'], 'event_kind': point['event_kind'],
                       'analytic_multiplicity': point['physical_multiplicity'],
                       'one_sided_orders': None, 'local_boundary_binding_sha256': b.digest(point)}
                if ident == 'exterior:left':
                    row['neighborhood_signs'] = [None, point['inward_sign']]
                elif ident == 'exterior:right':
                    row['neighborhood_signs'] = [point['inward_sign'], None]
                else:
                    row['neighborhood_signs'] = point['adjacent_cell_signs']
            boundaries.append(row)
        id_maps.append(mapping)
    for i, proof in enumerate(proofs):
        for j, cell in enumerate(proof['sign_cells']):
            ids = [id_maps[i][name] for name in cell['boundary_ids']]
            cells.append({'index': len(cells), 'source_span_index': i, 'local_cell_index': j,
                          'boundary_ids': ids, 'global_source_endpoints': cell['global_source_endpoints'],
                          'physical_sign': cell['physical_sign'], 'physical_relation': cell['physical_relation'],
                          'local_cell_binding_sha256': b.digest(cell), 'distinct_roots_open': 0,
                          'source_parameter_id': lowering['source_parameter_id']})
    require(len({p['id'] for p in boundaries}) == len(boundaries), 'global identifier collision')
    require(len(cells) == len(boundaries)-1, 'piecewise elementary coverage cardinality')
    for cell, left, right in zip(cells, boundaries, boundaries[1:]):
        require(cell['boundary_ids'] == [left['id'], right['id']], 'elementary source gap, overlap or wrong order')
        require(b.same(cell['global_source_endpoints'], [left['global_position'], right['global_position']]),
                'cell/source global endpoint mismatch')
        require(cell['physical_sign'] == left['neighborhood_signs'][1] == right['neighborhood_signs'][0],
                'elementary sign disagrees with endpoint neighborhood')
    lookup = {p['id']: p for p in boundaries}
    maximal = []
    for cell in cells:
        bridge = lookup[cell['boundary_ids'][0]]
        if maximal and bridge['kind'] == 'SOURCE_KNOT' and bridge['physical_relation'] != 'ZERO':
            current = maximal[-1]
            require(current['boundary_ids'][1] == bridge['id'] and current['physical_sign'] == cell['physical_sign'],
                    'nonzero knot coalescing sign or position mismatch')
            current['boundary_ids'][1] = cell['boundary_ids'][1]
            current['global_source_endpoints'][1] = cell['global_source_endpoints'][1]
            current['elementary_cell_indices'].append(cell['index'])
            current['included_nonzero_source_knots'].append(bridge['id'])
        else:
            maximal.append({'index': len(maximal), 'boundary_ids': list(cell['boundary_ids']),
                            'global_source_endpoints': list(cell['global_source_endpoints']),
                            'physical_sign': cell['physical_sign'], 'physical_relation': cell['physical_relation'],
                            'elementary_cell_indices': [cell['index']], 'included_nonzero_source_knots': [],
                            'distinct_roots_open': 0, 'connected_open_interval': True})
    roots = [row for row in boundaries if row['physical_relation'] == 'ZERO']
    open_roots = [row for row in roots if row['kind'] != 'SOURCE_EXTERIOR']
    zero_joins = sum(join['physical_relation'] == 'ZERO' for join in joins)
    local_closed = sum(proof['physical_root_summary']['total_distinct_roots_closed'] for proof in proofs)
    require(len(roots) == local_closed-zero_joins, 'shared source-knot root union double counted or omitted')
    require(len(maximal) == len(open_roots)+1, 'maximal nonzero cell decomposition incomplete')
    summary = {'distinct_roots_open': len(open_roots), 'total_distinct_roots_closed': len(roots),
               'crossings_open': sum(x['event_kind'] == 'CROSSING' for x in open_roots),
               'tangencies_open': sum(x['event_kind'] == 'TANGENCY' for x in open_roots),
               'source_knot_roots': zero_joins,
               'knot_roots_without_global_analytic_multiplicity': zero_joins,
               'analytic_multiple_roots_strictly_inside_spans': sum(x['kind'] == 'SPAN_ROOT' and x['analytic_multiplicity'] > 1 for x in roots),
               'exterior_root_orders': {side: p['analytic_multiplicity'] for side, p in
                                       (('left', boundaries[0]), ('right', boundaries[-1])) if p['physical_relation'] == 'ZERO'}}
    return {'status': 'PIECEWISE_PRODUCT_CERTIFIED', 'method': RELATION, 'source_lowering': lowering,
            'source_binding_sha256': lowering['source_binding_sha256'], 'span_proofs': proofs,
            'knot_evidence': joins, 'ordered_boundaries': boundaries, 'ordered_physical_events': roots,
            'elementary_open_cells': cells, 'maximal_open_sign_cells': maximal, 'global_root_summary': summary,
            'coverage': 'CLOSED_SOURCE_EQUALS_ORDERED_BOUNDARY_POINTS_UNION_ALL_ELEMENTARY_OPEN_CELLS',
            'global_root_union_claimed': True, 'physical_continuity_at_every_source_knot_proved': True,
            'global_analytic_multiplicity_at_source_knots_claimed': False,
            'general_nonmonotone_solver_claimed': False, 'material_body_transition_claimed': False,
            'native_topology_claimed': False, 'source_knots_counted_as_extra_physical_roots': False,
            'historical_span_evidence_changed': False}


def build_piecewise_certificate(spec, span_proofs):
    stage = 'source-lowering'
    try:
        lowering = lower_source(spec)
        if len(lowering['spans']) < 2:
            return {'status': 'NOT_APPLICABLE', 'reason': 'ONE_SOURCE_SPAN_RETAINS_V51'}
        stage = 'span-checking'
        checked = check_spans(lowering, span_proofs)
        if checked is not True:
            return checked
        stage = 'source-knot-continuity'
        joins = build_joins(lowering, span_proofs)
        if isinstance(joins, dict):
            return joins
        stage = 'global-composition'
        return assemble(lowering, span_proofs, joins)
    except RESOURCE_ERRORS as exc:
        return refusal(stage + ':' + type(exc).__name__)


def build_piecewise_source_evidence(spec):
    """Preserve actual complete V51 outcome; new truth lives in the full-source certificate."""
    import pb00701_ordered_product_model as v51
    predecessor = None
    try:
        predecessor = v51.build_ordered_source_evidence(spec)
        if not isinstance(predecessor, dict) or predecessor.get('status') != 'ORDERED_SOURCE_EVIDENCE_CERTIFIED':
            return predecessor
        # Some historical APIs ignore named caller annotations. Do not reinterpret
        # that old disposition as canonical-source admission for a new certificate.
        if set(spec)-ALLOWED:
            return predecessor
        lowering = lower_source(spec)
        if len(lowering['spans']) < 2:
            return predecessor
        entries = predecessor['ordered_spans']
        if (not predecessor['all_source_spans_have_ordered_evidence'] or
                [x['span_index'] for x in entries] != list(range(len(lowering['spans'])))):
            return {**b.blocked('NOT_ALL_SOURCE_SPANS_HAVE_V51_PRODUCT_WITNESSES'),
                    'predecessor_result': predecessor, 'piecewise_evidence_complete': False}
        proofs = [x['ordered_evidence'] for x in entries]
        result = build_piecewise_certificate(spec, proofs)
        if result.get('status') != 'PIECEWISE_PRODUCT_CERTIFIED':
            return {**result, 'predecessor_result': predecessor, 'piecewise_evidence_complete': False}
        return {'status': 'PIECEWISE_SOURCE_EVIDENCE_CERTIFIED', 'method': RELATION,
                'predecessor_result': predecessor, 'certificate': result,
                'piecewise_evidence_complete': True,
                'unchanged_predecessor_envelope_is_not_new_truth_authority': True}
    except RESOURCE_ERRORS as exc:
        result = refusal('source:' + type(exc).__name__)
        if predecessor is not None:
            result['predecessor_result'] = predecessor
        return result
