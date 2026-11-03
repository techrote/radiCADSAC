#!/usr/bin/env python3
"""Replay three frozen-source Bernstein/sector proofs and challenge premises."""
from __future__ import annotations

import argparse
import builtins
import copy
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from math import comb
import os
from pathlib import Path
import py_compile
import sys
import tempfile
import types
import unittest
from unittest import mock

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "pb00701_bernstein_sector_source_witnesses.py"
MODEL_BLOB = "d71f25124c9780bdd4c77ff16e6d7c9cb63d4385"


def load_reviewed_model(path=MODEL_PATH, expected=MODEL_BLOB):
    """Execute the bounded, reviewed source buffer, ignoring import caches."""
    with Path(path).open("rb") as stream:
        raw = stream.read(1048577)
    if len(raw) > 1048576:
        raise ValueError("reviewed model source byte limit")
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    if actual != expected:
        raise ValueError("reviewed model source blob drift")
    result = types.ModuleType("sector_witness_reviewed_model")
    result.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), result.__dict__)
    return result


model = load_reviewed_model()


V18_ZERO = "composite:" + model.V18 + ":tail0"
V18_RAMP = "composite:" + model.V18 + ":tail100"
V26_ZERO = "composite:" + model.V26 + ":tail0"


def matching_bytecode_counterexample(path, trusted, altered):
    """Install an actual accepted timestamp/size cache in a temporary fixture."""
    if len(trusted) != len(altered) or trusted == altered:
        raise AssertionError("cache counterexample requires distinct equal-length sources")
    alternate = path.with_name("alternate.py")
    path.write_bytes(trusted)
    alternate.write_bytes(altered)
    for candidate in (path, alternate):
        os.utime(candidate, (1700000000, 1700000000))
    cache = Path(importlib.util.cache_from_source(str(path)))
    cache.parent.mkdir(exist_ok=True)
    py_compile.compile(str(alternate), cfile=str(cache), doraise=True,
                       invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
    spec = importlib.util.spec_from_file_location("observed_stale_cache", path)
    ordinary = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ordinary)
    return ordinary


def copied_frozen_inputs(directory):
    for name, expected in model.PINS.items():
        (directory / name).write_bytes(model.pinned_bytes(HERE / name, expected))
    return directory / "verify_pb00701_post_v54_frontier.py"


def spline(left, right):
    assert len(left) == len(right)
    degree = len(left)-1
    return {"degree": degree,
            "knots": ["0"]*(degree+1)+["1"]*(degree+1)+["2"]*(degree+1),
            "controls": [str(x) for x in left+right]}


def dominance_fixture(c0=-Q(2), slope=Q(0), c1=Q(0), s2=Q(0)):
    return {"grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
            "source_parameter_id": "synthetic-proof-premise-control", "parameter_lo": "0",
            "parameter_hi": "2", "phase_turn_offset": "1/24", "phase_turn_rate": "1/24",
            "cos_splines": {"0": spline([c0, c0], [c0, c0+slope]),
                            "1": spline([c1], [c1])},
            "sin_splines": {"2": spline([s2], [s2])}}


def sector_fixture(a=None, b=None, epsilon=Q(0)):
    a = [Q(1)] if a is None else a
    b = [Q(2)] if b is None else b
    return {"grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
            "source_parameter_id": "synthetic-sector-premise-control", "parameter_lo": "0",
            "parameter_hi": "2", "phase_turn_offset": "1/6", "phase_turn_rate": "-1/3",
            "cos_splines": {"0": spline([Q(0)], [Q(0)]),
                            "1": spline(a, [a[-1]]*len(a)),
                            "2": spline([epsilon], [epsilon])},
            "sin_splines": {"1": spline(b, [b[-1]]*len(b))}}


class SourceWitnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.originals = model.load_originals()
        cls.report = model.expected_report()

    def bad_source(self, case_id, mutation):
        row = copy.deepcopy(self.originals[case_id])
        mutation(row)
        with self.assertRaises(model.Refusal):
            model.check_original(row)

    def bad_helper(self, case_id, mutation, message=None):
        source = copy.deepcopy(self.originals[case_id]["spec"])
        mutation(source)
        helper = model.prove_sector_source if case_id == V26_ZERO else model.prove_dominance_source
        with self.assertRaisesRegex(model.Refusal, message or ".*"):
            helper(source)

    def bad_report(self, mutation):
        report = copy.deepcopy(self.report)
        mutation(report)
        with self.assertRaises(model.Refusal):
            model.validate_report(report)

    def test_three_original_closed_source_results(self):
        wanted = {V18_ZERO: (0, None, ["NEGATIVE"]),
                  V18_RAMP: (1, ["1", "1001/1000"], ["NEGATIVE", "POSITIVE"]),
                  V26_ZERO: (1, ["1/2", "1"], ["POSITIVE", "NEGATIVE"])}
        for case_id, (count, bracket, signs) in wanted.items():
            proof = model.check_original(self.originals[case_id])
            event = proof["physical_event_proof"]
            self.assertEqual(event["closed_distinct_root_count"], count)
            self.assertEqual(event["open_distinct_root_count"], count)
            self.assertEqual([x["sign"] for x in event["maximal_sign_cells"]], signs)
            self.assertTrue(event["complete_for_original_closed_source"])
            self.assertFalse(event["continuum_zero_component"])
            self.assertFalse(event["interior_source_knots"][0]["is_zero_event"])
            self.assertTrue(all(not x["is_zero_event"] for x in event["exterior_endpoints"]))
            if count:
                root = event["events"][0]
                self.assertEqual(root["analytic_order"], 1)
                self.assertEqual(root["coordinate"]["isolating_interval"], bracket)
                self.assertEqual(root["coordinate"]["original_source_sha256"],
                                 model.CASES[case_id]["source_sha256"])
                self.assertEqual(root["coordinate"]["kind"], "IMPLICIT_ORIGINAL_SOURCE_ROOT")
            self.assertTrue(all(not c["is_zero_event"] for c in event["proof_cuts"]))
        self.assertTrue(model.validate_report(model.read_report()))

    def test_frozen_exact_envelopes_are_reconstructed(self):
        negative = model.check_original(self.originals[V18_ZERO])["derived_envelopes"]
        ramp = model.check_original(self.originals[V18_RAMP])["derived_envelopes"]
        sector = model.check_original(self.originals[V26_ZERO])["derived_envelopes"]
        self.assertEqual(negative["first_F_upper"], "-9943/279936")
        self.assertEqual(negative["tail_F_upper"], "-4459/109350")
        self.assertEqual(ramp["tail_F_derivative_lower"], "5467423/54675")
        self.assertEqual(ramp["bracket_right_F_lower"], "2797/54675")
        self.assertEqual(sector["first_half_F_lower"], "20149/10000")
        self.assertEqual(sector["right_half_F_derivative_upper"], "-220489/26250")
        self.assertEqual(sector["original_knot_F_upper"], "-67301/20000")
        self.assertEqual(sector["tail_sector_1"]["F_upper"], "-33649/10000")
        self.assertEqual(sector["tail_sector_2"]["F_upper"], "-40299/10000")

    def test_subdivision_against_direct_bernstein_evaluation(self):
        # Independent finite exact identity controls, not sampling authority
        # for positivity or root completeness.
        def evaluate(controls, t):
            n = len(controls)-1
            return sum(c*comb(n, i)*t**i*(1-t)**(n-i) for i, c in enumerate(controls))
        for row in self.originals.values():
            for channel in ("cos_splines", "sin_splines"):
                for original in row["spec"][channel].values():
                    for controls in model.two_span_controls(original):
                        left, right = model.split_controls(controls)
                        for u in (Q(0), Q(1, 5), Q(1, 2), Q(4, 5), Q(1)):
                            self.assertEqual(evaluate(left, u), evaluate(controls, u/2))
                            self.assertEqual(evaluate(right, u), evaluate(controls, (1+u)/2))
        self.assertEqual(model.split_controls([Q(0), Q(0), Q(1)]),
                         ([Q(0), Q(0), Q(1, 4)], [Q(1, 4), Q(1, 2), Q(1)]))
        self.assertEqual(model.derivative_controls([Q(0), Q(0), Q(1)]), [Q(0), Q(2)])

    def test_v26_derivative_controls_have_independent_polynomial_identity(self):
        original = self.originals[V26_ZERO]["spec"]
        a = model.two_span_controls(original["cos_splines"]["1"])[0]
        b = model.two_span_controls(original["sin_splines"]["1"])[0]
        self.assertEqual(model.power_coefficients(a),
                         [Q(83, 20), Q(2, 5), Q(321, 50), Q(-363, 25), Q(379, 50)])
        self.assertEqual(model.power_coefficients(b),
                         [Q(1081, 100), Q(-1, 5), Q(39, 50), Q(6, 5), Q(-183, 100)])
        self.assertEqual(model.split_controls(model.derivative_controls(a))[1],
                         [Q(-7, 25), Q(-161, 100), Q(-139, 50), Q(0)])
        self.assertEqual(model.split_controls(model.derivative_controls(b))[1],
                         [Q(113, 200), Q(51, 100), Q(-4, 25), Q(-59, 25)])

    def test_conditional_dominance_helpers_prove_nonfrozen_sources(self):
        zero = model.prove_dominance_source(dominance_fixture())
        self.assertEqual(zero["physical_event_proof"]["closed_distinct_root_count"], 0)
        self.assertEqual(zero["derived_envelopes"]["first_F_upper"], "-2")
        source = dominance_fixture(c0=Q(-1, 10000), slope=Q(1))
        proof = model.prove_dominance_source(source)
        self.assertEqual(proof["physical_event_proof"]["closed_distinct_root_count"], 1)
        # This synthetic original is exactly F=t-1-1/10000 on the tail.
        root = Q(10001, 10000)
        self.assertTrue(Q(1) < root < Q(1001, 1000))
        self.assertEqual(root-1-Q(1, 10000), 0)
        row = copy.deepcopy(self.originals[V18_RAMP]); row["spec"] = source
        with self.assertRaisesRegex(model.Refusal, "source SHA-256"):
            model.check_original(row)

    def test_dominance_does_not_require_monotone_first_amplitudes(self):
        source = dominance_fixture()
        source["cos_splines"]["0"] = spline([Q(-2), Q(-4), Q(-2)], [Q(-2)]*3)
        self.assertEqual(model.derivative_controls([Q(-2), Q(-4), Q(-2)]), [Q(-4), Q(4)])
        proof = model.prove_dominance_source(source)
        self.assertEqual(proof["derived_envelopes"]["first_F_upper"], "-2")
        self.assertEqual(proof["physical_event_proof"]["closed_distinct_root_count"], 0)

    def test_conditional_sector_helper_is_not_a_three_row_answer_table(self):
        source = sector_fixture()
        proof = model.prove_sector_source(source)
        self.assertEqual(proof["derived_envelopes"]["right_half_F_derivative_upper"], "-2")
        self.assertEqual(proof["physical_event_proof"]["closed_distinct_root_count"], 1)
        row = copy.deepcopy(self.originals[V26_ZERO]); row["spec"] = source
        with self.assertRaisesRegex(model.Refusal, "source SHA-256"):
            model.check_original(row)

    def test_nonmonotone_counterexample_cannot_use_decreasing_sector_proof(self):
        source = sector_fixture(a=[Q(1), Q(1), Q(1), Q(100), Q(100)], b=[Q(1)])
        derivative = model.derivative_controls([Q(1), Q(1), Q(1), Q(100), Q(100)])
        mid_derivative = model.split_controls(derivative)[1][0]
        # theta(1/2)=0 and B=1. Thus F'(1/2)=A'(1/2)-2*pi/3.
        # Its exact lower bound is POSITIVE: this is a real counterexample to
        # accepting arbitrary positive amplitudes as globally decreasing.
        self.assertGreater(mid_derivative-2*Q(22, 7)/3, 0)
        with self.assertRaisesRegex(model.Refusal, "positive control"):
            model.prove_sector_source(source)

    def test_derivative_equality_and_wrong_sign_remain_nontruth(self):
        for first_b in (Q(2), Q(3)):
            source = sector_fixture(a=[Q(1, 4)], b=[first_b, Q(1)])
            with self.assertRaisesRegex(model.Refusal, "strict decreasing"):
                model.prove_sector_source(source)
        source = dominance_fixture(c0=Q(-2), slope=Q(11, 42), c1=Q(1))
        with self.assertRaisesRegex(model.Refusal, "strict increasing"):
            model.prove_dominance_source(source)

    def test_zero_or_inconclusive_dominance_is_not_empty_zero_set(self):
        for source in (dominance_fixture(c0=Q(0)),
                       dominance_fixture(c0=Q(-1), c1=Q(1))):
            with self.assertRaisesRegex(model.Refusal, "strict dominance"):
                model.prove_dominance_source(source)
        # The first example is identically zero: it must never be encoded as
        # a finite empty root list merely because strict bounds are absent.

    def test_crossing_requires_opposite_strict_bracket_signs(self):
        with self.assertRaisesRegex(model.Refusal, "positive tail bracket"):
            model.prove_dominance_source(dominance_fixture(c0=Q(-1), slope=Q(1)))
        with self.assertRaisesRegex(model.Refusal, "negative knot or tail"):
            model.prove_sector_source(sector_fixture(a=[Q(3)], b=[Q(2)]))
        with self.assertRaisesRegex(model.Refusal, "nonnegative-ramp"):
            model.prove_dominance_source(dominance_fixture(slope=Q(-1)))

    def test_phase_sector_is_not_inferred_from_samples_or_root_count(self):
        for case_id in (V18_ZERO, V18_RAMP, V26_ZERO):
            for name, value in (("phase_turn_offset", "0"),
                                ("phase_turn_rate", "1/3"),
                                ("phase_turn_rate", "-1/6")):
                with self.subTest(case=case_id, field=name, value=value):
                    self.bad_helper(case_id, lambda s: s.update({name: value}), "phase")

    def test_residual_channels_and_constant_tail_assumptions_are_checked(self):
        self.bad_helper(V26_ZERO, lambda s: s["cos_splines"]["0"].update(controls=["1", "1"]),
                        "harmonic-zero")
        self.bad_helper(V26_ZERO, lambda s: s["cos_splines"].pop("2"), "harmonic")
        self.bad_helper(V18_RAMP, lambda s: s["sin_splines"].update(
            {"3": copy.deepcopy(s["sin_splines"]["2"])}), "harmonic")
        self.bad_helper(V18_RAMP, lambda s: s["cos_splines"]["1"]["controls"].__setitem__(-1, "1"),
                        "constant")
        self.bad_helper(V26_ZERO, lambda s: s["cos_splines"]["1"]["controls"].__setitem__(-1, "1"),
                        "constant")

    def test_original_piece_clamping_continuity_and_degree_are_required(self):
        mutations = [
            lambda s: s["cos_splines"]["0"]["knots"].__setitem__(0, "-1"),
            lambda s: s["cos_splines"]["0"]["knots"].__setitem__(8, "1/2"),
            lambda s: s["cos_splines"]["0"]["controls"].__setitem__(8, "0"),
            lambda s: s["cos_splines"]["0"]["controls"].pop(),
            lambda s: s["cos_splines"]["0"].update(degree=True),
            lambda s: s["cos_splines"]["0"].update(degree=10000),
            lambda s: s.update(parameter_hi="3"),
            lambda s: s.update(parameter_projection={"mode": "invented"}),
        ]
        for mutation in mutations:
            self.bad_helper(V18_RAMP, mutation)

    def test_source_and_whole_row_custody_are_not_interchangeable(self):
        for case_id in self.originals:
            changes = [lambda r: r.update(id="other-source"),
                       lambda r: r.update(origin="other-producer"),
                       lambda r: r.update(kind="HARVESTED"),
                       lambda r: r["spec"].update(source_parameter_id="another-parameter"),
                       lambda r: r["spec"]["cos_splines"]["1"]["controls"].__setitem__(0, "0"),
                       lambda r: r["expected"].update(v54_disposition="CERTIFIED"),
                       lambda r: r["expected"]["observed"]["spans"][0].__setitem__(0, "other-owner"),
                       lambda r: r.update(extra_authority=True)]
            for change in changes:
                self.bad_source(case_id, change)

    def test_rational_lexical_guards_precede_fraction_construction(self):
        forbidden = (True, 1, 0.0, "1e1000000000", "1E9", "1e-9", "0.5", ".5", "1.",
                     " 1", "1 ", "1\n", "+1", "-0", "01", "1/01", "1/0", "1/-2",
                     "0/1", "1/1", "2/4", "0/2", "1_000", "\u0661", "\uff11",
                     "9"*79, "1/"+"9"*79, str(2**256), "1/"+str(2**256))
        with mock.patch.object(model, "Q", side_effect=AssertionError("unsafe Fraction call")) as ctor:
            for value in forbidden:
                with self.subTest(value=value):
                    with self.assertRaises(model.Refusal):
                        model.exact(value)
            ctor.assert_not_called()
        for value in ("0", "1", "-1", "1/2", "-1/2", str(2**255), "1/"+str(2**255)):
            self.assertEqual(str(model.exact(value)), value)

    def test_internal_helper_resource_and_numeric_type_boundaries(self):
        for controls in ([True], [1], [0.0], [Q(1)]*14, [Q(2**4097)]):
            with self.assertRaises(model.Refusal):
                model.power_coefficients(controls)
        with self.assertRaisesRegex(model.Refusal, "derived rational bit budget"):
            model.power_coefficients([Q(1, 2**4090-1), Q(1, 2**4089-1)])
        for at in (True, Q(0), Q(1), Q(-1), Q(2), Q(1, 2**257)):
            with self.assertRaises(model.Refusal):
                model.split_controls([Q(0), Q(1)], at)

    def test_report_bounds_source_bindings_and_implicit_root_semantics(self):
        mutations = [
            lambda r: r["source_witnesses"][0].update(original_source_sha256="0"*64),
            lambda r: r["source_witnesses"][0].update(original_row_sha256="0"*64),
            lambda r: r["source_witnesses"][0]["source_specific_proof"]["derived_envelopes"].update(
                first_F_upper="-1"),
            lambda r: r["source_witnesses"][1]["source_specific_proof"]["derived_envelopes"].update(
                tail_F_derivative_lower="100"),
            lambda r: r["source_witnesses"][1]["source_specific_proof"]["physical_event_proof"][
                "events"][0].update(analytic_order=2),
            lambda r: r["source_witnesses"][1]["source_specific_proof"]["physical_event_proof"][
                "events"][0]["coordinate"].update(kind="RATIONAL", value="1"),
            lambda r: r["source_witnesses"][1]["source_specific_proof"]["physical_event_proof"][
                "events"][0]["coordinate"].update(isolating_interval=["0", "1"]),
            lambda r: r["source_witnesses"][2]["source_specific_proof"]["physical_event_proof"][
                "events"][0].update(left_sign="NEGATIVE"),
        ]
        for change in mutations:
            self.bad_report(change)

    def test_proof_cuts_and_original_knot_cannot_be_laundered_into_events(self):
        self.bad_report(lambda r: r["source_witnesses"][2]["source_specific_proof"][
            "physical_event_proof"]["proof_cuts"][1].update(is_zero_event=True))
        self.bad_report(lambda r: r["source_witnesses"][2]["source_specific_proof"][
            "physical_event_proof"]["interior_source_knots"][0].update(is_zero_event=True))
        self.bad_report(lambda r: r["source_witnesses"][2]["source_specific_proof"][
            "physical_event_proof"]["maximal_sign_cells"][0].update(right={"kind": "RATIONAL", "value": "1/2"}))
        self.bad_report(lambda r: r["source_witnesses"][0]["source_specific_proof"][
            "physical_event_proof"]["exterior_endpoints"][0].update(is_zero_event=True))

    def test_boolean_integer_aliases_and_gate_count_promotions_are_rejected(self):
        for index, count in ((0, False), (1, True), (2, 0)):
            self.bad_report(lambda r: r["source_witnesses"][index]["source_specific_proof"][
                "physical_event_proof"].update(closed_distinct_root_count=count))
        for field, value in (("production_authorized", 0), ("protected_operation_count", 25),
                             ("MC_B", "ESTABLISHED"), ("MC_1", "ESTABLISHED"),
                             ("historical_owner_routes_repaired", True), ("PB00701_closed", True),
                             ("native_material_topology_or_STEP_qualified", True)):
            self.bad_report(lambda r: r["scope"].update({field: value}))
        self.bad_report(lambda r: r["frozen_v54_census"].update(missing_ordered_premises=27))
        self.bad_report(lambda r: r["summary"].update(complete_original_sources=4))

    def test_typed_json_cycle_depth_and_aggregate_resource_refusals(self):
        cycle = {}; cycle["self"] = cycle
        deep = leaf = {}
        for _ in range(model.MAX_DEPTH+1):
            leaf["next"] = {}; leaf = leaf["next"]
        bad = [cycle, deep, {"x": "a"*4097}, ["a"*4096]*100, {"n": 2**256},
               {"x": Q(1)}, {"x": 1.0}, {"x": object()}, {1: "key"}]
        for value in bad:
            with self.assertRaises(model.Refusal):
                model.canonical(value)
        self.assertNotEqual(model.canonical({"x": True}), model.canonical({"x": 1}))

    def test_json_file_duplicate_nonexact_and_resource_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"candidate.json"
            for text in ('{"x":1,"x":2}', '{"x":1.0}', '{"x":NaN}',
                         '{"x":1e1000000000}', '{"x":'+"9"*79+'}',
                         '['*2000+']'*2000, " "*(model.MAX_JSON_BYTES+1)):
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(model.Refusal):
                    model.read_report(path)
            path.write_bytes(b"\xff")
            with self.assertRaises(model.Refusal):
                model.read_report(path)

    def test_pinned_reads_are_bounded_and_source_drift_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"source.json"; path.write_bytes(b"{}\n")
            sha = model.blob(path); model.pin(path, sha)
            path.write_bytes(b"[]\n")
            with self.assertRaisesRegex(model.Refusal, "pinned source drift"):
                model.pin(path, sha)
            with path.open("wb") as stream:
                stream.truncate(model.MAX_DEPENDENCY_BYTES+1)
            with self.assertRaisesRegex(model.Refusal, "file byte budget"):
                model.pin(path, sha)

    def test_failed_fresh_proof_aborts_report_validation(self):
        with mock.patch.object(model, "prove_sector_source", side_effect=model.Refusal(
                "SEMANTIC_BLOCKER: deliberately missing sector premise")):
            with self.assertRaisesRegex(model.Refusal, "missing sector premise"):
                model.validate_report(self.report)

    def test_pinned_json_parses_the_same_verified_byte_buffer(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"custody.json"; path.write_bytes(b'{"value":1}\n')
            sha = model.blob(path)
            original_decode = model.decode_json

            def replace_after_hash(raw):
                path.write_bytes(b'{"value":2}\n')
                return original_decode(raw)

            with mock.patch.object(model, "decode_json", side_effect=replace_after_hash):
                self.assertEqual(model.pinned_json(path, sha), {"value": 1})
            with self.assertRaisesRegex(model.Refusal, "pinned source drift"):
                model.pinned_json(path, sha)

    def test_reviewed_model_ignores_matching_bytecode_and_preloaded_modules(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reviewed_model.py"
            ordinary = matching_bytecode_counterexample(path, b"VALUE = 1\n", b"VALUE = 2\n")
            self.assertEqual(ordinary.VALUE, 2)
            expected = model.blob(path)
            decoy = types.ModuleType("preloaded_model")
            decoy.VALUE = 3
            names = ("pb00701_bernstein_sector_source_witnesses", "sector_witness_reviewed_model")
            with mock.patch.dict(sys.modules, {name: decoy for name in names}):
                self.assertEqual(load_reviewed_model(path, expected).VALUE, 1)
                self.assertTrue(all(sys.modules[name] is decoy for name in names))

    def test_reviewed_model_uses_verified_buffer_and_refuses_drift_or_oversize(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reviewed_model.py"
            path.write_bytes(b"VALUE = 1\n")
            expected = model.blob(path)

            def replace_after_hash(raw, filename, mode):
                path.write_bytes(b"VALUE = 9\n")
                return builtins.compile(raw, filename, mode)

            with mock.patch.dict(globals(), {"compile": replace_after_hash}):
                self.assertEqual(load_reviewed_model(path, expected).VALUE, 1)
            with mock.patch.dict(globals(), {"compile": mock.Mock(side_effect=AssertionError(
                    "unchecked model reached compiler"))}):
                with self.assertRaisesRegex(ValueError, "source blob drift"):
                    load_reviewed_model(path, expected)
                with path.open("wb") as stream:
                    stream.truncate(1048577)
                with self.assertRaisesRegex(ValueError, "source byte limit"):
                    load_reviewed_model(path, expected)
                globals()["compile"].assert_not_called()

    def test_auditor_ignores_matching_bytecode_and_preloaded_module(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path = copied_frozen_inputs(directory)
            trusted = path.read_bytes()
            altered = trusted.replace(b"def audit(", b"def bogus(", 1)
            ordinary = matching_bytecode_counterexample(path, trusted, altered)
            self.assertFalse(hasattr(ordinary, "audit"))
            self.assertTrue(hasattr(ordinary, "bogus"))
            decoy = types.ModuleType("preloaded_auditor")
            decoy.audit = mock.Mock(side_effect=AssertionError("preloaded auditor executed"))
            names = ("sector_witness_frozen_frontier", "verify_pb00701_post_v54_frontier")
            with mock.patch.dict(sys.modules, {name: decoy for name in names}), \
                    mock.patch.object(model, "HERE", directory):
                self.assertEqual(model.canonical(model.load_originals()), model.canonical(self.originals))
                self.assertTrue(all(sys.modules[name] is decoy for name in names))
                decoy.audit.assert_not_called()

    def test_auditor_compiles_the_same_verified_buffer_after_path_replacement(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path = copied_frozen_inputs(directory)
            original = path.read_bytes()

            def replace_after_hash(raw, filename, mode):
                self.assertEqual(raw, original)
                path.write_bytes(b"raise AssertionError('unchecked replacement executed')\n")
                return builtins.compile(raw, filename, mode)

            with mock.patch.object(model, "HERE", directory), mock.patch.object(
                    model, "compile", side_effect=replace_after_hash, create=True):
                self.assertEqual(model.canonical(model.load_originals()), model.canonical(self.originals))
            with mock.patch.object(model, "HERE", directory):
                with self.assertRaisesRegex(model.Refusal, "pinned source drift"):
                    model.load_originals()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.contract or not args.self_test:
        model.validate_report(model.read_report())
        print(json.dumps({"result": "THREE_COMPLETE_ORIGINAL_SOURCE_WITNESSES",
                          "root_free_sources": 1, "one_simple_root_sources": 2,
                          "historical_dispositions_changed": False,
                          "MC_B": "NOT_ESTABLISHED"}, sort_keys=True))
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(SourceWitnessTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            raise SystemExit(1)


if __name__ == "__main__":
    main()
