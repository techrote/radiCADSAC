#!/usr/bin/env python3
"""Single ORIGINAL V9 physical event/sign-source certificate (model only).

The exact trigonometric sector proof appears in the accompanying RAG note.
Refusal is nontruth, never evidence for no root on unsupported sources.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import tempfile

BASE = Path(__file__).resolve().parent
CASE = "composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail0"
SHA = "4d1ef1cbecceeb4a43b4e30fd37327fa204164cc9ce25dfe4f1744a052cebcc2"
ROW_SHA = "406ec73609a8213051afd3361478416e496c782b2b89ae2a857b772146059279"
V54_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
ORDERED_WITNESS_BLOB = "8e662094df4106b2a79711c565cd865008fadc8c"
ORDERED_PRODUCER_BLOB = "549251696e43f22122f8ba957baa2befcd8d77a8"

class Refused(ValueError):
    pass

def need(ok, code):
    if not ok:
        raise Refused(code)

def gitblob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def read(path, maximum, blob=None):
    with Path(path).open("rb") as f:
        raw = f.read(maximum+1)
    need(len(raw)<=maximum, "INPUT_BYTE_BUDGET")
    if blob is not None:
        need(gitblob(raw)==blob, "PINNED_GIT_BLOB_DRIFT")
    return raw

def unique(pairs):
    result={}
    for k,v in pairs:
        need(k not in result, "DUPLICATE_JSON_KEY")
        result[k]=v
    return result

def badconstant(_):
    raise Refused("NONFINITE_JSON")

def badfloat(_):
    raise Refused("RECEIPT_FLOAT_NONTRUTH")

def smallint(s):
    need(len(s)<=12, "RECEIPT_INTEGER_TOKEN_BUDGET")
    return int(s)

def decode(raw, receipt=False):
    try:
        return json.loads(raw, object_pairs_hook=unique, parse_constant=badconstant,
                          parse_float=badfloat if receipt else float,
                          parse_int=smallint if receipt else int)
    except (RecursionError, OverflowError) as e:
        raise Refused("JSON_RESOURCE_NONTRUTH") from e

def packed(value):
    return json.dumps(value, sort_keys=True, separators=(",",":"), ensure_ascii=True,
                      allow_nan=False)

def fingerprint(value):
    return hashlib.sha256(packed(value).encode()).hexdigest()

def q(s):
    need(type(s) is str and 0<len(s)<=80, "RATIONAL_TOKEN_NONTRUTH")
    try:
        v=Q(s)
    except (ValueError, ZeroDivisionError, OverflowError) as e:
        raise Refused("RATIONAL_GRAMMAR_NONTRUTH") from e
    need(v.numerator.bit_length()<=256 and v.denominator.bit_length()<=256,
         "RATIONAL_ARITHMETIC_BUDGET")
    return v

def lower(record):
    need(type(record) is dict and set(record)=={"degree","knots","controls"},
         "SPLINE_SCHEMA")
    d=record["degree"]
    k=record["knots"]
    c=record["controls"]
    need(type(d) is int and type(k) is list and type(c) is list, "SPLINE_TYPES")
    if d==0:
        need(k==["0","1","2"] and len(c)==2, "SPLINE0_KNOTS")
        a,b=map(q,c)
        return ((a,Q(0)),(b,Q(0)))
    need(d==1 and k==["0","0","1","1","2","2"] and len(c)==4,
         "SPLINE1_KNOTS")
    a,b,e,f=map(q,c)
    return ((a,b-a),(2*e-f,f-e))

def at(p,t):
    return p[0]+t*p[1]

def prove(spec):
    need(type(spec) is dict and set(spec)=={
        "grammar","source_parameter_id","parameter_lo","parameter_hi",
        "phase_turn_offset","phase_turn_rate","cos_splines","sin_splines"},
        "SOURCE_SCHEMA")
    need(spec["grammar"]=="RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE" and
         spec["source_parameter_id"]=="source-time-t" and
         [spec["parameter_lo"],spec["parameter_hi"]]==["0","2"] and
         [spec["phase_turn_offset"],spec["phase_turn_rate"]]==["0","1/8"],
         "SOURCE_TIME_OR_PHASE")
    cs=spec["cos_splines"]
    ss=spec["sin_splines"]
    need(type(cs) is dict and set(cs)=={"0","1"} and
         type(ss) is dict and set(ss)=={"1"}, "HARMONIC_GRAMMAR")
    c0,c1,s1=lower(cs["0"]),lower(cs["1"]),lower(ss["1"])
    for pieces in (c0,c1,s1):
        need(at(pieces[0],Q(1))==at(pieces[1],Q(1)),
             "TRUE_KNOT_DISCONTINUITY")
    need(c0==((Q(0),Q(0)),(Q(0),Q(0))) and
         c1==((Q(-1,2),Q(1)),(Q(1,2),Q(0))) and
         s1==((Q(1),Q(0)),(Q(1),Q(0))),
         "UNPROVED_SOURCE_AMPLITUDE")
    need(fingerprint(spec)==SHA, "SOURCE_SHA256_DRIFT")
    need(at(c1[0],Q(0))==Q(-1,2) and at(c1[0],Q(1,2))==0 and
         at(c1[0],Q(1))==at(c1[1],Q(1))==Q(1,2),
         "ENDPOINT_OR_KNOT_ALGEBRA")
    # Verified symbolic theorem (RAG): alpha=pi/4, theta=alpha*t.
    # F'_L=(1+alpha)cos(theta)-alpha*(t-1/2)sin(theta)>0
    # on [0,1/2] directly; on [1/2,1] via sin<=cos.
    # F(0)=-1/2, F(1/2)=sin(pi/8)>0 => unique SIMPLE crossing.
    # F_R=cos(theta)/2+sin(theta)>0 on [1,2] although
    # F'_R changes from positive at 1 to negative at 2.

def expected():
    return {
      "schema":"radicadsac-pb00701-v9-two-span-sign/1.0",
      "evidence_class":"DETERMINISTIC_MODEL",
      "case_id":CASE,"source_sha256":SHA,"original_row_sha256":ROW_SHA,
      "source_parameter":["0","2"],"true_knot":"1","phase_turns":["0","1/8"],
      "proof_method":"EXACT_SOURCE_TWO_SPAN_TRIG_SECTOR_SIGN",
      "implicit_root_open":["0","1/2"],"root_count":1,
      "root_kind":"SIMPLE_NEGATIVE_TO_POSITIVE","root_multiplicity":1,
      "knot_sign":"POSITIVE","endpoint_signs":["NEGATIVE","POSITIVE"],
      "right_piece_nonmonotone":True,"right_piece_root_count":0,
      "maximal_sign_cells":[["0","r","NEGATIVE"],["r","2","POSITIVE"]],
      "v54_source_count":121,"v54_route_refusals":20,
      "v54_missing_ordered":30,"v2_preexisting_complete":50,
      "accepted_historical_delta":0,
      "proof_role":"ALTERNATE_SYMBOLIC_PROOF_NOT_NEW_SOURCE_CLOSURE",
      "preexisting_v2_signed_event_witness_git_blob":ORDERED_WITNESS_BLOB,
      "preexisting_v2_signed_event_producer_git_blob":ORDERED_PRODUCER_BLOB,
      "alternate_proof_case_ids":[CASE],
      "new_unique_ordered_source_closures":0,
      "new_complete_source_witnesses":0,
      "new_generic_event_theorem":False,
      "pb_obligations_discharged":0,"pb007_status":"OPEN",
      "mc_b":"NOT_ESTABLISHED","mc1":"NOT_ESTABLISHED",
      "native_geometry":False,"engineering_step":False,
      "production_authorized":False,"supported_operations":26
    }

def verify_receipt(r):
    need(type(r) is dict and packed(r)==packed(expected()),"RECEIPT_TYPED_DRIFT")

def census(c,v):
    rows=c["cases"]
    need(type(rows) is list and len(rows)==121 and
         len(set(x["id"] for x in rows))==121,"V54_SOURCE_DENOMINATOR")
    count=Counter(x["expected"]["v54_disposition"] for x in rows)
    need(count["BLOCKED"]==20 and
         count["BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"]==30,
         "V54_BLOCKER_CENSUS")
    matches=[x for x in rows if x["id"]==CASE]
    need(len(matches)==1 and matches[0]["expected"]["v54_disposition"]==
         "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE" and
         matches[0]["expected"]["observed"]["spans"]==[
           ["PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO","CERTIFIED",None],
           ["DELEGATED_V6_CONSTANT_MODULATION","CERTIFIED",None]],
         "HISTORICAL_CATEGORY3_OWNER")
    prove(matches[0]["spec"])
    need(type(v.get("source_cases")) is list and len(v["source_cases"])==50,
         "V2_DENOMINATOR")
    old=[x for x in v["source_cases"] if x["case_id"]==CASE]
    need(len(old)==1 and old[0]["source_sha256"]==SHA and
         old[0]["original_row_sha256"]==ROW_SHA and
         old[0]["registered_evidence_level"]=="COMPLETE_SOURCE_SPECIFIC" and
         old[0]["phase_turn_law"]=={"offset":"0","rate":"1/8"} and
         old[0]["original_source_piece_edges"]==["0","1","2"],
         "V2_EXISTING_SOURCE_WITNESS")
    return matches[0]


def prior_signed_event(w,v):
    """Fail closed unless the already accepted V2 signed certificate subsumes this claim."""
    need(type(w) is dict and type(w.get("source_cases")) is list and
         len(w["source_cases"]) == 15, "PINNED_PRIOR_SIGNED_REPORT_SCHEMA")
    matches=[x for x in w["source_cases"] if x.get("case_id")==CASE]
    need(len(matches)==1, "PRIOR_SIGNED_CASE_MISSING")
    old=matches[0]
    need(old.get("source_sha256")==SHA and old.get("original_row_sha256")==ROW_SHA and
         old.get("source_interval")==["0","2"] and
         old.get("original_source_piece_edges")==["0","1","2"] and
         old.get("phase_turn_law")=={"offset":"0","rate":"1/8"} and
         old.get("status")=="COMPLETE_PINNED_ORIGINAL_SOURCE_PROOF_RESEARCH_ONLY" and
         old.get("complete_closed_zero_set_kind")=="FINITE" and
         type(old.get("complete_closed_root_count")) is int and
         old["complete_closed_root_count"]==1 and
         old.get("complete_original_source_zero_set") is True and
         old.get("historical_disposition_changed") is False,
         "PRIOR_SIGNED_CUSTODY_OR_COMPLETENESS")
    roots=old.get("ordered_root_events")
    need(type(roots) is list and len(roots)==1 and type(roots[0]) is dict,
         "PRIOR_ORDERED_EVENTS")
    root=roots[0]
    need(root.get("root_ref")=="ROOT_1" and
         type(root.get("source_span_index")) is int and root["source_span_index"]==0 and
         root.get("source_interval")==["0","1"] and
         root.get("strict_bracket")==["17/64","9/32"] and
         type(root.get("left_sign")) is int and root["left_sign"]==-1 and
         type(root.get("right_sign")) is int and root["right_sign"]==1 and
         type(root.get("smooth_multiplicity")) is int and root["smooth_multiplicity"]==1 and
         type(root.get("derivative_sign")) is int and root["derivative_sign"]==1,
         "PRIOR_SIGNED_ROOT_ALREADY_CERTIFIED")
    need(old.get("maximal_open_physical_sign_cells")==[
        {"left":"ORIGINAL_SOURCE_START","right":"ROOT_1","sign":-1},
        {"left":"ROOT_1","right":"ORIGINAL_SOURCE_END","sign":1}] and
         old.get("exterior_endpoint_signs")==[-1,1] and
         old.get("true_source_knots")==[{
             "position":"1","channel_continuous":True,"left_sign":1,"right_sign":1,
             "is_physical_zero":False,"is_physical_event":False}],
         "PRIOR_SIGN_CELLS_OR_KNOT_ALREADY_CERTIFIED")
    spans=old.get("original_spans")
    need(type(spans) is list and len(spans)==2 and
         spans[1].get("source_span_index")==1 and
         spans[1].get("interval_proof",{}).get("partition")==[
             {"kind":"NO_ROOT","interval":["1","2"],"sign":1}],
         "PRIOR_RIGHT_SPAN_ALREADY_CERTIFIED")
    producers=v.get("producer_registry")
    need(type(producers) is list, "V2_PRODUCER_REGISTRY")
    matches=[p for p in producers if p.get("producer")=="ordered_children"]
    need(len(matches)==1 and
         matches[0].get("code_git_blob")==ORDERED_PRODUCER_BLOB and
         matches[0].get("saved_report",{}).get("git_blob")==ORDERED_WITNESS_BLOB and
         CASE in matches[0].get("selected_original_source_ids",[]),
         "PRIOR_V2_PRODUCER_PIN")
    rows=[x for x in v["source_cases"] if x["case_id"]==CASE]
    need(len(rows)==1 and
         rows[0].get("evidence",{}).get("producer")=="ordered_children" and
         rows[0].get("evidence",{}).get("producer_git_blob")==ORDERED_PRODUCER_BLOB and
         rows[0].get("registered_evidence_level")=="COMPLETE_SOURCE_SPECIFIC",
         "PRIOR_V2_SIGNED_OWNERSHIP")
    # The pinned old root bracket is strictly inside this alternate (0,1/2).
    need(Q(0) < Q("17/64") < Q("9/32") < Q(1,2),
         "PRIOR_ROOT_BRACKET_NOT_STRONGER")

def reject(fn,*args):
    try:
        fn(*args)
    except Refused:
        return
    raise AssertionError("UNPROVED_ADVERSARY_ADMITTED")

def tests(c,v,row,r,w):
    n=0
    for path,alteration in [
        (["phase_turn_offset"],"1/2"),(["phase_turn_rate"],"1/12"),
        (["parameter_hi"],"1"),(["cos_splines","1","degree"],2),
        (["cos_splines","1","controls"],["0","0","0","0"]),
        (["cos_splines","1","controls"],["-1/2","1/2","1/2","2/3"]),
        (["sin_splines","1","controls"],["0","0"]), # identity-zero candidate
        (["sin_splines","1","controls"],["-1","-1"]),
        (["cos_splines","1","knots"],["0","1","2"]),
        (["cos_splines","1","controls"],["-1/2","1/2","1/2",True])
    ]:
        changed=deepcopy(row["spec"])
        cur=changed
        for k in path[:-1]:
            cur=cur[k]
        cur[path[-1]]=alteration
        reject(prove,changed)
        n+=1
    for field,alteration in [
        ("root_kind","DOUBLE_TANGENCY"),("root_kind","IDENTITY_ZERO"),
        ("root_kind","ENDPOINT_ROOT"),("root_multiplicity",2),
        ("implicit_root_open",["0","1/1208925819614629174706176"]),
        ("root_count",2),("right_piece_nonmonotone",False),
        ("new_unique_ordered_source_closures",1),
        ("new_generic_event_theorem",True),
        ("preexisting_v2_signed_event_witness_git_blob","0"*40),
        ("right_piece_root_count",1),("accepted_historical_delta",True),
        ("v54_missing_ordered",True),("production_authorized",True),
        ("mc_b","ESTABLISHED"),("supported_operations",25)
    ]:
        changed=deepcopy(r)
        changed[field]=alteration
        reject(verify_receipt,changed)
        n+=1
    # Novelty guard must reject loss or sign inversion of the already-complete
    # V2 signed event, knot, or root-free second span.
    for mutation in ("missing_root", "inverted_left_sign"):
        changed=deepcopy(w)
        old_case=next(x for x in changed["source_cases"] if x["case_id"]==CASE)
        if mutation=="missing_root":
            old_case["ordered_root_events"]=[]
        else:
            old_case["ordered_root_events"][0]["left_sign"]=1
        reject(prior_signed_event,changed,v)
        n+=1
    for field,value in [
        ("maximal_open_physical_sign_cells",[]),
        ("true_source_knots",[]),
        ("original_spans",[])
    ]:
        changed=deepcopy(w)
        old_case=next(x for x in changed["source_cases"] if x["case_id"]==CASE)
        old_case[field]=value
        reject(prior_signed_event,changed,v)
        n+=1
    old=deepcopy(v)
    for x in old["source_cases"]:
        if x["case_id"]==CASE:
            x["source_sha256"]="0"*64
    reject(census,c,old)
    n+=1
    changed=deepcopy(c)
    changed["cases"][0]["expected"]["v54_disposition"]="BLOCKED"
    reject(census,changed,v)
    n+=1
    for data in [b'{"a":1,"a":2}',b'{"a":NaN}',b'{"a":1.0}',
                 b'{"a":1e999}',b'{"a":'+b'9'*100+b'}']:
        reject(decode,data,True)
        n+=1
    with tempfile.TemporaryDirectory() as td:
        path=Path(td)/"bad.json"
        path.write_bytes(b"x"*30001)
        reject(read,path,30000)
        n+=1
        path.write_bytes(b"{}")
        reject(read,path,300000,V54_BLOB)
        n+=1
    return n

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--contract",action="store_true")
    p.add_argument("--self-test",action="store_true")
    opts=p.parse_args()
    c=decode(read(BASE/"pb00701-finite-owner-corpus-v54.json",300000,V54_BLOB))
    v=decode(read(BASE/"pb00701-post-v54-evidence-reconciliation-v2.json",200000,V2_BLOB))
    row=census(c,v)
    w=decode(read(BASE/"pb00701-ordered-child-source-completion-witness.json",
                  150000,ORDERED_WITNESS_BLOB))
    read(BASE/"pb00701_ordered_child_source_completion.py",
         60000,ORDERED_PRODUCER_BLOB)
    prior_signed_event(w,v)
    r=decode(read(BASE/"pb00701-v9-two-span-sign-20261106.json",30000),True)
    verify_receipt(r)
    print("SOURCE",CASE,"SHA256",SHA)
    print("ALTERNATE PROOF: ONE SIMPLE ROOT IN (0,1/2), NEGATIVE THEN POSITIVE")
    print("PREEXISTING V2 SIGNED ROOT BRACKET (17/64,9/32), CELLS AND KNOT VERIFIED")
    print("V54 FROZEN 121/20/30; EXISTING V2 50; ACCEPTED DELTA ZERO")
    if opts.self_test:
        print("ADVERSARIAL_REFUSALS",tests(c,v,row,r,w))
    print("MODEL ONLY; PB-007 OPEN; MC-B/MC-1 NOT_ESTABLISHED")

if __name__=="__main__":
    try:
        main()
    except Refused as exc:
        raise SystemExit("REFUSED_NONTRUTH: "+str(exc)) from exc
