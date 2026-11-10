#!/usr/bin/env python3
"""Independent exact adversarial tests for A2-SPARSE-001."""
import unittest
from fractions import Fraction as F
from sparse_phase_germ import analyze, attempt, verify, Refusal, moment, formal_difference

def src(rate, *, off=0, cos=(1,), sin=(0,), constant=None):
    terms = {1: (cos, sin)}
    if constant is not None:
        terms[0] = (constant, (0,))
    return {'interval': (F(-1), F(1)), 'phase': (F(off), F(rate)), 'terms': terms}

class TestSparse(unittest.TestCase):
    def test_independent_rate_family(self):
        count = 0
        for n in (3, 7, 31, 32, 101, 997, 4096):
            for p in range(4):
                amp = tuple([F(0)]*p+[F(1)])
                a = src(F(1,n), cos=amp)
                b = src(F(1,n+1), cos=amp)
                result = analyze(a, b, F(0))
                self.assertEqual(result['first_mismatch_order'], p+2)
                self.assertEqual(result['right_sign'], 1)
                self.assertEqual(result['left_sign'], (-1)**p)
                self.assertTrue(verify(a,b,0,result))
                count += 1
        self.assertEqual(count, 28)

    def test_a3_31_32_numerical_free(self):
        a, b = src(F(1,31)), src(F(1,32))
        result = analyze(a,b,0)
        self.assertEqual(result['first_mismatch_order'], 2)
        self.assertEqual(result['moment_terms'], [[2, str(F(63,492032))]])
        self.assertEqual((result['left_sign'],result['right_sign']), (1,1))
        self.assertEqual(result['source_kind'], 'EXPRESSION_ONLY_NOT_PHYSICAL_KNOT')

    def test_phase_alias_negative_rate_and_identity(self):
        a = src(F(1,4), cos=(0,), sin=(1,))
        b = src(F(-1,4), off=F(1,4), cos=(1,))
        self.assertEqual(analyze(a,b,0)['status'], 'ANALYTICALLY_IDENTICAL')
        c = src(F(-1,31), cos=(0,), sin=(-1,))
        d = src(F(1,31), cos=(0,), sin=(1,))
        self.assertEqual(analyze(c,d,0)['status'], 'ANALYTICALLY_IDENTICAL')

    def test_mixed_pi_polynomial_signs(self):
        # Difference s^2 - (1-cos(2*pi*s/q)) has leading 1-2*pi^2/q^2.
        for q, expected in ((2,-1),(7,1)):
            a = src(F(1,q), cos=(-1,), constant=(1,))
            b = src(F(1,q), cos=(0,), constant=(0,0,1))
            got = analyze(a,b,0)
            self.assertEqual(got['first_mismatch_order'],2)
            self.assertEqual(got['right_sign'],expected)
            self.assertEqual(len(got['moment_terms']),2)

    def test_distinct_source_and_receipt_forgery(self):
        a, b = src(F(1,31)),src(F(1,32))
        r = analyze(a,b,0)
        self.assertNotEqual(r['left_sha256'],r['right_sha256'])
        for key,value in (('right_sign',-1),('first_mismatch_order',4),('source_kind','TRUE_BSPLINE')):
            forged = dict(r);forged[key]=value
            with self.assertRaises(Refusal):verify(a,b,0,forged)
        with self.assertRaises(Refusal):verify(a,src(F(1,33)),0,r)

    def test_hostile_python_receipt_equality(self):
        # Negative control from published pre-fix head: dict equality accepted this.
        class EqualAlways:
            def __eq__(self, other):
                return True
        a, b = src(F(1,31)), src(F(1,32))
        r = analyze(a,b,0)
        for key, spoof in (('right_sign', EqualAlways()),
                           ('right_sign', True),
                           ('first_mismatch_order', EqualAlways())):
            forged = dict(r); forged[key] = spoof
            with self.assertRaises(Refusal):
                verify(a,b,0,forged)
        forged = dict(r)
        forged['moment_terms'] = [[2, EqualAlways()]]
        with self.assertRaises(Refusal):
            verify(a,b,0,forged)
        forged['moment_terms'] = [[2, '63/492032']] * 100_000
        with self.assertRaises(Refusal):
            verify(a,b,0,forged)
        self.assertTrue(verify(a,b,0,r))

    def test_quarter_budget_and_bad_shapes(self):
        a=src(F(1,31));b=src(F(1,32))
        for bad in (src(F(1,31),off=F(1,8)),
                    {'interval': (-1,1),'phase':(0,0),'terms':{1:((1,),(0,))}},
                    src(F(1,31),cos=tuple([1]*100000)),
                    {'interval': (-1,1),'phase':(0,F(1,31)),
                     'terms':{1:((1,),tuple([0]*100000))}},
                    {'interval':(-1,1),'phase':(0,F(1,31)), 'terms':{3:((1,),(0,))}}):
            got=attempt(bad,b,0)
            self.assertEqual(got['status'],'RESOURCE_REFUSAL_OR_BLOCKED')
            self.assertFalse(got['is_truth_value'])
        self.assertEqual(attempt(a,b,F(2))['status'],'RESOURCE_REFUSAL_OR_BLOCKED')

    def test_exact_moment_order_ceiling(self):
        a = src(F(1,31),cos=(0,))
        b = src(F(1,32),cos=(1,))
        freqs=formal_difference(a,b,0)
        self.assertEqual(moment(freqs[0],0),1)
        self.assertEqual(analyze(a,b,0)['first_mismatch_order'],0)

if __name__ == '__main__':
    unittest.main()
