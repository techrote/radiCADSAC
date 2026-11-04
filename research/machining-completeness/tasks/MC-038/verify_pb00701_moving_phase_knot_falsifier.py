#!/usr/bin/env python3
"""Adversarial check of the exact moving-phase source-knot falsifier."""
from __future__ import annotations

import copy
import json
import unittest
from fractions import Fraction as Q

import pb00701_moving_phase_knot_falsifier as m


def verify_historical_census():
    """Read actual frozen v54 sources and qualified v2 rows, not saved totals."""
    from collections import Counter
    from pathlib import Path
    import hashlib

    here = Path(__file__).resolve().parent
    v54 = json.loads((here / "pb00701-finite-owner-corpus-v54.json").read_text())
    v2 = json.loads((here / "pb00701-post-v54-evidence-reconciliation-v2.json").read_text())
    original = {c["id"]: c for c in v54["cases"]}
    rows = v2["source_cases"]
    assert len(original) == len(v54["cases"]) == 121
    assert len(rows) == len({r["case_id"] for r in rows}) == 50
    assert v2["frozen_corpus_git_blob"] == "5841c331579489b25caef38cd412bdbf286f9134"
    assert v2["historical_v54"] == {
        "original_source_cases": 121, "route_refusals": 20,
        "missing_ordered_span_premises": 30, "dispositions_changed": False
    }
    observed = Counter()
    for row in rows:
        prior = original[row["case_id"]]
        assert row["historical_v54_disposition"] == prior["expected"]["v54_disposition"]
        assert row["source_sha256"] == hashlib.sha256(
            m.canonical(prior["spec"])).hexdigest()
        assert row["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC"
        assert row["historical_disposition_changed"] is False
        observed[row["historical_v54_disposition"]] += 1
    assert observed == {
        "BLOCKED": 20,
        "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE": 30
    }
    old_unresolved = {c["id"] for c in v54["cases"] if
                      c["expected"]["v54_disposition"] in (
                          "BLOCKED", "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE")}
    assert old_unresolved == {r["case_id"] for r in rows}
    assert m.source_binding(m.SOURCE) not in {r["source_sha256"] for r in rows}
    s = v2["summary"]
    assert s["by_registered_evidence_level"] == {
        "COMPLETE_SOURCE_SPECIFIC": 50, "PARTIAL_REFUSED_TAIL_ONLY": 0,
        "PARTIAL_ORDERED_CHILD": 0,
        "NO_REGISTERED_SOURCE_EVENT_OR_ORDER_WITNESS": 0
    }
    assert s["complete_finite_sources"] == 49 and s["complete_continuum_sources"] == 1
    assert s["newly_completed_original_sources"] == 35
    return {"historical_cases": len(original), "historical_unresolved": len(rows),
            "now_source_specific_complete": 50, "new_historical_completions": 0}


class FalsifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = copy.deepcopy(m.SOURCE)
        cls.truth = m.analyze(cls.spec)

    def test_original_coefficient_identities_are_global_exact(self):
        sha, coeffs = m.exact_source_coefficients(self.spec)
        self.assertEqual(sha, self.truth["source_sha256"])
        self.assertEqual(coeffs["0"], ((Q(0), Q(0), Q(1,2)),)*2)
        self.assertEqual(coeffs["1"][0], (Q(0), Q(0), Q(1,2)))
        self.assertEqual(coeffs["1"][1], (Q(0), Q(0), Q(-1,2)))
        self.assertEqual([m.poly_eval(coeffs["0"][0], t)
                          for t in [Q(-1), Q(-1,2), Q(0)]],
                         [Q(1,2), Q(1,8), Q(0)])

    def test_finite_moving_roots_and_positive_cells(self):
        self.assertEqual(self.truth["moving_distinct_zero_coordinates"],
                         ["-1/2", "0", "1"])
        self.assertEqual(self.truth["moving_distinct_root_count"], 3)
        self.assertEqual(len(self.truth["moving_positive_components"]), 3)
        self.assertEqual(self.truth["moving_zero_set_kind"],
                         "FINITE_DISTINCT_CLOSED_SOURCE_ROOTS")

    def test_true_knot_one_sided_orders_are_two_and_four(self):
        k = self.truth["moving_events"][1]
        self.assertEqual(k["source_t"], "0")
        self.assertEqual((k["left_one_sided_order"], k["right_one_sided_order"]),
                         (2, 4))
        self.assertIsNone(k["global_smooth_multiplicity"])
        self.assertEqual((k["left_sign"], k["right_sign"]), (1, 1))

    def test_tangency_and_right_exterior(self):
        events = self.truth["moving_events"]
        self.assertEqual(events[0]["source_t"], "-1/2")
        self.assertEqual(events[0]["order"], 2)
        self.assertEqual(events[0]["kind"], "TOUCHING")
        self.assertEqual(events[2]["source_t"], "1")
        self.assertEqual(events[2]["right_inward_order"], 2)

    def test_stationary_identity_zero_is_not_moving_continuum(self):
        c = self.truth["stationary_counterfactual"]
        self.assertEqual(c["phase_turn_rate"], "0")
        self.assertEqual(c["closed_zero_components"], [["0", "1"]])
        self.assertIsNone(c["finite_total_root_count"])
        self.assertNotEqual(c["zero_set_kind"], self.truth["moving_zero_set_kind"])
        # Replacing the moving source rate must refuse, never silently
        # substitute the stationary proof.
        mutated = copy.deepcopy(self.spec)
        mutated["phase_turn_rate"] = "0"
        self.assertEqual(m.attempt(mutated)["status"], "BLOCKED")

    def test_source_knot_and_controls_mutations_refuse(self):
        for harmonic in ("0", "1"):
            for key, index, value in (("controls", 0, "1"),
                                      ("controls", 2, "1/2"),
                                      ("controls", 4, "0"),
                                      ("knots", 3, "-1/2"),
                                      ("knots", 4, "-1/2")):
                mutant = copy.deepcopy(self.spec)
                mutant["cos_splines"][harmonic][key][index] = value
                self.assertEqual(m.attempt(mutant)["status"], "BLOCKED",
                                 (harmonic, key, index))

    def test_phase_parameter_domain_and_grammar_mutations_refuse(self):
        changes = (("source_parameter_id", "other-source"),
                   ("parameter_lo", "-2"),
                   ("parameter_hi", "2"),
                   ("phase_turn_offset", "1/2"),
                   ("phase_turn_rate", "2"),
                   ("grammar", "ALTERNATE_GRAMMAR"))
        for key, value in changes:
            mutant = copy.deepcopy(self.spec)
            mutant[key] = value
            self.assertEqual(m.attempt(mutant)["status"], "BLOCKED", key)

    def test_noncanonical_or_binary_rational_refuse(self):
        for raw in ("2/4", "0.0", 0.0, "1/0"):
            mutant = copy.deepcopy(self.spec)
            mutant["cos_splines"]["0"]["controls"][0] = raw
            self.assertEqual(m.attempt(mutant)["status"], "BLOCKED")

    def test_oversize_is_resource_nontruth(self):
        mutant = copy.deepcopy(self.spec)
        mutant["source_parameter_id"] = "x"*m.MAX_BYTES
        result = m.attempt(mutant)
        self.assertEqual(result["status"], "RESOURCE_REFUSAL")
        self.assertFalse(result["is_truth_value"])

    def test_bad_report_and_gate_escalation_refuse(self):
        self.assertEqual(m.validate_report(self.spec, self.truth), self.truth)
        mutants = [
            lambda d: d["moving_distinct_zero_coordinates"].remove("-1/2"),
            lambda d: d["moving_events"][1].__setitem__("right_one_sided_order", 2),
            lambda d: d["moving_events"][1].__setitem__("global_smooth_multiplicity", 3),
            lambda d: d["stationary_counterfactual"].__setitem__(
                "zero_set_kind", "FINITE_DISTINCT_CLOSED_SOURCE_ROOTS"),
            lambda d: d.__setitem__("historical_source_closure_delta", 1),
            lambda d: d.__setitem__("pb00701_certified", True),
            lambda d: d.__setitem__("production_authorized", True),
            lambda d: d.__setitem__("source_sha256", "f"*64),
        ]
        for mutate in mutants:
            report = copy.deepcopy(self.truth)
            mutate(report)
            self.assertEqual(m.validate_report(self.spec, report)["status"],
                             "BLOCKED")

    def test_historical_registry_source_ids_are_exact(self):
        self.assertEqual(verify_historical_census()["new_historical_completions"], 0)

    def test_historical_census_unchanged(self):
        r = self.truth
        self.assertEqual((r["historical_121_source_denominator"],
                          r["historical_route_refusals"],
                          r["historical_missing_ordered_premises"]), (121, 20, 30))
        self.assertEqual((r["before_complete_fifty_source_supplemental_proofs"],
                          r["after_complete_fifty_source_supplemental_proofs"]), (50,50))
        self.assertEqual(r["historical_source_closure_delta"], 0)
        self.assertFalse(r["mc_b_established"])
        self.assertFalse(r["mc1_established"])
        self.assertFalse(r["native_brep_or_step_qualified"])
        self.assertFalse(r["production_authorized"])

    def test_two_contrasting_endpoint_modes_are_source_faithful(self):
        # Independently check the fixed original Bernstein extraction at
        # the actual -1,0,1 endpoints (not evidence from a numeric scan).
        for harmonic in ("0","1"):
            c = [m.rational(x) for x in self.spec["cos_splines"][harmonic]["controls"]]
            left, right = (m.piece_poly(c[:3], Q(-1), Q(0)),
                           m.piece_poly(c[2:], Q(0), Q(1)))
            self.assertEqual(m.poly_eval(left,Q(0)),m.poly_eval(right,Q(0)))
            self.assertEqual(m.poly_eval(left,Q(-1)),Q(1,2))
            self.assertEqual(m.poly_eval(right,Q(1)),
                             Q(1,2) if harmonic == "0" else Q(-1,2))


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--contract", action="store_true")
    args=parser.parse_args()
    if not (args.self_test or args.contract):
        parser.error("select --self-test and/or --contract")
    if args.contract:
        verify_historical_census()
        actual=m.analyze(m.SOURCE)
        assert m.validate_report(m.SOURCE,actual)==actual
        with open(__file__.rsplit("/",1)[0]+"/pb00701-moving-phase-knot-falsifier.json",
                  encoding="utf-8") as stream:
            saved=json.load(stream)
        assert m.canonical(saved)==m.canonical(actual), "saved evidence/source drift"
        print("PASS: exact original-source counterexample, saved evidence and census custody")
    if args.self_test:
        result=unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(FalsifierTests))
        if not result.wasSuccessful():
            raise SystemExit(1)


if __name__=="__main__":
    main()
