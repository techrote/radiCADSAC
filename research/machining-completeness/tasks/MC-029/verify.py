#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, json
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
TASK=ROOT/'research'/'machining-completeness'/'tasks'/'MC-029'
CONTRACT=TASK/'sparse-levelset-falsification-v1.json'
OUTCOME=TASK/'outcome.json'
REPORT=TASK/'report.md'
DOC=ROOT/'docs'/'machining-completeness'/'21-MC029-SPARSE-VOLUME-LEVELSET.md'
REGISTRY=ROOT/'research'/'machining-completeness'/'outcomes-v1.json'
WORKFLOW=ROOT/'.github'/'workflows'/'mc1-static.yml'
EXPECTED_BASELINE='4f99c99b524049a9e288416f6329e2b14badaded'
EXPECTED_DEPS={
'MC-010':('research/machining-completeness/tasks/MC-010/outcome.json','4960730316f89dbb3fbf958d054127fa4fc0d789','COMPLETED_RESEARCH'),
'MC-016':('research/machining-completeness/tasks/MC-016/outcome.json','606a7d0b8be61131b2272f2eb161d6a4dbba703a','COMPLETED_RESEARCH'),
'MC-018':('research/machining-completeness/tasks/MC-018/outcome.json','085f864b4bd58b38f154b6c9d58d9e68b60ee7ec','COMPLETED_RESEARCH'),
'MC-019':('research/machining-completeness/tasks/MC-019/outcome.json','4456c964315c10b46ce61a5a8d4a45e8025730b7','COMPLETED_RESEARCH'),
'MC-020':('research/machining-completeness/tasks/MC-020/outcome.json','19504a35f47bca710bb6369abb723de83d1afede','COMPLETED_RESEARCH')}
EXPECTED_BLOCKERS={'PB-007-03','RB-016-02','RB-016-03','RB-016-04'}
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def q(x):
    if isinstance(x,bool) or isinstance(x,float): raise AssertionError('authority quantity must not be bool/binary float')
    return x if isinstance(x,Fraction) else Fraction(x)
def reject_float(x):
    if isinstance(x,float): raise AssertionError('binary float forbidden in decisive MC-029 contract data')
    if isinstance(x,dict):
        for v in x.values(): reject_float(v)
    elif isinstance(x,list):
        for v in x: reject_float(v)
def blob(p):
    b=p.read_bytes(); return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def overlap(a,b): return max(Fraction(0),min(q(a[1]),q(b[1]))-max(q(a[0]),q(b[0])))
def validate_contract(c,check_files=True):
    reject_float(c)
    assert c['schema']=='radicadsac-mc029-sparse-volume-levelset-falsification/1.0'
    assert c['task']=='MC-029' and c['issue']==91 and c['source_baseline']==EXPECTED_BASELINE
    assert c['result']=='NEGATIVE_RESULT_AS_TOTAL_MATERIAL_AUTHORITY'
    assert c['native_execution'] is False and c['native_or_paid_campaign_run'] is False
    deps={d['task']:d for d in c['formal_dependencies']}; assert set(deps)==set(EXPECTED_DEPS)
    for t,(p,s,r) in EXPECTED_DEPS.items():
        assert deps[t]=={'task':t,'path':p,'blob_sha':s,'result_kind':r}
        if check_files:
            fp=ROOT/p; assert fp.is_file() and blob(fp)==s, f'{t} dependency blob drift'; assert load(fp)['result_kind']==r
    cand=c['candidate']; assert cand['sole_material_authority'] is False and cand['primary_engineering_output_authority'] is False
    assert cand['sampling_resolution_is_authority'] is False and cand['refinement_convergence_is_exact_equality'] is False
    assert cand['extracted_surface_is_canonical_material'] is False and cand['voxel_components_are_durable_body_identity'] is False
    err=c['error_contract']; assert err['formula']=='e_total = e_source + e_sampling + e_resampling + e_extraction'
    assert err['all_terms_nonnegative'] is True and err['unknown_term_result']=='UNCERTIFIED'
    assert not err['error_scalar_may_decide_topology'] and not err['error_scalar_may_delete_positive_material'] and not err['error_scalar_may_fuse_exact_zero_contacts']
    topo=c['topology_contract']; assert topo['same_corner_sign_implies_uniform_cell'] is False and topo['surface_extraction_success_implies_topology_correctness'] is False and topo['component_label_is_durable_identity'] is False
    micro=c['exact_controls']['hidden_microfeature']; a,b=map(q,micro['cell']); x0,x1=map(q,micro['positive_feature'])
    assert a < x0 < x1 < b and x1-x0==q(micro['feature_width'])==Fraction(1,500000)
    assert micro['sample_nodes']==micro['cell'] and micro['sample_node_membership_without_feature']==micro['sample_node_membership_with_feature']==[False,False]
    z=c['exact_controls']['zero_contact']; assert overlap(z['stock_interval'],z['tangent_sweep_interval'])==q(z['tangent_positive_overlap'])==0
    assert overlap(z['stock_interval'],z['penetrating_sweep_interval'])==q(z['penetrating_positive_overlap'])==Fraction(1,1000000)
    assert overlap(z['stock_interval'],z['separated_sweep_interval'])==q(z['separated_positive_overlap'])==0
    eb=c['exact_controls']['error_budget']; total=sum(q(eb[k]) for k in ('e_source','e_sampling','e_resampling','e_extraction')); assert total==q(eb['e_total'])==Fraction(1,500000)
    ref=c['exact_controls']['refinement']; assert q(ref['refined_pitch']) < q(ref['initial_pitch']); assert q(ref['positive_feature_width']) < q(ref['refined_pitch'])
    assert set(c['required_fail_closed_states'])=={'UNCERTIFIED_SAMPLING','UNCERTIFIED_RESAMPLING','UNCERTIFIED_EXTRACTION','TOPOLOGY_UNCERTIFIED','SOURCE_RELATION_UNAVAILABLE'}
    assert {b['id'] for b in c['blockers']}==EXPECTED_BLOCKERS and all(b['status'].startswith('OPEN') for b in c['blockers'])
    assert c['capability_state']['MC-A']=='ACCEPTED'
    for g in ('MC-B','MC-C','MC-D','MC-E','MC-F','MC-1'): assert c['capability_state'][g]=='NOT_ESTABLISHED'
    role=' '.join(c['retained_role']['requirements']).lower()
    for s in ('source-faithful','e_source','positive-volume','topology','step','fail'): assert s in role
    prot=' '.join(c['protected_semantics']).lower()
    for s in ('source/audio/provenance','canonical operation journal','positive-volume','durable body','step remains mandatory'): assert s in prot

def validate_repository():
    o=load(OUTCOME); assert o['task']=='MC-029' and o['result_kind']=='NEGATIVE_RESULT' and o['issue']==91 and o['source_baseline']==EXPECTED_BASELINE
    assert o['native_execution'] is False and o['resources']['native_or_paid_campaign_run'] is False and {b['id'] for b in o['blockers']}==EXPECTED_BLOCKERS
    r=load(REGISTRY)['tasks']['MC-029']; assert r['state']=='NEGATIVE_RESULT' and r['issue']==91 and {b['id'] for b in r['blockers']}==EXPECTED_BLOCKERS
    expected={'research/machining-completeness/tasks/MC-029/sparse-levelset-falsification-v1.json','research/machining-completeness/tasks/MC-029/report.md','research/machining-completeness/tasks/MC-029/outcome.json','research/machining-completeness/tasks/MC-029/verify.py','docs/machining-completeness/21-MC029-SPARSE-VOLUME-LEVELSET.md'}
    assert set(r['accepted_artifacts'])==expected
    wf=WORKFLOW.read_text(); assert 'tasks/MC-029/verify.py' in wf and 'mc_workflow.py verify MC-029' in wf
    for text in (REPORT.read_text(),DOC.read_text()):
        low=text.lower()
        for s in ('negative_result','resolution','resampling','extraction','1/500000','rb-016-02','rb-016-03','rb-016-04','pb-007-03','not_established','step','source/audio/provenance'): assert s in low

def expect_rejected(mut):
    c=copy.deepcopy(load(CONTRACT)); mut(c)
    try: validate_contract(c,False)
    except Exception: return
    raise AssertionError('adversarial mutation accepted')
def self_test():
    validate_contract(load(CONTRACT),False)
    attacks=[
      lambda c:c['candidate'].__setitem__('sole_material_authority',True),
      lambda c:c['topology_contract'].__setitem__('same_corner_sign_implies_uniform_cell',True),
      lambda c:c['error_contract'].__setitem__('formula','e_total = e_sampling'),
      lambda c:c['exact_controls']['error_budget'].__setitem__('e_source','0'),
      lambda c:c['candidate'].__setitem__('refinement_convergence_is_exact_equality',True),
      lambda c:c['candidate'].__setitem__('voxel_components_are_durable_body_identity',True),
      lambda c:c['capability_state'].__setitem__('MC-B','ACCEPTED'),
      lambda c:c['blockers'].__setitem__(0,{**c['blockers'][0],'status':'CLOSED'}),
      lambda c:c['exact_controls']['error_budget'].__setitem__('e_sampling',0.5)]
    for a in attacks: expect_rejected(a)
    print('MC-029 adversarial self-test passed')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--contract',action='store_true'); ap.add_argument('--self-test',action='store_true'); a=ap.parse_args()
    if not (a.contract or a.self_test): ap.error('choose --contract or --self-test')
    if a.contract: validate_contract(load(CONTRACT)); validate_repository(); print('MC-029 contract verification passed')
    if a.self_test: self_test()
if __name__=='__main__': main()
