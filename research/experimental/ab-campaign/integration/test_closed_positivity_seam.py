"""B5 independent exact-rational interop falsifier; no author-module imports.

Pins: radiCADSAC B1 #473 4ecf9087 (kind POS permits zero Bernstein
endpoints); A1 #470 42da787b (square-lift demands every coefficient > 0).
This checks only the algebraic seam witness, not a complete A1 root oracle.
"""
from fractions import Fraction as Q
from math import comb
import unittest


def bernstein(coeff):
    n = len(coeff) - 1
    return tuple(sum((coeff[k] * Q(comb(i, k), comb(n, k))
                      for k in range(i + 1)), Q(0)) for i in range(n + 1))


def b1_open_positive(b):
    return any(x > 0 for x in b) and all(x >= 0 for x in b)


def a1_closed_positivity_sufficient(b):
    return all(x > 0 for x in b)


class ClosedPositivitySeam(unittest.TestCase):
    def test_zero_seam_from_two_valid_b1_pos_leaves(self):
        # Physical u in [0,1]: P_L(u)=1/2-u, P_R(u)=u-1/2.
        # Local Bernstein coordinates v in [0,1] on each half-cell.
        left = bernstein((Q(1, 2), -Q(1, 2)))
        right = bernstein((Q(0), Q(1, 2)))
        self.assertEqual(left, (Q(1, 2), Q(0)))
        self.assertEqual(right, (Q(0), Q(1, 2)))
        self.assertTrue(b1_open_positive(left))
        self.assertTrue(b1_open_positive(right))
        self.assertFalse(a1_closed_positivity_sufficient(left))
        self.assertFalse(a1_closed_positivity_sufficient(right))
        # P_L(1/2)=P_R(1/2)=0; G(k+1/2)=(-1)^k exactly.
        # So the product has an extra ZERO at a genuine C0 knot.
        for k in range(3, 33):
            g_at_knot = (-1) ** k
            self.assertNotEqual(g_at_knot, 0)
            self.assertEqual(Q(0) * g_at_knot * g_at_knot, 0)
        # Sided one-sided derivatives P'_L=-1, P'_R=+1,
        # hence F'_R-F'_L=2 G(knot)^2=2, with a TOUCH zero.
        self.assertEqual(Q(1) - Q(-1), Q(2))

    def test_closed_positive_multiplier_has_no_new_knot_zero(self):
        # Strictly positive constant P=1 satisfies both disciplines.
        b = bernstein((Q(1),))
        self.assertTrue(b1_open_positive(b))
        self.assertTrue(a1_closed_positivity_sufficient(b))
        for k in range(3, 33):
            g_at_knot = (-1) ** k
            self.assertEqual(Q(1) * g_at_knot * g_at_knot, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
