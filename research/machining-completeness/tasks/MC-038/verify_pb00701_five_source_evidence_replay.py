#!/usr/bin/env python3
"""Adversarial source/semantics/replay tests for five selected frozen cases.

Checks actual pinned source-specific mathematics and a finite normalized event
consumer, not general analytic event decidability or native qualification.
"""
from __future__ import annotations

import argparse
import copy
import json
from fractions import Fraction as Q
from pathlib import Path
import sys
import tempfile
import unittest

import pb00701_five_source_evidence_replay as core

REPORT = core.HERE / "pb00701-five-source-evidence-replay.json"


class FiveSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.expected = core.expected_report()
        cls.views = {v["case_id"]: v for v in cls.expected["source_attested_views"]}
        cls.rows = core.original_corpus()

    def test_01_all_three_source_producers_replayed_and_pinned(self):
        self.assertEqual(set(core.PRODUCERS), {"V27_THREE", "V6_KNOT", "V9_V43"})
        self.assertTrue(core.validate_report(self.actual))
        self.assertEqual(self.actual, self.expected)
        self.assertEqual(len(self.views), 5)
        self.assertEqual(len({v["source_sha256"] for v in self.views.values()}), 5)

    def test_02_historical_census_and_exact_selected_five_overlay(self):
        self.assertEqual(self.expected["frozen_v54"], {
            "source_case_count": 121,
            "historical_route_blocked": 20,
            "historical_missing_order_premises": 30,
            "frozen_historical_dispositions_modified": False,
        })
        result = self.expected["selected_five_case_overlay"]
        self.assertEqual(result["qualified_distinct_source_witnesses"], 5)
        self.assertEqual(result["qualified_v27_child_not_certified_frozen_source_cases"], 4)
        self.assertEqual(result["qualified_v43_refusal_frozen_source_cases"], 1)
        self.assertEqual(result["historical_route_refusals_without_only_these_five_proofs"], 15)
        self.assertEqual(len(result["other_historical_refused_case_ids"]), 15)
        self.assertTrue(result["not_an_exhaustive_combined_post_v54_census"])
        self.assertTrue(result["not_a_generic_V27_or_V43_solver"])
        self.assertEqual(len(set(result["other_historical_refused_case_ids"])
                             & set(self.views)), 0)
        for cid, view in self.views.items():
            self.assertEqual(self.rows[cid]["expected"]["v54_disposition"], "BLOCKED")
            self.assertFalse(view["generic_route_repaired"])

    def test_03_harvested_source_endpoint_not_interpreted_as_open_root(self):
        v = self.views[core.H]
        self.assertEqual(v["source_interval"], ["0", "1"])
        self.assertEqual(v["closed_root_count"], 1)
        self.assertEqual(v["strict_source_open_root_count"], 0)
        self.assertEqual(v["strict_span_open_root_counts"], [0])
        self.assertEqual(v["maximal_open_signs"], ["POSITIVE"])
        e = v["events"][0]
        self.assertEqual(e["location"], "SOURCE_LEFT_ENDPOINT")
        self.assertEqual(e["order"], {"kind": "ONE_SIDED", "right": 1})
        self.assertTrue(core.validate_view(v, self.rows[core.H]))

    def test_04_v8_tangency_and_crossing_with_separate_original_sources(self):
        t0, t100 = self.views[core.V8_0], self.views[core.V8_100]
        self.assertEqual(t0["strict_span_open_root_counts"], [1, 1])
        self.assertEqual(t100["strict_span_open_root_counts"], [1, 0])
        self.assertEqual([e["classification"] for e in t0["events"]],
                         ["TOUCHING", "CROSSING"])
        self.assertEqual(t0["maximal_open_signs"],
                         ["POSITIVE", "POSITIVE", "NEGATIVE"])
        self.assertEqual(t100["maximal_open_signs"],
                         ["POSITIVE", "POSITIVE"])
        self.assertEqual(t0["events"][0]["coordinate"],
                         t100["events"][0]["coordinate"])
        self.assertNotEqual(t0["source_sha256"], t100["source_sha256"])
        self.assertNotEqual(t0["case_id"], t100["case_id"])

    def test_05_knot_one_physical_root_two_one_sided_orders(self):
        v = self.views[core.V6_100]
        self.assertEqual(v["strict_span_open_root_counts"], [0, 0])
        self.assertEqual(v["strict_source_open_root_count"], 1)
        e = v["events"][0]
        self.assertEqual(e["coordinate"], {"kind": "RATIONAL", "value": "1"})
        self.assertEqual(e["location"], "SOURCE_KNOT")
        self.assertEqual(e["order"], {"kind": "ONE_SIDED", "left": 1, "right": 1})
        self.assertEqual(e["classification"], "TOUCHING")
        self.assertEqual(v["maximal_open_signs"], ["POSITIVE", "POSITIVE"])

    def test_06_implicit_v43_root_has_only_source_interval_identity(self):
        v = self.views[core.V9_100]
        self.assertEqual(v["strict_span_open_root_counts"], [1, 0])
        self.assertEqual(v["maximal_open_signs"], ["NEGATIVE", "POSITIVE"])
        self.assertEqual(v["events"][0]["coordinate"], {
            "kind": "IMPLICIT_STRICT_BRACKET", "lower": "1/4",
            "upper": "1/3", "source_root_unique_by_producer_theorem": True})
        self.assertNotIn("rational_root_value", v["events"][0]["coordinate"])
        self.assertTrue(core.validate_view(v, self.rows[core.V9_100]))

    def test_07_forgeries_location_order_parity_sign_and_bracket_refuse(self):
        attacks = [
            (core.H, lambda v: v["events"][0].update(location="SPAN_OPEN")),
            (core.V6_100, lambda v: v["events"][0].update(location="SPAN_OPEN")),
            (core.V6_100, lambda v: v["events"][0]["order"].update(right=2)),
            (core.V8_0, lambda v: v["events"].reverse()),
            (core.V8_0, lambda v: v["events"][0].update(classification="CROSSING")),
            (core.V8_0, lambda v: v["events"][1].update(left_sign="NEGATIVE")),
            (core.V8_100, lambda v: v["events"][0].update(
                coordinate={"kind": "RATIONAL", "value": "1/4"})),
            (core.V9_100, lambda v: v["events"][0]["coordinate"].update(
                lower="1/3", upper="1/4")),
            (core.V9_100, lambda v: v["events"][0]["coordinate"].update(
                lower="1/5")),
            (core.V9_100, lambda v: v["events"][0]["coordinate"].update(
                source_root_unique_by_producer_theorem=False)),
            (core.V9_100, lambda v: v["events"][0].update(
                coordinate={"kind": "RATIONAL", "value": "1/3"})),
            (core.V9_100, lambda v: v.update(maximal_open_signs=[
                "POSITIVE", "POSITIVE"])),
            (core.V8_0, lambda v: v.update(strict_span_open_root_counts=[2, 0])),
            (core.V6_100, lambda v: v.update(strict_source_open_root_count=0)),
        ]
        for cid, mutate in attacks:
            changed = copy.deepcopy(self.views[cid])
            mutate(changed)
            with self.subTest(cid=cid, attack=str(mutate)):
                with self.assertRaises((ValueError, KeyError, TypeError)):
                    core.validate_view(changed, self.rows[cid])

    def test_08_unapproved_source_or_producer_cannot_gain_certificate(self):
        with self.assertRaisesRegex(ValueError, "UNSUPPORTED_SOURCE"):
            core.normalize_one("fabricated-source", {}, {})
        with self.assertRaisesRegex(ValueError, "UNSUPPORTED_SOURCE"):
            core.validate_view({"case_id": "fabricated-source"}, {})
        # A source with an exact-zero continuum must be a separate analytic
        # identity semantic case; the finite five-source allowlist never
        # upgrades arbitrary zero-function sources to a discrete event list.
        zero = {
            "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
            "cos_splines": {"0": {"controls": ["0"], "degree": 0,
                                  "knots": ["0", "1"]}},
            "sin_splines": {}, "phase_turn_offset": "0",
            "phase_turn_rate": "0", "parameter_lo": "0",
            "parameter_hi": "1", "source_parameter_id": "source-time-t"}
        self.assertNotIn(json.dumps(zero, sort_keys=True), str(self.expected))

    def test_09_untrusted_report_preflight_and_pin_mutations(self):
        with self.assertRaisesRegex(ValueError, "RESOURCE_REFUSAL"):
            core.bounded_json({"large": "x" * (core.MAX_REPORT_BYTES+100)})
        with self.assertRaisesRegex(ValueError, "RESOURCE_REFUSAL"):
            core.bounded_json({"entries": [0] * 129})
        deep = []
        node = deep
        for _ in range(20):
            item = []
            node.append(item)
            node = item
        with self.assertRaisesRegex(ValueError, "RESOURCE_REFUSAL"):
            core.bounded_json(deep)
        cycle = []
        cycle.append(cycle)
        with self.assertRaisesRegex(ValueError, "RESOURCE_REFUSAL"):
            core.bounded_json(cycle)
        with self.assertRaisesRegex(ValueError, "invalid report scalar"):
            core.bounded_json({"fake": 1.2})
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "producer.py"
            p.write_bytes(b"changed historical source")
            with self.assertRaisesRegex(ValueError, "pinned original source"):
                core.pin(p, core.PRODUCERS["V27_THREE"]["code_blob"])

    def test_10_forged_manifest_source_hash_and_gates_refuse(self):
        attacks = [
            lambda x: x["source_attested_views"].pop(),
            lambda x: x["source_attested_views"].append(
                copy.deepcopy(x["source_attested_views"][0])),
            lambda x: x["source_attested_views"][0].update(
                source_sha256="a" * 64),
            lambda x: x["source_attested_views"][0].update(
                historical_disposition="CERTIFIED"),
            lambda x: x["source_attested_views"][0].update(
                generic_route_repaired=True),
            lambda x: x["producer_pins"][0].update(code_blob="f" * 40),
            lambda x: x["selected_five_case_overlay"].update(
                historical_route_refusals_without_only_these_five_proofs=14),
            lambda x: x["selected_five_case_overlay"].update(
                not_an_exhaustive_combined_post_v54_census=False),
            lambda x: x["frozen_v54"].update(historical_route_blocked=15),
            lambda x: x["gates"].update({"MC-B": "ESTABLISHED"}),
            lambda x: x["gates"].update(production_authorized=True),
        ]
        for attack in attacks:
            mutated = copy.deepcopy(self.actual)
            attack(mutated)
            with self.subTest(attack=str(attack)), self.assertRaises(ValueError):
                core.validate_report(mutated)

    def test_11_close_roots_and_touching_not_sign_sampling_proofs(self):
        f = lambda t: (t-Q(1, 2))**2
        self.assertTrue(f(Q(0)) > 0 and f(Q(1)) > 0)
        self.assertEqual(f(Q(1, 2)), Q(0))
        eps = Q(1, 2**100)
        g = lambda t: (t-Q(1, 2))**2 - eps**2
        roots = [Q(1,2)-eps, Q(1,2)+eps]
        self.assertEqual([g(x) for x in roots], [Q(0), Q(0)])
        self.assertEqual(roots[1]-roots[0], Q(1,2**99))
        self.assertTrue(all(g(x)>0 for x in (Q(0), Q(1,4), Q(3,4), Q(1))))
        self.assertTrue(all(v["source_specific_mathematics_only"] for v in self.views.values()))
        self.assertFalse(self.expected["selected_five_case_overlay"][
            "not_a_generic_V27_or_V43_solver"] is False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("select --contract and/or --self-test")
    if args.contract:
        reported = json.loads(REPORT.read_text(encoding="utf-8"))
        core.validate_report(reported)
        print("PASS: original frozen 121/20/30 census unchanged; 5 distinct source-specific")
        print("PASS: four V27 child-refused and one V43-refused original source verified")
        print("PASS: selected-five overlay 20 -> 15 is NOT a general current census")
        print(json.dumps({
            "source_case_count": 121,
            "historical_route_refusals": 20,
            "historical_missing_order_premises": 30,
            "selected_distinct_complete_original_source_witnesses": 5,
            "selected_five_overlay_without_only_these_proofs": 15,
            "generic_PB007_or_MC_B_closed": False,
        }, sort_keys=True))
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(FiveSourceTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            raise SystemExit(1)


if __name__ == "__main__":
    main()
