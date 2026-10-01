#!/usr/bin/env python3
"""Actual predecessor lowering and whole-child composition; no mocked acceptance."""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import copy
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pb00701_algebraic_monotone_cut_model as m
import pb00701_algebraic_monotone_cut_certificate as checker
import pb00701_algebraic_endpoint_model as v46
import pb00701_algebraic_orientation_cut_model as v44
import test_pb00701_algebraic_monotone_cut as core
import test_pb00701_algebraic_orientation_cut_adversarial as old44
import test_pb00701_correlated_closed_handoff_adversarial as old43
import test_pb00701_multiharmonic_monotone_anchor_adversarial as base

a=m.a


def source(args):
    c,s,ident,span,offset,rate=args
    spec=base._spec(c,s,offset=str(offset),rate=str(rate),source_parameter_id=ident)
    lo,hi=map(Q,span)
    spec['parameter_lo'],spec['parameter_hi']=str(lo),str(hi)
    for channel in ('cos_splines','sin_splines'):
        for spline in spec[channel].values():
            spline['knots']=[str(lo+(hi-lo)*Q(k)) for k in spline['knots']]
    return spec


def reverse_poly(p):
    out=[Q(0)]*len(p)
    for k,c in enumerate(p):
        for j in range(k+1):out[j]+=Q(c)*comb(k,j)*(-1)**j
    return a.trim(out)


def route(result):
    rows=[s['route'] for s in result.get('spans',[]) if s.get('route_kind')=='PB00701_V47_EXACT_ALGEBRAIC_SINGLE_CUT']
    assert rows and result['status']=='CERTIFIED',result
    return rows[0]


def physical_root_args(power=1):
    p=[-1,1,1];b=[Q(1)]
    for _ in range(power):b=a.pmul(b,p)
    A=a.pscale(a.pmul(b,p),Q(1,100))
    return ({1:a.padd(A,b),2:a.pscale(a.pmul(b,p),Q(1,10**8))},
            {1:a.padd(A,a.pscale(b,-1))},'physical-zero',('0','1'),'-1/8','1/16')


class WholeChildTests(unittest.TestCase):
    def test_genuine_predecessor_residual_parent_now_certified(self):
        args=core.candidate_args();spec=source(args)
        prior=v46.classify_required_analytic_event(spec)
        self.assertEqual(prior['status'],'BLOCKED')
        self.assertTrue(any(s.get('route',{}).get('relation')==v44.V44_ROUTE for s in prior['spans']))
        result=m.classify_required_analytic_event(spec);proof=route(result)
        self.assertEqual([c['derivative_certificate']['mode'] for c in proof['children']],['V42','V43'])
        self.assertEqual(proof['bisection']['field']['minimal_polynomial'],[-1250,5000,1])
        self.assertEqual(proof['endpoint_evidence'][1]['relation'],'NEGATIVE')
        self.assertEqual(proof['endpoint_evidence'][1]['physical_multiplicity'],0)
        self.assertEqual(proof['distinct_roots_open'],1)
        self.assertEqual(proof['internal_cut_roots'],[])
        self.assertTrue(proof['analytic_single_cut_consumed'])
        self.assertFalse(proof['full_multi_cut_partition_claimed'])
        self.assertTrue(checker.validate_single_cut_event(proof,*args))
        print('v47 genuine residual: V42 left / V43 right; 1 open physical root; irrational proof cut nonzero')

    def test_reverse_direction_negation_and_global_source_coordinates(self):
        original=core.candidate_args()
        for reversal,negative,global_span in ((True,False,False),(False,True,False),(False,False,True)):
            c,s=original[0],original[1];off,rate=Q(original[4]),Q(original[5]);span=('0','1')
            if reversal:
                c={h:reverse_poly(p) for h,p in c.items()};s={h:reverse_poly(p) for h,p in s.items()};off,rate=off+rate,-rate
            if negative:
                c={h:a.pscale(p,-1) for h,p in c.items()};s={h:a.pscale(p,-1) for h,p in s.items()}
            if global_span:span=('2','5');off,rate=off-rate*Q(2,3),rate/3
            args=(c,s,'transformed-s',span,str(off),str(rate))
            proof=route(m.classify_required_analytic_event(source(args)))
            self.assertEqual(proof['distinct_roots_open'],1)
            self.assertEqual(proof['children'][0]['summary']['derivative_sign'],-1 if reversal or negative else 1)
            self.assertTrue(checker.validate_single_cut_event(proof,*args))

    def test_zero_open_and_external_endpoint_roots(self):
        original=list(core.candidate_args())
        original[0]=dict(original[0]);original[0][0]=[1]
        neutral=m.build_single_cut_event(*original)
        self.assertEqual(neutral['status'],'CERTIFIED')
        self.assertEqual(neutral['total_distinct_roots_closed'],0)
        self.assertTrue(checker.validate_single_cut_event(neutral,*original))
        A=[Q(-1,10000),Q(1,10000),Q(1,10000)]
        eps=Q(1,10**9)
        # Keep orientation polynomials away from rational endpoint roots, which
        # the preserved v44 irrational-cut producer does not handle. At the
        # rational turn -1/8, C3*cos(3*theta) exactly cancels sqrt(2)*B.
        for endpoint,B,off,c3 in (('left',[eps,Q(7,20)],'-1/8',2*eps),('right',[-Q(7,20)-eps,Q(7,20)],'-3/16',-2*eps)):
            args=({1:a.padd(A,B),2:[Q(1,10**8)],3:[c3]},{1:a.padd(A,a.pscale(B,-1))},'external-root',('0','1'),off,'1/16')
            result=m.build_single_cut_event(*args)
            self.assertEqual(result['status'],'CERTIFIED',result)
            self.assertEqual(result['endpoint_root_multiplicity'],{endpoint:1})
            self.assertEqual(result['distinct_roots_open'],0)
            self.assertEqual(result['total_distinct_roots_closed'],1)
            self.assertTrue(checker.validate_single_cut_event(result,*args))

    def test_physical_internal_root_once_and_multiple_root_not_monotone(self):
        args=physical_root_args();proof=m.build_single_cut_event(*args)
        self.assertEqual(proof['status'],'CERTIFIED',proof)
        self.assertEqual(proof['endpoint_evidence'][1]['relation'],'ZERO')
        self.assertEqual(proof['endpoint_evidence'][1]['physical_multiplicity'],1)
        self.assertEqual(proof['distinct_roots_open'],1)
        self.assertEqual(len(proof['internal_cut_roots']),1)
        self.assertEqual(sum(c['summary']['distinct_roots_open'] for c in proof['children']),0)
        self.assertEqual({x['coordinate']:x['multiplicity'] for x in proof['bisection']['orientation_ownership']},{'A':2,'B':1})
        self.assertTrue(checker.validate_single_cut_event(proof,*args))
        multiple=physical_root_args(2)
        ep=v46.build_source_endpoint_evidence(*multiple)
        self.assertEqual(ep['status'],'ENDPOINTS_CERTIFIED')
        self.assertEqual(ep['endpoints'][0]['physical_multiplicity'],2)
        self.assertEqual(m.build_single_cut_event(*multiple)['status'],'BLOCKED')
        bad=copy.deepcopy(proof);bad['endpoint_evidence'][1]['physical_multiplicity']=2
        with self.assertRaises(ValueError):checker.validate_single_cut_event(bad,*args)

    def test_source_certificates_and_composition_corruption(self):
        args=core.candidate_args();proof=m.build_single_cut_event(*args)
        mutations=[
            (['source_parameter_id'],'another-source'),
            (['source_material','phase_turn_law','offset'],'0'),
            (['bisection','field','minimal_polynomial'],[-1,0,2]),
            (['bisection','field','isolating_interval'],['1/4','1/2']),
            (['bisection','children',0,'parent_local_map','width'],['1/4']),
            (['children',0,'map','parent_source_map','width'],['1/4']),
            (['children',0,'derivative_certificate','phase_cell','cell_index'],99),
            (['children',0,'derivative_certificate','orthants'],[]),
            (['children',0,'derivative_certificate','orthants',0,'certificate','sturm_sequence'],[['1']]),
            (['children',0,'derivative_certificate','orthants',0,'certificate','variations'],[8,8]),
            (['children',0,'derivative_certificate','retained_nonanchor_channels'],[]),
            (['children',1,'derivative_certificate','constraints',0,'certificate','weak_sign'],-1),
            (['children',0,'summary','distinct_roots_open'],3),
            (['children',1,'summary','left_event','relation'],'POSITIVE'),
            (['endpoint_evidence',1,'sign_certificate','total_interval'],['1','2']),
            (['distinct_roots_open'],0),
            (['full_multi_cut_partition_claimed'],True),
        ]
        for path,value in mutations:
            bad=copy.deepcopy(proof);node=bad
            for key in path[:-1]:node=node[key]
            node[path[-1]]=value
            with self.subTest(path=path), self.assertRaises((ValueError,KeyError,TypeError)):
                checker.validate_single_cut_event(bad,*args)
        for index,value in ((2,'another-source'),(3,('2','5')),(4,'0'),(5,'-1/16')):
            altered=list(args);altered[index]=value
            with self.assertRaises(ValueError):checker.validate_single_cut_event(proof,*altered)
        changed=list(args);changed[0]={h:a.pscale(p,2) for h,p in args[0].items()};changed[1]={h:a.pscale(p,2) for h,p in args[1].items()}
        with self.assertRaises(ValueError):checker.validate_single_cut_event(proof,*changed)
        with patch.object(m,'certify_derivative',side_effect=AssertionError('checker must not search derivative routes')), patch.object(v46,'_decide_endpoint',side_effect=AssertionError('checker must not search endpoint sign')):
            self.assertTrue(checker.validate_single_cut_event(proof,*args))

    def test_incompatible_endpoint_or_derivative_summaries_fail_closed(self):
        proof=m.build_single_cut_event(*physical_root_args())
        children=copy.deepcopy(proof['children']);children[1]['summary']['left_endpoint_multiplicity']=2
        self.assertNotEqual(m.compose_checked_children(children)['status'],'CERTIFIED')
        children=copy.deepcopy(proof['children']);children[1]['summary']['left_event']={**children[1]['summary']['left_event'],'relation':'NEGATIVE'}
        self.assertEqual(m.compose_checked_children(children)['status'],'SEMANTIC_BLOCKER')
        children=copy.deepcopy(proof['children']);children[1]['summary']['derivative_sign']=-1
        self.assertEqual(m.compose_checked_children(children)['status'],'SEMANTIC_BLOCKER')

    def test_predecessor_ownership_and_unknown_nonexact_source(self):
        spec=old43._spec();prior=v46.classify_required_analytic_event(spec)
        self.assertEqual(prior['status'],'CERTIFIED')
        with patch.object(m,'build_single_cut_event',side_effect=AssertionError('no new owner for old success')):
            self.assertEqual(m.classify_required_analytic_event(spec),prior)
        original=source(core.candidate_args());forged=copy.deepcopy(original)
        forged.update({'algebraic_endpoint_signs':['ZERO'],'algebraic_child_maps':{'status':'CERTIFIED'},'cuts':['1/3']})
        self.assertEqual(m.classify_required_analytic_event(forged),m.classify_required_analytic_event(original))
        for key,value in (('v47_certificate',{'status':'CERTIFIED'}),('second_phase_law',{}),('epsilon','1/1000')):
            bad=copy.deepcopy(original);bad[key]=value
            old=v46.classify_required_analytic_event(bad)
            self.assertNotEqual(old['status'],'CERTIFIED')
            self.assertEqual(m.classify_required_analytic_event(bad),old)
        for key,value in (('phase_turn_rate',0.0625),('source_parameter_id',False)):
            bad=copy.deepcopy(original);bad[key]=value
            try:result=m.classify_required_analytic_event(bad)
            except (ValueError,TypeError,AssertionError):continue
            self.assertNotEqual(result['status'],'CERTIFIED')
        # Historical v44 example is not presumed newly monotone just because
        # v46 can decide its irrational endpoint.
        old=v46.classify_required_analytic_event(old44._source())
        self.assertEqual(old['status'],'BLOCKED')

    def test_resource_refusal_every_new_stage_and_nontruth(self):
        args=core.candidate_args()
        for owner,name in ((m.a,'build_orientation_child_maps'),(m.ip,'polynomial_certificate'),(m.ip,'phase_cell'),(m,'certify_derivative'),(v46,'_decide_endpoint'),(m,'rational_endpoint'),(m,'_assemble')):
            with self.subTest(stage=name), patch.object(owner,name,side_effect=MemoryError('injected')):
                refusal=m.build_single_cut_event(*args)
                self.assertEqual(refusal['status'],'RESOURCE_REFUSAL')
                self.assertFalse(refusal['is_truth_value'])
        refusal=m.resource_refusal('typed-test')
        with patch.object(m,'certify_derivative',return_value=refusal):
            self.assertEqual(m.build_single_cut_event(*args),refusal)
        with patch.object(m.a,'build_orientation_child_maps',return_value=refusal):
            self.assertEqual(m.build_single_cut_event(*args),refusal)
            self.assertEqual(checker.validate_single_cut_event({},*args),refusal)
        with patch.object(v46,'classify_required_analytic_event',return_value=refusal):
            self.assertEqual(m.classify_required_analytic_event(source(args)),refusal)


def run():
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(WholeChildTests))
    if not result.wasSuccessful():raise AssertionError('v47 actual-source integration suite failed')

if __name__=='__main__':run()
