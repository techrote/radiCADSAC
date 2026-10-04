#!/usr/bin/env python3
"""V51 ordered evidence for checked V50 products, not a replacement event owner.

A factor-owned nonzero theorem precedes sign refinement. Strict carrier signs
order its unique implicit root; exact product jets and multiplicity parity give
sign cells. No arithmetic between unrelated fields or numerical root is used.
"""
from fractions import Fraction as Q
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_vanishing_source_factor_model as v50
import pb00701_algebraic_endpoint_certificate as epcheck

a, b, e = v50.a, v50.b, v50.v46
E, q, require = a.engine, a.q, a.require
RESOURCE_ERRORS = v50.RESOURCE_ERRORS
RELATION = 'EXACT_ORDERED_V50_PRODUCT_ROOTS_AND_SIGN_CELLS'
SIGN_METHOD = 'SOURCE_FACTOR_OWNED_ALGEBRAIC_CARRIER_SIGN'
V50_OWNER = 'PB00701_V50_VANISHING_SOURCE_FACTOR'
SIGNS = {'NEGATIVE': -1, 'ZERO': 0, 'POSITIVE': 1}
COUNT_FIELDS = ('distinct_roots_open', 'multiple_roots_open', 'crossings_open',
                'tangencies_open', 'left_endpoint_root', 'right_endpoint_root',
                'endpoint_root_multiplicity', 'total_distinct_roots_closed',
                'all_roots_simple')


def refusal(stage):
    return {'status': 'RESOURCE_REFUSAL', 'reason': 'PB00701_V51_EXACT_RESOURCE_REFUSAL',
            'stage': stage, 'is_truth_value': False}


def _factorization(source_args):
    result = v50.factor_source(*source_args)
    require(result['status'] == 'FACTORIZATION_CERTIFIED', 'V51 needs a nonconstant source factor')
    return result


def _sign_context(factorization, certificate):
    """Finite source/GCD/field/phase regeneration; never invent H orientation."""
    endpoint = v50.irrational_factor_event(factorization, certificate)
    require(endpoint['status'] == 'FACTOR_ENDPOINT_CERTIFIED'
            and endpoint['carrier_relation'] == 'NONZERO', 'no proved carrier nonvanishing')
    field = a.RealField.from_source_certificate(factorization['monic_factor'], certificate)
    carrier = factorization['carrier_material']
    jets, values = e.algebraic_jets(field, *v50.maps(carrier))
    require(b.same(jets, endpoint['carrier_jets']) and jets['physical_multiplicity'] == 0,
            'source-factor carrier jet mismatch')
    offset, rate = b.local_phase(carrier)
    header = {'status': 'FACTOR_CARRIER_SIGN_CERTIFIED', 'method': SIGN_METHOD,
              'source_binding_sha256': factorization['source_binding_sha256'],
              'carrier_binding_sha256': factorization['carrier_binding_sha256'],
              'factor_endpoint_evidence': endpoint, 'nonzero_proved_before_refinement': True,
              'carrier_orientation_ownership_invented': False, 'whole_span_certified': False}
    return header, field, values, offset, rate


def _decide_factor_sign(factorization, certificate):
    header, field, values, offset, rate = _sign_context(factorization, certificate)
    n = 1
    while True:
        proof = e.sign_enclosure(field, values, offset, rate, n)
        relation = e._separated(proof)
        if relation is not None:
            return {**header, 'relation': relation, 'sign_certificate': proof}
        n *= 2  # Convergence and the PREVIOUSLY PROVED nonzero branch terminate.


def build_factor_carrier_sign(certificate, *source_args):
    """Endpoint-only exact source interface; never qualifies an unchecked carrier."""
    try:
        return _decide_factor_sign(_factorization(source_args), certificate)
    except RESOURCE_ERRORS as exc:
        return refusal('factor-sign:' + type(exc).__name__)


def _check_factor_sign(candidate, factorization, certificate):
    header, field, values, offset, rate = _sign_context(factorization, certificate)
    proof = candidate['sign_certificate']
    epcheck._audit_series(proof)  # Independent direct sums and analytic remainders.
    regenerated = e.sign_enclosure(field, values, offset, rate, proof['precision'])
    require(b.same(proof, regenerated), 'carrier sign isolation/phase/amplitude/remainder mismatch')
    relation = e._separated(regenerated)
    require(relation is not None, 'carrier sign witness does not strictly exclude zero')
    require(b.same(candidate, {**header, 'relation': relation, 'sign_certificate': regenerated}),
            'factor-owned carrier sign/source/nonzero binding mismatch')
    return True


def carrier_direction(carrier):
    """Called only after V50 owner-specific checking of the complete carrier."""
    owner, route = carrier['owner'], carrier['route']
    require(owner in v50.OWNERS, 'unknown strict carrier owner')
    version = v50.OWNERS[owner]
    if version == 19:
        derivative = route['derivative_certificate']
        require(derivative['direction'] in ('INCREASING', 'DECREASING'), 'invalid V19 direction')
        delta = 1 if derivative['direction'] == 'INCREASING' else -1
        witnesses = [{'path': ['derivative_certificate'], 'sign': delta,
                      'binding_sha256': b.digest(derivative)}]
    else:
        children = route['children']
        require(len(children) == 2 if version in (47, 48) else len(children) >= 3,
                'owner-specific strict carrier coverage mismatch')
        witnesses = []
        for i, child in enumerate(children):
            derivative = child['derivative_certificate']
            delta = derivative['derivative_sign']
            require(type(delta) is int and delta in (-1, 1)
                    and type(child['summary']['derivative_sign']) is int
                    and child['summary']['derivative_sign'] == delta,
                    'strict carrier derivative/summary mismatch')
            witnesses.append({'path': ['children', i, 'derivative_certificate'], 'sign': delta,
                              'binding_sha256': b.digest(derivative)})
        require(len({x['sign'] for x in witnesses}) == 1, 'inconsistent closed-child directions')
        delta = witnesses[0]['sign']
    require(route['distinct_roots_open'] + len(route['endpoint_root_multiplicity']) <= 1,
            'strict carrier cannot have two closed roots')
    return {'owner': owner, 'route_binding_sha256': b.digest(route), 'delta': delta,
            'closed_derivative_witnesses': witnesses,
            'coordinate': 'INCREASING_ORIGINAL_NORMALIZED_PARENT',
            'consistent_strict_direction_on_complete_smooth_span': True}


def _factor_point(factorization, event):
    record = event['source_cut']
    if record['kind'] == 'RATIONAL':
        point = b.Boundary.at(record['value'])
    else:
        require(record['kind'] == 'ALGEBRAIC_IRRATIONAL', 'invalid factor position')
        cert = event['algebraic_disjointness_evidence']['factor_root_certificate']
        point = b.Boundary.from_source(factorization['monic_factor'], cert)
    require(b.same(point.record(), record), 'factor position has a different source embedding')
    return point


def _sign_row(index, event, proof=None):
    if event['source_cut']['kind'] == 'RATIONAL':
        require(proof is None, 'rational coincidence cannot use an irrational sign proof')
        relation = event['carrier_endpoint_evidence']['relation']
        method = 'V50_EXACT_RATIONAL_TURN_COINCIDENCE'
    else:
        require(proof is not None and proof['relation'] in ('NEGATIVE', 'POSITIVE'),
                'irrational factor needs a nonzero carrier sign')
        relation, method = proof['relation'], SIGN_METHOD
    sign = SIGNS[relation]
    require(event['carrier_multiplicity'] == int(sign == 0), 'factor/carrier coincidence mismatch')
    return {'factor_event_index': index, 'factor_event_binding_sha256': b.digest(event),
            'source_cut': event['source_cut'], 'method': method, 'relation': relation,
            'sign': sign, 'sign_evidence': proof}


def _factor_signs(product):
    factorization = product['factorization']
    result = []
    for i, event in enumerate(product['factor_root_evidence']['factor_events']):
        proof = None
        if event['source_cut']['kind'] == 'ALGEBRAIC_IRRATIONAL':
            certificate = event['algebraic_disjointness_evidence']['factor_root_certificate']
            proof = _decide_factor_sign(factorization, certificate)
        result.append(_sign_row(i, event, proof))
    return result


def _inward_exteriors(product, delta):
    factorization = product['factorization']
    g = factorization['monic_factor']
    lo, hi = map(q, factorization['source_material']['parent_source_interval'])
    result = []
    for t, side, inward, row in zip((0, 1), ('left', 'right'), ('right', 'left'),
                                  product['physical_exterior_evidence']['endpoints']):
        require(row['side'] == side, 'exterior order mismatch')
        jet = b.side_jet(g, b.Boundary.at(t), inward)
        require(jet['order'] == row['factor_multiplicity'] and jet['sign'] in (-1, 1),
                'unproved factor inward jet')
        value_sign = SIGNS[row['carrier_event']['relation']]
        hsign = value_sign if value_sign else delta * (1 if t == 0 else -1)
        require(row['carrier_multiplicity'] == int(value_sign == 0), 'carrier exterior jet mismatch')
        result.append({'side': side, 'inward_direction': inward, 'factor_jet': jet,
                       'global_factor_derivative_scale': str(Q(1) / (hi - lo) ** jet['order']),
                       'carrier_inward_sign': hsign,
                       'carrier_jet_order': row['carrier_multiplicity'],
                       'carrier_sign_method': ('EXACT_NONZERO_ENDPOINT' if value_sign else
                                               'CHECKED_STRICT_DERIVATIVE_AND_INWARD_DIRECTION'),
                       'physical_inward_sign': jet['sign'] * hsign,
                       'physical_multiplicity': row['physical_multiplicity'],
                       'exterior_evidence_binding_sha256': b.digest(row)})
    return result


def _assemble_ordered(product, signs):
    """Internal composition: outer interfaces check product and each finite sign."""
    fac, carrier = product['factorization'], product['carrier_evidence']
    material = fac['source_material']
    direction = carrier_direction(carrier)
    delta = direction['delta']
    factor_events = product['factor_root_evidence']['factor_events']
    require(len(signs) == len(factor_events), 'missing or extra factor sign')
    points = [_factor_point(fac, event) for event in factor_events]
    global_lo, global_hi = map(q, material['parent_source_interval'])
    source_hash = b.digest(material)

    def node(ident, point, gm, hm, index, location, hsign):
        mult = gm + hm
        return {'id': ident, 'position': point.record(),
                'global_position': b.value_record(point.affine(global_lo, global_hi - global_lo)),
                'location': location, 'factor_event_index': index,
                'factor_multiplicity': gm, 'carrier_multiplicity': hm,
                'physical_multiplicity': mult,
                'physical_relation': ('ZERO' if mult else
                                      {-1: 'NEGATIVE', 1: 'POSITIVE'}[b.value_sign(point.evaluate(fac['monic_factor'])) * hsign]),
                'event_kind': 'NONZERO' if not mult else 'CROSSING' if mult % 2 else 'TANGENCY',
                'coincidence_counted_once': gm > 0 and hm > 0,
                'carrier_value_sign': hsign, 'source_binding_sha256': source_hash}

    interior, runtime = [], {}
    for i, (event, point, sign) in enumerate(zip(factor_events, points, signs)):
        require(type(sign['sign']) is int and sign['sign'] in (-1, 0, 1), 'invalid carrier sign')
        if event['location'] == 'OPEN':
            ident = 'factor:' + str(i)
            interior.append(node(ident, point, event['factor_multiplicity'],
                                 event['carrier_multiplicity'], i, 'OPEN', sign['sign']))
            runtime[ident] = point
    exteriors = []
    for t, side, row in zip((0, 1), ('left', 'right'), product['physical_exterior_evidence']['endpoints']):
        point = b.Boundary.at(t)
        indices = [i for i, p in enumerate(points) if b.same(p.record(), point.record())]
        require(len(indices) <= 1, 'duplicated exterior factor root')
        hsign = SIGNS[row['carrier_event']['relation']]
        if indices:
            require(signs[indices[0]]['sign'] == hsign, 'factor/exterior carrier sign contradiction')
        ident = 'source:' + side
        exteriors.append(node(ident, point, row['factor_multiplicity'], row['carrier_multiplicity'],
                              indices[0] if indices else None, 'ENDPOINT', hsign))
        runtime[ident] = point

    carrier_open = carrier['route']['distinct_roots_open']
    implicit = None
    ordering = {'carrier_open_roots': carrier_open, 'direction': direction,
                'factor_comparisons': [], 'carrier_root_boundary_id': None,
                'implicit_root_descriptor': None}
    if carrier_open:
        comparisons = [delta * row['sign'] for row in signs]
        require(comparisons == sorted(comparisons), 'carrier signs contradict exact factor order')
        ordering['factor_comparisons'] = [
            {'factor_event_index': i, 'sign_evidence_binding_sha256': b.digest(row),
             'comparison_to_carrier_root': comparison,
             'rule': 'sign(delta*H(x))=sign(x-rho)'}
            for i, (row, comparison) in enumerate(zip(signs, comparisons))]
        coincident = [row for row in interior if row['carrier_value_sign'] == 0]
        require(len(coincident) <= 1, 'more than one carrier coincidence')
        if coincident:
            root = coincident[0]
            require(root['position']['kind'] == 'RATIONAL', 'irrational carrier coincidence is excluded')
            require(product['carrier_root_correspondence']['carrier_only_open_roots'] == 0,
                    'v50 carrier coincidence correspondence mismatch')
            ordering['carrier_root_boundary_id'] = root['id']
        else:
            require(product['carrier_root_correspondence']['carrier_only_open_roots'] == 1,
                    'v50 carrier-only root correspondence mismatch')
            insertion = sum(delta * row['carrier_value_sign'] < 0 for row in interior)
            finite = [exteriors[0], *interior, exteriors[1]]
            left, right = finite[insertion], finite[insertion + 1]
            require([delta * x['carrier_value_sign'] for x in (left, right)] == [-1, 1],
                    'implicit carrier root is not strictly bracketed')
            bracket_order = b.order_certificate(runtime[left['id']], runtime[right['id']])
            require(bracket_order['comparison'] == -1, 'implicit carrier bracket reversed')
            implicit = {'kind': 'UNIQUE_ANALYTIC_ROOT', 'id': 'carrier:open',
                        'coordinate': 'ORIGINAL_NORMALIZED_PARENT',
                        'carrier_binding_sha256': fac['carrier_binding_sha256'],
                        'physical_source_binding_sha256': source_hash,
                        'carrier_witness_binding_sha256': b.digest(carrier['route']),
                        'strict_derivative_sign': delta,
                        'defining_interval': [left['position'], right['position']],
                        'defining_boundary_ids': [left['id'], right['id']],
                        'carrier_endpoint_signs': [left['carrier_value_sign'], right['carrier_value_sign']],
                        'positive_width_proof': bracket_order,
                        'existence_and_uniqueness': 'CHECKED_STRICT_CARRIER_AND_EXACT_OPPOSITE_SIGNS',
                        'factor_roots_in_defining_open_interval': 0,
                        'algebraic_minimal_polynomial': None, 'arithmetic_nature': 'UNCLAIMED'}
            root = {'id': 'carrier:open', 'position': implicit,
                    'global_position': {'kind': 'AFFINE_ANALYTIC_ROOT_IMAGE',
                                        'local_root_binding_sha256': b.digest(implicit),
                                        'offset': str(global_lo), 'positive_scale': str(global_hi - global_lo)},
                    'location': 'OPEN', 'factor_event_index': None, 'factor_multiplicity': 0,
                    'carrier_multiplicity': 1, 'physical_multiplicity': 1, 'physical_relation': 'ZERO', 'event_kind': 'CROSSING',
                    'coincidence_counted_once': False, 'carrier_value_sign': 0,
                    'source_binding_sha256': source_hash}
            interior.insert(insertion, root)
            ordering['carrier_root_boundary_id'] = 'carrier:open'
            ordering['implicit_root_descriptor'] = implicit
    else:
        require(all(row['carrier_multiplicity'] == 0 for row in interior),
                'interior coincidence without an open carrier root')

    boundaries = [exteriors[0], *interior, exteriors[1]]
    inward = _inward_exteriors(product, delta)
    if not carrier_open:
        hsign = inward[0]['carrier_inward_sign']
        require(hsign == inward[1]['carrier_inward_sign']
                and all(row['carrier_value_sign'] == hsign for row in interior),
                'root-free carrier signs contradict complete carrier authority')
    current = inward[0]['physical_inward_sign']
    cells = []
    for i, (left, right) in enumerate(zip(boundaries, boundaries[1:])):
        if left['id'] in runtime and right['id'] in runtime:
            order = b.order_certificate(runtime[left['id']], runtime[right['id']])
            require(order['comparison'] == -1, 'ordered physical boundary pair is not increasing')
        else:
            require(implicit is not None, 'unproved analytic boundary')
            finite = left if left['id'] in runtime else right
            comparison = delta * finite['carrier_value_sign']
            require(comparison == (-1 if finite is left else 1), 'analytic/finite boundary order mismatch')
            order = {'method': 'CHECKED_STRICT_CARRIER_SIGN_ORDER', 'comparison': -1,
                     'boundary_ids': [left['id'], right['id']],
                     'finite_boundary_id': finite['id'], 'finite_carrier_sign': finite['carrier_value_sign'],
                     'finite_comparison_to_carrier_root': comparison,
                     'implicit_descriptor_binding_sha256': b.digest(implicit)}
        cells.append({'index': i, 'boundary_ids': [left['id'], right['id']],
                      'parent_local_interval': [left['position'], right['position']],
                      'global_source_endpoints': [left['global_position'], right['global_position']],
                      'source_parameter_id': material['source_parameter_id'],
                      'source_binding_sha256': source_hash, 'positive_width_proof': order,
                      'physical_sign': current, 'physical_relation': {-1: 'NEGATIVE', 1: 'POSITIVE'}[current],
                      'distinct_roots_open': 0, 'open_interval': True, 'normalized_mixed_field_map': None})
        if i < len(interior):
            interior[i]['adjacent_cell_signs'] = [current, current * (-1) ** interior[i]['physical_multiplicity']]
            current = interior[i]['adjacent_cell_signs'][1]
    require(current == inward[1]['physical_inward_sign'], 'physical parity contradicts right inward jet')
    exteriors[0]['inward_sign'], exteriors[1]['inward_sign'] = inward[0]['physical_inward_sign'], current
    physical_events = [row for row in boundaries if row['physical_multiplicity'] > 0]
    endpoint_mult = {side: row['physical_multiplicity'] for side, row in zip(('left', 'right'), exteriors)
                     if row['physical_multiplicity'] > 0}
    summary = {'distinct_roots_open': len(interior),
               'multiple_roots_open': sum(x['physical_multiplicity'] > 1 for x in interior),
               'crossings_open': sum(x['event_kind'] == 'CROSSING' for x in interior),
               'tangencies_open': sum(x['event_kind'] == 'TANGENCY' for x in interior),
               'left_endpoint_root': 'left' in endpoint_mult, 'right_endpoint_root': 'right' in endpoint_mult,
               'endpoint_root_multiplicity': endpoint_mult, 'total_distinct_roots_closed': len(physical_events),
               'all_roots_simple': all(x['physical_multiplicity'] == 1 for x in physical_events)}
    require(b.same(summary, {key: product[key] for key in COUNT_FIELDS}), 'ordered roots changed v50 counts')
    return {'status': 'ORDERED_PRODUCT_CERTIFIED', 'method': RELATION,
            'source_material': material, 'source_binding_sha256': source_hash,
            'physical_event_result': product, 'physical_event_binding_sha256': b.digest(product),
            'factor_carrier_signs': signs, 'carrier_ordering': ordering, 'exterior_inward_evidence': inward,
            'ordered_boundaries': boundaries, 'ordered_physical_events': physical_events, 'sign_cells': cells,
            'physical_root_summary': summary,
            'coverage': 'EXACT_ORIGINAL_PARENT_OPEN_CELLS_PLUS_ORDERED_BOUNDARY_POINTS',
            'ordering_claim_scope': 'THIS_CHECKED_V50_PRODUCT_ON_ONE_LOWERED_SPAN',
            'ordered_full_product_root_list_claimed': True,
            'physical_product_strict_monotonicity_claimed': False,
            'general_nonmonotone_solver_claimed': False, 'material_body_transition_claimed': False,
            'native_topology_claimed': False, 'cross_spline_span_continuity_claimed': False,
            'compositum_claimed': False, 'proof_cuts_counted_as_extra_physical_roots': False}


def build_ordered_product_event(product, *source_args):
    """Augment a supplied V50 construction, after checking it against original F."""
    import pb00701_vanishing_source_factor_certificate as product_check
    stage = 'product'
    try:
        checked = product_check.validate_product_event(product, *source_args)
        if checked is not True:
            return checked
        stage = 'factor-signs'
        signs = _factor_signs(product)
        stage = 'ordered-composition'
        return _assemble_ordered(product, signs)
    except RESOURCE_ERRORS as exc:
        return refusal(stage + ':' + type(exc).__name__)


def build_ordered_source_evidence(spec):
    """Complete V50 first; preserve its result/owners and separate source spans.

Older successes/rejections are returned unchanged. Only V50-owned certified
spans receive additional evidence. This wrapper does not claim global source-
knot continuity; the finite truth interface checks each original lowered span.
    """
    baseline = None
    try:
        baseline = v50.classify_required_analytic_event(spec)
        if not isinstance(baseline, dict) or baseline.get('status') != 'CERTIFIED':
            return baseline
        selected = [(i, span) for i, span in enumerate(baseline.get('spans', []))
                    if span.get('route_kind') == V50_OWNER]
        if not selected:
            return baseline
        evidence = []
        for i, span in selected:
            phase = baseline['phase_turn_law']
            source_args = ({int(h): p for h, p in span['cos_polynomials'].items()},
                           {int(h): p for h, p in span['sin_polynomials'].items()},
                           baseline['source_parameter_id'], span['source_interval'], phase['offset'], phase['rate'])
            ordered = build_ordered_product_event(span['route'], *source_args)
            if ordered.get('status') != 'ORDERED_PRODUCT_CERTIFIED':
                return {**ordered, 'physical_event_result': baseline, 'failed_span_index': i,
                        'ordered_evidence_complete': False}
            evidence.append({'span_index': i, 'source_interval': span['source_interval'],
                             'physical_owner': span['route_kind'], 'ordered_evidence': ordered})
        return {'status': 'ORDERED_SOURCE_EVIDENCE_CERTIFIED', 'method': RELATION,
                'source_spec_binding_sha256': b.digest(spec), 'physical_event_result': baseline,
                'ordered_spans': evidence, 'all_source_spans_have_ordered_evidence': len(selected) == len(baseline['spans']),
                'cross_spline_span_continuity_claimed': False, 'global_cross_span_root_union_claimed': False}
    except RESOURCE_ERRORS as exc:
        result = refusal('source:' + type(exc).__name__)
        if baseline is not None:
            result['physical_event_result'] = baseline
        return result
