#!/usr/bin/env python3
"""Reproduce source-pinned V27/V41 child views and adversarial fail-closed tests."""
from __future__ import annotations

import argparse
import copy
import json
import sys
import unittest
from pathlib import Path

import pb00701_pinned_trig_child_views as core


class PinnedChildViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proofs = core.replay_original_proofs()
        cls.valid = {case_id: core.reference_view(case_id, cls.proofs)
                     for case_id in core.CASES}

    def test_all_fixed_original_sources_compose_without_numeric_roots(self):
        for case_id, view in self.valid.items():
            with self.subTest(case_id=case_id):
                result = core.compose(view)
                self.assertEqual(result["status"],
                                 "PINNED_TRIGONOMETRIC_CHILD_VIEWS_RECONCILED_RESEARCH_ONLY")
                self.assertEqual(result["distinct_open_roots_proved_for_this_fixed_source"], 2)
                self.assertEqual(len(result["ordered_implicit_root_events"]), 2)
                self.assertEqual(len(result["maximal_open_physical_sign_cells"]), 3)
                self.assertFalse(result["exact_root_coordinates_claimed"])
                for name in ("historical_child_certified",
                             "general_v27_v41_theorem_claimed",
                             "pb00701_certified", "mc_b_established",
                             "mc1_established", "native_brep_or_step_qualified",
                             "production_authorized"):
                    self.assertIs(result[name], False)

    def test_v27_two_span_original_physical_join(self):
        for case_id in (core.v27.TAIL0, core.v27.TAIL100):
            result = core.compose(self.valid[case_id])
            self.assertEqual([x["sign"] for x in
                              result["maximal_open_physical_sign_cells"]],
                             ["POSITIVE", "NEGATIVE", "POSITIVE"])
            self.assertEqual(result["true_source_knots"],
                             [{"position": "1", "left_sign": "NEGATIVE",
                               "right_sign": "NEGATIVE", "is_physical_zero": False}])
            self.assertEqual([x["source_span"] for x in
                              result["ordered_implicit_root_events"]],
                             [["0", "1"], ["1", "2"]])
            self.assertEqual(result["proof_cuts_not_physical_events"],
                             ["3/4", "1", "9/8", "3/2"])

    def test_v27_mixed_original_owners_preserved(self):
        a = core.compose(self.valid[core.v27.TAIL0])
        b = core.compose(self.valid[core.v27.TAIL100])
        self.assertEqual([x["strict_bracket"] for x in
                          a["ordered_implicit_root_events"]],
                         [["3/4", "1"], ["9/8", "3/2"]])
        self.assertEqual([x["strict_bracket"] for x in
                          b["ordered_implicit_root_events"]],
                         [["3/4", "1"], ["1", "9/8"]])
        self.assertEqual(self.valid[core.v27.TAIL0]["children"][1]["owner"],
                         core.v27.OWNER)
        self.assertEqual(self.valid[core.v27.TAIL100]["children"][1]["owner"],
                         core.v27.V19)
        self.assertNotEqual(a["source_binding_sha256"],
                            b["source_binding_sha256"])

    def test_v41_two_open_crossings_and_no_knot(self):
        result = core.compose(self.valid[core.v41.SOURCE_ID])
        self.assertEqual([x["sign"] for x in
                          result["maximal_open_physical_sign_cells"]],
                         ["NEGATIVE", "POSITIVE", "NEGATIVE"])
        self.assertEqual([x["strict_bracket"] for x in
                          result["ordered_implicit_root_events"]],
                         [["3/20", "1/5"], ["4/5", "17/20"]])
        self.assertEqual(result["true_source_knots"], [])
        self.assertEqual(result["proof_cuts_not_physical_events"],
                         ["3/20", "1/5", "4/5", "17/20"])

    def test_missing_or_reversed_or_extra_root_fails_closed(self):
        for case_id in core.CASES:
            for mutation in ("omit", "duplicate", "reverse", "invent_coordinate"):
                with self.subTest(case_id=case_id, mutation=mutation):
                    x = copy.deepcopy(self.valid[case_id])
                    roots = x["children"][0]["roots"]
                    if mutation == "omit":
                        roots.clear()
                    elif mutation == "duplicate":
                        roots.append(copy.deepcopy(roots[0]))
                    elif mutation == "reverse":
                        roots[0]["left_sign"], roots[0]["right_sign"] = (
                            roots[0]["right_sign"], roots[0]["left_sign"])
                    else:
                        roots[0]["exact_coordinate"] = "1/2"
                    with self.assertRaises(core.InvalidView):
                        core.compose(x)

    def test_forged_multiplicity_brackets_and_parity_rejected(self):
        for mutation, value in (
            ("smooth_physical_multiplicity", 2),
            ("smooth_physical_multiplicity", 1.0),
            ("smooth_physical_multiplicity", True),
            ("parity", "EVEN_TANGENCY"),
            ("descriptor", "EXACT_RATIONAL_ROOT"),
            ("strict_bracket", ["1/2", "1"]),
            ("strict_bracket", ["3/4", "3/4"]),
            ("strict_bracket", ["2/4", "1"]),
            ("strict_bracket", [0.75, 1.0]),
        ):
            x = copy.deepcopy(self.valid[core.v27.TAIL0])
            x["children"][0]["roots"][0][mutation] = value
            with self.subTest(mutation=mutation, value=value):
                with self.assertRaises(core.InvalidView):
                    core.compose(x)

    def test_wrong_proof_source_owner_phase_and_producer_rejected(self):
        for field, value in (
            ("source_case_id", core.v27.TAIL100),
            ("original_source_binding_sha256", "0"*64),
            ("source_parameter_id", "local-s"),
            ("proof_family", "COUNT_ONLY_HISTORICAL_CHILD"),
            ("schema", "unsupported-version"),
        ):
            x = copy.deepcopy(self.valid[core.v27.TAIL0])
            x[field] = value
            with self.subTest(field=field):
                with self.assertRaises(core.InvalidView):
                    core.compose(x)
        x = copy.deepcopy(self.valid[core.v27.TAIL100])
        x["children"][1]["owner"] = core.v27.OWNER
        with self.assertRaises(core.InvalidView):
            core.compose(x)

    def test_fake_knot_and_certificate_cuts_rejected(self):
        for mutation in ("knot_zero", "knot_sign", "knot_position",
                         "proof_cut_to_root", "delete_cut", "add_cut"):
            x = copy.deepcopy(self.valid[core.v27.TAIL0])
            if mutation == "knot_zero":
                x["true_source_knots"][0]["is_physical_zero"] = True
            elif mutation == "knot_sign":
                x["true_source_knots"][0]["right_sign"] = "POSITIVE"
            elif mutation == "knot_position":
                x["true_source_knots"][0]["position"] = "3/2"
            elif mutation == "proof_cut_to_root":
                x["children"][1]["roots"][0]["strict_bracket"] = ["1", "1"]
            elif mutation == "delete_cut":
                x["certificate_cuts"].pop()
            else:
                x["certificate_cuts"].append("7/4")
            with self.subTest(mutation=mutation):
                with self.assertRaises(core.InvalidView):
                    core.compose(x)

    def test_historical_count_only_assertion_is_not_new_witness(self):
        x = copy.deepcopy(self.valid[core.v41.SOURCE_ID])
        for claim in ({"root_count": 2}, {"status": "CERTIFIED"},
                      {"historical_v54_disposition_changed": True},
                      {"production_authorized": True}):
            forged = copy.deepcopy(x)
            forged.update(claim)
            with self.assertRaises(core.InvalidView):
                core.compose(forged)

    def test_unsupported_source_and_resource_refusal_not_truth(self):
        x = {"schema": core.SCHEMA, "source_case_id": "new V41 source"}
        result = core.compose(x)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIs(result["is_truth_value"], False)
        self.assertIs(result["production_authorized"], False)
        x = copy.deepcopy(self.valid[core.v27.TAIL0])
        x["extra_material"] = "X"*(core.MAX_PAYLOAD_BYTES+1)
        refused = core.compose(x)
        self.assertEqual(refused["status"], "RESOURCE_REFUSAL")
        self.assertIs(refused["is_truth_value"], False)

    def test_original_source_corpus_mutations_fail_upstream_proofs(self):
        corpus = json.loads(core.CORPUS.read_text())
        v27_bad = copy.deepcopy(corpus)
        row = next(r for r in v27_bad["cases"] if r["id"] == core.v27.TAIL0)
        row["spec"]["phase_turn_rate"] = "-1/2"
        with self.assertRaises(ValueError):
            core.v27.analyze(v27_bad)
        v41_bad = copy.deepcopy(corpus)
        row = next(r for r in v41_bad["cases"] if r["id"] == core.v41.SOURCE_ID)
        row["spec"]["cos_splines"]["3"]["controls"][1] = "1/2"
        with self.assertRaises(ValueError):
            core.v41.analyze(v41_bad)

    def test_exact_pins_and_26_operation_authority(self):
        self.assertEqual(core.git_blob(core.CORPUS), core.CORPUS_BLOB)
        self.assertEqual(core.git_blob(core.DOMAIN), core.DOMAIN_BLOB)
        self.assertEqual(core.git_blob(core.AUTH), core.AUTH_BLOB)
        self.assertEqual(core.git_blob(core.TASK /
                         "verify_pb00701_v27_fixed_source_order.py"),
                         core.V27_PROOF_BLOB)
        self.assertEqual(core.git_blob(core.TASK /
                         "verify_pb00701_v41_v13_fixed_source_order.py"),
                         core.V41_PROOF_BLOB)
        programme = json.loads((core.ROOT /
            "research/machining-completeness/programme-v1.json").read_text())
        self.assertEqual(programme["capability_status"], "NOT_ESTABLISHED")
        self.assertIs(programme["production_authorized"], False)
        domain = json.loads(core.DOMAIN.read_text())
        self.assertEqual(len(domain["coverage_rule"]["required_operation_ids"]), 26)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("use --contract and/or --self-test")
    if args.contract:
        proofs = core.replay_original_proofs()
        for case_id in core.CASES:
            report = core.compose(core.reference_view(case_id, proofs))
            print(json.dumps({
                "case": case_id, "status": report["status"],
                "root_brackets": [x["strict_bracket"] for x in
                                  report["ordered_implicit_root_events"]],
                "signs": [x["sign"] for x in
                          report["maximal_open_physical_sign_cells"]],
                "historical_child_certified": report["historical_child_certified"],
            }, sort_keys=True))
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(PinnedChildViewTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
