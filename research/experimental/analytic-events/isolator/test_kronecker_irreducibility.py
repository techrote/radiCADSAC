"""stdlib adversarial checker for exact Kronecker and source-pinned germ."""
import copy
import unittest
from fractions import Fraction as Q
from kronecker_irreducibility import (Refusal, certify, verify, irreducible_by_kronecker, evaluate,
                                      MAX_TUPLES)

def doc(h0=(0,), c1=(0,), s1=(0,), c2=(0,), s2=(0,), *, a="0/1", b="1/1"):
    return {"a": a, "b": b, **{k: [f"{Q(v).numerator}/{Q(v).denominator}" for v in p]
       for k, p in zip(("H0", "C1", "S1", "C2", "S2"),
                       (h0, c1, s1, c2, s2))}}

def mul(a, b):
    result = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i+j] += x*y
    return result

class Research(unittest.TestCase):
    m = (1, 0, -10, 0, 1)  # sqrt(2)+sqrt(3), no prime-mod-p irreducibility witness

    def test_original_a3_quartic_crossing_and_touch(self):
        for source, order, parity in ((doc(self.m, c1=(1,)), 0, None),
                                      (doc(self.m), 1, True),
                                      (doc(mul(self.m,self.m), s2=mul(self.m,self.m)), 2, False)):
            receipt = certify(source, self.m, ("3/1", "4/1"))
            self.assertTrue(verify(source, receipt))
            self.assertEqual(receipt["multiplicity"], order or None)
            self.assertEqual(receipt["crossing_parity"], parity)
            self.assertEqual(receipt["sign"], "UNDETERMINED")

    def test_translated_infinite_family_controls(self):
        for k in range(-4,5):
            # m(t-k): (t-k)^4-10(t-k)^2+1
            # exact integer polynomial coefficients
            m = (k**4 - 10*k*k + 1, -4*k**3 + 20*k,
                 6*k*k - 10, -4*k, 1)
            r = certify(doc(m), m, (f"{k+3}/1", f"{k+4}/1"))
            self.assertEqual(r["multiplicity"], 1)
            self.assertTrue(verify(doc(m), r))

    def test_rescaled_algebraic_roots(self):
        for scale in (2, 10, 100):
            m = (1, 0, -10*scale*scale, 0, scale**4)
            lo, hi = Q(3,scale), Q(4,scale)
            r = certify(doc(m), m, (f"{lo.numerator}/{lo.denominator}",
                                    f"{hi.numerator}/{hi.denominator}"))
            self.assertEqual(r["multiplicity"], 1)

    def test_close_bracket_exact_sturm(self):
        m=self.m
        a,b=Q(3),Q(4)
        # Exact sign-directed bisection of the single root; not a root-exhaustion proof.
        for _ in range(45):
            mid=(a+b)/2
            if evaluate(m, mid) < 0:
                a=mid
            else:
                b=mid
        s=doc(m)
        r=certify(s,m,(f"{a.numerator}/{a.denominator}",f"{b.numerator}/{b.denominator}"))
        self.assertTrue(verify(s,r))
        self.assertLess(b-a,Q(1,10**12))

    def test_reducible_quartic_refuses_not_certifies(self):
        for polynomial in ((6,0,-5,0,1), (4,0,-4,0,1), (1,0,2,0,1)):
            with self.assertRaisesRegex(Refusal,"RATIONAL_FACTOR"):
                irreducible_by_kronecker(polynomial)

    def test_nonzero_and_identity_zero(self):
        r=certify(doc(c1=(1,)),self.m,("3/1","4/1"))
        self.assertEqual(r["result"], "EXACT_NONZERO")
        self.assertEqual(r["multiplicity"], None)
        r=certify(doc(),self.m,("3/1","4/1"))
        self.assertEqual(r["result"], "IDENTICAL_ZERO_PIECE")

    def test_tamper_source_phase_receipt(self):
        original=doc(self.m)
        r=certify(original,self.m,("3/1","4/1"))
        s=copy.deepcopy(original);s["b"]="-1/1"
        self.assertFalse(verify(s,r))
        for key,new in (("multiplicity",2),("root_count",2),
                        ("irreducibility_procedure","PRIME"),
                        ("factor_search_counts",{}),
                        ("minimal_polynomial",[1,0,-5,0,1])):
            forged=copy.deepcopy(r);forged[key]=new
            self.assertFalse(verify(original,forged))

    def test_typed_input_refusals(self):
        for polynomial in ((1,0,-10,0,0), (2,0,2), (1,)*12):
            with self.assertRaises(Refusal):
                irreducible_by_kronecker(polynomial)
        with self.assertRaisesRegex(Refusal,"NOT_ONE_REAL_ROOT"):
            certify(doc(self.m),self.m,("0/1","4/1"))
        bad=doc(self.m);bad["C1"]=iter(["0/1"])
        with self.assertRaisesRegex(Refusal,"POLYNOMIAL_SHAPE"):
            certify(bad,self.m,("3/1","4/1"))

    def test_existing_modular_family_still_admitted_independently(self):
        m=(-1,-1,0,1)
        r=certify(doc(m, s2=m),m,("1/1","2/1"))
        self.assertTrue(verify(doc(m,s2=m),r))
        self.assertEqual(r["multiplicity"],1)

if __name__ == "__main__": unittest.main(verbosity=2)
