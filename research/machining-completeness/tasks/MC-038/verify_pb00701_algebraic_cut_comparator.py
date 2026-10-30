#!/usr/bin/env python3
"""Source-bound deterministic and adversarial root-comparison checks."""
from fractions import Fraction as Q
import argparse
import json
import unittest
import pb00701_algebraic_cut_comparator as m
import verify_pb00701_multiquadratic_embedding as pinned_predecessor

# This must execute the repository's independent fixed-field source and
# historical-authority pin checks. A bare locally copied polynomial is not
# acceptable proof of the producing original-source identity.
FROZEN_SOURCE_SHA256 = "d3b3a90024ea283dfd96811b8fc2b66ceff621b3b48defc44c77f85557adbba2"

# Source reference: exact historical V45 cut alpha=+sqrt(2)/2.
# The first isolator is not a numerical approximation: one exact Sturm root.
ALPHA={"polynomial":["-1","0","2"],"lower":"7/10","upper":"3/4"}
# Different squarefree polynomial, same real root. Independent factor x^2-3.
ALPHA_PRODUCT={"polynomial":["3","0","-7","0","2"],"lower":"7/10","upper":"3/4"}
BETA={"polynomial":["-1","0","3"],"lower":"1/2","upper":"3/5"}
NEG_ALPHA={"polynomial":["-1","0","2"],"lower":"-3/4","upper":"-7/10"}
# Cubic irrational root (strictly between 1 and 2).
CUBIC={"polynomial":["-2","0","0","1"],"lower":"1","upper":"2"}
# Rational root isolated as a polynomial root, not decimal/float approximation.
ONE={"polynomial":["-1","1"],"lower":"0","upper":"2"}


def contract():
    previous=pinned_predecessor.source_contract()
    if (previous["original_source_sha256"] != FROZEN_SOURCE_SHA256 or
            previous["checked_vectors"] != 625 or
            previous["mc_b_established"] is not False):
        raise m.Refusal("PREDECESSOR_ORIGINAL_SOURCE_PIN_MISMATCH")
    examples = [(ALPHA,ALPHA_PRODUCT,0), (BETA,ALPHA,-1),
                (NEG_ALPHA,BETA,-1), (ALPHA,CUBIC,-1),
                (ONE,CUBIC,-1), (ONE,ALPHA,1)]
    methods=[]
    for a,b,sign in examples:
        actual=m.compare(a,b)
        if actual["relation"]!=sign or m.verify_comparison(a,b,actual)!={"status":"CERTIFIED","relation":sign}:
            raise m.Refusal("SOURCE_CUT_COMPARISON_DISAGREEMENT")
        reverse=m.compare(b,a)
        if reverse["relation"] != -sign:
            raise m.Refusal("ANTISYMMETRY_DISAGREEMENT")
        methods.append(actual["method"])
    # Three independently represented exact roots ordered by their polynomial,
    # not by samples or a shared multiquadratic field.
    order=[NEG_ALPHA,BETA,ALPHA,ONE,CUBIC]
    checked=0
    for i,a in enumerate(order):
        for j,b in enumerate(order):
            result=m.compare(a,b)
            expected=(i>j)-(i<j)
            if result["relation"]!=expected:
                raise m.Refusal("EXACT_TOTAL_ORDER_DISAGREEMENT")
            checked+=1
    return {"schema":m.SCHEMA,"status":"EXACT_BOUNDED_ROOT_CUT_ORDERING_PASSED",
            "evidence_class":"DETERMINISTIC_MODEL","examples":len(examples),
            "ordered_pairs":checked,"gcd_equalities":methods.count("COMMON_ROOT_GCD"),
            "original_source_sha256":FROZEN_SOURCE_SHA256,
            "max_degree":m.MAX_DEGREE,"bounded_rounds":m.MAX_ROUNDS,
            "arbitrary_algebraic_compositum":False,
            "irrational_trigonometric_zero_decider":False,
            "nonmonotone_source_root_theorem":False,
            "historical_v54_admitted":False,"mc_b_established":False,
            "mc1_established":False,"production_authorized":False}

class Tests(unittest.TestCase):
    def test_exact_equality_and_order(self):
        r=m.compare(ALPHA,ALPHA_PRODUCT)
        self.assertEqual(r["relation"],0)
        self.assertEqual(r["method"],"COMMON_ROOT_GCD")
        self.assertEqual(m.compare(BETA,ALPHA)["relation"],-1)
        self.assertEqual(m.compare(ALPHA,BETA)["relation"],1)
        self.assertEqual(m.compare(CUBIC,CUBIC)["relation"],0)
    def test_rational_midpoint_and_reducible_polynomial(self):
        # Midpoint q=1 exactly meets the first root; comparisons cannot
        # classify a zero at q as a strictly separated root.
        self.assertEqual(m.compare(ONE,CUBIC)["relation"],-1)
        self.assertEqual(m.compare(ALPHA_PRODUCT,ALPHA)["relation"],0)
    def test_midpoint_rational_equality_and_sign(self):
        sqrt2={"polynomial":["-2","0","1"],"lower":"0","upper":"2"}
        product={"polynomial":["-2","1","1"],"lower":"0","upper":"2"}
        self.assertEqual(m.compare(ONE,sqrt2)["relation"],-1)
        self.assertEqual(m.compare(ONE,product)["relation"],0)
        self.assertEqual(m.compare(sqrt2,ONE)["relation"],1)
    def test_very_close_distinct_roots_refuse_boundedly(self):
        n=(1<<90)+1
        # Exact selected-root gap 2/n lies strictly between 2^-90 and 2^-89.
        gap=Q(2,n)
        self.assertLess(Q(1,1<<90),gap)
        self.assertLess(gap,Q(1,1<<89))
        a={"polynomial":[str(-n-2),str(n)],"lower":"0","upper":"2"}
        b={"polynomial":[str(-n-4),str(n)],"lower":"0","upper":"2"}
        with self.assertRaisesRegex(m.ResourceRefusal,"SEPARATION_ROUND_BUDGET"):
            m.compare(a,b)
        self.assertEqual(m.verify_comparison(a,b,m.compare(BETA,ALPHA))["status"],"RESOURCE_REFUSAL")
    def test_independent_rational_order_grid(self):
        # Exact independent Fraction ordering, including equality at q=0.
        roots=[Q(-5,2),Q(-3,2),Q(-1,2),Q(0),Q(1,2),Q(3,2),Q(5,2)]
        records=[{"polynomial":[str(-x.numerator),str(x.denominator)],
                  "lower":"-3","upper":"3"} for x in roots]
        for i,a in enumerate(records):
            for j,b in enumerate(records):
                self.assertEqual(m.compare(a,b)["relation"], (i>j)-(i<j))
    def test_same_polynomial_distinct_overlapping_conjugates(self):
        a={"polynomial":["-1","0","2"],"lower":"-2","upper":"0"}
        b={"polynomial":["-1","0","2"],"lower":"-1/10","upper":"2"}
        self.assertEqual(m.compare(a,b)["relation"],-1)
        self.assertEqual(m.compare(b,a)["relation"],1)
    def test_invalid_isolators(self):
        for candidate in (
            dict(ALPHA,lower="0",upper="2"),
            dict(ALPHA,lower="1",upper="0"),
            dict(ALPHA,lower="7/10",upper="7/10"),
            dict(ALPHA,lower="1/2",upper="1/2"),
            dict(ALPHA,lower="01/2"),
            {"polynomial":["1","-2","1"],"lower":"0","upper":"2"},
            {"polynomial":["2","0","-4"],"lower":"0","upper":"1"},
            {"polynomial":["0","0","1"],"lower":"-1","upper":"1"},
            {"polynomial":["1","0","1"],"lower":"0","upper":"1"},
            {"polynomial":["0","1"],"lower":"0","upper":"1"},
        ):
            with self.subTest(candidate=candidate):
                self.assertEqual(m.verify_comparison(candidate,ONE,{} )["status"],"BLOCKED")
    def test_forged_comparison_and_resource(self):
        good=m.compare(BETA,ALPHA)
        self.assertEqual(m.verify_comparison(BETA,ALPHA,good)["status"],"CERTIFIED")
        self.assertEqual(m.verify_comparison(BETA,ALPHA,dict(good,relation=0))["status"],"BLOCKED")
        self.assertEqual(m.verify_comparison(BETA,ALPHA,{"large":"x"*m.MAX_CERT_BYTES})["status"],"BLOCKED")
        self.assertEqual(m.verify_comparison(BETA,ALPHA,dict(good,gcd=["x"*(m.MAX_CERT_BYTES+1)]))["status"],"RESOURCE_REFUSAL")
        self.assertEqual(m.verify_comparison(BETA,ALPHA,dict(good,gcd=[{}]))["status"],"BLOCKED")
        big={"polynomial":["1","0",str((1<<97)+1)],"lower":"-1","upper":"1"}
        self.assertEqual(m.verify_comparison(big,ALPHA,good)["status"],"RESOURCE_REFUSAL")
    def test_source_bound_contract(self):
        r=contract()
        self.assertEqual(r["ordered_pairs"],25)
        self.assertFalse(r["mc_b_established"])

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract",action="store_true")
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("Choose --contract and/or --self-test")
    if args.contract:
        print(json.dumps(contract(),sort_keys=True))
    if args.self_test:
        result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
        raise SystemExit(0 if result.wasSuccessful() else 1)
if __name__ == "__main__":
    main()
