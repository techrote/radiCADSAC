#!/usr/bin/env python3
"""Independent exact-source checks for all selected implicit-root refinements.

One fresh qualified-parent replay and complete 69-root refinement supplies the
normal contract. Independent symbolic coefficient evaluation and conditional
counterexamples check the refinement mathematics without using a saved PASS as
proof or promoting synthetic sources into the original-source cohort.
"""
from __future__ import annotations

import argparse
import builtins
import copy
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import py_compile
import re
import sys
import tempfile
import types
import unittest
from unittest import mock

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TASK = "research/machining-completeness/tasks/MC-038/"
MODEL_PATH = HERE / "pb00701_selected_implicit_root_refinement.py"
MODEL_BLOB = "47dfd31a204d6edfb5fb2a82d7ce84c565aca7da"
RUNTIME_PATH = TASK + "pb00701_pinned_source_runtime.py"
RUNTIME_BLOB = "058c06e4a1e0aee0297880622ee1157a46ef9067"
LOWERER_PATH = TASK + "pb00701_coupled_bspline_model.py"
LOWERER_BLOB = "a086b625e1a6dea8bd202699d161167bb69cc9e7"
TRIG_PATH = TASK + "pb00701_transverse_trig_interval.py"
TRIG_BLOB = "2320f92efe4316d865a89f6d848737e2c000ca4d"


def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load_reviewed_model(path, expected):
    """Execute the bounded verified source buffer, bypassing caches/preloads."""
    with Path(path).open("rb") as stream:
        raw = stream.read(1048577)
    if len(raw) > 1048576:
        raise ValueError("MODEL_BYTE_LIMIT")
    if git_blob(raw) != expected:
        raise ValueError("MODEL_SOURCE_DRIFT")
    module = types.ModuleType("selected_refinement_reviewed_model")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec", dont_inherit=True, optimize=0), module.__dict__)
    return module


def install_accepted_stale_cache(path, trusted, altered):
    """Positive control: ordinary import must actually accept the stale payload."""
    if len(trusted) != len(altered) or trusted == altered:
        raise AssertionError("matching source size required for stale-cache control")
    alternate = path.with_name("stale_payload.py")
    path.write_bytes(trusted)
    alternate.write_bytes(altered)
    for source in (path, alternate):
        os.utime(source, (1700000000, 1700000000))
    cache = Path(importlib.util.cache_from_source(str(path)))
    cache.parent.mkdir(parents=True, exist_ok=True)
    py_compile.compile(str(alternate), cfile=str(cache), doraise=True,
                       invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
    spec = importlib.util.spec_from_file_location("ordinary_refinement_cache_control", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_bootstrap_tests(model_path, model_blob):
    class VerifierBootstrapTests(unittest.TestCase):
        def test_actual_accepted_cache_and_preloaded_model_cannot_replace_source(self):
            trusted = Path(model_path).read_bytes()
            self.assertEqual(git_blob(trusted), model_blob)
            payload = b"CACHE_SUBSTITUTION = True\n#"
            altered = payload + b" " * (len(trusted) - len(payload))
            with tempfile.TemporaryDirectory(prefix="selected-refiner-cache-") as directory:
                here = Path(directory) / TASK
                here.mkdir(parents=True)
                path = here / Path(model_path).name
                ordinary = install_accepted_stale_cache(path, trusted, altered)
                self.assertTrue(ordinary.CACHE_SUBSTITUTION)
                fake = types.ModuleType("selected_refinement_reviewed_model")
                fake.CACHE_SUBSTITUTION = True
                with mock.patch.dict(sys.modules, {fake.__name__: fake, Path(model_path).stem: fake}):
                    checked = load_reviewed_model(path, model_blob)
                    self.assertFalse(hasattr(checked, "CACHE_SUBSTITUTION"))
                    self.assertTrue(callable(checked.expected_report))
                    self.assertIs(sys.modules[fake.__name__], fake)

        def test_checked_buffer_survives_posthash_path_replacement(self):
            with tempfile.TemporaryDirectory(prefix="selected-refiner-replace-") as directory:
                path = Path(directory) / "model.py"
                trusted = b"VALUE = 1\n"
                path.write_bytes(trusted)

                def replace(raw, filename, mode, **options):
                    path.write_bytes(b"VALUE = 9\n")
                    return builtins.compile(raw, filename, mode, **options)

                with mock.patch.dict(load_reviewed_model.__globals__, {"compile": mock.Mock(side_effect=replace)}):
                    checked = load_reviewed_model(path, git_blob(trusted))
                self.assertEqual(checked.VALUE, 1)
                with self.assertRaisesRegex(ValueError, "SOURCE_DRIFT"):
                    load_reviewed_model(path, git_blob(trusted))

        def test_model_bounds_and_blob_drift_precede_compile(self):
            with tempfile.TemporaryDirectory(prefix="selected-refiner-bounds-") as directory:
                path = Path(directory) / "model.py"
                path.write_bytes(b"VALUE = 1\n")
                compiler = mock.Mock(side_effect=AssertionError("unverified source compiled"))
                with mock.patch.dict(load_reviewed_model.__globals__, {"compile": compiler}):
                    with self.assertRaisesRegex(ValueError, "SOURCE_DRIFT"):
                        load_reviewed_model(path, "0" * 40)
                    with path.open("wb") as stream:
                        stream.truncate(1048577)
                    with self.assertRaisesRegex(ValueError, "BYTE_LIMIT"):
                        load_reviewed_model(path, "0" * 40)
                compiler.assert_not_called()

        def test_original_future_flags_and_assertions_are_preserved(self):
            with tempfile.TemporaryDirectory(prefix="selected-refiner-flags-") as directory:
                path = Path(directory) / "model.py"
                eager = b"VALUE: int = 1\n"
                path.write_bytes(eager)
                checked = load_reviewed_model(path, git_blob(eager))
                self.assertIs(checked.__annotations__["VALUE"], int)
                assertion = b"assert False, 'original assertion survives'\n"
                path.write_bytes(assertion)
                with self.assertRaisesRegex(AssertionError, "original assertion survives"):
                    load_reviewed_model(path, git_blob(assertion))

    return VerifierBootstrapTests


def synthetic_spec(*, controls=("-1", "1"), degree=1, knots=("0", "0", "1", "1"),
                   harmonic="0", channel="cos_splines", offset="0", rate="0",
                   lo="0", hi="1", parameter="conditional-test-parameter"):
    """A test premise only; never an original-source admission record."""
    spec = {"grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
            "cos_splines": {}, "sin_splines": {}, "parameter_lo": lo,
            "parameter_hi": hi, "phase_turn_offset": offset,
            "phase_turn_rate": rate, "source_parameter_id": parameter}
    spec[channel][harmonic] = {"degree": degree, "knots": list(knots),
                               "controls": list(controls)}
    return spec


def round_outward(raw, bits=80):
    scale = 1 << bits
    return (Q((raw[0] * scale).__floor__(), scale),
            Q((raw[1] * scale).__ceil__(), scale))


def interval_sign(interval):
    return 1 if interval[0] > 0 else -1 if interval[1] < 0 else 0


def polynomial_value(coefficients, x):
    result = Q(0)
    for coefficient in reversed(coefficients):
        result = result * x + coefficient
    return result


def read_pinned_runtime():
    path = ROOT / RUNTIME_PATH
    with path.open("rb") as stream:
        raw = stream.read(1048577)
    if len(raw) > 1048576 or git_blob(raw) != RUNTIME_BLOB:
        raise AssertionError("independent runtime source drift")
    module = types.ModuleType("independent_selected_refinement_runtime")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec", dont_inherit=True, optimize=0), module.__dict__)
    return module


def lower_original_coefficients(lowerer, spec):
    """Independent symbolic lowering, including both exact knot-side limits."""
    result = {}
    for channel in ("cos_splines", "sin_splines"):
        for harmonic, spline in spec[channel].items():
            parts = lowerer.lower_bspline(spline)
            for left, right in zip(parts, parts[1:]):
                if left["source_interval"][1] != right["source_interval"][0]:
                    raise AssertionError("independent coefficient pieces have a gap")
                if left["right_limit"] != right["left_limit"]:
                    raise AssertionError("selected original coefficient is discontinuous")
            result[channel, harmonic] = parts
    return result


def symbolic_point(trig, spec, parts, source_span, point):
    """Original global phase plus local exact polynomial amplitudes.

    This deliberately does not call the candidate's B-spline basis or interval
    assembly helpers. Only the already qualified trig enclosure is shared.
    """
    a, b = map(Q, source_span)
    x = Q(point)
    if not a <= x <= b:
        raise AssertionError("point escaped its original source span")
    phase = Q(spec["phase_turn_offset"]) + Q(spec["phase_turn_rate"]) * x
    lo = hi = Q(0)
    amplitudes = {}
    for (channel, harmonic), coefficients in parts.items():
        selected = [p for p in coefficients if p["source_interval"][0] <= a < b <= p["source_interval"][1]]
        if len(selected) != 1:
            raise AssertionError("original common span is not one symbolic coefficient piece")
        piece = selected[0]
        left, right = piece["source_interval"]
        amplitude = polynomial_value(piece["coefficients"], (x-left)/(right-left))
        amplitudes[channel, harmonic] = amplitude
        enclosure = trig.trig(int(harmonic) * phase)[0 if channel == "cos_splines" else 1]
        scaled = (enclosure[0] * amplitude, enclosure[1] * amplitude)
        lo += min(scaled)
        hi += max(scaled)
    raw = (lo, hi)
    outward = round_outward(raw)
    if not outward[0] <= raw[0] <= raw[1] <= outward[1]:
        raise AssertionError("independent outward enclosure lost containment")
    return amplitudes, raw, outward


def actual_source_event_map(parent_report):
    """Select only actual parent implicit simple events, never a static map."""
    selected = {}
    for source in parent_report["source_cases"]:
        zeros = source["zero_set"]
        if zeros["kind"] == "CLOSED_CONTINUUM_ZERO_COMPONENT":
            continue
        if zeros["kind"] != "FINITE_ORIGINAL_SOURCE_ZERO_SET":
            raise AssertionError("unrecognized qualified zero-set kind")
        for event in zeros["events"]:
            coordinate = event["coordinate"]
            if coordinate["kind"] == "RATIONAL":
                continue
            if coordinate["kind"] != "UNIQUE_IMPLICIT_ZERO_OF_PINNED_ORIGINAL_SOURCE":
                raise AssertionError("unrecognized qualified implicit locator")
            if event["order"] != {"kind": "SMOOTH", "value": 1}:
                raise AssertionError("selected parent root is not simple")
            key = source["case_id"], event["event_id"]
            if key in selected:
                raise AssertionError("duplicate source-scoped parent event")
            selected[key] = (source, event)
    return selected


class ConditionalMathematicsTests(unittest.TestCase):
    """Synthetic premises exercise the kernel and never establish corpus truth."""

    def test_true_midpoint_zero_refuses_without_guessed_half(self):
        source = model.prepare_source_spec(synthetic_spec(controls=("-1", "1")))
        with self.assertRaises(model.Refusal):
            model.point_receipt(source, Q(1, 2))
        with self.assertRaises(model.Refusal):
            model.refine_bracket(source, ["0", "1"], -1, 1, 1)

    def test_positive_and_negative_rounding_loss_refuse(self):
        tiny = Q(1, 1 << 82)
        self.assertEqual(interval_sign((tiny, tiny)), 1)
        self.assertEqual(interval_sign(round_outward((tiny, tiny))), 0)
        self.assertEqual(interval_sign((-tiny, -tiny)), -1)
        self.assertEqual(interval_sign(round_outward((-tiny, -tiny))), 0)
        for value in (tiny, -tiny):
            spec = synthetic_spec(controls=(str(value), str(value)))
            source = model.prepare_source_spec(spec)
            with self.subTest(sign=1 if value > 0 else -1), self.assertRaises(model.Refusal):
                model.point_receipt(source, Q(1, 2))

    def test_jump_inside_bracket_cannot_create_a_root_from_opposite_signs(self):
        # F is -1 then +1, so there is no zero despite opposite endpoints.
        spec = synthetic_spec(degree=0, controls=("-1", "1"),
                              knots=("0", "1/2", "1"))
        with self.assertRaises(model.Refusal):
            model.prepare_source_spec(spec)

    def test_jump_at_right_endpoint_requires_left_right_agreement(self):
        # The first span is identically -1. A right-continuous endpoint value
        # +1 at t=1 cannot justify IVT on [0,1], even without an interior knot.
        spec = synthetic_spec(controls=("-1", "-1", "1", "1"),
                              knots=("0", "0", "1", "1", "2", "2"), hi="2")
        with self.assertRaises(model.Refusal):
            model.prepare_source_spec(spec)

    def test_forged_prepared_edges_cannot_hide_an_original_coefficient_knot(self):
        # Continuous, with a genuine knot at1 and a unique zero after it.
        # Removing the knot from metadata must not turn (0,2) into one span.
        source=model.prepare_source_spec(synthetic_spec(
            controls=("-1","-1/2","-1/2","1"),
            knots=("0","0","1","1","2","2"),hi="2"))
        forged=source._replace(edges=(Q(0),Q(2)))
        with self.assertRaises(model.Refusal):
            model.refine_bracket(forged,["0","2"],-1,1,1)

    def test_nonzero_but_undecided_enclosure_does_not_supply_a_sign(self):
        source=model.prepare_source_spec(synthetic_spec(controls=("1","1"),
            harmonic="1",offset="1/8",rate="0"))
        self.assertEqual(model.point_receipt(source,Q(1,2))["sign"],1)
        # [-1,1] is a true but inconclusive enclosure of cos(pi/4).
        with mock.patch.object(source.trig_provider,"trig",return_value=((Q(-1),Q(1)),(Q(-1),Q(1)))):
            with self.assertRaises(model.Refusal) as error:
                model.point_receipt(source,Q(1,2))
        self.assertEqual(error.exception.code,"UNRESOLVED_POINT_SIGN")

    def test_endpoint_zero_and_wrong_inherited_signs_are_not_strict_brackets(self):
        source = model.prepare_source_spec(synthetic_spec())
        for bracket, left, right in ((["1/2", "1"], -1, 1),
                                     (["0", "1"], 1, -1),
                                     (["0", "1"], -1, -1),
                                     (["0", "1"], 0, 1),
                                     (["0", "1"], True, 1)):
            with self.subTest(bracket=bracket, signs=(left, right)), self.assertRaises(model.Refusal):
                model.refine_bracket(source, bracket, left, right, 0)

    def test_prepared_source_is_independent_of_mutable_input_aliases(self):
        raw = synthetic_spec(controls=("-1", "2"))
        source = model.prepare_source_spec(raw)
        before = model.point_receipt(source, Q(1, 2))
        raw["cos_splines"]["0"]["controls"][:] = ["200", "200"]
        raw["phase_turn_rate"] = "2"
        self.assertEqual(model.point_receipt(source, Q(1, 2)), before)

    def test_forged_prepared_phase_channels_or_identity_cannot_reuse_source_hash(self):
        source=model.prepare_source_spec(synthetic_spec(controls=("-1","2")))
        channel=source.channels[0]
        changed_channel=channel._replace(spline=channel.spline._replace(controls=(Q(2),Q(2))))
        forged=(source._replace(offset=Q(1,4)),source._replace(rate=Q(1,4)),
                source._replace(source_parameter_id="another-original-parameter"),
                source._replace(source_sha256="0"*64),source._replace(channels=(changed_channel,)))
        for i,value in enumerate(forged):
            with self.subTest(index=i),self.assertRaises(model.Refusal):
                model.point_receipt(value,Q(1,2))

    def test_bounded_source_structure_rejects_invalid_grammar(self):
        bad = []
        for field, value in (("degree", True), ("degree", -1),
                             ("controls", []), ("knots", ["0", "0", "1", "0"]),
                             ("controls", ["1/0", "1"]),
                             ("controls", ["1e1000000000", "1"]),
                             ("knots", ["-1", "0", "1", "2"])):
            value_spec = synthetic_spec()
            value_spec["cos_splines"]["0"][field] = value
            bad.append(value_spec)
        bad.append(synthetic_spec(degree=8, controls=("1",)*9,
                                  knots=("0",)*9+("1",)*9))
        bad.append(synthetic_spec(controls=("1",)*17,
                                  knots=("0", "0")+tuple(str(Q(i,16)) for i in range(1,16))+("1", "1")))
        bad.append(synthetic_spec(controls=("1",)*5,
                                  knots=("0", "0", "1/2", "1/2", "1/2", "1", "1")))
        for field, value in (("grammar", "another-grammar"),
                             ("source_parameter_id", False),
                             ("parameter_hi", "0"), ("phase_turn_rate", "3"),
                             ("phase_turn_offset", "-3"),
                             ("cos_splines", {"8": {"degree":0,"knots":["0","1"],"controls":["1"]}})):
            value_spec = synthetic_spec()
            value_spec[field] = value
            bad.append(value_spec)
        missing = synthetic_spec(); del missing["phase_turn_offset"]; bad.append(missing)
        extra = synthetic_spec(); extra["unregistered"] = True; bad.append(extra)
        bad.extend((None, [], True, 1, "source"))
        for i, source in enumerate(bad):
            with self.subTest(index=i), self.assertRaises(model.Refusal):
                model.prepare_source_spec(source)


    def test_degree_seven_and_two_piece_exact_amplitudes(self):
        source = model.prepare_source_spec(synthetic_spec(
            degree=7, controls=("0",)*7+("1",), knots=("0",)*8+("1",)*8))
        spline = source.channels[0].spline
        for point in (Q(0), Q(1, 2), Q(1)):
            self.assertEqual(model.spline_value(spline, point), point**7)
        two = model.prepare_source_spec(synthetic_spec(
            degree=7, controls=("0",)*7+("1",)+("1",)*7+("2",),
            knots=("0",)*8+("1",)*8+("2",)*8, hi="2"))
        spline = two.channels[0].spline
        self.assertEqual(model.spline_value(spline, Q(3, 2)), Q(129,128))
        self.assertEqual(model.spline_value(spline, Q(1), "LEFT_LIMIT"), Q(1))
        self.assertEqual(model.spline_value(spline, Q(1), "RIGHT_LIMIT"), Q(1))
        self.assertEqual(model.spline_value(spline, Q(2)), Q(2))
        self.assertTrue(two.continuity)
        for record in two.continuity:
            self.assertEqual(record.left_limit, record.right_limit)

    def test_closed_final_value_and_inward_side_conventions(self):
        source = model.prepare_source_spec(synthetic_spec(controls=("3", "3")))
        spline = source.channels[0].spline
        for point in (Q(0), Q(1, 2), Q(1)):
            self.assertEqual(model.spline_value(spline, point), Q(3))
        self.assertEqual(model.spline_value(spline, Q(0), "RIGHT_LIMIT"), Q(3))
        self.assertEqual(model.spline_value(spline, Q(1), "LEFT_LIMIT"), Q(3))
        for point, side in ((Q(0), "LEFT_LIMIT"), (Q(1), "RIGHT_LIMIT"),
                            (Q(1,2), "UNREGISTERED_SIDE")):
            with self.subTest(point=str(point), side=side), self.assertRaises(model.Refusal):
                model.spline_value(spline, point, side)

    def test_global_parameter_offset_and_sine_phase_are_preserved(self):
        for offset, expected in (("0", -1), ("-1/2", 1)):
            source = model.prepare_source_spec(synthetic_spec(
                controls=("1", "1"), knots=("1", "1", "2", "2"),
                lo="1", hi="2", harmonic="1", rate="1/4", offset=offset))
            point = model.point_receipt(source, Q(2))
            self.assertEqual(point["sign"], expected)
            self.assertEqual(point["outward_dyadic_interval"], [str(expected)]*2)
            self.assertIs(point["coordinate_is_original_parameter"], True)
        sine = model.prepare_source_spec(synthetic_spec(controls=("1", "1"),
            harmonic="1", channel="sin_splines", offset="-1/4", rate="0"))
        self.assertEqual(model.point_receipt(sine, Q(1,2))["outward_dyadic_interval"], ["-1", "-1"])

    def test_negative_amplitude_reverses_noncardinal_enclosure_bounds(self):
        source = model.prepare_source_spec(synthetic_spec(controls=("-3", "-3"),
            harmonic="1", offset="1/8", rate="0"))
        raw = source.trig_provider.trig(Q(1,8))[0]
        expected = round_outward((-3*raw[1], -3*raw[0]))
        self.assertLess(expected[1], 0)
        point = model.point_receipt(source, Q(1,2))
        self.assertEqual(point["outward_dyadic_interval"], list(map(str, expected)))
        self.assertEqual(point["sign"], -1)

    def test_zero_steps_keep_a_proved_initial_bracket_without_cohort_claim(self):
        source = model.prepare_source_spec(synthetic_spec(controls=("-1", "2")))
        result = model.refine_bracket(source, ["0", "1"], -1, 1, 0)
        self.assertEqual(result["requested_steps"], 0)
        self.assertEqual(result["trace"], [])
        self.assertEqual(result["initial_bracket"], result["final_bracket"])
        self.assertEqual(result["initial_endpoint_receipts"], result["final_endpoint_receipts"])
        self.assertEqual(result["initial_width"], result["final_width"])
        self.assertIs(result["conditional_on_unique_simple_root"], True)
        self.assertNotIn("all_selected_events_refined", result)
        self.assertNotIn("complete_original_source_zero_set", result)
        model.bounded_bytes(result)

    def test_bisection_uses_strict_receipts_and_conditional_uniqueness(self):
        source = model.prepare_source_spec(synthetic_spec(controls=("-1", "2")))
        result = model.refine_bracket(source, ["0", "1"], -1, 1, 12)
        self.assertEqual(len(result["trace"]), 12)
        lo, hi = map(Q, result["final_bracket"])
        self.assertLess(lo, Q(1,3)); self.assertLess(Q(1,3), hi)
        self.assertEqual(hi-lo, Q(1,4096))
        self.assertEqual(result["final_width"], "1/4096")
        self.assertIs(result["no_exact_root_coordinate_claimed"], True)
        self.assertIs(result["proof_cuts_create_no_physical_events"], True)


class SelectedRefinementTests(unittest.TestCase):
    replay = None

    @classmethod
    def setUpClass(cls):
        if cls.replay is None:
            cls.replay = model.replay_refinements(12)
        cls.report = model.report_from_replay(cls.replay)
        cls.expected_bytes = model.bounded_bytes(cls.report)
        cls.parent = cls.replay["parent_report"]
        cls.originals = cls.replay["indexed"]
        cls.selected = actual_source_event_map(cls.parent)
        cls.refinements = {(r["case_id"], r["event_id"]): r for r in cls.report["refinements"]}

    def report_rejects(self, mutate):
        changed = json.loads(self.expected_bytes)
        mutate(changed)
        with self.assertRaises(model.Refusal):
            model._compare_with_replayed_bytes(changed, self.expected_bytes)

    def assert_point(self, receipt, coordinate, sign=None):
        self.assertEqual(receipt["coordinate"], str(Q(coordinate)))
        self.assertIs(type(receipt["sign"]), int)
        self.assertIn(receipt["sign"], (-1,1))
        if sign is not None:
            self.assertEqual(receipt["sign"], sign)
        self.assertEqual(receipt["dyadic_bits"], 80)
        self.assertIs(type(receipt["dyadic_bits"]), int)
        self.assertIs(receipt["strict"], True)
        self.assertIs(receipt["exact_source_enclosure_is_contained"], True)
        self.assertIs(receipt["coordinate_is_original_parameter"], True)
        interval = tuple(map(Q, receipt["outward_dyadic_interval"]))
        self.assertLessEqual(*interval)
        self.assertEqual(interval_sign(interval), receipt["sign"])
        for value, text in zip(interval, receipt["outward_dyadic_interval"]):
            self.assertEqual(str(value), text)
            self.assertEqual((1 << 80) % value.denominator, 0)
        return interval

    def test_exact_cohort_comes_from_fresh_parent_physical_events(self):
        self.assertEqual(len(self.selected), 69)
        self.assertEqual(len({cid for cid,_ in self.selected}), 28)
        self.assertEqual(len(self.report["refinements"]), len(self.refinements))
        self.assertEqual(set(self.refinements), set(self.selected))
        self.assertEqual(self.report["requested_steps"], 12)
        self.assertEqual(self.report["parent_baseline"], self.parent)
        self.assertEqual(digest(self.parent), model.PARENT_REPORT_VALUE_SHA256)
        self.assertEqual(self.report["gates"], self.parent["gates"])
        summary = self.parent["summary"]
        self.assertEqual((summary["original_source_count"], summary["finite_source_count"],
            summary["continuum_source_count"], summary["sum_of_per_source_distinct_isolated_zeros"],
            summary["rational_zero_coordinates"], summary["implicit_original_source_zero_locators"],
            summary["maximal_connected_nonzero_cells"]), (50,49,1,81,12,69,128))
        continuum = [s for s in self.parent["source_cases"]
                     if s["zero_set"]["kind"] == "CLOSED_CONTINUUM_ZERO_COMPONENT"]
        self.assertEqual(len(continuum),1)
        self.assertIs(continuum[0]["zero_set"]["events"], None)
        self.assertNotIn(continuum[0]["case_id"], {cid for cid,_ in self.selected})

    def test_each_refinement_binds_original_source_and_actual_parent_event(self):
        parameters = set()
        for key, record in self.refinements.items():
            source, event = self.selected[key]
            original = self.originals[key[0]]
            parameters.add(record["source_parameter_id"])
            self.assertEqual(record["source_sha256"], digest(original["spec"]))
            self.assertEqual(record["source_sha256"], source["source_sha256"])
            self.assertEqual(record["original_row_sha256"], digest(original))
            self.assertEqual(record["source_parameter_id"], source["source_parameter_id"])
            self.assertEqual(record["source_interval"], source["source_interval"])
            self.assertEqual(record["phase_turn_law"], source["phase_turn_law"])
            self.assertEqual(record["parent_source_record_sha256"], digest(source))
            self.assertEqual(record["parent_event_sha256"], digest(event))
            self.assertEqual(record["parent_coordinate"], event["coordinate"])
            self.assertEqual(record["parent_uniqueness_evidence"], event["coordinate"]["uniqueness_evidence"])
            self.assertEqual(record["inherited_order"], {"kind":"SMOOTH","value":1})
            self.assertIs(record["unique_simple_root_inherited"], True)
            self.assertEqual(record["parent_left_sign"], event["left_sign"])
            self.assertEqual(record["parent_right_sign"], event["right_sign"])
            self.assertEqual(record["event_ordinal"], source["zero_set"]["events"].index(event))
            coordinate = record["coordinate"]
            self.assertEqual(coordinate["kind"], "REFINED_IMPLICIT_ZERO_OF_PINNED_ORIGINAL_SOURCE")
            self.assertEqual(coordinate["source_case_id"], key[0])
            self.assertEqual(coordinate["source_sha256"], source["source_sha256"])
            self.assertEqual(coordinate["source_parameter_id"], source["source_parameter_id"])
            self.assertEqual(coordinate["source_piece_index"], event["coordinate"]["source_piece_index"])
            self.assertEqual(coordinate["source_span"], event["coordinate"]["source_span"])
            self.assertEqual(coordinate["strict_open_bracket"], record["refinement"]["final_bracket"])
        self.assertEqual(len(parameters), 5)

    def test_all_trace_halves_widths_endpoint_signs_and_source_spans(self):
        points = 0
        knots_as_bounds = 0
        for key, record in self.refinements.items():
            source, event = self.selected[key]
            initial = event["coordinate"]["strict_open_bracket"]
            refined = record["refinement"]
            self.assertEqual(refined["initial_bracket"], initial)
            self.assertEqual(refined["requested_steps"], 12)
            self.assertEqual(len(refined["trace"]), 12)
            self.assertIs(refined["conditional_on_unique_simple_root"], True)
            self.assertIs(refined["source_continuity_checked"], True)
            self.assertIs(refined["all_points_in_original_parameter"], True)
            self.assertIs(refined["proof_cuts_create_no_physical_events"], True)
            lo, hi = map(Q, initial)
            width = hi-lo
            source_lo, source_hi = map(Q, record["original_source_span"])
            self.assertLessEqual(source_lo, lo); self.assertLessEqual(hi, source_hi)
            if lo == source_lo or hi == source_hi:
                knots_as_bounds += 1
            left_sign, right_sign = event["left_sign"], event["right_sign"]
            self.assertEqual(left_sign, -right_sign)
            left, right = refined["initial_endpoint_receipts"]
            self.assert_point(left, lo, left_sign); self.assert_point(right, hi, right_sign)
            points += 2
            for step, entry in enumerate(refined["trace"], 1):
                self.assertEqual(entry["step"], step)
                self.assertEqual(entry["before_bracket"], list(map(str,(lo,hi))))
                midpoint = (lo+hi)/2
                self.assertEqual(entry["midpoint"], str(midpoint))
                receipt = entry["midpoint_receipt"]
                self.assert_point(receipt, midpoint)
                points += 1
                if receipt["sign"] == left_sign:
                    lo, left = midpoint, receipt
                    self.assertEqual(entry["kept_half"], "RIGHT")
                else:
                    self.assertEqual(receipt["sign"], right_sign)
                    hi, right = midpoint, receipt
                    self.assertEqual(entry["kept_half"], "LEFT")
                self.assertEqual(entry["after_bracket"], list(map(str,(lo,hi))))
                self.assertEqual(hi-lo, width/(1 << step))
                self.assertEqual(entry["width"], str(hi-lo))
            self.assertEqual(refined["final_bracket"], list(map(str,(lo,hi))))
            self.assertEqual(refined["initial_width"], str(width))
            self.assertEqual(refined["final_width"], str(width/(1 << 12)))
            self.assertEqual(refined["final_endpoint_receipts"], [left,right])
        self.assertEqual(points, 966)
        self.assertEqual(knots_as_bounds, 13)

    def test_independent_symbolic_amplitudes_and_enclosures_at_every_point(self):
        runtime = read_pinned_runtime()
        self.assertEqual(model.PINS[LOWERER_PATH], LOWERER_BLOB)
        self.assertEqual(model.PINS[TRIG_PATH], TRIG_BLOB)
        aliases = {"radicadsac_mc032_event_engine": "research/machining-completeness/tasks/MC-032/event_engine.py"}
        points = amplitudes = 0
        cache = {}
        with runtime.PinnedRuntime(ROOT, model.PINS, aliases) as checked:
            lower = checked.load(LOWERER_PATH)
            trig = checked.load(TRIG_PATH)
            for key, record in self.refinements.items():
                cid = key[0]
                spec = self.originals[cid]["spec"]
                if cid not in cache:
                    cache[cid] = (lower_original_coefficients(lower, spec),
                                  model.prepare_source_spec(spec))
                parts, prepared = cache[cid]
                prepared_channels = {("cos_splines" if c.kind == "cos" else "sin_splines",str(c.harmonic)):c.spline
                                     for c in prepared.channels}
                self.assertEqual(set(parts), set(prepared_channels))
                refinement = record["refinement"]
                receipts = refinement["initial_endpoint_receipts"] + [s["midpoint_receipt"] for s in refinement["trace"]]
                for receipt in receipts:
                    point = Q(receipt["coordinate"])
                    values, raw, outward = symbolic_point(trig, spec, parts,
                        record["original_source_span"], point)
                    for channel, value in values.items():
                        self.assertEqual(model.spline_value(prepared_channels[channel],point), value,
                                         (cid,channel,str(point)))
                        amplitudes += 1
                    self.assertEqual(receipt["outward_dyadic_interval"], list(map(str,outward)))
                    self.assertEqual(receipt["source_spec_sha256"], digest(spec))
                    self.assertEqual(receipt["sign"], interval_sign(raw))
                    self.assertEqual(receipt["sign"], interval_sign(outward))
                    points += 1
        self.assertEqual((len(cache),points,amplitudes),(28,966,4130))


    def test_physical_negative_factor_signs_and_v44_cut_neutrality_survive(self):
        v17 = "composite:PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER:tail100"
        v13 = "composite:PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC:tail100"
        for ordinal in (0,1):
            a = self.refinements[v17,f"ROOT_{ordinal}"]
            b = self.refinements[v13,f"ROOT_{ordinal}"]
            self.assertEqual(a["parent_coordinate"]["strict_open_bracket"],
                             b["parent_coordinate"]["strict_open_bracket"])
            self.assertEqual(a["refinement"]["final_bracket"],b["refinement"]["final_bracket"])
            self.assertEqual(a["parent_left_sign"],-b["parent_left_sign"])
            self.assertEqual(a["parent_right_sign"],-b["parent_right_sign"])
            self.assertNotEqual(a["source_sha256"],b["source_sha256"])
        v44 = "harvested:verify_pb00701_v44:ffaea08e30c9"
        selected = [(key,r) for key,r in self.refinements.items() if key[0] == v44]
        self.assertEqual(len(selected),1)
        record = selected[0][1]
        self.assertEqual(record["refinement"]["initial_bracket"],["9/16","37/64"])
        self.assertEqual((record["parent_left_sign"],record["parent_right_sign"]),(-1,1))
        self.assertEqual(record["source_parameter_id"],"pb00701-v44-algebraic-orientation")
        self.assertEqual(len(self.selected[selected[0][0]][0]["zero_set"]["events"]),1)
        self.assertIs(record["refinement"]["proof_cuts_create_no_physical_events"],True)

    def test_actual_original_producer_failure_is_whole_request_nontruth(self):
        parent = model.qualified_parent_module()
        v2 = parent.qualified_v2_module()
        runtime_module = v2._runtime_module()
        original_load = runtime_module.PinnedRuntime.load
        invoked = []

        def fail_original():
            invoked.append("actual-five-source-proof")
            raise RuntimeError("CONTROLLED_ORIGINAL_SOURCE_PRODUCER_FAILURE")

        def load(runtime, path):
            module = original_load(runtime,path)
            if Path(str(path)).name == v2.PRODUCERS["five"][0]:
                module.expected_report = fail_original
            return module

        with mock.patch.object(model,"qualified_parent_module",return_value=parent), \
             mock.patch.object(parent,"qualified_v2_module",return_value=v2), \
             mock.patch.object(v2,"_runtime_module",return_value=runtime_module), \
             mock.patch.object(runtime_module.PinnedRuntime,"load",autospec=True,side_effect=load):
            result = model.refine_selected(12)
        self.assertEqual(invoked,["actual-five-source-proof"])
        self.assertEqual(result["status"],"REFUSED")
        self.assertIs(result["proof_established"],False)
        self.assertIs(result["all_selected_events_refined"],False)
        self.assertNotIn("refinements",result)
        self.assertNotIn("parent_baseline",result)

    def test_one_actual_selected_midpoint_failure_cannot_become_partial_success(self):
        # Reuse the already freshly established parent context for this fault
        # control. The actual public selection/refinement path still executes.
        parent = model.qualified_parent_module()
        target = self.report["refinements"][3]
        target_point = Q(target["refinement"]["trace"][0]["midpoint"])
        original_point = model.point_receipt
        invoked = []
        successful = []

        def undecided(source, coordinate):
            if source.source_sha256 == target["source_sha256"] and Q(coordinate) == target_point:
                invoked.append((source.source_sha256,str(coordinate)))
                raise model.Refusal("CONTROLLED_SELECTED_MIDPOINT_UNDECIDED", "UNRESOLVED_POINT_SIGN")
            result = original_point(source,coordinate)
            successful.append(result["coordinate"])
            return result

        with mock.patch.object(model,"qualified_parent_module",return_value=parent), \
             mock.patch.object(parent,"replay_sources",return_value=copy.deepcopy(self.replay["parent_context"])), \
             mock.patch.object(model,"point_receipt",side_effect=undecided):
            result = model.refine_selected(12)
        self.assertEqual(len(invoked),1)
        self.assertGreater(len(successful),14)
        self.assertEqual(result["status"],"REFUSED")
        self.assertIs(result["proof_established"],False)
        self.assertIs(result["all_selected_events_refined"],False)
        self.assertNotIn("refinements",result)
        self.assertNotIn("successful_partial_count",result)

    def test_formatter_rejects_missing_duplicate_and_rebound_cohort_records(self):
        mutations = [
            lambda r:r["selected_events"].pop(),
            lambda r:r["refinements"].pop(),
            lambda r:r["refinements"].__setitem__(1,copy.deepcopy(r["refinements"][0])),
            lambda r:r["refinements"][0].__setitem__("source_sha256","0"*64),
            lambda r:r["refinements"][0].__setitem__("parent_event_sha256","0"*64),
            lambda r:r["refinements"][0].__setitem__("event_ordinal",True),
            lambda r:r["refinements"][0].__setitem__("parent_uniqueness_evidence",{}),
            lambda r:r["refinements"][0].__setitem__("inherited_order",{"kind":"SMOOTH","value":2}),
            lambda r:r["refinements"][0].__setitem__("unique_simple_root_inherited",False),
        ]
        for i,mutate in enumerate(mutations):
            changed = copy.deepcopy(self.replay)
            mutate(changed)
            with self.subTest(index=i),self.assertRaises(model.Refusal):
                model.report_from_replay(changed)

    def test_formatter_preserves_original_rows_and_qualified_parent_authority(self):
        cid = next(iter(self.selected))[0]
        changed = copy.deepcopy(self.replay)
        changed["indexed"][cid]["spec"]["phase_turn_rate"] = "1/8"
        with self.assertRaises(model.Refusal):model.report_from_replay(changed)
        changed = copy.deepcopy(self.replay)
        changed["parent_report"]["gates"]["production_authorized"] = True
        changed["parent_report_sha256"] = digest(changed["parent_report"])
        with self.assertRaises(model.Refusal):model.report_from_replay(changed)
        changed = copy.deepcopy(self.replay)
        changed["parent_report"]["source_cases"][0]["source_parameter_id"] = "different-clock"
        changed["parent_report_sha256"] = digest(changed["parent_report"])
        with self.assertRaises(model.Refusal):model.report_from_replay(changed)

    def test_formatter_checks_actual_trace_order_half_and_width_premises(self):
        changes = [
            lambda r:r["refinement"]["trace"].pop(),
            lambda r:r["refinement"]["trace"][0].__setitem__("step",True),
            lambda r:r["refinement"]["trace"][0].__setitem__("midpoint","0"),
            lambda r:r["refinement"]["trace"][0].__setitem__("width","1"),
            lambda r:r["refinement"]["trace"][0].__setitem__("kept_half","UNPROVED"),
            lambda r:r["refinement"]["trace"][0]["midpoint_receipt"].__setitem__("sign",True),
            lambda r:r["refinement"]["trace"][0]["midpoint_receipt"].__setitem__("outward_dyadic_interval",["-1","1"]),
            lambda r:r["refinement"].__setitem__("source_continuity_checked",False),
            lambda r:r["coordinate"].__setitem__("kind","RATIONAL"),
        ]
        for i,mutate in enumerate(changes):
            changed=copy.deepcopy(self.replay)
            mutate(changed["refinements"][0])
            with self.subTest(index=i),self.assertRaises(model.Refusal):
                model.report_from_replay(changed)

    def test_submitted_report_forgeries_cannot_promote_or_shorten_the_result(self):
        self.report_rejects(lambda r:r["refinements"].pop())
        self.report_rejects(lambda r:r["refinements"].__setitem__(1,copy.deepcopy(r["refinements"][0])))
        self.report_rejects(lambda r:r.__setitem__("requested_steps",True))
        self.report_rejects(lambda r:r.__setitem__("requested_steps",0))
        self.report_rejects(lambda r:r["refinements"][0]["refinement"]["trace"].pop())
        self.report_rejects(lambda r:r["refinements"][0]["coordinate"].__setitem__("source_case_id","another-source"))
        self.report_rejects(lambda r:r["parent_baseline"]["source_cases"].pop())
        for key,value in (("production_authorized",True),("MC-B","ACCEPTED"),("MC-1","ACCEPTED"),("PB-007-01","CLOSED")):
            self.report_rejects(lambda r,key=key,value=value:r["gates"].__setitem__(key,value))

    def test_actual_parent_and_trig_sources_beat_accepted_caches_and_preloads(self):
        for relative,blob,factory,kind in (
            (model.PARENT_MODEL,model.PARENT_MODEL_BLOB,model.qualified_parent_module,"parent"),
            (model.TRIG_FILE,model.TRIG_BLOB,model.qualified_trig_module,"trig")):
            trusted=(model.ROOT/relative).read_bytes()
            self.assertEqual(git_blob(trusted),blob)
            name=factory().__name__
            payload=b"CACHE_SUBSTITUTION = True\n#"
            altered=payload+b" "*(len(trusted)-len(payload))
            with self.subTest(kind=kind),tempfile.TemporaryDirectory(prefix="selected-dependency-cache-") as directory:
                root=Path(directory);path=root/relative
                path.parent.mkdir(parents=True)
                ordinary=install_accepted_stale_cache(path,trusted,altered)
                self.assertTrue(ordinary.CACHE_SUBSTITUTION)
                fake=types.ModuleType(name);fake.CACHE_SUBSTITUTION=True
                with mock.patch.object(model,"ROOT",root),mock.patch.dict(sys.modules,{name:fake,path.stem:fake}):
                    checked=factory()
                    self.assertFalse(hasattr(checked,"CACHE_SUBSTITUTION"))
                    self.assertIs(sys.modules[name],fake)
                    self.assertIs(sys.modules[path.stem],fake)
                    if kind=="parent":self.assertTrue(callable(checked.replay_sources))
                    else:self.assertEqual(checked.trig(Q(0)),((Q(1),Q(1)),(Q(0),Q(0))))

    def test_parent_and_trig_compile_the_same_verified_buffer_after_replacement(self):
        for relative,factory in ((model.PARENT_MODEL,model.qualified_parent_module),
                                 (model.TRIG_FILE,model.qualified_trig_module)):
            trusted=(model.ROOT/relative).read_bytes()
            with self.subTest(path=relative),tempfile.TemporaryDirectory(prefix="selected-dependency-buffer-") as directory:
                root=Path(directory);path=root/relative
                path.parent.mkdir(parents=True);path.write_bytes(trusted)
                calls=[]
                def replace(raw,filename,mode,**options):
                    self.assertEqual(raw,trusted)
                    self.assertEqual(options,{"dont_inherit":True,"optimize":0})
                    calls.append(raw);path.write_bytes(b"CACHE_SUBSTITUTION = True\n")
                    return builtins.compile(raw,filename,mode,**options)
                with mock.patch.object(model,"ROOT",root), \
                     mock.patch.dict(model.__dict__,{"compile":mock.Mock(side_effect=replace)}):
                    checked=factory()
                    self.assertFalse(hasattr(checked,"CACHE_SUBSTITUTION"))
                    with self.assertRaises(model.Refusal):factory()
                self.assertEqual(len(calls),1)

    def test_dependency_byte_limits_drift_and_aliases_precede_compile(self):
        compiler=mock.Mock(side_effect=AssertionError("unchecked dependency compiled"))
        with mock.patch.dict(model.__dict__,{"compile":compiler}):
            for factory in (model.qualified_parent_module,model.qualified_trig_module):
                for raw in (b"UNREGISTERED = True\n",b"x"*(model.MAX_CODE_BYTES+1),"not-bytes"):
                    with self.assertRaises(model.Refusal):factory(raw=raw)
            compiler.assert_not_called()
        with tempfile.TemporaryDirectory(prefix="selected-refiner-path-alias-") as directory:
            root=Path(directory);path=root/model.TRIG_FILE
            path.parent.mkdir(parents=True)
            target=path.with_name("unlisted.py")
            target.write_bytes((model.ROOT/model.TRIG_FILE).read_bytes())
            path.symlink_to(target)
            with mock.patch.object(model,"ROOT",root),mock.patch.dict(model.__dict__,{"compile":compiler}):
                with self.assertRaises(model.Refusal):model.qualified_trig_module()
                with self.assertRaises(model.Refusal):model._checked_buffer("unlisted.json","0"*40)
            compiler.assert_not_called()

    def test_original_corpus_and_parent_json_use_the_same_verified_buffers(self):
        original_read=model._read_bounded
        for relative,blob in ((model.CORPUS_FILE,model.CORPUS_BLOB),
                              (model.PARENT_REPORT,model.PARENT_REPORT_BLOB)):
            trusted=(model.ROOT/relative).read_bytes()
            expected=json.loads(trusted)
            with self.subTest(path=relative),tempfile.TemporaryDirectory(prefix="selected-refiner-json-buffer-") as directory:
                root=Path(directory);path=root/relative
                path.parent.mkdir(parents=True);path.write_bytes(trusted)
                def replace_after_read(requested,limit):
                    raw=original_read(requested,limit)
                    requested.write_bytes(b'{"status":"forged-PASS"}')
                    return raw
                with mock.patch.object(model,"ROOT",root), \
                     mock.patch.object(model,"_read_bounded",side_effect=replace_after_read):
                    raw=model._checked_buffer(relative,blob)
                    self.assertEqual(model.parse_json_bytes(raw),expected)
                    with self.assertRaises(model.Refusal):model._checked_buffer(relative,blob)

    def test_input_pin_drift_aborts_before_actual_parent_execution(self):
        original_read=model._read_bounded
        for relative in (model.PARENT_REPORT,model.CORPUS_FILE,model.TRIG_FILE):
            def drift(path,limit):
                if path==model.ROOT/relative:return b'{"status":"PASS"}'
                return original_read(path,limit)
            with self.subTest(path=relative),mock.patch.object(model,"_read_bounded",side_effect=drift), \
                 mock.patch.object(model,"qualified_parent_module",side_effect=AssertionError("drifted input reached proof")) as parent:
                result=model.refine_selected(12)
                self.assertEqual(result["status"],"REFUSED")
                self.assertIs(result["proof_established"],False)
                self.assertIs(result["all_selected_events_refined"],False)
                self.assertNotIn("refinements",result)
                parent.assert_not_called()

    def test_internal_custody_receipts_require_exact_captured_buffer_identities(self):
        custody=self.replay["input_custody"]
        self.assertEqual(len(custody),4)
        self.assertEqual(self.report["executed_byte_custody"]["direct_input_buffers"],custody)
        for item in custody:
            raw=(ROOT/item["path"]).read_bytes()
            self.assertEqual(item["git_blob"],git_blob(raw))
            self.assertEqual(item["bytes"],len(raw))
            self.assertEqual(item["sha256"],hashlib.sha256(raw).hexdigest())
        for index in range(4):
            for field,value in (("bytes",custody[index]["bytes"]+1),("sha256","0"*64)):
                changed=copy.deepcopy(self.replay)
                changed["input_custody"][index][field]=value
                with self.subTest(index=index,field=field),self.assertRaises(model.Refusal):
                    model.report_from_replay(changed)

    def test_derived_arithmetic_growth_refuses_before_large_fraction_product(self):
        operand=Q(1,1 << 40000)
        with mock.patch.object(Q,"__mul__",side_effect=AssertionError("overbudget product was computed")) as multiply:
            with self.assertRaises(model.Refusal) as error:model._safe(operand,operand,"mul")
            self.assertEqual(error.exception.code,"RESOURCE_REFUSAL")
            multiply.assert_not_called()
        with self.assertRaises(model.Refusal) as error:
            model._outward_receipt((Q(1 << 300),Q(1 << 300)))
        self.assertEqual(error.exception.code,"RESOURCE_REFUSAL")


    def test_invalid_step_requests_refuse_before_parent_execution(self):
        class IndexAlias:
            def __index__(self):
                raise AssertionError("request must not coerce arbitrary objects")
        invalid=(True,False,-1,13,"12",12.0,None,IndexAlias(),1 << 20000)
        with mock.patch.object(model,"qualified_parent_module",
                               side_effect=AssertionError("invalid request reached parent execution")) as parent:
            for i,steps in enumerate(invalid):
                with self.subTest(index=i):
                    result=model.refine_selected(steps)
                    self.assertEqual(result["status"],"REFUSED")
                    self.assertIs(result["proof_established"],False)
                    self.assertIs(result["all_selected_events_refined"],False)
                    self.assertNotIn("refinements",result)
            parent.assert_not_called()
        with mock.patch.object(model,"expected_report",
                               side_effect=AssertionError("invalid request reached expected report")) as expected:
            with self.assertRaises(model.Refusal):model.validate_report({},True)
            expected.assert_not_called()

    def test_rational_token_and_operand_bounds_precede_fraction_construction(self):
        bad=(True,1,0.25,None,"","1e1000000000","0.25","+1","01","--1",
             "1/-2","1/0"," 1","\uff11","9"*129,str(1 << 128),"1/"+str(1 << 128))
        with mock.patch.object(model,"Fraction",side_effect=AssertionError("unsafe rational constructor")) as fraction:
            for i,value in enumerate(bad):
                with self.subTest(index=i),self.assertRaises(model.Refusal):model.rational(value)
            fraction.assert_not_called()
        for value in ("0","1","-3","1/2","-2/3",str((1 << 127)-1)):
            self.assertEqual(model.rational(value),Q(value))
        for value in ("-0","2/4","1/1","0/2"):
            with self.subTest(value=value),self.assertRaises(model.Refusal):model.rational(value)

    def test_whole_source_preflight_precedes_any_fraction_or_trig_work(self):
        source=synthetic_spec(controls=("1","1"))
        source["sin_splines"]["7"]={"degree":1,"knots":["0","0","1","1"],
                                     "controls":["1","1e1000000000"]}
        with mock.patch.object(model,"Fraction",side_effect=AssertionError("partial source parsed before complete preflight")) as fraction, \
             mock.patch.object(model,"qualified_trig_module",side_effect=AssertionError("invalid source reached trig loading")) as trig:
            with self.assertRaises(model.Refusal):model.prepare_source_spec(source)
            fraction.assert_not_called();trig.assert_not_called()

    def test_point_coordinate_bounds_and_exact_types_precede_trig(self):
        source=model.prepare_source_spec(synthetic_spec(controls=("1","1")))
        invalid=(True,0,0.5,None,"1e1000000000",Q(1,1 << 129),Q(-1),Q(2))
        with mock.patch.object(source.trig_provider,"trig",side_effect=AssertionError("invalid point reached trig")) as trig:
            for i,point in enumerate(invalid):
                with self.subTest(index=i),self.assertRaises(model.Refusal):model.point_receipt(source,point)
            trig.assert_not_called()

    def test_public_report_preflight_blocks_cycles_aliases_numbers_and_resources(self):
        cycle=[];cycle.append(cycle)
        shared={"x":1}
        deep=0
        for _ in range(40):deep=[deep]
        class MappingAlias(dict):pass
        invalid=(cycle,[shared,shared],deep,{"x":0.5},{"x":float("nan")},
                 {"x":b"not-json"},{"x":(1,2)},MappingAlias(x=1),
                 {"x":"x"*(2*1024*1024+1)},{"x":1 << 20000})
        with mock.patch.object(model,"expected_report",side_effect=AssertionError("malformed report reached proof")) as expected:
            for i,candidate in enumerate(invalid):
                with self.subTest(index=i),self.assertRaises(model.Refusal):
                    model.validate_report(candidate,12)
            expected.assert_not_called()
        self.assertNotEqual(model.bounded_bytes({"sign":True}),model.bounded_bytes({"sign":1}))

    def test_report_reader_rejects_duplicate_keys_nonexact_numbers_and_oversize(self):
        with tempfile.TemporaryDirectory(prefix="selected-refiner-json-") as directory:
            path=Path(directory)/"candidate.json"
            for raw in (b'{"x":1,"x":2}',b'{"x":NaN}',b'{"x":Infinity}',b'{"x":0.5}',
                        b'{"x":1e99999999}',b'['*40+b'0'+b']'*40,b'not-json'):
                path.write_bytes(raw)
                with self.subTest(raw=raw[:30]),self.assertRaises(model.Refusal):model.read_report(path)
            with path.open("wb") as stream:stream.truncate(2*1024*1024+1)
            with self.assertRaises(model.Refusal):model.read_report(path)
            path.write_bytes(b'{"status":"bounded candidate"}')
            self.assertEqual(model.read_report(path),{"status":"bounded candidate"})

    def test_report_path_text_is_bounded_before_open(self):
        bad=("x"*10000,Path("x"*10000),"", "a\0b",True,1,None,[])
        with mock.patch.object(Path,"open",side_effect=AssertionError("invalid path reached open")) as reader:
            for i,path in enumerate(bad):
                with self.subTest(index=i),self.assertRaises(model.Refusal):model.read_report(path)
            reader.assert_not_called()
        with tempfile.TemporaryDirectory(prefix="selected-refiner-missing-") as directory:
            with self.assertRaises(model.Refusal):model.read_report(Path(directory)/"missing.json")

    def test_fresh_exact_manifest_and_both_workflow_trigger_closures(self):
        parent=model.qualified_parent_module()
        expected=dict(parent.DEPENDENCY_PINS)
        expected.update({model.PARENT_MODEL:model.PARENT_MODEL_BLOB,
                         model.PARENT_REPORT:model.PARENT_REPORT_BLOB})
        self.assertEqual(model.PINS,expected)
        self.assertEqual(len(expected),101)
        self.assertEqual(expected[LOWERER_PATH],LOWERER_BLOB)
        self.assertEqual(expected[TRIG_PATH],TRIG_BLOB)
        self.assertEqual(expected[RUNTIME_PATH],RUNTIME_BLOB)
        own={TASK+name for name in (
            "pb00701_selected_implicit_root_refinement.py",
            "verify_pb00701_selected_implicit_root_refinement.py",
            "pb00701-selected-implicit-root-refinement.json",
            "pb00701-selected-implicit-root-refinement-research.md")}
        workflow=".github/workflows/mc1-pb00701-selected-implicit-root-refinement.yml"
        own.add(workflow)
        text=(ROOT/workflow).read_text()
        before,after=text.split("  push:",1)
        for section in (before,after):
            paths=re.findall(r"^      - ['\"]([^'\"]+)['\"]$",section,re.M)
            self.assertEqual(set(paths),set(expected)|own)
            self.assertEqual(len(paths),106)
        self.assertNotIn("strategy:",text)
        self.assertIn("github.event.pull_request.head.sha || github.sha",text)
        self.assertIn("verify_pb00701_selected_implicit_root_refinement.py --contract --self-test",text)
        self.assertIn("python-version: '3.12'",text)


def test_suite(replay=None):
    SelectedRefinementTests.replay=replay
    classes=(ConditionalMathematicsTests,SelectedRefinementTests,
             build_bootstrap_tests(MODEL_PATH,MODEL_BLOB))
    loader=unittest.defaultTestLoader
    return unittest.TestSuite(loader.loadTestsFromTestCase(case) for case in classes)


model=load_reviewed_model(MODEL_PATH,MODEL_BLOB)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract",action="store_true")
    parser.add_argument("--self-test",action="store_true")
    options=parser.parse_args()
    if not (options.contract or options.self_test):
        parser.error("choose --contract and/or --self-test")
    # One fresh all-selected mathematical run, shared by normal contract and
    # test fixtures. Negative controls never use a saved PASS as fallback.
    replay=model.replay_refinements(12)
    report=model.report_from_replay(replay)
    expected_bytes=model.bounded_bytes(report)
    if options.contract:
        model._compare_with_replayed_bytes(model.read_report(),expected_bytes)
    if options.self_test:
        result=unittest.TextTestRunner(verbosity=2).run(test_suite(replay))
        if not result.wasSuccessful():
            raise SystemExit(1)
    print("PASS: 69 implicit original-source zeros refined through 12 exact bisections")
    print("PASS: original point signs, inherited uniqueness, source knots and physical events are preserved")
    print("PASS: failed or zero-inclusive decisions remain nontruth; parent baseline and all gates are unchanged")


if __name__=="__main__":
    main()
