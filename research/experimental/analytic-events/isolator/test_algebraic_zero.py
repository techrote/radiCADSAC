"""Independent deterministic A1 regression controls; python3 -m unittest."""
from fractions import Fraction as Q
import unittest

from algebraic_zero import (Refusal, Source, source, rational_event, quadratic_event,
                            constant_phase_identity, verify_rational_event,
                            verify_quadratic_event)


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
        self.assertEqual(rational_event(high, Q(4,9))["result"], "IDENTICAL_ZERO_PIECE")

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


    def test_a3_zero_rate_continuum_vs_isolated_point(self):
        # A3 PRR_kwDOUd7FHc8AAAABW61vCw: point zero is not a continuum.
        cosine = source([-1], cos=([1],), sin=([],), phase_rate=0)
        sine = source([-1], cos=([],), sin=([1],),
                      phase_offset=Q(1, 2), phase_rate=0)
        for src in (cosine, sine):
            self.assertTrue(constant_phase_identity(src))
            for at in (Q(-7, 2), Q(1, 3), Q(5)):
                receipt = rational_event(src, at)
                self.assertEqual(receipt["result"], "IDENTICAL_ZERO_PIECE")
                self.assertTrue(verify_rational_event(src, receipt))
        isolated = source([-1, 1], phase_rate=0)
        self.assertFalse(constant_phase_identity(isolated))
        self.assertEqual(rational_event(isolated, 1)["result"], "EXACT_ZERO")
        self.assertEqual(rational_event(isolated, 2)["result"], "EXACT_NONZERO")
        cancellation = source([0, 1], cos=([0, -1],), sin=([],),
                              phase_rate=0)
        self.assertTrue(constant_phase_identity(cancellation))
        self.assertRaises(Refusal, constant_phase_identity, source([1]))
        self.assertRaises(Refusal, rational_event,
                          source([1], phase_offset=Q(1, 33), phase_rate=0), 1)

    def test_a3_infinite_family_rational_polynomial_amplitudes(self):
        # The cancellation holds for arbitrary rational polynomials, not specimens.
        for degree in range(17):
            coeff = [Q(0)] * degree + [Q(1, 3)]
            src = source(coeff, cos=([-v for v in coeff],),
                         sin=([],), phase_rate=0)
            self.assertTrue(constant_phase_identity(src))
            self.assertEqual(rational_event(src, Q(7, 8))["result"],
                             "IDENTICAL_ZERO_PIECE")
            neg = source(coeff, cos=(coeff,), sin=([],), phase_rate=0)
            self.assertFalse(constant_phase_identity(neg))

    def test_a3_direct_source_validation_and_mutation(self):
        invalid = [
            dict(c0=(), cos=((Q(1),),), sin=(),
                 phase_offset=Q(0), phase_rate=Q(1)),
            dict(c0=(0.25,), cos=(), sin=(),
                 phase_offset=Q(0), phase_rate=Q(1)),
            dict(c0=(Q(1), Q(0)), cos=(), sin=(),
                 phase_offset=Q(0), phase_rate=Q(1)),
            dict(c0=(Q(1),) * 18, cos=(), sin=(),
                 phase_offset=Q(0), phase_rate=Q(1)),
            dict(c0=(Q(2 ** 300),), cos=(), sin=(),
                 phase_offset=Q(0), phase_rate=Q(1)),
            dict(c0=(Q(1),), cos=(), sin=(),
                 phase_offset=0.0, phase_rate=Q(1)),
        ]
        for fields in invalid:
            with self.subTest(fields=fields), self.assertRaises(Refusal):
                Source(**fields)
        src = source([1], cos=([1],), sin=([],))
        r = rational_event(src, 0)
        q = quadratic_event(src, 1, 0, -2)
        object.__setattr__(src, "sin", ())  # hostile frozen-dataclass bypass
        self.assertRaises(Refusal, rational_event, src, 0)
        self.assertRaises(Refusal, quadratic_event, src, 1, 0, -2)
        self.assertFalse(verify_rational_event(src, r))
        self.assertFalse(verify_quadratic_event(src, q))


if __name__ == "__main__":
    unittest.main()

class BoundedSourceIngressTests(unittest.TestCase):
    """A3 resource falsifier: the real source() must not traverse huge inputs."""

    def test_preflight_17_coefficients_and_hash_unchanged(self):
        from algebraic_zero import source_sha
        s = source([0] * 16 + [1], cos=([2],), sin=([],))
        self.assertEqual(len(s.c0), 17)
        self.assertEqual(source_sha(s), source_sha(source(tuple([0] * 16 + [1]),
                                                  cos=((2,),), sin=((),))))
        self.assertEqual(source_sha(source([1], cos=([2],), sin=([],))),
                         source_sha(source((1,), cos=((2,),), sin=((),))))

    def test_huge_top_level_and_nested_preflight(self):
        huge = [0] * 100000
        for kwargs in ({'c0': huge},
                       {'c0': [0], 'cos': [huge], 'sin': [[]]},
                       {'c0': [0], 'cos': [[]], 'sin': [huge]}):
            with self.subTest(kind=tuple(kwargs)):
                with self.assertRaises(Refusal):
                    source(**kwargs)
        for kwargs in ({'c0': [0] * 18},
                       {'c0': [0], 'cos': [[0] * 18], 'sin': [[]]},
                       {'c0': [0], 'cos': [[]], 'sin': [[0] * 18]}):
            with self.subTest(kind=tuple(kwargs)):
                with self.assertRaisesRegex(Refusal, 'degree exceeds 16'):
                    source(**kwargs)

    def test_bomb_iterators_are_never_consumed(self):
        class Bomb:
            def __init__(self):
                self.pulls = 0
            def __iter__(self):
                self.pulls += 1
                raise AssertionError('unbounded iterator consumed')
            def __len__(self):
                raise AssertionError('custom length consulted')
        for which in ('c0', 'cos', 'sin', 'cos_inner', 'sin_inner'):
            item = Bomb()
            args = {'c0': [0], 'cos': ([1],), 'sin': ([],)}
            if which in ('c0', 'cos', 'sin'):
                args[which] = item
            elif which == 'cos_inner':
                args['cos'] = (item,)
            else:
                args['sin'] = (item,)
            with self.subTest(which=which):
                with self.assertRaises(Refusal):
                    source(**args)
                self.assertEqual(item.pulls, 0)

    def test_bounded_index_and_noncanonical_subclasses(self):
        class DynamicList(list):
            def __iter__(self):
                raise AssertionError('untrusted iterator used')
        for value in (DynamicList([1]), tuple(range(18))):
            with self.assertRaises(Refusal):
                source(value)
        # Both H1 and H2 remain accepted as exact primitive list/tuple shapes.
        src = source([1], cos=([2], [3]), sin=([4], [5]))
        self.assertEqual(len(src.channels()), 5)
