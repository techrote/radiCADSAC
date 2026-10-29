#!/usr/bin/env python3
"""Research-only exact composition of verified stationary cardinal polynomial spans.

Consumes the exact original-source stationary owner views from pinned v54/#281.
Synthetic polynomial controls exercise knot handling independently of source
authority. No trigonometric, count-only, or production acceptance follows.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
STATIONARY_PATH = HERE / 'verify_pb00701_stationary_polynomial_order.py'
CORPUS = HERE / 'pb00701-finite-owner-corpus-v54.json'
DOMAIN = ROOT / 'research/machining-completeness/tasks/MC-002/domain-contract-v1.json'
AUTH = ROOT / 'handoffs/current-authority.json'
STATIONARY_BLOB = '0954c5e1ad63ec1c8dd2acb3202882650b02c516'
CORPUS_BLOB = '5841c331579489b25caef38cd412bdbf286f9134'
AUTH_BLOB = 'fa0233323a0804d8a5d3eb7cd892a274a6173fab'
DOMAIN_BLOB = '23de82f5240a72509f7afe4acd5948b65bc4ff13'
SCHEMA = 'radicadsac-mc038-stationary-knot-composition-research/1.0'
MAX_SPANS = 32
MAX_EVENTS = 256


class InvalidComposition(ValueError):
    pass


class ResourceRefusal(RuntimeError):
    pass


def need(ok, reason):
    if not ok:
        raise InvalidComposition(reason)


def git_blob(path):
    raw = Path(path).read_bytes()
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def stationary():
    need(git_blob(STATIONARY_PATH) == STATIONARY_BLOB,
         'original stationary mathematical verifier blob changed')
    spec = importlib.util.spec_from_file_location('pinned_mc038_stationary', STATIONARY_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sign(s):
    need(s in ('POSITIVE', 'NEGATIVE'), 'missing exact physical side sign')
    return s


def span_event(root, span_index):
    kind = root['kind']
    event = {'kind': 'OPEN_SOURCE_ROOT', 'span_index': span_index,
             'descriptor': copy.deepcopy(root),
             'left_sign': sign(root['left_sign']),
             'right_sign': sign(root['right_sign']),
             'multiplicity': root['multiplicity'],
             'event_kind': root['event_kind']}
    if kind == 'RATIONAL_ROOT':
        event['coordinate'] = root['source_value']
        event['coordinate_kind'] = 'EXACT_RATIONAL'
    elif kind == 'UNIQUE_REAL_ALGEBRAIC_ROOT':
        event['strict_bracket'] = root['source_isolating_interval']
        event['coordinate_kind'] = 'UNIQUE_IMPLICIT_ALGEBRAIC_ZERO'
    else:
        raise InvalidComposition('unrecognized algebraic root descriptor')
    return event


def compose_polynomial_spans(spans, prover):
    """Exact conditional math; original-source/owner binding is enforced upstream.

    Inputs are a source interval, local polynomial, and checked ordered view;
    the pinned prover independently regenerates the entire exact view.
    Caller-provided polynomial records do NOT by themselves grant source authority.
    """
    need(type(spans) is list and spans, 'empty source spans')
    if len(spans) > MAX_SPANS:
        raise ResourceRefusal('STATIONARY_COMPOSITION_SPAN_BUDGET_EXCEEDED')
    events = []
    knots = []
    previous = None
    left_physical = None
    right_physical = None
    for index, row in enumerate(spans):
        need(type(row) is dict and set(row) == {'interval', 'polynomial', 'view'},
             'source span is missing an exact required field')
        lo, hi = (prover.IDENTITY.q_exact(x) for x in row['interval'])
        need(lo < hi, 'nonpositive original-source span')
        poly = prover.trim(row['polynomial'])
        view = row['view']
        need(poly != [Q(0)], 'identity-zero interval cannot have discrete ordered roots')
        need(prover.validate_polynomial_view(view, poly, source_left=lo, source_right=hi),
             'unverified source-span witness')
        need(view == prover.build_polynomial_view(poly, source_left=lo, source_right=hi),
             'view differs from independently regenerated complete exact polynomial proof')
        if index == 0:
            left_physical = {'position': str(lo), **copy.deepcopy(view['left_endpoint'])}
        else:
            need(lo == previous['hi'], 'source spans have a gap or overlap')
            left_eval = prover.EE.peval(previous['poly'], Q(1))
            right_eval = prover.EE.peval(poly, Q(0))
            need(left_eval == right_eval, 'original-source knot is discontinuous')
            l = previous['view']['right_endpoint']
            r = view['left_endpoint']
            knot = {'position': str(lo),
                    'left_inward_sign': sign(l['inward_sign']),
                    'right_inward_sign': sign(r['inward_sign']),
                    'left_one_sided_order': l['multiplicity'],
                    'right_one_sided_order': r['multiplicity'],
                    'is_physical_zero': left_eval == 0}
            need((l['relation'] == 'ZERO') == (left_eval == 0) and
                 (r['relation'] == 'ZERO') == (right_eval == 0),
                 'knot event equality contradiction')
            if left_eval:
                need(l['relation'] == r['relation'] == prover.sign_name(left_eval),
                     'nonzero source-knot relation mismatch')
                need(l['inward_sign'] == r['inward_sign'],
                     'nonzero source-knot side signs disagree')
                knot['kind'] = 'NONZERO_KNOT_NOT_ROOT'
            else:
                knot['kind'] = 'SOURCE_KNOT_ZERO'
                knot['global_smooth_multiplicity_claimed'] = False
                knot['event_kind'] = ('CROSSING' if l['inward_sign'] != r['inward_sign']
                                      else 'TOUCHING')
                events.append({'kind': 'SOURCE_KNOT_ZERO',
                               'coordinate_kind': 'EXACT_RATIONAL_SOURCE_KNOT',
                               'coordinate': str(lo),
                               'left_sign': sign(l['inward_sign']),
                               'right_sign': sign(r['inward_sign']),
                               'left_one_sided_order': l['multiplicity'],
                               'right_one_sided_order': r['multiplicity'],
                               'global_smooth_multiplicity_claimed': False,
                               'event_kind': knot['event_kind']})
            knots.append(knot)
        for root in view['ordered_open_roots']:
            events.append(span_event(root, index))
        previous = {'hi': hi, 'poly': poly, 'view': view}
        right_physical = {'position': str(hi), **copy.deepcopy(view['right_endpoint'])}
    if len(events) > MAX_EVENTS:
        raise ResourceRefusal('STATIONARY_COMPOSITION_ROOT_BUDGET_EXCEEDED')
    # Root ordering follows complete per-span Sturm witnesses and strict
    # original source intervals. Only physical zeros split maximal sign cells.
    current = sign(left_physical['inward_sign'])
    boundaries = ['ORIGINAL_SOURCE_START']
    cells = []
    for i, event in enumerate(events):
        need(current == event['left_sign'],
             'a physical sign cell or knot join is inconsistent')
        marker = 'PHYSICAL_ZERO_' + str(i + 1)
        cells.append({'left_boundary': boundaries[-1], 'right_boundary': marker,
                      'sign': current})
        boundaries.append(marker)
        current = event['right_sign']
    need(current == sign(right_physical['inward_sign']),
         'right physical endpoint contradicts continuous sign sequence')
    cells.append({'left_boundary': boundaries[-1],
                  'right_boundary': 'ORIGINAL_SOURCE_END', 'sign': current})
    return {'schema': SCHEMA,
            'status': 'CONDITIONAL_EXACT_STATIONARY_POLYNOMIAL_KNOT_COMPOSITION',
            'source_span_count': len(spans), 'ordered_physical_zero_events': events,
            'true_source_knots': knots, 'maximal_open_sign_cells': cells,
            'left_physical_endpoint': left_physical,
            'right_physical_endpoint': right_physical,
            'distinct_open_physical_zeros': len(events),
            'historical_route_admitted': False,
            'arbitrary_trigonometric_child_certified': False,
            'general_v27_v41_theorem_claimed': False, 'pb00701_certified': False,
            'mc_b_established': False, 'mc1_established': False,
            'native_brep_or_step_qualified': False, 'production_authorized': False}


def replay_frozen_stationary_cases(prover=None):
    prover = prover or stationary()
    need(git_blob(CORPUS) == CORPUS_BLOB, 'frozen v54 case identity changed')
    need(git_blob(AUTH) == AUTH_BLOB, 'production and gate authority changed')
    need(git_blob(DOMAIN) == DOMAIN_BLOB, '26-operation MC-002 domain changed')
    need(len(json.loads(DOMAIN.read_text())['coverage_rule']['required_operation_ids']) == 26,
         'original machining operation denominator changed')
    need(json.loads(AUTH.read_text())['production_authorized'] is False,
         'research cannot run under new production authority')
    corpus = json.loads(CORPUS.read_text())
    source_rows = [row for row in corpus['cases']
                   if prover.OWNER in json.dumps(row.get('expected', {}), sort_keys=True)]
    need(len(source_rows) == 3, 'stationary frozen-case population changed')
    results = []
    for row in source_rows:
        spec = row['spec']
        candidate = prover.build_source_candidate(spec)
        need(candidate['status'] == 'STATIONARY_POLYNOMIAL_ORDERED_VIEWS_CERTIFIED',
             'pinned stationary owner lacks complete ordered views')
        need(candidate['all_historical_spans_stationary'] is True,
             'mixed owner is not admitted by this conditional composition')
        prover.validate_source_candidate(candidate, spec)
        source_spans = prover.source_stationary_spans(spec)
        need(len(candidate['views']) == len(source_spans),
             'incomplete stationary source-span population')
        aligned = []
        for index, (item, actual) in enumerate(zip(candidate['views'], source_spans)):
            need(item['span_index'] == index and actual['owner'] == prover.OWNER,
                 'historical span ownership/order drifted')
            aligned.append({'interval': item['source_interval'],
                            'polynomial': actual['polynomial'],
                            'view': item['ordered_view']})
        composed = compose_polynomial_spans(aligned, prover)
        composed['source_case_id'] = row['id']
        composed['original_source_sha256'] = candidate['source_sha256']
        composed['historical_v54_disposition'] = row['expected']['v54_disposition']
        results.append(composed)
    need(sum(r['historical_v54_disposition'] ==
             'BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE' for r in results) == 2,
         'historical stationary multi-span blocked cases changed')
    return results


def no_truth(status, reason):
    return {'status': status, 'reason': reason, 'is_truth_value': False,
            'pb00701_certified': False, 'mc_b_established': False,
            'production_authorized': False}


def run_bounded():
    try:
        return replay_frozen_stationary_cases()
    except ResourceRefusal as exc:
        return no_truth('RESOURCE_REFUSAL', str(exc))
    except (MemoryError, RecursionError, OverflowError) as exc:
        return no_truth('RESOURCE_REFUSAL', type(exc).__name__)
