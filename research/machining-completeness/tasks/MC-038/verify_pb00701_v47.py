#!/usr/bin/env python3
"""V47 contract, preserved evidence and source-bound adversarial acceptance."""
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
BASE='2b67c7e6b4befff04dfc456af6afb0894aafc4e8'
PREFIX='research/machining-completeness/tasks/'
PINS={
 PREFIX+'MC-032/event_engine.py':'789a709c5141479a343035d1b7055dd4e53534e1',
 PREFIX+'MC-038/pb00701_algebraic_child_map_model.py':'c055e7f392a921b386a1a99cc70b5004121ae7f6',
 PREFIX+'MC-038/pb00701_algebraic_endpoint_model.py':'77c18cb5c8c0700072c65969c973e8f3c4c12a99',
 PREFIX+'MC-038/pb00701_algebraic_endpoint_certificate.py':'92258bbad7fa4cfa1be5413a7253369e73abc318',
 PREFIX+'MC-038/pb00701_algebraic_orientation_cut_model.py':'a56d6487963d269405ab82f3db4cce58a0165520',
 PREFIX+'MC-038/pb00701_orientation_root_partition_model.py':'2f96622b5c69655279d66fe2b36f8f3e03414660',
 PREFIX+'MC-038/pb00701_phase_sector_partition_model.py':'6211e658621af7100c2509dcafdaeaf348e48d46',
 PREFIX+'MC-038/pb00701_orientation_transition_bridge_model.py':'a0930d7bfddd619bf930a51bbfa14570e2450fe5',
 PREFIX+'MC-038/pb00701_correlated_closed_handoff_model.py':'d47b8dd8fe8b4b91fd12c1e76974a5a4e85b03b2',
}
PROTECTED={'source_audio_provenance','canonical_journal','exact_time_path_phase','source_uncertainty','positive_volume_material','cutter_holder_access','durable_body_lineage','refusal_uncertified','conventional_step'}
CONTROLS={'genuine_predecessor_residual','exact_algebraic_sturm_one_sided_jets','open_closed_multiplicity','strict_margin_equality_neighbors','weak_not_strict','uniform_phase_containment','all_derivative_channels','global_chain_rule','both_phase_directions','external_root_outcomes','internal_physical_root_once','neutral_orientation_cut','multiple_root_strict_derivative_contradiction','forged_sturm_field_map_source_phase','finite_checker_no_route_or_sign_search','unknown_source_rejection','exact_resource_refusal','historical_precedence','frozen_26_operations','no_false_gate_promotion'}
EFFECT={'PB-007-01':'OPEN','PB-007-02':'OPEN_DEPENDENT_ON_PB-007-01','PB-007-03':'OPEN','PB-007-04':'OPEN_PROPAGATED','PO-04':'OPEN','PO-05':'OPEN','PO-08':'OPEN','MC-B':'NOT_ESTABLISHED','MC-1':'NOT_ESTABLISHED','domain_operation_count':26,'domain_narrowed':False}
AUTHORITY={'polynomial':'RATIONAL_STURM_WITH_EXACT_ONE_SIDED_FIELD_JETS','derivative':'V42_V43_COMPLETE_ORTHANTS_ON_CLOSED_ALGEBRAIC_CHILDREN','external_endpoint':'PRESERVED_V19_V6_RATIONAL_TURN','internal_endpoint':'VERIFIED_V46_SOURCE_BOUND_ENDPOINT','composition':'SOURCE_VALIDATION_THEN_PRESERVED_V27_TWO_CHILD_COMPOSER','representation':'VERIFIED_V45_SINGLE_GENERATOR_BISECTION'}


def load(path):return json.loads(path.read_text())
def blob(path):
    raw=path.read_bytes()
    return hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()


def contract(data,check_repo=True):
    assert data['schema']=='radicadsac-mc038-pb00701-algebraic-single-cut/47.0'
    assert data['task']=='MC-038' and data['corrective_issue']==259
    assert data['source_baseline']==BASE and data['evidence_class']=='DETERMINISTIC_MODEL'
    assert data['decision']=='BOUNDED_CLOSED_CHILD_AND_ALGEBRAIC_SINGLE_CUT_COMPOSITION_ESTABLISHED'
    assert data['authority']==AUTHORITY and data['historical_git_blob_pins']==PINS
    assert set(data['boundary_controls'])==CONTROLS and len(data['boundary_controls'])==len(CONTROLS)
    assert data['bounded_single_cut_consumption'] is True
    for key in ('full_multi_cut_partition','caller_metadata_trusted','resource_refusal_is_truth','unknown_source_fields_stripped'):
        assert data[key] is False
    assert set(data['protected_semantics'])==PROTECTED
    assert all(x is True for x in data['protected_semantics'].values())
    assert data['programme_effect']==EFFECT
    assert data['resources']=={'native_campaign_run':False,'paid_campaign_run':False,'production_authorized':False,'expensive_execution_authorized':False}
    assert data['unsupported']==['GENERAL_NONMONOTONE_COUPLED_ZERO_ISOLATION','FULL_MULTI_CUT_OR_MULTIGENERATOR_PARTITION','NONCOMMENSURATE_OR_INDEPENDENT_PHASE_LAWS']
    if not check_repo:return
    for path,sha in PINS.items():assert blob(ROOT/path)==sha,path
    domain=load(MC/'tasks/MC-002/domain-contract-v1.json')
    assert len(domain['coverage_rule']['required_operation_ids'])==26
    programme=load(MC/'programme-v1.json')
    assert programme['capability_status']=='NOT_ESTABLISHED'
    assert programme['production_authorized'] is False and programme['expensive_execution_authorized'] is False
    assert {g['id']:g for g in programme['gates']}['MC-B']['state']=='NOT_ESTABLISHED'
    obligations={p['id']:p for p in load(MC/'proof-obligations-v1.json')['obligations']}
    for po in ('PO-04','PO-05','PO-08'):assert obligations[po]['state']=='OPEN'
    for path in (ROOT/'docs/machining-completeness/71-PB00701-ALGEBRAIC-SINGLE-CUT.md',TASK/'pb00701-report-v47.md'):
        text=path.read_text().lower()
        for token in ('sturm','closed','single-cut','not_established','26 operations'):
            assert token in text,(path,token)
    for name in ('pb00701_algebraic_interval_model.py','pb00701_algebraic_monotone_cut_model.py','pb00701_algebraic_monotone_cut_certificate.py'):
        for node in ast.walk(ast.parse((TASK/name).read_text())):
            if isinstance(node,ast.Constant):assert not isinstance(node.value,float),'floating truth constant'
            if isinstance(node,(ast.Import,ast.ImportFrom)):
                names=([node.module or ''] if isinstance(node,ast.ImportFrom) else [x.name for x in node.names])
                assert all(not n.startswith(('numpy','mpmath','decimal','sympy','math')) for n in names)
    workflow=(ROOT/'.github/workflows/mc1-pb00701-v47.yml').read_text()
    assert 'verify_pb00701_v47.py --contract --self-test' in workflow
    import pb00701_algebraic_monotone_cut_model as m
    import pb00701_correlated_closed_handoff_model as old
    assert (m.L,m.U,m.W,m.K)==(old.Y_LOWER,old.X_UPPER,old.Y_UPPER,old.TWO_PI_UPPER)


def rejected(fn):
    try:fn()
    except (AssertionError,ValueError,KeyError,TypeError):return
    raise AssertionError('adversarial contract mutation accepted')


def self_test():
    import test_pb00701_algebraic_monotone_cut as core
    import test_pb00701_algebraic_monotone_cut_integration as integration
    core.run();integration.run()
    data=load(TASK/'pb00701-algebraic-single-cut-v47.json')
    for key in ('full_multi_cut_partition','resource_refusal_is_truth','unknown_source_fields_stripped'):
        bad=copy.deepcopy(data);bad[key]=True;rejected(lambda:contract(bad,False))
    for key,value in (('MC-B','ESTABLISHED'),('domain_operation_count',25)):
        bad=copy.deepcopy(data);bad['programme_effect'][key]=value;rejected(lambda:contract(bad,False))
    bad=copy.deepcopy(data);bad['historical_git_blob_pins'][next(iter(PINS))]='0'*40
    rejected(lambda:contract(bad,False))
    subprocess.run([sys.executable,str(TASK/'verify_pb00701_v46.py'),'--contract'],check=True)
    subprocess.run([sys.executable,str(TASK/'verify_pb00701_v45.py'),'--contract'],check=True)
    print('PB-007-01 v47 closed-child/single-cut self-test: PASS')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--contract',action='store_true');parser.add_argument('--self-test',action='store_true');args=parser.parse_args()
    if not (args.contract or args.self_test):parser.error('choose --contract and/or --self-test')
    if args.contract:
        contract(load(TASK/'pb00701-algebraic-single-cut-v47.json'))
        print('PB-007-01 v47 contract: PASS')
    if args.self_test:self_test()

if __name__=='__main__':main()
