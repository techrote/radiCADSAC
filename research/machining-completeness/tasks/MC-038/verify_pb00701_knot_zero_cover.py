#!/usr/bin/env python3
"""Adversarial verification for complete two-span source-knot zero research."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
import unittest

import pb00701_knot_zero_cover as core
import pb00701_rational_phase_point as point


def source(left, right, harmonics, *, offset="0", rate="1"):
    return {
        "schema": "radicadsac-pb00701-exact-original-trig-span/1.0",
        "source_parameter_id": "source-time-t",
        "source_interval": [left, right],
        "phase_turns": [offset, rate],
        "harmonics": harmonics,
    }


# F_L(s)=(s-1)^2*(1+sin(2*pi*s)/2^20), s in [0,1].
LEFT = source("0", "1", {
    "0": {"cos": ["1", "-2", "1"], "sin": ["0"]},
    "1": {"cos": ["0"],
          "sin": ["1/1048576", "-1/524288", "1/1048576"]},
})

# F_R(s)=-(s-1)^3*(1+sin(2*pi*s)/2^20), s in [1,2].
# The physical knot signs are POSITIVE -> NEGATIVE: a crossing even though
# the left/right smooth orders differ (2 vs 3).
RIGHT_CROSS = source("1", "2", {
    "0": {"cos": ["1", "-3", "3", "-1"], "sin": ["0"]},
    "1": {"cos": ["0"],
          "sin": ["1/1048576", "-3/1048576",
                  "3/1048576", "-1/1048576"]},
})

# Sign-reversed right span: same zero and order, but POSITIVE -> POSITIVE.
RIGHT_TOUCH = source("1", "2", {
    "0": {"cos": ["-1", "3", "-3", "1"], "sin": ["0"]},
    "1": {"cos": ["0"],
          "sin": ["-1/1048576", "3/1048576",
                  "-3/1048576", "1/1048576"]},
})

# Same order-2 zero at s=1 and positive endpoint signs, but two omitted
# tangencies at s=1/4 and s=3/4. Endpoint signs alone cannot prove completeness.
EXTRA_LEFT_ROOTS = source("0", "1", {
    "0": {"cos": ["1", "-2", "1"], "sin": ["0"]},
    "2": {"cos": ["1", "-2", "1"], "sin": ["0"]},
})

ZERO_LEFT = source("0", "1", {"0": {"cos": ["0"], "sin": ["0"]}})
ZERO_RIGHT = source("1", "2", {"0": {"cos": ["0"], "sin": ["0"]}})


class KnotZeroCoverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cross = core.prove(LEFT, RIGHT_CROSS, "1", ["7/8", "9/8"])
        cls.touch = core.prove(LEFT, RIGHT_TOUCH, "1", ["7/8", "9/8"])

    def test_crossing_knot_is_one_physical_zero_with_separate_orders(self):
        r = self.cross
        self.assertEqual(r["status"],
                         "COMPLETE_SINGLE_SOURCE_KNOT_ZERO_UNION_RESEARCH")
        self.assertEqual((r["left_one_sided_order"],
                          r["right_one_sided_order"]), (2, 3))
        self.assertEqual((r["physical_left_sign"],
                          r["physical_right_sign"]), (1, -1))
        self.assertEqual(r["event_kind"], "CROSSING")
        self.assertEqual(r["physical_zero_events"], 1)
        self.assertTrue(r["source_knot_counted_once"])
        self.assertFalse(r["global_smooth_multiplicity_claimed"])
        self.assertTrue(r["complete_other_source_roots_excluded"])

    def test_sign_reversed_right_span_is_touching_not_crossing(self):
        r = self.touch
        self.assertEqual((r["left_one_sided_order"],
                          r["right_one_sided_order"]), (2, 3))
        self.assertEqual((r["physical_left_sign"],
                          r["physical_right_sign"]), (1, 1))
        self.assertEqual(r["event_kind"], "TOUCHING")
        self.assertEqual(r["physical_zero_events"], 1)

    def test_two_one_sided_guards_and_outer_covers_tile_union(self):
        for r in (self.cross, self.touch):
            self.assertEqual(r["left_source_interval"], ["0", "1"])
            self.assertEqual(r["right_source_interval"], ["1", "2"])
            self.assertEqual(r["left_zero_free_outer_cover"]["source_interval"],
                             ["0", "7/8"])
            self.assertEqual(r["left_knot_guard"]["guard_interval"],
                             ["7/8", "1"])
            self.assertEqual(r["right_knot_guard"]["guard_interval"],
                             ["1", "9/8"])
            self.assertEqual(r["right_zero_free_outer_cover"]["source_interval"],
                             ["9/8", "2"])
            self.assertGreater(r["left_zero_free_outer_cover"]["cells"], 0)
            self.assertGreater(r["right_zero_free_outer_cover"]["cells"], 0)
            self.assertLessEqual(r["combined_outer_cover_nodes"], 20000)
            self.assertEqual(
                r["left_zero_free_outer_cover"]["strict_sign"],
                r["physical_left_sign"])
            self.assertEqual(
                r["right_zero_free_outer_cover"]["strict_sign"],
                r["physical_right_sign"])
            self.assertEqual(
                len(r["left_zero_free_outer_cover"]
                    ["full_cell_certificate_sha256"]), 64)
            self.assertEqual(
                len(r["right_zero_free_outer_cover"]
                    ["full_cell_certificate_sha256"]), 64)

    def test_exact_knot_composition_is_source_bound_and_replayable(self):
        checked = core.validate_report(
            LEFT, RIGHT_CROSS, "1", ["7/8", "9/8"], self.cross)
        self.assertEqual(checked, self.cross)
        self.assertEqual(
            self.cross["left_source_record_sha256"],
            hashlib.sha256(core.canonical(LEFT).encode("ascii")).hexdigest())
        self.assertEqual(
            self.cross["right_source_record_sha256"],
            hashlib.sha256(core.canonical(RIGHT_CROSS).encode("ascii")).hexdigest())
        self.assertEqual(
            self.cross["left_source_binding_sha256"],
            point.span_binding(core.guarded.source_span(LEFT)))
        self.assertEqual(
            self.cross["right_source_binding_sha256"],
            point.span_binding(core.guarded.source_span(RIGHT_CROSS)))
        self.assertFalse(self.cross["historical_v54_admitted"])
        self.assertFalse(self.cross["pb00701_certified"])
        self.assertFalse(self.cross["mc_b_established"])
        self.assertFalse(self.cross["production_authorized"])

    def test_two_omitted_remote_tangencies_with_same_endpoint_sign_refuse(self):
        refused = core.attempt(
            EXTRA_LEFT_ROOTS, RIGHT_CROSS, "1", ["7/8", "9/8"])
        self.assertEqual(refused["status"], "RESOURCE_REFUSAL", refused)
        self.assertIn("OUTER_ROOT_FREE_COVER_DEPTH_EXHAUSTED",
                      refused["reason"])
        self.assertFalse(refused["is_truth_value"])

    def test_discontinuous_phase_mismatched_and_coordinate_mismatched_knots_refuse(self):
        discontinuous = copy.deepcopy(RIGHT_CROSS)
        discontinuous["harmonics"]["0"]["cos"][0] = "2"
        a = core.attempt(LEFT, discontinuous, "1", ["7/8", "9/8"])
        self.assertEqual(a["status"], "BLOCKED")
        self.assertIn("DISCONTINUOUS_SOURCE_KNOT", a["reason"])

        phase = copy.deepcopy(RIGHT_CROSS)
        phase["phase_turns"][1] = "1/2"
        b = core.attempt(LEFT, phase, "1", ["7/8", "9/8"])
        self.assertEqual(b["status"], "BLOCKED")
        self.assertIn("SOURCE_KNOT_PHASE_OR_COORDINATE_MISMATCH", b["reason"])

        coordinate = copy.deepcopy(RIGHT_CROSS)
        coordinate["source_interval"][0] = "3/2"
        c = core.attempt(LEFT, coordinate, "1", ["7/8", "13/8"])
        self.assertEqual(c["status"], "BLOCKED")
        self.assertIn("SOURCE_KNOT_PHASE_OR_COORDINATE_MISMATCH", c["reason"])

    def test_nonzero_and_identity_zero_knots_are_not_promoted(self):
        left = copy.deepcopy(LEFT)
        right = copy.deepcopy(RIGHT_CROSS)
        left["harmonics"]["0"]["cos"][0] = "2"
        right["harmonics"]["0"]["cos"][0] = "2"
        nonzero = core.attempt(left, right, "1", ["7/8", "9/8"])
        self.assertEqual(nonzero["status"], "BLOCKED")
        self.assertIn("EXACT_ZERO_SOURCE_KNOT_NOT_ESTABLISHED",
                      nonzero["reason"])

        identity = core.attempt(
            ZERO_LEFT, ZERO_RIGHT, "1", ["7/8", "9/8"], max_order=4)
        self.assertEqual(identity["status"], "RESOURCE_REFUSAL")
        self.assertIn("JET_ORDER_RESOURCE_LIMIT_UNRESOLVED",
                      identity["reason"])
        self.assertFalse(identity["is_truth_value"])

    def test_resource_exhaustion_is_nontruth(self):
        for options in (
            {"max_nodes": 2},
            {"max_depth": 0},
            {"max_order": 2},
        ):
            refused = core.attempt(
                LEFT, RIGHT_CROSS, "1", ["7/8", "9/8"], **options)
            self.assertEqual(refused["status"], "RESOURCE_REFUSAL", refused)
            self.assertFalse(refused["is_truth_value"])

    def test_noncanonical_guard_and_source_parameter_refuse(self):
        bad_source = copy.deepcopy(RIGHT_CROSS)
        bad_source["source_parameter_id"] = "other-coordinate"
        cases = (
            (LEFT, RIGHT_CROSS, "1.0", ["7/8", "9/8"]),
            (LEFT, RIGHT_CROSS, 1.0, ["7/8", "9/8"]),
            (LEFT, RIGHT_CROSS, "1", ["0.875", "9/8"]),
            (LEFT, RIGHT_CROSS, "1", ["7/8", 1.125]),
            (LEFT, bad_source, "1", ["7/8", "9/8"]),
        )
        for left, right, knot, guards in cases:
            refused = core.attempt(left, right, knot, guards)
            self.assertEqual(refused["status"], "BLOCKED", refused)
            self.assertFalse(refused["is_truth_value"])

    def test_source_mutations_cannot_reuse_report(self):
        mutations = (
            lambda l, r: l["harmonics"]["1"]["sin"].__setitem__(0, "1/524288"),
            lambda l, r: r["harmonics"]["1"]["sin"].__setitem__(1, "-1/262144"),
            lambda l, r: r["phase_turns"].__setitem__(0, "1/4"),
            lambda l, r: r["source_interval"].__setitem__(1, "3"),
        )
        for mutate in mutations:
            left, right = copy.deepcopy(LEFT), copy.deepcopy(RIGHT_CROSS)
            mutate(left, right)
            checked = core.validate_report(
                left, right, "1", ["7/8", "9/8"], self.cross)
            self.assertNotEqual(
                checked.get("status"),
                "COMPLETE_SINGLE_SOURCE_KNOT_ZERO_UNION_RESEARCH")
            self.assertFalse(checked["is_truth_value"])

    def test_forged_reports_and_capability_elevation_rejected(self):
        mutations = (
            lambda x: x.__setitem__("physical_zero_events", 2),
            lambda x: x.__setitem__("source_knot_counted_once", False),
            lambda x: x.__setitem__("global_smooth_multiplicity_claimed", True),
            lambda x: x.__setitem__("left_one_sided_order", 3),
            lambda x: x.__setitem__("physical_right_sign", 1),
            lambda x: x["left_zero_free_outer_cover"].__setitem__(
                "full_cell_certificate_sha256", "0"*64),
            lambda x: x.__setitem__("complete_other_source_roots_excluded", False),
            lambda x: x.__setitem__("historical_v54_admitted", True),
            lambda x: x.__setitem__("pb00701_certified", True),
            lambda x: x.__setitem__("mc_b_established", True),
            lambda x: x.__setitem__("native_brep_or_step_qualified", True),
            lambda x: x.__setitem__("production_authorized", True),
        )
        for mutate in mutations:
            forged = copy.deepcopy(self.cross)
            mutate(forged)
            checked = core.validate_report(
                LEFT, RIGHT_CROSS, "1", ["7/8", "9/8"], forged)
            self.assertEqual(checked["status"], "BLOCKED", checked)
            self.assertFalse(checked["is_truth_value"])

    def test_oversized_untrusted_report_refuses(self):
        forged = copy.deepcopy(self.cross)
        forged["junk"] = "x" * (core.MAX_CERT_BYTES + 1)
        checked = core.validate_report(
            LEFT, RIGHT_CROSS, "1", ["7/8", "9/8"], forged)
        self.assertEqual(checked["status"], "RESOURCE_REFUSAL")
        self.assertFalse(checked["is_truth_value"])

    def test_full_custody_and_26_operation_denominator(self):
        core.pins()
        authority = json.loads(
            (core.ROOT / "handoffs/current-authority.json").read_text())
        domain = json.loads(
            (core.ROOT /
             "research/machining-completeness/tasks/MC-002/domain-contract-v1.json")
            .read_text())
        self.assertFalse(authority["production_authorized"])
        self.assertEqual(authority["capability_status"], "NOT_ESTABLISHED")
        self.assertEqual(
            len(domain["coverage_rule"]["required_operation_ids"]), 26)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("specify --contract and/or --self-test")
    if args.contract:
        for label, right in (
            ("order2_order3_crossing", RIGHT_CROSS),
            ("order2_order3_touching", RIGHT_TOUCH),
        ):
            report = core.prove(LEFT, right, "1", ["7/8", "9/8"])
            print(json.dumps({
                "label": label,
                "status": report["status"],
                "left_source_sha256": report["left_source_record_sha256"],
                "right_source_sha256": report["right_source_record_sha256"],
                "knot": report["knot_coordinate"],
                "orders": [report["left_one_sided_order"],
                           report["right_one_sided_order"]],
                "physical_signs": [report["physical_left_sign"],
                                   report["physical_right_sign"]],
                "event_kind": report["event_kind"],
                "physical_zero_events": report["physical_zero_events"],
                "outer_cell_counts": [
                    report["left_zero_free_outer_cover"]["cells"],
                    report["right_zero_free_outer_cover"]["cells"],
                ],
                "pb00701_certified": False,
                "production_authorized": False,
            }, sort_keys=True))
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(
            KnotZeroCoverTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
