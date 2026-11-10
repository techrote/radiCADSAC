"""Exact rational B1-E4 adversarial checks; run from this directory.

python3 -m unittest -v test_rational_quotient.py
"""
from __future__ import annotations

import copy
import unittest
from fractions import Fraction as Q
from itertools import product

from certificate_algebra import (Piece, EvidenceMeter, Refusal, affine,
                                 base_record, verify_base)
from rational_quotient import derive, verify


def _base(pieces):
    return base_record(tuple(pieces))


def _numerator(a, mode='CROSS'):
    if mode == 'CROSS':
        # N(t)=t-a, with single-sided weak cones around its exact root.
        return _base([Piece(Q(0), a, (-a, a)),
                      Piece(a, Q(1), (Q(0), Q(1)-a))])
    if mode == 'TOUCH':
        return _base([Piece(Q(0), a, (a*a, -2*a*a, a*a)),
                      Piece(a, Q(1), (Q(0), Q(0), (1-a)**2))])
    if mode == 'CONTINUUM':
        return _base([Piece(Q(0), a, (Q(0),)),
                      Piece(a, Q(1), (Q(0), Q(1)-a))])
    raise AssertionError(mode)


def _denominator(b, c, sign=1):
    # D(t)=sign*(c+(t-b)^2), partitioned at b. Both pieces have
    # exact nonnegative Bernstein vectors and strict nonzero endpoints.
    return _base([
        Piece(Q(0), b, tuple(sign*z for z in (c+b*b, -2*b*b, b*b))),
        Piece(b, Q(1), tuple(sign*z for z in (c, Q(0), (1-b)**2))),
    ])


def _value(raw, t):
    ps = tuple(Piece(Q(p['left']), Q(p['right']), tuple(Q(c) for c in p['coeff']))
               for p in raw['pieces'])
    for p in ps:
        if p.left <= t <= p.right:
            return p.at(t)
    raise AssertionError('outside source')


def _reversed(raw):
    m = EvidenceMeter()
    s = verify_base(raw['pieces'], raw['receipts'], m)
    r = affine(s, Q(1), Q(-1), EvidenceMeter())
    return {'pieces':[p.source() for p in r.pieces],
            'receipts':[c.record() for c in r.certs], 'hash':r.hash}


class RationalQuotientTests(unittest.TestCase):
    def _derive(self, n, d):
        return derive(n,d,numerator_pin=n['hash'],denominator_pin=d['hash'])

    def test_infinite_rational_family_representatives(self):
        cases = 0
        for a,b,c,sig in product((Q(1,4),Q(1,2),Q(3,4)),
                                 (Q(1,3),Q(2,3)),
                                 (Q(1,2),Q(1),Q(3,2)), (-1,1)):
            n,d = _numerator(a),_denominator(b,c,sig)
            receipt,meter = self._derive(n,d)
            self.assertEqual(receipt['denominator_closed_sign'],
                             'POS' if sig>0 else 'NEG')
            self.assertEqual(receipt['events']['identity_intervals'],[])
            self.assertEqual([(ev['time'],ev['kind']) for ev in receipt['events']['isolated_points']],
                             [(str(a),'CROSS')])
            self.assertEqual(meter.full_leaf_checks,4)  # two parents, two leaves each
            for i in range(1,10):
                t=Q(i,10)
                if t==a: continue
                q=_value(n,t)/_value(d,t)
                self.assertEqual((q>0)-(q<0),sig*((t>a)-(t<a)))
            self.assertEqual(verify(n,d,receipt,numerator_pin=n['hash'],
                                    denominator_pin=d['hash'])[0],receipt)
            cases+=1
        self.assertEqual(cases,36)

    def test_touch_and_continuum(self):
        for mode in ('TOUCH','CONTINUUM'):
            n,d=_numerator(Q(1,2),mode),_denominator(Q(1,3),Q(1),-1)
            receipt,_=self._derive(n,d)
            if mode=='TOUCH':
                self.assertEqual([x['kind'] for x in receipt['events']['isolated_points']], ['TOUCH'])
                self.assertEqual(set(receipt['open_piece_signs']),{'NEG'})
            else:
                self.assertEqual(receipt['events']['identity_intervals'],[['0','1/2']])
                self.assertEqual(receipt['events']['isolated_points'],[])
                self.assertEqual(receipt['open_piece_signs'][0],'ZERO')

    def test_denominator_zero_at_genuine_seam_refuses(self):
        b=Q(1,3)
        n=_numerator(Q(1,2))
        bad=_base([Piece(Q(0),b,(b*b,-2*b*b,b*b)),
                   Piece(b,Q(1),(Q(0),Q(0),(1-b)**2))])
        with self.assertRaises(Refusal): self._derive(n,bad)

    def test_forged_parent_and_quotient_and_external_pin_refuse(self):
        n,d=_numerator(Q(1,2)),_denominator(Q(1,3),Q(1))
        receipt,_=self._derive(n,d)
        fake=copy.deepcopy(n)
        fake['pieces'][1]['coeff']=['0','2']
        with self.assertRaises(Refusal): self._derive(fake,d)
        forged=copy.deepcopy(receipt)
        forged['events']['isolated_points'][0]['kind']='TOUCH'
        with self.assertRaises(Refusal): verify(n,d,forged,numerator_pin=n['hash'],denominator_pin=d['hash'])
        with self.assertRaises(Refusal): derive(n,d,numerator_pin=d['hash'],denominator_pin=n['hash'])
        with self.assertRaises(Refusal): verify(n,d,receipt,numerator_pin=n['hash'],denominator_pin=d['hash'],expected_quotient_hash='0'*64)

    def test_negative_affine_source_reversal_swaps_event_sides(self):
        n,d=_numerator(Q(1,4)),_denominator(Q(1,3),Q(1))
        r,_=self._derive(n,d)
        nn,dd=_reversed(n),_reversed(d)
        rev,_=self._derive(nn,dd)
        self.assertEqual(rev['events']['isolated_points'][0]['time'],'3/4')
        ev,rr=r['events']['isolated_points'][0],rev['events']['isolated_points'][0]
        self.assertEqual((ev['left'],ev['right']),(rr['right'],rr['left']))

    def test_a2_same_local_germ_different_global_source_refuses(self):
        # Two right-hand Bernstein control vectors have same first two
        # controls (same local value/first-sided jet), different full zeros.
        # A complete parent source receipt, not that local germ, is required.
        left=Piece(Q(0),Q(1,2),(Q(0),))
        right=Piece(Q(1,2),Q(1),(Q(0),Q(1)))
        n=_base([left,right])
        d=_denominator(Q(1,3),Q(1))
        receipt,_=self._derive(n,d)
        substituted=copy.deepcopy(n)
        # Right Bernstein [0,1/2,1] -> [0,1/2,-1]; preserve first
        # derivative at left, introduce a new interior crossing.
        substituted['pieces'][1]['coeff']=['0','1','-2']
        with self.assertRaises(Refusal):
            self._derive(substituted,d)
        self.assertEqual(receipt['events']['identity_intervals'],[['0','1/2']])

    def test_positive_but_weak_cone_unknown_is_conservative_refusal(self):
        # P(u)=(1-2u)^2+epsilon > 0, but B1 Bernstein middle
        # coefficient epsilon-1 is negative when 0<epsilon<1.
        # Correctly outside this particular sufficient certificate grammar.
        with self.assertRaises(Refusal):
            _base([Piece(Q(0),Q(1),(Q(5,4),Q(-4),Q(4)))])

    def test_non_matching_domain_refuses(self):
        n=_numerator(Q(1,2))
        d=_base([Piece(Q(0),Q(1,2),(Q(1),))])
        with self.assertRaises(Refusal): self._derive(n,d)

    def test_genuine_zero_at_new_knot_preserved(self):
        a,b=Q(1,2),Q(1,3)
        n,d=_numerator(a),_denominator(b,Q(1))
        r,m=self._derive(n,d)
        self.assertEqual(r['physical_knots'],['0','1/3','1/2','1'])
        self.assertEqual(r['events']['isolated_points'][0]['time'],'1/2')
        self.assertEqual(len(r['open_piece_signs']),3)
        self.assertEqual(m.full_leaf_checks,4)
        self.assertEqual(m.transform_checks,2+3)


if __name__=='__main__': unittest.main()
