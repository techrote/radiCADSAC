"""Deterministic adversarial tests for the restricted exact square-lift certificate."""
import json
import sys
import unittest
from dataclasses import replace
from fractions import Fraction as Q
from square_lift import (Spec, Refusal, make_spec, issue, verify, channels,
                         payload, mul, add, scale, evaluate, positive, bernstein_coefficients)


class SquareLiftTests(unittest.TestCase):
    def test_infinite_integer_family_bounded_samples(self):
        # This is a bounded computation over a parameterized, infinitely proven family.
        for k in list(range(3, 45)) + [67, 137, 997, 10000]:
            s = make_spec(k)
            r = issue(s)
            self.assertTrue(verify(s, r))
            self.assertEqual(r["classification"], "ONE_TRANSCENDENTAL_ORDER_2_TOUCH")
            self.assertEqual((r["root_order"],r["crosses"],r["root_count_total"]), (2,False,1))
            self.assertEqual(r["seam_value"], "2")
            self.assertTrue(r["genuine_physical_kink"])
            self.assertEqual(r["knot_right_minus_left_derivative"], "1/2")
            lo,hi = [Q(x) for x in r["root_bracket_open"]]
            self.assertTrue(Q(k) < lo < hi < k+1)
            self.assertEqual(hi-lo, Q(1,3*k))
            # Bracket width shrinks as 1/k; exact rationals, no floating-point root claim.

    def test_infinite_multiplier_and_polynomial_amplitude_family(self):
        for k in (3, 4, 13, 41):
            for a in range(1, 6):
                # Both pieces share P(1/2); selected derivatives are genuinely distinct.
                left = (Q(a), Q(1,4))
                right = (Q(a-Q(1,8)), Q(1,2))
                for r in ((Q(1),), (Q(1),Q(1,3)), (Q(2),Q(-1,3),Q(1,4))):
                    s = make_spec(k,left,right,r)
                    result=issue(s)
                    self.assertTrue(verify(s,result))
                    self.assertEqual(result["root_count_total"],1)
                    self.assertNotEqual(result["knot_right_minus_left_derivative"],"0")

    def test_exact_formal_h2_identity_in_power_basis(self):
        for k in (3, 8, 173):
            s=make_spec(k, r=(Q(2),Q(1,3),Q(1,5)))
            for p in (s.left_p,s.right_p):
                h=channels(s,p)
                t=(Q(k),Q(1))
                q=mul(p,mul(s.r,s.r))
                c0=tuple(Q(x) for x in h["c0"])
                c2=tuple(Q(x) for x in h["c2"])
                s2=tuple(Q(x) for x in h["s2"])
                # coefficient identity under sin^2+cos^2=1:
                # q(sin - t cos)^2 = (q(1+t²)/2) + (q(t²-1)/2)cos2θ - qt sin2θ.
                self.assertEqual(add(c0,c2), mul(q,mul(t,t)))
                self.assertEqual(add(c0,scale(c2,-1)),q)
                self.assertEqual(s2,scale(mul(q,t),-1))
                self.assertEqual(h["c1"], ["0"])
                self.assertEqual(h["s1"], ["0"])

    def test_bernstein_translation_and_conservative_refusal(self):
        b=bernstein_coefficients((Q(1), Q(-1),Q(1)),Q(0),Q(1))
        self.assertTrue(all(x>0 for x in b))
        # a positive polynomial can have a negative Bernstein coefficient;
        # strict-cone checker is sufficient, NOT necessary (explicit refusal).
        with self.assertRaises(Refusal):
            positive((Q(1),Q(-4),Q(5)),Q(0),Q(1))
        for k in (3,10):
            with self.assertRaises(Refusal):
                make_spec(k,r=(Q(-1,2),Q(1)))  # root at u=1/2 would add zeros
            with self.assertRaises(Refusal):
                make_spec(k, left_p=(Q(0),), right_p=(Q(0),))

    def test_identity_zero_is_continuum_not_knot_event(self):
        s=make_spec(3,r=(Q(0),))
        cert=issue(s)
        self.assertTrue(verify(s,cert))
        self.assertEqual(cert["classification"],"IDENTICAL_ZERO_CONTINUUM")
        self.assertEqual(cert["zero_set"],["3","4"])
        self.assertEqual(cert["knot_right_minus_left_derivative"],"0")
        self.assertFalse(cert["genuine_physical_kink"])
        self.assertNotIn("root_bracket_open",cert)

    def test_knot_is_source_derived_and_c0(self):
        s=make_spec(5)
        self.assertEqual(evaluate(s.left_p,Q(1,2)),evaluate(s.right_p,Q(1,2)))
        self.assertTrue(issue(s)["genuine_physical_kink"])
        self.assertRaises(Refusal, make_spec,5,(Q(2),),(Q(3),),(Q(1),))
        smooth=make_spec(5,(Q(2),),(Q(2),),(Q(1),))
        self.assertFalse(issue(smooth)["genuine_physical_kink"])

    def test_forgery_phase_source_and_result(self):
        s=make_spec(3); base=issue(s)
        for modification in ("classification","phase_basis","proof_rule","root_order", "root_bracket_open", "source_sha256", "seam_value", "genuine_physical_kink"):
            altered={**base,modification: "FRAUD"}
            self.assertFalse(verify(s,altered), modification)
        self.assertFalse(verify(s,{**base,"extra":"UNTRUSTED"}))
        self.assertFalse(verify(make_spec(4),base))
        self.assertFalse(verify(make_spec(3,r=(Q(2),)),base))
        # hostile bypass of frozen input dataclass
        object.__setattr__(s,"left_p",(Q(1,2),))
        self.assertFalse(verify(s,base))
        self.assertRaises(Refusal,issue,s)

    def test_source_digest_mutation_cannot_forge_receipt(self):
        # Original-parent negative: issue captures k=4, then source_hash reads
        # mutated caller-owned Spec(k=5), producing an incoherent receipt.
        # The published pre-fix verifier accepted under the same interleaving.
        import square_lift as original

        source = make_spec(4)
        expected = issue(source)
        digest_five = issue(make_spec(5))["source_sha256"]

        def mutate_original_at_hash(compute):
            seen = []
            def trace(frame, event, arg):
                if event == "call" and frame.f_code is original.source_hash.__code__:
                    seen.append(True)
                    object.__setattr__(source, "k", 5)
                    sys.settrace(None)
                return trace
            sys.settrace(trace)
            try:
                outcome = compute()
            finally:
                sys.settrace(None)
            self.assertTrue(seen, "must execute original source_hash boundary")
            return outcome

        raced = mutate_original_at_hash(lambda: issue(source))
        self.assertEqual(raced, expected)  # entire receipt is bound to k=4
        self.assertNotEqual(raced["source_sha256"], digest_five)

        # Construct the previously issuable contradictory source-bound receipt.
        forgery = {**expected, "source_sha256": digest_five}
        object.__setattr__(source, "k", 4)
        self.assertFalse(mutate_original_at_hash(lambda: verify(source, forgery)))
        object.__setattr__(source, "k", 4)
        self.assertTrue(mutate_original_at_hash(lambda: verify(source, expected)))
        self.assertFalse(verify(source, expected))  # source now k=5
        object.__setattr__(source, "k", 4)
        self.assertTrue(verify(source, expected))

    def test_snapshot_preflights_forged_fraction_budget(self):
        # No gcd/reconstruction of a forged unbounded Fraction before refusal.
        s = make_spec(4)
        object.__setattr__(s, "left_p", (Q(2**200000, 3),))
        with self.assertRaisesRegex(Refusal, "bit budget"):
            issue(s)
        self.assertFalse(verify(s, issue(make_spec(4))))

    def test_malformed_and_budget_refusals(self):
        invalid=[(2,(),(),()), (10001,(),(),()),(True,(),(),()),
                 (3,(0.1,),(0.1,),(1,)), (3,tuple(Q(1) for _ in range(6)),(Q(1),),(Q(1),)),
                 (3,(Q(2**130),),(Q(2**130),),(Q(1),)),
                 (3,(Q(1),Q(0)),(Q(1),),(Q(1),)),
                 (3,(Q(1),),(Q(1),),"infinite")]
        for k,a,b,r in invalid:
            with self.subTest(k=k,a=a,b=b,r=r):
                self.assertRaises(Refusal,make_spec,k,a,b,r)
        # Never consume unbounded generators of input coefficients.
        class Bomb:
            def __iter__(self): raise AssertionError("must not consume")
        self.assertRaises(Refusal,make_spec,3,Bomb(),(Q(2),),(Q(1),))


if __name__=="__main__": unittest.main(verbosity=2)
