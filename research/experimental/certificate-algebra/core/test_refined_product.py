"""Adversarial deterministic controls for B1-E3 unaligned C0 partitions."""
import copy
from fractions import Fraction as Q
from math import comb
import unittest

from certificate_algebra import (EvidenceMeter, Piece, Refusal, affine,
                                 base_record, bernstein)
from refined_product import derive, verify


def section(lo, hi, c, neg=False):
    # Physical p(t) = +/-[1+c*t*(1-t)], in the local B1 power basis.
    a = Q(hi-lo)
    z = [1+c*lo*(1-lo), c*a*(1-2*lo), -c*a*a]
    if c == 0:
        z = z[:1]
    if neg:
        z = [-v for v in z]
    return Piece(lo, hi, tuple(z))


def source(bounds, c=Q(0), neg=False):
    return base_record(tuple(section(l,r,c,neg) for l,r in zip(bounds,bounds[1:])))


def raw_state(s):
    return {"pieces": [p.source() for p in s.pieces],
            "receipts": [c.record() for c in s.certs], "hash": s.hash}


class RefinedProductTests(unittest.TestCase):
    def setUp(self):
        self.a = source([Q(0),Q(1,3),Q(1)],Q(2))
        self.b = source([Q(0),Q(1,2),Q(1)],Q(3),True)

    def test_unaligned_rational_family_fresh_oracle(self):
        cases = 0
        for c in (Q(0),Q(1,5),Q(1),Q(7,3),Q(17)):
            for d in (Q(0),Q(1,7),Q(2),Q(11)):
                a = source([Q(0),Q(1,3),Q(1)],c)
                b = source([Q(0),Q(1,2),Q(1)],d,True)
                s,w,m = derive(a,b,left_pin=a['hash'],right_pin=b['hash'])
                checked,_ = verify(a,b,w,left_pin=a['hash'],right_pin=b['hash'],
                                   expected_product_pin=s.hash)
                self.assertEqual(checked.hash,s.hash)
                self.assertEqual(w['physical_knots'], ['0','1/3','1/2','1'])
                self.assertEqual(w['events'], {'identity_intervals':[], 'isolated_points':[]})
                self.assertEqual([c.sign for c in s.certs], ['NEG']*3)
                self.assertEqual(m.full_leaf_checks, 4) # no output leaf reproving
                self.assertEqual(m.transform_checks, 5) # two splits + 3 products
                for p,cert in zip(s.pieces,s.certs):
                    self.assertEqual(bernstein(p),cert.b) # independent output proof
                    for u in (Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1)):
                        t=p.left+(p.right-p.left)*u
                        self.assertEqual(p.at(t), -(1+c*t*(1-t))*(1+d*t*(1-t)))
                cases += 1
        self.assertEqual(cases,20)

    def test_identity_continuum_and_inserted_knot(self):
        a=base_record((Piece(Q(0),Q(1,2),(Q(0),)),
                       Piece(Q(1,2),Q(1),(Q(0),Q(1,2)))))
        b=source([Q(0),Q(1,3),Q(1)],Q(0))
        s,w,_=derive(a,b,left_pin=a['hash'],right_pin=b['hash'])
        self.assertEqual(w['events']['identity_intervals'],[['0','1/2']])
        self.assertEqual(w['events']['isolated_points'],[])
        self.assertEqual([c.sign for c in s.certs],['ZERO','ZERO','POS'])

    def test_cross_at_knot_owned_once(self):
        a=base_record((Piece(Q(0),Q(1,2),(Q(-1,2),Q(1,2))),
                       Piece(Q(1,2),Q(1),(Q(0),Q(1,2)))))
        b=source([Q(0),Q(1,3),Q(1)],Q(0))
        _,w,_=derive(a,b,left_pin=a['hash'],right_pin=b['hash'])
        self.assertEqual(w['events']['isolated_points'],[
            {'time':'1/2','kind':'CROSS','left':'NEG','right':'POS'}])
        self.assertEqual(w['events']['identity_intervals'],[])

    def test_signed_reversal(self):
        s,w,_=derive(self.a,self.b,left_pin=self.a['hash'],right_pin=self.b['hash'])
        r=affine(s,Q(1),Q(-1),EvidenceMeter())
        self.assertEqual([p.left for p in r.pieces],[Q(0),Q(1,2),Q(2,3)])
        for t in (Q(0),Q(1,5),Q(1,2),Q(4,5),Q(1)):
            expected=-(1+2*(1-t)*t)*(1+3*(1-t)*t)
            self.assertEqual(next(p.at(t) for p in r.pieces if p.left<=t<=p.right),expected)
        self.assertEqual(w['events']['isolated_points'],[])

    def test_source_alias_and_forged_witness_refused(self):
        _,w,_=derive(self.a,self.b,left_pin=self.a['hash'],right_pin=self.b['hash'])
        tampered=copy.deepcopy(self.a)
        tampered['pieces'][1]['coeff'][0] = '100'
        with self.assertRaises(Refusal):
            verify(tampered,self.b,w,left_pin=self.a['hash'],right_pin=self.b['hash'])
        for key, changed in [('product_hash','0'*64),
                             ('physical_knots',['0','1/3','1']),
                             ('leaf_signs',['POS']*3),
                             ('events',{'identity_intervals':[['0','1']], 'isolated_points':[]})]:
            forged=copy.deepcopy(w);forged[key]=changed
            with self.assertRaises(Refusal):
                verify(self.a,self.b,forged,left_pin=self.a['hash'],right_pin=self.b['hash'])
        with self.assertRaises(Refusal):
            verify(self.a,self.b,w,left_pin=self.a['hash'],right_pin=self.b['hash'],
                   expected_product_pin='f'*64)

    def test_same_knot_germ_but_extra_root_fails_sign_cone(self):
        # Right-cell b=(0,1/2,1) has order-one positive germ at knot;
        # changing ONLY last Bernstein control to -1 preserves the germ
        # but inserts a root. No complete B1 certificate exists for it.
        a=base_record((Piece(Q(0),Q(1),(Q(0),)),
                       Piece(Q(1),Q(2),(Q(0),Q(1)))))
        b=source([Q(0),Q(1,2),Q(2)],Q(0))
        _,w,_=derive(a,b,left_pin=a['hash'],right_pin=b['hash'])
        changed=copy.deepcopy(a)
        changed['pieces'][1]['coeff']=['0','1','-2']
        with self.assertRaises(Refusal):
            verify(changed,b,w,left_pin=a['hash'],right_pin=b['hash'])
        # Even supplying a fresh self-authored pin and newly computed receipt
        # cannot turn the mixed-sign Bernstein cell into a nonzero proof.
        with self.assertRaises(Refusal):
            derive(changed,b,left_pin=a['hash'],right_pin=b['hash'])

    def test_e3_e4_e5_reject_hostile_parent_mapping_keys(self):
        # B1-D3: the real E3 parent boundary is shared by refined product,
        # E4 rational quotient and E5 sided germ. A string-subclass key must
        # not masquerade as a genuine builtin field even if the *values* and
        # independently held snapshot hashes remain otherwise correct.
        from rational_quotient import derive as quotient_derive
        from quotient_sided_germ import derive as germ_derive

        class AliasKey(str):
            def __new__(cls, alias):
                obj = str.__new__(cls, 'untrusted-alien-field')
                obj.alias = alias
                return obj
            def __hash__(self):
                return hash(self.alias)
            def __eq__(self, other):
                return other == self.alias

        n = base_record((Piece(Q(0), Q(1), (Q(2),)),))
        d = base_record((Piece(Q(0), Q(1), (Q(3),)),))
        # Positive controls: valid E3, E4 and E5 still replay exactly.
        _, product_receipt, _ = derive(n, d, left_pin=n['hash'], right_pin=d['hash'])
        verify(n, d, product_receipt, left_pin=n['hash'], right_pin=d['hash'])
        quotient_receipt, _ = quotient_derive(n, d, numerator_pin=n['hash'],
                                               denominator_pin=d['hash'])
        germ, _ = germ_derive(n, d, quotient_receipt,
                              numerator_pin=n['hash'], denominator_pin=d['hash'],
                              time='1/2')
        self.assertEqual(germ['left']['leading'], '2/3')
        for field in ('pieces', 'receipts', 'hash'):
            with self.subTest(field=field):
                forged = dict(n)
                value = forged.pop(field)
                forged[AliasKey(field)] = value
                self.assertFalse(any(type(k) is str and k == field for k in forged))
                # No fresh pins; these remain the genuine, externally selected
                # original parent snapshot hashes. The problem is Python key
                # equality/grammar execution before structural source admission.
                with self.assertRaises(Refusal):
                    derive(forged, d, left_pin=n['hash'], right_pin=d['hash'])
                with self.assertRaises(Refusal):
                    quotient_derive(forged, d, numerator_pin=n['hash'],
                                    denominator_pin=d['hash'])
                with self.assertRaises(Refusal):
                    germ_derive(forged, d, quotient_receipt,
                                numerator_pin=n['hash'], denominator_pin=d['hash'],
                                time='1/2')
        # Recursive and overbudget graphs must refuse at shared ingress.
        for hostile in (('oversize', 'x'*4097), ('cycle', None)):
            with self.subTest(hostile=hostile[0]):
                forged = dict(n)
                forged['hash'] = hostile[1] if hostile[1] is not None else forged
                with self.assertRaises(Refusal):
                    derive(forged, d, left_pin=n['hash'], right_pin=d['hash'])

    def test_boundary_and_budget_refusals(self):
        wrong=source([Q(0),Q(1,2),Q(2)],Q(0))
        with self.assertRaises(Refusal):
            derive(self.a,wrong,left_pin=self.a['hash'],right_pin=wrong['hash'])
        for n,m in ((13,12),(20,5)):
            a=base_record((Piece(Q(0),Q(1),tuple(Q(comb(n,k)) for k in range(n+1))),))
            b=base_record((Piece(Q(0),Q(1),tuple(Q(comb(m,k)) for k in range(m+1))),))
            with self.assertRaises(Refusal):
                derive(a,b,left_pin=a['hash'],right_pin=b['hash'])
        a=source([Q(i,66) for i in range(67)],Q(0))
        b=source([Q(i,67) for i in range(68)],Q(0))
        with self.assertRaises(Refusal):
            derive(a,b,left_pin=a['hash'],right_pin=b['hash'])


if __name__ == '__main__':
    unittest.main()
