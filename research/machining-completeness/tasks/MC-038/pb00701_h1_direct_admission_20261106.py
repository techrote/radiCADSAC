#!/usr/bin/env python3
"""Read-only exact frozen source-grammar applicability challenge for #439.

This only proves necessary direct admission conditions; NOT a physical event
theorem, general impossibility, source closure, or MC-B/MC-1 acceptance.
"""
import argparse
import copy
import hashlib
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE=Path(__file__).resolve().parent
V54=HERE/"pb00701-finite-owner-corpus-v54.json"
V2=HERE/"pb00701-post-v54-evidence-reconciliation-v2.json"
RECEIPT=HERE/"pb00701-h1-direct-admission-20261106.json"
V54_BLOB="5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB="e52d3baf3692a011cf86234eeaa992ef407d99fd"
THEOREM_HEAD="e3264629c967189f5b843bbb7e73b80df2f3c56c"
FIELDS={"grammar","source_parameter_id","parameter_lo","parameter_hi",
        "phase_turn_offset","phase_turn_rate","cos_splines","sin_splines"}
MISSING="BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"
ADMITTED={
 "harvested:verify_pb00701_v10:f8b83299bd55",
 "harvested:verify_pb00701_v9:4e7b85fa122a",
 "composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail0"
}

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode("ascii")

def read_pinned(path,pin):
    with path.open("rb") as f:
        data=f.read(400001)
    assert len(data)<=400000, "JSON_BYTE_BUDGET"
    h=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    assert h==pin, "SOURCE_BLOB_MISMATCH"
    return json.loads(data)

def number(s):
    assert type(s) is str and 0<len(s)<=128
    value=Q(s)
    assert str(value)==s, "NONCANONICAL_RATIONAL"
    return value

def pieces(item,edges):
    if type(item) is not dict or set(item)!={"degree","knots","controls"}:
        return None
    degree=item["degree"]
    if type(degree) is not int or degree not in (0,1):return None
    knots=edges if degree==0 else [x for e in edges for x in (e,e)]
    if item["knots"]!=knots or type(item["controls"]) is not list:return None
    n=len(edges)-1
    if len(item["controls"])!=n*(degree+1):return None
    try: controls=[number(x) for x in item["controls"]]
    except (AssertionError,ValueError,TypeError,ZeroDivisionError):return None
    p=[(x,x) for x in controls] if degree==0 else [
      (controls[2*i],controls[2*i+1]) for i in range(n)]
    if n==2 and p[0][1]!=p[1][0]:return None
    return p

def classify(s):
    if type(s) is not dict or set(s)!=FIELDS:
        return "FIELD_MISMATCH"
    if (s["grammar"]!="RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE"
        or s["source_parameter_id"]!="source-time-t"
        or s["parameter_lo"]!="0" or s["parameter_hi"] not in ("1","2")):
        return "TIME_OR_GRAMMAR"
    if s["phase_turn_offset"]!="0" or s["phase_turn_rate"]!="1/8":
        return "PHASE_MISMATCH"
    co,si=s["cos_splines"],s["sin_splines"]
    if (type(co) is not dict or type(si) is not dict or "1" not in co
        or not set(co).issubset({"0","1"}) or set(si)!={"1"}):
        return "HARMONIC_MISMATCH"
    edges=["0","1"] if s["parameter_hi"]=="1" else ["0","1","2"]
    if "0" in co:
        p=pieces(co["0"],edges)
        if p is None or not all(a==b==0 for a,b in p):
            return "H0_NONZERO_OR_STRUCTURE"
    if pieces(co["1"],edges) is None or pieces(si["1"],edges) is None:
        return "H1_KNOT_OR_AFFINITY"
    return "STRUCTURALLY_ELIGIBLE"

def audit():
    corpus,prior=read_pinned(V54,V54_BLOB),read_pinned(V2,V2_BLOB)
    rows=corpus["cases"]
    assert len(rows)==len({r["id"] for r in rows})==121
    blocked={r["id"] for r in rows if r["expected"]["v54_disposition"]=="BLOCKED"}
    missing={r["id"] for r in rows if r["expected"]["v54_disposition"]==MISSING}
    assert len(blocked)==20 and len(missing)==30 and not blocked & missing
    v2={r["case_id"]:r for r in prior["source_cases"]}
    assert len(v2)==50 and set(v2)==blocked|missing
    for row in rows:
        if row["id"] in v2:
            existing=v2[row["id"]]
            assert existing["source_sha256"]==hashlib.sha256(canonical(row["spec"])).hexdigest()
            assert existing["evidence"]["original_row_sha256"]==hashlib.sha256(canonical(row)).hexdigest()
            assert existing["registered_evidence_level"]=="COMPLETE_SOURCE_SPECIFIC"
            assert existing["origin"]==row["origin"]
    first=Counter(classify(row["spec"]) for row in rows)
    assert first=={
        "STRUCTURALLY_ELIGIBLE":3,"PHASE_MISMATCH":91,"TIME_OR_GRAMMAR":24,
        "HARMONIC_MISMATCH":1,"FIELD_MISMATCH":1,
        "H0_NONZERO_OR_STRUCTURE":1},first
    selected=[row for row in rows if classify(row["spec"])=="STRUCTURALLY_ELIGIBLE"]
    assert {r["id"] for r in selected}==ADMITTED
    assert len([r for r in selected if r["id"] in v2])==2
    # Independent positive/negative source-preserving mutation challenges.
    s=selected[0]["spec"]
    assert classify(s)=="STRUCTURALLY_ELIGIBLE"
    for kind,result in [
        ("phase","PHASE_MISMATCH"),("harmonic","HARMONIC_MISMATCH"),
        ("knot","H1_KNOT_OR_AFFINITY"),("fields","FIELD_MISMATCH"),
        ("H0","H0_NONZERO_OR_STRUCTURE")]:
        alt=copy.deepcopy(s)
        if kind=="phase":alt["phase_turn_rate"]="1/9"
        if kind=="harmonic":alt["cos_splines"]["2"]=copy.deepcopy(alt["cos_splines"]["1"])
        if kind=="knot":alt["cos_splines"]["1"]["knots"][1]="1/2"
        if kind=="fields":alt["parameter_projection"]="path-length"
        if kind=="H0":alt["cos_splines"]["0"]={
           "degree":0,"knots":["0","1"],"controls":["1"]}
        assert classify(alt)==result,(kind,classify(alt))
    result={
        "schema":"radicadsac-mc038-h1-direct-admission/1.0",
        "evidence_class":"DETERMINISTIC_MODEL","theorem_head":THEOREM_HEAD,
        "source_v54_git_blob":V54_BLOB,"source_v2_git_blob":V2_BLOB,
        "method":"EXACT_NECESSARY_SOURCE_GRAMMAR_DIRECT_APPLICATION_ONLY",
        "first_necessary_exclusion_counts":dict(sorted(first.items())),
        "structurally_eligible_originals":[{
            "id":r["id"],"v54_disposition":r["expected"]["v54_disposition"],
            "original_source_sha256":hashlib.sha256(canonical(r["spec"])).hexdigest(),
            "existing_complete_v2_witness":r["id"] in v2
        } for r in selected],
        "frozen_total":121,"historical_unresolved_total":50,
        "historical_missing_ordered":30,"historical_refusals":20,
        "structurally_eligible_total":3,"excluded_total":118,
        "historical_unresolved_structurally_eligible":2,
        "historical_unresolved_directly_excluded":48,
        "historical_complete_v2_witnesses":50,
        "before_after":{name:{"before":v,"after":v,"delta":0} for name,v in [
          ("frozen_originals",121),("route_refusals",20),
          ("missing_ordered_premises",30),("complete_v2_witnesses",50)]},
        "newly_closed_historical_ids":[],"required_pb_po_discharges":0,
        "general_event_impossibility_claimed":False,
        "transformed_source_admission_ruled_out":False,
        "pb00701_established":False,"mc_b_established":False,
        "mc1_established":False,"native_geometry_qualified":False,
        "engineering_step_qualified":False,"production_authorized":False,
        "supported_operations_unchanged":26}
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--contract",action="store_true")
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    actual=audit()
    if args.contract:
        receipt=read_pinned_untrusted(RECEIPT)
        assert canonical(receipt)==canonical(actual),"CERTIFICATE_RECEIPT_MISMATCH"
    print(json.dumps(actual if not args.contract else {
      "status":"PASS","structural_total":3,"unresolved_directly_excluded":48,
      "historical_delta":0,"proof_obligations_discharged":0},sort_keys=True))

def read_pinned_untrusted(path):
    with path.open("rb") as f:raw=f.read(400001)
    assert len(raw)<=400000,"RECEIPT_BYTE_BUDGET"
    def pairs(kv):
        o={}
        for k,v in kv:
            assert k not in o,"DUPLICATE_JSON_KEY"
            o[k]=v
        return o
    return json.loads(raw,object_pairs_hook=pairs)

if __name__=="__main__":main()
