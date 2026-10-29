#!/usr/bin/env python3
"""Deterministic adversarial contract tests for exact half-angle proof."""
import argparse, copy, hashlib, json, sys, unittest
from pathlib import Path
from fractions import Fraction as Q
import pb00701_half_angle_knot as p

def harmonics(**terms):
    return {str(k):{'cos':str(v[0]),'sin':str(v[1])} for k,v in terms.items()}
COS=harmonics(**{'1':('1','0')})
SIN=harmonics(**{'1':('0','1')})
COS2=harmonics(**{'0':('1/2','0'),'2':('1/2','0')})
PLUS=harmonics(**{'0':('1','0'),'1':('1','0')})
MINUS=harmonics(**{'0':('1','0'),'1':('-1','0')})
def spec(a,b):
    return {'schema':p.SCHEMA,'source_parameter_id':'s',
        'spans':[{'interval':['0','1'],'harmonics':a},
                 {'interval':['1','2'],'harmonics':b}]}

class T(unittest.TestCase):
    def test_exact_half_angle_identity(self):
        for terms,expected in ((COS,[1,0,-1]),(SIN,[0,2]),
                               (COS2,[1,0,-2,0,1]),(PLUS,[2]),(MINUS,[0,0,2])):
            f=p.coef_pair_terms(terms); P,H=p.half_angle(f)
            self.assertEqual(P,list(map(Q,expected)))
            self.assertEqual(P[0],sum(a for a,b in f.values()))
            self.assertEqual(P[2*H] if len(P)>2*H else 0,p.at_pi(f))
    def test_simple_crossings(self):
        r=p.contract(spec(COS,COS))
        self.assertEqual((r['root_count_open'],r['maximal_open_signs']),(2,[1,-1,1]))
        self.assertEqual([e['multiplicity'] for e in r['ordered_physical_events']],[1,1])
        self.assertEqual(r['source_knot_value'],'-1')
    def test_double_tangencies(self):
        r=p.contract(spec(COS2,COS2))
        self.assertEqual((r['root_count_open'],r['maximal_open_signs']),(2,[1,1,1]))
        self.assertEqual([e['multiplicity'] for e in r['ordered_physical_events']],[2,2])
    def test_asymmetric_zero_source_knot(self):
        r=p.contract(spec(PLUS,SIN));e=r['ordered_physical_events'][0]
        self.assertEqual((r['root_count_open'],r['maximal_open_signs']),(1,[1,-1]))
        self.assertEqual((e['kind'],e['event_kind']),('SOURCE_KNOT_ZERO','CROSSING'))
        self.assertEqual((e['left_one_sided_order'],e['right_one_sided_order']),(2,1))
        self.assertEqual(r['endpoint_zeros'],[{'position':'2','one_sided_order':1}])
    def test_knot_touching_and_endpoint_zeros(self):
        r=p.contract(spec(PLUS,PLUS));e=r['ordered_physical_events'][0]
        self.assertEqual((r['root_count_open'],r['maximal_open_signs']),(1,[1,1]))
        self.assertEqual((e['left_one_sided_order'],e['right_one_sided_order']),(2,2))
        self.assertEqual(e['event_kind'],'TOUCHING')
        r=p.contract(spec(MINUS,MINUS))
        self.assertEqual(r['root_count_open'],0)
        self.assertEqual(r['endpoint_zeros'],[{'position':'0','one_sided_order':2},
                                             {'position':'2','one_sided_order':2}])
    def test_simple_knot_and_endpoints(self):
        r=p.contract(spec(SIN,SIN))
        self.assertEqual((r['root_count_open'],r['maximal_open_signs']),(1,[1,-1]))
        self.assertEqual([e['one_sided_order'] for e in r['endpoint_zeros']],[1,1])
    def test_refusal_and_no_promotion(self):
        for s in (spec(COS,SIN), spec({'1':{'cos':'0','sin':'0'}},COS),
                  spec({'1':{'cos':'1.0','sin':'0'}},COS),
                  spec({'9':{'cos':'1','sin':'0'}},COS)):
            self.assertIs(p.attempt(s)['is_truth_value'],False)
        s=spec(COS,COS);s['spans'][1]['interval']=['1','3']
        self.assertEqual(p.attempt(s)['status'],'BLOCKED')
        good=p.contract(spec(COS,COS))
        for flag in ('pb00701_certified','original_v27_v41_admitted','production_authorized'):
            self.assertFalse(good[flag])
        self.assertIs(p.attempt(good)['is_truth_value'],False)
        forged=copy.deepcopy(good);forged['ordered_physical_events'].pop()
        self.assertNotEqual(forged,p.contract(spec(COS,COS)))
    def test_rational_sturm_multiple_roots(self):
        for pairs in ([(-2,1),(1,2)], [(-1,2),(2,3)], [(0,2),(1,1),(-3,2)]):
            poly=[Q(1)]
            for x,m in pairs: poly=p.mul(poly,p.power([-Q(x),Q(1)],m))
            roots,k=p.isolate(poly)
            self.assertEqual(k,next((m for x,m in pairs if x==0),0))
            self.assertEqual(sorted(e['multiplicity'] for e in roots),
                             sorted(m for x,m in pairs if x!=0))
            for e in roots:
                a,b=map(Q,e['t_bracket'])
                self.assertTrue(any(a<x<b for x,m in pairs if x!=0))
    def test_repository_custody_on_ci_checkout(self):
        parents=Path(__file__).resolve().parents
        root=parents[4] if len(parents)>4 else None
        if root is None or not (root/'AGENTS.md').exists():
            self.skipTest('standalone local mathematical checkout; GitHub custody checked in CI')
        pins={
            'research/machining-completeness/tasks/MC-038/pb00701-finite-owner-corpus-v54.json':
                '5841c331579489b25caef38cd412bdbf286f9134',
            'research/machining-completeness/tasks/MC-002/domain-contract-v1.json':
                '23de82f5240a72509f7afe4acd5948b65bc4ff13',
            'handoffs/current-authority.json':
                'fa0233323a0804d8a5d3eb7cd892a274a6173fab',
        }
        for name,expected in pins.items():
            raw=(root/name).read_bytes()
            actual=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            self.assertEqual(actual,expected,name)
        auth=json.loads((root/'handoffs/current-authority.json').read_text())
        self.assertIs(auth['production_authorized'],False)
        self.assertEqual(auth['capability_status'],'NOT_ESTABLISHED')
        domain=json.loads((root/'research/machining-completeness/tasks/MC-002/domain-contract-v1.json').read_text())
        self.assertEqual(len(domain['coverage_rule']['required_operation_ids']),26)

    def test_generic_higher_harmonic(self):
        t=harmonics(**{'0':('1','0'),'3':('-1','0')})
        r=p.contract(spec(t,t))
        self.assertTrue(r['root_count_open']>0)
        self.assertFalse(r['mc_b_established'])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--contract',action='store_true');ap.add_argument('--self-test',action='store_true')
    a=ap.parse_args();
    if not(a.contract or a.self_test):ap.error('specify --contract and/or --self-test')
    if a.contract:
        for name,s in [('simple',spec(COS,COS)),('double',spec(COS2,COS2)),
                       ('knot',spec(PLUS,SIN))]:
            r=p.contract(s);print(json.dumps({'case':name,'events':r['root_count_open'],
                    'signs':r['maximal_open_signs'],'endpoint_zeros':r['endpoint_zeros'],
                    'production_authorized':False},sort_keys=True))
    if a.self_test:
        result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(T))
        sys.exit(0 if result.wasSuccessful() else 1)
if __name__=='__main__':main()
