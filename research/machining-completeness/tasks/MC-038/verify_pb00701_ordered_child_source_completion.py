#!/usr/bin/env python3
"""Replay fifteen complete original-source proofs and challenge their consumer."""
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
MODEL_PATH = Path(__file__).resolve().with_name("pb00701_ordered_child_source_completion.py")
MODEL_BLOB = "549251696e43f22122f8ba957baa2befcd8d77a8"
MAX_MODEL_BYTES = 1048576


def _load_model():
    """The verifier executes the same bounded model buffer it checks."""
    with MODEL_PATH.open("rb") as stream:
        raw = stream.read(MAX_MODEL_BYTES + 1)
    if len(raw) > MAX_MODEL_BYTES:
        raise ValueError("MODEL_SOURCE_BYTE_LIMIT")
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    if actual != MODEL_BLOB:
        raise ValueError("PINNED_MODEL_SOURCE_DRIFT")
    module = types.ModuleType("pb00701_ordered_child_source_completion")
    module.__file__ = str(MODEL_PATH)
    exec(compile(raw, str(MODEL_PATH), "exec"), module.__dict__)
    return module


model = _load_model()


class CompletionTests(unittest.TestCase):
    expected = None

    @classmethod
    def setUpClass(cls):
        if cls.expected is None:
            cls.expected = model.expected_report()
        cls.expected_bytes = model.bounded_bytes(cls.expected)
        cls.rows = model.original_rows()
        cls.lower, cls.trig = model.implementation()

    def source(self, marker):
        return next(row for cid, row in self.rows.items() if marker in cid)

    def views(self, marker="_V37_"):
        row = self.source(marker)
        return row, model.lower_original(row, self.lower, self.trig)

    def rejects_report(self, change):
        candidate = copy.deepcopy(self.expected)
        change(candidate)
        with self.assertRaises(model.Refusal):
            model._compare_with_replayed_bytes(candidate, self.expected_bytes)

    def pinned_tree(self, directory):
        root = Path(directory)
        for relative in model.PINS:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((model.ROOT / relative).read_bytes())
        return root

    def accepted_stale_cache(self, original):
        """Build a real cache that ordinary importlib accepts over pinned source."""
        alternate = original.with_name("alternate_cached_source.py")
        prefix = b"CACHE_POISON = True\n#"
        alternate.write_bytes(prefix + b"x" * (original.stat().st_size - len(prefix) - 1) + b"\n")
        for path in (original, alternate):
            os.utime(path, (1700000000, 1700000000))
        cache = Path(importlib.util.cache_from_source(str(original)))
        cache.parent.mkdir(exist_ok=True)
        py_compile.compile(str(alternate), cfile=str(cache), doraise=True,
                           invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
        spec = importlib.util.spec_from_file_location("accepted_cache_control", original)
        poisoned = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(poisoned)
        self.assertTrue(poisoned.CACHE_POISON)

    def test_exact_original_results_and_full_coverage(self):
        self.assertEqual(len(model.CASES), 15)
        sources = self.expected["source_cases"]
        self.assertEqual({r["case_id"] for r in sources}, set(model.CASES))
        self.assertEqual(sum(r["complete_closed_root_count"] for r in sources), 8)
        self.assertEqual(sum(r["complete_closed_root_count"] == 0 for r in sources), 8)
        for row in sources:
            self.assertEqual(row["source_interval"], ["0", "2"])
            self.assertEqual([s["original_interval"] for s in row["original_spans"]],
                             [["0", "1"], ["1", "2"]])
            self.assertTrue(row["complete_original_source_zero_set"])
            self.assertFalse(row["true_source_knots"][0]["is_physical_zero"])
            self.assertEqual(row["source_sha256"], model.CASE_PINS[row["case_id"]][0])
        self.assertTrue(model.validate_report(self.expected))

    def test_cubic_lowering_uses_original_global_parameter(self):
        expected = {
            "_V37_": ((Q(9, 10), Q(34, 25), Q(417, 800), Q(9, 1600)),
                       (Q(1), Q(301, 200), Q(57, 100), Q(9, 3200))),
            "_V42_": ((Q(-7, 10), Q(3, 5), Q(8, 9), Q(2, 16875)),
                       (Q(7, 10), Q(-19, 15), Q(8, 9), Q(2, 16875))),
            "_V48_": ((Q(-7, 40), Q(9, 40), Q(1, 2), Q(1, 10000)),
                       (Q(7, 40), Q(-19, 40), Q(1, 2), Q(1, 10000))),
        }
        for marker, terms in expected.items():
            with self.subTest(marker=marker):
                _, views = self.views(marker)
                self.assertEqual(views[0]["terms"][1], terms)
                for channel in (0, 1):
                    self.assertEqual(self.trig.polynomial(terms[channel], Q(1)),
                                     views[1]["terms"][1][channel][0])

    def test_v30_has_two_ordered_crossings_across_a_nonzero_knot(self):
        row = next(r for r in self.expected["source_cases"] if "_V30_" in r["case_id"])
        self.assertEqual([e["strict_bracket"] for e in row["ordered_root_events"]],
                         [["3/32", "7/64"], ["121/64", "61/32"]])
        self.assertEqual([c["sign"] for c in row["maximal_open_physical_sign_cells"]], [-1, 1, -1])
        self.assertEqual(row["true_source_knots"][0]["left_sign"], 1)
        self.assertFalse(row["true_source_knots"][0]["is_physical_event"])

    def test_source_mutations_refuse_before_legacy_parsing(self):
        row = self.source("_V37_")
        mutations = [
            lambda r: r["spec"].__setitem__("phase_turn_rate", "1e1000000000"),
            lambda r: r["spec"].__setitem__("source_parameter_id", "other-clock"),
            lambda r: r["spec"]["cos_splines"]["1"]["controls"].__setitem__(0, "-9/10"),
            lambda r: r["spec"]["cos_splines"]["1"]["knots"].__setitem__(4, "3/4"),
            lambda r: r.__setitem__("origin", "invented-source"),
            lambda r: r["expected"].__setitem__("v54_disposition", "CERTIFIED"),
            lambda r: r["expected"]["observed"]["spans"][0].__setitem__(0, model.V6),
        ]
        for change in mutations:
            changed = copy.deepcopy(row)
            change(changed)
            with self.subTest(change=change), mock.patch.object(
                    self.lower, "_normalise_harmonic_splines",
                    side_effect=AssertionError("unbound source reached old parser")) as legacy:
                with self.assertRaises(model.Refusal):
                    model.lower_original(changed, self.lower, self.trig)
                legacy.assert_not_called()

    def test_finite_set_excludes_the_three_exact_zero_cases(self):
        for cid in model.DEFERRED:
            with self.subTest(cid=cid), self.assertRaisesRegex(model.Refusal, "FINITE_SET"):
                model.lower_original(self.rows[cid], self.lower, self.trig)
        self.assertEqual(len(self.expected["preserved_negative_controls"]), 3)
        for control in self.expected["preserved_negative_controls"]:
            self.assertEqual(control["kernel_status"], "REFUSAL")
            self.assertEqual(control["reason"], model.DEFERRED[control["case_id"]])
            self.assertFalse(control["included_in_complete_sources"])
            self.assertFalse(control["mathematical_impossibility_claimed"])

    def test_actual_channel_discontinuity_cannot_be_composed(self):
        row, views = self.views()
        second = views[1]
        p, q = second["terms"][1]
        second["terms"][1] = ((p[0] + 1,), q)
        second["span"] = self.trig.Span(*second["interval"], *second["phase"], second["terms"])
        with self.assertRaisesRegex(model.Refusal, "CHANNEL_KNOT_DISCONTINUITY"):
            model.check_source_cover(row, views, self.trig)

    def test_actual_span_gap_overlap_omission_and_order_refuse(self):
        for mode in ("gap", "overlap", "omission", "duplicate", "reverse"):
            row, views = self.views()
            if mode == "omission":
                views.pop()
            elif mode == "duplicate":
                views.append(views[1])
            elif mode == "reverse":
                views.reverse()
            else:
                left = Q(5, 4) if mode == "gap" else Q(3, 4)
                views[1]["interval"] = (left, Q(2))
                views[1]["span"] = self.trig.Span(left, Q(2), *views[1]["phase"], views[1]["terms"])
            with self.subTest(mode=mode), self.assertRaises(model.Refusal):
                model.check_source_cover(row, views, self.trig)

    def test_companion_phase_or_parameter_change_refuses(self):
        row, views = self.views()
        views[1]["phase"] = (views[1]["phase"][0] + Q(1, 24), views[1]["phase"][1])
        views[1]["span"] = self.trig.Span(*views[1]["interval"], *views[1]["phase"], views[1]["terms"])
        with self.assertRaisesRegex(model.Refusal, "PARAMETER_OR_PHASE"):
            model.check_source_cover(row, views, self.trig)
        row, views = self.views()
        views[1]["source_parameter_id"] = "independent-tail-coordinate"
        with self.assertRaisesRegex(model.Refusal, "PARAMETER_OR_PHASE"):
            model.check_source_cover(row, views, self.trig)

    def test_proof_function_must_match_its_original_lowered_view(self):
        row, views = self.views()
        views[1]["span"] = self.trig.Span(Q(1), Q(2), *views[1]["phase"], {0: ((Q(1),), (Q(0),))})
        with self.assertRaisesRegex(model.Refusal, "FUNCTION_BINDING"):
            model.check_source_cover(row, views, self.trig)

    def test_missing_companion_proof_is_not_complete(self):
        row, views = self.views()
        proof = views[0]["span"].prove()
        with self.assertRaisesRegex(model.Refusal, "SPAN_PROOF"):
            model.compose(row, views, [proof], self.trig)

    def test_real_partition_gap_and_overlap_are_detected(self):
        _, views = self.views()
        valid = views[0]["span"].prove()
        self.assertGreater(len(valid["partition"]), 1)
        for mode in ("omit", "duplicate", "reverse"):
            changed = copy.deepcopy(valid)
            if mode == "omit":
                changed["partition"].pop(0)
            elif mode == "duplicate":
                changed["partition"].insert(1, copy.deepcopy(changed["partition"][0]))
            else:
                changed["partition"].reverse()
            with self.subTest(mode=mode), self.assertRaisesRegex(model.Refusal, "PARTITION_GAP"):
                model.check_partition(views[0], changed, self.trig)

    def test_root_isolation_sign_derivative_and_count_are_rechecked(self):
        _, views = self.views("_V30_")
        valid = views[0]["span"].prove()
        mutations = [
            lambda p: next(c for c in p["partition"] if c["kind"] == "ONE_SIMPLE_ROOT").__setitem__("strict_isolation", ["0", "1/64"]),
            lambda p: next(c for c in p["partition"] if c["kind"] == "ONE_SIMPLE_ROOT").__setitem__("derivative_sign", -1),
            lambda p: next(c for c in p["partition"] if c["kind"] == "ONE_SIMPLE_ROOT").__setitem__("right_sign", -1),
            lambda p: next(c for c in p["partition"] if c["kind"] == "ONE_SIMPLE_ROOT").__setitem__("smooth_multiplicity", 2),
            lambda p: p.__setitem__("complete_simple_root_count", 0),
        ]
        for change in mutations:
            changed = copy.deepcopy(valid)
            change(changed)
            with self.subTest(change=change), self.assertRaises(model.Refusal):
                model.check_partition(views[0], changed, self.trig)

    def test_false_root_free_cell_cannot_erase_actual_crossing(self):
        _, views = self.views("_V9_")
        proof = views[0]["span"].prove()
        self.assertEqual(len(proof["partition"]), 1)
        proof["partition"] = [{"kind": "NO_ROOT", "interval": ["0", "1"], "sign": -1}]
        proof["complete_simple_root_count"] = 0
        with self.assertRaisesRegex(model.Refusal, "NO_ROOT_CELL_NOT_PROVED"):
            model.check_partition(views[0], proof, self.trig)

    def test_real_resource_exhaustion_is_nontruth(self):
        row = self.source("_V37_")
        with mock.patch.object(model, "PROOF_DEPTH", 0), mock.patch.object(model, "PROOF_NODES", 1):
            with self.assertRaisesRegex(model.Refusal, "INTERVAL_REPLAY_REFUSAL"):
                model.prove_original(row, self.lower, self.trig)

    def test_replay_refusal_aborts_without_saved_report_fallback(self):
        with mock.patch.object(model, "implementation", return_value=(self.lower, self.trig)), \
                mock.patch.object(self.trig.Span, "prove", side_effect=self.trig.Refusal("NODE_RESOURCE_LIMIT")):
            with self.assertRaisesRegex(model.Refusal, "INTERVAL_REPLAY_REFUSAL"):
                model.expected_report()
        with mock.patch.object(model, "implementation", return_value=(self.lower, self.trig)), \
                mock.patch.object(self.trig.Span, "prove", return_value={"status": "RESOURCE_REFUSAL", "is_truth_value": False}):
            with self.assertRaisesRegex(model.Refusal, "REPLAY_NOT_PROOF"):
                model.expected_report()

    def test_original_source_omission_duplication_and_swapping(self):
        self.rejects_report(lambda r: r["source_cases"].pop())
        self.rejects_report(lambda r: r["source_cases"].append(copy.deepcopy(r["source_cases"][0])))
        self.rejects_report(lambda r: r["source_cases"].__setitem__(1, copy.deepcopy(r["source_cases"][0])))
        self.rejects_report(lambda r: r["source_cases"][0].__setitem__("case_id", model.CASES[1]))

    def test_report_events_cannot_be_moved_removed_or_fabricated(self):
        def event_row(r):
            return next(x for x in r["source_cases"] if x["ordered_root_events"])
        self.rejects_report(lambda r: event_row(r)["ordered_root_events"].pop())
        self.rejects_report(lambda r: event_row(r)["ordered_root_events"][0].__setitem__("strict_bracket", ["0", "2"]))
        self.rejects_report(lambda r: event_row(r)["true_source_knots"][0].__setitem__("is_physical_event", True))
        self.rejects_report(lambda r: event_row(r)["maximal_open_physical_sign_cells"][0].__setitem__("sign", 1))
        self.rejects_report(lambda r: event_row(r)["original_spans"].pop())

    def test_boolean_integer_aliases_and_gate_claims_are_rejected(self):
        self.rejects_report(lambda r: r["summary"].__setitem__("finite_simple_roots", 8.0))
        self.rejects_report(lambda r: r["source_cases"][0].__setitem__("complete_original_source_zero_set", 1))
        self.rejects_report(lambda r: r["source_cases"][0]["true_source_knots"][0].__setitem__("is_physical_zero", 0))
        self.rejects_report(lambda r: r["gates"].__setitem__("production_authorized", 0))
        for key, value in (("PB-007-01", "CLOSED"), ("MC-B", "ACCEPTED"),
                           ("MC-1", "ACCEPTED"), ("required_machining_operations", 25),
                           ("native_geometry_or_STEP_qualified", True)):
            self.rejects_report(lambda r, key=key, value=value: r["gates"].__setitem__(key, value))

    def test_preflight_blocks_resource_and_type_abuse_before_replay(self):
        cycle = []; cycle.append(cycle)
        deep = []
        for _ in range(model.MAX_DEPTH + 2):
            deep = [deep]
        invalid = [cycle, deep, "x" * (model.MAX_STRING + 1), 1 << 257,
                   float("nan"), 0.0, object(), {1: "not-a-string-key"},
                   ["x" * 8192 for _ in range(129)]]
        for candidate in invalid:
            with self.subTest(type=type(candidate)), mock.patch.object(model, "expected_report") as replay:
                with self.assertRaises(model.Refusal):
                    model.validate_report(candidate)
                replay.assert_not_called()

    def test_duplicate_keys_and_numeric_json_abuse(self):
        invalid = [b'{"x":1,"x":2}', b'{"x":1.0}', b'{"x":NaN}',
                   ('{"x":' + '9' * 1000 + '}').encode(), b'{"x":Infinity}']
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "candidate.json"
            for raw in invalid:
                path.write_bytes(raw)
                with self.subTest(raw=raw[:32]), self.assertRaises(model.Refusal):
                    model.read_json(path)
            path.write_bytes(b"x" * (model.MAX_BYTES + 1))
            with self.assertRaisesRegex(model.Refusal, "FILE_BYTE_LIMIT"):
                model.read_json(path)

    def test_rational_lexical_guards_precede_fraction_construction(self):
        for value in ("1e1000000000", "1E-1000000000", "0.5", "+1", "1/0",
                      "9" * 40, "1/" + "9" * 40, "\u0661/2", 1.0, True):
            with self.subTest(value=value), mock.patch.object(model, "Q", side_effect=AssertionError("unsafe parse")) as parser:
                with self.assertRaises(model.Refusal):
                    model.exact_rational(value)
                parser.assert_not_called()
        for value in ("01", "-0", "1/1", "2/4", "1/02"):
            with self.subTest(value=value), self.assertRaises(model.Refusal):
                model.exact_rational(value)

    def test_dependency_drift_precedes_source_replay(self):
        real_read = model.read_bytes
        def changed(path):
            return b"altered source\n" if Path(path).name == "event_engine.py" else real_read(path)
        with mock.patch.object(model, "read_bytes", side_effect=changed), mock.patch.object(
                model, "implementation", side_effect=AssertionError("unpinned replay")) as replay:
            with self.assertRaisesRegex(model.Refusal, "PINNED_INPUT_DRIFT"):
                model.expected_report()
            replay.assert_not_called()

    def test_preloaded_project_modules_are_ignored_without_global_import_changes(self):
        poisoned = {}
        for name, relative in model.MODULE_PATHS.items():
            module = types.ModuleType(name)
            module.__file__ = str(model.ROOT / relative)
            module.CACHE_POISON = True
            poisoned[name] = module
        importer, factory, search_path = builtins.__import__, importlib.util.spec_from_file_location, list(sys.path)
        with mock.patch.dict(sys.modules, poisoned):
            lower, trig = model.implementation()
            actual = (lower, lower.v6, lower.v6.base, trig, lower.EE)
            self.assertTrue(all(not hasattr(module, "CACHE_POISON") for module in actual))
            self.assertTrue(all(sys.modules[name] is module for name, module in poisoned.items()))
            proof = model.prove_original(self.source("_V9_"), lower, trig)
            self.assertEqual(proof["complete_closed_root_count"], 1)
            self.assertIs(lower.EE, lower.v6.base.EE)
        self.assertIs(builtins.__import__, importer)
        self.assertIs(importlib.util.spec_from_file_location, factory)
        self.assertEqual(sys.path, search_path)

    def test_actual_stale_bytecode_cannot_replace_any_implementation_module(self):
        with tempfile.TemporaryDirectory(prefix="radicadsac-children-cache-") as directory:
            root = self.pinned_tree(directory)
            for relative in model.MODULE_PATHS.values():
                self.accepted_stale_cache(root / relative)
            with mock.patch.object(model, "ROOT", root):
                lower, trig = model.implementation()
                self.assertTrue(all(not hasattr(module, "CACHE_POISON") for module in
                                    (lower, lower.v6, lower.v6.base, lower.EE, trig)))
                proof = model.prove_original(self.source("_V37_"), lower, trig)
                self.assertEqual(proof["complete_closed_root_count"], 1)

    def test_transitive_execution_uses_buffer_pinned_before_path_replacement(self):
        with tempfile.TemporaryDirectory(prefix="radicadsac-children-buffer-") as directory:
            root = self.pinned_tree(directory)
            with mock.patch.object(model, "ROOT", root):
                session = model._PinnedImplementation()
                engine = root / model.MODULE_PATHS[model.ENGINE_MODULE]
                engine.write_bytes(b"raise AssertionError('replaced path executed')\n")
                lower = session.load("pb00701_coupled_bspline_model")
                self.assertEqual(lower.EE.q("1/7"), Q(1, 7))
                with self.assertRaisesRegex(model.Refusal, "PINNED_INPUT_DRIFT"):
                    model.implementation()
                with self.assertRaisesRegex(model.Refusal, "UNPINNED_DYNAMIC_MODULE"):
                    session._engine_spec(model.ENGINE_MODULE, root / "unlisted.py")
                with self.assertRaisesRegex(model.Refusal, "UNPINNED_PROJECT_IMPORT"):
                    session._import("pb00701_unlisted_producer")

    def test_json_decode_uses_same_pinned_buffer_and_exact_input_path(self):
        with tempfile.TemporaryDirectory(prefix="radicadsac-children-json-") as directory:
            root = self.pinned_tree(directory)
            path = root / "handoffs/current-authority.json"
            expected, decode = json.loads(path.read_bytes()), model._decode_json
            def replace(raw):
                path.write_bytes(b'{"changed_after_hash":true}\n')
                return decode(raw)
            with mock.patch.object(model, "ROOT", root):
                with mock.patch.object(model, "_decode_json", side_effect=replace):
                    self.assertEqual(model.read_pinned_json(path), expected)
                with self.assertRaisesRegex(model.Refusal, "PINNED_INPUT_DRIFT"):
                    model.read_pinned_json(path)
                with mock.patch.object(model, "_decode_json", side_effect=AssertionError("unlisted input decoded")) as decode_call:
                    with self.assertRaisesRegex(model.Refusal, "JSON_PATH_OUTSIDE_PINNED_INPUTS"):
                        model.read_pinned_json(root / "unlisted.json")
                    decode_call.assert_not_called()

    def test_all_consumed_original_json_uses_pinned_buffer_reader(self):
        with mock.patch.object(model, "read_pinned_json", wraps=model.read_pinned_json) as reader:
            rows = model.original_rows()
        self.assertEqual(set(rows), set(model.CASE_PINS))
        expected = {model.ROOT / path for path in (
            "handoffs/current-authority.json", "research/machining-completeness/programme-v1.json",
            "research/machining-completeness/tasks/MC-002/domain-contract-v1.json",
            model.TASK_PREFIX + "pb00701-finite-owner-corpus-v54.json",
            model.TASK_PREFIX + "pb00701-post-v54-evidence-reconciliation.json")}
        self.assertEqual({call.args[0] for call in reader.call_args_list}, expected)
        with mock.patch.object(model, "read_pinned_json", side_effect=model.Refusal("controlled input refusal")):
            with self.assertRaisesRegex(model.Refusal, "controlled input refusal"):
                model.original_rows()

    def test_verifier_bootstrap_ignores_accepted_cache_and_preloaded_model(self):
        with tempfile.TemporaryDirectory(prefix="radicadsac-children-bootstrap-") as directory:
            root = self.pinned_tree(directory)
            path = root / model.TASK_PREFIX / MODEL_PATH.name
            path.write_bytes(MODEL_PATH.read_bytes())
            self.accepted_stale_cache(path)
            fake = types.ModuleType("pb00701_ordered_child_source_completion")
            fake.CACHE_POISON = True
            with mock.patch.dict(globals(), {"MODEL_PATH": path}), \
                    mock.patch.dict(sys.modules, {fake.__name__: fake}):
                checked = _load_model()
                self.assertFalse(hasattr(checked, "CACHE_POISON"))
                self.assertIs(sys.modules[fake.__name__], fake)
                self.assertEqual(checked.bounded_bytes(checked.expected_report()), self.expected_bytes)

    def test_verifier_bootstrap_refuses_changed_or_oversized_model(self):
        with tempfile.TemporaryDirectory(prefix="radicadsac-children-bootstrap-bound-") as directory:
            path = Path(directory) / "model.py"
            for raw, reason in ((b"raise AssertionError('unverified model executed')\n", "PINNED_MODEL_SOURCE_DRIFT"),
                                (b" " * (MAX_MODEL_BYTES + 1), "MODEL_SOURCE_BYTE_LIMIT")):
                path.write_bytes(raw)
                with mock.patch.dict(globals(), {"MODEL_PATH": path}):
                    with self.assertRaisesRegex(ValueError, reason):
                        _load_model()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("choose --contract and/or --self-test")
    expected = model.expected_report()
    model._compare_with_replayed_bytes(model.read_report(), model.bounded_bytes(expected))
    print("PASS: 15 original whole-source proofs; eight simple roots; eight root-free sources")
    print("PASS: both original spans, exact channel continuity, complete checked partitions")
    print("PASS: three deferred exact-zero refusals and frozen 121/20/30 preserved")
    if args.self_test:
        CompletionTests.expected = expected
        result = unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(CompletionTests))
        if not result.wasSuccessful():
            raise SystemExit(1)


if __name__ == "__main__":
    main()
