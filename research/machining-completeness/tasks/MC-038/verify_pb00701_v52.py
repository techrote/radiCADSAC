#!/usr/bin/env python3
"""V52 source/knot/coverage contract and actual-repository adversarial execution."""
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
BASE='08f22be41d14cd13fd17c00aa43b987259e887a9'
PINS={
    'pb00701_coupled_bspline_model.py':'a086b625e1a6dea8bd202699d161167bb69cc9e7',
    'pb00701_ordered_product_model.py':'d36c5f5ce3b12840273d8483c467ff41a6e9ae01',
    'pb00701_ordered_product_certificate.py':'81af2b07cb800a1e0636a8c737b9a492d774bb34',
    'verify_pb00701_v51.py':'d4717e4825adee49444153291c6e721559401644',
    'pb00701-ordered-product-v51.json':'08438d377a136f00fcfbda65d368f2b3291876c1',
    'pb00701-report-v51.md':'384c3544de8ca5c835459b4ab46116122c7a85b6',
}
CONTROLS=['original_bspline_source_regenerated','all_channel_source_knot_union','exact_bernstein_roundtrip',
          'repeated_knots_and_different_degrees','cropped_and_affine_global_source',
          'actual_multi_span_predecessor_result_preserved','implicit_and_algebraic_roots_in_multiple_spans',
          'shared_knot_root_counted_once','unequal_one_sided_orders_not_added',
          'same_orders_crossing_or_tangency_from_physical_signs','exact_physical_continuity_difference',
          'harmonic_cancellation_at_nonzero_knot','same_sign_tiny_jump_refusal',
          'nonzero_bridge_maximal_cell_coverage','exterior_root_orders','source_reversal_and_negation',
          'finite_full_source_checker_no_search','source_and_lowering_corruption',
          'span_knot_order_count_and_cell_corruption','unknown_boolean_float_rejection',
          'unsupported_owner_and_single_span_precedence','resource_nontruth_preserves_predecessor',
          'unrelated_errors_propagate','historical_pins_and_full_v51_regression','frozen_26_and_no_false_capability']
FLAGS={'full_original_source_checker':True,'global_root_union_claimed':True,
       'physical_continuity_at_every_source_knot_required':True,
       'global_analytic_multiplicity_at_source_knots_claimed':False,
       'discontinuous_source_point_policy_claimed':False,'general_nonmonotone_solver_claimed':False,
       'native_topology_claimed':False,'material_body_transition_claimed':False,
       'caller_lowering_trusted':False,'historical_span_evidence_changed':False,
       'resource_refusal_is_truth':False}
UNSUPPORTED=['SPAN_WITHOUT_CHECKED_V51_PRODUCT','DISCONTINUOUS_PHYSICAL_SOURCE_KNOT',
             'GLOBAL_ANALYTIC_MULTIPLICITY_AT_NONANALYTIC_KNOT','GENERAL_NONMONOTONE_OR_NONCOMMON_FACTOR_SOLVER',
             'NATIVE_MATERIAL_TOPOLOGY_AND_STEP_QUALIFICATION']


def load(path):return json.loads(path.read_text())


def same(x,y):return json.dumps(x,sort_keys=True,allow_nan=False)==json.dumps(y,sort_keys=True,allow_nan=False)


def blob(path):
    data=path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()


def contract(data,check_repo=True):
    import verify_pb00701_v51 as parent
    assert data['schema']=='radicadsac-mc038-pb00701-piecewise-product/52.0'
    assert data['task']=='MC-038' and type(data['corrective_issue']) is int and data['corrective_issue']==269
    assert data['source_baseline']==BASE and data['evidence_class']=='DETERMINISTIC_MODEL'
    assert data['decision']=='BOUNDED_CONTINUOUS_PIECEWISE_SOURCE_CERTIFICATE'
    assert data['acceptance_authority']=='EXECUTED_REPOSITORY_SELF_TEST_AND_VERIFIED_ISSUE_LEDGER'
    assert data['source_interface']=='ORIGINAL_RATIONAL_BSPLINE_CONTROLS_KNOTS_ID_INTERVAL_AND_AFFINE_PHASE'
    assert data['historical_additional_git_blob_pins']==PINS
    assert data['inherited_contract']=='verify_pb00701_v51.py'
    assert data['boundary_controls']==CONTROLS and len(set(CONTROLS))==len(CONTROLS)
    assert data['unsupported']==UNSUPPORTED
    for name,value in FLAGS.items():assert data[name] is value,name
    assert same(data['programme_effect'],parent.EFFECT)
    assert same(data['protected_semantics'],parent.PROTECTED)
    assert same(data['resources'],parent.RESOURCES)
    if not check_repo:return
    for name,sha in PINS.items():assert blob(TASK/name)==sha,name
    parent.contract(load(TASK/'pb00701-ordered-product-v51.json'),check_repo=True)
    for path in (TASK/'pb00701-report-v52.md',ROOT/'docs/machining-completeness/76-PB00701-PIECEWISE-PRODUCT.md'):
        text=path.read_text().lower()
        for token in ('original source','continuity','one-sided','not_established','26 operations','multiplicity'):
            assert token in text,(path,token)
    for name in ('pb00701_piecewise_product_model.py','pb00701_piecewise_product_certificate.py',
                 'test_pb00701_piecewise_product.py','test_pb00701_piecewise_product_integration.py'):
        tree=ast.parse((TASK/name).read_text())
        if name.startswith('test_'):continue
        for node in ast.walk(tree):
            if isinstance(node,ast.Constant):assert not isinstance(node.value,float)
            if isinstance(node,(ast.Import,ast.ImportFrom)):
                names=([node.module or ''] if isinstance(node,ast.ImportFrom) else [x.name for x in node.names])
                assert all(not n.startswith(('numpy','sympy','mpmath','decimal')) for n in names)
            if name.endswith('_certificate.py') and isinstance(node,ast.Call):
                called=node.func.attr if isinstance(node.func,ast.Attribute) else ''
                assert called not in {'classify_required_analytic_event','build_ordered_source_evidence',
                                      'build_piecewise_source_evidence','build_piecewise_certificate',
                                      'carrier_proof','certify_derivative','_decide_factor_sign','_decide_endpoint'}
    workflow=(ROOT/'.github/workflows/mc1-pb00701-v52.yml').read_text()
    assert 'verify_pb00701_v52.py --contract --self-test' in workflow
    assert 'github.event.pull_request.head.sha || github.sha' in workflow


def rejected(fn):
    try:fn()
    except (ValueError,TypeError,KeyError,AssertionError):return
    raise AssertionError('corrupt V52 contract accepted')


def multi_knot_self_test():
    """Additional actual-source control: three spans, two distinct zero joins.

This exercises composition beyond a single join, not merely repeated execution
of the two-span fixture or fabricated per-span event summaries.
    """
    from contextlib import ExitStack
    from unittest.mock import patch
    import pb00701_piecewise_product_model as m
    import pb00701_piecewise_product_certificate as checker
    import pb00701_ordered_product_model as predecessor
    import test_pb00701_piecewise_product as core
    common=core.power([-1,0,2],2)
    left=core.a.pmul(core.power([-1,1],2),common)
    middle=core.a.pmul(core.power([0,1],3),left)
    right=core.a.pmul(core.power([0,1],3),common)
    spec=core.encode([core.physical_piece(factor) for factor in (left,middle,right)])
    prior=predecessor.build_ordered_source_evidence(spec)
    assert prior['status']=='ORDERED_SOURCE_EVIDENCE_CERTIFIED',prior.get('reason')
    result=m.build_piecewise_source_evidence(spec)
    assert result['status']=='PIECEWISE_SOURCE_EVIDENCE_CERTIFIED',result.get('reason')
    assert same(prior,result['predecessor_result'])
    proof=result['certificate']
    assert checker.validate_piecewise_certificate(proof,spec) is True
    assert proof['source_lowering']['source_boundaries']==['0','1','2','3']
    assert [join['one_sided_orders'] for join in proof['knot_evidence']]==[[2,3],[2,3]]
    summary=proof['global_root_summary']
    assert summary['distinct_roots_open']==summary['total_distinct_roots_closed']==8
    assert (summary['crossings_open'],summary['tangencies_open'])==(5,3)
    assert summary['source_knot_roots']==2
    assert [cell['physical_sign'] for cell in proof['maximal_open_sign_cells']]==[-1,1,1]*3
    assert [root['id'] for root in proof['ordered_physical_events'] if root['kind']=='SOURCE_KNOT']==['knot:0','knot:1']
    assert len(proof['span_proofs'])==3 and len(proof['elementary_open_cells'])==9
    bad=copy.deepcopy(proof);bad['knot_evidence'].reverse()
    rejected(lambda:checker.validate_piecewise_certificate(bad,spec))
    bad=copy.deepcopy(proof);bad['span_proofs'][1]=copy.deepcopy(bad['span_proofs'][0])
    rejected(lambda:checker.validate_piecewise_certificate(bad,spec))
    with ExitStack() as stack:
        for module,name in ((predecessor,'build_ordered_source_evidence'),
                            (predecessor.v50,'classify_required_analytic_event'),
                            (predecessor.v50,'carrier_proof'),
                            (predecessor,'_decide_factor_sign'),
                            (predecessor.e,'_decide_endpoint')):
            stack.enter_context(patch.object(module,name,side_effect=AssertionError('no replacement search')))
        assert checker.validate_piecewise_certificate(proof,spec) is True
    print('v52 THREE-SPAN ACTUAL SOURCE: eight ordered roots, two distinct knot crossings counted once each, nine sign cells: PASS')


def self_test():
    import test_pb00701_piecewise_product as core
    import test_pb00701_piecewise_product_integration as integration
    core.run();integration.run()
    multi_knot_self_test()
    data=load(TASK/'pb00701-piecewise-product-v52.json')
    for key,value in FLAGS.items():
        bad=copy.deepcopy(data);bad[key]=not value
        rejected(lambda:contract(bad,False))
    for key,value in (('MC-B','ESTABLISHED'),('MC-1','ESTABLISHED'),('domain_operation_count',25),('domain_operation_count',True)):
        bad=copy.deepcopy(data);bad['programme_effect'][key]=value
        rejected(lambda:contract(bad,False))
    for key in data['protected_semantics']:
        bad=copy.deepcopy(data);bad['protected_semantics'][key]=False
        rejected(lambda:contract(bad,False))
    bad=copy.deepcopy(data);bad['historical_additional_git_blob_pins']['pb00701_ordered_product_model.py']='0'*40
    rejected(lambda:contract(bad,False))
    subprocess.run([sys.executable,str(TASK/'verify_pb00701_v51.py'),'--contract','--self-test'],check=True)
    print('PB-007-01 v52 full-source continuous knot composition self-test: PASS')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--contract',action='store_true');parser.add_argument('--self-test',action='store_true')
    opts=parser.parse_args()
    if not(opts.contract or opts.self_test):parser.error('choose --contract and/or --self-test')
    if opts.contract:
        contract(load(TASK/'pb00701-piecewise-product-v52.json'))
        print('PB-007-01 v52 contract: PASS')
    if opts.self_test:self_test()


if __name__=='__main__':main()
