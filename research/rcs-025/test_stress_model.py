#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("stress_model", HERE / "stress_model.py")
m = importlib.util.module_from_spec(spec)
sys.modules["stress_model"] = m
spec.loader.exec_module(m)


class StressBoundaryTests(unittest.TestCase):
    def test_private_identity_rejected_from_durable_state(self):
        state = m.DurableState("r0", ["body-main"])
        state.lineage_events.append({"relation": "bad", "object_address": "0xdeadbeef"})
        with self.assertRaises(m.ContractError):
            state.view()

    def test_fallback_error_cannot_be_cancelled_without_independent_reconstruction(self):
        with self.assertRaises(m.ContractError):
            m.reconcile_fallback(independent_reconstruction=False)

    def test_fallback_is_not_step_authoritative(self):
        case = m.mill_fallback_brep()
        self.assertEqual(case["budgets"]["pending_status"], "bounded_representation_inexact")
        self.assertEqual(case["transition"][-1], m.PROVIDERS["brep"])
        self.assertEqual(case["step"]["engineering_status"], "interoperability_unqualified")

    def test_curved_nonorthogonal_boundary_is_truthful(self):
        scope = m.mill_fallback_brep()["fallback_scope"]
        self.assertEqual(scope["arbitrary_nonorthogonal_tool_axis"], "refused_unsupported")
        self.assertIn("volume_budget_only", scope["ball_rounded_constant_z"])

    def test_connectivity_query_blocks_before_reconciliation(self):
        case = m.split_merge_pending()
        self.assertFalse(case["pre_reconciliation_connectivity_query"]["body_selection_permitted"])
        self.assertEqual(case["body_count_after_split"], 2)
        self.assertEqual(case["body_count_final"], 1)

    def test_lineage_ambiguity_fails_closed(self):
        case = m.topology_regeneration_and_ambiguity()
        self.assertTrue(case["topology_ids_changed"])
        self.assertTrue(case["durable_body_id_stable"])
        self.assertEqual(case["ambiguous_control"]["engineering_status"], "accepted_pending")
        self.assertFalse(case["ambiguous_control"]["silent_mapping_permitted"])

    def test_threshold_policy_bounds_pending_state(self):
        case = m.repeated_defer_policies()
        self.assertEqual(case["growth_probe"]["hard_peak_pending_units"], 64)
        self.assertEqual(case["growth_probe"]["threshold_peak_pending_units"], 2)
        self.assertGreater(
            case["hard_plus_pending_threshold"]["reconciliation_count"],
            case["hard_semantic_boundaries_only"]["reconciliation_count"],
        )

    def test_replay_equal_after_private_state_discard(self):
        case = m.mixed_replay()
        self.assertTrue(case["provider_private_state_discarded"])
        self.assertTrue(case["replay_invariant_equal"])

    def test_budget_breach_fails_closed_without_tolerance_widening(self):
        case = m.error_budget_controls()
        self.assertEqual(case["within_budget"]["engineering_status"], "interoperability_unqualified")
        self.assertEqual(case["breach"]["engineering_status"], "error_budget_breach")
        self.assertFalse(case["tolerance_widening_permitted"])

    def test_positive_sub_uncertainty_intent_not_erased(self):
        positive = m.error_budget_controls()["positive_sub_uncertainty_removal"]
        self.assertTrue(positive["commanded_positive_intent_preserved"])
        self.assertEqual(positive["status"], "accepted_pending")

    def test_campaign_contract_all_true(self):
        result = m.run_campaign()
        self.assertTrue(all(result["contract_result"].values()))


if __name__ == "__main__":
    unittest.main()
