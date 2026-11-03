#!/usr/bin/env python3
"""Replay the complete finite V2 census once; challenge custody and actual premises."""
from __future__ import annotations

import argparse
import builtins
from collections import Counter
import copy
from fractions import Fraction as Q
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import py_compile
import re
import sys
import tempfile
import types
from types import SimpleNamespace
import unittest
from unittest import mock
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "pb00701_post_v54_evidence_reconciliation_v2.py"
MODEL_BLOB = "8dede56cebbbd5540b52a280b9a31191c8901fbb"


def bootstrap_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def load_reviewed_model(path, expected):
    """Checked source bytes are the only source of executed model code."""
    with Path(path).open("rb") as stream:
        raw = stream.read(1048577)
    if len(raw) > 1048576:
        raise ValueError("MODEL_BYTE_LIMIT")
    if bootstrap_blob(raw) != expected:
        raise ValueError("MODEL_SOURCE_DRIFT")
    module = types.ModuleType("reconciliation_v2_reviewed_model")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec", dont_inherit=True, optimize=0), module.__dict__)
    return module


def install_accepted_stale_cache(path, trusted, altered):
    if len(trusted) != len(altered) or trusted == altered:
        raise AssertionError("stale-cache control must have matching source size")
    alternate = path.with_name("stale_payload.py")
    path.write_bytes(trusted)
    alternate.write_bytes(altered)
    for source in (path, alternate):
        os.utime(source, (1700000000, 1700000000))
    cache = Path(importlib.util.cache_from_source(str(path)))
    cache.parent.mkdir(parents=True, exist_ok=True)
    py_compile.compile(str(alternate), cfile=str(cache), doraise=True,
                       invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
    spec = importlib.util.spec_from_file_location("ordinary_bootstrap_cache_counterexample", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_bootstrap_tests(model_path, model_blob):
    class VerifierBootstrapTests(unittest.TestCase):
        def test_real_reviewed_source_beats_accepted_cache_and_preloaded_model(self):
            trusted = Path(model_path).read_bytes()
            self.assertEqual(bootstrap_blob(trusted), model_blob)
            payload = b"CACHE_SUBSTITUTION = True\n#"
            altered = payload + b" " * (len(trusted) - len(payload))
            with tempfile.TemporaryDirectory(prefix="v2-bootstrap-cache-") as directory:
                here = Path(directory) / "research/machining-completeness/tasks/MC-038"
                here.mkdir(parents=True)
                path = here / Path(model_path).name
                ordinary = install_accepted_stale_cache(path, trusted, altered)
                self.assertTrue(ordinary.CACHE_SUBSTITUTION)
                fake = types.ModuleType("reconciliation_v2_reviewed_model")
                fake.CACHE_SUBSTITUTION = True
                with mock.patch.dict(sys.modules, {fake.__name__: fake, Path(model_path).stem: fake}):
                    checked = load_reviewed_model(path, model_blob)
                    self.assertFalse(hasattr(checked, "CACHE_SUBSTITUTION"))
                    self.assertTrue(callable(checked.expected_report))
                    self.assertIs(sys.modules[fake.__name__], fake)

        def test_bootstrap_consumes_same_checked_buffer_after_path_replacement(self):
            with tempfile.TemporaryDirectory(prefix="v2-bootstrap-replace-") as directory:
                path = Path(directory) / "model.py"
                trusted = b"VALUE = 1\n"
                path.write_bytes(trusted)

                def substitute(raw, filename, mode, **options):
                    path.write_bytes(b"VALUE = 9\n")
                    return builtins.compile(raw, filename, mode, **options)

                with mock.patch.dict(load_reviewed_model.__globals__, {"compile": mock.Mock(side_effect=substitute)}):
                    checked = load_reviewed_model(path, bootstrap_blob(trusted))
                self.assertEqual(checked.VALUE, 1)
                with self.assertRaisesRegex(ValueError, "SOURCE_DRIFT"):
                    load_reviewed_model(path, bootstrap_blob(trusted))

        def test_bootstrap_bounds_and_drift_precede_compile(self):
            with tempfile.TemporaryDirectory(prefix="v2-bootstrap-bounds-") as directory:
                path = Path(directory) / "model.py"
                path.write_bytes(b"VALUE = 1\n")
                compiler = mock.Mock(side_effect=AssertionError("unchecked source compiled"))
                with mock.patch.dict(load_reviewed_model.__globals__, {"compile": compiler}):
                    with self.assertRaisesRegex(ValueError, "SOURCE_DRIFT"):
                        load_reviewed_model(path, "0" * 40)
                    with path.open("wb") as stream:
                        stream.truncate(1048577)
                    with self.assertRaisesRegex(ValueError, "BYTE_LIMIT"):
                        load_reviewed_model(path, "0" * 40)
                compiler.assert_not_called()

        def test_bootstrap_preserves_original_future_flags_and_assertions(self):
            with tempfile.TemporaryDirectory(prefix="v2-bootstrap-flags-") as directory:
                path = Path(directory) / "model.py"
                eager = b"VALUE: int = 1\n"
                path.write_bytes(eager)
                checked = load_reviewed_model(path, bootstrap_blob(eager))
                self.assertIs(checked.__annotations__["VALUE"], int)
                assertion = b"assert False, 'original assertion must survive'\n"
                path.write_bytes(assertion)
                with self.assertRaisesRegex(AssertionError, "original assertion must survive"):
                    load_reviewed_model(path, bootstrap_blob(assertion))

    return VerifierBootstrapTests


model = load_reviewed_model(MODEL_PATH, MODEL_BLOB)


def build_runtime_tests(runtime_module):
    Runtime = runtime_module.PinnedRuntime
    Refusal = runtime_module.RuntimeRefusal
    blob = runtime_module.git_blob

    class PinnedRuntimeTests(unittest.TestCase):
        def files(self, root, definitions):
            pins = {}
            for relative, text in definitions.items():
                path = root/relative
                path.parent.mkdir(parents=True, exist_ok=True)
                raw = text.encode("utf-8") if type(text) is str else text
                path.write_bytes(raw)
                pins[relative] = blob(raw)
            return pins

        def altered_cache(self, path):
            raw = path.read_bytes()
            payload = b"CACHE_SUBSTITUTION = True\n#"
            self.assertGreaterEqual(len(raw), len(payload))
            alternate = path.with_name("cache_payload_"+path.name)
            alternate.write_bytes(payload+b" "*(len(raw)-len(payload)))
            for item in (path, alternate):
                os.utime(item, (1700000000, 1700000000))
            cache = Path(importlib.util.cache_from_source(str(path)))
            cache.parent.mkdir(parents=True, exist_ok=True)
            py_compile.compile(str(alternate), cfile=str(cache), doraise=True)
            # Establish that the ordinary loader really accepts this altered
            # cache; merely placing an ignored malformed file is insufficient.
            spec = importlib.util.spec_from_file_location("ordinary_cache_control", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.assertTrue(module.CACHE_SUBSTITUTION)

        def test_direct_normal_and_dynamic_imports_ignore_real_matching_cache_and_preloads(self):
            with tempfile.TemporaryDirectory(prefix="pinned-runtime-cache-") as directory:
                root = Path(directory)
                pins = self.files(root, {
                    "pb00701_fixture_leaf.py": "VALUE = 'trusted original source'\n",
                    "pb00701_fixture_root.py":
                        "from pathlib import Path\nimport importlib.util\n"
                        "import pb00701_fixture_leaf as ordinary\n"
                        "spec=importlib.util.spec_from_file_location('leaf_alias',Path(__file__).with_name('pb00701_fixture_leaf.py'))\n"
                        "dynamic=importlib.util.module_from_spec(spec)\nspec.loader.exec_module(dynamic)\n"
                        "SAME=ordinary is dynamic\nVALUE=ordinary.VALUE\n"})
                for name in pins:
                    self.altered_cache(root/name)
                fake = SimpleNamespace(VALUE="preloaded substitution")
                with patch.dict(sys.modules, {"pb00701_fixture_leaf": fake, "pb00701_fixture_root": fake}):
                    with Runtime(root, pins, {"leaf_alias": "pb00701_fixture_leaf.py"}) as runtime:
                        module = runtime.load("pb00701_fixture_root.py")
                        self.assertEqual(module.VALUE, "trusted original source")
                        self.assertTrue(module.SAME)
                        self.assertFalse(hasattr(module, "CACHE_SUBSTITUTION"))
                        self.assertEqual(len(runtime.loaded_paths), 2)
                    self.assertIs(sys.modules["pb00701_fixture_leaf"], fake)
                    self.assertIs(sys.modules["pb00701_fixture_root"], fake)

        def test_hashed_code_and_all_legacy_read_interfaces_consume_retained_buffers(self):
            with tempfile.TemporaryDirectory(prefix="pinned-runtime-buffer-") as directory:
                root = Path(directory)
                source = ("from pathlib import Path\nimport json\n"
                          "DATA=Path(__file__).with_name('original.json')\n"
                          "def consume():\n"
                          "    with DATA.open('rb') as stream: binary=stream.read()\n"
                          "    with open(DATA,'r',encoding='utf-8') as stream: text=stream.read()\n"
                          "    return (DATA.read_bytes(),DATA.read_text(),binary,text,DATA.is_file(),DATA.stat().st_size)\n")
                raw = b'{"value":1}\n'
                pins = self.files(root, {"pb00701_fixture_reader.py": source, "original.json": raw})
                with Runtime(root, pins) as runtime:
                    first = runtime.read_bytes("original.json")
                    (root/"original.json").write_bytes(b'{"value":2}\n')
                    (root/"pb00701_fixture_reader.py").write_text("raise RuntimeError('replacement source must not run')\n")
                    module = runtime.load("pb00701_fixture_reader.py")
                    self.assertEqual(module.consume(), (raw, raw.decode(), raw, raw.decode(), True, len(raw)))
                    self.assertIs(runtime.read_bytes("original.json"), first)
                    self.assertEqual(runtime.read_json("original.json"), {"value": 1})
                with self.assertRaisesRegex(Refusal, "PINNED_DEPENDENCY_DRIFT"):
                    with Runtime(root, pins):
                        self.fail("changed files were recaptured as original")

        def test_replacement_symlink_cannot_rebind_an_accepted_logical_path(self):
            with tempfile.TemporaryDirectory(prefix="pinned-runtime-symlink-") as directory:
                root = Path(directory)
                pins = self.files(root, {"first.json": '{"value":1}', "second.json": '{"value":2}'})
                with Runtime(root, pins) as runtime:
                    path = runtime.Path(root/"first.json")
                    (root/"first.json").unlink()
                    (root/"first.json").symlink_to(root/"second.json")
                    self.assertEqual(str(path.resolve()), str(root/"first.json"))
                    self.assertEqual(runtime.read_json(path), {"value": 1})
                with self.assertRaisesRegex(Refusal, "SYMLINK_ALIAS"):
                    with Runtime(root, pins):
                        self.fail("initial symlink accepted")

        def test_unlisted_paths_imports_aliases_and_write_modes_refuse(self):
            with tempfile.TemporaryDirectory(prefix="pinned-runtime-denials-") as directory:
                root = Path(directory)
                pins = self.files(root, {"pb00701_one.py": "VALUE=1\n", "pb00701_two.py": "VALUE=2\n",
                                         "data.json": '{"v":1}'})
                with Runtime(root, pins, {"one_alias": "pb00701_one.py"}) as runtime:
                    for call in (lambda: runtime.read_bytes("unlisted.json"),
                                 lambda: runtime.load("unlisted.py"),
                                 lambda: runtime._import("pb00701_unlisted"),
                                 lambda: runtime._import("unlisted_nonstdlib_module"),
                                 lambda: runtime._import("pb00701_one", level=1),
                                 lambda: runtime._spec("unknown_alias", root/"pb00701_one.py"),
                                 lambda: runtime._spec("one_alias", root/"pb00701_two.py"),
                                 lambda: runtime.Path(root/"unlisted.json").stat(),
                                 lambda: runtime.Path(root/"data.json").write_text("bad")):
                        with self.assertRaises(Refusal):
                            call()
                    for mode in ("w", "wb", "a", "r+", "w+", "x", True):
                        with self.assertRaises(Refusal):
                            runtime.open("data.json", mode)
                    with runtime.open("data.json", "rb") as stream:
                        self.assertEqual(stream.read(), b'{"v":1}')
                        self.assertFalse(stream.writable())
                        with self.assertRaises(Refusal):
                            stream.write(b"bad")
                    with runtime.open("data.json", "r") as stream:
                        self.assertEqual(stream.read(), '{"v":1}')
                        self.assertFalse(stream.writable())
                        with self.assertRaises((Refusal, io.UnsupportedOperation)):
                            stream.write("bad")

        def test_private_registration_restores_existing_entries_on_success_and_failure(self):
            for failing in (False, True):
                with self.subTest(failing=failing), tempfile.TemporaryDirectory(prefix="pinned-runtime-cleanup-") as directory:
                    root = Path(directory)
                    source = ("from __future__ import annotations\nfrom dataclasses import dataclass\n"
                              "@dataclass(frozen=True)\nclass Value:\n    data:int\n")
                    if failing:
                        source += "raise RuntimeError('controlled compilation-body failure')\n"
                    pins = self.files(root, {"pb00701_scoped.py": source})
                    runtime = Runtime(root, pins, namespace="_radicadsac_pinned_restore_control")
                    name = runtime.private_name("pb00701_scoped.py")
                    previous = SimpleNamespace(previous=True)
                    with patch.dict(sys.modules, {name: previous}):
                        if failing:
                            with self.assertRaisesRegex(RuntimeError, "controlled"):
                                with runtime:
                                    runtime.load("pb00701_scoped.py")
                        else:
                            with runtime:
                                module = runtime.load("pb00701_scoped.py")
                                self.assertIs(sys.modules[module.Value.__module__], module)
                                self.assertEqual(module.Value(7).data, 7)
                                self.assertIsNot(sys.modules[name], previous)
                        self.assertIs(sys.modules[name], previous)
                    self.assertFalse(runtime.active)
                    self.assertEqual(runtime._registered, {})
                    self.assertEqual(runtime.loading, set())

        def test_dataclass_and_engine_style_aliases_share_constructor_identity(self):
            with tempfile.TemporaryDirectory(prefix="pinned-runtime-identity-") as directory:
                root = Path(directory)
                pins = self.files(root, {"pb00701_field.py":
                    "from __future__ import annotations\nfrom dataclasses import dataclass\n"
                    "@dataclass(frozen=True)\nclass Element:\n    value:int\n"
                    "def accepts(value):return isinstance(value,Element)\n"})
                aliases = {"first_alias": "pb00701_field.py", "second_alias": "pb00701_field.py"}
                with Runtime(root, pins, aliases) as runtime:
                    first = runtime.load("pb00701_field.py")
                    second = runtime.local_importlib.util.module_from_spec(runtime._spec("second_alias", root/"pb00701_field.py"))
                    self.assertIs(first, second)
                    self.assertIs(first.Element, second.Element)
                    self.assertTrue(second.accepts(first.Element(3)))
                    self.assertEqual(first.Element.__annotations__["value"], "int")

        def test_source_future_flags_and_assertions_are_preserved(self):
            with tempfile.TemporaryDirectory(prefix="pinned-runtime-compile-") as directory:
                root = Path(directory)
                pins = self.files(root, {"pb00701_eager.py": "VALUE:int=1\n",
                                         "pb00701_assertion.py": "assert False, 'original assertion retained'\n"})
                with Runtime(root, pins) as runtime:
                    self.assertIs(runtime.load("pb00701_eager.py").__annotations__["VALUE"], int)
                    with self.assertRaisesRegex(AssertionError, "original assertion retained"):
                        runtime.load("pb00701_assertion.py")

        def test_global_import_machinery_and_sys_path_are_untouched(self):
            ordinary_import = builtins.__import__
            factory = importlib.util.spec_from_file_location
            module_cache = sys.modules
            path, values = sys.path, list(sys.path)
            meta_path, meta_values = sys.meta_path, list(sys.meta_path)
            with tempfile.TemporaryDirectory(prefix="pinned-runtime-globals-") as directory:
                root = Path(directory)
                pins = self.files(root, {"pb00701_local_sys.py":
                    "import sys\nimport builtins\nimport importlib.util\n"
                    "sys.path.insert(0,'LOCAL_ONLY_MARKER')\n"
                    "sys.modules['LOCAL_ONLY_MODULE']=object()\n"})
                with Runtime(root, pins) as runtime:
                    module = runtime.load("pb00701_local_sys.py")
                    self.assertEqual(module.sys.path[0], "LOCAL_ONLY_MARKER")
                    self.assertNotIn("LOCAL_ONLY_MODULE", sys.modules)
                self.assertIs(builtins.__import__, ordinary_import)
                self.assertIs(importlib.util.spec_from_file_location, factory)
                self.assertIs(sys.modules, module_cache)
                self.assertIs(sys.path, path)
                self.assertEqual(sys.path, values)
                self.assertIs(sys.meta_path, meta_path)
                self.assertEqual(sys.meta_path, meta_values)

        def test_unreviewed_cycles_refuse_without_partial_registration(self):
            with tempfile.TemporaryDirectory(prefix="pinned-runtime-cycle-") as directory:
                root = Path(directory)
                pins = self.files(root, {"pb00701_cycle_a.py": "import pb00701_cycle_b\n",
                                         "pb00701_cycle_b.py": "import pb00701_cycle_a\n"})
                with Runtime(root, pins) as runtime:
                    with self.assertRaisesRegex(Refusal, "CYCLIC_PROJECT_IMPORT"):
                        runtime.load("pb00701_cycle_a.py")
                    self.assertEqual(runtime.loading, set())
                    self.assertEqual(runtime._registered, {})
                    self.assertEqual(runtime.modules, {})

        def test_snapshot_file_aggregate_manifest_and_pin_budgets_precede_execution(self):
            with tempfile.TemporaryDirectory(prefix="pinned-runtime-bounds-") as directory:
                root = Path(directory)
                pins = self.files(root, {"pb00701_large.py": "raise AssertionError('must not execute')\n"})
                with patch.object(Runtime, "MAX_FILE_BYTES", 8):
                    with self.assertRaisesRegex(Refusal, "FILE_BYTE_BUDGET"):
                        with Runtime(root, pins):
                            self.fail("oversized source accepted")
                with patch.object(Runtime, "MAX_TOTAL_BYTES", 8):
                    with self.assertRaisesRegex(Refusal, "AGGREGATE_BYTE_BUDGET"):
                        with Runtime(root, pins):
                            self.fail("oversized snapshot accepted")
                with self.assertRaisesRegex(Refusal, "DEPENDENCY_DRIFT"):
                    with Runtime(root, {"pb00701_large.py": "0"*40}):
                        self.fail("unverified source accepted")
                for invalid in ({"../escape.py": "0"*40}, {"/absolute.py": "0"*40},
                                {"alias//file.py": "0"*40}, {"module.py": True},
                                {f"module{i}.py": "0"*40 for i in range(Runtime.MAX_FILES+1)}):
                    with self.assertRaises(Refusal):
                        Runtime(root, invalid)

        def test_exact_json_refuses_duplicate_float_nonfinite_large_and_deep_inputs(self):
            bad = ('{"x":1,"x":2}', '{"x":1.0}', '{"x":NaN}', '{"x":1e999999}',
                   '{"x":'+'9'*79+'}', '['*2000+']'*2000)
            with tempfile.TemporaryDirectory(prefix="pinned-runtime-json-") as directory:
                root = Path(directory)
                for text in bad:
                    pins = self.files(root, {"data.json": text})
                    with Runtime(root, pins) as runtime:
                        with self.assertRaises(Refusal):
                            runtime.read_json("data.json")

        def test_attestation_is_deterministic_and_does_not_expose_mutable_snapshot_state(self):
            with tempfile.TemporaryDirectory(prefix="pinned-runtime-attestation-") as directory:
                root = Path(directory)
                pins = self.files(root, {"pb00701_marker.py": "VALUE=1\n", "data.json": '{"v":1}'})
                reports = []
                for suffix in ("first", "second"):
                    with Runtime(root, pins, namespace="_radicadsac_pinned_"+suffix) as runtime:
                        runtime.load("pb00701_marker.py")
                        runtime.read_json("data.json")
                        reports.append(runtime.attestation())
                        changed = runtime.attestation()
                        changed["snapshots"][0]["git_blob"] = "0"*40
                        self.assertNotEqual(changed, runtime.attestation())
                    with self.assertRaisesRegex(Refusal, "NOT_ACTIVE"):
                        runtime.read_bytes("data.json")
                self.assertEqual(reports[0], reports[1])
                self.assertFalse(reports[0]["python_sandbox_claimed"])
                self.assertTrue(reports[0]["standard_library_runtime_trusted"])

    return PinnedRuntimeTests


class ReconciliationV2Tests(unittest.TestCase):
    replay = None
    runtime_module = None

    @classmethod
    def setUpClass(cls):
        # One successful mathematical replay per invocation. All report
        # adversaries use immutable bytes from that replay, never saved PASS.
        if cls.replay is None:
            cls.replay = model.replay_sources()
        cls.expected_bytes = model.bounded_bytes(model.report_from_replay(cls.replay))
        cls.original = cls.replay["indexed"]
        cls.previous = {r["case_id"]: r for r in cls.replay["prior"]["source_cases"]}
        cls.receipts = cls.replay["receipts"]
        cls.views = cls.replay["views"]
        if cls.runtime_module is None:
            cls.runtime_module = model._runtime_module()

    def report(self):
        return json.loads(self.expected_bytes)

    def report_rejects(self, change):
        changed = self.report()
        change(changed)
        with self.assertRaises(model.Refusal):
            model._compare_with_replayed_bytes(changed, self.expected_bytes)

    def registry_rejects(self, change):
        receipts = copy.deepcopy(self.receipts)
        change(receipts)
        with self.assertRaises(model.Refusal):
            model.validate_registry(receipts, self.original, self.replay["prior"])

    def source_row(self, report, cid=None):
        return next(r for r in report["source_cases"] if cid is None or r["case_id"] == cid)

    def test_independent_fifty_source_census_and_fourteen_disjoint_families(self):
        report = self.report()
        original_ids = {cid for cid, row in self.original.items()
                        if row["expected"]["v54_disposition"] in ("BLOCKED", model.ORDER_GAP)}
        self.assertEqual(len(self.original), 121)
        self.assertEqual(len(original_ids), 50)
        self.assertEqual(len(report["source_cases"]), 50)
        self.assertEqual({r["case_id"] for r in report["source_cases"]}, original_ids)
        expected_families = {"five": 5, "continuum": 1, "knot": 1, "trig_fixed": 3,
            "stationary": 2, "v44": 1, "refusal_cone": 1, "v23_bernstein": 1,
            "bernstein_sectors": 3, "component_prefix": 5, "exact_zero_children": 3,
            "multiplier_tails": 5, "ordered_children": 15, "ratio_prefix": 4}
        self.assertEqual(Counter(r["evidence"]["producer"] for r in report["source_cases"]),
                         Counter(expected_families))
        self.assertEqual(set(model.PRODUCERS), set(expected_families))
        self.assertEqual(report["summary"], {
            "total_historical_unresolved_source_cases": 50,
            "by_registered_evidence_level": {model.COMPLETE: 50, model.TAIL: 0, model.CHILD: 0, model.UNREGISTERED: 0},
            "prior_v1_by_registered_evidence_level": {model.COMPLETE: 15, model.TAIL: 9, model.CHILD: 18, model.UNREGISTERED: 8},
            "newly_completed_original_sources": 35,
            "prior_complete_result_digests_preserved": 15,
            "complete_finite_sources": 49, "complete_continuum_sources": 1,
            "historical_route_refusals_with_complete_source_evidence": 20,
            "historical_missing_ordered_premises_with_complete_source_evidence": 30,
            "selected_producer_families": 14,
            "supplemented_executable_closed_endpoint_sources": 2,
        })
        self.assertEqual(Counter(self.original[cid]["expected"]["v54_disposition"] for cid in original_ids),
                         Counter({"BLOCKED": 20, model.ORDER_GAP: 30}))
        self.assertTrue(model.validate_registry(self.receipts, self.original, self.replay["prior"]))

    def test_fifteen_actual_prior_outputs_retain_their_independent_v1_receipts(self):
        selected = [cid for cid, before in self.previous.items()
                    if before["registered_evidence_level"] == model.COMPLETE]
        self.assertEqual(len(selected), 15)
        self.assertEqual(len({self.receipts[cid]["producer"] for cid in selected}), 8)
        for cid in selected:
            expected = self.previous[cid]["evidence"]["replayed_result_sha256"]
            # Independent canonical hashing, not the model's digest helper.
            raw = json.dumps(self.views[cid], sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True, allow_nan=False).encode("ascii")
            self.assertEqual(hashlib.sha256(raw).hexdigest(), expected, cid)
            self.assertEqual(self.receipts[cid]["replayed_result_sha256"], expected, cid)
        self.assertEqual(self.receipts[model.V44_ID]["replayed_result_sha256"],
                         "1a0a97f0723086e52787fddf60298a272139eae814d3c4259a377a76f8cfbe54")
        self.assertTrue(self.views[model.V44_ID]["all_proof_cuts_are_event_neutral"])

    def test_six_new_family_transitions_are_exact_and_do_not_recount_union_metadata(self):
        previous_level = {"component_prefix": model.TAIL, "ratio_prefix": model.TAIL,
                          "ordered_children": model.CHILD, "exact_zero_children": model.CHILD,
                          "bernstein_sectors": model.UNREGISTERED, "multiplier_tails": model.UNREGISTERED}
        additions = set()
        for key, prior in previous_level.items():
            for cid in model.FAMILY_IDS[key]:
                self.assertNotIn(cid, additions)
                additions.add(cid)
                self.assertEqual(self.previous[cid]["registered_evidence_level"], prior)
                actual = model.new_source_receipt(key, self.views[cid], self.original[cid])
                self.assertEqual(model.bounded_bytes(actual), model.bounded_bytes(self.receipts[cid]))
        self.assertEqual(len(additions), 35)
        self.assertEqual(sum(r["producer"] == "five" for r in self.receipts.values()), 5)
        self.assertEqual(sum(r["producer"] == "continuum" for r in self.receipts.values()), 1)
        self.assertTrue(all(self.original[cid]["expected"]["v54_disposition"] != "CERTIFIED"
                            for cid in self.receipts))
        self.assertNotIn("v6_ordered", model.PRODUCERS)
        self.assertFalse(any(p.endswith("verify_pb00701_v6_source_order.py") for p in model.PINS))

    def test_original_source_bytes_provenance_phase_and_piece_edges_are_preserved(self):
        for row in self.report()["source_cases"]:
            original = self.original[row["case_id"]]
            spec = original["spec"]
            for value, field in ((spec, "source_sha256"), (original, "original_row_sha256")):
                raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
                self.assertEqual(row[field], hashlib.sha256(raw).hexdigest())
            edges = {spec["parameter_lo"], spec["parameter_hi"]}
            for channel in ("cos_splines", "sin_splines"):
                for spline in spec[channel].values():
                    edges.update(spline["knots"])
            self.assertEqual(row["original_source_piece_edges"], sorted(edges, key=Q))
            self.assertEqual(row["source_interval"], [spec["parameter_lo"], spec["parameter_hi"]])
            self.assertEqual(row["phase_turn_law"], {"offset": spec["phase_turn_offset"], "rate": spec["phase_turn_rate"]})
            self.assertEqual(row["source_parameter_id"], spec["source_parameter_id"])
            self.assertEqual((row["origin"], row["provenance_kind"]), (original["origin"], original["kind"]))
            self.assertEqual(row["historical_spans"], original["expected"]["observed"]["spans"])

    def test_continuum_stays_typed_and_boundary_and_knot_events_keep_their_semantics(self):
        continuum = self.views[model.CONTINUUM_ID]["zero_set"]
        self.assertEqual(continuum["kind"], "CLOSED_CONTINUUM_ZERO_COMPONENT")
        self.assertIs(continuum["isolated_root_count"], None)
        self.assertIs(continuum["isolated_finite_root_list_applicable"], False)
        self.assertIs(continuum["every_closed_source_point_is_zero"], True)
        self.assertEqual(self.receipts[model.CONTINUUM_ID]["scope"], model.CONTINUUM)
        self.assertNotIn("closed_root_count", self.receipts[model.CONTINUUM_ID])
        v23 = self.views[model.V23_ID]["source_specific_proof"]["physical_event_proof"]
        self.assertEqual((v23["closed_distinct_root_count"], v23["open_distinct_root_count"]), (1, 0))
        self.assertEqual(v23["events"][0]["analytic_order"], 2)
        exact_events = [self.views[cid]["physical_events"][0] for cid in model.FAMILY_IDS["exact_zero_children"]]
        self.assertEqual(Counter(e["kind"] for e in exact_events),
                         Counter({"EXACT_PHYSICAL_SOURCE_KNOT_ZERO": 2, "EXACT_SMOOTH_INTERIOR_ZERO": 1}))
        for event in exact_events:
            if event["kind"] == "EXACT_PHYSICAL_SOURCE_KNOT_ZERO":
                self.assertEqual(event["coordinate"], "1")
                self.assertIs(event["global_smooth_multiplicity_claimed"], False)
                self.assertIs(event["exact_sided_derivatives_unequal"], True)
                self.assertEqual((event["left_one_sided_order"], event["right_one_sided_order"]), (1, 1))

    def test_v27_closed_exteriors_are_derived_from_original_phase_and_endpoint_controls(self):
        self.assertEqual(len(model.V27_IDS), 2)
        for cid in model.V27_IDS:
            row = self.original[cid]
            spec = row["spec"]
            actual = model.v27_closed_endpoint_guard(row)
            endpoints = actual["endpoints"]
            offset, rate = Q(spec["phase_turn_offset"]), Q(spec["phase_turn_rate"])
            self.assertEqual([offset, offset+2*rate], [Q(1, 2), Q(-5, 6)])
            c0 = tuple(Q(spec["cos_splines"]["0"]["controls"][i]) for i in (0, -1))
            c2 = tuple(Q(spec["cos_splines"]["2"]["controls"][i]) for i in (0, -1))
            s1 = tuple(Q(spec["sin_splines"]["1"]["controls"][i]) for i in (0, -1))
            rational = (c0[0]+c2[0], c0[1]-c2[1]/2)
            radical = (Q(0), s1[1]/2)
            self.assertEqual(rational[0], Q(501, 100))
            self.assertEqual(rational[1], Q(20999 if cid.endswith(":tail100") else 999, 200))
            self.assertEqual(radical, (0, 3))
            for i, endpoint in enumerate(endpoints):
                self.assertEqual(endpoint["value"], {"rational": str(rational[i]), "sqrt_3_coefficient": str(radical[i])})
                self.assertGreater(rational[i], 0)
                self.assertEqual(endpoint["sign"], "POSITIVE")
                self.assertIs(endpoint["is_physical_zero"], False)
            self.assertEqual(actual["closed_exterior_root_count"], 0)
            self.assertIs(actual["root_count_copied_from_previous_complete_label"], False)
            self.assertEqual(self.receipts[cid]["supplemental_closed_endpoint_evidence"], actual)

    def test_v27_endpoint_helper_refuses_changed_analytic_premises(self):
        cid = sorted(model.V27_IDS)[0]
        mutations = [
            lambda r: r["spec"].update(parameter_hi="3"),
            lambda r: r["spec"].update(source_parameter_id="another-clock"),
            lambda r: r["spec"].update(phase_turn_offset="0"),
            lambda r: r["spec"].update(phase_turn_rate="2/3"),
            lambda r: r["spec"]["cos_splines"]["0"]["controls"].__setitem__(-1, "0"),
            lambda r: r["spec"]["cos_splines"]["2"]["controls"].__setitem__(-1, "-1/100"),
            lambda r: r["spec"]["sin_splines"]["1"]["controls"].__setitem__(-1, "-6"),
            lambda r: r["spec"]["sin_splines"]["1"].update(degree=True),
            lambda r: r["spec"]["sin_splines"]["1"]["knots"].__setitem__(-1, "3"),
            lambda r: r["spec"]["cos_splines"].__setitem__("4", r["spec"]["cos_splines"].pop("2")),
            lambda r: r.update(id=model.V41_ID),
        ]
        for change in mutations:
            changed = copy.deepcopy(self.original[cid])
            change(changed)
            with self.subTest(change=change), self.assertRaises(model.Refusal):
                model.v27_closed_endpoint_guard(changed)

    def test_endpoint_only_proof_does_not_rebind_a_changed_original_interior(self):
        cid = sorted(model.V27_IDS)[0]
        changed = copy.deepcopy(self.original[cid])
        # This genuine endpoint theorem remains true: interior controls do not
        # alter fully clamped exterior values. Whole-source identity still fails.
        changed["spec"]["sin_splines"]["1"]["controls"][1] = "7"
        closure = model.v27_closed_endpoint_guard(changed)
        self.assertEqual(closure["endpoints"], self.receipts[cid]["supplemental_closed_endpoint_evidence"]["endpoints"])
        self.assertNotEqual(closure["source_sha256"], self.receipts[cid]["source_sha256"])
        altered = dict(self.original)
        altered[cid] = changed
        with self.assertRaises(model.Refusal):
            model.validate_registry(self.receipts, altered, self.replay["prior"])

    def test_complete_entry_rejects_partial_intervals_unregistered_pairs_and_kind_confusion(self):
        cid = model.FAMILY_IDS["component_prefix"][0]
        original, result = self.original[cid], self.views[cid]
        for key, selected, row, interval, kind in (
            ("component_prefix", cid, original, ["1", "2"], model.FINITE),
            ("unknown_family", cid, original, ["0", "2"], model.FINITE),
            ("multiplier_tails", cid, original, ["0", "2"], model.FINITE),
            ("component_prefix", cid, original, ["0", "2"], model.CONTINUUM),
            ("continuum", model.CONTINUUM_ID, self.original[model.CONTINUUM_ID],
             self.receipts[model.CONTINUUM_ID]["source_interval"], model.FINITE),
        ):
            with self.subTest(key=key, kind=kind, interval=interval), self.assertRaises(model.Refusal):
                model.evidence_entry(key, selected, row, result, interval, kind)
        changed = copy.deepcopy(original)
        changed["expected"]["v54_disposition"] = "CERTIFIED"
        with self.assertRaises(model.Refusal):
            model.evidence_entry("component_prefix", cid, changed, result, ["0", "2"], model.FINITE)
        changed = copy.deepcopy(original)
        changed["id"] = model.KNOT_ID
        with self.assertRaises(model.Refusal):
            model.evidence_entry("component_prefix", cid, changed, result, ["0", "2"], model.FINITE)

    def test_new_adapter_requires_actual_source_and_whole_row_identity(self):
        for key in model.NEW_FAMILIES:
            cid = model.FAMILY_IDS[key][0]
            original = self.original[cid]
            baseline = self.views[cid]
            hash_field = "original_source_sha256" if "original_source_sha256" in baseline else "source_sha256"
            id_field = model.NEW_FAMILIES[key][1]
            changes = [lambda v: v.__setitem__(hash_field, "0"*64),
                       lambda v: v.__setitem__("original_row_sha256", "0"*64),
                       lambda v: v.__setitem__(id_field, model.KNOT_ID)]
            if "source_parameter_id" in baseline:
                changes.append(lambda v: v.__setitem__("source_parameter_id", "another-clock"))
            if "source_interval" in baseline:
                changes.append(lambda v: v.__setitem__("source_interval", ["1", "2"]))
            if "phase_turn_law" in baseline:
                changes.append(lambda v: v["phase_turn_law"].__setitem__("rate", "1/100"))
            if "original_source" in baseline:
                changes.append(lambda v: v["original_source"].__setitem__("grammar", "REPLACED_SOURCE"))
            if "historical_observation" in baseline:
                changes.append(lambda v: v["historical_observation"].__setitem__("v54_disposition", "CERTIFIED"))
            for change in changes:
                altered = copy.deepcopy(baseline)
                change(altered)
                with self.subTest(family=key, change=change), self.assertRaises(model.Refusal):
                    model.new_source_receipt(key, altered, original)

    def test_new_adapter_refuses_partial_nontruth_count_aliases_and_continuum_substitution(self):
        for key in model.NEW_FAMILIES:
            cid = model.FAMILY_IDS[key][0]
            baseline = self.views[cid]
            if key == "ordered_children":
                paths = [("complete_original_source_zero_set", False), ("complete_closed_root_count", True),
                         ("complete_closed_zero_set_kind", "CLOSED_CONTINUUM"),
                         ("certificate_partition_cuts_are_not_physical_events", False)]
                target = lambda v: v
            elif key == "exact_zero_children":
                paths = [("complete_original_source_zero_set", False), ("complete_finite_physical_event_count", True),
                         ("historical_disposition_changed", True), ("production_authorized", True)]
                target = lambda v: v
            else:
                paths = [("complete_for_original_closed_source", False), ("closed_distinct_root_count", True),
                         ("continuum_zero_component", True), ("source_interval", ["1", "2"])]
                target = (lambda v: v["source_specific_proof"]["physical_event_proof"]) if key == "bernstein_sectors" else (lambda v: v["physical_event_proof"])
            for field, value in paths:
                changed = copy.deepcopy(baseline)
                target(changed)[field] = value
                with self.subTest(family=key, field=field), self.assertRaises(model.Refusal):
                    model.new_source_receipt(key, changed, self.original[cid])
        cid = model.FAMILY_IDS["bernstein_sectors"][0]
        changed = copy.deepcopy(self.views[cid])
        changed["source_specific_proof"]["phase_turn_law"]["rate"] = "1/100"
        with self.assertRaises(model.Refusal):
            model.new_source_receipt("bernstein_sectors", changed, self.original[cid])

    def test_registry_refuses_omission_overlap_unknown_and_historically_certified_sources(self):
        cid = sorted(self.receipts)[0]
        self.registry_rejects(lambda r: r.pop(cid))
        certified = next(k for k, row in self.original.items() if row["expected"]["v54_disposition"] == "CERTIFIED")
        self.registry_rejects(lambda r: r.__setitem__(certified, copy.deepcopy(r[cid])))
        self.registry_rejects(lambda r: r.__setitem__("invented-source", r.pop(cid)))
        families = copy.deepcopy(model.FAMILY_IDS)
        families["five"].append(families["five"][0])
        with mock.patch.dict(model.FAMILY_IDS, families, clear=True), self.assertRaises(model.Refusal):
            model.validate_registry(self.receipts, self.original, self.replay["prior"])
        families = copy.deepcopy(model.FAMILY_IDS)
        families["five"][0], families["component_prefix"][0] = families["component_prefix"][0], families["five"][0]
        with mock.patch.dict(model.FAMILY_IDS, families, clear=True), self.assertRaises(model.Refusal):
            model.validate_registry(self.receipts, self.original, self.replay["prior"])

    def test_registry_rejects_original_binding_and_complete_source_forgery(self):
        cid = model.FAMILY_IDS["component_prefix"][0]
        changes = [("producer", "ratio_prefix"), ("producer_code", "unregistered.py"),
                   ("producer_git_blob", "0"*40), ("source_sha256", "0"*64),
                   ("original_row_sha256", "0"*64), ("source_parameter_id", "other-clock"),
                   ("source_interval", ["1", "2"]), ("original_source_piece_edges", ["0", "2"]),
                   ("phase_turn_law", {"offset": "0", "rate": "1/100"}),
                   ("level", model.TAIL), ("complete_original_source_zero_set", 1),
                   ("covered_original_source_interval", ["1", "2"]), ("scope", model.CONTINUUM),
                   ("replayed_result_sha256", "g"*64)]
        for field, value in changes:
            with self.subTest(field=field):
                self.registry_rejects(lambda r, field=field, value=value: r[cid].__setitem__(field, value))
        # A genuine old partial-tail receipt cannot become the complete source.
        self.registry_rejects(lambda r: r[cid].update(copy.deepcopy(self.previous[cid]["evidence"])))

    def test_registry_preserves_old_receipts_and_requires_the_new_v27_closures(self):
        cid = model.V44_ID
        self.registry_rejects(lambda r: r[cid].__setitem__("replayed_result_sha256", "0"*64))
        cid = sorted(model.V27_IDS)[0]
        self.registry_rejects(lambda r: r[cid].__setitem__("supplemental_closed_endpoint_evidence", None))
        self.registry_rejects(lambda r: r[cid]["supplemental_closed_endpoint_evidence"]["endpoints"].pop())
        self.registry_rejects(lambda r: r[cid]["supplemental_closed_endpoint_evidence"]["endpoints"][1].__setitem__("is_physical_zero", True))
        self.registry_rejects(lambda r: r[cid]["supplemental_closed_endpoint_evidence"]["endpoints"][1]["value"].__setitem__("sqrt_3_coefficient", "-3"))
        self.registry_rejects(lambda r: r[model.V44_ID].__setitem__("supplemental_closed_endpoint_evidence", copy.deepcopy(r[cid]["supplemental_closed_endpoint_evidence"])))

    def test_prior_registry_cannot_be_rewritten_to_hide_historical_or_source_gaps(self):
        mutations = [lambda p: p["source_cases"].pop(),
                     lambda p: p["source_cases"].append(copy.deepcopy(p["source_cases"][0])),
                     lambda p: p["source_cases"][0].__setitem__("source_sha256", "0"*64),
                     lambda p: p["source_cases"][0].__setitem__("historical_v54_disposition", "CERTIFIED"),
                     lambda p: p["source_cases"][0].__setitem__("historical_observed_source_status", "REFUSED"),
                     lambda p: p["source_cases"][0]["historical_spans"][0].__setitem__(0, "UNREGISTERED_OWNER"),
                     lambda p: p["source_cases"][0].__setitem__("registered_evidence_level", model.UNREGISTERED)]
        for change in mutations:
            prior = copy.deepcopy(self.replay["prior"])
            change(prior)
            with self.subTest(change=change), self.assertRaises(model.Refusal):
                model.validate_registry(self.receipts, self.original, prior)

    def test_report_omissions_duplicates_count_preserving_swaps_and_scope_promotion_refuse(self):
        self.report_rejects(lambda r: r["source_cases"].pop())
        self.report_rejects(lambda r: r["source_cases"].append(copy.deepcopy(r["source_cases"][0])))
        self.report_rejects(lambda r: r["source_cases"].__setitem__(1, copy.deepcopy(r["source_cases"][0])))
        def swap(r):
            a, b = r["source_cases"][:2]
            a["evidence"], b["evidence"] = b["evidence"], a["evidence"]
        self.report_rejects(swap)
        self.report_rejects(lambda r: r["summary"].__setitem__("complete_continuum_sources", 0))
        self.report_rejects(lambda r: self.source_row(r, model.CONTINUUM_ID)["evidence"].__setitem__("scope", model.FINITE))
        self.report_rejects(lambda r: self.source_row(r, model.CONTINUUM_ID)["evidence"].__setitem__("closed_root_count", 0))
        for field in ("all_original_analytic_sources_covered", "generic_owner_routes_repaired",
                      "all_possible_post_v54_proofs_exhaustively_discovered", "new_general_root_event_or_composition_theorem"):
            self.report_rejects(lambda r, field=field: r["registry_scope"].__setitem__(field, True))

    def test_report_code_data_receipt_and_closure_bindings_cannot_be_detached(self):
        self.report_rejects(lambda r: r["producer_registry"][0].__setitem__("code_git_blob", "0"*40))
        self.report_rejects(lambda r: r["producer_registry"][0]["saved_report"].__setitem__("git_blob", "0"*40))
        self.report_rejects(lambda r: r["source_cases"][0]["evidence"].__setitem__("replayed_result_sha256", "0"*64))
        self.report_rejects(lambda r: r["executed_byte_custody"].__setitem__("runtime_git_blob", "0"*40))
        self.report_rejects(lambda r: r["executed_byte_custody"]["snapshot"]["snapshots"][0].__setitem__("git_blob", "0"*40))
        self.report_rejects(lambda r: self.source_row(r, sorted(model.V27_IDS)[0])["evidence"].__setitem__("supplemental_closed_endpoint_evidence", None))

    def test_historical_dispositions_denominators_and_all_gates_remain_unchanged(self):
        report = self.report()
        self.assertEqual(report["gates"], self.replay["prior"]["gates"])
        self.assertEqual(report["historical_v54"], self.replay["prior"]["historical_v54"])
        for field, value in (("PB-007-01", "CLOSED"), ("PB-007-02", "CLOSED"),
                             ("MC-B", "ACCEPTED"), ("MC-1", "ACCEPTED"),
                             ("production_authorized", True), ("native_geometry_or_STEP_qualified", True),
                             ("required_machining_operations", 25)):
            with self.subTest(field=field):
                self.report_rejects(lambda r, field=field, value=value: r["gates"].__setitem__(field, value))
        self.report_rejects(lambda r: r["historical_v54"].__setitem__("route_refusals", 0))
        self.report_rejects(lambda r: r["source_cases"][0].__setitem__("historical_v54_disposition", "CERTIFIED"))

    def test_boolean_integer_aliases_remain_distinct(self):
        for change in (lambda r: r["gates"].__setitem__("production_authorized", 0),
                       lambda r: r["registry_scope"].__setitem__("all_50_have_fresh_complete_source_specific_evidence", 1),
                       lambda r: r["summary"].__setitem__("complete_continuum_sources", True),
                       lambda r: r["source_cases"][0].__setitem__("historical_disposition_changed", 0)):
            self.report_rejects(change)

    def test_public_input_preflight_precedes_any_producer_or_legacy_parser(self):
        cycle = []; cycle.append(cycle)
        deep = None
        for _ in range(40):
            deep = [deep]
        class StringAlias(str):
            pass
        class DictAlias(dict):
            pass
        shared = "a"*8192
        bad = (cycle, deep, "a"*8193, 1<<257, float("nan"), float("inf"), 1.0,
               {"x": object()}, StringAlias("string"), DictAlias(), [shared]*200,
               {"x": [0]*1025}, {1: "non-string-key"})
        with mock.patch.object(model, "expected_report", side_effect=AssertionError("unbounded input reached replay")) as replay, \
             mock.patch.object(model, "_runtime_module", side_effect=AssertionError("unbounded input reached source runtime")) as runtime:
            for candidate in bad:
                with self.subTest(kind=type(candidate).__name__), self.assertRaises(model.Refusal):
                    model.validate_report(candidate)
            replay.assert_not_called()
            runtime.assert_not_called()
        # This bounded exponent is inert caller report text, not a source
        # coefficient. The supplied source parser is never invoked.
        changed = self.report()
        changed["source_cases"][0]["phase_turn_law"]["rate"] = "1e999999999999999999999999999"
        with mock.patch.object(model, "source_metadata", side_effect=AssertionError("report parsed as original source")):
            with self.assertRaises(model.Refusal):
                model._compare_with_replayed_bytes(changed, self.expected_bytes)

    def test_report_reader_rejects_duplicate_nonexact_invalid_and_oversized_data(self):
        with tempfile.TemporaryDirectory(prefix="v2-report-input-") as directory:
            path = Path(directory)/"report.json"
            bad = (b'{"schema":1,"schema":2}', b'{"x":NaN}', b'{"x":1.25}', b'{"x":1e999999}',
                   b'{"x":'+b'9'*5000+b'}', b'\xff', b'['*2000+b']'*2000)
            for raw in bad:
                path.write_bytes(raw)
                with self.subTest(raw=raw[:30]), self.assertRaises(model.Refusal):
                    model.read_report(path)
            with path.open("wb") as stream:
                stream.truncate(model.MAX_BYTES+1)
            with self.assertRaises(model.Refusal):
                model.read_report(path)

    def test_bounded_rational_lexical_and_bit_guards_precede_constructor(self):
        invalid = (True, 1, 0.5, None, "", "1e1000000000", "0.5", "+1", "01",
                   "--1", "1/-2", "1/0", " 1", "1 ", "\uff11", "9"*129,
                   str(1<<256), "1/"+str(1<<256))
        with mock.patch.object(model, "Fraction", side_effect=AssertionError("unsafe Fraction construction")) as constructor:
            for token in invalid:
                with self.subTest(token=str(token)[:30]), self.assertRaises(model.Refusal):
                    model.bounded_rational_token(token)
            constructor.assert_not_called()
        for token in ("0", "1", "-3", "1/2", "-2/3", str((1<<255)-1)):
            self.assertEqual(model.bounded_rational_token(token), Q(token))
        # These short bounded integers are safe to construct; canonicality is
        # checked immediately afterwards, as the documented parser promises.
        for token in ("-0", "2/4", "1/1", "0/2"):
            with self.subTest(noncanonical=token), self.assertRaises(model.Refusal):
                model.bounded_rational_token(token)

    def test_changed_phase_controls_and_source_edges_never_expand_exponent_tokens(self):
        cid = sorted(model.V27_IDS)[0]
        bad = "1e1000000000"
        helpers = [
            (model.v27_closed_endpoint_guard, lambda r: r["spec"].update(phase_turn_offset=bad)),
            (model.v27_closed_endpoint_guard, lambda r: r["spec"].update(phase_turn_rate=bad)),
            (model.v27_closed_endpoint_guard, lambda r: r["spec"]["cos_splines"]["0"]["controls"].__setitem__(0, bad)),
            (model.v27_closed_endpoint_guard, lambda r: r["spec"]["sin_splines"]["1"]["controls"].__setitem__(-1, bad)),
            (model.source_metadata, lambda r: r["spec"].update(parameter_lo=bad)),
            (model.source_metadata, lambda r: r["spec"].update(parameter_hi=bad)),
            (model.source_metadata, lambda r: r["spec"]["cos_splines"]["0"]["knots"].__setitem__(0, bad)),
            (model.source_metadata, lambda r: r["spec"]["sin_splines"]["1"]["knots"].__setitem__(-1, bad)),
        ]
        def bounded_constructor(*operands):
            # Valid earlier tokens may be parsed before the bad field. The
            # constructor must never receive its exponent text or huge value.
            self.assertTrue(all(type(x) is int and x.bit_length() <= 256 for x in operands), operands)
            return Q(*operands)
        for helper, change in helpers:
            changed = copy.deepcopy(self.original[cid])
            change(changed)
            with self.subTest(helper=helper.__name__, change=change), \
                    mock.patch.object(model, "Fraction", side_effect=bounded_constructor):
                with self.assertRaises(model.Refusal):
                    helper(changed)

    def test_direct_source_row_preflight_precedes_any_rational_parser(self):
        cid = sorted(model.V27_IDS)[0]
        changes = [lambda r: r["spec"].update(phase_turn_rate=float("inf")),
                   lambda r: r["spec"].update(phase_turn_rate="x"*8193),
                   lambda r: r["spec"]["sin_splines"]["1"]["controls"].__setitem__(0, 1<<257),
                   lambda r: r.__setitem__("cycle", r)]
        for helper in (model.source_metadata, model.v27_closed_endpoint_guard):
            for change in changes:
                changed = copy.deepcopy(self.original[cid])
                change(changed)
                with self.subTest(helper=helper.__name__, change=change), \
                        mock.patch.object(model, "Fraction", side_effect=AssertionError("unbounded source parsed")) as constructor:
                    with self.assertRaises(model.Refusal):
                        helper(changed)
                    constructor.assert_not_called()

    def test_registered_code_and_saved_report_manifest_disagreement_precedes_runtime(self):
        filenames = (model.PRODUCERS["five"][0], model.SAVED_REPORTS["five"][0])
        for filename in filenames:
            with self.subTest(filename=filename), \
                    mock.patch.dict(model.PINS, {model.TASK_DIR+filename: "0"*40}), \
                    mock.patch.object(model, "_runtime_module", side_effect=AssertionError("unchecked manifest executed")) as runtime:
                with self.assertRaisesRegex(model.Refusal, "MANIFEST_DISAGREEMENT"):
                    model.replay_sources()
                runtime.assert_not_called()

    def test_actual_producer_refusal_aborts_even_with_saved_success_available(self):
        runtime_module = self.runtime_module
        original_load = runtime_module.PinnedRuntime.load
        invoked = []
        def refuse():
            invoked.append(True)
            raise RuntimeError("CONTROLLED_ACTUAL_FIVE_PRODUCER_REFUSAL")
        def load(runtime, path):
            module = original_load(runtime, path)
            if Path(str(path)).name == model.PRODUCERS["five"][0]:
                module.expected_report = refuse
            return module
        with mock.patch.object(model, "_runtime_module", return_value=runtime_module), \
             mock.patch.object(runtime_module.PinnedRuntime, "load", autospec=True, side_effect=load):
            with self.assertRaisesRegex(RuntimeError, "CONTROLLED_ACTUAL_FIVE_PRODUCER_REFUSAL"):
                model.expected_report()
        self.assertEqual(invoked, [True])

    def test_actual_changed_producer_output_cannot_fall_back_to_saved_success(self):
        runtime_module = self.runtime_module
        with runtime_module.PinnedRuntime(model.ROOT, model.PINS, model.ALIASES) as runtime:
            saved = runtime.read_json(model.TASK_DIR+model.SAVED_REPORTS["five"][0])
        changed = copy.deepcopy(saved)
        changed["source_attested_views"][0]["source_sha256"] = "0"*64
        original_load = runtime_module.PinnedRuntime.load
        invoked = []
        def forged():
            invoked.append(True)
            return copy.deepcopy(changed)
        def load(runtime, path):
            module = original_load(runtime, path)
            if Path(str(path)).name == model.PRODUCERS["five"][0]:
                module.expected_report = forged
            return module
        with mock.patch.object(model, "_runtime_module", return_value=runtime_module), \
             mock.patch.object(runtime_module.PinnedRuntime, "load", autospec=True, side_effect=load):
            with self.assertRaisesRegex(model.Refusal, "SAVED_PRODUCER_REPORT_DISAGREES"):
                model.expected_report()
        self.assertEqual(invoked, [True])

    def test_actual_legacy_graph_is_same_buffer_and_fully_triggered_by_workflow(self):
        report = self.report()
        snapshot = report["executed_byte_custody"]["snapshot"]
        self.assertEqual(snapshot["declared_code_paths"], 77)
        self.assertEqual(snapshot["declared_data_paths"], 19)
        self.assertEqual({r["path"]: r["git_blob"] for r in snapshot["snapshots"]}, model.PINS)
        self.assertEqual(len(model.ALIASES), 13)
        self.assertIs(report["executed_byte_custody"]["hostile_python_security_sandbox_claimed"], False)
        self.assertIs(report["executed_byte_custody"]["python_and_standard_library_trusted"], True)
        own = {model.TASK_DIR+name for name in (
            "pb00701_post_v54_evidence_reconciliation_v2.py",
            "verify_pb00701_post_v54_evidence_reconciliation_v2.py",
            "pb00701_pinned_source_runtime.py",
            "pb00701-post-v54-evidence-reconciliation-v2.json",
            "pb00701-post-v54-evidence-reconciliation-v2-research.md")}
        workflow_path = ".github/workflows/mc1-pb00701-post-v54-evidence-reconciliation-v2.yml"
        own.add(workflow_path)
        text = (model.ROOT/workflow_path).read_text()
        before_push, after_push = text.split("  push:", 1)
        def paths(section):
            return set(re.findall(r"^      - ['\"]([^'\"]+)['\"]$", section, re.M))
        self.assertEqual(paths(before_push), set(model.PINS)|own)
        self.assertEqual(paths(after_push), set(model.PINS)|own)
        self.assertEqual(len(paths(before_push)), 102)
        self.assertNotIn("strategy:", text)
        self.assertIn("github.event.pull_request.head.sha || github.sha", text)


def test_suite(replay=None):
    ReconciliationV2Tests.replay = replay
    runtime_module = model._runtime_module()
    ReconciliationV2Tests.runtime_module = runtime_module
    classes = (ReconciliationV2Tests, build_runtime_tests(runtime_module),
               build_bootstrap_tests(MODEL_PATH, MODEL_BLOB))
    loader = unittest.defaultTestLoader
    return unittest.TestSuite(loader.loadTestsFromTestCase(cls) for cls in classes)


def load_tests(loader, tests, pattern):
    # Supports ordinary unittest module loading with the same fresh-replay rule.
    return test_suite()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    options = parser.parse_args()
    if not (options.contract or options.self_test):
        parser.error("choose --contract and/or --self-test")
    replay = model.replay_sources()
    expected_bytes = model.bounded_bytes(model.report_from_replay(replay))
    if options.contract:
        model._compare_with_replayed_bytes(model.read_report(), expected_bytes)
        print("PASS: all 50 original sources have freshly replayed complete witnesses; finite49 / continuum1")
        print("PASS: eight prior families preserve15 receipts; six new families complete35 sources")
        print("PASS: two original V27 exterior closures proved; historical121/20/30 and all gates unchanged")
    if options.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(test_suite(replay))
        if not result.wasSuccessful():
            raise SystemExit(1)


if __name__ == "__main__":
    main()
