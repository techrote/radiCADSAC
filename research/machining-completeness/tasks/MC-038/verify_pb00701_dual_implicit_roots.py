#!/usr/bin/env python3
"""Exact-head contract and adversarial checks of two complete root proof paths."""
from __future__ import annotations
import argparse
import copy
import json
import sys
import unittest
from fractions import Fraction as Q
import pb00701_dual_implicit_roots as core

class DualImplicitRootTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reports = core.catalogue()

    def test_all_three_frozen_original_sources(self):
        self.assertEqual(set(self.reports), set(core.CASES))
        for case, report in self.reports.items():
            with self.subTest(case=case):
                self.assertEqual(core.validate(report)["status"],
                                 "SAME_SOURCE_DUAL_ROOT_PROOFS_RECONCILED")
                self.assertEqual(report["complete_open_roots"], 2)
                self.assertEqual(len(report["root_matches"]), 2)
                self.assertEqual(len(report["physical_signs"]), 3)
                self.assertFalse(report["historical_child_certified"])
                self.assertFalse(report["general_v27_v41_theorem"])
                self.assertFalse(report["mc_b_established"])
                self.assertFalse(report["production_authorized"])

    def test_intersections_are_exact_strict_ordered_and_not_coordinates(self):
        for report in self.reports.values():
            prior = None
            for root in report["root_matches"]:
                a, b = map(Q, root["fixed_bracket"])
                c, d = map(Q, root["transverse_bracket"])
                lo, hi = map(Q, root["strict_intersection_bracket"])
                self.assertEqual((lo, hi), (max(a, c), min(b, d)))
                self.assertLess(lo, hi)
                self.assertLessEqual(hi-lo, min(b-a, d-c))
                if prior is not None:
                    self.assertLessEqual(prior, lo)
                prior = hi
                self.assertFalse(root["source_root_closed_form_claimed"])

    def test_same_source_exact_rank_relation(self):
        for report in self.reports.values():
            for first, second, expected in ((0, 0, "SAME"), (1, 1, "SAME"),
                                            (0, 1, "LESS"), (1, 0, "GREATER")):
                relation = core.compare(report, first, report, second)
                self.assertEqual(relation["status"], "CHECKED_SAME_SOURCE_ORDER")
                self.assertEqual(relation["relation"], expected)

    def test_cross_source_comparison_refuses_even_if_brackets_overlap(self):
        cases = list(core.CASES)
        result = core.compare(self.reports[cases[0]], 0,
                              self.reports[cases[1]], 0)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["is_truth_value"])

    def test_unverified_overlapping_brackets_not_same_root(self):
        first = copy.deepcopy(self.reports[list(core.CASES)[0]])
        first["root_matches"][0]["fixed_bracket"] = (
            first["root_matches"][0]["transverse_bracket"])
        self.assertEqual(core.validate(first)["status"], "BLOCKED")

    def test_nonvacuous_different_owner_root_comparison(self):
        # V27 tail100 has different physical child owners across its knot.
        report = self.reports[core.fixed.v27.TAIL100]
        owners = [root["owner"] for root in report["root_matches"]]
        self.assertNotEqual(owners[0], owners[1])
        self.assertEqual(core.compare(report, 0, report, 1)["relation"], "LESS")

    def test_different_hash_serializations_are_bound_not_equated(self):
        for report in self.reports.values():
            self.assertNotEqual(report["fixed_source_sha256"],
                                report["transverse_source_sha256"])
            self.assertEqual(len(report["fixed_source_sha256"]), 64)
            self.assertEqual(len(report["transverse_source_sha256"]), 64)

    def test_strictly_overlapping_intervals_can_contain_distinct_roots(self):
        # For (x-1/4)(x-7/4), each interval isolates a different root,
        # yet the intervals overlap: intersection alone is NOT equality.
        a, b = Q(1, 4), Q(7, 4)
        i1, i2 = (Q(0), Q(3, 2)), (Q(1), Q(2))
        self.assertTrue(i1[0] < a < i1[1] < b)
        self.assertTrue(a < i2[0] < b < i2[1])
        self.assertLess(max(i1[0], i2[0]), min(i1[1], i2[1]))
        self.assertNotEqual(a, b)

    def test_forged_counts_source_owners_roots_events_and_gates_refuse(self):
        report = self.reports[list(core.CASES)[0]]
        changes = {
            "omitted_root": lambda x: x["root_matches"].pop(),
            "changed_count": lambda x: x.__setitem__("complete_open_roots", 1),
            "duplicate_root": lambda x: x["root_matches"].__setitem__(
                1, copy.deepcopy(x["root_matches"][0])),
            "reversed_order": lambda x: x["root_matches"].reverse(),
            "forged_rank": lambda x: x["root_matches"][0].__setitem__("rank", 99),
            "forged_owner": lambda x: x["root_matches"][0].__setitem__("owner", "OTHER"),
            "forged_source_sha": lambda x: x.__setitem__("fixed_source_sha256", "0"*64),
            "forged_phase": lambda x: x.__setitem__("source_phase_turns", ["0", "0"]),
            "forged_parameter": lambda x: x.__setitem__("source_parameter_id", "other"),
            "forged_bracket": lambda x: x["root_matches"][0].__setitem__(
                "strict_intersection_bracket", ["0", "1/64"]),
            "forged_crossing": lambda x: x["root_matches"][0].__setitem__(
                "crossing", "NEGATIVE_TO_POSITIVE"),
            "forged_signs": lambda x: x.__setitem__(
                "physical_signs", ["POSITIVE"]*3),
            "false_child_authority": lambda x: x.__setitem__(
                "historical_child_certified", True),
            "false_general_theorem": lambda x: x.__setitem__(
                "general_v27_v41_theorem", True),
            "false_pb007": lambda x: x.__setitem__("pb00701_certified", True),
            "false_mc_b": lambda x: x.__setitem__("mc_b_established", True),
            "false_native": lambda x: x.__setitem__(
                "native_brep_or_step_qualified", True),
            "false_production": lambda x: x.__setitem__(
                "production_authorized", True),
        }
        for name, change in changes.items():
            with self.subTest(name=name):
                forged = copy.deepcopy(report)
                change(forged)
                result = core.validate(forged)
                self.assertEqual(result["status"], "BLOCKED", result)

    def test_float_nonfinite_oversized_and_unknown_source_refuse(self):
        base = self.reports[list(core.CASES)[0]]
        for changed in (
            {"case_id": "unknown"},
            dict(base, untrusted_padding="x"*20000),
            dict(base, complete_open_roots=2.0),
            dict(base, complete_open_roots=float("nan")),
        ):
            result = core.validate(changed)
            self.assertIn(result["status"], ("BLOCKED", "RESOURCE_REFUSAL"))
            self.assertFalse(result["is_truth_value"])

    def test_unproved_rank_type_and_range_refuse(self):
        report = self.reports[list(core.CASES)[0]]
        for rank in (-1, 2, "0", True):
            self.assertEqual(core.compare(report, rank, report, 0)["status"], "BLOCKED")

    def test_source_pins_denominator_and_gate_stay_frozen(self):
        core.check_pins()
        auth = json.loads((core.ROOT / "handoffs/current-authority.json").read_text())
        domain = json.loads((core.ROOT /
            "research/machining-completeness/tasks/MC-002/domain-contract-v1.json").read_text())
        self.assertFalse(auth["production_authorized"])
        self.assertEqual(auth["capability_status"], "NOT_ESTABLISHED")
        self.assertEqual(len(domain["coverage_rule"]["required_operation_ids"]), 26)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("specify --contract and/or --self-test")
    if args.contract:
        for case, report in core.catalogue().items():
            print(json.dumps({
                "case": case, "status": report["status"],
                "intersection_brackets": [
                    root["strict_intersection_bracket"] for root in report["root_matches"]],
                "historical_child_certified": False, "mc_b_established": False,
            }, sort_keys=True))
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(DualImplicitRootTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == "__main__":
    main()
