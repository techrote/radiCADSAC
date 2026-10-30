#!/usr/bin/env python3
"""Adversarial verification for frozen V44 proof-cut/root-set partition."""
from __future__ import annotations

import argparse
import copy
import json
import sys
import unittest
from unittest.mock import patch

import pb00701_v44_algebraic_cut_root_partition as core


class V44ProofCutRootPartitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = core.prove()

    def test_frozen_v44_complete_physical_root_set_is_partitioned(self):
        r = self.report
        self.assertEqual(
            r["status"],
            "EXACT_FROZEN_V44_PROOF_CUT_ROOT_SET_PARTITION_RESEARCH",
        )
        self.assertEqual(r["frozen_case_id"], core.CASE_ID)
        self.assertEqual(r["historical_v54_disposition"], "BLOCKED")
        self.assertEqual(
            r["historical_v44_blocker"],
            "ALGEBRAIC_ORIENTATION_COORDINATE_CERTIFIED_BUT_EXACT_CONSUMPTION_AUTHORITY_MISSING",
        )
        self.assertEqual(r["complete_physical_root_count"], 1)
        self.assertEqual(sum(r["proof_cell_open_root_counts"]), 1)
        self.assertTrue(r["root_count_conserved_across_proof_cells"])
        self.assertEqual(
            r["proof_cell_open_root_counts"]
            [r["root_occupying_proof_cell_index"]], 1
        )

    def test_physical_root_is_simple_and_source_endpoints_are_opposite(self):
        r = self.report
        root = r["physical_root"]
        self.assertEqual(root["smooth_multiplicity"], 1)
        self.assertIn(root["derivative_sign"], (-1, 1))
        self.assertEqual(root["left_sign"], -root["right_sign"])
        self.assertEqual(
            r["physical_endpoint_signs"],
            [root["left_sign"], root["right_sign"]],
        )
        lo, hi = map(core.Q, root["strict_isolation"])
        self.assertLess(lo, hi)
        self.assertGreaterEqual(r["physical_partition_nodes"], 1)

    def test_ordered_proof_cuts_switch_side_at_most_once(self):
        rels = [
            x["relation_to_physical_root"]
            for x in self.report["proof_cut_relations"]
        ]
        self.assertTrue(rels)
        seen_after = False
        before = 0
        for rel in rels:
            self.assertIn(
                rel,
                ("CUT_BEFORE_PHYSICAL_ROOT", "PHYSICAL_ROOT_BEFORE_CUT"),
            )
            if rel == "PHYSICAL_ROOT_BEFORE_CUT":
                seen_after = True
            else:
                self.assertFalse(seen_after)
                before += 1
        self.assertEqual(before, self.report["root_occupying_proof_cell_index"])
        self.assertEqual(
            len(rels), self.report["ordered_proof_cut_count"]
        )

    def test_algebraic_cut_is_exact_nonzero_event_neutral_boundary(self):
        r = self.report
        self.assertIn(r["algebraic_cut_endpoint_relation"],
                      ("POSITIVE", "NEGATIVE"))
        self.assertEqual(r["algebraic_cut_physical_multiplicity"], 0)
        self.assertFalse(r["algebraic_cut_is_physical_event"])
        self.assertTrue(r["all_proof_cuts_are_event_neutral"])
        algebraic = [
            x for x in r["proof_cut_relations"]
            if x["coordinate"]["kind"] == "ISOLATED_REAL_ROOT"
        ]
        self.assertEqual(len(algebraic), 1)
        self.assertFalse(
            any(x["proof_cut_is_physical_event"]
                for x in r["proof_cut_relations"])
        )

    def test_v46_endpoint_and_v41_cut_identity_uses_exact_gcd_sturm(self):
        self.assertEqual(
            self.report["algebraic_cut_identity_method"],
            "EXACT_POLYNOMIAL_GCD_PLUS_STURM_COMMON_ROOT",
        )
        # Overlapping rational intervals are not root identity. Replace the
        # V46 minimal factor with a distinct polynomial while retaining the
        # same interval; the candidate must refuse rather than merge by overlap.
        endpoint_report, endpoint = core._algebraic_endpoint(
            core.frozen_row()["spec"]
        )
        forged_endpoint = copy.deepcopy(endpoint)
        forged_endpoint["field"]["minimal_polynomial"] = [-1, 0, 3]
        with patch.object(
            core, "_algebraic_endpoint",
            return_value=(endpoint_report, forged_endpoint),
        ):
            refused = core.attempt()
        self.assertEqual(refused["status"], "BLOCKED", refused)
        self.assertIn(
            "V46_ENDPOINT_AND_V41_CUT_EXACT_ROOT_IDENTITY_NOT_ESTABLISHED",
            refused["reason"],
        )
        self.assertFalse(refused["is_truth_value"])

    def test_current_v47_sufficient_derivative_route_still_does_not_own_source(self):
        self.assertFalse(self.report["v47_still_certifies_this_frozen_source"])
        self.assertFalse(self.report["closed_child_derivative_theorem_claimed"])
        self.assertFalse(self.report["algebraic_child_reparameterization_claimed"])

    def test_source_bound_cut_order_evidence_is_same_frozen_source(self):
        e = self.report["source_bound_cut_order_evidence"]
        self.assertEqual(e["source_sha256"], self.report["source_sha256"])
        self.assertIn(
            "IRRATIONAL_ALGEBRAIC_ORIENTATION_ROOT_NOT_REPRESENTABLE",
            e["current_v41_boundary"],
        )
        self.assertEqual(
            e["ordered_cut_count"], self.report["ordered_proof_cut_count"]
        )
        self.assertTrue(e["orientation_roots_are_proof_geometry_only"])

    def test_report_replay_is_exact(self):
        self.assertEqual(core.validate_report(self.report), self.report)

    def test_forged_counts_cut_order_and_capability_promotion_refuse(self):
        mutations = (
            lambda x: x.__setitem__("complete_physical_root_count", 2),
            lambda x: x.__setitem__("root_occupying_proof_cell_index", 0),
            lambda x: x["proof_cell_open_root_counts"].append(1),
            lambda x: x["proof_cut_relations"][0].__setitem__(
                "proof_cut_is_physical_event", True),
            lambda x: x.__setitem__("algebraic_cut_is_physical_event", True),
            lambda x: x.__setitem__("root_count_conserved_across_proof_cells", False),
            lambda x: x.__setitem__("algebraic_child_reparameterization_claimed", True),
            lambda x: x.__setitem__("closed_child_derivative_theorem_claimed", True),
            lambda x: x.__setitem__("historical_v54_admitted", True),
            lambda x: x.__setitem__("historical_v54_dispositions_changed", True),
            lambda x: x.__setitem__("pb00701_certified", True),
            lambda x: x.__setitem__("mc_b_established", True),
            lambda x: x.__setitem__("mc1_established", True),
            lambda x: x.__setitem__("native_brep_or_step_qualified", True),
            lambda x: x.__setitem__("production_authorized", True),
        )
        for mutate in mutations:
            forged = copy.deepcopy(self.report)
            mutate(forged)
            checked = core.validate_report(forged)
            self.assertEqual(checked["status"], "BLOCKED", checked)
            self.assertFalse(checked["is_truth_value"])

    def test_cut_omission_or_reordering_in_submitted_report_refuses(self):
        omitted = copy.deepcopy(self.report)
        omitted["proof_cut_relations"].pop()
        checked = core.validate_report(omitted)
        self.assertEqual(checked["status"], "BLOCKED")
        reversed_report = copy.deepcopy(self.report)
        reversed_report["proof_cut_relations"].reverse()
        checked = core.validate_report(reversed_report)
        self.assertEqual(checked["status"], "BLOCKED")

    def test_algebraic_zero_endpoint_cannot_be_partitioned_as_event_neutral(self):
        fake_endpoint = copy.deepcopy(
            core._algebraic_endpoint(core.frozen_row()["spec"])
        )
        fake_endpoint[1]["relation"] = "ZERO"
        fake_endpoint[1]["physical_multiplicity"] = 1
        with patch.object(core, "_algebraic_endpoint", return_value=fake_endpoint):
            refused = core.attempt()
        self.assertEqual(refused["status"], "BLOCKED")
        self.assertFalse(refused["is_truth_value"])

    def test_physical_root_resource_exhaustion_is_nontruth(self):
        refused = core.attempt(max_nodes=1)
        self.assertEqual(refused["status"], "RESOURCE_REFUSAL", refused)
        self.assertFalse(refused["is_truth_value"])

    def test_noncanonical_frozen_source_mutation_refuses(self):
        row = copy.deepcopy(core.frozen_row())
        row["spec"]["phase_turn_rate"] = 0.0625
        with patch.object(core, "frozen_row", return_value=row):
            refused = core.attempt()
        self.assertNotEqual(
            refused.get("status"),
            "EXACT_FROZEN_V44_PROOF_CUT_ROOT_SET_PARTITION_RESEARCH",
            refused,
        )
        self.assertFalse(refused["is_truth_value"])

    def test_full_custody_domain_authority_and_nonpromotion(self):
        core.pins()
        domain = json.loads(core.DOMAIN.read_text())
        authority = json.loads(core.AUTH.read_text())
        self.assertEqual(
            len(domain["coverage_rule"]["required_operation_ids"]), 26
        )
        self.assertFalse(authority["production_authorized"])
        self.assertEqual(authority["capability_status"], "NOT_ESTABLISHED")
        for key in (
            "historical_v54_admitted",
            "historical_v54_dispositions_changed",
            "pb00701_certified",
            "mc_b_established",
            "mc1_established",
            "native_brep_or_step_qualified",
            "production_authorized",
        ):
            self.assertFalse(self.report[key])


def contract():
    r = core.prove()
    return {
        "case_id": r["frozen_case_id"],
        "status": r["status"],
        "source_sha256": r["source_sha256"],
        "historical_v54_disposition": r["historical_v54_disposition"],
        "physical_root_count": r["complete_physical_root_count"],
        "physical_root_strict_isolation":
            r["physical_root"]["strict_isolation"],
        "proof_cut_count": r["ordered_proof_cut_count"],
        "proof_cell_root_counts": r["proof_cell_open_root_counts"],
        "root_cell_index": r["root_occupying_proof_cell_index"],
        "algebraic_cut_relation": r["algebraic_cut_endpoint_relation"],
        "algebraic_cut_identity_method": r["algebraic_cut_identity_method"],
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
            V44ProofCutRootPartitionTests
        )
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
