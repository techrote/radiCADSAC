#!/usr/bin/env python3
"""Replay the three original exact-zero proofs and adversarial source controls."""
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
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
MODEL_BLOB = "668eef22876afdeec0931a6ccb6a48573b053203"


def _load_verified_model(path, expected):
    with Path(path).open("rb") as stream:
        raw = stream.read(1048577)
    if len(raw) > 1048576:
        raise ValueError("RESOURCE_REFUSAL: model byte budget")
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if actual != expected:
        raise ValueError("VERIFIER_MODEL_SOURCE_DRIFT")
    module = types.ModuleType("exact_zero_verified_model")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


model = _load_verified_model(HERE / "pb00701_exact_zero_child_source_completion.py", MODEL_BLOB)


def _matching_cache(path):
    path.write_bytes(b"VALUE = 'trusted'\n")
    alternate = path.with_name("alternate.py")
    alternate.write_bytes(b"VALUE = 'altered'\n")
    for item in (path, alternate):
        os.utime(item, (1700000000, 1700000000))
    cache = Path(importlib.util.cache_from_source(str(path)))
    cache.parent.mkdir(exist_ok=True)
    py_compile.compile(str(alternate), cfile=str(cache), doraise=True,
                       invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
    spec = importlib.util.spec_from_file_location("actual_cache_control", path)
    ordinary = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ordinary)
    if ordinary.VALUE != "altered":
        raise AssertionError("stale cache counterexample did not reproduce")
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


class ExactZeroSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = model.expected_report()
        cls.rows = model.original_rows()

    def reject_report(self, mutate):
        candidate = copy.deepcopy(self.report)
        mutate(candidate)
        with self.assertRaises(ValueError):
            model.validate_report(candidate)

    def test_original_complete_witness_and_saved_record(self):
        self.assertEqual(model.guards.bounded_bytes(self.report),
                         model.guards.bounded_bytes(model.read_report()))
        self.assertEqual(self.report["summary"], {
            "complete_original_sources": 3, "physical_zero_events": 3,
            "nonsmooth_source_knot_events": 2, "smooth_interior_events": 1,
            "exterior_zero_events": 0, "continuum_sources": 0})
        for proof, coordinate, signs in zip(self.report["source_specific_proofs"],
                                            ("1", "1", "1/2"),
                                            ([-1, 1], [-1, 1], [1, -1])):
            self.assertEqual(proof["physical_zero_set"], [coordinate])
            self.assertEqual(proof["ordered_nonzero_signs"], signs)
            self.assertEqual(proof["complete_finite_physical_event_count"], 1)
            self.assertTrue(proof["complete_original_source_zero_set"])
            self.assertFalse(proof["retained_transverse_negative_control"]["is_truth_value"])

    def test_v23_sufficient_condition_has_a_real_strict_boundary(self):
        self.assertEqual(model.v23_derivative_lower(Q(1, 1000)), Q(249, 1000))
        self.assertGreater(model.v23_derivative_lower(Q(1, 8)), 0)
        for epsilon in (Q(1, 4), Q(1, 3), Q(-1, 1000)):
            with self.subTest(epsilon=epsilon), self.assertRaises(ValueError):
                model.v23_derivative_lower(epsilon)

    def test_v25_dominance_requires_strictly_positive_margin(self):
        self.assertEqual(model.v25_derivative_lower(Q(1, 20), Q(4), Q(1, 1000)),
                         Q(487, 500))
        for parameters in ((Q(2), Q(4), Q(0)), (Q(3), Q(4), Q(0)),
                           (Q(0), Q(-4), Q(0)), (Q(-1), Q(4), Q(0))):
            with self.subTest(parameters=parameters), self.assertRaises(ValueError):
                model.v25_derivative_lower(*parameters)

    def test_v40_negative_coefficient_and_residual_are_both_required(self):
        actual = model.v40_derivative_upper(Q(19, 20), Q(1, 10), Q(1, 100000000))
        self.assertEqual(actual, -Q(49, 80) + Q(11, 700000000))
        self.assertLess(actual, 0)
        for parameters in ((Q(1), Q(3, 4), Q(0)),
                           (Q(19, 20), Q(1, 10), Q(1)),
                           (Q(0), Q(0), Q(0))):
            with self.subTest(parameters=parameters), self.assertRaises(ValueError):
                model.v40_derivative_upper(*parameters)

    def test_conditional_helpers_do_not_coerce_unsafe_rationals(self):
        for value in (True, 0.01, "1/1000", "1e999999999", Q(1 << 129)):
            with self.subTest(value_type=type(value).__name__), self.assertRaises(ValueError):
                model.v23_derivative_lower(value)

    def test_exact_source_mutations_never_reach_legacy_lowerer(self):
        for field, value in (("phase_turn_offset", "1/12"),
                             ("phase_turn_rate", "1e999999999"),
                             ("source_parameter_id", "aliased-time"),
                             ("parameter_hi", "3")):
            row = copy.deepcopy(self.rows["v23"])
            row["spec"][field] = value
            with self.subTest(field=field), patch.object(
                    model.lower, "_normalise_harmonic_splines",
                    side_effect=AssertionError("untrusted source reached lowerer")):
                with self.assertRaises(ValueError):
                    model.source_proof(row)

    def test_original_record_provenance_and_old_disposition_are_bound(self):
        for mutate in (
                lambda r: r.update(origin="different-producer"),
                lambda r: r["expected"].update(v54_disposition="CERTIFIED"),
                lambda r: r["spec"]["cos_splines"]["2"]["controls"].__setitem__(0, "1/1000"),
                lambda r: r["spec"]["sin_splines"]["1"]["knots"].__setitem__(2, "1/2")):
            row = copy.deepcopy(self.rows["v23"])
            mutate(row)
            with self.assertRaises(ValueError):
                model.check_original(row)

    def test_actual_source_continuity_is_checked_before_composition(self):
        _, _, spans = model.lower_original(self.rows["v23"])
        terms = copy.deepcopy(spans[1].terms)
        terms[0] = ((terms[0][0][0] + Q(1, 1000),), (Q(0),))
        bad = model.interval.Span(1, 2, 0, Q(1, 12), terms)
        with self.assertRaisesRegex(ValueError, "COEFFICIENT_DISCONTINUITY"):
            model.require_continuous_pair([spans[0], bad])

    def test_source_gap_overlap_and_phase_mismatch_refuse(self):
        _, _, spans = model.lower_original(self.rows["v25"])
        for left, phase in ((Q(3, 2), Q(-1, 12)), (Q(1, 2), Q(-1, 12)),
                            (Q(1), Q(0))):
            bad = model.interval.Span(left, 2, phase, Q(1, 12), spans[1].terms)
            with self.subTest(left=left, phase=phase), self.assertRaises(ValueError):
                model.require_continuous_pair([spans[0], bad])

    def test_analytic_identity_checks_all_harmonics(self):
        _, _, spans = model.lower_original(self.rows["v40"])
        terms = copy.deepcopy(spans[0].terms)
        terms[2] = ((Q(0),), (Q(0),))
        bad = model.interval.Span(0, 1, Q(1, 16), Q(1, 8), terms)
        with self.assertRaisesRegex(ValueError, "ANALYTIC_FACTOR_OR_PHASE_IDENTITY"):
            model._require_analytic_identities("v40", [bad, spans[1]])

    def test_local_point_proof_does_not_establish_whole_source_alone(self):
        _, _, spans = model.lower_original(self.rows["v40"])
        root = model.point.point(spans[0], Q(1, 2), max_order=1)
        shifted = model.point.point(spans[0], Q(1, 4), max_order=1)
        self.assertEqual(root["status"], "EXACT_RATIONAL_POINT_EVENT")
        self.assertFalse(root["complete_open_roots_claimed"])
        self.assertEqual(shifted["status"], "EXACT_NONZERO_RATIONAL_POINT")
        self.assertEqual(shifted["value_sign"], 1)

    def test_sided_knot_order_is_not_global_smooth_multiplicity(self):
        for proof in self.report["source_specific_proofs"][:2]:
            event = proof["physical_events"][0]
            self.assertTrue(event["exact_sided_derivatives_unequal"])
            self.assertFalse(event["global_smooth_multiplicity_claimed"])
            self.assertEqual([event["left_one_sided_order"], event["right_one_sided_order"]],
                             [1, 1])
            self.assertNotIn("smooth_multiplicity", event)
        self.reject_report(lambda r: r["source_specific_proofs"][0]["physical_events"][0].update(
            smooth_multiplicity=1, global_smooth_multiplicity_claimed=True))

    def test_knot_cannot_be_double_counted(self):
        self.reject_report(lambda r: r["source_specific_proofs"][0]["physical_events"].append(
            copy.deepcopy(r["source_specific_proofs"][0]["physical_events"][0])))

    def test_exact_cut_root_is_not_a_true_spline_knot(self):
        proof = self.report["source_specific_proofs"][2]
        self.assertEqual(proof["original_source_piece_edges"], ["0", "1", "2"])
        self.assertEqual(proof["source_knot_receipt"]["physical_zero_events"], 0)
        self.assertFalse(proof["physical_events"][0]["is_original_source_knot"])
        self.reject_report(lambda r: r["source_specific_proofs"][2]["physical_events"][0].update(
            coordinate="1", is_original_source_knot=True))

    def test_missing_source_and_count_preserving_identity_swap_refuse(self):
        self.reject_report(lambda r: r["source_specific_proofs"].pop())
        self.reject_report(lambda r: r["source_specific_proofs"][0].update(
            case_id=r["source_specific_proofs"][1]["case_id"]))

    def test_sign_bounds_and_whole_source_coverage_cannot_be_forged(self):
        self.reject_report(lambda r: r["source_specific_proofs"][0].update(ordered_nonzero_signs=[1, -1]))
        self.reject_report(lambda r: r["source_specific_proofs"][1]["whole_source_completeness_proof"].update(
            strict_derivative_lower_bound_on_each_span="1"))
        self.reject_report(lambda r: r["source_specific_proofs"][2]["source_spans"].pop())

    def test_bool_integer_alias_is_rejected_by_canonical_comparison(self):
        self.reject_report(lambda r: r["source_specific_proofs"][0].update(
            complete_finite_physical_event_count=True))

    def test_programme_and_historical_claims_cannot_be_promoted(self):
        self.reject_report(lambda r: r.update(mc_b_established=True))
        self.reject_report(lambda r: r["historical_v54"].update(route_refusals=17))
        self.reject_report(lambda r: r["source_specific_proofs"][0]["retained_transverse_negative_control"].update(
            is_truth_value=True))

    def test_dependency_drift_refuses_before_replay(self):
        key = model.TASK + "pb00701_rational_phase_point.py"
        with patch.dict(model.PINS, {key: "0" * 40}), self.assertRaisesRegex(
                ValueError, "PINNED_DEPENDENCY_DRIFT"):
            model.expected_report()

    def test_transitive_runtime_modules_require_exact_paths(self):
        for module in (model.guards, model.lower, model.interval, model.point,
                       model.lower.v6, model.lower.v6.base, model.lower.EE):
            actual = Path(module.__file__)
            with self.subTest(module=module.__name__), patch.object(
                    module, "__file__", str(actual.with_name("other_" + actual.name))):
                with self.assertRaisesRegex(ValueError, "IMPORTED_DEPENDENCY_PATH_CHANGED"):
                    model.original_rows()

    def test_point_resource_refusal_is_never_a_completed_witness(self):
        with patch.object(model.point, "point", side_effect=model.point.Refusal("JET_ORDER_RESOURCE_LIMIT")):
            with self.assertRaises(ValueError):
                model.source_proof(self.rows["v23"])

    def test_transverse_negative_control_cannot_be_silently_reclassified(self):
        with patch.object(model.interval, "attempt", return_value={"is_truth_value": True}):
            with self.assertRaisesRegex(ValueError, "EXPECTED_TRANSVERSE_REFUSAL"):
                model.source_proof(self.rows["v40"])

    def test_transverse_refusal_must_retain_its_exact_status_and_reason(self):
        for altered in (
                {"is_truth_value": False, "status": "BLOCKED", "reason": "UNDECIDED_ISOLATION_CUT"},
                {"is_truth_value": False, "status": "RESOURCE_REFUSAL", "reason": "NODE_RESOURCE_LIMIT"},
                {"is_truth_value": False}):
            with self.subTest(control=altered), patch.object(model.interval, "attempt", return_value=altered):
                with self.assertRaisesRegex(ValueError, "EXPECTED_TRANSVERSE_REFUSAL_CHANGED"):
                    model.source_proof(self.rows["v40"])

    def test_unsafe_report_data_refuses_before_proof_execution(self):
        cycle = []
        cycle.append(cycle)
        deep = None
        for _ in range(40):
            deep = [deep]
        for value in (cycle, deep, {"x": float("nan")}, {"x": 1 << 257},
                      {"x": "z" * 8193}, {"x": object()}):
            with self.subTest(kind=type(value).__name__), patch.object(
                    model, "expected_report", side_effect=AssertionError("unsafe data reached replay")):
                with self.assertRaises(ValueError):
                    model.validate_report(value)

    def test_duplicate_keys_and_oversized_files_refuse(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "witness.json"
            path.write_text('{"status":false,"status":true}')
            with self.assertRaises(ValueError):
                model.read_report(path)
            path.write_bytes(b" " * (model.guards.MAX_BYTES + 1))
            with self.assertRaises(ValueError):
                model.read_report(path)

    def test_aggregate_escaped_bytes_are_bounded_before_replay(self):
        oversized = {"x": ["\U0010ffff" * 8192 for _ in range(12)]}
        with patch.object(model, "expected_report", side_effect=AssertionError("oversized report reached replay")):
            with self.assertRaises(ValueError):
                model.validate_report(oversized)

    def test_verifier_bootstrap_ignores_real_cache_and_preloaded_model(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.py"
            expected = _matching_cache(path)
            poison = types.SimpleNamespace(VALUE="preloaded")
            names = ("exact_zero_verified_model", "pb00701_exact_zero_child_source_completion")
            with patch.dict(sys.modules, {name: poison for name in names}):
                self.assertEqual(_load_verified_model(path, expected).VALUE, "trusted")
                self.assertTrue(all(sys.modules[name] is poison for name in names))

    def test_verifier_bootstrap_uses_checked_buffer_and_refuses_before_compile(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.py"
            expected = _matching_cache(path)

            def replace_after_hash(raw, filename, mode):
                path.write_bytes(b"raise AssertionError('unverified replacement')\n")
                return builtins.compile(raw, filename, mode)

            with patch.dict(globals(), compile=replace_after_hash):
                self.assertEqual(_load_verified_model(path, expected).VALUE, "trusted")
            with patch.dict(globals(), compile=unittest.mock.Mock(
                    side_effect=AssertionError("unverified model compiled"))):
                with self.assertRaisesRegex(ValueError, "VERIFIER_MODEL_SOURCE_DRIFT"):
                    _load_verified_model(path, expected)
                with path.open("wb") as stream:
                    stream.truncate(1048577)
                with self.assertRaisesRegex(ValueError, "RESOURCE_REFUSAL"):
                    _load_verified_model(path, expected)
                globals()["compile"].assert_not_called()

    def test_private_import_graph_ignores_transitive_cache_and_preload(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            child = root / "pb00701_probe.py"
            child_blob = _matching_cache(child)
            parent = root / "parent.py"
            parent.write_text("import sys\nsys.path.insert(0, 'private-only')\n"
                              "import pb00701_probe as child\nVALUE = child.VALUE\n")
            pins = {child.name: child_blob, parent.name: model.guards.git_blob(parent)}
            importer, old_path = builtins.__import__, list(sys.path)
            poison = types.SimpleNamespace(VALUE="preloaded")
            with patch.dict(sys.modules, pb00701_probe=poison):
                runtime = model._PinnedRuntime(root, pins)
                loaded = runtime.load(parent)
                self.assertEqual(loaded.VALUE, "trusted")
                self.assertIs(loaded.child, runtime.load(child))
                self.assertIs(sys.modules["pb00701_probe"], poison)
            self.assertIs(builtins.__import__, importer)
            self.assertEqual(sys.path, old_path)
            self.assertEqual(runtime.local_sys.path[0], "private-only")

    def test_dynamic_project_import_uses_verified_bytes_and_exact_whitelist(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            child = root / "event_engine.py"
            child_blob = _matching_cache(child)
            parent = root / "parent.py"
            parent.write_text("import importlib.util\nfrom pathlib import Path\n"
                              "spec = importlib.util.spec_from_file_location('nested', "
                              "Path(__file__).with_name('event_engine.py'))\n"
                              "child = importlib.util.module_from_spec(spec)\n"
                              "spec.loader.exec_module(child)\nVALUE = child.VALUE\n")
            runtime = model._PinnedRuntime(root, {
                child.name: child_blob, parent.name: model.guards.git_blob(parent)})
            factory = importlib.util.spec_from_file_location
            self.assertEqual(runtime.load(parent).VALUE, "trusted")
            self.assertIs(importlib.util.spec_from_file_location, factory)
            with patch.object(model, "_pinned_bytes", side_effect=AssertionError("unlisted file read")) as reader:
                with self.assertRaisesRegex(ValueError, "UNPINNED_DYNAMIC_MODULE"):
                    runtime._spec("unlisted", root / "alternate.py")
                with self.assertRaisesRegex(ValueError, "UNPINNED_PROJECT_MODULE"):
                    runtime._import("pb00701_unlisted")
                reader.assert_not_called()

    def test_private_compiler_uses_verified_buffer_after_path_replacement(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "probe.py"
            expected = _matching_cache(path)

            def replace_after_hash(raw, filename, mode):
                path.write_bytes(b"raise AssertionError('unchecked code')\n")
                return builtins.compile(raw, filename, mode)

            runtime = model._PinnedRuntime(root, {path.name: expected})
            with patch.object(model, "compile", side_effect=replace_after_hash, create=True):
                self.assertEqual(runtime.load(path).VALUE, "trusted")
            with self.assertRaisesRegex(ValueError, "PINNED_DEPENDENCY_DRIFT"):
                model._PinnedRuntime(root, {path.name: expected}).load(path)

    def test_pinned_json_decodes_checked_buffer_and_rejects_unknown_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "input.json"
            path.write_bytes(b'{"value":1}\n')
            expected = model.guards.git_blob(path)
            decode = model._decode_json

            def replace_after_hash(raw):
                path.write_bytes(b'{"value":2}\n')
                return decode(raw)

            with patch.object(model, "ROOT", root), patch.object(model, "PINS", {path.name: expected}):
                with patch.object(model, "_decode_json", side_effect=replace_after_hash):
                    self.assertEqual(model._pinned_json(path), {"value": 1})
                with self.assertRaisesRegex(ValueError, "PINNED_DEPENDENCY_DRIFT"):
                    model._pinned_json(path)
                with patch.object(model, "_pinned_bytes", side_effect=AssertionError("unknown file read")) as reader:
                    with self.assertRaisesRegex(ValueError, "UNPINNED_JSON_INPUT"):
                        model._pinned_json(root / "unknown.json")
                    reader.assert_not_called()


def contract():
    fresh = model.expected_report()
    model.need(model.guards.bounded_bytes(model.read_report()) == model.guards.bounded_bytes(fresh),
               "SAVED_REPORT_DIFFERS_FROM_FRESH_ORIGINAL_PROOF")
    return fresh


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    report = contract()
    print(json.dumps(report["summary"], sort_keys=True))
    if args.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(ExactZeroSourceTests))
        if not result.wasSuccessful():
            raise SystemExit(1)


if __name__ == "__main__":
    main()
