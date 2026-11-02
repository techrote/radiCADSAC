#!/usr/bin/env python3
"""Replay the original V23 source proof and its adversarial refusal controls."""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction as Q
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import pb00701_v23_bernstein_source as model


class SourceProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = model.load_original()
        cls.report = model.expected_report()

    def changed_source_refuses(self, mutate):
        row = copy.deepcopy(self.original)
        mutate(row)
        with self.assertRaises(ValueError):
            model.check_original(row)

    def changed_proof_refuses(self, mutate):
        source = copy.deepcopy(self.original["spec"])
        mutate(source)
        with self.assertRaises(ValueError):
            model.prove_sector_source(source)

    def changed_report_refuses(self, mutate):
        report = copy.deepcopy(self.report)
        mutate(report)
        with self.assertRaises(ValueError):
            model.validate_report(report)

    def test_original_source_and_full_closed_event_set(self):
        proof = model.check_original(self.original)
        self.assertEqual(proof["strict_lower_bound"]["coefficient"], "49/34992")
        self.assertEqual(proof["left_endpoint_second_derivative"], "1/36")
        events = proof["physical_event_proof"]
        self.assertEqual(events["closed_distinct_root_count"], 1)
        self.assertEqual(events["open_distinct_root_count"], 0)
        self.assertEqual(events["events"][0]["location"], "SOURCE_EXTERIOR_LEFT_ENDPOINT")
        self.assertEqual(events["events"][0]["analytic_order"], 2)
        self.assertIsNone(events["events"][0]["left_sign"])
        self.assertTrue(model.validate_report(model.read_report()))

    def test_independent_de_casteljau_factor_identity(self):
        # These evaluations challenge the coefficient transformation. They are
        # not the positivity/completeness proof, which uses the exact basis.
        def de_casteljau(controls, t):
            values = list(controls)
            while len(values) > 1:
                values = [(1-t)*a+t*b for a, b in zip(values, values[1:])]
            return values[0]
        for channel in ("cos_splines", "sin_splines"):
            for spline in self.original["spec"][channel].values():
                controls = model.clamped_controls(spline)
                quotient = model.factor_t_squared(controls)
                for t in (Q(0), Q(1, 7), Q(2, 5), Q(1)):
                    self.assertEqual(de_casteljau(controls, t),
                                     t*t*de_casteljau(quotient, t))
        self.assertEqual(model.factor_t_squared([Q(0), Q(0), Q(1)]), [Q(1)])
        self.assertEqual(model.power_coefficients([Q(0), Q(0), Q(1)]),
                         [Q(0), Q(0), Q(1)])

    def test_conditional_checker_is_not_a_frozen_answer_table(self):
        source = copy.deepcopy(self.original["spec"])
        unit = {"degree": 2, "knots": ["0"]*3+["1"]*3,
                "controls": ["0", "0", "1"]}
        zero = {**unit, "controls": ["0", "0", "0"]}
        source["cos_splines"] = {"0": unit, "1": copy.deepcopy(zero)}
        source["sin_splines"] = {"2": copy.deepcopy(zero)}
        for rate in ("-1/24", "-1/48", "0"):
            source["phase_turn_rate"] = rate
            proof = model.prove_sector_source(source)
            self.assertEqual(proof["strict_lower_bound"]["coefficient"], "1")
            self.assertEqual(proof["left_endpoint_second_derivative"], "2")
        row = copy.deepcopy(self.original)
        row["spec"] = source
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            model.check_original(row)

    def test_original_source_metadata_and_hash_mutations(self):
        changes = [
            lambda r: r.update(id="another-original-source"),
            lambda r: r.update(origin="verify_pb00701_v53"),
            lambda r: r.update(kind="COMPOSITE_TAIL"),
            lambda r: r["spec"].update(source_parameter_id="other-parameter"),
            lambda r: r["spec"].update(phase_turn_offset="0"),
            lambda r: r["spec"].update(phase_turn_rate="-1/48"),
            lambda r: r["spec"].update(parameter_hi="2"),
            lambda r: r["spec"]["cos_splines"]["0"]["controls"].__setitem__(2, "1/1000"),
            lambda r: r["spec"]["cos_splines"]["1"]["knots"].__setitem__(6, "1/2"),
            lambda r: r["spec"].update(parameter_projection={"mode": "invented"}),
            lambda r: r.update(fabricated_authority=True),
        ]
        for change in changes:
            with self.subTest(change=changes.index(change)):
                self.changed_source_refuses(change)

    def test_historical_owner_refusal_and_disposition_are_immutable(self):
        for field, value in (("v54_disposition", "CERTIFIED"), ("id", "fake")):
            self.changed_source_refuses(lambda r: r["expected"].update({field: value}))
        for index, value in ((0, "V43"), (1, "CERTIFIED"), (2, None)):
            self.changed_source_refuses(
                lambda r: r["expected"]["observed"]["spans"][0].__setitem__(index, value))
        self.changed_source_refuses(lambda r: r["expected"]["observed"].update(status="CERTIFIED"))

    def test_negative_bernstein_control_refuses_without_truth_claim(self):
        for channel, harmonic in (("cos_splines", "0"), ("cos_splines", "1"),
                                  ("sin_splines", "2")):
            self.changed_proof_refuses(
                lambda s: s[channel][harmonic]["controls"].__setitem__(-1, "-1"))
        # A0 must have a strictly positive quotient over the CLOSED unit
        # interval. A zero last control would leave the right endpoint open.
        self.changed_proof_refuses(
            lambda s: s["cos_splines"]["0"]["controls"].__setitem__(-1, "0"))

    def test_boundary_factor_and_order_are_derived(self):
        for channel, harmonic in (("cos_splines", "0"), ("cos_splines", "1"),
                                  ("sin_splines", "2")):
            for index in (0, 1):
                self.changed_proof_refuses(
                    lambda s: s[channel][harmonic]["controls"].__setitem__(index, "1"))
        self.changed_proof_refuses(
            lambda s: s["cos_splines"]["0"]["controls"].__setitem__(2, "0"))

    def test_unclamped_discontinuous_or_multispan_source_refuses(self):
        self.changed_proof_refuses(
            lambda s: s["cos_splines"]["0"]["knots"].__setitem__(7, "1/2"))
        self.changed_proof_refuses(
            lambda s: s["cos_splines"]["0"]["knots"].pop())
        self.changed_proof_refuses(
            lambda s: s["sin_splines"]["2"]["controls"].append("1"))
        self.changed_proof_refuses(
            lambda s: s["cos_splines"]["0"].update(degree=6))

    def test_quadrant_and_harmonic_residual_controls(self):
        for value in ("1/24", "-1/12"):
            self.changed_proof_refuses(lambda s: s.update(phase_turn_rate=value))
        self.changed_proof_refuses(lambda s: s.update(phase_turn_offset="3/4"))
        self.changed_proof_refuses(lambda s: s["cos_splines"].pop("1"))
        self.changed_proof_refuses(lambda s: s["sin_splines"].update(
            {"3": copy.deepcopy(s["sin_splines"]["2"])}))

    def test_canonical_rationals_and_python_numeric_aliases(self):
        for value in (0.0, True, 0, "0/1", "01", "1/0", "nan", "1/" + "9"*170):
            self.changed_proof_refuses(lambda s: s.update(parameter_lo=value))
        self.changed_proof_refuses(lambda s: s["cos_splines"]["0"].update(degree=True))

    def test_lexical_and_size_checks_precede_fraction_construction(self):
        # Never evaluate these through the real constructor. The mock proves
        # that exponent and other forbidden input is refused before Fraction.
        forbidden = (
            "1e1000000000", "1E9", "1e-9", "0.5", ".5", "1.",
            " 1", "1 ", "1\n", "\t1", "+1", "-0", "01", "1/01",
            "0/1", "1/1", "2/4", "0/2", "1/-2", "1/+2", "1/0",
            "1_000", "\u0661", "1/\u0662", "\uff11", "\u22121",
            "9"*79, "1/" + "9"*79, str(2**256), "1/" + str(2**256),
        )
        with mock.patch.object(model, "Q", side_effect=AssertionError(
                "Fraction constructor must not receive rejected input")) as constructor:
            for value in forbidden:
                with self.subTest(value=value):
                    with self.assertRaises(ValueError):
                        model.exact(value)
            constructor.assert_not_called()
        for value in ("0", "1", "-1", "1/2", "-1/2", str(2**255),
                      "1/" + str(2**255)):
            self.assertEqual(str(model.exact(value)), value)

    def test_resource_refusal_does_not_become_a_source_verdict(self):
        for bad in ({"cycle": None}, {"large": "x"*5000}, {"big": 2**300}):
            if "cycle" in bad:
                bad["cycle"] = bad
            with self.assertRaisesRegex(ValueError, "RESOURCE_REFUSAL"):
                model.canonical(bad)
        deep = leaf = {}
        for _ in range(18):
            leaf["next"] = {}
            leaf = leaf["next"]
        with self.assertRaisesRegex(ValueError, "RESOURCE_REFUSAL"):
            model.canonical(deep)
        self.changed_proof_refuses(lambda s: s["cos_splines"]["0"].update(degree=10000))

    def test_report_root_order_sign_and_derivative_forgery(self):
        for field, value in (("closed_distinct_root_count", 0),
                             ("open_distinct_root_count", 1),
                             ("closed_distinct_root_count", True),
                             ("continuum_zero_component", True)):
            self.changed_report_refuses(lambda r: r["source_specific_proof"][
                "physical_event_proof"].update({field: value}))
        self.changed_report_refuses(lambda r: r["source_specific_proof"].update(
            left_endpoint_second_derivative="0"))
        self.changed_report_refuses(lambda r: r["source_specific_proof"][
            "physical_event_proof"]["events"][0].update(analytic_order=1))
        self.changed_report_refuses(lambda r: r["source_specific_proof"][
            "physical_event_proof"]["sign_cells"][0].update(sign="NEGATIVE"))
        self.changed_report_refuses(lambda r: r["source_specific_proof"][
            "physical_event_proof"]["events"][0].update(left_sign="POSITIVE"))

    def test_report_source_and_certificate_substitution(self):
        self.changed_report_refuses(lambda r: r.update(original_source_sha256="0"*64))
        self.changed_report_refuses(lambda r: r.update(case_id="another-source"))
        self.changed_report_refuses(lambda r: r["source_specific_proof"]["strict_lower_bound"].update(
            coefficient="1/36"))
        self.changed_report_refuses(lambda r: r["source_specific_proof"]["channels"]["C0"][
            "t_squared_quotient_controls"].__setitem__(0, "1/36"))
        self.changed_report_refuses(lambda r: r["dependencies"]["MC038_git_blobs"].update(
            {"pb00701-finite-owner-corpus-v54.json": "0"*40}))

    def test_no_report_capability_or_census_promotion(self):
        for field, value in (("MC_B", "ESTABLISHED"), ("MC_1", "ESTABLISHED"),
                             ("production_authorized", True), ("PB00701_closed", True),
                             ("historical_V23_route_repaired", True),
                             ("exhaustive_post_v54_census", True),
                             ("native_material_topology_or_STEP_qualified", True),
                             ("protected_operation_count", 25)):
            self.changed_report_refuses(lambda r: r["scope"].update({field: value}))
        self.changed_report_refuses(lambda r: r["frozen_v54_census"].update(route_refusals=19))
        self.changed_report_refuses(lambda r: r["scope"].update(production_authorized=0))

    def test_report_file_duplicate_keys_and_size(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text('{"key": 1, "key": 2}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                model.read_report(path)
            path.write_text(" " * (model.MAX_JSON_BYTES + 1), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "RESOURCE_REFUSAL"):
                model.read_report(path)

    def test_git_blob_custody_rejects_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.txt"
            path.write_bytes(b"original\n")
            digest = model.blob(path)
            model.pin(path, digest)
            path.write_bytes(b"altered\n")
            with self.assertRaisesRegex(ValueError, "pinned source drift"):
                model.pin(path, digest)
            with path.open("wb") as handle:
                handle.truncate(model.MAX_DEPENDENCY_BYTES + 1)
            with self.assertRaisesRegex(ValueError, "RESOURCE_REFUSAL"):
                model.pin(path, digest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.contract or not args.self_test:
        model.validate_report(model.read_report())
        print(json.dumps({"case_id": model.CASE_ID,
                          "source_sha256": model.SOURCE_SHA256,
                          "result": "COMPLETE_SOURCE_SPECIFIC_MATHEMATICAL_WITNESS",
                          "closed_roots": 1, "open_roots": 0,
                          "left_endpoint_order": 2,
                          "historical_V54": "BLOCKED", "MC_B": "NOT_ESTABLISHED"},
                         sort_keys=True))
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(SourceProofTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            raise SystemExit(1)


if __name__ == "__main__":
    main()
