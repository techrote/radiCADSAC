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
        with self.assertRaisesRegex(Refusal,"SOURCE_HASH_MISMATCH"):
            partition(s)

    def test_hash_bound_source_snapshot_under_interleaving(self):
        # A frozen Source is caller mutable with object.__setattr__.
        # On the original producer/verifier, modifying pieces immediately
        # after validation caused real negative-sign EMPTY cells to be issued
        # under the original positive-function SHA, and verify accepted them.
        import sys
        import simple_promise as f8
        positive = source(input_doc([("0/1", "1/1", {"H0": ["4/1"]})]))
        negative = source(input_doc([("0/1", "1/1", {"H0": ["-4/1"]})]))
        original = positive.pieces
        calls = []

        def interleave(frame, event, arg):
            if frame.f_code is f8.valid_source.__code__:
                if event == "call":
                    object.__setattr__(positive, "pieces", original)
                elif event == "return" and arg is True:
                    calls.append("admitted")
                    object.__setattr__(positive, "pieces", negative.pieces)
            return interleave

        sys.settrace(interleave)
        try:
            certificate = partition(positive, limit_level=0, max_shifts=1,
                                    precision=(4,))
            accepted = verify(positive, certificate)
        finally:
            sys.settrace(None)
            object.__setattr__(positive, "pieces", original)
        # Fixed producer/consumer never re-read the outside Source after
        # admission. The attack hook may no longer run at all; either way,
        # no source-incoherent negative-sign receipt may be accepted.
        self.assertEqual(certificate["source_sha256"], positive.sha256)
        self.assertTrue(all(c["sign"] == 1 for c in certificate["cells"]))
        self.assertTrue(accepted)
        self.assertTrue(verify(positive, certificate))
        self.assertFalse(verify(negative, certificate))
        forged = partition(negative, limit_level=0, max_shifts=1,
                           precision=(4,))
        forged["source_sha256"] = positive.sha256
        sys.settrace(interleave)
        try:
            self.assertFalse(verify(positive, forged))
        finally:
            sys.settrace(None)
            object.__setattr__(positive, "pieces", original)

    def test_doc_ingress_hash_matches_parsed_capture(self):
        # At the exact json.dumps boundary, an external dict may change.
        # The captured polynomial and source digest must still agree.
        import sys
        doc = input_doc([("0/1", "1/1", {"H0": ["4/1"]})])
        intact = source(doc)
        mutated = False

        def interleave(frame, event, arg):
            nonlocal mutated
            # json.dumps itself is ordinarily a pure-Python entrypoint.
            if (event == "call" and not mutated and
                    frame.f_code.co_name == "dumps" and
                    frame.f_globals.get("__name__") == "json"):
                mutated = True
                doc["pieces"][0]["H0"][0] = "-4/1"
            return interleave

        sys.settrace(interleave)
        try:
            rebuilt = source(doc)
        finally:
            sys.settrace(None)
        self.assertTrue(mutated)
        self.assertEqual(rebuilt.sha256, intact.sha256)
        self.assertTrue(valid_source(rebuilt))
        self.assertEqual(partition(rebuilt)["cells"][0]["sign"], 1)

    def test_source_snapshot_rejects_oversized_fraction_before_recompute(self):
        s = source(input_doc([("0/1", "1/1", {"H0": ["4/1"]})]))
        object.__setattr__(s, "a", Q(1 << 2000, 1))
        self.assertFalse(valid_source(s))
        with self.assertRaisesRegex(Refusal, "SOURCE_RATIONAL_BUDGET"):
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
