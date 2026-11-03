#!/usr/bin/env python3
"""Fresh fifty-source physical zero sets and independent semantic falsifiers."""
from __future__ import annotations

import argparse
import builtins
from collections import Counter
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
MODEL_PATH = HERE / "pb00701_fifty_source_zero_set_consumer.py"
MODEL_BLOB = "d5eef89ab168a2acc2588f13a6d87ab88b998d40"


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
    module = types.ModuleType("fifty_source_reviewed_model")
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
            with tempfile.TemporaryDirectory(prefix="fifty-source-bootstrap-cache-") as directory:
                here = Path(directory) / "research/machining-completeness/tasks/MC-038"
                here.mkdir(parents=True)
                path = here / Path(model_path).name
                ordinary = install_accepted_stale_cache(path, trusted, altered)
                self.assertTrue(ordinary.CACHE_SUBSTITUTION)
                fake = types.ModuleType("fifty_source_reviewed_model")
                fake.CACHE_SUBSTITUTION = True
                with mock.patch.dict(sys.modules, {fake.__name__: fake, Path(model_path).stem: fake}):
                    checked = load_reviewed_model(path, model_blob)
                    self.assertFalse(hasattr(checked, "CACHE_SUBSTITUTION"))
                    self.assertTrue(callable(checked.expected_report))
                    self.assertIs(sys.modules[fake.__name__], fake)

        def test_bootstrap_consumes_same_checked_buffer_after_path_replacement(self):
            with tempfile.TemporaryDirectory(prefix="fifty-source-bootstrap-replace-") as directory:
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
            with tempfile.TemporaryDirectory(prefix="fifty-source-bootstrap-bounds-") as directory:
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
            with tempfile.TemporaryDirectory(prefix="fifty-source-bootstrap-flags-") as directory:
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

V6_0 = "composite:DELEGATED_V6_CONSTANT_MODULATION:tail0"
V6_100 = "composite:DELEGATED_V6_CONSTANT_MODULATION:tail100"
V8_0 = "composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail0"
V8_100 = "composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail100"
V9_EXTERIOR = "harvested:verify_pb00701_v9:1a5fd052a155"
V23_EXTERIOR = "harvested:verify_pb00701_v52:2250401ce435"
CONTINUUM_ID = "harvested:verify_pb00701_v53:cb01c327d5f1"
V44_ID = "harvested:verify_pb00701_v44:ffaea08e30c9"
V30_ID = "composite:PB00701_V30_EXACT_SOURCE_ADAPTIVE_PROJECTIVE_RATIONAL_SEPARATOR:tail0"
V27_100 = "composite:PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION:tail100"
V17_MULT = "composite:PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER:tail100"
V13_MULT = "composite:PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC:tail100"
V41_ID = "harvested:verify_pb00701_v13:c426f65b5c10"
POSITIVE_ID = "harvested:verify_pb00701_v9:4e7b85fa122a"
NEGATIVE_ID = "composite:PB00701_V18_EXACT_NONVANISHING_SOURCE_MODULE_FACTOR:tail0"


def physical_sign(value):
    if value is None:
        return None
    if type(value) is str:
        if value not in ("POSITIVE", "NEGATIVE"):
            raise AssertionError("unproved producer sign")
        return 1 if value == "POSITIVE" else -1
    if type(value) is not int or value not in (-1, 1):
        raise AssertionError("nonexact producer sign")
    return value


def independent_raw_projection(family, view):
    """Read actual proof fields without calling either consumer adapter.

    This projection is only a verifier oracle over this run's freshly checked
    views. It performs no root search and accepts no saved static event map.
    """
    events = []
    def add(coordinate, left, right, order=1, location="SPAN_INTERIOR", implicit=False):
        if type(order) is int:
            typed_order = ("SMOOTH", order)
        elif location == "SOURCE_KNOT":
            typed_order = ("KNOT_SIDED", order["left"], order["right"])
        else:
            side = "RIGHT" if location == "SOURCE_LEFT_ENDPOINT" else "LEFT"
            typed_order = ("ONE_SIDED", side, order[side.lower()])
        events.append(("IMPLICIT" if implicit else "RATIONAL", coordinate, location,
                       typed_order, physical_sign(left), physical_sign(right)))
    if family == "five":
        for root in view["events"]:
            coord, order = root["coordinate"], root["order"]
            implicit = coord["kind"] != "RATIONAL"
            value = [coord["lower"], coord["upper"]] if implicit else coord["value"]
            n = order["value"] if order["kind"] == "INTEGER" else {k:v for k,v in order.items() if k != "kind"}
            loc = "SPAN_INTERIOR" if root["location"] == "SPAN_OPEN" else root["location"]
            add(value, root["left_sign"], root["right_sign"], n, loc, implicit)
        signs = view["maximal_open_signs"]
    elif family == "continuum":
        zeros = view["zero_set"]
        if not (zeros["kind"] == "CLOSED_CONTINUUM_ZERO_COMPONENT" and
                zeros["every_closed_source_point_is_zero"] is True and
                zeros["isolated_root_count"] is None and zeros["isolated_finite_root_list_applicable"] is False):
            raise AssertionError("invalid actual continuum proof")
        return None, None
    elif family == "knot":
        knot = view["shared_source_knot"]
        add(knot["coordinate"], knot["left_sign"], knot["right_sign"],
            {"left":knot["left_one_sided_order"], "right":knot["right_one_sided_order"]}, "SOURCE_KNOT")
        signs = [knot["left_sign"], knot["right_sign"]]
    elif family == "stationary":
        for root in view["ordered_physical_zero_events"]:
            if root["coordinate_kind"] != "EXACT_RATIONAL":
                raise AssertionError("unreviewed physical algebraic root")
            add(root["coordinate"], root["left_sign"], root["right_sign"], root["multiplicity"])
        signs = [c["sign"] for c in view["maximal_open_sign_cells"]]
    elif family == "trig_fixed":
        for root in view["ordered_implicit_root_events"]:
            add(root["strict_bracket"], root["left_sign"], root["right_sign"], root["smooth_physical_multiplicity"], implicit=True)
        signs = [c["sign"] for c in view["maximal_open_physical_sign_cells"]]
    elif family == "v44":
        root = view["physical_root"]
        add(root["strict_isolation"], root["left_sign"], root["right_sign"], root["smooth_multiplicity"], implicit=True)
        signs = view["physical_endpoint_signs"]
    elif family == "refusal_cone":
        if view["sign"] != "POSITIVE_ON_CLOSED_SOURCE_SPAN" or view["strict_lower_bound"] != "7/24":
            raise AssertionError("missing root-free closed-source theorem")
        signs = [1]
    elif family == "v23_bernstein":
        proof = view["source_specific_proof"]["physical_event_proof"]
        for root in proof["events"]:
            add(root["coordinate"]["value"], None, root["right_sign"],
                {"right":root["analytic_order"]}, "SOURCE_LEFT_ENDPOINT")
        signs = [c["sign"] for c in proof["sign_cells"]]
    elif family == "ordered_children":
        for root in view["ordered_root_events"]:
            add(root["strict_bracket"], root["left_sign"], root["right_sign"], root["smooth_multiplicity"], implicit=True)
        signs = [c["sign"] for c in view["maximal_open_physical_sign_cells"]]
    elif family == "exact_zero_children":
        for root in view["physical_events"]:
            knot = root["kind"] == "EXACT_PHYSICAL_SOURCE_KNOT_ZERO"
            order = {"left":root["left_one_sided_order"], "right":root["right_one_sided_order"]} if knot else root["smooth_multiplicity"]
            add(root["coordinate"], root["left_sign"], root["right_sign"], order,
                "SOURCE_KNOT" if knot else "SPAN_INTERIOR")
        signs = view["ordered_nonzero_signs"]
    elif family == "component_prefix":
        proof = view["physical_event_proof"]
        for root in proof["events"]:
            add(root["strict_source_bracket"], root["physical_sign_before"], root["physical_sign_after"], root["multiplicity"], implicit=True)
        signs = proof["maximal_source_sign_cells"]
    elif family in ("ratio_prefix", "bernstein_sectors", "multiplier_tails"):
        proof = view["source_specific_proof"]["physical_event_proof"] if family == "bernstein_sectors" else view["physical_event_proof"]
        bracket = {"ratio_prefix":"strict_open_isolating_interval", "bernstein_sectors":"isolating_interval", "multiplier_tails":"strict_bracket"}[family]
        order = "smooth_physical_multiplicity" if family == "multiplier_tails" else "analytic_order"
        for root in proof["events"]:
            add(root["coordinate"][bracket], root["left_sign"], root["right_sign"], root[order], implicit=True)
        field = "maximal_open_sign_cells" if family == "multiplier_tails" else "maximal_sign_cells"
        signs = [c["sign"] for c in proof[field]]
    else:
        raise AssertionError("unregistered family " + family)
    return events, [physical_sign(s) for s in signs]


def normalized_signature(event):
    coord, order = event["coordinate"], event["order"]
    if coord["kind"] == "RATIONAL":
        kind, value = "RATIONAL", coord["value"]
    else:
        if coord["kind"] != "UNIQUE_IMPLICIT_ZERO_OF_PINNED_ORIGINAL_SOURCE":
            raise AssertionError("unreviewed physical locator kind")
        kind, value = "IMPLICIT", coord["strict_open_bracket"]
    if order["kind"] == "SMOOTH":
        typed_order = ("SMOOTH", order["value"])
    elif order["kind"] == "KNOT_SIDED":
        typed_order = ("KNOT_SIDED", order["left"], order["right"])
    else:
        if order["kind"] != "ONE_SIDED":
            raise AssertionError("unreviewed order kind")
        typed_order = ("ONE_SIDED", order["side"], order["value"])
    return kind, value, event["location"], typed_order, event["left_sign"], event["right_sign"]


def resolve_actual_proof_field(value, path):
    """Resolve a bounded reference inside its explicitly identified owner."""
    if type(path) is str:
        if not 0 < len(path) <= 512:
            raise AssertionError("invalid proof path text")
        components=[]
        for part in path.split("."):
            match=re.fullmatch(r"([A-Za-z_][A-Za-z_0-9]*)(?:\[([0-9]+)\])?",part)
            if match is None:
                raise AssertionError("invalid proof path component")
            components.append(match[1])
            if match[2] is not None:components.append(int(match[2]))
    elif type(path) is list and 0 < len(path) <= 32:
        components=path
    else:
        raise AssertionError("invalid typed proof path")
    for component in components:
        if type(component) is str and 0 < len(component) <= 256:
            if type(value) is not dict or component not in value:
                raise AssertionError("proof field does not belong to its claimed owner: "+component)
        elif type(component) is int and 0 <= component <= 1024:
            if type(value) is not list or component >= len(value):
                raise AssertionError("proof index does not belong to its claimed owner")
        else:
            raise AssertionError("invalid proof component type")
        value=value[component]
    return value


class FiftySourceTests(unittest.TestCase):
    replay = None

    @classmethod
    def setUpClass(cls):
        if cls.replay is None:
            cls.replay = model.replay_qualified_sources()
        cls.expected_bytes = model.bounded_bytes(model.report_from_replay(cls.replay))
        cls.originals = cls.replay["indexed"]
        cls.receipts = cls.replay["receipts"]
        cls.views = cls.replay["views"]
        cls.auxiliary = cls.replay["auxiliary"]
        cls.semantics = {cid:model.adapt_source(cid,cls.originals[cid],cls.receipts[cid],cls.views[cid],cls.auxiliary)
                         for cid in cls.receipts}
        cls.sources = {cid:model.assemble_source(cid,cls.originals[cid],cls.receipts[cid],cls.semantics[cid])
                       for cid in cls.receipts}

    def report_rejects(self, change):
        changed = json.loads(self.expected_bytes)
        change(changed)
        with self.assertRaises(model.Refusal):
            model._compare_with_replayed_bytes(changed, self.expected_bytes)

    def semantic_rejects(self, cid, change):
        semantic = copy.deepcopy(self.semantics[cid])
        change(semantic)
        with self.assertRaises(model.Refusal):
            model.assemble_source(cid, self.originals[cid], self.receipts[cid], semantic)

    def test_every_actual_proof_event_and_sign_is_preserved_before_aggregate_counts(self):
        totals = Counter()
        identities = set()
        for cid, source in self.sources.items():
            receipt, view = self.receipts[cid], self.views[cid]
            raw_events, raw_signs = independent_raw_projection(receipt["producer"], view)
            zeros = source["zero_set"]
            if raw_events is None:
                self.assertEqual(zeros["kind"], "CLOSED_CONTINUUM_ZERO_COMPONENT")
                totals["continuum"] += 1
                continue
            self.assertEqual(zeros["kind"], "FINITE_ORIGINAL_SOURCE_ZERO_SET")
            actual = [normalized_signature(e) for e in zeros["events"]]
            self.assertEqual(actual, raw_events, cid)
            self.assertEqual([c["sign"] for c in zeros["maximal_nonzero_cells"]], raw_signs, cid)
            self.assertEqual(zeros["isolated_root_count"], len(raw_events))
            exterior = sum(e["location"] in ("SOURCE_LEFT_ENDPOINT","SOURCE_RIGHT_ENDPOINT") for e in zeros["events"])
            knots = sum(e["location"] == "SOURCE_KNOT" for e in zeros["events"])
            self.assertEqual(zeros["source_open_root_count"], len(raw_events)-exterior)
            self.assertEqual(sum(zeros["strict_span_open_root_counts"]), len(raw_events)-exterior-knots)
            self.assertEqual(len(zeros["maximal_nonzero_cells"]), 1+len(raw_events)-exterior)
            totals.update(finite=1, events=len(raw_events), cells=len(raw_signs), exteriors=exterior,
                          knots=knots, spans=len(raw_events)-exterior-knots,
                          rational=sum(e[0]=="RATIONAL" for e in raw_events),
                          implicit=sum(e[0]=="IMPLICIT" for e in raw_events), root_free=int(not raw_events))
            for event in zeros["events"]:
                self.assertEqual(event["source_case_id"],cid)
                self.assertEqual(event["source_sha256"],source["source_sha256"])
                side_signs=(event["left_sign"],event["right_sign"])
                classification=("BOUNDARY" if None in side_signs else
                                "CROSSING" if side_signs[0]!=side_signs[1] else "TOUCHING")
                self.assertEqual(event["classification"],classification)
                scoped=(cid,source["source_sha256"],event["event_id"])
                self.assertNotIn(scoped,identities)
                identities.add(scoped)
        self.assertEqual(totals, Counter(finite=49,continuum=1,events=81,cells=128,
                         exteriors=2,knots=4,spans=75,rational=12,implicit=69,root_free=10))
        self.assertEqual(len(identities),81)

    def test_exact_original_fifty_ids_and_source_identity_are_bound(self):
        expected={cid for cid,row in self.originals.items() if row["expected"]["v54_disposition"] in
                  ("BLOCKED","BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE")}
        self.assertEqual(len(self.originals),121)
        self.assertEqual(set(self.sources),expected)
        self.assertEqual(len(expected),50)
        for cid,source in self.sources.items():
            row=self.originals[cid];spec=row["spec"]
            for value,field in ((spec,"source_sha256"),(row,"original_row_sha256")):
                raw=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()
                self.assertEqual(source[field],hashlib.sha256(raw).hexdigest(),cid)
            self.assertEqual(source["case_id"],cid)
            self.assertEqual(source["source_interval"],[spec["parameter_lo"],spec["parameter_hi"]])
            self.assertEqual(source["phase_turn_law"],{"offset":spec["phase_turn_offset"],"rate":spec["phase_turn_rate"]})
            self.assertEqual(source["source_parameter_id"],spec["source_parameter_id"])
            self.assertEqual((source["origin"],source["provenance_kind"]),(row["origin"],row["kind"]))
            self.assertEqual(source["historical_v54_disposition"],row["expected"]["v54_disposition"])

    def test_all_event_and_uniqueness_references_resolve_in_their_actual_producer(self):
        owners={
            "five":"events", "knot":"shared_source_knot",
            "stationary":"ordered_physical_zero_events", "trig_fixed":"ordered_implicit_root_events",
            "v44":"physical_root", "v23_bernstein":"source_specific_proof.physical_event_proof.events",
            "ordered_children":"ordered_root_events", "exact_zero_children":"physical_events",
            "component_prefix":"physical_event_proof.events", "ratio_prefix":"physical_event_proof.events",
            "bernstein_sectors":"source_specific_proof.physical_event_proof.events",
            "multiplier_tails":"physical_event_proof.events"}
        events_checked=implicit_checked=0
        for cid,source in self.sources.items():
            receipt,view=self.receipts[cid],self.views[cid]
            source_proof=source["producer_evidence"]
            for key in ("producer","producer_code","producer_git_blob","replayed_result_sha256"):
                self.assertEqual(source_proof[key],receipt[key])
            resolve_actual_proof_field(view,source_proof["field_path"])
            zeros=source["zero_set"]
            events=zeros["events"] or []
            if not events:continue
            raw=resolve_actual_proof_field(view,owners[receipt["producer"]])
            raw_events=raw if type(raw) is list else [raw]
            self.assertEqual(len(events),len(raw_events),cid)
            for event,expected_raw_event in zip(events,raw_events):
                actual=resolve_actual_proof_field(view,event["proof_path"])
                self.assertEqual(model.bounded_bytes(actual),model.bounded_bytes(expected_raw_event),cid)
                events_checked+=1
                coordinate=event["coordinate"]
                if coordinate["kind"]=="RATIONAL":continue
                proof=coordinate["uniqueness_evidence"]
                for key in ("producer","producer_code","producer_git_blob","replayed_result_sha256"):
                    self.assertEqual(proof[key],receipt[key])
                self.assertEqual(proof["field_path"],event["proof_path"])
                actual=resolve_actual_proof_field(view,proof["field_path"])
                self.assertEqual(model.bounded_bytes(actual),model.bounded_bytes(expected_raw_event),cid)
                implicit_checked+=1
        self.assertEqual((events_checked,implicit_checked),(81,69))

    def test_endpoint_and_knot_references_keep_their_distinct_proof_owners(self):
        checked=expected=0
        kinds=Counter()
        for cid,source in self.sources.items():
            zeros=source["zero_set"]
            if zeros["kind"]!="FINITE_ORIGINAL_SOURCE_ZERO_SET":continue
            row=self.originals[cid];spec=row["spec"]
            edges={Q(spec["parameter_lo"]),Q(spec["parameter_hi"])}
            for channel in ("cos_splines","sin_splines"):
                for spline in spec[channel].values():edges.update(map(Q,spline["knots"]))
            expected+=len(edges)
            for point in zeros["exterior_points"]+zeros["true_source_knots"]:
                proof=point["proof"];kind=proof["kind"]
                family=self.receipts[cid]["producer"]
                expected_kind=("CHECKED_AUXILIARY_REPORT" if family=="five" else
                               "ORIGINAL_SOURCE_ENDPOINT_IDENTITY" if cid==V41_ID and "side" in point else
                               "FRESH_V2_SOURCE_RECEIPT" if family=="trig_fixed" and "side" in point else
                               "FRESH_PRODUCER_VIEW")
                self.assertEqual(kind,expected_kind,(cid,point["coordinate"]))
                kinds[kind]+=1;checked+=1
                if kind=="FRESH_PRODUCER_VIEW":
                    for key in ("producer","producer_code","producer_git_blob","replayed_result_sha256"):
                        self.assertEqual(proof[key],self.receipts[cid][key])
                    resolve_actual_proof_field(self.views[cid],proof["field_path"])
                elif kind=="CHECKED_AUXILIARY_REPORT":
                    aux=self.auxiliary[proof["auxiliary_key"]]
                    self.assertEqual(proof["report_path"],aux["path"])
                    self.assertEqual(proof["report_git_blob"],aux["git_blob"])
                    digest=hashlib.sha256(model.bounded_bytes(aux["report"])).hexdigest()
                    self.assertEqual(proof["canonical_report_sha256"],digest)
                    resolve_actual_proof_field(aux["report"],proof["field_path"])
                elif kind=="FRESH_V2_SOURCE_RECEIPT":
                    self.assertEqual(proof["source_case_id"],cid)
                    self.assertEqual(proof["qualified_v2_model_git_blob"],model.V2_BLOB)
                    receipt=self.receipts[cid]
                    self.assertEqual(proof["receipt_sha256"],hashlib.sha256(model.bounded_bytes(receipt)).hexdigest())
                    resolve_actual_proof_field(receipt,proof["field_path"])
                elif kind=="ORIGINAL_SOURCE_ENDPOINT_IDENTITY":
                    self.assertEqual(cid,V41_ID)
                    self.assertEqual(proof["source_case_id"],cid)
                    self.assertEqual(proof["source_sha256"],source["source_sha256"])
                    self.assertEqual(proof["original_row_sha256"],source["original_row_sha256"])
                    self.assertEqual(proof["lemma"],"V41_CLAMPED_AFFINE_CHANNELS_AT_ZERO_AND_QUARTER_TURN")
                    self.assertEqual(len(proof["source_field_paths"]),6)
                    for path in proof["source_field_paths"]:resolve_actual_proof_field(row,path)
                    value=(Q(spec["cos_splines"]["1"]["controls"][0])+Q(spec["cos_splines"]["3"]["controls"][0])
                           if point["coordinate"]=="0" else Q(spec["sin_splines"]["1"]["controls"][-1]))
                    self.assertLess(value,0)
                    self.assertEqual(point["value_sign"],-1)
                else:
                    self.fail("unowned endpoint/knot proof: "+str(kind))
        self.assertEqual(checked,expected)
        self.assertEqual(set(kinds),{"FRESH_PRODUCER_VIEW","CHECKED_AUXILIARY_REPORT",
                                    "FRESH_V2_SOURCE_RECEIPT","ORIGINAL_SOURCE_ENDPOINT_IDENTITY"})
        self.assertEqual(kinds["ORIGINAL_SOURCE_ENDPOINT_IDENTITY"],2)
        self.assertEqual(kinds["FRESH_V2_SOURCE_RECEIPT"],4)

    def test_actual_four_knot_zeros_are_deduplicated_and_keep_sided_orders(self):
        expected={V6_0:(1,-1),V6_100:(1,1),
          "composite:PB00701_V23_EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR:tail0":(-1,1),
          "composite:PB00701_V25_EXACT_COMPONENT_CONE_MIXED_PROJECTION_ANCHOR:tail0":(-1,1)}
        actual={cid for cid,s in self.sources.items() if s["zero_set"]["kind"]=="FINITE_ORIGINAL_SOURCE_ZERO_SET"
                and any(e["location"]=="SOURCE_KNOT" for e in s["zero_set"]["events"])}
        self.assertEqual(actual,set(expected))
        local=self.views[V6_0]["shared_source_knot"]["span_local_records"]
        self.assertEqual((local["same_source_coordinate_root_records"],local["deduplicated_distinct_source_root_events"]),(2,1))
        for cid,signs in expected.items():
            zeros=self.sources[cid]["zero_set"]
            self.assertEqual(zeros["isolated_root_count"],1)
            event=zeros["events"][0]
            self.assertEqual(event["coordinate"],{"kind":"RATIONAL","value":"1"})
            self.assertEqual(event["order"],{"kind":"KNOT_SIDED","left":1,"right":1,"global_smooth_multiplicity_claimed":False})
            self.assertEqual((event["left_sign"],event["right_sign"]),signs)
            self.assertEqual(zeros["strict_span_open_root_counts"],[0,0])
            self.assertEqual(zeros["source_open_root_count"],1)
            self.assertEqual(len(zeros["maximal_nonzero_cells"]),2)

    def test_knot_parity_and_shared_endpoint_premises_are_not_fabricated(self):
        for cid in (V6_0,V6_100):
            for change in (
                lambda s:s["events"].append(copy.deepcopy(s["events"][0])),
                lambda s:s["events"].clear(),
                lambda s:s["events"][0].__setitem__("order",{"kind":"SMOOTH","value":1}),
                lambda s:s["events"][0]["order"].__setitem__("global_smooth_multiplicity_claimed",True),
                lambda s:s["events"][0]["order"].__setitem__("left",0),
                lambda s:s["events"][0]["coordinate"].__setitem__("value","3/4"),
                lambda s:s["knots"].clear(),
                lambda s:s["knots"][0].__setitem__("is_zero",False),
                lambda s:s["knots"][0].__setitem__("continuous",False),
                lambda s:s["knots"][0].__setitem__("right_sign",-s["knots"][0]["right_sign"]),
            ):
                with self.subTest(case=cid,change=change):self.semantic_rejects(cid,change)
        # This actual +/+ order1/1 knot is valid. No smooth odd-parity rule.
        self.assertEqual([c["sign"] for c in self.sources[V6_100]["zero_set"]["maximal_nonzero_cells"]],[1,1])

    def test_smooth_even_touches_split_connected_cells_without_a_sign_change(self):
        for cid,cell_signs in ((V8_0,[1,1,-1]),(V8_100,[1,1])):
            zeros=self.sources[cid]["zero_set"]
            touch=zeros["events"][0]
            self.assertEqual(touch["coordinate"],{"kind":"RATIONAL","value":"1/2"})
            self.assertEqual(touch["order"],{"kind":"SMOOTH","value":2})
            self.assertEqual((touch["left_sign"],touch["right_sign"]),(1,1))
            cells=zeros["maximal_nonzero_cells"]
            self.assertEqual([c["sign"] for c in cells],cell_signs)
            self.assertEqual(cells[0]["right_boundary"],{
                "kind":"PHYSICAL_ZERO_EVENT","event_id":touch["event_id"],
                "source_case_id":cid,"source_sha256":self.sources[cid]["source_sha256"]})
            self.assertEqual(cells[1]["left_boundary"],cells[0]["right_boundary"])
            self.assertIs(cells[0]["right_included"],False)
            self.assertIs(cells[1]["left_included"],False)
            for change in (lambda s:s["events"][0]["order"].__setitem__("value",1),
                           lambda s:s["events"][0].__setitem__("right_sign",-1),
                           lambda s:s["events"][0].__setitem__("order",{"kind":"KNOT_SIDED","left":1,"right":1,"global_smooth_multiplicity_claimed":False})):
                self.semantic_rejects(cid,change)

    def test_two_left_exterior_zeros_have_only_inward_order_and_no_empty_cell(self):
        found=[]
        for cid,source in self.sources.items():
            zeros=source["zero_set"]
            if zeros["kind"]!="FINITE_ORIGINAL_SOURCE_ZERO_SET":continue
            for event in zeros["events"]:
                if event["location"].startswith("SOURCE_") and event["location"]!="SOURCE_KNOT":found.append((cid,event))
        self.assertEqual({cid for cid,_ in found},{V9_EXTERIOR,V23_EXTERIOR})
        for cid,order in ((V9_EXTERIOR,1),(V23_EXTERIOR,2)):
            zeros=self.sources[cid]["zero_set"];event=zeros["events"][0]
            self.assertEqual(event["location"],"SOURCE_LEFT_ENDPOINT")
            self.assertEqual(event["coordinate"],{"kind":"RATIONAL","value":"0"})
            self.assertEqual(event["order"],{"kind":"ONE_SIDED","side":"RIGHT","value":order,
                             "outside_order":None,"global_smooth_multiplicity_claimed":False})
            self.assertIs(event["left_sign"],None)
            self.assertEqual(event["right_sign"],1)
            self.assertEqual(zeros["source_open_root_count"],0)
            cells=zeros["maximal_nonzero_cells"]
            self.assertEqual(len(cells),1)
            self.assertEqual(cells[0]["left_boundary"],{
                "kind":"PHYSICAL_ZERO_EVENT","event_id":event["event_id"],
                "source_case_id":cid,"source_sha256":self.sources[cid]["source_sha256"]})
            self.assertIs(cells[0]["left_included"],False)
            self.assertIs(cells[0]["right_included"],True)
            self.assertEqual(cells[0]["sign"],1)
            for change in (lambda s:s["events"][0].__setitem__("left_sign",-1),
                           lambda s:s["events"][0].__setitem__("order",{"kind":"SMOOTH","value":order}),
                           lambda s:s["events"][0]["order"].__setitem__("side","LEFT"),
                           lambda s:s["events"][0].__setitem__("location","SPAN_INTERIOR"),
                           lambda s:s["endpoints"][0].__setitem__("is_zero",False),
                           lambda s:s["endpoints"].pop()):
                self.semantic_rejects(cid,change)

    def test_all_implicit_locators_keep_their_source_and_original_piece(self):
        count=0
        for cid,source in self.sources.items():
            zeros=source["zero_set"]
            if zeros["kind"]!="FINITE_ORIGINAL_SOURCE_ZERO_SET":continue
            edges=list(map(Q,source["original_source_piece_edges"]))
            for event in zeros["events"]:
                coord=event["coordinate"]
                if coord["kind"]=="RATIONAL":continue
                count+=1
                self.assertEqual(coord["kind"],"UNIQUE_IMPLICIT_ZERO_OF_PINNED_ORIGINAL_SOURCE")
                self.assertEqual(coord["source_case_id"],cid)
                self.assertEqual(coord["source_sha256"],source["source_sha256"])
                self.assertEqual(coord["source_parameter_id"],source["source_parameter_id"])
                lo,hi=map(Q,coord["strict_open_bracket"])
                indices=[i for i,(a,b) in enumerate(zip(edges,edges[1:])) if a<=lo<hi<=b]
                self.assertEqual(len(indices),1)
                self.assertEqual(coord["source_piece_index"],indices[0])
                self.assertEqual(list(map(Q,coord["source_span"])),[edges[indices[0]],edges[indices[0]+1]])
                self.assertTrue(coord["uniqueness_evidence"])
        self.assertEqual(count,69)
        v30=self.sources[V30_ID]["zero_set"]["events"]
        self.assertEqual(len(v30),2)
        self.assertEqual(v30[1]["coordinate"]["strict_open_bracket"],["121/64","61/32"])
        self.assertEqual(v30[1]["coordinate"]["source_piece_index"],1)
        self.semantic_rejects(V30_ID,lambda s:s["events"][1].__setitem__("source_piece_index",0))
        self.semantic_rejects(V30_ID,lambda s:s["events"].pop())

    def test_shared_open_bracket_boundaries_preserve_strict_root_order(self):
        expected={
          "composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail0":"1/2",
          "composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail100":"1/2",
          "composite:PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO:tail0":"7/8",
          "composite:PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO:tail100":"7/8",
          V27_100:"1"}
        for cid,bound in expected.items():
            events=self.sources[cid]["zero_set"]["events"]
            pairs=[(a,b) for a,b in zip(events,events[1:])
                   if a["coordinate"].get("strict_open_bracket",[None,None])[1]==bound
                   and b["coordinate"].get("strict_open_bracket",[None,None])[0]==bound]
            self.assertEqual(len(pairs),1,cid)
            self.assertNotEqual(pairs[0][0]["event_id"],pairs[0][1]["event_id"])
        for change in (lambda s:s["events"][0]["coordinate"].__setitem__("upper","9/8"),
                       lambda s:s["events"][0]["coordinate"].__setitem__("lower","1"),
                       lambda s:s["events"].reverse(),
                       lambda s:s["events"][0]["coordinate"].__setitem__("unique",False),
                       lambda s:s["events"][0]["coordinate"].__setitem__("kind","IMPLICIT_CLOSED"),
                       lambda s:s["events"][0].__setitem__("coordinate",{"kind":"RATIONAL","value":"1"})):
            self.semantic_rejects(V27_100,change)

    def test_maximal_cells_use_physical_events_and_cross_nonzero_knots(self):
        for cid,source in self.sources.items():
            zeros=source["zero_set"]
            if zeros["kind"]!="FINITE_ORIGINAL_SOURCE_ZERO_SET":continue
            events={e["event_id"]:e for e in zeros["events"]}
            for cell in zeros["maximal_nonzero_cells"]:
                for side in ("left","right"):
                    boundary=cell[side+"_boundary"]
                    self.assertIn(boundary["kind"],("SOURCE_EXTERIOR","PHYSICAL_ZERO_EVENT"))
                    if boundary["kind"]=="PHYSICAL_ZERO_EVENT":
                        self.assertIn(boundary["event_id"],events)
                        self.assertEqual(set(boundary),{"kind","event_id","source_case_id","source_sha256"})
                        self.assertEqual(boundary["source_case_id"],cid)
                        self.assertEqual(boundary["source_sha256"],source["source_sha256"])
                        self.assertIs(cell[side+"_included"],False)
                    else:
                        self.assertIs(cell[side+"_included"],True)
            for knot in zeros["true_source_knots"]:
                if knot["is_zero"]:
                    self.assertIn(knot["event_ref"],events)
                else:
                    self.assertIs(knot["event_ref"],None)
                    crossed=[cell for cell in zeros["maximal_nonzero_cells"] if knot["coordinate"] in cell["crossed_nonzero_source_knots"]]
                    self.assertEqual(len(crossed),1,(cid,knot))
        v30=self.sources[V30_ID]["zero_set"]["maximal_nonzero_cells"]
        middle=next(c for c in v30 if "1" in c["crossed_nonzero_source_knots"])
        self.assertEqual(middle["source_piece_indices"],[0,1])
        self.assertEqual(middle["sign"],1)

    def test_exact_rational_event_inventory_is_source_scoped(self):
        actual={cid:[(e["coordinate"]["value"],e["location"]) for e in s["zero_set"]["events"]
                     if e["coordinate"]["kind"]=="RATIONAL"]
                for cid,s in self.sources.items() if s["zero_set"]["kind"]=="FINITE_ORIGINAL_SOURCE_ZERO_SET"}
        actual={cid:events for cid,events in actual.items() if events}
        expected={V6_0:[("1","SOURCE_KNOT")],V6_100:[("1","SOURCE_KNOT")],
          V8_0:[("1/2","SPAN_INTERIOR"),("3/2","SPAN_INTERIOR")],V8_100:[("1/2","SPAN_INTERIOR")],
          V9_EXTERIOR:[("0","SOURCE_LEFT_ENDPOINT")],V23_EXTERIOR:[("0","SOURCE_LEFT_ENDPOINT")],
          "composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail0":[("1/2","SPAN_INTERIOR")],
          "composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail100":[("1/2","SPAN_INTERIOR")],
          "composite:PB00701_V23_EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR:tail0":[("1","SOURCE_KNOT")],
          "composite:PB00701_V25_EXACT_COMPONENT_CONE_MIXED_PROJECTION_ANCHOR:tail0":[("1","SOURCE_KNOT")],
          "composite:PB00701_V40_EXACT_SIGNED_B_ANTI_DIAGONAL_DIRECT_ROTATED_COORDINATE:tail0":[("1/2","SPAN_INTERIOR")]}
        self.assertEqual(actual,expected)
        self.assertEqual(sum(map(len,actual.values())),12)
        # Equal carrier coordinates belong to different original functions.
        a=self.sources[V13_MULT]["zero_set"]["events"][0]["coordinate"]
        b=self.sources[V17_MULT]["zero_set"]["events"][0]["coordinate"]
        self.assertEqual(a["strict_open_bracket"],b["strict_open_bracket"])
        self.assertNotEqual(a["source_case_id"],b["source_case_id"])
        self.assertNotEqual(a["source_sha256"],b["source_sha256"])

    def test_count_preserving_duplicate_reversal_and_false_piece_assignments_refuse(self):
        for change in (lambda s:s["events"].__setitem__(1,copy.deepcopy(s["events"][0])),
                       lambda s:s["events"].reverse(),
                       lambda s:s["events"][0].__setitem__("location","SOURCE_KNOT"),
                       lambda s:s["events"][0].__setitem__("source_piece_index",1),
                       lambda s:s.__setitem__("span_open_counts",[2,0]),
                       lambda s:s["events"][0]["coordinate"].__setitem__("value","1")):
            self.semantic_rejects(V8_0,change)
        # Closed and source-open counts can differ only by actual exteriors;
        # the four source knots must not disappear into strict-span counts.
        for cid in (V6_0,V9_EXTERIOR,V23_EXTERIOR):
            self.semantic_rejects(cid,lambda s:s.__setitem__("source_open_count",s["source_open_count"]+1))
            self.semantic_rejects(cid,lambda s:s["span_open_counts"].__setitem__(0,s["span_open_counts"][0]+1))

    def test_continuum_and_empty_finite_sets_never_alias(self):
        zeros=self.sources[CONTINUUM_ID]["zero_set"]
        self.assertEqual(zeros["kind"],"CLOSED_CONTINUUM_ZERO_COMPONENT")
        self.assertIs(zeros["every_closed_source_point_is_zero"],True)
        self.assertIs(zeros["isolated_root_count"],None)
        self.assertIs(zeros["events"],None)
        self.assertIs(zeros["maximal_nonzero_cells"],None)
        for flag in ("finite_event_list_applicable","nonzero_sign_cells_applicable","vanishing_orders_applicable"):
            self.assertIs(zeros[flag],False)
        for cid,sign in ((POSITIVE_ID,1),(NEGATIVE_ID,-1)):
            finite=self.sources[cid]["zero_set"]
            self.assertEqual(finite["kind"],"FINITE_ORIGINAL_SOURCE_ZERO_SET")
            self.assertEqual(finite["isolated_root_count"],0)
            self.assertEqual(finite["events"],[])
            self.assertEqual(len(finite["maximal_nonzero_cells"]),1)
            cell=finite["maximal_nonzero_cells"][0]
            self.assertEqual(cell["sign"],sign)
            self.assertIs(cell["left_included"],True)
            self.assertIs(cell["right_included"],True)
            self.semantic_rejects(cid,lambda s:s.__setitem__("kind","CLOSED_CONTINUUM_ZERO_COMPONENT"))
        for change in (lambda s:s.__setitem__("kind","FINITE"),
                       lambda s:s.__setitem__("every_closed_source_point_is_zero",False),
                       lambda s:s.__setitem__("isolated_root_count",0),
                       lambda s:s.__setitem__("events",[]),
                       lambda s:s.__setitem__("nonzero_sign_cells_applicable",True)):
            self.semantic_rejects(CONTINUUM_ID,change)

    def test_v44_cut_geometry_never_becomes_physical_events_or_cell_boundaries(self):
        raw=self.views[V44_ID]
        self.assertIs(raw["all_proof_cuts_are_event_neutral"],True)
        self.assertIs(raw["root_count_conserved_across_proof_cells"],True)
        self.assertIs(raw["algebraic_cut_is_physical_event"],False)
        self.assertEqual(raw["algebraic_cut_physical_multiplicity"],0)
        self.assertTrue(raw["proof_cut_relations"])
        self.assertTrue(all(p["proof_cut_is_physical_event"] is False for p in raw["proof_cut_relations"]))
        zeros=self.sources[V44_ID]["zero_set"]
        self.assertEqual(len(zeros["events"]),1)
        root=zeros["events"][0]
        self.assertEqual(root["coordinate"]["strict_open_bracket"],["9/16","37/64"])
        self.assertEqual(root["order"],{"kind":"SMOOTH","value":1})
        self.assertEqual([c["sign"] for c in zeros["maximal_nonzero_cells"]],[-1,1])
        self.assertEqual(len(zeros["maximal_nonzero_cells"]),2)
        self.semantic_rejects(V44_ID,lambda s:s.__setitem__("proof_cuts_event_neutral",False))
        self.semantic_rejects(V44_ID,lambda s:s["events"][0].__setitem__("coordinate",copy.deepcopy(raw["proof_cut_relations"][0]["coordinate"])))
        self.semantic_rejects(V44_ID,lambda s:s["events"][0].__setitem__("coordinate",{"kind":"ISOLATED_REAL_ROOT","polynomial":["-1","0","2"],"isolating_interval":["2/3","3/4"]}))
        changed=copy.deepcopy(raw);changed["all_proof_cuts_are_event_neutral"]=False
        with self.assertRaises(model.Refusal):
            model.adapt_source(V44_ID,self.originals[V44_ID],self.receipts[V44_ID],changed,self.auxiliary)

    def test_original_source_phase_row_and_raw_proof_substitution_refuse(self):
        cid=V13_MULT
        for change in (lambda r:r["spec"].__setitem__("source_parameter_id","another-clock"),
                       lambda r:r["spec"].__setitem__("phase_turn_rate","1/8"),
                       lambda r:r["spec"].__setitem__("parameter_hi","3"),
                       lambda r:r.__setitem__("origin","invented-producer"),
                       lambda r:r["expected"].__setitem__("v54_disposition","CERTIFIED")):
            changed=copy.deepcopy(self.originals[cid]);change(changed)
            with self.subTest(change=change),self.assertRaises(model.Refusal):
                model.adapt_source(cid,changed,self.receipts[cid],self.views[cid],self.auxiliary)
        for substitute in (V17_MULT,V41_ID):
            with self.subTest(substitute=substitute),self.assertRaises(model.Refusal):
                model.adapt_source(cid,self.originals[cid],self.receipts[cid],self.views[substitute],self.auxiliary)
        for field,value in (("source_sha256","0"*64),("original_row_sha256","0"*64),
                            ("producer","trig_fixed"),("replayed_result_sha256","0"*64),
                            ("covered_original_source_interval",["1","2"]),
                            ("complete_original_source_zero_set",False)):
            changed=copy.deepcopy(self.receipts[cid]);changed[field]=value
            with self.subTest(field=field),self.assertRaises(model.Refusal):
                model.adapt_source(cid,self.originals[cid],changed,self.views[cid],self.auxiliary)

    def test_v27_requires_closed_exterior_supplement_without_changing_open_root_digest(self):
        receipt=self.receipts[V27_100]
        digest=receipt["replayed_result_sha256"]
        self.assertEqual(self.views[V27_100]["distinct_open_roots_proved_for_this_fixed_source"],2)
        for change in (lambda r:r.__setitem__("supplemental_closed_endpoint_evidence",None),
                       lambda r:r["supplemental_closed_endpoint_evidence"]["endpoints"].pop(),
                       lambda r:r["supplemental_closed_endpoint_evidence"]["endpoints"][0].__setitem__("is_physical_zero",True),
                       lambda r:r["supplemental_closed_endpoint_evidence"]["endpoints"][1]["value"].__setitem__("sqrt_3_coefficient","-3")):
            changed=copy.deepcopy(receipt);change(changed)
            self.assertEqual(changed["replayed_result_sha256"],digest)
            with self.subTest(change=change),self.assertRaises(model.Refusal):
                model.adapt_source(V27_100,self.originals[V27_100],changed,self.views[V27_100],self.auxiliary)
        exterior=self.sources[V27_100]["zero_set"]["exterior_points"]
        self.assertEqual([e["value_sign"] for e in exterior],[1,1])
        self.assertEqual([e["value_sign"] for e in self.sources[V41_ID]["zero_set"]["exterior_points"]],[-1,-1])

    def test_auxiliary_original_endpoint_reports_have_checked_provenance(self):
        self.assertEqual(set(self.auxiliary),{"V27_THREE","V6_KNOT","V9_V43"})
        snapshots={r["path"]:r["git_blob"] for r in self.replay["runtime_attestation"]["snapshots"]}
        for key,aux in self.auxiliary.items():
            self.assertEqual(aux["git_blob"],snapshots[aux["path"]])
            self.assertGreater(aux["replayed_read_count"],0)
            self.assertIs(type(aux["replayed_read_count"]),int)
            self.assertIs(type(aux["report"]),dict)
        for key,cid in (("V27_THREE",V8_0),("V6_KNOT",V6_100),("V9_V43","composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail100")):
            for field,value in (("git_blob","0"*40),("replayed_read_count",0),("path","unlisted.json")):
                changed=copy.deepcopy(self.auxiliary);changed[key][field]=value
                with self.subTest(key=key,field=field),self.assertRaises(model.Refusal):
                    model.adapt_source(cid,self.originals[cid],self.receipts[cid],self.views[cid],changed)
        # Actual auxiliary endpoint evidence is tested directly, independently
        # of the compact normalized five-source event list.
        changed=copy.deepcopy(self.auxiliary)
        changed["V6_KNOT"]["report"]["proof"]["exact_exterior_values"] = {"forged":"zero"}
        with self.assertRaises(model.Refusal):
            model.adapt_source(V6_100,self.originals[V6_100],self.receipts[V6_100],self.views[V6_100],changed)

    def test_sign_order_count_and_boolean_aliases_refuse_at_semantic_boundary(self):
        for field,value in (("closed_count",True),("source_open_count",True),("complete",1),
                            ("proof_cuts_event_neutral",1)):
            self.semantic_rejects(V8_100,lambda s,field=field,value=value:s.__setitem__(field,value))
        for change in (lambda s:s["events"][0].__setitem__("left_sign",True),
                       lambda s:s["events"][0].__setitem__("right_sign",0),
                       lambda s:s["events"][0]["order"].__setitem__("value",True),
                       lambda s:s["events"][0]["order"].__setitem__("value",0),
                       lambda s:s["endpoints"][0].__setitem__("is_zero",0),
                       lambda s:s["span_open_counts"].__setitem__(0,True),
                       lambda s:s["cell_signs"].__setitem__(0,True)):
            self.semantic_rejects(V8_100,change)
        self.semantic_rejects(V6_100,lambda s:s["events"][0]["order"].__setitem__("left",True))

    def test_rational_lexical_and_operand_bounds_precede_fraction(self):
        bad=(True,1,0.5,None,"","1e1000000000","0.25","+1","01","--1","1/-2","1/0",
             " 1","\uff11","9"*129,str(1<<256),"1/"+str(1<<256))
        with mock.patch.object(model,"Fraction",side_effect=AssertionError("unsafe rational construction")) as fraction:
            for value in bad:
                with self.subTest(value=str(value)[:25]),self.assertRaises(model.Refusal):model.rational(value)
            fraction.assert_not_called()
        for value in ("0","1","-3","1/2","-2/3",str((1<<255)-1)):
            self.assertEqual(model.rational(value),Q(value))
        for value in ("-0","2/4","1/1","0/2"):
            with self.subTest(noncanonical=value),self.assertRaises(model.Refusal):model.rational(value)

    def test_direct_semantic_coordinate_guards_block_exponent_expansion(self):
        def safe_fraction(*operands):
            self.assertTrue(all(type(v) is int and v.bit_length()<=256 for v in operands),operands)
            return Q(*operands)
        changes=[(V8_100,lambda s:s["events"][0]["coordinate"].__setitem__("value","1e1000000000")),
                 (V13_MULT,lambda s:s["events"][0]["coordinate"].__setitem__("lower","1e1000000000")),
                 (V13_MULT,lambda s:s["events"][0]["coordinate"].__setitem__("upper","1e1000000000")),
                 (V8_100,lambda s:s["endpoints"][0].__setitem__("coordinate","1e1000000000")),
                 (V6_100,lambda s:s["knots"][0].__setitem__("coordinate","1e1000000000"))]
        for cid,change in changes:
            with self.subTest(case=cid,change=change),mock.patch.object(model,"Fraction",side_effect=safe_fraction):
                self.semantic_rejects(cid,change)

    def test_public_report_preflight_happens_before_replay_or_rational_parsing(self):
        cycle=[];cycle.append(cycle)
        deep=None
        for _ in range(100):deep=[deep]
        class Alias(str):pass
        bad=(cycle,deep,"x"*(4*1024*1024),1<<4097,float("nan"),float("inf"),1.5,
             {"x":object()},Alias("1"),{1:"invalid key"})
        with mock.patch.object(model,"expected_report",side_effect=AssertionError("unbounded public input replayed")) as replay, \
             mock.patch.object(model,"Fraction",side_effect=AssertionError("unbounded input parsed as rational")) as fraction:
            for candidate in bad:
                with self.subTest(kind=type(candidate).__name__),self.assertRaises(model.Refusal):
                    model.validate_report(candidate)
            replay.assert_not_called();fraction.assert_not_called()

    def test_report_reader_rejects_duplicate_nonexact_invalid_and_oversized_inputs(self):
        with tempfile.TemporaryDirectory(prefix="fifty-source-report-") as directory:
            path=Path(directory)/"report.json"
            for raw in (b'{"x":1,"x":2}',b'{"x":1.0}',b'{"x":NaN}',b'{"x":1e999999}',
                        b'{"x":'+b'9'*5000+b'}',b'\xff',b'['*2000+b']'*2000):
                path.write_bytes(raw)
                with self.subTest(raw=raw[:30]),self.assertRaises(model.Refusal):model.read_report(path)
            with path.open("wb") as stream:stream.truncate(4*1024*1024+1)
            with self.assertRaises(model.Refusal):model.read_report(path)

    def test_report_path_text_is_bounded_before_any_file_read(self):
        class Alias(str):pass
        for path in ("x"*4097,Path("x"*4097),"broken\0path",Path("broken\0path"),
                     Alias("report.json"),None,True,1):
            with self.subTest(kind=type(path).__name__), \
                 mock.patch.object(model,"_read_bounded",side_effect=AssertionError("unchecked path reached filesystem")) as read:
                with self.assertRaises(model.Refusal):model.read_report(path)
                read.assert_not_called()
        with tempfile.TemporaryDirectory(prefix="fifty-source-missing-report-") as directory:
            with self.assertRaises(model.Refusal):model.read_report(Path(directory)/"missing.json")

    def test_unsupported_public_source_ids_are_nontruth_without_replay(self):
        cycle=[];cycle.append(cycle)
        with mock.patch.object(model,"replay_qualified_sources",side_effect=AssertionError("unsupported source replayed")) as replay:
            for cid in ("unlisted-source",True,1,None,"x"*10000,cycle):
                with self.subTest(kind=type(cid).__name__):
                    result=model.consume_original_source(cid)
                    self.assertEqual(result["status"],"REFUSED")
                    self.assertIs(result["proof_established"],False)
                    self.assertIs(result["finite_zero_set_claimed"],False)
                    self.assertNotIn("zero_set",result)
            replay.assert_not_called()

    def test_public_selection_uses_the_fresh_source_result_without_another_proof_pass(self):
        # Reuse this invocation's already proved bundle solely to exercise
        # selection; the actual successful all50 replay occurred in setup.
        with mock.patch.object(model,"replay_qualified_sources",return_value=copy.deepcopy(self.replay)) as replay:
            result=model.consume_original_source(V8_100)
        self.assertEqual(model.bounded_bytes(result),model.bounded_bytes(self.sources[V8_100]))
        self.assertEqual(replay.call_count,1)

    def test_actual_producer_failure_is_nontruth_and_never_root_free_fallback(self):
        v2=model.qualified_v2_module();runtime_module=v2._runtime_module()
        original_load=runtime_module.PinnedRuntime.load
        invoked=[]
        def refuse():
            invoked.append(True)
            raise RuntimeError("CONTROLLED_ACTUAL_PHYSICAL_SOURCE_PROOF_FAILURE")
        def load(runtime,path):
            module=original_load(runtime,path)
            if Path(str(path)).name==v2.PRODUCERS["five"][0]:module.expected_report=refuse
            return module
        with mock.patch.object(model,"qualified_v2_module",return_value=v2), \
             mock.patch.object(v2,"_runtime_module",return_value=runtime_module), \
             mock.patch.object(runtime_module.PinnedRuntime,"load",autospec=True,side_effect=load):
            with self.assertRaises(model.Refusal):model.expected_report()
            result=model.consume_original_source(V8_100)
        self.assertEqual(invoked,[True,True])
        self.assertEqual(result["status"],"REFUSED")
        self.assertIs(result["proof_established"],False)
        self.assertIs(result["finite_zero_set_claimed"],False)
        self.assertNotIn("zero_set",result)

    def test_report_forgeries_cannot_promote_scope_or_preserve_a_wrong_zero_set(self):
        self.report_rejects(lambda r:r["source_cases"].pop())
        self.report_rejects(lambda r:r["source_cases"].append(copy.deepcopy(r["source_cases"][0])))
        def exchange(r):
            a,b=r["source_cases"][:2]
            a["zero_set"],b["zero_set"]=b["zero_set"],a["zero_set"]
        self.report_rejects(exchange)
        self.report_rejects(lambda r:r["source_cases"][0].__setitem__("source_sha256","0"*64))
        self.report_rejects(lambda r:r["source_cases"][0]["zero_set"].__setitem__("isolated_root_count",True))
        self.report_rejects(lambda r:r["gates"].__setitem__("production_authorized",True))
        self.report_rejects(lambda r:r["gates"].__setitem__("MC-B","ACCEPTED"))
        self.report_rejects(lambda r:r["gates"].__setitem__("MC-1","ACCEPTED"))
        self.report_rejects(lambda r:r["gates"].__setitem__("PB-007-01","CLOSED"))

    def test_actual_qualified_v2_source_beats_valid_cache_and_preload(self):
        trusted=(model.ROOT/model.V2_MODEL).read_bytes()
        self.assertEqual(bootstrap_blob(trusted),model.V2_BLOB)
        payload=b"CACHE_SUBSTITUTION = True\n#"
        altered=payload+b" "*(len(trusted)-len(payload))
        with tempfile.TemporaryDirectory(prefix="fifty-source-v2-cache-") as directory:
            root=Path(directory)
            path=root/model.V2_MODEL
            path.parent.mkdir(parents=True)
            ordinary=install_accepted_stale_cache(path,trusted,altered)
            self.assertTrue(ordinary.CACHE_SUBSTITUTION)
            private_name="_qualified_pb00701_v2_"+model.V2_BLOB
            fake=types.ModuleType(private_name)
            fake.CACHE_SUBSTITUTION=True
            with mock.patch.object(model,"ROOT",root), \
                 mock.patch.dict(sys.modules,{private_name:fake,path.stem:fake}):
                checked=model.qualified_v2_module()
                self.assertFalse(hasattr(checked,"CACHE_SUBSTITUTION"))
                self.assertTrue(callable(checked.replay_sources))
                self.assertEqual(checked.PINS,model.V2_PINS)
                self.assertIs(sys.modules[private_name],fake)
                self.assertIs(sys.modules[path.stem],fake)

    def test_qualified_v2_execution_uses_retained_checked_source_buffer(self):
        trusted=(model.ROOT/model.V2_MODEL).read_bytes()
        with tempfile.TemporaryDirectory(prefix="fifty-source-v2-buffer-") as directory:
            root=Path(directory);path=root/model.V2_MODEL
            path.parent.mkdir(parents=True);path.write_bytes(trusted)
            compiled=[]
            def replace_after_read(raw,filename,mode,**options):
                self.assertEqual(raw,trusted)
                compiled.append(raw)
                path.write_bytes(b"CACHE_SUBSTITUTION = True\n")
                return builtins.compile(raw,filename,mode,**options)
            with mock.patch.object(model,"ROOT",root), \
                 mock.patch.dict(model.__dict__,{"compile":mock.Mock(side_effect=replace_after_read)}):
                checked=model.qualified_v2_module()
                self.assertFalse(hasattr(checked,"CACHE_SUBSTITUTION"))
                self.assertEqual(checked.PINS,model.V2_PINS)
                with self.assertRaises(model.Refusal):model.qualified_v2_module()
            self.assertEqual(len(compiled),1)

    def test_qualified_v2_drift_resource_and_path_checks_precede_compilation(self):
        with tempfile.TemporaryDirectory(prefix="fifty-source-v2-refusals-") as directory:
            root=Path(directory);path=root/model.V2_MODEL
            path.parent.mkdir(parents=True)
            compiler=mock.Mock(side_effect=AssertionError("unchecked v2 source was compiled"))
            with mock.patch.object(model,"ROOT",root),mock.patch.dict(model.__dict__,{"compile":compiler}):
                path.write_bytes(b"UNREGISTERED = True\n")
                with self.assertRaises(model.Refusal):model.qualified_v2_module()
                with path.open("wb") as stream:stream.truncate(model.MAX_CODE_BYTES+1)
                with self.assertRaises(model.Refusal):model.qualified_v2_module()
                target=path.with_name("unlisted_v2.py")
                target.write_bytes(b"UNREGISTERED = True\n")
                path.unlink();path.symlink_to(target)
                with self.assertRaises(model.Refusal):model.qualified_v2_module()
                with self.assertRaises(model.Refusal):model._checked_buffer("unlisted.json","0"*40)
            compiler.assert_not_called()

    def test_pinned_json_parser_consumes_the_same_verified_original_buffer(self):
        trusted=(model.ROOT/model.V2_REPORT).read_bytes()
        expected=json.loads(trusted)
        original_read=model._read_bounded
        with tempfile.TemporaryDirectory(prefix="fifty-source-json-buffer-") as directory:
            root=Path(directory);path=root/model.V2_REPORT
            path.parent.mkdir(parents=True);path.write_bytes(trusted)
            def replace_after_read(requested,limit):
                raw=original_read(requested,limit)
                requested.write_bytes(b'{"forged_saved_PASS":true}')
                return raw
            with mock.patch.object(model,"ROOT",root), \
                 mock.patch.object(model,"_read_bounded",side_effect=replace_after_read):
                raw=model._checked_buffer(model.V2_REPORT,model.V2_REPORT_BLOB)
                self.assertEqual(model.parse_json_bytes(raw),expected)
                with self.assertRaises(model.Refusal):
                    model._checked_buffer(model.V2_REPORT,model.V2_REPORT_BLOB)

    def test_actual_saved_buffer_drift_aborts_before_proof_and_never_supplies_pass(self):
        original_read=model._read_bounded
        watched={model.V2_REPORT,model.AUX_PINS["V6_KNOT"][0]}
        for relative in watched:
            def drift(path,limit):
                if path==model.ROOT/relative:
                    return b'{"status":"PASS","complete_original_source_zero_set":true}'
                return original_read(path,limit)
            with self.subTest(path=relative), \
                 mock.patch.object(model,"_read_bounded",side_effect=drift), \
                 mock.patch.object(model,"qualified_v2_module",side_effect=AssertionError("drifted input reached replay")) as replay:
                with self.assertRaises(model.Refusal):model.expected_report()
                result=model.consume_original_source(V8_100)
                self.assertEqual(result["status"],"REFUSED")
                self.assertIs(result["proof_established"],False)
                self.assertIs(result["finite_zero_set_claimed"],False)
                self.assertNotIn("zero_set",result)
                replay.assert_not_called()

    def test_internal_formatter_cannot_rebind_qualified_census_or_byte_snapshot(self):
        changed=copy.deepcopy(self.replay)
        changed["v2_report"]["gates"]["production_authorized"]=True
        # A self-consistent caller digest cannot replace the qualified value.
        changed["v2_report_sha256"]=hashlib.sha256(model.bounded_bytes(changed["v2_report"])).hexdigest()
        with self.assertRaises(model.Refusal):model.report_from_replay(changed)
        changed=copy.deepcopy(self.replay)
        changed["runtime_attestation"]["snapshot_manifest_sha256"]="0"*64
        with self.assertRaises(model.Refusal):model.report_from_replay(changed)
        changed=copy.deepcopy(self.replay)
        changed["runtime_attestation"]["read_counts"][model.AUX_PINS["V6_KNOT"][0]]=0
        with self.assertRaises(model.Refusal):model.report_from_replay(changed)
        changed=copy.deepcopy(self.replay)
        changed["receipts"].pop(V30_ID)
        with self.assertRaises(model.Refusal):model.report_from_replay(changed)

    def test_actual_adapter_premise_failure_produces_public_nontruth(self):
        original=model.adapt_source
        invoked=[]
        def broken_piece_binding(cid,row,receipt,view,auxiliary):
            semantic=original(cid,row,receipt,view,auxiliary)
            if cid==V30_ID:
                invoked.append(cid)
                semantic["events"][1]["source_piece_index"]=0
            return semantic
        # The already fresh proof bundle is immutable evidence for this run;
        # only the actual adapter's second-span premise is faulted here.
        with mock.patch.object(model,"replay_qualified_sources",return_value=copy.deepcopy(self.replay)), \
             mock.patch.object(model,"adapt_source",side_effect=broken_piece_binding):
            with self.assertRaises(model.Refusal):model.expected_report()
            result=model.consume_original_source(V30_ID)
        self.assertEqual(invoked,[V30_ID,V30_ID])
        self.assertEqual(result["status"],"REFUSED")
        self.assertIs(result["proof_established"],False)
        self.assertIs(result["finite_zero_set_claimed"],False)
        self.assertNotIn("zero_set",result)

    def test_fresh_transitive_byte_custody_matches_exact_workflow_dependency_closure(self):
        snapshot=self.replay["runtime_attestation"]
        self.assertEqual({entry["path"]:entry["git_blob"] for entry in snapshot["snapshots"]},model.V2_PINS)
        self.assertEqual(snapshot["declared_code_paths"],77)
        self.assertEqual(snapshot["declared_data_paths"],19)
        expected=dict(model.V2_PINS)
        expected.update({model.V2_MODEL:model.V2_BLOB,model.V2_REPORT:model.V2_REPORT_BLOB,
                         model.RUNTIME_FILE:model.RUNTIME_BLOB})
        self.assertEqual(model.DEPENDENCY_PINS,expected)
        self.assertEqual(len(expected),99)
        for key,(path,blob) in model.AUX_PINS.items():
            self.assertEqual(expected[path],blob,key)
        own={model.TASK_DIR+name for name in (
            "pb00701_fifty_source_zero_set_consumer.py",
            "verify_pb00701_fifty_source_zero_set_consumer.py",
            "pb00701-fifty-source-zero-set-consumer.json",
            "pb00701-fifty-source-zero-set-consumer-research.md")}
        workflow_path=".github/workflows/mc1-pb00701-fifty-source-zero-set-consumer.yml"
        own.add(workflow_path)
        text=(model.ROOT/workflow_path).read_text()
        before_push,after_push=text.split("  push:",1)
        for section in (before_push,after_push):
            paths=re.findall(r"^      - ['\"]([^'\"]+)['\"]$",section,re.M)
            self.assertEqual(set(paths),set(expected)|own)
            self.assertEqual(len(paths),104)
        self.assertNotIn("strategy:",text)
        self.assertIn("github.event.pull_request.head.sha || github.sha",text)
        self.assertIn("verify_pb00701_fifty_source_zero_set_consumer.py --contract --self-test",text)
        report=json.loads(self.expected_bytes)
        custody=report["executed_byte_custody"]
        self.assertEqual(custody["dependency_path_count"],99)
        self.assertIs(custody["python_and_standard_library_trusted"],True)
        self.assertIs(custody["hostile_python_sandbox_claimed"],False)


def test_suite(replay=None):
    FiftySourceTests.replay=replay
    classes=(FiftySourceTests,build_bootstrap_tests(MODEL_PATH,MODEL_BLOB))
    loader=unittest.defaultTestLoader
    return unittest.TestSuite(loader.loadTestsFromTestCase(cls) for cls in classes)


def load_tests(loader,tests,pattern):
    # Ordinary unittest entry follows the same one-successful-replay rule.
    return test_suite()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract",action="store_true")
    parser.add_argument("--self-test",action="store_true")
    options=parser.parse_args()
    if not (options.contract or options.self_test):
        parser.error("choose --contract and/or --self-test")
    replay=model.replay_qualified_sources()
    expected_bytes=model.bounded_bytes(model.report_from_replay(replay))
    if options.contract:
        model._compare_with_replayed_bytes(model.read_report(),expected_bytes)
        print("PASS: fresh original-source proofs normalize 49 finite zero sets and one typed continuum")
        print("PASS: physical events retain original-source identity, order, knot and exterior semantics")
        print("PASS: cells partition only at physical zeros; historical dispositions and gates are unchanged")
    if options.self_test:
        result=unittest.TextTestRunner(verbosity=2).run(test_suite(replay))
        if not result.wasSuccessful():raise SystemExit(1)


if __name__=="__main__":
    main()
