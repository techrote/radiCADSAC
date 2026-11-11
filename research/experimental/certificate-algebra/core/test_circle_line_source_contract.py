"""B1-D22 independent second-geometry qualification: exact line/circle intersections.

Distinct from the cubic C0 spline-shaped A2 source: a straight parameterized
line x=t,y=0 intersecting the circle (x-1/2)^2+y^2=(1/6)^2.
This is an exact scalar-implicit polynomial source, NOT a physical kernel/STEP
certificate or authenticated machining geometry provenance.
"""
from __future__ import annotations

import unittest
from fractions import Fraction as Q

from certificate_algebra import (Piece, Refusal, EvidenceMeter, affine,
    base_record, events, replace, split, verify_base)

CENTER = Q(1, 2)
RADIUS = Q(1, 6)
BREAKS = (Q(0), Q(1, 3), Q(2, 3), Q(1))


def circle_residual(t: Q) -> Q:
    return (t-CENTER)**2 - RADIUS**2


def interval_piece(left: Q, right: Q) -> Piece:
    width = right-left
    # Independent substitution of the 2D circle's implicit polynomial,
    # rather than a Bernstein certificate or a B1-provided polynomial helper.
    return Piece(left,right,(circle_residual(left), 2*(left-CENTER)*width, width**2))


def fixture():
    ps = tuple(interval_piece(l,r) for l,r in zip(BREAKS,BREAKS[1:]))
    original = base_record(ps)
    m = EvidenceMeter()
    checked = verify_base(original['pieces'],original['receipts'],m)
    return original, checked


class DifferentGeometryCircleLine(unittest.TestCase):
    def test_implicit_circle_two_crossings_split_signed_affine(self):
        original, state = fixture()
        self.assertEqual(len(original['pieces']),3)
        self.assertEqual([c.sign for c in state.certs],['POS','NEG','POS'])
        self.assertEqual(events(state),{'identity_intervals':[], 'isolated_points':[
            {'time':'1/3','kind':'CROSS','left':'POS','right':'NEG'},
            {'time':'2/3','kind':'CROSS','left':'NEG','right':'POS'}]})
        m=EvidenceMeter()
        divided=split(state,1,Q(1,2),m)
        self.assertEqual(m.full_leaf_checks,0)
        self.assertEqual([c.sign for c in divided.certs],['POS','NEG','NEG','POS'])
        backwards=affine(divided,Q(2),Q(-1),EvidenceMeter())
        self.assertEqual(events(backwards),{'identity_intervals':[], 'isolated_points':[
            {'time':'4/3','kind':'CROSS','left':'POS','right':'NEG'},
            {'time':'5/3','kind':'CROSS','left':'NEG','right':'POS'}]})
        for k in range(121):
            t=Q(k,120)
            p=next(p for p in state.pieces if p.left<=t<=p.right)
            q=next(p for p in divided.pieces if p.left<=t<=p.right)
            r=next(p for p in backwards.pieces if p.left<=2-t<=p.right)
            expected=circle_residual(t)
            self.assertEqual(p.at(t),expected)
            self.assertEqual(q.at(t),expected)
            self.assertEqual(r.at(2-t),expected)

    def test_local_edit_changes_contact_class_and_rejects_stale_source(self):
        original,state=fixture()
        center=state.pieces[1]
        m=EvidenceMeter()
        altered=replace(state,1,tuple(-c for c in center.coeff),m)
        self.assertEqual((m.full_leaf_checks,m.seam_checks),(1,2))
        self.assertEqual(altered.certs[0],state.certs[0])
        self.assertEqual(altered.certs[2],state.certs[2])
        self.assertNotEqual(altered.hash,state.hash)
        self.assertEqual(events(altered),{'identity_intervals':[], 'isolated_points':[
            {'time':'1/3','kind':'TOUCH','left':'POS','right':'POS'},
            {'time':'2/3','kind':'TOUCH','left':'POS','right':'POS'}]})
        swapped=[dict(p) for p in original['pieces']]
        swapped[1]=altered.pieces[1].source()
        with self.assertRaises(Refusal):
            verify_base(swapped, original['receipts'], EvidenceMeter())
        forged=[dict(c) for c in original['receipts']]
        forged[1]['source_hash']='0'*64
        with self.assertRaises(Refusal):
            verify_base(original['pieces'],forged,EvidenceMeter())
        # Changing only the physical shape but reissuing valid polynomial
        # receipts would NOT prove source ancestry: outside B1's source grammar.

if __name__=='__main__':
    unittest.main()
