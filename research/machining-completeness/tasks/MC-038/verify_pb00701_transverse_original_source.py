#!/usr/bin/env python3
"""Adversarial checks for general bounded transverse original-source trig interval proof."""
from __future__ import annotations
import argparse
import copy
import json
import sys
import unittest
from fractions import Fraction as Q

import pb00701_transverse_trig_interval as interval
import pb00701_transverse_original_source as original


def basic_span(kind):
    if kind == "V41":
        return interval.Span(0, 1, 0, Q(1, 4), {
            1: ((Q(-5, 6), Q(5, 2)), (1, Q(-3, 2))),
            3: ((Q(-1, 6), Q(1, 2)), (0,)),
            4: ((0,), (Q(1, 3), Q(-1, 2)))})
    return interval.Span(0 if kind == "FIRST" else 1,
                         1 if kind == "FIRST" else 2,
                         Q(1, 2), Q(-2, 3), {
        0: (((-95, 100) if kind == "TAIL100" else (5,)), (0,)),
        2: ((Q(1, 100),), (0,)),
        1: ((0,), (2, 4) if kind == "FIRST" else (6,)),
    })


class TransverseResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = original.custody()
        cls.report = original.contract()

    def test_exact_pi_and_trig_controls(self):
        lo, hi = interval.pi_bounds()
        self.assertLess(Q(3), lo)
        self.assertLess(hi, Q(22, 7))
        for value, expected in ((Q(0), (1, 0)),
                                (Q(1, 4), (0, 1)),
                                (Q(-1, 4), (0, -1)),
                                (Q(1, 2), (-1, 0))):
            c, s = interval.trig(value)
            self.assertEqual((c[0], s[0]), tuple(map(Q, expected)))
            self.assertEqual(c[0], c[1])
            self.assertEqual(s[0], s[1])
        cos, sin = interval.trig(Q(1, 12))
        self.assertLessEqual(sin[0], Q(1, 2))
        self.assertGreaterEqual(sin[1], Q(1, 2))
        cos, sin = interval.trig(Q(1, 6))
        self.assertLessEqual(cos[0], Q(1, 2))
        self.assertGreaterEqual(cos[1], Q(1, 2))

    def test_generic_new_source_transverse(self):
        span = interval.Span(0, 1, 0, 0, {0: ((Q(-1, 3), 1), (0,))})
        result = span.prove()
        self.assertEqual(result["complete_simple_root_count"], 1)
        root = next(x for x in result["partition"] if x["kind"] == "ONE_SIMPLE_ROOT")
        a, b = map(Q, root["strict_isolation"])
        self.assertLess(a, Q(1, 3))
        self.assertLess(Q(1, 3), b)
        self.assertEqual(result["endpoint_signs"], [-1, 1])

    def test_generic_v27_v41_proofs_not_historical_counts(self):
        expected = {"V41": 2, "FIRST": 1, "TAIL0": 1, "TAIL100": 1}
        for name, count in expected.items():
            with self.subTest(name=name):
                span = basic_span(name)
                result = span.prove()
                self.assertEqual(result["complete_simple_root_count"], count)
                self.assertEqual(result["historical_child_certified"], False)
                cursor = span.left
                for cell in result["partition"]:
                    left, right = map(Q, cell["interval"])
                    self.assertEqual(left, cursor)
                    self.assertLess(left, right)
                    cursor = right
                self.assertEqual(cursor, span.right)

    def test_real_original_source_binding(self):
        self.assertEqual(set(self.report), set(original.CASES))
        for case in original.CASES:
            with self.subTest(case=case):
                report = self.report[case]
                self.assertEqual(report["complete_simple_open_roots"], 2)
                self.assertEqual(len(report["ordered_implicit_roots"]), 2)
                self.assertEqual(report["historical_v54_disposition"],
                                 self.index[case]["expected"]["v54_disposition"])
                self.assertIs(report["historical_child_certified"], False)
                self.assertIs(report["general_trig_theorem_claimed"], False)
                self.assertIs(report["production_authorized"], False)
                self.assertEqual(report["source_binding_sha256"],
                                 original.source_binding(self.index[case]))
                if case == original.v41.SOURCE_ID:
                    self.assertEqual(report["maximal_physical_signs"], [-1, 1, -1])
                else:
                    self.assertEqual(report["maximal_physical_signs"], [1, -1, 1])

    def test_exact_brackets_stay_inside_prior_source_bounds(self):
        coarse = {
            original.v27.TAIL0: [(Q(3, 4), Q(1)), (Q(9, 8), Q(3, 2))],
            original.v27.TAIL100: [(Q(3, 4), Q(1)), (Q(1), Q(9, 8))],
            original.v41.SOURCE_ID: [(Q(3, 20), Q(1, 5)),
                                     (Q(4, 5), Q(17, 20))],
        }
        for case in original.CASES:
            for event, (left, right) in zip(self.report[case]["ordered_implicit_roots"],
                                            coarse[case]):
                lo, hi = map(Q, event["strict_bracket"])
                self.assertLessEqual(left, lo)
                self.assertLess(lo, hi)
                self.assertLessEqual(hi, right)
                self.assertLessEqual(hi-lo, Q(1, 64))
                self.assertEqual(event["smooth_multiplicity"], 1)

    def test_source_and_owner_falsifiers(self):
        corpus = original.load(original.CORPUS)
        changes = [
            (original.v27.TAIL0, lambda x: x["spec"].__setitem__("phase_turn_rate", "-1/2")),
            (original.v27.TAIL100, lambda x: x["spec"]["cos_splines"]["0"]["controls"].__setitem__(3, "104")),
            (original.v27.TAIL0, lambda x: x["expected"].__setitem__("v54_disposition", "CERTIFIED")),
            (original.v41.SOURCE_ID, lambda x: x["spec"]["sin_splines"]["4"]["controls"].__setitem__(1, "-1/3")),
        ]
        for case, change in changes:
            with self.subTest(case=case):
                forged = copy.deepcopy(corpus)
                row = next(r for r in forged["cases"] if r["id"] == case)
                change(row)
                with self.assertRaises(ValueError):
                    if case == original.v41.SOURCE_ID:
                        original.v41.check_source(forged)
                    else:
                        original.v27.select(forged)

    def test_forged_result_never_admitted(self):
        case = original.v27.TAIL0
        for kind in ("drop_root", "forge_root", "claim", "owner", "source", "proof"):
            with self.subTest(kind=kind):
                bad = copy.deepcopy(self.report[case])
                if kind == "drop_root": bad["ordered_implicit_roots"].pop()
                if kind == "forge_root":
                    bad["ordered_implicit_roots"][0]["strict_bracket"] = ["0", "1/4"]
                if kind == "claim": bad["general_trig_theorem_claimed"] = True
                if kind == "owner": bad["ordered_implicit_roots"][0]["owner"] = "fake"
                if kind == "source": bad["source_binding_sha256"] = "0"*64
                if kind == "proof":
                    bad["per_original_span"][0]["proof"]["partition"].pop()
                with self.assertRaises(original.InvalidOriginal):
                    original.validate_submitted(case, bad)

    def test_tangency_and_identity_zero_refuse_not_truth(self):
        for polynom in ((Q(1, 9), Q(-2, 3), 1), (Q(0),)):
            span = interval.Span(0, 1, 0, 0, {0: (polynom, (0,))})
            result = interval.attempt(span, max_depth=12)
            self.assertEqual(result["status"], "RESOURCE_REFUSAL")
            self.assertIs(result["is_truth_value"], False)
        endpoint = interval.Span(0, 1, 0, 0, {0: ((0, 1), (0,))})
        self.assertEqual(interval.attempt(endpoint, max_depth=12)["status"],
                         "RESOURCE_REFUSAL")

    def test_resource_and_unsupported_grammar_refuse(self):
        for source in (
            lambda: interval.Span(0, 1, 0, Q(1, 4), {1: ((1.,), (0,))}),
            lambda: interval.Span(0, 1, 0, Q(1, 4), {9: ((1,), (0,))}),
            lambda: interval.Span(0, 1, 0, Q(1, 4), {1: ((1, 2, 3, 4, 5), (0,))}),
        ):
            with self.assertRaises(interval.Refusal): source()
        self.assertEqual(interval.attempt(basic_span("V41"), max_nodes=1)["status"],
                         "RESOURCE_REFUSAL")

    def test_unchanged_authority_and_source_pins(self):
        for path, sha in original.PINS.items():
            self.assertEqual(original.git_blob(path), sha)
        self.assertEqual(len(original.load(original.DOMAIN)["coverage_rule"][
            "required_operation_ids"]), 26)
        authority = original.load(original.AUTH)
        self.assertFalse(authority["production_authorized"])
        self.assertEqual(authority["capability_status"], "NOT_ESTABLISHED")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("specify --contract and/or --self-test")
    if args.contract:
        for case, report in original.contract().items():
            print(json.dumps({"case": case,
                              "status": report["status"],
                              "root_brackets": [r["strict_bracket"] for r in
                                               report["ordered_implicit_roots"]],
                              "signs": report["maximal_physical_signs"],
                              "historical_child_certified": False},
                             sort_keys=True))
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(TransverseResearchTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == "__main__":
    main()
