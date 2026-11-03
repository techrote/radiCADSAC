#!/usr/bin/env python3
"""Adversarial prospective-source tests; deterministic mathematics, not native evidence."""
import copy
import random
import unittest
from fractions import Fraction as Q

import pb00701_two_span_stationary_components as m


def at(p, x):
    return p[0]+x*(p[1]+x*p[2])


def controls(p, lo, hi):
    width = hi-lo
    return [at(p,lo), at(p,lo)+width*(p[1]+2*p[2]*lo)/2, at(p,hi)]


def source(left, right, lo=Q(0), knot=Q(1), hi=Q(2), name="test-source"):
    assert at(left,knot) == at(right,knot)
    # Physical F is C0 + C1, as cos(0)=1 for both original channels.
    c0_left = controls([left[0]-1,left[1],left[2]],lo,knot)
    c0_right = controls([right[0]-1,right[1],right[2]],knot,hi)
    assert c0_left[-1] == c0_right[0]
    return {"grammar":m.GRAMMAR, "source_parameter_id":name,
            "parameter_lo":str(lo), "parameter_hi":str(hi),
            "phase_turn_offset":"0", "phase_turn_rate":"0",
            "cos_splines":{
                "0":{"degree":2,"knots":list(map(str,[lo]*3+[knot]*2+[hi]*3)),
                     "controls":list(map(str,c0_left+c0_right[1:]))},
                "1":{"degree":2,"knots":list(map(str,[lo]*3+[knot]*2+[hi]*3)),
                     "controls":["1"]*5}},"sin_splines":{}}


class MixedComponents(unittest.TestCase):
    def ok(self,s):
        r=m.attempt(s)
        self.assertEqual(r["status"],"EXACT_STATIONARY_ORIGINAL_SOURCE_MIXED_COMPONENTS_RESEARCH",r)
        self.assertFalse(r["pb00701_certified"])
        self.assertFalse(r["mc_b_established"])
        self.assertFalse(r["production_authorized"])
        self.assertEqual(m.validate_report(s,r),r)
        return r

    def test_zero_left_finite_right(self):
        s=source([Q(0)]*3,[Q(-1),Q(1),Q(0)]) # t-1
        r=self.ok(s)
        self.assertEqual(r["maximal_closed_zero_intervals"],[["0","1"]])
        self.assertEqual(r["isolated_zero_points"],[])
        self.assertEqual(r["nonzero_sign_cells"],[
            {"left":"1","right":"2","left_included":False,"right_included":True,"sign":"POSITIVE"}])
        self.assertFalse(r["finite_total_root_cardinality"])
        self.assertEqual(s["cos_splines"]["0"]["controls"][:3],["-1","-1","-1"])

    def test_zero_interval_plus_disjoint_isolated_endpoint(self):
        s=source([Q(0)]*3,[Q(2),Q(-3),Q(1)]) # (t-1)(t-2)
        r=self.ok(s)
        self.assertEqual(r["maximal_closed_zero_intervals"],[["0","1"]])
        self.assertEqual(r["isolated_zero_points"],[
            {"coordinate":"2","source_knot":False,"left_order":1,
             "right_order":None,"global_smooth_knot_multiplicity_claimed":False}])
        self.assertEqual(r["nonzero_sign_cells"][0]["sign"],"NEGATIVE")

    def test_mirror_continuum(self):
        r=self.ok(source([Q(-1),Q(1),Q(0)],[Q(0)]*3))
        self.assertEqual(r["maximal_closed_zero_intervals"],[["1","2"]])
        self.assertFalse(r["isolated_zero_points"])

    def test_isolated_knot_distinct_one_sided_order(self):
        r=self.ok(source([Q(1),Q(-2),Q(1)],[Q(-1),Q(1),Q(0)]))
        self.assertEqual(r["maximal_closed_zero_intervals"],[])
        self.assertEqual(r["isolated_zero_points"],[
            {"coordinate":"1","source_knot":True,"left_order":2,
             "right_order":1,"global_smooth_knot_multiplicity_claimed":False}])
        self.assertEqual(len(r["nonzero_sign_cells"]),2)
        self.assertTrue(r["finite_total_root_cardinality"])

    def test_nonzero_knot_merges_sign_cells(self):
        r=self.ok(source([Q(0),Q(1),Q(0)],[Q(2),Q(-1),Q(0)]))
        self.assertEqual([x["coordinate"] for x in r["isolated_zero_points"]],["0","2"])
        self.assertEqual(len(r["nonzero_sign_cells"]),1)
        self.assertEqual((r["nonzero_sign_cells"][0]["left"],r["nonzero_sign_cells"][0]["right"]),("0","2"))

    def test_full_continuum_and_stationary_cancellation(self):
        s=source([Q(0)]*3,[Q(0)]*3)
        r=self.ok(s)
        self.assertEqual(r["maximal_closed_zero_intervals"],[["0","2"]])
        self.assertFalse(r["nonzero_sign_cells"])
        self.assertEqual(s["cos_splines"]["0"]["controls"],["-1"]*5)
        self.assertEqual(s["cos_splines"]["1"]["controls"],["1"]*5)

    def test_negative_nonunit_domain(self):
        # interval [-3,-1] zero, right (t+1)(t-1) on [-1,1]
        r=self.ok(source([Q(0)]*3,[Q(-1),Q(0),Q(1)],Q(-3),Q(-1),Q(1)))
        self.assertEqual(r["maximal_closed_zero_intervals"],[["-3","-1"]])
        self.assertEqual([x["coordinate"] for x in r["isolated_zero_points"]],["1"])

    def test_negative_and_fractional_original_controls(self):
        r=self.ok(source([Q(0),Q(1),Q(0)],[Q(2),Q(-1),Q(0)],Q(0),Q(1),Q(2)))
        self.assertIn("-1/2",source([Q(0),Q(1),Q(0)],[Q(2),Q(-1),Q(0)])["cos_splines"]["0"]["controls"])
        self.assertTrue(r["finite_total_root_cardinality"])

    def test_refuse_invalid_source_and_forged_report(self):
        s=source([Q(0)]*3,[Q(-1),Q(1),Q(0)])
        good=self.ok(s)
        bad=copy.deepcopy(good)
        bad["maximal_closed_zero_intervals"]=[]
        self.assertEqual(m.validate_report(s,bad)["status"],"BLOCKED")
        s2=copy.deepcopy(s)
        s2["phase_turn_rate"]="1"
        self.assertEqual(m.attempt(s2)["status"],"BLOCKED")
        s3=copy.deepcopy(s)
        s3["cos_splines"]["1"]["knots"][3]="1/2"
        self.assertEqual(m.attempt(s3)["status"],"BLOCKED")
        s4=copy.deepcopy(s)
        s4["cos_splines"]["0"]["controls"][3]="-2"
        self.assertEqual(m.validate_report(s4,good)["status"],"BLOCKED")
        s5=copy.deepcopy(s)
        s5["cos_splines"]["0"]["controls"][0]="1.0"
        self.assertEqual(m.attempt(s5)["status"],"BLOCKED")
        s6=copy.deepcopy(s)
        s6["cos_splines"]["1"]["controls"][1]=0.5
        self.assertEqual(m.attempt(s6)["status"],"BLOCKED")

    def test_unsplit_irrational_quadratic_fails_closed(self):
        # t^2-2 gives irrational roots; no invented finite order proof.
        s=source([Q(-2),Q(0),Q(1)],[Q(-2),Q(0),Q(1)],Q(0),Q(1),Q(3))
        r=m.attempt(s)
        self.assertEqual(r["status"],"BLOCKED")
        self.assertIn("UNSPLIT_IRRATIONAL",r["reason"])
        self.assertFalse(r["is_truth_value"])

    def test_randomized_exact_linear_two_span_recompositions(self):
        rng=random.Random(38011)
        for i in range(120):
            lo=Q(rng.randint(-7,-2),rng.randint(1,3))
            knot=lo+Q(rng.randint(1,4),rng.randint(1,4))
            hi=knot+Q(rng.randint(1,5),rng.randint(1,4))
            a=Q(rng.randint(-5,5))
            b=Q(rng.choice([-4,-3,-2,-1,1,2,3,4]))
            d=Q(rng.choice([-4,-2,-1,1,2,4]))
            # Independently constructed continuous linear pieces.
            left=[a,b,Q(0)]
            right=[a+b*knot-d*knot,d,Q(0)]
            r=self.ok(source(left,right,lo,knot,hi,name=f"random-{i}"))
            self.assertEqual(r["maximal_closed_zero_intervals"],[])


if __name__ == "__main__":
    unittest.main(verbosity=2)
