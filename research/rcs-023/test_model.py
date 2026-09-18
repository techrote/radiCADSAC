#!/usr/bin/env python3
"""Adversarial and boundary tests for RCS-023."""
from __future__ import annotations

from decimal import Decimal as D
import unittest

from model import (
    BudgetError,
    BudgetTrace,
    Contribution,
    Interval,
    affine_pipeline_bound,
    classify_contact,
    classify_positive_removal,
    compose_conservative,
    correlated_linear_bound,
    export_decision,
    representation_status,
    rss_symmetric,
    semantic_no_change,
)


class IntervalTests(unittest.TestCase):
    def test_rejects_inverted_interval(self):
        with self.assertRaises(BudgetError):
            Interval(D("1"), D("-1"))

    def test_conservative_composition_keeps_asymmetry(self):
        got = compose_conservative([Interval(D("-2"), D("3")), Interval(D("-5"), D("1"))])
        self.assertEqual((got.low_mm, got.high_mm), (D("-7"), D("4")))

    def test_rotation_uses_conservative_small_angle_bound(self):
        t = BudgetTrace("rot", {"journal_event_id": "j", "revision_id": "r", "body_ids": ["b"], "semantic_operation": "turning.external"})
        disp = t.add_rotation_bound(stage="frame", radius_mm="100", angle_nrad="5", basis="test")
        self.assertEqual(disp, D("0.000000500"))


class SafetySemanticsTests(unittest.TestCase):
    def test_contact_boundary_is_pending_not_snapped(self):
        u = Interval.symmetric("0.000010")
        self.assertEqual(classify_contact("-0.000010", u)["status"], "accepted_pending")
        self.assertEqual(classify_contact("0", u)["status"], "accepted_pending")
        self.assertEqual(classify_contact("0.000010", u)["status"], "accepted_pending")

    def test_decisive_contact_sides(self):
        u = Interval.symmetric("0.000010")
        self.assertEqual(classify_contact("-0.000020", u)["status"], "decisively_positive_material_change")
        self.assertEqual(classify_contact("0.000020", u)["status"], "decisively_no_material_change")

    def test_positive_sub_tolerance_removal_never_becomes_noop(self):
        got = classify_positive_removal("0.000001", Interval.symmetric("0.000005"))
        self.assertEqual(got["status"], "accepted_pending")
        self.assertTrue(got["commanded_positive_intent_preserved"])

    def test_semantic_retrace_needs_proof(self):
        self.assertEqual(semantic_no_change(proof=None)["status"], "accepted_pending")
        self.assertEqual(semantic_no_change(proof="same durable semantic envelope")["status"], "decisively_no_material_change")

    def test_representation_must_reconcile_before_export(self):
        self.assertEqual(representation_status(representation_bound_mm="0.000006", representation_budget_mm="0.000010", reconciled=False), "bounded_representation_inexact")


class CompositionTests(unittest.TestCase):
    def test_rss_is_forbidden_without_independence_evidence(self):
        with self.assertRaises(BudgetError):
            rss_symmetric(["0.1", "0.1"], independence_evidence=None)

    def test_correlated_same_sign_witness_exceeds_rss(self):
        rss = rss_symmetric(["0.000001"] * 100, independence_evidence="diagnostic witness")
        self.assertGreater(D("0.000100"), rss)

    def test_cancellation_requires_shared_source_proof(self):
        with self.assertRaises(BudgetError):
            correlated_linear_bound("0.001", [1, -1], shared_source_proof=None)
        self.assertEqual(correlated_linear_bound("0.001", [1, -1], shared_source_proof="same calibration residual"), 0)

    def test_provider_handoff_sums_source_conversion_destination(self):
        got = compose_conservative([Interval.symmetric("0.000008"), Interval.symmetric("0.000006"), Interval.symmetric("0.000004")])
        self.assertEqual(got.max_abs_mm, D("0.000018"))

    def test_order_sensitive_stage_gains(self):
        first = affine_pipeline_bound([("a", 2, "0.000020"), ("b", 1, "0.000005")])
        second = affine_pipeline_bound([("b", 2, "0.000005"), ("a", 1, "0.000020")])
        self.assertEqual(first, D("0.000045"))
        self.assertEqual(second, D("0.000030"))
        self.assertNotEqual(first, second)


class ExportTests(unittest.TestCase):
    def trace(self, half: str) -> BudgetTrace:
        t = BudgetTrace("x", {"journal_event_id": "j", "revision_id": "r", "body_ids": ["b"], "semantic_operation": "milling.general"})
        t.add_symmetric(stage="provider", channel="numerical_algorithm", half_width_mm=half, basis="test")
        return t

    def test_exact_budget_boundary_passes(self):
        got = export_decision(self.trace("0.000020"), max_surface_deviation_mm="0.000020", max_dimension_error_mm="0.000020", reconciliation_complete=True)
        self.assertEqual(got["status"], "export_eligible")

    def test_over_budget_fails_closed(self):
        got = export_decision(self.trace("0.0000201"), max_surface_deviation_mm="0.000020", max_dimension_error_mm="0.000020", reconciliation_complete=True)
        self.assertEqual(got["status"], "error_budget_breach")

    def test_unknown_channel_refuses_even_when_known_bound_is_small(self):
        t = self.trace("0.000001")
        t.mark_unresolved("unmeasured fit")
        got = export_decision(t, max_surface_deviation_mm="1", max_dimension_error_mm="1", reconciliation_complete=False)
        self.assertEqual(got["status"], "refused_accuracy_unproven")

    def test_manufacturing_tolerance_cannot_hide_unknown_numerics(self):
        t = self.trace("0.000001")
        t.mark_unresolved("provider numerical error unknown")
        got = export_decision(t, max_surface_deviation_mm="10", max_dimension_error_mm="10", reconciliation_complete=False)
        self.assertEqual(got["status"], "refused_accuracy_unproven")

    def test_manufacturing_requirement_is_not_composable_error(self):
        with self.assertRaises(BudgetError):
            Contribution(stage="requirement", channel="manufacturing_requirement", bound=Interval.symmetric("0.1"), basis="must remain a comparison budget")

    def test_unknown_channel_name_rejected(self):
        with self.assertRaises(BudgetError):
            Contribution(stage="x", channel="magic_epsilon", bound=Interval.symmetric("1"), basis="unsafe")

    def test_provider_private_identity_rejected_from_durable_context(self):
        with self.assertRaises(BudgetError):
            BudgetTrace("x", {"journal_event_id": "j", "TopoDS_handle": "secret"})


if __name__ == "__main__":
    unittest.main()
