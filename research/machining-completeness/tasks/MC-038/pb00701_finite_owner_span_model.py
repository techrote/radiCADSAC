#!/usr/bin/env python3
"""V54: finite historical-owner inventory and owner-specific ordered-span adapters.

Every reachable route_kind of the admitted PB-007-01 B-spline chain is assigned
exactly one category. Only category-2 owners receive a new view, and each view
is regenerated from the owner's OWN fixed proof recipe on the unchanged original
source span. A constant-sign amplitude theorem is a root-free SIGN_SPAN, never a
derivative or monotonicity certificate. No historical validator is patched and
no owner is relabelled. See 79-PB00701-FINITE-OWNER-COVERAGE.md.
"""
from fractions import Fraction as Q
from importlib import import_module
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_mixed_owner_span_model as v53

v52, v51, v50 = v53.v52, v53.v51, v53.v50
a, b, q, require = v53.a, v53.b, v53.q, v53.require
RESOURCE_ERRORS = v53.RESOURCE_ERRORS
SIGNS = v53.SIGNS
COMMON = v53.COMMON
RELATION = 'EXACT_CONTINUOUS_FINITE_OWNER_ROOTS_AND_SIGN_CELLS'
VIEW_SCHEMA = 'radicadsac-ordered-span-view/54.0'
SCHEMA = 'radicadsac-finite-owner-source-certificate/54.0'
V53_KINDS = ('V51_PRODUCT', 'STRICT_SPAN')
V54_KINDS = ('SIGN_SPAN', 'OWNER_STRICT_SPAN')

# Category 1: ordered views that already exist (v51 product; v53 strict v19/47/48/49).
ALREADY_ORDERED = {v51.V50_OWNER: {'version': 50, 'view_kind': 'V51_PRODUCT'},
                   **{owner: {'version': version, 'view_kind': 'STRICT_SPAN'}
                      for owner, version in v50.OWNERS.items()}}

# Category 2a: closed-span exact amplitude dominance. Root-free sign only.
SIGN_OWNER = 'EXACT_RATIONAL_AMPLITUDE_DOMINANCE'
SIGN_ADAPTERS = {SIGN_OWNER: {'version': 7, 'module': 'pb00701_coupled_bspline_model',
                              'recipe': '_dominance_certificate',
                              'adapter': 'V54_V7_AMPLITUDE_DOMINANCE_ROOT_FREE_SIGN_SPAN'}}

# Category 2b: owners whose CERTIFIED route proves a strict nonzero complete
# derivative on the whole closed span through v19._root_summary(direction, ...).
# (version, module, fixed owner recipe, certificate key carrying 'direction').
_STRICT = (
    (20, 'PB00701_V20_EXACT_POINTWISE_DERIVATIVE_ENVELOPE', 'pointwise_derivative_envelope',
     '_pointwise_envelope_route', 'derivative_certificate'),
    (21, 'PB00701_V21_EXACT_SIGN_ORTHANT_L1_DERIVATIVE_ENVELOPE', 'l1_sign_orthant_envelope',
     '_l1_envelope_route', 'derivative_certificate'),
    (22, 'PB00701_V22_EXACT_PHASE_SECTOR_PARTIAL_DERIVATIVE_ANCHOR', 'phase_sector_anchor',
     '_phase_partial_anchor_route', 'phase_anchor_certificate'),
    (23, 'PB00701_V23_EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR', 'nonconstant_phase_anchor',
     '_nonconstant_phase_anchor_route', 'nonconstant_phase_anchor_certificate'),
    (24, 'PB00701_V24_EXACT_MIXED_QUADRATURE_PHASE_ANCHOR', 'mixed_quadrature_phase_anchor',
     '_mixed_phase_anchor_route', 'mixed_phase_anchor_certificate'),
    (25, 'PB00701_V25_EXACT_COMPONENT_CONE_MIXED_PROJECTION_ANCHOR', 'component_cone_phase_anchor',
     '_component_cone_phase_anchor_route', 'component_cone_phase_anchor_certificate'),
    (26, 'PB00701_V26_EXACT_POINTWISE_COMPONENT_CONE_RESIDUAL_ORTHANTS', 'pointwise_component_cone',
     '_pointwise_component_cone_route', 'pointwise_component_cone_certificate'),
    (28, 'PB00701_V28_EXACT_ALGEBRAIC_RATIONAL_TURN_PHASE_CELL_PROJECTION', 'algebraic_phase_cell',
     '_algebraic_phase_cell_route', 'algebraic_phase_cell_certificate'),
    (29, 'PB00701_V29_EXACT_5_12_13_NESTED_ALGEBRAIC_PHASE_CELL_PROJECTION', 'pythagorean_phase_cell',
     '_phase_cell_route', 'pythagorean_phase_cell_certificate'),
    (30, 'PB00701_V30_EXACT_SOURCE_ADAPTIVE_PROJECTIVE_RATIONAL_SEPARATOR', 'source_adaptive_separator',
     '_source_adaptive_route', 'source_adaptive_projective_separator_certificate'),
    (34, 'PB00701_V34_EXACT_PHASE_CORRELATED_COMMON_FACTOR', 'phase_correlated_common_factor',
     '_phase_correlated_route', 'phase_correlated_common_factor_certificate'),
    (35, 'PB00701_V35_EXACT_PHASE_CORRELATED_PROPORTIONAL_COMMON_FACTOR',
     'phase_correlated_proportional_common_factor', '_phase_correlated_proportional_route',
     'phase_correlated_proportional_common_factor_certificate'),
    (36, 'PB00701_V36_EXACT_PHASE_CORRELATED_VARYING_RATIO_SHARED_FACTOR',
     'phase_correlated_varying_ratio_shared_factor', '_phase_correlated_varying_ratio_route',
     'phase_correlated_varying_ratio_shared_factor_certificate'),
    (37, 'PB00701_V37_EXACT_PHASE_CORRELATED_TWO_POLYNOMIAL_SHARED_FACTOR',
     'phase_correlated_two_polynomial_shared_factor', '_phase_correlated_two_polynomial_route',
     'phase_correlated_two_polynomial_shared_factor_certificate'),
    (38, 'PB00701_V38_EXACT_DIRECT_ROTATED_COORDINATE_TWO_QUADRATURE', 'direct_rotated_coordinate',
     '_phase_correlated_direct_route', 'phase_correlated_direct_rotated_coordinate_certificate'),
    (39, 'PB00701_V39_EXACT_SIGNED_A_DIRECT_ROTATED_COORDINATE', 'signed_a_direct_rotated_coordinate',
     '_phase_correlated_signed_direct_route', 'phase_correlated_signed_direct_rotated_coordinate_certificate'),
    (40, 'PB00701_V40_EXACT_SIGNED_B_ANTI_DIAGONAL_DIRECT_ROTATED_COORDINATE', 'signed_b_anti_diagonal',
     '_phase_correlated_signed_b_route', 'phase_correlated_signed_b_anti_diagonal_certificate'),
    (42, 'PB00701_V42_EXACT_ROTATED_COORDINATE_ORIENTATION_TRANSITION_BRIDGE', 'orientation_transition_bridge',
     '_transition_route', 'orientation_transition_bridge_certificate'),
    (43, 'PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF', 'correlated_closed_handoff',
     '_correlated_handoff_route', 'correlated_closed_handoff_certificate'),
)
STRICT_ADAPTERS = {owner: {'version': version, 'module': 'pb00701_' + module + '_model', 'recipe': recipe,
                           'direction_certificate': key,
                           'adapter': 'V54_V%d_WHOLE_SPAN_STRICT_DERIVATIVE' % version}
                   for version, owner, module, recipe, key in _STRICT}

# Category 3: exact owners whose actual proof object lacks a premise needed for
# an ordered physical span view. Counts/delegated zero sets are NOT order.
LACKING_PREMISE = {
    'EXACT_STATIONARY_PHASE_POLYNOMIAL': (
        7, 'POLYNOMIAL_ROOT_COUNTS_WITHOUT_ORDERED_ROOT_ISOLATION_OR_PER_ROOT_MULTIPLICITY'),
    'DELEGATED_V6_CONSTANT_MODULATION': (
        6, 'TAN_HALF_TURN_WINDOW_ROOT_COUNTS_WITHOUT_SOURCE_ORDERED_ROOTS_OR_SIGN_CELLS'),
    'PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION': (
        8, 'FACTOR_AND_TRIG_CHART_ROOT_COUNTS_WITHOUT_CROSS_FACTOR_ROOT_ORDER_OR_SIGN_CELLS'),
    'PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO': (
        9, 'PER_TANGENT_CHART_AUXILIARY_RATIO_MONOTONICITY_WITHOUT_PHYSICAL_SIGN_OR_CROSS_CHART_ORDER'),
    'PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO': (
        10, 'PER_COTANGENT_CHART_AUXILIARY_RATIO_MONOTONICITY_WITHOUT_PHYSICAL_SIGN_OR_CROSS_CHART_ORDER'),
    'PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO': (
        11, 'PER_CHART_AUXILIARY_RATIO_PHASE_DOMINANCE_WITHOUT_PHYSICAL_SIGN_OR_CROSS_CHART_ORDER'),
    'PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC': (
        12, 'PARTITION_CELL_DECISIONS_COMPOSED_BY_COUNTS_WITHOUT_ORDERED_CELL_VIEWS'),
    **{owner: (version, 'NONVANISHING_MULTIPLIER_ZERO_SET_EQUIVALENCE_OVER_V10_V11_V12_CARRIER_'
                        'WITHOUT_ORDERED_CARRIER_VIEW_OR_PHYSICAL_SIGN_TRANSFER')
       for version, owner in (
           (13, 'PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC'),
           (14, 'PB00701_V14_EXACT_STRICT_DOMINANCE_MULTITERM_MULTIPLIER'),
           (15, 'PB00701_V15_EXACT_FINITE_STRICT_DOMINANCE_MULTIPLIER'),
           (16, 'PB00701_V16_EXACT_CHEBYSHEV_STURM_MULTIPLIER'),
           (17, 'PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER'))},
    'PB00701_V18_EXACT_NONVANISHING_SOURCE_MODULE_FACTOR': (
        18, 'CLASSIFIER_DELEGATED_RESIDUAL_WITHOUT_ORDERED_RESIDUAL_VIEW'),
    'PB00701_V18_EXACT_LAURENT_MODULE_FACTOR': (
        18, 'CLASSIFIER_DELEGATED_RESIDUAL_WITHOUT_ORDERED_RESIDUAL_VIEW_OR_FACTOR_SIGN'),
    'PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION': (
        27, 'RECLASSIFIED_CHILDREN_COMPOSED_BY_COUNT_SUMMARY_WITHOUT_ORDERED_CHILD_COMPOSITION'),
    'PB00701_V41_EXACT_ROTATED_COORDINATE_ORIENTATION_ROOT_PARTITION_COMPOSITION': (
        41, 'RECLASSIFIED_CHILDREN_COMPOSED_BY_COUNT_SUMMARY_WITHOUT_ORDERED_CHILD_COMPOSITION'),
}

# Category 4: blocker / refusal / non-event dispositions; never a span view.
BLOCKED_OWNERS = {
    'PB00701_GENERAL_COUPLED_THEOREM_BOUNDARY': (7, 'GENERAL_POLYNOMIAL_TRIGONOMETRIC_ZERO_THEOREM_BOUNDARY'),
    'PB00701_V44_EXACT_REAL_ALGEBRAIC_ORIENTATION_CUT_BOUNDARY': (44, 'ALGEBRAIC_ORIENTATION_CUT_CONSUMPTION_BOUNDARY'),
}


def category(owner):
    """Exactly one category per historical owner identifier; unknown owners have none."""
    found = [n for n, table in ((1, ALREADY_ORDERED), (2, SIGN_ADAPTERS), (2, STRICT_ADAPTERS),
                                (3, LACKING_PREMISE), (4, BLOCKED_OWNERS)) if owner in table]
    require(len(found) <= 1, 'owner classified more than once')
    return found[0] if found else None


def refusal(stage):
    return {'status': 'RESOURCE_REFUSAL', 'reason': 'PB00701_V54_EXACT_RESOURCE_REFUSAL',
            'stage': stage, 'is_truth_value': False}


def _fraction_maps(material):
    return tuple({h: [q(x) for x in p] for h, p in mapping.items()} for mapping in b.maps(material))


def owner_recipe(owner):
    entry = STRICT_ADAPTERS.get(owner) or SIGN_ADAPTERS.get(owner)
    require(entry is not None, 'owner has no finite category-2 recipe')
    return getattr(import_module(entry['module']), entry['recipe'])


def regenerate_owner_route(owner, material):
    """The owner's OWN fixed recipe on the original lowered span; never a classifier."""
    c, s = _fraction_maps(material)
    if owner in SIGN_ADAPTERS:
        return owner_recipe(owner)(c, s)
    offset, rate = b.local_phase(material)
    return owner_recipe(owner)(c, s, offset, rate, material['source_parameter_id'])


def _exterior(side, point, u, relation, order, inward, source_hash, witness):
    return {'id': 'source:' + side, 'position': point.record(),
            'global_position': {'kind': 'RATIONAL', 'value': str(u)},
            'location': 'ENDPOINT', 'physical_relation': relation, 'physical_multiplicity': order,
            'event_kind': 'CROSSING' if order else 'NONZERO', 'inward_sign': inward,
            'source_binding_sha256': source_hash, **witness}


def _cell(index, left, right, sign, order, material, source_hash):
    return {'index': index, 'boundary_ids': [left['id'], right['id']],
            'parent_local_interval': [left['position'], right['position']],
            'global_source_endpoints': [left['global_position'], right['global_position']],
            'source_parameter_id': material['source_parameter_id'], 'source_binding_sha256': source_hash,
            'positive_width_proof': order, 'physical_sign': sign,
            'physical_relation': {-1: 'NEGATIVE', 1: 'POSITIVE'}[sign],
            'distinct_roots_open': 0, 'open_interval': True, 'normalized_mixed_field_map': None}


def sign_span_components(owner, route, material, *, checked_witness=False):
    """Closed-span amplitude dominance: |F| >= margin > 0 on [0,1]; no root, no direction."""
    require(owner == SIGN_OWNER, 'unsupported sign-span owner')
    if not checked_witness:
        expected = regenerate_owner_route(owner, material)
        require(expected is not None and expected.get('status') == 'CERTIFIED' and b.same(route, expected),
                'amplitude-dominance witness does not regenerate from original source span')
    c, _ = _fraction_maps(material)
    constant = a.trim(c.get(0, [Q(0)]))[0]
    sign = {'POSITIVE': 1, 'NEGATIVE': -1}[route['sign']]
    margin = q(route['margin'])
    require(margin > 0 and constant * sign > 0, 'dominance sign/margin is not the exact source constant')
    require(route['distinct_roots_open'] == 0 and route['multiple_roots_open'] == 0,
            'root-free dominance owner reports a root')
    source_hash = b.digest(material)
    lo, hi = map(q, material['parent_source_interval'])
    points = [b.Boundary.at(0), b.Boundary.at(1)]
    witness = {'sign_witness_binding_sha256': b.digest(route),
               'endpoint_relation_authority': 'CLOSED_SPAN_EXACT_AMPLITUDE_DOMINANCE',
               'closed_span_absolute_lower_bound': str(margin), 'global_jet_scale': '1'}
    exteriors = [_exterior(side, point, u, route['sign'], 0, sign, source_hash, witness)
                 for side, point, u in zip(('left', 'right'), points, (lo, hi))]
    cells = [_cell(0, exteriors[0], exteriors[1], sign, b.order_certificate(*points), material, source_hash)]
    summary = {'distinct_roots_open': 0, 'multiple_roots_open': 0, 'crossings_open': 0,
               'tangencies_open': 0, 'left_endpoint_root': False, 'right_endpoint_root': False,
               'endpoint_root_multiplicity': {}, 'total_distinct_roots_closed': 0, 'all_roots_simple': True}
    return {'ordered_boundaries': exteriors, 'ordered_physical_events': [], 'sign_cells': cells,
            'physical_root_summary': summary,
            'sign_evidence': {'owner_witness_binding_sha256': b.digest(route), 'closed_span_sign': sign,
                              'closed_span_absolute_lower_bound': str(margin),
                              'endpoint_roots_possible': False,
                              'endpoint_root_impossibility': 'MARGIN_POSITIVE_ON_CLOSED_SPAN',
                              'derivative_certificate_claimed': False, 'monotonicity_claimed': False,
                              'nonconstant_factor_claimed': False,
                              'physical_source_replaced_by_carrier': False}}


def strict_direction(owner, route):
    """Read the owner's own whole-span derivative certificate after regeneration."""
    entry = STRICT_ADAPTERS[owner]
    key = entry['direction_certificate']
    certificate = route[key]
    require(isinstance(certificate, dict) and certificate.get('status') == 'CERTIFIED',
            'owner derivative certificate missing or uncertified')
    direction = certificate['direction']
    require(direction in ('INCREASING', 'DECREASING'), 'invalid owner derivative direction')
    delta = 1 if direction == 'INCREASING' else -1
    return {'owner': owner, 'owner_version': entry['version'], 'route_binding_sha256': b.digest(route),
            'delta': delta, 'certificate_path': [key], 'certificate_binding_sha256': b.digest(certificate),
            'coordinate': 'INCREASING_ORIGINAL_NORMALIZED_PARENT',
            'consistent_strict_direction_on_complete_smooth_span': True}


def strict_adapter_components(owner, route, material, *, checked_witness=False):
    """Whole-span strict derivative owner; endpoint relations are the route's own exact events."""
    require(owner in STRICT_ADAPTERS, 'unsupported owner-specific strict adapter')
    if not checked_witness:
        expected = regenerate_owner_route(owner, material)
        if isinstance(expected, dict) and expected.get('status') == 'RESOURCE_REFUSAL':
            return expected
        require(expected is not None and expected.get('status') == 'CERTIFIED' and b.same(route, expected),
                'owner-specific strict witness does not regenerate from original source span')
    direction = strict_direction(owner, route)
    delta = direction['delta']
    endpoints = [route['left_event'], route['right_event']]
    for endpoint, u in zip(endpoints, (0, 1)):
        require(endpoint.get('status') == 'DECIDED' and endpoint['relation'] in SIGNS,
                'unresolved physical exterior')
        require(q(endpoint['source_value']) == u, 'endpoint event is not this span exterior')
    left, right = [SIGNS[x['relation']] for x in endpoints]
    signs = [left, right]
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
        witness = {'endpoint_witness_binding_sha256': b.digest(endpoint),
                   'derivative_witness_binding_sha256': b.digest(direction),
                   'global_jet_scale': str(Q(1) / width ** order)}
        exteriors.append(_exterior(side, point, u, endpoint['relation'], order, inward[i], source_hash, witness))
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
                    'existence_and_uniqueness': 'CHECKED_OWNER_WHOLE_SPAN_STRICT_DERIVATIVE_AND_EXACT_OPPOSITE_SIGNS',
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
        cells.append(_cell(i, left_point, right_point, sign, order, material, source_hash))
    return {'ordered_boundaries': boundaries,
            'ordered_physical_events': [x for x in boundaries if x['physical_relation'] == 'ZERO'],
            'sign_cells': cells, 'physical_root_summary': summary,
            'strict_evidence': {'complete_derivative': direction, 'physical_exteriors': endpoints,
                                'inward_signs': inward, 'implicit_root_descriptor': implicit,
                                'nonconstant_factor_claimed': False,
                                'physical_source_replaced_by_carrier': False}}


def regenerate_view(kind, owner, witness, *source_args, checked_witness=False):
    """Finite owner-specific view construction; the witness is always checked first."""
    material = a._material(*source_args)
    if kind == 'SIGN_SPAN':
        require(owner in SIGN_ADAPTERS, 'sign span has a forged or unsupported owner')
        components = sign_span_components(owner, witness, material, checked_witness=checked_witness)
        entry = SIGN_ADAPTERS[owner]
    else:
        require(kind == 'OWNER_STRICT_SPAN' and owner in STRICT_ADAPTERS,
                'unsupported V54 ordered span evidence kind/owner')
        components = strict_adapter_components(owner, witness, material, checked_witness=checked_witness)
        if 'ordered_boundaries' not in components:
            return components
        entry = STRICT_ADAPTERS[owner]
    lo, hi = map(q, material['parent_source_interval'])
    return {'schema': VIEW_SCHEMA, 'status': 'ORDERED_SPAN_VIEW_CERTIFIED',
            'kind': kind, 'owner': owner, 'owner_version': entry['version'],
            'adapter': entry['adapter'], 'owner_recipe': entry['module'] + '.' + entry['recipe'],
            'source_material': material, 'source_binding_sha256': b.digest(material),
            'parent_map': {'offset': str(lo), 'positive_scale': str(hi - lo)},
            'underlying_witness': witness, 'underlying_witness_binding_sha256': b.digest(witness),
            **components, 'normalized_view_alone_is_authority': False,
            'historical_owner_changed': False, 'implicit_root_arithmetic_claimed': False}


def build_ordered_span_view(kind, owner, witness, *source_args):
    try:
        if kind in V53_KINDS:
            return v53.build_ordered_span_view(kind, owner, witness, *source_args)
        return regenerate_view(kind, owner, witness, *source_args)
    except RESOURCE_ERRORS as exc:
        return refusal('span-view:' + type(exc).__name__)


def check_views(lowering, views):
    import pb00701_finite_owner_span_certificate as checker
    require(isinstance(views, list) and len(views) == len(lowering['spans']) and len(views) >= 2,
            'missing/extra source span or not a piecewise source')
    for row, view in zip(lowering['spans'], views):
        checked = checker.validate_ordered_span_view(view, *v52.source_args(row))
        if checked is not True:
            return checked
    return True


def assemble(lowering, views, joins):
    # Identical original-source knot union and maximal-cell formula (V52/V53).
    return {**v52.assemble(lowering, views, joins), 'schema': SCHEMA,
            'status': 'FINITE_OWNER_SOURCE_CERTIFIED', 'method': RELATION,
            'span_evidence_kinds': [view['kind'] for view in views],
            'span_original_owners': [view['owner'] for view in views],
            'span_owner_categories': [category(view['owner']) for view in views],
            'strict_owners_relabelled_as_product': False, 'historical_owners_relabelled': False,
            'sign_spans_claim_derivative_or_monotonicity': False}


def build_finite_owner_certificate(spec, views):
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
    return {**result, 'predecessor_result': predecessor, 'finite_owner_evidence_complete': False}


def owner_disposition(owner, span_index):
    """Category-3/4/unknown owners are reported precisely, never adapted."""
    if owner in LACKING_PREMISE:
        version, premise = LACKING_PREMISE[owner]
        return b.blocked('SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE', span_index=span_index, owner=owner,
                         owner_version=version, owner_category=3, missing_premise=premise)
    if owner in BLOCKED_OWNERS:
        version, disposition = BLOCKED_OWNERS[owner]
        return b.blocked('SPAN_OWNER_IS_BLOCKER_OR_NON_EVENT', span_index=span_index, owner=owner,
                         owner_version=version, owner_category=4, disposition=disposition)
    return b.blocked('SPAN_OWNER_OUTSIDE_FINITE_V54_INVENTORY', span_index=span_index, owner=owner)


def build_finite_owner_source_evidence(spec):
    """Complete V53 first. Only its outside-V53-owner boundary may grow."""
    predecessor = None
    stage = 'complete-predecessor'
    try:
        predecessor = v53.build_mixed_source_evidence(spec)
        if not (isinstance(predecessor, dict) and predecessor.get('status') == 'BLOCKED' and
                predecessor.get('reason') == 'SPAN_OWNER_OUTSIDE_FINITE_V53_SCOPE'):
            return predecessor
        prior = predecessor['predecessor_result']
        ordered = {}
        if prior.get('status') == 'CERTIFIED':
            physical = prior
        else:
            require(prior.get('status') == 'BLOCKED' and
                    prior.get('reason') == 'NOT_ALL_SOURCE_SPANS_HAVE_V51_PRODUCT_WITNESSES',
                    'unexpected V53 outside-owner predecessor')
            envelope = prior['predecessor_result']
            physical = envelope['physical_event_result']
            entries = envelope['ordered_spans']
            ordered = {entry['span_index']: entry for entry in entries}
            require(len(ordered) == len(entries), 'duplicated predecessor ordered span')
        stage = 'source-lowering'
        lowering = v52.lower_source(spec)
        require(physical['status'] == 'CERTIFIED' and len(physical['spans']) == len(lowering['spans']) >= 2,
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
            elif owner in SIGN_ADAPTERS:
                kind, witness = 'SIGN_SPAN', span['route']
            elif owner in STRICT_ADAPTERS:
                kind, witness = 'OWNER_STRICT_SPAN', span['route']
            else:
                return retained_failure(owner_disposition(owner, row['span_index']), predecessor)
            view = build_ordered_span_view(kind, owner, witness, *v52.source_args(row))
            if view.get('status') != 'ORDERED_SPAN_VIEW_CERTIFIED':
                return retained_failure(view, predecessor)
            views.append(view)
        stage = 'full-source-composition'
        result = build_finite_owner_certificate(spec, views)
        if result.get('status') != 'FINITE_OWNER_SOURCE_CERTIFIED':
            return retained_failure(result, predecessor)
        return {'status': 'FINITE_OWNER_SOURCE_EVIDENCE_CERTIFIED', 'method': RELATION,
                'predecessor_result': predecessor, 'certificate': result,
                'finite_owner_evidence_complete': True,
                'unchanged_predecessor_envelope_is_not_new_truth_authority': True}
    except RESOURCE_ERRORS as exc:
        result = refusal(stage + ':' + type(exc).__name__)
        return retained_failure(result, predecessor) if predecessor is not None else result
