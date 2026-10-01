#!/usr/bin/env python3
"""Full-repository source acceptance. Never substitutes a predecessor or oracle."""
from fractions import Fraction as Q
from pathlib import Path
import copy
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_mixed_multicut_model as m
import pb00701_mixed_multicut_certificate as checker
import test_pb00701_mixed_boundary as core
import pb00701_mixed_orientation_roots_model as roots
import pb00701_mixed_orientation_consumer as v48
import pb00701_algebraic_endpoint_model as v46
import test_pb00701_algebraic_monotone_cut_integration as fixtures
import test_pb00701_algebraic_monotone_cut as oldcore

a, b = m.a, m.b


def route(result):
    matches = [s['route'] for s in result.get('spans', [])
               if s.get('route_kind') == 'PB00701_V49_MIXED_BOUNDARY_MULTICUT']
    assert result['status'] == 'CERTIFIED' and len(matches) == 1, result
    return matches[0]


class MultiCutSourceTests(unittest.TestCase):
    def test_actual_v48_residual_needs_multiple_exact_cuts(self):
        args = core.candidate_args()
        source = fixtures.source(args)
        prior = v48.classify_required_analytic_event(source)
        self.assertEqual(prior['status'], 'BLOCKED', prior)
        single = v48.build_single_cut_event(*args)
        self.assertEqual(single['status'], 'BLOCKED', single)
        proof = route(m.classify_required_analytic_event(source))
        self.assertEqual(proof['child_count'], 4)
        self.assertEqual([c['derivative_certificate']['mode'] for c in proof['children']],
                         ['V43', 'V42', 'V42', 'V43'])
        self.assertEqual(proof['distinct_roots_open'], 1)
        self.assertEqual(proof['internal_cut_roots'], [])
        self.assertTrue(proof['analytic_multicut_consumed'])
        self.assertFalse(proof['compositum_claimed'])
        self.assertTrue(checker.validate_multicut_event(proof, *args))
        print('v49 ACTUAL-SOURCE acceptance: complete v48 BLOCKED -> four checked children, one open root')

    def test_phase_certificate_and_rational_orientation_coincidence(self):
        args = core.candidate_args()
        partition = m.build_partition(*args)
        self.assertEqual(partition['status'], 'PARTITION_CERTIFIED')
        self.assertEqual(partition['cell_count'], 4)
        self.assertEqual(len(partition['boundaries']), 5)
        half = next(x for x in partition['boundaries'] if x['point'] == b.Boundary.at('1/2').record())
        self.assertEqual({c['kind'] for c in half['causes']},
                         {'RATIONAL_ORIENTATION_ROOT', 'DIAGONAL_CERTIFICATE_BOUNDARY'})
        self.assertTrue(m.validate_partition(partition, *args))
        for cell in partition['cells']:
            self.assertIsNone(cell['normalized_child_map'])
            self.assertEqual(cell['positive_width_proof']['comparison'], -1)
        self.assertFalse(partition['normalized_mixed_field_maps_claimed'])

    def test_actual_differing_minimal_polynomial_child(self):
        args = list(core.candidate_args()); args[0], args[1] = dict(args[0]), dict(args[1])
        p, scale = [-1, 0, 2], Q(1, 10**12)
        args[0][3], args[1][3] = a.pscale(p, 3*scale), a.pscale(p, -scale)
        proof = m.build_multicut_event(*args)
        self.assertEqual(proof['status'], 'CERTIFIED', proof)
        self.assertEqual(proof['child_count'], 5)
        self.assertTrue(any(c['cell']['parent_local_interval'][0]['kind'] ==
                            c['cell']['parent_local_interval'][1]['kind'] == 'ALGEBRAIC_IRRATIONAL'
                            for c in proof['children']))
        fields = [x['point']['field']['minimal_polynomial'] for x in proof['partition']['boundaries']
                  if x['point']['kind'] == 'ALGEBRAIC_IRRATIONAL']
        self.assertIn([-1, 0, 2], fields)
        self.assertIn([469, -2500, 2500], fields)
        self.assertEqual(proof['distinct_roots_open'], 1)
        self.assertTrue(checker.validate_multicut_event(proof, *args))

    def test_mixed_endpoint_factors_repetition_and_common_owner_accounting(self):
        p = a.pmul(a.pmul([0,1], [-1,1]), a.pmul([Q(-1,2),1], a.pmul([-1,0,2],[-1,0,2])))
        args = ({1:a.pscale(p,3)}, {1:a.pscale(p,-1)}, 'mixed-full-source', ('0','1'), '-1/8','1/16')
        partition = m.build_partition(*args)
        self.assertEqual(partition['status'], 'PARTITION_CERTIFIED')
        records = partition['root_certificate']['source_root_records']
        self.assertEqual(len(records), 2)
        for record in records:
            self.assertEqual(record['roots']['distinct_roots_open'], 2)
            self.assertEqual(record['roots']['distinct_roots_closed'], 4)
            self.assertEqual(record['roots']['irrational_open_roots'][0]['multiplicity'], 2)
            self.assertTrue(record['roots']['all_roots_accounted_exactly'])
            self.assertFalse(record['roots']['physical_source_deflated'])
        irrational = [x for x in partition['boundaries'] if x['point']['kind'] == 'ALGEBRAIC_IRRATIONAL']
        self.assertEqual(len(irrational), 1)
        self.assertEqual({c['coordinate'] for c in irrational[0]['causes']}, {'A','B'})
        self.assertEqual(partition['boundaries'][0]['point'], b.Boundary.at(0).record())
        self.assertEqual(partition['boundaries'][-1]['point'], b.Boundary.at(1).record())
        self.assertTrue(m.validate_partition(partition, *args))

    def test_reverse_global_and_source_scale(self):
        args = core.candidate_args()
        for reverse, negate, global_span in ((True,False,False),(False,True,False),(False,False,True)):
            c, s, ident, span, off, rate = args
            off, rate = Q(off), Q(rate)
            if reverse:
                c = {h:fixtures.reverse_poly(p) for h,p in c.items()}
                s = {h:fixtures.reverse_poly(p) for h,p in s.items()}
                off, rate = off + rate, -rate
            if negate:
                c = {h:a.pscale(p,-3) for h,p in c.items()}
                s = {h:a.pscale(p,-3) for h,p in s.items()}
            if global_span:
                span, off, rate = ('2','5'), off-rate*Q(2,3), rate/3
            changed = (c,s,ident,span,str(off),str(rate))
            proof = route(m.classify_required_analytic_event(fixtures.source(changed)))
            self.assertEqual(proof['distinct_roots_open'], 1)
            self.assertEqual(proof['children'][0]['summary']['derivative_sign'], -1 if reverse or negate else 1)
            self.assertTrue(checker.validate_multicut_event(proof, *changed))

    def test_internal_physical_root_once_and_multiple_root_refused(self):
        args = fixtures.physical_root_args()
        proof = m.build_multicut_event(*args)
        self.assertEqual(proof['status'], 'CERTIFIED', proof)
        self.assertEqual(proof['distinct_roots_open'], 1)
        self.assertEqual(len(proof['internal_cut_roots']), 1)
        self.assertEqual(sum(c['summary']['distinct_roots_open'] for c in proof['children']), 0)
        self.assertEqual(proof['internal_cut_roots'][0]['multiplicity'], 1)
        self.assertTrue(checker.validate_multicut_event(proof,*args))
        multiple = fixtures.physical_root_args(2)
        self.assertEqual(m.build_multicut_event(*multiple)['status'], 'BLOCKED')
        ep = v46.build_source_endpoint_evidence(*multiple)
        self.assertEqual(ep['endpoints'][0]['physical_multiplicity'], 2)

    def test_zero_roots_and_rational_exterior_root_outcomes(self):
        args = list(core.candidate_args()); args[0] = dict(args[0]); args[0][0] = [1]
        positive = m.build_multicut_event(*args)
        self.assertEqual(positive['status'], 'CERTIFIED', positive)
        self.assertEqual(positive['total_distinct_roots_closed'], 0)
        self.assertTrue(checker.validate_multicut_event(positive, *args))
        A, eps = [Q(-1,10000), Q(1,10000), Q(1,10000)], Q(1,10**9)
        for side, B, off, c3 in (('left',[eps,Q(7,20)],'-1/8',2*eps),
                                ('right',[-Q(7,20)-eps,Q(7,20)],'-3/16',-2*eps)):
            args = ({1:a.padd(A,B),2:[Q(1,10**8)],3:[c3]},
                    {1:a.padd(A,a.pscale(B,-1)),4:[Q(1,10**12)]},'outer-root',('0','1'),off,'1/16')
            proof=m.build_multicut_event(*args)
            self.assertEqual(proof['status'],'CERTIFIED',proof)
            self.assertEqual(proof['endpoint_root_multiplicity'],{side:1})
            self.assertEqual(proof['distinct_roots_open'],0)
            self.assertTrue(checker.validate_multicut_event(proof,*args))

    def test_all_source_and_proof_corruption_rejects(self):
        args=core.candidate_args();proof=m.build_multicut_event(*args)
        self.assertEqual(proof['status'],'CERTIFIED')
        mutations=[
            (['partition','boundaries'], proof['partition']['boundaries'][:-1]),
            (['partition','boundaries',1,'point','field','root_index_in_open_unit_interval'],1),
            (['partition','boundaries',1,'point','field','minimal_polynomial'],[-1,0,2]),
            (['partition','boundaries',2,'point','value'],'3/5'),
            (['partition','cells',0,'normalized_child_map'],{'offset':0,'width':'1/4'}),
            (['partition','cells',0,'positive_width_proof','comparison'],True),
            (['partition','source_material','phase_turn_law','rate'],'-1/16'),
            (['partition','root_certificate','source_root_records',0,'roots','distinct_roots_open'],1),
            (['children',0,'derivative_certificate','orthants'],[]),
            (['children',0,'derivative_certificate','harmonic'],True),
            (['children',1,'derivative_certificate','orthants',0,'certificate','variations'],[99,99]),
            (['children',1,'derivative_certificate','phase_cell','cell_index'],-1),
            (['children',0,'cell','source_parameter_id'],'different'),
            (['children',0,'summary','distinct_roots_open'],1),
            (['endpoint_evidence',1,'relation'],'POSITIVE'),
            (['endpoint_evidence',1,'sign_certificate','total_interval'],['1','2']),
            (['distinct_roots_open'],0), (['compositum_claimed'],True),
        ]
        for path,value in mutations:
            bad=copy.deepcopy(proof);node=bad
            for key in path[:-1]:node=node[key]
            node[path[-1]]=value
            with self.subTest(path=path), self.assertRaises((ValueError,KeyError,TypeError)):
                checker.validate_multicut_event(bad,*args)
        for index,value in ((2,'different'),(3,('2','5')),(4,'0'),(5,'-1/16')):
            changed=list(args);changed[index]=value
            with self.assertRaises(ValueError):checker.validate_multicut_event(proof,*changed)
        with (patch.object(b,'certify_derivative',side_effect=AssertionError('no route search')),
              patch.object(v46,'_decide_endpoint',side_effect=AssertionError('no sign search'))):
            self.assertTrue(checker.validate_multicut_event(proof,*args))

    def test_summary_mismatch_and_strict_multiplicity_contradiction(self):
        proof=m.build_multicut_event(*fixtures.physical_root_args())
        derivatives=[c['derivative_certificate'] for c in proof['children']]
        bad=copy.deepcopy(derivatives);bad[1]['derivative_sign']=-bad[1]['derivative_sign']
        self.assertEqual(m._assemble(proof['partition'],bad,proof['endpoint_evidence'])['status'],'SEMANTIC_BLOCKER')
        bad=copy.deepcopy(proof['endpoint_evidence'])
        index=next(i for i,x in enumerate(bad) if x['relation']=='ZERO')
        bad[index]['physical_multiplicity']=2
        self.assertEqual(m._assemble(proof['partition'],derivatives,bad)['status'],'SEMANTIC_BLOCKER')

    def test_prior_success_and_unknown_source_fields_preserved(self):
        source=fixtures.source(oldcore.candidate_args())
        baseline=v48.classify_required_analytic_event(source)
        self.assertEqual(baseline['status'],'CERTIFIED')
        with patch.object(m,'build_multicut_event',side_effect=AssertionError('do not relabel prior success')):
            self.assertEqual(m.classify_required_analytic_event(source),baseline)
        source=fixtures.source(core.candidate_args())
        for key,value in (('v49_certificate',{}),('second_phase_law',{}),('epsilon','1/100')):
            bad=copy.deepcopy(source);bad[key]=value
            prior=v48.classify_required_analytic_event(bad)
            self.assertNotEqual(prior['status'],'CERTIFIED')
            self.assertEqual(m.classify_required_analytic_event(bad),prior)
        for key,value in (('phase_turn_rate',0.0625),('source_parameter_id',False)):
            bad=copy.deepcopy(source);bad[key]=value
            try:out=m.classify_required_analytic_event(bad)
            except (ValueError,TypeError,AssertionError):continue
            self.assertNotEqual(out['status'],'CERTIFIED')

    def test_resources_every_new_stage_and_unrelated_errors(self):
        args=core.candidate_args()
        for owner,name in ((roots,'exact_orientation_cuts'),(a,'_bisection'),(b,'order_certificate'),
                           (b,'polynomial_certificate'),(b,'phase_cell'),(m,'_endpoint'),(m,'_assemble')):
            with self.subTest(stage=name),patch.object(owner,name,side_effect=MemoryError('injected')):
                result=m.build_multicut_event(*args)
                self.assertEqual(result['status'],'RESOURCE_REFUSAL')
                self.assertFalse(result['is_truth_value'])
        refused=b.refusal('typed')
        with patch.object(roots,'exact_orientation_cuts',return_value=refused):
            self.assertEqual(m.build_multicut_event(*args),refused)
            self.assertEqual(checker.validate_multicut_event({},*args),refused)
        with patch.object(v48,'classify_required_analytic_event',side_effect=ValueError('unrelated source failure')):
            with self.assertRaisesRegex(ValueError,'unrelated'):m.classify_required_analytic_event(fixtures.source(args))


def run():
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MultiCutSourceTests))
    if not result.wasSuccessful():raise AssertionError('v49 actual-source integration failed')

if __name__=='__main__':run()
