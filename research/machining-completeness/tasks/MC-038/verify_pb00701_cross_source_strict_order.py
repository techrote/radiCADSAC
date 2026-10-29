#!/usr/bin/env python3
"""Contract and adversarial tests: cross-source root order only if strictly separated."""
from __future__ import annotations

import argparse
import copy
import json
import sys
import unittest
from fractions import Fraction as Q

import pb00701_cross_source_strict_order as core


class CrossSourceStrictOrderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reports = core.dual.catalogue()
        cls.tail0, cls.tail100, cls.v41 = core.dual.CASES

    def result(self, a, i, b, j):
        return core.compare(self.reports[a], i, self.reports[b], j)

    def test_exact_source_custody_and_no_gate_promotion(self):
        core.source_pins()
        self.assertEqual(len(self.reports), 3)
        for case, report in self.reports.items():
            with self.subTest(case=case):
                self.assertEqual(report["source_parameter_id"], core.PARAMETER)
                self.assertEqual(report["complete_open_roots"], 2)
                self.assertEqual(
                    core.dual.validate(report)["status"],
                    "SAME_SOURCE_DUAL_ROOT_PROOFS_RECONCILED")
        auth = json.loads((core.dual.ROOT /
                           "handoffs/current-authority.json").read_text())
        domain = json.loads((core.dual.ROOT /
            "research/machining-completeness/tasks/MC-002/domain-contract-v1.json"
        ).read_text())
        self.assertEqual(auth["capability_status"], "NOT_ESTABLISHED")
        self.assertFalse(auth["production_authorized"])
        self.assertEqual(len(domain["coverage_rule"]["required_operation_ids"]), 26)

    def test_all_v41_versus_both_v27_source_roots_strict_less(self):
        # Original V41/V13 physical zeros lie near .18 and .82; the
        # original V27 first zero is near .99. The proof uses exact
        # disjoint strict rational intervals, never these approximations.
        checked = 0
        for v27 in (self.tail0, self.tail100):
            for i in (0, 1):
                for j in (0, 1):
                    with self.subTest(v27=v27, left=i, right=j):
                        r = self.result(self.v41, i, v27, j)
                        self.assertEqual(r["status"],
                                         "CHECKED_STRICT_PARAMETER_ORDER", r)
                        self.assertEqual(r["relation"], "LESS")
                        self.assertEqual(r["coordinate_id"], "source-time-t")
                        self.assertFalse(r["root_equality_claimed"])
                        self.assertFalse(r["physical_temporal_sequence_claimed"])
                        self.assertFalse(r["mc_b_established"])
                        self.assertFalse(r["production_authorized"])
                        a = tuple(map(Q, r["left_strict_bracket"]))
                        b = tuple(map(Q, r["right_strict_bracket"]))
                        self.assertLessEqual(a[1], b[0])
                        checked += 1
        self.assertEqual(checked, 8)

    def test_different_v27_tail_second_roots_order(self):
        r = self.result(self.tail0, 1, self.tail100, 1)
        self.assertEqual(r["relation"], "GREATER")
        self.assertEqual(self.result(self.tail100, 1, self.tail0, 1)[
            "relation"], "LESS")
        r = self.result(self.tail0, 0, self.tail100, 1)
        self.assertEqual(r["relation"], "LESS")

    def test_cross_case_overlap_never_proves_same_or_different(self):
        # The first V27 spans actually agree as functions, but the
        # complete *whole-source* reports are different. Pure bracket
        # overlap never licenses cross-case equality, even here.
        r = self.result(self.tail0, 0, self.tail100, 0)
        self.assertEqual(r["status"], "BLOCKED")
        self.assertEqual(r["reason"], "OVERLAPPING_BRACKETS_UNRESOLVED")
        self.assertFalse(r["is_truth_value"])
        self.assertFalse(r["root_equality_claimed"])
        self.assertEqual(self.result(self.tail100, 0, self.tail0, 0)[
            "status"], "BLOCKED")

    def test_touching_open_brackets_are_strictly_separated(self):
        self.assertEqual(core._relation((Q(0), Q(1)), (Q(1), Q(2))),
                         "LESS")
        self.assertEqual(core._relation((Q(1), Q(2)), (Q(0), Q(1))),
                         "GREATER")
        with self.assertRaisesRegex(core.Refusal, "OVERLAPPING"):
            core._relation((Q(0), Q(2)), (Q(1), Q(3)))
        with self.assertRaisesRegex(core.Refusal, "NONSTRICT"):
            core._relation((Q(0), Q(0)), (Q(1), Q(2)))

    def test_same_source_must_use_existing_rank_proof(self):
        self.assertEqual(self.result(self.tail0, 0, self.tail0, 1)[
            "status"], "BLOCKED")
        self.assertEqual(self.result(self.tail0, 0, self.tail0, 1)[
            "reason"], "SAME_SOURCE_USE_DUAL_ROOT_RANK_PROOF")

    def test_forged_source_phase_parameter_owner_and_bracket_refuse(self):
        src = self.reports[self.v41]
        target = self.reports[self.tail0]
        mutations = {
            "case": lambda x: x.__setitem__("case_id", "fabricated"),
            "coordinate": lambda x: x.__setitem__(
                "source_parameter_id", "fabricated"),
            "source_digest": lambda x: x.__setitem__(
                "transverse_source_sha256", "0" * 64),
            "phase": lambda x: x.__setitem__(
                "source_phase_turns", ["100", "0"]),
            "owner": lambda x: x["root_matches"][0].__setitem__(
                "owner", "fabricated"),
            "bracket": lambda x: x["root_matches"][0].__setitem__(
                "strict_intersection_bracket", ["0", "1"]),
            "root_count": lambda x: x.__setitem__("complete_open_roots", 1),
            "promotion": lambda x: x.__setitem__("mc_b_established", True),
        }
        for name, mutate in mutations.items():
            with self.subTest(mutation=name):
                altered = copy.deepcopy(src)
                mutate(altered)
                result = core.compare(altered, 0, target, 0)
                self.assertEqual(result["status"], "BLOCKED", result)
                self.assertFalse(result["is_truth_value"])

    def test_bad_ranks_and_unsupported_sources_refuse(self):
        for rank in (-1, 2, "0", True, 1.0):
            with self.subTest(rank=rank):
                result = self.result(self.v41, rank, self.tail0, 0)
                self.assertEqual(result["status"], "BLOCKED")
        bad = core.compare({"case_id": "unsupported"}, 0,
                           self.reports[self.tail0], 0)
        self.assertEqual(bad["status"], "BLOCKED")

    def test_claim_revalidation_prevents_spoofed_equality_and_promotion(self):
        a, b = self.reports[self.v41], self.reports[self.tail0]
        valid = core.compare(a, 1, b, 0)
        self.assertEqual(core.validate_claim(a, 1, b, 0, valid), valid)
        for field, wrong in (
            ("relation", "SAME"),
            ("physical_temporal_sequence_claimed", True),
            ("mc_b_established", True),
            ("left_phase_turns", ["0", "0"]),
            ("left_case_id", "forged"),
            ("left_strict_bracket", ["0", "1"]),
        ):
            if field not in valid:
                continue
            altered = copy.deepcopy(valid)
            altered[field] = wrong
            self.assertEqual(core.validate_claim(a, 1, b, 0, altered)[
                "status"], "BLOCKED", field)
        overlap = self.result(self.tail0, 0, self.tail100, 0)
        self.assertEqual(core.validate_claim(
            self.reports[self.tail0], 0,
            self.reports[self.tail100], 0, overlap)["status"], "BLOCKED")

    def test_nonfinite_and_oversized_reports_refuse_without_truth(self):
        a, b = self.reports[self.v41], self.reports[self.tail0]
        good = core.compare(a, 0, b, 0)
        for forged in (
            dict(good, relation=float("nan")),
            dict(good, padding="!" * 20000),
            [good],
        ):
            refused = core.validate_claim(a, 0, b, 0, forged)
            self.assertIn(refused["status"], ("BLOCKED", "RESOURCE_REFUSAL"))
            self.assertFalse(refused["is_truth_value"])
        huge = dict(a, padding="x"*20000)
        refused = core.compare(huge, 0, b, 0)
        self.assertEqual(refused["status"], "RESOURCE_REFUSAL")
        self.assertFalse(refused["is_truth_value"])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--contract", action="store_true")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if not (args.contract or args.self_test):
        p.error("specify --contract and/or --self-test")
    if args.contract:
        cases = core.dual.CASES
        reports = core.dual.catalogue()
        for a, i, b, j in ((cases[2], 0, cases[0], 0),
                           (cases[0], 1, cases[1], 1),
                           (cases[0], 0, cases[1], 0)):
            out = core.compare(reports[a], i, reports[b], j)
            print(json.dumps({
                "left_case_id": a, "right_case_id": b,
                "left_rank": i, "right_rank": j,
                "status": out["status"],
                "relation": out.get("relation"),
                "reason": out.get("reason"),
                "pb00701_certified": False,
                "mc_b_established": False,
            }, sort_keys=True))
    if args.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(
                CrossSourceStrictOrderTests))
        sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
