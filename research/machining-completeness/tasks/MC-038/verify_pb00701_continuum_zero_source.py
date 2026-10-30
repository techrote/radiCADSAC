#!/usr/bin/env python3
"""Adversarial proofs for exact original-source closed continuum-zero semantics.

Distinct typed continuum event grammar; no finite-root event or V54 owner edit.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction as Q
import json
import sys
import unittest

import pb00701_continuum_zero_source as core


def bezier(*controls, degree=0, knots=None):
    if knots is None:
        knots = ["0"] * (degree + 1) + ["1"] * (degree + 1)
    return {"degree": degree, "knots": list(knots),
            "controls": [str(x) for x in controls]}


def source(cos=None, sin=None, offset="0", rate="1/4", hi="1"):
    return {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "cos_splines": cos if cos is not None else {"0": bezier("0")},
        "sin_splines": sin if sin is not None else {},
        "parameter_lo": "0", "parameter_hi": hi,
        "phase_turn_offset": offset, "phase_turn_rate": rate,
        "source_parameter_id": "synthetic-zero-source-u",
    }


class ContinuumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.row, cls.corpus = core.load_original_case()
        cls.proof = core.prove_closed_zero(cls.row["spec"])
        cls.report = core.expected_record()

    def test_01_frozen_v53_v54_identity_original_source_bound(self):
        self.assertEqual(cls_case := self.row["id"], core.TARGET)
        self.assertEqual(self.row["expected"]["v54_disposition"], "BLOCKED")
        self.assertEqual(self.row["expected"]["observed"]["spans"][0][2],
                         "TRIGONOMETRIC_IDENTITY_ZERO_REQUIRES_SEPARATE_SEMANTIC_HANDLING")
        self.assertEqual(self.proof["source_sha256"], core.TARGET_SHA256)
        self.assertEqual(self.proof["source_parameter_id"], "v52-original-source")
        self.assertEqual(self.proof["source_interval"], ["0", "1"])
        self.assertEqual(self.proof["original_source_edges"], ["0", "1"])
        self.assertEqual(self.proof["original_open_span_identity"][0][
            "identity_status"], "IDENTITY_ZERO")
        self.assertEqual(self.proof["original_amplitude_channel_continuity"][0][
            "original_piece_endpoint_values"], [{"at_left": "0", "at_right": "0"}])
        self.assertFalse(self.proof["general_PB00701_closed"])

    def test_02_continuum_zero_is_not_finite_root_list_or_zero_roots(self):
        z = self.proof["zero_set"]
        self.assertEqual(z["kind"], "CLOSED_CONTINUUM_ZERO_COMPONENT")
        self.assertEqual(z["closed_source_interval"], ["0", "1"])
        self.assertEqual(z["cardinality"], "UNCOUNTABLY_INFINITE")
        self.assertIsNone(z["isolated_root_count"])
        self.assertFalse(z["isolated_finite_root_list_applicable"])
        self.assertFalse(z["ordered_sign_cells_applicable"])
        self.assertTrue(z["every_closed_source_point_is_zero"])
        # For any finite proposed root set, this constructive rational
        # pigeonhole challenge gives a point in (0,1) absent from it.
        finite = [Q(1,2), Q(1,3), Q(1,4), Q(1,5)]
        candidates = [Q(1,n+2) for n in range(len(finite)+1)]
        self.assertTrue(any(x not in finite for x in candidates))

    def test_03_generic_moving_identity_and_two_source_piece_continuity(self):
        moving = source({"0": bezier("0"), "1": bezier("0")},rate="-1/5")
        p = core.prove_closed_zero(moving)
        self.assertEqual(p["zero_set"]["closed_source_interval"], ["0","1"])
        self.assertEqual(len(p["original_amplitude_channel_continuity"]), 2)
        two = source({"0": bezier("0","0",knots=["0","1","2"])},hi="2")
        c = core.prove_closed_zero(two)
        self.assertEqual(c["original_source_edges"],["0","1","2"])
        self.assertEqual(len(c["original_open_span_identity"]),2)
        self.assertEqual(c["original_amplitude_channel_continuity"][0][
            "source_knots_exactly_continuous"],["1"])
        self.assertEqual(c["zero_set"]["closed_source_interval"],["0","2"])

    def test_04_stationary_exact_cross_harmonic_cancellation(self):
        # At 1/8 turn cos(theta)=sin(theta); C1=+1,S1=-1 cancel.
        s=source(cos={"1":bezier("1")},sin={"1":bezier("-1")},
                 offset="1/8",rate="0")
        p=core.prove_closed_zero(s)
        self.assertEqual(p["original_open_span_identity"][0]["identity_status"],
                         "IDENTITY_ZERO")
        self.assertEqual(p["zero_set"]["cardinality"],"UNCOUNTABLY_INFINITE")
        moved=copy.deepcopy(s)
        moved["phase_turn_rate"]="1/8"
        with self.assertRaisesRegex(core.Refusal,"NONIDENTITY"):
            core.prove_closed_zero(moved)

    def test_05_nonidentity_even_with_interior_or_endpoint_roots_refuses(self):
        # Neither an exact crossing nor a touching is an identity-zero interval.
        crossing=source({"0":bezier("-1/2","1/2",
                                    degree=1,knots=["0","0","1","1"])})
        tangent=source({"0":bezier("1/4","-1/4","1/4",
                                   degree=2,knots=["0","0","0","1","1","1"])})
        endpoint=source({"0":bezier("0","1",degree=1,
                                    knots=["0","0","1","1"])})
        for s in (crossing,tangent,endpoint):
            with self.subTest(s=s),self.assertRaisesRegex(core.Refusal,"NONIDENTITY"):
                core.prove_closed_zero(s)
            refused=core.attempt(s)
            self.assertEqual(refused["status"],"BLOCKED")
            self.assertFalse(refused["is_truth_value"])

    def test_06_individual_channel_discontinuity_refused_conservatively(self):
        # Even if a STATIONARY exact trig cancellation happens separately on
        # each open piece, the stronger channel continuity premise is absent.
        s=source({"1":bezier("1","2",knots=["0","1","2"])},
                 {"1":bezier("-1","-2",knots=["0","1","2"])},
                 offset="1/8",rate="0",hi="2")
        with self.assertRaisesRegex(core.Refusal,"CONTINUITY"):
            core.prove_closed_zero(s)
        self.assertFalse(core.attempt(s)["is_truth_value"])
        mixed=source({"0":bezier("0","1",knots=["0","1","2"])},hi="2")
        with self.assertRaises(core.Refusal):
            core.prove_closed_zero(mixed)

    def test_07_source_endpoints_and_knot_semantics_fail_closed(self):
        original=copy.deepcopy(self.row["spec"])
        attacks=[
            lambda s:s["cos_splines"]["0"]["knots"].__setitem__(1,"2"),
            lambda s:s["cos_splines"]["0"].__setitem__("controls",["0","0"]),
            lambda s:s["cos_splines"]["0"].__setitem__("degree",1),
            lambda s:s["cos_splines"]["0"]["controls"].__setitem__(0,"0.0"),
            lambda s:s.__setitem__("parameter_hi","2"),
            lambda s:s.__setitem__("phase_turn_rate","0.25"),
            lambda s:s.__setitem__("source_parameter_id",""),
            lambda s:s.__setitem__("parameter_projection","v52-original-source"),
            lambda s:s["sin_splines"].__setitem__("0",bezier("0")),
            lambda s:s["cos_splines"].__setitem__("-1",bezier("0")),
        ]
        for change in attacks:
            s=copy.deepcopy(original)
            change(s)
            with self.subTest(change=str(change)):
                self.assertFalse(core.attempt(s)["status"] ==
                                 "COMPLETE_CLOSED_CONTINUUM_ZERO_SOURCE_RESEARCH")
        unclamped=source({"0":bezier("0","0",knots=["0","1","2"])})
        self.assertEqual(core.attempt(unclamped)["status"],"BLOCKED")

    def test_08_excess_clamp_and_internal_knot_multiplicity_refused(self):
        # These vectors pass a superficial prefix/suffix clamp check but
        # exceed valid degree+1 knot multiplicity. Original B-spline validity
        # must be decided BEFORE promoting any identity-zero interval.
        excessive_endpoint = source({
            "0": bezier("0","0","0",degree=1,
                        knots=["0","0","0","1","1"])})
        self.assertEqual(core.attempt(excessive_endpoint)["status"],"BLOCKED")
        excessive_interior = source({
            "0": bezier("0","0","0","0","0",degree=1,
                        knots=["0","0","1","1","1","2","2"])},hi="2")
        self.assertEqual(core.attempt(excessive_interior)["status"],"BLOCKED")
        for bad in (excessive_endpoint, excessive_interior):
            with self.assertRaises(core.Refusal):
                core.guard_original_source(bad)

    def test_09_lowerer_untrusted_exceptions_are_typed_nontruth(self):
        # A malformed source which escapes a future preflight should still
        # produce a deterministic BLOCKED result, not raise to the consumer.
        original = core.original_piece_channel_continuity
        try:
            def parser_fails(*args, **kwargs):
                raise ValueError("simulated historical B-spline parser refusal")
            core.original_piece_channel_continuity = parser_fails
            result = core.attempt(source())
            self.assertEqual(result["status"], "BLOCKED")
            self.assertEqual(
                result["reason"], "INVALID_EXACT_ORIGINAL_SOURCE_LOWERER_OR_INPUT")
            self.assertFalse(result["is_truth_value"])
        finally:
            core.original_piece_channel_continuity = original

    def test_10_resource_budget_and_typed_nontruth(self):
        identity=source({"0":bezier("0")},offset="1/257",rate="0")
        result=core.attempt(identity)
        self.assertEqual(result["status"],"RESOURCE_REFUSAL")
        self.assertFalse(result["is_truth_value"])
        huge=source()
        huge["source_parameter_id"]="x" * 10000
        self.assertFalse(core.attempt(huge)["is_truth_value"])
        many=source()
        many["cos_splines"]={str(h):bezier("0") for h in range(13)}
        self.assertFalse(core.attempt(many)["is_truth_value"])
        with self.assertRaisesRegex(core.Refusal,"RESOURCE_REFUSAL"):
            core.bounded_json({"payload":"a"*(core.MAX_BYTES+1)})
        cycle=[]
        cycle.append(cycle)
        with self.assertRaisesRegex(core.Refusal,"RESOURCE_REFUSAL"):
            core.bounded_json(cycle)
        with self.assertRaises(core.Refusal):
            core.bounded_json({"binary":0.2})

    def test_11_six_case_union_preserves_prior_five_original_sources(self):
        rec=self.report
        sel=rec["separate_source_zero_set_views"]
        self.assertEqual(sel["kind"],"DISJOINT_FINITE_OR_CONTINUUM_ZERO_SET")
        self.assertEqual(sel["selected_continuum_original_case_id"],core.TARGET)
        self.assertEqual(len(sel["selected_prior_finite_case_ids"]),5)
        self.assertNotIn(core.TARGET,sel["selected_prior_finite_case_ids"])
        self.assertTrue(sel["finite_event_semantics_never_used_for_continuum"])
        self.assertTrue(core.verify_record(rec))
        self.assertEqual(rec["selected_six_source_only_overlay"][
            "historical_route_refusals_not_in_these_six"],14)
        self.assertEqual(len(rec["selected_six_source_only_overlay"][
            "remaining_historical_case_ids"]),14)
        self.assertTrue(rec["selected_six_source_only_overlay"][
            "not_a_global_reconciled_post_v54_census"])
        self.assertEqual(rec["historical_v54"],
                         {"source_cases":121,"route_refusals":20,
                          "missing_ordered_span_premises":30,
                          "original_route_dispositions_unchanged":True})

    def test_12_forged_root_cardinality_source_identity_and_gate_refuse(self):
        for mutation in [
            lambda x:x["separate_source_zero_set_views"]["continuum"][
                "zero_set"].update(isolated_root_count=0),
            lambda x:x["separate_source_zero_set_views"]["continuum"][
                "zero_set"].update(cardinality="FINITE"),
            lambda x:x["separate_source_zero_set_views"]["continuum"][
                "zero_set"].update(every_closed_source_point_is_zero=False),
            lambda x:x["separate_source_zero_set_views"]["continuum"][
                "source_interval"].__setitem__(1,"2"),
            lambda x:x["separate_source_zero_set_views"].update(
                selected_continuum_original_case_id=
                x["separate_source_zero_set_views"]["selected_prior_finite_case_ids"][0]),
            lambda x:x["selected_six_source_only_overlay"].update(
                historical_route_refusals_not_in_these_six=13),
            lambda x:x["historical_v54"].update(route_refusals=14),
            lambda x:x["gates"].update({"MC-B":"ESTABLISHED"}),
            lambda x:x["gates"].update(production_authorized=True),
        ]:
            record=copy.deepcopy(self.report)
            mutation(record)
            with self.subTest(mutation=str(mutation)):
                with self.assertRaises(core.Refusal):
                    core.verify_record(record)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--contract",action="store_true")
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if not (a.contract or a.self_test):
        p.error("choose --contract and/or --self-test")
    if a.contract:
        loaded=json.loads(core.MACHINE.read_text(encoding="utf-8"))
        core.verify_record(loaded)
        print("PASS: exact frozen original V6 identity-zero => closed [0,1] continuum zero")
        print("PASS: selected 5 finite + 1 continuum source-only overlay: 20 -> 14")
        print("PASS: historical V54 121/20/30 unchanged; PB-007/MC-B/MC-1 remain open")
    if a.self_test:
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(ContinuumTests)
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            sys.exit(1)


if __name__=="__main__":
    main()
