import unittest, copy
from fractions import Fraction as Q
from simple_promise import *

class Research(unittest.TestCase):
    def test_zero_free_oscillatory_nonmonotone(self):
        # F = 3 + sin(pi t) + cos(2 pi t) > 1 on [0,2].
        d=input_doc([("0/1","2/1",{"H0":["3/1"],"S1":["1/1"],"C2":["1/1"]})])
        s=source(d);p=partition(s,limit_level=4)
        self.assertTrue(verify(s,p));self.assertEqual(sum(c["kind"]=="CROSS" for c in p["cells"]),0)
    def test_two_simple_h1_roots(self):
        # F = sin(pi t) + 1/2 has 2 simple roots on [0,2].
        s=source(input_doc([("0/1","2/1",{"H0":["1/2"],"S1":["1/1"]})]))
        p=partition(s,limit_level=5)
        self.assertTrue(verify(s,p));self.assertEqual(sum(c["kind"]=="CROSS" for c in p["cells"]),2)
    def test_piece_kink_and_h2(self):
        # (t+2)+cos(2 pi t) is root-free, with a physically genuine kink at t=1
        # because H0 on right is 2t+1, both equal 3 at t=1.
        s=source(input_doc([("0/1","1/1",{"H0":["2/1","1/1"],"C2":["1/4"]}),
                            ("1/1","2/1",{"H0":["1/1","2/1"],"C2":["1/4"]})]))
        p=partition(s,limit_level=3)
        self.assertTrue(verify(s,p));self.assertEqual(len(s.pieces),2)
    def test_close_pair_polynomial_crossings(self):
        # (t-1/2)*(t-17/32), separation 1/32. No signed grid sample is
        # permitted to *assume* the pair is absent.
        # t^2 - 33/32 t + 17/64
        s=source(input_doc([("0/1","1/1",{"H0":["17/64","-33/32","1/1"]})]))
        p=partition(s,limit_level=8,max_shifts=8,precision=(4,6,8))
        self.assertTrue(verify(s,p));self.assertEqual(sum(c["kind"]=="CROSS" for c in p["cells"]),2)
    def test_near_knot_simple_crossing(self):
        # Root 31/64 lies only 1/64 before the C0 join at 1/2.
        # Value at join is 1/64, but physical derivatives differ by 2.
        s=source(input_doc([("0/1","1/2",{"H0":["-31/64","1/1"]}),
                            ("1/2","1/1",{"H0":["-95/64","3/1"]})]))
        p=partition(s,limit_level=7,precision=(4,6,8))
        self.assertTrue(verify(s,p))
        self.assertEqual(sum(c["kind"]=="CROSS" for c in p["cells"]),1)
        self.assertEqual([c["piece"] for c in p["cells"] if c["kind"]=="CROSS"],[0])

    def test_negative_affine_phase_h2(self):
        s=source(input_doc([("0/1","1/1",{"C2":["1/1"]})],b="-1/1"))
        p=partition(s,limit_level=7,precision=(4,6,8,12))
        self.assertTrue(verify(s,p))
        self.assertEqual(sum(c["kind"]=="CROSS" for c in p["cells"]),2)

    def test_close_pair_low_budget_refuses(self):
        s=source(input_doc([("0/1","1/1",{"H0":["17/64","-33/32","1/1"]})]))
        with self.assertRaisesRegex(Refusal,"UNRESOLVED_BUDGET"):
            partition(s,limit_level=2,max_shifts=2,precision=(4,))

    def test_tangent_returns_nontruth(self):
        # (t-1/2)^2: at root F'=0, same-signed endpoints cannot certify absence
        s=source(input_doc([("0/1","1/1",{"H0":["1/4","-1/1","1/1"]})]))
        with self.assertRaisesRegex(Refusal,"UNRESOLVED_BUDGET"):
            partition(s,limit_level=3,max_shifts=3,precision=(4,6))
    def test_identity_continuum_nontruth(self):
        s=source(input_doc([("0/1","1/1",{})]))
        with self.assertRaisesRegex(Refusal,"UNRESOLVED_BUDGET"):
            partition(s,limit_level=2,max_shifts=2,precision=(4,))
    def test_mutated_source_direct_forgery(self):
        s=source(input_doc([("0/1","1/1",{"H0":["4/1"]})]))
        p=partition(s)
        object.__setattr__(s, "a", Q(1,3))
        self.assertFalse(verify(s,p))
        with self.assertRaisesRegex(Refusal,"BUDGET"):
            partition(s)

    def test_tamper_and_genuine_knot_refusal(self):
        s=source(input_doc([("0/1","1/1",{"H0":["4/1"]})]))
        p=partition(s)
        p2=copy.deepcopy(p);p2["cells"][0]["sign"]=-1
        self.assertFalse(verify(s,p2))
        p3=copy.deepcopy(p);p3["source_sha256"]="0"*64
        self.assertFalse(verify(s,p3))
        with self.assertRaisesRegex(Refusal,"KNOT_DISCONTINUITY"):
            source(input_doc([("0/1","1/1",{"H0":["1/1"]}),
                              ("1/1","2/1",{"H0":["2/1"]})]))

if __name__=="__main__":unittest.main(verbosity=2)
