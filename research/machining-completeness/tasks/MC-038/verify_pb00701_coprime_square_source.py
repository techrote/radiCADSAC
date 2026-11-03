#!/usr/bin/env python3
"""Independent exact checks for generic bounded coprime-square source proofs.

Fixtures are generated independently from global polynomials. Source lowering,
Bezout identities, exhaustive phase candidates and order-two physical events
are checked before aggregate counts. No fixture name admits a supplied source.
"""
from __future__ import annotations

import argparse
import builtins
from collections import Counter
import copy
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from math import comb
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
MODEL_PATH = HERE / "pb00701_coprime_square_source.py"
MODEL_BLOB = "4db47f79acff3c036e67ba03dd11b9bfb0a96bdb"

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
    module = types.ModuleType("coprime_square_reviewed_model")
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
    spec = importlib.util.spec_from_file_location("ordinary_coprime_square_cache_control", path)
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
            with tempfile.TemporaryDirectory(prefix="coprime-square-cache-") as directory:
                here = Path(directory) / TASK
                here.mkdir(parents=True)
                path = here / Path(model_path).name
                ordinary = install_accepted_stale_cache(path, trusted, altered)
                self.assertTrue(ordinary.CACHE_SUBSTITUTION)
                fake = types.ModuleType("coprime_square_reviewed_model")
                fake.CACHE_SUBSTITUTION = True
                with mock.patch.dict(sys.modules, {fake.__name__: fake, Path(model_path).stem: fake}):
                    checked = load_reviewed_model(path, model_blob)
                    self.assertFalse(hasattr(checked, "CACHE_SUBSTITUTION"))
                    self.assertTrue(callable(checked.expected_report))
                    self.assertIs(sys.modules[fake.__name__], fake)

        def test_checked_buffer_survives_posthash_path_replacement(self):
            with tempfile.TemporaryDirectory(prefix="coprime-square-replace-") as directory:
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
            with tempfile.TemporaryDirectory(prefix="coprime-square-bounds-") as directory:
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
            with tempfile.TemporaryDirectory(prefix="coprime-square-flags-") as directory:
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


def trim(poly):
    result=list(map(Q,poly))
    while len(result)>1 and result[-1]==0:result.pop()
    return result or [Q(0)]


def plus(a,b):
    return trim([(a[i] if i<len(a) else Q(0))+(b[i] if i<len(b) else Q(0))
                 for i in range(max(len(a),len(b)))])


def times(a,b):
    result=[Q(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):result[i+j]+=x*y
    return trim(result)


def at(poly,x):
    return sum((coefficient*x**i for i,coefficient in enumerate(poly)),Q(0))


def derivative(poly):
    return trim([i*poly[i] for i in range(1,len(poly))])


def power_to_bernstein(poly,left,right,degree):
    """Independent exact elevation, preserving global t in every coefficient."""
    poly=trim(poly);width=right-left
    if degree<len(poly)-1:raise ValueError("degree too small for exact elevation")
    local=[sum((poly[k]*comb(k,j)*left**(k-j)*width**j for k in range(j,len(poly))),Q(0))
           for j in range(len(poly))]
    return [sum((local[j]*Q(comb(i,j),comb(degree,j))
                 for j in range(min(i,len(local)-1)+1)),Q(0)) for i in range(degree+1)]


def supplied_source(p,q,*,lo=Q(0),hi=Q(1),offset=Q(0),rate=Q(1),
                    degree0=None,degree1=None,parameter="independent-coprime-square-original-t"):
    """Build test input without calling a candidate source or polynomial helper."""
    p,q=trim(p),trim(q)
    p2,q2=times(p,p),times(q,q)
    c0=[x/2 for x in plus(p2,q2)]
    c1=[x/2 for x in plus(p2,[-x for x in q2])]
    def spline(poly,degree):
        if degree is None:degree=len(trim(poly))-1
        return {"degree":degree,"knots":[str(lo)]*(degree+1)+[str(hi)]*(degree+1),
                "controls":list(map(str,power_to_bernstein(poly,lo,hi,degree)))}
    return {"grammar":"RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
            "source_parameter_id":parameter,"parameter_lo":str(lo),"parameter_hi":str(hi),
            "phase_turn_offset":str(offset),"phase_turn_rate":str(rate),
            "cos_splines":{"0":spline(c0,degree0),"1":spline(c1,degree1)},"sin_splines":{}}


def bernstein_value(spline,left,right,t):
    """Direct basis evaluation, independent of the candidate power lowering."""
    degree=spline["degree"];x=(t-left)/(right-left)
    return sum((Q(control)*comb(degree,i)*x**i*(1-x)**(degree-i)
                for i,control in enumerate(spline["controls"])),Q(0))


def independent_phase_candidates(spec,p,q):
    left,right=Q(spec["parameter_lo"]),Q(spec["parameter_hi"])
    offset,rate=Q(spec["phase_turn_offset"]),Q(spec["phase_turn_rate"])
    endpoints=(offset+rate*left,offset+rate*right)
    low,high=min(endpoints),max(endpoints)
    first=-((-2*low).__floor__());last=(2*high).__floor__()
    result=[]
    for m in range(first,last+1):
        t=(Q(m,2)-offset)/rate
        if not left<=t<=right:raise AssertionError("phase lattice escaped original source")
        pv,qv=at(p,t),at(q,t)
        root=pv==0 if m%2==0 else qv==0
        result.append({"m":m,"coordinate":t,"phase":Q(m,2),"p":pv,"q":qv,"is_zero":root})
    return sorted(result,key=lambda item:item["coordinate"])


def audit_lowering(test,spec,p,q,lowered):
    test.assertEqual(lowered["source_sha256"],digest(spec))
    test.assertEqual(lowered["source_parameter_id"],spec["source_parameter_id"])
    test.same(lowered["original_source_interval"],[spec["parameter_lo"],spec["parameter_hi"]])
    test.same(lowered["global_phase_turn_law"],{"offset":spec["phase_turn_offset"],"rate":spec["phase_turn_rate"]})
    p2,q2=times(p,p),times(q,q)
    expected0=trim([x/2 for x in plus(p2,q2)])
    expected1=trim([x/2 for x in plus(p2,[-x for x in q2])])
    test.same(lowered["C0"],list(map(str,expected0)))
    test.same(lowered["C1"],list(map(str,expected1)))
    test.assertEqual([c["harmonic"] for c in lowered["channels"]],[0,1])
    left,right=Q(spec["parameter_lo"]),Q(spec["parameter_hi"])
    for channel in lowered["channels"]:
        harmonic=str(channel["harmonic"]);spline=spec["cos_splines"][harmonic];degree=spline["degree"]
        test.assertIs(type(channel["degree"]),int)
        test.assertEqual(channel["degree"],degree)
        test.same(channel["original_knots"],spline["knots"])
        test.same(channel["original_controls"],spline["controls"])
        coefficients=trim(channel["global_power_coefficients"])
        test.assertLessEqual(len(coefficients)-1,degree)
        test.same(channel["global_power_coefficients"],lowered["C"+harmonic])
        basis=[trim(b) for b in channel["bernstein_basis_in_original_parameter"]]
        test.assertEqual(len(basis),degree+1)
        unity=[Q(0)];weighted=[Q(0)]
        for term,control in zip(basis,spline["controls"]):
            test.assertLessEqual(len(term)-1,degree)
            unity=plus(unity,term);weighted=plus(weighted,[Q(control)*v for v in term])
        test.assertEqual(unity,[Q(1)])
        test.assertEqual(weighted,coefficients)
        test.assertIs(channel["partition_of_unity_verified"],True)
        # Degree-bounded polynomial identities, not trigonometric root sampling.
        for j in range(degree+1):
            u=Q(j,degree) if degree else Q(0)
            t=left+(right-left)*u
            test.assertEqual(at(coefficients,t),bernstein_value(spline,left,right,t))
            for i,term in enumerate(basis):
                test.assertEqual(at(term,t),comb(degree,i)*u**i*(1-u)**(degree-i))
        test.assertEqual(channel["left_endpoint_value"],str(at(coefficients,left)))
        test.assertEqual(channel["right_endpoint_value"],str(at(coefficients,right)))
        test.assertEqual(channel["left_endpoint_value"],spline["controls"][0])
        test.assertEqual(channel["right_endpoint_value"],spline["controls"][-1])
    return expected0,expected1


def audit_bezout(test,p,q,proof):
    a,b=trim(proof["A"]),trim(proof["B"])
    test.assertEqual(plus(times(a,p),times(b,q)),[Q(1)])
    test.assertEqual(proof["normalized_gcd"],["1"])
    test.assertEqual(proof["identity_coefficients"],["1"])
    test.assertIs(proof["identity_verified_coefficientwise"],True)
    test.assertIs(proof["common_complex_zero_excluded_by_identity"],True)
    dividend,divisor=p,q
    for row in proof["euclidean_trace"]:
        test.assertEqual(trim(row["dividend"]),dividend)
        test.assertEqual(trim(row["divisor"]),divisor)
        test.assertNotEqual(divisor,[Q(0)])
        quotient,remainder=trim(row["quotient"]),trim(row["remainder"])
        test.assertEqual(plus(times(quotient,divisor),remainder),dividend)
        test.assertTrue(remainder==[Q(0)] or len(remainder)<len(divisor))
        dividend,divisor=divisor,remainder
    test.assertEqual(divisor,[Q(0)])
    test.assertEqual(len(dividend),1)
    test.assertNotEqual(dividend[0],0)


def audit_enumeration(test,spec,p,q,proof):
    expected=independent_phase_candidates(spec,p,q)
    left,right=Q(spec["parameter_lo"]),Q(spec["parameter_hi"])
    offset,rate=Q(spec["phase_turn_offset"]),Q(spec["phase_turn_rate"])
    phases=(offset+rate*left,offset+rate*right);low,high=sorted(phases)
    first=-((-2*low).__floor__());last=(2*high).__floor__()
    test.same(proof["phase_range"],{"original_left_phase":str(phases[0]),"original_right_phase":str(phases[1]),
              "closed_phase_range":[str(low),str(high)],"first_phase_index":first,"last_phase_index":last,
              "candidate_count":len(expected),"negative_rate_reverses_phase_order":rate<0})
    rows=[{"phase_index":c["m"],"phase_turn":str(c["phase"]),"coordinate":str(c["coordinate"]),
           "P_value":str(c["p"]),"Q_value":str(c["q"]),
           "branch":"INTEGER_PHASE_P_ZERO" if c["m"]%2==0 else "ODD_HALF_PHASE_Q_ZERO",
           "is_physical_zero":c["is_zero"]} for c in expected]
    test.same(proof["candidates"],rows)
    return expected


def audit_jet(test,spec,p,q,c0,c1,candidate,jet):
    t=candidate["coordinate"];m=candidate["m"];rate=Q(spec["phase_turn_rate"])
    integer=m%2==0
    vanishing,opposite=(p,q) if integer else (q,p)
    deriv=at(derivative(vanishing),t);other=at(opposite,t)
    test.assertEqual(at(vanishing,t),0)
    test.assertNotEqual(other,0)
    constant=deriv**2;pi_squared=(rate*other)**2
    # A second derivation differentiates the audited original harmonic source.
    parity=Q(1 if integer else -1)
    test.assertEqual(at(c0,t)+parity*at(c1,t),0)
    test.assertEqual(at(derivative(c0),t)+parity*at(derivative(c1),t),0)
    source_constant=(at(derivative(derivative(c0)),t)+parity*at(derivative(derivative(c1)),t))/2
    source_pi_squared=-2*rate**2*parity*at(c1,t)
    test.assertEqual((constant,pi_squared),(source_constant,source_pi_squared))
    test.assertGreaterEqual(constant,0);test.assertGreater(pi_squared,0)
    expected={"coordinate":str(t),"phase_turn":str(candidate["phase"]),"phase_index":m,
              "vanishing_amplitude":"P" if integer else "Q","vanishing_amplitude_value":"0",
              "vanishing_amplitude_first_derivative":str(deriv),"opposite_amplitude":"Q" if integer else "P",
              "opposite_amplitude_value":str(other),"original_phase_rate":str(rate),
              "exact_function_value":"0","exact_first_derivative":"0",
              "quadratic_taylor_coefficient":{"rational":str(constant),"pi_squared":str(pi_squared)},
              "pi_squared_coefficient_strictly_positive":True,"first_nonzero_order":2,
              "pi_nonzero_is_sufficient":True,"pi_irrationality_or_transcendence_used":False}
    test.same(jet,expected)


def audit_certificate(test,spec,p,q,certificate,expected_counts=None):
    """Independent original-source proof and full physical topology projection."""
    p,q=trim(p),trim(q)
    test.assertEqual(certificate["status"],"ESTABLISHED_COPRIME_SQUARE_ORIGINAL_SOURCE")
    test.assertIs(certificate["proof_established"],True)
    test.assertIs(certificate["source_zero_set_established"],True)
    test.assertIs(certificate["production_authorized"],False)
    test.same(certificate["original_source"],spec)
    source_hash=digest(spec)
    test.assertEqual(certificate["source_sha256"],source_hash)
    test.assertEqual(certificate["source_parameter_id"],spec["source_parameter_id"])
    test.same(certificate["source_interval"],[spec["parameter_lo"],spec["parameter_hi"]])
    test.same(certificate["phase_turn_law"],{"offset":spec["phase_turn_offset"],"rate":spec["phase_turn_rate"]})
    witness={"P":list(map(str,p)),"Q":list(map(str,q))}
    test.same(certificate["supplied_witness"],witness)
    test.same(certificate["normalized_witness"],witness)
    test.assertEqual(certificate["witness_sha256"],digest(witness))
    c0,c1=audit_lowering(test,spec,p,q,certificate["whole_source_lowering"])
    test.same(certificate["source_identity"],{
        "P_squared":list(map(str,times(p,p))),"Q_squared":list(map(str,times(q,q))),
        "C0_equals_half_sum_of_squares":list(map(str,c0)),
        "C1_equals_half_difference_of_squares":list(map(str,c1)),
        "identities_verified_coefficientwise":True,"original_source_equals_nonnegative_square_sum":True,
        "all_original_channels_reconstructed":True,"phase_used_in_original_parameter":True})
    audit_bezout(test,p,q,certificate["bezout_identity"])
    candidates=audit_enumeration(test,spec,p,q,certificate["phase_candidates"])
    roots=[c for c in candidates if c["is_zero"]]
    jets=certificate["root_jets"]
    test.assertEqual(len(jets),len(roots))
    for candidate,jet in zip(roots,jets):audit_jet(test,spec,p,q,c0,c1,candidate,jet)
    left,right=Q(spec["parameter_lo"]),Q(spec["parameter_hi"])
    events=[]
    for index,(root,jet) in enumerate(zip(roots,jets)):
        t=root["coordinate"];at_left=t==left;at_right=t==right
        order=({"kind":"ONE_SIDED","side":"RIGHT" if at_left else "LEFT","value":2,
                "outside_order":None,"global_smooth_multiplicity_claimed":False} if at_left or at_right
               else {"kind":"SMOOTH","value":2})
        events.append({"event_id":"ROOT_"+str(index),"source_sha256":source_hash,
                       "source_parameter_id":spec["source_parameter_id"],
                       "coordinate":{"kind":"RATIONAL","value":str(t)},
                       "location":"LEFT_EXTERIOR" if at_left else "RIGHT_EXTERIOR" if at_right else "SPAN_INTERIOR",
                       "source_piece_indices":[0],"classification":"TOUCHING", "phase_index":root["m"],
                       "phase_turn":str(root["phase"]),
                       "branch":"INTEGER_PHASE_P_ZERO" if root["m"]%2==0 else "ODD_HALF_PHASE_Q_ZERO",
                       "order":order,"left_sign":None if at_left else 1,"right_sign":None if at_right else 1,
                       "quadratic_jet":copy.deepcopy(jet)})
    by_coordinate={Q(e["coordinate"]["value"]):e for e in events}
    test.assertEqual(len(by_coordinate),len(events))
    def node(t):
        event=by_coordinate.get(t)
        if event:
            return {"kind":"PHYSICAL_ZERO_EVENT","event_id":event["event_id"],"coordinate":str(t),
                    "source_sha256":source_hash,"source_parameter_id":spec["source_parameter_id"]}
        return {"kind":"SOURCE_EXTERIOR","coordinate":str(t),"side":"LEFT" if t==left else "RIGHT"}
    boundaries=[left,*[root["coordinate"] for root in roots if left<root["coordinate"]<right],right]
    cells=[]
    for index,(a,b) in enumerate(zip(boundaries,boundaries[1:])):
        test.assertLess(a,b)
        cells.append({"cell_id":"CELL_"+str(index),"interval":[str(a),str(b)],"left_boundary":node(a),
                      "right_boundary":node(b),"left_included":a not in by_coordinate,
                      "right_included":b not in by_coordinate,"sign":1,"source_piece_indices":[0],
                      "crossed_nonzero_source_knots":[]})
    exteriors=[]
    offset,rate=Q(spec["phase_turn_offset"]),Q(spec["phase_turn_rate"])
    for side,t in (("LEFT",left),("RIGHT",right)):
        event=by_coordinate.get(t)
        exteriors.append({"side":side,"coordinate":str(t),"phase_turn":str(offset+rate*t),
                          "is_zero":event is not None,"event_ref":event["event_id"] if event else None,
                          "value_sign":0 if event else 1,"exact_value":"0" if event else None,
                          "nonzero_exact_scalar_value_claimed":False,
                          "positive_sign_from_complete_nonnegative_square_proof":event is None,
                          "inward_sign":1,"inward_order":2 if event else 0,"outside_sign":None,
                          "outside_order":None,"global_smooth_multiplicity_claimed":False})
    exterior_count=sum(c["coordinate"] in (left,right) for c in roots)
    expected={"kind":"FINITE_ORIGINAL_SOURCE_ZERO_SET","complete_for_original_closed_source":True,
              "source_interval":[str(left),str(right)],"closed_root_count":len(events),"events":events,
              "source_open_root_count":len(roots)-exterior_count,"exterior_root_count":exterior_count,
              "true_source_knots":[],"exterior_points":exteriors,"maximal_nonzero_cells":cells,
              "finite_event_list_applicable":True,"nonzero_sign_cells_applicable":True,
              "all_physical_roots_have_order_two":True,"nonzero_source_points_strictly_positive":True,
              "continuum_excluded_by_coprime_and_moving_phase_premises":True,
              "global_cross_source_zero_deduplication_performed":False}
    test.same(certificate["source_zero_set"],expected)
    test.same(certificate["theorem_premises"],{
        "both_summands_nonnegative":True,"sine_and_cosine_never_vanish_simultaneously":True,
        "no_common_amplitude_zero_from_verified_bezout":True,"half_integer_phase_candidates_are_exhaustive":True,
        "nonzero_phase_rate_makes_candidates_finite_and_distinct":True,
        "pi_nonzero_suffices_for_positive_quadratic_jets":True,
        "numerical_sampling_used_as_completeness_authority":False,"pi_irrationality_or_transcendence_used":False})
    for key in ("fixture_allowlist_used_for_admission","frozen_corpus_addition",
                "historical_source_completion_claimed","generic_owner_route_repaired","native_geometry_evidence"):
        test.assertIs(certificate["scope"][key],False)
    for key in ("generic_supplied_source_and_witness_checked","one_original_clamped_span",
                "valid_degree_elevation_admitted","original_parameter_and_global_phase_preserved"):
        test.assertIs(certificate["scope"][key],True)
    test.same(certificate["context_references"],model.REFERENCE_RECORDS)
    counts=len(candidates),len(roots),exterior_count,len(cells)
    if expected_counts is not None:test.assertEqual(counts,expected_counts)
    return counts


class CoprimeSquareTests(unittest.TestCase):
    replay=None
    report=None

    @classmethod
    def setUpClass(cls):
        if cls.replay is None:cls.replay=model.replay_sources()
        if cls.report is None:cls.report=model.report_from_replay(cls.replay)
        cls.expected_bytes=canonical(cls.report)

    def same(self,a,b,message=None):
        self.assertEqual(canonical(a),canonical(b),message)

    def nontruth(self,result):
        self.assertEqual(result["status"],"REFUSED")
        for key in ("source_zero_set_established","proof_established","production_authorized"):
            self.assertIs(result[key],False)
        self.assertIsNone(result["source_zero_set"])
        for key in ("successful_partial_roots","certificate","complete_root_list"):
            self.assertNotIn(key,result)

    def prove(self,p,q,**options):
        p,q=trim(p),trim(q)
        spec=supplied_source(p,q,**options)
        hints=list(map(str,p)),list(map(str,q))
        certificate=model.certify_source(spec,*hints)
        audit_certificate(self,spec,p,q,certificate)
        return spec,hints,certificate

    def test_all_eight_default_original_sources_and_physical_certificates(self):
        cases=self.replay["cases"]
        self.assertEqual(len(cases),8)
        self.assertEqual(len({c["case_id"] for c in cases}),8)
        self.assertEqual(len({digest(c["spec"]) for c in cases}),8)
        expected_roots=(["1"],[],["1/2","1"],["0","1/2","1"],["0","1","2"],
                        ["1/2","3/2"],["0","1/2","1"],["1/2","3/2"])
        counts=Counter()
        for case,root_coordinates in zip(cases,expected_roots):
            spec=case["spec"];p,q=trim(case["P"]),trim(case["Q"])
            values=audit_certificate(self,spec,p,q,case["certificate"])
            counts.update(dict(zip(("phase_candidates","per_source_closed_physical_roots",
                                    "original_exterior_roots","maximal_positive_nonzero_cells"),values)))
            counts["original_research_sources"]+=1
            counts["strict_source_interior_roots"]+=values[1]-values[2]
            counts["root_free_sources"]+=values[1]==0
            counts["order_two_root_jets"]+=values[1]
            zero=case["certificate"]["source_zero_set"]
            self.assertEqual([e["coordinate"]["value"] for e in zero["events"]],root_coordinates)
            original=supplied_source(p,q,lo=Q(spec["parameter_lo"]),hi=Q(spec["parameter_hi"]),
                                    offset=Q(spec["phase_turn_offset"]),rate=Q(spec["phase_turn_rate"]),
                                    degree0=spec["cos_splines"]["0"]["degree"],
                                    degree1=spec["cos_splines"]["1"]["degree"],parameter=spec["source_parameter_id"])
            self.same(spec,original)
        self.same(self.report["cases"],cases)
        self.same(self.report["summary"],dict(counts))
        self.assertEqual(dict(counts),{"original_research_sources":8,"phase_candidates":27,
            "per_source_closed_physical_roots":16,"original_exterior_roots":7,"strict_source_interior_roots":9,
            "maximal_positive_nonzero_cells":17,"root_free_sources":1,"order_two_root_jets":16})
        previous_path=TASK+"pb00701-mtp-irreducible-boundary.json"
        with (ROOT/previous_path).open("rb") as stream:raw=stream.read(model.MAX_REFERENCE_BYTES+1)
        self.assertLessEqual(len(raw),model.MAX_REFERENCE_BYTES)
        self.assertEqual(git_blob(raw),model.REFERENCE_PINS[previous_path])
        previous=json.loads(raw)
        self.same(cases[0]["spec"],previous["source"]["spec"])
        self.assertEqual(cases[0]["case_id"],previous["source"]["case_id"])
        self.assertEqual(cases[0]["certificate"]["source_sha256"],previous["source"]["source_sha256"])

    def test_report_scope_keeps_class_proof_separate_from_historical_gate_claims(self):
        self.same(self.report["gates"],{"PB-007-01":"OPEN","PB-007-02":"OPEN","PB-007-03":"OPEN", "PB-007-04":"OPEN",
            "MC-B":"NOT_ESTABLISHED","MC-1":"NOT_ESTABLISHED","production_authorized":False,
            "frozen_fifty_source_cohort_unchanged":True,"frozen_121_source_corpus_unchanged":True,
            "historical_20_blocked_and_30_order_gap_dispositions_unchanged":True,"all_26_operations_unchanged":True})
        scope=self.report["scope"]
        for key in ("generic_owner_route_repaired","project_context_code_executed","hostile_python_sandbox_claimed",
                    "native_geometry_evidence"):
            self.assertIs(scope[key],False)
        self.assertEqual((scope["prior_qualified_research_source_reproved"],scope["new_research_sources"]),(1,7))
        self.assertEqual(scope["frozen_corpus_additions"],0)
        self.assertEqual(scope["historical_route_or_source_completions_claimed"],0)
        self.assertIs(scope["all_examples_outside_frozen_fifty_source_cohort"],True)
        contract=self.report["supplied_source_contract"]
        for key in ("fixture_allowlist_used_for_admission","pi_irrationality_or_transcendence_used",
                    "stationary_phase_or_nonconstant_gcd_admitted"):
            self.assertIs(contract[key],False)

    def test_maximum_phase_enumeration_and_root_count_are_supported(self):
        spec,hints,certificate=self.prove([0],[1],lo=Q(-2),hi=Q(2),rate=Q(8),
                                        parameter="dynamic-65-candidates-33-roots")
        expected=independent_phase_candidates(spec,trim([0]),trim([1]))
        self.assertEqual(len(expected),65)
        self.assertEqual([c["coordinate"] for c in expected if c["is_zero"]],[Q(n,8) for n in range(-16,17)])
        audit_certificate(self,spec,trim([0]),trim([1]),certificate,expected_counts=(65,33,2,32))
        spec,hints,certificate=self.prove([0],[-2],lo=Q(-2),hi=Q(2),rate=Q(-8),
                                        parameter="dynamic-reversed-maximum")
        audit_certificate(self,spec,trim([0]),trim([-2]),certificate,expected_counts=(65,33,2,32))

    def test_equal_nonzero_constants_and_explicit_zero_harmonic_are_valid(self):
        for p,q in (([1],[1]),([2],[2]),([-3],[3]),([2],[3])):
            with self.subTest(p=p,q=q):
                spec,hints,certificate=self.prove(p,q,degree0=0,degree1=0,
                                                parameter="dynamic-constant-normalized-bezout")
                audit_certificate(self,spec,trim(p),trim(q),certificate,expected_counts=(3,0,0,1))
                if p[0]**2==q[0]**2:self.assertEqual(spec["cos_splines"]["1"]["controls"],["0"])

    def test_repeated_component_root_still_has_physical_order_two(self):
        for p in ([1,-2,1],[-1,3,-3,1]):
            spec,hints,certificate=self.prove(p,[1],lo=Q(0),hi=Q(2),parameter="dynamic-repeated-component")
            self.assertEqual(at(trim(p),Q(1)),0)
            self.assertEqual(at(derivative(trim(p)),Q(1)),0)
            audit_certificate(self,spec,trim(p),trim([1]),certificate,expected_counts=(5,1,0,2))

    def test_nonunit_domain_negative_origin_and_original_global_phase(self):
        spec,hints,certificate=self.prove([1,1],[-Q(1,2),1],lo=Q(-1),hi=Q(1),
                                        offset=Q(1,2),rate=Q(1,2),parameter="dynamic-nonunit-original-t")
        expected=independent_phase_candidates(spec,trim([1,1]),trim([-Q(1,2),1]))
        self.assertEqual([c["coordinate"] for c in expected if c["is_zero"]],[Q(-1)])
        audit_certificate(self,spec,trim([1,1]),trim([-Q(1,2),1]),certificate,expected_counts=(3,1,1,1))
        self.prove([0,-1,1],[-Q(1,2),1],offset=Q(1),rate=Q(-1),
                   parameter="dynamic-negative-rate-and-offset")
        p,q=trim([-Q(1,3),1]),trim([Q(2,3),1])
        spec,hints,certificate=self.prove(p,q,lo=Q(-1),hi=Q(2),offset=-Q(1,6),rate=Q(1,2),
                                        parameter="dynamic-three-unit-domain")
        self.assertEqual([c["coordinate"] for c in independent_phase_candidates(spec,p,q) if c["is_zero"]],
                         [-Q(2,3),Q(1,3)])
        audit_certificate(self,spec,p,q,certificate,expected_counts=(3,2,0,3))

    def test_empty_phase_candidate_set_is_a_valid_positive_certificate(self):
        spec,hints,certificate=self.prove([1],[1],offset=Q(1,8),rate=Q(1,16),
                                        parameter="dynamic-no-cardinal-phase")
        self.assertEqual(independent_phase_candidates(spec,trim([1]),trim([1])),[])
        audit_certificate(self,spec,trim([1]),trim([1]),certificate,expected_counts=(0,0,0,1))

    def test_noncardinal_exteriors_have_positive_sign_without_fake_rational_value(self):
        spec,hints,certificate=self.prove([1],[2],offset=Q(1,5),rate=Q(1,7),
                                        parameter="dynamic-noncardinal-exterior")
        audit_certificate(self,spec,trim([1]),trim([2]),certificate,expected_counts=(0,0,0,1))

    def test_valid_degree_elevation_is_new_admitted_source_not_allowlist(self):
        p,q=trim([-1,1]),trim([1])
        natural,hints,old=self.prove(p,q,lo=Q(1,2),hi=Q(3,2),parameter="dynamic-elevation-original")
        elevated,hints,new=self.prove(p,q,lo=Q(1,2),hi=Q(3,2),degree0=6,degree1=6,
                                     parameter="dynamic-elevation-original")
        self.assertNotEqual(digest(natural),digest(elevated))
        for harmonic in ("0","1"):
            for i in range(7):
                t=Q(1,2)+Q(i,6)
                self.assertEqual(bernstein_value(natural["cos_splines"][harmonic],Q(1,2),Q(3,2),t),
                                 bernstein_value(elevated["cos_splines"][harmonic],Q(1,2),Q(3,2),t))
        with self.assertRaises(model.Refusal):model.validate_certificate(elevated,*hints,old)
        self.assertTrue(model.validate_certificate(elevated,*hints,new))
        broken=copy.deepcopy(elevated)
        broken["cos_splines"]["1"]["controls"][3]=str(Q(broken["cos_splines"]["1"]["controls"][3])+Q(1,128))
        self.nontruth(model.check_source(broken,*hints))

    def test_changed_valid_phase_and_parameter_require_new_certificate_binding(self):
        p,q=trim([0,-1,1]),trim([-Q(1,2),1])
        old,hints,certificate=self.prove(p,q,parameter="dynamic-original-parameter")
        for field,value in (("source_parameter_id","another-bounded-original-t"),
                            ("phase_turn_offset","1/4"),("phase_turn_rate","-1")):
            new=copy.deepcopy(old);new[field]=value
            fresh=model.certify_source(new,*hints)
            audit_certificate(self,new,p,q,fresh)
            self.assertNotEqual(digest(old),digest(new))
            with self.assertRaises(model.Refusal):model.validate_certificate(new,*hints,certificate)
            self.assertTrue(model.validate_certificate(new,*hints,fresh))

    def test_opposite_polynomial_hints_preserve_squares_but_rebind_witness(self):
        p,q=trim([-1,1]),trim([1])
        spec,hints,old=self.prove(p,q)
        changed=(list(map(str,[-x for x in p])),list(map(str,[-x for x in q])))
        fresh=model.certify_source(spec,*changed)
        audit_certificate(self,spec,[-x for x in p],[-x for x in q],fresh)
        with self.assertRaises(model.Refusal):model.validate_certificate(spec,*changed,old)
        self.assertTrue(model.validate_certificate(spec,*changed,fresh))

    def test_shared_factor_has_hidden_noncardinal_root_and_must_refuse(self):
        p=trim([-Q(1,3),1]);spec=supplied_source(p,p)
        candidates=independent_phase_candidates(spec,p,p)
        self.assertEqual([c["coordinate"] for c in candidates],[Q(0),Q(1,2),Q(1)])
        self.assertTrue(all(not c["is_zero"] for c in candidates))
        self.assertEqual(bernstein_value(spec["cos_splines"]["0"],Q(0),Q(1),Q(1,3)),0)
        self.assertEqual(spec["cos_splines"]["1"]["controls"],["0"])
        self.nontruth(model.check_source(spec,list(map(str,p)),list(map(str,p))))
        with self.assertRaises(model.Refusal):model.compute_bezout(tuple(p),tuple(p))

    def test_zero_components_and_stationary_phase_do_not_inherit_moving_phase_proof(self):
        for p,q in (([0],[0]),([0],[-1,1]),([-1,1],[0])):
            spec=supplied_source(p,q)
            self.nontruth(model.check_source(spec,list(map(str,p)),list(map(str,q))))
        for p,q in (([-Q(1,3),1],[1]),([1],[1])):
            spec=supplied_source(p,q,rate=Q(0))
            self.nontruth(model.check_source(spec,list(map(str,p)),list(map(str,q))))
        self.prove([0],[-3],lo=Q(0),hi=Q(2),parameter="dynamic-zero-P-nonunit-constant")
        self.prove([-2],[0],lo=Q(0),hi=Q(2),parameter="dynamic-zero-Q-nonunit-constant")

    def test_amplitude_zero_at_nonmatching_phase_is_not_physical_zero(self):
        p,q=trim([-Q(1,2),1]),trim([Q(1,4),1])
        spec,hints,certificate=self.prove(p,q)
        self.assertEqual(at(p,Q(1,2)),0)
        self.assertEqual(at(q,Q(1,2)),Q(3,4))
        # beta=1/2 selects Q, so the actual F value here is 9/16.
        self.assertEqual(at(q,Q(1,2))**2,Q(9,16))
        audit_certificate(self,spec,p,q,certificate,expected_counts=(3,0,0,1))

    def test_wrong_original_coefficients_and_unsupported_channels_fail_identity(self):
        p,q=trim([-1,1]),trim([1]);spec=supplied_source(p,q)
        hints=list(map(str,p)),list(map(str,q))
        mutations=(lambda s:s["cos_splines"]["0"]["controls"].__setitem__(0,"9"),
                   lambda s:s["cos_splines"]["1"]["controls"].__setitem__(0,"9"),
                   lambda s:s["cos_splines"].pop("1"),
                   lambda s:s["cos_splines"].__setitem__("2",copy.deepcopy(s["cos_splines"]["1"])),
                   lambda s:s["sin_splines"].__setitem__("1",copy.deepcopy(s["cos_splines"]["1"])))
        for mutate in mutations:
            changed=copy.deepcopy(spec);mutate(changed)
            self.nontruth(model.check_source(changed,*hints))
        self.nontruth(model.check_source(spec,["0","1"],hints[1]))

    def test_complete_source_and_hints_preflight_precedes_fraction_work(self):
        spec=supplied_source([-1,1],[1]);p=["-1","1"];q=["1"]
        cases=[]
        for change in (lambda s:s["cos_splines"]["1"]["controls"].__setitem__(-1,"1e999999999"),
                       lambda s:s["cos_splines"]["1"].__setitem__("degree",True),
                       lambda s:s["cos_splines"]["1"].__setitem__("degree",7),
                       lambda s:s.__setitem__("source_parameter_id","x"*10000),
                       lambda s:s.__setitem__("phase_turn_rate","1/0")):
            altered=copy.deepcopy(spec);change(altered);cases.append((altered,p,q))
        cases.extend([(spec,p,["1","1e999999999"]),(spec,[True],q),(spec,["1"]*5,q)])
        with mock.patch.object(model,"Fraction",side_effect=AssertionError("invalid whole input reached Fraction")) as fraction:
            for index,args in enumerate(cases):
                with self.subTest(index=index):self.nontruth(model.check_source(*args))
            fraction.assert_not_called()

    def test_full_clamping_degree_domain_and_channel_shapes_are_required(self):
        spec=supplied_source([-1,1],[1]);hints=(["-1","1"],["1"])
        changes=(lambda s:s["cos_splines"]["0"]["knots"].__setitem__(2,"1/2"),
                 lambda s:s["cos_splines"]["0"]["knots"].pop(),
                 lambda s:s["cos_splines"]["0"]["controls"].pop(),
                 lambda s:s["cos_splines"]["0"].__setitem__("degree",-1),
                 lambda s:s["cos_splines"]["0"].__setitem__("degree",2.0),
                 lambda s:s.__setitem__("parameter_hi","0"),
                 lambda s:s.__setitem__("parameter_lo","3"),
                 lambda s:s.__setitem__("phase_turn_offset","9"),
                 lambda s:s.__setitem__("phase_turn_rate","9"),
                 lambda s:s.__setitem__("sin_splines",[]),
                 lambda s:s.__setitem__("unbound_field",True))
        for index,change in enumerate(changes):
            altered=copy.deepcopy(spec);change(altered)
            with self.subTest(index=index):self.nontruth(model.check_source(altered,*hints))

    def test_rational_input_tokens_types_reduction_and_bits_are_bounded(self):
        bad=(True,False,1,0.5,None,"","-0","+1","01","1/1","2/4","0/2","1/0","1/-2",
             " 1","1 ","1e999999999","0.25","\uff11","9"*129,str(1<<128),"1/"+str(1<<128))
        with mock.patch.object(model,"Fraction",side_effect=AssertionError("malformed token constructed")) as fraction:
            for index,value in enumerate(bad):
                with self.subTest(index=index),self.assertRaises(model.Refusal):model.rational(value)
            fraction.assert_not_called()
        for value in ("0","-3","1/2","-2/3",str((1<<127)-1)):
            self.assertEqual(model.rational(value),Q(value))

    def test_caller_supplied_parser_limits_cannot_enlarge_hard_budgets(self):
        with mock.patch.object(model,"Fraction",side_effect=AssertionError("unbounded helper constructor")) as fraction:
            for value in (True,False,0,-1,4097,10**100,1.5,"128",None):
                with self.subTest(bits=value),self.assertRaises(model.Refusal):model.rational("1",max_bits=value)
            for value in (True,False,0,-1,2501,10**100,1.5,"128",None):
                with self.subTest(chars=value),self.assertRaises(model.Refusal):model.rational("1",max_chars=value)
            for value in (True,False,-1,13,10**100,1.5,"3",None):
                with self.subTest(degree=value),self.assertRaises(model.Refusal):model.decode_poly(["1"],max_degree=value)
            for value in (0,1,"true",None,[]):
                with self.subTest(derived=value),self.assertRaises(model.Refusal):model.decode_poly(["1"],derived=value)
            fraction.assert_not_called()
        value=Q(1,1<<200)
        self.assertEqual(model.rational(str(value),max_bits=256,max_chars=128),value)

    def test_actual_proof_hook_failure_returns_atomic_nontruth(self):
        spec=supplied_source([0,-1,1],[-Q(1,2),1]);hints=(["0","-1","1"],["-1/2","1"])
        for name in ("lower_source","compute_bezout","enumerate_phase_candidates","prove_root_jet"):
            def fail(*args,**kwargs):raise model.Refusal("CONTROLLED_"+name.upper()+"_FAILURE")
            with self.subTest(hook=name),mock.patch.object(model,name,side_effect=fail) as hook:
                result=model.check_source(spec,*hints)
                self.nontruth(result);self.assertGreater(hook.call_count,0)

    def test_forged_lowering_and_bezout_hook_outputs_are_rechecked(self):
        spec=supplied_source([0,-1,1],[-Q(1,2),1]);hints=(["0","-1","1"],["-1/2","1"])
        mutations={"lower_source":(
            lambda proof:proof.__setitem__("C0",["1"]),
            lambda proof:proof["channels"][0]["bernstein_basis_in_original_parameter"].__setitem__(0,["1"]),
            lambda proof:proof["channels"][0]["original_controls"].__setitem__(0,"99")),
            "compute_bezout":(
            lambda proof:proof.__setitem__("A",["0"]),
            lambda proof:proof.__setitem__("B",["0"]),
            lambda proof:proof["euclidean_trace"].pop(),
            lambda proof:proof["euclidean_trace"][0].__setitem__("quotient",["99"]))}
        for name,changes in mutations.items():
            original=getattr(model,name)
            for index,change in enumerate(changes):
                def forged(*args,**kwargs):
                    proof=original(*args,**kwargs);change(proof);return proof
                with self.subTest(hook=name,index=index),mock.patch.object(model,name,side_effect=forged):
                    self.nontruth(model.check_source(spec,*hints))

    def test_candidate_hook_cannot_omit_reorder_or_reclassify_physical_roots(self):
        spec=supplied_source([0,-1,1],[-Q(1,2),1],offset=Q(1),rate=Q(-1))
        hints=(["0","-1","1"],["-1/2","1"])
        original=model.enumerate_phase_candidates
        changes=(lambda p:p["candidates"].pop(),lambda p:p["candidates"].reverse(),
                 lambda p:p["candidates"].__setitem__(1,copy.deepcopy(p["candidates"][0])),
                 lambda p:p["candidates"][0].__setitem__("is_physical_zero",False),
                 lambda p:p["candidates"][0].__setitem__("is_physical_zero",1),
                 lambda p:p["candidates"][0].__setitem__("phase_index",True),
                 lambda p:p["candidates"][0].__setitem__("coordinate","1/4"),
                 lambda p:p["candidates"][0].__setitem__("branch","ODD_HALF_PHASE_Q_ZERO"))
        for index,change in enumerate(changes):
            def forged(*args):
                proof=original(*args);change(proof);return proof
            with self.subTest(index=index),mock.patch.object(model,"enumerate_phase_candidates",side_effect=forged):
                self.nontruth(model.check_source(spec,*hints))

    def test_actual_positive_quadratic_jet_is_required_for_every_root(self):
        spec=supplied_source([-1,3,-3,1],[1],lo=Q(0),hi=Q(2));hints=(["-1","3","-3","1"],["1"])
        original=model.prove_root_jet
        changes=(lambda j:j.__setitem__("first_nonzero_order",4),
                 lambda j:j.__setitem__("first_nonzero_order",True),
                 lambda j:j["quadratic_taylor_coefficient"].__setitem__("pi_squared","0"),
                 lambda j:j["quadratic_taylor_coefficient"].__setitem__("rational","1"),
                 lambda j:j.__setitem__("original_phase_rate","2"),
                 lambda j:j.__setitem__("opposite_amplitude_value","0"),
                 lambda j:j.__setitem__("pi_irrationality_or_transcendence_used",True))
        for index,change in enumerate(changes):
            def forged(*args):
                jet=original(*args);change(jet);return jet
            with self.subTest(index=index),mock.patch.object(model,"prove_root_jet",side_effect=forged):
                self.nontruth(model.check_source(spec,*hints))

    def test_physical_topology_and_exterior_germs_cannot_be_rewritten(self):
        spec,hints,certificate=self.prove([0,-1,1],[-Q(1,2),1])
        changes=(lambda c:c["source_zero_set"]["events"].pop(),
                 lambda c:c["source_zero_set"]["events"][0]["order"].__setitem__("side","LEFT"),
                 lambda c:c["source_zero_set"]["events"][0].__setitem__("left_sign",1),
                 lambda c:c["source_zero_set"]["maximal_nonzero_cells"].pop(),
                 lambda c:c["source_zero_set"]["maximal_nonzero_cells"][0].__setitem__("right_included",True),
                 lambda c:c["source_zero_set"]["maximal_nonzero_cells"][0].__setitem__("right_boundary",
                              copy.deepcopy(c["source_zero_set"]["maximal_nonzero_cells"][-1]["right_boundary"])),
                 lambda c:c["source_zero_set"].__setitem__("closed_root_count",2),
                 lambda c:c["source_zero_set"].__setitem__("kind","CLOSED_CONTINUUM_ZERO_COMPONENT"))
        for index,change in enumerate(changes):
            candidate=copy.deepcopy(certificate);change(candidate)
            with self.subTest(index=index),self.assertRaises(model.Refusal):model.validate_certificate(spec,*hints,candidate)
        spec,hints,certificate=self.prove([1],[2],offset=Q(1,5),rate=Q(1,7))
        for change in (lambda c:c["source_zero_set"]["exterior_points"][0].__setitem__("exact_value","1"),
                       lambda c:c["source_zero_set"]["exterior_points"][0].__setitem__("nonzero_exact_scalar_value_claimed",True)):
            candidate=copy.deepcopy(certificate);change(candidate)
            with self.assertRaises(model.Refusal):model.validate_certificate(spec,*hints,candidate)

    def test_full_report_formatter_rechecks_actual_proofs_and_completeness(self):
        mutations=(lambda r:r["cases"].pop(),lambda r:r["cases"].reverse(),
                   lambda r:r["cases"].__setitem__(1,copy.deepcopy(r["cases"][0])),
                   lambda r:r["cases"][0]["certificate"]["phase_candidates"]["candidates"].pop(),
                   lambda r:r["cases"][0]["certificate"]["source_zero_set"]["maximal_nonzero_cells"].pop(),
                   lambda r:r["cases"][0]["certificate"]["root_jets"][0]["quadratic_taylor_coefficient"].__setitem__("pi_squared","0"),
                   lambda r:r["cases"][0]["certificate"]["bezout_identity"].__setitem__("B",["0"]),
                   lambda r:r["cases"][0]["spec"].__setitem__("source_parameter_id","rebased-parameter"),
                   lambda r:r["context_references"][0].__setitem__("sha256","0"*64))
        for index,change in enumerate(mutations):
            replay=copy.deepcopy(self.replay);change(replay)
            with self.subTest(index=index),self.assertRaises(model.Refusal):model.report_from_replay(replay)

    def test_report_bytes_cannot_promote_gates_or_hide_original_source_proofs(self):
        changes=[lambda r:r["cases"].pop(),lambda r:r["summary"].__setitem__("per_source_closed_physical_roots",33),
                 lambda r:r["supplied_source_contract"].__setitem__("fixture_allowlist_used_for_admission",True)]
        for key,value in (("production_authorized",True),("MC-1","ACCEPTED"),("MC-B","ACCEPTED"),("PB-007-01","CLOSED")):
            changes.append(lambda r,key=key,value=value:r["gates"].__setitem__(key,value))
        for change in changes:
            candidate=json.loads(self.expected_bytes);change(candidate)
            with self.assertRaises(model.Refusal):model._compare_with_replayed_bytes(candidate,self.expected_bytes)

    def test_derived_polynomial_growth_is_bounded_before_large_products(self):
        operand=Q(1,1<<3000)
        with mock.patch.object(Q,"__mul__",side_effect=AssertionError("overbudget product executed")) as multiply:
            with self.assertRaises(model.Refusal) as error:model.poly_mul((operand,),(operand,))
            self.assertEqual(error.exception.code,"RESOURCE_REFUSAL")
            multiply.assert_not_called()
        with self.assertRaises(model.Refusal):model.poly_mul((Q(1),)*13,(Q(1),)*2)

    def test_derived_bezout_receipts_may_exceed_raw_input_bit_limit(self):
        n=Q((1<<50)-3)
        p,q=trim([1,n,0,1]),trim([2,n,1])
        spec=supplied_source(p,q,parameter="dynamic-derived-bezout-bits")
        for spline in spec["cos_splines"].values():
            for token in spline["controls"]:
                value=Q(token)
                self.assertLessEqual(max(value.numerator.bit_length(),value.denominator.bit_length()),128)
        certificate=model.certify_source(spec,list(map(str,p)),list(map(str,q)))
        audit_certificate(self,spec,p,q,certificate)
        proof=model.compute_bezout(tuple(p),tuple(q))
        values=[Q(token) for key in ("A","B") for token in proof[key]]
        self.assertGreater(max(max(v.numerator.bit_length(),v.denominator.bit_length()) for v in values),128)
        self.assertEqual(plus(times(trim(proof["A"]),p),times(trim(proof["B"]),q)),[Q(1)])

    def test_phase_resource_bounds_precede_candidate_enumeration(self):
        p,q=(Q(0),),(Q(1),)
        requests=((Q(-2),Q(2),Q(8),Q(8)),(Q(-3),Q(2),Q(0),Q(1)),
                  (Q(-2),Q(2),Q(0),Q(9)),(Q(0),Q(1),Q(0),Q(0)))
        counter=mock.Mock(side_effect=AssertionError("out-of-bounds phase was enumerated"))
        with mock.patch.dict(model.__dict__,{"range":counter}):
            for args in requests:
                with self.assertRaises(model.Refusal):model.enumerate_phase_candidates(*args,p,q)
            counter.assert_not_called()
        calls=[]
        def observed_range(*args):calls.append(args);return range(*args)
        with mock.patch.dict(model.__dict__,{"range":observed_range}):
            proof=model.enumerate_phase_candidates(Q(-2),Q(2),Q(0),Q(8),p,q)
        self.assertEqual(calls,[(-32,33)])
        self.assertEqual(len(proof["candidates"]),65)

    def test_certificate_preflight_rejects_cycles_aliases_and_nonexact_json(self):
        spec=supplied_source([-1,1],[1]);hints=(["-1","1"],["1"])
        cycle=[];cycle.append(cycle);shared={"x":1};deep=0
        for _ in range(model.MAX_DEPTH+1):deep=[deep]
        class DictAlias(dict):pass
        invalid=(cycle,[shared,shared],deep,{"x":0.5},{"x":float("nan")},{"x":b"bytes"},
                 {"x":(1,2)},DictAlias(x=1),{"x":"x"*(model.MAX_STRING+1)},
                 {"x":1<<20000},list(range(1025)),[[0]*900 for _ in range(80)])
        with mock.patch.object(model,"certify_source",side_effect=AssertionError("unsafe certificate reached proof")) as proof:
            for i,candidate in enumerate(invalid):
                with self.subTest(index=i),self.assertRaises(model.Refusal):
                    model.validate_certificate(spec,*hints,candidate)
            proof.assert_not_called()
        with mock.patch.object(model,"expected_report",side_effect=AssertionError("unsafe report reached proof")) as replay:
            for i,candidate in enumerate(invalid):
                with self.subTest(index=i),self.assertRaises(model.Refusal):model.validate_report(candidate)
            replay.assert_not_called()
        self.assertNotEqual(model.bounded_bytes({"is_root":True}),model.bounded_bytes({"is_root":1}))

    def test_report_json_rejects_duplicate_nonexact_deep_and_oversized_inputs(self):
        with tempfile.TemporaryDirectory(prefix="coprime-square-json-") as directory:
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

    def test_report_path_bounds_precede_reads(self):
        invalid=("x"*10000,Path("x"*10000),"","a\0b",True,1,None,[])
        with mock.patch.object(model,"_read_bounded",side_effect=AssertionError("invalid path read")) as reader:
            for i,path in enumerate(invalid):
                with self.subTest(index=i),self.assertRaises(model.Refusal):model.read_report(path)
            reader.assert_not_called()
        with tempfile.TemporaryDirectory(prefix="coprime-square-missing-") as directory:
            with self.assertRaises(model.Refusal):model.read_report(Path(directory)/"missing.json")

    def test_all_context_references_have_exact_bytes_and_are_not_executed(self):
        self.assertEqual(len(model.REFERENCE_PINS),4)
        records=[]
        for path,blob in sorted(model.REFERENCE_PINS.items()):
            raw=(ROOT/path).read_bytes()
            self.assertEqual(git_blob(raw),blob,path)
            records.append({"path":path,"git_blob":blob,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),
                            "use":"PINNED_NONEXECUTED_GRAMMAR_AND_PRIOR_RESEARCH_CONTEXT"})
        self.same(model.REFERENCE_RECORDS,records)
        self.same(self.replay["context_references"],records)
        self.same(self.report["context_references"],records)
        compiler=mock.Mock(side_effect=AssertionError("context-only project source executed"))
        with mock.patch.object(builtins,"compile",compiler):
            self.same(model.capture_references(),records)
        compiler.assert_not_called()

    def test_captured_reference_bytes_survive_path_replacement_without_execution(self):
        raw_inputs={path:(ROOT/path).read_bytes() for path in model.REFERENCE_PINS}
        read=model._read_bounded
        with tempfile.TemporaryDirectory(prefix="coprime-square-reference-buffer-") as directory:
            root=Path(directory)
            for relative,raw in raw_inputs.items():
                path=root/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
            seen=[]
            def replace(path,limit):
                raw=read(path,limit);seen.append(str(path.relative_to(root)))
                path.write_bytes(b"CONTEXT_SUBSTITUTED = True\n")
                return raw
            with mock.patch.object(model,"ROOT",root),mock.patch.object(model,"_read_bounded",side_effect=replace):
                self.same(model.capture_references(),model.REFERENCE_RECORDS)
                self.assertEqual(seen,sorted(model.REFERENCE_PINS))
                with self.assertRaises(model.Refusal):model.capture_references()

    def test_reference_caches_and_preloads_cannot_supply_context_custody(self):
        with tempfile.TemporaryDirectory(prefix="coprime-square-context-cache-") as directory:
            root=Path(directory)
            for relative in model.REFERENCE_PINS:
                path=root/relative;path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes((ROOT/relative).read_bytes())
            relative=TASK+"pb00701_mtp_irreducible_boundary.py";path=root/relative
            trusted=path.read_bytes();payload=b"CONTEXT_CACHE_SUBSTITUTION = True\n#"
            altered=payload+b" "*(len(trusted)-len(payload))
            ordinary=install_accepted_stale_cache(path,trusted,altered)
            self.assertTrue(ordinary.CONTEXT_CACHE_SUBSTITUTION)
            fake=types.ModuleType(path.stem);fake.CONTEXT_CACHE_SUBSTITUTION=True
            with mock.patch.object(model,"ROOT",root),mock.patch.dict(sys.modules,{path.stem:fake}):
                self.same(model.capture_references(),model.REFERENCE_RECORDS)
                self.assertIs(sys.modules[path.stem],fake)

    def test_reference_drift_alias_and_size_failure_aborts_before_proof(self):
        read=model._read_bounded
        spec=supplied_source([-1,1],[1]);hints=(["-1","1"],["1"])
        for relative in model.REFERENCE_PINS:
            def drift(path,limit):return b"changed reference" if path==ROOT/relative else read(path,limit)
            with self.subTest(path=relative),mock.patch.object(model,"_read_bounded",side_effect=drift), \
                 mock.patch.object(model,"lower_source",side_effect=AssertionError("drift reached proof")) as lower:
                self.nontruth(model.check_source(spec,*hints));lower.assert_not_called()
        with tempfile.TemporaryDirectory(prefix="coprime-square-reference-alias-") as directory:
            root=Path(directory)
            for relative in model.REFERENCE_PINS:
                path=root/relative;path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes((ROOT/relative).read_bytes())
            path=root/sorted(model.REFERENCE_PINS)[0];saved=path.read_bytes();path.unlink()
            target=path.with_name("unlisted-context.txt");target.write_bytes(saved);path.symlink_to(target)
            with mock.patch.object(model,"ROOT",root):
                with self.assertRaises(model.Refusal):model.capture_references()
                path.unlink()
                with path.open("wb") as stream:stream.truncate(model.MAX_REFERENCE_BYTES+1)
                with self.assertRaises(model.Refusal):model.capture_references()

    def test_workflow_contains_exact_nonexecuted_context_and_owned_file_closure(self):
        own={TASK+name for name in ("pb00701_coprime_square_source.py","verify_pb00701_coprime_square_source.py",
                                  "pb00701-coprime-square-source.json","pb00701-coprime-square-source-research.md")}
        workflow=".github/workflows/mc1-pb00701-coprime-square-source.yml";own.add(workflow)
        text=(ROOT/workflow).read_text()
        before,after=text.split("  push:",1)
        for section in (before,after):
            paths=re.findall(r"^      - ['\"]([^'\"]+)['\"]$",section,re.M)
            self.assertEqual(set(paths),set(model.REFERENCE_PINS)|own)
            self.assertEqual(len(paths),9)
        self.assertNotIn("strategy:",text)
        self.assertIn("github.event.pull_request.head.sha || github.sha",text)
        self.assertIn("verify_pb00701_coprime_square_source.py --contract --self-test",text)
        self.assertIn("python-version: '3.12'",text)


def test_suite(replay=None,report=None):
    CoprimeSquareTests.replay=replay
    CoprimeSquareTests.report=report
    classes=(CoprimeSquareTests,build_bootstrap_tests(MODEL_PATH,MODEL_BLOB))
    return unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(case) for case in classes)


model=load_reviewed_model(MODEL_PATH,MODEL_BLOB)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract",action="store_true")
    parser.add_argument("--self-test",action="store_true")
    options=parser.parse_args()
    if not(options.contract or options.self_test):parser.error("choose --contract and/or --self-test")
    replay=model.replay_sources()
    report=model.report_from_replay(replay)
    if options.contract:model._compare_with_replayed_bytes(model.read_report(),canonical(report))
    if options.self_test:
        result=unittest.TextTestRunner(verbosity=2).run(test_suite(replay,report))
        if not result.wasSuccessful():raise SystemExit(1)
    print("PASS: generic supplied-source square identities and coefficientwise Bezout proofs are checked")
    print("PASS: exact phase candidates exhaust physical zeros; direct source jets prove order two")
    print("PASS: eight research sources yield 27 candidates, 16 roots and 17 positive cells")
    print("PASS: dynamic maximum/elevation/empty-candidate sources are supported; all gates remain unchanged")


if __name__=="__main__":main()

