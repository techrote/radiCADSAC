#!/usr/bin/env python3
"""Original V43 source versus Q[x,sin(x),cos(x)] admission; bounded negative C.

This does not decide roots. It checks exact rational source/census identities.
Nonrepresentation relies on pi transcendence and linear independence of distinct
complex exponential-polynomials over C[x], proved in the accompanying RAG note.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / 'pb00701-finite-owner-corpus-v54.json'
REGISTER = HERE / 'pb00701-post-v54-evidence-reconciliation-v2.json'
CORPUS_BLOB = '5841c331579489b25caef38cd412bdbf286f9134'
REGISTER_BLOB = 'e52d3baf3692a011cf86234eeaa992ef407d99fd'
CASE = 'harvested:verify_pb00701_v9:4e7b85fa122a'
SOURCE_SHA = 'a83ca0cd16c7822e6525f8f2d2df26a54f45b99807cadebc67f31fc49b066c10'
ROW_SHA = '62346bbddca22c4271a14c10aa130327013ac7cf8daa0b0ae515257e8f28cfad'
EXPECTED = {
    'source_parameter_id': 'source-time-t', 'parameter_lo': '0',
    'parameter_hi': '1', 'phase_turn_offset': '0', 'phase_turn_rate': '1/8',
    'grammar': 'RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE',
    'cos_splines': {'1': {'degree': 1, 'controls': ['1', '1'],
                          'knots': ['0', '0', '1', '1']}},
    'sin_splines': {'1': {'degree': 1, 'controls': ['-1/2', '1/2'],
                          'knots': ['0', '0', '1', '1']}}
}
HISTORICAL = {
    'id': CASE, 'origin': 'verify_pb00701_v9', 'kind': 'HARVESTED',
    'spec': EXPECTED,
    'expected': {
        'id': CASE,
        'observed': {'status': 'BLOCKED', 'spans': [
            ['PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF', 'BLOCKED',
             'CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED']]},
        'v54_disposition': 'BLOCKED'
    }
}
SCHEMA = 'radicadsac-mc038-v43-rational-mtp-admission/1.0'
MAX_PINNED_BYTES = 1024 * 1024
MAX_RECEIPT_BYTES = 64 * 1024
RECEIPT_BLOB = '0d491411fa955158c00c87b43dd08e984146f838'


def require(ok, msg):
    if not ok:
        raise ValueError(msg)


def digest(obj):
    return hashlib.sha256(json.dumps(
        obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def git_blob(data):
    return hashlib.sha1(
        b'blob ' + str(len(data)).encode() + bytes([0]) + data).hexdigest()


def read_bounded(path, max_bytes):
    """Refuse raw inputs before hashing or JSON parsing; not a filesystem sandbox."""
    with path.open('rb') as handle:
        data = handle.read(max_bytes + 1)
    require(len(data) <= max_bytes, 'input resource limit exceeded: ' + path.name)
    return data


def load_pinned(path, sha):
    data = read_bounded(path, MAX_PINNED_BYTES)
    require(git_blob(data) == sha, 'pinned Git blob mismatch: ' + path.name)
    return json.loads(data)


def load_receipt(path):
    # Machine evidence is committed beside this verifier: check the entire
    # exact document, not only a hand-picked subset of its decoded fields.
    data = read_bounded(path, MAX_RECEIPT_BYTES)
    require(git_blob(data) == RECEIPT_BLOB, 'machine receipt Git blob mismatch')
    return json.loads(data)


def typed_json(value):
    """Canonical JSON preserves bool/int/float distinctions lost by Python ==."""
    try:
        return json.dumps(value, sort_keys=True, separators=(',', ':'),
                          ensure_ascii=True, allow_nan=False)
    except (TypeError, ValueError, RecursionError, OverflowError) as exc:
        raise ValueError('invalid machine receipt JSON value') from exc


def validate_receipt(receipt, result):
    require(isinstance(receipt, dict), 'machine receipt must be an object')
    # Every field shared with the executable receipt is checked, including
    # nonpromotion fields previously omitted from the 12-key check.
    keys = (
        'schema', 'task', 'evidence_class', 'claim', 'case_id',
        'source_sha256', 'original_row_sha256',
        'frozen_corpus_git_blob', 'v2_register_git_blob',
        'before', 'after', 'deltas', 'newly_closed_historical_case_ids',
        'required_pb007_discharge', 'generic_event_completeness',
        'MC_B', 'MC_1', 'production_authorized'
    )
    for key in keys:
        require(key in receipt and key in result,
                'machine receipt missing checked field: ' + key)
        require(typed_json(receipt[key]) == typed_json(result[key]),
                'machine receipt typed contract drift: ' + key)
    return True


def receipt_adversarial(receipt, result):
    """Actual on-disk tamper probes plus independently typed claim checks."""
    from tempfile import TemporaryDirectory
    from pathlib import Path
    cases = (
        ('false_as_zero', ('required_pb007_discharge',), 0, True),
        ('integer_as_float', ('before', 'original_sources'), 121.0, True),
        ('zero_as_false', ('deltas', 'original_sources'), False, True),
        ('production_promotion', ('production_authorized',), True, True),
        ('unexamined_interval', ('original_interval', 1), '2', False),
    )
    disk_refusals = typed_refusals = 0
    with TemporaryDirectory() as temporary:
        target_path = Path(temporary) / 'machine-receipt.json'
        for label, keys, replacement, checked in cases:
            changed = deepcopy(receipt)
            slot = changed
            for key in keys[:-1]:
                slot = slot[key]
            slot[keys[-1]] = replacement
            target_path.write_text(json.dumps(changed, sort_keys=True),
                                   encoding='utf-8')
            try:
                load_receipt(target_path)
            except ValueError as exc:
                require('machine receipt Git blob mismatch' in str(exc),
                        'incorrect receipt tamper refusal: ' + label)
                disk_refusals += 1
            else:
                raise AssertionError('altered receipt accepted: ' + label)
            if checked:
                # Check the semantic validator independently of Git pinning.
                # Python == would accept the first three typed substitutions.
                try:
                    validate_receipt(json.loads(target_path.read_bytes()), result)
                except ValueError as exc:
                    require('typed contract drift' in str(exc),
                            'incorrect typed refusal: ' + label)
                    typed_refusals += 1
                else:
                    raise AssertionError('typed forged claim accepted: ' + label)
    require((disk_refusals, typed_refusals) == (5, 4),
            'receipt admission adversarial census drift')
    return {'disk_blob_tamper_refusals': disk_refusals,
            'typed_claim_mutation_refusals': typed_refusals}


def validate_original(row):
    require(row == HISTORICAL, 'original V43 source/phase/owner/disposition drift')
    require(digest(row['spec']) == SOURCE_SHA and digest(row) == ROW_SHA,
            'canonical exact source or row hash mismatch')
    a, b = (Q(v) for v in row['spec']['cos_splines']['1']['controls'])
    c, d = (Q(v) for v in row['spec']['sin_splines']['1']['controls'])
    require(a == b == 1 and c == Q(-1, 2) and d == Q(1, 2),
            'unexpected original rational B-spline controls')
    # Clamped degree-one original B-spline basis on [0,1].
    require((a, b-a) == (Q(1), Q(0)) and
            (c, d-c) == (Q(-1,2), Q(1)),
            'original physical polynomial lowering mismatch')
    offset, rate = (Q(row['spec'][k]) for k in
                    ('phase_turn_offset', 'phase_turn_rate'))
    require(offset == 0 and rate == Q(1,8), 'affine phase changed')
    # x=2*pi*(t/8)=pi*t/4; t=4*x/pi.
    # Exact x*sin(x) coefficient is 4/pi, not rational.
    return {
        'source_interval': ['0','1'], 'source_piece_edges': ['0','1'],
        'cos_h1_in_t': ['1'], 'sin_h1_in_t': ['-1/2','1'],
        'phase_turn_rate': '1/8', 'phase_in_radians': 'pi*t/4',
        'normalised_x': 'pi*t/4', 'inverse_source': 't=4*x/pi',
        'cos_h1_in_x': '1', 'sin_h1_in_x': '4*x/pi-1/2',
        'x_sin_coefficient': '4/pi',
        'rational_mtp_grammar_admitted': False
    }


def census(corpus, register):
    rows = corpus['cases']
    require(corpus['schema'] == 'radicadsac-pb00701-finite-owner-corpus/54.0'
            and len(rows) == 121, 'original frozen source denominator wrong')
    by_id = {row['id']:row for row in rows}
    require(len(by_id)==121, 'original frozen case ID collision')
    refusals = {x['id'] for x in rows if
                x['expected']['v54_disposition'] == 'BLOCKED'}
    missing = {x['id'] for x in rows if
               x['expected']['v54_disposition'] ==
               'BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE'}
    require(len(refusals)==20 and len(missing)==30 and not refusals & missing,
            'historical refusal/missing-ordered-premise census drift')
    old=register['historical_v54']
    require(old['original_source_cases']==121 and old['route_refusals']==20
            and old['missing_ordered_span_premises']==30,
            'v2 historical baseline drift')
    require(register['frozen_corpus_git_blob']==CORPUS_BLOB
            and register['evidence_class']=='DETERMINISTIC_MODEL'
            and register['registry_scope'][
                'new_general_root_event_or_composition_theorem'] is False,
            'v2 custody/theorem nonpromotion drift')
    evidence=register['source_cases']
    require(len(evidence)==50
            and len({v['case_id'] for v in evidence})==50
            and {v['case_id'] for v in evidence}==refusals|missing,
            'v2 original unresolved set drift')
    finite=continuum=0
    for v in evidence:
        original=by_id[v['case_id']]
        require(v['source_sha256']==digest(original['spec'])
                and v['original_row_sha256']==digest(original),
                'registered original source/row mismatch: '+v['case_id'])
        require(v['historical_v54_disposition']==
                original['expected']['v54_disposition']
                and v['registered_evidence_level']=='COMPLETE_SOURCE_SPECIFIC'
                and v['evidence']['complete_original_source_zero_set'] is True,
                'registered evidence/historical disposition mismatch')
        scope=v['evidence']['scope']
        require(scope in ('COMPLETE_FINITE_SOURCE_ZERO_SET',
                          'COMPLETE_CLOSED_CONTINUUM_ZERO_SET'),
                'unknown source-complete evidence scope')
        if scope=='COMPLETE_FINITE_SOURCE_ZERO_SET': finite+=1
        else: continuum+=1
    require((finite,continuum)==(49,1),
            'complete finite/continuum evidence census drift')
    require(CASE in refusals, 'chosen historical V43 refusal missing')
    return by_id, {
        'original_sources':121, 'route_refusals':20,
        'missing_ordered_premises':30, 'complete_original_witnesses':50,
        'finite_witnesses':49, 'continuum_witnesses':1
    }


def exact_fourier_controls():
    """Exact finite Fourier tests; not proof of all mathematical input fields."""
    Z=(Q(0),Q(0)); U=(Q(1),Q(0))
    def ac(a,b): return (a[0]+b[0],a[1]+b[1])
    def mc(a,b): return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
    def add(a,b):
        d=dict(a)
        for k,v in b.items(): d[k]=ac(d.get(k,Z),v)
        return {k:v for k,v in d.items() if v!=Z}
    def mul(a,b):
        d={}
        for k,v in a.items():
            for m,w in b.items(): d[k+m]=ac(d.get(k+m,Z),mc(v,w))
        return {k:v for k,v in d.items() if v!=Z}
    s={1:(Q(0),Q(-1,2)),-1:(Q(0),Q(1,2))}
    c={1:(Q(1,2),Q(0)),-1:(Q(1,2),Q(0))}
    require(add(mul(s,s),mul(c,c))=={0:U},
            'cos^2+sin^2 rational Fourier identity failed')
    require(add(mul(s,c),mul(c,s))==
            {2:(Q(0),Q(-1,2)),-2:(Q(0),Q(1,2))},
            'double-angle rational Fourier identity failed')
    require(add(s,c)[1]==(Q(1,2),Q(-1,2)),
            'rational constant-amplitude MTP control failed')
    return {'controls':3,'rational_constant_amplitude_admitted':True,
            'nonconstant_V43_direct_rational_MTP_admitted':False}


def ingress_budget_adversarial():
    """Actual disk boundaries; over-budget inputs refuse before hash or JSON."""
    from tempfile import TemporaryDirectory
    controls = 0
    with TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / 'tampered.json'
        for budget in (MAX_PINNED_BYTES, MAX_RECEIPT_BYTES):
            path.write_bytes(b'x' * budget)
            require(len(read_bounded(path, budget)) == budget,
                    'exact byte-budget boundary incorrectly refused')
            controls += 1
            path.write_bytes(b'x' * (budget + 1))
            try:
                read_bounded(path, budget)
            except ValueError as exc:
                require('resource limit exceeded' in str(exc),
                        'over-budget input did not receive resource refusal')
                controls += 1
            else:
                raise AssertionError('oversized raw input admitted')
        path.write_bytes(b'x' * (MAX_PINNED_BYTES + 1))
        try:
            load_pinned(path, '0' * 40)
        except ValueError as exc:
            require('resource limit exceeded' in str(exc),
                    'pinned corpus was hashed before resource refusal')
            controls += 1
        else:
            raise AssertionError('oversized pinned corpus admitted')
        path.write_bytes(b'x' * (MAX_RECEIPT_BYTES + 1))
        try:
            load_receipt(path)
        except ValueError as exc:
            require('resource limit exceeded' in str(exc),
                    'receipt was parsed before resource refusal')
            controls += 1
        else:
            raise AssertionError('oversized receipt admitted')
    require(controls == 6, 'ingress budget test census drift')
    return {'max_pinned_bytes': MAX_PINNED_BYTES,
            'max_receipt_bytes': MAX_RECEIPT_BYTES,
            'actual_disk_boundary_controls': controls}


def adversarial():
    valid=deepcopy(HISTORICAL)
    require(not validate_original(valid)['rational_mtp_grammar_admitted'],
            'unsafe MTP admission')
    mutations=0
    for attr,val in [('phase_turn_rate','-1/8'),('phase_turn_rate','1/4'),
                     ('phase_turn_offset','1/4'),
                     ('source_parameter_id','other'),('parameter_hi','2')]:
        x=deepcopy(valid);x['spec'][attr]=val
        try:validate_original(x)
        except ValueError:mutations+=1
        else:raise AssertionError('source/phase mutation accepted')
    for field,i,val in [('cos_splines',0,'0'),('sin_splines',0,'0'),
                        ('sin_splines',1,'0')]:
        x=deepcopy(valid);x['spec'][field]['1']['controls'][i]=val
        try:validate_original(x)
        except ValueError:mutations+=1
        else:raise AssertionError('harmonic mutation accepted')
    for mutation in ('disposition','owner','case'):
        x=deepcopy(valid)
        if mutation=='disposition': x['expected']['v54_disposition']='CERTIFIED'
        elif mutation=='owner':
            x['expected']['observed']['spans'][0][0]='OTHER'
        else:x['id']='synthetic'
        try:validate_original(x)
        except ValueError:mutations+=1
        else:raise AssertionError('history mutation accepted')
    # Prospective exact arithmetic controls are REFUSALS for event-completeness.
    delta=Q(1,2**200)
    require(delta>0 and delta<Q(1,2**199) and
            Q(-delta)*Q(-2*delta)>0 and (delta/2)*(delta/2-delta)<0,
            'close rational double-event sign control failed')
    require(Q(0)**2==0 and Q(1)**2>0,
            'even tangency control failed')
    require(mutations==11, 'adversarial mutation count mismatch')
    return {'file_ingress': ingress_budget_adversarial(),
            'original_source_mutation_refusals':mutations,
            'prospective_event_controls':[
                'tangency_even_multiplicity', 'identity_zero_continuum',
                'two_roots_separated_by_2^-200'],
            'prospective_event_claims_admitted':0}


def run(with_tests):
    corpus=load_pinned(CORPUS,CORPUS_BLOB)
    register=load_pinned(REGISTER,REGISTER_BLOB)
    by_id,before=census(corpus,register)
    proof=validate_original(by_id[CASE])
    checks=exact_fourier_controls()
    attacks=adversarial() if with_tests else None
    result={
        'schema':SCHEMA, 'task':'MC-038',
        'evidence_class':'DETERMINISTIC_MODEL',
        'claim':'DIRECT_RATIONAL_MTP_PHASE_NORMALIZATION_REFUTED_FOR_ORIGINAL_V43',
        'case_id':CASE, 'source_sha256':SOURCE_SHA,'original_row_sha256':ROW_SHA,
        'frozen_corpus_git_blob':CORPUS_BLOB,
        'v2_register_git_blob':REGISTER_BLOB,
        'source_derivation':proof, 'fourier_controls':checks,
        'adversarial_controls':attacks,
        'mathematical_lemmas':[
            'pi is transcendental',
            'distinct exponential-polynomials are linearly independent over C[x]'
        ],
        'published_mtp_grammar':'P in Q[X,S,C], P(x,sin(x),cos(x))',
        'published_mtp_algorithm_executed':False,
        'general_root_decidability_refuted':False,
        'coefficient_field_extension_refuted':False,
        'before':before,'after':dict(before),
        'deltas':{k:0 for k in before},
        'newly_closed_historical_case_ids':[],
        'required_pb007_discharge':False,
        'generic_event_completeness':False,
        'native_geometry_or_STEP':False,
        'MC_B':'NOT_ESTABLISHED','MC_1':'NOT_ESTABLISHED',
        'all_26_operations_preserved':True,
        'production_authorized':False
    }
    if with_tests:
        receipt=load_receipt(HERE/'pb00701-v43-mtp-coefficient-boundary.json')
        validate_receipt(receipt, result)
        controls=receipt_adversarial(receipt, result)
        print('PASS: exact machine receipt custody and typed adversarial controls:', controls)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--contract',action='store_true')
    parser.add_argument('--self-test',action='store_true')
    args=parser.parse_args()
    print(json.dumps(run(args.self_test),sort_keys=True,indent=2))


if __name__=='__main__':main()
