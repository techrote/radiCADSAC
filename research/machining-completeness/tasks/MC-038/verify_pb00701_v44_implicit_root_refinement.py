#!/usr/bin/env python3
"""Positive, source-custody and adversarial tests for frozen V44 root refinement."""
from __future__ import annotations

import argparse
import copy
import json
import sys
import unittest
from fractions import Fraction as Q
from unittest.mock import patch

import pb00701_v44_implicit_root_refinement as core


class FrozenImplicitRootRefinementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        core.pins()
        cls.view = core.atlas.prove()

    def refine(self, steps=8):
        return core.refine(steps=steps, supplied_atlas=self.view)

    def test_zero_steps_preserves_complete_pinned_original_root(self):
        r = self.refine(0)
        self.assertEqual(r["status"], core.SUCCESS)
        self.assertEqual(r["frozen_case_id"], core.atlas.previous.CASE_ID)
        self.assertEqual(r["source_sha256"], core.atlas.SOURCE_SHA256)
        self.assertEqual(r["initial_strict_source_bracket"], ["9/16", "37/64"])
        self.assertEqual(r["final_strict_source_bracket"],
                         r["initial_strict_source_bracket"])
        self.assertEqual(r["initial_endpoint_signs"],
                         ["NEGATIVE", "POSITIVE"])
        self.assertEqual(r["refinement_trace"], [])
        self.assertTrue(r["unique_simple_root_strictly_inside_final_bracket"])

    def test_strict_midpoint_enclosures_and_exact_width_conservation(self):
        r = self.refine(8)
        lo, hi = map(Q, r["initial_strict_source_bracket"])
        width = hi - lo
        self.assertEqual(len(r["refinement_trace"]), 8)
        for i, item in enumerate(r["refinement_trace"], 1):
            with self.subTest(step=i):
                mid = Q(item["exact_original_source_midpoint"])
                self.assertEqual(item["step"], i)
                self.assertEqual(mid, (lo + hi)/2)
                bounds = list(map(Q, item["strict_rational_trig_enclosure"]))
                self.assertLessEqual(bounds[0], bounds[1])
                if item["strict_physical_value_sign"] == "NEGATIVE":
                    self.assertLess(bounds[1], 0)
                    self.assertEqual(item["root_containing_half"],
                                     "LEFT_BOUND_MOVED_RIGHT")
                    lo = mid
                else:
                    self.assertEqual(item["strict_physical_value_sign"],
                                     "POSITIVE")
                    self.assertGreater(bounds[0], 0)
                    self.assertEqual(item["root_containing_half"],
                                     "RIGHT_BOUND_MOVED_LEFT")
                    hi = mid
                self.assertEqual(item["new_strict_source_bracket"],
                                 [str(lo), str(hi)])
                self.assertFalse(item["midpoint_is_physical_zero"])
                self.assertEqual(hi - lo, width/(2**i))
        self.assertEqual(r["final_strict_source_bracket"], [str(lo), str(hi)])
        self.assertEqual(Q(r["final_bracket_width"]), width/256)
        self.assertLess(Q(r["final_bracket_width"]), Q(1, 1024))

    def test_refinement_reaches_twelve_source_rational_bisections(self):
        r = self.refine(12)
        self.assertEqual(r["status"], core.SUCCESS)
        self.assertEqual(len(r["refinement_trace"]), 12)
        self.assertEqual(Q(r["final_bracket_width"]), Q(1, 64*4096))
        self.assertLess(Q(r["final_bracket_width"]), Q(1, 100000))
        self.assertTrue(r["refinement_is_root_set_restriction_only"])
        self.assertFalse(r["implicit_root_declared_rational_or_algebraic"])

    def test_invalid_step_budgets_refuse_before_proof(self):
        for count in (-1, 13, True, 1.0, "8", None):
            with self.subTest(count=repr(count)):
                r = core.attempt(steps=count, supplied_atlas=self.view)
                self.assertEqual(r["status"], "BLOCKED")
                self.assertFalse(r["is_truth_value"])

    def test_source_replayed_atlas_rejects_plausible_sign_forgery(self):
        forged = copy.deepcopy(self.view)
        forged["proof_boundaries"][0]["physical_value_sign"] = "POSITIVE"
        result = core.attempt(steps=0, supplied_atlas=forged)
        self.assertEqual(result["status"], "BLOCKED", result)
        self.assertFalse(result["is_truth_value"])

    def test_pinned_producer_drift_refuses(self):
        with patch.object(core.atlas.previous, "git_blob",
                          return_value="f"*40):
            result = core.attempt(steps=0, supplied_atlas=self.view)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["is_truth_value"])

    def test_undecidable_midpoint_refuses_without_partial_success(self):
        # A genuine strict-sign inconclusive enclosure at any bisection
        # must NOT yield a shortened 'truth' bracket or infer root equality.
        class Uncertain:
            calls = 0
            def __call__(self, span, x):
                self.calls += 1
                if self.calls == 3:
                    raise core.ResourceRefusal(
                        "RATIONAL_SOURCE_MIDPOINT_SIGN_UNDECIDED")
                return ((-1, ["-2", "-1"]) if self.calls == 1
                        else (1, ["1", "2"]))
        with patch.object(core, "_strict_source_sign", new=Uncertain()):
            result = core.attempt(steps=1, supplied_atlas=self.view)
        self.assertEqual(result["status"], "RESOURCE_REFUSAL", result)
        self.assertFalse(result["is_truth_value"])
        self.assertFalse(result["historical_v54_admitted"])

    def test_forged_midpoint_label_fails_source_sign_invariant(self):
        # The midpoint may never be represented as an exact zero, and
        # cannot be assigned a sign inconsistent with both crossing sides.
        with patch.object(core, "_strict_source_sign",
                          side_effect=[(-1, ["-2", "-1"]),
                                       (1, ["1", "2"]), (0, ["-1", "1"])]):
            result = core.attempt(steps=1, supplied_atlas=self.view)
        self.assertEqual(result["status"], "BLOCKED", result)

    def test_report_replay_rejects_forged_refinement(self):
        good = self.refine(2)
        self.assertEqual(core.validate_report(
            good, steps=2, supplied_atlas=self.view), good)
        forged = copy.deepcopy(good)
        forged["refinement_trace"][0]["midpoint_is_physical_zero"] = True
        checked = core.validate_report(
            forged, steps=2, supplied_atlas=self.view)
        self.assertEqual(checked["status"], "BLOCKED")
        self.assertIn("FORGED_OR_INCONSISTENT", checked["reason"])

    def test_deeply_nested_submitted_report_is_typed_resource_nontruth(self):
        # The JSON encoder can exhaust its recursion budget before checking
        # serialized size; a hostile report must not leak that exception.
        malicious = []
        for _ in range(1100):
            malicious = [malicious]
        checked = core.validate_report(
            malicious, steps=0, supplied_atlas=self.view)
        self.assertEqual(checked["status"], "RESOURCE_REFUSAL", checked)
        self.assertFalse(checked["is_truth_value"])
        self.assertFalse(checked["historical_v54_admitted"])

    def test_oversized_and_excessive_node_reports_are_resource_nontruth(self):
        # Neither a huge scalar nor a very wide valid JSON list can silently
        # become an accepted proof report or an untyped decoder failure.
        examples = ("x" * (core.MAX_REPORT_BYTES + 1),
                    [0] * (core.MAX_REPORT_VISITED_NODES + 1))
        for report in examples:
            with self.subTest(kind=type(report).__name__):
                result = core.validate_report(
                    report, steps=0, supplied_atlas=self.view)
                self.assertEqual(result["status"], "RESOURCE_REFUSAL", result)
                self.assertFalse(result["is_truth_value"])

    def test_never_promotes_unproved_analytic_child_or_programme(self):
        r = self.refine(0)
        for flag in (
            "new_complete_root_isolation_theorem_claimed",
            "implicit_root_declared_rational_or_algebraic",
            "physical_proof_cuts_promoted_to_events",
            "algebraic_child_analytic_chart_constructed",
            "closed_child_derivative_theorem_proved",
            "historical_v41_v47_route_certified",
            "historical_v54_admitted", "pb00701_certified",
            "mc_b_established", "mc1_established",
            "native_material_or_step_qualified",
            "production_authorized",
        ):
            self.assertIs(r[flag], False, flag)
        self.assertEqual(r["historical_v54_disposition"], "BLOCKED")


def contract():
    result = core.attempt(steps=8)
    if result.get("status") != core.SUCCESS:
        raise RuntimeError("FROZEN_V44_REFINEMENT_NOT_ESTABLISHED: "
                           + repr(result))
    return {
        "status": result["status"],
        "source_sha256": result["source_sha256"],
        "initial": result["initial_strict_source_bracket"],
        "final": result["final_strict_source_bracket"],
        "steps": len(result["refinement_trace"]),
        "width": result["final_bracket_width"],
        "complete_original_source_root_count":
            result["complete_original_source_physical_root_count"],
        "historical_v54_admitted": result["historical_v54_admitted"],
        "production_authorized": result["production_authorized"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("specify --contract and/or --self-test")
    if args.contract:
        print(json.dumps(contract(), sort_keys=True))
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(
            FrozenImplicitRootRefinementTests)
        checked = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if checked.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
