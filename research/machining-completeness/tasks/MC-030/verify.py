#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, importlib.util, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT/'research'/'machining-completeness'/'tasks'/'MC-030'
CONTRACT = TASK/'provider-dispatch-contract-v1.json'
MODEL = TASK/'dispatch_model.py'
OUTCOME = TASK/'outcome.json'
REPORT = TASK/'report.md'
DOC = ROOT/'docs'/'machining-completeness'/'22-MC030-NATIVE-PROVIDER-DISPATCH.md'
REGISTRY = ROOT/'research'/'machining-completeness'/'outcomes-v1.json'
WORKFLOW = ROOT/'.github'/'workflows'/'mc1-static.yml'
EXPECTED_BASELINE = 'fd0662dbefcc1eaa03e2be0503e53860feaa4cf0'
EXPECTED_DEPS = {
    'MC-010':('research/machining-completeness/tasks/MC-010/outcome.json','4960730316f89dbb3fbf958d054127fa4fc0d789','COMPLETED_RESEARCH'),
    'MC-016':('research/machining-completeness/tasks/MC-016/outcome.json','606a7d0b8be61131b2272f2eb161d6a4dbba703a','COMPLETED_RESEARCH'),
    'MC-018':('research/machining-completeness/tasks/MC-018/outcome.json','085f864b4bd58b38f154b6c9d58d9e68b60ee7ec','COMPLETED_RESEARCH'),
    'MC-019':('research/machining-completeness/tasks/MC-019/outcome.json','4456c964315c10b46ce61a5a8d4a45e8025730b7','COMPLETED_RESEARCH'),
    'MC-020':('research/machining-completeness/tasks/MC-020/outcome.json','19504a35f47bca710bb6369abb723de83d1afede','COMPLETED_RESEARCH'),
    'MC-021':('research/machining-completeness/tasks/MC-021/outcome.json','442397474c596bc3a73e9442e4ab2f955e19b0e6','COMPLETED_RESEARCH'),
    'MC-022':('research/machining-completeness/tasks/MC-022/outcome.json','8ca7cfd0d098d746394cab71257b1dfc6e3a7250','COMPLETED_RESEARCH'),
    'MC-023':('research/machining-completeness/tasks/MC-023/outcome.json','15cd3b128cdaa14370594debd490e76a4a0d6b23','COMPLETED_RESEARCH'),
}
EXPECTED_BLOCKERS = {'PB-007-01','PB-007-02','PB-007-03','RB-016-02','RB-016-04'}
EXPECTED_FAST = {'FP-MILL-ANALYTIC-TRANSLATION','FP-FORM-BOX-UNION','FP-LATHE-AXISYMMETRIC','FP-LATHE-PHASE-BOUNDED'}
EXPECTED_ARTIFACTS = {
    'research/machining-completeness/tasks/MC-030/provider-dispatch-contract-v1.json',
    'research/machining-completeness/tasks/MC-030/dispatch_model.py',
    'research/machining-completeness/tasks/MC-030/report.md',
    'research/machining-completeness/tasks/MC-030/outcome.json',
    'research/machining-completeness/tasks/MC-030/verify.py',
    'docs/machining-completeness/22-MC030-NATIVE-PROVIDER-DISPATCH.md',
}

def load(p): return json.loads(p.read_text(encoding='utf-8'))
def blob(p):
    b=p.read_bytes(); return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def model():
    spec=importlib.util.spec_from_file_location('mc030_dispatch', MODEL)
    mod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod); return mod

def validate_contract(c, check_files=True):
    assert c['schema']=='radicadsac-mc030-provider-dispatch/1.0'
    assert c['task']=='MC-030' and c['issue']==92 and c['source_baseline']==EXPECTED_BASELINE
    assert c['result']=='COMPLETED_RESEARCH_TOTAL_NONCYCLING_DISPATCH_DESIGN'
    assert c['native_execution'] is False and c['native_or_paid_campaign_run'] is False
    deps={d['task']:d for d in c['formal_dependencies']}; assert set(deps)==set(EXPECTED_DEPS)
    for t,(p,s,r) in EXPECTED_DEPS.items():
        assert deps[t]=={'task':t,'path':p,'blob_sha':s,'result_kind':r}
        if check_files:
            fp=ROOT/p; assert fp.is_file() and blob(fp)==s, f'{t} dependency blob drift'; assert load(fp)['result_kind']==r
    a=c['authority']
    assert a['kernel_brep_validity_is_material_correctness'] is False
    assert a['kernel_topology_is_body_or_lineage_authority'] is False
    assert a['fast_success_requires_independent_material_certificate'] is True
    assert a['step_or_brep_write_success_is_engineering_output_qualification'] is False
    assert a['fallback_may_rewrite_source_history'] is False
    fps={x['id']:x for x in c['fast_paths']}; assert set(fps)==EXPECTED_FAST
    for fp in fps.values(): assert fp['fallback']=='GENERAL_CERTIFIED_ROUTE' and fp['sufficient_admission']
    assert 'complete_finite_cutter_region' in ' '.join(fps['FP-MILL-ANALYTIC-TRANSLATION']['sufficient_admission'])
    assert 'COMPLETE_TOOL_CLEAR' in ' '.join(fps['FP-FORM-BOX-UNION']['sufficient_admission'])
    assert 'full_phase_orbit' in ' '.join(fps['FP-LATHE-AXISYMMETRIC']['sufficient_admission'])
    assert 'shared_exact_time_parameter' in ' '.join(fps['FP-LATHE-PHASE-BOUNDED']['sufficient_admission'])
    g=c['general_route']; assert g['id']=='GENERAL_CERTIFIED_ROUTE'
    assert g['implemented_as_total_success_by_mc030'] is False and g['timeout_or_resource_refusal_is_success'] is False and g['uncertified_is_success'] is False
    assert g['may_dispatch_back_to_fast_path'] is False and g['derived_accelerators']['may_become_canonical_authority'] is False
    assert {'PB-007-01','PB-007-02','PB-007-03','UNCERTIFIED','RESOURCE_REFUSAL','SEMANTIC_BLOCKER'} <= set(g['terminal_outcomes'])
    d=c['dispatcher']; assert d['max_fast_provider_invocations']==1 and d['max_general_route_invocations']==1 and d['cycles_allowed'] is False and d['request_semantics_are_immutable'] is True
    ms=c['multi_setup_composition']; assert ms['reclamp_is_material_changing'] is False and ms['each_material_changing_operation_is_dispatched_independently'] is True and ms['inherited_error_resets_at_setup_transition'] is False
    assert {b['id'] for b in c['blockers']}==EXPECTED_BLOCKERS and all(b['status'].startswith('OPEN') for b in c['blockers'])
    assert c['capability_state']['MC-A']=='ACCEPTED'
    for gate in ('MC-B','MC-C','MC-D','MC-E','MC-F','MC-1'): assert c['capability_state'][gate]=='NOT_ESTABLISHED'
    protected=' '.join(c['protected_semantics']).lower()
    for token in ('source/audio/provenance','positive-volume','durable body','step remains mandatory'): assert token in protected

def base_request(operation='mill_flat'):
    return {
        'operation_family':operation, 'material_changing':True,
        'source_bound':True, 'common_frame_bound':True, 'body_id':'body-A', 'input_revision':'rev-7',
        'engagement_bound':True, 'setup_bound':True, 'no_engaged_teleport':True,
        'transform_contract':'RIGHT_HANDED_PARENT_FROM_CHILD', 'exact_source_kind':'EXACT_RATIONAL',
        'body_transition_required':False, 'singular_or_exact_zero_output_boundary':False,
        'fixed_axis':True, 'motion_kind':'line', 'complete_finite_cutter_region':True, 'mc058_uncertainty':'ZERO'
    }

def model_controls():
    m=model()
    r=base_request(); assert m.select_route(r)=='FP-MILL-ANALYTIC-TRANSLATION'
    r=base_request('mill_ball_round'); r['motion_kind']='polyline'; assert m.select_route(r)=='FP-MILL-ANALYTIC-TRANSLATION'
    r=base_request(); r['mc058_uncertainty']='NONZERO_CERTIFIED_SHELL'; assert m.select_route(r)==m.GENERAL
    r=base_request('mill_accessible_undercut'); r.update(cutter_codec='EXACT_RATIONAL_BOX_UNION_V1',complete_holder_region=True,access_witness='COMPLETE_TOOL_CLEAR'); assert m.select_route(r)=='FP-FORM-BOX-UNION'
    r['access_witness']='HOLDER_COLLISION'; assert m.select_route(r)==m.GENERAL
    r=base_request('lathe_conventional'); r.update(axisymmetric_target_certificate=True,coaxial_setup=True,phase_independent_meridian=True,full_phase_orbit=True,meridian_codec='EXACT_RATIONAL_RECTANGLES_V1',phase_sensitive=False); assert m.select_route(r)=='FP-LATHE-AXISYMMETRIC'
    phase=base_request('lathe_threading_synchronized'); phase.update(shared_exact_time_parameter=True,unwrapped_spindle_phase=True,phase_constructor='CERTIFIED_FINITE_EXACT_SUBTYPE',transcendental_event_status='NONE'); assert m.select_route(phase)=='FP-LATHE-PHASE-BOUNDED'
    phase['transcendental_event_status']='PB-007-01'; assert m.select_route(phase)==m.GENERAL
    r=base_request(); r['body_transition_required']=True; assert m.select_route(r)==m.GENERAL
    r=base_request(); r['singular_or_exact_zero_output_boundary']=True; assert m.select_route(r)==m.GENERAL
    r=base_request(); r['input_revision']=''; assert m.select_route(r)==m.INVALID
    r=base_request('reclamp'); r['material_changing']=False; assert m.select_route(r)==m.SETUP_EVENT
    exact=base_request(); before=copy.deepcopy(exact)
    out=m.dispatch(exact,fast_result='SUCCESS',certificate='ACCEPTED'); assert out['terminal']=='FAST_SUCCESS_CERTIFIED' and out['fast_invocations']==1 and out['general_invocations']==0 and exact==before
    out=m.dispatch(exact,fast_result='KERNEL_FAILURE',general_result='SUCCESS_CERTIFIED'); assert out['terminal']=='SUCCESS_CERTIFIED' and out['fast_invocations']==1 and out['general_invocations']==1
    out=m.dispatch(exact,fast_result='SUCCESS',certificate='UNCERTIFIED',general_result='PB-007-01'); assert out['terminal']=='PB-007-01' and out['general_invocations']==1
    gen=base_request(); gen['body_transition_required']=True
    out=m.dispatch(gen,general_result='RESOURCE_REFUSAL'); assert out['terminal']=='RESOURCE_REFUSAL' and out['general_invocations']==1

def validate_repository():
    o=load(OUTCOME); assert o['task']=='MC-030' and o['result_kind']=='COMPLETED_RESEARCH' and o['issue']==92 and o['source_baseline']==EXPECTED_BASELINE
    assert o['native_execution'] is False and o['resources']['native_or_paid_campaign_run'] is False and {b['id'] for b in o['blockers']}==EXPECTED_BLOCKERS
    r=load(REGISTRY)['tasks']['MC-030']; assert r['state']=='COMPLETED_RESEARCH' and r['issue']==92 and set(r['accepted_artifacts'])==EXPECTED_ARTIFACTS and {b['id'] for b in r['blockers']}==EXPECTED_BLOCKERS
    wf=WORKFLOW.read_text(encoding='utf-8'); assert 'tasks/MC-030/dispatch_model.py' in wf and 'tasks/MC-030/verify.py' in wf and 'mc_workflow.py verify MC-030' in wf
    for text in (REPORT.read_text(encoding='utf-8'),DOC.read_text(encoding='utf-8')):
        low=text.lower()
        for token in ('noncycling','independent material certificate','pb-007-01','pb-007-02','pb-007-03','rb-016-02','rb-016-04','not_established','source/audio/provenance'): assert token in low
    model_controls()

def expect_rejected(mut):
    c=copy.deepcopy(load(CONTRACT)); mut(c)
    try: validate_contract(c,False)
    except Exception: return
    raise AssertionError('adversarial mutation accepted')

def self_test():
    validate_contract(load(CONTRACT),False); model_controls()
    attacks=[
        lambda c:c['authority'].__setitem__('kernel_brep_validity_is_material_correctness',True),
        lambda c:c['authority'].__setitem__('kernel_topology_is_body_or_lineage_authority',True),
        lambda c:c['authority'].__setitem__('fallback_may_rewrite_source_history',True),
        lambda c:c['dispatcher'].__setitem__('cycles_allowed',True),
        lambda c:c['dispatcher'].__setitem__('max_general_route_invocations',2),
        lambda c:c['general_route'].__setitem__('may_dispatch_back_to_fast_path',True),
        lambda c:c['general_route'].__setitem__('timeout_or_resource_refusal_is_success',True),
        lambda c:c['general_route']['derived_accelerators'].__setitem__('may_become_canonical_authority',True),
        lambda c:c['blockers'].__setitem__(0,{**c['blockers'][0],'status':'CLOSED'}),
        lambda c:c['capability_state'].__setitem__('MC-B','ACCEPTED'),
        lambda c:c['fast_paths'][1].__setitem__('sufficient_admission',['source_bound'])
    ]
    for attack in attacks: expect_rejected(attack)
    print('MC-030 adversarial self-test passed')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--contract',action='store_true'); ap.add_argument('--self-test',action='store_true'); a=ap.parse_args()
    if not (a.contract or a.self_test): ap.error('choose --contract or --self-test')
    if a.contract: validate_contract(load(CONTRACT)); validate_repository(); print('MC-030 contract verification passed')
    if a.self_test: self_test()
if __name__=='__main__': main()
