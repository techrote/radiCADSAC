#!/usr/bin/env python3
"""Replay five original multiplier sources and challenge their actual premises."""
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
import sys
import tempfile
import types
import unittest
from unittest import mock

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "pb00701_multiplier_tail_source_completion.py"
MODEL_BLOB = "c5a3118b7eb486e5289d5a75c85d099d3e9d802b"


def load_reviewed_model(path=MODEL_PATH, expected=MODEL_BLOB):
    with Path(path).open("rb") as stream:
        raw = stream.read(1048577)
    if len(raw) > 1048576:
        raise ValueError("MODEL_BYTE_LIMIT")
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    if actual != expected:
        raise ValueError("MODEL_SOURCE_DRIFT")
    module = types.ModuleType("multiplier_reviewed_model")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


model = load_reviewed_model()


def install_stale_cache(path, trusted, altered):
    if len(trusted) != len(altered) or trusted == altered:
        raise AssertionError("the cache counterexample must have matching source length")
    other = path.with_name("alternate.py")
    path.write_bytes(trusted)
    other.write_bytes(altered)
    for candidate in (path, other):
        os.utime(candidate, (1700000000, 1700000000))
    cache = Path(importlib.util.cache_from_source(str(path)))
    cache.parent.mkdir(exist_ok=True)
    py_compile.compile(str(other), cfile=str(cache), doraise=True,
                       invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
    spec = importlib.util.spec_from_file_location("observed_cache_counterexample", path)
    ordinary = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ordinary)
    return ordinary


class MultiplierSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = model.original_rows()
        cls.carrier = model.load_carrier()
        cls.report = model.expected_report()
        cls.by_family = {p["family"]: p for p in cls.report["source_cases"]}

    def row(self, family):
        return next(r for cid, r in self.rows.items() if model.CASES[cid]["family"] == family)

    def source(self, family):
        return copy.deepcopy(self.row(family)["spec"])

    def report_rejects(self, change):
        altered = copy.deepcopy(self.report)
        change(altered)
        with self.assertRaises(model.Refusal):
            model.validate_report(altered)

    def test_five_complete_original_results_and_source_bound_events(self):
        self.assertTrue(model.validate_report(model.read_report()))
        self.assertEqual(list(self.report["summary"]["by_case_closed_root_count"].values()), [3, 3, 3, 2, 3])
        self.assertEqual(self.report["summary"]["finite_simple_roots"], 14)
        self.assertEqual({p["case_id"] for p in self.report["source_cases"]}, set(model.CASES))
        for family, proof in self.by_family.items():
            physical = proof["physical_event_proof"]
            self.assertEqual(physical["source_interval"], ["0", "2"])
            self.assertTrue(physical["complete_for_original_closed_source"])
            self.assertFalse(physical["original_source_knot"]["is_physical_event"])
            self.assertTrue(all(not e["is_physical_zero"] for e in physical["exterior_endpoints"]))
            signs = [1, -1, 1] if family == "V17" else [-1, 1, -1, 1]
            self.assertEqual([c["sign"] for c in physical["maximal_open_sign_cells"]], signs)
            self.assertEqual([e["coordinate"]["strict_bracket"] for e in physical["events"][:2]],
                             [["1/6", "1/4"], ["3/4", "5/6"]])
            for event in physical["events"]:
                self.assertEqual(event["coordinate"]["source_sha256"], proof["original_source_sha256"])
                self.assertEqual(event["smooth_physical_multiplicity"], 1)
                self.assertEqual(event["derivative_sign_at_root"], event["right_sign"])

    def test_exact_bounds_and_original_endpoint_values(self):
        expected = {
            "V13": ("1", "-1", "-1/3", "98", "8/3", "11/3", "1979/21", "22/3"),
            "V14": ("1/2", "-5/6", "-7/6", "295/3", "17/6", "17/3", "1913/21", "43/6"),
            "V15": ("9/4", "-7/4", "-3/4", "193/2", "21/4", "21/2", "167/2", "19/4"),
            "V17": ("1", "2/3", "2/3", "304/3", "3", "4", "656/7", "7"),
            "V18_LAURENT": ("7/8", "-4/3", "-2/3", "292/3", "10/3", "20/3", "1880/21", "20/3"),
        }
        for family, values in expected.items():
            proof = self.by_family[family]
            prefix, tail = proof["prefix_proof"], proof["tail_proof"]
            actual = (prefix["factor_reconstruction"]["multiplier"]["strict_nonzero_margin"],
                      *prefix["endpoint_values"], tail["endpoint_values"][1],
                      tail["amplitude_absolute_sum"], tail["harmonic_weighted_absolute_sum"],
                      tail["strict_derivative_lower_bound"],
                      tail["bound_at_rational_proof_cut"]["lower_bound"])
            self.assertEqual(actual, values)

    def test_original_factor_coefficients_by_independent_product_to_sum(self):
        a, b = (Q(-1, 3), Q(1)), (Q(2, 3), Q(-1))
        series = {"V13": {0: Q(2), 2: Q(1)},
                  "V14": {0: Q(2), 2: Q(-1, 2), 4: Q(1)},
                  "V15": {0: Q(4), 2: Q(1, 2), 4: Q(-1, 4), 6: Q(1)},
                  "V18_LAURENT": {0: Q(2), 2: Q(1), 4: Q(1)}}
        for family in self.by_family:
            expected = {"cos_splines": {}, "sin_splines": {}}

            def put(channel, harmonic, coefficients, scalar):
                target = expected[channel].setdefault(harmonic, [Q(0), Q(0)])
                for i in (0, 1):
                    target[i] += scalar * coefficients[i]

            if family == "V17":
                # sin(2θ)cosθ=(sin3θ+sinθ)/2;
                # sin(2θ)sinθ=(cosθ-cos3θ)/2.
                put("cos_splines", 1, a, -2)
                put("sin_splines", 1, b, -2)
                put("sin_splines", 1, a, Q(1, 2))
                put("sin_splines", 3, a, Q(1, 2))
                put("cos_splines", 1, b, Q(1, 2))
                put("cos_splines", 3, b, Q(-1, 2))
            else:
                for h, coefficient in series[family].items():
                    if h == 0:
                        put("cos_splines", 1, a, coefficient)
                        put("sin_splines", 1, b, coefficient)
                    else:
                        for n in (h - 1, h + 1):
                            put("cos_splines", n, a, coefficient / 2)
                        put("sin_splines", h + 1, b, coefficient / 2)
                        put("sin_splines", h - 1, b, -coefficient / 2)
            spec = self.source(family)
            for channel, channels in expected.items():
                for h, coefficients in channels.items():
                    spline = spec[channel][str(h)]
                    controls = list(map(Q, spline["controls"]))
                    actual = [controls[0], controls[1] - controls[0]] if spline["degree"] else [controls[0], Q(0)]
                    self.assertEqual(actual, coefficients, (family, channel, h))
                    # The frozen second span is held at the first endpoint.
                    tail = controls[spline["degree"] + 1:]
                    self.assertTrue(all(value == sum(coefficients) for value in tail))
            self.assertEqual(spec["cos_splines"]["0"]["controls"], ["0", "0", "0", "100"])

    def test_v14_wrong_sign_has_a_valid_bound_but_fails_original_identity(self):
        correct = model.multiplier_for("V14")
        wrong = model.even_multiplier({"0": "2", "2": "1/2", "4": "1"})
        self.assertEqual(correct["strict_nonzero_margin"], wrong["strict_nonzero_margin"])
        with self.assertRaisesRegex(model.Refusal, "HARMONIC_FACTOR_IDENTITY"):
            model.factor_identity(self.source("V14"), wrong)
        self.assertEqual(self.by_family["V14"]["prefix_proof"]["endpoint_values"][1], "-7/6")

    def test_each_original_harmonic_participates_in_the_identity(self):
        for family in self.by_family:
            original = self.source(family)
            for channel in ("cos_splines", "sin_splines"):
                for h in original[channel]:
                    spec = copy.deepcopy(original)
                    spline = spec[channel][h]
                    if h == "0" or spline["degree"] == 0:
                        spline["controls"] = [str(Q(v) + Q(1, 100)) for v in spline["controls"]]
                    else:
                        spline["controls"][0] = str(Q(spline["controls"][0]) + Q(1, 100))
                    with self.subTest(family=family, channel=channel, harmonic=h):
                        with self.assertRaises(model.Refusal):
                            model.factor_identity(spec, model.multiplier_for(family))

    def test_v18_square_proves_a_margin_where_l1_is_inconclusive(self):
        raw = {"0": "2", "2": "1", "4": "1"}
        with self.assertRaisesRegex(model.Refusal, "MAY_VANISH"):
            model.even_multiplier(raw)
        proved = model.even_multiplier(raw, square=True)
        self.assertEqual(proved["strict_nonzero_margin"], "7/8")
        self.assertEqual(proved["nonvanishing_proof"]["shift"], "1/4")
        self.assertEqual(proved["nonvanishing_proof"]["quadratic"], "2")

    def test_vanishing_or_sign_uncertain_factors_cannot_transfer_two_roots(self):
        # 1+cos(4θ) is exactly zero at t=1/2; R is positive there.
        for raw in ({"0": "1", "4": "1"}, {"0": "0", "2": "1"}, {"0": "0"}):
            with self.subTest(series=raw), self.assertRaisesRegex(model.Refusal, "MAY_VANISH"):
                model.even_multiplier(raw)
        # -1+sin(2θ) also vanishes at t=1/2.
        with self.assertRaisesRegex(model.Refusal, "MAY_VANISH"):
            model.negative_sine_multiplier("-1", "1")
        with self.assertRaisesRegex(model.Refusal, "MAY_VANISH"):
            model.even_multiplier({"0": "1", "2": "1", "4": "1"}, square=True)
        with self.assertRaisesRegex(model.Refusal, "NOT_POSITIVE"):
            model.even_multiplier({"0": "3", "2": "1", "4": "-1"}, square=True)

    def test_forged_factor_bound_or_sign_is_recomputed(self):
        for key, value in (("strict_nonzero_margin", "1000"), ("sign", 1)):
            factor = model.multiplier_for("V17")
            factor[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(model.Refusal, "FORGED_MULTIPLIER"):
                model.factor_identity(self.source("V17"), factor)
        factor = model.multiplier_for("V18_LAURENT")
        factor["nonvanishing_proof"]["positive_remainder"] = "1"
        with self.assertRaisesRegex(model.Refusal, "FORGED_MULTIPLIER"):
            model.factor_identity(self.source("V18_LAURENT"), factor)

    def test_conditional_factor_checker_accepts_a_valid_nonfrozen_identity(self):
        spec = self.source("V13")
        for channel in ("cos_splines", "sin_splines"):
            for h, spline in spec[channel].items():
                if h != "0":
                    spline["controls"] = [str(2 * Q(v)) for v in spline["controls"]]
        factor = model.even_multiplier({"0": "4", "2": "2"})
        self.assertTrue(model.factor_identity(spec, factor)["all_original_harmonics_reconstructed"])
        self.assertEqual(model.prove_tail(spec)["closed_distinct_root_count"], 1)
        changed = copy.deepcopy(self.row("V13"))
        changed["spec"] = spec
        with self.assertRaisesRegex(model.Refusal, "ORIGINAL_SOURCE"):
            model.source_proof(changed)

    def test_v17_negative_factor_reverses_carrier_signs_without_tail_crossing(self):
        proof = self.by_family["V17"]
        self.assertEqual(proof["prefix_proof"]["maximal_sign_cells"], [1, -1, 1])
        self.assertEqual(proof["prefix_proof"]["simple_root_derivative_signs"], [-1, 1])
        self.assertEqual(proof["tail_proof"]["closed_distinct_root_count"], 0)
        self.assertEqual(proof["tail_proof"]["maximal_sign_cells"], [1])
        self.assertGreater(Q(proof["tail_proof"]["strict_derivative_lower_bound"]), 0)

    def test_lost_or_nonstrict_tail_derivative_refuses(self):
        spec = self.source("V13")
        weighted = Q(self.by_family["V13"]["tail_proof"]["harmonic_weighted_absolute_sum"])
        for slope in (Q(0), Q(11, 7) * weighted):
            changed = copy.deepcopy(spec)
            changed["cos_splines"]["0"]["controls"][3] = str(slope)
            with self.subTest(slope=slope), self.assertRaisesRegex(model.Refusal, "STRICT_DERIVATIVE"):
                model.prove_tail(changed)
        # With no ramp, the exact derivative at t=1 has pi/2 coefficient -2/3.
        self.assertEqual(-Q(5, 3) + 3 * Q(1, 3), Q(-2, 3))

    def test_tail_bound_must_prove_a_strict_positive_bracket(self):
        spec = self.source("V13")
        with self.assertRaisesRegex(model.Refusal, "BRACKET_SIGN"):
            model.prove_tail(spec, "1001/1000")
        for cut in ("1", "2", "3"):
            with self.subTest(cut=cut), self.assertRaisesRegex(model.Refusal, "OUTSIDE"):
                model.prove_tail(spec, cut)

    def test_tail_amplitudes_must_actually_be_constant(self):
        for channel in ("cos_splines", "sin_splines"):
            spec = self.source("V13")
            controls = spec[channel]["1"]["controls"]
            controls[3] = str(Q(controls[3]) + 1)
            with self.subTest(channel=channel), self.assertRaisesRegex(model.Refusal, "NONCONSTANT"):
                model.prove_tail(spec)

    def test_exact_zero_knot_is_not_omitted_or_called_an_interior_root(self):
        spec = self.source("V13")
        controls = spec["sin_splines"]["1"]["controls"]
        controls[1:] = ["-1/6"] * 3
        pieces, _ = model.parse_source(spec)
        self.assertEqual(model.cardinal_value(pieces, 1, Q(1)), 0)
        with self.assertRaisesRegex(model.Refusal, "EXACT_KNOT_ZERO"):
            model.prove_tail(spec)

    def test_phase_parameter_and_original_piece_geometry_are_required(self):
        mutations = [
            lambda s: s.update(phase_turn_rate="-1/4"),
            lambda s: s.update(phase_turn_offset="1/24"),
            lambda s: s.update(parameter_hi="3"),
            lambda s: s["cos_splines"]["1"]["knots"].__setitem__(2, "3/4"),
            lambda s: s["cos_splines"]["1"].update(degree=True),
            lambda s: s["sin_splines"]["1"]["controls"].__setitem__(2, "1"),
            lambda s: s["cos_splines"].update({"2": copy.deepcopy(s["cos_splines"]["1"])}),
        ]
        for change in mutations:
            spec = self.source("V13")
            change(spec)
            with self.subTest(change=change), self.assertRaises(model.Refusal):
                model.prove_tail(spec)

    def test_omitted_or_renamed_original_harmonics_refuse(self):
        for action in ("omit", "harmonic4"):
            spec = self.source("V13")
            value = spec["sin_splines"].pop("3")
            if action == "harmonic4":
                spec["sin_splines"]["4"] = value
            with self.subTest(action=action), self.assertRaises(model.Refusal):
                model.factor_identity(spec, model.multiplier_for("V13"))

    def test_source_and_whole_row_hashes_precede_mathematical_parsing(self):
        mutations = [
            lambda r: r["spec"].update(phase_turn_rate="1e1000000000"),
            lambda r: r["spec"].update(source_parameter_id="unrelated-clock"),
            lambda r: r.update(origin="another-generator"),
            lambda r: r.update(id=self.row("V14")["id"]),
            lambda r: r["expected"].update(v54_disposition="CERTIFIED"),
            lambda r: r["spec"]["cos_splines"]["1"]["controls"].__setitem__(0, "0"),
        ]
        for change in mutations:
            row = copy.deepcopy(self.row("V13"))
            change(row)
            with self.subTest(change=change), mock.patch.object(model, "parse_source") as parser, \
                    mock.patch.object(model, "load_carrier") as carrier:
                with self.assertRaises(model.Refusal):
                    model.source_proof(row)
                parser.assert_not_called()
                carrier.assert_not_called()

    def test_carrier_receipt_alone_does_not_bind_an_original_source(self):
        self.assertFalse(self.carrier["original_source_binding_supplied_by_this_lemma"])
        spec = self.source("V13")
        spec["cos_splines"]["1"]["controls"][0] = "0"
        with self.assertRaisesRegex(model.Refusal, "FACTOR_IDENTITY"):
            model._prefix_proof(spec, "V13", self.carrier)
        for change in (lambda r: r["root_brackets"][0].__setitem__(0, "0"),
                       lambda r: r["phase_turn_law"].update(rate="-1/4"),
                       lambda r: r.update(original_source_binding_supplied_by_this_lemma=True)):
            receipt = copy.deepcopy(self.carrier)
            change(receipt)
            with self.subTest(change=change), self.assertRaisesRegex(model.Refusal, "CARRIER_CONTRACT"):
                model._prefix_proof(self.source("V13"), "V13", receipt)

    def test_composition_rejects_cross_source_partial_order_and_aliases(self):
        spec = self.source("V13")
        _, continuity = model.parse_source(spec)
        valid_prefix = copy.deepcopy(self.by_family["V13"]["prefix_proof"])
        valid_tail = copy.deepcopy(self.by_family["V13"]["tail_proof"])
        mutations = [
            lambda p, t: t.update(source_sha256=self.by_family["V14"]["original_source_sha256"]),
            lambda p, t: t.update(source_interval=["1", "3"]),
            lambda p, t: p["root_brackets"].reverse(),
            lambda p, t: p["root_brackets"].append(["1/3", "2/3"]),
            lambda p, t: t.update(complete_for_original_second_closed_span=False),
            lambda p, t: t["endpoint_values"].__setitem__(0, "0"),
            lambda p, t: p["maximal_sign_cells"].__setitem__(1, True),
            lambda p, t: t["simple_root_derivative_signs"].__setitem__(0, -1),
        ]
        for change in mutations:
            prefix, tail = copy.deepcopy(valid_prefix), copy.deepcopy(valid_tail)
            change(prefix, tail)
            with self.subTest(change=change), self.assertRaises(model.Refusal):
                model._compose(spec, prefix, tail, continuity)

    def test_report_source_count_scope_and_event_forgeries_refuse(self):
        changes = [
            lambda r: r["source_cases"].pop(),
            lambda r: r["source_cases"].append(copy.deepcopy(r["source_cases"][0])),
            lambda r: r["source_cases"][0].update(original_row_sha256="0" * 64),
            lambda r: r["source_cases"][0]["physical_event_proof"]["events"][0].update(smooth_physical_multiplicity=2),
            lambda r: r["source_cases"][0]["physical_event_proof"]["events"][0]["coordinate"].update(kind="EXACT_RATIONAL"),
            lambda r: r["source_cases"][0]["physical_event_proof"]["original_source_knot"].update(is_physical_event=True),
            lambda r: r["source_cases"][0]["tail_proof"]["bound_at_rational_proof_cut"].update(is_physical_event=True),
            lambda r: r["source_cases"][0]["tail_proof"].update(strict_derivative_lower_bound="100"),
            lambda r: r["summary"].update(complete_original_sources=6),
            lambda r: r["gates"].update(production_authorized=True),
            lambda r: r["gates"].update(**{"MC-B": "ACCEPTED", "required_machining_operations": 25}),
        ]
        for change in changes:
            with self.subTest(change=change):
                self.report_rejects(change)

    def test_boolean_integer_aliases_do_not_survive_canonical_report_comparison(self):
        for change in (
                lambda r: r["source_cases"][0]["physical_event_proof"].update(complete_for_original_closed_source=1),
                lambda r: r["source_cases"][0]["physical_event_proof"]["events"][0].update(smooth_physical_multiplicity=True),
                lambda r: r["gates"].update(production_authorized=0),
                lambda r: r["summary"].update(finite_simple_roots=14.0)):
            self.report_rejects(change)

    def test_refused_carrier_or_tail_aborts_without_saved_success(self):
        with mock.patch.object(model, "load_carrier", side_effect=model.Refusal("carrier unavailable")):
            with self.assertRaisesRegex(model.Refusal, "carrier unavailable"):
                model.validate_report(self.report)
        with mock.patch.object(model, "prove_tail", side_effect=model.Refusal("derivative unavailable")):
            with self.assertRaisesRegex(model.Refusal, "derivative unavailable"):
                model.validate_report(self.report)

    def test_rational_lexical_and_bit_guards_precede_fraction_construction(self):
        invalid = ("1e1000000000", "1E-1000000000", "0.5", "+1", "-0", "01", "1/0",
                   "2/4", "1/1", "1/02", "\u0661/2", "9" * 79, "1/" + "9" * 79,
                   str(1 << 256), True, 0.5)
        for value in invalid:
            with self.subTest(value=value), mock.patch.object(model, "Q") as constructor:
                with self.assertRaises(model.Refusal):
                    model.exact(value)
                constructor.assert_not_called()
        self.assertEqual(model.exact("-1/2"), Q(-1, 2))

    def test_internal_exact_arithmetic_is_bounded_before_construction(self):
        for values in ([True], [0.5], [1 << 4097], [Q(1, 1 << 4097)], [Q(1)] * 17):
            with self.subTest(values=str(values)[:20]), self.assertRaises(model.Refusal):
                model.qvector(values)
        with self.assertRaisesRegex(model.Refusal, "product degree"):
            model.multiply([1] * 9, [1] * 9)

    def test_public_preflight_refuses_resource_and_type_inputs_before_replay(self):
        cycle = []
        cycle.append(cycle)
        deep = []
        for _ in range(model.MAX_DEPTH + 2):
            deep = [deep]
        invalid = [cycle, deep, "x" * (model.MAX_STRING + 1), 1 << 257, float("nan"), Q(1),
                   object(), {True: "key"}, ["x" * 8192 for _ in range(129)]]
        for candidate in invalid:
            with self.subTest(type=type(candidate)), mock.patch.object(model, "expected_report") as replay:
                with self.assertRaises(model.Refusal):
                    model.validate_report(candidate)
                replay.assert_not_called()

    def test_duplicate_json_numeric_and_file_resource_inputs_refuse(self):
        invalid = [b'{"x":1,"x":2}', b'{"x":1.0}', b'{"x":NaN}', b'{"x":Infinity}',
                   ('{"x":' + '9' * 1000 + '}').encode(), b'\xff', b'[' * 2000 + b']' * 2000]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.json"
            for raw in invalid:
                path.write_bytes(raw)
                with self.subTest(raw=raw[:30]), self.assertRaises(model.Refusal):
                    model.read_report(path)
            with path.open("wb") as stream:
                stream.truncate(model.MAX_BYTES + 1)
            with self.assertRaisesRegex(model.Refusal, "file bytes"):
                model.read_report(path)

    def test_pinned_json_decodes_the_verified_buffer_after_replacement(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data.json"
            path.write_bytes(b'{"value":1}\n')
            expected = model.git_blob(path)
            decode = model.decode_json

            def replace(raw):
                path.write_bytes(b'{"value":2}\n')
                return decode(raw)

            with mock.patch.object(model, "decode_json", side_effect=replace):
                self.assertEqual(model.pinned_json(path, expected), {"value": 1})
            with self.assertRaisesRegex(model.Refusal, "PINNED_SOURCE_DRIFT"):
                model.pinned_json(path, expected)

    def test_actual_carrier_source_ignores_stale_cache_and_preloaded_module(self):
        trusted = model.pinned_bytes(HERE / model.CARRIER_FILE, model.CARRIER_BLOB)
        altered = trusted.replace(b"def carrier_prefix_proof(", b"def carrier_prefix_sp00f(", 1)
        with tempfile.TemporaryDirectory() as tmp:
            provider_here = Path(tmp) / "research/machining-completeness/tasks/MC-038"
            provider_here.mkdir(parents=True)
            path = provider_here / model.CARRIER_FILE
            original_path, original_import = list(sys.path), builtins.__import__
            try:
                ordinary = install_stale_cache(path, trusted, altered)
            finally:
                sys.path[:] = original_path
            self.assertFalse(hasattr(ordinary, "carrier_prefix_proof"))
            decoy = types.ModuleType("preloaded_carrier")
            decoy.carrier_prefix_proof = mock.Mock(side_effect=AssertionError("preload used"))
            names = (Path(model.CARRIER_FILE).stem, "multiplier_private_" + Path(model.CARRIER_FILE).stem)
            # The temporary directory contains no tail producers or reports.
            with mock.patch.dict(sys.modules, {name: decoy for name in names}), \
                    mock.patch.object(model, "HERE", provider_here):
                self.assertEqual(model.canonical(model.load_carrier()), model.canonical(self.carrier))
                decoy.carrier_prefix_proof.assert_not_called()
            self.assertEqual(sys.path, original_path)
            self.assertIs(builtins.__import__, original_import)

    def test_pinned_module_executes_verified_buffer_and_blocks_new_dependencies(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "probe.py"
            path.write_bytes(b"VALUE = 1\n")
            expected = model.git_blob(path)

            def replace(raw, filename, mode):
                path.write_bytes(b"VALUE = 9\n")
                return builtins.compile(raw, filename, mode)

            with mock.patch.object(model, "compile", side_effect=replace, create=True):
                self.assertEqual(model.pinned_module(path, expected).VALUE, 1)
            with self.assertRaisesRegex(model.Refusal, "PINNED_SOURCE_DRIFT"):
                model.pinned_module(path, expected)
            path.write_bytes(b"import pb00701_unreviewed_source\n")
            with self.assertRaisesRegex(model.Refusal, "UNREVIEWED_DEPENDENCY_IMPORT"):
                model.pinned_module(path, model.git_blob(path))

    def test_dependency_drift_aborts_before_carrier_execution(self):
        real = model.pinned_bytes

        def refuse(path, expected):
            if Path(path).name == model.CARRIER_FILE:
                raise model.Refusal("controlled provider drift")
            return real(path, expected)

        with mock.patch.object(model, "pinned_bytes", side_effect=refuse), \
                mock.patch.object(model, "_prefix_proof") as prefix:
            with self.assertRaisesRegex(model.Refusal, "provider drift"):
                model.expected_report()
            prefix.assert_not_called()

    def test_verifier_bootstrap_ignores_real_cache_and_preloaded_module(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "probe.py"
            ordinary = install_stale_cache(path, b"VALUE = 1\n", b"VALUE = 2\n")
            self.assertEqual(ordinary.VALUE, 2)
            decoy = types.ModuleType("multiplier_reviewed_model")
            decoy.VALUE = 3
            with mock.patch.dict(sys.modules, {decoy.__name__: decoy}):
                self.assertEqual(load_reviewed_model(path, model.git_blob(path)).VALUE, 1)
                self.assertIs(sys.modules[decoy.__name__], decoy)

    def test_verifier_bootstrap_drift_and_oversize_refuse_before_compilation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "probe.py"
            path.write_bytes(b"VALUE = 1\n")
            with mock.patch.dict(globals(), {"compile": mock.Mock(side_effect=AssertionError("unchecked source compiled"))}):
                with self.assertRaisesRegex(ValueError, "SOURCE_DRIFT"):
                    load_reviewed_model(path, "0" * 40)
                with path.open("wb") as stream:
                    stream.truncate(1048577)
                with self.assertRaisesRegex(ValueError, "BYTE_LIMIT"):
                    load_reviewed_model(path, "0" * 40)
                globals()["compile"].assert_not_called()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    options = parser.parse_args()
    if not (options.contract or options.self_test):
        parser.error("choose --contract and/or --self-test")
    if options.contract:
        model.validate_report(model.read_report())
        print("PASS: five original complete multiplier sources; root counts 3/3/3/2/3")
        print("PASS: qualified unbound carrier, exact original factors, strict ramp tails and nonzero knots")
        print("PASS: frozen 121/20/30, 26 operations and all open programme gates retained")
    if options.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(MultiplierSourceTests))
        if not result.wasSuccessful():
            raise SystemExit(1)


if __name__ == "__main__":
    main()
