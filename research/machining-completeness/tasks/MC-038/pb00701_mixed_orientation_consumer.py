#!/usr/bin/env python3
"""V48 source adapter. No global monkeypatch and no new derivative theorem."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_mixed_orientation_roots_model as roots
import pb00701_algebraic_monotone_cut_model as prior
import pb00701_algebraic_endpoint_model as endpoint
import pb00701_algebraic_endpoint_certificate as epcheck

LEGACY_ROOT_ERRORS = frozenset((
    'Sturm open interval endpoint is an exact root',
    'multiplicity interval is not source-root unique',
))
RELATION = 'EXACT_SINGLE_CUT_EVENT_WITH_REPAIRED_MIXED_ROOT_PRODUCER'


def _finish(material, split, derivatives, endpoints, root_certificate):
    event = prior._assemble(material, split, derivatives, endpoints)
    if event['status'] != 'CERTIFIED':
        return event
    return {**event, 'relation': RELATION, 'root_producer_version': 48,
            'mixed_root_certificate': root_certificate}


def build_single_cut_event(*source_args):
    try:
        rep = roots.build_child_maps(*source_args)
        if rep['status'] != 'REPRESENTATION_CERTIFIED':
            return rep
        material = rep['source_material']
        if not roots.q(material['phase_turn_law']['rate']):
            return prior.blocked('ZERO_PHASE_PREDECESSOR_OWNERSHIP')
        attempts = []
        for split in rep['independent_single_cut_bisections']:
            field = prior.field_from_split(split)
            zero, alpha, one = field.element(0), field.element([0, 1]), field.element(1)
            derivatives = []
            for lo, hi in ((zero, alpha), (alpha, one)):
                cert = prior.certify_derivative(material, field, lo, hi)
                if cert['status'] in ('RESOURCE_REFUSAL', 'SEMANTIC_BLOCKER'):
                    return cert
                derivatives.append(cert)
            if any(d['status'] != 'CERTIFIED' for d in derivatives):
                attempts.append({'field': field.record(), 'derivatives': derivatives})
                continue
            internal = endpoint._decide_endpoint(material, split)
            if internal['status'] != 'ENDPOINT_CERTIFIED':
                return internal
            epcheck._validate_endpoint(internal, material, split)
            exteriors = [prior.rational_endpoint(material, i) for i in (0, 1)]
            for event in exteriors:
                if event.get('status') in ('RESOURCE_REFUSAL', 'SEMANTIC_BLOCKER'):
                    return event
                if event.get('status') != 'DECIDED':
                    return prior.blocked('RATIONAL_ENDPOINT_UNRESOLVED')
            return _finish(material, split, derivatives, [exteriors[0], internal, exteriors[1]], rep['root_certificate'])
        return prior.blocked('NO_QUALIFIED_MIXED_ROOT_SINGLE_CUT', attempts=attempts)
    except roots.RESOURCE_ERRORS as exc:
        return roots.refusal('event:' + type(exc).__name__)


def validate_single_cut_event(candidate, *source_args):
    """Regenerate source/cuts plus finite witness-specified old theorem recipes."""
    try:
        rep = roots.build_child_maps(*source_args)
        if rep['status'] == 'RESOURCE_REFUSAL':
            return rep
        roots.require(rep['status'] == 'REPRESENTATION_CERTIFIED', 'source has no algebraic representation')
        material = rep['source_material']
        roots.require(prior.ip.same(candidate['mixed_root_certificate'], rep['root_certificate']), 'root accounting/source corruption')
        splits = [s for s in rep['independent_single_cut_bisections'] if prior.ip.same(s, candidate['bisection'])]
        roots.require(len(splits) == 1, 'forged mixed-root bisection')
        split = splits[0]
        field = prior.field_from_split(split)
        zero, alpha, one = field.element(0), field.element([0, 1]), field.element(1)
        children, derivatives = candidate['children'], []
        roots.require(len(children) == 2, 'invalid child count')
        for child, (lo, hi) in zip(children, ((zero, alpha), (alpha, one))):
            proof = child['derivative_certificate']
            expected = prior.derivative_attempt(material, field, lo, hi, proof['harmonic'], proof['mode'])
            roots.require(expected['status'] == 'CERTIFIED' and prior.ip.same(expected, proof), 'invalid derivative witness')
            derivatives.append(expected)
        endpoints = candidate['endpoint_evidence']
        roots.require(len(endpoints) == 3, 'invalid endpoint count')
        epcheck._validate_endpoint(endpoints[1], material, split)
        for i, j in ((0, 0), (2, 1)):
            expected = prior.rational_endpoint(material, j)
            if expected.get('status') == 'RESOURCE_REFUSAL':
                return expected
            roots.require(prior.ip.same(expected, endpoints[i]), 'external endpoint corruption')
        expected = _finish(material, split, derivatives, endpoints, rep['root_certificate'])
        roots.require(expected['status'] == 'CERTIFIED' and prior.ip.same(expected, candidate), 'source/map/physical composition mismatch')
        return True
    except roots.RESOURCE_ERRORS as exc:
        return roots.refusal('checker:' + type(exc).__name__)


def classify_required_analytic_event(spec):
    try:
        legacy_failure = None
        try:
            baseline = prior.classify_required_analytic_event(spec)
        except ValueError as exc:
            if str(exc) not in LEGACY_ROOT_ERRORS:
                raise
            # The message only selects a recovery path. Independent complete
            # historical validation/lowering, not that message, admits source.
            legacy_failure = str(exc)
            baseline = roots.old.v41.classify_required_analytic_event(spec)
        if not isinstance(baseline, dict) or baseline.get('status') != 'BLOCKED':
            return baseline
        if baseline.get('relation') != 'FINITE_EXACT_PIECEWISE_LOWERING_WITH_RESIDUAL_COUPLED_THEOREM_BLOCKER':
            return baseline
        spans, changed = [], False
        for old_span in baseline.get('spans', []):
            span = dict(old_span)
            if span.get('route', {}).get('status') == 'BLOCKED' and all(k in span for k in ('cos_polynomials', 'sin_polynomials')):
                phase = baseline['phase_turn_law']
                result = build_single_cut_event(
                    {int(h): p for h, p in span['cos_polynomials'].items()},
                    {int(h): p for h, p in span['sin_polynomials'].items()},
                    baseline['source_parameter_id'], span['source_interval'], phase['offset'], phase['rate'])
                if result.get('status') in ('CERTIFIED', 'RESOURCE_REFUSAL', 'SEMANTIC_BLOCKER'):
                    span['route_kind'], span['route'] = 'PB00701_V48_MIXED_ROOT_SINGLE_CUT', result
                    changed = True
            spans.append(span)
        if not changed:
            return {**baseline, 'legacy_root_failure': legacy_failure} if legacy_failure else baseline
        statuses = {s.get('route', {}).get('status') for s in spans}
        status = ('RESOURCE_REFUSAL' if 'RESOURCE_REFUSAL' in statuses else
                  'SEMANTIC_BLOCKER' if 'SEMANTIC_BLOCKER' in statuses else
                  'CERTIFIED' if statuses == {'CERTIFIED'} else 'BLOCKED')
        return {**baseline, 'status': status, 'spans': spans,
                'relation': 'FINITE_EXACT_PIECEWISE_MIXED_ROOT_SINGLE_CUT_EVENT_DECISION' if status == 'CERTIFIED' else baseline['relation'],
                'blocker': None if status == 'CERTIFIED' else 'PB-007-01',
                'v48_mixed_root_extension': True,
                **({'legacy_root_failure': legacy_failure} if legacy_failure else {}),
                **({'is_truth_value': False} if status == 'RESOURCE_REFUSAL' else {})}
    except roots.RESOURCE_ERRORS as exc:
        return roots.refusal('source:' + type(exc).__name__)
