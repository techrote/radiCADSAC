#!/usr/bin/env python3
"""Source-bound exact jet/Taylor root guards and complete dyadic partition tests."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
import unittest
from fractions import Fraction as Q

import pb00701_jet_guarded_nontransverse as core
import pb00701_rational_phase_point as point
import pb00701_transverse_trig_interval as interval

def source(terms, *, left="1/2", right="3/2", offset="0", rate="1"):
    return {
        "schema": core.SOURCE_SCHEMA,
        "source_parameter_id": "source-time-t",
        "source_interval": [left, right],
        "phase_turns": [offset, rate],
        "harmonics": terms,
    }

# A non-polynomial-modulation-trivial physical double tangency:
# F(s) = 1 - cos(2pi*s) + (s-1)^2 * sin(2pi*s)/8.
# No general trigonometric factor is assumed by the proof checker.
EVEN = source({
    "0": {"cos": ["1"], "sin": ["0"]},
    "1": {"cos": ["-1"], "sin": ["1/8", "-1/4", "1/8"]},
})
# F(s) = (s-1)^3 * (1 + sin(2pi*s)/1024), order-3 stationary crossing.
ODD = source({
    "0": {"cos": ["-1", "3", "-3", "1"], "sin": ["0"]},
    "1": {"cos": ["0"],
          "sin": ["-1/1024", "3/1024", "-3/1024", "1/1024"]},
})
# The second exact rational root lies outside the guarded event.
SECOND_ROOT = source({
    "0": {"cos": ["-1/4", "3/2", "-9/4", "1"], "sin": ["0"]},
})

class NontransverseRootTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = {
            "even": core.prove(EVEN, "1", ["15/16", "17/16"]),
            "odd": core.prove(ODD, "1", ["7/8", "9/8"]),
        }

    def test_nontrivial_trigonometric_double_tangency_full_root_completeness(self):
        record = self.good["even"]
        self.assertEqual(record["certified_exact_multiplicity"], 2)
        self.assertEqual(record["event_kind"], "TANGENCY")
        self.assertEqual(record["complete_open_root_count"], 1)
        self.assertEqual(record["complete_open_source_signs"], [1, 1])
        self.assertEqual(record["point_derivative_jet"]["status"],
                         "EXACT_RATIONAL_POINT_EVENT")
        self.assertEqual(record["point_derivative_jet"]["exact_vanishing_derivatives"],
                         [0, 1])
        self.assertEqual(record["guard_derivative_strict_sign"], 1)
        self.assertTrue(record["root_coordinate_is_exact_rational"])

    def test_cubic_stationary_crossing_full_root_completeness(self):
        record = self.good["odd"]
        self.assertEqual(record["certified_exact_multiplicity"], 3)
        self.assertEqual(record["event_kind"], "CROSSING")
        self.assertEqual(record["complete_open_root_count"], 1)
        self.assertEqual(record["complete_open_source_signs"], [-1, 1])
        self.assertEqual(record["point_derivative_jet"]["exact_vanishing_derivatives"],
                         [0, 1, 2])
        self.assertEqual(record["guard_derivative_strict_sign"], 1)

    def test_each_left_right_cell_is_complete_and_proved_nonzero(self):
        for record in self.good.values():
            a,b = record["source_interval"]
            l,r = record["guard"]
            left,right = record["zero_free_left_cover"],record["zero_free_right_cover"]
            self.assertEqual(left["source_interval"],[a,l])
            self.assertEqual(right["source_interval"],[r,b])
            self.assertGreater(left["cells"],0)
            self.assertGreater(right["cells"],0)
            self.assertGreaterEqual(left["nodes"],left["cells"])
            self.assertGreaterEqual(right["nodes"],right["cells"])
            self.assertEqual(left["strict_sign"],record["root_left_sign"])
            self.assertEqual(right["strict_sign"],record["root_right_sign"])
            self.assertEqual(len(left["full_cell_certificate_sha256"]),64)
            self.assertEqual(len(right["full_cell_certificate_sha256"]),64)
            mth = list(map(Q,record["guard_mth_derivative_enclosure"]))
            if record["guard_derivative_strict_sign"]==1:
                self.assertGreater(mth[0],0)
            else:
                self.assertLess(mth[1],0)

    def test_replay_consistent_sha_source_binding_and_authority(self):
        for label, record in self.good.items():
            original = EVEN if label=="even" else ODD
            guard = ["15/16","17/16"] if label=="even" else ["7/8","9/8"]
            checked = core.validate_report(original,"1",guard,record)
            self.assertEqual(checked,record)
            self.assertEqual(record["source_record_sha256"],
                             hashlib.sha256(core.canonical(original).encode()).hexdigest())
            self.assertEqual(record["canonical_source_binding_sha256"],
                             point.span_binding(core.source_span(original)))
            self.assertIs(record["frozen_v54_source_admitted"],False)
            self.assertIs(record["mc_b_established"],False)
            self.assertIs(record["production_authorized"],False)

    def test_negated_even_tangency_keeps_even_multiplicity_and_negative_sign(self):
        neg = copy.deepcopy(EVEN)
        neg["harmonics"]["0"]["cos"] = ["-1"]
        neg["harmonics"]["1"]["cos"] = ["1"]
        neg["harmonics"]["1"]["sin"] = ["-1/8","1/4","-1/8"]
        record = core.prove(neg,"1",["15/16","17/16"])
        self.assertEqual((record["root_left_sign"],record["root_right_sign"]),(-1,-1))
        self.assertEqual(record["certified_exact_multiplicity"],2)
        self.assertEqual(record["complete_open_root_count"],1)

    def test_point_jet_alone_not_a_global_root_count(self):
        s = core.source_span(SECOND_ROOT)
        jet = point.point(s,Q(1))
        self.assertEqual(jet["status"],"EXACT_RATIONAL_POINT_EVENT")
        self.assertEqual(jet["one_sided_order"],2)
        self.assertIs(jet["complete_open_roots_claimed"],False)
        refused = core.attempt(SECOND_ROOT,"1",["15/16","17/16"])
        self.assertEqual(refused["status"],"BLOCKED")
        self.assertIs(refused["is_truth_value"],False)

    def test_wide_guard_mth_derivative_not_established(self):
        refusal = core.attempt(EVEN,"1",["3/4","5/4"])
        self.assertEqual(refusal["status"],"RESOURCE_REFUSAL")
        self.assertIn("LOCAL_MTH_DERIVATIVE_SIGN_UNDECIDED",refusal["reason"])

    def test_budget_and_max_jet_order_exhaustion_is_not_truth(self):
        for src,guard,options in (
            (EVEN,["15/16","17/16"],{"max_nodes":1}),
            (EVEN,["15/16","17/16"],{"max_depth":0}),
            (ODD,["7/8","9/8"],{"max_order":2}),
        ):
            refused=core.attempt(src,"1",guard,**options)
            self.assertEqual(refused["status"],"RESOURCE_REFUSAL",refused)
            self.assertIs(refused["is_truth_value"],False)

    def test_missing_or_nonzero_rational_event_is_not_admitted(self):
        bad = copy.deepcopy(EVEN)
        bad["harmonics"]["0"]["cos"] = ["2"]
        refused = core.attempt(bad,"1",["15/16","17/16"])
        self.assertEqual(refused["status"],"BLOCKED")
        self.assertIs(refused["is_truth_value"],False)

    def test_source_mutations_cannot_reuse_original_report(self):
        mutations = (
            lambda x: x["harmonics"]["0"]["cos"].__setitem__(0,"2"),
            lambda x: x["harmonics"]["1"]["sin"].__setitem__(1,"-1/8"),
            lambda x: x["phase_turns"].__setitem__(1,"1/2"),
            lambda x: x["phase_turns"].__setitem__(0,"1/4"),
            lambda x: x["source_interval"].__setitem__(0,"1/4"),
            lambda x: x.__setitem__("source_parameter_id","alien-parameter"),
        )
        for change in mutations:
            altered = copy.deepcopy(EVEN)
            change(altered)
            check = core.validate_report(altered,"1",["15/16","17/16"],
                                         self.good["even"])
            self.assertNotEqual(check.get("status"),
                                "COMPLETE_ONE_NONTRANSVERSE_ORIGINAL_SPAN_ROOT_RESEARCH")
            self.assertIs(check["is_truth_value"],False)

    def test_forged_reports_and_capability_elevation_rejected(self):
        actions = (
            lambda x: x.__setitem__("complete_open_root_count",0),
            lambda x: x.__setitem__("certified_exact_multiplicity",1),
            lambda x: x.__setitem__("guard",["1/2","3/2"]),
            lambda x: x.__setitem__("source_record_sha256","0"*64),
            lambda x: x["zero_free_left_cover"].__setitem__("cells",0),
            lambda x: x["zero_free_right_cover"].__setitem__(
                "full_cell_certificate_sha256","0"*64),
            lambda x: x["point_derivative_jet"].__setitem__("one_sided_order",3),
            lambda x: x.__setitem__("pb00701_certified",True),
            lambda x: x.__setitem__("mc_b_established",True),
            lambda x: x.__setitem__("native_brep_or_step_qualified",True),
            lambda x: x.__setitem__("production_authorized",True),
        )
        for change in actions:
            item=copy.deepcopy(self.good["even"])
            change(item)
            rejected=core.validate_report(EVEN,"1",["15/16","17/16"],item)
            self.assertEqual(rejected["status"],"BLOCKED")
            self.assertIs(rejected["is_truth_value"],False)

    def test_noncanonical_float_unadmitted_and_oversized_inputs(self):
        invalids = [
            (dict(EVEN,source_parameter_id="foreign-id"),"1",["15/16","17/16"]),
            (EVEN,"1.0",["15/16","17/16"]),
            (EVEN,1.0,["15/16","17/16"]),
            (EVEN,"1",["0.9375","17/16"]),
            (EVEN,"1",["1","17/16"]),
            (EVEN,"1",["15/16","1"]),
            (EVEN,"1",["15/16",1.0625]),
            (dict(EVEN,unreviewed="unexpected"),"1",["15/16","17/16"]),
        ]
        for src,r,guard in invalids:
            refused = core.attempt(src,r,guard)
            self.assertEqual(refused["status"],"BLOCKED",refused)
            self.assertIs(refused["is_truth_value"],False)
        oversized=copy.deepcopy(self.good["even"])
        oversized["extra"]="x"*20000
        refused=core.validate_report(EVEN,"1",["15/16","17/16"],oversized)
        self.assertEqual(refused["status"],"RESOURCE_REFUSAL")

    def test_full_custody_and_exact_denominator(self):
        core.pins()
        authority = json.loads((core.ROOT/"handoffs/current-authority.json").read_text())
        domain = json.loads((core.ROOT/
            "research/machining-completeness/tasks/MC-002/domain-contract-v1.json").read_text())
        self.assertFalse(authority["production_authorized"])
        self.assertEqual(authority["capability_status"],"NOT_ESTABLISHED")
        self.assertEqual(len(domain["coverage_rule"]["required_operation_ids"]),26)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract",action="store_true")
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("specify --contract and/or --self-test")
    if args.contract:
        for label,src,guard in (
            ("noncommonfactor_even",EVEN,["15/16","17/16"]),
            ("cubic_odd",ODD,["7/8","9/8"]),
        ):
            report=core.prove(src,"1",guard)
            print(json.dumps({
                "label":label,"status":report["status"],
                "source_sha256":report["source_record_sha256"],
                "exact_root":report["certified_exact_rational_root"],
                "multiplicity":report["certified_exact_multiplicity"],
                "event_kind":report["event_kind"],
                "complete_open_roots":report["complete_open_root_count"],
                "source_signs":report["complete_open_source_signs"],
                "outer_cell_counts":[report["zero_free_left_cover"]["cells"],
                                     report["zero_free_right_cover"]["cells"]],
                "pb00701_certified":False,"production_authorized":False
            },sort_keys=True))
    if args.self_test:
        result=unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(NontransverseRootTests))
        sys.exit(0 if result.wasSuccessful() else 1)

if __name__=="__main__":
    main()
