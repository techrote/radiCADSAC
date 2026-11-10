"""Adversarial exact tests; run: python3 -m unittest -v test_algebraic_degree.py"""
import copy
import unittest
from algebraic_degree import *

def doc(h0=None, c1=None, s1=None, c2=None, s2=None, *, a="0/1", b="1/1"):
    cs = [h0,c1,s1,c2,s2]
    return {"a":a,"b":b,**{k:[f"{Q(v).numerator}/{Q(v).denominator}" for v in (p if p is not None else [0])] for k,p in zip(CHANNELS,cs)}}

def multiply(a,b):
    z=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):z[i+j]+=x*y
    return z

class Research(unittest.TestCase):
    def test_irreducible_cubic_and_finite_valuation(self):
        m=(-1,-1,0,1)  # x^3 - x - 1; irreducible modulo 2
        src=doc(multiply(m,m), c1=m, s2=multiply(m,m), b="-2/1")
        cert=certify(src,m,2,("1/1","2/1"))
        self.assertTrue(verify(src,cert));self.assertEqual(cert["multiplicity"],1)
        self.assertTrue(cert["crossing_parity"])
        self.assertEqual(cert["result"],"EXACT_ZERO")
        self.assertEqual(cert["sign"],"UNDETERMINED")
    def test_even_quartic_touch_and_two_real_brackets(self):
        m=(-1,-1,0,0,1)  # x^4-x-1; irreducible mod 2
        src=doc(multiply(m,m), s2=multiply(m,m))
        for ends in (("-1/1","0/1"),("1/1","2/1")):
            result=certify(src,m,2,ends)
            self.assertTrue(verify(src,result))
            self.assertEqual(result["multiplicity"],2)
            self.assertFalse(result["crossing_parity"])
    def test_two_sided_distinct_irrational_quadratic(self):
        m=(-2,0,1)
        s=doc(multiply(m,multiply(m,m)), c2=multiply(m,multiply(m,m)))
        for bracket in (("-2/1","-1/1"),("1/1","2/1")):
            r=certify(s,m,3,bracket)
            self.assertTrue(verify(s,r))
            self.assertEqual(r["multiplicity"],3)
    def test_algebraic_nonzero_despite_fourier_channels(self):
        m=(-1,-1,0,1)
        s=doc([1],c1=m,s2=[3])
        r=certify(s,m,2,("1/1","2/1"))
        self.assertEqual(r["result"],"EXACT_NONZERO")
        self.assertIsNone(r["multiplicity"])
    def test_identity_continuum_not_single_root(self):
        m=(-1,-1,0,1)
        r=certify(doc(),m,2,("1/1","2/1"))
        self.assertEqual(r["result"],"IDENTICAL_ZERO_PIECE")
        self.assertIsNone(r["crossing_parity"])
    def test_reducible_and_unsupported_polynomials_refuse(self):
        with self.assertRaises(Refusal):certify(doc([1]),(-1,0,1),2,("0/1","2/1"))
        with self.assertRaises(Refusal):certify(doc([1]),(-1,0,1),3,("0/1","2/1"))
        with self.assertRaises(Refusal):certify(doc([1]),tuple([1]+[0]*8+[1]),2,("0/1","2/1"))
    def test_root_count_refusals(self):
        m=(-1,-1,0,0,1)
        with self.assertRaisesRegex(Refusal,"NOT_ONE_REAL_ROOT"):
            certify(doc([1]),m,2,("-2/1","2/1"))
        with self.assertRaisesRegex(Refusal,"NOT_ONE_REAL_ROOT"):
            certify(doc([1]),m,2,("2/1","3/1"))
    def test_phase_and_source_binding(self):
        m=(-1,-1,0,1);s=doc(m,c2=[2])
        r=certify(s,m,2,("1/1","2/1"))
        self.assertTrue(verify(s,r))
        altered=copy.deepcopy(s);altered["b"]="-1/1"
        self.assertFalse(verify(altered,r))
        forged=copy.deepcopy(r);forged["multiplicity"]=3
        self.assertFalse(verify(s,forged))
        forged=copy.deepcopy(r);forged["root_count"]=2
        self.assertFalse(verify(s,forged))
    def test_zero_rate_and_noncanonical_refuse(self):
        m=(-1,-1,0,1)
        with self.assertRaisesRegex(Refusal,"ZERO_RATE"):
            certify(doc(m,b="0/1"),m,2,("1/1","2/1"))
        bad=doc(m);bad["C1"]=["0"]
        with self.assertRaisesRegex(Refusal,"NONCANONICAL"):
            certify(bad,m,2,("1/1","2/1"))
    def test_bounded_container_rejection(self):
        m=(-1,-1,0,1)
        bad=doc([1]);bad["S2"]=["0/1"]*100000
        with self.assertRaisesRegex(Refusal,"POLYNOMIAL_SHAPE"):
            certify(bad,m,2,("1/1","2/1"))
        bad=doc([1]);bad["S2"]=iter(["0/1"])
        with self.assertRaisesRegex(Refusal,"POLYNOMIAL_SHAPE"):
            certify(bad,m,2,("1/1","2/1"))
    def test_infinite_family_of_rational_amplitudes_sample(self):
        m=(-1,-1,0,1)
        for k in range(-15,16):
            # m^2*(t+k) is order 2 when k is rational: alpha is irrational.
            src=doc(multiply(multiply(m,m),[k,1]))
            r=certify(src,m,2,("1/1","2/1"))
            self.assertEqual(r["multiplicity"],2)
            self.assertTrue(verify(src,r))

if __name__ == "__main__":unittest.main(verbosity=2)
