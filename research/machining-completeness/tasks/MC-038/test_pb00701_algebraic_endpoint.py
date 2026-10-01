#!/usr/bin/env python3
"""Exact mathematical unit oracles; actual source admission is tested separately."""
from fractions import Fraction as Q
from pathlib import Path
import copy
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_algebraic_endpoint_model as m
import pb00701_algebraic_endpoint_certificate as checker


def field(poly=(-1,0,2), index=0):
    return m.v45.RealField(tuple(poly), m.v45._canonical_interval(poly, index), index)


def inputs(cos, sin, *, offset='0', rate='1/8', parent=('0','1'), f=None):
    f = f or field()
    # Deliberately internal mathematical unit fixture, not a source-owned cut API.
    return m.v45._material(cos, sin, 'unit-s', parent, offset, rate), {'field':f.record()}


def power(p, n):
    out = [Q(1)]
    for _ in range(n): out = m.v45.pmul(out, p)
    return out


class ExactEndpointTests(unittest.TestCase):
    def test_rational_interval_arithmetic(self):
        self.assertEqual(m.imul(m.interval(-2,3), m.interval(-5,7)), (-15,21))
        self.assertEqual(m.iscale(m.interval(-2,3), -2), (-6,4))
        self.assertEqual(m.ipoly([1,2,3], m.interval(2)), (17,17))
        with self.assertRaises(ValueError): m.interval(2,1)
        with self.assertRaises(TypeError): m.interval(0.1)

    def test_machin_and_taylor_analytic_oracles(self):
        previous = None
        for n in (1,2,4,8,16):
            pi = m.machin_pi(n); bounds = tuple(map(Q,pi['interval']))
            self.assertGreater(bounds[0],3); self.assertLess(bounds[1],4)
            if n >= 2: self.assertLess(bounds[1],Q(22,7))
            width = bounds[1]-bounds[0]
            if previous is not None: self.assertLess(width,previous)
            previous = width
            for kind, target in (('SIN',0),('COS',1)):
                self.assertEqual(tuple(map(Q,m.trig_enclosure(m.interval(0),n,kind)['interval'])), (target,target))
            half_pi = m.iscale(bounds,Q(1,2))
            for kind, exact in (('SIN',1),('COS',0)):
                lo, hi = map(Q,m.trig_enclosure(half_pi,n,kind)['interval'])
                self.assertLessEqual(lo,exact); self.assertGreaterEqual(hi,exact)
        for x in (True,0,-1,1.0):
            with self.assertRaises(ValueError): m.machin_pi(x)

    def test_exact_field_nonzero_and_laurent_collection(self):
        f = field()
        self.assertTrue(f.element([-1,0,2]).is_zero())
        self.assertEqual(f.element([0,0,1]), f.element(Q(1,2)))
        # Same harmonic contributions collect exactly in Q(alpha,i), not approximately.
        v = f.element([0,1])
        self.assertEqual(m._laurent(f,[('COS',1,v),('COS',1,-v)]), [])
        packet, values = m.algebraic_jets(f,{1:[1]},{1:[-1]})
        self.assertEqual(packet['physical_multiplicity'],0)
        self.assertEqual(len(packet['endpoint_laurent']),2)
        self.assertTrue(all(x['real'] != ['0'] and x['imaginary'] != ['0'] for x in packet['endpoint_laurent']))

    def test_positive_negative_phase_and_harmonics(self):
        for rate, expected in (('1/8','POSITIVE'),('-1/8','NEGATIVE')):
            material, split = inputs({0:[0],1:[0]},{1:[1],2:[Q(1,100)]},rate=rate)
            result = m._decide_endpoint(material,split)
            self.assertEqual(result['relation'],expected)
            self.assertEqual(result['physical_multiplicity'],0)
            checker._validate_endpoint(result,material,split)
        for scale, expected in ((1,'POSITIVE'),(-1,'NEGATIVE')):
            material, split = inputs({0:[scale],3:[Q(scale,100)]},{7:[Q(scale,1000)]})
            self.assertEqual(m._decide_endpoint(material,split)['relation'],expected)

    def test_near_cancellation_at_rational_turn_boundary(self):
        # cos-sin changes sign at 1/8 turn. Both perturbations are exact irrational turns.
        for rate, expected in (('1/100000000','NEGATIVE'),('-1/100000000','POSITIVE')):
            material, split = inputs({1:[1]},{1:[-1]},offset='1/8',rate=rate)
            result = m._decide_endpoint(material,split)
            self.assertEqual(result['relation'],expected)
            self.assertGreater(result['sign_certificate']['precision'],1)
            checker._validate_endpoint(result,material,split)

    def test_tiny_nonzero_scaling_and_rational_straddles(self):
        for bound, expected in ((Q(707106,1000000),'POSITIVE'),(Q(707107,1000000),'NEGATIVE')):
            for scale in (Q(1),Q(1,10**80)):
                material, split = inputs({0:[-bound*scale,scale],1:[scale/10**12]}, {})
                result = m._decide_endpoint(material,split)
                self.assertEqual(result['relation'],expected)
                self.assertEqual(result['physical_multiplicity'],0)

    def test_odd_even_unequal_orders_are_physical(self):
        p = [-1,0,2]
        for order in (1,2,3,4):
            material, split = inputs({0:power(p,order+1),1:power(p,order)}, {1:power(p,order+2),2:[0]})
            with patch.object(m,'sign_enclosure',side_effect=AssertionError('zero must never refine')):
                result = m._decide_endpoint(material,split)
                checker._validate_endpoint(result,material,split)
            self.assertEqual(result['relation'],'ZERO')
            self.assertEqual(result['physical_multiplicity'],order)
            self.assertEqual(result['sign_change'],bool(order%2))
            self.assertEqual(result['jets']['endpoint_laurent'],[])
            self.assertTrue(result['jets']['first_nonzero_jet_laurent'])
            self.assertNotIn('sign_certificate',result)

    def test_identity_and_zero_phase_do_not_search(self):
        material, split = inputs({0:[0],1:[0]},{1:[0]})
        with patch.object(m,'sign_enclosure',side_effect=AssertionError('identity must not refine')):
            result = m._decide_endpoint(material,split)
        self.assertEqual(result['reason'],'DEGENERATE_IDENTITY_ZERO')
        self.assertIsNone(result['physical_multiplicity'])
        with self.assertRaises(ValueError): m._decide_endpoint(*inputs({1:[1]}, {}, rate='0'))

    def test_global_source_maps_and_physical_jet_scale(self):
        p = [-1,0,2]
        a = inputs({1:p},{2:power(p,2)},parent=('-2','3'),offset='1/5',rate='1/8')
        b = inputs({1:p},{2:power(p,2)},offset='-1/20',rate='5/8')
        x,y = m._decide_endpoint(*a),m._decide_endpoint(*b)
        self.assertEqual(x['phase_turn'],y['phase_turn'])
        self.assertEqual(x['relation'],y['relation'])
        self.assertEqual(x['physical_multiplicity'],1)
        self.assertEqual(x['global_jet_scale'],'1/5')
        self.assertEqual(x['source_cut'],['-2','5'])
        self.assertNotEqual(x['source_binding_sha256'],y['source_binding_sha256'])

    def test_distinct_conjugates_and_integer_turn_shift(self):
        for index, expected in ((0,'NEGATIVE'),(1,'POSITIVE')):
            result = m._decide_endpoint(*inputs({0:[Q(-1,2),1],1:[Q(1,1000)]},{},f=field((1,-8,8),index)))
            self.assertEqual(result['relation'],expected)
            self.assertEqual(result['field']['root_index_in_open_unit_interval'],index)
        a = m._decide_endpoint(*inputs({1:[1]},{1:[-1]},offset='0'))
        b = m._decide_endpoint(*inputs({1:[1]},{1:[-1]},offset=str(10**12)))
        self.assertEqual(a['relation'],b['relation'])
        self.assertEqual(a['sign_certificate']['total_interval'],b['sign_certificate']['total_interval'])

    def test_checker_is_not_a_second_sign_search(self):
        material,split = inputs({0:[1],1:[Q(1,100)]},{2:[1]})
        result = m._decide_endpoint(material,split)
        with patch.object(m,'_decide_endpoint',side_effect=AssertionError('checker must not regenerate search')):
            checker._validate_endpoint(result,material,split)
        with patch.object(m,'trig_enclosure',side_effect=MemoryError('injected')):
            with self.assertRaises(MemoryError): checker._validate_endpoint(result,material,split)

    def test_unsupported_channels_rejected(self):
        for cos,sin in (({Q(1,2):[1]},{}),({-1:[1]},{}),({True:[1]},{}),({1:[1.0]},{}),({},{0:[1]})):
            with self.assertRaises((ValueError,TypeError)):
                m._decide_endpoint(*inputs(cos,sin))


def run():
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ExactEndpointTests))
    if not result.wasSuccessful(): raise AssertionError('v46 core suite failed')

if __name__ == '__main__': run()
