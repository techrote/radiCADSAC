"""Independent deterministic A1 regression controls; python3 -m unittest."""
from fractions import Fraction as Q
import unittest

from algebraic_zero import (Refusal, source, rational_event, quadratic_event,
                            verify_rational_event, verify_quadratic_event)


class ExactPointTests(unittest.TestCase):
    def test_rational_cos_half_turn(self):
        s = source([], cos=([1],), sin=([],))
        self.assertEqual(rational_event(s, Q(1,2))["result"], "EXACT_ZERO")
        self.assertEqual(rational_event(s, 1)["result"], "EXACT_NONZERO")

    def test_sine_exception_and_h2(self):
        s = source([1], cos=([],), sin=([-1],))
        self.assertEqual(rational_event(s, Q(1,2))["result"], "EXACT_ZERO")
        self.assertEqual(rational_event(s, Q(1,3))["result"], "EXACT_NONZERO")
        h2 = source([1], cos=([], [1]), sin=([], []))
        self.assertEqual(rational_event(h2, Q(1,2))["result"], "EXACT_ZERO")

    def test_other_cyclotomic_and_phase(self):
        s = source([-1], cos=([2],), sin=([],))
        self.assertEqual(rational_event(s, Q(1,3))["result"], "EXACT_ZERO")
        reversed_phase = source([-1], cos=([2],), sin=([],), phase_rate=-1)
        self.assertEqual(rational_event(reversed_phase, Q(1,3))["result"], "EXACT_ZERO")
        high = source([-1], cos=([2],), sin=([],), phase_rate=0, phase_offset=Q(1,3))
        self.assertEqual(rational_event(high, Q(4,9))["result"], "EXACT_ZERO")

    def test_close_rational_arguments_stay_separate(self):
        s = source([1], cos=([-1],), sin=([],))
        self.assertEqual(rational_event(s, 0)["result"], "EXACT_ZERO")
        with self.assertRaises(Refusal):
            rational_event(s, Q(1,2**10))  # bounded denominator, not NONZERO
        self.assertEqual(rational_event(s, Q(1,16))["result"], "EXACT_NONZERO")

    def test_identically_zero_rational_piece(self):
        z=source([0],cos=([],),sin=([],))
        self.assertEqual(rational_event(z,Q(1,7))["result"], "IDENTICAL_ZERO_PIECE")

    def test_irrat_absence_and_first_order(self):
        cos = source([], cos=([1],), sin=([],))
        self.assertEqual(quadratic_event(cos, 1, 0, -2)["result_at_both_roots"], "EXACT_NONZERO")
        poly = source([-2,0,1], cos=([-2,0,1],), sin=([],))
        r=quadratic_event(poly, 1, 0, -2)
        self.assertEqual((r["result_at_both_roots"], r["multiplicity_at_both"], r["crosses_at_each"]),
                         ("EXACT_ZERO", 1, True))
        self.assertEqual(r["root_intervals"], [["-3/2", "-1"], ["1", "3/2"]])

    def test_cubic_tangency_and_continuum(self):
        # (t^2-2)^3 = t^6-6*t^4+12*t^2-8
        cube = [-8, 0, 12, 0, -6, 0, 1]
        f = source(cube, cos=([],), sin=(cube,))
        r = quadratic_event(f, 1, 0, -2)
        self.assertEqual((r["multiplicity_at_both"], r["crosses_at_each"]), (3, True))
        square=[4,0,-4,0,1]
        f2=source(square, cos=(square,), sin=([],))
        r2=quadratic_event(f2, 1, 0, -2)
        self.assertEqual((r2["multiplicity_at_both"],r2["crosses_at_each"]), (2,False))
        self.assertEqual(quadratic_event(source([0]),1,0,-2)["result_at_both_roots"],
                         "IDENTICAL_ZERO_PIECE")

    def test_new_quadratic_and_negative_phase(self):
        poly=[-3,0,1]  # alpha=+-sqrt(3)
        f = source(poly, cos=([], poly), sin=([], []), phase_offset=Q(1,5), phase_rate=-Q(2,7))
        self.assertEqual(quadratic_event(f,1,0,-3)["multiplicity_at_both"],1)
        self.assertEqual(quadratic_event(f,1,0,-2)["result_at_both_roots"],"EXACT_NONZERO")

    def test_refusal_zero_rate_and_bad_inputs(self):
        self.assertRaises(Refusal, quadratic_event, source([1],phase_rate=0),1,0,-2)
        self.assertRaises(Refusal, quadratic_event, source([1]),1,0,-1)
        self.assertRaises(Refusal, quadratic_event, source([1]),1,0,2)
        self.assertRaises(Refusal, source, [0.1])
        self.assertRaises(Refusal, source, [1], ([1],), ([],[]))

    def test_receipt_tampering_and_source_binding(self):
        s=source([1], cos=([-1],),sin=([],))
        r=rational_event(s, 0)
        self.assertTrue(verify_rational_event(s,r))
        self.assertFalse(verify_rational_event(source([2],cos=([-1],),sin=([],)),r))
        self.assertFalse(verify_rational_event(s,{**r,"result":"EXACT_NONZERO"}))
        self.assertFalse(verify_rational_event(s,{**r,"remainder":["0"]}))
        q=quadratic_event(s,1,0,-2)
        self.assertTrue(verify_quadratic_event(s,q))
        self.assertFalse(verify_quadratic_event(s,{**q,"multiplicity_at_both":100}))
        self.assertFalse(verify_quadratic_event(source([2],cos=([-1],),sin=([],)),q))


if __name__ == "__main__":
    unittest.main()
