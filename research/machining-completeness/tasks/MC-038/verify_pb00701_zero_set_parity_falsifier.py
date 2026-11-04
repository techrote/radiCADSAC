#!/usr/bin/env python3
"""Independent exact/adversarial checks for zero-set-only sign-transfer falsifier."""
from __future__ import annotations
import argparse
import copy
import json
import sys
import unittest
from fractions import Fraction as Q
from pathlib import Path
import pb00701_zero_set_parity_falsifier as core

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "pb00701-zero-set-parity-falsifier.json"


def independent_laurent(m):
    """Repeated exact convolution, separate from the model's binomial formula."""
    coefficients = {0: Q(1)}
    for _ in range(m):
        nxt = {}
        for exp, c in coefficients.items():
            for sign in (-1, 1):
                nxt[exp + sign] = nxt.get(exp + sign, Q(0)) + c / 2
        coefficients = nxt
    return coefficients


def projection(report):
    return {
        "schema": report["schema"],
        "evidence_class": report["evidence_class"],
        "accepted_bounded_outcome": "C_NEGATIVE_SOURCE_BOUND_ZERO_SET_ONLY_TRANSFER",
        "historical_case_id": report["historical"]["frozen_reference_id"],
        "historical_source_sha256": report["historical"]["frozen_reference_source_sha256"],
        "before": {
            "frozen_sources": report["before"]["frozen_sources"],
            "historical_route_refusals": report["before"]["historical_route_refusals"],
            "historical_missing_ordered_premises":
                report["before"]["historical_missing_ordered_premises"],
            "supplemental_complete_original_sources":
                report["before"]["supplemental_complete_original_sources"],
        },
        "after": {
            "frozen_sources": report["after"]["frozen_sources"],
            "historical_route_refusals": report["after"]["historical_route_refusals"],
            "historical_missing_ordered_premises":
                report["after"]["historical_missing_ordered_premises"],
            "supplemental_complete_original_sources":
                report["after"]["supplemental_complete_original_sources"],
        },
        "delta": report["historical_delta"],
        "same_closed_source_zero_set_for_all_variants": ["1"],
        "orders": [r["left_one_sided_order"] for r in report["variants"]],
        "right_cell_signs": [r["right_nonzero_cell_sign"]
                             for r in report["variants"]],
        "changed_historical_case_ids": [],
        "pb00701_certified": report["pb00701_certified"],
        "mc_b_established": report["mc_b_established"],
        "mc1_established": report["mc1_established"],
        "production_authorized": report["production_authorized"],
        "scope": "Original frozen m=1 plus seven NEW source-specific prospective variants; no generic PB route",
    }


class FalsifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = core.report()

    def test_literal_historical_source_and_refusal(self):
        h = self.report["historical"]
        self.assertEqual(h["frozen_reference_id"], core.CASE)
        self.assertEqual(h["frozen_reference_source_sha256"], core.CASE_SOURCE_SHA256)
        self.assertEqual(core.digest(core.source_for_power(1)), core.CASE_SOURCE_SHA256)

    def test_real_frozen_census_and_saved_identity_replay(self):
        h = self.report["historical"]
        self.assertEqual((h["frozen_sources"], h["historical_route_refusals"],
                          h["historical_missing_ordered_premises"],
                          h["supplemental_complete_original_sources"]),
                         (121, 20, 30, 50))
        self.assertEqual(h["supplemental_finite"], 49)
        self.assertEqual(h["supplemental_continuum"], 1)

    def test_exact_laurent_identity_independent_recurrence(self):
        for m in range(1, 9):
            self.assertEqual(core.laurent_from_cosines(core.coefficients(m)),
                             independent_laurent(m))

    def test_all_variants_have_identical_distinct_zero_sets(self):
        self.assertEqual(len(self.report["variants"]), 8)
        for m, r in enumerate(self.report["variants"], 1):
            self.assertEqual(r["power"], m)
            self.assertEqual(r["closed_source_zero_set"], ["1"])
            self.assertEqual(r["global_distinct_closed_root_count"], 1)
            self.assertTrue(r["knot_root_deduplicated"])
            self.assertEqual(r["original_knot"], "1")

    def test_parity_changes_right_cell_but_not_left(self):
        for m, r in enumerate(self.report["variants"], 1):
            self.assertEqual(r["left_nonzero_cell_sign"], 1)
            self.assertEqual(r["right_nonzero_cell_sign"], (-1 if m % 2 else 1))
            self.assertEqual(r["source_knot_event"],
                             "CROSSING" if m % 2 else "TOUCHING")

    def test_multiplicity_is_not_inferred_from_cardinality(self):
        for m, r in enumerate(self.report["variants"], 1):
            self.assertEqual(r["left_one_sided_order"], m)
            self.assertEqual(r["right_one_sided_order"], m)
        self.assertEqual([r["global_distinct_closed_root_count"]
                          for r in self.report["variants"]], [1] * 8)

    def test_phase_and_original_knot_preserved_for_every_variant(self):
        for m in range(1, 9):
            s = core.source_for_power(m)
            self.assertEqual(s["source_parameter_id"], "source-time-t")
            self.assertEqual(s["phase_turn_rate"], "1/4")
            self.assertEqual(s["parameter_hi"], "2")
            self.assertEqual(s["parameter_lo"], "0")
            self.assertTrue(core.source_guard(m, s))
            for c in s["cos_splines"].values():
                self.assertEqual(c["degree"], 0)
                self.assertEqual(c["knots"], ["0", "1", "2"])
                self.assertEqual(c["controls"][0], c["controls"][1])

    def test_mutated_controls_refuse(self):
        for m in (1, 2, 3, 8):
            s = core.source_for_power(m)
            s["cos_splines"]["0"]["controls"][1] = "9"
            self.assertEqual(core.attempt_power(m, s)["status"], "BLOCKED")

    def test_mutated_global_phase_refuses(self):
        for m in (1, 2, 8):
            s = core.source_for_power(m)
            s["phase_turn_rate"] = "0"
            self.assertEqual(core.attempt_power(m, s)["status"], "BLOCKED")
            s = core.source_for_power(m)
            s["phase_turn_offset"] = "1/4"
            self.assertEqual(core.attempt_power(m, s)["status"], "BLOCKED")

    def test_mutated_source_parameter_and_interval_refuse(self):
        for key, value in (
            ("source_parameter_id", "other-t"),
            ("parameter_lo", "-1"),
            ("parameter_hi", "3"),
        ):
            s = core.source_for_power(3)
            s[key] = value
            self.assertEqual(core.attempt_power(3, s)["status"], "BLOCKED")

    def test_mutated_original_knots_and_channels_refuse(self):
        s = core.source_for_power(4)
        s["cos_splines"]["0"]["knots"][1] = "1/2"
        self.assertEqual(core.attempt_power(4, s)["status"], "BLOCKED")
        s = core.source_for_power(4)
        s["sin_splines"]["1"] = {"degree": 0,
                                "knots": ["0", "1", "2"],
                                "controls": ["0", "0"]}
        self.assertEqual(core.attempt_power(4, s)["status"], "BLOCKED")

    def test_unadmitted_powers_are_nontruth(self):
        for m in (0, -1, 1.0, "1", None, True):
            self.assertFalse(core.attempt_power(m, core.source_for_power(1))
                             .get("is_truth_value", True))
        r = core.attempt_power(9, core.source_for_power(8))
        self.assertEqual(r["status"], "RESOURCE_REFUSAL")
        self.assertFalse(r["is_truth_value"])

    def test_fake_events_signs_and_gates_refuse(self):
        for mutate in (
            lambda r: r["variants"][0].__setitem__("right_nonzero_cell_sign", 1),
            lambda r: r["variants"][1].__setitem__("left_one_sided_order", 1),
            lambda r: r["variants"][2].__setitem__("closed_source_zero_set", []),
            lambda r: r["historical_delta"].__setitem__("route_refusals", -1),
            lambda r: r.__setitem__("mc_b_established", True),
            lambda r: r.__setitem__("pb00701_certified", True),
        ):
            forged = copy.deepcopy(self.report)
            mutate(forged)
            self.assertFalse(core.validate_report(forged))

    def test_saved_machine_before_after_evidence(self):
        saved = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(saved, projection(self.report))

    def test_same_zero_set_is_not_a_sign_transfer_function(self):
        variants = self.report["variants"]
        zero_sets = {tuple(v["closed_source_zero_set"]) for v in variants}
        right_signs = {v["right_nonzero_cell_sign"] for v in variants}
        orders = {v["left_one_sided_order"] for v in variants}
        self.assertEqual(len(zero_sets), 1)
        self.assertEqual(right_signs, {-1, 1})
        self.assertEqual(orders, set(range(1, 9)))

    def test_full_scope_does_not_authorize_gates_or_native(self):
        r = self.report
        self.assertEqual(r["evidence_class"], "DETERMINISTIC_MODEL")
        self.assertTrue(r["not_a_general_impossibility_result"])
        self.assertFalse(r["pb00701_certified"])
        self.assertFalse(r["mc_b_established"])
        self.assertFalse(r["mc1_established"])
        self.assertFalse(r["production_authorized"])
        self.assertEqual(r["historical_delta"]["newly_disposed_frozen_case_ids"], [])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.contract and not args.self_test:
        parser.error("specify --contract and/or --self-test")
    if args.contract:
        r = core.report()
        print(json.dumps(projection(r), sort_keys=True))
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(FalsifierTests)
        outcome = unittest.TextTestRunner(verbosity=2).run(suite)
        if not outcome.wasSuccessful():
            sys.exit(1)


if __name__ == "__main__":
    main()
