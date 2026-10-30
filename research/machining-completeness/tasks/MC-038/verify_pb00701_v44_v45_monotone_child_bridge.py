#!/usr/bin/env python3
"""Adversarial frozen V44 -> actual V45 algebraic split source-bridge contract."""
from __future__ import annotations

import argparse
import copy
import json
import sys
import unittest
from fractions import Fraction as Q
from unittest.mock import patch

import pb00701_v44_v45_monotone_child_bridge as core


class FrozenV44V45MonotoneBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.view = core.atlas.prove()
        cls.good = core.attempt(supplied_atlas=cls.view)
        if cls.good.get("status") != core.SUCCESS:
            raise RuntimeError("REAL_FROZEN_V45_SPLIT_NOT_PROVED: " +
                               repr(cls.good))

    def test_real_frozen_source_strict_single_cut_bridge(self):
        report = self.good
        self.assertEqual(report["status"], core.SUCCESS)
        self.assertEqual(report["evidence_class"], "DETERMINISTIC_MODEL")
        self.assertEqual(report["source_sha256"], core.atlas.SOURCE_SHA256)
        self.assertEqual(report["frozen_case_id"], core.previous.CASE_ID)
        self.assertEqual(report["original_source_interval"], ["0", "1"])
        self.assertEqual(report["alpha_identity_method"],
                         "EXACT_POLYNOMIAL_GCD_PLUS_STURM_COMMON_ROOT")
        self.assertIn(report["source_algebraic_boundary_nonzero_sign"],
                      ("NEGATIVE", "POSITIVE"))
        self.assertGreater(Q(report[
            "strict_rational_whole_source_physical_derivative_lower_bound"]), 0)

    def test_v45_real_field_is_not_rational_cut_surrogate(self):
        f = core._field(self.good["v45_field"])
        alpha = f.element([0, 1])
        self.assertEqual(alpha.sign(), 1)
        self.assertEqual((f.element(1) - alpha).sign(), 1)
        self.assertGreaterEqual(len(f.minimal), 3)
        self.assertNotEqual(f.element(0), alpha)
        self.assertNotEqual(f.element(1), alpha)

    def test_exact_source_algebraic_cut_identity(self):
        field = core._field(self.good["v45_field"])
        idx, boundary, method = core._exact_alpha_boundary(self.view, field)
        self.assertTrue(0 < idx < 4)
        self.assertEqual(boundary["boundary_id"],
                         self.good["source_algebraic_proof_boundary_id"])
        self.assertEqual(boundary["physical_value_sign"],
                         self.good["source_algebraic_boundary_nonzero_sign"])
        self.assertEqual(method, self.good["alpha_identity_method"])
        self.assertFalse(boundary["is_physical_zero"])

    def test_complete_child_root_partition_and_boundary_sign(self):
        report = self.good
        self.assertEqual(sum(report["complete_v45_split_open_root_counts"]), 1)
        self.assertEqual(sorted(report["complete_v45_split_open_root_counts"]),
                         [0, 1])
        expected = ([1, 0] if report[
            "source_algebraic_boundary_nonzero_sign"] == "POSITIVE"
                    else [0, 1])
        self.assertEqual(report["complete_v45_split_open_root_counts"],
                         expected)
        self.assertEqual([c["complete_open_physical_root_count"]
                          for c in report["v45_closed_children"]], expected)
        self.assertTrue(report["root_count_conserved_without_cut_event"])
        self.assertFalse(report["algebraic_cut_is_physical_event"])

    def test_exact_polynomial_and_phase_restriction_in_both_children(self):
        report = self.good
        self.assertEqual(len(report["v45_closed_children"]), 2)
        self.assertEqual([c["side"] for c in report["v45_closed_children"]],
                         ["left", "right"])
        f = core._field(report["v45_field"])
        left, right = report["v45_closed_children"]
        lo = left["parent_source_map"]
        hi = right["parent_source_map"]
        self.assertEqual(f.element(lo["offset"]), f.element(0))
        self.assertEqual(f.element(lo["width"]), f.element(hi["offset"]))
        self.assertEqual(f.element(lo["width"]) + f.element(hi["width"]),
                         f.element(1))
        for c in (left, right):
            self.assertEqual(f.element(c["parent_source_map"]["width"]).sign(),
                             1)
            self.assertTrue(c["exact_polynomial_roundtrip_replayed"])
            self.assertTrue(c["original_source_phase_affine_restriction_replayed"])
            self.assertTrue(c["closed_child_physical_derivative_strictly_positive"])
            self.assertFalse(c["new_algebraic_phase_trig_endpoint_evaluation"])

    def test_historic_v45_endpoint_event_authority_still_deferred(self):
        self.assertEqual(self.good[
            "historical_v45_irrational_phase_endpoint_authority"], "DEFERRED")
        for name in (
            "new_algebraic_child_trig_zero_solver_constructed",
            "general_v41_v47_child_event_route_certified",
            "historical_v54_admitted", "pb00701_certified",
            "mc_b_established", "mc1_established",
            "native_material_or_step_qualified", "production_authorized",
        ):
            self.assertIs(self.good[name], False, name)
        self.assertEqual(self.good["historical_v54_disposition"], "BLOCKED")

    def test_exact_replay_and_forged_root_allocation_refusal(self):
        self.assertEqual(core.validate_report(
            self.good, supplied_atlas=self.view), self.good)
        forged = copy.deepcopy(self.good)
        forged["complete_v45_split_open_root_counts"].reverse()
        checked = core.validate_report(forged, supplied_atlas=self.view)
        self.assertEqual(checked["status"], "BLOCKED")
        self.assertFalse(checked["is_truth_value"])

    def test_forged_field_embedding_and_source_map_refusal(self):
        for path, fake in (
            (("v45_field", "root_index_in_open_unit_interval"), 99),
            (("v45_closed_children", 0, "parent_source_map", "width"),
             ["1"]),
            (("source_sha256",), "0" * 64),
            (("alpha_identity_method",), "INTERVAL_OVERLAP_ONLY"),
            (("historical_v54_admitted",), True),
        ):
            forged = copy.deepcopy(self.good)
            target = forged
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = fake
            checked = core.validate_report(forged, supplied_atlas=self.view)
            self.assertEqual(checked["status"], "BLOCKED", path)
            self.assertFalse(checked["is_truth_value"])

    def test_forged_source_atlas_stays_nontruth(self):
        forged = copy.deepcopy(self.view)
        for b in forged["proof_boundaries"]:
            if b.get("coordinate_descriptor", {}).get("kind") == \
                    "ISOLATED_REAL_ROOT":
                b["physical_value_sign"] = (
                    "NEGATIVE" if b["physical_value_sign"] ==
                    "POSITIVE" else "POSITIVE"
                )
        result = core.attempt(supplied_atlas=forged)
        self.assertEqual(result["status"], "BLOCKED", result)
        self.assertFalse(result["is_truth_value"])

    def test_v45_source_pin_drift_stays_nontruth(self):
        with patch.object(core.previous, "git_blob", return_value="f" * 40):
            result = core.attempt(supplied_atlas=self.view)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["is_truth_value"])

    def test_missing_or_wrong_v45_source_representation_refuses(self):
        with patch.object(core.v45, "build_orientation_child_maps",
                          return_value={"status": "BLOCKED"}):
            result = core.attempt(supplied_atlas=self.view)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["is_truth_value"])

    def test_wrong_v45_child_width_refuses(self):
        original = core.v45.build_orientation_child_maps
        def corrupt(*args, **kwargs):
            report = original(*args, **kwargs)
            report["independent_single_cut_bisections"][0]["children"][0][
                "parent_source_map"]["width"] = ["-1"]
            return report
        with patch.object(core.v45, "build_orientation_child_maps",
                          side_effect=corrupt):
            result = core.attempt(supplied_atlas=self.view)
        self.assertEqual(result["status"], "BLOCKED", result)
        self.assertFalse(result["is_truth_value"])

    def test_derivative_proof_failure_never_becomes_child_truth(self):
        with patch.object(core.derivative, "prove",
                          side_effect=core.derivative.Refusal(
                              "GLOBAL_SOURCE_DERIVATIVE_NOT_ESTABLISHED")):
            result = core.attempt(supplied_atlas=self.view)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["is_truth_value"])

    def test_resource_refusal_never_becomes_capability(self):
        with patch.object(core, "_check_children",
                          side_effect=core.ResourceRefusal(
                              "V45_ALGEBRAIC_FIELD_RESOURCE_EXHAUSTED")):
            result = core.attempt(supplied_atlas=self.view)
        self.assertEqual(result["status"], "RESOURCE_REFUSAL")
        self.assertFalse(result["is_truth_value"])

    def test_deep_wide_cyclic_oversized_reports_are_resource_nontruth(self):
        nested = []
        for _ in range(1100):
            nested = [nested]
        cyclic = []
        cyclic.append(cyclic)
        for bad in (nested, cyclic, "x" * (core.MAX_REPORT_BYTES + 1),
                    [0] * (core.predecessor.MAX_REPORT_VISITED_NODES + 1)):
            with self.subTest(category=type(bad).__name__):
                result = core.validate_report(bad, supplied_atlas=self.view)
                self.assertEqual(result["status"], "RESOURCE_REFUSAL", result)
                self.assertFalse(result["is_truth_value"])


def contract():
    report = core.attempt()
    if report.get("status") != core.SUCCESS:
        raise RuntimeError(
            "FROZEN_V44_V45_BRIDGE_NOT_ESTABLISHED: " + repr(report)
        )
    return {
        "status": report["status"],
        "frozen_case_id": report["frozen_case_id"],
        "source_sha256": report["source_sha256"],
        "field": report["v45_field"],
        "alpha_identity_method": report["alpha_identity_method"],
        "alpha_nonzero_sign": report["source_algebraic_boundary_nonzero_sign"],
        "child_root_counts": report["complete_v45_split_open_root_counts"],
        "source_derivative_lower_bound": report[
            "strict_rational_whole_source_physical_derivative_lower_bound"],
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
            FrozenV44V45MonotoneBridgeTests
        )
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
