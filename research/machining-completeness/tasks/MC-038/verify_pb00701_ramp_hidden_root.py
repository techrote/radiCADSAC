#!/usr/bin/env python3
"""Independent exact/adversarial checks for source-bound ramp hidden-root C."""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction as Q
import json
from pathlib import Path
import sys
import unittest

import pb00701_ramp_hidden_root as m

REPORT = Path(__file__).resolve().parent / "pb00701-ramp-hidden-root.json"


def validate_report(submitted):
    try:
        result = m.proof_c()
        if m.canonical(result) != m.canonical(submitted):
            raise m.Refusal("FORGED_OR_DRIFTED_RAMP_HIDDEN_ROOT_REPORT")
        return result
    except (m.Refusal, TypeError, ValueError, OverflowError, MemoryError) as exc:
        return {"status": "BLOCKED", "reason": str(exc), "is_truth": False,
                "pb00701_full_grammar_certified": False,
                "mc_b_established": False, "mc1_established": False,
                "production_authorized": False}


class ExactRampHiddenRootTests(unittest.TestCase):
    def test_original_source_is_pinned_unmodified_historical(self):
        c = m.census()
        self.assertEqual(c["frozen_source_count_before_after"], [121, 121])
        self.assertEqual(c["historical_route_refusals_before_after"], [20, 20])
        self.assertEqual(c["historical_missing_order_premises_before_after"], [30, 30])
        self.assertEqual(c["complete_source_specific_witnesses_before_after"], [50, 50])
        self.assertEqual(c["new_frozen_case_ids_resolved"], [])
        self.assertEqual(m.source_sha(m.variant_from_anchor("100")), m.ANCHOR_SHA)

    def test_exact_rational_mutation_and_original_geometry(self):
        source = m.variant_from_anchor("3/2")
        self.assertEqual(m.source_sha(source), m.MUTATION_SHA)
        self.assertEqual(source["phase_turn_rate"], "1/4")
        self.assertEqual(source["source_parameter_id"], "source-time-t")
        self.assertEqual(source["parameter_lo"], "0")
        self.assertEqual(source["parameter_hi"], "2")
        self.assertEqual(source["cos_splines"]["0"]["degree"], 1)
        self.assertEqual(source["cos_splines"]["0"]["knots"], ["0", "0", "1", "1", "2", "2"])
        self.assertEqual(source["cos_splines"]["0"]["controls"], ["0", "0", "0", "3/2"])
        self.assertEqual(source["cos_splines"]["1"],
                         {"degree": 0, "knots": ["0", "1", "2"], "controls": ["1", "1"]})
        self.assertEqual(source["sin_splines"], {})

    def test_historical_ramp_has_only_touching_source_knot(self):
        a = m.classify_slope("100")
        self.assertEqual(a["case"], "POSITIVE_RIGHT_NO_EXTRA_ROOT")
        self.assertEqual(a["source_knot_event"], "TOUCHING")
        self.assertEqual(a["distinct_closed_source_root_count"], 1)
        self.assertEqual(a["ordered_physical_open_signs"], ["POSITIVE", "POSITIVE"])
        self.assertEqual(a["exterior_values"], {"t=0": "1", "t=2": "99"})
        self.assertFalse(a["global_smooth_source_knot_multiplicity_claimed"])

    def test_positive_exteriors_hide_one_exact_interior_crossing(self):
        a = m.classify_slope("3/2")
        self.assertEqual(a["case"], "ONE_UNIQUE_SIMPLE_RIGHT_OPEN_CROSSING")
        self.assertEqual(a["source_knot_event"], "CROSSING")
        self.assertEqual(a["right_source_open_root_count"], 1)
        self.assertEqual(a["distinct_closed_source_root_count"], 2)
        self.assertEqual(a["source_knot_one_sided_orders"], [1, 1])
        self.assertEqual(a["ordered_physical_open_signs"],
                         ["POSITIVE", "NEGATIVE", "POSITIVE"])
        self.assertEqual(a["exterior_values"], {"t=0": "1", "t=2": "1/2"})
        self.assertEqual(a["interior_root_bracket_local_x"], ["1/4", "1/2"])

    def test_exact_pi_separation_for_derivative_sign(self):
        # Classical Archimedean 3 < pi < 22/7, not a numerical pi approximation
        # used as a truth oracle. All consequences here are rational.
        self.assertLess(Q(3, 2), Q(11, 7))
        self.assertLess(Q(3), Q(22, 7))
        self.assertGreater(Q(100), Q(11, 7))
        self.assertGreater(Q(13, 35), Q(1, 3))

    def test_exact_cyclotomic_negative_at_quarter(self):
        # sin(pi/8)^2=(2-sqrt(2))/4 > (3/8)^2 iff sqrt(2)<23/16.
        # Positivity and (23/16)^2>2 make the radical comparison exact.
        self.assertGreater(Q(23, 16)**2, Q(2))
        self.assertGreater(Q(23, 16), 0)
        self.assertGreater(Q(2)-Q(23, 16), Q(9, 16))

    def test_exact_cyclotomic_positive_at_half(self):
        # G(1/2)=3/4-sqrt(2)/2 > 0 from (3/4)^2>1/2.
        self.assertGreater(Q(3, 4)**2, Q(1, 2))

    def test_strict_convexity_implies_uniqueness_and_simple_event(self):
        # Mathematical lemma: G''(x)=(pi/2)^2 sin(pi x/2)>0, x in (0,1).
        # Together with G(0)=0, G'(0)<0 and G(1)>0 this implies exactly
        # one open simple root (a strict-convex differentiable return-to-zero).
        for a in ["100", "3/2", "1", "1/2", "0"]:
            result = m.classify_slope(a)
            self.assertEqual(result["source_knot_one_sided_orders"], [1, 1])
            self.assertFalse(result["global_smooth_source_knot_multiplicity_claimed"])
        self.assertEqual(m.classify_slope("3/2")["right_source_open_root_count"], 1)
        self.assertEqual(m.classify_slope("100")["right_source_open_root_count"], 0)

    def test_exact_right_endpoint_zero_not_swallowed(self):
        a = m.classify_slope("1")
        self.assertEqual(a["right_source_open_root_count"], 0)
        self.assertEqual(a["right_exterior_root_count"], 1)
        self.assertEqual(a["exterior_values"]["t=2"], "0")
        self.assertEqual(a["distinct_closed_source_root_count"], 2)
        self.assertEqual(a["ordered_physical_open_signs"], ["POSITIVE", "NEGATIVE"])

    def test_small_positive_and_zero_ramps_do_not_invent_open_root(self):
        for a in ["0", "1/2"]:
            result = m.classify_slope(a)
            self.assertEqual(result["right_source_open_root_count"], 0)
            self.assertEqual(result["source_knot_event"], "CROSSING")
            self.assertEqual(result["ordered_physical_open_signs"],
                             ["POSITIVE", "NEGATIVE"])

    def test_very_near_exterior_endpoint_root_is_not_omitted(self):
        delta = Q(1, 2**100)
        slope = str(1 + delta)
        a = m.classify_slope(slope)
        self.assertEqual(a["right_source_open_root_count"], 1)
        self.assertEqual(a["distinct_closed_source_root_count"], 2)
        self.assertEqual(a["exterior_values"]["t=2"], str(delta))
        self.assertIsNotNone(a["root_near_t2_bound"])
        # For x>=3/4: cos(pi*x/2)<=cos(3*pi/8)<2/5 and pi/2<11/7
        # so G'(x)>1-22/35=13/35>1/3.
        self.assertLess(Q(34, 25)**2, 2)  # sqrt(2)>34/25
        self.assertGreater(Q(1)-Q(22, 35), Q(1, 3))
        # At x=3/4, sin(3pi/8)>sqrt(3)/2>99/128 >=3A/4.
        self.assertLess(Q(99, 128)**2, Q(3, 4))
        self.assertLess(3 * delta, Q(1, 2**98))
        self.assertGreater(Q(2)-3*delta, Q(7, 4))

    def test_ramp_slopes_inside_unproved_pi_window_refuse(self):
        # 11/7 > pi/2 > 3/2: these coarse premises do NOT classify 31/20.
        with self.assertRaisesRegex(m.Refusal, "INSUFFICIENT_RATIONAL_PI_SEPARATION"):
            m.classify_slope("31/20")

    def test_negative_and_oversized_inputs_refuse_as_nontruth(self):
        for a in ["-1", "nan", "0.1", "01", "2/4", "1/0"]:
            with self.assertRaises(m.Refusal, msg=a):
                m.classify_slope(a)
        for a in [2, 1.5, True]:
            with self.assertRaises(m.Refusal):
                m.classify_slope(a)
        with self.assertRaisesRegex(m.Refusal, "RESOURCE_REFUSAL"):
            m.classify_slope(str(2**600))

    def test_identity_zero_source_is_not_implicitly_admitted(self):
        source = m.variant_from_anchor("100")
        source["cos_splines"]["1"]["controls"] = ["0", "0"]
        source["cos_splines"]["0"]["controls"] = ["0", "0", "0", "0"]
        with self.assertRaisesRegex(m.Refusal, "UNAUTHORIZED_OR_UNBOUND_ANCHOR"):
            m.variant_from_anchor("3/2", source)

    def test_phase_or_original_true_knot_mutations_are_rejected(self):
        source = m.variant_from_anchor("100")
        for change in [
            lambda s: s.__setitem__("phase_turn_rate", "1/8"),
            lambda s: s.__setitem__("source_parameter_id", "other"),
            lambda s: s["cos_splines"]["0"]["knots"].__setitem__(3, "3/2"),
            lambda s: s["cos_splines"]["1"]["controls"].__setitem__(0, "2"),
            lambda s: s.__setitem__("parameter_hi", "3")]:
            damaged = copy.deepcopy(source)
            change(damaged)
            with self.assertRaises(m.Refusal):
                m.variant_from_anchor("3/2", damaged)

    def test_census_mutations_refuse_without_changing_repo_files(self):
        original = json.loads(m.CORPUS.read_text())
        v2 = json.loads(m.REGISTRY.read_text())
        bad = copy.deepcopy(original)
        bad["cases"][0]["id"] = bad["cases"][1]["id"]
        with self.assertRaises(m.Refusal):
            m.census(bad, v2)
        bad = copy.deepcopy(v2)
        bad["source_cases"][0]["source_sha256"] = "0"*64
        with self.assertRaises(m.Refusal):
            m.census(original, bad)
        bad = copy.deepcopy(v2)
        bad["source_cases"][0]["historical_disposition_changed"] = True
        with self.assertRaises(m.Refusal):
            m.census(original, bad)

    def test_falsified_shortcut_cannot_be_promoted_to_general_pb007(self):
        claim = m.proof_c()
        self.assertTrue(claim["positive_exteriors_knot_zero_shortcut_falsified"])
        self.assertFalse(claim["pb00701_full_grammar_certified"])
        self.assertFalse(claim["mc_b_established"])
        self.assertFalse(claim["mc1_established"])
        self.assertFalse(claim["production_authorized"])
        self.assertEqual(claim["census"]["new_frozen_case_ids_resolved"], [])

    def test_saved_machine_evidence_forgery_refuses(self):
        report = json.loads(REPORT.read_text())
        self.assertEqual(validate_report(report), m.proof_c())
        for mutate in (
            lambda x: x.__setitem__("mc_b_established", True),
            lambda x: x["changed_control_exact_case"].__setitem__(
                "right_source_open_root_count", 0),
            lambda x: x["changed_control_exact_case"].__setitem__(
                "ordered_physical_open_signs", ["POSITIVE", "POSITIVE"]),
            lambda x: x["census"].__setitem__(
                "complete_source_specific_witnesses_before_after", [50, 51]),
            lambda x: x.__setitem__("historical_v54_accepted_route_changed", True)):
            forged = copy.deepcopy(report)
            mutate(forged)
            self.assertEqual(validate_report(forged)["status"], "BLOCKED")


def contract():
    report = json.loads(REPORT.read_text())
    checked = validate_report(report)
    if checked.get("status") == "BLOCKED":
        raise m.Refusal(checked["reason"])
    assert checked["census"]["new_frozen_case_ids_resolved"] == []
    return {
        "status": "EXACT_RAMP_POSITIVE_EXTERIOR_HIDDEN_ROOT_FALSIFIER",
        "evidence_class": "DETERMINISTIC_MODEL",
        "original_case": checked["historical_anchor_case_id"],
        "original_source_sha256": checked["historical_anchor_source_sha256"],
        "mutated_source_sha256": checked["prospective_slope_3_2_source_sha256"],
        "historical_original_roots": checked["original_exact_case"][
            "distinct_closed_source_root_count"],
        "mutated_source_roots": checked["changed_control_exact_case"][
            "distinct_closed_source_root_count"],
        "frozen_census_deltas": [0, 0, 0, 0],
        "pb00701_full_grammar_certified": False,
        "production_authorized": False
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("select --contract and/or --self-test")
    if args.contract:
        print(json.dumps(contract(), sort_keys=True))
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(ExactRampHiddenRootTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            sys.exit(1)


if __name__ == "__main__":
    main()
