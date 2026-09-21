#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, importlib.util, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT/'research'/'machining-completeness'/'tasks'/'MC-026'
CONTRACT = TASK/'candidate-selection-contract-v1.json'
MODEL = TASK/'selection_model.py'
OUTCOME = TASK/'outcome.json'
REPORT = TASK/'report.md'
DOC = ROOT/'docs'/'machining-completeness'/'23-MC026-CANDIDATE-SELECTION.md'
REGISTRY = ROOT/'research'/'machining-completeness'/'outcomes-v1.json'
WORKFLOW = ROOT/'.github'/'workflows'/'mc1-static.yml'
DOMAIN = ROOT/'research'/'machining-completeness'/'tasks'/'MC-002'/'domain-contract-v1.json'
EXPECTED_BASELINE = 'b4739cb1941918e6d26d32800b622d631adfad99'
EXPECTED_DOMAIN_BLOB = '23de82f5240a72509f7afe4acd5948b65bc4ff13'
EXPECTED_DEPS = {
    'MC-024':('research/machining-completeness/tasks/MC-024/outcome.json','81802ee3f50e22f35166818c7883dc6e47668fbc','NEGATIVE_RESULT'),
    'MC-025':('research/machining-completeness/tasks/MC-025/outcome.json','b45cbabc7fa5f958491f8b02b1027b0efe9bd39a','NEGATIVE_RESULT'),
    'MC-027':('research/machining-completeness/tasks/MC-027/outcome.json','b1f015af98fa973b91b67beb14d10a140da8884f','NEGATIVE_RESULT'),
    'MC-028':('research/machining-completeness/tasks/MC-028/outcome.json','b4c1c39ec60baea748b117804f8bcc3400c03c2a','NEGATIVE_RESULT'),
    'MC-029':('research/machining-completeness/tasks/MC-029/outcome.json','6bfc3449d2a0273971a3e8714043b620a46c6aa9','NEGATIVE_RESULT'),
    'MC-030':('research/machining-completeness/tasks/MC-030/outcome.json','4c763731ea71ec5e2291e340636ecfa6a84062db','COMPLETED_RESEARCH'),
    'MC-049':('research/machining-completeness/tasks/MC-049/outcome.json','ecf9e2fad37adcf4f71c8fc4e1399d57ce1fc93f','COMPLETED_RESEARCH'),
}
EXPECTED_BLOCKERS = {'PB-007-01','PB-007-02','PB-007-03','RB-016-02','RB-016-03','RB-016-04'}
EXPECTED_LEAVES = {'MC031-A','MC031-B','MC031-C','MC032-A','MC032-B','MC032-C','MC033-A','MC033-B','CTRL-026-A','CERT-026-A'}
EXPECTED_ARTIFACTS = {
    'research/machining-completeness/tasks/MC-026/candidate-selection-contract-v1.json',
    'research/machining-completeness/tasks/MC-026/selection_model.py',
    'research/machining-completeness/tasks/MC-026/report.md',
    'research/machining-completeness/tasks/MC-026/outcome.json',
    'research/machining-completeness/tasks/MC-026/verify.py',
    'docs/machining-completeness/23-MC026-CANDIDATE-SELECTION.md',
}

def load(p): return json.loads(p.read_text(encoding='utf-8'))
def blob(p):
    b=p.read_bytes()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def model():
    spec=importlib.util.spec_from_file_location('mc026_selection', MODEL)
    mod=importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod
def required_operations():
    d=load(DOMAIN)
    return set(d['coverage_rule']['required_operation_ids'])

def validate_contract(c, check_files=True):
    assert c['schema']=='radicadsac-mc026-candidate-selection/1.0'
    assert c['task']=='MC-026' and c['issue']==88 and c['source_baseline']==EXPECTED_BASELINE
    assert c['result']=='COMPLETED_RESEARCH_SELECTION_WITH_OPEN_GAPS'
    assert c['native_execution'] is False and c['native_or_paid_campaign_run'] is False
    da=c['domain_authority']
    assert da['path']=='research/machining-completeness/tasks/MC-002/domain-contract-v1.json'
    assert da['blob_sha']==EXPECTED_DOMAIN_BLOB
    if check_files:
        assert blob(DOMAIN)==EXPECTED_DOMAIN_BLOB, 'MC-002 domain authority drift'
    deps={d['task']:d for d in c['formal_dependencies']}
    assert set(deps)==set(EXPECTED_DEPS)
    for t,(p,s,r) in EXPECTED_DEPS.items():
        assert deps[t]=={'task':t,'path':p,'blob_sha':s,'result_kind':r}
        if check_files:
            fp=ROOT/p
            assert fp.is_file() and blob(fp)==s, f'{t} dependency blob drift'
            assert load(fp)['result_kind']==r
    s=c['selection']; p=s['primary']
    assert p['id']=='PRIMARY_CERTIFIED_ADAPTIVE_IMPLICIT'
    assert p['may_claim_total_success'] is False
    assert {'PB-007-01','PB-007-02','PB-007-03','UNCERTIFIED','RESOURCE_REFUSAL','SEMANTIC_BLOCKER'} <= set(p['terminal_fail_closed'])
    ch=s['challenger']
    assert ch['id']=='EXACT_CELL_SEMIALGEBRAIC_CONTROL' and ch['basis_task']=='MC-024'
    assert ch['may_become_primary_by_agreement'] is False and ch['may_claim_total_domain'] is False
    independence=' '.join(ch['independence_requirements']).lower()
    for token in ('separate material representation','separate certificate','no shared adaptive-cell classification code'):
        assert token in independence
    acc={x['id']:x for x in s['derived_accelerators']}
    assert set(acc)=={'DIRECTIONAL_INTERVAL_INDEX','NATIVE_MESH_BOOLEAN','SPARSE_LEVELSET'}
    assert all(x['canonical_authority'] is False for x in acc.values())
    fd=s['fast_path_dispatch']
    assert fd['basis_task']=='MC-030' and fd['unique_general_route']==p['id']
    assert fd['cycles_allowed'] is False and fd['fast_success_requires_independent_material_certificate'] is True
    assert fd['max_fast_invocations']==1 and fd['max_general_invocations']==1
    freeze=c['challenge_freeze']
    assert freeze['basis_task']=='MC-049'
    assert freeze['custody']=='PUBLIC_PRESELECTION_PREREGISTRATION'
    assert freeze['generated_challenge_count']==64 and freeze['executed_by_mc026'] is False
    assert freeze['candidate_identity_is_generator_input'] is False
    assert freeze['later_independent_execution_owner']=='MC-057'
    required=required_operations()
    classes={x['id']:x for x in c['routing_classes']}
    assert set(classes)=={'LATHE_AXISYMMETRIC_OR_GENERAL','LATHE_PHASE_OR_GENERAL','MILL_ANALYTIC_OR_GENERAL','MILL_FORM_OR_GENERAL','COMPOSITION_AND_GENERAL'}
    routed=[]
    for x in classes.values():
        routed.extend(x['operations'])
        assert x['primary']==p['id']
        assert set(x['open_gaps']) <= EXPECTED_BLOCKERS
    assert len(routed)==len(set(routed))
    assert set(routed)==required
    assert classes['LATHE_PHASE_OR_GENERAL']['fast_path']=='FP-LATHE-PHASE-BOUNDED'
    assert set(classes['LATHE_PHASE_OR_GENERAL']['open_gaps'])=={'PB-007-01','PB-007-02'}
    assert classes['MILL_FORM_OR_GENERAL']['fast_path']=='FP-FORM-BOX-UNION'
    assert 'PB-007-03' in classes['MILL_FORM_OR_GENERAL']['open_gaps']
    assert set(c['global_output_gaps'])=={'RB-016-02','RB-016-03','RB-016-04'}
    leaves={x['id']:x for x in c['leaf_blueprints']}
    assert set(leaves)==EXPECTED_LEAVES
    assert len(leaves)==len(c['leaf_blueprints'])
    for leaf in leaves.values():
        assert leaf['owner_task'] in {'MC-031','MC-032','MC-033'}
        assert len(leaf['acceptance']) >= 2
    assert leaves['CTRL-026-A']['owner_task']=='MC-031'
    assert leaves['CERT-026-A']['owner_task']=='MC-032'
    gaps={x['id']:x for x in c['open_gaps']}
    assert set(gaps)==EXPECTED_BLOCKERS
    assert all(x['status'].startswith('OPEN') for x in gaps.values())
    assert c['capability_state']['MC-A']=='ACCEPTED'
    for gate in ('MC-B','MC-C','MC-D','MC-E','MC-F','MC-1'):
        assert c['capability_state'][gate]=='NOT_ESTABLISHED'
    protected=' '.join(c['protected_semantics']).lower()
    for token in ('source/audio/provenance','canonical journal','positive-volume','durable body','step remains mandatory'):
        assert token in protected

def model_controls():
    m=model(); required=required_operations()
    assert m.REQUIRED_OPERATIONS==required
    for op in required:
        p=m.plan({'operation_id':op})
        assert p['terminal'] is None and p['primary']==m.PRIMARY
        assert p['cycles_allowed'] is False
        assert p['max_fast_invocations']==1 and p['max_general_invocations']==1
    assert m.plan({'operation_id':'not-in-D'})['terminal']==m.INVALID
    assert m.plan({'operation_id':'mill_face','source_bound':False})['terminal']=='INVALID_SOURCE'
    assert m.plan({'operation_id':'mill_face','common_frame_bound':False})['terminal']=='INVALID_SOURCE'
    p=m.plan({'operation_id':'lathe_threading_synchronized'})
    assert p['requires_critical_event_service'] is True
    assert m.fast_candidate('lathe_threading_synchronized')=='FP-LATHE-PHASE-BOUNDED'
    p=m.plan({'operation_id':'mill_accessible_undercut'})
    assert p['open_source_codec_gap']=='PB-007-03'
    p=m.plan({'operation_id':'lathe_parting_cutthrough'})
    assert p['requires_body_state_machine'] is True
    p=m.plan({'operation_id':'mill_face','semialgebraic_proved':True}); assert p['challenger']==m.CHALLENGER
    p=m.plan({'operation_id':'mill_face','semialgebraic_proved':False}); assert p['challenger'] is None
    req={'operation_id':'mill_face','fast_predicate_satisfied':True}
    out=m.dispatch(req,fast_result='SUCCESS',fast_certificate='ACCEPTED')
    assert out['terminal']=='FAST_SUCCESS_CERTIFIED' and out['fast_invocations']==1 and out['general_invocations']==0
    out=m.dispatch(req,fast_result='SUCCESS',fast_certificate='UNCERTIFIED',general_result='PB-007-01')
    assert out['terminal']=='PB-007-01' and out['fast_invocations']==1 and out['general_invocations']==1
    out=m.dispatch({'operation_id':'mill_face'},general_result='RESOURCE_REFUSAL',accelerator_result='SUCCESS')
    assert out['terminal']=='RESOURCE_REFUSAL' and out['accelerator_is_authority'] is False
    out=m.dispatch({'operation_id':'mill_face','semialgebraic_proved':True},general_result='UNCERTIFIED',challenger_result='SUCCESS_CERTIFIED')
    assert out['terminal']=='UNCERTIFIED' and out['challenger_evidence']=='SUCCESS_CERTIFIED'

def validate_repository():
    o=load(OUTCOME)
    assert o['task']=='MC-026' and o['result_kind']=='COMPLETED_RESEARCH' and o['issue']==88 and o['source_baseline']==EXPECTED_BASELINE
    assert o['native_execution'] is False and o['resources']['native_or_paid_campaign_run'] is False
    assert o['resources']['required_domain_operation_count']==len(required_operations())
    assert o['resources']['leaf_blueprint_count']==len(EXPECTED_LEAVES)
    assert {b['id'] for b in o['blockers']}==EXPECTED_BLOCKERS
    r=load(REGISTRY)['tasks']['MC-026']
    assert r['state']=='COMPLETED_RESEARCH' and r['issue']==88
    assert set(r['accepted_artifacts'])==EXPECTED_ARTIFACTS
    assert {b['id'] for b in r['blockers']}==EXPECTED_BLOCKERS
    wf=WORKFLOW.read_text(encoding='utf-8')
    assert 'tasks/MC-026/selection_model.py' in wf
    assert 'tasks/MC-026/verify.py' in wf
    assert 'mc_workflow.py verify MC-026' in wf
    for text in (REPORT.read_text(encoding='utf-8'),DOC.read_text(encoding='utf-8')):
        low=text.lower()
        for token in ('primary_certified_adaptive_implicit','exact_cell_semialgebraic_control','pb-007-01','pb-007-02','pb-007-03','rb-016-02','rb-016-03','rb-016-04','not_established','source/audio/provenance'):
            assert token in low
    model_controls()

def expect_rejected(mut):
    c=copy.deepcopy(load(CONTRACT)); mut(c)
    try: validate_contract(c,False)
    except Exception: return
    raise AssertionError('adversarial mutation accepted')

def self_test():
    validate_contract(load(CONTRACT),False)
    attacks=[
        lambda c:c['selection']['primary'].__setitem__('may_claim_total_success',True),
        lambda c:c['selection']['challenger'].__setitem__('may_claim_total_domain',True),
        lambda c:c['selection']['challenger'].__setitem__('independence_requirements',['same classifier']),
        lambda c:c['selection']['fast_path_dispatch'].__setitem__('cycles_allowed',True),
        lambda c:c['selection']['fast_path_dispatch'].__setitem__('max_general_invocations',2),
        lambda c:c['selection']['derived_accelerators'][0].__setitem__('canonical_authority',True),
        lambda c:c['challenge_freeze'].__setitem__('generated_challenge_count',63),
        lambda c:c['challenge_freeze'].__setitem__('candidate_identity_is_generator_input',True),
        lambda c:c['routing_classes'][0].__setitem__('operations',c['routing_classes'][0]['operations'][:-1]),
        lambda c:c['open_gaps'].__setitem__(0,{**c['open_gaps'][0],'status':'CLOSED'}),
        lambda c:c['capability_state'].__setitem__('MC-B','ACCEPTED'),
        lambda c:c['leaf_blueprints'][0].__setitem__('owner_task','MC-999'),
    ]
    for attack in attacks: expect_rejected(attack)
    model_controls()
    print('MC-026 adversarial self-test passed')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--contract',action='store_true'); ap.add_argument('--self-test',action='store_true'); a=ap.parse_args()
    if not (a.contract or a.self_test): ap.error('choose --contract or --self-test')
    if a.contract:
        validate_contract(load(CONTRACT)); validate_repository(); print('MC-026 contract verification passed')
    if a.self_test: self_test()
if __name__=='__main__': main()
