#!/usr/bin/env python3
"""Adversarial contract checks for the one-frozen-source biquadratic study."""
from __future__ import annotations
import argparse
import copy
import json
import unittest
from fractions import Fraction as Q
from unittest.mock import patch
import pb00701_v44_two_quadratic_cut_restriction as core

class ExactBiquadraticArithmetic(unittest.TestCase):
    def test_quadratic_generators_and_exact_order(self):
        a=core.K((Q(0),Q(1,2),Q(0),Q(0)))
        b=core.K((Q(0),Q(0),Q(1,3),Q(0)))
        self.assertTrue((2*a*a-core.K.of(1)).zero())
        self.assertTrue((3*b*b-core.K.of(1)).zero())
        self.assertEqual([b.sign(),(a-b).sign(),(core.K.of(1)-a).sign()],[1,1,1])
        self.assertEqual((a+b)*(a-b),core.K.of(Q(1,2)-Q(1,3)))
    def test_exact_signs_near_cancellation(self):
        r=core.K
        self.assertEqual(r((Q(-577),Q(408),Q(0),Q(0))).sign(),-1)
        self.assertEqual(r((Q(577),Q(-408),Q(0),Q(0))).sign(),1)
        self.assertEqual(r((Q(-98),Q(70),Q(0),Q(0))).sign(),1)
        self.assertEqual(r((Q(0),Q(0),Q(0),Q(1))).sign(),1)
        self.assertEqual(r((Q(0),Q(0),Q(0),Q(-1))).sign(),-1)
        self.assertEqual(r((Q(0),Q(0),Q(0),Q(0))).sign(),0)
    def test_basis_product_and_inverse_identity(self):
        root2=core.K((Q(0),Q(1),Q(0),Q(0)))
        root3=core.K((Q(0),Q(0),Q(1),Q(0)))
        root6=core.K((Q(0),Q(0),Q(0),Q(1)))
        self.assertEqual(root2*root3,root6)
        self.assertEqual(root6*root6,core.K.of(6))
        self.assertEqual(root3*root6,root2*3)
        for n in range(1,40):
            p=core.K(tuple(Q(x) for x in (n,n%5-2,n%7-3,n%11-5)))
            self.assertEqual(p*p.inverse(),core.K.of(1))
    def test_field_record_noncanonical_and_nonexact_refuse(self):
        good=core.K((Q(1,2),Q(3),Q(0),Q(-2)))
        self.assertEqual(core.K.parse(good.record()),good)
        for bad in ([1,2,3,4],["1","2","3","4/2"],["0","0","0"],
                    ["1.0","0","0","0"]):
            with self.subTest(bad=bad):
                with self.assertRaises((core.Refusal,ValueError)):core.K.parse(bad)
        with self.assertRaises(core.Refusal):core.K.of(0.1)
        with self.assertRaises(core.Refusal):core.K((Q(1),Q(0),Q(0),1))
        with self.assertRaises(core.Refusal):core.K.of(0).inverse()
    def test_exact_horner_roundtrip(self):
        a=core.K((Q(1),Q(1),Q(-1),Q(0)))
        w=core.K((Q(0),Q(1,2),Q(-1,3),Q(0)))
        p=[Q(1,3),Q(-3,5),Q(7,11)]
        q=core.affine(p,a,w)
        inverse=w.inverse()
        self.assertEqual(core.affine(q,-a*inverse,inverse),
                         [core.K.of(x) for x in p])
        self.assertEqual(core.affine([Q(0)],a,w),[core.K.of(0)])

class FrozenSourceContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good=core.attempt()
        if cls.good.get("status")!=core.SUCCESS:
            raise RuntimeError("SOURCE_PROOF_FAILED:"+repr(cls.good))
    def test_exact_source_sign_order_and_root_counts(self):
        r=self.good
        self.assertEqual(r["evidence_class"],"DETERMINISTIC_MODEL")
        self.assertEqual(r["boundary_signs"],[-1,1,1,1])
        self.assertEqual(r["synthetic_open_root_counts"],[1,0,0])
        self.assertEqual(r["beta_source_sign"],1)
        self.assertEqual(r["beta_sign_method"],
                         "EXACT_STURM_RATIONAL_MIDPOINT_OUTWARD_TRIG_LIPSCHITZ")
        self.assertEqual(r["beta_minimal_polynomial"],[-1,0,3])
        self.assertFalse(r["synthetic_cut_is_historical_orientation_owner"])
    def test_three_positive_child_widths_source_phase_and_channels(self):
        r=self.good
        children=r["synthetic_closed_children"]
        self.assertEqual(len(children),3)
        _,span,_,_=core.parent.derivative._source_snapshot(None)
        last=core.K.of(0)
        m=Q(r["source_derivative_lower"])
        for i,child in enumerate(children):
            a=core.K.parse(child["offset"])
            w=core.K.parse(child["width"])
            b=core.K.parse(child["right"])
            self.assertEqual(child["index"],i)
            self.assertEqual(a,last)
            self.assertEqual(a+w,b)
            self.assertEqual(w.sign(),1)
            self.assertEqual(core.K.parse(child["derivative_lower"]),w*m)
            self.assertEqual(core.K.parse(child["phase_offset"]),
                             core.K.of(span.offset)+a*span.rate)
            self.assertEqual(core.K.parse(child["phase_rate"]),w*span.rate)
            self.assertEqual(set(child["channels"]),set(map(str,span.terms)))
            for h,channels in span.terms.items():
                for j,poly in enumerate(channels):
                    actual=[core.K.parse(x) for x in child["channels"][str(h)][j]]
                    self.assertEqual(actual,core.affine(poly,a,w))
                    inverse=w.inverse()
                    self.assertEqual(core.affine(actual,-a*inverse,inverse),
                                     [core.K.of(x) for x in poly])
            last=b
        self.assertEqual(last,core.K.of(1))
    def test_report_forgery_mutations_fail_closed(self):
        for path,value in (
            (("beta_source_sign",),-1),
            (("boundary_signs",),[-1,-1,1,1]),
            (("synthetic_open_root_counts",),[0,1,0]),
            (("synthetic_closed_children",1,"width"),["0"]*4),
            (("synthetic_closed_children",0,"phase_rate"),["0"]*4),
            (("synthetic_closed_children",2,"root_count"),1),
            (("source_sha256",),"a"*64),
            (("historical_v54_admitted",),True),
            (("mc_b_established",),True),
            (("production_authorized",),True)
        ):
            changed=copy.deepcopy(self.good)
            obj=changed
            for k in path[:-1]:obj=obj[k]
            obj[path[-1]]=value
            with self.subTest(path=path):
                verdict=core.validate_report(changed)
                self.assertEqual(verdict["status"],"BLOCKED",verdict)
                self.assertFalse(verdict["production_authorized"])
    def test_resource_and_cycle_refusal_nontruth(self):
        self.assertEqual(core.validate_report(self.good)["status"],core.SUCCESS)
        self.assertLess(len(core.parent.bridge.previous.canonical(self.good)),
                        core.CAP)
        for bad in ("a"*(core.CAP+10),[0]*40000):
            with self.subTest(kind=type(bad).__name__):
                r=core.validate_report(bad)
                self.assertEqual(r["status"],"RESOURCE_REFUSAL",r)
                self.assertFalse(r["is_truth_value"])
        cyclic=[];cyclic.append(cyclic)
        self.assertEqual(core.validate_report(cyclic)["status"],"RESOURCE_REFUSAL")
    def test_wrong_source_or_budget_remains_nontruth(self):
        with patch.object(core.parent.bridge.previous,"git_blob",return_value="f"*40):
            r=core.attempt()
        self.assertEqual(r["status"],"BLOCKED")
        with patch.object(core.parent.source_sign,"certify_strict_sign",
                          side_effect=core.parent.source_sign.ResourceRefusal(
                              "EXACT_STURM_SIGN_BUDGET_EXHAUSTED")):
            r=core.attempt()
        self.assertEqual(r["status"],"RESOURCE_REFUSAL")
        self.assertFalse(r["is_truth_value"])
    def test_no_authority_promotion(self):
        for flag in ("general_multifield_compositum_constructed",
                     "general_irrational_trig_zero_decider_constructed",
                     "historical_v54_admitted","pb00701_certified",
                     "mc_b_established","mc1_established",
                     "native_geometry_or_step_qualified",
                     "production_authorized"):
            self.assertFalse(self.good[flag],flag)

def contract():
    r=core.attempt()
    if r.get("status")!=core.SUCCESS:raise RuntimeError("TWO_QUADRATIC_SOURCE_REFUSED:"+repr(r))
    return {"status":r["status"],"source_sha256":r["source_sha256"],
        "basis":r["exact_field_basis"],"cuts":r["cut_order"],
        "signs":r["boundary_signs"],"roots":r["synthetic_open_root_counts"],
        "beta_refinements":r["beta_refinements"],
        "report_bytes":len(core.parent.bridge.previous.canonical(r)),
        "historical_v54_admitted":r["historical_v54_admitted"],
        "production_authorized":r["production_authorized"]}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--contract",action="store_true")
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if not (args.contract or args.self_test):p.error("choose --contract or --self-test")
    if args.contract:print(json.dumps(contract(),sort_keys=True))
    if args.self_test:
        suite=unittest.TestSuite()
        suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ExactBiquadraticArithmetic))
        suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(FrozenSourceContract))
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        raise SystemExit(0 if result.wasSuccessful() else 1)

if __name__=="__main__":main()
