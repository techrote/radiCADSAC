#!/usr/bin/env python3
"""Independent exact original-source and stationary-weight proof verification.

Independent original Bernstein identities, exact phase branches, polynomial
root counts and product orders precede all demonstration summaries.
"""
from __future__ import annotations

import argparse
import builtins
from collections import Counter
from contextlib import ExitStack
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

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
TASK="research/machining-completeness/tasks/MC-038/"
MODEL_PATH=HERE/"pb00701_stationary_square_source.py"
MODEL_BLOB="245ff3da07ce6c8b23e8fa544333b86afc809c48"


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
    module = types.ModuleType("stationary_square_reviewed_model")
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
    spec = importlib.util.spec_from_file_location("ordinary_stationary_square_cache_control", path)
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
            with tempfile.TemporaryDirectory(prefix="stationary-square-cache-") as directory:
                here = Path(directory) / TASK
                here.mkdir(parents=True)
                path = here / Path(model_path).name
                ordinary = install_accepted_stale_cache(path, trusted, altered)
                self.assertTrue(ordinary.CACHE_SUBSTITUTION)
                fake = types.ModuleType("stationary_square_reviewed_model")
                fake.CACHE_SUBSTITUTION = True
                with mock.patch.dict(sys.modules, {fake.__name__: fake, Path(model_path).stem: fake}):
                    checked = load_reviewed_model(path, model_blob)
                    self.assertFalse(hasattr(checked, "CACHE_SUBSTITUTION"))
                    self.assertTrue(callable(checked.expected_report))
                    self.assertIs(sys.modules[fake.__name__], fake)

        def test_checked_buffer_survives_posthash_path_replacement(self):
            with tempfile.TemporaryDirectory(prefix="stationary-square-replace-") as directory:
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
            with tempfile.TemporaryDirectory(prefix="stationary-square-bounds-") as directory:
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
            with tempfile.TemporaryDirectory(prefix="stationary-square-flags-") as directory:
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


def supplied_source(p,q,*,lo=Q(0),hi=Q(1),offset=Q(0),rate=Q(0),
                    degree0=None,degree1=None,parameter="independent-stationary-square-original-t"):
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


def independent_phase(offset):
    b=Q(offset);integer=b.denominator==1;half=b.denominator==2
    return {"phase_turn_offset":str(b),"phase_turn_rate":"0",
            "branch":"INTEGER_COSINE_WEIGHT_ONE" if integer else "ODD_HALF_SINE_WEIGHT_ONE" if half else "BOTH_WEIGHTS_STRICTLY_POSITIVE",
            "reduced_offset_numerator":str(b.numerator),"reduced_offset_denominator":str(b.denominator),
            "cos_squared_exact_value":"1" if integer else "0" if half else None,
            "sin_squared_exact_value":"0" if integer else "1" if half else None,
            "cos_squared_strictly_positive":not half,"sin_squared_strictly_positive":not integer,
            "both_weights_sum_to_one":True,"floating_angle_tolerance_used":False,
            "noncardinal_weight_field_or_exact_value_required":False}


def audit_selection(test,p,q,c0,c1,phase,selection):
    branch=phase["branch"]
    test.assertEqual(selection["branch"],branch)
    if branch in ("INTEGER_COSINE_WEIGHT_ONE","ODD_HALF_SINE_WEIGHT_ONE"):
        active="P" if branch=="INTEGER_COSINE_WEIGHT_ONE" else "Q"
        selected=p if active=="P" else q
        kind="ACTIVE_AMPLITUDE";square=True;positive=selected!=[Q(0)]
        test.assertIsNone(selection["decomposition"]);test.assertIsNone(selection["residual_bezout"])
        direct=plus(c0,c1 if active=="P" else [-v for v in c1])
        test.assertEqual(direct,times(selected,selected))
    elif p==q==[Q(0)]:
        selected=[Q(0)];active=None;kind="BOTH_AMPLITUDES_ZERO";square=True;positive=False
        test.assertIsNone(selection["decomposition"]);test.assertIsNone(selection["residual_bezout"])
    else:
        active=None;kind="COMMON_FACTOR_WITH_POSITIVE_WEIGHTED_RESIDUAL";square=False;positive=True
        d=selection["decomposition"]
        selected=audit_gcd(test,p,q,d["gcd_proof"])
        test.assertEqual(trim(d["G"]),selected)
        quotients=[]
        for name,poly in (("P",p),("Q",q)):
            quotient,remainder=independent_division(poly,selected)
            test.assertEqual(remainder,[Q(0)]);quotients.append(quotient)
            test.same(d[name+"_division"],{"dividend":list(map(str,poly)),"divisor":list(map(str,selected)),
                "quotient":list(map(str,quotient)),"remainder":["0"]})
            test.assertEqual(trim(d[name+"0"]),quotient)
        p0,q0=quotients;g2=times(selected,selected)
        h0=[v/2 for v in plus(times(p0,p0),times(q0,q0))]
        h1=[v/2 for v in plus(times(p0,p0),[-v for v in times(q0,q0)])]
        for key,poly in (("G_squared",g2),("residual_C0",h0),("residual_C1",h1),
                         ("original_C0_product",c0),("original_C1_product",c1)):
            test.assertEqual(trim(d[key]),trim(poly))
        test.assertEqual(times(g2,h0),c0);test.assertEqual(times(g2,h1),c1)
        test.assertIs(d["original_parameter_and_scale_preserved"],True)
        test.assertIs(d["factor_square_not_discarded"],True)
        audit_bezout(test,p0,q0,selection["residual_bezout"])
    test.assertEqual(selection["selection_kind"],kind)
    test.assertEqual(selection["active_amplitude"],active)
    test.same(selection["selected_polynomial"],list(map(str,selected)))
    test.assertIs(selection["original_source_equals_selected_square"],square)
    test.assertIs(selection["remaining_factor_strictly_positive"],positive)
    test.assertIs(selection["selected_polynomial_identically_zero"],selected==[Q(0)])
    return selected


def independent_stationary_zero_set(test,spec,phase,selection,roots):
    left,right=Q(spec["parameter_lo"]),Q(spec["parameter_hi"])
    source_hash=digest(spec);parameter=spec["source_parameter_id"]
    if selection["selected_polynomial_identically_zero"]:
        return {"kind":"CLOSED_CONTINUUM_ORIGINAL_SOURCE_ZERO_SET","complete_for_original_closed_source":True,
            "source_interval":[str(left),str(right)],"zero_interval":{"interval":[str(left),str(right)],"left_included":True,"right_included":True},
            "original_source_identically_zero":True,"stationary_weight_branch":phase["branch"],
            "identity_selection_kind":selection["selection_kind"],"inactive_amplitude_may_be_nonzero":selection["selection_kind"]=="ACTIVE_AMPLITUDE",
            "closed_root_count":None,"events":None,"source_open_root_count":None,"exterior_root_count":None,"true_source_knots":[],
            "exterior_points":[{"side":side,"coordinate":str(t),"is_zero":True,"exact_value":"0",
                "isolated_root_order":None,"outside_sign":None,"outside_order":None} for side,t in (("LEFT",left),("RIGHT",right))],
            "maximal_nonzero_cells":None,"finite_event_list_applicable":False,"nonzero_sign_cells_applicable":False,
            "finite_root_cardinality_claimed":False,"polynomial_isolator_applicable":False,"moving_source_producer_called":False}
    events=[];previous=None
    for index,root in enumerate(roots):
        coordinate=root["coordinate"];a,b=coordinate_bounds(coordinate)
        test.assertTrue(left<=a<=b<=right)
        if previous is not None:test.assertLess(compare_coordinates(previous,coordinate),0)
        previous=coordinate
        at_left=a==b==left;at_right=a==b==right;m=root["multiplicity"];order=2*m
        test.assertIn(order,(2,4,6))
        order_record=({"kind":"ONE_SIDED","side":"RIGHT" if at_left else "LEFT","inward_order":order,
            "outside_order":None,"global_smooth_multiplicity_claimed":False} if at_left or at_right else
            {"kind":"SMOOTH","multiplicity":order})
        events.append({"event_id":"ZERO_"+str(index),"source_sha256":source_hash,"source_parameter_id":parameter,
            "coordinate":copy.deepcopy(coordinate),"location":"LEFT_EXTERIOR" if at_left else "RIGHT_EXTERIOR" if at_right else "SPAN_INTERIOR",
            "source_piece_indices":[0],"classification":"TOUCHING","order":order_record,"physical_order":order,
            "polynomial_root_id":root["polynomial_root_id"],"polynomial_multiplicity":m,"stationary_weight_branch":phase["branch"],
            "order_derivation":{"selected_polynomial_multiplicity":m,"squared_polynomial_order":order,"remaining_factor_order":0},
            "moving_carrier_root_order_added":False,"left_sign":None if at_left else 1,"right_sign":None if at_right else 1})
    by_exterior={Q(event["coordinate"]["value"]):event for event in events if event["location"]!="SPAN_INTERIOR"}
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
    for index,(a,b) in enumerate(zip(boundaries,boundaries[1:])):
        test.assertLess(compare_coordinates(a["coordinate"],b["coordinate"]),0)
        cells.append({"cell_id":"CELL_"+str(index),"left_boundary":a,"right_boundary":b,
            "left_included":a["kind"]=="SOURCE_EXTERIOR","right_included":b["kind"]=="SOURCE_EXTERIOR",
            "sign":1,"source_piece_indices":[0],"crossed_nonzero_source_knots":[],
            "positive_from_selected_square_and_stationary_weight_proof":True})
    exteriors=[]
    for side,t in (("LEFT",left),("RIGHT",right)):
        event=by_exterior.get(t)
        exteriors.append({"side":side,"coordinate":str(t),"phase_turn":spec["phase_turn_offset"],"is_zero":event is not None,
            "event_ref":event["event_id"] if event else None,"value_sign":0 if event else 1,"exact_value":"0" if event else None,
            "nonzero_exact_scalar_value_claimed":False,"positive_sign_from_stationary_weight_and_complete_polynomial_proof":event is None,
            "inward_sign":1,"inward_order":event["physical_order"] if event else 0,"outside_sign":None,"outside_order":None,
            "global_smooth_multiplicity_claimed":False})
    return {"kind":"FINITE_ORIGINAL_SOURCE_ZERO_SET","complete_for_original_closed_source":True,
        "source_interval":[str(left),str(right)],"closed_root_count":len(events),"events":events,
        "source_open_root_count":len(events)-len(by_exterior),"exterior_root_count":len(by_exterior),"true_source_knots":[],
        "exterior_points":exteriors,"maximal_nonzero_cells":cells,"finite_event_list_applicable":True,"nonzero_sign_cells_applicable":True,
        "all_physical_roots_have_even_order":True,"nonzero_source_points_strictly_positive":True,
        "continuum_excluded_by_nonzero_selected_polynomial":True,"global_cross_source_zero_deduplication_performed":False,
        "isolator_endpoints_substituted_for_physical_root_boundaries":False}


def audit_stationary_certificate(test,spec,p,q,certificate):
    p,q=trim(p),trim(q)
    test.assertEqual(certificate["status"],"ESTABLISHED_STATIONARY_SQUARE_ORIGINAL_SOURCE")
    test.assertIs(certificate["proof_established"],True);test.assertIs(certificate["source_zero_set_established"],True)
    test.assertIs(certificate["production_authorized"],False)
    test.same(certificate["original_source"],spec)
    test.assertEqual(certificate["source_sha256"],digest(spec))
    test.assertEqual(certificate["source_parameter_id"],spec["source_parameter_id"])
    test.same(certificate["source_interval"],[spec["parameter_lo"],spec["parameter_hi"]])
    test.assertEqual(spec["phase_turn_rate"],"0")
    test.same(certificate["phase_turn_law"],{"offset":spec["phase_turn_offset"],"rate":"0"})
    witness={"P":list(map(str,p)),"Q":list(map(str,q))}
    test.same(certificate["supplied_witness"],witness);test.same(certificate["normalized_witness"],witness)
    test.assertEqual(certificate["witness_sha256"],digest(witness))
    c0,c1=audit_lowering(test,spec,p,q,certificate["whole_source_lowering"])
    test.same(certificate["source_identity"],{"P_squared":list(map(str,times(p,p))),"Q_squared":list(map(str,times(q,q))),
        "C0_equals_half_sum_of_squares":list(map(str,c0)),"C1_equals_half_difference_of_squares":list(map(str,c1)),
        "identities_verified_coefficientwise":True,"original_source_equals_nonnegative_square_sum":True,
        "all_original_channels_reconstructed":True,"phase_used_in_original_parameter":True})
    phase=independent_phase(spec["phase_turn_offset"])
    test.same(certificate["stationary_phase_proof"],phase)
    selection=certificate["stationary_polynomial_selection"]
    selected=audit_selection(test,p,q,c0,c1,phase,selection)
    continuum=selected==[Q(0)]
    if continuum:
        test.assertIsNone(certificate["polynomial_root_proof"]);roots=[]
    else:
        roots=audit_isolation(test,selected,Q(spec["parameter_lo"]),Q(spec["parameter_hi"]),[],certificate["polynomial_root_proof"])
    test.same(certificate["source_zero_set"],independent_stationary_zero_set(test,spec,phase,selection,roots))
    test.same(certificate["input_custody"],model.INPUT_RECORDS)
    test.same(certificate["theorem_premises"],{"complete_original_coefficients_equal_supplied_square_sum":True,
        "actual_original_rate_is_zero":True,"stationary_weights_classified_exactly":True,
        "finite_roots_equal_selected_polynomial_roots":not continuum,"physical_order_is_twice_polynomial_multiplicity":not continuum,
        "zero_active_polynomial_gives_closed_continuum":continuum,"inactive_amplitude_remains_bound_by_full_source_identity":True,
        "moving_carrier_order_added":False,"moving_source_certifier_used":False,
        "numerical_samples_or_saved_reports_used_as_completeness_authority":False,"exact_noncardinal_trig_weight_field_required":False,
        "pi_irrationality_or_transcendence_used":False})
    for key in ("generic_supplied_source_and_witness_checked","one_original_clamped_span","valid_degree_elevation_admitted",
                "original_parameter_and_zero_rate_preserved","legacy_quarter_turn_stationary_overlap_acknowledged",
                "algebraic_descriptors_do_not_claim_minimality_or_irrationality","only_conditional_polynomial_stages_reused"):
        test.assertIs(certificate["scope"][key],True)
    for key in ("fixture_allowlist_used_for_admission","derived_residual_source_or_raw_control_conversion_required",
                "frozen_corpus_addition","historical_source_completion_claimed","generic_owner_route_repaired","native_geometry_evidence"):
        test.assertIs(certificate["scope"][key],False)


class StationarySquareTests(unittest.TestCase):
    replay=None
    report=None

    @classmethod
    def setUpClass(cls):
        if cls.replay is None:cls.replay=model.replay_sources()
        if cls.report is None:cls.report=model.report_from_replay(cls.replay)
        cls.expected_bytes=canonical(cls.report)
        cls.s,cls.c=model.qualified_modules()

    def same(self,a,b,message=None):self.assertEqual(canonical(a),canonical(b),message)

    def nontruth(self,result):
        self.assertEqual(result["status"],"REFUSED")
        for key in ("proof_established","source_zero_set_established","production_authorized"):
            self.assertIs(result[key],False)
        self.assertIsNone(result["source_zero_set"])
        for key in ("certificate","partial_roots","successful_partial_roots"):self.assertNotIn(key,result)

    def prove(self,p,q,**options):
        p,q=trim(p),trim(q);spec=supplied_source(p,q,**options);hints=list(map(str,p)),list(map(str,q))
        certificate=model.certify_source(spec,*hints)
        audit_stationary_certificate(self,spec,p,q,certificate)
        return spec,hints,certificate

    def test_all_eight_complete_original_proofs_and_physical_projections(self):
        counts=Counter();branches=Counter();orders=Counter()
        self.assertEqual(len(self.replay["cases"]),8)
        self.assertEqual(len({r["case_id"] for r in self.replay["cases"]}),8)
        for row in self.replay["cases"]:
            with self.subTest(case=row["case_id"]):
                certificate=row["certificate"]
                audit_stationary_certificate(self,row["spec"],trim(row["P"]),trim(row["Q"]),certificate)
                counts["original_research_sources"]+=1
                branches[certificate["stationary_phase_proof"]["branch"]]+=1
                zero=certificate["source_zero_set"]
                if zero["kind"]=="CLOSED_CONTINUUM_ORIGINAL_SOURCE_ZERO_SET":
                    counts["closed_continuum_sources"]+=1;continue
                counts["finite_sources"]+=1
                counts["per_source_closed_physical_roots"]+=len(zero["events"])
                counts["original_exterior_roots"]+=sum(e["location"]!="SPAN_INTERIOR" for e in zero["events"])
                counts["strict_source_interior_roots"]+=sum(e["location"]=="SPAN_INTERIOR" for e in zero["events"])
                counts["root_free_finite_sources"]+=int(not zero["events"])
                counts["maximal_positive_nonzero_cells"]+=len(zero["maximal_nonzero_cells"])
                for event in zero["events"]:
                    counts["rational_root_coordinates" if event["coordinate"]["kind"]=="RATIONAL" else "algebraic_format_root_coordinates"]+=1
                    orders[str(event["physical_order"])]+=1
        expected=dict(counts);expected["physical_order_histogram"]=dict(orders);expected["stationary_weight_branches"]=dict(branches)
        self.same(self.report["summary"],expected)
        self.same(dict(counts),{"original_research_sources":8,"finite_sources":5,"closed_continuum_sources":3,
            "per_source_closed_physical_roots":5,"original_exterior_roots":0,"strict_source_interior_roots":5,
            "root_free_finite_sources":1,"maximal_positive_nonzero_cells":10,"rational_root_coordinates":3,
            "algebraic_format_root_coordinates":2})
        self.same(dict(orders),{"2":4,"4":1})
        self.same(dict(branches),{"INTEGER_COSINE_WEIGHT_ONE":2,"ODD_HALF_SINE_WEIGHT_ONE":2,"BOTH_WEIGHTS_STRICTLY_POSITIVE":4})
        self.same(self.report["cases"],self.replay["cases"])

    def test_same_two_amplitudes_select_three_distinct_exact_zero_sets(self):
        p=[-Q(1,3),1];q=[-Q(2,3),1]
        for offset,expected in ((Q(0),[Q(1,3)]),(-Q(1,2),[Q(2,3)]),(Q(1,5),[])):
            spec,hints,certificate=self.prove(p,q,offset=offset,parameter="independent-three-branches")
            zero=certificate["source_zero_set"]
            self.assertEqual([Q(e["coordinate"]["value"]) for e in zero["events"]],expected)
            self.assertEqual(len(zero["maximal_nonzero_cells"]),len(expected)+1)
            self.assertEqual(certificate["phase_turn_law"],{"offset":str(offset),"rate":"0"})

    def test_near_cardinal_rationals_are_not_rounded_to_continua(self):
        epsilon=Q(1,1<<120)
        for p,q,offset in (([0],[1],Q(1)),([1],[0],Q(1,2)),([1],[0],-Q(1,2))):
            self.assertEqual(float(offset),float(offset+epsilon))
            for actual,continuum in ((offset,True),(offset+epsilon,False)):
                spec,hints,certificate=self.prove(p,q,offset=actual,parameter="exact-near-cardinal-source")
                zero=certificate["source_zero_set"]
                self.assertEqual(zero["kind"]=="CLOSED_CONTINUUM_ORIGINAL_SOURCE_ZERO_SET",continuum)
                if not continuum:
                    self.assertEqual(zero["closed_root_count"],0)
                    self.assertEqual(len(zero["maximal_nonzero_cells"]),1)
                    self.assertEqual(certificate["stationary_phase_proof"]["branch"],"BOTH_WEIGHTS_STRICTLY_POSITIVE")
                    self.assertTrue(all(e["value_sign"]==1 and e["exact_value"] is None for e in zero["exterior_points"]))

    def test_exact_negative_offsets_and_legacy_quarter_turn_overlap(self):
        for offset in (Q(-8),-Q(7,2),-Q(2,3),-Q(1,2),Q(0),Q(1,4),Q(1,3),Q(5,2),Q(8)):
            phase=model.classify_stationary_phase(self.c,str(offset))
            self.same(phase,independent_phase(offset))
        for offset in (Q(1,4),-Q(1,5)):
            _,_,certificate=self.prove([0],[-Q(1,3),1],offset=offset)
            self.assertEqual(certificate["source_zero_set"]["closed_root_count"],1)
            self.assertIs(certificate["scope"]["legacy_quarter_turn_stationary_overlap_acknowledged"],True)

    def test_inactive_nonzero_amplitudes_can_cancel_complete_nonzero_channels(self):
        for p,q,offset in (([0],[1],Q(2)),([1],[0],-Q(1,2))):
            spec,hints,certificate=self.prove(p,q,offset=offset,degree0=6,degree1=6)
            self.assertNotEqual(certificate["whole_source_lowering"]["C0"],["0"])
            self.assertNotEqual(certificate["whole_source_lowering"]["C1"],["0"])
            self.assertEqual(certificate["source_zero_set"]["kind"],"CLOSED_CONTINUUM_ORIGINAL_SOURCE_ZERO_SET")
            self.assertIs(certificate["source_zero_set"]["inactive_amplitude_may_be_nonzero"],True)
            self.assertIsNone(certificate["polynomial_root_proof"])

    def test_maximum_order_six_has_no_moving_order_contribution(self):
        cubic=[-1,3,-3,1]
        for p,q,offset in ((cubic,[0],Q(0)),([0],cubic,-Q(1,2)),([0],cubic,Q(1,5))):
            _,_,certificate=self.prove(p,q,lo=Q(1,2),hi=Q(3,2),offset=offset)
            event=certificate["source_zero_set"]["events"][0]
            self.assertEqual((event["physical_order"],event["polynomial_multiplicity"]),(6,3))
            self.assertIs(event["moving_carrier_root_order_added"],False)
            self.assertEqual(event["order_derivation"]["remaining_factor_order"],0)
            self.assertNotIn("residual_event_id",event)
        _,_,certificate=self.prove(cubic,[1,-2,1],lo=Q(1,2),hi=Q(3,2),offset=Q(1,3))
        self.assertEqual(certificate["source_zero_set"]["events"][0]["physical_order"],4)

    def test_two_original_exterior_roots_and_one_interior_root(self):
        polynomial=factored_polynomial([Q(-1),Q(0),Q(1)])
        _,_,certificate=self.prove(polynomial,[1],lo=Q(-1),hi=Q(1),offset=Q(0))
        zeros=certificate["source_zero_set"]
        self.assertEqual((zeros["closed_root_count"],zeros["source_open_root_count"],zeros["exterior_root_count"]),(3,1,2))
        self.assertEqual(len(zeros["maximal_nonzero_cells"]),2)
        self.assertEqual([e["location"] for e in zeros["events"]],["LEFT_EXTERIOR","SPAN_INTERIOR","RIGHT_EXTERIOR"])
        for endpoint in zeros["exterior_points"]:
            self.assertEqual(endpoint["inward_order"],2);self.assertIsNone(endpoint["outside_order"])
        self.assertTrue(all(not c["left_included"] and not c["right_included"] for c in zeros["maximal_nonzero_cells"]))

    def test_reducible_descriptors_true_midpoint_and_global_endpoint_cleaning_budget(self):
        polynomial=[0,-Q(1,2),0,1]
        spec,hints,certificate=self.prove(polynomial,polynomial,lo=Q(-1),hi=Q(1),offset=Q(1,5))
        zeros=certificate["source_zero_set"]
        self.assertEqual((zeros["closed_root_count"],len(zeros["maximal_nonzero_cells"])),(3,4))
        self.assertEqual(certificate["polynomial_root_proof"]["midpoint_operations"],3)
        for root in certificate["polynomial_root_proof"]["roots"]:
            coordinate=root["coordinate"]
            if coordinate["kind"]=="REAL_ALGEBRAIC_ISOLATOR":
                self.assertEqual(trim(coordinate["defining_polynomial"]),trim(polynomial))
                self.assertIs(coordinate["defining_polynomial_irreducible_claimed"],False)
                self.assertIs(coordinate["coordinate_irrationality_claimed"],False)
                self.assertTrue(all(at(trim(polynomial),Q(t))!=0 for t in coordinate["isolating_interval"]))
        for budget in (0,1,2):
            with self.subTest(budget=budget),mock.patch.object(model,"qualified_modules",return_value=(self.s,self.c)), \
                 mock.patch.object(self.s,"MAX_MIDPOINT_OPERATIONS",budget):
                result=model.check_source(spec,*hints);self.nontruth(result);self.assertEqual(result["code"],"RESOURCE_REFUSAL")
        for budget in (True,False,-1,129,"128",None):
            with mock.patch.object(model,"qualified_modules",return_value=(self.s,self.c)), \
                 mock.patch.object(self.s,"MAX_MIDPOINT_OPERATIONS",budget):self.nontruth(model.check_source(spec,*hints))

    def test_rational_coordinates_can_use_algebraic_format_without_false_claim(self):
        polynomial=factored_polynomial([Q(1,3),Q(2,3)])
        _,_,certificate=self.prove(polynomial,polynomial,offset=Q(1,5))
        for event,actual in zip(certificate["source_zero_set"]["events"],(Q(1,3),Q(2,3))):
            coordinate=event["coordinate"];left,right=coordinate_bounds(coordinate)
            self.assertTrue(left==right==actual or left<actual<right)
            if left<right:self.assertIs(coordinate["coordinate_irrationality_claimed"],False)

    def test_201_bit_derived_identity_is_admitted_without_residual_raw_conversion(self):
        n=Q(1<<100)
        spec,hints,certificate=self.prove([0,n],[0,n],hi=1/n,offset=Q(1,5),parameter="stationary-201-bit-derived-positive")
        self.assertEqual(spec["cos_splines"]["0"]["controls"],["0","0","1"])
        self.assertEqual(spec["cos_splines"]["1"]["controls"],["0"])
        original_coefficient=Q(certificate["whole_source_lowering"]["C0"][2])
        self.assertEqual(original_coefficient.numerator.bit_length(),201)
        self.assertEqual(certificate["stationary_polynomial_selection"]["selected_polynomial"],["0","1"])
        zero=certificate["source_zero_set"]
        self.assertEqual((zero["closed_root_count"],zero["exterior_root_count"]),(1,1))
        self.assertEqual(zero["events"][0]["physical_order"],2)
        self.assertIs(certificate["scope"]["derived_residual_source_or_raw_control_conversion_required"],False)
        # Raw controls still fit128 bits while the exact interior root needs
        # a161-bit denominator. Output coordinates use the derived envelope.
        denominator=Q((1<<60)+1);intercept=-1/denominator
        narrow,_,interior=self.prove([intercept,n],[intercept,n],hi=1/n,offset=Q(1,5),
                                     parameter="stationary-161-bit-root-coordinate")
        for spline in narrow["cos_splines"].values():
            for token in spline["knots"]+spline["controls"]:
                value=Q(token)
                self.assertLessEqual(max(value.numerator.bit_length(),value.denominator.bit_length()),128)
        coordinate=interior["source_zero_set"]["events"][0]["coordinate"]
        self.assertEqual(coordinate,{"kind":"RATIONAL","value":str(1/(n*denominator))})
        self.assertEqual(Q(coordinate["value"]).denominator.bit_length(),161)
        self.assertEqual(interior["source_zero_set"]["events"][0]["location"],"SPAN_INTERIOR")

    def test_nonunit_signed_domain_scale_and_valid_degree_elevation(self):
        common=[-Q(1,3),1];p=[-6*v for v in times(common,[-1,1])];q=[9*v for v in common]
        spec,hints,old=self.prove(p,q,lo=-Q(3,2),hi=Q(2),offset=-Q(2,5),parameter="signed-original-parameter")
        elevated,hints,new=self.prove(p,q,lo=-Q(3,2),hi=Q(2),offset=-Q(2,5),degree0=6,degree1=6,parameter="signed-original-parameter")
        self.assertNotEqual(digest(spec),digest(elevated))
        self.assertTrue(model.validate_certificate(elevated,*hints,new)["valid"])
        with self.assertRaises(model.Refusal):model.validate_certificate(elevated,*hints,old)
        changed=copy.deepcopy(spec);changed["source_parameter_id"]="another-valid-original-parameter"
        fresh=model.certify_source(changed,*hints);audit_stationary_certificate(self,changed,p,q,fresh)
        with self.assertRaises(model.Refusal):model.validate_certificate(changed,*hints,old)
        # Active branches retain the actual signed/nonmonic polynomial; the
        # conditional isolator must not silently assume the selection is monic.
        for a,b,offset in ((p,[1],Q(-2)),([1],p,-Q(3,2))):
            _,_,active=self.prove(a,b,lo=-Q(3,2),hi=Q(2),offset=offset)
            self.assertEqual(trim(active["stationary_polynomial_selection"]["selected_polynomial"]),trim(p))
            self.assertEqual(active["source_zero_set"]["closed_root_count"],2)

    def test_inactive_amplitude_source_binding_and_old_certificate_reuse(self):
        spec,hints,old=self.prove([0],[1],offset=Q(2))
        self.nontruth(model.check_source(spec,["0"],["2"]))
        changed=copy.deepcopy(spec);changed["cos_splines"]["1"]["controls"][0]="-1/3"
        self.nontruth(model.check_source(changed,*hints))
        other,hints,new=self.prove([0],[2],offset=Q(2))
        self.assertEqual(new["source_zero_set"]["kind"],old["source_zero_set"]["kind"])
        with self.assertRaises(model.Refusal):model.validate_certificate(other,*hints,old)

    def test_no_moving_source_builder_certifier_or_phase_lattice_is_called(self):
        functions=[(self.s,name) for name in ("certify_source","check_source","source_from_polynomials","prove_residual_source","_residual_source","_verify_residual")]
        functions += [(self.c,name) for name in ("certify_source","check_source","source_from_polynomials","lower_source","_phase_range","enumerate_phase_candidates","prove_root_jet")]
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(model,"qualified_modules",return_value=(self.s,self.c)))
            spies=[stack.enter_context(mock.patch.object(module,name,side_effect=AssertionError("stationary proof entered moving stage "+name)))
                   for module,name in functions]
            for row in self.replay["cases"]:
                certificate=model.certify_source(row["spec"],row["P"],row["Q"])
                self.same(certificate,row["certificate"])
            n=Q(1<<100);spec=supplied_source([0,n],[0,n],hi=1/n,offset=Q(1,5))
            certificate=model.certify_source(spec,["0",str(n)],["0",str(n)])
            audit_stationary_certificate(self,spec,[Q(0),n],[Q(0),n],certificate)
            for spy in spies:spy.assert_not_called()

    def test_active_branches_and_continua_do_not_invent_common_factor_proofs(self):
        with mock.patch.object(model,"qualified_modules",return_value=(self.s,self.c)), \
             mock.patch.object(self.s,"decompose_amplitudes",side_effect=AssertionError("active branch used gcd selection")) as decomposition, \
             mock.patch.object(self.c,"compute_bezout",side_effect=AssertionError("active branch used residual Bezout")) as bezout:
            for index in (0,1,5,6,7):
                row=self.replay["cases"][index]
                self.same(model.certify_source(row["spec"],row["P"],row["Q"]),row["certificate"])
            decomposition.assert_not_called();bezout.assert_not_called()
        with mock.patch.object(model,"isolate_stationary_polynomial",side_effect=AssertionError("continuum isolated zero polynomial")) as isolate:
            for index in (5,6,7):
                row=self.replay["cases"][index]
                self.same(model.certify_source(row["spec"],row["P"],row["Q"]),row["certificate"])
            isolate.assert_not_called()




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
             mock.patch.object(model,"qualified_modules",side_effect=AssertionError("unsafe raw input loaded proof")) as loader:
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
        with tempfile.TemporaryDirectory(prefix="stationary-square-json-") as directory:
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
        with tempfile.TemporaryDirectory(prefix="stationary-square-missing-") as directory:
            with self.assertRaises(model.Refusal):model.read_report(Path(directory)/"missing.json")

    def test_original_nonzero_rate_refuses_before_any_dependency_or_fraction_work(self):
        spec=supplied_source([-Q(1,3),1],[1],offset=Q(1,5))
        with mock.patch.object(model,"Fraction",side_effect=AssertionError("moving input constructed fraction")) as fraction, \
             mock.patch.object(model,"qualified_modules",side_effect=AssertionError("moving input loaded proof")) as loader:
            for value in ("1","-1",str(Q(1,1<<120))):
                changed=copy.deepcopy(spec);changed["phase_turn_rate"]=value
                result=model.check_source(changed,["-1/3","1"],["1"])
                self.nontruth(result);self.assertEqual(result["code"],"UNSUPPORTED_MOVING_PHASE")
            fraction.assert_not_called();loader.assert_not_called()

    def test_inactive_input_tokens_and_original_clamps_are_still_fully_preflighted(self):
        spec=supplied_source([0],[1],offset=Q(2))
        bad=[]
        changed=copy.deepcopy(spec);changed["cos_splines"]["1"]["controls"][0]="1e999999999";bad.append((changed,["0"],["1"]))
        bad.append((spec,["0"],["1e999999999"]))
        for field,value in (("parameter_lo","-3"),("parameter_hi","3"),("phase_turn_offset","9"),
                            ("parameter_hi","0")):
            changed=copy.deepcopy(spec);changed[field]=value;bad.append((changed,["0"],["1"]))
        changed=copy.deepcopy(spec);changed["cos_splines"]["1"]["knots"][-1]="1/2";bad.append((changed,["0"],["1"]))
        with mock.patch.object(model,"Fraction",side_effect=AssertionError("bad inactive data parsed")) as fraction, \
             mock.patch.object(model,"qualified_modules",side_effect=AssertionError("bad source loaded proof")) as loader:
            for index,args in enumerate(bad):
                with self.subTest(index=index):self.nontruth(model.check_source(*args))
            fraction.assert_not_called();loader.assert_not_called()

    def test_actual_stationary_and_conditional_proof_stage_failures_are_atomic(self):
        p=["-1/2","0","1"];spec=supplied_source(p,p,lo=Q(-1),hi=Q(1),offset=Q(1,5))
        for name in ("lower_stationary_source","classify_stationary_phase","select_stationary_polynomial",
                     "isolate_stationary_polynomial","assemble_stationary_zero_set"):
            with self.subTest(stage=name),mock.patch.object(model,name,side_effect=RuntimeError("CONTROLLED_STAGE_FAILURE")) as hook:
                self.nontruth(model.check_source(spec,p,p));self.assertGreater(hook.call_count,0)
        for module,name in ((self.s,"decompose_amplitudes"),(self.c,"compute_bezout"),(self.s,"isolate_polynomial_roots"),
                            (self.s,"count_roots_open")):
            with self.subTest(conditional=name),mock.patch.object(model,"qualified_modules",return_value=(self.s,self.c)), \
                 mock.patch.object(module,name,side_effect=RuntimeError("CONTROLLED_CONDITIONAL_FAILURE")) as hook:
                self.nontruth(model.check_source(spec,p,p));self.assertGreater(hook.call_count,0)

    def test_actual_returned_stationary_proofs_are_revalidated(self):
        p=["-1/3","1"];spec=supplied_source(p,p,offset=Q(1,5))
        mutations={
            "lower_stationary_source":lambda r:r.__setitem__("C0",["1"]),
            "classify_stationary_phase":lambda r:r.__setitem__("branch","INTEGER_COSINE_WEIGHT_ONE"),
            "select_stationary_polynomial":lambda r:r.__setitem__("selected_polynomial",["1"]),
            "isolate_stationary_polynomial":lambda r:r["roots"].clear(),
            "assemble_stationary_zero_set":lambda r:r["events"][0].__setitem__("physical_order",4)}
        for name,mutate in mutations.items():
            actual=getattr(model,name);changes=[]
            def changed(*args,**kwargs):
                result=copy.deepcopy(actual(*args,**kwargs));before=canonical(result)
                mutate(result);changes.append(canonical(result)!=before);return result
            with self.subTest(stage=name),mock.patch.object(model,name,side_effect=changed) as hook:
                self.nontruth(model.check_source(spec,p,p));self.assertEqual(hook.call_count,1);self.assertEqual(changes,[True])
        actual=self.c.compute_bezout;changes=[]
        def wrong_bezout(*args,**kwargs):
            result=copy.deepcopy(actual(*args,**kwargs));before=canonical(result)
            result["A"]=["0"];result["B"]=["0"];changes.append(canonical(result)!=before);return result
        with mock.patch.object(model,"qualified_modules",return_value=(self.s,self.c)), \
             mock.patch.object(self.c,"compute_bezout",side_effect=wrong_bezout) as bezout:
            self.nontruth(model.check_source(spec,p,p));self.assertEqual(bezout.call_count,1);self.assertEqual(changes,[True])

    def test_phase_selection_and_original_source_receipt_falsifiers(self):
        def reject(index,mutate):
            replay=copy.deepcopy(self.replay);mutate(replay["cases"][index]["certificate"])
            with self.assertRaises(model.Refusal):model.report_from_replay(replay)
        controls=[
            (0,lambda c:c["stationary_phase_proof"].__setitem__("branch","BOTH_WEIGHTS_STRICTLY_POSITIVE")),
            (0,lambda c:c["stationary_polynomial_selection"].__setitem__("active_amplitude","Q")),
            (0,lambda c:c["stationary_polynomial_selection"].__setitem__("selected_polynomial",["1"])),
            (1,lambda c:c["stationary_phase_proof"].__setitem__("sin_squared_exact_value","0")),
            (2,lambda c:c["stationary_polynomial_selection"]["decomposition"].__setitem__("G",["1"])),
            (2,lambda c:c["stationary_polynomial_selection"]["residual_bezout"].__setitem__("B",["0"])),
            (3,lambda c:c["stationary_polynomial_selection"]["decomposition"].__setitem__("G_squared",["1"])),
            (4,lambda c:c["stationary_polynomial_selection"].__setitem__("selected_polynomial",["-1/3","1"])),
            (5,lambda c:c["whole_source_lowering"].__setitem__("C1",["0"])),
            (5,lambda c:c["stationary_polynomial_selection"].__setitem__("selected_polynomial_identically_zero",False)),
            (6,lambda c:c["stationary_phase_proof"].__setitem__("reduced_offset_numerator","1")),
            (7,lambda c:c["stationary_polynomial_selection"].__setitem__("selection_kind","ACTIVE_AMPLITUDE")),
            (0,lambda c:c["whole_source_lowering"]["global_phase_turn_law"].__setitem__("rate","1"))]
        for index,(case,mutate) in enumerate(controls):
            with self.subTest(control=index):reject(case,mutate)

    def test_polynomial_coverage_multiplicity_and_descriptor_falsifiers(self):
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
            (2,lambda p:p["roots"][0]["discovery"].__setitem__("node_id","UNSEARCHED")),
            (2,lambda p:p["closed_interval_open_count_receipt"].__setitem__("open_root_count",1)),
            (2,lambda p:p.__setitem__("global_midpoint_budget",True)),
            (3,lambda p:p["multiplicity_chain"].pop()),
            (3,lambda p:p["roots"][0].__setitem__("multiplicity",1)),
            (3,lambda p:p["roots"][0]["multiplicity_evidence"]["chain_membership"][1].__setitem__("root_count",0))]
        for index,(case,mutate) in enumerate(controls):
            with self.subTest(control=index):reject(case,mutate)

    def test_finite_physical_orders_cells_and_continuum_types_cannot_be_forged(self):
        def reject(index,mutate):
            replay=copy.deepcopy(self.replay);mutate(replay["cases"][index]["certificate"]["source_zero_set"])
            with self.assertRaises(model.Refusal):model.report_from_replay(replay)
        controls=[
            (0,lambda z:z["events"][0].__setitem__("moving_carrier_root_order_added",True)),
            (0,lambda z:z["events"][0].__setitem__("physical_order",4)),
            (0,lambda z:z["events"][0]["order_derivation"].__setitem__("remaining_factor_order",2)),
            (2,lambda z:z["events"].reverse()),
            (2,lambda z:z["events"].__setitem__(1,copy.deepcopy(z["events"][0]))),
            (2,lambda z:z["maximal_nonzero_cells"][0]["right_boundary"].__setitem__("coordinate",{"kind":"RATIONAL","value":"0"})),
            (2,lambda z:z["maximal_nonzero_cells"][0].__setitem__("right_included",True)),
            (2,lambda z:z["maximal_nonzero_cells"].pop()),
            (3,lambda z:z["events"][0].__setitem__("physical_order",6)),
            (4,lambda z:z["exterior_points"][0].__setitem__("exact_value","1")),
            (4,lambda z:z["exterior_points"][0].__setitem__("outside_order",0)),
            (5,lambda z:z.__setitem__("events",[])),
            (5,lambda z:z.__setitem__("closed_root_count",0)),
            (6,lambda z:z.__setitem__("maximal_nonzero_cells",[])),
            (7,lambda z:z.__setitem__("inactive_amplitude_may_be_nonzero",True))]
        for index,(case,mutate) in enumerate(controls):
            with self.subTest(control=index):reject(case,mutate)

    def test_formatter_rechecks_receipts_without_repeating_polynomial_production(self):
        with mock.patch.object(model,"isolate_stationary_polynomial",side_effect=AssertionError("formatter reran isolation")) as isolate, \
             mock.patch.object(model,"select_stationary_polynomial",side_effect=AssertionError("formatter repeated actual selection")) as select:
            self.same(model.report_from_replay(self.replay),self.report)
            isolate.assert_not_called();select.assert_not_called()
        controls=(lambda r:r["cases"].pop(),lambda r:r["cases"].reverse(),
                  lambda r:r["cases"].__setitem__(1,copy.deepcopy(r["cases"][0])),
                  lambda r:r["cases"][0]["spec"].__setitem__("source_parameter_id","changed-original"),
                  lambda r:r["input_custody"][0].__setitem__("bytes",True),
                  lambda r:r["cases"][0]["certificate"]["input_custody"][0].__setitem__("sha256","0"*64))
        for index,mutate in enumerate(controls):
            replay=copy.deepcopy(self.replay);mutate(replay)
            with self.subTest(index=index),self.assertRaises(model.Refusal):model.report_from_replay(replay)
        with mock.patch.object(model,"replay_sources",side_effect=RuntimeError("ACTUAL_REPLAY_FAILURE")) as replay:
            with self.assertRaises(model.Refusal):model.validate_report(self.report)
            replay.assert_called_once()

    def test_canonical_report_rejects_count_scope_custody_and_gate_changes(self):
        self.assertTrue(model._compare_with_replayed_bytes(self.report,self.expected_bytes))
        controls=(lambda r:r["summary"].__setitem__("root_free_finite_sources",True),
                  lambda r:r["summary"].__setitem__("closed_continuum_sources",0),
                  lambda r:r["scope"].__setitem__("legacy_quarter_turn_stationary_overlap_acknowledged",False),
                  lambda r:r["gates"].__setitem__("MC-1","ESTABLISHED"),
                  lambda r:r["gates"].__setitem__("production_authorized",True),
                  lambda r:r["budgets"].__setitem__("maximum_physical_events",36),
                  lambda r:r["executed_byte_custody"].__setitem__("saved_moving_report_replayed",True),
                  lambda r:r["supplied_source_contract"].__setitem__("moving_public_source_certifier_called",True))
        for index,mutate in enumerate(controls):
            changed=copy.deepcopy(self.report);mutate(changed)
            with self.subTest(index=index),self.assertRaises(model.Refusal):model._compare_with_replayed_bytes(changed,self.expected_bytes)
        for key in ("PB-007-01","PB-007-02","PB-007-03","PB-007-04"):self.assertEqual(self.report["gates"][key],"OPEN")
        for key in ("MC-B","MC-1"):self.assertEqual(self.report["gates"][key],"NOT_ESTABLISHED")
        self.assertEqual(self.report["gates"]["required_operation_count"],26)
        self.assertIs(self.report["scope"]["frozen_fifty_source_cohort_changed"],False)
        self.assertIs(self.report["scope"]["frozen_121_source_corpus_changed"],False)

    def test_seven_exact_input_records_and_only_two_conditional_modules_execute(self):
        self.assertEqual(len(model.DEPENDENCY_PINS),7);self.assertEqual(len(model.INPUT_RECORDS),7)
        observed=[];shared_records={r["path"]:r for r in self.s.INPUT_RECORDS}
        for record,(relative,pin) in zip(model.INPUT_RECORDS,sorted(model.DEPENDENCY_PINS.items())):
            raw=(ROOT/relative).read_bytes()
            self.assertEqual(git_blob(raw),pin)
            if relative in (model.SHARED_MODEL,model.COPRIME_MODEL):
                self.assertTrue(record["use"].startswith("EXECUTED_"))
            else:self.assertEqual(record["use"],shared_records[relative]["use"])
            observed.append({"path":relative,"git_blob":pin,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),"use":record["use"]})
        self.same(model.INPUT_RECORDS,observed);self.same(self.replay["input_custody"],observed)
        self.same(self.report["executed_byte_custody"]["inputs"],observed)
        compiled=[];actual_compile=builtins.compile
        def compiler(raw,path,mode,**options):
            compiled.append((git_blob(raw),path,options));return actual_compile(raw,path,mode,**options)
        with mock.patch.object(builtins,"compile",side_effect=compiler):
            shared,coprime=model.qualified_modules()
            self.same(coprime.capture_references(),coprime.REFERENCE_RECORDS)
        self.assertEqual(compiled,[(model.SHARED_BLOB,str(ROOT/model.SHARED_MODEL),{"dont_inherit":True,"optimize":0}),
                                   (model.COPRIME_BLOB,str(ROOT/model.COPRIME_MODEL),{"dont_inherit":True,"optimize":0})])
        self.same(shared._stationary_input_custody,observed);self.same(coprime._stationary_input_custody,observed)
        self.same(self.report["executed_byte_custody"]["executed_project_modules"],[model.SHARED_MODEL,model.COPRIME_MODEL])
        self.assertIs(self.report["executed_byte_custody"]["hostile_python_sandbox_claimed"],False)

    def test_both_actual_accepted_project_caches_and_preloads_are_ignored(self):
        with tempfile.TemporaryDirectory(prefix="stationary-square-dependency-cache-") as directory:
            root=Path(directory)
            for relative in model.DEPENDENCY_PINS:
                path=root/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((ROOT/relative).read_bytes())
            for relative in (model.SHARED_MODEL,model.COPRIME_MODEL):
                path=root/relative;trusted=path.read_bytes();payload=b"PROJECT_CACHE_SUBSTITUTION = True\n#"
                ordinary=install_accepted_stale_cache(path,trusted,payload+b" "*(len(trusted)-len(payload)))
                self.assertTrue(ordinary.PROJECT_CACHE_SUBSTITUTION)
            names=("_radicadsac_stationary_shared_"+model.SHARED_BLOB,"_radicadsac_shared_square_coprime_"+model.COPRIME_BLOB,
                   Path(model.SHARED_MODEL).stem,Path(model.COPRIME_MODEL).stem)
            preloads={name:types.ModuleType(name) for name in names}
            for module in preloads.values():module.PROJECT_CACHE_SUBSTITUTION=True
            with mock.patch.object(model,"ROOT",root),mock.patch.dict(sys.modules,preloads):
                shared,coprime=model.qualified_modules()
                for module in (shared,coprime):self.assertFalse(hasattr(module,"PROJECT_CACHE_SUBSTITUTION"))
                for name,module in preloads.items():self.assertIs(sys.modules[name],module)
                self.same(coprime.capture_references(),coprime.REFERENCE_RECORDS)
                spec=supplied_source([-Q(1,3),1],[-Q(1,3),1],offset=Q(1,5))
                with mock.patch.object(model,"qualified_modules",return_value=(shared,coprime)):
                    certificate=model.certify_source(spec,["-1/3","1"],["-1/3","1"])
                audit_stationary_certificate(self,spec,[-Q(1,3),Q(1)],[-Q(1,3),Q(1)],certificate)

    def test_all_seven_replaced_paths_still_consume_the_original_captured_bytes(self):
        with tempfile.TemporaryDirectory(prefix="stationary-square-retained-buffers-") as directory:
            root=Path(directory)
            for relative in model.DEPENDENCY_PINS:
                path=root/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((ROOT/relative).read_bytes())
            read=model._read_bounded;seen=[]
            def replace(path,limit):
                raw=read(path,limit);seen.append(str(path.relative_to(root)))
                path.write_bytes(b"DEPENDENCY_PATH_REPLACED = True\n");return raw
            with mock.patch.object(model,"ROOT",root),mock.patch.object(model,"_read_bounded",side_effect=replace):
                shared,coprime=model.qualified_modules()
                self.assertEqual(seen,sorted(model.DEPENDENCY_PINS))
                self.assertFalse(hasattr(shared,"DEPENDENCY_PATH_REPLACED"));self.assertFalse(hasattr(coprime,"DEPENDENCY_PATH_REPLACED"))
                self.same(coprime.capture_references(),coprime.REFERENCE_RECORDS)
                p=[-Q(1,2),Q(0),Q(1)];spec=supplied_source(p,p,lo=Q(-1),hi=Q(1),offset=Q(1,5))
                with mock.patch.object(model,"qualified_modules",return_value=(shared,coprime)):
                    certificate=model.certify_source(spec,list(map(str,p)),list(map(str,p)))
                audit_stationary_certificate(self,spec,p,p,certificate)
                with self.assertRaises(model.Refusal):model.qualified_modules()
                for module,relative in ((shared,model.COPRIME_MODEL),(coprime,next(iter(coprime.REFERENCE_PINS)))):
                    for path,limit in ((root/"undeclared.json",256),(root/relative,0),(root/relative,True),
                                       (root/relative,-1),(root/relative,model.MAX_CODE_BYTES+1)):
                        with self.assertRaises((model.Refusal,shared.Refusal,coprime.Refusal)):module._read_bounded(path,limit)

    def test_dependency_drift_alias_size_and_missing_inputs_fail_before_compile(self):
        reader=model._read_bounded
        for relative in model.DEPENDENCY_PINS:
            def drift(path,limit):return b"changed dependency" if path==ROOT/relative else reader(path,limit)
            compiler=mock.Mock(side_effect=AssertionError("unverified dependency compiled"))
            with self.subTest(path=relative),mock.patch.object(model,"_read_bounded",side_effect=drift), \
                 mock.patch.dict(model.__dict__,{"compile":compiler}):
                with self.assertRaises(model.Refusal):model.qualified_modules()
                compiler.assert_not_called()
        with tempfile.TemporaryDirectory(prefix="stationary-square-dependency-alias-") as directory:
            root=Path(directory)
            for relative in model.DEPENDENCY_PINS:
                path=root/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((ROOT/relative).read_bytes())
            for relative in (model.SHARED_MODEL,model.COPRIME_MODEL):
                path=root/relative;raw=path.read_bytes();path.unlink()
                target=path.with_name("unlisted-"+path.name);target.write_bytes(raw);path.symlink_to(target)
                with mock.patch.object(model,"ROOT",root):
                    with self.assertRaises(model.Refusal):model.qualified_modules()
                    path.unlink()
                    with self.assertRaises(model.Refusal):model.qualified_modules()
                    with path.open("wb") as stream:stream.truncate(model.MAX_CODE_BYTES+1)
                    with self.assertRaises(model.Refusal):model.qualified_modules()
                path.write_bytes(raw)

    def test_fixture_builder_preserves_zero_rate_and_original_elevated_controls(self):
        p=["-1/3","1"];q=["1"]
        actual=model.source_from_polynomials(p,q,"-1","2","-2/5","0","independent-fixture-original",degrees=(6,6))
        expected=supplied_source(p,q,lo=Q(-1),hi=Q(2),offset=-Q(2,5),degree0=6,degree1=6,parameter="independent-fixture-original")
        self.same(actual,expected)
        audit_stationary_certificate(self,actual,trim(p),trim(q),model.certify_source(actual,p,q))
        with mock.patch.object(model,"qualified_modules",side_effect=AssertionError("invalid fixture loaded dependencies")) as loader:
            for rate in ("1","-1","1/"+str(1<<120)):
                with self.assertRaises(model.Refusal):model.source_from_polynomials(p,q,"0","1","0",rate,"id")
            for degrees in ((True,6),(7,6),(0,False),[6],"66"):
                with self.assertRaises(model.Refusal):model.source_from_polynomials(p,q,"0","1","0","0","id",degrees=degrees)
            loader.assert_not_called()

    def test_conditional_coefficient_overflow_and_invalid_phase_tokens_are_bounded(self):
        with self.assertRaises(self.c.Refusal):self.c._safe(Q(1<<4095),Q(2),"mul")
        with mock.patch.object(self.c,"rational",side_effect=AssertionError("invalid phase reached arithmetic")) as rational:
            for value in (True,0,None,"1e999999999","1/0","1/1","-0","9"*129):
                with self.assertRaises(model.Refusal):model.classify_stationary_phase(self.c,value)
            rational.assert_not_called()

    def test_workflow_has_exact_seven_dependency_and_five_owned_path_closure(self):
        own={TASK+name for name in ("pb00701_stationary_square_source.py","verify_pb00701_stationary_square_source.py",
                                  "pb00701-stationary-square-source.json","pb00701-stationary-square-source-research.md")}
        workflow=".github/workflows/mc1-pb00701-stationary-square-source.yml";own.add(workflow)
        text=(ROOT/workflow).read_text();before,after=text.split("  push:",1)
        for section in (before,after):
            paths=re.findall(r"^      - ['\"]([^'\"]+)['\"]$",section,re.M)
            self.assertEqual(set(paths),set(model.DEPENDENCY_PINS)|own);self.assertEqual(len(paths),12)
        self.assertNotIn("strategy:",text)
        self.assertIn("github.event.pull_request.head.sha || github.sha",text)
        self.assertIn("verify_pb00701_stationary_square_source.py --contract --self-test",text)
        self.assertIn("python-version: '3.12'",text)


def test_suite(replay=None,report=None):
    StationarySquareTests.replay=replay
    StationarySquareTests.report=report
    classes=(StationarySquareTests,build_bootstrap_tests(MODEL_PATH,MODEL_BLOB))
    return unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(case) for case in classes)


model=load_reviewed_model(MODEL_PATH,MODEL_BLOB)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract",action="store_true")
    parser.add_argument("--self-test",action="store_true")
    options=parser.parse_args()
    if not(options.contract or options.self_test):parser.error("choose --contract and/or --self-test")
    replay=model.replay_sources();report=model.report_from_replay(replay)
    if options.contract:model._compare_with_replayed_bytes(model.read_report(),canonical(report))
    if options.self_test:
        result=unittest.TextTestRunner(verbosity=2).run(test_suite(replay,report))
        if not result.wasSuccessful():raise SystemExit(1)
    print("PASS: complete original stationary controls, exact weight branches and polynomial selections are checked")
    print("PASS: independent isolation/multiplicity/topology projection proves five finite source sets and three continua")
    print("PASS: near-cardinal rationals, inactive cancellation, order six and the 201-bit derived positive retain exact semantics")
    print("PASS: moving proof routes remain unused; bounded same-buffer custody and twelve-path CI closure are checked")


if __name__=="__main__":main()


