#!/usr/bin/env python3
"""Adversarial verification for exact two-span source-knot root-set composition."""
from __future__ import annotations

import argparse
import copy
import json
from fractions import Fraction as Q
import sys
import unittest

import pb00701_two_span_source_knot_root_set as core

CASE_ID = "composite:DELEGATED_V6_CONSTANT_MODULATION:tail0"


def _span(left, right, poly, *, offset=Q(0), rate=Q(0)):
    return core.point.interval.Span(
        Q(left), Q(right), Q(offset), Q(rate),
        {1: (tuple(Q(x) for x in poly), (Q(0),))}
    )


class TwoSpanSourceKnotRootSetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = core.local307.load_frozen_case(CASE_ID)
        cls.spec = cls.case["spec"]
        cls.report = core.analyze_source(cls.spec)
        cls.frozen = core.analyze_frozen_case(CASE_ID)

    def test_frozen_source_has_one_global_distinct_root(self):
        r = self.report
        self.assertEqual(
            r["status"],
            "EXACT_SOURCE_BOUND_TWO_SPAN_KNOT_ROOT_SET_RESEARCH",
        )
        self.assertEqual(r["span_count"], 2)
        self.assertEqual(
            [x["distinct_roots_open"] for x in r["span_local_root_summaries"]],
            [0, 0],
        )
        self.assertEqual(r["distinct_roots_in_open_span_interiors"], 0)
        self.assertFalse(r["left_exterior_is_root"])
        self.assertFalse(r["right_exterior_is_root"])
        self.assertEqual(r["shared_source_knot_distinct_root_events"], 1)
        self.assertEqual(r["global_distinct_roots_closed_source"], 1)
        self.assertTrue(r["global_source_knot_deduplication_established"])
        self.assertTrue(r["global_multispan_root_count_established"])
        self.assertFalse(r["global_smooth_knot_multiplicity_claimed"])
        self.assertFalse(r["global_multiple_root_count_claimed"])

    def test_shared_knot_is_exact_one_event_crossing_with_separate_orders(self):
        k = self.report["shared_source_knot"]
        self.assertEqual(k["status"], "EXACT_SINGLE_SOURCE_KNOT_ZERO")
        self.assertEqual(k["coordinate"], "1")
        self.assertEqual(k["source_coordinate"], "1")
        self.assertEqual(k["physical_zero_events"], 1)
        self.assertEqual(
            [k["left_one_sided_order"], k["right_one_sided_order"]],
            [1, 1],
        )
        self.assertEqual([k["left_sign"], k["right_sign"]], [1, -1])
        self.assertEqual(k["event_kind"], "CROSSING")
        self.assertFalse(k["global_smooth_multiplicity_claimed"])
        records = k["span_local_records"]
        self.assertEqual(records["same_source_coordinate_root_records"], 2)
        self.assertEqual(records["deduplicated_distinct_source_root_events"], 1)
        self.assertEqual(records["left_span_right_endpoint_multiplicity"], 1)
        self.assertEqual(records["right_span_left_endpoint_multiplicity"], 1)

    def test_exterior_endpoints_are_exact_nonzero_opposite_signs(self):
        left = self.report["left_exterior_point"]
        right = self.report["right_exterior_point"]
        self.assertEqual(left["status"], "EXACT_NONZERO_RATIONAL_POINT")
        self.assertEqual(right["status"], "EXACT_NONZERO_RATIONAL_POINT")
        self.assertEqual(left["coordinate"], "0")
        self.assertEqual(right["coordinate"], "2")
        self.assertEqual(left["value_sign"], 1)
        self.assertEqual(right["value_sign"], -1)

    def test_frozen_binding_and_historical_nonclaims(self):
        r = self.frozen
        self.assertEqual(r["frozen_case_id"], CASE_ID)
        self.assertEqual(r["frozen_origin"], "verify_pb00701_v7")
        self.assertEqual(r["historical_v54_disposition"], "BLOCKED")
        self.assertEqual(r["source_sha256"], core.local307.source_sha256(self.spec))
        self.assertEqual(r["source_parameter_id"], "source-time-t")
        self.assertEqual(r["source_interval"], ["0", "2"])
        self.assertEqual(r["phase_turn_law"], {"offset": "0", "rate": "1/4"})
        self.assertFalse(r["historical_v54_admitted"])
        self.assertFalse(r["historical_v54_dispositions_changed"])
        self.assertFalse(r["pb00701_certified"])
        self.assertFalse(r["mc_b_established"])
        self.assertFalse(r["mc1_established"])
        self.assertFalse(r["native_brep_or_step_qualified"])
        self.assertFalse(r["production_authorized"])

    def test_local_to_source_polynomial_substitution_is_exact(self):
        local = [Q(1), Q(2), Q(3)]
        source = core.local_poly_to_source(local, Q(2), Q(5))
        for t in (Q(2), Q(5, 2), Q(7, 2), Q(5)):
            s = (t - Q(2)) / Q(3)
            self.assertEqual(core.peval(source, t), core.peval(local, s))

    def test_different_one_sided_orders_remain_separate(self):
        left = _span(-1, 0, [0, 0, 1])
        right = _span(0, 1, [0, 0, 0, 1])
        join = core._exact_join(left, right, Q(0))
        self.assertEqual(join["physical_zero_events"], 1)
        self.assertEqual(
            [join["left_one_sided_order"], join["right_one_sided_order"]],
            [2, 3],
        )
        self.assertEqual([join["left_sign"], join["right_sign"]], [1, 1])
        self.assertEqual(join["event_kind"], "TOUCHING")
        self.assertFalse(join["global_smooth_multiplicity_claimed"])

    def test_exact_discontinuity_refuses_join(self):
        left = _span(-1, 0, [1])
        right = _span(0, 1, [2])
        with self.assertRaisesRegex(
            core.ResearchRefusal, "DISCONTINUOUS_SOURCE_KNOT"
        ):
            core._exact_join(left, right, Q(0))

    def test_phase_or_coordinate_mismatch_refuses_join(self):
        left = _span(-1, 0, [0, 1], offset=Q(0), rate=Q(0))
        right = _span(0, 1, [0, 1], offset=Q(0), rate=Q(1, 4))
        with self.assertRaisesRegex(
            core.ResearchRefusal, "SOURCE_KNOT_PHASE_OR_COORDINATE_MISMATCH"
        ):
            core._exact_join(left, right, Q(0))

    def test_missing_or_negative_span_open_root_count_refuses(self):
        with self.assertRaisesRegex(
            core.ResearchRefusal, "SPAN_LOCAL_EXACT_OPEN_ROOT_COUNT_MISSING"
        ):
            core._route_open_summary({
                "shadow_upgrade_applied": False,
                "route": {"status": "CERTIFIED"},
            })
        with self.assertRaisesRegex(
            core.ResearchRefusal, "SPAN_LOCAL_EXACT_OPEN_ROOT_COUNT_MISSING"
        ):
            core._route_open_summary({
                "shadow_upgrade_applied": False,
                "route": {"status": "CERTIFIED", "distinct_roots_open": -1},
            })

    def test_source_mutation_cannot_reuse_report(self):
        mutations = (
            lambda s: s.__setitem__("phase_turn_rate", "1/5"),
            lambda s: s.__setitem__("source_parameter_id", "forged-source"),
            lambda s: s["cos_splines"]["1"]["controls"].__setitem__(0, "2"),
            lambda s: s.__setitem__("parameter_hi", "3"),
        )
        for mutate in mutations:
            spec = copy.deepcopy(self.spec)
            mutate(spec)
            checked = core.validate_report(spec, self.report)
            self.assertNotEqual(
                checked.get("status"),
                "EXACT_SOURCE_BOUND_TWO_SPAN_KNOT_ROOT_SET_RESEARCH",
                checked,
            )
            self.assertFalse(checked["is_truth_value"])

    def test_binary_float_and_extra_caller_authority_refuse(self):
        floating = copy.deepcopy(self.spec)
        floating["phase_turn_rate"] = 0.25
        a = core.attempt(floating)
        self.assertEqual(a["status"], "BLOCKED")
        self.assertIn("BINARY_FLOAT", a["reason"])

        forged = copy.deepcopy(self.spec)
        forged["global_root_count"] = 1
        b = core.attempt(forged)
        self.assertEqual(b["status"], "BLOCKED")
        self.assertFalse(b["is_truth_value"])

    def test_report_replay_is_exact(self):
        checked = core.validate_report(self.spec, self.report)
        self.assertEqual(checked, self.report)

    def test_report_forgery_and_capability_promotion_refuse(self):
        mutations = (
            lambda r: r.__setitem__("global_distinct_roots_closed_source", 2),
            lambda r: r.__setitem__(
                "global_source_knot_deduplication_established", False
            ),
            lambda r: r.__setitem__("global_multispan_root_count_established", False),
            lambda r: r.__setitem__("global_smooth_knot_multiplicity_claimed", True),
            lambda r: r.__setitem__("global_multiple_root_count_claimed", True),
            lambda r: r.__setitem__("historical_v54_admitted", True),
            lambda r: r.__setitem__("historical_v54_dispositions_changed", True),
            lambda r: r.__setitem__("pb00701_certified", True),
            lambda r: r.__setitem__("mc_b_established", True),
            lambda r: r.__setitem__("mc1_established", True),
            lambda r: r.__setitem__("native_brep_or_step_qualified", True),
            lambda r: r.__setitem__("production_authorized", True),
        )
        for mutate in mutations:
            forged = copy.deepcopy(self.report)
            mutate(forged)
            checked = core.validate_report(self.spec, forged)
            self.assertEqual(checked["status"], "BLOCKED", checked)
            self.assertFalse(checked["is_truth_value"])

    def test_oversized_report_refuses_as_nontruth(self):
        forged = copy.deepcopy(self.report)
        forged["junk"] = "x" * (core.MAX_REPORT_BYTES + 1)
        checked = core.validate_report(self.spec, forged)
        self.assertEqual(checked["status"], "RESOURCE_REFUSAL")
        self.assertFalse(checked["is_truth_value"])

    def test_pinned_domain_and_authority_remain_closed(self):
        core.pins()
        domain = json.loads(
            (core.ROOT /
             "research/machining-completeness/tasks/MC-002/domain-contract-v1.json")
            .read_text()
        )
        authority = json.loads(
            (core.ROOT / "handoffs/current-authority.json").read_text()
        )
        self.assertEqual(
            len(domain["coverage_rule"]["required_operation_ids"]), 26
        )
        self.assertFalse(authority["production_authorized"])
        self.assertEqual(authority["capability_status"], "NOT_ESTABLISHED")


def contract():
    r = core.analyze_frozen_case(CASE_ID)
    k = r["shared_source_knot"]
    return {
        "case_id": CASE_ID,
        "status": r["status"],
        "source_sha256": r["source_sha256"],
        "historical_v54_disposition": r["historical_v54_disposition"],
        "span_open_root_counts": [
            x["distinct_roots_open"] for x in r["span_local_root_summaries"]
        ],
        "shared_source_coordinate": k["source_coordinate"],
        "shared_source_knot_orders": [
            k["left_one_sided_order"], k["right_one_sided_order"]
        ],
        "shared_source_knot_signs": [k["left_sign"], k["right_sign"]],
        "shared_source_knot_event_kind": k["event_kind"],
        "global_distinct_roots_closed_source":
            r["global_distinct_roots_closed_source"],
        "global_source_knot_deduplication_established": True,
        "global_smooth_knot_multiplicity_claimed": False,
        "historical_v54_admitted": False,
        "pb00701_certified": False,
        "production_authorized": False,
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
            TwoSpanSourceKnotRootSetTests
        )
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
