#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, importlib.util, json, sys
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
CONTRACT_PATH=HERE/'multi-setup-composition-contract-v1.json'
IMPL_PATH=HERE/'multi_setup.py'

def load_module(path,name):
    spec=importlib.util.spec_from_file_location(name,path); assert spec and spec.loader
    mod=importlib.util.module_from_spec(spec); sys.modules[name]=mod; spec.loader.exec_module(mod); return mod

def blob_sha(path):
    data=path.read_bytes(); return hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()

def validate_contract(c):
    e=[]
    if c.get('schema')!='radicadsac-mc023-multi-setup-composition/1.0': e.append('schema')
    if c.get('task')!='MC-023' or c.get('issue')!=85: e.append('identity')
    if c.get('source_baseline')!='318f9173466c20116236167183d8524e076e34c0': e.append('baseline')
    if c.get('native_execution') is not False: e.append('native')
    deps={d.get('task'):d for d in c.get('formal_dependencies',[])}
    exp={'MC-005':('adec886597a06345fdfdf65ee018596cd396d249','CAPABILITY_ACCEPTED'),'MC-010':('4960730316f89dbb3fbf958d054127fa4fc0d789','COMPLETED_RESEARCH'),'MC-058':('038fccda9142650ee7e29c626aeb8e4602420278','COMPLETED_RESEARCH')}
    if set(deps)!=set(exp): e.append('deps')
    else:
        for k,(sha,kind) in exp.items():
            if deps[k].get('blob_sha')!=sha or deps[k].get('result_kind')!=kind: e.append('dep:'+k)
    s=c.get('source_semantics',{})
    for k in ('saved_operations_immutable','single_parent_revisions','reclamp_is_non_cutting_journal_event','machine_transition_is_non_cutting_journal_event','common_frame_is_durable_workpiece_semantics','exact_input_revision_binding_required','exact_target_body_id_binding_required'):
        if s.get(k) is not True: e.append(k)
    for k in ('backend_topology_identity_as_durable_authority','largest_body_or_only_body_guess_allowed','historical_transform_mutation_allowed','binary_float_certifying_authority','global_epsilon_identity_authority'):
        if s.get(k) is not False: e.append(k)
    t=c.get('transform_contract',{})
    if t.get('mapping')!='p_common = R_setup * p_local + t_setup' or t.get('handedness')!='right-handed': e.append('transform')
    if t.get('inverse_may_not_replace_forward_mapping') is not True or t.get('reflection_as_rotation_allowed') is not False: e.append('transform_guard')
    b=c.get('material_body_contract',{})
    for k in ('journal_body_id_backend_independent','semantic_lineage_backend_independent','cuts_mutate_only_bound_target_body','unrelated_bodies_preserved','connectivity_change_requires_explicit_material_body_transition','ambiguous_lineage_must_remain_explicit','detached_material_may_not_be_silently_discarded'):
        if b.get(k) is not True: e.append(k)
    if b.get('kernel_shape_order_as_target_selector') is not False: e.append('kernel_target')
    p=c.get('provider_composition',{})
    if p.get('lathe_to_mill_transition_supported') is not True or p.get('provider_geometry_reinterpreted_in_place') is not False or p.get('open_provider_blockers_propagate') is not True: e.append('provider_composition')
    x=c.get('mc058_transfer',{})
    if x.get('formula')!='e_total = e_inherited + e_translation + rho*e_rotation + e_tool': e.append('formula')
    if x.get('error_reset_at_reclamp') is not False or x.get('error_reset_at_machine_transition') is not False or x.get('unknown_error_becomes_zero') is not False: e.append('error_reset')
    prot=c.get('protected_semantics',{})
    for k in ('historical_source_audio_provenance_unchanged','canonical_journal_immutable','positive_volume_preserved','durable_body_lineage_preserved','negative_results_preserved'):
        if prot.get(k) is not True: e.append(k)
    if prot.get('native_geometry_claim') is not False: e.append('native_claim')
    ps=c.get('programme_state',{})
    if ps.get('MC-A')!='ACCEPTED': e.append('MC-A')
    for g in ('MC-B','MC-C','MC-D','MC-E','MC-F','MC-1'):
        if ps.get(g)!='NOT_ESTABLISHED': e.append(g)
    a=c.get('acceptance',{})
    if not all(a.get(k) is True for k in ('reoriented_full_3d_controls_preserve_material_body_semantics','task_specific_artifacts_validate_without_chat','negative_results_and_unresolved_claims_preserved')): e.append('acceptance')
    return e

def bound_dependencies(c):
    for d in c['formal_dependencies']:
        p=ROOT/d['path']; assert p.exists(),d['path']; assert blob_sha(p)==d['blob_sha'],d['task']

def exact_controls():
    m=load_module(IMPL_PATH,'mc023_impl')
    I=m.RigidTransform.identity()
    T=m.RigidTransform(((0,-1,0),(1,0,0),(0,0,1)),(4,0,0))
    assert T.apply((0,0,0))==(Fraction(4),Fraction(0),Fraction(0))
    p=(Fraction(2,3),Fraction(5,7),Fraction(11,13)); assert T.inverse().apply(T.apply(p))==p
    local=m.Box((0,0,0),(4,1,4)); assert local.transform(T)==m.Box((3,0,0),(4,4,4))
    assert T.apply((Fraction(1,2),Fraction(1,2),0))!=(T.inverse().apply((Fraction(1,2),Fraction(1,2),0)))
    U=m.RigidTransform(((1,0,0),(0,0,-1),(0,1,0)),(0,6,0))
    assert T.compose(U).apply((1,2,3)) != U.compose(T).apply((1,2,3))
    try: m.RigidTransform(((1,0,0),(0,1,0),(0,0,-1)),(0,0,0))
    except ValueError: pass
    else: raise AssertionError('reflection admitted')
    A=m.Body('A','L-A',(m.Box((0,0,0),(4,4,4)),))
    B=m.Body('B','L-B',(m.Box((10,0,0),(12,2,2)),))
    s0=m.Setup('S0','LATHE',I,Fraction(1,4000))
    w=m.Workpiece('R0',(A,B),s0)
    c1=m.Cut('lathe-cut','R0','A','LATHE_CONTROL',(m.Box((0,0,0),(1,4,4)),))
    w1=m.apply_cut(w,c1)
    assert not w1.body('A').material_at((Fraction(1,2),2,2))
    assert w1.body('A').material_at((2,2,2))
    assert w1.body('B').material_at((11,1,1))
    s1=m.Setup('S1','MILL',T,Fraction(1,4000))
    w2=m.reclamp(w1,'reclamp-lathe-to-mill',s1)
    assert w2.bodies==w1.bodies and w2.journal[-1]=='reclamp-lathe-to-mill'
    c2=m.Cut('mill-cut',w2.revision,'A','MILL_CONTROL',(local,))
    w3=m.apply_cut(w2,c2)
    assert w3.body('A').material_at((2,2,2))
    assert not w3.body('A').material_at((Fraction(7,2),2,2))
    assert w3.body('B').material_at((11,1,1))
    d=Fraction(1,1000000)
    assert w3.body('A').material_at((3-d,2,2))
    assert not w3.body('A').material_at((3,2,2))
    assert not w3.body('A').material_at((3+d,2,2))
    try: m.apply_cut(w3,m.Cut('stale','R0','A','X',(local,)))
    except ValueError: pass
    else: raise AssertionError('stale revision admitted')
    try: m.apply_cut(w3,m.Cut('missing',w3.revision,'NOPE','X',(local,)))
    except ValueError: pass
    else: raise AssertionError('missing target guessed')
    assert m.actual_sweep_error_bound(Fraction(1,4000),Fraction(1,1000),5,Fraction(1,10000),Fraction(1,2000))==Fraction(9,4000)
    for bad in (0.25, True):
        try: m.q(bad)
        except TypeError: pass
        else: raise AssertionError('binary/bool authority admitted')

def adversarial(c):
    muts=[]
    def add(fn): x=copy.deepcopy(c); fn(x); muts.append(x)
    add(lambda x:x['source_semantics'].__setitem__('saved_operations_immutable',False))
    add(lambda x:x['source_semantics'].__setitem__('largest_body_or_only_body_guess_allowed',True))
    add(lambda x:x['source_semantics'].__setitem__('binary_float_certifying_authority',True))
    add(lambda x:x['transform_contract'].__setitem__('mapping','p_local = R * p_common + t'))
    add(lambda x:x['transform_contract'].__setitem__('reflection_as_rotation_allowed',True))
    add(lambda x:x['material_body_contract'].__setitem__('cuts_mutate_only_bound_target_body',False))
    add(lambda x:x['material_body_contract'].__setitem__('kernel_shape_order_as_target_selector',True))
    add(lambda x:x['provider_composition'].__setitem__('provider_geometry_reinterpreted_in_place',True))
    add(lambda x:x['provider_composition'].__setitem__('open_provider_blockers_propagate',False))
    add(lambda x:x['mc058_transfer'].__setitem__('error_reset_at_reclamp',True))
    add(lambda x:x['protected_semantics'].__setitem__('positive_volume_preserved',False))
    add(lambda x:x['programme_state'].__setitem__('MC-B','ACCEPTED'))
    for i,x in enumerate(muts): assert validate_contract(x),f'mutation {i} escaped'

def main():
    ap=argparse.ArgumentParser(); g=ap.add_mutually_exclusive_group(required=True); g.add_argument('--contract',action='store_true'); g.add_argument('--self-test',action='store_true'); a=ap.parse_args()
    c=json.loads(CONTRACT_PATH.read_text()); errs=validate_contract(c)
    if errs: raise SystemExit('MC-023 contract invalid: '+', '.join(errs))
    exact_controls(); adversarial(c)
    if a.contract: bound_dependencies(c)
    print('MC-023 verification passed'); return 0
if __name__=='__main__': raise SystemExit(main())
