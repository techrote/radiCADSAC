#!/usr/bin/env python3
"""Cheap contract plus deterministic endpoint/certificate adversarial gates."""
from __future__ import annotations
import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[4]
TASK=Path(__file__).resolve().parent
MC=ROOT/'research/machining-completeness'
BASE='e5efc6e441483b2ba594928b84aaa76cc7af1dc3'
PREFIX='research/machining-completeness/tasks/'
PINS={
 PREFIX+'MC-032/event_engine.py':'789a709c5141479a343035d1b7055dd4e53534e1',
 PREFIX+'MC-038/pb00701_algebraic_orientation_cut_model.py':'a56d6487963d269405ab82f3db4cce58a0165520',
 PREFIX+'MC-038/pb00701_algebraic_child_map_model.py':'c055e7f392a921b386a1a99cc70b5004121ae7f6',
 PREFIX+'MC-038/test_pb00701_algebraic_child_map_integration.py':'13792a40ae3c8f2e7484743938972812541bc0cb',
 PREFIX+'MC-038/pb00701-algebraic-child-map-v45.json':'b0a8424f0416dbbdd409f742cce8feec2f7cfb70',
}
PROTECTED={'source_audio_provenance','canonical_journal','exact_time_path_phase','source_uncertainty','positive_volume_material','cutter_holder_access','durable_body_lineage','refusal_uncertified','conventional_step'}
CONTROL_COUNT=26


def load(path): return json.loads(path.read_text())

def blob(path):
    raw=path.read_bytes()
    return hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()


def contract(a,check_repo=True):
    assert a['schema']=='radicadsac-mc038-pb00701-algebraic-endpoint/46.0'
    assert a['task']=='MC-038' and a['corrective_issue']==257
    assert a['source_baseline']==BASE and a['evidence_class']=='DETERMINISTIC_MODEL'
    assert a['decision']=='EXACT_ALGEBRAIC_IRRATIONAL_ENDPOINT_DECISION_ESTABLISHED'
    assert a['authority']=={
        'equality':'GELFOND_SCHNEIDER_ALGEBRAIC_COEFFICIENT_LAURENT_ZERO_TEST',
        'multiplicity':'MINIMUM_FINITE_SOURCE_AMPLITUDE_VANISHING_ORDER',
        'sign':'RATIONAL_MACHIN_TAYLOR_LAGRANGE_LIPSCHITZ',
        'termination':'ALGEBRAIC_NONZERO_BRANCH_PLUS_CONVERGENT_ENCLOSURES',
        'checker':'SOURCE_REGENERATION_AND_DIRECT_FINITE_SERIES_AUDIT',
        'source':'VERIFIED_V45_SINGLE_GENERATOR_REPRESENTATION'}
    assert a['historical_git_blob_pins']==PINS
    assert len(set(a['boundary_controls']))==CONTROL_COUNT
    for key in ('whole_span_certified','analytic_cut_consumed','caller_metadata_trusted','resource_refusal_is_truth','unknown_source_fields_stripped'):
        assert a[key] is False
    assert set(a['protected_semantics'])==PROTECTED
    assert all(v is True for v in a['protected_semantics'].values())
    assert a['resources']=={'native_campaign_run':False,'paid_campaign_run':False,'production_authorized':False,'expensive_execution_authorized':False}
    effect=a['programme_effect']
    assert effect=={'PB-007-01':'OPEN','PB-007-02':'OPEN_DEPENDENT_ON_PB-007-01','PB-007-03':'OPEN','PB-007-04':'OPEN_PROPAGATED','PO-04':'OPEN','PO-05':'OPEN','PO-08':'OPEN','MC-B':'NOT_ESTABLISHED','MC-1':'NOT_ESTABLISHED','domain_operation_count':26,'domain_narrowed':False}
    assert a['unsupported']==['WHOLE_CHILD_ROOT_ISOLATION','FULL_MULTI_CUT_ANALYTIC_COMPOSITION','NONCOMMENSURATE_OR_INDEPENDENT_PHASE_LAWS']
    assert 'do not retry MC-B' in a['next_repair']
    if not check_repo: return
    for path,sha in PINS.items(): assert blob(ROOT/path)==sha, path
    domain=load(MC/'tasks/MC-002/domain-contract-v1.json')
    assert len(domain['coverage_rule']['required_operation_ids'])==26
    programme=load(MC/'programme-v1.json')
    assert programme['capability_status']=='NOT_ESTABLISHED'
    assert programme['production_authorized'] is False and programme['expensive_execution_authorized'] is False
    assert {g['id']:g for g in programme['gates']}['MC-B']['state']=='NOT_ESTABLISHED'
    obligations={p['id']:p for p in load(MC/'proof-obligations-v1.json')['obligations']}
    for po in ('PO-04','PO-05','PO-08'): assert obligations[po]['state']=='OPEN'
    for path in (ROOT/'docs/machining-completeness/70-PB00701-ALGEBRAIC-ENDPOINT.md',TASK/'pb00701-report-v46.md'):
        text=path.read_text().lower()
        for token in ('gelfond','machin','lagrange','multiplicity','endpoint','not_established','26 operations'):
            assert token in text,(path,token)
    for name in ('pb00701_algebraic_endpoint_model.py','pb00701_algebraic_endpoint_certificate.py'):
        tree=ast.parse((TASK/name).read_text())
        for node in ast.walk(tree):
            if isinstance(node,(ast.Import,ast.ImportFrom)):
                names=([node.module or ''] if isinstance(node,ast.ImportFrom) else [x.name for x in node.names])
                assert all(not n.startswith(('numpy','mpmath','decimal')) for n in names)
                if isinstance(node,ast.ImportFrom) and node.module=='math':
                    assert all(x.name=='factorial' for x in node.names)
    workflow=(ROOT/'.github/workflows/mc1-pb00701-v46.yml').read_text()
    assert 'verify_pb00701_v46.py --contract --self-test' in workflow


def rejected(fn):
    try: fn()
    except (AssertionError,ValueError,TypeError,KeyError): return
    raise AssertionError('mutation was accepted')


def self_test():
    import test_pb00701_algebraic_endpoint as core
    import test_pb00701_algebraic_endpoint_integration as integration
    core.run(); integration.run()
    a=load(TASK/'pb00701-algebraic-endpoint-v46.json')
    for key,value in (('whole_span_certified',True),('analytic_cut_consumed',True),('resource_refusal_is_truth',True),('unknown_source_fields_stripped',True)):
        b=copy.deepcopy(a); b[key]=value; rejected(lambda:contract(b,False))
    for key,value in (('MC-B','ESTABLISHED'),('domain_operation_count',25)):
        b=copy.deepcopy(a); b['programme_effect'][key]=value; rejected(lambda:contract(b,False))
    b=copy.deepcopy(a); b['historical_git_blob_pins'][next(iter(PINS))]='0'*40
    rejected(lambda:contract(b,False))
    # Do not lose the predecessor's own contract behind a transitive import.
    subprocess.run([sys.executable,str(TASK/'verify_pb00701_v45.py'),'--contract'],check=True)
    print('PB-007-01 v46 endpoint/certificate self-test: PASS')


def main():
    p=argparse.ArgumentParser(); p.add_argument('--contract',action='store_true'); p.add_argument('--self-test',action='store_true')
    args=p.parse_args()
    if not (args.contract or args.self_test): p.error('choose --contract or --self-test')
    if args.contract:
        contract(load(TASK/'pb00701-algebraic-endpoint-v46.json'))
        print('PB-007-01 v46 contract: PASS')
    if args.self_test: self_test()

if __name__=='__main__': main()
