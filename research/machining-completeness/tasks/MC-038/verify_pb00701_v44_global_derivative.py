#!/usr/bin/env python3
"""Exact source, derivative coverage, replay and adversarial frozen V44 tests."""
from __future__ import annotations

import argparse
import copy
import json
import sys
import unittest
from fractions import Fraction as Q
from unittest.mock import patch

import pb00701_v44_global_derivative as core


class FrozenV44GlobalDerivativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        core.pins()
        cls.view = core.atlas.prove()

    def certify(self, cells=16):
        return core.prove(cells=cells, supplied_atlas=self.view)

    def test_sixteen_cell_exact_whole_closed_source_derivative(self):
        report = self.certify()
        self.assertEqual(report["status"], core.SUCCESS)
        self.assertEqual(report["source_sha256"], core.atlas.SOURCE_SHA256)
        self.assertEqual(report["frozen_case_id"], core.previous.CASE_ID)
        self.assertEqual(report["original_source_interval"], ["0", "1"])
        self.assertEqual(report["original_affine_phase"],
                         {"offset": "-1/8", "rate": "1/16"})
        self.assertEqual(Q(report["universal_abs_second_derivative_upper_bound"]),
                         core.EXPECTED_M2)
        self.assertEqual(report["requested_dyadic_cells"], 16)
        self.assertTrue(report["whole_closed_source_derivative_strictly_positive"])
        self.assertGreater(Q(report[
            "whole_closed_source_strict_derivative_lower_bound"]), 0)
        self.assertEqual(report["certified_endpoint_physical_value_signs"],
                         ["NEGATIVE", "POSITIVE"])
        self.assertTrue(report[
            "exactly_one_simple_physical_root_from_IVT_and_global_monotonicity"])

    def test_exact_dyadic_cover_and_independently_checked_outward_rounding(self):
        report = self.certify()
        _, span, _, m2 = core._source_snapshot(self.view)
        self.assertEqual(len(report["closed_dyadic_cover"]), 16)
        lowers = []
        for i, cell in enumerate(report["closed_dyadic_cover"]):
            with self.subTest(i=i):
                left, right = map(Q, cell["closed_original_source_interval"])
                midpoint = Q(cell["exact_rational_midpoint"])
                self.assertEqual(cell["index"], i)
                self.assertEqual((left, right),
                                 (Q(i, 16), Q(i + 1, 16)))
                self.assertEqual(midpoint, (left + right)/2)
                real = span.evaluate(midpoint, first_derivative=True)
                rounded = tuple(map(Q, cell[
                    "outward_rounded_physical_derivative_enclosure"]))
                self.assertLessEqual(rounded[0], real[0])
                self.assertLessEqual(real[1], rounded[1])
                self.assertEqual(rounded[0],
                                 core._outward_dyadic(real[0], upward=False))
                self.assertEqual(rounded[1],
                                 core._outward_dyadic(real[1], upward=True))
                # Every reported dyadic rounding is exact to a 2^-32 grid.
                self.assertTrue(all(
                    (x * (1 << core.DYADIC_ENCLOSURE_BITS)).denominator == 1
                    for x in rounded))
                drift = m2 * (right-left)/2
                self.assertEqual(Q(cell["universal_second_derivative_drift"]),
                                 drift)
                lower = rounded[0] - drift
                self.assertEqual(
                    Q(cell["strict_physical_derivative_lower_bound"]), lower)
                self.assertGreater(lower, 0)
                self.assertIs(
                    cell["derivative_positive_everywhere_on_closed_cell"], True)
                lowers.append(lower)
        self.assertEqual(Q(report[
            "whole_closed_source_strict_derivative_lower_bound"]), min(lowers))

    def test_thirty_two_cells_remain_strictly_positive(self):
        report = self.certify(32)
        self.assertEqual(len(report["closed_dyadic_cover"]), 32)
        self.assertGreater(Q(report[
            "whole_closed_source_strict_derivative_lower_bound"]), 0)

    def test_eight_cells_are_insufficient_proof_not_counterexample(self):
        report = core.attempt(cells=8, supplied_atlas=self.view)
        self.assertEqual(report["status"], "BLOCKED", report)
        self.assertIn("POSITIVITY_NOT_ESTABLISHED", report["reason"])
        self.assertFalse(report["is_truth_value"])
        self.assertFalse(report["historical_v54_admitted"])

    def test_invalid_cell_count_refuses_without_truth(self):
        for count in (0, 7, 15, 17, 64, -1, True, 16.0, "16", None):
            with self.subTest(count=repr(count)):
                report = core.attempt(cells=count, supplied_atlas=self.view)
                self.assertEqual(report["status"], "BLOCKED")
                self.assertFalse(report["is_truth_value"])

    def test_exact_original_source_coefficients_and_independent_m2(self):
        _, span, _, m2 = core._source_snapshot(self.view)
        self.assertEqual(span.terms, core.EXPECTED_TERMS)
        self.assertEqual(span.m2, m2)
        self.assertEqual(m2, Q(335000000121, 19600000000))
        self.assertLess(core.trig.pi_bounds()[1], Q(22, 7))

    def test_four_exact_proof_children_inherit_strict_derivative(self):
        report = self.certify()
        children = report["original_source_proof_cut_children"]
        self.assertEqual(len(children), 4)
        self.assertEqual([x["physical_open_root_count"] for x in children],
                         [0, 1, 0, 0])
        self.assertTrue(report[
            "closed_proof_children_derivative_positive_by_restriction"])
        for i, child in enumerate(children):
            self.assertEqual(child["index"], i)
            self.assertEqual(child["left_boundary_id"], "b" + str(i))
            self.assertEqual(child["right_boundary_id"], "b" + str(i + 1))
            self.assertTrue(child[
                "normalized_affine_child_width_strictly_positive_by_exact_cut_order"])
            self.assertTrue(child[
                "strict_positive_child_derivative_inherited_by_chain_rule"])
            self.assertFalse(child["irrational_endpoint_trig_evaluation_required"])
            self.assertFalse(child["child_analytic_chart_constructed"])

    def test_source_replay_rejects_plausible_proof_cut_sign_forgery(self):
        forged = copy.deepcopy(self.view)
        forged["proof_boundaries"][1]["physical_value_sign"] = "POSITIVE"
        report = core.attempt(cells=16, supplied_atlas=forged)
        self.assertEqual(report["status"], "BLOCKED", report)
        self.assertFalse(report["is_truth_value"])

    def test_historical_source_pin_drift_refuses(self):
        with patch.object(core.previous, "git_blob", return_value="f"*40):
            report = core.attempt(cells=16, supplied_atlas=self.view)
        self.assertEqual(report["status"], "BLOCKED")
        self.assertFalse(report["is_truth_value"])

    def test_reject_wrong_source_polynomials_even_if_proof_replayed(self):
        with patch.object(core, "EXPECTED_TERMS",
                          {1: ((Q(1),), (Q(0),))}):
            report = core.attempt(cells=16, supplied_atlas=self.view)
        self.assertEqual(report["status"], "BLOCKED", report)
        self.assertIn("COEFFICIENT_DRIFT", report["reason"])

    def test_derivative_margin_failure_does_not_create_physical_truth(self):
        with patch.object(core, "_cell",
                          side_effect=core.Refusal(
                              "CLOSED_DYADIC_CELL_DERIVATIVE_POSITIVITY_NOT_ESTABLISHED")):
            report = core.attempt(cells=16, supplied_atlas=self.view)
        self.assertEqual(report["status"], "BLOCKED")
        self.assertFalse(report["is_truth_value"])

    def test_resource_refusal_is_explicit_nontruth(self):
        with patch.object(core, "_cell",
                          side_effect=core.ResourceRefusal(
                              "EXACT_DERIVATIVE_ENCLOSURE_RESOURCE_EXHAUSTED")):
            report = core.attempt(cells=16, supplied_atlas=self.view)
        self.assertEqual(report["status"], "RESOURCE_REFUSAL")
        self.assertFalse(report["is_truth_value"])

    def test_report_replay_accepts_exact_and_rejects_margin_forgery(self):
        good = self.certify()
        self.assertEqual(core.validate_report(
            good, cells=16, supplied_atlas=self.view), good)
        forged = copy.deepcopy(good)
        forged["closed_dyadic_cover"][0][
            "strict_physical_derivative_lower_bound"] = "1000"
        checked = core.validate_report(
            forged, cells=16, supplied_atlas=self.view)
        self.assertEqual(checked["status"], "BLOCKED")
        self.assertIn("FORGED_OR_INCONSISTENT", checked["reason"])

    def test_noncanonical_and_deep_reports_are_never_accepted(self):
        nested = []
        for _ in range(1100):
            nested = [nested]
        for submitted in (
            nested,
            "x" * (core.MAX_REPORT_BYTES + 1),
            [0] * (core.predecessor.MAX_REPORT_VISITED_NODES + 1),
        ):
            checked = core.validate_report(
                submitted, cells=16, supplied_atlas=self.view)
            self.assertEqual(checked["status"], "RESOURCE_REFUSAL")
            self.assertFalse(checked["is_truth_value"])
        cyclic = []
        cyclic.append(cyclic)
        checked = core.validate_report(
            cyclic, cells=16, supplied_atlas=self.view)
        self.assertEqual(checked["status"], "RESOURCE_REFUSAL")

    def test_no_historical_route_or_programme_promotion(self):
        report = self.certify()
        self.assertEqual(report["historical_v54_disposition"], "BLOCKED")
        self.assertTrue(report["whole_closed_source_derivative_strictly_positive"])
        for flag in (
            "proof_cuts_are_physical_events",
            "general_algebraic_child_analytic_chart_constructed",
            "general_v41_v47_child_derivative_interface_certified",
            "historical_v41_v47_route_certified",
            "historical_v54_admitted", "pb00701_certified",
            "mc_b_established", "mc1_established",
            "native_material_or_step_qualified", "production_authorized",
        ):
            self.assertIs(report[flag], False, flag)


def contract():
    report = core.attempt(cells=16)
    if report.get("status") != core.SUCCESS:
        raise RuntimeError(
            "FROZEN_V44_WHOLE_SOURCE_DERIVATIVE_NOT_ESTABLISHED: "
            + repr(report))
    return {
        "status": report["status"],
        "frozen_case_id": report["frozen_case_id"],
        "source_sha256": report["source_sha256"],
        "dyadic_cells": report["requested_dyadic_cells"],
        "universal_m2": report["universal_abs_second_derivative_upper_bound"],
        "strict_global_lower_bound":
            report["whole_closed_source_strict_derivative_lower_bound"],
        "closed_proof_children": len(report["original_source_proof_cut_children"]),
        "whole_source_derivative_positive":
            report["whole_closed_source_derivative_strictly_positive"],
        "historical_v54_admitted": report["historical_v54_admitted"],
        "production_authorized": report["production_authorized"],
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
            FrozenV44GlobalDerivativeTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
