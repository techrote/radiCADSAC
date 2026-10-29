#!/usr/bin/env python3
"""MC-038 exact source-prefix identity, uniqueness and adversarial controls."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
import unittest
from fractions import Fraction as Q

import pb00701_v27_prefix_root_identity as model


class PrefixRootResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = model.checked_result()
        cls.rows = model.original.custody()
        cls.lowerer = model.original.v27.exact_lowerer()

    def test_exact_original_restriction_identical_and_tails_diverge(self):
        signature, a, b = model.prove_restricted_equality(
            self.rows[model.LEFT_CASE], self.rows[model.RIGHT_CASE],
            self.lowerer)
        self.assertEqual(signature, self.result["exact_common_restriction"])
        self.assertEqual(signature["interval"], ["0", "1"])
        self.assertEqual(signature["phase_turns"], ["1/2", "-2/3"])
        self.assertEqual(signature["source_parameter"], "source-time-t")
        self.assertEqual(signature["owner"], model.original.v27.OWNER)
        self.assertEqual([x["harmonic"] for x in
                          signature["original_harmonic_coefficients"]], [0, 1, 2])
        expected = {
            0: (["5"], ["0"]),
            1: (["0"], ["2", "4"]),
            2: (["1/100"], ["0"]),
        }
        for h in signature["original_harmonic_coefficients"]:
            self.assertEqual(
                (h["cos_poly"], h["sin_poly"]), expected[h["harmonic"]])
        self.assertEqual(a["owner"], b["owner"])

    def test_both_first_span_proofs_unique_simple_crossing(self):
        for case in (model.LEFT_CASE, model.RIGHT_CASE):
            parts = model.original.original_spans(
                self.rows[case], self.lowerer)
            first_root = model.first_transverse_simple_root(parts[0])
            self.assertEqual(parts[0]["interval"], (Q(0), Q(1)))
            lo, hi = map(Q, first_root)
            self.assertLess(Q(0), lo)
            self.assertLess(lo, hi)
            self.assertLessEqual(hi, Q(1))

    def test_different_full_sources_share_only_first_root(self):
        result = self.result
        self.assertNotEqual(result["whole_source_sha256"][0],
                            result["whole_source_sha256"][1])
        self.assertEqual(result["status"],
                         "CHECKED_IDENTICAL_PREFIX_ROOT_AND_DIVERGENT_TAIL")
        self.assertEqual(result["first_root"]["relation"],
                         "SAME_UNIQUE_SOURCE_PARAMETER_ROOT")
        self.assertEqual(result["first_root"]["crossing"],
                         "POSITIVE_TO_NEGATIVE")
        self.assertEqual(result["first_root"]["multiplicity_in_each_span"], 1)
        self.assertEqual(
            result["divergent_second_roots"]["relation"],
            "LEFT_GREATER_THAN_RIGHT_SOURCE_PARAMETER_VALUE")
        self.assertFalse(result["first_root"]["same_physical_manufacturing_event_claimed"])
        self.assertFalse(result["divergent_second_roots"]["same_physical_manufacturing_event_claimed"])

    def test_strict_bracket_shared_only_after_source_expression_identity(self):
        lo, hi = map(Q, self.result["first_root"]["strict_rational_isolation"])
        self.assertLess(lo, hi)
        self.assertGreater(lo, Q(0))
        self.assertLessEqual(hi, Q(1))
        sources = model.dual.catalogue()
        for case in (model.LEFT_CASE, model.RIGHT_CASE):
            a,b = map(Q, sources[case]["root_matches"][0]["strict_intersection_bracket"])
            self.assertLessEqual(a, lo)
            self.assertLessEqual(hi, b)
        self.assertTrue(self.result["no_shared_physical_clock_or_journal_claimed"])

    def test_first_span_is_not_equal_after_control_or_phase_mutations(self):
        a, b = (copy.deepcopy(self.rows[case]) for case in
                (model.LEFT_CASE, model.RIGHT_CASE))
        mutations = [
            lambda x: x["spec"]["cos_splines"]["0"]["controls"].__setitem__(0,"6"),
            lambda x: x["spec"]["sin_splines"]["1"]["controls"].__setitem__(0,"3"),
            lambda x: x["spec"]["cos_splines"]["2"]["controls"].__setitem__(0,"1/50"),
            lambda x: x["spec"].__setitem__("phase_turn_offset","1/4"),
            lambda x: x["spec"].__setitem__("phase_turn_rate","-1/2"),
            lambda x: x["spec"].__setitem__("source_parameter_id","foreign-clock"),
            lambda x: x["spec"].__setitem__("parameter_lo","-1"),
            lambda x: x["spec"].__setitem__("parameter_hi","3"),
            lambda x: x["expected"]["observed"]["spans"][0].__setitem__(0,"FAKE_OWNER"),
        ]
        for idx, mutate in enumerate(mutations):
            with self.subTest(idx=idx):
                changed = copy.deepcopy(b)
                mutate(changed)
                with self.assertRaises((ValueError, model.Refusal)):
                    model.prove_restricted_equality(a, changed, self.lowerer)

    def test_mathematically_distinct_roots_can_have_overlapping_brackets(self):
        # Verified source identity is essential, not two coincidental intervals.
        left_zero, right_zero = Q(1,4), Q(7,4)
        first_interval, second_interval = (Q(0),Q(3,2)),(Q(1),Q(2))
        self.assertTrue(first_interval[0] < left_zero < first_interval[1])
        self.assertTrue(second_interval[0] < right_zero < second_interval[1])
        self.assertLess(max(first_interval[0],second_interval[0]),
                        min(first_interval[1],second_interval[1]))
        self.assertNotEqual(left_zero, right_zero)

    def test_cross_source_strict_tail_noncoincidence_is_replayed(self):
        pair = model.dual.catalogue()
        order = model.cross.compare(pair[model.LEFT_CASE],1,
                                    pair[model.RIGHT_CASE],1)
        self.assertEqual(order["status"],"CHECKED_STRICT_PARAMETER_ORDER")
        self.assertEqual(order["relation"],"GREATER")
        self.assertFalse(order["physical_temporal_sequence_claimed"])
        tail0 = model.dual.rational(
            pair[model.LEFT_CASE]["root_matches"][1]["strict_intersection_bracket"][0])
        tail100 = model.dual.rational(
            pair[model.RIGHT_CASE]["root_matches"][1]["strict_intersection_bracket"][1])
        self.assertGreaterEqual(tail0,tail100)

    def test_untrusted_claims_and_capability_mutations_refuse(self):
        mutations = {
            "false_shared_clock": lambda x: x.__setitem__(
                "no_shared_physical_clock_or_journal_claimed",False),
            "false_manufacturing_identity": lambda x: x["first_root"].__setitem__(
                "same_physical_manufacturing_event_claimed",True),
            "forged_source": lambda x: x["whole_source_sha256"].__setitem__(0,"0"*64),
            "forged_first_root": lambda x: x["first_root"].__setitem__(
                "strict_rational_isolation",["0","1/8"]),
            "false_root_coordinate": lambda x: x["first_root"].__setitem__(
                "coordinate_closed_form_claimed",True),
            "false_divergence": lambda x: x["divergent_second_roots"].__setitem__(
                "relation","SAME"),
            "altered_source_coefficients": lambda x: x[
                "exact_common_restriction"]["original_harmonic_coefficients"][0][
                    "cos_poly"].__setitem__(0,"6"),
            "forged_phase": lambda x: x["exact_common_restriction"].__setitem__(
                "phase_turns",["0","0"]),
            "global_theorem": lambda x: x.__setitem__(
                "general_v27_v41_composition_proved",True),
            "mc_b": lambda x: x.__setitem__("mc_b_established",True),
            "pb00701": lambda x: x.__setitem__("pb00701_certified",True),
            "production": lambda x: x.__setitem__("production_authorized",True),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                forged = copy.deepcopy(self.result)
                mutate(forged)
                refused = model.validate_claim(forged)
                self.assertEqual(refused["status"],"BLOCKED")
                self.assertIs(refused["is_truth_value"],False)

    def test_nonfinite_float_oversized_and_missing_reports_refuse(self):
        cases = [
            {"foo":"bar"},
            dict(self.result, untrusted_padding="a"*20000),
            dict(self.result, nonexact=0.125),
            dict(self.result, nonexact=float("nan")),
        ]
        for item in cases:
            outcome = model.validate_claim(item)
            self.assertIn(outcome["status"],("BLOCKED","RESOURCE_REFUSAL"))
            self.assertFalse(outcome["is_truth_value"])

    def test_source_blob_custody_and_no_promotion(self):
        model.pin_sources()
        self.assertEqual(model.validate_claim(self.result)["status"],
                         "CHECKED_IDENTICAL_PREFIX_ROOT_AND_DIVERGENT_TAIL")
        self.assertFalse(self.result["historical_child_certified"])
        self.assertFalse(self.result["general_v27_v41_composition_proved"])
        self.assertFalse(self.result["nontransverse_events_qualified"])
        self.assertFalse(self.result["native_brep_or_step_qualified"])
        self.assertFalse(self.result["production_authorized"])
        auth=json.loads((model.dual.ROOT/"handoffs/current-authority.json").read_text())
        self.assertEqual(auth["capability_status"],"NOT_ESTABLISHED")
        self.assertIs(auth["production_authorized"],False)
        domain=json.loads((model.dual.ROOT/
            "research/machining-completeness/tasks/MC-002/domain-contract-v1.json").read_text())
        self.assertEqual(len(domain["coverage_rule"]["required_operation_ids"]),26)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract",action="store_true")
    parser.add_argument("--self-test",action="store_true")
    opts=parser.parse_args()
    if not (opts.contract or opts.self_test):
        parser.error("supply --contract and/or --self-test")
    if opts.contract:
        result=model.checked_result()
        print(json.dumps({
            "status":result["status"],"cases":result["case_ids"],
            "common_restriction_sha256":result["common_restriction_sha256"],
            "first_root":result["first_root"],
            "divergent_second_roots":result["divergent_second_roots"],
            "mc_b_established":False,"production_authorized":False,
        },sort_keys=True))
    if opts.self_test:
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(PrefixRootResearchTests)
        tests=unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if tests.wasSuccessful() else 1)

if __name__=="__main__":
    main()
