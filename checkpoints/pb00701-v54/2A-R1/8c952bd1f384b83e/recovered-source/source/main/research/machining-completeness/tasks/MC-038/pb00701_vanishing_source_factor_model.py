#!/usr/bin/env python3
"""V50: physical product roots, never a strict-derivative claim for the product.

F=gH is regenerated from every amplitude; g is the maximal monic Q[t] GCD.
The carrier is delegated to fixed predecessor authority. Rational coincidences
are evaluated exactly; irrational disjointness uses coprime amplitude values
and the scoped v46 Laurent theorem. See 74-PB00701-VANISHING-FACTOR.md.
"""
from fractions import Fraction as Q
from functools import cmp_to_key
from math import comb
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_algebraic_child_map_model as a
import pb00701_mixed_boundary_model as b
import pb00701_algebraic_endpoint_model as v46

E, q, require = a.engine, a.q, a.require
RELATION = 'EXACT_VANISHING_SOURCE_FACTOR_WITH_CHECKED_SIMPLE_CARRIER'
RESOURCE_ERRORS = (MemoryError, OverflowError, RecursionError)
OWNERS = {
    'PB00701_V19_EXACT_MULTI_HARMONIC_MONOTONE_ANCHOR': 19,
    'PB00701_V47_EXACT_ALGEBRAIC_SINGLE_CUT': 47,
    'PB00701_V48_MIXED_ROOT_SINGLE_CUT': 48,
    'PB00701_V49_MIXED_BOUNDARY_MULTICUT': 49,
}


def refusal(stage):
    return {'status': 'RESOURCE_REFUSAL', 'reason': 'PB00701_V50_EXACT_RESOURCE_REFUSAL',
            'stage': stage, 'is_truth_value': False}


def blocked(reason, **data):
    return {'status': 'BLOCKED', 'reason': reason, 'blocker': 'PB-007-01', **data}


def maps(material):
    return tuple({int(h): a.trim(p) for h, p in material[key].items()}
                 for key in ('cos_polynomials', 'sin_polynomials'))


def args(material):
    c, s = maps(material)
    return (c, s, material['source_parameter_id'], material['parent_source_interval'],
            material['phase_turn_law']['offset'], material['phase_turn_law']['rate'])


def amplitude_gcd(cos, sin):
    factor = [Q(0)]
    for source in (cos, sin):
        for h in sorted(source):
            p = a.trim(source[h])
            if p != [0]:
                factor = E.pgcd(factor, p)
    return factor


def factor_source(*source_args):
    """Only proof workspace division; every original physical channel is retained."""
    material = a._material(*source_args)
    c, s = maps(material)
    g = amplitude_gcd(c, s)
    if g == [0]:
        return blocked('DEGENERATE_IDENTITY_ZERO')
    if E.degree(g) <= 0:
        return {'status': 'NOT_APPLICABLE', 'reason': 'CONSTANT_AMPLITUDE_GCD'}
    quotients, identities = [], []
    for kind, source in (('COS', c), ('SIN', s)):
        quotient_map = {}
        for h, p in sorted(source.items()):
            quotient, remainder = E.pdivmod(p, g)
            require(remainder == [0] and a.pmul(g, quotient) == p, 'physical factor reconstruction failed')
            if quotient != [0]:
                quotient_map[h] = quotient
            identities.append({'kind': kind, 'harmonic': h, 'source': [str(x) for x in p],
                               'quotient': [str(x) for x in quotient], 'remainder': ['0'],
                               'regenerated': [str(x) for x in a.pmul(g, quotient)]})
        quotients.append(quotient_map)
    require(amplitude_gcd(*quotients) == [1], 'maximal source GCD did not leave coprime amplitudes')
    carrier = a._material(*quotients, *source_args[2:])
    return {'status': 'FACTORIZATION_CERTIFIED', 'source_material': material,
            'source_binding_sha256': b.digest(material), 'monic_factor': [str(x) for x in g],
            'carrier_material': carrier, 'carrier_binding_sha256': b.digest(carrier),
            'quotient_amplitude_gcd': ['1'], 'channel_identities': identities,
            'physical_source_replaced_by_carrier': False}


def source_spec(material):
    """Exact power-to-clamped-Bernstein source adapter, not a competing DSP/geometry engine."""
    lo, hi = material['parent_source_interval']
    def spline(poly):
        p = a.trim(poly)
        n = len(p) - 1
        controls = [str(sum((p[k] * Q(comb(j, k), comb(n, k))
                             for k in range(j + 1)), Q(0))) for j in range(n + 1)]
        return {'degree': n, 'knots': [lo] * (n + 1) + [hi] * (n + 1), 'controls': controls}
    return {'grammar': 'RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE',
            'source_parameter_id': material['source_parameter_id'],
            'parameter_lo': lo, 'parameter_hi': hi,
            'phase_turn_offset': material['phase_turn_law']['offset'],
            'phase_turn_rate': material['phase_turn_law']['rate'],
            'cos_splines': {h: spline(p) for h, p in material['cos_polynomials'].items()},
            'sin_splines': {h: spline(p) for h, p in material['sin_polynomials'].items()}}


def carrier_proof(material):
    """One fixed-predecessor delegation; never recursive v50 carrier search."""
    import pb00701_mixed_multicut_model as v49
    result = v49.classify_required_analytic_event(source_spec(material))
    if result.get('status') in ('RESOURCE_REFUSAL', 'SEMANTIC_BLOCKER'):
        return result
    if result.get('status') != 'CERTIFIED':
        return blocked('CARRIER_NOT_CERTIFIED', predecessor_result=result)
    spans = result.get('spans', [])
    if len(spans) != 1 or spans[0].get('route_kind') not in OWNERS:
        return blocked('CARRIER_OWNER_NOT_IN_FINITE_STRICT_CHECKER_SCOPE',
                       predecessor_relation=result.get('relation'),
                       owners=[s.get('route_kind') for s in spans])
    span = spans[0]
    require(list(span['source_interval']) == list(material['parent_source_interval']), 'carrier source interval drift')
    proof = {'status': 'CARRIER_CERTIFIED', 'owner': span['route_kind'], 'route': span['route'],
             'source_material': material, 'source_binding_sha256': b.digest(material)}
    checked = validate_carrier(proof, material)
    return proof if checked is True else checked


def validate_carrier(proof, material):
    """Finite owner-specific checking; never call the predecessor classifier here."""
    require(proof.get('status') == 'CARRIER_CERTIFIED', 'carrier not certified')
    require(b.same(proof['source_material'], material), 'carrier physical source mismatch')
    require(proof['source_binding_sha256'] == b.digest(material), 'carrier binding mismatch')
    owner, route = proof['owner'], proof['route']
    require(owner in OWNERS, 'unsupported or forged carrier owner')
    if OWNERS[owner] == 49:
        import pb00701_mixed_multicut_certificate as checker
        checked = checker.validate_multicut_event(route, *args(material))
    elif OWNERS[owner] == 48:
        import pb00701_mixed_orientation_consumer as checker
        checked = checker.validate_single_cut_event(route, *args(material))
    elif OWNERS[owner] == 47:
        import pb00701_algebraic_monotone_cut_certificate as checker
        checked = checker.validate_single_cut_event(route, *args(material))
    else:
        import pb00701_multiharmonic_monotone_anchor_model as v19
        c, s = maps(material)
        offset, rate = b.local_phase(material)
        expected = v19._monotone_anchor_route(c, s, offset, rate, material['source_parameter_id'])
        if isinstance(expected, dict) and expected.get('status') == 'RESOURCE_REFUSAL':
            return expected
        require(expected is not None and expected.get('status') == 'CERTIFIED' and b.same(route, expected),
                'carrier v19 finite derivative/endpoint witness mismatch')
        checked = True
    if checked is not True:
        return checked
    require(route.get('all_roots_simple') is True and route.get('multiple_roots_open') == 0,
            'carrier multiplicity is not independently simple')
    n = route['distinct_roots_open']
    require(type(n) is int and n in (0, 1), 'strict carrier open-root count invalid')
    require(all(type(m) is int and m == 1 for m in route['endpoint_root_multiplicity'].values()),
            'unsupported carrier endpoint multiplicity')
    require(b.same(proof, {'status': 'CARRIER_CERTIFIED', 'owner': owner, 'route': route,
                          'source_material': material, 'source_binding_sha256': b.digest(material)}),
            'unknown carrier authority metadata')
    return True


def rational_event(material, t):
    import pb00701_multiharmonic_monotone_anchor_model as v19
    c, s = maps(material)
    offset, rate = b.local_phase(material)
    return v19._endpoint_relation(c, s, q(t), offset + rate * q(t))


def irrational_factor_event(factorization, certificate):
    """Source-bound factor-root interface; no invented quotient orientation owner."""
    g = a.trim(factorization['monic_factor'])
    field = a.RealField.from_source_certificate(g, certificate)
    physical, carrier = factorization['source_material'], factorization['carrier_material']
    c, s = maps(carrier)
    require(amplitude_gcd(c, s) == [1], 'carrier amplitudes are not coprime')
    offset, rate = b.local_phase(physical)
    require(rate != 0, 'rational phase cannot enter irrational disjointness theorem')
    tau = field.element(offset) + field.element([0, 1]) * rate
    require(len(tau.coefficients) > 1, 'phase exponent is not algebraic irrational')
    carrier_jets, _ = v46.algebraic_jets(field, c, s)
    require(carrier_jets['status'] == 'ALGEBRAIC_JETS_CERTIFIED'
            and carrier_jets['physical_multiplicity'] == 0 and carrier_jets['endpoint_laurent'],
            'coprime quotient contradicted by algebraic amplitude vanishing')
    physical_jets, _ = v46.algebraic_jets(field, *maps(physical))
    m = certificate['multiplicity']
    require(type(m) is int and m > 0 and physical_jets['physical_multiplicity'] == m,
            'physical product jet multiplicity mismatch')
    lo, hi = map(q, physical['parent_source_interval'])
    return {'status': 'FACTOR_ENDPOINT_CERTIFIED', 'source_binding_sha256': b.digest(physical),
            'factorization_binding_sha256': b.digest(factorization), 'factor_root_certificate': certificate,
            'field': field.record(), 'source_parameter_id': physical['source_parameter_id'],
            'global_source_cut': (field.element(lo) + field.element([0, 1]) * (hi - lo)).record(),
            'phase_turn': tau.record(), 'carrier_relation': 'NONZERO', 'physical_relation': 'ZERO',
            'physical_multiplicity': m, 'carrier_jets': carrier_jets, 'physical_jets': physical_jets,
            'global_jet_scale': str(Q(1) / (hi - lo) ** m),
            'disjointness': {'theorem': 'GELFOND_SCHNEIDER_NIVEN_10_1_AND_V46_LAURENT',
                            'base': '-1', 'exponent': (tau * 2).record(), 'chosen_logarithm': 'i*pi',
                            'quotient_amplitude_gcd': ['1'], 'coefficient_field': 'Q(alpha,i)',
                            'nonzero_collected_laurent': True},
            'carrier_orientation_ownership_invented': False, 'trigonometric_sign_search_used': False}


def factor_root_events(factorization):
    import pb00701_mixed_orientation_roots_model as roots
    g = a.trim(factorization['monic_factor'])
    root_proof = roots.exact_orientation_roots(g, 'COMMON_SOURCE_FACTOR')
    if root_proof['status'] != 'CERTIFIED':
        return root_proof
    material, carrier = factorization['source_material'], factorization['carrier_material']
    records = []
    for location, key in (('ENDPOINT', 'endpoint_roots'), ('OPEN', 'rational_open_roots')):
        for root in root_proof[key]:
            t, m = q(root['source']), root['multiplicity']
            event = rational_event(carrier, t)
            if event.get('status') in ('RESOURCE_REFUSAL', 'SEMANTIC_BLOCKER'):
                return event
            require(event.get('status') == 'DECIDED' and event.get('relation') in ('NEGATIVE', 'ZERO', 'POSITIVE'),
                    'rational carrier coincidence undecided')
            records.append((b.Boundary.at(t), {'location': location, 'factor_multiplicity': m,
                             'carrier_multiplicity': int(event['relation'] == 'ZERO'),
                             'carrier_endpoint_evidence': event}))
    for certificate in root_proof['irrational_open_roots']:
        event = irrational_factor_event(factorization, certificate)
        if event.get('status') in ('RESOURCE_REFUSAL', 'SEMANTIC_BLOCKER'):
            return event
        point = b.Boundary.from_source(g, certificate)
        records.append((point, {'location': 'OPEN', 'factor_multiplicity': certificate['multiplicity'],
                               'carrier_multiplicity': 0, 'algebraic_disjointness_evidence': event}))
    records.sort(key=cmp_to_key(lambda x, y: b.order_certificate(x[0], y[0])['comparison']))
    ordering = [b.order_certificate(x[0], y[0]) for x, y in zip(records, records[1:])]
    require(all(o['comparison'] == -1 for o in ordering), 'factor root order or duplication failure')
    output = []
    lo, hi = map(q, material['parent_source_interval'])
    for point, record in records:
        m = record['factor_multiplicity'] + record['carrier_multiplicity']
        output.append({**record, 'source_cut': point.record(),
                       'global_source_cut': b.value_record(point.affine(lo, hi - lo)),
                       'physical_multiplicity': m, 'relation': 'ZERO',
                       'event_kind': 'CROSSING' if m % 2 else 'TANGENCY',
                       'coincidence_counted_once': record['carrier_multiplicity'] == 1})
    require(len(output) == root_proof['distinct_roots_closed'], 'factor enumeration count mismatch')
    return {'status': 'FACTOR_ROOTS_CERTIFIED', 'root_certificate': root_proof,
            'factor_events': output, 'exact_factor_root_order': ordering}


def physical_exteriors(factorization, carrier):
    g = a.trim(factorization['monic_factor'])
    out = []
    for t, side in ((Q(0), 'left'), (Q(1), 'right')):
        he = rational_event(factorization['carrier_material'], t)
        fe = rational_event(factorization['source_material'], t)
        for ev in (he, fe):
            if ev.get('status') in ('RESOURCE_REFUSAL', 'SEMANTIC_BLOCKER'):
                return ev
            require(ev.get('status') == 'DECIDED' and ev['relation'] in ('NEGATIVE', 'ZERO', 'POSITIVE'),
                    'physical exterior unresolved')
        hm = int(he['relation'] == 'ZERO')
        require(carrier['route']['endpoint_root_multiplicity'].get(side, 0) == hm,
                'carrier external equality contradicts checked route')
        gm = E.multiplicity_at(g, t)
        require(type(gm) is int and gm >= 0, 'invalid factor endpoint multiplicity')
        sign = E.sign(E.peval(g, t)) * {'NEGATIVE': -1, 'ZERO': 0, 'POSITIVE': 1}[he['relation']]
        require(fe['relation'] == {-1: 'NEGATIVE', 0: 'ZERO', 1: 'POSITIVE'}[sign],
                'physical sign does not equal factor times carrier')
        out.append({'side': side, 'source_value': str(t), 'factor_value': str(E.peval(g, t)),
                    'factor_multiplicity': gm, 'carrier_multiplicity': hm,
                    'physical_multiplicity': gm + hm,
                    'event_kind': ('NONZERO' if gm + hm == 0 else 'CROSSING' if (gm + hm) % 2 else 'TANGENCY'),
                    'carrier_event': he, 'physical_event': fe})
    return {'status': 'EXTERIORS_CERTIFIED', 'endpoints': out}


def assemble_product(factorization, carrier, factor_events, exteriors):
    """Exact set union after all input proofs are checked by the outer interface."""
    require(factorization['status'] == 'FACTORIZATION_CERTIFIED' and carrier['status'] == 'CARRIER_CERTIFIED',
            'incomplete product inputs')
    require(factor_events['status'] == 'FACTOR_ROOTS_CERTIFIED' and exteriors['status'] == 'EXTERIORS_CERTIFIED',
            'incomplete root or exterior proof')
    events = factor_events['factor_events']
    interior = [x for x in events if x['location'] == 'OPEN']
    coincidences = [x for x in interior if x['carrier_multiplicity'] == 1]
    carrier_open = carrier['route']['distinct_roots_open']
    require(len(coincidences) <= carrier_open, 'coincidences exceed independently counted carrier roots')
    count = len(interior) + carrier_open - len(coincidences)
    multiple = sum(x['physical_multiplicity'] > 1 for x in interior)
    tangencies = sum(x['physical_multiplicity'] % 2 == 0 for x in interior)
    endpoint_mult = {x['side']: x['physical_multiplicity'] for x in exteriors['endpoints'] if x['physical_multiplicity']}
    for row in events:
        if row['location'] == 'ENDPOINT':
            side = 'left' if row['source_cut'] == b.Boundary.at(0).record() else 'right'
            require(endpoint_mult.get(side) == row['physical_multiplicity'], 'endpoint union multiplicity mismatch')
    correspondence = {'carrier_owner': carrier['owner'],
                      'carrier_open_roots': carrier_open,
                      'rational_open_coincidences': len(coincidences),
                      'carrier_only_open_roots': carrier_open - len(coincidences),
                      'carrier_only_multiplicity': 1,
                      'carrier_witness_binding_sha256': b.digest(carrier['route']),
                      'coincident_factor_event_indices': [i for i, e in enumerate(events) if e in coincidences]}
    return {'status': 'CERTIFIED', 'relation': RELATION,
            'source_parameter_id': factorization['source_material']['source_parameter_id'],
            'source_binding_sha256': factorization['source_binding_sha256'],
            'factorization': factorization, 'carrier_evidence': carrier,
            'factor_root_evidence': factor_events, 'physical_exterior_evidence': exteriors,
            'distinct_roots_open': count, 'multiple_roots_open': multiple,
            'crossings_open': count - tangencies, 'tangencies_open': tangencies,
            'left_endpoint_root': 'left' in endpoint_mult, 'right_endpoint_root': 'right' in endpoint_mult,
            'endpoint_root_multiplicity': endpoint_mult,
            'total_distinct_roots_closed': count + len(endpoint_mult),
            'all_roots_simple': multiple == 0 and all(m == 1 for m in endpoint_mult.values()),
            'carrier_root_correspondence': correspondence,
            'multiplicity_rule': 'ord(F)=ord(g)+ord(H); root sets unioned with rational coincidences once',
            'physical_product_strict_monotonicity_claimed': False,
            'ordered_full_analytic_root_list_claimed': False,
            'proof_cuts_counted_as_extra_physical_roots': False,
            'general_nonmonotone_solver_claimed': False}


def build_product_event(*source_args):
    stage = 'factorization'
    try:
        factorization = factor_source(*source_args)
        if factorization['status'] != 'FACTORIZATION_CERTIFIED':
            return factorization
        offset, rate = b.local_phase(factorization['source_material'])
        if not rate:
            return blocked('ZERO_PHASE_PREDECESSOR_OWNERSHIP')
        stage = 'carrier'
        carrier = carrier_proof(factorization['carrier_material'])
        if carrier['status'] != 'CARRIER_CERTIFIED':
            return carrier
        stage = 'factor-roots'
        factor_events = factor_root_events(factorization)
        if factor_events['status'] != 'FACTOR_ROOTS_CERTIFIED':
            return factor_events
        stage = 'physical-exteriors'
        exteriors = physical_exteriors(factorization, carrier)
        if exteriors['status'] != 'EXTERIORS_CERTIFIED':
            return exteriors
        stage = 'physical-composition'
        return assemble_product(factorization, carrier, factor_events, exteriors)
    except RESOURCE_ERRORS as exc:
        return refusal(stage + ':' + type(exc).__name__)


def classify_required_analytic_event(spec):
    import pb00701_mixed_multicut_model as v49
    try:
        baseline = v49.classify_required_analytic_event(spec)
        if not isinstance(baseline, dict) or baseline.get('status') != 'BLOCKED':
            return baseline
        if baseline.get('relation') != 'FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER':
            return baseline
        spans, changed = [], False
        for original in baseline.get('spans', []):
            span = dict(original)
            if span.get('route', {}).get('status') == 'BLOCKED' and all(k in span for k in ('cos_polynomials', 'sin_polynomials')):
                phase = baseline['phase_turn_law']
                result = build_product_event(
                    {int(h): p for h, p in span['cos_polynomials'].items()},
                    {int(h): p for h, p in span['sin_polynomials'].items()},
                    baseline['source_parameter_id'], span['source_interval'], phase['offset'], phase['rate'])
                if result.get('status') in ('CERTIFIED', 'RESOURCE_REFUSAL', 'SEMANTIC_BLOCKER'):
                    span['route_kind'], span['route'] = 'PB00701_V50_VANISHING_SOURCE_FACTOR', result
                    changed = True
            spans.append(span)
        if not changed:
            return baseline
        statuses = {s.get('route', {}).get('status') for s in spans}
        status = ('RESOURCE_REFUSAL' if 'RESOURCE_REFUSAL' in statuses else
                  'SEMANTIC_BLOCKER' if 'SEMANTIC_BLOCKER' in statuses else
                  'CERTIFIED' if statuses == {'CERTIFIED'} else 'BLOCKED')
        return {**baseline, 'status': status, 'spans': spans,
                'relation': 'FINITE_EXACT_PIECEWISE_VANISHING_FACTOR_EVENT_DECISION' if status == 'CERTIFIED' else baseline['relation'],
                'blocker': None if status == 'CERTIFIED' else 'PB-007-01',
                'v50_vanishing_source_factor_extension': True,
                **({'is_truth_value': False} if status == 'RESOURCE_REFUSAL' else {})}
    except RESOURCE_ERRORS as exc:
        return refusal('source:' + type(exc).__name__)
