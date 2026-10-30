#!/usr/bin/env python3
"""Adversarial replay for source-bound irrational phase-cut sign transport."""
from __future__ import annotations

import argparse
import copy
import json
import sys
import unittest
from fractions import Fraction as Q
from unittest.mock import patch

import pb00701_v44_irrational_cut_source_sign as core


class FrozenIrrationalCutSourceSignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.view = core.bridge.atlas.prove()
        cls.good = core.attempt(supplied_atlas=cls.view)
        if cls.good.get("status") != core.SUCCESS:
            raise RuntimeError("FROZEN_CUT_SIGN_NOT_PROVED:" + repr(cls.good))
        cls.field = core.bridge._field(cls.good["exact_v45_field"])

    def test_actual_v45_algebraic_cut_strict_source_sign(self):
        r = self.good
        self.assertEqual(r["status"], core.SUCCESS)
        self.assertEqual(r["evidence_class"], "DETERMINISTIC_MODEL")
        self.assertEqual(r["source_sha256"], core.bridge.atlas.SOURCE_SHA256)
        self.assertEqual(r["independently_certified_irrational_cut_sign"],
                         "POSITIVE")
        self.assertTrue(r["agrees_with_preserved_v46_source_atlas"])
        self.assertTrue(r["physical_cut_is_nonzero"])
        self.assertFalse(r["proof_cut_is_physical_event"])
        self.assertEqual(r["source_proof"]["strict_nonzero_sign"], 1)
        self.assertEqual(r["source_proof"][
            "strict_sign_certification_method"],
            "EXACT_STURM_RATIONAL_MIDPOINT_OUTWARD_TRIG_LIPSCHITZ")

    def test_exact_rational_point_and_lipschitz_witness(self):
        r = self.good["source_proof"]
        span = core.derivative._source_snapshot(self.view)[1]
        self.assertEqual(Q(r["source_lipschitz_derivative_upper_bound"]),
                         core.independent_lipschitz_bound(span))
        self.assertEqual(r["initial_exact_algebraic_isolation"],
                         [str(x) for x in self.field.interval])
        trace = r["refinement_history"]
        self.assertEqual(trace[-1], r["certificate"])
        self.assertEqual([x["refinements_used"] for x in trace],
                         list(range(len(trace))))
        self.assertLessEqual(len(trace)-1, core.MAX_REFINEMENTS)
        for item in trace:
            lo, hi = map(Q, item["algebraic_cut_sturm_isolation"])
            mid = Q(item["exact_rational_source_midpoint"])
            self.assertEqual(mid, (lo+hi)/2)
            self.assertEqual(
                core.v45.engine.distinct_roots_open(
                    self.field.minimal, lo, hi), 1)
            point = tuple(map(Q, item["rational_source_trig_enclosure"]))
            drift = Q(item["global_derivative_lipschitz_radius"])
            transported = tuple(map(
                Q, item["transported_irrational_cut_value_enclosure"]))
            self.assertEqual(transported, (point[0]-drift, point[1]+drift))
        self.assertGreater(Q(trace[-1][
            "transported_irrational_cut_value_enclosure"][0]), 0)

    def test_exact_zero_at_algebraic_cut_is_resource_refusal(self):
        # F(t)=2t^2-1 vanishes at *the exact same* irrational field root.
        # The source enclosure can never prove a strict nonzero sign.
        span = core.trig.Span(0, 1, 0, 0, {
            0: ((-1, 0, 2), (0,))
        })
        self.assertGreater(core.independent_lipschitz_bound(span), 0)
        with self.assertRaisesRegex(core.ResourceRefusal,
                                    "IRRATIONAL_CUT_NONZERO_SIGN_UNDECIDED"):
            core.certify_strict_sign(span, self.field, max_refinements=12)

    def test_synthetic_source_signs_are_certified_not_guessed(self):
        for poly, expected in (
            ((1,), 1), ((-1,), -1),
            ((-1, 2), 1), ((1, -2), -1),
            ((0, 1), 1), ((-1, 1), -1),
        ):
            with self.subTest(poly=poly):
                span = core.trig.Span(0, 1, 0, 0, {
                    0: (poly, (0,))
                })
                result = core.certify_strict_sign(
                    span, self.field, max_refinements=24)
                self.assertEqual(result["strict_nonzero_sign"], expected)
                self.assertFalse(result[
                    "irrational_trigonometric_evaluation_performed"])

    def test_near_zero_and_zero_are_never_forced_to_nonzero(self):
        for poly in ((0,), (-1, 0, 2),
                     (Q(-1) + Q(1, 2**32), 0, 2)):
            span = core.trig.Span(0, 1, 0, 0, {0: (poly, (0,))})
            with self.subTest(poly=poly):
                with self.assertRaises(core.ResourceRefusal):
                    core.certify_strict_sign(
                        span, self.field, max_refinements=3)

    def test_lipschitz_input_source_ownership_refuses(self):
        span = core.trig.Span(0, 1, 0, 0, {
            0: ((-1, 2), (0,))
        })
        span.m1 = Q(0)  # forged global derivative bound
        with self.assertRaisesRegex(core.Refusal, "LIPSCHITZ_DRIFT"):
            core.certify_strict_sign(span, self.field)

    def test_invalid_budgets_and_cut_outside_span_refuse(self):
        span = core.trig.Span(0, 1, 0, 0, {
            0: ((1,), (0,))
        })
        for bad in (True, -1, core.MAX_REFINEMENTS + 1, Q(3, 2)):
            with self.subTest(bad=bad):
                with self.assertRaises(core.Refusal):
                    core.certify_strict_sign(
                        span, self.field, max_refinements=bad)
        restricted = core.trig.Span(Q(3, 4), 1, 0, 0,
                                    {0: ((1,), (0,))})
        with self.assertRaises(core.Refusal):
            core.certify_strict_sign(restricted, self.field)

    def test_nominal_report_canonical_size_and_self_replay(self):
        size = len(core.bridge.previous.canonical(self.good))
        self.assertLessEqual(
            size, core.MAX_REPORT_BYTES,
            f"nominal report bytes={size}, cap={core.MAX_REPORT_BYTES}"
        )
        self.assertEqual(core.validate_report(
            self.good, supplied_atlas=self.view)["status"], core.SUCCESS)

    def test_forged_report_sign_interval_bound_and_gate_refuse(self):
        for path, forged_value in (
            (("independently_certified_irrational_cut_sign",), "NEGATIVE"),
            (("source_proof", "source_lipschitz_derivative_upper_bound"), "0"),
            (("source_proof", "certificate",
              "transported_irrational_cut_value_enclosure"), ["1", "1"]),
            (("source_proof", "refinement_history"), []),
            (("exact_v45_field", "root_index_in_open_unit_interval"), 99),
            (("source_sha256",), "f" * 64),
            (("historical_v54_admitted",), True),
            (("production_authorized",), True),
        ):
            forged = copy.deepcopy(self.good)
            target = forged
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = forged_value
            result = core.validate_report(forged, supplied_atlas=self.view)
            self.assertEqual(result["status"], "BLOCKED", (path, result))
            self.assertFalse(result["is_truth_value"])

    def test_predecessor_drift_and_atlas_sign_mutation_refuse(self):
        with patch.object(core.bridge.previous, "git_blob",
                          return_value="f"*40):
            result = core.attempt(supplied_atlas=self.view)
        self.assertEqual(result["status"], "BLOCKED")
        forged = copy.deepcopy(self.view)
        for boundary in forged["proof_boundaries"]:
            if boundary.get("coordinate_descriptor", {}).get("kind") == \
                    "ISOLATED_REAL_ROOT":
                boundary["physical_value_sign"] = "NEGATIVE"
        result = core.attempt(supplied_atlas=forged)
        self.assertEqual(result["status"], "BLOCKED")

    def test_bounded_resource_refusal_does_not_promote_authority(self):
        with patch.object(core, "certify_strict_sign",
                          side_effect=core.ResourceRefusal(
                              "SOURCE_SIGN_REFINEMENT_EXHAUSTED")):
            result = core.attempt(supplied_atlas=self.view)
        self.assertEqual(result["status"], "RESOURCE_REFUSAL")
        self.assertFalse(result["is_truth_value"])
        for key in ("pb00701_certified", "mc_b_established",
                    "mc1_established", "production_authorized"):
            self.assertFalse(result[key])

    def test_deep_cyclic_oversized_evidence_is_resource_nontruth(self):
        deep = []
        for _ in range(1100):
            deep = [deep]
        cyclic = []
        cyclic.append(cyclic)
        for bad in (deep, cyclic, "x" * (core.MAX_REPORT_BYTES + 1),
                    [0]*(core.bridge.predecessor.MAX_REPORT_VISITED_NODES+1)):
            with self.subTest(kind=type(bad).__name__):
                result = core.validate_report(bad, supplied_atlas=self.view)
                self.assertEqual(result["status"], "RESOURCE_REFUSAL")
                self.assertFalse(result["is_truth_value"])

    def test_no_global_event_or_production_promotion(self):
        r = self.good
        self.assertEqual(r["historical_v54_disposition"], "BLOCKED")
        self.assertEqual(r[
            "historical_v45_irrational_phase_endpoint_authority"],
            "DEFERRED")
        for key in ("general_irrational_phase_endpoint_zero_decider_constructed",
                    "general_v41_v47_child_event_route_certified",
                    "historical_v54_admitted", "pb00701_certified",
                    "mc_b_established", "mc1_established",
                    "native_geometry_or_step_qualified",
                    "production_authorized"):
            self.assertFalse(r[key], key)


def contract():
    r = core.attempt()
    if r.get("status") != core.SUCCESS:
        raise RuntimeError("V44_IRRATIONAL_SOURCE_SIGN_UNPROVED:" + repr(r))
    return {
        "status": r["status"],
        "source_sha256": r["source_sha256"],
        "source_field": r["exact_v45_field"],
        "strict_physical_cut_sign":
            r["independently_certified_irrational_cut_sign"],
        "source_lipschitz_bound":
            r["source_proof"]["source_lipschitz_derivative_upper_bound"],
        "bisections": r["source_proof"][
            "certificate"]["refinements_used"],
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
            FrozenIrrationalCutSourceSignTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
