#!/usr/bin/env python3
"""Deterministic falsifiers for MC-038 ordered MULTIPLE nontransverse roots."""
from __future__ import annotations

import argparse
import copy
import json
import unittest

import pb00701_multi_nontransverse as model

SOURCE = {
    "schema": model.single.SOURCE_SCHEMA,
    "source_parameter_id": "source-time-t",
    "source_interval": ["-5/8", "5/8"],
    "phase_turns": ["0", "1"],
    "harmonics": {
        "0": {"cos": ["0", "1"], "sin": ["0"]},
        "2": {"cos": ["0", "-1"], "sin": ["0"]},
    },
}
ROOTS = ["-1/2", "0", "1/2"]
GUARDS = [
    ["-65/128", "-63/128"],
    ["-1/128", "1/128"],
    ["63/128", "65/128"],
]


def checked():
    return model.attempt(SOURCE, ROOTS, GUARDS)


class Qualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = checked()
        assert cls.good.get("status") == (
            "COMPLETE_ORDERED_MULTIPLE_NONTRANSVERSE_ROOTS_RESEARCH"
        ), cls.good

    def test_01_full_ordered_multiple_nontransverse(self):
        p = self.good
        self.assertEqual(p["root_count"], 3)
        self.assertEqual(p["ordered_rational_roots"], ROOTS)
        self.assertEqual(p["ordered_multiplicities"], [2, 3, 2])
        self.assertEqual(p["ordered_event_kinds"],
                         ["TANGENCY", "CROSSING", "TANGENCY"])
        self.assertEqual(p["gap_signs"], [-1, -1, 1, 1])
        self.assertEqual(len(p["complete_complement_covers"]), 4)
        self.assertEqual(len(p["root_guard_witnesses"]), 3)
        self.assertTrue(all(x["cells"] >= 1 and
                            len(x["full_cell_certificate_sha256"]) == 64
                            for x in p["complete_complement_covers"]))
        self.assertLess(len(model.single.canonical(p)), model.MAX_CERT_BYTES)

    def test_02_report_recomputed_and_bound(self):
        self.assertEqual(model.validate_report(
            SOURCE, ROOTS, GUARDS, self.good), self.good)

    def test_03_forged_count_and_complete_cell_digest_refuse(self):
        bad = copy.deepcopy(self.good)
        bad["root_count"] = 2
        self.assertNotEqual(model.validate_report(
            SOURCE, ROOTS, GUARDS, bad)["status"],
            self.good["status"])
        bad = copy.deepcopy(self.good)
        bad["complete_complement_covers"][1][
            "full_cell_certificate_sha256"] = "0"*64
        self.assertNotEqual(model.validate_report(
            SOURCE, ROOTS, GUARDS, bad)["status"],
            self.good["status"])

    def test_04_missing_jet_and_unlisted_roots_refuse(self):
        bad = model.attempt(SOURCE, ROOTS[:1] + ROOTS[2:],
                            GUARDS[:1] + GUARDS[2:])
        self.assertNotEqual(bad["status"], self.good["status"])
        # The added pair of simple roots at 1/8 and 1/4 changes neither
        # the nominated 2,3,2 local multiplicities nor the gap-end signs.
        # Therefore only a COMPLETE gap proof can exclude those omissions.
        altered = copy.deepcopy(SOURCE)
        altered["harmonics"]["0"]["cos"] = [
            "0", "1/32", "-3/8", "1"]
        altered["harmonics"]["2"]["cos"] = [
            "0", "-1/32", "3/8", "-1"]
        extra = model.attempt(altered, ROOTS, GUARDS)
        self.assertNotEqual(extra["status"], self.good["status"],
                            "unlisted double simple roots falsely admitted")

    def test_05_forged_root_and_out_of_order_guards_refuse(self):
        fabricated_roots = ["-1/2", "0", "1/8", "1/2"]
        fabricated_guards = GUARDS[:2] + [
            ["31/256", "33/256"], GUARDS[2]]
        self.assertNotEqual(model.attempt(
            SOURCE, fabricated_roots, fabricated_guards)["status"],
            self.good["status"])
        swapped = [GUARDS[1], GUARDS[0], GUARDS[2]]
        self.assertNotEqual(model.attempt(
            SOURCE, ROOTS, swapped)["status"], self.good["status"])
        overlapping = copy.deepcopy(GUARDS)
        overlapping[1] = ["-3/8", "1/128"]
        self.assertNotEqual(model.attempt(
            SOURCE, ROOTS, overlapping)["status"], self.good["status"])

    def test_06_exhausted_budgets_are_nontruth(self):
        for budget in ({"max_nodes": 1}, {"max_depth": 0},
                       {"max_order": 2}):
            result = model.attempt(SOURCE, ROOTS, GUARDS, **budget)
            self.assertNotEqual(result["status"], self.good["status"])
            self.assertFalse(result["is_truth_value"])

    def test_07_source_and_phase_drift_refuse(self):
        for edit in ("phase", "amp", "identity"):
            altered = copy.deepcopy(SOURCE)
            if edit == "phase":
                altered["phase_turns"][0] = "1/7"
            elif edit == "amp":
                altered["harmonics"]["2"]["cos"][1] = "-2"
            else:
                altered["source_parameter_id"] = "made-up-param"
            self.assertNotEqual(model.attempt(
                altered, ROOTS, GUARDS)["status"], self.good["status"])

    def test_08_untrusted_source_candidate_mismatch(self):
        altered = copy.deepcopy(SOURCE)
        altered["harmonics"]["0"]["cos"][1] = "2"
        self.assertNotEqual(model.validate_report(
            altered, ROOTS, GUARDS, self.good)["status"],
            self.good["status"])

    def test_09_noncanonical_and_nonfinite_inputs(self):
        for bad_root in ("-2/4", 0.5, "NaN", "1" * 130):
            roots = ROOTS.copy()
            roots[0] = bad_root
            out = model.attempt(SOURCE, roots, GUARDS)
            self.assertNotEqual(out["status"], self.good["status"])
            self.assertFalse(out["is_truth_value"])

    def test_10_capability_and_order_mutations_refuse(self):
        for field, value in (
            ("mc_b_established", True), ("production_authorized", True),
            ("ordered_multiplicities", [2, 2, 2]),
            ("gap_signs", [-1, 1, 1, 1])):
            report = copy.deepcopy(self.good)
            report[field] = value
            self.assertNotEqual(model.validate_report(
                SOURCE, ROOTS, GUARDS, report)["status"],
                self.good["status"])

    def test_11_source_blob_and_gate_authority(self):
        model.pins()
        self.assertFalse(self.good["historical_v54_dispositions_changed"])
        self.assertFalse(self.good["pb00701_certified"])
        self.assertFalse(self.good["frozen_v27_v41_owner_certified"])
        self.assertFalse(self.good["mc1_established"])
        self.assertFalse(self.good["production_authorized"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.contract:
        result = checked()
        print(json.dumps({
            "status": result["status"],
            "source_sha256": result.get("source_sha256"),
            "roots": result.get("ordered_rational_roots"),
            "orders": result.get("ordered_multiplicities"),
            "gap_signs": result.get("gap_signs"),
            "cover_cells": [c["cells"] for c in
                result.get("complete_complement_covers", [])],
            "no_capability_promotion": not result.get("mc_b_established", True),
        }, sort_keys=True))
        if result["status"] != (
            "COMPLETE_ORDERED_MULTIPLE_NONTRANSVERSE_ROOTS_RESEARCH"):
            raise SystemExit(1)
    if args.self_test:
        unittest.main(argv=[__file__], exit=False, verbosity=2,
                      failfast=True)
    elif not args.contract:
        ap.error("provide --contract and/or --self-test")
