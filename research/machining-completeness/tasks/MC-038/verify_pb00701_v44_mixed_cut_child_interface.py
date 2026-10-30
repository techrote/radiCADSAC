#!/usr/bin/env python3
"""Adversarial exact-source replay for frozen V44 four mixed-cut children."""
from __future__ import annotations

import argparse
import copy
import json
import sys
import unittest
from fractions import Fraction as Q
from unittest.mock import patch

import pb00701_v44_mixed_cut_child_interface as core


class FrozenV44MixedCutInterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.atlas = core.bridge.atlas.prove()
        cls.good = core.attempt(supplied_atlas=cls.atlas)
        if cls.good.get("status") != core.SUCCESS:
            raise RuntimeError("FROZEN_MIXED_CUT_CHILD_PROOF_FAILED:" +
                               repr(cls.good))
        cls.field = core.bridge._field(cls.good["shared_exact_algebraic_field"])
        cls.span = core.derivative._source_snapshot(cls.atlas)[1]

    def test_four_exact_mixed_children_and_independent_root_partition(self):
        r = self.good
        self.assertEqual(r["evidence_class"], "DETERMINISTIC_MODEL")
        self.assertEqual(r["complete_open_simple_physical_root_counts"],
                         [0, 1, 0, 0])
        self.assertEqual(
            [x["strict_sign_name"] for x in
             r["independently_recomputed_boundary_signs"]],
            ["NEGATIVE", "NEGATIVE", "POSITIVE", "POSITIVE", "POSITIVE"])
        self.assertEqual(len(r["closed_mixed_cut_qalpha_children"]), 4)
        self.assertEqual(r["proof_cut_physical_events"], 0)
        self.assertEqual(r["one_irrational_cut_identity_method"],
                         "EXACT_POLYNOMIAL_GCD_PLUS_STURM_COMMON_ROOT")
        self.assertTrue(r[
            "root_counts_derived_from_new_signs_and_global_monotonicity"])

    def test_all_exact_child_maps_polynomial_roundtrips_phase_and_derivative(self):
        r = self.good
        field = self.field
        children = r["closed_mixed_cut_qalpha_children"]
        zero, one = field.element(0), field.element(1)
        m = Q(r["global_strict_source_derivative_lower"])
        self.assertEqual(field.element(
            children[0]["source_affine_offset_qalpha"]), zero)
        end = zero
        for i, child in enumerate(children):
            with self.subTest(i=i):
                left = field.element(child["source_affine_offset_qalpha"])
                width = field.element(child["source_affine_width_qalpha"])
                right = field.element(child["source_affine_right_qalpha"])
                self.assertEqual(left, end)
                self.assertEqual(left+width, right)
                self.assertEqual(width.sign(), 1)
                self.assertEqual(field.element(
                    child["strict_child_derivative_lower_qalpha"]),
                    field.element(m) * width)
                self.assertEqual(field.element(
                    child["strict_child_derivative_lower_qalpha"]).sign(), 1)
                self.assertEqual(
                    field.element(child["phase_offset_qalpha"]),
                    field.element(self.span.offset)+left*self.span.rate)
                self.assertEqual(
                    field.element(child["phase_rate_qalpha"]),
                    width*self.span.rate)
                channels = child["restricted_cos_sin_polynomials_qalpha"]
                self.assertEqual(set(channels),
                                 {str(h) for h in self.span.terms})
                inv = width.inverse()
                for h, polys in self.span.terms.items():
                    for c, original in enumerate(polys):
                        actual = [field.element(x) for x in
                                  channels[str(h)][c]]
                        expected = core.v45.compose_affine(
                            original, left, width)
                        self.assertEqual(actual, expected)
                        self.assertEqual(core.v45.compose_affine(
                            actual, -left*inv, inv),
                            core.v45.compose_affine(
                                original, zero, one))
                end = right
        self.assertEqual(end, one)

    def test_independent_source_point_enclosure_for_each_rational_boundary(self):
        witnesses = self.good["independently_recomputed_boundary_signs"]
        self.assertEqual(
            sum(w["method"] ==
                "EXACT_STURM_RATIONAL_MIDPOINT_OUTWARD_TRIG_LIPSCHITZ"
                for w in witnesses), 1)
        for w in witnesses:
            if w["method"] != "ORIGINAL_RATIONAL_SOURCE_TRIG_OUTWARD_ENCLOSURE":
                continue
            t = Q(w["exact_source_coordinate"])
            raw_lo, raw_hi = self.span.evaluate(t)
            lower, upper = map(Q, w["outward_enclosure"])
            self.assertLessEqual(lower, raw_lo)
            self.assertGreaterEqual(upper, raw_hi)
            self.assertTrue(lower > 0 or upper < 0)
            self.assertEqual(
                (1 if lower > 0 else -1), w["strict_nonzero_sign"])
            self.assertFalse(w["binary_float_or_epsilon_used"])

    def test_irrational_cut_sign_and_source_witness(self):
        proof = self.good["independent_irrational_cut_sign_source_proof"]
        self.assertEqual(proof["strict_nonzero_sign"], 1)
        self.assertFalse(proof["irrational_trigonometric_evaluation_performed"])
        self.assertLessEqual(proof["certificate"]["refinements_used"],
                             core.source_sign.MAX_REFINEMENTS)
        self.assertEqual(self.good["shared_exact_algebraic_field"][
            "minimal_polynomial"], [-1, 0, 2])

    def test_exact_zero_at_rational_coordinate_refuses_nonzero(self):
        span = core.trig.Span(0, 1, 0, 0, {
            0: ((0, 1), (0,))
        })
        with self.assertRaisesRegex(
            core.Refusal, "RATIONAL_BOUNDARY_SIGN_NOT_STRICTLY_DECIDED"):
            core._rational_source_witness(span, Q(0))
        self.assertEqual(core._rational_source_witness(
            span, Q(1))["strict_nonzero_sign"], 1)

    def test_irrational_cut_or_predecessor_source_refusal_stays_nontruth(self):
        with patch.object(core.source_sign, "prove",
                          side_effect=core.source_sign.ResourceRefusal(
                              "IRRATIONAL_SIGN_BUDGET_EXHAUSTED")):
            result = core.attempt(supplied_atlas=self.atlas)
        self.assertEqual(result["status"], "RESOURCE_REFUSAL")
        self.assertFalse(result["is_truth_value"])
        with patch.object(core.bridge.previous, "git_blob",
                          return_value="f" * 40):
            result = core.attempt(supplied_atlas=self.atlas)
        self.assertEqual(result["status"], "BLOCKED")

    def test_mutated_source_cut_order_sign_and_event_cannot_be_accepted(self):
        cases = []
        sign = copy.deepcopy(self.atlas)
        sign["proof_boundaries"][1]["physical_value_sign"] = "POSITIVE"
        cases.append(sign)
        moved = copy.deepcopy(self.atlas)
        for b in moved["proof_boundaries"]:
            if b.get("coordinate_descriptor", {}).get("kind") in (
                    "RATIONAL_PROOF_CUT", "RATIONAL_ROOT"):
                b["coordinate_descriptor"]["local_value"] = "7/8"
                break
        cases.append(moved)
        event = copy.deepcopy(self.atlas)
        event["proof_boundaries"][2]["is_physical_zero"] = True
        cases.append(event)
        dropped = copy.deepcopy(self.atlas)
        dropped["source_proof_cells"].pop()
        cases.append(dropped)
        for case in cases:
            with self.subTest(mutated=repr(case)[:70]):
                r = core.attempt(supplied_atlas=case)
                self.assertNotEqual(r["status"], core.SUCCESS, r)
                self.assertFalse(r["is_truth_value"])

    def test_forged_boundary_child_derivative_and_gate_reports_refuse(self):
        for path, forged_value in (
            (("independently_recomputed_boundary_signs",), []),
            (("closed_mixed_cut_qalpha_children", 1,
              "source_affine_width_qalpha"), ["0"]),
            (("closed_mixed_cut_qalpha_children", 1,
              "strict_child_derivative_lower_qalpha"), ["0"]),
            (("complete_open_simple_physical_root_counts",), [1, 0, 0, 0]),
            (("shared_exact_algebraic_field",
              "minimal_polynomial"), [1, 0, 2]),
            (("global_strict_source_derivative_lower",), "0"),
            (("source_sha256",), "f" * 64),
            (("historical_v54_admitted",), True),
            (("mc_b_established",), True),
            (("production_authorized",), True),
        ):
            changed = copy.deepcopy(self.good)
            obj = changed
            for key in path[:-1]:
                obj = obj[key]
            obj[path[-1]] = forged_value
            with self.subTest(path=path):
                verdict = core.validate_report(
                    changed, supplied_atlas=self.atlas)
                self.assertEqual(verdict["status"], "BLOCKED", verdict)

    def test_bounded_report_canonical_replay_and_resource_limits(self):
        raw = core.bridge.previous.canonical(self.good)
        self.assertLessEqual(len(raw), core.MAX_REPORT_BYTES)
        self.assertEqual(
            core.validate_report(self.good, supplied_atlas=self.atlas)[
                "status"], core.SUCCESS)
        self.assertGreater(len(core.bridge.previous.canonical(
            [0] * 40000)), core.MAX_REPORT_BYTES)
        for value in ("a" * (core.MAX_REPORT_BYTES + 1),
                      [0] * 40000):
            with self.subTest(oversized_type=type(value).__name__):
                verdict = core.validate_report(value)
                self.assertEqual(verdict["status"], "RESOURCE_REFUSAL")
        cycle = []
        cycle.append(cycle)
        verdict = core.validate_report(cycle)
        self.assertEqual(verdict["status"], "RESOURCE_REFUSAL")

    def test_no_global_production_or_historical_gate_promotion(self):
        r = self.good
        self.assertEqual(r["historical_v54_disposition"], "BLOCKED")
        for name in (
            "general_multifield_algebraic_compositum_constructed",
            "general_irrational_trig_endpoint_zero_decider_constructed",
            "historical_v47_v49_analytic_child_route_certified",
            "historical_v54_admitted", "pb00701_certified",
            "mc_b_established", "mc1_established",
            "native_geometry_or_step_qualified", "production_authorized"):
            self.assertFalse(r[name], name)


def contract():
    r = core.attempt()
    if r.get("status") != core.SUCCESS:
        raise RuntimeError("FROZEN_MIXED_CUT_SOURCE_CHILD_UNPROVED:" +
                           repr(r))
    return {
        "status": r["status"],
        "source_sha256": r["source_sha256"],
        "field": r["shared_exact_algebraic_field"],
        "mixed_child_count": len(r["closed_mixed_cut_qalpha_children"]),
        "source_boundary_signs": [x["strict_sign_name"] for x in
                                  r["independently_recomputed_boundary_signs"]],
        "physical_root_counts":
            r["complete_open_simple_physical_root_counts"],
        "canonical_report_bytes": len(
            core.bridge.previous.canonical(r)),
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
            FrozenV44MixedCutInterfaceTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
