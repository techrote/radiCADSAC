#!/usr/bin/env python3
"""Exact algebraic boundary, complete derivative and composition controls."""
from fractions import Fraction as Q
from pathlib import Path
import copy
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pb00701_algebraic_monotone_cut_model as m
ip, a = m.ip, m.a


def sqrt_field():
    return a.RealField((-1, 0, 2), (Q(1, 2), Q(3, 4)), 0)


def candidate_args():
    A, B = [Q(-1, 8), Q(1, 2), Q(1, 10000)], [Q(-7, 40), Q(7, 20)]
    return ({1: a.padd(A, B), 2: [Q(1, 100000000)]},
            {1: a.padd(A, a.pscale(B, -1))}, 'v47-candidate', ('0', '1'), '-1/8', '1/16')


def candidate_field():
    return a.RealField((-1250, 5000, 1), (Q(1, 8), Q(1, 4)), 0)


class AlgebraicIntervalTests(unittest.TestCase):
    def test_exact_sturm_zero_member_and_endpoint_multiplicities(self):
        f = sqrt_field(); z, alpha, one = f.element(0), f.element([0, 1]), f.element(1)
        p = [-1, 0, 2]
        left, right = ip.polynomial_certificate(p, z, alpha), ip.polynomial_certificate(p, alpha, one)
        self.assertEqual(left['distinct_roots_open'], 0)
        self.assertEqual(left['endpoint_signs'], [-1, 0])
        self.assertEqual(left['weak_sign'], -1)
        self.assertEqual(right['endpoint_signs'], [0, 1])
        self.assertEqual(right['weak_sign'], 1)
        self.assertEqual(left['right_inward_jets'][0]['order'], 1)
        self.assertEqual(right['left_inward_jets'][0]['order'], 1)
        repeated = ip.polynomial_certificate(a.pmul(p, p), z, alpha)
        self.assertEqual(repeated['endpoint_multiplicities'], [0, 2])
        self.assertEqual(repeated['weak_sign'], 1)
        self.assertFalse(repeated['strict_positive'])
        with_inside = a.pmul(a.pmul([-Q(1,2),1], [-Q(1,2),1]), p)
        self.assertEqual(ip.polynomial_certificate(with_inside,z,alpha)['distinct_roots_open'],1)
        self.assertEqual(ip.polynomial_certificate(with_inside,alpha,one)['distinct_roots_open'],0)
        with_endpoint = a.pmul([0,-1,1],p)
        self.assertEqual(ip.polynomial_certificate(with_endpoint,z,alpha)['endpoint_multiplicities'],[1,1])
        self.assertEqual(ip.polynomial_certificate(with_endpoint,z,one)['distinct_roots_open'],1)

    def test_horner_coordinate_and_zero_identity(self):
        f = sqrt_field(); alpha = f.element([0,1])
        self.assertEqual(ip.evaluate([-1,0,2], f.element(0)), f.element(-1))
        self.assertEqual(ip.evaluate([-1,0,2], f.element(1)), f.element(1))
        self.assertTrue(ip.evaluate([-1,0,2], alpha).is_zero())
        proof = ip.polynomial_certificate([0], f.element(0), alpha)
        self.assertIsNone(proof['distinct_roots_open'])
        self.assertFalse(proof['strict_positive'])
        self.assertEqual(proof['weak_sign'],0)

    def test_strict_equality_and_signed_neighbors(self):
        f=sqrt_field();lo=f.element(0);hi=f.element([0,1]);eps=Q(1,1000000)
        sq=a.pmul([-1,0,2],[-1,0,2])
        self.assertFalse(ip.polynomial_certificate(sq,lo,hi)['strict_positive'])
        self.assertTrue(ip.polynomial_certificate(a.padd(sq,[eps]),lo,hi)['strict_positive'])
        self.assertFalse(ip.polynomial_certificate(a.padd(sq,[-eps]),lo,hi)['strict_positive'])
        # The inherited weak theorem excludes even interior roots too.
        weak=ip.polynomial_certificate([Q(1,4),-1,1],lo,hi)
        self.assertIsNone(weak['weak_sign'])
        self.assertEqual(weak['distinct_roots_open'],1)

    def test_phase_cell_boundaries_rates_and_exact_order(self):
        f=sqrt_field();z,alpha,one=f.element(0),f.element([0,1]),f.element(1)
        for lo,hi in ((z,alpha),(alpha,one)):
            for off,rate in ((Q(-1,8),Q(1,16)),(Q(-1,16),Q(-1,16))):
                self.assertEqual(ip.phase_cell(lo,hi,off,rate,1)['status'],'CERTIFIED')
        for off,expected in ((Q(-1,8),'CERTIFIED'),(Q(-1,8)+Q(1,1000000),'BLOCKED'),(Q(-1,8)-Q(1,1000000),'CERTIFIED')):
            self.assertEqual(ip.phase_cell(alpha,one,off,Q(1,16),1)['status'],expected)
        opposite=ip.phase_cell(z,alpha,Q(3,8),Q(1,16),1)
        self.assertEqual(opposite['diagonal_sign'],-1)
        with self.assertRaises(ValueError):ip.polynomial_certificate([1],alpha,z)
        other=a.RealField((-4999,0,10000),(Q(1,2),Q(3,4)),0)
        with self.assertRaises(ValueError):ip.polynomial_certificate([1],z,other.element([0,1]))

    def test_sturm_proof_mutation_nonexact_and_false_strict(self):
        f=sqrt_field();z=f.element(0);alpha=f.element([0,1]);p=[1,1]
        cert=ip.polynomial_certificate(p,z,alpha)
        self.assertTrue(ip.validate_polynomial_certificate(cert,p,z,alpha))
        for key,value in (('strict_positive',False),('distinct_roots_open',1),('variations',[50,49]),('sturm_sequence',[['1']]),('field',{})):
            bad=copy.deepcopy(cert);bad[key]=value
            with self.assertRaises(ValueError):ip.validate_polynomial_certificate(bad,p,z,alpha)
        for v in (1.0,True):
            with self.assertRaises((ValueError,TypeError)):ip.polynomial_certificate([v],z,alpha)

    def test_candidate_needs_two_distinct_closed_child_theorems(self):
        material=a._material(*candidate_args());f=candidate_field()
        z,alpha,one=f.element(0),f.element([0,1]),f.element(1)
        left=m.certify_derivative(material,f,z,alpha);right=m.certify_derivative(material,f,alpha,one)
        self.assertEqual((left['status'],left['mode']),('CERTIFIED','V42'))
        self.assertEqual((right['status'],right['mode']),('CERTIFIED','V43'))
        self.assertEqual(left['derivative_sign'],right['derivative_sign'])
        self.assertEqual(right['constraints'][0]['certificate']['endpoint_signs'][0],0)
        self.assertTrue(all(p['certificate']['strict_positive'] for p in right['orthants']))
        self.assertEqual(m.derivative_attempt(material,f,z,one,1,'V42')['status'],'BLOCKED')
        self.assertEqual(m.derivative_attempt(material,f,z,one,1,'V43')['status'],'BLOCKED')

    def test_complete_margin_equality_cannot_use_weak_admission(self):
        source=list(candidate_args());f=candidate_field();z=f.element(0);alpha=f.element([0,1])
        # Exact worst v42 margin at t=0, excluding harmonic-zero derivative.
        r=Q(1,16)
        constant=m.L*Q(7,20)-m.U*Q(1,2)-m.K*r*(m.W*Q(1,8)+m.U*Q(7,40))-m.K*2*r*Q(1,100000000)
        for delta,expected in ((-Q(1,1000000),'CERTIFIED'),(Q(0),'BLOCKED'),(Q(1,1000000),'BLOCKED')):
            cos=dict(source[0]);cos[0]=[0,constant+delta]
            material=a._material(cos,*source[1:])
            proof=m.derivative_attempt(material,f,z,alpha,1,'V42')
            self.assertEqual(proof['status'],expected)

    def test_residual_channels_and_global_chain_rule(self):
        args=list(candidate_args());args[0]=dict(args[0]);args[1]=dict(args[1])
        args[0][0]=[0,Q(1,10**8)];args[0][2]=[Q(1,10**8),Q(1,10**9)];args[1][2]=[Q(1,10**9),-Q(1,10**9)]
        mat=a._material(*args);f=candidate_field();z=f.element(0);alpha=f.element([0,1])
        result=m.derivative_attempt(mat,f,z,alpha,1,'V42')
        self.assertEqual(result['status'],'CERTIFIED')
        self.assertEqual({x['kind'] for x in result['retained_nonanchor_channels']}, {'C0_prime','C_prime','C_phase_upper','S_prime','S_phase_upper'})
        moved=a._material(args[0],args[1],args[2],('2','5'),Q(-1,8)-Q(1,24),Q(1,48))
        scaled=m.derivative_attempt(moved,f,z,alpha,1,'V42')
        self.assertEqual(scaled['parent_local_phase'],result['parent_local_phase'])
        self.assertEqual(scaled['orthants'],result['orthants'])
        self.assertEqual(scaled['global_derivative_scale'],'1/3')

    def test_summary_monotonicity_and_multiplicity_contradictions(self):
        d={'status':'CERTIFIED','derivative_sign':1}
        zero={'status':'ENDPOINT_CERTIFIED','relation':'ZERO','physical_multiplicity':1};neg={'status':'DECIDED','relation':'NEGATIVE'};pos={'status':'DECIDED','relation':'POSITIVE'}
        self.assertEqual(m.child_summary(d,neg,pos)['distinct_roots_open'],1)
        self.assertEqual(m.child_summary(d,zero,pos)['distinct_roots_open'],0)
        self.assertEqual(m.child_summary(d,pos,neg)['status'],'SEMANTIC_BLOCKER')
        self.assertEqual(m.child_summary(d,zero,zero)['status'],'SEMANTIC_BLOCKER')
        self.assertEqual(m.child_summary(d,neg,{**zero,'physical_multiplicity':2})['status'],'SEMANTIC_BLOCKER')
        self.assertEqual(m.child_summary(d,neg,{'relation':'UNKNOWN'})['status'],'BLOCKED')


def run():
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(AlgebraicIntervalTests))
    if not result.wasSuccessful():raise AssertionError('v47 core suite failed')

if __name__=='__main__':run()
