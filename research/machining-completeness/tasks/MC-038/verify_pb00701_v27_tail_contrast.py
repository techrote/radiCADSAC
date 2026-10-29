#!/usr/bin/env python3
"""Adversarial contract for MC-038 V27 original-source tail contrast.

No native geometry or historical corpus write. All successful source claims
are reconstructed from pinned originals and two complete checked root routes.
"""
from __future__ import annotations

import argparse
import copy
import json
import unittest
from fractions import Fraction as Q

import pb00701_v27_tail_contrast as model

class TailContrastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected = model.checked_result()

    def test_source_bound_positive_contrast_and_distinct_owners(self):
        result = self.expected
        self.assertEqual(result["status"], "CHECKED_STRICT_SOURCE_TAIL_CONTRAST")
        self.assertEqual(result["case_ids"], [model.LEFT, model.RIGHT])
        self.assertNotEqual(*result["whole_source_sha256"])
        self.assertEqual(result["source_parameter"], "source-time-t")
        self.assertEqual(result["phase_turns"], ["1/2", "-2/3"])
        self.assertEqual(result["original_second_span_owners"],
                         [model.original.v27.OWNER, model.original.v27.V19])
        w = result["strict_positive_difference_certificate"]
        self.assertEqual(w["difference_polynomial_t"], ["-100", "100"])
        self.assertEqual(w["difference_polynomial_u"], ["0", "100"])
        self.assertEqual(w["source_knot_order"], 1)
        self.assertEqual(w["positive_quotient_bernstein"], ["100"])
        self.assertTrue(result["root_noncoincidence_proved"])
        self.assertEqual(result["root_order_relation"], "RIGHT_LESS_THAN_LEFT")
        self.assertFalse(result["disjoint_brackets_needed_for_order_proof"])

    def test_all_trig_channels_cancel_except_harmonic_zero(self):
        channels = self.expected["all_original_harmonic_differences_checked"]
        self.assertEqual(len(channels), 6)
        self.assertEqual([(x["harmonic"], x["channel"]) for x in channels],
                         [(0, "cos"), (0, "sin"), (1, "cos"), (1, "sin"),
                          (2, "cos"), (2, "sin")])
        self.assertEqual(channels[0]["difference"], ["-100", "100"])
        self.assertTrue(all(x["difference"] == ["0"] for x in channels[1:]))

    def test_complete_source_proof_replay_and_claim_validation(self):
        self.assertEqual(model.validate_claim(self.expected), self.expected)
        self.assertEqual(model.attempt(), self.expected)
        self.assertEqual(self.expected["unique_second_root_strict_brackets"].__len__(), 2)
        for l, r in self.expected["unique_second_root_strict_brackets"]:
            self.assertLess(Q(1), Q(l))
            self.assertLess(Q(l), Q(r))
            self.assertLess(Q(r), Q(2))

    def test_exact_bernstein_nontrivial_positive_polynomial(self):
        # u*(1-u/4) is positive for 0<u<=1 although a power coefficient
        # is negative. Its degree-1 Bernstein quotient is (1,3/4).
        result = model.positive_contrast_on_unit_tail(
            ["-5/4", "3/2", "-1/4"])
        self.assertEqual(result["difference_polynomial_u"], ["0", "1", "-1/4"])
        self.assertEqual(result["positive_quotient_bernstein"], ["1", "3/4"])

    def test_polynomial_zero_sign_and_interior_root_refusals(self):
        for source in (["0"], ["100", "-100"],
                       ["3/2", "-5/2", "1"],
                       ["1"], ["-1", "1/2"]):
            with self.subTest(source=source), self.assertRaises(model.Refusal):
                model.positive_contrast_on_unit_tail(source)

    def test_noncanonical_and_resource_polynomial_refusal(self):
        for bad in ([1.0, 2], [True, 1], [0, 2**500],
                    ["0", "1/0"], ["0", "1"] * 9):
            with self.subTest(input=bad), self.assertRaises(model.Refusal):
                model.positive_contrast_on_unit_tail(bad)

    def test_original_phase_and_parameter_tamper_refused(self):
        index = model.original.custody()
        a, b = index[model.LEFT], index[model.RIGHT]
        for key, value in (("phase_turn_offset", "0"),
                           ("phase_turn_rate", "-1/2"),
                           ("source_parameter_id", "new-clock"),
                           ("parameter_hi", "3")):
            bad = copy.deepcopy(b)
            bad["spec"][key] = value
            with self.subTest(key=key), self.assertRaises(model.Refusal):
                model.source_tail_contrast(a, bad)

    def test_nonconstant_harmonic_and_owner_tamper_refused(self):
        index = model.original.custody()
        a, b = index[model.LEFT], index[model.RIGHT]
        bad = copy.deepcopy(b)
        bad["spec"]["cos_splines"]["2"]["controls"] = ["1/50", "1/50"]
        with self.assertRaises(model.Refusal):
            model.source_tail_contrast(a, bad)
        bad = copy.deepcopy(b)
        bad["expected"]["observed"]["spans"][1][0] = model.original.v27.OWNER
        with self.assertRaises(model.Refusal):
            model.source_tail_contrast(a, bad)

    def test_forged_order_source_and_physical_chronology_refused(self):
        changes = (
            ("root_order_relation", "LEFT_LESS_THAN_RIGHT"),
            ("root_noncoincidence_proved", False),
            ("disjoint_brackets_needed_for_order_proof", True),
            ("source_parameter", "shared-machine-clock"),
            ("common_physical_clock_or_event_claimed", True),
            ("pb00701_certified", True),
            ("mc_b_established", True),
            ("production_authorized", True),
        )
        for key, value in changes:
            bad = copy.deepcopy(self.expected)
            bad[key] = value
            with self.subTest(key=key):
                self.assertFalse(model.validate_claim(bad).get("is_truth_value", True))

    def test_forged_harmonics_bernstein_roots_and_gates_refused(self):
        mutations = (
            ("all_original_harmonic_differences_checked", 0, "difference", ["1"]),
            ("unique_second_root_strict_brackets", 0, 0, "0"),
        )
        for parent, index, key, value in mutations:
            bad = copy.deepcopy(self.expected)
            bad[parent][index][key] = value
            self.assertEqual(model.validate_claim(bad)["status"], "BLOCKED")
        bad = copy.deepcopy(self.expected)
        bad["strict_positive_difference_certificate"]["positive_quotient_bernstein"] = ["0"]
        self.assertEqual(model.validate_claim(bad)["status"], "BLOCKED")
        bad = copy.deepcopy(self.expected)
        bad["whole_source_sha256"][0] = "0" * 64
        self.assertEqual(model.validate_claim(bad)["status"], "BLOCKED")

    def test_resource_and_nonfinite_report_refusals(self):
        self.assertFalse(model.validate_claim({"forged": float("nan")})["is_truth_value"])
        self.assertEqual(model.validate_claim({"very_large": "x" * 20000})["status"],
                         "RESOURCE_REFUSAL")
        self.assertEqual(model.validate_claim([])["status"], "BLOCKED")

    def test_capability_boundary_remains_closed(self):
        for key in ("common_physical_clock_or_event_claimed",
                    "shared_manufacturing_journal_or_material_claimed",
                    "general_nontransverse_or_composition_proved",
                    "historical_v54_dispositions_changed",
                    "pb00701_certified", "mc_b_established", "mc1_established",
                    "native_brep_or_step_qualified", "production_authorized"):
            self.assertIs(self.expected[key], False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract and args.self_test):
        parser.error("required: --contract --self-test")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TailContrastTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    print(json.dumps({"status": "VERIFIED_CONDITIONAL_DETERMINISTIC_RESEARCH",
                      "tests_run": result.testsRun,
                      "tail_contrast": model.checked_result()},
                     sort_keys=True))
if __name__ == "__main__":
    main()
