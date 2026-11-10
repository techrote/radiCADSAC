"""Exact rational controls for signed algebraic-time local-cell research."""
import unittest
from fractions import Fraction as Q
from signed_cell import *

M=(-2,0,1) # x^2-2, irreducible over Q

def poly_mul(a,b):
    out=[Q(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    return out

def doc(h0=(0,),c1=(0,),s1=(0,),c2=(0,),s2=(0,),b='1/1'):
    def enc(v): return [fmt(Q(x)) for x in v]
    return dict(a='0/1',b=b,H0=enc(h0),C1=enc(c1),S1=enc(s1),C2=enc(c2),S2=enc(s2))

def germ(r=1):return {"result":"EXACT_ZERO","multiplicity":r,"source_sha256":"test-only-untrusted"}

class ExactControls(unittest.TestCase):
    def test_pi_and_trig_bounds(self):
        for n in (4,8,12,16):
            l,h=pi_interval(n)
            self.assertLess(l,Q(22,7));self.assertGreater(h,Q(3))
            for phase in (Q(0),Q(1,2),Q(1),Q(3,2),Q(-1,2),Q(89,7)):
                cosi,sini=trig_interval(phase,1,n,(l,h))
                self.assertLessEqual(cosi[0],cosi[1]);self.assertLessEqual(sini[0],sini[1])
                # quarter turns have exact values, even after period reduction
                if phase in (Q(0),Q(1,2),Q(1),Q(3,2),Q(-1,2)):
                    cosval={Q(0):1,Q(1,2):0,Q(1):-1,Q(3,2):0,Q(-1,2):0}[phase]
                    sinval={Q(0):0,Q(1,2):1,Q(1):0,Q(3,2):-1,Q(-1,2):-1}[phase]
                    self.assertLessEqual(cosi[0],cosval);self.assertGreaterEqual(cosi[1],cosval)
                    self.assertLessEqual(sini[0],sinval);self.assertGreaterEqual(sini[1],sinval)

    def test_dc_positive_crossing(self):
        src=doc(h0=poly_mul(M,[5]),c1=M,s2=poly_mul(M,[Q(1,2)]))
        cert=signed_from_verified_germ(src,M,['7/5','3/2'],germ(1),16)
        self.assertEqual((cert['left_sign'],cert['right_sign'],cert['zero_kind']),(-1,1,'CROSS'))

    def test_mixed_negative_touch(self):
        m2=poly_mul(M,M)
        src=doc(h0=poly_mul(m2,[-5]),c1=m2,s2=m2,b='-2/1')
        cert=signed_from_verified_germ(src,M,['1414/1000','1415/1000'],germ(2),16)
        self.assertEqual((cert['left_sign'],cert['right_sign'],cert['zero_kind']),(-1,-1,'TOUCH'))

    def test_pure_cos_crossing_no_dc(self):
        src=doc(c1=M)
        cert=signed_from_verified_germ(src,M,['1414/1000','1415/1000'],germ(1),16)
        self.assertEqual((cert['left_sign'],cert['right_sign']), (1,-1))

    def test_family_and_sign_reversal(self):
        for k in range(1,11):
            base=poly_mul(M,[k])
            src=doc(h0=base,c1=M)
            cert=signed_from_verified_germ(src,M,['1414/1000','1415/1000'],germ(1),16)
            self.assertEqual((cert['left_sign'],cert['right_sign']),(-1,1))

    def test_low_budget_and_forgery_refuse(self):
        src=doc(c1=M)
        with self.assertRaisesRegex(Refusal,'COFACTOR_SIGN_UNKNOWN'):
            signed_from_verified_germ(src,M,['1/1','2/1'],germ(1),4)
        with self.assertRaisesRegex(Refusal,'VALUATION_MISMATCH'):
            signed_from_verified_germ(doc(c1=[1]),M,['7/5','3/2'],germ(1),16)
        with self.assertRaisesRegex(Refusal,'NOT_ISOLATED'):
            signed_from_verified_germ(doc(c1=M),M,['7/5','3/2'],{'result':'EXACT_NONZERO','multiplicity':0},16)
        with self.assertRaisesRegex(Refusal,'COFACTOR_SIGN_UNKNOWN'):
            # cos near a zero at rational quarter turn; cannot prove strict sign in enclosing wide cell.
            signed_from_verified_germ(doc(c1=M),M,['1/2','3/2'],germ(1),4)

    def test_signed_germ_and_cofactor_share_captured_source(self):
        # A real F2 parent returns a source SHA, then F9 must not observe a
        # different caller-owned H0 when forming signed sides. Before this fix,
        # sys.settrace deterministically caused original F9 verify to accept
        # a receipt with OLD source SHA and the OPPOSITE source's sided signs.
        import copy
        import sys
        import signed_cell
        minimal = (-2, 0, 1)
        bracket = ['707/500', '283/200']
        original = doc(h0=poly_mul(minimal, [5]))
        opposite = doc(h0=poly_mul(minimal, [-5]))
        honest = signed_cell.certify(original, minimal, 3, bracket, 16)
        opposite_receipt = signed_cell.certify(opposite, minimal, 3, bracket, 16)
        self.assertTrue(signed_cell.verify(original, honest))
        self.assertNotEqual((honest['left_sign'], honest['right_sign']),
                            (opposite_receipt['left_sign'], opposite_receipt['right_sign']))

        def trace_source_change(source):
            triggered = [False]
            def tracer(frame, event, arg):
                if (event == 'call' and
                        frame.f_code is signed_cell.signed_from_verified_germ.__code__
                        and not triggered[0]):
                    triggered[0] = True
                    source['H0'][:] = opposite['H0']
                return tracer
            return tracer, triggered

        producer_input = copy.deepcopy(original)
        tracer, triggered = trace_source_change(producer_input)
        sys.settrace(tracer)
        try:
            raced = signed_cell.certify(producer_input, minimal, 3, bracket, 16)
        finally:
            sys.settrace(None)
        self.assertTrue(triggered[0])
        self.assertEqual(raced['source_sha256'], honest['source_sha256'])
        self.assertEqual((raced['left_sign'], raced['right_sign']),
                         (honest['left_sign'], honest['right_sign']))
        self.assertTrue(signed_cell.verify(original, raced))
        self.assertFalse(signed_cell.verify(opposite, raced))

        # A forged mixed-source receipt is refused even when the *caller input*
        # is altered at the same real verifier/signing function boundary.
        forged = copy.deepcopy(honest)
        forged['left_sign'], forged['right_sign'] = (
            opposite_receipt['left_sign'], opposite_receipt['right_sign'])
        self.assertFalse(signed_cell.verify(original, forged))
        verifier_input = copy.deepcopy(original)
        tracer, triggered = trace_source_change(verifier_input)
        sys.settrace(tracer)
        try:
            accepted = signed_cell.verify(verifier_input, forged)
        finally:
            sys.settrace(None)
        self.assertTrue(triggered[0])
        self.assertFalse(accepted)

    def test_source_anchored_original_module_replay(self):
        # This uses the REAL A1 module when checked out in the repository.
        try:
            import algebraic_degree
        except ModuleNotFoundError:
            self.skipTest('exact original algebraic_degree.py not present in scratch')
        import copy
        src=doc(h0=poly_mul(M,[5]),c1=M,s2=poly_mul(M,[Q(1,2)]))
        receipt=certify(src,M,3,['7/5','3/2'],16)
        self.assertTrue(verify(src,receipt))
        self.assertEqual((receipt['left_sign'],receipt['right_sign']),(-1,1))
        altered=copy.deepcopy(src)
        altered['b']='-1/1'
        self.assertFalse(verify(altered,receipt))
        changed=copy.deepcopy(receipt)
        changed['left_sign']=1
        self.assertFalse(verify(src,changed))
        changed=copy.deepcopy(receipt)
        changed['germ']['multiplicity']=2
        self.assertFalse(verify(src,changed))

if __name__=='__main__':unittest.main(verbosity=2)
