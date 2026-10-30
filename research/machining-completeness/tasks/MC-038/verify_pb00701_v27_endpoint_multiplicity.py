#!/usr/bin/env python3
"""Adversarial verification for source-bound V27 endpoint multiplicity research."""
from __future__ import annotations

import argparse
import copy
import json
from fractions import Fraction as Q
import sys
import unittest

import pb00701_v27_endpoint_multiplicity as core

CASE_ID = "composite:DELEGATED_V6_CONSTANT_MODULATION:tail0"


def _frozen_spec():
    return core.load_frozen_case(CASE_ID)["spec"]


def _zero_event(child_cos, child_sin, offset, rate, side="left"):
    coordinate = Q(0) if side == "left" else Q(1)
    phase = core.q(offset) + core.q(rate) * coordinate
    return core.v27.v19._endpoint_relation(
        child_cos, child_sin, coordinate, phase
    )


class V27EndpointMultiplicityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = core.load_frozen_case(CASE_ID)
        cls.spec = cls.case["spec"]
        cls.baseline = core.v27.classify_required_analytic_event(cls.spec)
        cls.report = core.analyze_source(cls.spec)
        cls.frozen = core.analyze_frozen_case(CASE_ID)

    def test_frozen_case_reproduces_live_v27_blocker_before_upgrade(self):
        self.assertEqual(self.baseline["status"], "BLOCKED", self.baseline)
        blocked = [
            span for span in self.baseline["spans"]
            if span.get("route", {}).get("status") != "CERTIFIED"
        ]
        self.assertEqual(len(blocked), 1, blocked)
        self.assertEqual(
            blocked[0]["route_kind"],
            "PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION",
        )
        self.assertEqual(
            blocked[0]["route"]["reason"],
            "V27_CHILD_LEFT_ENDPOINT_MULTIPLICITY_NOT_COMPOSABLE",
        )

    def test_exact_frozen_source_endpoint_jet_supplies_order_one(self):
        r = self.report
        self.assertEqual(
            r["status"],
            "EXACT_SOURCE_BOUND_V27_ENDPOINT_MULTIPLICITY_COMPOSITION_RESEARCH",
        )
        self.assertTrue(r["all_shadow_span_routes_certified"])
        supplied = r["point_jet_supplied_endpoint_multiplicity"]
        self.assertEqual(len(supplied), 1, supplied)
        evidence = supplied[0]
        self.assertEqual(evidence["side"], "left")
        self.assertEqual(evidence["multiplicity"], 1)
        witness = evidence["witness"]
        self.assertEqual(witness["status"], "EXACT_RATIONAL_POINT_EVENT")
        self.assertEqual(witness["one_sided_order"], 1)
        self.assertEqual(witness["first_nonzero_derivative_order"], 1)
        self.assertEqual(witness["phase_turn"], "1/4")
        self.assertEqual(witness["first_nonzero_derivative_sign"], -1)
        self.assertEqual(witness["right_sign"], -1)
        self.assertFalse(witness["left_in_source"])
        self.assertTrue(witness["right_in_source"])

    def test_frozen_source_binding_and_nonclaims(self):
        r = self.frozen
        self.assertEqual(r["frozen_case_id"], CASE_ID)
        self.assertEqual(r["frozen_origin"], "verify_pb00701_v7")
        self.assertEqual(r["historical_v54_disposition"], "BLOCKED")
        self.assertEqual(r["source_sha256"], core.source_sha256(self.spec))
        self.assertEqual(r["source_parameter_id"], "source-time-t")
        self.assertEqual(r["source_interval"], ["0", "2"])
        self.assertEqual(r["phase_turn_law"], {"offset": "0", "rate": "1/4"})
        self.assertFalse(r["global_multispan_root_count_claimed"])
        self.assertFalse(r["global_source_knot_deduplication_claimed"])
        self.assertTrue(r["shared_source_knot_has_two_span_local_endpoint_records"])
        self.assertFalse(r["global_cross_span_multiplicity_claimed"])
        self.assertFalse(r["historical_v54_admitted"])
        self.assertFalse(r["historical_v54_dispositions_changed"])
        self.assertFalse(r["pb00701_certified"])
        self.assertFalse(r["mc_b_established"])
        self.assertFalse(r["mc1_established"])
        self.assertFalse(r["native_brep_or_step_qualified"])
        self.assertFalse(r["production_authorized"])

    def test_shadow_route_keeps_current_child_composition_rules(self):
        upgraded = [
            span for span in self.report["shadow_spans"]
            if span["shadow_upgrade_applied"]
        ]
        self.assertEqual(len(upgraded), 1)
        route = upgraded[0]["route"]
        self.assertEqual(route["status"], "CERTIFIED")
        self.assertEqual(
            route["current_v27_blocker"]["reason"],
            "V27_CHILD_LEFT_ENDPOINT_MULTIPLICITY_NOT_COMPOSABLE",
        )
        self.assertFalse(route["multiplicity_invented_from_root_count"])
        self.assertFalse(route["caller_multiplicity_trusted"])
        self.assertFalse(route["historical_v27_model_modified"])
        self.assertGreater(route["child_count"], 1)
        self.assertEqual(
            route["composition"]["status"], "CERTIFIED", route["composition"]
        )
        self.assertFalse(
            route["composition"]["multiplicity_invented_from_root_count"]
        )

    def test_frozen_deeper_v6_endpoint_pole_is_exactly_normalized(self):
        evidence = self.report["endpoint_pole_normalizations"]
        self.assertEqual(len(evidence), 1, evidence)
        item = evidence[0]
        self.assertEqual(item["child_index"], 2)
        self.assertEqual(item["original_turn_interval"], ["5/12", "1/2"])
        self.assertEqual(item["pole_endpoint"], "right")
        self.assertEqual(item["pole_turn"], "1/2")
        self.assertEqual(item["normalized_turn_interval"], ["-1/12", "0"])
        self.assertEqual(item["shifted_cos_coefficients"], {"1": "-1"})
        self.assertEqual(item["shifted_sin_coefficients"], {})
        normalized = item["normalized_v6_result"]
        self.assertEqual(normalized["status"], "CERTIFIED")
        self.assertEqual(normalized["turn_interval"], ["-1/12", "0"])
        self.assertEqual(normalized["distinct_roots_open"], 0)
        self.assertEqual(normalized["multiple_roots_open"], 0)
        self.assertEqual(normalized["right_event"]["relation"], "NEGATIVE")
        self.assertFalse(item["interior_pole_partition_claimed"])

    def test_interior_tan_half_pole_still_refuses(self):
        blocked = {
            "status": "BLOCKED",
            "spans": [{
                "route_kind": "DELEGATED_V6_CONSTANT_MODULATION",
                "route": {
                    "status": "BLOCKED",
                    "reason": "TAN_HALF_POLE_REQUIRES_EXACT_WINDOW_PARTITION",
                },
            }],
        }
        with self.assertRaisesRegex(
            core.ResearchRefusal,
            "V6_TAN_HALF_POLE_NOT_AT_EXACTLY_ONE_ENDPOINT",
        ):
            core._normalized_v6_endpoint_pole_route(
                blocked, {1: [Q(1)]}, {},
                Q(1, 3), Q(1, 3), "source-time-t",
            )

    def test_half_turn_or_wider_endpoint_pole_window_refuses(self):
        blocked = {
            "status": "BLOCKED",
            "spans": [{
                "route_kind": "DELEGATED_V6_CONSTANT_MODULATION",
                "route": {
                    "status": "BLOCKED",
                    "reason": "TAN_HALF_POLE_REQUIRES_EXACT_WINDOW_PARTITION",
                },
            }],
        }
        with self.assertRaisesRegex(
            core.ResearchRefusal,
            "V6_ENDPOINT_POLE_WINDOW_NOT_STRICTLY_SHORTER_THAN_HALF_TURN",
        ):
            core._normalized_v6_endpoint_pole_route(
                blocked, {1: [Q(1)]}, {},
                Q(0), Q(1, 2), "source-time-t",
            )

    def test_nonconstant_modulation_cannot_use_v6_pole_normalization(self):
        blocked = {
            "status": "BLOCKED",
            "spans": [{
                "route_kind": "DELEGATED_V6_CONSTANT_MODULATION",
                "route": {
                    "status": "BLOCKED",
                    "reason": "TAN_HALF_POLE_REQUIRES_EXACT_WINDOW_PARTITION",
                },
            }],
        }
        with self.assertRaisesRegex(
            core.ResearchRefusal,
            "V6_ENDPOINT_POLE_NORMALIZATION_REQUIRES_CONSTANT_MODULATION",
        ):
            core._normalized_v6_endpoint_pole_route(
                blocked, {1: [Q(1), Q(1)]}, {},
                Q(5, 12), Q(1, 12), "source-time-t",
            )

    def test_left_endpoint_pole_and_harmonic_parity_normalize_exactly(self):
        blocked = {
            "status": "BLOCKED",
            "spans": [{
                "route_kind": "DELEGATED_V6_CONSTANT_MODULATION",
                "route": {
                    "status": "BLOCKED",
                    "reason": "TAN_HALF_POLE_REQUIRES_EXACT_WINDOW_PARTITION",
                },
            }],
        }
        adapted, evidence = core._normalized_v6_endpoint_pole_route(
            blocked,
            {1: [Q(1)], 2: [Q(1)]},
            {},
            Q(1, 2), Q(1, 12), "source-time-t",
        )
        self.assertEqual(adapted["status"], "CERTIFIED")
        self.assertEqual(evidence["pole_endpoint"], "left")
        self.assertEqual(evidence["pole_turn"], "1/2")
        self.assertEqual(evidence["normalized_turn_interval"], ["0", "1/12"])
        self.assertEqual(
            evidence["shifted_cos_coefficients"], {"1": "-1", "2": "1"}
        )
        self.assertFalse(evidence["interior_pole_partition_claimed"])

    def test_endpoint_order_is_not_hardcoded_to_simple(self):
        # F(u)=u^2*cos(2*pi*u/8) has an exact order-2 endpoint root.
        child_cos = {1: [Q(0), Q(0), Q(1)]}
        child_sin = {}
        event = _zero_event(child_cos, child_sin, "0", "1/8")
        self.assertEqual(event["relation"], "ZERO", event)
        mult, witness, method = core._checked_endpoint_multiplicity(
            "left", event, {}, child_cos, child_sin, "0", "1/8"
        )
        self.assertEqual(mult, 2)
        self.assertEqual(witness["one_sided_order"], 2)
        self.assertEqual(
            method, "MISSING_ROUTE_MULTIPLICITY_SUPPLIED_BY_EXACT_POINT_JET"
        )

    def test_existing_route_multiplicity_must_agree_with_point_jet(self):
        child_cos = {1: [Q(1)]}
        child_sin = {}
        event = _zero_event(child_cos, child_sin, "1/4", "1/12")
        self.assertEqual(event["relation"], "ZERO", event)
        with self.assertRaisesRegex(
            core.ResearchRefusal,
            "ROUTE_AND_POINT_ENDPOINT_MULTIPLICITY_DISAGREE",
        ):
            core._checked_endpoint_multiplicity(
                "left", event,
                {"endpoint_root_multiplicity": {"left": 2}},
                child_cos, child_sin, "1/4", "1/12",
            )

    def test_nonzero_endpoint_is_rechecked_not_given_multiplicity(self):
        child_cos = {1: [Q(1)]}
        child_sin = {}
        event = _zero_event(child_cos, child_sin, "0", "1/12")
        self.assertEqual(event["relation"], "POSITIVE", event)
        mult, witness, method = core._checked_endpoint_multiplicity(
            "left", event, {}, child_cos, child_sin, "0", "1/12"
        )
        self.assertIsNone(mult)
        self.assertEqual(witness["status"], "EXACT_NONZERO_RATIONAL_POINT")
        self.assertEqual(witness["value_sign"], 1)
        self.assertEqual(method, "EXACT_NONZERO_ENDPOINT_RECHECK")

    def test_internal_cut_multiplicity_mismatch_still_fails_closed(self):
        zero = {"relation": "ZERO"}
        left = {
            "parent_local_interval": ["0", "1/2"],
            "summary": {
                "status": "CERTIFIED",
                "right_event": zero,
                "left_event": {"relation": "POSITIVE"},
                "right_endpoint_multiplicity": 1,
                "left_endpoint_multiplicity": None,
                "distinct_roots_open": 0,
                "multiple_roots_open": 0,
                "all_roots_simple": True,
            },
        }
        right = {
            "parent_local_interval": ["1/2", "1"],
            "summary": {
                "status": "CERTIFIED",
                "left_event": zero,
                "right_event": {"relation": "NEGATIVE"},
                "left_endpoint_multiplicity": 2,
                "right_endpoint_multiplicity": None,
                "distinct_roots_open": 0,
                "multiple_roots_open": 0,
                "all_roots_simple": False,
            },
        }
        result = core.v27._compose_child_summaries([left, right])
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(
            result["reason"],
            "V27_INTERNAL_CUT_ROOT_MULTIPLICITY_MISMATCH_OR_MISSING",
        )

    def test_report_replay_is_exact_and_source_bound(self):
        checked = core.validate_report(self.spec, self.report)
        self.assertEqual(checked, self.report)

    def test_source_mutations_cannot_reuse_report(self):
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
                "EXACT_SOURCE_BOUND_V27_ENDPOINT_MULTIPLICITY_COMPOSITION_RESEARCH",
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
        forged["endpoint_root_multiplicity"] = {"left": 1}
        b = core.attempt(forged)
        self.assertEqual(b["status"], "BLOCKED")
        self.assertIn("UNREVIEWED_SOURCE_AUTHORITY_FIELD", b["reason"])

    def test_report_forgery_and_capability_promotion_refuse(self):
        mutations = (
            lambda r: r.__setitem__("global_multispan_root_count_claimed", True),
            lambda r: r.__setitem__("global_source_knot_deduplication_claimed", True),
            lambda r: r.__setitem__("shared_source_knot_has_two_span_local_endpoint_records", False),
            lambda r: r.__setitem__("global_cross_span_multiplicity_claimed", True),
            lambda r: r.__setitem__("historical_v54_admitted", True),
            lambda r: r.__setitem__("historical_v54_dispositions_changed", True),
            lambda r: r.__setitem__("pb00701_certified", True),
            lambda r: r.__setitem__("mc_b_established", True),
            lambda r: r.__setitem__("mc1_established", True),
            lambda r: r.__setitem__("native_brep_or_step_qualified", True),
            lambda r: r.__setitem__("production_authorized", True),
            lambda r: r["point_jet_supplied_endpoint_multiplicity"][0].__setitem__(
                "multiplicity", 2
            ),
        )
        for mutate in mutations:
            forged = copy.deepcopy(self.report)
            mutate(forged)
            checked = core.validate_report(self.spec, forged)
            self.assertEqual(checked["status"], "BLOCKED", checked)
            self.assertFalse(checked["is_truth_value"])

    def test_oversized_untrusted_report_refuses(self):
        forged = copy.deepcopy(self.report)
        forged["junk"] = "x" * (core.MAX_REPORT_BYTES + 1)
        checked = core.validate_report(self.spec, forged)
        self.assertEqual(checked["status"], "RESOURCE_REFUSAL")
        self.assertFalse(checked["is_truth_value"])

    def test_pinned_custody_domain_and_authority_remain_closed(self):
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
    report = core.analyze_frozen_case(CASE_ID)
    evidence = report["point_jet_supplied_endpoint_multiplicity"][0]
    return {
        "case_id": CASE_ID,
        "status": report["status"],
        "source_sha256": report["source_sha256"],
        "historical_v54_disposition": report["historical_v54_disposition"],
        "supplied_endpoint_side": evidence["side"],
        "supplied_endpoint_multiplicity": evidence["multiplicity"],
        "phase_turn": evidence["witness"]["phase_turn"],
        "first_nonzero_derivative_sign":
            evidence["witness"]["first_nonzero_derivative_sign"],
        "all_shadow_span_routes_certified":
            report["all_shadow_span_routes_certified"],
        "endpoint_pole_normalization_count":
            len(report["endpoint_pole_normalizations"]),
        "endpoint_pole_original_window":
            report["endpoint_pole_normalizations"][0]["original_turn_interval"],
        "endpoint_pole_normalized_window":
            report["endpoint_pole_normalizations"][0]["normalized_turn_interval"],
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
            V27EndpointMultiplicityTests
        )
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
