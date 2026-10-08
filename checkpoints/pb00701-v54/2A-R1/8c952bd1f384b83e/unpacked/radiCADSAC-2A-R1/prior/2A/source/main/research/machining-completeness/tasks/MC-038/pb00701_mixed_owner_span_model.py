#!/usr/bin/env python3
"""V53: checked STRICT_SPAN / V51_PRODUCT views over unchanged original source.

The legacy carrier checker is reused solely as its finite strict-owner router.
Its temporary argument is NOT a factorization or a claim of V50 ownership.
No historical validator is patched, and no implicit root gets a guessed type.
"""
from fractions import Fraction as Q
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_piecewise_product_model as v52
import pb00701_ordered_product_model as v51
import pb00701_ordered_product_certificate as product_check

v50 = v51.v50
a, b, q, require = v52.a, v52.b, v52.q, v52.require
RESOURCE_ERRORS = v52.RESOURCE_ERRORS
RELATION = 'EXACT_CONTINUOUS_MIXED_OWNER_ROOTS_AND_SIGN_CELLS'
VIEW_SCHEMA = 'radicadsac-ordered-span-view/53.0'
SCHEMA = 'radicadsac-mixed-owner-source-certificate/53.0'
SIGNS = v52.SIGNS
COMMON = ('ordered_boundaries', 'ordered_physical_events', 'sign_cells', 'physical_root_summary')


def refusal(stage):
    return {'status': 'RESOURCE_REFUSAL', 'reason': 'PB00701_V53_EXACT_RESOURCE_REFUSAL',
            'stage': stage, 'is_truth_value': False}


def strict_components(owner, route, material):
    """Regenerate one smooth span from its supplied complete historical proof."""
    require(owner in v50.OWNERS, 'unsupported strict owner')
    owner_argument = {'status': 'CARRIER_CERTIFIED', 'owner': owner, 'route': route,
                      'source_material': material, 'source_binding_sha256': b.digest(material)}
    checked = v50.validate_carrier(owner_argument, material)
    if checked is not True:
        return checked
    direction = v51.carrier_direction(owner_argument)
    delta = direction['delta']
    endpoints = [v50.rational_event(material, t) for t in (Q(0), Q(1))]
    for endpoint in endpoints:
        if endpoint.get('status') != 'DECIDED':
            return endpoint
        require(endpoint['relation'] in SIGNS, 'unresolved physical exterior')
    signs = [SIGNS[x['relation']] for x in endpoints]
    left, right = signs
    require(delta * left <= delta * right and not (left == right == 0),
            'endpoints contradict complete strict derivative')
    opened = left * right < 0
    inward = [left if left else delta, right if right else -delta]
    require(opened or inward[0] == inward[1], 'root-free strict span changes sign')
    multiplicities = {side: 1 for side, sign in zip(('left', 'right'), signs) if sign == 0}
    summary = {'distinct_roots_open': int(opened), 'multiple_roots_open': 0,
               'crossings_open': int(opened), 'tangencies_open': 0,
               'left_endpoint_root': left == 0, 'right_endpoint_root': right == 0,
               'endpoint_root_multiplicity': multiplicities,
               'total_distinct_roots_closed': int(opened) + len(multiplicities),
               'all_roots_simple': True}
    # Some old owners omit crossing/tangency fields. They are derived above,
    # never used as a substitute for checking the complete derivative witness.
    for key, value in summary.items():
        if key in route:
            require(b.same(route[key], value), 'strict root summary disagrees with original owner')
    source_hash = b.digest(material)
    lo, hi = map(q, material['parent_source_interval'])
    width = hi - lo
    points = [b.Boundary.at(0), b.Boundary.at(1)]
    exteriors = []
    for i, (side, point, u, endpoint) in enumerate(zip(('left', 'right'), points, (lo, hi), endpoints)):
        order = int(signs[i] == 0)
        exteriors.append({'id': 'source:' + side, 'position': point.record(),
                          'global_position': {'kind': 'RATIONAL', 'value': str(u)},
                          'location': 'ENDPOINT', 'physical_relation': endpoint['relation'],
                          'physical_multiplicity': order,
                          'event_kind': 'CROSSING' if order else 'NONZERO',
                          'inward_sign': inward[i], 'source_binding_sha256': source_hash,
                          'endpoint_witness_binding_sha256': b.digest(endpoint),
                          'derivative_witness_binding_sha256': b.digest(direction),
                          'global_jet_scale': str(Q(1) / width ** order)})
    implicit = None
    interior = []
    if opened:
        require(signs == [-delta, delta], 'opposite signs are inconsistent with strict direction')
        implicit = {'kind': 'UNIQUE_ANALYTIC_ROOT', 'id': 'strict:open',
                    'coordinate': 'ORIGINAL_NORMALIZED_PARENT', 'owner': owner,
                    'source_parameter_id': material['source_parameter_id'],
                    'physical_source_binding_sha256': source_hash,
                    'owner_witness_binding_sha256': b.digest(route),
                    'strict_derivative_binding_sha256': b.digest(direction),
                    'strict_derivative_sign': delta,
                    'defining_interval': [x.record() for x in points],
                    'defining_boundary_ids': [x['id'] for x in exteriors],
                    'endpoint_signs': signs,
                    'endpoint_witness_bindings_sha256': [b.digest(x) for x in endpoints],
                    'positive_width_proof': b.order_certificate(*points),
                    'existence_and_uniqueness': 'CHECKED_COMPLETE_STRICT_DERIVATIVE_AND_EXACT_OPPOSITE_SIGNS',
                    'physical_multiplicity': 1, 'algebraic_minimal_polynomial': None,
                    'arithmetic_nature': 'UNCLAIMED'}
        interior.append({'id': 'strict:open', 'position': implicit,
                         'global_position': {'kind': 'AFFINE_ANALYTIC_ROOT_IMAGE',
                                             'local_root_binding_sha256': b.digest(implicit),
                                             'offset': str(lo), 'positive_scale': str(width)},
                         'location': 'OPEN', 'physical_relation': 'ZERO', 'physical_multiplicity': 1,
                         'event_kind': 'CROSSING', 'adjacent_cell_signs': [-delta, delta],
                         'source_binding_sha256': source_hash})
    boundaries = [exteriors[0], *interior, exteriors[1]]
    cells = []
    for i, (left_point, right_point) in enumerate(zip(boundaries, boundaries[1:])):
        sign = inward[i] if opened else inward[0]
        order = (b.order_certificate(*points) if not opened else
                 {'method': 'CHECKED_STRICT_ENDPOINT_SIGN_ORDER', 'comparison': -1,
                  'boundary_ids': [left_point['id'], right_point['id']],
                  'implicit_descriptor_binding_sha256': b.digest(implicit),
                  'finite_endpoint_sign': signs[i], 'strict_derivative_sign': delta})
        cells.append({'index': i, 'boundary_ids': [left_point['id'], right_point['id']],
                      'parent_local_interval': [left_point['position'], right_point['position']],
                      'global_source_endpoints': [left_point['global_position'], right_point['global_position']],
                      'source_parameter_id': material['source_parameter_id'], 'source_binding_sha256': source_hash,
                      'positive_width_proof': order, 'physical_sign': sign,
                      'physical_relation': {-1: 'NEGATIVE', 1: 'POSITIVE'}[sign],
                      'distinct_roots_open': 0, 'open_interval': True, 'normalized_mixed_field_map': None})
    return {'ordered_boundaries': boundaries,
            'ordered_physical_events': [x for x in boundaries if x['physical_relation'] == 'ZERO'],
            'sign_cells': cells, 'physical_root_summary': summary,
            'strict_evidence': {'complete_derivative': direction, 'physical_exteriors': endpoints,
                                'inward_signs': inward, 'implicit_root_descriptor': implicit,
                                'nonconstant_factor_claimed': False,
                                'physical_source_replaced_by_carrier': False}}


def regenerate_view(kind, owner, witness, *source_args):
    """Finite normalized view construction; the witness is always checked first."""
    material = a._material(*source_args)
    if kind == 'V51_PRODUCT':
        require(owner == v51.V50_OWNER, 'product view has a forged physical owner')
        checked = product_check.validate_ordered_product_event(witness, *source_args)
        if checked is not True:
            return checked
        components = {key: witness[key] for key in COMMON}
        components['strict_evidence'] = None
    else:
        require(kind == 'STRICT_SPAN' and owner in v50.OWNERS, 'unsupported ordered span evidence kind/owner')
        components = strict_components(owner, witness, material)
        if 'ordered_boundaries' not in components:
            return components
    lo, hi = map(q, material['parent_source_interval'])
    return {'schema': VIEW_SCHEMA, 'status': 'ORDERED_SPAN_VIEW_CERTIFIED',
            'kind': kind, 'owner': owner, 'source_material': material,
            'source_binding_sha256': b.digest(material),
            'parent_map': {'offset': str(lo), 'positive_scale': str(hi - lo)},
            'underlying_witness': witness, 'underlying_witness_binding_sha256': b.digest(witness),
            **components, 'normalized_view_alone_is_authority': False,
            'historical_owner_changed': False, 'implicit_root_arithmetic_claimed': False}


def build_ordered_span_view(kind, owner, witness, *source_args):
    try:
        return regenerate_view(kind, owner, witness, *source_args)
    except RESOURCE_ERRORS as exc:
        return refusal('span-view:' + type(exc).__name__)


def check_views(lowering, views):
    import pb00701_mixed_owner_span_certificate as checker
    require(isinstance(views, list) and len(views) == len(lowering['spans']) and len(views) >= 2,
            'missing/extra source span or not a piecewise source')
    for row, view in zip(lowering['spans'], views):
        checked = checker.validate_ordered_span_view(view, *v52.source_args(row))
        if checked is not True:
            return checked
    return True


def assemble(lowering, views, joins):
    # Reuse the identical original-source knot union and maximal-cell formula.
    # The separately versioned wrapper changes no historical theorem or artifact.
    return {**v52.assemble(lowering, views, joins), 'schema': SCHEMA,
            'status': 'MIXED_OWNER_SOURCE_CERTIFIED', 'method': RELATION,
            'span_evidence_kinds': [view['kind'] for view in views],
            'span_original_owners': [view['owner'] for view in views],
            'strict_owners_relabelled_as_product': False}


def build_mixed_certificate(spec, views):
    stage = 'source-lowering'
    try:
        lowering = v52.lower_source(spec)
        if len(lowering['spans']) < 2:
            return {'status': 'NOT_APPLICABLE', 'reason': 'ONE_SOURCE_SPAN_RETAINS_PREDECESSOR'}
        stage = 'span-checking'
        checked = check_views(lowering, views)
        if checked is not True:
            return checked
        stage = 'source-knot-continuity'
        joins = v52.build_joins(lowering, views)
        if isinstance(joins, dict):
            return joins
        stage = 'global-composition'
        return assemble(lowering, views, joins)
    except RESOURCE_ERRORS as exc:
        return refusal(stage + ':' + type(exc).__name__)


def retained_failure(result, predecessor):
    return {**result, 'predecessor_result': predecessor, 'mixed_owner_evidence_complete': False}


def build_mixed_source_evidence(spec):
    """Complete V52 first. Only its missing-view boundary or all-strict success grows."""
    predecessor = None
    stage = 'complete-predecessor'
    try:
        predecessor = v52.build_piecewise_source_evidence(spec)
        if not isinstance(predecessor, dict):
            return predecessor
        ordered = {}
        if predecessor.get('status') == 'CERTIFIED':
            physical = predecessor
        elif (predecessor.get('status') == 'BLOCKED' and
              predecessor.get('reason') == 'NOT_ALL_SOURCE_SPANS_HAVE_V51_PRODUCT_WITNESSES'):
            envelope = predecessor['predecessor_result']
            physical = envelope['physical_event_result']
            entries = envelope['ordered_spans']
            ordered = {entry['span_index']: entry for entry in entries}
            require(len(ordered) == len(entries), 'duplicated predecessor ordered span')
        else:
            return predecessor
        # Preserve historical handling of ignored annotations and other grammars.
        if (not isinstance(spec, dict) or spec.get('grammar') != v52.GRAMMAR or set(spec) - v52.ALLOWED):
            return predecessor
        stage = 'source-lowering'
        lowering = v52.lower_source(spec)
        if len(lowering['spans']) < 2:
            return predecessor
        require(physical['status'] == 'CERTIFIED' and len(physical['spans']) == len(lowering['spans']),
                'predecessor does not cover every original source span')
        require(physical['source_parameter_id'] == lowering['source_parameter_id'] and
                physical['phase_turn_law']['shared_parameter'] == lowering['source_parameter_id'] and
                all(q(physical['phase_turn_law'][key]) == q(lowering['phase_turn_law'][key])
                    for key in ('offset', 'rate')), 'predecessor source/phase drift')
        views = []
        for row, span in zip(lowering['spans'], physical['spans']):
            stage = 'span-view:' + str(row['span_index'])
            material = a._material({int(h): p for h, p in span['cos_polynomials'].items()},
                                   {int(h): p for h, p in span['sin_polynomials'].items()},
                                   physical['source_parameter_id'], span['source_interval'],
                                   physical['phase_turn_law']['offset'], physical['phase_turn_law']['rate'])
            require(b.same(material, row['material']), 'predecessor span differs from original source lowering')
            owner = span['route_kind']
            if owner == v51.V50_OWNER:
                entry = ordered.get(row['span_index'])
                if entry is None:
                    return retained_failure(b.blocked('PRODUCT_SPAN_WITHOUT_CHECKED_V51_VIEW'), predecessor)
                require(entry['physical_owner'] == owner and
                        b.same(entry['source_interval'], row['source_interval']) and
                        b.same(entry['ordered_evidence']['physical_event_result'], span['route']),
                        'substituted predecessor product route')
                kind, witness = 'V51_PRODUCT', entry['ordered_evidence']
            elif owner in v50.OWNERS:
                kind, witness = 'STRICT_SPAN', span['route']
            else:
                return retained_failure(b.blocked('SPAN_OWNER_OUTSIDE_FINITE_V53_SCOPE',
                                                 span_index=row['span_index'], owner=owner), predecessor)
            view = build_ordered_span_view(kind, owner, witness, *v52.source_args(row))
            if view.get('status') != 'ORDERED_SPAN_VIEW_CERTIFIED':
                return retained_failure(view, predecessor)
            views.append(view)
        stage = 'full-source-composition'
        result = build_mixed_certificate(spec, views)
        if result.get('status') != 'MIXED_OWNER_SOURCE_CERTIFIED':
            return retained_failure(result, predecessor)
        return {'status': 'MIXED_OWNER_SOURCE_EVIDENCE_CERTIFIED', 'method': RELATION,
                'predecessor_result': predecessor, 'certificate': result,
                'mixed_owner_evidence_complete': True,
                'unchanged_predecessor_envelope_is_not_new_truth_authority': True}
    except RESOURCE_ERRORS as exc:
        result = refusal(stage + ':' + type(exc).__name__)
        return retained_failure(result, predecessor) if predecessor is not None else result
