#!/usr/bin/env python3
"""V47: complete closed-child derivative proofs and exact single-cut composition.

Lift only the pinned v42/v43 identities; keep rational source polynomials and
rational derivatives in the lowered-parent coordinate. This is not a general
multi-cut solver. Historical event/source admission always runs first.
"""
from fractions import Fraction as Q
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_algebraic_child_map_model as a
import pb00701_algebraic_interval_model as ip

q, require, engine = a.q, a.require, a.engine
RELATION = 'EXACT_ALGEBRAIC_INTERVAL_SINGLE_CUT_MONOTONE_COMPOSITION'
L, U, W, K = Q(2856, 2197), Q(99, 182), Q(99, 70), Q(44, 7)
RESOURCE_ERRORS = (MemoryError, RecursionError, OverflowError)


def resource_refusal(stage):
    return {'status': 'RESOURCE_REFUSAL', 'reason': 'PB00701_V47_EXACT_RESOURCE_REFUSAL',
            'stage': stage, 'is_truth_value': False}


def blocked(reason, **data):
    return {'status': 'BLOCKED', 'reason': reason, 'blocker': 'PB-007-01', **data}


def _maps(material):
    return tuple({int(h): a.trim(p) for h, p in material[key].items()}
                 for key in ('cos_polynomials', 'sin_polynomials'))


def _local_phase(material):
    left, right = map(q, material['parent_source_interval'])
    phase = material['phase_turn_law']
    return q(phase['offset']) + q(phase['rate']) * left, q(phase['rate']) * (right - left)


def field_from_split(split):
    f = split['field']
    return a.RealField(tuple(f['minimal_polynomial']), tuple(map(q, f['isolating_interval'])),
                       f['root_index_in_open_unit_interval'])


def residual_channels(material, harmonic, rate):
    """Every non-anchor derivative channel, source-regenerated (no C/S loss)."""
    cos, sin = _maps(material)
    terms = []
    def add(kind, h, p):
        p = a.trim(p)
        if p != [0]:
            terms.append({'kind': kind, 'harmonic': h, 'polynomial': [str(x) for x in p]})
    add('C0_prime', 0, engine.deriv(cos.get(0, [0])))
    for h in sorted((set(cos) | set(sin)) - {0, harmonic}):
        for kind, maps in (('C', cos), ('S', sin)):
            p = maps.get(h, [0])
            add(kind + '_prime', h, engine.deriv(p))
            add(kind + '_phase_upper', h, a.pscale(p, K * abs(h * rate)))
    return terms


def derivative_attempt(material, field, left, right, harmonic, mode):
    """One finite recipe. No alternate-route search: used by proof checking too."""
    require(mode in ('V42', 'V43'), 'unsupported derivative theorem')
    require(field == left.field == right.field, 'mixed derivative field/interval')
    offset, rate = _local_phase(material)
    if not rate:
        return blocked('ZERO_PHASE_PREDECESSOR_OWNERSHIP')
    cell = ip.phase_cell(left, right, offset, rate, harmonic)
    if cell['status'] != 'CERTIFIED':
        return blocked('PHASE_CELL_NOT_CONTAINED', phase_cell=cell)
    cos, sin = _maps(material)
    c, s = cos.get(harmonic, [Q(0)]), sin.get(harmonic, [Q(0)])
    if c == [0] or s == [0]:
        return blocked('TWO_SOURCE_QUADRATURES_REQUIRED')
    A = a.pscale(a.padd(c, s), Q(1, 2))
    B = a.pscale(a.padd(c, a.pscale(s, -1)), Q(1, 2))
    Ap, Bp, hr = engine.deriv(A), engine.deriv(B), harmonic * rate
    constraints = []
    def proof(p, name):
        result = ip.polynomial_certificate(p, left, right)
        constraints.append({'name': name, 'certificate': result})
        return result
    residuals = residual_channels(material, harmonic, rate)
    if mode == 'V42':
        bp = proof(Bp, 'STRICT_B_PRIME_SIGN')
        sigma = bp['weak_sign']
        if sigma not in (-1, 1) or bp.get('endpoint_signs') != [sigma, sigma]:
            return blocked('B_PRIME_NOT_STRICT', constraints=constraints)
        base = a.pscale(Bp, sigma * L)
        selected = [('A_prime_X', a.pscale(Ap, U)),
                    ('A_phase_Y_adverse', a.pscale(A, K * abs(hr) * W)),
                    ('B_phase_X', a.pscale(B, K * abs(hr) * U))]
        orientation = sigma
    else:
        pa = proof(A, 'WEAK_A_WITH_ENDPOINT_ZEROS')
        sigma = pa['weak_sign']
        if sigma not in (-1, 1):
            return blocked('A_NOT_WEAK_ONE_SIGN', constraints=constraints)
        orientation = sigma * (1 if hr > 0 else -1)
        oriented_bp = a.pscale(Bp, orientation)
        pb = proof(oriented_bp, 'WEAK_ORIENTED_B_PRIME')
        sb = pb['weak_sign']
        if sb not in (-1, 0, 1):
            return blocked('B_PRIME_NOT_WEAK_ONE_SIGN', constraints=constraints)
        base = a.padd(a.pscale(oriented_bp, L if sb >= 0 else W),
                      a.pscale(A, 6 * L * orientation * hr))
        selected = [('A_prime_X', a.pscale(Ap, U)),
                    ('B_phase_X', a.pscale(B, K * hr * U))]
    terms = [{'kind': kind, 'harmonic': harmonic, 'polynomial': [str(x) for x in p]}
             for kind, p in selected] + residuals
    # Retain zero selected channels too: the full selected derivative identity
    # is explicit, while identically zero non-anchor channels need no orthant.
    orthants = []
    for mask in range(1 << len(terms)):
        signs = [1 if (mask >> i) & 1 else -1 for i in range(len(terms))]
        margin = list(base)
        for sign, term in zip(signs, terms):
            margin = a.padd(margin, a.pscale(term['polynomial'], -sign))
        certificate = ip.polynomial_certificate(margin, left, right)
        if not certificate['strict_positive']:
            return blocked('COMPLETE_STRICT_MARGIN_NOT_CERTIFIED', mode=mode,
                           failed_orthant=mask, failed_margin=certificate,
                           constraints=constraints)
        orthants.append({'mask': mask, 'signs': signs, 'certificate': certificate})
    return {'status': 'CERTIFIED', 'method': 'V47_LIFT_' + mode,
            'harmonic': harmonic, 'mode': mode, 'phase_cell': cell,
            'source_parameter_id': material['source_parameter_id'],
            'source_binding_sha256': _digest(material),
            'interval': [left.record(), right.record()], 'field': field.record(),
            'parent_local_phase': [str(offset), str(rate)],
            'global_derivative_scale': str(Q(1) / (q(material['parent_source_interval'][1]) - q(material['parent_source_interval'][0]))),
            'coordinates': {name: [str(x) for x in p] for name, p in
                            (('C', c), ('S', s), ('A', A), ('B', B), ('A_prime', Ap), ('B_prime', Bp))},
            'identity': "F'_anchor=A'*X+B'*Y+2*pi*h*r*(A*Y-B*X)",
            'bounds': {'L': str(L), 'U': str(U), 'W': str(W), 'two_pi_lower': '6', 'two_pi_upper': str(K)},
            'orientation': orientation, 'derivative_sign': orientation * cell['diagonal_sign'],
            'constraints': constraints, 'margin_base': [str(x) for x in base],
            'orthant_terms': terms, 'retained_nonanchor_channels': residuals,
            'orthant_count': len(orthants), 'orthants': orthants}


def _digest(value):
    from hashlib import sha256
    return sha256(a._json(value).encode()).hexdigest()


def certify_derivative(material, field, left, right):
    cos, sin = _maps(material)
    attempts = []
    for h in sorted((set(cos) & set(sin)) - {0}):
        for mode in ('V42', 'V43'):
            proof = derivative_attempt(material, field, left, right, h, mode)
            if proof['status'] == 'CERTIFIED':
                return proof
            attempts.append({'harmonic': h, 'mode': mode, 'result': proof})
    return blocked('NO_COMPLETE_CLOSED_CHILD_DERIVATIVE', attempts=attempts)


def rational_endpoint(material, endpoint):
    import pb00701_multiharmonic_monotone_anchor_model as v19
    require(endpoint in (0, 1), 'external endpoint not rational parent boundary')
    cos, sin = _maps(material)
    offset, rate = _local_phase(material)
    return v19._endpoint_relation(cos, sin, Q(endpoint), offset + rate * endpoint)


def child_summary(derivative, left_event, right_event):
    if derivative.get('status') != 'CERTIFIED':
        return derivative
    for event in (left_event, right_event):
        if event.get('status') in ('RESOURCE_REFUSAL', 'SEMANTIC_BLOCKER'):
            return event
        if event.get('status') not in ('DECIDED', 'ENDPOINT_CERTIFIED'):
            return blocked('ENDPOINT_AUTHORITY_NOT_CERTIFIED')
    relation_sign = {'NEGATIVE': -1, 'ZERO': 0, 'POSITIVE': 1}
    signs = [relation_sign.get(x.get('relation')) for x in (left_event, right_event)]
    if any(x is None for x in signs):
        return blocked('ENDPOINT_RELATION_UNAVAILABLE')
    direction = derivative['derivative_sign']
    require(type(direction) is int and direction in (-1, 1), 'invalid derivative direction')
    if signs == [0, 0] or direction * (signs[1] - signs[0]) < 0:
        return {'status': 'SEMANTIC_BLOCKER', 'reason': 'ENDPOINT_MONOTONICITY_CONTRADICTION'}
    multiplicities = []
    for sign, event in zip(signs, (left_event, right_event)):
        if sign == 0:
            # Rational boundary simplicity follows from the complete strict
            # derivative. The internal v46 multiplicity is independently known.
            if event.get('physical_multiplicity', 1) != 1:
                return {'status': 'SEMANTIC_BLOCKER', 'reason': 'STRICT_DERIVATIVE_PHYSICAL_MULTIPLICITY_CONTRADICTION'}
            multiplicities.append(1)
        else:
            if event.get('physical_multiplicity', 0) != 0:
                return {'status': 'SEMANTIC_BLOCKER', 'reason': 'NONZERO_ENDPOINT_MULTIPLICITY_CONTRADICTION'}
            multiplicities.append(None)
    return {'status': 'CERTIFIED', 'relation': 'EXACT_STRICT_MONOTONE_CHILD_EVENT',
            'left_event': left_event, 'right_event': right_event,
            'left_endpoint_multiplicity': multiplicities[0], 'right_endpoint_multiplicity': multiplicities[1],
            'distinct_roots_open': int(signs[0] * signs[1] == -1),
            'multiple_roots_open': 0, 'all_roots_simple': True,
            'derivative_sign': direction}


def compose_checked_children(children):
    """Internal semantic composition only; source/proofs checked by outer layer."""
    import pb00701_phase_sector_partition_model as v27
    require(len(children) == 2, 'v47 owns exactly two children')
    for child in children:
        if child.get('summary', {}).get('status') != 'CERTIFIED':
            return child.get('summary', blocked('MISSING_CHILD_SUMMARY'))
    # F is smooth on this one lowered polynomial span. Opposite STRICT closed
    # derivative directions at the shared endpoint cannot both be true. Do not
    # impose this on historical weak/non-strict or separate-spline composition.
    if children[0]['summary']['derivative_sign'] != children[1]['summary']['derivative_sign']:
        return {'status': 'SEMANTIC_BLOCKER', 'reason': 'INCOMPATIBLE_STRICT_CLOSED_DERIVATIVES_AT_SMOOTH_CUT'}
    return v27._compose_child_summaries(children)


def _assemble(material, split, derivatives, endpoints):
    require(len(derivatives) == 2 and len(endpoints) == 3, 'single-cut cardinality mismatch')
    field = field_from_split(split)
    alpha, zero, one = field.element([0, 1]), field.element(0), field.element(1)
    children = []
    for i, (left, right) in enumerate(((zero, alpha), (alpha, one))):
        derivative = derivatives[i]
        summary = child_summary(derivative, endpoints[i], endpoints[i + 1])
        if summary['status'] != 'CERTIFIED':
            return summary
        children.append({'parent_local_interval': [left.record(), right.record()],
                         'source_parameter_id': material['source_parameter_id'],
                         'map': split['children'][i], 'derivative_certificate': derivative,
                         'summary': summary})
    composition = compose_checked_children(children)
    if composition['status'] != 'CERTIFIED':
        return composition
    return {**composition, 'relation': RELATION,
            'source_parameter_id': material['source_parameter_id'],
            'source_material': material, 'source_binding_sha256': _digest(material),
            'bisection': split, 'children': children, 'endpoint_evidence': endpoints,
            'child_count': 2, 'analytic_single_cut_consumed': True,
            'full_multi_cut_partition_claimed': False}


def build_single_cut_event(*source_args):
    """Exact lowered-source interface; returns a whole-span route only if proved."""
    try:
        import pb00701_algebraic_endpoint_model as v46
        import pb00701_algebraic_endpoint_certificate as epcheck
        representation = a.build_orientation_child_maps(*source_args)
        if representation.get('status') != 'REPRESENTATION_CERTIFIED':
            return representation
        material = representation['source_material']
        if not q(material['phase_turn_law']['rate']):
            return blocked('ZERO_PHASE_PREDECESSOR_OWNERSHIP')
        attempts = []
        for split in representation['independent_single_cut_bisections']:
            field = field_from_split(split)
            alpha, zero, one = field.element([0, 1]), field.element(0), field.element(1)
            left = certify_derivative(material, field, zero, alpha)
            if left['status'] in ('RESOURCE_REFUSAL', 'SEMANTIC_BLOCKER'):
                return left
            right = certify_derivative(material, field, alpha, one)
            if right['status'] in ('RESOURCE_REFUSAL', 'SEMANTIC_BLOCKER'):
                return right
            if left['status'] != 'CERTIFIED' or right['status'] != 'CERTIFIED':
                attempts.append({'field': field.record(), 'left': left, 'right': right})
                continue
            internal = v46._decide_endpoint(material, split)
            if internal['status'] == 'RESOURCE_REFUSAL':
                return internal
            if internal['status'] != 'ENDPOINT_CERTIFIED':
                return blocked('INTERNAL_ENDPOINT_UNRESOLVED', endpoint=internal)
            epcheck._validate_endpoint(internal, material, split)
            external = [rational_endpoint(material, i) for i in (0, 1)]
            for event in external:
                if event.get('status') == 'RESOURCE_REFUSAL':
                    return event
                if event.get('status') != 'DECIDED' or event.get('relation') not in ('NEGATIVE', 'ZERO', 'POSITIVE'):
                    return blocked('RATIONAL_ENDPOINT_UNRESOLVED', endpoint=event)
            route = _assemble(material, split, [left, right], [external[0], internal, external[1]])
            if route['status'] != 'CERTIFIED':
                return route
            return route
        return blocked('NO_QUALIFIED_ALGEBRAIC_SINGLE_CUT', attempts=attempts)
    except RESOURCE_ERRORS as exc:
        return resource_refusal(type(exc).__name__)


def classify_required_analytic_event(spec):
    import pb00701_algebraic_endpoint_model as v46
    baseline = v46.classify_required_analytic_event(spec)
    if not isinstance(baseline, dict) or baseline.get('status') != 'BLOCKED':
        return baseline
    if baseline.get('relation') != 'FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER':
        return baseline
    upgraded, changed = [], False
    for original in baseline.get('spans', []):
        span = dict(original)
        if span.get('route', {}).get('status') == 'BLOCKED' and all(k in span for k in ('cos_polynomials', 'sin_polynomials')):
            phase = baseline['phase_turn_law']
            result = build_single_cut_event(
                {int(h): p for h, p in span['cos_polynomials'].items()},
                {int(h): p for h, p in span['sin_polynomials'].items()},
                baseline['source_parameter_id'], span['source_interval'], phase['offset'], phase['rate'])
            if result.get('status') in ('CERTIFIED', 'RESOURCE_REFUSAL', 'SEMANTIC_BLOCKER'):
                span['route_kind'] = 'PB00701_V47_EXACT_ALGEBRAIC_SINGLE_CUT'
                span['route'] = result
                changed = True
        upgraded.append(span)
    if not changed:
        return baseline
    statuses = {s.get('route', {}).get('status') for s in upgraded}
    status = ('RESOURCE_REFUSAL' if 'RESOURCE_REFUSAL' in statuses else
              'SEMANTIC_BLOCKER' if 'SEMANTIC_BLOCKER' in statuses else
              'CERTIFIED' if statuses == {'CERTIFIED'} else 'BLOCKED')
    return {**baseline, 'status': status, 'spans': upgraded,
            'relation': 'FINITE_EXACT_PIECEWISE_ALGEBRAIC_SINGLE_CUT_EVENT_DECISION' if status == 'CERTIFIED' else baseline['relation'],
            'blocker': None if status == 'CERTIFIED' else 'PB-007-01',
            'v47_algebraic_single_cut_extension': True,
            **({'is_truth_value': False} if status == 'RESOURCE_REFUSAL' else {})}
