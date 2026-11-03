#!/usr/bin/env python3
"""Adversarial verification of five exact original prefix/tail compositions."""
from __future__ import annotations

import argparse
import builtins
import copy
from fractions import Fraction as Q
import hashlib
import importlib.util
import os
from pathlib import Path
import py_compile
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODEL_BLOB = "530e552bb41c020456fdf0f17506cb18577896f3"
MAX_MODEL_BYTES = 1048576


def _load_verified_model(path, expected):
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_MODEL_BYTES + 1)
    if len(raw) > MAX_MODEL_BYTES:
        raise ValueError("RESOURCE_REFUSAL: model source byte budget")
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    if actual != expected:
        raise ValueError("VERIFIER_MODEL_SOURCE_DRIFT")
    module = ModuleType("component_prefix_verified_model")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


model = _load_verified_model(HERE / "pb00701_component_prefix_composition.py", MODEL_BLOB)


def contract():
    report = model.read_report()
    model.validate_report(report)
    if report["summary"]["complete_original_source_witnesses"] != 5:
        raise AssertionError("five-source result missing")
    if list(report["summary"]["by_case_closed_root_count"].values()) != [2, 3, 2, 3, 2]:
        raise AssertionError("original complete root counts changed")
    return report


class TestComponentPrefix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = model.original_rows()
        cls.report = model.expected_report()
        cls.ids = sorted(cls.rows)
        cls.proofs = {row["source_case_id"]: row for row in cls.report["source_cases"]}
        cls.receipts = model._tail_receipts()

    def reject(self, function, *args):
        with self.assertRaises(model.Refusal):
            function(*args)

    def test_complete_original_sources_and_actual_endpoints(self):
        expected = [(2, ["-1/3", "-1/3", "-2/3"]),
                    (3, ["-1/3", "-1/3", "298/3"]),
                    (2, ["-1", "-1/3", "-2"]),
                    (3, ["-11/3", "-409/3", "278/3"]),
                    (2, ["2/3", "2/3", "4/3"])]
        for cid, (count, values) in zip(self.ids, expected):
            proof = self.proofs[cid]
            physical = proof["physical_event_proof"]
            self.assertEqual(physical["closed_distinct_root_count"], count)
            self.assertEqual(proof["prefix_proof"]["endpoint_values"] +
                             proof["tail_proof"]["endpoint_values"][1:], values)
            self.assertEqual(physical["source_interval"], ["0", "2"])
            self.assertTrue(physical["complete_for_original_closed_source"])
            self.assertEqual(physical["exterior_root_count"], 0)
            self.assertEqual(physical["source_knot_root_count"], 0)

    def test_carrier_symmetry_strict_brackets_and_simple_roots(self):
        lemma = model.carrier_prefix_proof()
        self.assertEqual(lemma["root_brackets"], [["1/6", "1/4"], ["3/4", "5/6"]])
        self.assertEqual(lemma["strict_derivative_lower_bound"],
                         {"interval": ["0", "1/3"], "bound": "1/3"})
        self.assertEqual(lemma["root_multiplicities"], [1, 1])
        self.assertFalse(lemma["original_source_binding_supplied_by_this_lemma"])
        lemma["root_brackets"][0][0] = "0"
        self.assertEqual(model.carrier_prefix_proof()["root_brackets"][0][0], "1/6")

    def test_every_original_harmonic_participates_in_factor_identity(self):
        # Bypass the frozen hash deliberately to exercise the mathematical
        # coefficient checker itself, not just source-custody rejection.
        for cid, row in self.rows.items():
            family = model.CASES[cid]["family"]
            for channel in ("cos_splines", "sin_splines"):
                for harmonic in row["spec"][channel]:
                    if harmonic == "0":
                        continue
                    changed = copy.deepcopy(row["spec"])
                    controls = changed[channel][harmonic]["controls"]
                    controls[0] = str(Q(controls[0]) + Q(1, 120))
                    pieces, _ = model._lower_source(changed)
                    self.reject(model._factor_identity, pieces, family)

    def test_added_omitted_harmonics_and_bias_refuse(self):
        row = self.rows[self.ids[2]]
        for kind in ("omit", "add", "bias"):
            spec = copy.deepcopy(row["spec"])
            if kind == "omit":
                del spec["sin_splines"]["3"]
            elif kind == "add":
                spec["cos_splines"]["5"] = {"degree": 0, "knots": ["0", "1", "2"], "controls": ["0", "0"]}
            else:
                spec["cos_splines"]["0"]["controls"] = ["1", "1"]
            pieces, _ = model._lower_source(spec)
            self.reject(model._factor_identity, pieces, "V13")

    def test_chebyshev_identity_and_positive_bound(self):
        factor = self.proofs[self.ids[3]]["prefix_proof"]["factor_reconstruction"]
        self.assertEqual(factor["nonvanishing_proof"]["P_1_minus_w"], ["11", "-18", "448", "-32"])
        self.assertEqual(factor["nonvanishing_proof"]["value"], "4495/416")
        self.assertEqual(Q(11)-Q(18)**2/(4*Q(416)), Q(4495, 416))
        broken = copy.deepcopy(self.rows[self.ids[3]]["spec"])
        broken["cos_splines"]["7"]["controls"][0] = "1/6"
        pieces, _ = model._lower_source(broken)
        self.reject(model._factor_identity, pieces, "V16")

    def test_v17_negative_factor_reverses_physical_signs(self):
        cid = self.ids[4]
        proof = self.proofs[cid]
        factor = proof["prefix_proof"]["factor_reconstruction"]
        self.assertEqual(factor["multiplier_sign"], "NEGATIVE")
        self.assertEqual(factor["nonvanishing_proof"]["range"], ["-2", "-1"])
        self.assertEqual(proof["physical_event_proof"]["maximal_source_sign_cells"], ["POSITIVE", "NEGATIVE", "POSITIVE"])
        pieces, _ = model._lower_source(self.rows[cid]["spec"])
        self.reject(model._factor_identity, pieces, "V13")
        forged = copy.deepcopy(factor)
        forged["multiplier_sign"] = "POSITIVE"
        with patch.object(model, "_factor_identity", return_value=forged):
            self.reject(model._source_proof, self.rows[cid], self.receipts[cid])

    def test_original_phase_parameter_knots_and_continuity(self):
        base = self.rows[self.ids[0]]["spec"]
        mutations = [
            lambda s: s.__setitem__("phase_turn_offset", "1/4"),
            lambda s: s.__setitem__("phase_turn_rate", "-1/4"),
            lambda s: s.__setitem__("parameter_hi", "3"),
            lambda s: s.__setitem__("source_parameter_id", "normalized-u"),
            lambda s: s["cos_splines"]["1"]["knots"].__setitem__(3, "3/2"),
            lambda s: s["cos_splines"]["1"]["controls"].__setitem__(2, "1"),
            lambda s: s["cos_splines"]["1"].__setitem__("degree", True),
            lambda s: s["sin_splines"].__setitem__("2", s["sin_splines"].pop("1")),
        ]
        for mutation in mutations:
            source = copy.deepcopy(base)
            mutation(source)
            self.reject(model._lower_source, source)

    def test_frozen_source_changes_refuse_before_legacy_execution(self):
        cid = self.ids[0]
        for mutation in (
            lambda r: r.__setitem__("origin", "forged"),
            lambda r: r.__setitem__("id", self.ids[1]),
            lambda r: r["spec"]["cos_splines"]["1"]["controls"].__setitem__(0, "1e1000000000"),
            lambda r: r["expected"]["observed"]["spans"][0].__setitem__(0, "FORGED_OWNER"),
            lambda r: r["expected"]["observed"]["spans"][1].__setitem__(1, "CERTIFIED"),
            lambda r: r["spec"]["cos_splines"]["1"].__setitem__("degree", True),
        ):
            row = copy.deepcopy(self.rows[cid])
            mutation(row)
            with patch.object(model, "_tail_receipts", side_effect=AssertionError("legacy execution reached")) as replay:
                self.reject(model.source_proof, row)
                replay.assert_not_called()

    def test_public_source_proof_replays_actual_frozen_source(self):
        for cid in self.ids:
            self.assertEqual(model.bounded_bytes(model.source_proof(self.rows[cid])), model.bounded_bytes(self.proofs[cid]))

    def test_same_prefix_different_sources_remain_distinct(self):
        left, right = [self.proofs[cid] for cid in self.ids[:2]]
        self.assertEqual(left["prefix_proof"]["carrier_lemma_sha256"], right["prefix_proof"]["carrier_lemma_sha256"])
        self.assertNotEqual(left["original_source_sha256"], right["original_source_sha256"])
        self.assertNotEqual(left["physical_event_proof"]["closed_distinct_root_count"],
                            right["physical_event_proof"]["closed_distinct_root_count"])
        self.reject(model._join_views, left["prefix_proof"], right["tail_proof"], Q(-1, 3))

    def test_nonzero_knot_merges_sign_cells_without_event(self):
        physical = self.proofs[self.ids[1]]["physical_event_proof"]
        self.assertEqual(physical["maximal_source_sign_cells"], ["NEGATIVE", "POSITIVE", "NEGATIVE", "POSITIVE"])
        self.assertTrue(physical["source_knot"]["adjacent_equal_sign_cells_merged"])
        self.assertFalse(physical["source_knot"]["is_physical_event"])
        self.assertEqual([e["source_piece_index"] for e in physical["events"]], [0, 0, 1])
        for event in physical["events"]:
            self.assertNotEqual(event["strict_source_bracket"], ["1", "1"])
            self.assertEqual(type(event["multiplicity"]), int)
        proof = self.proofs[self.ids[1]]
        self.reject(model._join_views, proof["prefix_proof"], proof["tail_proof"], Q(0))

    def test_proof_cut_cannot_be_inserted_as_physical_root(self):
        proof = self.proofs[self.ids[0]]
        prefix = copy.deepcopy(proof["prefix_proof"])
        prefix["root_brackets"].insert(1, ["1/3", "1/3"])
        prefix["root_multiplicities"].insert(1, 1)
        prefix["maximal_sign_cells"] = ["NEGATIVE", "POSITIVE", "NEGATIVE", "NEGATIVE"]
        self.reject(model._join_views, prefix, proof["tail_proof"], Q(-1, 3))

    def test_composition_rejects_interval_order_point_and_multiplicity_forgery(self):
        proof = self.proofs[self.ids[1]]
        mutations = [
            lambda p, t: p.__setitem__("source_interval", ["0", "2"]),
            lambda p, t: t.__setitem__("source_interval", ["0", "1"]),
            lambda p, t: p["root_brackets"].reverse(),
            lambda p, t: p["root_brackets"].__setitem__(0, ["0", "0"]),
            lambda p, t: t["root_brackets"].__setitem__(0, ["1/2", "3/4"]),
            lambda p, t: p["endpoint_values"].__setitem__(1, "1/3"),
            lambda p, t: t["maximal_sign_cells"].__setitem__(0, "POSITIVE"),
            lambda p, t: p["root_multiplicities"].__setitem__(0, True),
            lambda p, t: p.__setitem__("source_piece_index", False),
            lambda p, t: p["root_multiplicities"].pop(),
        ]
        for mutation in mutations:
            prefix, tail = copy.deepcopy(proof["prefix_proof"]), copy.deepcopy(proof["tail_proof"])
            mutation(prefix, tail)
            self.reject(model._join_views, prefix, tail, Q(-1, 3))

    def test_tail_receipt_cannot_omit_or_invent_events(self):
        for cid, key in ((self.ids[1], "open_physical_root_count"), (self.ids[3], "exact_distinct_open_roots")):
            changed = copy.deepcopy(self.receipts[cid])
            changed[key] = 0
            self.reject(model._tail_view, cid, changed)
        self.reject(model._tail_view, self.ids[0], self.receipts[self.ids[1]])

    def test_four_tail_producers_reexecute_and_failure_aborts(self):
        real = model._module
        with patch.object(model, "_module", wraps=real) as loader:
            replayed = model._tail_receipts()
        self.assertEqual(set(replayed), set(self.ids))
        self.assertEqual([c.args[0] for c in loader.call_args_list], [v[0] for v in model.PRODUCERS.values()])
        with patch.object(model, "_module", return_value=SimpleNamespace(contract=lambda: (_ for _ in ()).throw(model.Refusal("producer refused")))):
            self.reject(model._tail_receipts)
        changed = copy.deepcopy(self.receipts[self.ids[0]])
        changed["open_physical_root_count"] = 1
        fake = {"v12_v43_tail_reports": [changed, self.receipts[self.ids[1]]]}
        with patch.object(model, "_module", return_value=SimpleNamespace(contract=lambda: fake)):
            self.reject(model._tail_receipts)

    def test_dependency_drift_refuses_before_loading_legacy_code(self):
        filename, _ = model.PRODUCERS["V12"]
        with patch.dict(model.PRODUCERS, {"V12": (filename, "0" * 40)}), \
                patch.object(model, "_module", side_effect=AssertionError("untrusted dependency loaded")) as loader:
            self.reject(model.expected_report)
            loader.assert_not_called()

    def test_cached_bytecode_cannot_replace_the_pinned_module(self):
        with tempfile.TemporaryDirectory(prefix="radicadsac-prefix-cache-") as directory:
            here = Path(directory)
            original, alternate = here / "probe.py", here / "alternate.py"
            original.write_text("VALUE = 'trusted'\n", encoding="utf-8")
            alternate.write_text("VALUE = 'altered'\n", encoding="utf-8")
            for path in (original, alternate):
                os.utime(path, (1700000000, 1700000000))
            self.assertEqual(original.stat().st_size, alternate.stat().st_size)
            cache = Path(importlib.util.cache_from_source(str(original)))
            cache.parent.mkdir()
            py_compile.compile(str(alternate), cfile=str(cache), doraise=True)
            # This is a real accepted timestamp/size cache, not a mocked loader.
            spec = importlib.util.spec_from_file_location("untrusted_cache_control", original)
            cached = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cached)
            self.assertEqual(cached.VALUE, "altered")
            expected = model.git_blob(original)
            with patch.object(model, "HERE", here):
                checked = model._module("probe.py", expected)
            self.assertEqual(checked.VALUE, "trusted")
            self.assertEqual(model.git_blob(original), expected)

    def test_verifier_model_bootstrap_ignores_real_cache_and_preloaded_module(self):
        with tempfile.TemporaryDirectory(prefix="radicadsac-prefix-bootstrap-") as directory:
            here = Path(directory)
            original, alternate = here / "probe.py", here / "alternate.py"
            original.write_text("VALUE = 'trusted'\n", encoding="utf-8")
            alternate.write_text("VALUE = 'altered'\n", encoding="utf-8")
            for path in (original, alternate):
                os.utime(path, (1700000000, 1700000000))
            cache = Path(importlib.util.cache_from_source(str(original)))
            cache.parent.mkdir()
            py_compile.compile(str(alternate), cfile=str(cache), doraise=True)
            spec = importlib.util.spec_from_file_location("bootstrap_cache_control", original)
            cached = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cached)
            self.assertEqual(cached.VALUE, "altered")
            poisoned = ModuleType("component_prefix_verified_model")
            poisoned.VALUE = "preloaded"
            with patch.dict(sys.modules, {poisoned.__name__: poisoned}):
                checked = _load_verified_model(original, model.git_blob(original))
                self.assertEqual(checked.VALUE, "trusted")
                self.assertIs(sys.modules[poisoned.__name__], poisoned)

    def test_verifier_model_drift_and_oversize_refuse_before_compilation(self):
        with tempfile.TemporaryDirectory(prefix="radicadsac-prefix-bootstrap-guard-") as directory:
            path = Path(directory) / "probe.py"
            path.write_bytes(b"raise AssertionError('must not execute')\n")
            expected = model.git_blob(path)
            with patch("builtins.compile", side_effect=AssertionError("unverified source compiled")) as compiler:
                with self.assertRaisesRegex(ValueError, "VERIFIER_MODEL_SOURCE_DRIFT"):
                    _load_verified_model(path, "0" * 40)
                with patch.dict(globals(), MAX_MODEL_BYTES=2):
                    with self.assertRaisesRegex(ValueError, "RESOURCE_REFUSAL"):
                        _load_verified_model(path, expected)
                compiler.assert_not_called()

    def test_transitive_lowerer_uses_pinned_bytes_without_global_import_changes(self):
        with tempfile.TemporaryDirectory(prefix="radicadsac-prefix-lowerer-") as directory:
            here = Path(directory)
            filename = "verify_pb00701_v43_refusal_cone.py"
            original, alternate = here / filename, here / "alternate.py"
            original.write_text("VALUE = 'trusted'\n", encoding="utf-8")
            alternate.write_text("VALUE = 'altered'\n", encoding="utf-8")
            for path in (original, alternate):
                os.utime(path, (1700000000, 1700000000))
            cache = Path(importlib.util.cache_from_source(str(original)))
            cache.parent.mkdir()
            py_compile.compile(str(alternate), cfile=str(cache), doraise=True)
            producer = here / "producer.py"
            producer.write_text(
                "import importlib.util\nfrom pathlib import Path\n"
                "spec = importlib.util.spec_from_file_location('checked_lowerer', "
                "Path(__file__).with_name('verify_pb00701_v43_refusal_cone.py'))\n"
                "LOWERER = importlib.util.module_from_spec(spec)\n"
                "spec.loader.exec_module(LOWERER)\nVALUE = LOWERER.VALUE\n", encoding="utf-8")
            importer = builtins.__import__
            factory = importlib.util.spec_from_file_location
            with patch.object(model, "HERE", here), patch.dict(model.PINS, {filename: model.git_blob(original)}):
                checked = model._module("producer.py", model.git_blob(producer))
                self.assertEqual(checked.VALUE, "trusted")
                self.reject(model._verified_lowerer_spec, "other", here / "alternate.py")
            self.assertIs(builtins.__import__, importer)
            self.assertIs(importlib.util.spec_from_file_location, factory)

    def test_pinned_json_decodes_the_verified_buffer_after_path_replacement(self):
        with tempfile.TemporaryDirectory(prefix="radicadsac-prefix-json-") as directory:
            path = Path(directory) / "original.json"
            path.write_bytes(b'{"value":1}\n')
            expected = model.git_blob(path)
            decode = model._decode_json

            def replace_after_hash(raw):
                path.write_bytes(b'{"value":2}\n')
                return decode(raw)

            with patch.object(model, "_decode_json", side_effect=replace_after_hash):
                self.assertEqual(model._pinned_json(path, expected), {"value": 1})
            self.reject(model._pinned_json, path, expected)

    def test_legacy_json_adapter_requires_an_exact_pinned_path(self):
        with tempfile.TemporaryDirectory(prefix="radicadsac-prefix-input-") as directory:
            path = Path(directory) / "unlisted.json"
            path.write_bytes(b'{}\n')
            with patch.object(model, "_pinned_json", side_effect=AssertionError("unlisted file parsed")) as parser:
                self.reject(model._dependency_json, path)
                parser.assert_not_called()
        for family, (filename, expected) in model.PRODUCERS.items():
            producer = model._module(filename, expected)
            producer.load_json = model._dependency_json
            producer.blob_sha = model._dependency_blob
            with patch.object(model, "_pinned_json", side_effect=model.Refusal("controlled read failure")):
                self.reject(producer.contract)

    def test_noncanonical_rationals_never_reach_fraction_constructor(self):
        tokens = ["1e1000000000", "1.0", "+1", "01", "-0", "1/1", "2/2", "0/2", "1/0", "١", "9" * 78, "1/" + "9" * 79]
        for token in tokens:
            with patch.object(model, "Q", side_effect=AssertionError("Fraction construction reached")) as constructor:
                self.reject(model.exact, token)
                constructor.assert_not_called()
        self.assertEqual(model.exact("-3/7"), Q(-3, 7))
        self.assertEqual(model.exact("0"), Q(0))

    def test_resource_and_nonexact_inputs_refuse_before_replay(self):
        cycle = []
        cycle.append(cycle)
        deep = None
        for _ in range(model.MAX_DEPTH + 2):
            deep = [deep]
        class CustomList(list):
            pass
        bad = [cycle, deep, 1 << 300, 0.5, float("inf"), {1: "key"},
               "x" * (model.MAX_STRING + 1), ["x" * model.MAX_STRING] * 200, CustomList([1])]
        for value in bad:
            with patch.object(model, "expected_report", side_effect=AssertionError("replay reached")) as replay:
                self.reject(model.validate_report, value)
                replay.assert_not_called()

    def test_duplicate_keys_and_numeric_json_resource_controls(self):
        samples = [b'{"x":1,"x":2}', b'{"x":1.0}', b'{"x":NaN}',
                   ('{"x":' + '9' * 300 + '}').encode(), b'[' * 1200 + b']' * 1200,
                   b' ' * (model.MAX_BYTES + 1)]
        with tempfile.TemporaryDirectory(prefix="radicadsac-prefix-test-") as directory:
            path = Path(directory) / "candidate.json"
            for data in samples:
                path.write_bytes(data)
                self.reject(model.read_report, path)

    def test_report_boolean_integer_aliases_and_authority_forgery(self):
        mutations = [
            lambda r: r["source_cases"][0]["physical_event_proof"]["events"][0].__setitem__("multiplicity", True),
            lambda r: r["source_cases"][0]["physical_event_proof"].__setitem__("closed_distinct_root_count", 1),
            lambda r: r["source_cases"][0]["physical_event_proof"].__setitem__("source_knot_root_count", 1),
            lambda r: r["source_cases"][0].__setitem__("original_source_sha256", "0" * 64),
            lambda r: r["source_cases"][0]["prefix_proof"]["root_brackets"][0].__setitem__(0, "0"),
            lambda r: r["historical_v54"].__setitem__("route_refusals", 15),
            lambda r: r["gates"].__setitem__("production_authorized", 0),
            lambda r: r["gates"].__setitem__("MC-B", "ACCEPTED"),
            lambda r: r["source_cases"][0].__setitem__("general_v43_route_or_universal_proof_consumer_established", True),
        ]
        for mutation in mutations:
            report = copy.deepcopy(self.report)
            mutation(report)
            self.reject(model.validate_report, report)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.contract:
        contract()
        print("PASS: five original whole-source proofs, exact factor identities, fresh pinned tail replay and frozen scope")
    if args.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(TestComponentPrefix))
        if not result.wasSuccessful():
            raise SystemExit(1)
    if not args.contract and not args.self_test:
        parser.error("select --contract and/or --self-test")


if __name__ == "__main__":
    main()
