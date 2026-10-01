#!/usr/bin/env python3
"""Actual v44/v45 source admission, binding and non-promotion controls."""
from fractions import Fraction as Q
from pathlib import Path
import copy
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_algebraic_endpoint_model as m
import pb00701_algebraic_endpoint_certificate as checker
import pb00701_algebraic_orientation_cut_model as v44
import test_pb00701_algebraic_orientation_cut_adversarial as v44test
import test_pb00701_correlated_closed_handoff_adversarial as v43test
from test_pb00701_algebraic_endpoint import power, field


def args(p=(-1,0,2), *, rate='1/8', parent=('0','1'), offset='0', add_constant=True):
    cos = {1:m.v45.pscale(p,3)}
    if add_constant: cos[0] = [1]
    return (cos,{1:m.v45.pscale(p,-1)},'physical-source-s',parent,offset,rate)


class SourceEndpointTests(unittest.TestCase):
    def test_genuine_source_endpoint_does_not_certify_span(self):
        source = v44test._source()
        baseline = m.classify_required_analytic_event(source)
        self.assertEqual(baseline['status'],'BLOCKED')
        result = m.decide_required_event_endpoints(source)
        self.assertEqual(result['status'],'ENDPOINTS_CERTIFIED')
        self.assertEqual(result['predecessor_event_result'],baseline)
        self.assertFalse(result['analytic_cut_consumed'])
        self.assertTrue(result['span_endpoint_evidence'])
        for item in result['span_endpoint_evidence']:
            evidence = item['endpoint_evidence']
            endpoint = evidence['endpoints'][0]
            self.assertEqual(endpoint['relation'],'POSITIVE')
            self.assertEqual(endpoint['physical_multiplicity'],0)
            self.assertFalse(endpoint['whole_span_certified'])
            self.assertEqual(endpoint['field']['minimal_polynomial'],[-1,0,2])
            # The non-anchor harmonic must be present in the actual sign certificate.
            self.assertIn(2,[x['harmonic'] for x in endpoint['sign_certificate']['components']])
        ignored = copy.deepcopy(source)
        ignored.update({'algebraic_roots':['1/2'], 'algebraic_endpoint_signs':['ZERO'],
                        'algebraic_child_maps':{'status':'CERTIFIED'}})
        self.assertEqual(m.decide_required_event_endpoints(ignored),result)

    def test_physical_zero_and_neutral_orientation_cut(self):
        for order in (1,2,3):
            inputs = args(power([-1,0,2],order),add_constant=False)
            result = m.build_source_endpoint_evidence(*inputs)
            self.assertEqual(result['status'],'ENDPOINTS_CERTIFIED')
            self.assertEqual(len(result['endpoints']),1)  # A/B common cut once.
            endpoint = result['endpoints'][0]
            self.assertEqual(endpoint['relation'],'ZERO')
            self.assertEqual(endpoint['physical_multiplicity'],order)
            self.assertIs(checker.validate_source_endpoint_evidence(result,*inputs),True)
            neutral = m.build_source_endpoint_evidence(*args(power([-1,0,2],order)))
            self.assertEqual(neutral['endpoints'][0]['relation'],'POSITIVE')
            self.assertEqual(neutral['endpoints'][0]['physical_multiplicity'],0)
        # A different harmonic has a smaller order: orientation multiplicity is not F's.
        inputs = list(args(power([-1,0,2],3),add_constant=False))
        inputs[0][2] = [-1,0,2]
        result = m.build_source_endpoint_evidence(*inputs)
        self.assertEqual(result['endpoints'][0]['physical_multiplicity'],1)

    def test_shared_endpoint_child_values_and_multiplicity(self):
        inputs = args(power([-1,0,2],2),add_constant=False)
        representation = m.v45.build_orientation_child_maps(*inputs)
        split = representation['independent_single_cut_bisections'][0]
        f = field(); alpha = f.element([0,1])
        def ev(poly,x):
            out = f.element(0)
            for c in reversed(poly): out = out*x+f.element(c)
            return out
        for child, x, width in ((split['children'][0],f.element(1),alpha),
                                (split['children'][1],f.element(0),f.element(1)-alpha)):
            for channel in ('cos_polynomials','sin_polynomials'):
                for h,p in child['restricted_polynomials'][channel].items():
                    self.assertTrue(ev(p,x).is_zero())
                    first = [f.element(c)*i for i,c in enumerate(p)][1:]
                    self.assertTrue(ev(first,x).is_zero())
                    second = [c*i for i,c in enumerate(first)][1:]
                    physical_jet = ev(second,x)*((width**2).inverse())
                    parent = representation['source_material'][channel][h]
                    expected = f.element(m.v45.engine.deriv(m.v45.engine.deriv(parent)))
                    self.assertEqual(physical_jet,expected)
        endpoint = m.build_source_endpoint_evidence(*inputs)['endpoints'][0]
        self.assertEqual(endpoint['physical_multiplicity'],2)
        self.assertFalse(endpoint['sign_change'])

    def test_phase_rates_global_interval_and_scaling(self):
        for rate in ('1/8','-1/8'):
            inputs = args(rate=rate,parent=('-2','3'),offset='1/5')
            result = m.build_source_endpoint_evidence(*inputs)
            endpoint = result['endpoints'][0]
            self.assertEqual(endpoint['relation'],'POSITIVE')  # harmonic-0 survives alone here.
            self.assertEqual(endpoint['source_cut'],['-2','5'])
            self.assertIs(checker.validate_source_endpoint_evidence(result,*inputs),True)
            changed = list(inputs)
            changed[0] = {h:m.v45.pscale(p,-Q(1,10**40)) for h,p in inputs[0].items()}
            changed[1] = {h:m.v45.pscale(p,-Q(1,10**40)) for h,p in inputs[1].items()}
            scaled = m.build_source_endpoint_evidence(*changed)
            self.assertEqual(scaled['endpoints'][0]['relation'],'NEGATIVE')
            with self.assertRaises(ValueError): checker.validate_source_endpoint_evidence(result,*changed)
        self.assertEqual(m.build_source_endpoint_evidence(*args(rate='0'))['status'],'NOT_APPLICABLE')

    def test_forged_source_field_phase_laurent_and_sign_bounds(self):
        # Live selected harmonic values at A=0 are nonzero and opposite, so both trig channels matter.
        a,b = [-1,0,2],[1]
        inputs = ({0:[1],1:m.v45.padd(a,b)}, {1:m.v45.padd(a,[-1])},'source-s',('0','1'),'0','1/8')
        original = m.build_source_endpoint_evidence(*inputs)
        self.assertEqual(original['status'],'ENDPOINTS_CERTIFIED')
        self.assertIs(checker.validate_source_endpoint_evidence(original,*inputs),True)
        mutations = [
            (['endpoints',0,'field','minimal_polynomial'],[-1,0,3]),
            (['endpoints',0,'field','isolating_interval'],['1/100','1/50']),
            (['endpoints',0,'field','root_index_in_open_unit_interval'],True),
            (['endpoints',0,'phase_turn'],['0']),
            (['endpoints',0,'transcendence','exponent'],['1']),
            (['endpoints',0,'jets','endpoint_laurent'],[]),
            (['endpoints',0,'jets','first_nonzero_jet_laurent'],[]),
            (['endpoints',0,'physical_multiplicity'],1),
            (['endpoints',0,'relation'],'ZERO'),
            (['endpoints',0,'source_parameter_id'],'other'),
            (['endpoints',0,'source_cut'],['1/2']),
            (['endpoints',0,'sign_certificate','alpha_interval'],['1/100','1/50']),
            (['endpoints',0,'sign_certificate','precision'],True),
            (['endpoints',0,'sign_certificate','pi','atan_1_5','signed_next_term'],'0'),
            (['endpoints',0,'sign_certificate','total_interval'],['1','1']),
            (['endpoints',0,'sign_certificate','components'],[]),
            (['analytic_cut_consumed'],True),
            (['whole_span_certified'],True),
        ]
        # Locate a nonconstant-frequency trig proof without assuming map iteration order.
        components = original['endpoints'][0]['sign_certificate']['components']
        j = next(i for i,c in enumerate(components) if c['harmonic'] > 0)
        for key,value in (('lagrange_remainder','0'),('taylor_sum','0'),('lipschitz_constant','0'),('radius','0')):
            mutations.append((['endpoints',0,'sign_certificate','components',j,'trig',key],value))
        for path,value in mutations:
            forged = copy.deepcopy(original); target=forged
            for key in path[:-1]: target=target[key]
            target[path[-1]]=value
            with self.subTest(path=path), self.assertRaises((ValueError,TypeError,KeyError)):
                checker.validate_source_endpoint_evidence(forged,*inputs)
        for index,value in ((2,'different-s'),(3,('-1','2')),(4,'1/9'),(5,'-1/8')):
            changed=list(inputs); changed[index]=value
            with self.assertRaises(ValueError): checker.validate_source_endpoint_evidence(original,*changed)
        zero = m.build_source_endpoint_evidence(*args(add_constant=False))
        zero['endpoints'][0]['physical_multiplicity']=2
        with self.assertRaises(ValueError): checker.validate_source_endpoint_evidence(zero,*args(add_constant=False))

    def test_nonexact_unknown_grammar_and_coordinate_rejection(self):
        source=v44test._source()
        for key,value in (('phase_turn_rate',0.125),('source_parameter_id',None),
                          ('v46_endpoint_certificate',{'status':'CERTIFIED'}),
                          ('independent_phase_laws',['sqrt(2)','sqrt(3)'])):
            changed=copy.deepcopy(source); changed[key]=value
            baseline=m.classify_required_analytic_event(changed)
            self.assertNotEqual(baseline['status'],'CERTIFIED')
            result=m.decide_required_event_endpoints(changed)
            self.assertEqual(result['predecessor_event_result'],baseline)
            self.assertEqual(result['status'],baseline['status'])
            self.assertEqual(result['span_endpoint_evidence'],[])
        for index,value in ((0,{1:[-3.0,0,6]}),(3,('0',1.0)),(4,False),(5,0.125)):
            changed=list(args()); changed[index]=value
            with self.assertRaises((ValueError,TypeError)): m.build_source_endpoint_evidence(*changed)

    def test_resource_refusal_at_each_new_stage(self):
        live = ({1:[1,0,2]}, {1:[-3,0,2]},'s',('0','1'),'0','1/8')
        for target in ('algebraic_jets','alpha_interval','machin_pi','trig_enclosure','_endpoint_header'):
            with patch.object(m,target,side_effect=MemoryError('injected')):
                refused=m.build_source_endpoint_evidence(*live)
                self.assertEqual(refused['status'],'RESOURCE_REFUSAL',target)
                self.assertFalse(refused['is_truth_value'])
                self.assertFalse(refused['analytic_cut_consumed'])
        original=m.build_source_endpoint_evidence(*live)
        with patch.object(m,'alpha_interval',side_effect=OverflowError('injected')):
            refused=checker.validate_source_endpoint_evidence(original,*live)
            self.assertEqual(refused['status'],'RESOURCE_REFUSAL')
            self.assertFalse(refused['is_truth_value'])
        with patch.object(m.v45,'represent_required_event_children',side_effect=RecursionError('injected')):
            self.assertEqual(m.decide_required_event_endpoints(v44test._source())['status'],'RESOURCE_REFUSAL')
        refusal=m.v45.resource_refusal('injected')
        with patch.object(m.v45,'build_orientation_child_maps',return_value=refusal):
            self.assertEqual(m.build_source_endpoint_evidence(*args()),refusal)
            self.assertEqual(checker.validate_source_endpoint_evidence(original,*live),refusal)

    def test_predecessor_success_no_endpoint_relabel(self):
        source=v43test._spec()
        baseline=m.classify_required_analytic_event(source)
        self.assertEqual(baseline['status'],'CERTIFIED')
        with patch.object(m,'_decide_endpoint',side_effect=AssertionError('no new owner')):
            result=m.decide_required_event_endpoints(source)
        self.assertEqual(result['status'],'NOT_APPLICABLE')
        self.assertEqual(result['predecessor_event_result'],baseline)
        self.assertFalse(result['analytic_cut_consumed'])
        self.assertEqual(result['span_endpoint_evidence'],[])


def run():
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceEndpointTests))
    if not result.wasSuccessful(): raise AssertionError('v46 source integration suite failed')

if __name__ == '__main__': run()
