"""Direct, actual B1 parent-ingress falsifiers: hostile Fraction subclasses.

Run: python3 -m unittest -v test_transform_scalar_integrity.py
Evidence class: Python deterministic model, not native/STEP or adversarial-process isolation.
"""
from fractions import Fraction as Q
import unittest

from certificate_algebra import (
    Piece, Refusal, EvidenceMeter, affine, base_record, bernstein,
    prove, replace, split, verify_base,
)


class HostileOffset(Q):
    """Presents zero, but moves an affine interval one unit via __rsub__."""
    def __rsub__(self, other):
        return Q(other) - Q(self) + 1


class HostileCut(Q):
    """Presents 1/2, but injects 1/8 into a split coordinate calculation."""
    def __sub__(self, other):
        if isinstance(other, Q):
            return Q(self) - Q(other) + Q(1, 8)
        return super().__sub__(other)


class HostileCoefficient(Q):
    """Presents -2; lies when computing a Bernstein multiplication."""
    def __mul__(self, other):
        return abs(Q(self)) * other


def admitted():
    p = Piece(Q(0), Q(1), (Q(1), Q(1)))
    b = base_record((p,))
    return verify_base(b["pieces"], b["receipts"], EvidenceMeter()), p


class TransformScalarIntegrityTests(unittest.TestCase):
    def test_affine_rejects_fraction_subclass_that_corrupts_domain(self):
        s, p = admitted()
        with self.assertRaises(Refusal):
            affine(s, HostileOffset(0), Q(1), EvidenceMeter())
        correct = affine(s, Q(0), Q(1), EvidenceMeter())
        self.assertEqual(correct.pieces[0], p)

    def test_split_rejects_fraction_subclass_that_breaks_restriction(self):
        s, p = admitted()
        with self.assertRaises(Refusal):
            split(s, 0, HostileCut(1, 2), EvidenceMeter())
        correct = split(s, 0, Q(1, 2), EvidenceMeter())
        for piece in correct.pieces:
            mid = (piece.left + piece.right) / 2
            self.assertEqual(piece.at(mid), p.at(mid))

    def test_direct_piece_rejects_malicious_coefficient_arithmetic(self):
        with self.assertRaises(Refusal):
            Piece(Q(0), Q(1), (Q(1), HostileCoefficient(-2)))
        with self.assertRaises(Refusal):
            Piece(HostileOffset(0), Q(1), (Q(1),))
        with self.assertRaises(Refusal):
            Piece(Q(0), Q(1), (HostileCoefficient(1),))

    def test_replace_refuses_hostile_index_and_coefficients(self):
        s, p = admitted()
        with self.assertRaises(Refusal):
            replace(s, True, (Q(1),), EvidenceMeter())
        with self.assertRaises(Refusal):
            replace(s, 0, (Q(1), HostileCoefficient(-2)), EvidenceMeter())
        unchanged = replace(s, 0, (Q(1), Q(1)), EvidenceMeter())
        self.assertEqual(unchanged.pieces[0], p)


if __name__ == "__main__":
    unittest.main()
