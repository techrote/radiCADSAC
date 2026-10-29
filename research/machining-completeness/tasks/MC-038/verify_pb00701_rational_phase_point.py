#!/usr/bin/env python3
"""Independent deterministic point-jet tests and pinned original-source replay."""
from __future__ import annotations

import argparse
import copy
import json
import sys
import unittest
from fractions import Fraction as Q

import pb00701_rational_phase_point as point
import pb00701_transverse_trig_interval as interval
import pb00701_transverse_original_source as original


def span(left,right,rate,terms,offset=0):
    return interval.Span(left,right,offset,rate,terms)


class RationalPointResearchTests(unittest.TestCase):
    def test_cyclotomic_exact_primitive_arithmetic(self):
        self.assertEqual(point.cyclotomic(4),(Q(1),Q(0),Q(1)))
        self.assertEqual(point.cyclotomic(12),
                         (Q(1),Q(0),Q(-1),Q(0),Q(1)))
        phi=point.cyclotomic(4)
        self.assertEqual(point.ring_trig(Q(1,4),4,phi),
                         ((Q(0),Q(0)),(Q(1),Q(0))))
        self.assertEqual(point.ring_trig(Q(-1,4),4,phi),
                         ((Q(0),Q(0)),(Q(-1),Q(0))))

    def test_exact_polynomial_derivatives(self):
        polynomial=(Q(3),Q(2),Q(5),Q(7))
        self.assertEqual(point.point_derivative(polynomial,Q(2),0),Q(3+4+20+56))
        self.assertEqual(point.point_derivative(polynomial,Q(2),1),Q(2+20+84))
        self.assertEqual(point.point_derivative(polynomial,Q(2),2),Q(10+84))
        self.assertEqual(point.point_derivative(polynomial,Q(2),3),Q(42))

    def test_simple_trig_crossing_at_exact_quarter_turn(self):
        s=span(0,1,1,{1:((1,),(0,))})
        result=point.point(s,Q(1,4))
        self.assertEqual(result["status"],"EXACT_RATIONAL_POINT_EVENT")
        self.assertEqual(result["one_sided_order"],1)
        self.assertEqual((result["left_sign"],result["right_sign"]),(1,-1))
        self.assertEqual(result["event_kind"],"CROSSING")
        self.assertFalse(result["complete_open_roots_claimed"])

    def test_even_trigonometric_tangency_and_endpoint_semantics(self):
        s=span(0,1,1,{0:((Q(1,2),),(0,)),
                      2:((Q(-1,2),),(0,))})
        result=point.point(s,0)
        self.assertEqual(result["one_sided_order"],2)
        self.assertEqual(result["event_kind"],"TANGENCY")
        self.assertEqual((result["left_sign"],result["right_sign"]),(1,1))
        self.assertFalse(result["left_in_source"])
        self.assertTrue(result["right_in_source"])

    def test_polynomial_modulated_exact_even_and_odd_orders(self):
        even=span(0,2,1,{1:((0,),(-1,1))})
        odd=span(0,2,1,{1:((0,),(1,-2,1))})
        a,b=point.point(even,1),point.point(odd,1)
        self.assertEqual((a["one_sided_order"],a["event_kind"]),(2,"TANGENCY"))
        self.assertEqual((a["left_sign"],a["right_sign"]),(1,1))
        self.assertEqual((b["one_sided_order"],b["event_kind"]),(3,"CROSSING"))
        self.assertEqual((b["left_sign"],b["right_sign"]),(-1,1))

    def test_different_source_knot_orders_single_physical_event(self):
        left=span(0,1,Q(1,2),{0:((1,),(0,)),1:((1,),(0,))})
        right=span(1,2,Q(1,2),{1:((0,),(1,))})
        result=point.compose_knot(left,right,1)
        self.assertEqual(result["status"],"EXACT_SINGLE_SOURCE_KNOT_ZERO")
        self.assertEqual(result["physical_zero_events"],1)
        self.assertEqual((result["left_one_sided_order"],
                          result["right_one_sided_order"]),(2,1))
        self.assertEqual((result["left_sign"],result["right_sign"]),(1,-1))
        self.assertEqual(result["event_kind"],"CROSSING")
        self.assertFalse(result["global_smooth_multiplicity_claimed"])

    def test_touching_knot_and_nonzero_knot(self):
        left=span(0,1,Q(1,2),{0:((1,),(0,)),1:((1,),(0,))})
        right=span(1,2,Q(1,2),{0:((1,),(0,)),1:((1,),(0,))})
        zero=point.compose_knot(left,right,1)
        self.assertEqual(zero["event_kind"],"TOUCHING")
        self.assertEqual((zero["left_one_sided_order"],
                          zero["right_one_sided_order"]),(2,2))
        first=span(0,1,1,{1:((1,),(0,))})
        second=span(1,2,1,{1:((1,),(0,))})
        nonzero=point.compose_knot(first,second,1)
        self.assertEqual(nonzero["status"],"EXACT_NONZERO_SOURCE_KNOT")
        self.assertEqual(nonzero["sign"],1)
        self.assertEqual(nonzero["physical_zero_events"],0)

    def test_discontinuity_and_phase_mismatch_refuse(self):
        left=span(0,1,Q(1,2),{0:((1,),(0,)),1:((1,),(0,))})
        bad=span(1,2,Q(1,2),{0:((1,),(0,)),1:((0,),(1,))})
        result=point.attempt(point.compose_knot,left,bad,1)
        self.assertEqual(result["reason"],"DISCONTINUOUS_SOURCE_KNOT")
        phase=span(1,2,1,{1:((1,),(0,))})
        self.assertEqual(point.attempt(point.compose_knot,left,phase,1)
                         ["status"],"BLOCKED")

    def test_exact_identity_and_resource_refusals(self):
        zero=span(0,1,0,{0:((0,),(0,))})
        self.assertEqual(point.attempt(point.point,zero,0,3)["status"],
                         "RESOURCE_REFUSAL")
        repeated=span(0,1,1,{0:((Q(1,2),),(0,)),
                             2:((Q(-1,2),),(0,))})
        self.assertEqual(point.attempt(point.point,repeated,0,1)["status"],
                         "RESOURCE_REFUSAL")
        expensive=span(0,1,Q(1,37),{1:((1,),(0,))})
        refusal=point.attempt(point.point,expensive,Q(1,2))
        self.assertEqual(refusal["reason"],"CYCLOTOMIC_ORDER_RESOURCE_LIMIT")
        self.assertIs(refusal["is_truth_value"],False)

    def test_mutated_span_cannot_bypass_source_grammar(self):
        s=span(0,1,1,{1:((1,),(0,))})
        s.terms[1]=((1.0,),(0,))
        failure=point.attempt(point.point,s,Q(1,4))
        self.assertEqual(failure["status"],"BLOCKED")
        self.assertEqual(failure["reason"],"NONEXACT_COEFFICIENT_TYPE")

    def test_forged_or_count_only_point_witness_rejected(self):
        s=span(0,1,1,{1:((1,),(0,))})
        good=point.point(s,Q(1,4))
        self.assertEqual(point.validate_submitted(s,Q(1,4),good),good)
        for key,value in (("one_sided_order",2),("left_sign",-1),
                          ("historical_v54_admitted",True),
                          ("complete_open_roots_claimed",True),
                          ("source_binding_sha256","0"*64)):
            forged=copy.deepcopy(good)
            forged[key]=value
            with self.subTest(key=key),self.assertRaises(point.Refusal):
                point.validate_submitted(s,Q(1,4),forged)

    def test_pinned_v27_v41_original_source_rational_points(self):
        index=original.custody()
        lowerer=original.v27.exact_lowerer()
        for case in original.CASES:
            with self.subTest(case=case):
                views=original.original_spans(index[case],lowerer)
                expected=(1,-1,1) if case in (original.v27.TAIL0,
                                                original.v27.TAIL100) else (-1,-1)
                actual=[]
                for i,view in enumerate(views):
                    if i==0:
                        first=point.point(view["span"],view["interval"][0])
                        self.assertEqual(first["status"],"EXACT_NONZERO_RATIONAL_POINT")
                        actual.append(first["value_sign"])
                    last=point.point(view["span"],view["interval"][1])
                    self.assertEqual(last["status"],"EXACT_NONZERO_RATIONAL_POINT")
                    actual.append(last["value_sign"])
                self.assertEqual(tuple(actual),expected)
                if len(views)==2:
                    join=point.compose_knot(views[0]["span"],views[1]["span"],1)
                    self.assertEqual(join["status"],"EXACT_NONZERO_SOURCE_KNOT")
                    self.assertEqual(join["sign"],-1)
        for path,sha in original.PINS.items():
            self.assertEqual(original.git_blob(path),sha)
        self.assertEqual(len(original.load(original.DOMAIN)["coverage_rule"]
                             ["required_operation_ids"]),26)
        self.assertFalse(original.load(original.AUTH)["production_authorized"])


def run():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract",action="store_true")
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("specify --contract and/or --self-test")
    if args.contract:
        index=original.custody()
        lowerer=original.v27.exact_lowerer()
        for case in original.CASES:
            views=original.original_spans(index[case],lowerer)
            results=[point.point(v["span"],x) for v in views
                     for x in v["interval"]]
            print(json.dumps({"case":case,"point_statuses":[r["status"] for r in results],
                              "point_signs":[r["value_sign"] for r in results],
                              "source_knots":[point.compose_knot(
                                  views[i]["span"],views[i+1]["span"],
                                  views[i]["interval"][1])["status"]
                                  for i in range(len(views)-1)],
                              "historical_child_certified":False},
                             sort_keys=True))
    if args.self_test:
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(RationalPointResearchTests)
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)


if __name__=="__main__":
    run()
