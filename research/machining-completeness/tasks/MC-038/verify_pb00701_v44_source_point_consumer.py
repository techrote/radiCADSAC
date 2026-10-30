#!/usr/bin/env python3
"""Source-bound positive and adversarial tests for V44 rational point consumer."""
from __future__ import annotations

import argparse
import copy
import json
import sys
import unittest
from fractions import Fraction as Q
from unittest.mock import patch

import pb00701_v44_source_point_consumer as core


class SourcePointConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        core.pins()
        cls.atlas = core.atlas.prove()

    def decide(self, x):
        return core.consume(core.request_for(x), self.atlas)

    def test_exact_frozen_source_endpoint_signs(self):
        for x, idx in (("0", 0), ("1", 4)):
            with self.subTest(x=x):
                r = self.decide(x)
                self.assertEqual(r["status"], core.SUCCESS)
                self.assertEqual(r["source_sha256"],
                                 core.atlas.SOURCE_SHA256)
                self.assertEqual(r["source_coordinate"], x)
                self.assertEqual(r["point_location"]["kind"],
                                 "ORIGINAL_SOURCE_ENDPOINT")
                self.assertEqual(r["point_location"]["boundary_index"], idx)
                self.assertEqual(r["exact_point_evidence"]["status"],
                                 "EXACT_NONZERO_RATIONAL_POINT")
                self.assertEqual(
                    r["physical_point_sign"],
                    self.atlas["proof_boundaries"][idx]["physical_value_sign"],
                )
                self.assertFalse(r["physical_point_is_zero"])

    def test_independent_rational_phase_point_against_proof_cell(self):
        # phase(-1/8 + t/16) at t=1/2 is -3/32: cyclotomic order 32.
        # It is NOT certified by guessing a sign from the root bracket.
        r = self.decide("1/2")
        self.assertEqual(r["status"], core.SUCCESS)
        self.assertEqual(r["source_coordinate"], "1/2")
        self.assertEqual(r["exact_point_evidence"]["phase_turn"], "-3/32")
        self.assertEqual(r["exact_point_evidence"]["cyclotomic_order"], 32)
        self.assertFalse(r["physical_point_is_zero"])
        self.assertIn(r["physical_point_sign"], ("NEGATIVE", "POSITIVE"))
        self.assertIn(r["point_location"]["kind"], (
            "ORIGINAL_SOURCE_OPEN_PROOF_CELL",
            "EXACT_NONPHYSICAL_SOURCE_PROOF_CUT",
        ))

    def test_frozen_proof_cut_equality_is_not_physical_event(self):
        rational = [
            (i, b) for i, b in enumerate(
                self.atlas["proof_boundaries"][1:-1], 1)
            if b["coordinate_descriptor"]["kind"] in
            ("RATIONAL_ROOT", "RATIONAL_PROOF_CUT")
        ]
        self.assertGreaterEqual(len(rational), 1)
        for idx, b in rational:
            with self.subTest(idx=idx):
                x = Q(b["coordinate_descriptor"]["local_value"])
                loc = core._locate_rational_point(self.atlas, x)
                self.assertEqual(loc["kind"],
                                 "EXACT_NONPHYSICAL_SOURCE_PROOF_CUT")
                self.assertEqual(loc["boundary_index"], idx)
                self.assertFalse(b["is_physical_zero"])

    def test_every_exact_location_respects_partition_order(self):
        self.assertEqual(
            core._locate_rational_point(self.atlas, Q(0))["boundary_index"], 0)
        self.assertEqual(
            core._locate_rational_point(self.atlas, Q(1))["boundary_index"], 4)
        for i, b in enumerate(self.atlas["proof_boundaries"][1:-1], 1):
            self.assertFalse(b["is_physical_zero"])
            if b["coordinate_descriptor"]["kind"] == "ISOLATED_REAL_ROOT":
                self.assertTrue(
                    b["coordinate_descriptor"]["local_isolating_interval"]
                )

    def test_noncanonical_and_outside_queries_fail_closed(self):
        malformed = ("00", "+1", "0/1", "2/4", "1.0", "0.5",
                     "1/0", "-1", "2", "1e-3", "1/" + "0"*130)
        for value in malformed:
            with self.subTest(value=value):
                r = core.attempt(core.request_for(value), self.atlas)
                self.assertNotEqual(r["status"], core.SUCCESS, r)
                self.assertFalse(r["is_truth_value"])
        for value in (1, Q(1, 2), 0.5, True, None):
            with self.subTest(type=str(type(value))):
                r = core.attempt(core.request_for(value), self.atlas)
                self.assertEqual(r["status"], "BLOCKED")
                self.assertFalse(r["is_truth_value"])

    def test_source_identity_and_request_capability_cannot_be_spoofed(self):
        changes = (
            ("source_sha256", "f"*64),
            ("source_parameter_id", "new-source"),
            ("frozen_case_id", "invented"),
            ("requested_capability", "ALGEBRAIC_CHILD_ANALYTIC_CHART"),
            ("requested_capability", "CLOSED_CHILD_DERIVATIVE"),
            ("requested_capability", "HISTORICAL_V54_ADMISSION"),
            ("schema", "unknown"),
        )
        for field, value in changes:
            with self.subTest(field=field, value=value):
                req = core.request_for("0")
                req[field] = value
                r = core.attempt(req, self.atlas)
                self.assertEqual(r["status"], "BLOCKED")
        req = core.request_for("0")
        req["caller_admission_override"] = True
        self.assertEqual(core.attempt(req, self.atlas)["status"], "BLOCKED")

    def test_atlas_source_replay_rejects_plausible_forgery(self):
        forged = copy.deepcopy(self.atlas)
        original = forged["source_proof_cells"][0]["root_free_constant_sign"]
        forged["source_proof_cells"][0]["root_free_constant_sign"] = (
            "POSITIVE" if original == "NEGATIVE" else "NEGATIVE"
        )
        r = core.attempt(core.request_for("0"), forged)
        self.assertEqual(r["status"], "BLOCKED", r)
        self.assertFalse(r["is_truth_value"])

    def test_independent_point_jet_cannot_be_replaced_by_fake_event(self):
        event = {
            "status": "EXACT_RATIONAL_POINT_EVENT",
            "source_binding_sha256": "forged",
            "coordinate": "0",
            "phase_turn": "-1/8",
            "exact_zero_decision": "ROOT_OF_UNITY_AND_PI_TRANSCENDENCE",
            "historical_v54_admitted": False,
            "complete_open_roots_claimed": False,
        }
        with patch.object(core.jets, "point", return_value=event):
            r = core.attempt(core.request_for("0"), self.atlas)
        self.assertEqual(r["status"], "BLOCKED", r)
        self.assertFalse(r["is_truth_value"])

    def test_oversized_cyclotomic_point_is_nontruth_not_sign_sampling(self):
        # t=1/128 has phase denominator 2048 (> pinned #298's 48).
        r = core.attempt(core.request_for("1/128"), self.atlas)
        self.assertEqual(r["status"], "RESOURCE_REFUSAL", r)
        self.assertFalse(r["is_truth_value"])
        self.assertFalse(r["historical_v54_admitted"])

    def test_source_pins_fail_closed_on_mutation(self):
        with patch.object(core.atlas.previous, "git_blob",
                          return_value="0"*40):
            r = core.attempt(core.request_for("0"), self.atlas)
        self.assertEqual(r["status"], "BLOCKED", r)
        self.assertFalse(r["is_truth_value"])

    def test_full_report_replay_and_forged_result(self):
        request = core.request_for("0")
        good = core.consume(request, self.atlas)
        self.assertEqual(core.validate_report(request, good, self.atlas),
                         good)
        forged = copy.deepcopy(good)
        forged["physical_point_sign"] = "POSITIVE" if (
            good["physical_point_sign"] == "NEGATIVE"
        ) else "NEGATIVE"
        checked = core.validate_report(request, forged, self.atlas)
        self.assertEqual(checked["status"], "BLOCKED")
        self.assertIn("FORGED_SOURCE_POINT_CONSUMER_REPORT",
                      checked["reason"])

    def test_no_historical_or_programme_promotion(self):
        r = self.decide("0")
        for field in (
            "algebraic_child_analytic_chart_constructed",
            "closed_child_derivative_theorem_proved",
            "historical_v41_v47_route_certified",
            "historical_v54_admitted", "pb00701_certified",
            "mc_b_established", "mc1_established",
            "native_material_or_step_qualified", "production_authorized",
            "proof_cuts_are_physical_events",
        ):
            self.assertIs(r[field], False, field)
        self.assertEqual(r["historical_v54_disposition"], "BLOCKED")
        self.assertTrue(r["source_coordinate_point_query_only"])


def contract():
    core.pins()
    r = core.attempt(core.request_for("0"))
    if r.get("status") != core.SUCCESS:
        raise RuntimeError("FROZEN_V44_SOURCE_POINT_CONSUMER_NOT_CERTIFIED: "
                           + repr(r))
    return {
        "status": r["status"],
        "source_sha256": r["source_sha256"],
        "source_coordinate": r["source_coordinate"],
        "point_status": r["exact_point_evidence"]["status"],
        "physical_point_sign": r["physical_point_sign"],
        "point_location": r["point_location"]["kind"],
        "source_replayed": True,
        "analytic_child_chart_constructed":
            r["algebraic_child_analytic_chart_constructed"],
        "historical_v54_admitted": r["historical_v54_admitted"],
        "production_authorized": r["production_authorized"],
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
            SourcePointConsumerTests
        )
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
