"""Research-only independent cubic B-spline-shaped C0 source contract.

The control/knot shape is the documented A2 example. The evaluator below is
separate exact Bernstein/Bezier arithmetic. This does NOT execute A2's source
adapter or establish original MC-038 physical source ancestry.
"""
import unittest
from fractions import Fraction as Q
from math import comb
from certificate_algebra import (EvidenceMeter, Piece, Refusal, affine,
                                 base_record, events, replace, split, verify_base)


def cubic_bezier(control, u):
    return sum(comb(3, i) * control[i] * u**i * (1-u)**(3-i)
               for i in range(4))


class CubicC0PhysicalShape(unittest.TestCase):
    def setUp(self):
        # Degree-3, knots [0]*4 + [1]*3 + [2]*4, 7 actual rational controls.
        self.controls = (Q(1), Q(1, 3), Q(0), Q(0), Q(0), Q(0), Q(-1))
        self.left = Piece(Q(0), Q(1), (Q(1), Q(-2), Q(1)))
        self.right = Piece(Q(1), Q(2), (Q(0), Q(0), Q(0), Q(-1)))
        self.source = base_record((self.left, self.right))
        self.verified = verify_base(self.source["pieces"],
                                    self.source["receipts"], EvidenceMeter())

    def test_real_consumer_matches_independent_bezier_controls_and_reversal(self):
        self.assertEqual(events(self.verified), {"identity_intervals": [],
            "isolated_points": [{"time": "1", "kind": "CROSS",
                                 "left": "POS", "right": "NEG"}]})
        reversed_state = affine(self.verified, Q(2), Q(-1), EvidenceMeter())
        self.assertEqual(events(reversed_state), {"identity_intervals": [],
            "isolated_points": [{"time": "1", "kind": "CROSS",
                                 "left": "NEG", "right": "POS"}]})
        divided = split(self.verified, 0, Q(1, 2), EvidenceMeter())
        for n in range(33):
            t = Q(n, 16)
            p = self.left if t <= 1 else self.right
            u = t if t <= 1 else t-1
            expected = cubic_bezier(self.controls[:4] if t <= 1
                                     else self.controls[3:], u)
            with self.subTest(control="source", n=n):
                self.assertEqual(p.at(t), expected)
            x = 2-t
            px = reversed_state.pieces[0] if x <= 1 else reversed_state.pieces[1]
            with self.subTest(control="reversal", n=n):
                self.assertEqual(px.at(x), expected)
            if t <= 1:
                q = divided.pieces[0] if t <= Q(1, 2) else divided.pieces[1]
                with self.subTest(control="split", n=n):
                    self.assertEqual(q.at(t), expected)

    def test_real_consumer_refuses_source_swaps_and_seam_invalidation(self):
        changed = replace(self.verified, 0, (Q(4), Q(-8), Q(4)), EvidenceMeter())
        self.assertEqual(changed.pieces[1], self.verified.pieces[1])
        self.assertEqual(changed.certs[1], self.verified.certs[1])
        self.assertNotEqual(changed.hash, self.verified.hash)
        with self.assertRaises(Refusal):
            replace(self.verified, 0, (Q(1),), EvidenceMeter())
        with self.assertRaises(Refusal):
            verify_base(self.source["pieces"], list(reversed(self.source["receipts"])), EvidenceMeter())
        forged = [dict(self.source["receipts"][0], source_hash="0" * 64),
                  self.source["receipts"][1]]
        with self.assertRaises(Refusal):
            verify_base(self.source["pieces"], forged, EvidenceMeter())


if __name__ == "__main__":
    unittest.main()
