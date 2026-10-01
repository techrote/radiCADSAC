#!/usr/bin/env python3
"""Exact boundary/derivative controls; no mocked algebraic arithmetic."""
from fractions import Fraction as Q
from math import comb, isqrt
from pathlib import Path
from unittest.mock import patch
import copy
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_mixed_boundary_model as m
import pb00701_mixed_multicut_model as consumer

a, E = m.a, m.E


def algebraic(poly, index=0):
    minimal = a.primitive(poly)
    return m.Boundary(field=a.RealField(minimal, a._canonical_interval(minimal, index), index))


def candidate_args():
    A, B = [Q(469, 2500), -1, 1], [Q(-1, 4), Q(1, 2)]
    return ({1: a.padd(A, B), 2: [Q(1, 10**8)]},
            {1: a.padd(A, a.pscale(B, -1))}, 'v49-source', ('0', '1'), '-1/8', '1/16')


def candidate_points():
    return [m.Boundary.at(0), algebraic([469, -2500, 2500], 0),
            m.Boundary.at(Q(1, 2)), algebraic([469, -2500, 2500], 1), m.Boundary.at(1)]


class MixedBoundaryTests(unittest.TestCase):
    def test_exact_order_conjugates_and_different_minimal_polynomials(self):
        lo, hi = algebraic([469, -2500, 2500], 0), algebraic([469, -2500, 2500], 1)
        other = algebraic([-1, 0, 2])
        self.assertNotEqual(lo.field, hi.field)
        for left, right in ((lo, other), (other, hi), (lo, hi), (m.Boundary.at(0), lo), (hi, m.Boundary.at(1))):
            self.assertEqual(m.order_certificate(left, right)['comparison'], -1)
            self.assertEqual(m.order_certificate(right, left)['comparison'], 1)
        self.assertEqual(m.order_certificate(lo, lo)['comparison'], 0)
        self.assertEqual(m.order_certificate(m.Boundary.at('1/2'), m.Boundary.at(Q(1, 2)))['comparison'], 0)
        with self.assertRaises(ValueError):
            lo.field.element([0, 1]) - hi.field.element([0, 1])
        # This test is exactly the operation avoided by boundary-local proofs.
        p = m.polynomial_certificate([-1, 0, 2], lo, hi)
        self.assertEqual(p['distinct_roots_open'], 1)

    def test_nearby_different_field_roots_overlap_is_not_equality(self):
        lo, hi = algebraic([-4999, 0, 10000]), algebraic([-5001, 0, 10000])
        self.assertEqual(lo.field.interval, hi.field.interval)
        order = m.order_certificate(lo, hi)
        self.assertEqual(order['comparison'], -1)
        self.assertGreater(sum(order['refinement_steps']), 0)
        self.assertLessEqual(Q(order['isolations'][0][1]), Q(order['isolations'][1][0]))

    def test_one_sided_sturm_endpoint_and_repeated_roots(self):
        lo, hi = algebraic([469, -2500, 2500], 0), algebraic([469, -2500, 2500], 1)
        p = [Q(469, 2500), -1, 1]
        cert = m.polynomial_certificate(p, lo, hi)
        self.assertEqual(cert['distinct_roots_open'], 0)
        self.assertEqual(cert['endpoint_multiplicities'], [1, 1])
        self.assertEqual(cert['endpoint_signs'], [0, 0])
        self.assertEqual(cert['weak_sign'], -1)
        repeated = a.pmul(p, p)
        cert2 = m.polynomial_certificate(repeated, lo, hi)
        self.assertEqual(cert2['endpoint_multiplicities'], [2, 2])
        self.assertEqual(cert2['weak_sign'], 1)
        self.assertFalse(cert2['strict_positive'])
        interior_tangent = [Q(1, 4), -1, 1]
        cert3 = m.polynomial_certificate(interior_tangent, lo, hi)
        self.assertEqual(cert3['distinct_roots_open'], 1)
        self.assertIsNone(cert3['weak_sign'])
        end = m.polynomial_certificate(p, lo, m.Boundary.at('1/2'))
        self.assertTrue(any(j['order'] > 0 for j in end['right_inward_jets'] if j['order'] is not None))

    def test_rational_and_algebraic_boundary_polynomial_values(self):
        alpha = algebraic([-1, 0, 2])
        cert = m.polynomial_certificate([-1, 0, 2], m.Boundary.at(0), alpha)
        self.assertEqual(cert['endpoint_signs'], [-1, 0])
        self.assertEqual(cert['distinct_roots_open'], 0)
        self.assertEqual(cert['weak_sign'], -1)
        self.assertEqual(m.polynomial_certificate([0], m.Boundary.at(0), alpha)['distinct_roots_open'], None)
        self.assertTrue(m.polynomial_certificate([1], m.Boundary.at(0), alpha)['strict_positive'])
        with self.assertRaises(ValueError): m.polynomial_certificate([1], alpha, alpha)
        with self.assertRaises(ValueError): m.polynomial_certificate([1], alpha, m.Boundary.at(0))

    def test_strict_equality_exact_neighbors_and_tiny_nonzero(self):
        lo, hi = m.Boundary.at(0), algebraic([-1, 0, 2])
        p = [1, 0, -2]
        for delta, expected in ((Q(1, 10**6), True), (Q(0), False), (Q(-1, 10**6), False)):
            cert = m.polynomial_certificate(a.padd(p, [delta]), lo, hi)
            self.assertEqual(cert['strict_positive'], expected)
        self.assertTrue(m.polynomial_certificate([Q(1, 10**100)], lo, hi)['strict_positive'])

    def test_two_algebraic_phase_bounds_floor_and_both_rates(self):
        lo, hi = algebraic([469, -2500, 2500], 0), algebraic([469, -2500, 2500], 1)
        for off, rate in ((Q(-1, 8), Q(1, 16)), (Q(-1, 16), Q(-1, 16))):
            cell = m.phase_cell(lo, hi, off, rate, 1)
            self.assertEqual(cell['status'], 'CERTIFIED')
            self.assertEqual(cell['cell_index'], 0)
        self.assertEqual(m._floor_affine(lo, 0, 100), 25)
        self.assertEqual(m._floor_affine(lo, 0, -100), -26)
        self.assertEqual(m._floor_affine(lo, 5, 0), 5)
        for delta, ok in ((Q(0), True), (Q(1, 10**6), False), (Q(-1, 10**6), False)):
            cell = m.phase_cell(m.Boundary.at(0), m.Boundary.at(1), Q(-3,16)+delta, Q(1,8), 1)
            self.assertEqual(cell['status'] == 'CERTIFIED', ok)
        with self.assertRaises((ValueError, TypeError)): m.phase_cell(lo, hi, '-1/8', '0', 1)

    def test_candidate_all_four_child_margins_and_single_cut_failure(self):
        material, points = a._material(*candidate_args()), candidate_points()
        proofs = [m.certify_derivative(material, lo, hi) for lo, hi in zip(points, points[1:])]
        self.assertEqual([p['status'] for p in proofs], ['CERTIFIED']*4)
        self.assertEqual([p['mode'] for p in proofs], ['V43', 'V42', 'V42', 'V43'])
        self.assertEqual([p['derivative_sign'] for p in proofs], [1]*4)
        for cut in points[1:-1]:
            pair = [m.certify_derivative(material, points[0], cut), m.certify_derivative(material, cut, points[-1])]
            self.assertFalse(all(p['status'] == 'CERTIFIED' for p in pair))
        self.assertEqual([p['orthant_count'] for p in proofs], [8,16,16,8])
        inserted = algebraic([-1, 0, 2])
        for lo, hi in ((points[1], inserted), (inserted, points[3])):
            self.assertEqual(m.derivative_attempt(material, lo, hi, 1, 'V42')['status'], 'CERTIFIED')

    def test_independent_fraction_bernstein_margin_witness(self):
        # Independent polynomial arithmetic and Bernstein enclosure, not a
        # repeat of the implementation's Sturm/field sign predicate.
        def add(x, y):
            return [(x[i] if i < len(x) else Q(0)) + (y[i] if i < len(y) else Q(0))
                    for i in range(max(len(x), len(y)))]
        def scale(x, k):
            return [k * c for c in x]
        def bernstein_on(x, lo, hi):
            n = len(x) - 1
            power = [sum((x[k] * comb(k,j) * lo**(k-j) * (hi-lo)**j
                          for k in range(j,n+1)),Q(0)) for j in range(n+1)]
            return [sum((power[j] * Q(comb(i,j),comb(n,j)) for j in range(i+1)),Q(0))
                    for i in range(n+1)]
        A, B, Ap = [Q(469,2500),-Q(1),Q(1)], [-Q(1,4),Q(1,2)], [-Q(1),Q(2)]
        lower, transverse, upper, two_pi = Q(2856,2197), Q(99,182), Q(99,70), Q(44,7)
        rate, residual = Q(1,16), [Q(44,7)*Q(1,8)*Q(1,10**8)]
        discriminant = 2500**2 - 4*2500*469
        self.assertLess(isqrt(discriminant)**2, discriminant)
        for t, expected in ((Q(1,4),1),(Q(251,1000),-1),(Q(749,1000),-1),(Q(3,4),1)):
            value = sum((c*t**i for i,c in enumerate(A)),Q(0))
            self.assertEqual(1 if value>0 else -1,expected)
        material, points = a._material(*candidate_args()), candidate_points()
        boxes = [(Q(0),Q(251,1000)), (Q(1,4),Q(1,2)),
                 (Q(1,2),Q(3,4)), (Q(749,1000),Q(1))]
        floors=[]
        for i, (lo,hi) in enumerate(zip(points,points[1:])):
            proof=m.certify_derivative(material,lo,hi)
            if i in (0,3):
                base=add([lower/2],scale(A,6*lower*rate))
                terms=[scale(Ap,transverse),scale(B,two_pi*rate*transverse),residual]
            else:
                base=[lower/2]
                terms=[scale(Ap,transverse),scale(A,two_pi*rate*upper),
                       scale(B,two_pi*rate*transverse),residual]
            bounds=[]
            for mask in range(1<<len(terms)):
                margin=list(base)
                for j,term in enumerate(terms):
                    margin=add(margin,scale(term,-1 if (mask>>j)&1 else 1))
                self.assertEqual(a.trim(margin),a.trim(proof['orthants'][mask]['certificate']['polynomial']))
                floor=min(bernstein_on(margin,*boxes[i]))
                self.assertGreater(floor,0)
                bounds.append(floor)
            floors.append(str(min(bounds)))
        print('independent Fraction/Bernstein complete-margin floors:', floors)

    def test_finite_phase_crossings_rational_cut_coincidence(self):
        cuts = consumer.finite_phase_cuts(a._material(*candidate_args()))
        half = [c for c in cuts if c['source'] == '1/2']
        self.assertEqual(len(half), 1)
        self.assertEqual(half[0]['harmonic'], 2)
        self.assertEqual(half[0]['harmonic_phase'], '-3/16')
        args = list(candidate_args()); args[4], args[5] = '-1/16', '-1/16'
        reverse = consumer.finite_phase_cuts(a._material(*args))
        self.assertIn('1/2', [c['source'] for c in reverse])
        self.assertEqual(consumer.finite_phase_cuts(a._material(*candidate_args()[:-1], '0')), [])

    def test_exact_source_negation_and_global_chain_rule(self):
        args, points = list(candidate_args()), candidate_points()
        for negative, global_span in ((True, False), (False, True)):
            variant = copy.deepcopy(args)
            if negative:
                variant[0] = {h:a.pscale(p,-1) for h,p in variant[0].items()}
                variant[1] = {h:a.pscale(p,-1) for h,p in variant[1].items()}
            if global_span:
                variant[3], variant[4], variant[5] = ('2','5'), '-1/6', '1/48'
            material = a._material(*variant)
            proofs = [m.certify_derivative(material, lo, hi) for lo,hi in zip(points,points[1:])]
            self.assertEqual([p['status'] for p in proofs], ['CERTIFIED']*4)
            self.assertEqual([p['derivative_sign'] for p in proofs], [-1 if negative else 1]*4)
            self.assertEqual([p['global_derivative_scale'] for p in proofs], ['1/3' if global_span else '1']*4)

    def test_all_selected_and_nonanchor_channels_live(self):
        args = list(candidate_args()); args[0] = dict(args[0]); args[1] = dict(args[1])
        args[0][0] = [0, Q(1,10**9)]; args[0][2] = [Q(1,10**8),Q(1,10**10)]
        args[1][2] = [Q(1,10**10),Q(1,10**11)]
        material, points = a._material(*args), candidate_points()
        for lo,hi in zip(points,points[1:]):
            proof = m.certify_derivative(material,lo,hi)
            self.assertEqual(proof['status'],'CERTIFIED')
            kinds = {t['kind'] for t in proof['retained_nonanchor_channels']}
            self.assertEqual(kinds, {'C0_prime','C_prime','S_prime','C_phase_upper','S_phase_upper'})
            self.assertNotEqual(proof['coordinates']['A_prime'], ['0'])
            self.assertNotEqual(proof['coordinates']['B_prime'], ['0'])

    def test_complete_v42_margin_equality_and_neighbors(self):
        A, B = [Q(1,100)], [-1,Q(1,2)]
        threshold = m.L/2 - m.K/16*(m.W/100 + m.U)
        self.assertGreater(threshold,0)
        for delta, status in ((Q(-1,10**6),'CERTIFIED'),(Q(0),'BLOCKED'),(Q(1,10**6),'BLOCKED')):
            args=({0:[0,threshold+delta],1:a.padd(A,B)},
                  {1:a.padd(A,a.pscale(B,-1))},'strict-margin',('0','1'),'-1/8','1/16')
            proof=m.derivative_attempt(a._material(*args),m.Boundary.at(0),algebraic([-1,0,2]),1,'V42')
            self.assertEqual(proof['status'],status)
            if delta==0:
                self.assertEqual(proof['reason'],'COMPLETE_STRICT_MARGIN_NOT_CERTIFIED')
                self.assertEqual(proof['failed_margin']['endpoint_signs'][0],0)
                self.assertFalse(proof['failed_margin']['strict_positive'])

    def test_type_rejections_and_forged_finite_polynomial_evidence(self):
        lo,hi=m.Boundary.at(0),algebraic([-1,0,2])
        proof=m.polynomial_certificate([1,0,-2],lo,hi)
        for key,value in (('strict_positive',True),('weak_sign',-1),('variations',[4,4]),('endpoint_multiplicities',[0,2])):
            bad=copy.deepcopy(proof);bad[key]=value
            with self.assertRaises(ValueError):m.validate_polynomial_certificate(bad,[1,0,-2],lo,hi)
        for x in (True, False, 0.25):
            with self.assertRaises((ValueError,TypeError)):m.Boundary.at(x)
        for h in (True, Q(1,2), '1'):
            with self.assertRaises((ValueError,TypeError)):m.phase_cell(lo,hi,'-1/8','1/16',h)
        with self.assertRaises(TypeError):m.polynomial_certificate([1.0],lo,hi)
        args=list(candidate_args()); args[5]=0.0625
        with self.assertRaises(TypeError):a._material(*args)

    def test_resource_refusal_is_not_a_false_sign(self):
        lo,hi=m.Boundary.at(0),algebraic([-1,0,2])
        with patch.object(E,'sturm_sequence',side_effect=MemoryError('test')):
            with self.assertRaises(MemoryError):m.polynomial_certificate([1,0,-2],lo,hi)
        with patch.object(m,'_refine',side_effect=MemoryError('test')):
            with self.assertRaises(MemoryError):m.order_certificate(algebraic([-4999,0,10000]),algebraic([-5001,0,10000]))
        self.assertFalse(m.refusal('test')['is_truth_value'])


def run():
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MixedBoundaryTests))
    if not result.wasSuccessful():raise AssertionError('v49 exact boundary core failed')

if __name__=='__main__':run()
