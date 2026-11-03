#!/usr/bin/env python3
"""Independent exact polynomial-root and physical-union checks for shared squares.

Fixtures are generated independently from global polynomials. Source lowering,
Bezout identities, one-sided Sturm counts and product orders are checked before
aggregate counts. No fixture name admits a supplied source.
"""
from __future__ import annotations

import argparse
import builtins
from collections import Counter
import copy
from fractions import Fraction as Q
from functools import cmp_to_key
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
MODEL_PATH = HERE / "pb00701_shared_square_source.py"
MODEL_BLOB = "e445aae10a2a0eab49b4e958d030fa19f0cd3f7a"

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
    module = types.ModuleType("shared_square_reviewed_model")
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
    spec = importlib.util.spec_from_file_location("ordinary_shared_square_cache_control", path)
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
            with tempfile.TemporaryDirectory(prefix="shared-square-cache-") as directory:
                here = Path(directory) / TASK
                here.mkdir(parents=True)
                path = here / Path(model_path).name
                ordinary = install_accepted_stale_cache(path, trusted, altered)
                self.assertTrue(ordinary.CACHE_SUBSTITUTION)
                fake = types.ModuleType("shared_square_reviewed_model")
                fake.CACHE_SUBSTITUTION = True
                with mock.patch.dict(sys.modules, {fake.__name__: fake, Path(model_path).stem: fake}):
                    checked = load_reviewed_model(path, model_blob)
                    self.assertFalse(hasattr(checked, "CACHE_SUBSTITUTION"))
                    self.assertTrue(callable(checked.expected_report))
                    self.assertIs(sys.modules[fake.__name__], fake)

        def test_checked_buffer_survives_posthash_path_replacement(self):
            with tempfile.TemporaryDirectory(prefix="shared-square-replace-") as directory:
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
            with tempfile.TemporaryDirectory(prefix="shared-square-bounds-") as directory:
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
            with tempfile.TemporaryDirectory(prefix="shared-square-flags-") as directory:
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
                    degree0=None,degree1=None,parameter="independent-shared-square-original-t"):
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


def audit_residual_certificate(test,spec,p,q,certificate,expected_counts=None):
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
    test.same(certificate["context_references"],test.c.REFERENCE_RECORDS)
    counts=len(candidates),len(roots),exterior_count,len(cells)
    if expected_counts is not None:test.assertEqual(counts,expected_counts)
    return counts


def independent_degree(p):
    p=trim(p)
    return -1 if p==[0] else len(p)-1


def independent_division(p,q):
    p,q=trim(p),trim(q)
    if q==[0]:raise AssertionError("independent polynomial division by zero")
    if len(p)<len(q):return [Q(0)],p
    quotient=[Q(0)]*(len(p)-len(q)+1)
    while p!=[0] and len(p)>=len(q):
        power=len(p)-len(q);value=p[-1]/q[-1]
        quotient[power]+=value
        p=plus(p,[Q(0)]*power+[-value*c for c in q])
    return trim(quotient),trim(p)


def independent_gcd(p,q):
    p,q=trim(p),trim(q)
    while q!=[0]:p,q=q,independent_division(p,q)[1]
    return [v/p[-1] for v in p] if p!=[0] else p


def independent_square_free(p):
    p=trim(p)
    if independent_degree(p)<=0:return p
    out,remainder=independent_division(p,independent_gcd(p,derivative(p)))
    if remainder!=[0]:raise AssertionError("nonexact independent square-free division")
    return [v/out[-1] for v in out]


def independent_sturm(p):
    first=independent_square_free(p)
    if independent_degree(first)<=0:return [first]
    sequence=[first,derivative(first)]
    while True:
        remainder=independent_division(sequence[-2],sequence[-1])[1]
        if remainder==[0]:break
        sequence.append([-v for v in remainder])
    return sequence


def independent_side_sign(p,x,side):
    if side not in (-1,1):raise AssertionError("invalid independent side")
    order=0;p=trim(p)
    while p!=[0]:
        value=at(p,x)
        if value:return ((value>0)-(value<0))*(side**order)
        p=derivative(p);order+=1
    return 0


def independent_variations(signs):
    nonzero=[s for s in signs if s]
    return sum(a!=b for a,b in zip(nonzero,nonzero[1:]))


def independent_count(p,a,b):
    if not(a<b and 0<=independent_degree(p)<=3):raise AssertionError("independent count scope")
    seq=independent_sturm(p)
    return independent_variations([independent_side_sign(s,a,1) for s in seq])-\
        independent_variations([independent_side_sign(s,b,-1) for s in seq])


def rational_multiplicity(p,x):
    if trim(p)==[0]:raise AssertionError("identity polynomial has no finite order")
    order=0;p=trim(p)
    while p!=[0] and at(p,x)==0:order+=1;p=derivative(p)
    return order


def independent_multiplicity_chain(g):
    g=trim(g);chain=[]
    while independent_degree(g)>0:
        chain.append(g);g=independent_gcd(g,derivative(g))
    return chain


def coordinate_bounds(coordinate):
    if coordinate["kind"]=="RATIONAL":
        q=Q(coordinate["value"]);return q,q
    if coordinate["kind"]!="REAL_ALGEBRAIC_ISOLATOR":raise AssertionError("unknown coordinate kind")
    return tuple(map(Q,coordinate["isolating_interval"]))


def compare_coordinates(a,b):
    al,ah=coordinate_bounds(a);bl,bh=coordinate_bounds(b)
    if al==ah and bl==bh:return (al>bl)-(al<bl)
    if ah<=bl:return -1
    if bh<=al:return 1
    raise AssertionError("physical coordinates lack separated, source-ordered locators")


def factored_polynomial(roots):
    p=[Q(1)]
    for q in roots:p=times(p,[-q,Q(1)])
    return p


def audit_gcd(test,p,q,proof):
    test.assertEqual(trim(proof["left_polynomial"]),trim(p))
    test.assertEqual(trim(proof["right_polynomial"]),trim(q))
    a,b=trim(p),trim(q)
    for row in proof["euclidean_trace"]:
        test.assertEqual(trim(row["dividend"]),a)
        test.assertEqual(trim(row["divisor"]),b)
        quotient,remainder=independent_division(a,b)
        test.assertEqual(trim(row["quotient"]),quotient)
        test.assertEqual(trim(row["remainder"]),remainder)
        test.assertTrue(remainder==[0] or len(remainder)<len(b))
        a,b=b,remainder
    test.assertEqual(b,[Q(0)]);test.assertNotEqual(a,[Q(0)])
    test.assertEqual(trim(proof["last_nonzero_remainder"]),a)
    test.assertEqual(Q(proof["monic_scale"]),1/a[-1])
    test.assertEqual(trim(proof["monic_gcd"]),independent_gcd(p,q))
    test.assertIs(proof["all_divisions_and_degree_descents_verified"],True)
    return independent_gcd(p,q)


def audit_sturm(test,p,proof):
    p=trim(p);test.assertNotEqual(p,[0])
    test.assertEqual(trim(proof["polynomial"]),p)
    repeated=audit_gcd(test,p,derivative(p),proof["gcd_with_derivative"])
    square_free,remainder=independent_division(p,repeated)
    test.assertEqual(remainder,[Q(0)])
    test.same(proof["square_free_division"],{"dividend":list(map(str,p)),"divisor":list(map(str,repeated)),
              "quotient":list(map(str,square_free)),"remainder":["0"]})
    test.assertEqual(trim(proof["square_free_polynomial"]),square_free)
    seq=[square_free]
    if independent_degree(square_free)>0:seq.append(derivative(square_free))
    trace=[]
    while len(seq)>1:
        a,b=seq[-2:];quotient,remainder=independent_division(a,b)
        trace.append({"dividend":list(map(str,a)),"divisor":list(map(str,b)),
                      "quotient":list(map(str,quotient)),"remainder":list(map(str,remainder))})
        if remainder==[0]:break
        seq.append([-v for v in remainder])
    test.same(proof["sequence"],[list(map(str,row)) for row in seq])
    test.same(proof["division_trace"],trace)
    test.assertIs(proof["negative_remainders_without_sign_changing_rescaling"],True)
    test.assertIs(proof["square_free_part_verified"],True)
    return seq


def audit_side_sign(test,p,x,side,proof):
    member=trim(p);order=0
    while at(member,x)==0:
        member=derivative(member);order+=1
        if member==[0]:raise AssertionError("zero polynomial side receipt")
    value=at(member,x);sign=independent_side_sign(p,x,-1 if side=="LEFT" else 1)
    test.same(proof,{"polynomial":list(map(str,p)),"coordinate":str(x),"side":side,
                    "first_nonzero_derivative_order":order,"first_nonzero_derivative_value":str(value),
                    "sign":sign,"exact_taylor_side_sign":True})
    return sign


def audit_open_count(test,p,a,b,proof):
    p=trim(p)
    test.assertEqual(trim(proof["polynomial"]),p)
    test.same(proof["interval"],[str(a),str(b)])
    seq=audit_sturm(test,p,proof["sturm"])
    left,right=proof["left_right_limit_signs"],proof["right_left_limit_signs"]
    test.assertEqual(len(left),len(seq));test.assertEqual(len(right),len(seq))
    ls=[audit_side_sign(test,s,a,"RIGHT",r) for s,r in zip(seq,left)]
    rs=[audit_side_sign(test,s,b,"LEFT",r) for s,r in zip(seq,right)]
    test.assertIs(type(proof["left_variations"]),int)
    test.assertIs(type(proof["right_variations"]),int)
    test.assertIs(type(proof["open_root_count"]),int)
    lv,rv=independent_variations(ls),independent_variations(rs)
    test.assertEqual((proof["left_variations"],proof["right_variations"]),(lv,rv))
    test.assertEqual(proof["open_root_count"],lv-rv)
    test.assertEqual(proof["open_root_count"],independent_count(p,a,b))
    test.assertIs(proof["both_interval_endpoints_excluded"],True)
    return lv-rv


def audit_isolation(test,g,left,right,h_events,proof):
    """Check the complete search tree using an independent Fraction/Sturm oracle."""
    g=trim(g)
    test.assertEqual(trim(proof["G"]),g)
    test.same(proof["source_interval"],[str(left),str(right)])
    sequence=audit_sturm(test,g,proof["sturm"])
    square_free=sequence[0]
    test.assertEqual(trim(proof["square_free_polynomial"]),square_free)
    h_by_point={Q(event["coordinate"]["value"]):event for event in h_events}
    points=sorted({left,right,*h_by_point})
    boundaries=[{"coordinate":str(t),"G_value":str(at(g,t)),"is_G_root":at(g,t)==0,
                 "residual_event_id":h_by_point[t]["event_id"] if t in h_by_point else None,
                 "source_exterior_side":"LEFT" if t==left else "RIGHT" if t==right else None}
                for t in points]
    test.same(proof["partition_boundaries"],boundaries)
    raw_roots=[{"coordinate":{"kind":"RATIONAL","value":str(t)},
                "discovery":{"kind":"PARTITION_BOUNDARY","boundary_index":i}}
               for i,t in enumerate(points) if at(g,t)==0]
    closed=audit_open_count(test,g,left,right,proof["closed_interval_open_count_receipt"])
    closed+=int(at(g,left)==0)+int(at(g,right)==0)
    test.assertIs(type(proof["closed_polynomial_root_count"]),int)
    test.assertEqual(proof["closed_polynomial_root_count"],closed)
    test.assertLessEqual(closed,max(0,independent_degree(g)))
    gaps=proof["initial_gap_searches"]
    test.assertEqual(len(gaps),len(points)-1)
    queue=[]
    for i,(a,b,gap) in enumerate(zip(points,points[1:],gaps)):
        node="GAP_"+str(i)
        test.assertEqual(gap["node_id"],node)
        test.same(gap["interval"],[str(a),str(b)])
        count=audit_open_count(test,g,a,b,gap["count_receipt"])
        queue.append((node,a,b,count))
    operations=0
    for row in proof["isolation_trace"]:
        test.assertTrue(queue,"trace contains a node outside the complete search tree")
        node,a,b,count=queue.pop(0)
        test.assertEqual(row["node_id"],node)
        test.same(row["interval"],[str(a),str(b)])
        test.assertIs(type(row["open_root_count"]),int)
        test.assertEqual(row["open_root_count"],count)
        test.assertEqual(audit_open_count(test,g,a,b,row["count_receipt"]),count)
        av,bv=at(g,a),at(g,b)
        test.assertEqual((row["left_G_value"],row["right_G_value"]),(str(av),str(bv)))
        action=row["action"]
        if action=="EMPTY_OPEN_INTERVAL":
            test.assertEqual(count,0)
        elif action=="LINEAR_EXACT_ROOT":
            test.assertEqual(count,1);test.assertEqual(independent_degree(square_free),1)
            t=-square_free[0]/square_free[1]
            test.assertTrue(a<t<b);test.assertEqual(at(g,t),0)
            test.same(row["coordinate"],{"kind":"RATIONAL","value":str(t)})
            raw_roots.append({"coordinate":copy.deepcopy(row["coordinate"]),
                              "discovery":{"kind":action,"node_id":node}})
        elif action=="STRICT_UNIQUE_OPEN_ISOLATOR":
            test.assertEqual(count,1);test.assertNotEqual(av,0);test.assertNotEqual(bv,0)
            coordinate={"kind":"REAL_ALGEBRAIC_ISOLATOR","defining_polynomial":list(map(str,square_free)),
                        "isolating_interval":[str(a),str(b)],"unique_root_in_open_interval":True,
                        "defining_polynomial_square_free":True,"defining_polynomial_irreducible_claimed":False,
                        "coordinate_irrationality_claimed":False}
            test.same(row["coordinate"],coordinate)
            test.assertFalse(any(a<t<b for t in h_by_point))
            raw_roots.append({"coordinate":coordinate,"discovery":{"kind":action,"node_id":node}})
        else:
            test.assertEqual(action,"EXACT_MIDPOINT_SPLIT")
            test.assertGreater(count,0)
            t=(a+b)/2;value=at(g,t)
            test.assertEqual(row["midpoint"],str(t))
            test.assertEqual(row["midpoint_G_value"],str(value))
            test.assertIs(row["midpoint_is_G_root"],value==0)
            nl=audit_open_count(test,g,a,t,row["left_count_receipt"])
            nr=audit_open_count(test,g,t,b,row["right_count_receipt"])
            test.assertEqual(count,nl+int(value==0)+nr)
            operations+=1
            if value==0:
                raw_roots.append({"coordinate":{"kind":"RATIONAL","value":str(t)},
                                  "discovery":{"kind":"EXACT_MIDPOINT","node_id":node}})
            queue.extend(((node+":L",a,t,nl),(node+":R",t,b,nr)))
    test.assertEqual(queue,[],"a strict original search gap has not been discharged")
    test.assertIs(type(proof["midpoint_operations"]),int)
    test.assertEqual(proof["midpoint_operations"],operations)
    test.assertIs(type(proof["global_midpoint_budget"]),int)
    test.assertTrue(0<=operations<=proof["global_midpoint_budget"]<=128)
    chain=independent_multiplicity_chain(g)
    test.assertEqual(len(proof["multiplicity_chain"]),len(chain))
    for i,(poly,row) in enumerate(zip(chain,proof["multiplicity_chain"])):
        test.assertIs(type(row["level"]),int);test.assertEqual(row["level"],i)
        test.assertEqual(trim(row["polynomial"]),poly)
        audit_sturm(test,poly,row["sturm"])
        audit_gcd(test,poly,derivative(poly),row["next_gcd"])
    raw_roots.sort(key=cmp_to_key(lambda a,b:compare_coordinates(a["coordinate"],b["coordinate"])))
    test.assertEqual(len(raw_roots),closed)
    test.assertEqual(len(proof["roots"]),closed)
    previous=None
    for i,(actual,raw) in enumerate(zip(proof["roots"],raw_roots)):
        test.assertEqual(actual["polynomial_root_id"],"GROOT_"+str(i))
        test.same(actual["coordinate"],raw["coordinate"])
        test.same(actual["discovery"],raw["discovery"])
        a,b=coordinate_bounds(raw["coordinate"])
        if previous is not None:test.assertLess(compare_coordinates(previous,raw["coordinate"]),0)
        previous=raw["coordinate"]
        memberships=[]
        evidence=actual["multiplicity_evidence"]
        test.assertEqual(len(evidence["chain_membership"]),len(chain))
        for level,(poly,row) in enumerate(zip(chain,evidence["chain_membership"])):
            test.assertIs(type(row["level"]),int);test.assertEqual(row["level"],level)
            if a==b:
                value=at(poly,a);count=int(value==0)
                test.assertEqual(row["rational_value"],str(value))
                test.assertIsNone(row["open_count_receipt"])
            else:
                count=audit_open_count(test,poly,a,b,row["open_count_receipt"])
                test.assertIsNone(row["rational_value"])
            test.assertIs(type(row["root_count"]),int)
            test.assertEqual(row["root_count"],count)
            memberships.append(count)
        test.assertEqual(memberships,sorted(memberships,reverse=True))
        multiplicity=sum(memberships)
        test.assertIn(multiplicity,(1,2,3))
        test.assertEqual((actual["multiplicity"],evidence["multiplicity"]),(multiplicity,multiplicity))
        if a==b:
            test.assertEqual(rational_multiplicity(g,a),multiplicity)
            derivative_poly=g
            for _ in range(multiplicity):derivative_poly=derivative(derivative_poly)
            test.same(evidence["rational_derivative_cross_check"],{"first_nonzero_order":multiplicity,
                      "first_nonzero_derivative_value":str(at(derivative_poly,a))})
        else:test.assertIsNone(evidence["rational_derivative_cross_check"])
        test.assertIs(evidence["multiplicity_counted_from_actual_gcd_chain"],True)
    for key in ("all_endpoint_cleaning_splits_counted","all_original_gaps_searched",
                "closed_count_equals_boundary_plus_isolated_roots","no_residual_root_inside_exported_open_isolator"):
        test.assertIs(proof[key],True)
    test.assertIs(proof["minimal_polynomial_or_irrationality_claimed"],False)
    return proof["roots"]


def independent_physical_union(test,spec,g,g_roots,residual):
    """Project the separately proved G and H sets, retaining both owner identities."""
    source_hash=digest(spec);parameter=spec["source_parameter_id"]
    left,right=Q(spec["parameter_lo"]),Q(spec["parameter_hi"])
    h_events=residual["source_zero_set"]["events"]
    h_by_point={Q(e["coordinate"]["value"]):e for e in h_events}
    occurrences=[];consumed=set()
    for groot in g_roots:
        coordinate=groot["coordinate"];a,b=coordinate_bounds(coordinate)
        h=h_by_point.get(a) if a==b else None
        if h is not None:
            test.assertEqual(at(g,a),0);consumed.add(h["event_id"])
        else:test.assertFalse(any(a<t<b for t in h_by_point))
        occurrences.append((coordinate,groot,h))
    for h in h_events:
        if h["event_id"] not in consumed:
            test.assertNotEqual(at(g,Q(h["coordinate"]["value"])),0)
            occurrences.append((h["coordinate"],None,h))
    occurrences.sort(key=cmp_to_key(lambda a,b:compare_coordinates(a[0],b[0])))
    events=[]
    for i,(coordinate,groot,h) in enumerate(occurrences):
        a,b=coordinate_bounds(coordinate);at_left=a==b==left;at_right=a==b==right
        gm=groot["multiplicity"] if groot else 0;ho=2 if h else 0;order=2*gm+ho
        test.assertIn(order,(2,4,6,8))
        order_record=({"kind":"ONE_SIDED","side":"RIGHT" if at_left else "LEFT","inward_order":order,
                       "outside_order":None,"global_smooth_multiplicity_claimed":False} if at_left or at_right
                      else {"kind":"SMOOTH","multiplicity":order})
        events.append({"event_id":"ZERO_"+str(i),"source_sha256":source_hash,"source_parameter_id":parameter,
            "coordinate":copy.deepcopy(coordinate),"location":"LEFT_EXTERIOR" if at_left else "RIGHT_EXTERIOR" if at_right else "SPAN_INTERIOR",
            "source_piece_indices":[0],"classification":"TOUCHING","order":order_record,"physical_order":order,
            "polynomial_root_id":groot["polynomial_root_id"] if groot else None,"polynomial_multiplicity":gm,
            "residual_event_id":h["event_id"] if h else None,"residual_root_order":ho,
            "residual_source_sha256":residual["source_sha256"],
            "order_addition":{"squared_G_order":2*gm,"H_order":ho,"physical_order":order},
            "left_sign":None if at_left else 1,"right_sign":None if at_right else 1,
            "complete_residual_positivity_used_away_from_its_roots":h is None})
    by_exterior={Q(e["coordinate"]["value"]):e for e in events if e["location"]!="SPAN_INTERIOR"}
    def event_boundary(event):
        return {"kind":"PHYSICAL_ZERO_EVENT","event_id":event["event_id"],"coordinate":copy.deepcopy(event["coordinate"]),
                "source_sha256":source_hash,"source_parameter_id":parameter}
    def exterior_boundary(t,side):
        if t in by_exterior:return event_boundary(by_exterior[t])
        return {"kind":"SOURCE_EXTERIOR","side":side,"coordinate":{"kind":"RATIONAL","value":str(t)},
                "source_sha256":source_hash,"source_parameter_id":parameter}
    boundaries=[exterior_boundary(left,"LEFT"),*[event_boundary(e) for e in events if e["location"]=="SPAN_INTERIOR"],
                exterior_boundary(right,"RIGHT")]
    cells=[]
    for i,(a,b) in enumerate(zip(boundaries,boundaries[1:])):
        test.assertLess(compare_coordinates(a["coordinate"],b["coordinate"]),0)
        cells.append({"cell_id":"CELL_"+str(i),"left_boundary":a,"right_boundary":b,
                      "left_included":a["kind"]=="SOURCE_EXTERIOR","right_included":b["kind"]=="SOURCE_EXTERIOR",
                      "sign":1,"source_piece_indices":[0],"crossed_nonzero_source_knots":[],
                      "positive_from_G_squared_times_complete_residual":True})
    offset,rate=Q(spec["phase_turn_offset"]),Q(spec["phase_turn_rate"])
    exteriors=[]
    for side,t in (("LEFT",left),("RIGHT",right)):
        event=by_exterior.get(t)
        exteriors.append({"side":side,"coordinate":str(t),"phase_turn":str(offset+rate*t),"is_zero":event is not None,
            "event_ref":event["event_id"] if event else None,"value_sign":0 if event else 1,
            "exact_value":"0" if event else None,"nonzero_exact_scalar_value_claimed":False,
            "positive_sign_from_complete_nonnegative_square_proof":event is None,"inward_sign":1,
            "inward_order":event["physical_order"] if event else 0,"outside_sign":None,"outside_order":None,
            "global_smooth_multiplicity_claimed":False})
    return {"kind":"FINITE_ORIGINAL_SOURCE_ZERO_SET","complete_for_original_closed_source":True,
            "source_interval":[str(left),str(right)],"closed_root_count":len(events),"events":events,
            "source_open_root_count":len(events)-len(by_exterior),"exterior_root_count":len(by_exterior),
            "true_source_knots":[],"exterior_points":exteriors,"maximal_nonzero_cells":cells,
            "finite_event_list_applicable":True,"nonzero_sign_cells_applicable":True,
            "all_physical_roots_have_even_order":True,"nonzero_source_points_strictly_positive":True,
            "continuum_excluded_by_nonzero_G_and_coprime_moving_residual":True,
            "global_cross_source_zero_deduplication_performed":False,
            "isolator_endpoints_substituted_for_physical_root_boundaries":False}


def audit_shared_certificate(test,spec,p,q,certificate):
    p,q=trim(p),trim(q)
    test.assertEqual(certificate["status"],"ESTABLISHED_SHARED_SQUARE_ORIGINAL_SOURCE")
    test.assertIs(certificate["proof_established"],True);test.assertIs(certificate["source_zero_set_established"],True)
    test.assertIs(certificate["production_authorized"],False)
    test.same(certificate["original_source"],spec)
    test.assertEqual(certificate["source_sha256"],digest(spec))
    test.assertEqual(certificate["source_parameter_id"],spec["source_parameter_id"])
    test.same(certificate["source_interval"],[spec["parameter_lo"],spec["parameter_hi"]])
    test.same(certificate["phase_turn_law"],{"offset":spec["phase_turn_offset"],"rate":spec["phase_turn_rate"]})
    witness={"P":list(map(str,p)),"Q":list(map(str,q))}
    test.same(certificate["normalized_witness"],witness)
    test.same(certificate["supplied_witness"],witness)
    test.assertEqual(certificate["witness_sha256"],digest(witness))
    c0,c1=audit_lowering(test,spec,p,q,certificate["whole_source_lowering"])
    test.same(certificate["source_identity"],{"P_squared":list(map(str,times(p,p))),"Q_squared":list(map(str,times(q,q))),
        "C0_equals_half_sum_of_squares":list(map(str,c0)),"C1_equals_half_difference_of_squares":list(map(str,c1)),
        "identities_verified_coefficientwise":True,"original_source_equals_nonnegative_square_sum":True,
        "all_original_channels_reconstructed":True,"phase_used_in_original_parameter":True})
    test.same(certificate["input_custody"],model.INPUT_RECORDS)
    continuum=p==q==[Q(0)]
    if continuum:
        for key in ("decomposition","residual","polynomial_root_proof"):test.assertIsNone(certificate[key])
        interval=[spec["parameter_lo"],spec["parameter_hi"]]
        expected={"kind":"CLOSED_CONTINUUM_ORIGINAL_SOURCE_ZERO_SET","complete_for_original_closed_source":True,
            "source_interval":interval,"zero_interval":{"interval":interval,"left_included":True,"right_included":True},
            "original_source_identically_zero":True,"closed_root_count":None,"events":None,"source_open_root_count":None,
            "exterior_root_count":None,"true_source_knots":[],
            "exterior_points":[{"side":side,"coordinate":spec[key],"is_zero":True,"exact_value":"0",
                "isolated_root_order":None,"outside_sign":None,"outside_order":None}
                for side,key in (("LEFT","parameter_lo"),("RIGHT","parameter_hi"))],
            "maximal_nonzero_cells":None,"finite_event_list_applicable":False,"nonzero_sign_cells_applicable":False,
            "finite_root_cardinality_claimed":False,"residual_producer_applicable":False}
        test.same(certificate["source_zero_set"],expected)
    else:
        d=certificate["decomposition"]
        g=audit_gcd(test,p,q,d["gcd_proof"])
        test.assertEqual(trim(d["G"]),g)
        quotients=[]
        for name,poly in (("P",p),("Q",q)):
            quotient,remainder=independent_division(poly,g)
            test.assertEqual(remainder,[Q(0)]);quotients.append(quotient)
            test.same(d[name+"_division"],{"dividend":list(map(str,poly)),"divisor":list(map(str,g)),
                      "quotient":list(map(str,quotient)),"remainder":["0"]})
            test.assertEqual(trim(d[name+"0"]),quotient)
        p0,q0=quotients;g2=times(g,g)
        h0=[v/2 for v in plus(times(p0,p0),times(q0,q0))]
        h1=[v/2 for v in plus(times(p0,p0),[-v for v in times(q0,q0)])]
        for key,poly in (("G_squared",g2),("residual_C0",h0),("residual_C1",h1),
                         ("original_C0_product",c0),("original_C1_product",c1)):
            test.assertEqual(trim(d[key]),trim(poly))
        test.assertEqual(times(g2,h0),c0);test.assertEqual(times(g2,h1),c1)
        test.assertIs(d["original_parameter_and_scale_preserved"],True)
        test.assertIs(d["factor_square_not_discarded"],True)
        residual=certificate["residual"]
        test.assertEqual(residual["producer_code"],model.COPRIME_MODEL)
        test.assertEqual(residual["producer_git_blob"],model.COPRIME_BLOB)
        test.assertIs(residual["actual_generic_producer_called"],True);test.assertIs(residual["saved_report_used_as_proof"],False)
        source=residual["source"]
        independently_built=supplied_source(p0,q0,lo=Q(spec["parameter_lo"]),hi=Q(spec["parameter_hi"]),
            offset=Q(spec["phase_turn_offset"]),rate=Q(spec["phase_turn_rate"]),parameter=spec["source_parameter_id"])
        test.same(source,independently_built)
        test.assertEqual(residual["source_sha256"],digest(source))
        test.same(residual["P0"],list(map(str,p0)));test.same(residual["Q0"],list(map(str,q0)))
        audit_residual_certificate(test,source,p0,q0,residual["certificate"])
        g_roots=audit_isolation(test,g,Q(spec["parameter_lo"]),Q(spec["parameter_hi"]),
                                residual["certificate"]["source_zero_set"]["events"],certificate["polynomial_root_proof"])
        test.same(certificate["source_zero_set"],independent_physical_union(test,spec,g,g_roots,residual["certificate"]))
    test.same(certificate["theorem_premises"],{
        "original_source_equals_G_squared_times_fresh_coprime_residual":not continuum,
        "shared_polynomial_factor_is_retained":not continuum,"complete_polynomial_roots_from_checked_sturm":not continuum,
        "residual_roots_and_positive_complement_freshly_proved":not continuum,"analytic_product_orders_add":not continuum,
        "identity_zero_proved_from_complete_original_controls":continuum,
        "numerical_samples_or_saved_reports_used_as_completeness_authority":False,
        "pi_irrationality_or_transcendence_used":False})
    for key in ("generic_supplied_source_and_witness_checked","one_original_clamped_span","valid_degree_elevation_admitted",
                "original_parameter_and_global_phase_preserved","algebraic_descriptors_do_not_claim_minimality_or_irrationality",
                "residual_raw_input_envelope_unchanged"):
        test.assertIs(certificate["scope"][key],True)
    for key in ("fixture_allowlist_used_for_admission","MC032_reference_executed","frozen_corpus_addition",
                "historical_source_completion_claimed","generic_owner_route_repaired","native_geometry_evidence"):
        test.assertIs(certificate["scope"][key],False)


class SharedSquareTests(unittest.TestCase):
    replay=None
    report=None

    @classmethod
    def setUpClass(cls):
        if cls.replay is None:cls.replay=model.replay_sources()
        if cls.report is None:cls.report=model.report_from_replay(cls.replay)
        cls.expected_bytes=canonical(cls.report)
        cls.c=model.qualified_coprime_module()

    def same(self,a,b,message=None):self.assertEqual(canonical(a),canonical(b),message)

    def nontruth(self,result):
        self.assertEqual(result["status"],"REFUSED")
        for key in ("source_zero_set_established","proof_established","production_authorized"):
            self.assertIs(result[key],False)
        self.assertIsNone(result["source_zero_set"])
        for key in ("partial_roots","successful_partial_roots","certificate"):
            self.assertNotIn(key,result)

    def prove(self,p,q,**options):
        p,q=trim(p),trim(q);spec=supplied_source(p,q,**options)
        hints=list(map(str,p)),list(map(str,q))
        certificate=model.certify_source(spec,*hints)
        audit_shared_certificate(self,spec,p,q,certificate)
        return spec,hints,certificate

    def test_independent_one_sided_oracle_against_known_factored_roots(self):
        endpoints=[Q(-2),Q(-1),-Q(1,2),Q(0),Q(1,3),Q(1,2),Q(2,3),Q(1),Q(2)]
        families=([Q(0)],[Q(1,2),Q(1,2)],[-Q(1,2),Q(0),Q(1)],
                  [-Q(1,3),Q(1,2),Q(1,2)],[Q(1,3),Q(2,3)],[Q(1),Q(1),Q(1)])
        total=0
        for roots in families:
            p=factored_polynomial(roots)
            for i,a in enumerate(endpoints):
                for b in endpoints[i+1:]:
                    count=sum(a<r<b for r in set(roots))
                    self.assertEqual(independent_count(p,a,b),count)
                    receipt=model.count_roots_open(self.c,tuple(p),a,b)
                    audit_open_count(self,p,a,b,receipt)
                    total+=1
            for root in set(roots):self.assertEqual(rational_multiplicity(p,root),roots.count(root))
        self.assertEqual(total,216)

    def test_maximum_order_eight_from_zero_amplitude_and_cubic_common_root(self):
        p,q=trim([0]),trim([-1,3,-3,1])
        spec,hints,certificate=self.prove(p,q,lo=Q(1,2),hi=Q(3,2),parameter="dynamic-order-eight")
        zero=certificate["source_zero_set"]
        self.assertEqual(zero["closed_root_count"],1)
        self.assertEqual(zero["events"][0]["coordinate"],{"kind":"RATIONAL","value":"1"})
        self.assertEqual(zero["events"][0]["physical_order"],8)
        self.assertEqual(zero["events"][0]["polynomial_multiplicity"],3)
        self.assertEqual(zero["events"][0]["residual_root_order"],2)

    def test_thirty_six_roots_include_three_polynomial_roots_in_one_carrier_gap(self):
        g=factored_polynomial([Q(1,10),Q(1,11),Q(1,12)])
        spec,hints,certificate=self.prove([0],g,lo=Q(-2),hi=Q(2),rate=Q(8),
                                        parameter="dynamic-thirty-six-roots")
        zero=certificate["source_zero_set"]
        self.assertEqual(zero["closed_root_count"],36)
        self.assertEqual(zero["exterior_root_count"],2)
        self.assertEqual(len(zero["maximal_nonzero_cells"]),35)
        self.assertTrue(all(e["physical_order"]==2 for e in zero["events"]))
        self.assertEqual(len(certificate["residual"]["certificate"]["phase_candidates"]["candidates"]),65)
        self.assertEqual(independent_count(g,Q(0),Q(1,8)),3)

    def test_reducible_square_free_descriptors_and_zero_midpoint_cleanup(self):
        p=trim([0,-Q(1,2),0,1])
        spec,hints,certificate=self.prove(p,p,lo=Q(-1),hi=Q(1),parameter="dynamic-reducible-descriptors")
        zero=certificate["source_zero_set"]
        self.assertEqual(zero["closed_root_count"],3)
        rational=[e for e in zero["events"] if e["coordinate"]["kind"]=="RATIONAL"]
        self.assertEqual([e["coordinate"]["value"] for e in rational],["0"])
        algebraic=[e["coordinate"] for e in zero["events"] if e["coordinate"]["kind"]!="RATIONAL"]
        self.assertEqual(len(algebraic),2)
        for coordinate in algebraic:
            self.assertIs(coordinate["defining_polynomial_irreducible_claimed"],False)
            self.assertIs(coordinate["coordinate_irrationality_claimed"],False)
            self.assertEqual(trim(coordinate["defining_polynomial"]),p)
            for bound in coordinate["isolating_interval"]:self.assertNotEqual(at(p,Q(bound)),0)

    def test_polynomial_isolator_bounds_may_be_physical_carrier_zeros(self):
        g=trim([-Q(1,2),0,1])
        spec,hints,certificate=self.prove([0],g,lo=Q(-1),hi=Q(1),parameter="dynamic-carrier-zero-isolator-bounds")
        zero=certificate["source_zero_set"]
        self.assertEqual((zero["closed_root_count"],zero["exterior_root_count"],len(zero["maximal_nonzero_cells"])),(5,2,4))
        descriptors=[e["coordinate"] for e in zero["events"] if e["coordinate"]["kind"]=="REAL_ALGEBRAIC_ISOLATOR"]
        self.assertEqual(len(descriptors),2)
        carrier_zeros={Q(-1),Q(0),Q(1)}
        for coordinate in descriptors:
            lo,hi=coordinate_bounds(coordinate)
            self.assertNotEqual(at(g,lo),0);self.assertNotEqual(at(g,hi),0)
            self.assertTrue(lo in carrier_zeros and hi in carrier_zeros)

    def test_residual_raw_envelope_failure_is_atomic_for_valid_bounded_original(self):
        n=Q(1<<60)
        self.prove([0,n],[0,n],hi=1/n,parameter="dynamic-small-domain-admitted-residual")
        n=Q(1<<100);spec=supplied_source([0,n],[0,n],hi=1/n,
                                       parameter="dynamic-small-domain-residual-resource-limit")
        self.assertEqual(spec["cos_splines"]["0"]["controls"],["0","0","1"])
        self.assertEqual(spec["cos_splines"]["1"]["controls"],["0"])
        for spline in spec["cos_splines"].values():
            for token in spline["knots"]+spline["controls"]:
                value=Q(token)
                self.assertLessEqual(max(value.numerator.bit_length(),value.denominator.bit_length()),128)
        result=model.check_source(spec,["0",str(n)],["0",str(n)])
        self.nontruth(result)
        self.assertEqual(result["code"],"RESOURCE_REFUSAL")

    def test_rational_root_may_use_algebraic_format_without_irrationality_claim(self):
        p=factored_polynomial([Q(1,3),Q(2,3)])
        spec,hints,certificate=self.prove(p,p,parameter="dynamic-rational-algebraic-format")
        roots=certificate["source_zero_set"]["events"]
        self.assertEqual(len(roots),2)
        for event,actual in zip(roots,(Q(1,3),Q(2,3))):
            coordinate=event["coordinate"]
            if coordinate["kind"]=="RATIONAL":self.assertEqual(Q(coordinate["value"]),actual)
            else:
                lo,hi=coordinate_bounds(coordinate)
                self.assertTrue(lo<actual<hi)
                self.assertIs(coordinate["coordinate_irrationality_claimed"],False)

    def test_gcd_one_and_empty_residual_candidate_sources_remain_admitted(self):
        self.prove([-1,1],[1],lo=Q(1,2),hi=Q(3,2),parameter="dynamic-gcd-one")
        self.prove([1],[1],offset=Q(1,8),rate=Q(1,16),parameter="dynamic-empty-residual-candidates")

    def test_repeated_noncoincident_common_root_has_order_six(self):
        p=factored_polynomial([Q(1,3)]*3)
        spec,hints,certificate=self.prove(p,p,parameter="dynamic-order-six-noncoincident")
        event=certificate["source_zero_set"]["events"][0]
        self.assertEqual(event["physical_order"],6)
        self.assertEqual(event["residual_root_order"],0)
        self.assertIsNone(event["residual_event_id"])

    def test_nonmonic_signed_factors_preserve_exact_scale_in_quotients(self):
        g=trim([-Q(1,3),1]);p=[-6*x for x in times(g,[-1,1])];q=[9*x for x in g]
        self.prove(p,q,lo=-Q(1,2),hi=Q(3,2),offset=Q(1,4),rate=-Q(1,2),
                   parameter="dynamic-nonmonic-signed-global-source")

    def test_valid_elevation_and_changed_parameter_cannot_reuse_old_certificate(self):
        p=trim([-Q(1,3),1]);spec,hints,old=self.prove(p,p,parameter="dynamic-elevated-shared-source")
        elevated,hints,new=self.prove(p,p,degree0=6,degree1=6,parameter="dynamic-elevated-shared-source")
        self.assertNotEqual(digest(spec),digest(elevated))
        with self.assertRaises(model.Refusal):model.validate_certificate(elevated,*hints,old)
        self.assertTrue(model.validate_certificate(elevated,*hints,new))
        for field,value in (("source_parameter_id","new-shared-original-parameter"),("phase_turn_offset","1/4"),
                            ("phase_turn_rate","-1")):
            changed=copy.deepcopy(spec);changed[field]=value
            fresh=model.certify_source(changed,*hints);audit_shared_certificate(self,changed,p,p,fresh)
            with self.assertRaises(model.Refusal):model.validate_certificate(changed,*hints,old)

    def test_continuum_proves_original_zero_without_residual_call(self):
        spec=supplied_source([0],[0],degree0=6,degree1=6,parameter="dynamic-elevated-identity-zero")
        with mock.patch.object(model,"qualified_coprime_module",return_value=self.c), \
             mock.patch.object(self.c,"certify_source",side_effect=AssertionError("continuum reached coprime producer")) as residual:
            certificate=model.certify_source(spec,["0"],["0"])
        residual.assert_not_called()
        audit_shared_certificate(self,spec,[Q(0)],[Q(0)],certificate)
        self.assertIsNone(certificate["residual"])
        self.assertIsNone(certificate["polynomial_root_proof"])
        wrong=copy.deepcopy(spec);wrong["cos_splines"]["0"]["controls"][0]="1"
        self.nontruth(model.check_source(wrong,["0"],["0"]))

    def test_actual_residual_producer_failure_is_not_replaced_with_saved_evidence(self):
        spec=supplied_source([-Q(1,3),1],[-Q(1,3),1])
        with mock.patch.object(model,"qualified_coprime_module",return_value=self.c), \
             mock.patch.object(self.c,"certify_source",side_effect=RuntimeError("CONTROLLED_ACTUAL_RESIDUAL_FAILURE")) as producer:
            result=model.check_source(spec,["-1/3","1"],["-1/3","1"])
        self.assertGreater(producer.call_count,0)
        self.nontruth(result)

    def test_actual_source_lowering_and_new_proof_hook_failures_are_atomic(self):
        p=["-1/2","0","1"];spec=supplied_source(p,p,lo=Q(-1),hi=Q(1))
        with mock.patch.object(model,"qualified_coprime_module",return_value=self.c), \
             mock.patch.object(self.c,"lower_source",side_effect=self.c.Refusal("CONTROLLED_LOWERING_FAILURE")) as lower:
            self.nontruth(model.check_source(spec,p,p));self.assertGreater(lower.call_count,0)
        for name in ("checked_gcd","sturm_sequence","one_sided_sign","count_roots_open",
                     "isolate_polynomial_roots","assemble_physical_union"):
            def fail(*args,**kwargs):raise model.Refusal("CONTROLLED_"+name.upper()+"_FAILURE")
            with self.subTest(hook=name),mock.patch.object(model,name,side_effect=fail) as hook:
                self.nontruth(model.check_source(spec,p,p));self.assertGreater(hook.call_count,0)

    def test_complete_original_identity_and_moving_phase_class_are_required(self):
        p=["-1/3","1"];spec=supplied_source(p,p)
        # A common-root hint does not authorize discarding the actual original
        # constant source, or accepting a different full harmonic coefficient.
        constant=supplied_source([1],[1])
        self.nontruth(model.check_source(constant,p,p))
        changed=copy.deepcopy(spec);changed["cos_splines"]["0"]["controls"][-1]="1"
        self.nontruth(model.check_source(changed,p,p))
        changed=copy.deepcopy(spec);changed["cos_splines"]["1"]["controls"][0]="1/7"
        self.nontruth(model.check_source(changed,p,p))
        for field,value in (("phase_turn_rate","0"),("phase_turn_rate","9"),
                            ("phase_turn_offset","17"),("parameter_lo","-3"),("parameter_hi","3")):
            changed=copy.deepcopy(spec);changed[field]=value
            with self.subTest(field=field,value=value):self.nontruth(model.check_source(changed,p,p))
        for source in (dict(spec,sin_splines={"1":copy.deepcopy(spec["cos_splines"]["1"])}),
                       dict(spec,cos_splines={"0":copy.deepcopy(spec["cos_splines"]["0"])})):
            self.nontruth(model.check_source(source,p,p))

    def test_global_isolation_budget_includes_midpoint_and_bound_cleanup(self):
        p=["0","-1/2","0","1"];spec=supplied_source(p,p,lo=Q(-1),hi=Q(1))
        # Three roots require a midpoint-zero split, then cleaning zero0 from
        # each of the two other roots' isolator boundaries: at least3 operations.
        for budget in (0,1,2):
            with self.subTest(budget=budget),mock.patch.object(model,"MAX_MIDPOINT_OPERATIONS",budget):
                result=model.check_source(spec,p,p)
                self.nontruth(result);self.assertEqual(result["code"],"RESOURCE_REFUSAL")
        for budget in (True,False,-1,129,10**100,"128",None):
            with self.subTest(budget=budget),mock.patch.object(model,"MAX_MIDPOINT_OPERATIONS",budget):
                self.nontruth(model.check_source(spec,p,p))

    def test_sturm_input_degree_and_operand_bounds_precede_arithmetic(self):
        with mock.patch.object(self.c,"poly_divmod",side_effect=AssertionError("unbounded polynomial divided")) as division:
            for p in ((Q(1),)*5,(Q(1,1<<4097),),[True],[1],["1"]):
                with self.subTest(poly_type=type(p).__name__),self.assertRaises(model.Refusal):
                    model.checked_gcd(self.c,p,(Q(1),))
            division.assert_not_called()
        with mock.patch.object(self.c,"poly_eval",side_effect=AssertionError("unbounded point evaluated")) as evaluate:
            for q in (True,0,0.5,"0",None,Q(1,1<<4097)):
                with self.subTest(point_type=type(q).__name__),self.assertRaises(model.Refusal):
                    model.one_sided_sign(self.c,(Q(0),Q(1)),q,"RIGHT")
            evaluate.assert_not_called()

    def test_complete_raw_source_hint_preflight_precedes_fraction_work(self):
        p=["-1/3","1"];spec=supplied_source(p,p)
        cases=[]
        for mutate in (lambda s:s["cos_splines"]["1"]["controls"].__setitem__(-1,"1e999999999"),
                       lambda s:s["cos_splines"]["0"].__setitem__("degree",True),
                       lambda s:s["cos_splines"]["0"].__setitem__("degree",7),
                       lambda s:s.__setitem__("source_parameter_id","x"*10000),
                       lambda s:s.__setitem__("phase_turn_rate","1/0")):
            changed=copy.deepcopy(spec);mutate(changed);cases.append((changed,p,p))
        cases.extend(((spec,p,["1","1e999999999"]),(spec,[True],p),(spec,["1"]*5,p)))
        with mock.patch.object(model,"Fraction",side_effect=AssertionError("unsafe raw input constructed")) as fraction, \
             mock.patch.object(model,"qualified_coprime_module",side_effect=AssertionError("unsafe raw input loaded proof")) as loader:
            for index,args in enumerate(cases):
                with self.subTest(index=index):self.nontruth(model.check_source(*args))
            fraction.assert_not_called();loader.assert_not_called()

    def test_canonical_rational_tokens_and_caller_limits_are_bounded(self):
        bad=(True,False,1,0.5,None,"","-0","+1","01","1/1","2/4","0/2","1/0","1/-2",
             " 1","1e999999999","0.25","\uff11","9"*129,str(1<<128),"1/"+str(1<<128))
        with mock.patch.object(model,"Fraction",side_effect=AssertionError("invalid rational constructed")) as fraction:
            for value in bad:
                with self.subTest(value_type=type(value).__name__),self.assertRaises(model.Refusal):model.rational(value)
            for value in (True,False,0,-1,4097,10**100,1.5,"128",None):
                with self.assertRaises(model.Refusal):model.rational("1",max_bits=value)
            for value in (True,False,0,-1,2501,10**100,1.5,"128",None):
                with self.assertRaises(model.Refusal):model.rational("1",max_chars=value)
            fraction.assert_not_called()
        self.assertEqual(model.rational(str(Q(1,1<<200)),max_bits=256,max_chars=128),Q(1,1<<200))

    def test_certificate_and_report_resources_precede_fresh_proof(self):
        p=["-1/3","1"];spec=supplied_source(p,p)
        cycle=[];cycle.append(cycle);shared={"x":1};deep=0
        for _ in range(model.MAX_DEPTH+1):deep=[deep]
        class Alias(dict):pass
        invalid=(cycle,[shared,shared],deep,{"x":0.5},{"x":float("nan")},{"x":b"bytes"},{"x":(1,2)},
                 Alias(x=1),{"x":"x"*(model.MAX_STRING+1)},{"x":1<<20000},list(range(1025)),
                 [[0]*900 for _ in range(200)])
        with mock.patch.object(model,"certify_source",side_effect=AssertionError("invalid certificate reached proof")) as proof:
            for index,candidate in enumerate(invalid):
                with self.subTest(index=index),self.assertRaises(model.Refusal):model.validate_certificate(spec,p,p,candidate)
            proof.assert_not_called()
        with mock.patch.object(model,"expected_report",side_effect=AssertionError("invalid report reached proof")) as replay:
            for candidate in invalid:
                with self.assertRaises(model.Refusal):model.validate_report(candidate)
            replay.assert_not_called()
        self.assertNotEqual(model.bounded_bytes({"count":True}),model.bounded_bytes({"count":1}))

    def test_report_reader_handles_duplicate_keys_nonexact_values_and_resource_limits(self):
        with tempfile.TemporaryDirectory(prefix="shared-square-json-") as directory:
            path=Path(directory)/"candidate.json"
            for raw in (b'{"x":1,"x":2}',b'{"x":NaN}',b'{"x":Infinity}',b'{"x":0.5}',
                        b'{"x":1e999999999}',b'{"x":'+b'9'*81+b'}',b'\xff',b'not-json',
                        b'['*(model.MAX_DEPTH+1)+b'0'+b']'*(model.MAX_DEPTH+1)):
                path.write_bytes(raw)
                with self.assertRaises(model.Refusal):model.read_report(path)
            with path.open("wb") as stream:stream.truncate(model.MAX_BYTES+1)
            with self.assertRaises(model.Refusal):model.read_report(path)
            path.write_bytes(b'{"status":"bounded candidate"}')
            self.assertEqual(model.read_report(path),{"status":"bounded candidate"})

    def test_report_path_bounds_precede_any_read(self):
        with mock.patch.object(model,"_read_bounded",side_effect=AssertionError("invalid report path read")) as reader:
            for path in ("x"*10000,Path("x"*10000),"","a\0b",True,1,None,[]):
                with self.assertRaises(model.Refusal):model.read_report(path)
            reader.assert_not_called()
        with tempfile.TemporaryDirectory(prefix="shared-square-missing-") as directory:
            with self.assertRaises(model.Refusal):model.read_report(Path(directory)/"missing.json")

    def test_all_default_original_proofs_and_complete_physical_sets(self):
        counts=Counter();orders=Counter()
        self.assertEqual(len(self.replay["cases"]),8)
        self.assertEqual(len({row["case_id"] for row in self.replay["cases"]}),8)
        for row in self.replay["cases"]:
            with self.subTest(case=row["case_id"]):
                certificate=row["certificate"]
                audit_shared_certificate(self,row["spec"],trim(row["P"]),trim(row["Q"]),certificate)
                counts["original_research_sources"]+=1
                zero=certificate["source_zero_set"]
                if zero["kind"]=="CLOSED_CONTINUUM_ORIGINAL_SOURCE_ZERO_SET":
                    counts["closed_continuum_sources"]+=1;continue
                counts["finite_sources"]+=1
                counts["per_source_closed_physical_roots"]+=len(zero["events"])
                counts["strict_source_interior_roots"]+=sum(e["location"]=="SPAN_INTERIOR" for e in zero["events"])
                counts["original_exterior_roots"]+=sum(e["location"]!="SPAN_INTERIOR" for e in zero["events"])
                counts["maximal_positive_nonzero_cells"]+=len(zero["maximal_nonzero_cells"])
                counts["root_free_finite_sources"]+=int(not zero["events"])
                counts["common_polynomial_roots"]+=len(certificate["polynomial_root_proof"]["roots"])
                counts["actual_residual_proofs"]+=1
                h=certificate["residual"]["certificate"]
                counts["residual_physical_roots"]+=len(h["source_zero_set"]["events"])
                counts["residual_half_integer_phase_candidates"]+=len(h["phase_candidates"]["candidates"])
                counts["actual_midpoint_operations"]+=sum(r["action"]=="EXACT_MIDPOINT_SPLIT"
                    for r in certificate["polynomial_root_proof"]["isolation_trace"])
                for event in zero["events"]:
                    counts["G_H_coincident_physical_roots"]+=int(event["polynomial_root_id"] is not None and event["residual_event_id"] is not None)
                    counts["rational_coordinate_events" if event["coordinate"]["kind"]=="RATIONAL" else "algebraic_isolator_coordinate_events"]+=1
                    orders[str(event["physical_order"])]+=1
        self.same(self.report["summary"],dict(counts))
        self.same(self.report["finite_physical_order_distribution"],dict(orders))
        self.same(dict(counts),{"original_research_sources":8,"closed_continuum_sources":1,"finite_sources":7,
            "per_source_closed_physical_roots":12,"strict_source_interior_roots":11,"original_exterior_roots":1,
            "maximal_positive_nonzero_cells":18,"root_free_finite_sources":0,"common_polynomial_roots":11,
            "actual_residual_proofs":7,"residual_physical_roots":3,"residual_half_integer_phase_candidates":27,
            "actual_midpoint_operations":3,"G_H_coincident_physical_roots":2,"rational_coordinate_events":8,
            "algebraic_isolator_coordinate_events":4})
        self.same(dict(orders),{"2":9,"4":2,"6":1})
        self.same(self.report["cases"],self.replay["cases"])

    def test_actual_hook_outputs_are_rechecked_before_source_truth(self):
        p=["1","-2","1"];q=["-1","1"]
        spec=supplied_source(p,q,lo=Q(1,2),hi=Q(3,2))
        mutations={
            "checked_gcd":lambda r:r.__setitem__("monic_gcd",["1"]),
            "decompose_amplitudes":lambda r:r.__setitem__("G_squared",["1"]),
            "prove_residual_source":lambda r:r["certificate"]["source_zero_set"]["events"].clear(),
            "sturm_sequence":lambda r:r["sequence"].pop(),
            "one_sided_sign":lambda r:r.__setitem__("sign",-r["sign"]),
            "count_roots_open":lambda r:r.__setitem__("open_root_count",True),
            "build_multiplicity_chain":lambda r:r.clear(),
            "prove_polynomial_multiplicity":lambda r:r.__setitem__("multiplicity",3),
            "isolate_polynomial_roots":lambda r:r["roots"].clear(),
            "assemble_physical_union":lambda r:r["events"][0].__setitem__("physical_order",2)}
        for name,mutate in mutations.items():
            actual=getattr(model,name)
            changes=[]
            def changed(*args,**kwargs):
                result=copy.deepcopy(actual(*args,**kwargs));before=canonical(result)
                mutate(result);changes.append(canonical(result)!=before);return result
            with self.subTest(hook=name),mock.patch.object(model,name,side_effect=changed) as hook:
                self.nontruth(model.check_source(spec,p,q));self.assertGreater(hook.call_count,0)
                self.assertTrue(changes);self.assertTrue(all(changes))

    def test_actual_qualified_residual_certificate_cannot_omit_or_invent_roots(self):
        p=["1","-2","1"];q=["-1","1"]
        spec=supplied_source(p,q,lo=Q(1,2),hi=Q(3,2));actual=self.c.certify_source
        for mutate in (lambda r:r["source_zero_set"]["events"].clear(),
                       lambda r:r["bezout_identity"].__setitem__("B",["0"]),
                       lambda r:r["root_jets"][0]["quadratic_taylor_coefficient"].__setitem__("pi_squared","0"),
                       lambda r:r["phase_candidates"]["candidates"].pop()):
            changes=[]
            def changed(*args,**kwargs):
                result=copy.deepcopy(actual(*args,**kwargs));before=canonical(result)
                mutate(result);changes.append(canonical(result)!=before);return result
            with mock.patch.object(model,"qualified_coprime_module",return_value=self.c), \
                 mock.patch.object(self.c,"certify_source",side_effect=changed) as producer:
                self.nontruth(model.check_source(spec,p,q));self.assertEqual(producer.call_count,1)
                self.assertEqual(changes,[True])

    def test_isolation_receipt_coverage_and_multiplicity_falsifiers(self):
        def reject(index,mutate):
            replay=copy.deepcopy(self.replay);mutate(replay["cases"][index]["certificate"]["polynomial_root_proof"])
            with self.assertRaises(model.Refusal):model.report_from_replay(replay)
        controls=[
            (2,lambda p:p["initial_gap_searches"].clear()),
            (2,lambda p:p["isolation_trace"].pop()),
            (2,lambda p:p["roots"].__setitem__(1,copy.deepcopy(p["roots"][0]))),
            (2,lambda p:p["roots"][0]["coordinate"].__setitem__("isolating_interval",["-1","1"])),
            (2,lambda p:p["roots"][0]["coordinate"].__setitem__("coordinate_irrationality_claimed",True)),
            (2,lambda p:p["roots"][0]["coordinate"].__setitem__("defining_polynomial",["-1/3","1"])),
            (2,lambda p:p["roots"][0]["discovery"].__setitem__("node_id","UNSEARCHED_GAP")),
            (2,lambda p:p["closed_interval_open_count_receipt"].__setitem__("open_root_count",1)),
            (2,lambda p:p.__setitem__("global_midpoint_budget",True)),
            (4,lambda p:p["multiplicity_chain"].pop()),
            (4,lambda p:p["roots"][0].__setitem__("multiplicity",1)),
            (4,lambda p:p["roots"][0]["multiplicity_evidence"]["chain_membership"][1].__setitem__("root_count",0)),
            (7,lambda p:p["partition_boundaries"][-1].__setitem__("is_G_root",False))]
        for index,(case,mutate) in enumerate(controls):
            with self.subTest(control=index):reject(case,mutate)
        # The cubic default discovers0 at an exact midpoint; a false nonroot
        # cannot be used to silently drop that root from child conservation.
        cubic=copy.deepcopy(self.replay)
        proof=cubic["cases"][7]["certificate"]["polynomial_root_proof"]
        split=next(row for row in proof["isolation_trace"] if row["action"]=="EXACT_MIDPOINT_SPLIT")
        split["midpoint_is_G_root"]=not split["midpoint_is_G_root"]
        with self.assertRaises(model.Refusal):model.report_from_replay(cubic)

    def test_union_coincidence_order_and_cell_boundaries_cannot_be_forged(self):
        def reject(index,mutate):
            replay=copy.deepcopy(self.replay);mutate(replay["cases"][index]["certificate"]["source_zero_set"])
            with self.assertRaises(model.Refusal):model.report_from_replay(replay)
        controls=[
            (1,lambda z:z["events"][0].__setitem__("residual_event_id",None)),
            (1,lambda z:z["events"][0].__setitem__("physical_order",2)),
            (1,lambda z:z["events"].append(copy.deepcopy(z["events"][0]))),
            (2,lambda z:z["maximal_nonzero_cells"][0]["right_boundary"].__setitem__("coordinate",{"kind":"RATIONAL","value":"0"})),
            (2,lambda z:z["maximal_nonzero_cells"][0].__setitem__("right_included",True)),
            (2,lambda z:z["maximal_nonzero_cells"].pop()),
            (2,lambda z:z["events"].reverse()),
            (7,lambda z:z["events"][-1].__setitem__("order",{"kind":"SMOOTH","multiplicity":2})),
            (7,lambda z:z["exterior_points"][-1].__setitem__("outside_order",2)),
            (0,lambda z:z["exterior_points"][0].__setitem__("exact_value","1")),
            (6,lambda z:z.__setitem__("events",[])),
            (6,lambda z:z.__setitem__("closed_root_count",0)),
            (6,lambda z:z.__setitem__("maximal_nonzero_cells",[]))]
        for index,(case,mutate) in enumerate(controls):
            with self.subTest(control=index):reject(case,mutate)

    def test_zero_midpoint_and_one_sided_endpoint_counts_are_actual_premises(self):
        p=(Q(0),Q(-1),Q(0),Q(1))
        for a,b,expected in ((Q(-1),Q(1),1),(Q(-1),Q(0),0),(Q(0),Q(1),0)):
            receipt=model.count_roots_open(self.c,p,a,b)
            self.assertEqual(audit_open_count(self,p,a,b,receipt),expected)
        left=model.one_sided_sign(self.c,(Q(0),Q(1)),Q(0),"LEFT")
        right=model.one_sided_sign(self.c,(Q(0),Q(1)),Q(0),"RIGHT")
        self.assertEqual((left["sign"],right["sign"]),(-1,1))
        double=model.one_sided_sign(self.c,(Q(0),Q(0),Q(1)),Q(0),"LEFT")
        self.assertEqual((double["first_nonzero_derivative_order"],double["sign"]),(2,1))

    def test_report_formatter_checks_actual_context_without_reproving_residuals(self):
        with mock.patch.object(model,"prove_residual_source",side_effect=AssertionError("formatter re-proved residual")) as hook:
            self.same(model.report_from_replay(self.replay),self.report)
            hook.assert_not_called()
        controls=(lambda r:r["cases"].pop(),lambda r:r["cases"].reverse(),
                  lambda r:r["cases"].__setitem__(1,copy.deepcopy(r["cases"][0])),
                  lambda r:r["cases"][0]["spec"].__setitem__("source_parameter_id","changed-original"),
                  lambda r:r["input_custody"][0].__setitem__("bytes",True),
                  lambda r:r["cases"][0]["certificate"]["input_custody"][0].__setitem__("sha256","0"*64))
        for index,mutate in enumerate(controls):
            replay=copy.deepcopy(self.replay);mutate(replay)
            with self.subTest(index=index),self.assertRaises(model.Refusal):model.report_from_replay(replay)
        with mock.patch.object(model,"replay_sources",side_effect=RuntimeError("ACTUAL_DEFAULT_REPLAY_FAILURE")) as replay:
            with self.assertRaises(model.Refusal):model.validate_report(self.report)
            replay.assert_called_once()

    def test_canonical_report_rejects_scope_budget_count_and_truth_changes(self):
        self.assertTrue(model._compare_with_replayed_bytes(self.report,self.expected_bytes))
        controls=(lambda r:r["summary"].__setitem__("closed_continuum_sources",True),
                  lambda r:r["summary"].__setitem__("per_source_closed_physical_roots",11),
                  lambda r:r["scope"].__setitem__("MC032_is_nonexecuted_algorithm_reference",False),
                  lambda r:r["gates"].__setitem__("MC-1","ESTABLISHED"),
                  lambda r:r["gates"].__setitem__("production_authorized",True),
                  lambda r:r["budgets"].__setitem__("structural_physical_event_budget",36),
                  lambda r:r["cases"][0]["certificate"]["scope"].__setitem__("residual_raw_input_envelope_unchanged",False))
        for index,mutate in enumerate(controls):
            changed=copy.deepcopy(self.report);mutate(changed)
            with self.subTest(index=index),self.assertRaises(model.Refusal):model._compare_with_replayed_bytes(changed,self.expected_bytes)
        self.assertEqual({self.report["gates"][key] for key in ("PB-007-01","PB-007-02","PB-007-03","PB-007-04")},{"OPEN"})
        for key in ("frozen_fifty_source_cohort_unchanged","frozen_121_source_corpus_unchanged",
                    "historical_20_blocked_and_30_order_gap_dispositions_unchanged","all_26_operations_unchanged"):
            self.assertIs(self.report["gates"][key],True)

    def test_all_six_inputs_have_exact_bytes_and_only_coprime_code_is_executed(self):
        records=[]
        for relative,pin in sorted(model.DEPENDENCY_PINS.items()):
            raw=(ROOT/relative).read_bytes();self.assertEqual(git_blob(raw),pin)
            use=("EXECUTED_QUALIFIED_COPRIME_PRODUCER" if relative==model.COPRIME_MODEL else
                 "PINNED_NONEXECUTED_ALGORITHM_REFERENCE" if relative==model.MC032_REFERENCE else
                 "PINNED_NONEXECUTED_GRAMMAR_AND_PRIOR_RESEARCH_CONTEXT")
            records.append({"path":relative,"git_blob":pin,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),"use":use})
        self.assertEqual(len(records),6)
        self.same(model.INPUT_RECORDS,records);self.same(self.replay["input_custody"],records)
        compiled=[]
        def compiler(raw,path,mode,**options):
            compiled.append((git_blob(raw),path,options));return builtins.compile(raw,path,mode,**options)
        with mock.patch.dict(model.__dict__,{"compile":mock.Mock(side_effect=compiler)}):
            producer=model.qualified_coprime_module()
            self.same(producer.capture_references(),producer.REFERENCE_RECORDS)
        self.assertEqual(compiled,[(model.COPRIME_BLOB,str(ROOT/model.COPRIME_MODEL),{"dont_inherit":True,"optimize":0})])

    def test_actual_accepted_coprime_cache_and_preloads_are_ignored(self):
        with tempfile.TemporaryDirectory(prefix="shared-square-producer-cache-") as directory:
            root=Path(directory)
            for relative in model.DEPENDENCY_PINS:
                path=root/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((ROOT/relative).read_bytes())
            path=root/model.COPRIME_MODEL;trusted=path.read_bytes();payload=b"PRODUCER_CACHE_SUBSTITUTION = True\n#"
            ordinary=install_accepted_stale_cache(path,trusted,payload+b" "*(len(trusted)-len(payload)))
            self.assertTrue(ordinary.PRODUCER_CACHE_SUBSTITUTION)
            name="_radicadsac_shared_square_coprime_"+model.COPRIME_BLOB
            fake=types.ModuleType(name);fake.PRODUCER_CACHE_SUBSTITUTION=True
            with mock.patch.object(model,"ROOT",root),mock.patch.dict(sys.modules,{name:fake,path.stem:fake}):
                checked=model.qualified_coprime_module()
                self.assertFalse(hasattr(checked,"PRODUCER_CACHE_SUBSTITUTION"))
                self.assertIs(sys.modules[name],fake)
                spec=supplied_source([1],[1]);certificate=checked.certify_source(spec,["1"],["1"])
                audit_residual_certificate(self,spec,[Q(1)],[Q(1)],certificate)

    def test_captured_code_and_all_context_bytes_survive_path_replacement(self):
        with tempfile.TemporaryDirectory(prefix="shared-square-retained-buffers-") as directory:
            root=Path(directory)
            for relative in model.DEPENDENCY_PINS:
                path=root/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((ROOT/relative).read_bytes())
            seen=[];read=model._read_bounded
            def replace(path,limit):
                raw=read(path,limit);seen.append(str(path.relative_to(root)))
                path.write_bytes(b"DEPENDENCY_PATH_REPLACED = True\n");return raw
            with mock.patch.object(model,"ROOT",root),mock.patch.object(model,"_read_bounded",side_effect=replace):
                producer=model.qualified_coprime_module()
                self.assertEqual(seen,sorted(model.DEPENDENCY_PINS))
                self.assertFalse(hasattr(producer,"DEPENDENCY_PATH_REPLACED"))
                self.same(producer.capture_references(),producer.REFERENCE_RECORDS)
                spec=supplied_source([1],[1]);certificate=producer.certify_source(spec,["1"],["1"])
                audit_residual_certificate(self,spec,[Q(1)],[Q(1)],certificate)
                with self.assertRaises(model.Refusal):model.qualified_coprime_module()
                declared=next(iter(producer.REFERENCE_PINS))
                for path,limit in ((root/"undeclared.json",256),(root/declared,0),(root/declared,True),
                                   (root/declared,-1),(root/declared,model.MAX_REFERENCE_BYTES+1)):
                    with self.assertRaises(model.Refusal):producer._read_bounded(path,limit)

    def test_dependency_drift_alias_and_size_fail_before_any_code_execution(self):
        reader=model._read_bounded
        for relative in model.DEPENDENCY_PINS:
            def drift(path,limit):return b"changed dependency" if path==ROOT/relative else reader(path,limit)
            compiler=mock.Mock(side_effect=AssertionError("unverified dependency compiled"))
            with self.subTest(path=relative),mock.patch.object(model,"_read_bounded",side_effect=drift), \
                 mock.patch.dict(model.__dict__,{"compile":compiler}):
                with self.assertRaises(model.Refusal):model.qualified_coprime_module()
                compiler.assert_not_called()
        with tempfile.TemporaryDirectory(prefix="shared-square-dependency-alias-") as directory:
            root=Path(directory)
            for relative in model.DEPENDENCY_PINS:
                path=root/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((ROOT/relative).read_bytes())
            path=root/model.COPRIME_MODEL;raw=path.read_bytes();path.unlink()
            target=path.with_name("undeclared.py");target.write_bytes(raw);path.symlink_to(target)
            with mock.patch.object(model,"ROOT",root):
                with self.assertRaises(model.Refusal):model.qualified_coprime_module()
                path.unlink()
                with path.open("wb") as stream:stream.truncate(model.MAX_CODE_BYTES+1)
                with self.assertRaises(model.Refusal):model.qualified_coprime_module()

    def test_workflow_has_exact_six_input_and_five_owned_path_closure(self):
        own={TASK+name for name in ("pb00701_shared_square_source.py","verify_pb00701_shared_square_source.py",
                                  "pb00701-shared-square-source.json","pb00701-shared-square-source-research.md")}
        workflow=".github/workflows/mc1-pb00701-shared-square-source.yml";own.add(workflow)
        text=(ROOT/workflow).read_text()
        before,after=text.split("  push:",1)
        for section in (before,after):
            paths=re.findall(r"^      - ['\"]([^'\"]+)['\"]$",section,re.M)
            self.assertEqual(set(paths),set(model.DEPENDENCY_PINS)|own);self.assertEqual(len(paths),11)
        self.assertNotIn("strategy:",text)
        self.assertIn("github.event.pull_request.head.sha || github.sha",text)
        self.assertIn("verify_pb00701_shared_square_source.py --contract --self-test",text)
        self.assertIn("python-version: '3.12'",text)


def test_suite(replay=None,report=None):
    SharedSquareTests.replay=replay
    SharedSquareTests.report=report
    classes=(SharedSquareTests,build_bootstrap_tests(MODEL_PATH,MODEL_BLOB))
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
    print("PASS: original square identity and exact shared-factor scale are reconstructed")
    print("PASS: independent Sturm, multiplicity and physical-union projections check every default event and cell")
    print("PASS: seven finite sources yield twelve roots and eighteen positive cells; one source is a typed continuum")
    print("PASS: dynamic order-eight and thirty-six-root sources are admitted; bounded failure remains atomic nontruth")
    print("PASS: verified same-buffer residual code/context and exact eleven-path CI closure are preserved")


if __name__=="__main__":main()


