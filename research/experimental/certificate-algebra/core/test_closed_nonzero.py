"""Deterministic B1-E2 controls; run from the B1 core directory.

python3 -m unittest -v test_closed_nonzero.py
"""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction as Q
import unittest

from certificate_algebra import (
    EvidenceMeter, Piece, Refusal, affine, base_record, bernstein,
    check_leaf, check_seam, enc, split, verify_base,
)
from product_cone import product
from closed_nonzero import (
    verify_closed_base, verify_closed_journal, verify_closed_product,
)


def record(*pieces: Piece):
    return base_record(tuple(pieces))


def pos(lo=0, hi=1):
    # f(u)=(1-u)^2+u^2 has b=(1,0,1); A1's all-b_i>0 rejects.
    return Piece(Q(lo), Q(hi), (Q(1), Q(-2), Q(2)))


class ClosedNonzeroTests(unittest.TestCase):
    def test_strict_positive_with_zero_interior_bernstein_coefficient(self):
        p = pos()
        self.assertEqual(bernstein(p), (Q(1), Q(0), Q(1)))
        raw = record(p)
        s, proof, meter = verify_closed_base(raw, source_pin=raw['hash'])
        self.assertEqual(proof['closed_sign'], 'POS')
        self.assertEqual(proof['physical_interval'], ['0', '1'])
        self.assertEqual((meter.full_leaf_checks, meter.seam_checks), (1, 0))
        verify_closed_base(raw, source_pin=raw['hash'], proposed=proof)
        forged = dict(proof, closed_sign='NEG')
        with self.assertRaises(Refusal):
            verify_closed_base(raw, source_pin=raw['hash'], proposed=forged)

    def test_b5_seam_touch_is_not_closed_positive(self):
        # POS on both OPEN cells; both vanish at the shared C0 knot.
        left = Piece(Q(0), Q(1,2), (Q(1), Q(-1)))
        right = Piece(Q(1,2), Q(1), (Q(0), Q(1)))
        raw = record(left, right)
        self.assertEqual(verify_base(raw['pieces'],raw['receipts'],EvidenceMeter()).certs[0].sign,'POS')
        with self.assertRaisesRegex(Refusal,'zero boundary'):
            verify_closed_base(raw, source_pin=raw['hash'])

    def test_negative_factor_and_zero_continuum(self):
        neg = record(Piece(Q(-2), Q(5), (Q(-3),)))
        self.assertEqual(verify_closed_base(neg, source_pin=neg['hash'])[1]['closed_sign'],'NEG')
        zero = record(Piece(Q(0), Q(1), (Q(0),)))
        with self.assertRaises(Refusal):
            verify_closed_base(zero, source_pin=zero['hash'])
        edge = record(Piece(Q(0),Q(1),(Q(0),Q(1))))
        with self.assertRaises(Refusal):
            verify_closed_base(edge,source_pin=edge['hash'])

    def test_source_pin_receipt_and_source_substitution(self):
        raw = record(pos())
        forged = deepcopy(raw)
        forged['pieces'][0]['coeff'][0] = '3'
        for other, pin in [(forged, raw['hash']), (raw, 'f'*64)]:
            with self.assertRaises(Refusal):
                verify_closed_base(other, source_pin=pin)
        bad = deepcopy(raw)
        bad['receipts'][0]['bernstein'][0]='17'
        with self.assertRaises(Refusal):
            verify_closed_base(bad,source_pin=raw['hash'])
        with self.assertRaises(Refusal):
            verify_closed_base(raw,source_pin='unknown')

    def test_exact_product_sign_without_output_leaf_reproof(self):
        a = record(pos())
        b = record(Piece(Q(0),Q(1),(Q(-1),Q(-1))))
        out, witness, initial_meter = product(a,b,left_pin=a['hash'],right_pin=b['hash'])
        s, proof, meter = verify_closed_product(
            a,b,witness,left_pin=a['hash'],right_pin=b['hash'],product_pin=out.hash)
        self.assertEqual(proof['closed_sign'],'NEG')
        self.assertEqual(proof['source_class'],'PRODUCT')
        self.assertEqual(meter.full_leaf_checks,2)   # both parents
        self.assertEqual(meter.transform_checks,1)   # exact Bernstein convolution
        # Independent fresh proof on output is only a comparison, not consumer work.
        shadow = EvidenceMeter()
        for p,c in zip(s.pieces,s.certs):
            check_leaf(p,c,shadow)
        self.assertEqual(shadow.full_leaf_checks,1)
        forged = dict(witness, signs=['POS'])
        with self.assertRaises(Refusal):
            verify_closed_product(a,b,forged,left_pin=a['hash'],right_pin=b['hash'],product_pin=out.hash)
        with self.assertRaises(Refusal):
            verify_closed_product(a,b,witness,left_pin=a['hash'],right_pin=b['hash'],product_pin='0'*64)
        with self.assertRaises(Refusal):
            verify_closed_product(a,b,witness,left_pin=a['hash'],right_pin=b['hash'],product_pin=out.hash, proposed=dict(proof,closed_sign='POS'))

    def test_product_with_endpoint_touch_refuses(self):
        a = record(Piece(Q(0),Q(1,2),(Q(1),Q(-1))),
                   Piece(Q(1,2),Q(1),(Q(0),Q(1))))
        b = record(Piece(Q(0),Q(1,2),(Q(1),)),Piece(Q(1,2),Q(1),(Q(1),)))
        s,w,_ = product(a,b,left_pin=a['hash'],right_pin=b['hash'])
        with self.assertRaisesRegex(Refusal,'zero boundary'):
            verify_closed_product(a,b,w,left_pin=a['hash'],right_pin=b['hash'],product_pin=s.hash)

    def test_split_signed_affine_journal_preserves_closed_nonzero(self):
        raw = record(pos())
        s = verify_base(raw['pieces'],raw['receipts'],EvidenceMeter())
        t = split(s,0,Q(1,2),EvidenceMeter())
        u = affine(t,Q(1),Q(-2),EvidenceMeter())
        self.assertEqual([p.left for p in u.pieces],[Q(0),Q(1,4)])
        log = {'schema':'b1-journal-v1','base':raw,'steps':[
            {'op':'split','before':s.hash,'after':t.hash,'index':0,'cut':'1/2'},
            {'op':'affine','before':t.hash,'after':u.hash,'offset':'1','rate':'-2'},
        ]}
        final, proof, meter = verify_closed_journal(log,base_pin=s.hash,final_pin=u.hash)
        self.assertEqual(proof['closed_sign'],'POS')
        self.assertEqual(proof['physical_interval'], ['0','1/2'])
        self.assertEqual(proof['source_class'],'JOURNAL')
        self.assertEqual(meter.full_leaf_checks,1)
        self.assertGreaterEqual(meter.transform_checks,3)
        with self.assertRaises(Refusal):
            verify_closed_journal(log,base_pin=s.hash,final_pin='0'*64)
        attack = deepcopy(log)
        attack['steps'][0]['cut']='1/3'
        with self.assertRaises(Refusal):
            verify_closed_journal(attack,base_pin=s.hash,final_pin=u.hash)

    def test_mutation_replay_does_not_reuse_obsolete_nonzero_claim(self):
        raw = record(pos())
        s = verify_base(raw['pieces'],raw['receipts'],EvidenceMeter())
        # One-cell update is C0-trivial; removes left endpoint strictness.
        from certificate_algebra import replace
        new = replace(s,0,(Q(0),Q(1)),EvidenceMeter())
        log = {'schema':'b1-journal-v1','base':raw,'steps':[
            {'op':'replace','before':s.hash,'after':new.hash,'index':0,'coeff':['0','1']},
        ]}
        with self.assertRaisesRegex(Refusal,'zero boundary'):
            verify_closed_journal(log,base_pin=s.hash,final_pin=new.hash)
        with self.assertRaises(Refusal):
            verify_closed_journal(log,base_pin='a'*64,final_pin=new.hash)

    def test_48_member_infinite_family_control_and_naive_work(self):
        # A bounded cross-section of the proved infinite rational family.
        for n in range(1,9):
            for k in range(1,7):
                f = record(Piece(Q(0),Q(1),(Q(1),Q(n,k),Q(-n,k))))
                g = record(Piece(Q(0),Q(1),(Q(-1),Q(-k,n),Q(k,n))))
                s,w,_=product(f,g,left_pin=f['hash'],right_pin=g['hash'])
                _,cert,_=verify_closed_product(f,g,w,left_pin=f['hash'],right_pin=g['hash'],product_pin=s.hash)
                self.assertEqual(cert['closed_sign'],'NEG')
        n=16
        left=[];right=[]
        for i in range(n):
            left.append(Piece(Q(i),Q(i+1),(Q(1),Q(i+1,7),Q(-(i+1),7))))
            right.append(Piece(Q(i),Q(i+1),(Q(-1),Q(-(i+1),9),Q(i+1,9))))
        a,b=record(*left),record(*right)
        s,w,m=product(a,b,left_pin=a['hash'],right_pin=b['hash'])
        _,proof,pm=verify_closed_product(a,b,w,left_pin=a['hash'],right_pin=b['hash'],product_pin=s.hash)
        self.assertEqual(pm.full_leaf_checks,2*n)
        self.assertEqual(pm.seam_checks,2*(n-1))
        self.assertEqual(pm.transform_checks,n)
        naive=EvidenceMeter()
        for p,c in zip(s.pieces,s.certs): check_leaf(p,c,naive)
        for x,y in zip(s.pieces,s.pieces[1:]): check_seam(x,y,naive)
        self.assertEqual((naive.full_leaf_checks,naive.seam_checks),(n,n-1))

    def test_misaligned_product_partitions_refuse(self):
        a = record(pos(0,1))
        b = record(pos(1,2))
        with self.assertRaises(Refusal):
            product(a,b,left_pin=a['hash'],right_pin=b['hash'])


if __name__ == '__main__':
    unittest.main()
