#!/usr/bin/env python3
"""Adversarial checks for the frozen-V44 source-coordinate proof-cell atlas."""
from __future__ import annotations

import argparse
import copy
import json
import sys
import unittest
from unittest.mock import patch

import pb00701_v44_source_proof_cell_atlas as atlas

class SourceProofCellAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        atlas.pins()
        cls.source = atlas.previous.prove()
        cls.view = atlas.compose(cls.source)

    def test_frozen_source_and_parent_proof_binding(self):
        v = self.view
        self.assertEqual(v["status"], atlas.SUCCESS)
        self.assertEqual(v["parent_source_sha256"], atlas.SOURCE_SHA256)
        self.assertEqual(v["parent_frozen_case_id"], atlas.previous.CASE_ID)
        self.assertEqual(v["source_parameter_id"],
                         "pb00701-v44-algebraic-orientation")
        self.assertEqual(v["original_source_interval"], ["0", "1"])
        self.assertEqual(v["original_affine_phase"],
                         {"offset": "-1/8", "rate": "1/16"})

    def test_complete_one_root_four_cell_atlas_and_endpoint_signs(self):
        v = self.view
        self.assertEqual(v["source_proof_cut_count"], 3)
        self.assertEqual(v["source_proof_cell_count"], 4)
        self.assertEqual(v["complete_original_source_physical_root_count"], 1)
        cells, bs = v["source_proof_cells"], v["proof_boundaries"]
        self.assertEqual(len(bs), 5)
        self.assertEqual(len(cells), 4)
        self.assertEqual([c["physical_open_root_count"] for c in cells],
                         [0, 1, 0, 0])
        self.assertEqual(v["one_physical_root_cell_index"], 1)
        self.assertEqual(sum(c["physical_open_root_count"] for c in cells), 1)
        self.assertEqual([b["boundary_id"] for b in bs],
                         ["b0", "b1", "b2", "b3", "b4"])
        self.assertEqual(
            [c["left_boundary_id"] for c in cells],
            ["b0", "b1", "b2", "b3"],
        )
        self.assertEqual(
            [c["right_boundary_id"] for c in cells],
            ["b1", "b2", "b3", "b4"],
        )
        self.assertEqual(
            [c["left_nonzero_boundary_sign"] for c in cells],
            [b["physical_value_sign"] for b in bs[:-1]],
        )
        self.assertEqual(
            [c["right_nonzero_boundary_sign"] for c in cells],
            [b["physical_value_sign"] for b in bs[1:]],
        )

    def test_zero_free_cells_have_same_end_sign_and_one_root_cell_crosses(self):
        cells = self.view["source_proof_cells"]
        for i, cell in enumerate(cells):
            self.assertEqual(cell["index"], i)
            if i == 1:
                self.assertEqual(cell["kind"],
                                 "EXACT_SOURCE_ONE_SIMPLE_ROOT_CELL")
                self.assertNotEqual(cell["left_nonzero_boundary_sign"],
                                    cell["right_nonzero_boundary_sign"])
                self.assertIsNone(cell["root_free_constant_sign"])
                witness = cell["one_simple_physical_root_witness"]
                self.assertEqual(witness["smooth_multiplicity"], 1)
                self.assertEqual(witness, self.source["physical_root"])
            else:
                self.assertEqual(cell["kind"],
                                 "EXACT_SOURCE_ROOT_FREE_SIGN_CELL")
                self.assertEqual(cell["left_nonzero_boundary_sign"],
                                 cell["right_nonzero_boundary_sign"])
                self.assertEqual(cell["root_free_constant_sign"],
                                 cell["left_nonzero_boundary_sign"])
                self.assertIsNone(cell["one_simple_physical_root_witness"])

    def test_exact_nonzero_proof_cuts_never_become_physical_events(self):
        self.assertFalse(self.view["proof_cuts_are_events"])
        for b in self.view["proof_boundaries"]:
            self.assertFalse(b["is_physical_zero"])
            self.assertIn(b["physical_value_sign"], ("POSITIVE", "NEGATIVE"))
            if b["kind"] == "EXACT_SOURCE_PROOF_CUT":
                self.assertTrue(b["is_proof_geometry_only"])
                self.assertIn("coordinate_descriptor", b)

    def test_rejected_child_and_programme_promotions_remain_explicit(self):
        self.assertTrue(self.view["source_coordinate_restrictions_only"])
        self.assertEqual(self.view["historical_v54_disposition"], "BLOCKED")
        for field in (
            "actual_algebraic_child_analytic_chart_constructed",
            "closed_child_derivative_theorem_proved",
            "v41_v47_historical_child_route_certified",
            "historical_v54_admitted",
            "pb00701_certified",
            "mc_b_established",
            "mc1_established",
            "native_material_or_step_qualified",
            "production_authorized",
        ):
            self.assertIs(self.view[field], False, field)
        for c in self.view["source_proof_cells"]:
            self.assertIs(c["analytic_algebraic_child_chart_claimed"], False)
            self.assertIs(c["closed_child_derivative_theorem_claimed"], False)

    def test_source_snapshot_forgery_controls(self):
        mutations = (
            lambda s: s.__setitem__("source_sha256", "0" * 64),
            lambda s: s["phase_turn_law"].__setitem__("rate", "1/8"),
            lambda s: s.__setitem__("root_occupying_proof_cell_index", 0),
            lambda s: s["proof_cell_open_root_counts"].__setitem__(1, 0),
            lambda s: s["physical_endpoint_signs"].__setitem__(
                0, -s["physical_endpoint_signs"][0]),
            lambda s: s["physical_root"].__setitem__("smooth_multiplicity", 2),
            lambda s: s["proof_cut_relations"][0].__setitem__(
                "physical_value_sign", 0),
            lambda s: s["proof_cut_relations"][0].__setitem__(
                "proof_cut_is_physical_event", True),
            lambda s: s["proof_cut_relations"][2].__setitem__(
                "relation_to_physical_root", "CUT_BEFORE_PHYSICAL_ROOT"),
            lambda s: s["proof_cut_relations"].pop(),
            lambda s: s.__setitem__("algebraic_child_reparameterization_claimed",
                                    True),
            lambda s: s.__setitem__("historical_v54_admitted", True),
        )
        for i, mutation in enumerate(mutations):
            with self.subTest(forgery=i):
                changed = copy.deepcopy(self.source)
                mutation(changed)
                with self.assertRaises((atlas.Refusal, IndexError, ValueError)):
                    atlas.compose(changed)

    def test_uncertified_algebraic_endpoint_and_refused_source_are_nontruth(self):
        changed = copy.deepcopy(self.source)
        changed["algebraic_cut_physical_multiplicity"] = 1
        with self.assertRaises(atlas.Refusal):
            atlas.compose(changed)
        with patch.object(
            atlas.previous, "prove",
            side_effect=atlas.previous.ResourceRefusal("ISOLATION_EXHAUSTED"),
        ):
            refused = atlas.attempt()
        self.assertEqual(refused["status"], "RESOURCE_REFUSAL")
        self.assertFalse(refused["is_truth_value"])

    def test_adversarial_atlas_mutation_fails_full_source_replay(self):
        forged = copy.deepcopy(self.view)
        forged["source_proof_cells"][0]["root_free_constant_sign"] = "NEGATIVE" \
            if self.view["source_proof_cells"][0]["root_free_constant_sign"] \
            == "POSITIVE" else "POSITIVE"
        checked = atlas.validate_report(forged)
        self.assertEqual(checked["status"], "BLOCKED")
        self.assertFalse(checked["is_truth_value"])
        self.assertIn("FORGED_FROZEN_V44_SOURCE_PROOF_CELL_ATLAS",
                      checked["reason"])

    def test_full_source_rerun_matches_exact_atlas(self):
        checked = atlas.validate_report(self.view)
        self.assertEqual(checked, self.view)

def contract():
    v = atlas.prove()
    return {
        "status": v["status"],
        "source_sha256": v["parent_source_sha256"],
        "source_coordinate_only": v["source_coordinate_restrictions_only"],
        "proof_cell_count": v["source_proof_cell_count"],
        "open_root_counts": [
            c["physical_open_root_count"] for c in v["source_proof_cells"]
        ],
        "root_cell_index": v["one_physical_root_cell_index"],
        "source_boundary_nonzero_signs": [
            b["physical_value_sign"] for b in v["proof_boundaries"]
        ],
        "historical_v54_admitted": v["historical_v54_admitted"],
        "child_analytic_chart_constructed":
            v["actual_algebraic_child_analytic_chart_constructed"],
        "production_authorized": v["production_authorized"],
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
            SourceProofCellAtlasTests
        )
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == "__main__":
    main()
