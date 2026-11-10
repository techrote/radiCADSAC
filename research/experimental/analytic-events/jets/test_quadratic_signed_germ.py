#!/usr/bin/env python3
"""Deterministic exact Fraction challenges for quadratic signed germs."""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction as Q
from math import comb
import unittest

import quadratic_signed_germ as z


def product(a,b):
    out=[Q(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            out[i+j]+=x*y
    return out


def power(poly,k):
    out=[Q(1)]
    for _ in range(k):
        out=product(out,poly)
    return out


def direct_order(p,t,D):
    # Independent formal derivative/Taylor oracle, not repeated polynomial division.
    for j in range(len(p)):
        coeffs=[p[k]*comb(k,j) for k in range(j,len(p))]
        if z.qsign(z.qeval(coeffs,t,D),D)!=0:
            return j
    return None


class QuadraticSignedGermTests(unittest.TestCase):
    def make(self,D,k,rate,sign=1):
        amp=power([Q(-D),Q(0),Q(1)],k)
        return z.source(-10,10,0,rate,
                        {0:([sign*c for c in amp],[]),
                         1:([],[-sign*c for c in amp])})

    def test_infinite_family_finite_controls(self):
        # (t^2-D)^k [1-sin(2pi*rate*t)] is positive apart from its algebraic
        # factor. A sine of +/-1 would force a rational quarter-turn phase.
        n=0
        for D in (2,3,5,7):
            for k in range(7):
                for v in (-1,1):
                    for rate in (Q(1,4),Q(-1,4)):
                        s=self.make(D,k,rate)
                        r=z.analyze(s,0,v,D)
                        self.assertEqual(r['order'],k)
                        self.assertEqual(r['status'], 'EXACT_POINT_ZERO' if k else 'EXACT_POINT_NONZERO')
                        self.assertEqual(r['right_sign'],v**k)
                        self.assertEqual(r['left_sign'],(-1)**k*v**k)
                        self.assertTrue(z.verify(s,0,v,D,r))
                        n+=1
        self.assertEqual(n,112)

    def test_independent_taylor_oracle(self):
        n=0
        for D in (2,3,6):
            for u,v in ((0,1),(Q(1,3),Q(2,5))):
                for k in range(6):
                    m=[u*u-D*v*v,-2*u,Q(1)]
                    p=product(power(m,k),[Q(3),Q(-2),Q(1)])
                    # Shifted Taylor and div-by-minpoly agree at the exact root.
                    self.assertEqual(z.valuation(p,m), direct_order(p,(u,v),D))
                    n+=1
        self.assertEqual(n,36)

    def test_negative_leading_factor_and_reversed_sign(self):
        s=self.make(3,3,Q(-1,7),sign=-1)
        r=z.analyze(s,0,1,3)
        self.assertEqual((r['left_sign'],r['right_sign']),(1,-1))
        self.assertEqual(r['event_kind'],'CROSSING')
        self.assertTrue(z.verify(s,0,1,3,r))

    def test_near_quarter_turn_cancellation(self):
        # sqrt(2)*q/p ~ 1: the sign of 1-sin(pi/2 + tiny) is positive,
        # while fixed low-precision sampling can see zero.
        levels=[]
        for p,q in ((99,70),(114243,80782),(665857,470832),
                    (22619537,15994428)):
            s=z.source(-4,4,0,Q(q,4*p),{0:([1],[]),1:([],[-1])})
            r=z.analyze(s,0,1,2)
            self.assertEqual(r['right_sign'],1)
            w=r['leading_G_enclosure']
            self.assertGreater(int(w['lower_integer']),0)
            self.assertTrue(z.verify(s,0,1,2,r))
            levels.append(r['sign_precision'])
        self.assertGreater(levels[-1],levels[0])

    def test_zero_piece_nonzero_and_contact(self):
        zero=z.source(-4,4,0,Q(1,4),{0:([],[]),1:([],[])})
        r=z.analyze(zero,0,1,2)
        self.assertEqual(r['status'],'IDENTITY_ZERO_ANALYTIC_SPAN')
        self.assertIsNone(r['order'])
        self.assertTrue(z.verify(zero,0,1,2,r))
        s=self.make(2,2,Q(1,7))
        r=z.analyze(s,0,1,2)
        self.assertEqual(r['event_kind'],'TANGENCY')
        self.assertEqual((r['left_sign'],r['right_sign']),(1,1))

    def test_nonsensical_and_untrusted_source_refused(self):
        with self.assertRaises(z.Refusal):
            z.source(-4,4,Q(1,4),0,{0:([1],[]),1:([],[-1])})
        with self.assertRaises(z.Refusal):
            z.source(-4,4,0,Q(1,4),{0:([1],[1])})
        with self.assertRaises(z.Refusal):
            z.analyze(self.make(2,1,Q(1,4)),0,0,2)
        with self.assertRaises(z.Refusal):
            z.analyze(self.make(2,1,Q(1,4)),0,1,4)
        with self.assertRaises(z.Refusal):
            z.analyze(z.source(-1,1,0,Q(1,4),{1:([1],[])}),0,1,2)

    def test_adversarial_receipt_identity_and_types(self):
        s=self.make(2,2,Q(1,4))
        valid=z.analyze(s,0,1,2)
        self.assertTrue(z.verify(s,0,1,2,valid))
        for field,bad in [('order',True),('right_sign',-1),('production_authorized',1),
                          ('quadratic_time',['0','-1',2]),('source_time_sha256','0'*64)]:
            fake=deepcopy(valid)
            fake[field]=bad
            with self.assertRaises(z.Refusal):
                z.verify(s,0,1,2,fake)
        class Lie(str):
            def __eq__(self,other):
                return True
        fake=deepcopy(valid)
        fake['status']=Lie('FORGED')
        with self.assertRaises(z.Refusal):
            z.verify(s,0,1,2,fake)
        other=self.make(2,2,Q(1,7))
        with self.assertRaises(z.Refusal):
            z.verify(other,0,1,2,valid)


if __name__=='__main__':
    unittest.main(verbosity=2)
