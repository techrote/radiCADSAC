#!/usr/bin/env python3
"""Adversarial verification for exact V41 implicit proof-cut equality/order."""
from __future__ import annotations

import argparse
import copy
import json
from fractions import Fraction as Q
from pathlib import Path
import sys
import unittest

import pb00701_v41_algebraic_cut_order as core


def _spec_from_ab(a, b, *, offset="0", rate="1/3",
                  source_id="source-time-t"):
    a = core.algebraic.trim(a)
    b = core.algebraic.trim(b)
    c = core.algebraic.padd(a, b)
    s = core.algebraic.padd(a, core.algebraic.pscale(b, -1))
    return {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "cos_splines": {"1": core.v41.v27._power_spline(c)},
        "sin_splines": {"1": core.v41.v27._power_spline(s)},
        "parameter_lo": "0",
        "parameter_hi": "1",
        "phase_turn_offset": offset,
        "phase_turn_rate": rate,
        "source_parameter_id": source_id,
    }


A_SQRT_HALF = [Q(-1), Q(0), Q(2)]
B_SAME_DIFFERENT_POLY = core.algebraic.pmul(
    A_SQRT_HALF, [Q(1), Q(1)]
)
B_SQRT_THIRD = [Q(-1), Q(0), Q(3)]

SAME_ROOT = _spec_from_ab(A_SQRT_HALF, B_SAME_DIFFERENT_POLY)
DISTINCT_ROOTS = _spec_from_ab(A_SQRT_HALF, B_SQRT_THIRD)
MIXED_MULTIPLICITY = _spec_from_ab(
    core.algebraic.ppow(A_SQRT_HALF, 2), A_SQRT_HALF
)
RATIONAL_COINCIDENCE = _spec_from_ab(
    [Q(-1, 2), Q(1)], A_SQRT_HALF
)
CLOSE_DISTINCT = _spec_from_ab(
    A_SQRT_HALF,
    [-(Q(1) + Q(1, 2**20)), Q(0), Q(2)],
)


def _cut_with_causes(report, required):
    required = set(required)
    hits = []
    for cut in report["ordered_proof_cuts"]:
        ids = {
            cause.get("cause_id", cause.get("cause_kind"))
            for cause in cut["causes"]
        }
        if required <= ids:
            hits.append(cut)
    if len(hits) != 1:
        raise AssertionError((required, hits))
    return hits[0]


def _cut_index_for_cause(report, cause_id):
    hits = [
        cut["index"] for cut in report["ordered_proof_cuts"]
        if cause_id in {
            cause.get("cause_id", cause.get("cause_kind"))
            for cause in cut["causes"]
        }
    ]
    if len(hits) != 1:
        raise AssertionError((cause_id, hits))
    return hits[0]


def _lowered_maps(spec):
    lowered = core.lowerer.classify_required_analytic_event(spec)
    if lowered.get("status") != "BLOCKED":
        raise AssertionError(lowered)
    spans = lowered.get("spans", [])
    if len(spans) != 1:
        raise AssertionError(lowered)
    span = spans[0]
    cos = {
        int(h): [core.q(x) for x in values]
        for h, values in span["cos_polynomials"].items()
    }
    sin = {
        int(h): [core.q(x) for x in values]
        for h, values in span["sin_polynomials"].items()
    }
    phase = lowered["phase_turn_law"]
    return lowered, span, cos, sin, core.q(phase["offset"]), core.q(phase["rate"])


class V41AlgebraicCutOrderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.same = core.source_bound_view(SAME_ROOT)
        cls.distinct = core.source_bound_view(DISTINCT_ROOTS)
        cls.mixed = core.source_bound_view(MIXED_MULTIPLICITY)
        cls.rational = core.source_bound_view(RATIONAL_COINCIDENCE)

    def test_current_v41_rational_only_route_really_blocks_fixture(self):
        _, _, cos, sin, offset, rate = _lowered_maps(SAME_ROOT)
        cert = core.v41._orientation_cut_certificate(
            cos, sin, offset, rate
        )
        self.assertEqual(cert["status"], "BLOCKED", cert)
        self.assertIn(
            "IRRATIONAL_ALGEBRAIC_ORIENTATION_ROOT_NOT_REPRESENTABLE",
            cert["reason"],
        )
        self.assertGreater(cert["missing_exact_root_count"], 0)

    def test_same_nonrational_root_across_different_polynomials_deduplicates(self):
        report = self.same
        self.assertEqual(
            report["status"],
            "EXACT_SOURCE_BOUND_V41_IMPLICIT_PROOF_CUT_ORDER_RESEARCH",
        )
        cut = _cut_with_causes(report, {"H1_A", "H1_B"})
        methods = {p["method"] for p in cut["coincidence_proofs"]}
        self.assertIn(
            "EXACT_POLYNOMIAL_GCD_PLUS_STURM_COMMON_ROOT", methods
        )
        self.assertFalse(report["interval_overlap_alone_is_equality"])
        self.assertTrue(report["orientation_roots_are_proof_geometry_only"])
        self.assertFalse(report["algebraic_child_reparameterization_constructed"])

        # Independent exact corroboration: the square-free A/B polynomials
        # have exactly one common open root in (0,1).
        gcd = core.algebraic.EE.pgcd(
            core.algebraic.EE.square_free(A_SQRT_HALF),
            core.algebraic.EE.square_free(B_SAME_DIFFERENT_POLY),
        )
        self.assertEqual(
            core.algebraic.EE.distinct_roots_open(gcd, Q(0), Q(1)), 1
        )

    def test_distinct_nonrational_roots_are_strictly_ordered(self):
        report = self.distinct
        b_index = _cut_index_for_cause(report, "H1_B")
        a_index = _cut_index_for_cause(report, "H1_A")
        self.assertLess(b_index, a_index)
        # Positive roots obey B^2=1/3 < A^2=1/2.
        self.assertLess(Q(1, 3), Q(1, 2))
        gcd = core.algebraic.EE.pgcd(
            core.algebraic.EE.square_free(A_SQRT_HALF),
            core.algebraic.EE.square_free(B_SQRT_THIRD),
        )
        self.assertLessEqual(core.algebraic.EE.degree(gcd), 0)

    def test_coincident_causes_keep_separate_multiplicity(self):
        cut = _cut_with_causes(self.mixed, {"H1_A", "H1_B"})
        multiplicity = {
            cause["cause_id"]: cause["multiplicity"]
            for cause in cut["causes"]
            if cause.get("cause_id") in {"H1_A", "H1_B"}
        }
        self.assertEqual(multiplicity, {"H1_A": 2, "H1_B": 1})
        self.assertFalse(self.mixed["frozen_v41_child_composition_claimed"])

    def test_rational_orientation_root_merges_with_existing_phase_cut_exactly(self):
        cut = _cut_with_causes(
            self.rational, {"H1_A", "historical_phase_sector_cut"}
        )
        self.assertEqual(cut["coordinate"]["kind"], "RATIONAL_PROOF_CUT")
        self.assertEqual(cut["coordinate"]["local_value"], "1/2")
        methods = {p["method"] for p in cut["coincidence_proofs"]}
        self.assertTrue(
            methods & {
                "EXACT_RATIONAL_VALUE",
                "EXACT_POLYNOMIAL_EVALUATION_AT_RATIONAL_CUT",
            }
        )

    def test_source_binding_and_replay_validation(self):
        checked = core.validate_report(SAME_ROOT, self.same)
        self.assertEqual(checked, self.same)
        self.assertEqual(
            self.same["source_sha256"], core.source_sha256(SAME_ROOT)
        )
        self.assertEqual(self.same["source_parameter_id"], "source-time-t")
        self.assertEqual(self.same["source_interval"], ["0", "1"])
        self.assertFalse(self.same["historical_v54_dispositions_changed"])
        self.assertFalse(self.same["pb00701_certified"])
        self.assertFalse(self.same["mc_b_established"])
        self.assertFalse(self.same["mc1_established"])
        self.assertFalse(self.same["native_brep_or_step_qualified"])
        self.assertFalse(self.same["production_authorized"])

    def test_source_mutation_cannot_reuse_report(self):
        mutations = (
            lambda s: s.__setitem__("phase_turn_rate", "1/4"),
            lambda s: s.__setitem__("source_parameter_id", "forged-source"),
            lambda s: s["cos_splines"]["1"]["controls"].__setitem__(0, "-5/2"),
            lambda s: s["sin_splines"]["1"]["controls"].__setitem__(-1, "7"),
        )
        for mutate in mutations:
            spec = copy.deepcopy(SAME_ROOT)
            mutate(spec)
            checked = core.validate_report(spec, self.same)
            self.assertNotEqual(
                checked.get("status"),
                "EXACT_SOURCE_BOUND_V41_IMPLICIT_PROOF_CUT_ORDER_RESEARCH",
                checked,
            )
            self.assertFalse(checked["is_truth_value"])

    def test_interval_overlap_alone_never_establishes_equality(self):
        a = {
            "kind": "ISOLATED_REAL_ROOT",
            "local_isolating_interval": ["1/2", "3/4"],
            "source_isolating_interval": ["1/2", "3/4"],
            "defining_square_free_polynomial": ["-1", "0", "2"],
            "minimal_polynomial_claimed": False,
        }
        b = {
            "kind": "ISOLATED_REAL_ROOT",
            "local_isolating_interval": ["1/2", "3/4"],
            "source_isolating_interval": ["1/2", "3/4"],
            "defining_square_free_polynomial": ["-1", "0", "3"],
            "minimal_polynomial_claimed": False,
        }
        same, method = core._same_coordinate(a, b)
        self.assertFalse(same)
        self.assertIsNone(method)
        budget = core.ComparisonBudget(64)
        relation, method, _, _ = core.compare_coordinates(
            a, b, budget, Q(0), Q(1)
        )
        self.assertEqual(relation, "RIGHT_BEFORE_LEFT")
        self.assertEqual(method, "DISJOINT_EXACT_RATIONAL_BOUNDS")
        self.assertGreater(budget.used, 0)

    def test_identity_orientation_coordinate_refuses(self):
        spec = _spec_from_ab([Q(0)], A_SQRT_HALF)
        refused = core.attempt(spec)
        self.assertEqual(refused["status"], "BLOCKED", refused)
        self.assertIn("IDENTICALLY_ZERO_ORIENTATION_COORDINATE",
                      refused["reason"])
        self.assertFalse(refused["is_truth_value"])

    def test_isolation_and_comparison_resource_exhaustion_are_nontruth(self):
        isolated = core.attempt(
            SAME_ROOT, max_isolation_bisections=1
        )
        self.assertEqual(isolated["status"], "RESOURCE_REFUSAL", isolated)
        self.assertFalse(isolated["is_truth_value"])

        ordered = core.attempt(
            CLOSE_DISTINCT, max_comparison_bisections=1
        )
        self.assertEqual(ordered["status"], "RESOURCE_REFUSAL", ordered)
        self.assertFalse(ordered["is_truth_value"])

    def test_noncanonical_binary_float_and_extra_authority_refuse(self):
        floating = copy.deepcopy(SAME_ROOT)
        floating["phase_turn_rate"] = 1 / 3
        a = core.attempt(floating)
        self.assertEqual(a["status"], "BLOCKED")
        self.assertIn("BINARY_FLOAT", a["reason"])

        forged = copy.deepcopy(SAME_ROOT)
        forged["orientation_roots"] = ["0.707"]
        b = core.attempt(forged)
        self.assertEqual(b["status"], "BLOCKED")
        self.assertIn("UNREVIEWED_SOURCE_AUTHORITY_FIELD", b["reason"])

    def test_report_forgery_and_capability_promotion_refuse(self):
        mutations = (
            lambda r: r.__setitem__("interval_overlap_alone_is_equality", True),
            lambda r: r.__setitem__("algebraic_child_reparameterization_constructed", True),
            lambda r: r.__setitem__("frozen_v41_child_composition_claimed", True),
            lambda r: r.__setitem__("pb00701_certified", True),
            lambda r: r.__setitem__("mc_b_established", True),
            lambda r: r.__setitem__("mc1_established", True),
            lambda r: r.__setitem__("native_brep_or_step_qualified", True),
            lambda r: r.__setitem__("production_authorized", True),
            lambda r: r["ordered_proof_cuts"].reverse(),
            lambda r: r["orientation_root_causes"].pop(),
        )
        for mutate in mutations:
            forged = copy.deepcopy(self.same)
            mutate(forged)
            checked = core.validate_report(SAME_ROOT, forged)
            self.assertEqual(checked["status"], "BLOCKED", checked)
            self.assertFalse(checked["is_truth_value"])

    def test_pinned_custody_domain_and_authority_stay_closed(self):
        core.pins()
        domain = json.loads(
            (core.ROOT /
             "research/machining-completeness/tasks/MC-002/domain-contract-v1.json")
            .read_text()
        )
        authority = json.loads(
            (core.ROOT / "handoffs/current-authority.json").read_text()
        )
        self.assertEqual(
            len(domain["coverage_rule"]["required_operation_ids"]), 26
        )
        self.assertFalse(authority["production_authorized"])
        self.assertEqual(authority["capability_status"], "NOT_ESTABLISHED")


def contract_rows():
    for label, spec in (
        ("same_implicit_root_different_polynomials", SAME_ROOT),
        ("distinct_implicit_roots", DISTINCT_ROOTS),
        ("coincident_different_multiplicity", MIXED_MULTIPLICITY),
        ("rational_cut_coincidence", RATIONAL_COINCIDENCE),
    ):
        report = core.source_bound_view(spec)
        yield {
            "label": label,
            "status": report["status"],
            "source_sha256": report["source_sha256"],
            "orientation_root_causes": len(report["orientation_root_causes"]),
            "ordered_proof_cuts": len(report["ordered_proof_cuts"]),
            "isolation_bisections_used": report["isolation_bisections_used"],
            "comparison_bisections_used": report["comparison_bisections_used"],
            "algebraic_child_reparameterization_constructed": False,
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
        for row in contract_rows():
            print(json.dumps(row, sort_keys=True))
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(
            V41AlgebraicCutOrderTests
        )
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
