#!/usr/bin/env python3
"""Bounded original-source odd multiplier/ramp physical-event theorem.

All admissions use exact rational original-spline control identities. Root
coordinates are exact implicit unique-root brackets, never numerical scans.
Evidence class DETERMINISTIC_MODEL, not an accepted PB/PO/MC gate.
"""
import argparse
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

DIR=Path(__file__).resolve().parent
FROZEN=DIR/"pb00701-finite-owner-corpus-v54.json"
V2=DIR/"pb00701-post-v54-evidence-reconciliation-v2.json"
FROZEN_BLOB="5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB="e52d3baf3692a011cf86234eeaa992ef407d99fd"
PASS="EXACT_ORIGINAL_ODD_MULTIPLIER_RAMP_RESEARCH"
ANCHORS={
"composite:PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC:tail100":("a7131bea021c5c71d0da2682cd6d4c1a982e8c86196c818ad3f69a926afda2e5","094b31ab55141488e39589ab6e0deda02b21066f06ba8568110609a23cd0a003"),
"composite:PB00701_V14_EXACT_STRICT_DOMINANCE_MULTITERM_MULTIPLIER:tail100":("bd10ad1d9503335b2d7f745c09805b82a421b8db7beea67329cf33d0c9d78ff2","1940ec5f6aafb641a25fcda3f8941ff7dd9f2afc2bf13056da6920159c3f0e18"),
"composite:PB00701_V15_EXACT_FINITE_STRICT_DOMINANCE_MULTIPLIER:tail100":("8e41009417dd65f9a47a04b492dd9a91b88a7682f12f45305ce64ac38dffd7b7","3954e79fceefbcd6e4b5932197f0314dbd4b90891b8fbad8410f9572f746725d"),
}

class Refused(ValueError):
    pass

def need(cond, reason):
    if not cond: raise Refused(reason)

def canonical(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()

def sha(v):
    return hashlib.sha256(canonical(v)).hexdigest()

def blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()

def q(s):
    need(type(s) is str and 0<len(s)<=128,"BAD_RATIONAL")
    try: v=Q(s)
    except (ValueError,TypeError,ZeroDivisionError,OverflowError) as e:
        raise Refused("BAD_RATIONAL") from e
    need(str(v)==s,"NONCANONICAL_RATIONAL")
    need(max(abs(v.numerator).bit_length(),v.denominator.bit_length())<=256,"RESOURCE_INPUT_BITS")
    return v

def small(*values):
    need(all(max(abs(x.numerator).bit_length(),x.denominator.bit_length())<=1024 for x in values),"RESOURCE_DERIVED_BITS")

def spline(x, harmonic):
    need(type(x) is dict and set(x)=={"degree","knots","controls"},"SPLINE_FIELDS")
    need(type(x["degree"]) is int and x["degree"]==1,"DEGREE")
    need(type(x["knots"]) is list and type(x["controls"]) is list,"SPLINE_LISTS")
    need(tuple(map(q,x["knots"]))==(Q(0),Q(0),Q(1),Q(1),Q(2),Q(2)),"TRUE_SOURCE_KNOTS")
    z=tuple(map(q,x["controls"]))
    need(len(z)==4,"CONTROLS")
    if harmonic: need(z[1]==z[2]==z[3],"TAIL_NOT_CONSTANT_OR_CONTINUOUS")
    return z

def prove(spec):
    need(type(spec) is dict and set(spec)=={"grammar","source_parameter_id","parameter_lo","parameter_hi","phase_turn_offset","phase_turn_rate","cos_splines","sin_splines"},"SPEC_FIELDS")
    need(len(canonical(spec))<=8192,"RESOURCE_SOURCE_BYTES")
    need(spec["grammar"]=="RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE" and spec["source_parameter_id"]=="source-time-t","SOURCE_TIME_GRAMMAR")
    need(tuple(q(spec[k]) for k in ("parameter_lo","parameter_hi","phase_turn_offset","phase_turn_rate"))==(Q(0),Q(2),Q(0),Q(1,4)),"SOURCE_PHASE_TIME")
    cs,ss=spec["cos_splines"],spec["sin_splines"]
    need(type(cs) is dict and type(ss) is dict,"CHANNEL_FIELDS")
    n=len(cs)-2
    need(1<=n<=4,"RESOURCE_HARMONIC_COUNT")
    hs=[str(2*j+1) for j in range(n+1)]
    need(set(cs)=={"0",*hs} and set(ss)==set(hs),"EXACT_ODD_HARMONICS")
    c0=spline(cs["0"],False)
    need(c0[:3]==(Q(0),Q(0),Q(0)),"H0_PREFIX_KNOT")
    m=c0[3]
    c={int(h):spline(cs[h],True) for h in hs}
    s={int(h):spline(ss[h],True) for h in hs}
    # Derive even multiplier exclusively from actual original first-span
    # cosine coefficients. Independently check every sine AND cosine control.
    L=[Q(0)]*(n+1)
    A0,A1=Q(-1,3),Q(2,3)
    B0,B1=Q(2,3),Q(-1,3)
    L[n]=2*c[2*n+1][0]/A0
    for j in range(n-1,0,-1):
        L[j]=2*c[2*j+1][0]/A0-L[j+1]
    L[0]=c[1][0]/A0-L[1]/2
    small(*L)
    margin=L[0]-sum(map(abs,L[1:]))
    need(L[-1]!=0 and margin>0,"NONZERO_MULTIPLIER_MARGIN_NOT_PROVED")
    for j in range(n+1):
        h=2*j+1
        if j==0:
            coef_c,coef_s=L[0]+L[1]/2,L[0]-L[1]/2
        else:
            nxt=L[j+1] if j<n else Q(0)
            coef_c,coef_s=(L[j]+nxt)/2,(L[j]-nxt)/2
        need(c[h]==(coef_c*A0,coef_c*A1,coef_c*A1,coef_c*A1)
             and s[h]==(coef_s*B0,coef_s*B1,coef_s*B1,coef_s*B1),
             "ORIGINAL_COEFFICIENTWISE_FACTOR_NOT_PROVED")
    # Strict analytic bound, not a sampled derivative certificate:
    # |G'| <= (pi/2) sum_h h(|a_h|+|b_h|)
    #       < (11/7) sum_h h(|a_h|+|b_h|), since pi<22/7.
    T=sum((Q(h)*(abs(c[h][1])+abs(s[h][1])) for h in c),Q(0))
    D=Q(11,7)*T
    small(T,D,m)
    need(m>D,"STRICT_TAIL_DERIVATIVE_NOT_PROVED")
    f0=sum((c[h][0] for h in c),Q(0))
    f1=sum((s[h][1]*((-1)**((h-1)//2)) for h in s),Q(0))
    f2=m-sum((c[h][1] for h in c),Q(0))
    need(f0<0 and f1<0 and f2>0,"EXACT_ENDPOINT_SIGNS_NOT_PROVED")
    # Positive M preserves physical carrier signs on [0,1]. Carrier R
    # has a unique simple root in (1/6,1/4) by the increasing tan ratio
    # vs decreasing (1/3-t)/(2/3-t). Exact bounds require only
    # sqrt(3)>5/3 and sqrt(2)>6/5; reflection R(t)=R(1-t).
    need(Q(3)>Q(25,9) and Q(2)>Q(36,25),"ROOT_BRACKET_LEMMA")
    H=sum((abs(c[h][1])+abs(s[h][1]) for h in c),Q(0))
    small(f0,f1,f2,H)
    return {
      "status":PASS,"evidence_class":"DETERMINISTIC_MODEL","source_sha256":sha(spec),
      "source_time":["0","2"],"source_parameter_id":"source-time-t",
      "true_knot":"1","phase_turns":["0","1/4"],
      "strict_multiplier_positive_margin":str(margin),
      "even_cosine_multiplier":list(map(str,L)),
      "tail_affine_slope":str(m),"tail_derivative_upper_rational":str(D),
      "tail_amplitude_abs_bound":str(H),
      "exact_F0":str(f0),"exact_F1":str(f1),"exact_F2":str(f2),
      "physical_roots":[
         {"id":"r1","bracket":["1/6","1/4"],"order":1,"sides":["-","+"]},
         {"id":"r2","bracket":["3/4","5/6"],"identity":"r2=1-r1","order":1,"sides":["+","-"]},
         {"id":"r3","bracket":["1","2"],"order":1,"sides":["-","+"]}],
      "physical_sign_cells":["-","+","-","+"],
      "knot_zero":False,"endpoint_zeros":[],"identity_zero_intervals":[],
      "whole_original_event_completeness_for_admitted_grammar":True,
      "historical_status_modified":False,"newly_closed_historical_case_ids":[],
      "pb00701_certified":False,"mc_b_established":False,"mc1_established":False,
      "native_qualified":False,"engineering_step_qualified":False,
      "production_authorized":False}

def attempt(source):
    try: return prove(source)
    except (Refused,KeyError,TypeError,ValueError,ArithmeticError,MemoryError,RecursionError) as e:
        why=str(e) if isinstance(e,Refused) else type(e).__name__
        return {"status":"RESOURCE_REFUSAL" if why.startswith("RESOURCE") or isinstance(e,(MemoryError,RecursionError)) else "BLOCKED",
                "reason":why,"is_truth_value":False,"pb00701_certified":False,
                "mc_b_established":False,"production_authorized":False}

def validate_receipt(source, candidate):
    actual=attempt(source)
    if actual["status"]!=PASS: return actual
    try:
        need(type(candidate) is dict and canonical(candidate)==canonical(actual),"FORGED_OR_STALE_RECEIPT")
    except (Refused,TypeError,ValueError):
        return {"status":"BLOCKED","reason":"FORGED_OR_STALE_RECEIPT","is_truth_value":False}
    return actual

def close_knot_bracket(source, epsilon):
    r=attempt(source)
    need(r["status"]==PASS,"SOURCE_NOT_CERTIFIED")
    e=q(epsilon)
    need(Q(0)<e<Q(1),"BAD_CLOSE_ROOT_INTERVAL")
    need(Q(r["tail_affine_slope"])*e>Q(r["tail_amplitude_abs_bound"]),
         "CLOSE_ROOT_BRACKET_NOT_PROVED")
    return ["1",str(1+e)]

def census():
    a,b=FROZEN.read_bytes(),V2.read_bytes()
    need(blob(a)==FROZEN_BLOB and blob(b)==V2_BLOB,"FROZEN_GIT_BLOBS_CHANGED")
    rows=json.loads(a)["cases"]; registered=json.loads(b)["source_cases"]
    rr={x["id"]:x for x in rows};er={x["case_id"]:x for x in registered}
    need(len(rows)==len(rr)==121 and len(registered)==len(er)==50,"CASE_ID_DENOMINATOR_CHANGED")
    refused={r["id"] for r in rows if r["expected"]["v54_disposition"]=="BLOCKED"}
    missing={r["id"] for r in rows if r["expected"]["v54_disposition"]=="BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"}
    need(len(refused)==20 and len(missing)==30 and refused|missing==set(er),"HISTORIC_CENSUS_CHANGED")
    for k,e in er.items():
        row=rr[k];spec=row["spec"]
        need(e["source_sha256"]==sha(spec) and e["original_row_sha256"]==sha(row)
             and e["origin"]==row["origin"]
             and e["source_parameter_id"]==spec["source_parameter_id"]
             and e["source_interval"]==[spec["parameter_lo"],spec["parameter_hi"]]
             and e["phase_turn_law"]=={"offset":spec["phase_turn_offset"],"rate":spec["phase_turn_rate"]}
             and e["historical_v54_disposition"]==row["expected"]["v54_disposition"]
             and e["registered_evidence_level"]=="COMPLETE_SOURCE_SPECIFIC"
             and e["evidence"]["complete_original_source_zero_set"] is True,
             "SOURCE_PROVENANCE_OR_V2_WITNESS_CHANGED")
    accepted={}
    for k,(source_hash,row_hash) in ANCHORS.items():
        row=rr[k]
        need(sha(row["spec"])==source_hash and sha(row)==row_hash,"FROZEN_ANCHOR_CHANGED")
        need(row["expected"]["v54_disposition"]=="BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE","HISTORICAL_STATUS_CHANGED")
        result=attempt(row["spec"])
        need(result["status"]==PASS and result["source_sha256"]==source_hash,"EXACT_ORIGINAL_REFUSED")
        need(validate_receipt(row["spec"],result)==result,"VALID_RECEIPT_REFUSED")
        accepted[k]=result
    return {"population":{"original_sources":121,"route_refusals":20,"missing_ordered":30,
                          "previous_complete_source_witnesses":50},
            "newly_closed_historical_case_ids":[],"original_cases":accepted}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--contract",action="store_true")
    p.add_argument("--source")
    args=p.parse_args()
    if args.contract:
        result=census()
        print(json.dumps({"status":"PASS",**result},sort_keys=True))
        return 0
    if args.source:
        out=attempt(json.loads(Path(args.source).read_text()))
        print(json.dumps(out,sort_keys=True,indent=2))
        return 0 if out["status"]==PASS else 1
    p.print_help()
    return 2

if __name__=="__main__":
    raise SystemExit(main())
