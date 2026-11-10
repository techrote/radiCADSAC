"""B1-E5 source-bound local order transport; standard-library unittest.

Execute from research/experimental/certificate-algebra/core on the literal
Draft branch: python3 -m unittest -v test_quotient_sided_germ.py
"""
from __future__ import annotations

import copy
from fractions import Fraction as Q
from itertools import product
import unittest

from certificate_algebra import (Piece, Refusal, EvidenceMeter, affine,
                                 base_record, verify_base)
from rational_quotient import derive as quotient_derive
from quotient_sided_germ import (derive, verify, project_signed_affine,
                                 taylor)


def raw(*parts):
    return base_record(tuple(parts))


def from_state(s):
    return {"pieces": [p.source() for p in s.pieces],
            "receipts": [c.record() for c in s.certs], "hash": s.hash}


def reverse(s):
    v = verify_base(s["pieces"], s["receipts"], EvidenceMeter())
    return from_state(affine(v, Q(2), Q(-1), EvidenceMeter()))


def family(k, c, d, sign=1):
    n = raw(Piece(Q(0), Q(1), (Q(0),)),
            Piece(Q(1), Q(2), (Q(0),)*k+(c,)))
    den = raw(Piece(Q(0), Q(1), (sign*d,)),
              Piece(Q(1), Q(2), (sign*d,)))
    return n, den


def attach(n, d, t='1'):
    q, _ = quotient_derive(n, d, numerator_pin=n['hash'],
                          denominator_pin=d['hash'])
    g, meter = derive(n, d, q, numerator_pin=n['hash'],
                      denominator_pin=d['hash'], time=t)
    return q, g, meter


class QuotientSidedGermTests(unittest.TestCase):
    def test_infinite_family_finite_representatives(self):
        count=0
        for k,c,d,s in product((1,2,3,8), (Q(1,3),Q(3),Q(-5,7)),
                               (Q(1,4),Q(2)), (1,-1)):
            n,den=family(k,c,d,s)
            q,g,m=attach(n,den)
            self.assertEqual(g['left'], {'kind':'IDENTITY_ZERO_SIDE'})
            self.assertEqual(g['right'], {'kind':'FINITE_ORDER','order':k,
                                          'leading':str(c/(s*d))})
            self.assertEqual(q['events']['identity_intervals'],[['0','1']])
            self.assertEqual(q['events']['isolated_points'],[])
            self.assertEqual(g['genuine_structural_knot'],'UNVERIFIED')
            self.assertEqual(g['source_piece_boundary_membership'],
                             {'numerator':True,'denominator':True})
            verified,_=verify(n,den,q,g,numerator_pin=n['hash'],
                               denominator_pin=den['hash'],time='1',
                               expected_germ_hash=g['germ_hash'])
            self.assertEqual(verified,g)
            self.assertEqual(m.full_leaf_checks,4)
            count += 1
        self.assertEqual(count,48)

    def test_signed_affine_order_leading_and_side_swap(self):
        for k in (1,2,3,5):
            n,d=family(k,Q(7,5),Q(3,2),-1)
            _,g,_=attach(n,d)
            prediction=project_signed_affine(g,offset='2',rate='-1')
            nn,dd=reverse(n),reverse(d)
            _,real,_=attach(nn,dd)
            self.assertEqual(prediction['time'],real['time'])
            self.assertEqual(prediction['left'],real['left'])
            self.assertEqual(prediction['right'],real['right'])
            self.assertEqual(real['right'],{'kind':'IDENTITY_ZERO_SIDE'})
            self.assertEqual(real['left']['leading'],str(Q(7,5)/-Q(3,2)*(-1)**k))
            self.assertEqual(prediction['status'],
                             'UNBOUND_PREDICTION_REVERIFY_TRANSFORMED_SOURCE')

    def test_refinement_boundary_is_not_a_physical_knot(self):
        n=raw(Piece(Q(0),Q(2),(Q(0),Q(2))))  # N(t)=t over [0,2]
        d=raw(Piece(Q(0),Q(1),(Q(2),)),
              Piece(Q(1),Q(2),(Q(2),)))
        q,g,_=attach(n,d)
        self.assertEqual(q['physical_knots'],['0','1','2'])
        self.assertEqual(g['partition_boundaries'],['0','1','2'])
        self.assertEqual(g['source_piece_boundary_membership'],
                         {'numerator':False,'denominator':True})
        self.assertEqual(g['genuine_structural_knot'],'UNVERIFIED')
        self.assertEqual(g['left'],{'kind':'FINITE_ORDER','order':0,'leading':'1/2'})
        self.assertEqual(g['right'],g['left'])

    def test_touch_at_two_sided_seam(self):
        n=raw(Piece(Q(0),Q(1),(Q(1),Q(-2),Q(1))),
              Piece(Q(1),Q(2),(Q(0),Q(0),Q(1))))
        d=raw(Piece(Q(0),Q(2),(Q(-2),)))
        q,g,_=attach(n,d)
        self.assertEqual(q['events']['isolated_points'][0]['kind'],'TOUCH')
        self.assertEqual(g['left'],{'kind':'FINITE_ORDER','order':2,'leading':'-1/2'})
        self.assertEqual(g['right'],g['left'])

    def test_identity_zero_and_domain_endpoints(self):
        n=raw(Piece(Q(0),Q(1),(Q(0),)),Piece(Q(1),Q(2),(Q(0),)))
        d=raw(Piece(Q(0),Q(2),(Q(3),)))
        for t,expect in [('0','ABSENT'),('1','IDENTITY_ZERO_SIDE'),('2','ABSENT')]:
            _,g,_=attach(n,d,t)
            if t == '0':
                self.assertEqual(g['left']['kind'],expect)
                self.assertEqual(g['right']['kind'],'IDENTITY_ZERO_SIDE')
            elif t == '2':
                self.assertEqual(g['right']['kind'],expect)
                self.assertEqual(g['left']['kind'],'IDENTITY_ZERO_SIDE')
            else:
                self.assertEqual(g['left']['kind'],expect)
                self.assertEqual(g['right']['kind'],expect)

    def test_denominator_seam_zero_must_refuse(self):
        n,d=family(2,Q(1),Q(1))
        bad=raw(Piece(Q(0),Q(1),(Q(1),Q(-1))),
                Piece(Q(1),Q(2),(Q(0),Q(1))))
        with self.assertRaises(Refusal):
            quotient_derive(n,bad,numerator_pin=n['hash'],
                            denominator_pin=bad['hash'])

    def test_wrong_pin_quotient_germ_and_time_refuse(self):
        n,d=family(2,Q(5),Q(2))
        q,g,_=attach(n,d)
        modified=copy.deepcopy(q);modified['denominator_closed_sign']='NEG'
        with self.assertRaises(Refusal):
            derive(n,d,modified,numerator_pin=n['hash'],
                   denominator_pin=d['hash'],time='1')
        bad=copy.deepcopy(g);bad['right']['order']=1
        with self.assertRaises(Refusal):
            verify(n,d,q,bad,numerator_pin=n['hash'],
                   denominator_pin=d['hash'],time='1')
        with self.assertRaises(Refusal):
            derive(n,d,q,numerator_pin=d['hash'],
                   denominator_pin=n['hash'],time='1')
        for t in ('-1','3','1/0','1.0'):
            with self.assertRaises(Refusal):
                derive(n,d,q,numerator_pin=n['hash'],
                       denominator_pin=d['hash'],time=t)

    def test_taylor_exact_series_and_nonzero_interior_point(self):
        p=Piece(Q(0),Q(2),(Q(1),Q(-8),Q(16))) # (2t-1)**2
        self.assertEqual(taylor(p,Q(1,2)),(Q(0),Q(0),Q(4)))
        n=raw(Piece(Q(0),Q(2),(Q(1),Q(2)))) # 1+t
        d=raw(Piece(Q(0),Q(2),(Q(2),)))
        _,g,_=attach(n,d,'1')
        self.assertEqual(g['left'],{'kind':'FINITE_ORDER','order':0,'leading':'1'})
        self.assertEqual(g['right'],g['left'])

    def test_projection_invalid_and_unbound(self):
        n,d=family(1,Q(1),Q(1))
        _,g,_=attach(n,d)
        with self.assertRaises(Refusal):
            project_signed_affine(g,offset='0',rate='0')
        with self.assertRaises(Refusal):
            project_signed_affine(g,offset='0',rate='0.5')
        with self.assertRaises(Refusal):
            project_signed_affine({'schema':'unknown'},offset='0',rate='1')
        projection=project_signed_affine(g,offset='1/3',rate='1/2')
        self.assertEqual(projection['time'],'4/3')
        self.assertEqual(projection['right']['order'],1)
        self.assertEqual(projection['right']['leading'],'1/2')


if __name__ == '__main__':
    unittest.main()
