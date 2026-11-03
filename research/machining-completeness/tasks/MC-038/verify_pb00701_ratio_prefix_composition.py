#!/usr/bin/env python3
"""Verify four full original ratio sources and falsify missing chart premises."""
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
MODEL_PATH = HERE / "pb00701_ratio_prefix_composition.py"
MODEL_BLOB = "bdb72a2f5426ed792d2f9f1ed783187be5f7ada3"
MODEL_BYTE_LIMIT = 1048576


class BootstrapRefusal(ValueError):
    pass


def _compile_model(raw, path):
    module = ModuleType("ratio_prefix_verified_source")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


def load_verified_model(path=MODEL_PATH):
    """No ordinary import, cached bytecode or preloaded module is authority."""
    try:
        with Path(path).open("rb") as stream:
            raw = stream.read(MODEL_BYTE_LIMIT + 1)
    except OSError as exc:
        raise BootstrapRefusal("model source unavailable") from exc
    if len(raw) > MODEL_BYTE_LIMIT:
        raise BootstrapRefusal("model source byte budget")
    actual = hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()
    if actual != MODEL_BLOB:
        raise BootstrapRefusal("model source Git blob drift")
    return _compile_model(raw, path)


model = load_verified_model()


def spline(first, second=None):
    second = [first[-1]]*len(first) if second is None else second
    assert len(first) == len(second)
    width = len(first)
    return {"degree": width-1, "knots": ["0"]*width+["1"]*width+["2"]*width,
            "controls": [str(x) for x in first+second]}


def fixture(owner, amplitude):
    cosine = [Q(1)] if owner == model.V10 else amplitude
    sine = amplitude if owner == model.V10 else [Q(1)]
    return {"grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
            "source_parameter_id": "synthetic-chart-control", "parameter_lo": "0", "parameter_hi": "2",
            "phase_turn_offset": "-1/2" if owner == model.V10 else "0", "phase_turn_rate": "2",
            "cos_splines": {"0": spline([Q(0)]), "1": spline(cosine)},
            "sin_splines": {"1": spline(sine)}}


def contract():
    report = model.read_report()
    model.validate_report(report)
    assert list(report["summary"]["by_case_closed_root_count"].values()) == [8, 5, 8, 4]
    return report


class RatioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = model.original_rows()
        cls.report = model.expected_report()
        cls.ids = sorted(cls.rows)
        cls.proofs = {p["source_case_id"]: p for p in cls.report["source_cases"]}
        cls.receipts = model._tail_receipts()

    def reject(self, function, *args):
        with self.assertRaises(model.Refusal):
            function(*args)

    def bad_report(self, mutate):
        candidate = copy.deepcopy(self.report)
        mutate(candidate)
        self.reject(model.validate_report, candidate)

    def test_four_complete_sources_actual_endpoints_and_signs(self):
        for cid, count, values, initial in zip(self.ids, (8, 5, 8, 4),
                (("-1", "-1", "-1"), ("-1", "-1", "99"),
                 ("1/8", "1/8", "1/8"), ("1/8", "1/8", "801/8")),
                ("NEGATIVE", "NEGATIVE", "POSITIVE", "POSITIVE")):
            proof = self.proofs[cid]
            physical = proof["physical_event_proof"]
            self.assertEqual(physical["closed_distinct_root_count"], count)
            self.assertEqual(physical["open_distinct_root_count"], count)
            self.assertEqual(proof["prefix_proof"]["endpoint_values"]+
                             proof["tail_proof"]["endpoint_values"][1:], list(values))
            signs = [initial]
            for _ in range(count):
                signs.append(model._opposite(signs[-1]))
            self.assertEqual([cell["sign"] for cell in physical["maximal_sign_cells"]], signs)
            self.assertTrue(physical["complete_for_original_closed_source"])
            self.assertFalse(physical["continuum_zero_component"])
            self.assertFalse(physical["original_source_knot"]["is_zero_event"])
            self.assertTrue(all(not end["is_zero_event"] for end in physical["exterior_endpoints"]))
        self.assertTrue(model.validate_report(model.read_report()))

    def test_original_prefix_identities_brackets_and_strict_derivatives(self):
        for cid in self.ids:
            prefix = self.proofs[cid]["prefix_proof"]
            if model.CASES[cid]["owner"] == model.V10:
                self.assertEqual(prefix["original_prefix_power_coefficients"]["C1"], ["1"])
                self.assertEqual(prefix["original_prefix_power_coefficients"]["S1"], ["1/2", "-1"])
                self.assertEqual(prefix["original_amplitude_derivative_controls"], ["-1"])
                self.assertEqual(prefix["strict_ratio_derivative_bound"]["value"], "-13")
                self.assertEqual(prefix["root_brackets"], [["1/8", "1/4"], ["3/8", "1/2"],
                                                          ["1/2", "5/8"], ["3/4", "7/8"]])
                self.assertEqual([chart["root_count"] for chart in prefix["charts"]], [1]*4)
            else:
                self.assertEqual(prefix["original_prefix_power_coefficients"]["C1"], ["1/8", "-1", "1"])
                self.assertEqual(prefix["original_prefix_power_coefficients"]["S1"], ["1"])
                self.assertEqual(prefix["original_amplitude_derivative_controls"], ["-1", "1"])
                self.assertEqual(prefix["strict_ratio_derivative_bound"]["value"], "11")
                self.assertEqual(prefix["root_brackets"], [["1/4", "3/8"], ["1/2", "5/8"],
                                                          ["3/4", "7/8"], ["7/8", "1"]])
                self.assertEqual([chart["root_count"] for chart in prefix["charts"]], [0, 1, 1, 1, 1])
            self.assertEqual(prefix["root_multiplicities"], [1]*4)
            self.assertTrue(prefix["strict_ratio_derivative_bound"]["strict"])

    def test_cotangent_conditional_lemma_accepts_other_original_amplitudes(self):
        source = fixture(model.V10, [Q(1), Q(12)])
        proof = model.cotangent_prefix_proof(source)
        self.assertEqual(proof["original_amplitude_derivative_controls"], ["11"])
        self.assertEqual(proof["strict_ratio_derivative_bound"]["value"], "-1")
        self.assertEqual(len(proof["root_brackets"]), 4)
        changed = copy.deepcopy(self.rows[self.ids[0]])
        changed["spec"] = source
        self.reject(model.check_original, changed)

    def test_tangent_conditional_lemma_and_strict_pi_boundary_are_not_answer_tables(self):
        source = fixture(model.V11, [Q(1, 8)])
        proof = model.tangent_prefix_proof(source)
        self.assertEqual(proof["root_brackets"], [["1/8", "1/4"], ["3/8", "1/2"],
                                                 ["5/8", "3/4"], ["7/8", "1"]])
        boundary = model.tangent_prefix_proof(fixture(model.V11, [Q(20), Q(8)]))
        self.assertEqual(boundary["strict_ratio_derivative_bound"]["value"], "0")
        self.assertTrue(boundary["strict_ratio_derivative_bound"]["strict"])
        self.assertEqual(len(boundary["root_brackets"]), 4)

    def test_nonmonotone_cotangent_has_three_roots_in_one_chart_and_refuses(self):
        # B=20(t-1/8). H(1/8)=0 and H'(1/8)=20-4*pi>0.
        # Together with H(0+)=+infinity and H(1/4-)=-infinity, this
        # forces an additional root on each side of the middle root.
        source = fixture(model.V10, [Q(-5, 2), Q(35, 2)])
        self.assertEqual(model._evaluate([Q(-5, 2), Q(35, 2)], Q(1, 8)), 0)
        self.assertGreater(Q(20)-4*Q(22, 7), 0)
        # Independent exact signs: cot(-3*pi/4)=1, cot(-pi/4)=-1.
        self.assertEqual(1+20*(Q(1, 16)-Q(1, 8)), -Q(1, 4))
        self.assertEqual(-1+20*(Q(3, 16)-Q(1, 8)), Q(1, 4))
        with self.assertRaisesRegex(model.Refusal, "STRICT_DECREASING_COTANGENT"):
            model.cotangent_prefix_proof(source)

    def test_nonmonotone_tangent_has_three_roots_despite_positive_endpoints(self):
        # A=40(t-1/2)^2-5/2. A(0)=A(1)=15/2>0, H(1/4)=0,
        # H'(1/4)=-20+4*pi<0, but the surrounding full tangent chart
        # goes from -infinity to +infinity. At least three roots result.
        controls = [Q(15, 2), Q(-25, 2), Q(15, 2)]
        self.assertEqual(model._power(controls), [Q(15, 2), Q(-40), Q(40)])
        self.assertEqual(model._evaluate(controls, Q(1, 4)), 0)
        self.assertLess(-Q(20)+4*Q(22, 7), 0)
        # tan(3*pi/4)=-1 and tan(5*pi/4)=1 give exact sided signs.
        self.assertEqual(model._evaluate(controls, Q(3, 16))-1, Q(13, 32))
        self.assertEqual(model._evaluate(controls, Q(5, 16))+1, -Q(3, 32))
        with self.assertRaisesRegex(model.Refusal, "STRICT_INCREASING_TANGENT"):
            model.tangent_prefix_proof(fixture(model.V11, controls))

    def test_truncated_chart_endpoint_premises_cannot_be_inferred_from_derivative(self):
        # A=t-1/2 gives positive H' but a root in both truncated charts:
        # it has five roots, not the four-root shape proved by this lemma.
        with self.assertRaisesRegex(model.Refusal, "POSITIVE_TRUNCATED_CHART_ENDPOINTS"):
            model.tangent_prefix_proof(fixture(model.V11, [Q(-1, 2), Q(1, 2)]))
        with self.assertRaisesRegex(model.Refusal, "STRICT_DECREASING_COTANGENT"):
            model.cotangent_prefix_proof(fixture(model.V10, [Q(1), Q(13)]))

    def test_exact_midpoint_zero_is_explicitly_unsupported_not_root_free(self):
        with self.assertRaisesRegex(model.Refusal, "EXACT_CHART_MIDPOINT_ZERO"):
            model.cotangent_prefix_proof(fixture(model.V10, [Q(0)]))
        # A=t^2-t+3/16 has a zero at the exact middle of a full chart.
        with self.assertRaisesRegex(model.Refusal, "EXACT_CHART_MIDPOINT_ZERO"):
            model.tangent_prefix_proof(fixture(model.V11, [Q(3, 16), Q(-5, 16), Q(3, 16)]))

    def test_chart_poles_bracket_endpoints_and_true_knot_are_non_events(self):
        for proof in self.proofs.values():
            physical = proof["physical_event_proof"]
            cuts = physical["proof_cuts"]
            self.assertTrue(all(not cut["is_zero_event"] and Q(cut["exact_source_value"]) != 0 for cut in cuts))
            poles = [cut for cut in cuts if cut["kind"] == "RATIO_CHART_POLE"]
            self.assertTrue(poles)
            self.assertTrue(all(abs(Q(cut["exact_source_value"])) == 1 for cut in poles))
            self.assertEqual(physical["original_piece_edges"], ["0", "1", "2"])
            for root in physical["events"]:
                self.assertEqual(root["coordinate"]["kind"], "IMPLICIT_ORIGINAL_SOURCE_ROOT")
                self.assertEqual(root["coordinate"]["original_source_sha256"], proof["original_source_sha256"])
                self.assertEqual(root["analytic_order"], 1)

    def test_prefix_factor_harmonics_and_phase_are_checked_before_chart_count(self):
        for owner, source in ((model.V10, fixture(model.V10, [Q(1), Q(2)])),
                              (model.V11, fixture(model.V11, [Q(1)]))):
            helper = model.cotangent_prefix_proof if owner == model.V10 else model.tangent_prefix_proof
            changes = [lambda s: s["cos_splines"]["0"].update(controls=["1", "1"]),
                       lambda s: s["cos_splines"].update({"2": spline([Q(1)])}),
                       lambda s: s.update(phase_turn_offset="1/8"),
                       lambda s: s.update(phase_turn_rate="-2"),
                       lambda s: s.update(parameter_hi="3"),
                       lambda s: s.update(parameter_projection={"new": True})]
            changes.append(lambda s: s["cos_splines" if owner == model.V10 else "sin_splines"]["1"].update(
                controls=["2", "2"]))
            for change in changes:
                altered = copy.deepcopy(source)
                change(altered)
                self.reject(helper, altered)

    def test_original_knots_continuity_and_bounded_degree_are_required(self):
        source = fixture(model.V11, [Q(1), Q(2), Q(1)])
        changes = [lambda s: s["cos_splines"]["1"]["controls"].__setitem__(3, "2"),
                   lambda s: s["cos_splines"]["1"]["knots"].__setitem__(3, "1/2"),
                   lambda s: s["cos_splines"]["1"].update(degree=True),
                   lambda s: s["cos_splines"]["1"].update(degree=10000),
                   lambda s: s["cos_splines"]["1"]["controls"].pop()]
        for change in changes:
            altered = copy.deepcopy(source)
            change(altered)
            self.reject(model.tangent_prefix_proof, altered)
        for controls in ([True], [1], [Q(1)]*8, [Q(2**4097)]):
            self.reject(model._power, controls)

    def test_source_row_identity_precedes_historical_execution(self):
        for cid in self.ids:
            changes = [lambda r: r.update(id="another-original"), lambda r: r.update(origin="other-producer"),
                       lambda r: r.update(kind="HARVESTED"), lambda r: r.update(extra=True),
                       lambda r: r["spec"].update(source_parameter_id="different-time"),
                       lambda r: r["expected"].update(v54_disposition="CERTIFIED"),
                       lambda r: r["spec"]["cos_splines"]["0"]["controls"].__setitem__(0, "1")]
            for change in changes:
                row = copy.deepcopy(self.rows[cid])
                change(row)
                with patch.object(model, "_tail_receipts", side_effect=AssertionError("legacy replay reached")) as replay:
                    self.reject(model.source_proof, row)
                    replay.assert_not_called()

    def test_same_prefix_different_original_sources_remain_separate_receipts(self):
        for left_id, right_id in ((self.ids[0], self.ids[1]), (self.ids[2], self.ids[3])):
            left, right = self.proofs[left_id], self.proofs[right_id]
            self.assertEqual(left["prefix_proof"]["root_brackets"], right["prefix_proof"]["root_brackets"])
            self.assertNotEqual(left["original_source_sha256"], right["original_source_sha256"])
            self.assertNotEqual(left["tail_proof"]["root_brackets"], right["tail_proof"]["root_brackets"])
        self.assertEqual(model.source_proof(self.rows[self.ids[0]]), self.proofs[self.ids[0]])

    def test_structural_composition_rejects_wrong_source_interval_knots_and_order(self):
        cid = self.ids[0]
        row, proof = self.rows[cid], self.proofs[cid]
        blocks, phase = model.check_original(row)
        changes = [lambda p, t: p.update(source_sha256="0"*64),
                   lambda p, t: t.update(source_interval=["0", "2"]),
                   lambda p, t: t["endpoint_values"].__setitem__(0, "1"),
                   lambda p, t: p["maximal_sign_cells"].__setitem__(-1, "POSITIVE"),
                   lambda p, t: p["root_brackets"].reverse(),
                   lambda p, t: p["root_uniqueness_cells"].__setitem__(0, ["1", "2"]),
                   lambda p, t: p["root_multiplicities"].__setitem__(0, 2),
                   lambda p, t: t["root_brackets"].pop()]
        for change in changes:
            prefix, tail = copy.deepcopy(proof["prefix_proof"]), copy.deepcopy(proof["tail_proof"])
            change(prefix, tail)
            self.reject(model._compose, row, blocks, phase, prefix, tail)

    def test_three_original_tail_contracts_reexecute_and_failure_is_nontruth(self):
        called = []
        loader = model._module

        def track(filename, expected):
            module = loader(filename, expected)
            original = module.contract
            def contract_call():
                called.append(filename)
                return original()
            module.contract = contract_call
            return module

        with patch.object(model, "_module", side_effect=track):
            self.assertEqual(model._tail_receipts(), self.receipts)
        self.assertEqual(sorted(called), sorted(value[0] for value in model.PRODUCERS.values()))
        with patch.object(model, "_module", return_value=SimpleNamespace(
                contract=lambda: (_ for _ in ()).throw(model.Refusal("missing proof")))):
            self.reject(model._tail_receipts)

    def test_tail_result_digest_scope_and_pin_are_required(self):
        changed = copy.deepcopy(self.receipts[self.ids[0]])
        changed["exact_open_roots"] = 3
        self.reject(model._tail_view, self.ids[0], changed)
        with patch.object(model, "_module", return_value=SimpleNamespace(contract=lambda: changed)):
            self.reject(model._tail_receipts)
        filename, _ = model.PRODUCERS["V10_ZERO"]
        with patch.dict(model.PRODUCERS, {"V10_ZERO": (filename, "0"*40)}), \
                patch.object(model, "_module", side_effect=AssertionError("untrusted module loaded")) as loader:
            self.reject(model.expected_report)
            loader.assert_not_called()

    def test_each_real_tail_contract_uses_its_bounded_blob_checker_name(self):
        # V10 ramp calls git_blob; the other two call blob_sha. Exercise the
        # actual contract entry point for each, so an unused adapter cannot
        # make this control pass while the original checker still runs.
        for name, producer in list(model.PRODUCERS.items()):
            with self.subTest(producer=name), patch.dict(model.PRODUCERS, {name: producer}, clear=True), \
                    patch.object(model, "_dependency_blob", side_effect=model.Refusal("bounded actual checker")) as guard:
                with self.assertRaisesRegex(model.Refusal, "bounded actual checker"):
                    model._tail_receipts()
                guard.assert_called_once_with(model.HERE / "pb00701-finite-owner-corpus-v54.json")

    def test_report_cannot_promote_poles_or_knots_to_roots_or_weaken_scope(self):
        changes = [lambda r: r["source_cases"][0]["physical_event_proof"]["proof_cuts"][0].update(is_zero_event=True),
                   lambda r: r["source_cases"][0]["physical_event_proof"]["original_source_knot"].update(is_zero_event=True),
                   lambda r: r["source_cases"][0]["physical_event_proof"]["events"][0].update(analytic_order=True),
                   lambda r: r["source_cases"][0]["physical_event_proof"]["events"][0]["coordinate"].update(kind="RATIONAL", value="1/8"),
                   lambda r: r["source_cases"][2]["prefix_proof"]["charts"][0].update(root_count=1),
                   lambda r: r["source_cases"][0]["physical_event_proof"].update(complete_for_original_closed_source=1),
                   lambda r: r["historical_v54"].update(route_refusals=16),
                   lambda r: r["scope"].update(production_authorized=0),
                   lambda r: r["scope"].update(MC_B="ESTABLISHED"),
                   lambda r: r["scope"].update(protected_operation_count=25),
                   lambda r: r["scope"].update(general_ratio_or_v43_event_solver=True)]
        for change in changes:
            self.bad_report(change)

    def test_returned_report_does_not_expose_mutable_pin_or_registration_state(self):
        report = model.expected_report()
        first = next(iter(model.PINS))
        original_pin = model.PINS[first]
        report["dependencies"]["local_git_blobs"][first] = "0"*40
        report["preregistration_comments"].append(0)
        self.assertEqual(model.PINS[first], original_pin)
        self.assertEqual(model.PREREGISTRATION_COMMENTS, [6591720927, 6591724660])

    def test_verifier_bootstrap_ignores_matching_cache_and_preloaded_module(self):
        with tempfile.TemporaryDirectory(prefix="ratio-bootstrap-") as directory:
            stage = Path(directory)/"a/b/c/d"
            stage.mkdir(parents=True)
            original, alternate = stage/MODEL_PATH.name, stage/"alternate.py"
            raw = MODEL_PATH.read_bytes()
            original.write_bytes(raw)
            payload = b"CACHE_SUBSTITUTION = True\n#"
            alternate.write_bytes(payload+b" "*(len(raw)-len(payload)))
            for path in (original, alternate):
                os.utime(path, (1700000000, 1700000000))
            cache = Path(importlib.util.cache_from_source(str(original)))
            cache.parent.mkdir()
            py_compile.compile(str(alternate), cfile=str(cache), doraise=True)
            spec = importlib.util.spec_from_file_location("cache_control", original)
            cached = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cached)
            self.assertTrue(cached.CACHE_SUBSTITUTION)
            fake = SimpleNamespace(CACHE_SUBSTITUTION=True)
            with patch.dict(sys.modules, {"pb00701_ratio_prefix_composition": fake,
                                         "ratio_prefix_verified_source": fake}):
                verified = load_verified_model(original)
            self.assertFalse(hasattr(verified, "CACHE_SUBSTITUTION"))
            self.assertEqual(verified.SCHEMA, model.SCHEMA)

    def test_verifier_bootstrap_uses_same_buffer_after_path_replacement(self):
        with tempfile.TemporaryDirectory(prefix="ratio-bootstrap-buffer-") as directory:
            stage = Path(directory)/"a/b/c/d"
            stage.mkdir(parents=True)
            path = stage/MODEL_PATH.name
            path.write_bytes(MODEL_PATH.read_bytes())
            compiler = _compile_model
            def replace_after_hash(raw, at):
                path.write_bytes(b"raise RuntimeError('replacement must not run')\n")
                return compiler(raw, at)
            with patch.dict(globals(), {"_compile_model": replace_after_hash}):
                self.assertEqual(load_verified_model(path).SCHEMA, model.SCHEMA)
            with self.assertRaises(BootstrapRefusal):
                load_verified_model(path)

    def test_verifier_bootstrap_checks_size_and_pin_before_compilation(self):
        with tempfile.TemporaryDirectory(prefix="ratio-bootstrap-bounds-") as directory:
            path = Path(directory)/"model.py"
            for raw in (b"raise RuntimeError('must not run')\n", b" "*(MODEL_BYTE_LIMIT+1)):
                path.write_bytes(raw)
                with patch.dict(globals(), {"_compile_model": lambda *args: self.fail("untrusted code compiled")}):
                    with self.assertRaises(BootstrapRefusal):
                        load_verified_model(path)


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
            producer.git_blob = model._dependency_blob
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.contract:
        contract()
        print("PASS: four complete original ratio sources; 8/5/8/4 simple roots; original poles and knots remain non-events")
    if args.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RatioTests))
        if not result.wasSuccessful():
            raise SystemExit(1)
    if not args.contract and not args.self_test:
        parser.error("select --contract and/or --self-test")


if __name__ == "__main__":
    main()
