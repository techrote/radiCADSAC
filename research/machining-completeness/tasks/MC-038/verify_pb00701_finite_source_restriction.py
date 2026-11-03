#!/usr/bin/env python3
"""Independent closed-source restriction, child-germ and recomposition checks.

One actual full qualified-refiner replay supplies all fifty original zero sets.
Independent exact comparisons and child/cell reconstruction verify the complete
restricted records before counts. Synthetic counterexamples never admit sources.
"""
from __future__ import annotations

import argparse
import builtins
from collections import Counter, defaultdict
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
MODEL_PATH = HERE / "pb00701_finite_source_restriction.py"
MODEL_BLOB = "c7e3953425ad1e981b78482c0783cb50f483600b"
RUNTIME_PATH = TASK + "pb00701_pinned_source_runtime.py"
RUNTIME_BLOB = "058c06e4a1e0aee0297880622ee1157a46ef9067"
LOWERER_PATH = TASK + "pb00701_coupled_bspline_model.py"
LOWERER_BLOB = "a086b625e1a6dea8bd202699d161167bb69cc9e7"
TRIG_PATH = TASK + "pb00701_transverse_trig_interval.py"
TRIG_BLOB = "2320f92efe4316d865a89f6d848737e2c000ca4d"
REFINER_PATH = TASK + "pb00701_selected_implicit_root_refinement.py"
REFINER_BLOB = "47dfd31a204d6edfb5fb2a82d7ce84c565aca7da"

V6_0 = "composite:DELEGATED_V6_CONSTANT_MODULATION:tail0"
V6_100 = "composite:DELEGATED_V6_CONSTANT_MODULATION:tail100"
V8_0 = "composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail0"
V8_100 = "composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail100"
V9_EXTERIOR = "harvested:verify_pb00701_v9:1a5fd052a155"
V23_EXTERIOR = "harvested:verify_pb00701_v52:2250401ce435"
CONTINUUM_ID = "harvested:verify_pb00701_v53:cb01c327d5f1"
V44_ID = "harvested:verify_pb00701_v44:ffaea08e30c9"
V10_0 = "composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail0"
V17_100 = "composite:PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER:tail100"
V13_100 = "composite:PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC:tail100"

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
    module = types.ModuleType("finite_restriction_reviewed_model")
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
            with tempfile.TemporaryDirectory(prefix="finite-restriction-cache-") as directory:
                here = Path(directory) / TASK
                here.mkdir(parents=True)
                path = here / Path(model_path).name
                ordinary = install_accepted_stale_cache(path, trusted, altered)
                self.assertTrue(ordinary.CACHE_SUBSTITUTION)
                fake = types.ModuleType("finite_restriction_reviewed_model")
                fake.CACHE_SUBSTITUTION = True
                with mock.patch.dict(sys.modules, {fake.__name__: fake, Path(model_path).stem: fake}):
                    checked = load_reviewed_model(path, model_blob)
                    self.assertFalse(hasattr(checked, "CACHE_SUBSTITUTION"))
                    self.assertTrue(callable(checked.expected_report))
                    self.assertIs(sys.modules[fake.__name__], fake)

        def test_checked_buffer_survives_posthash_path_replacement(self):
            with tempfile.TemporaryDirectory(prefix="finite-restriction-replace-") as directory:
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
            with tempfile.TemporaryDirectory(prefix="finite-restriction-bounds-") as directory:
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
            with tempfile.TemporaryDirectory(prefix="finite-restriction-flags-") as directory:
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

def read_pinned_runtime():
    path = ROOT / RUNTIME_PATH
    with path.open("rb") as stream:
        raw = stream.read(1048577)
    if len(raw) > 1048576 or git_blob(raw) != RUNTIME_BLOB:
        raise AssertionError("independent runtime source drift")
    module = types.ModuleType("independent_finite_restriction_runtime")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec", dont_inherit=True, optimize=0), module.__dict__)
    return module

def polynomial_value(coefficients, x):
    result = Q(0)
    for coefficient in reversed(coefficients):
        result = result * x + coefficient
    return result


def independent_default_cuts(source):
    a,b=map(Q,source["source_interval"])
    cuts={a+(b-a)*Q(i,4) for i in (1,2,3)}
    cuts.update(map(Q,source["original_source_piece_edges"][1:-1]))
    zeros=source["zero_set"]
    if zeros["kind"]=="FINITE_ORIGINAL_SOURCE_ZERO_SET":
        implicit=[e for e in zeros["events"]
                  if e["coordinate"]["kind"]=="UNIQUE_IMPLICIT_ZERO_OF_PINNED_ORIGINAL_SOURCE"]
        if implicit:
            lo,hi=map(Q,implicit[0]["coordinate"]["strict_open_bracket"])
            cuts.add((lo+hi)/2)
    return list(map(str,sorted(cuts)))


def strict_sign(interval):
    return 1 if interval[0]>0 else -1 if interval[1]<0 else 0


class IndependentPointOracle:
    """Symbolic coefficient lowering, separate from the new point consumer."""
    def __init__(self,pins):
        self.runtime=read_pinned_runtime().PinnedRuntime(ROOT,pins,
            {"radicadsac_mc032_event_engine":"research/machining-completeness/tasks/MC-032/event_engine.py"})
        self.parts={}
        self.points={}
        self.amplitudes={}
        self.amplitude_count=0

    def __enter__(self):
        self.runtime.__enter__()
        self.lower=self.runtime.load(LOWERER_PATH)
        self.trig=self.runtime.load(TRIG_PATH)
        return self

    def __exit__(self,*args):
        return self.runtime.__exit__(*args)

    def point(self,source,original,event,coordinate):
        q=Q(coordinate);cid=source["case_id"];key=cid,str(q)
        if key in self.points:return self.points[key]
        spec=original["spec"]
        if cid not in self.parts:
            parts={}
            for channel in ("cos_splines","sin_splines"):
                for harmonic,spline in spec[channel].items():
                    lowered=self.lower.lower_bspline(spline)
                    for a,b in zip(lowered,lowered[1:]):
                        if a["right_limit"]!=b["left_limit"]:
                            raise AssertionError("original coefficient discontinuity")
                    parts[channel,harmonic]=lowered
            self.parts[cid]=parts
        span=list(map(Q,event["coordinate"]["source_span"]))
        phase=Q(spec["phase_turn_offset"])+Q(spec["phase_turn_rate"])*q
        lo=hi=Q(0);values={}
        for (channel,harmonic),parts in self.parts[cid].items():
            selected=[p for p in parts if p["source_interval"][0]<=span[0]<span[1]<=p["source_interval"][1]]
            if len(selected)!=1:raise AssertionError("coefficient piece is not the original source span")
            piece=selected[0];a,b=piece["source_interval"]
            amplitude=polynomial_value(piece["coefficients"],(q-a)/(b-a))
            values[channel,harmonic]=amplitude
            enclosure=self.trig.trig(int(harmonic)*phase)[0 if channel=="cos_splines" else 1]
            products=[amplitude*x for x in enclosure]
            lo+=min(products);hi+=max(products)
            self.amplitude_count+=1
        scale=1<<80
        outward=(Q((lo*scale).__floor__(),scale),Q((hi*scale).__ceil__(),scale))
        if strict_sign((lo,hi))!=strict_sign(outward) or not strict_sign(outward):
            raise AssertionError("independent cut sign is not strictly established")
        result={"coordinate":str(q),"source_spec_sha256":digest(spec),
                "sign":strict_sign(outward),"outward_dyadic_interval":list(map(str,outward))}
        self.points[key]=result
        self.amplitudes[key]=values
        return result


def independent_relation(source,original,event,coordinate,oracle):
    """Order first; signs only in the actual strict unique isolator."""
    q=Q(coordinate);c=event["coordinate"]
    if c["kind"]=="RATIONAL":
        root=Q(c["value"])
        return (root>q)-(root<q),"EXACT_RATIONAL_COMPARISON",None
    if c["kind"]!="UNIQUE_IMPLICIT_ZERO_OF_PINNED_ORIGINAL_SOURCE":
        raise AssertionError("unrecognized original locator")
    a,b=map(Q,c["strict_open_bracket"])
    if q<=a:return 1,"STRICT_ORIGINAL_BRACKET_BOUND",None
    if q>=b:return -1,"STRICT_ORIGINAL_BRACKET_BOUND",None
    point=oracle.point(source,original,event,q)
    if event["left_sign"]!=-event["right_sign"]:
        raise AssertionError("implicit simple event lacks opposite physical sides")
    return (1 if point["sign"]==event["left_sign"] else -1),"STRICT_ORIGINAL_POINT_AND_PARENT_UNIQUENESS",point


def relative_order(event,at_left,at_right):
    if at_left and at_right:raise AssertionError("empty child around a root")
    original=event["order"]
    if not(at_left or at_right):
        if original["kind"]=="ONE_SIDED":raise AssertionError("original exterior moved into child interior")
        return copy.deepcopy(original)
    side="RIGHT" if at_left else "LEFT"
    if original["kind"]=="KNOT_SIDED":value=original[side.lower()]
    elif original["kind"]=="ONE_SIDED":
        if original["side"]!=side:raise AssertionError("child requested nonexistent original outside germ")
        value=original["value"]
    else:
        if original["kind"]!="SMOOTH":raise AssertionError("unknown parent order")
        value=original["value"]
    return {"kind":"ONE_SIDED","side":side,"value":value,
            "outside_order":None,"global_smooth_multiplicity_claimed":False}


def original_root_boundary(source,event):
    return {"kind":"PHYSICAL_ZERO_EVENT","event_id":event["event_id"],
            "source_case_id":source["case_id"],"source_sha256":source["source_sha256"]}


def independent_child_records(source,original,cuts,oracle):
    """Intersect actual parent components with rational closed intervals.

    This does not use the candidate's comparison, projection, node partition or
    reconstruction functions. In particular every parent nonzero component is
    intersected separately, so an equal-sign touching pair cannot be coalesced.
    """
    bounds=list(map(Q,[source["source_interval"][0],*cuts,source["source_interval"][1]]))
    edges=list(map(Q,source["original_source_piece_edges"]))
    zero=source["zero_set"]
    binding={"source_case_id":source["case_id"],"source_sha256":source["source_sha256"],
             "original_row_sha256":source["original_row_sha256"],
             "source_parameter_id":source["source_parameter_id"],
             "phase_turn_law":copy.deepcopy(source["phase_turn_law"]),
             "original_source_interval":copy.deepcopy(source["source_interval"]),
             "original_source_piece_edges":copy.deepcopy(source["original_source_piece_edges"]),
             "parent_source_record_sha256":digest(source)}
    continuum=zero["kind"]=="CLOSED_CONTINUUM_ZERO_COMPONENT"
    events=[] if continuum else zero["events"]
    relation={}
    methods=Counter()
    coordinates=sorted(set(bounds)|set(edges))
    for event in events:
        for q in coordinates:
            item=independent_relation(source,original,event,q,oracle)
            relation[event["event_id"],str(q)]=item
            methods[item[1]]+=1
    by_id={e["event_id"]:e for e in events}
    cut_ids={str(q):"CUT_"+str(i) for i,q in enumerate(bounds[1:-1])}

    def compare_boundary(node,q):
        if node["kind"]=="PHYSICAL_ZERO_EVENT":
            return relation[node["event_id"],str(q)][0]
        coordinate=Q(node["coordinate"])
        return (coordinate>q)-(coordinate<q)

    def cut_boundary(q):
        if q==bounds[0] or q==bounds[-1]:
            return {"kind":"SOURCE_EXTERIOR","side":"LEFT" if q==bounds[0] else "RIGHT",
                    "coordinate":str(q)}
        return {"kind":"RATIONAL_PARTITION_CUT","cut_id":cut_ids[str(q)],
                "coordinate":str(q),"source_case_id":source["case_id"],
                "source_sha256":source["source_sha256"]}

    children=[]
    for index,(a,b) in enumerate(zip(bounds,bounds[1:])):
        child=copy.deepcopy(binding)
        child.update(child_id="CHILD_"+str(index),child_index=index,interval=[str(a),str(b)],
                     closed_interval=True,source_piece_indices=[i for i,(x,y) in enumerate(zip(edges,edges[1:]))
                                                                if max(a,x)<min(b,y)])
        if continuum:
            child.update(kind="CLOSED_CONTINUUM_ZERO_COMPONENT",every_child_point_is_zero=True,
                         cardinality="UNCOUNTABLY_INFINITE",finite_event_list_applicable=False,
                         closed_root_count=None,events=None,maximal_nonzero_cells=None,endpoint_states=None,
                         original_exterior_points=None,original_true_source_knots=None,
                         vanishing_orders_applicable=False,nonzero_sign_cells_applicable=False)
            children.append(child)
            continue
        projected=[]
        for e in events:
            left=relation[e["event_id"],str(a)][0]
            right=relation[e["event_id"],str(b)][0]
            if left<0 or right>0:continue
            c=e["coordinate"]
            if c["kind"]=="RATIONAL":locator=copy.deepcopy(c)
            else:
                x,y=map(Q,c["strict_open_bracket"])
                locator={"kind":"RESTRICTED_IMPLICIT_ZERO_OF_PINNED_ORIGINAL_SOURCE",
                         "source_case_id":source["case_id"],"parent_event_id":e["event_id"],
                         "source_sha256":source["source_sha256"],
                         "source_parameter_id":source["source_parameter_id"],
                         "source_piece_index":c["source_piece_index"],"source_span":copy.deepcopy(c["source_span"]),
                         "strict_open_bracket":[str(max(x,a)),str(min(y,b))],
                         "unique_simple_root_inherited":True,
                         "exact_rational_or_algebraic_root_coordinate_claimed":False}
            projected.append({"original_event":copy.deepcopy(e),"parent_event_id":e["event_id"],
                              "parent_event_sha256":digest(e),"parent_coordinate":copy.deepcopy(c),
                              "original_location":e["location"],"original_order":copy.deepcopy(e["order"]),
                              "child_locator":locator,
                              "child_location":"CHILD_LEFT_ENDPOINT" if left==0 else
                                               "CHILD_RIGHT_ENDPOINT" if right==0 else "CHILD_INTERIOR",
                              "child_order":relative_order(e,left==0,right==0),
                              "left_sign":None if left==0 else e["left_sign"],
                              "right_sign":None if right==0 else e["right_sign"]})
        cells=[]
        for parent in zero["maximal_nonzero_cells"]:
            left,right=parent["left_boundary"],parent["right_boundary"]
            if compare_boundary(left,b)>=0 or compare_boundary(right,a)<=0:continue
            keep_left=compare_boundary(left,a)>=0
            keep_right=compare_boundary(right,b)<=0
            pieces=[]
            for i,(x,y) in enumerate(zip(edges,edges[1:])):
                low,high=max(a,x),min(b,y)
                if low<high and compare_boundary(left,high)<0 and compare_boundary(right,low)>0:
                    pieces.append(i)
            cells.append({"cell_id":"CELL_"+str(len(cells)),"parent_cell_id":parent["cell_id"],
                          "left_boundary":copy.deepcopy(left) if keep_left else cut_boundary(a),
                          "right_boundary":copy.deepcopy(right) if keep_right else cut_boundary(b),
                          "left_included":parent["left_included"] if keep_left else True,
                          "right_included":parent["right_included"] if keep_right else True,
                          "sign":parent["sign"],"source_piece_indices":pieces,
                          "crossed_nonzero_source_knots":[k for k in parent["crossed_nonzero_source_knots"]
                                                         if a<Q(k)<b]})
        endpoints=[]
        knots={k["coordinate"]:k for k in zero["true_source_knots"]}
        for side,q,cell in (("LEFT",a,cells[0]),("RIGHT",b,cells[-1])):
            equality=[e for e in projected if relation[e["parent_event_id"],str(q)][0]==0]
            event=equality[0] if equality else None
            location=("ORIGINAL_LEFT_EXTERIOR" if q==bounds[0] else
                      "ORIGINAL_RIGHT_EXTERIOR" if q==bounds[-1] else
                      "ORIGINAL_SOURCE_KNOT" if str(q) in knots else "ARTIFICIAL_PARTITION_CUT")
            endpoints.append({"side":side,"coordinate":str(q),"included":True,
                              "original_point_location":location,"is_zero":event is not None,
                              "event_ref":event["parent_event_id"] if event else None,
                              "value_sign":0 if event else cell["sign"],
                              "inward_sign":(event["right_sign"] if side=="LEFT" else event["left_sign"])
                                            if event else cell["sign"],
                              "inward_order":event["child_order"]["value"] if event else 0,
                              "outside_order":None,"outside_sign":None,
                              "global_smooth_multiplicity_claimed":False})
        child.update(kind="FINITE_RESTRICTED_ORIGINAL_SOURCE_ZERO_SET",finite_event_list_applicable=True,
                     closed_root_count=len(projected),events=projected,maximal_nonzero_cells=cells,
                     endpoint_states=endpoints,
                     original_exterior_points=copy.deepcopy([p for p in zero["exterior_points"]
                                                             if a<=Q(p["coordinate"])<=b]),
                     original_true_source_knots=copy.deepcopy([p for p in zero["true_source_knots"]
                                                               if a<=Q(p["coordinate"])<=b]),
                     vanishing_orders_applicable=True,nonzero_sign_cells_applicable=True)
        children.append(child)
    return children,relation,methods


def independently_rejoin(source,children,cuts):
    """Build the physical zero set from actual children after membership checks."""
    if source["zero_set"]["kind"]=="CLOSED_CONTINUUM_ZERO_COMPONENT":
        return {"kind":"CLOSED_CONTINUUM_ZERO_COMPONENT","cardinality":"UNCOUNTABLY_INFINITE",
                "interval":[children[0]["interval"][0],children[-1]["interval"][1]],
                "closed_interval":True,"complete_for_original_closed_source":True,
                "every_closed_source_point_is_zero":True,"events":None,"isolated_root_count":None,
                "maximal_nonzero_cells":None,"finite_event_list_applicable":False,
                "nonzero_sign_cells_applicable":False,"vanishing_orders_applicable":False},None,None
    event_records={};exteriors={};knots={};groups=defaultdict(list);occurrences=Counter()
    for index,child in enumerate(children):
        for event in child["events"]:
            key=event["parent_event_id"];occurrences[key]+=1
            if key in event_records and canonical(event_records[key])!=canonical(event["original_event"]):
                raise AssertionError("closed duplicates disagree")
            event_records[key]=event["original_event"]
        for record in child["original_exterior_points"]:exteriors[record["side"]]=record
        for record in child["original_true_source_knots"]:knots[record["coordinate"]]=record
        for cell in child["maximal_nonzero_cells"]:groups[cell["parent_cell_id"]].append((index,cell))
    events=list(event_records.values());cells=[];joins=0;duplicates=0
    for event in events:
        c=event["coordinate"]
        on_cut=c["kind"]=="RATIONAL" and c["value"] in cuts
        if occurrences[event["event_id"]]!=1+on_cut:raise AssertionError("wrong per-event occurrence law")
        duplicates+=on_cut
    for key,group in groups.items():
        pieces=set();crossed=set();signs=set()
        for _,cell in group:
            pieces.update(cell["source_piece_indices"]);crossed.update(cell["crossed_nonzero_source_knots"])
            signs.add(cell["sign"])
        if len(signs)!=1:raise AssertionError("sign changes inside parent nonzero component")
        for (i,left),(j,right) in zip(group,group[1:]):
            if j!=i+1 or canonical(left["right_boundary"])!=canonical(right["left_boundary"]):
                raise AssertionError("nonadjacent cell fragment join")
            bound=left["right_boundary"]
            if bound["kind"]!="RATIONAL_PARTITION_CUT" or not(left["right_included"] and right["left_included"]):
                raise AssertionError("zero or excluded point incorrectly rejoined")
            if bound["coordinate"] in knots:
                knot=knots[bound["coordinate"]]
                if knot["is_zero"]:raise AssertionError("zero knot incorrectly rejoined")
                crossed.add(bound["coordinate"])
            joins+=1
        first,last=group[0][1],group[-1][1]
        cells.append({"cell_id":key,"left_boundary":first["left_boundary"],"right_boundary":last["right_boundary"],
                      "left_included":first["left_included"],"right_included":last["right_included"],
                      "sign":next(iter(signs)),"source_piece_indices":sorted(pieces),
                      "crossed_nonzero_source_knots":sorted(crossed,key=Q)})
    rebuilt={"kind":"FINITE_ORIGINAL_SOURCE_ZERO_SET","finite_event_list_applicable":True,
             "complete_for_original_closed_source":True,"isolated_root_count":len(events),
             "source_open_root_count":sum(e["location"] in ("SPAN_INTERIOR","SOURCE_KNOT") for e in events),
             "strict_span_open_root_counts":[sum(e["location"]=="SPAN_INTERIOR" and e["source_piece_indices"]==[i]
                                                  for e in events)
                                              for i in range(len(source["original_source_piece_edges"])-1)],
             "events":events,"exterior_points":[exteriors["LEFT"],exteriors["RIGHT"]],
             "true_source_knots":[knots[q] for q in sorted(knots,key=Q)],"maximal_nonzero_cells":cells,
             "nonzero_sign_cells_applicable":True,"nonzero_knots_and_proof_cuts_are_not_partition_boundaries":True,
             "global_cross_source_zero_deduplication_performed":False}
    return rebuilt,{"child_sum":sum(occurrences.values()),"cut_duplicates":duplicates,"parent_distinct":len(events)},\
        {"child_sum":sum(len(g) for g in groups.values()),"nonzero_joins":joins,"parent_cells":len(cells)}


class FiniteRestrictionTests(unittest.TestCase):
    replay=None
    report=None

    @classmethod
    def setUpClass(cls):
        if cls.replay is None:cls.replay=model.replay_restrictions()
        if cls.report is None:cls.report=model.report_from_replay(cls.replay)
        cls.expected_bytes=canonical(cls.report)
        cls.context=cls.replay["qualified_context"]
        cls.baseline=cls.context["refiner_report"]["parent_baseline"]
        cls.originals=cls.context["refiner_context"]["indexed"]
        cls.sources={s["case_id"]:s for s in cls.baseline["source_cases"]}
        cls.partitions={p["source_case_id"]:p for p in cls.replay["partitions"]}
        cls.provider=model.qualified_refiner_module()
        # The symbolic oracle needs the qualified refiner's original graph.
        # Its own later 1.7 MB trace report is not a runtime input; feeding that
        # unnecessary artifact to the older 1 MB/file runtime would refuse.
        cls.oracle=IndependentPointOracle(model.REFINER_PINS)
        cls.oracle.__enter__()
        cls.addClassCleanup(cls.oracle.__exit__,None,None,None)
        cls.projections={cid:independent_child_records(source,cls.originals[cid],independent_default_cuts(source),cls.oracle)
                         for cid,source in cls.sources.items()}

    def same(self,actual,expected,message=None):
        self.assertEqual(canonical(actual),canonical(expected),message)

    def nontruth(self,result):
        self.assertEqual(result["status"],"REFUSED")
        for key in ("proof_established","all_requested_children_established","parent_zero_set_replaced","production_authorized"):
            self.assertIs(result[key],False,key)
        for key in ("partition","partitions","children","successful_partial_count","parent_baseline"):
            self.assertNotIn(key,result)

    def partition_refuses(self,cid,mutate):
        partition=copy.deepcopy(self.partitions[cid])
        mutate(partition)
        with self.assertRaises(model.Refusal):
            model.recompose_source(self.sources[cid],self.originals[cid],partition["cuts"],
                                   partition["children"],partition["comparison_receipts"],provider=self.provider)

    def report_refuses(self,mutate):
        candidate=json.loads(self.expected_bytes)
        mutate(candidate)
        with self.assertRaises(model.Refusal):
            model._compare_with_replayed_bytes(candidate,self.expected_bytes)

    def custom(self,cid,cuts):
        partition=model.partition_source(self.sources[cid],self.originals[cid],cuts,provider=self.provider)
        expected,_,_=independent_child_records(self.sources[cid],self.originals[cid],cuts,self.oracle)
        self.same(partition["children"],expected)
        rebuilt,closed,cells=independently_rejoin(self.sources[cid],partition["children"],cuts)
        self.same(rebuilt,self.sources[cid]["zero_set"])
        self.same(partition["recomposition"]["closed_count_conservation"],closed)
        self.same(partition["recomposition"]["cell_rejoin_conservation"],cells)
        return partition

    def test_complete_fresh_population_and_source_phase_identity(self):
        self.assertEqual(len(self.originals),121)
        self.assertEqual(len(self.sources),50)
        self.assertEqual(list(self.sources),list(self.partitions))
        self.same(self.report["parent_baseline"],self.baseline)
        self.assertEqual(digest(self.baseline),model.PARENT_REPORT_VALUE_SHA256)
        self.assertEqual(digest(self.context["refiner_report"]),model.REFINER_REPORT_VALUE_SHA256)
        self.assertEqual(self.context["refiner_report"]["requested_steps"],12)
        self.assertEqual(len(self.context["refiner_report"]["refinements"]),69)
        self.same(model.SOURCE_RECORD_SHA256S,{cid:digest(s) for cid,s in self.sources.items()})
        self.same(model.SOURCE_INTERVALS,{cid:s["source_interval"] for cid,s in self.sources.items()})
        for cid,source in self.sources.items():
            original=self.originals[cid];spec=original["spec"];partition=self.partitions[cid]
            self.assertEqual(source["source_sha256"],digest(spec))
            self.assertEqual(source["original_row_sha256"],digest(original))
            self.assertEqual(source["source_parameter_id"],spec["source_parameter_id"])
            self.same(source["phase_turn_law"],{"offset":spec["phase_turn_offset"],"rate":spec["phase_turn_rate"]})
            self.same(source["source_interval"],[spec["parameter_lo"],spec["parameter_hi"]])
            for key in ("source_sha256","original_row_sha256","source_parameter_id","phase_turn_law"):
                self.same(partition[key],source[key],(cid,key))
            self.assertEqual(partition["parent_source_record_sha256"],digest(source))
        self.same(self.report["gates"],self.baseline["gates"])
        self.assertIs(self.report["scope"]["new_root_completeness_theorem"],False)
        self.assertIs(self.report["scope"]["generic_owner_route_repaired"],False)
        self.assertIs(self.report["scope"]["native_geometry_evidence"],False)

    def test_every_default_child_and_recomposition_from_independent_intersections(self):
        counts=Counter();methods=Counter()
        for cid,source in self.sources.items():
            partition=self.partitions[cid];cuts=independent_default_cuts(source)
            children,relations,source_methods=self.projections[cid]
            self.same(partition["cuts"],cuts,cid)
            self.same(model.default_cuts(source),cuts,cid)
            self.same(partition["children"],children,cid)
            expected_keys=[(e["event_id"],str(q)) for e in (source["zero_set"].get("events") or [])
                           for q in sorted(set(map(Q,[*source["source_interval"],*cuts,*source["original_source_piece_edges"]])))]
            receipts=partition["comparison_receipts"]
            self.assertEqual([(r["event_id"],r["cut"]) for r in receipts],expected_keys,cid)
            for receipt in receipts:
                event=next(e for e in source["zero_set"]["events"] if e["event_id"]==receipt["event_id"])
                relation,method,point=relations[receipt["event_id"],receipt["cut"]]
                self.assertIs(type(receipt["relation"]),int)
                self.assertEqual(receipt["relation"],relation,(cid,receipt["cut"]))
                self.assertEqual(receipt["method"],method)
                self.assertEqual(receipt["source_case_id"],cid)
                self.assertEqual(receipt["source_sha256"],source["source_sha256"])
                self.assertEqual(receipt["parent_event_sha256"],digest(event))
                evidence=receipt["evidence"]
                if point:
                    actual=evidence["point_receipt"]
                    for key,value in point.items():self.same(actual[key],value,(cid,key))
                    self.assertIs(actual["strict"],True)
                    self.assertEqual(actual["dyadic_bits"],80)
                    self.assertIs(actual["coordinate_is_original_parameter"],True)
                    self.assertIs(actual["exact_source_enclosure_is_contained"],True)
                    self.same(evidence["parent_uniqueness_evidence"],event["coordinate"]["uniqueness_evidence"])
                    self.assertEqual(evidence["parent_event_sha256"],digest(event))
                    self.same(evidence["original_strict_open_bracket"],event["coordinate"]["strict_open_bracket"])
                    self.assertIs(evidence["strictly_inside_original_bracket"],True)
                    self.assertIs(evidence["unique_simple_root_inherited"],True)
                elif method=="STRICT_ORIGINAL_BRACKET_BOUND":
                    equality=receipt["cut"] in event["coordinate"]["strict_open_bracket"]
                    self.assertIs(evidence["equals_open_bracket_boundary"],equality)
                    self.assertIs(evidence["open_bound_equality_is_not_root_equality"],True)
                    self.assertNotEqual(relation,0)
                    counts["open_equalities"]+=equality
                else:self.same(evidence,{"root":event["coordinate"]["value"],"cut":receipt["cut"]})
            rebuilt,closed,cell=independently_rejoin(source,partition["children"],cuts)
            self.same(rebuilt,source["zero_set"],cid)
            reconstruction=partition["recomposition"]
            self.same(reconstruction["recomposed_zero_set"],rebuilt,cid)
            self.assertIsNot(reconstruction["recomposed_zero_set"],source["zero_set"])
            self.assertEqual(reconstruction["recomposed_zero_set_sha256"],digest(rebuilt))
            self.same(reconstruction["closed_count_conservation"],closed)
            self.same(reconstruction["cell_rejoin_conservation"],cell)
            self.assertIs(reconstruction["reconstructed_from_actual_children"],True)
            self.assertIs(reconstruction["parent_zero_set_replaced"],False)
            counts["sources"]+=1;counts["cuts"]+=len(cuts);counts["children"]+=len(children)
            counts["maxcuts"]=max(counts["maxcuts"],len(cuts));methods.update(source_methods)
            if closed is None:
                counts["continuum_children"]+=len(children);counts["continuum_sources"]+=1
                continue
            counts["finite_sources"]+=1;counts["finite_children"]+=len(children);counts["finite_cuts"]+=len(cuts)
            counts["child_roots"]+=closed["child_sum"];counts["duplicates"]+=closed["cut_duplicates"]
            counts["parent_roots"]+=closed["parent_distinct"];counts["fragments"]+=cell["child_sum"]
            counts["joins"]+=cell["nonzero_joins"];counts["parent_cells"]+=cell["parent_cells"]
            counts["point_sources"]+=bool(source_methods["STRICT_ORIGINAL_POINT_AND_PARENT_UNIQUENESS"])
            for child in children:
                for event in child["events"]:
                    counts["interior_roots" if event["child_location"]=="CHILD_INTERIOR" else "boundary_roots"]+=1
                    if event["parent_coordinate"]["kind"]!="RATIONAL":
                        counts["clips"]+=event["parent_coordinate"]["strict_open_bracket"]!=event["child_locator"]["strict_open_bracket"]
        # These numerical checks follow all per-source mathematical identities.
        self.assertEqual(dict(counts),{"sources":50,"cuts":178,"children":228,"maxcuts":4,
            "finite_sources":49,"finite_children":224,"finite_cuts":175,"child_roots":91,
            "duplicates":10,"parent_roots":81,"fragments":293,"joins":165,"parent_cells":128,
            "point_sources":28,"interior_roots":69,"boundary_roots":22,"clips":28,
            "open_equalities":22,"continuum_sources":1,"continuum_children":4})
        self.same(self.report["comparison_methods"],dict(methods))
        self.assertEqual(dict(methods),{"EXACT_RATIONAL_COMPARISON":60,"STRICT_ORIGINAL_BRACKET_BOUND":386,
                                       "STRICT_ORIGINAL_POINT_AND_PARENT_UNIQUENESS":28})
        self.assertEqual((len(self.oracle.points),self.oracle.amplitude_count),(28,120))
        self.assertEqual(counts["child_roots"]-counts["duplicates"],counts["parent_roots"])
        self.assertEqual(counts["fragments"]-counts["joins"],counts["parent_cells"])
        self.assertEqual(counts["finite_children"]+counts["interior_roots"],counts["fragments"])
        summary={"original_sources":counts["sources"],"all_interior_cuts":counts["cuts"],
                 "closed_children":counts["children"],"maximum_cuts_per_source":counts["maxcuts"],
                 "finite_sources":counts["finite_sources"],"finite_children":counts["finite_children"],
                 "finite_interior_cuts":counts["finite_cuts"],"continuum_sources":counts["continuum_sources"],
                 "continuum_children":counts["continuum_children"],"child_closed_finite_zero_occurrences":counts["child_roots"],
                 "physical_zeros_on_interior_cuts":counts["duplicates"],"recomposed_finite_physical_zeros":counts["parent_roots"],
                 "restricted_maximal_nonzero_cells":counts["fragments"],"admissible_nonzero_cell_joins":counts["joins"],
                 "recomposed_maximal_nonzero_cells":counts["parent_cells"],
                 "nonzero_finite_cuts":counts["finite_cuts"]-counts["duplicates"],
                 "strict_point_comparisons":methods["STRICT_ORIGINAL_POINT_AND_PARENT_UNIQUENESS"],
                 "sources_needing_point_comparison":counts["point_sources"],
                 "strict_open_bound_equalities_not_root_equalities":counts["open_equalities"],
                 "child_relative_interior_zero_occurrences":counts["interior_roots"],
                 "child_relative_boundary_zero_occurrences":counts["boundary_roots"],
                 "implicit_child_locators_clipped":counts["clips"]}
        self.same(self.report["summary"],summary)

    def test_all_strict_point_amplitudes_match_independent_original_polynomials(self):
        count=0
        for (cid,coordinate),values in self.oracle.amplitudes.items():
            prepared=self.provider.prepare_source_spec(self.originals[cid]["spec"])
            channels={("cos_splines" if c.kind=="cos" else "sin_splines",str(c.harmonic)):c.spline
                      for c in prepared.channels}
            self.assertEqual(set(values),set(channels))
            for key,value in values.items():
                self.assertEqual(self.provider.spline_value(channels[key],Q(coordinate)),value,(cid,coordinate,key))
                count+=1
        self.assertEqual(count,120)

    def test_original_open_bracket_bounds_precede_point_evaluation(self):
        total=0
        with mock.patch.object(model,"point_receipt",side_effect=AssertionError("open bound incorrectly evaluated")) as point:
            for cid,source in self.sources.items():
                for event in source["zero_set"].get("events") or []:
                    if event["coordinate"]["kind"]=="RATIONAL":continue
                    for q,expected in zip(event["coordinate"]["strict_open_bracket"],(1,-1)):
                        result=model.compare_event_with_cut(source,self.originals[cid],event,q,provider=self.provider)
                        self.assertEqual(result["method"],"STRICT_ORIGINAL_BRACKET_BOUND")
                        self.assertEqual(result["relation"],expected)
                        self.assertIs(result["evidence"]["equals_open_bracket_boundary"],True)
                        total+=1
            point.assert_not_called()
        self.assertEqual(total,138)

    def test_repeated_sign_outside_unique_bracket_cannot_decide_root_order(self):
        f=lambda t:(t-Q(1,3))*(t-Q(2,3))
        root=Q(1,3);a=Q(1,4);b=Q(1,2);q=Q(3,4)
        self.assertTrue(a<root<b<q)
        self.assertGreater(f(a),0);self.assertLess(f(b),0);self.assertGreater(f(q),0)
        self.assertEqual((root>q)-(root<q),-1)
        # Real admitted locators exercise this ordering branch without accepting
        # the synthetic polynomial as a public source or proof premise.
        source=self.sources[V10_0];event=source["zero_set"]["events"][0]
        with mock.patch.object(model,"point_receipt",side_effect=AssertionError("outside point invoked")) as point:
            for q,expected in ((source["source_interval"][0],1),(source["source_interval"][1],-1)):
                self.assertEqual(model.compare_event_with_cut(source,self.originals[V10_0],event,q,
                                                              provider=self.provider)["relation"],expected)
            point.assert_not_called()

    def test_three_root_counterexample_requires_actual_inherited_uniqueness(self):
        f=lambda t:(t-Q(1,4))*(t-Q(1,2))*(t-Q(3,4))
        q=Q(2,3);root=Q(1,4)
        self.assertGreater(q,root)
        self.assertLess(f(Q(0)),0);self.assertGreater(f(Q(1)),0);self.assertLess(f(q),0)
        self.assertEqual([f(t) for t in (Q(1,4),Q(1,2),Q(3,4))],[0,0,0])
        source=self.sources[V10_0];original=self.originals[V10_0]
        event=source["zero_set"]["events"][0]
        mutations=(lambda e:e["coordinate"].pop("uniqueness_evidence"),
                   lambda e:e["coordinate"].__setitem__("strict_open_bracket",["0","1"]),
                   lambda e:e["coordinate"]["uniqueness_evidence"].__setitem__("producer","unexecuted"),
                   lambda e:e["order"].__setitem__("value",True))
        with mock.patch.object(model,"point_receipt",side_effect=AssertionError("unbound uniqueness reached point")) as point:
            for mutate in mutations:
                changed=copy.deepcopy(event);mutate(changed)
                with self.assertRaises(model.Refusal):
                    model.compare_event_with_cut(source,original,changed,"3/16",provider=self.provider)
            point.assert_not_called()

    def test_empty_and_custom_cuts_keep_interior_rational_and_nonsmooth_events(self):
        for cid in (V6_100,V8_0,V9_EXTERIOR,CONTINUUM_ID):
            with self.subTest(cid=cid):
                partition=self.custom(cid,[])
                self.assertEqual(len(partition["children"]),1)
        partition=self.custom(V6_100,["1/2","3/2"])
        knot=next(e for e in partition["children"][1]["events"] if e["original_location"]=="SOURCE_KNOT")
        self.assertEqual(knot["child_location"],"CHILD_INTERIOR")
        self.same(knot["child_order"],knot["original_order"])
        self.assertEqual(knot["child_order"]["kind"],"KNOT_SIDED")
        self.assertEqual((knot["left_sign"],knot["right_sign"]),(1,1))
        for cid in (V6_0,V8_100,V44_ID):self.custom(cid,["1/3"])
        self.custom(V8_0,["1/8","1/4","3/8","5/8","3/4","7/8"])

    def test_touching_knots_keep_separate_same_sign_components_and_inward_orders(self):
        for cid,order in ((V6_100,1),(V8_100,2)):
            partition=self.partitions[cid]
            shared=[e for c in partition["children"] for e in c["events"]
                    if e["child_location"]!="CHILD_INTERIOR"]
            self.assertEqual(len(shared),2)
            self.assertEqual([e["child_location"] for e in shared],["CHILD_RIGHT_ENDPOINT","CHILD_LEFT_ENDPOINT"])
            self.assertEqual([e["child_order"]["value"] for e in shared],[order,order])
            self.assertEqual([(e["left_sign"],e["right_sign"]) for e in shared],[(1,None),(None,1)])
            self.assertEqual(len(partition["recomposition"]["recomposed_zero_set"]["maximal_nonzero_cells"]),2)
        knot=next(e for e in self.sources[V6_100]["zero_set"]["events"] if e["location"]=="SOURCE_KNOT")
        self.assertEqual(knot["order"]["kind"],"KNOT_SIDED")
        self.assertIs(knot["order"]["global_smooth_multiplicity_claimed"],False)

    def test_original_exterior_zeros_keep_only_existing_inward_germ(self):
        for cid,order in ((V9_EXTERIOR,1),(V23_EXTERIOR,2)):
            child=self.partitions[cid]["children"][0]
            event=child["events"][0]
            self.assertEqual(event["original_location"],"SOURCE_LEFT_ENDPOINT")
            self.assertEqual(event["child_location"],"CHILD_LEFT_ENDPOINT")
            self.assertEqual(event["child_order"]["value"],order)
            self.assertEqual(event["child_order"]["side"],"RIGHT")
            self.assertIsNone(event["left_sign"])
            self.assertEqual(child["endpoint_states"][0]["inward_order"],order)
            self.assertFalse(child["maximal_nonzero_cells"][0]["left_included"])
            self.assertGreater(len(child["maximal_nonzero_cells"]),0)

    def test_implicit_locators_are_separate_clippings_with_source_identity(self):
        count=0
        for cid,partition in self.partitions.items():
            for child in partition["children"]:
                for projected in child["events"] or []:
                    parent=projected["parent_coordinate"]
                    self.same(parent,projected["original_event"]["coordinate"])
                    if parent["kind"]=="RATIONAL":continue
                    locator=projected["child_locator"];a,b=map(Q,child["interval"])
                    lo,hi=map(Q,locator["strict_open_bracket"])
                    self.assertTrue(a<=lo<hi<=b)
                    self.assertEqual(locator["source_case_id"],cid)
                    self.assertEqual(locator["parent_event_id"],projected["parent_event_id"])
                    self.assertIs(locator["exact_rational_or_algebraic_root_coordinate_claimed"],False)
                    count+=locator["strict_open_bracket"]!=parent["strict_open_bracket"]
        self.assertEqual(count,28)
        def unclip(partition):
            event=next(e for c in partition["children"] for e in c["events"]
                       if e["parent_coordinate"]["kind"]!="RATIONAL" and
                       e["parent_coordinate"]["strict_open_bracket"]!=e["child_locator"]["strict_open_bracket"])
            event["child_locator"]["strict_open_bracket"]=copy.deepcopy(event["parent_coordinate"]["strict_open_bracket"])
        self.partition_refuses(V10_0,unclip)

    def test_child_germ_mutations_refuse_even_when_parent_event_and_counts_survive(self):
        def change(field,value):
            def mutate(partition):
                event=next(e for c in partition["children"] for e in c["events"])
                before=digest(event["original_event"])
                event[field]=value
                self.assertEqual(digest(event["original_event"]),before)
            return mutate
        for field,value in (("child_location","CHILD_INTERIOR"),("left_sign",None),("right_sign",-1),
                            ("child_order",{"kind":"SMOOTH","value":1}),
                            ("child_order",{"kind":"ONE_SIDED","side":"RIGHT","value":1,
                                            "outside_order":None,"global_smooth_multiplicity_claimed":False})):
            with self.subTest(field=field,value=value):self.partition_refuses(V6_100,change(field,value))

    def test_closed_cut_duplicate_must_exist_in_each_correct_adjacent_child(self):
        def drop_occurrence(partition):
            seen=False
            for child in partition["children"]:
                if child["events"]:
                    if seen:
                        child["events"].pop(0);child["closed_root_count"]-=1;return
                    seen=True
        self.partition_refuses(V6_100,drop_occurrence)
        def relocate(partition):
            nonempty=[i for i,c in enumerate(partition["children"]) if c["events"]]
            moved=partition["children"][nonempty[0]]["events"].pop()
            partition["children"][nonempty[0]]["closed_root_count"]-=1
            other=next(i for i,c in enumerate(partition["children"]) if not c["events"] and i!=nonempty[0])
            partition["children"][other]["events"].append(moved)
            partition["children"][other]["closed_root_count"]+=1
        self.partition_refuses(V6_100,relocate)

    def test_count_preserving_event_swap_cannot_hide_a_lost_original_root(self):
        def duplicate(partition):
            records=[(c,e) for c in partition["children"] for e in c["events"]]
            first=records[0][1]
            child,event=next((c,e) for c,e in records if e["parent_event_id"]!=first["parent_event_id"])
            child["events"][child["events"].index(event)]=copy.deepcopy(first)
        self.partition_refuses(V8_0,duplicate)

    def test_same_sign_touch_cells_cannot_merge_across_physical_zero(self):
        def relabel(partition):
            for child in partition["children"]:
                for cell in child["maximal_nonzero_cells"]:
                    if cell["parent_cell_id"]=="CELL_1":cell["parent_cell_id"]="CELL_0"
        self.partition_refuses(V8_100,relabel)
        def suppress_touch(partition):
            for child in partition["children"]:
                for cell in child["maximal_nonzero_cells"]:
                    for side in ("left","right"):
                        if cell[side+"_boundary"]["kind"]=="PHYSICAL_ZERO_EVENT":
                            cell[side+"_included"]=True;return
        self.partition_refuses(V6_100,suppress_touch)

    def test_nonzero_closed_cut_membership_and_parent_component_identity_are_required(self):
        def exclude(partition):
            cell=next(cell for child in partition["children"] for cell in child["maximal_nonzero_cells"]
                      if cell["right_boundary"]["kind"]=="RATIONAL_PARTITION_CUT")
            cell["right_included"]=False
        self.partition_refuses(V8_100,exclude)
        def foreign(partition):
            cell=next(cell for child in partition["children"] for cell in child["maximal_nonzero_cells"]
                      if cell["right_boundary"]["kind"]=="RATIONAL_PARTITION_CUT")
            cell["right_boundary"]["source_case_id"]=V8_0
        self.partition_refuses(V8_100,foreign)
        def sign(partition):partition["children"][0]["maximal_nonzero_cells"][0]["sign"]=-1
        self.partition_refuses(V8_100,sign)

    def test_actual_children_require_exact_coverage_order_and_original_knot_records(self):
        changes=(lambda p:p["children"].pop(),
                 lambda p:p["children"].reverse(),
                 lambda p:p["children"][0]["interval"].__setitem__(1,"1/3"),
                 lambda p:p["children"][1]["interval"].__setitem__(0,"1/3"),
                 lambda p:p["children"][0].__setitem__("child_index",True),
                 lambda p:next(c for c in p["children"] if c["original_true_source_knots"])["original_true_source_knots"].clear())
        for index,mutate in enumerate(changes):
            with self.subTest(index=index):self.partition_refuses(V6_100,mutate)
        def artificial_knot(partition):
            record=copy.deepcopy(self.sources[V6_100]["zero_set"]["true_source_knots"][0])
            record["coordinate"]="1/2"
            partition["children"][0]["original_true_source_knots"].append(record)
        self.partition_refuses(V6_100,artificial_knot)

    def test_continuum_reconstruction_uses_coverage_and_no_finite_count(self):
        partition=self.partitions[CONTINUUM_ID]
        self.assertEqual(len(partition["children"]),4)
        self.assertEqual(partition["comparison_receipts"],[])
        for child in partition["children"]:
            for key in ("events","closed_root_count","maximal_nonzero_cells","endpoint_states"):
                self.assertIsNone(child[key])
            self.assertIs(child["finite_event_list_applicable"],False)
            self.assertIs(child["every_child_point_is_zero"],True)
        for field,value in (("events",[]),("closed_root_count",0),("maximal_nonzero_cells",[]),
                            ("finite_event_list_applicable",True),("every_child_point_is_zero",False)):
            self.partition_refuses(CONTINUUM_ID,lambda p,field=field,value=value:p["children"][0].__setitem__(field,value))
        self.partition_refuses(CONTINUUM_ID,lambda p:p["children"].pop(1))

    def test_v44_proof_cuts_and_common_carrier_sources_remain_physical_source_scoped(self):
        partition=self.partitions[V44_ID];source=self.sources[V44_ID]
        self.assertEqual(len(source["zero_set"]["events"]),1)
        self.assertEqual(partition["recomposition"]["closed_count_conservation"]["parent_distinct"],1)
        self.assertEqual(source["source_parameter_id"],"pb00701-v44-algebraic-orientation")
        self.assertEqual(source["original_source_piece_edges"],["0","1"])
        self.assertEqual(source["zero_set"]["true_source_knots"],[])
        event=source["zero_set"]["events"][0]
        self.assertEqual(event["coordinate"]["strict_open_bracket"],["9/16","37/64"])
        self.assertEqual((event["left_sign"],event["right_sign"]),(-1,1))
        a=self.sources[V13_100]["zero_set"]["events"][0]
        b=self.sources[V17_100]["zero_set"]["events"][0]
        self.assertEqual(a["coordinate"]["strict_open_bracket"],b["coordinate"]["strict_open_bracket"])
        self.assertNotEqual(digest(a),digest(b));self.assertEqual(a["left_sign"],-b["left_sign"])
        def rebind(partition):
            projected=next(e for c in partition["children"] for e in c["events"])
            projected["original_event"]=copy.deepcopy(a)
            projected["parent_event_sha256"]=digest(a)
        self.partition_refuses(V17_100,rebind)

    def test_actual_original_producer_failure_aborts_public_restriction(self):
        refiner=model.qualified_refiner_module()
        parent=refiner.qualified_parent_module()
        v2=parent.qualified_v2_module()
        runtime_module=v2._runtime_module()
        original_load=runtime_module.PinnedRuntime.load
        invoked=[]
        def fail():
            invoked.append("actual-five-original-source-producer")
            raise RuntimeError("CONTROLLED_ORIGINAL_PRODUCER_FAILURE")
        def load(runtime,path):
            module=original_load(runtime,path)
            if Path(str(path)).name==v2.PRODUCERS["five"][0]:module.expected_report=fail
            return module
        with mock.patch.object(model,"qualified_refiner_module",return_value=refiner), \
             mock.patch.object(refiner,"qualified_parent_module",return_value=parent), \
             mock.patch.object(parent,"qualified_v2_module",return_value=v2), \
             mock.patch.object(v2,"_runtime_module",return_value=runtime_module), \
             mock.patch.object(runtime_module.PinnedRuntime,"load",autospec=True,side_effect=load):
            result=model.restrict_original_source(V10_0,["3/16"])
        self.assertEqual(invoked,["actual-five-original-source-producer"])
        self.nontruth(result)

    def test_public_path_demands_fresh_qualified_context_then_restricts_actual_children(self):
        # The success test reuses this run's actual fresh context, not a saved
        # success marker. The public function still calls and validates it.
        with mock.patch.object(model,"replay_qualified_refinements",return_value=self.context) as replay:
            result=model.restrict_original_source(V6_100,[])
        replay.assert_called_once_with()
        self.assertIs(result["proof_established"],True)
        self.assertIs(result["all_requested_children_established"],True)
        self.assertIs(result["parent_zero_set_replaced"],False)
        self.assertIs(result["production_authorized"],False)
        self.assertEqual(result["qualified_refiner_report_sha256"],model.REFINER_REPORT_VALUE_SHA256)
        self.same(result["partition"]["recomposition"]["recomposed_zero_set"],self.sources[V6_100]["zero_set"])
        self.assertEqual(len(result["partition"]["children"]),1)

    def test_true_zero_or_undecided_requested_point_returns_atomic_nontruth(self):
        spec={"grammar":"RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
              "source_parameter_id":"conditional-midpoint-zero","parameter_lo":"0","parameter_hi":"1",
              "phase_turn_offset":"0","phase_turn_rate":"0",
              "cos_splines":{"1":{"degree":1,"knots":["0","0","1","1"],"controls":["-1/2","1/2"]}},
              "sin_splines":{}}
        prepared=self.provider.prepare_source_spec(spec)
        self.assertEqual(self.provider.spline_value(prepared.channels[0].spline,Q(1,2)),0)
        with self.assertRaises(self.provider.Refusal) as zero:
            self.provider.point_receipt(prepared,Q(1,2))
        invoked=[]
        def actual_zero(provider,source,coordinate):
            invoked.append(str(coordinate))
            # Each checked module owns its prepared-source constructor. Build
            # within the actual provider instance, preserving that identity.
            return provider.point_receipt(provider.prepare_source_spec(spec),Q(1,2))
        with mock.patch.object(model,"replay_qualified_refinements",return_value=self.context), \
             mock.patch.object(model,"point_receipt",side_effect=actual_zero):
            result=model.restrict_original_source(V10_0,["3/16"])
        self.assertEqual(invoked,["3/16"])
        self.nontruth(result)
        self.assertEqual(result["code"],zero.exception.code)
        def zero_inclusive(provider,source,coordinate):
            receipt=provider.point_receipt(source,coordinate)
            receipt["outward_dyadic_interval"]=["-1","1"]
            return receipt
        with mock.patch.object(model,"replay_qualified_refinements",return_value=self.context), \
             mock.patch.object(model,"point_receipt",side_effect=zero_inclusive):
            self.nontruth(model.restrict_original_source(V10_0,["3/16"]))

    def test_comparison_receipt_corruption_cannot_drive_membership(self):
        changes=(lambda r:r.__setitem__("relation",-r["relation"]),
                 lambda r:r.__setitem__("relation",True),
                 lambda r:r.__setitem__("source_sha256","0"*64),
                 lambda r:r["evidence"]["point_receipt"].__setitem__("sign",-r["evidence"]["point_receipt"]["sign"]),
                 lambda r:r["evidence"]["point_receipt"].__setitem__("coordinate","1/5"),
                 lambda r:r["evidence"]["parent_uniqueness_evidence"].__setitem__("replayed_result_sha256","0"*64))
        for index,change in enumerate(changes):
            def mutate(partition):
                receipt=next(r for r in partition["comparison_receipts"]
                             if r["method"]=="STRICT_ORIGINAL_POINT_AND_PARENT_UNIQUENESS")
                change(receipt)
            with self.subTest(index=index):self.partition_refuses(V10_0,mutate)
        self.partition_refuses(V6_100,lambda p:p["comparison_receipts"].pop())

    def test_source_and_whole_original_row_binding_precede_numeric_work(self):
        source=self.sources[V10_0];original=self.originals[V10_0];event=source["zero_set"]["events"][0]
        changes=(lambda s:s.__setitem__("source_parameter_id","reparameterized-child"),
                 lambda s:s["phase_turn_law"].__setitem__("offset","1/4"),
                 lambda s:s["zero_set"]["events"][0]["coordinate"].__setitem__("strict_open_bracket",["0","1"]),
                 lambda s:s.__setitem__("source_sha256","0"*64),
                 lambda s:s.__setitem__("case_id",V17_100))
        with mock.patch.object(model,"Fraction",side_effect=AssertionError("unbound source reached rational work")) as fraction:
            for mutate in changes:
                changed=copy.deepcopy(source);mutate(changed)
                with self.assertRaises(model.Refusal):model.compare_event_with_cut(changed,original,event,"3/16")
            for field in ("phase_turn_offset","phase_turn_rate","source_parameter_id"):
                changed=copy.deepcopy(original);changed["spec"][field]="1e999999999"
                with self.assertRaises(model.Refusal):model.compare_event_with_cut(source,changed,event,"3/16")
            changed=copy.deepcopy(original);changed["additional_unbound_field"]=True
            with self.assertRaises(model.Refusal):model.compare_event_with_cut(source,changed,event,"3/16")
            fraction.assert_not_called()

    def test_formatter_requires_every_actual_partition_not_just_correct_aggregate(self):
        for mutate in (lambda p:p.pop(),lambda p:p.__setitem__(1,copy.deepcopy(p[0])),lambda p:p.reverse()):
            changed=dict(self.replay);changed["partitions"]=copy.deepcopy(self.replay["partitions"])
            mutate(changed["partitions"])
            with self.assertRaises(model.Refusal):model.report_from_replay(changed)
        partition=copy.deepcopy(self.partitions[V6_100])
        partition["recomposition"]["canonical_parent_zero_set_equal"]=False
        with self.assertRaises(model.Refusal):
            model._validate_partition(self.sources[V6_100],self.originals[V6_100],partition["cuts"],partition,self.provider)

    def test_internal_qualified_context_cannot_change_parent_sources_or_refiner_trace(self):
        changed=dict(self.context);changed["refiner_report"]=copy.deepcopy(self.context["refiner_report"])
        changed["refiner_report"]["parent_baseline"]["source_cases"].pop()
        with self.assertRaises(model.Refusal):model.restrict_from_context(changed,V6_100,[])
        changed=dict(self.context);changed["refiner_context"]=dict(self.context["refiner_context"])
        changed["refiner_context"]["refinements"]=copy.deepcopy(self.context["refiner_context"]["refinements"])
        changed["refiner_context"]["refinements"][0]["refinement"]["trace"].pop()
        with self.assertRaises(model.Refusal):model.restrict_from_context(changed,V6_100,[])
        changed=dict(self.context);changed["refiner_context"]=dict(self.context["refiner_context"])
        changed["refiner_context"]["indexed"]=dict(self.originals)
        changed["refiner_context"]["indexed"][V6_100]=copy.deepcopy(self.originals[V6_100])
        changed["refiner_context"]["indexed"][V6_100]["spec"]["phase_turn_offset"]="1/4"
        with self.assertRaises(model.Refusal):model.restrict_from_context(changed,V6_100,[])

    def test_reports_cannot_omit_child_events_create_root_equalities_or_promote_gates(self):
        self.report_refuses(lambda r:r["partitions"].pop())
        self.report_refuses(lambda r:r["partitions"][0]["children"].pop())
        self.report_refuses(lambda r:r["partitions"][0]["children"][0].__setitem__("closed_interval",1))
        self.report_refuses(lambda r:r["summary"].__setitem__("child_closed_finite_zero_occurrences",81))
        self.report_refuses(lambda r:r["scope"].__setitem__("new_root_completeness_theorem",True))
        self.report_refuses(lambda r:r["parent_baseline"]["source_cases"].pop())
        for key,value in (("production_authorized",True),("MC-B","ACCEPTED"),("MC-1","ACCEPTED"),("PB-007-01","CLOSED")):
            self.report_refuses(lambda r,key=key,value=value:r["gates"].__setitem__(key,value))

    def test_invalid_ids_cut_shapes_and_counts_refuse_before_replay(self):
        class ListAlias(list):pass
        class StrAlias(str):pass
        bad_ids=(True,1,None,[],StrAlias(V6_100),"unknown-source","x"*10000)
        bad_cuts=(True,1,None,(),{},ListAlias(),["1/8"]*7,["3/4","1/4"],["1/2","1/2"],
                  [True],[1],[Q(1,2)],[0.5],["1/2","1e999999999"])
        with mock.patch.object(model,"replay_qualified_refinements",side_effect=AssertionError("invalid input reached proof")) as replay:
            for value in bad_ids:
                with self.subTest(id_type=type(value).__name__):self.nontruth(model.restrict_original_source(value,[]))
            for i,value in enumerate(bad_cuts):
                with self.subTest(cuts=i):self.nontruth(model.restrict_original_source(V6_100,value))
            for cid,source in self.sources.items():
                a,b=map(Q,source["source_interval"])
                for q in (a-1,a,b,b+1):self.nontruth(model.restrict_original_source(cid,[str(q)]))
            replay.assert_not_called()

    def test_all_cut_tokens_and_operands_are_checked_before_fraction_constructor(self):
        invalid=(True,False,1,0.5,None,"","+1","-0","01","1/1","2/4","0/2","1/0","1/-2",
                 " 1","1 ","1e1000000000","0.25","\uff11","9"*129,str(1<<128),"1/"+str(1<<128))
        with mock.patch.object(model,"Fraction",side_effect=AssertionError("invalid token constructed")) as fraction:
            for i,value in enumerate(invalid):
                with self.subTest(index=i),self.assertRaises(model.Refusal):model.rational(value)
                with self.subTest(index=i,whole_request=True):
                    self.nontruth(model.restrict_original_source(V6_100,["1/4",value]))
            fraction.assert_not_called()
        for value in ("0","-3","1/2","-2/3",str((1<<127)-1)):
            self.assertEqual(model.rational(value),Q(value))

    def test_public_report_bounds_precede_any_fresh_proof(self):
        cycle=[];cycle.append(cycle)
        shared={"x":1};deep=0
        for _ in range(model.MAX_DEPTH+1):deep=[deep]
        class DictAlias(dict):pass
        invalid=(cycle,[shared,shared],deep,{"x":0.5},{"x":float("nan")},{"x":b"bytes"},
                 {"x":(1,2)},DictAlias(x=1),{"x":"x"*(model.MAX_STRING+1)},
                 {"x":1<<20000},list(range(1025)),[[0]*900 for _ in range(300)])
        with mock.patch.object(model,"expected_report",side_effect=AssertionError("unsafe report reached replay")) as expected:
            for i,candidate in enumerate(invalid):
                with self.subTest(index=i),self.assertRaises(model.Refusal):model.validate_report(candidate)
            expected.assert_not_called()
        self.assertNotEqual(model.bounded_bytes({"relation":True}),model.bounded_bytes({"relation":1}))

    def test_json_reader_rejects_duplicate_nonexact_deep_and_oversized_inputs(self):
        with tempfile.TemporaryDirectory(prefix="finite-restriction-json-") as directory:
            path=Path(directory)/"candidate.json"
            malformed=(b'{"x":1,"x":2}',b'{"x":NaN}',b'{"x":Infinity}',b'{"x":0.5}',
                       b'{"x":1e999999999}',b'{"x":'+b'9'*81+b'}',b'\xff',b'not-json',
                       b'['*(model.MAX_DEPTH+1)+b'0'+b']'*(model.MAX_DEPTH+1))
            for raw in malformed:
                path.write_bytes(raw)
                with self.subTest(raw=raw[:30]),self.assertRaises(model.Refusal):model.read_report(path)
            with path.open("wb") as stream:stream.truncate(model.MAX_BYTES+1)
            with self.assertRaises(model.Refusal):model.read_report(path)
            path.write_bytes(b'{"status":"bounded candidate"}')
            self.assertEqual(model.read_report(path),{"status":"bounded candidate"})

    def test_report_path_bounds_precede_read_or_open(self):
        bad=("x"*10000,Path("x"*10000),"","a\0b",True,1,None,[])
        with mock.patch.object(model,"_read_bounded",side_effect=AssertionError("invalid path read")) as reader:
            for i,path in enumerate(bad):
                with self.subTest(index=i),self.assertRaises(model.Refusal):model.read_report(path)
            reader.assert_not_called()
        with tempfile.TemporaryDirectory(prefix="finite-restriction-missing-") as directory:
            with self.assertRaises(model.Refusal):model.read_report(Path(directory)/"missing.json")

    def test_exact_refiner_source_ignores_actual_accepted_cache_and_preload(self):
        trusted=(ROOT/model.REFINER_MODEL).read_bytes()
        self.assertEqual(git_blob(trusted),REFINER_BLOB)
        name=self.provider.__name__;payload=b"CACHE_SUBSTITUTION = True\n#"
        altered=payload+b" "*(len(trusted)-len(payload))
        with tempfile.TemporaryDirectory(prefix="restriction-refiner-cache-") as directory:
            root=Path(directory);path=root/model.REFINER_MODEL;path.parent.mkdir(parents=True)
            ordinary=install_accepted_stale_cache(path,trusted,altered)
            self.assertTrue(ordinary.CACHE_SUBSTITUTION)
            fake=types.ModuleType(name);fake.CACHE_SUBSTITUTION=True
            with mock.patch.object(model,"ROOT",root),mock.patch.dict(sys.modules,{name:fake,path.stem:fake}):
                checked=model.qualified_refiner_module()
                self.assertFalse(hasattr(checked,"CACHE_SUBSTITUTION"))
                self.assertTrue(callable(checked.replay_refinements))
                self.assertIs(sys.modules[name],fake);self.assertIs(sys.modules[path.stem],fake)

    def test_same_verified_refiner_buffer_executes_after_path_replacement(self):
        trusted=(ROOT/model.REFINER_MODEL).read_bytes()
        with tempfile.TemporaryDirectory(prefix="restriction-refiner-replace-") as directory:
            root=Path(directory);path=root/model.REFINER_MODEL;path.parent.mkdir(parents=True);path.write_bytes(trusted)
            calls=[]
            def replace(raw,filename,mode,**options):
                self.assertEqual(raw,trusted);self.assertEqual(options,{"dont_inherit":True,"optimize":0})
                calls.append(raw);path.write_bytes(b"CACHE_SUBSTITUTION = True\n")
                return builtins.compile(raw,filename,mode,**options)
            with mock.patch.object(model,"ROOT",root),mock.patch.dict(model.__dict__,{"compile":mock.Mock(side_effect=replace)}):
                checked=model.qualified_refiner_module()
                self.assertFalse(hasattr(checked,"CACHE_SUBSTITUTION"))
                with self.assertRaises(model.Refusal):model.qualified_refiner_module()
            self.assertEqual(len(calls),1)

    def test_dependency_source_drift_bounds_and_aliases_refuse_before_compilation(self):
        compiler=mock.Mock(side_effect=AssertionError("unchecked source compiled"))
        with mock.patch.dict(model.__dict__,{"compile":compiler}):
            for raw in (b"DRIFT = True\n",b"x"*(model.MAX_CODE_BYTES+1),"not bytes",True):
                with self.assertRaises(model.Refusal):model.qualified_refiner_module(raw)
            compiler.assert_not_called()
        with tempfile.TemporaryDirectory(prefix="restriction-refiner-alias-") as directory:
            root=Path(directory);path=root/model.REFINER_MODEL;path.parent.mkdir(parents=True)
            target=path.with_name("unregistered.py");target.write_bytes((ROOT/model.REFINER_MODEL).read_bytes())
            path.symlink_to(target)
            with mock.patch.object(model,"ROOT",root),mock.patch.dict(model.__dict__,{"compile":compiler}):
                with self.assertRaises(model.Refusal):model.qualified_refiner_module()
                with self.assertRaises(model.Refusal):model._checked_buffer("unregistered.json","0"*40)
            compiler.assert_not_called()

    def test_qualified_json_is_parsed_from_captured_verified_buffer(self):
        trusted=(ROOT/model.REFINER_REPORT).read_bytes();expected=json.loads(trusted)
        read=model._read_bounded
        with tempfile.TemporaryDirectory(prefix="restriction-refiner-json-buffer-") as directory:
            root=Path(directory);path=root/model.REFINER_REPORT;path.parent.mkdir(parents=True);path.write_bytes(trusted)
            def replace(requested,limit):
                raw=read(requested,limit);requested.write_bytes(b'{"status":"forged-PASS"}');return raw
            with mock.patch.object(model,"ROOT",root),mock.patch.object(model,"_read_bounded",side_effect=replace):
                raw=model._checked_buffer(model.REFINER_REPORT,model.REFINER_REPORT_BLOB)
                self.same(model.parse_json_bytes(raw),expected)
                with self.assertRaises(model.Refusal):model._checked_buffer(model.REFINER_REPORT,model.REFINER_REPORT_BLOB)

    def test_direct_input_drift_stops_before_refiner_execution(self):
        read=model._read_bounded
        for relative in (model.REFINER_MODEL,model.REFINER_REPORT):
            def drift(path,limit):
                return b'{"status":"forged-PASS"}' if path==model.ROOT/relative else read(path,limit)
            with self.subTest(path=relative),mock.patch.object(model,"_read_bounded",side_effect=drift), \
                 mock.patch.object(model,"qualified_refiner_module",side_effect=AssertionError("drift reached proof")) as refiner:
                self.nontruth(model.restrict_original_source(V6_100,[]))
                refiner.assert_not_called()

    def test_captured_buffer_custody_requires_exact_path_blob_length_and_sha(self):
        custody=self.context["input_custody"]
        self.assertEqual(len(custody),2)
        self.same(custody,self.report["executed_byte_custody"]["direct_input_buffers"])
        for item in custody:
            raw=(ROOT/item["path"]).read_bytes()
            self.assertEqual(item["git_blob"],git_blob(raw))
            self.assertEqual(item["bytes"],len(raw))
            self.assertEqual(item["sha256"],hashlib.sha256(raw).hexdigest())
        for i in range(2):
            for key,value in (("path","unlisted.json"),("git_blob","0"*40),("bytes",True),
                              ("bytes",custody[i]["bytes"]+1),("sha256","0"*64)):
                changed=dict(self.context);changed["input_custody"]=copy.deepcopy(custody)
                changed["input_custody"][i][key]=value
                with self.subTest(index=i,field=key),self.assertRaises(model.Refusal):
                    model.restrict_from_context(changed,V6_100,[])

    def test_full_exact_dependency_and_workflow_trigger_closure(self):
        expected=dict(self.provider.PINS)
        expected.update({model.REFINER_MODEL:model.REFINER_MODEL_BLOB,model.REFINER_REPORT:model.REFINER_REPORT_BLOB})
        self.assertEqual(model.PINS,expected)
        self.assertEqual(len(expected),103)
        self.assertEqual(expected[LOWERER_PATH],LOWERER_BLOB)
        self.assertEqual(expected[TRIG_PATH],TRIG_BLOB)
        self.assertEqual(expected[RUNTIME_PATH],RUNTIME_BLOB)
        self.assertEqual(expected[REFINER_PATH],REFINER_BLOB)
        for relative,blob in expected.items():
            raw=(ROOT/relative).read_bytes()
            self.assertEqual(git_blob(raw),blob,relative)
        own={TASK+name for name in ("pb00701_finite_source_restriction.py",
                                  "verify_pb00701_finite_source_restriction.py",
                                  "pb00701-finite-source-restriction.json",
                                  "pb00701-finite-source-restriction-research.md")}
        workflow=".github/workflows/mc1-pb00701-finite-source-restriction.yml";own.add(workflow)
        text=(ROOT/workflow).read_text()
        before,after=text.split("  push:",1)
        for section in (before,after):
            paths=re.findall(r"^      - ['\"]([^'\"]+)['\"]$",section,re.M)
            self.assertEqual(set(paths),set(expected)|own)
            self.assertEqual(len(paths),108)
        self.assertNotIn("strategy:",text)
        self.assertIn("github.event.pull_request.head.sha || github.sha",text)
        self.assertIn("verify_pb00701_finite_source_restriction.py --contract --self-test",text)
        self.assertIn("python-version: '3.12'",text)


def test_suite(replay=None,report=None):
    FiniteRestrictionTests.replay=replay
    FiniteRestrictionTests.report=report
    classes=(FiniteRestrictionTests,build_bootstrap_tests(MODEL_PATH,MODEL_BLOB))
    return unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(case) for case in classes)


model=load_reviewed_model(MODEL_PATH,MODEL_BLOB)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract",action="store_true")
    parser.add_argument("--self-test",action="store_true")
    options=parser.parse_args()
    if not(options.contract or options.self_test):parser.error("choose --contract and/or --self-test")
    # One actual successful default12 refiner and all original producers supply
    # both the contract and the tests. Mutation controls share this fresh context.
    replay=model.replay_restrictions()
    report=model.report_from_replay(replay)
    if options.contract:model._compare_with_replayed_bytes(model.read_report(),canonical(report))
    if options.self_test:
        result=unittest.TextTestRunner(verbosity=2).run(test_suite(replay,report))
        if not result.wasSuccessful():raise SystemExit(1)
    print("PASS: all fifty original source zero sets have checked closed-child restrictions")
    print("PASS: child membership, inward orders, original locators and nonzero cells reconstruct the parent")
    print("PASS: 91 finite child roots and 293 cells rejoin to 81 original roots and 128 original cells")
    print("PASS: continuum and failed comparisons keep their exact types; all parent gates remain unchanged")


if __name__=="__main__":main()
