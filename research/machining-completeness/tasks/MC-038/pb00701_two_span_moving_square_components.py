#!/usr/bin/env python3
"""Bounded exact original two-span moving-phase squared-amplitude event theorem.

This is a prospective-source research proof, NOT a full PB-007-01, MC-B, or
native machining solver. No stored event assertion is accepted as authority.
All mathematical root decisions use rational source identities and a finite
enumeration of integer/half-integer phase values; no sign-change scan.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction as Q
from math import isqrt

SCHEMA = "radicadsac-mc038-two-span-moving-square-components/1.0"
GRAMMAR = "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE"
STATUS = "EXACT_ORIGINAL_TWO_SPAN_MOVING_SQUARE_COMPONENTS_RESEARCH"
MAX_SOURCE_BYTES = 16_384
MAX_BITS = 256
MAX_DERIVED_BITS = 1024
MAX_ABS_PHASE_TURNS = 32


class Refusal(ValueError):
    pass


class ResourceRefusal(Refusal):
    pass


def need(condition, reason):
    if not condition:
        raise Refusal(reason)


def budget(condition, reason):
    if not condition:
        raise ResourceRefusal(reason)


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def rational(token):
    need(type(token) is str and 0 < len(token) <= 128, "NONCANONICAL_RATIONAL")
    try:
        result = Q(token)
    except (ValueError, TypeError, ZeroDivisionError, OverflowError) as exc:
        raise Refusal("NONCANONICAL_RATIONAL") from exc
    need(str(result) == token, "NONCANONICAL_RATIONAL")
    budget(max(abs(result.numerator).bit_length(), result.denominator.bit_length())
           <= MAX_BITS, "RATIONAL_INPUT_BIT_BUDGET")
    return result


def bound(*values):
    for value in values:
        budget(max(abs(value.numerator).bit_length(), value.denominator.bit_length())
               <= MAX_DERIVED_BITS, "DERIVED_RATIONAL_BIT_BUDGET")


def isqrt_rational(value):
    if value < 0:
        raise Refusal("AFFINE_SQUARE_NEGATIVE")
    numerator, denominator = isqrt(value.numerator), isqrt(value.denominator)
    need(numerator * numerator == value.numerator and
         denominator * denominator == value.denominator,
         "AFFINE_SQUARE_NOT_RATIONAL")
    return Q(numerator, denominator)


def square_affine(q):
    """Return exact P(u)=p0+p1*u with P^2==q0+q1*u+q2*u^2."""
    q0, q1, q2 = q
    bound(q0, q1, q2)
    if q2 == 0:
        need(q1 == 0, "AFFINE_SQUARE_NONQUADRATIC_LINEAR")
        return isqrt_rational(q0), Q(0)
    root_slope = isqrt_rational(q2)
    need(root_slope != 0, "AFFINE_SQUARE_BAD_SLOPE")
    root_start = q1 / (2 * root_slope)
    bound(root_start)
    need(root_start * root_start == q0, "AFFINE_SQUARE_IDENTITY_FALSE")
    return root_start, root_slope


def eval_affine(p, u):
    return p[0] + p[1] * u


def is_identity(p):
    return p == (Q(0), Q(0))


def affine_order(p, u):
    if is_identity(p):
        return None  # analytic zero factor on the entire source piece
    if eval_affine(p, u) != 0:
        return 0
    need(p[1] != 0, "AFFINE_ZERO_ORDER_INVALID")
    return 1


def source(spec):
    need(type(spec) is dict and set(spec) == {
        "grammar", "source_parameter_id", "parameter_lo", "parameter_hi",
        "phase_turn_offset", "phase_turn_rate", "cos_splines", "sin_splines"
    }, "ORIGINAL_SOURCE_FIELDS_REQUIRED")
    raw = encode(spec)
    budget(len(raw) <= MAX_SOURCE_BYTES, "SOURCE_BYTE_BUDGET")
    need(spec["grammar"] == GRAMMAR, "WRONG_SOURCE_GRAMMAR")
    need(spec["source_parameter_id"] == "source-time-t", "WRONG_ORIGINAL_PARAMETER")
    lo, hi = rational(spec["parameter_lo"]), rational(spec["parameter_hi"])
    need(lo < hi, "INVALID_SOURCE_INTERVAL")
    offset, rate = rational(spec["phase_turn_offset"]), rational(spec["phase_turn_rate"])
    need(rate != 0, "STATIONARY_PHASE_OUTSIDE_MOVING_THEOREM")
    phase_ends = (offset + rate * lo, offset + rate * hi)
    bound(*phase_ends)
    budget(max(abs(v) for v in phase_ends) <= MAX_ABS_PHASE_TURNS,
           "MOVING_PHASE_TURN_BUDGET")
    need(type(spec["sin_splines"]) is dict and not spec["sin_splines"],
         "SINE_CHANNELS_NOT_ADMITTED")
    channels = spec["cos_splines"]
    need(type(channels) is dict and set(channels) == {"0", "1"},
         "EXACT_H0_H1_COSINE_CHANNELS_REQUIRED")
    knot = None
    original = []
    for h in ("0", "1"):
        entry = channels[h]
        need(type(entry) is dict and set(entry) == {"degree", "knots", "controls"},
             "ORIGINAL_SPLINE_FIELDS_REQUIRED")
        need(type(entry["degree"]) is int and entry["degree"] == 2,
             "ORIGINAL_QUADRATIC_REQUIRED")
        need(type(entry["knots"]) is list and len(entry["knots"]) == 8 and
             type(entry["controls"]) is list and len(entry["controls"]) == 5,
             "ORIGINAL_TWO_SPAN_CARDINALITY")
        knots = [rational(x) for x in entry["knots"]]
        k = knots[3]
        need(lo < k < hi and knots == [lo]*3 + [k]*2 + [hi]*3,
             "ORIGINAL_DOUBLE_KNOT_STRUCTURE")
        need(knot is None or knot == k, "CHANNEL_SOURCE_KNOT_MISMATCH")
        knot = k
        original.append([rational(x) for x in entry["controls"]])
    return lo, knot, hi, offset, rate, original, hashlib.sha256(raw).hexdigest()


def bernstein_quadratic(triple):
    a, b, c = triple
    return a, 2 * (b-a), a-2*b+c


def polynomial(q, u):
    return q[0] + u*(q[1]+u*q[2])


def original_cox(knots, controls, x):
    """Independent unsplit original degree-two Cox--de Boor evaluation."""
    base = [Q(int(knots[i] <= x < knots[i+1])) for i in range(7)]
    for degree in (1, 2):
        nxt = []
        for i in range(7-degree):
            left = knots[i+degree]-knots[i]
            right = knots[i+degree+1]-knots[i+1]
            nxt.append(((x-knots[i])*base[i]/left if left else Q(0)) +
                       ((knots[i+degree+1]-x)*base[i+1]/right if right else Q(0)))
        base = nxt
    need(len(base) == len(controls) and sum(base) == 1,
         "ORIGINAL_COX_BASIS_PARTITION")
    return sum((w*c for w,c in zip(base,controls)), Q(0))


def lower_piece(channels, idx, a, b, full_knots):
    """Exact original Bernstein extraction, plus independent Cox controls."""
    coeffs = []
    for control in channels:
        triple = control[idx*2:idx*2+3]
        q = bernstein_quadratic(triple)
        # The equality is an algebraic Bernstein identity; point evaluations
        # below are separate implementation adversarial controls, not the proof.
        bound(*q)
        for u in (Q(1, 7), Q(1, 3), Q(2, 3), Q(6, 7)):
            x = a+(b-a)*u
            bern = triple[0]*(1-u)**2 + 2*triple[1]*u*(1-u)+triple[2]*u*u
            need(polynomial(q,u) == bern, "BERNSTEIN_POLYNOMIAL_MISMATCH")
            need(polynomial(q,u) == original_cox(full_knots,control,x),
                 "ORIGINAL_UNSPLIT_SOURCE_EXTRACTION_MISMATCH")
        coeffs.append(q)
    c0, c1 = coeffs
    p2 = tuple(x+y for x,y in zip(c0,c1))
    q2 = tuple(x-y for x,y in zip(c0,c1))
    P, Qp = square_affine(p2), square_affine(q2)
    # Exact identity in Q[u], not merely equality at the control points:
    for affine, polynomial_coefficients in ((P,p2),(Qp,q2)):
        xx, yy = affine
        need((xx*xx,2*xx*yy,yy*yy) == polynomial_coefficients,
             "PROPOSED_SQUARE_IDENTITY_FALSE")
    return {"a":a,"b":b,"P":P,"Q":Qp,"c0":c0,"c1":c1,
            "identity":is_identity(P) and is_identity(Qp)}


def floor(value):
    return value.numerator // value.denominator


def phase_lattice(a,b,offset,rate):
    """Complete exact integer and half-integer phase preimages in [a,b]."""
    beta0, beta1 = offset+rate*a, offset+rate*b
    bound(beta0,beta1)
    low, high = min(beta0,beta1), max(beta0,beta1)
    budget(max(abs(low),abs(high)) <= MAX_ABS_PHASE_TURNS,
           "PHASE_LATTICE_BUDGET")
    # n/2 includes both integer and half-integer turns; padding cannot
    # omit any n/2 in the closed interval. Filtering is exact.
    candidates=[]
    for n in range(floor(2*low)-1, floor(2*high)+3):
        beta=Q(n,2)
        if low <= beta <= high:
            point=(beta-offset)/rate
            bound(point)
            need(a <= point <= b, "PHASE_LATTICE_INVERSE_OUTSIDE")
            candidates.append(point)
    return candidates


def factor_order(p,u,trig_zero):
    k=affine_order(p,u)
    return None if k is None else k+int(trig_zero)


def physical_order(piece, t, offset,rate):
    u=(t-piece["a"])/(piece["b"]-piece["a"])
    beta=offset+rate*t
    sin_zero=beta.denominator==1
    cos_zero=(2*beta).denominator==1 and not sin_zero
    op=factor_order(piece["P"],u,cos_zero)
    oq=factor_order(piece["Q"],u,sin_zero)
    finite=[v for v in (op,oq) if v is not None]
    if not finite:
        return None  # original physical source piece identically zero
    # F=P^2*cos^2(pi beta)+Q^2*sin^2(pi beta). Both analytic
    # summands are nonnegative; their leading squares cannot cancel.
    return 2*min(finite)


def all_piece_roots(piece,offset,rate):
    a,b=piece["a"],piece["b"]
    if piece["identity"]:
        return None
    candidates=set(phase_lattice(a,b,offset,rate))
    for p in (piece["P"],piece["Q"]):
        if p[1]:
            u=-p[0]/p[1]
            if 0<=u<=1:
                candidates.add(a+(b-a)*u)
    roots=[]
    for t in sorted(candidates):
        k=physical_order(piece,t,offset,rate)
        if k is not None and k>0:
            roots.append((t,k))
    return roots


def analyze(spec):
    lo,knot,hi,offset,rate,channels,binding=source(spec)
    ks=[lo]*3+[knot]*2+[hi]*3
    pieces=[lower_piece(channels,j,a,b,ks)
            for j,(a,b) in enumerate(((lo,knot),(knot,hi)))]
    # Both channel knot values are their actual shared original control,
    # so *physical* continuity at the knot is proved, not assumed.
    for channel, key in zip(channels,("c0","c1")):
        need(polynomial(pieces[0][key],1)==channel[2] and
             polynomial(pieces[1][key],0)==channel[2],
             "ORIGINAL_KNOT_CONTINUITY_NOT_PROVED")
    for piece in pieces:
        piece["roots"]=all_piece_roots(piece,offset,rate)
    point_in_left = (pieces[0]["roots"] is None or
                     knot in dict(pieces[0]["roots"]))
    point_in_right = (pieces[1]["roots"] is None or
                      knot in dict(pieces[1]["roots"]))
    need(point_in_left==point_in_right, "PHYSICAL_KNOT_ZERO_STATUS_CONFLICT")

    intervals = [[p["a"],p["b"]] for p in pieces if p["roots"] is None]
    if len(intervals)==2:
        intervals=[[lo,hi]]
    candidates=sorted({t for p in pieces if p["roots"] is not None
                       for t,_ in p["roots"]})
    points=[t for t in candidates if not any(a<=t<=b for a,b in intervals)]

    def sided(x,side):
        if side=="left":
            return next((p for p in pieces if p["a"]<x<=p["b"]),None)
        return next((p for p in pieces if p["a"]<=x<p["b"]),None)

    def side_order(x,side):
        p=sided(x,side)
        return None if p is None else physical_order(p,x,offset,rate)

    events=[]
    for x in points:
        left,right=side_order(x,"left"),side_order(x,"right")
        need(left is not None or right is not None,
             "ISOLATED_EVENT_WITHOUT_FINITE_GERM")
        need(left is None or left>0, "FALSE_LEFT_EVENT_GERM")
        need(right is None or right>0, "FALSE_RIGHT_EVENT_GERM")
        events.append({"coordinate":str(x),"true_source_knot":x==knot,
                       "left_order":left,"right_order":right,
                       "left_physical_sign":"POSITIVE" if left is not None else None,
                       "right_physical_sign":"POSITIVE" if right is not None else None,
                       "global_smooth_knot_multiplicity_claimed":False})
    continuum=[]
    for a,b in intervals:
        continuum.append({
            "interval":[str(a),str(b)], "left_included":True,
            "right_included":True,
            "left_boundary_inward_order":side_order(a,"right"),
            "right_boundary_inward_order":side_order(b,"left"),
            "left_boundary_outward_order":side_order(a,"left"),
            "right_boundary_outward_order":side_order(b,"right")})

    zero_at=lambda x: x in points or any(a<=x<=b for a,b in intervals)
    boundaries=sorted(set([lo,knot,hi]+points+
                          [v for interval in intervals for v in interval]))
    cells=[]
    for a,b in zip(boundaries,boundaries[1:]):
        midpoint=(a+b)/2
        if any(l<=midpoint<=r for l,r in intervals):
            continue
        need(not any(a<z<b for z in points),
             "UNENUMERATED_INTERIOR_ZERO")
        # Every non-identity piece is a sum of exact squares. Since the
        # exhaustive zero set contains no point in (a,b), F>0 on it.
        if cells and cells[-1][1]==a and not zero_at(a):
            cells[-1]=(cells[-1][0],b)
        else:
            cells.append((a,b))
    for a,b in cells:
        bound(a,b)
    return {
        "schema":SCHEMA,"status":STATUS,"evidence_class":"DETERMINISTIC_MODEL",
        "source_sha256":binding,"source_parameter_id":spec["source_parameter_id"],
        "original_source_interval":[str(lo),str(hi)],
        "true_original_source_knot":str(knot),
        "global_affine_phase_turns":{"offset":str(offset),"rate":str(rate)},
        "admitted_source_pieces":[{
            "interval":[str(p["a"]),str(p["b"])],
            "physical_nonnegative_squares":{
                "P_local_affine":list(map(str,p["P"])),
                "Q_local_affine":list(map(str,p["Q"]))},
            "original_H0_Bernstein":list(map(str,channels[0][idx*2:idx*2+3])),
            "original_H1_Bernstein":list(map(str,channels[1][idx*2:idx*2+3])),
            "identity_zero":p["identity"]} for idx,p in enumerate(pieces)],
        "maximal_closed_zero_intervals":continuum,
        "isolated_zero_points":events,"isolated_point_count":len(events),
        "finite_total_root_cardinality":not bool(intervals),
        "nonzero_sign_cells":[{
            "left":str(a),"right":str(b),
            "left_included":a==lo and not zero_at(a),
            "right_included":b==hi and not zero_at(b),
            "sign":"POSITIVE"} for a,b in cells],
        "complete_for_admitted_source_class":True,
        "historical_case_ids_newly_closed":[],
        "pb00701_certified":False,"pb00702_certified":False,
        "pb00703_certified":False,"pb00704_certified":False,
        "mc_b_established":False,"mc1_established":False,
        "native_geometry_qualified":False,"engineering_step_qualified":False,
        "production_authorized":False
    }


def attempt(spec):
    try:
        return analyze(spec)
    except ResourceRefusal as exc:
        kind="RESOURCE_REFUSAL"
        reason=str(exc)
    except (Refusal,ValueError,TypeError,KeyError,IndexError,
            ZeroDivisionError,OverflowError) as exc:
        kind="BLOCKED"
        reason=str(exc)
    except (MemoryError,RecursionError) as exc:
        kind="RESOURCE_REFUSAL"
        reason=type(exc).__name__
    return {"schema":SCHEMA,"status":kind,"reason":reason,
            "is_truth_value":False,"pb00701_certified":False,
            "mc_b_established":False,"mc1_established":False,
            "production_authorized":False}


def validate_report(spec,report):
    result=attempt(spec)
    if result.get("status")!=STATUS:
        return result
    try:
        need(type(report) is dict and encode(report)==encode(result),
             "FORGED_OR_STALE_ORIGINAL_SOURCE_REPORT")
    except (Refusal,TypeError,ValueError) as exc:
        return {"schema":SCHEMA,"status":"BLOCKED","is_truth_value":False,
                "reason":str(exc),"mc_b_established":False,
                "production_authorized":False}
    return result


def attempt_file(path):
    """Bound raw source input before JSON parsing; never promote parser refusals."""
    try:
        with open(path, "rb") as handle:
            raw = handle.read(MAX_SOURCE_BYTES + 1)
        budget(len(raw) <= MAX_SOURCE_BYTES, "SOURCE_FILE_BYTE_BUDGET")

        def unique_object(pairs):
            result = {}
            for key, value in pairs:
                need(key not in result, "DUPLICATE_SOURCE_JSON_KEY")
                result[key] = value
            return result

        def reject_nonfinite(_token):
            raise Refusal("NONFINITE_SOURCE_JSON")

        spec = json.loads(raw.decode("utf-8"),
                          object_pairs_hook=unique_object,
                          parse_constant=reject_nonfinite)
        return attempt(spec)
    except ResourceRefusal as exc:
        kind, reason = "RESOURCE_REFUSAL", str(exc)
    except (Refusal, OSError, UnicodeError, ValueError, TypeError,
            OverflowError) as exc:
        kind, reason = "BLOCKED", str(exc)
    except (MemoryError, RecursionError) as exc:
        kind, reason = "RESOURCE_REFUSAL", type(exc).__name__
    return {"schema": SCHEMA, "status": kind, "reason": reason,
            "is_truth_value": False, "pb00701_certified": False,
            "mc_b_established": False, "mc1_established": False,
            "production_authorized": False}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--contract",action="store_true")
    parser.add_argument("--source",help="A prospective canonical source JSON file")
    args=parser.parse_args()
    if args.source:
        result=attempt_file(args.source)
        print(json.dumps(result,indent=2,sort_keys=True))
        return 0 if result["status"]==STATUS else 1
    if args.contract:
        # A deterministic fresh original quadratic source; the full test
        # suite verifies the physical zero components and failure surface.
        knots=["0","0","0","1","1","2","2","2"]
        spec={"grammar":GRAMMAR,"source_parameter_id":"source-time-t",
              "parameter_lo":"0","parameter_hi":"2",
              "phase_turn_offset":"0","phase_turn_rate":"1",
              "cos_splines":{
                  "0":{"degree":2,"knots":knots,"controls":["0","0","0","0","1/2"]},
                  "1":{"degree":2,"knots":knots,"controls":["0","0","0","0","-1/2"]}},
              "sin_splines":{}}
        result=attempt(spec)
        need(result["status"]==STATUS,"POSITIVE_CONTRACT_REFUSED")
        need([[i["interval"][0],i["interval"][1]]
              for i in result["maximal_closed_zero_intervals"]]==[["0","1"]],
             "MIXED_CLOSED_INTERVAL_CONTRACT_FAILED")
        need([e["coordinate"] for e in result["isolated_zero_points"]]==["2"],
             "MIXED_ISOLATED_EXTERIOR_CONTRACT_FAILED")
        need(result["maximal_closed_zero_intervals"][0][
                 "right_boundary_outward_order"]==4,
             "CONTINUUM_KNOT_GERM_CONTRACT_FAILED")
        print(json.dumps({"status":"PASS","source_sha256":result["source_sha256"],
                          "zero_intervals":1,"isolated_points":1,
                          "historical_newly_closed":0},sort_keys=True))
        return 0
    parser.print_help()
    return 2


if __name__=="__main__":
    raise SystemExit(main())
