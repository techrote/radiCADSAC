#!/usr/bin/env python3
"""Independent frozen-source V12 falsifier for *direct* PR #441 quarter-grid admission.
Deterministic-model evidence only. No generic PB/PO discharge.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
V54 = HERE / "pb00701-finite-owner-corpus-v54.json"
V2 = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
RECEIPT = HERE / "pb00701-v12-phasegrid-admission-20261106.json"
V54_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
V12 = "composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail0"
V10 = "composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail0"
V12_SOURCE = "ee15e947924b45640dd16634247a476bb230fdc145fef94407d9a7c219928cd5"
V12_ROW = "d0acef7c69cb8ac1ba128b988e83817a91feff78509dd18007d0e56a506336c3"
PARENT_441 = "b1774a01898e423a1e3f62d0b0f881f65156ff23"
GRAMMAR = "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE"

class Refusal(ValueError):
    pass

def check(ok, label):
    if not ok:
        raise Refusal(label)

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",",":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")

def git_blob(buf):
    return hashlib.sha1(b"blob " + str(len(buf)).encode() + b"\0" + buf).hexdigest()

def unique_pairs(pairs):
    d = {}
    for k,v in pairs:
        check(k not in d, "DUPLICATE_JSON_KEY")
        d[k]=v
    return d

def parse_json(buf):
    check(len(buf)<=400000,"BYTE_BUDGET")
    def parse_int(s):
        check(len(s)<=12,"INTEGER_TOKEN_BUDGET")
        return int(s)
    def reject_number(_):
        raise Refusal("FLOAT_OR_NONFINITE")
    try:
        return json.loads(buf.decode("utf-8"),object_pairs_hook=unique_pairs,
                          parse_int=parse_int, parse_float=reject_number,
                          parse_constant=reject_number)
    except Refusal:
        raise
    except (ValueError,UnicodeError,RecursionError,OverflowError) as e:
        raise Refusal("JSON_REFUSED") from e

def pinned(path,blob):
    with path.open("rb") as fd:
        buf=fd.read(400001)
    check(len(buf)<=400000,"BYTE_BUDGET")
    check(git_blob(buf)==blob,"IMMUTABLE_BLOB_DRIFT")
    return parse_json(buf)

def rational(s):
    check(type(s) is str and 0<len(s)<=128, "RATIONAL_TOKEN")
    try:
        v=Q(s)
    except (ValueError,ZeroDivisionError,OverflowError) as e:
        raise Refusal("BAD_RATIONAL") from e
    check(str(v)==s and v.numerator.bit_length()<=512 and
          v.denominator.bit_length()<=512, "RATIONAL_CANON_OR_BUDGET")
    return v

def spline(src,edges):
    check(type(src) is dict and set(src)=={"degree","knots","controls"},
          "SPLINE_SHAPE")
    deg=src["degree"]
    check(type(deg) is int and deg in (0,1),"NOT_AFFINE")
    ref=[str(e) for e in edges] if deg==0 else [str(e) for e in edges for _ in range(2)]
    check(src["knots"]==ref,"KNOT_SEQUENCE")
    cs=src["controls"]
    check(type(cs) is list and len(cs)==(len(edges)-1)*(deg+1),
          "CONTROLS_SHAPE")
    vals=[rational(x) for x in cs]
    pieces=([(v,v) for v in vals] if deg==0 else
            [(vals[2*i],vals[2*i+1]) for i in range(len(edges)-1)])
    check(all(pieces[i][1]==pieces[i+1][0] for i in range(len(pieces)-1)),
          "DISCONTINUOUS_SOURCE_KNOT")
    return pieces

def structure(spec):
    keys={"grammar","source_parameter_id","parameter_lo","parameter_hi",
          "phase_turn_offset","phase_turn_rate","cos_splines","sin_splines"}
    check(type(spec) is dict and set(spec)==keys,"SOURCE_FIELDS")
    check(spec["grammar"]==GRAMMAR and
          spec["source_parameter_id"]=="source-time-t" and
          spec["parameter_lo"]=="0" and spec["parameter_hi"] in ("1","2"),
          "ORIGINAL_SOURCE_TIME")
    edges=[Q(0),Q(1)] if spec["parameter_hi"]=="1" else [Q(0),Q(1),Q(2)]
    co,si=spec["cos_splines"],spec["sin_splines"]
    check(type(co) is dict and type(si) is dict and "1" in co and
          set(co)<=set(("0","1")) and set(si)=={"1"},"HARMONIC_GRAMMAR")
    phase0=rational(spec["phase_turn_offset"])
    rate=rational(spec["phase_turn_rate"])
    check(rate!=0 and abs(rate)<=4,"RATE")
    check(all((4*(phase0+rate*t)).denominator==1 for t in edges),
          "ORIGINAL_KNOT_NOT_QUARTER_GRID")
    num=abs(int(4*(phase0+rate*edges[-1]))-int(4*phase0))
    check(0<num<=128,"QUARTER_GRID_CELL_BUDGET")
    C=spline(co["1"],edges)
    S=spline(si["1"],edges)
    if "0" in co:
        H=spline(co["0"],edges)
        check(all(x==y==0 for x,y in H),"NONZERO_H0")
    return edges,phase0,rate,C,S,num

def value(piece,x,lo,hi):
    a,b=piece
    return a+(b-a)*(x-lo)/(hi-lo)

def exact_local(C0,C1,S0,S1,turn):
    # Independent derivation: q is a convex quadratic, W is constant.
    dc,ds=C1-C0,S1-S0
    a=dc*dc+ds*ds
    b=C0*dc+S0*ds
    q0=C0*C0+S0*S0
    q1=C1*C1+S1*S1
    small,large=min(q0,q1),max(q0,q1)
    if a and 0 < -b/a < 1:
        small=min(small,q0-b*b/a)
    check(small>0,"SHARED_H1_ZERO")
    W=C0*ds-S0*dc
    wl,wu=sorted((W/small,W/large))
    theta_lo,theta_hi=sorted((6*turn,Q(44,7)*turn))
    lower,upper=theta_lo-wu,theta_hi-wl
    check(lower>0 or upper<0,"DELTA_DERIVATIVE_SIGN_UNPROVED")
    magnitude=max(abs(lower),abs(upper))
    check(magnitude<3,"ANGULAR_DRIFT_NOT_CERTIFIED_BELOW_PI")
    return small,large,W,lower,upper

def certify(spec):
    edges,off,rate,C,S,n=structure(spec)
    start=int(4*(off+rate*edges[0]))
    direction=1 if rate>0 else -1
    indices=[start+direction*j for j in range(n+1)]
    times=[(Q(k,4)-off)/rate for k in indices]
    check(times[0]==edges[0] and times[-1]==edges[-1],"TIME_GRID")
    signs=[]
    for t,k in zip(times,indices):
        piece=next(i for i in range(len(edges)-1) if edges[i]<=t<=edges[i+1])
        c=value(C[piece],t,edges[piece],edges[piece+1])
        s=value(S[piece],t,edges[piece],edges[piece+1])
        f=(c,s,-c,-s)[k%4]
        check(f!=0,"PHASE_NODE_ZERO")
        signs.append(1 if f>0 else -1)
    roots=0
    for i in range(n):
        midpoint=(times[i]+times[i+1])/2
        j=next(k for k in range(len(edges)-1) if edges[k]<=midpoint<edges[k+1])
        c0=value(C[j],times[i],edges[j],edges[j+1])
        c1=value(C[j],times[i+1],edges[j],edges[j+1])
        s0=value(S[j],times[i],edges[j],edges[j+1])
        s1=value(S[j],times[i+1],edges[j],edges[j+1])
        exact_local(c0,c1,s0,s1,rate*(times[i+1]-times[i]))
        roots+=int(signs[i]!=signs[i+1])
    return roots

def route(spec):
    try:
        return "ADMITTED",certify(spec)
    except Refusal as exc:
        return "REFUSED",str(exc)

def original_proof(row):
    s=row["spec"]
    check(s["phase_turn_offset"]=="0" and s["phase_turn_rate"]=="1/4" and
          s["parameter_hi"]=="2","V12_TIME_OR_PHASE")
    edges,off,rate,C,S,n=structure(s)
    check(edges==[0,1,2] and C==[(Q(-1,3),Q(2,3)),(Q(2,3),Q(2,3))] and
          S==[(Q(2,3),Q(-1,3)),(Q(-1,3),Q(-1,3))],
          "V12_COEFFICIENT_OR_KNOT_DRIFT")
    qmin,qmax,W=Q(1,18),Q(5,9),Q(-1,3)
    # The first exact quarter-turn cell [0,1] has these extrema.
    a,b=C[0],S[0]
    dc,ds=a[1]-a[0],b[1]-b[0]
    actualW=a[0]*ds-b[0]*dc
    vertex=-(a[0]*dc+b[0]*ds)/(dc*dc+ds*ds)
    actualQ=(a[0]+vertex*dc)**2+(b[0]+vertex*ds)**2
    check(vertex==Q(1,2) and actualQ==qmin and actualW==W and
          a[0]**2+b[0]**2==qmax and a[1]**2+b[1]**2==qmax,
          "V12_EXACT_Q_W_MISMATCH")
    # 3<pi<22/7: 2*pi*(1/4) in (3/2,11/7).
    # -W/q in [3/5,6], hence delta' in (21/10,53/7).
    check(Q(3,2)+Q(3,5)==Q(21,10) and
          Q(11,7)+6==Q(53,7) and Q(53,7)>3,
          "V12_DELTA_BOUNDS")
    check(route(s)==("REFUSED","ANGULAR_DRIFT_NOT_CERTIFIED_BELOW_PI"),
          "V12_SHOULD_REFUSE_NOT_DECLARE_NO_ROOTS")
    # Exact endpoint and rational interior signs:
    # F(0)=C(0)=-1/3; F(1)=S(1)=-1/3;
    # F(1/3)=(1/3)*sin(pi/6)>0; F(2/3)=(1/3)*cos(pi/3)>0.
    # For t in [0,1] the orientation phi=atan2(S,C) is continuous;
    # W=-1/3<0 and q>0 imply phi'<0, so delta'=pi/2-W/q>0.
    # delta(0) in (-pi,-pi/2), delta(1) in (pi/2,pi):
    # exactly the two cosine zeros -pi/2,+pi/2, both simple.
    # For t in [1,2], C=2/3>0,S=-1/3<0, theta in [pi/2,pi],
    # so C*cos(theta)+S*sin(theta) <0 (no tail roots).
    return {"source_case":V12,"roots":2,"first_span_roots":2,
            "tail_roots":0,"first_span_signs":["NEGATIVE","POSITIVE","NEGATIVE"],
            "all_root_multiplicities":"SIMPLE",
            "first_cell_qmin":"1/18","first_cell_qmax":"5/9",
            "first_cell_W":"-1/3","delta_prime_lower":"21/10",
            "delta_prime_upper":"53/7",
            "direct_pr441":"REFUSED_ANGULAR_DRIFT_NOT_CERTIFIED_BELOW_PI"}

def produce():
    corpus=pinned(V54,V54_BLOB)
    v2=pinned(V2,V2_BLOB)
    rows=corpus["cases"]
    prior=v2["source_cases"]
    check(len(rows)==121 and len({x["id"] for x in rows})==121,
          "V54_DENOMINATOR")
    un={x["id"] for x in rows if x["expected"]["v54_disposition"]=="BLOCKED"}
    ordered={x["id"] for x in rows if
             x["expected"]["v54_disposition"]==
             "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"}
    check(len(un)==20 and len(ordered)==30,"V54_HISTORICAL_CENSUS")
    ids={x["id"]:x for x in rows}
    check(len(prior)==50 and {x["case_id"] for x in prior}==un|ordered,
          "V2_UNION_CENSUS")
    for item in prior:
        x=ids[item["case_id"]]
        check(item["source_sha256"]==hashlib.sha256(canonical(x["spec"])).hexdigest()
              and item["original_row_sha256"]==hashlib.sha256(canonical(x)).hexdigest()
              and item["registered_evidence_level"]=="COMPLETE_SOURCE_SPECIFIC",
              "V2_PIN_MISMATCH")
    selected=ids[V12]
    check(hashlib.sha256(canonical(selected["spec"])).hexdigest()==V12_SOURCE
          and hashlib.sha256(canonical(selected)).hexdigest()==V12_ROW
          and V12 in un,"V12_SELECTED_ORIGINAL_IDENTITY")
    proof=original_proof(selected)
    structural=[]
    admitted=[]
    refused=[]
    for row in rows:
        try:
            structure(row["spec"])
            structural.append(row["id"])
            route_status,detail=route(row["spec"])
            if route_status=="ADMITTED":
                admitted.append(row["id"])
            else:
                refused.append([row["id"],detail])
        except Refusal:
            pass
    check(len(structural)==3 and len(admitted)==2 and len(refused)==1,
          "DIRECT_GRAMMAR_CENSUS_CHANGED:"+repr({"structural":structural,"admitted":admitted,"refused":refused}))
    check(set(admitted)=={
        "harvested:verify_pb00701_v10:a3af56296a12",V10},
          "DIRECT_ADMITTED_IDENTITY_CHANGED")
    check(set(x[0] for x in refused)=={V12},
          "DIRECT_REFUSED_IDENTITY_CHANGED")
    check(V12 in structural and V12 not in admitted,"V12_FALSE_DIRECT_CLOSURE")
    return {"schema":"radicadsac-mc038-v12-phasegrid-admission-c/1.0",
            "target_pr_head":PARENT_441,"evidence_class":"DETERMINISTIC_MODEL",
            "frozen_v54_blob":V54_BLOB,"complete_v2_blob":V2_BLOB,
            "chosen_historical_id":V12,"source_sha256":V12_SOURCE,
            "original_row_sha256":V12_ROW,
            "before":{"originals":121,"route_refusals":20,
                      "missing_ordered_premises":30,"complete_v2_witnesses":50},
            "after":{"originals":121,"route_refusals":20,
                     "missing_ordered_premises":30,"complete_v2_witnesses":50},
            "delta":{"originals":0,"route_refusals":0,
                     "missing_ordered_premises":0,"complete_v2_witnesses":0},
            "direct_structurally_eligible":len(structural),
            "direct_fully_admitted":len(admitted),
            "direct_historical_unresolved_structural":len(set(structural)&(un|ordered)),
            "direct_historical_unresolved_fully_admitted":len(set(admitted)&(un|ordered)),
            "direct_historical_unresolved_not_admitted":50-len(set(admitted)&(un|ordered)),
            "structurally_eligible_ids":structural,
            "fully_admitted_ids":admitted,
            "structurally_eligible_but_refused":refused,
            "selected_proof":proof,"newly_resolved_historical_ids":[],
            "required_pb_po_discharges":0,"pb00701_established":False,
            "mc_b_established":False,"mc1_established":False,
            "production_authorized":False}

class Tests(unittest.TestCase):
    def test_pinned_121_and_50_and_falsifier(self):
        x=produce()
        self.assertEqual((x["direct_structurally_eligible"],
                          x["direct_fully_admitted"],
                          x["direct_historical_unresolved_not_admitted"]),
                         (3,2,49))
    def test_receipt_is_recomputed(self):
        x=produce()
        self.assertEqual(x,parse_json(RECEIPT.read_bytes()))
    def test_actual_v12_refuses_not_no_root_claim(self):
        x=pinned(V54,V54_BLOB)
        row=next(y for y in x["cases"] if y["id"]==V12)
        self.assertEqual(original_proof(row)["roots"],2)
    def test_source_substitution_is_caught(self):
        x=pinned(V54,V54_BLOB)
        row=copy.deepcopy(next(y for y in x["cases"] if y["id"]==V12))
        row["spec"]["sin_splines"]["1"]["controls"][0]="1"
        self.assertNotEqual(hashlib.sha256(canonical(row["spec"])).hexdigest(),V12_SOURCE)
        with self.assertRaises(Refusal):
            original_proof(row)
    def test_changed_phase_or_grid_knots_refuse(self):
        x=pinned(V54,V54_BLOB)
        s=copy.deepcopy(next(y for y in x["cases"] if y["id"]==V12)["spec"])
        s["phase_turn_rate"]="1/7"
        self.assertEqual(route(s)[0],"REFUSED")
        s["phase_turn_rate"]="1/4"
        s["cos_splines"]["1"]["knots"]=["0","0","1/2","1/2","2","2"]
        self.assertEqual(route(s)[0],"REFUSED")
    def test_true_grid_zero_is_refusal(self):
        x=pinned(V54,V54_BLOB)
        s=copy.deepcopy(next(y for y in x["cases"] if y["id"]==V12)["spec"])
        s["sin_splines"]["1"]["controls"][1]="0"
        s["sin_splines"]["1"]["controls"][2]="0"
        self.assertEqual(route(s)[0],"REFUSED")
    def test_synthetic_tangency_and_ultraclose_roots_not_historical(self):
        x=Q(1,2)
        eps=Q(1,2**120)
        f=lambda t:(t-x)**2-eps**2
        self.assertEqual(f(x-eps),0)
        self.assertEqual(f(x+eps),0)
        self.assertLess(f(x),0)
        self.assertEqual((x+eps)-(x-eps),Q(1,2**119))
        tangent=lambda t:(t-x)**2
        self.assertEqual(tangent(x),0)
        self.assertGreater(tangent(x+eps),0)
        # A synthetic algebraic control is never promoted to frozen-source closure.
        self.assertEqual(produce()["newly_resolved_historical_ids"],[])
    def test_adversarial_json_ingress(self):
        for raw in (b'{"a":1,"a":2}', b'{"x":1.5}', b'{"x":NaN}',
                    b'\xff',b'['*10000+b'0'+b']'*10000):
            with self.assertRaises(Refusal):
                parse_json(raw)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--contract",action="store_true")
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    check(args.contract or args.self_test,"GATE_REQUIRED")
    if args.contract:
        current=produce()
        check(current==parse_json(RECEIPT.read_bytes()),"RECEIPT_DRIFT")
        print(json.dumps(current,sort_keys=True))
    if args.self_test:
        result=unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
        return 0 if result.wasSuccessful() else 1
    return 0

if __name__=="__main__":
    try:
        raise SystemExit(main())
    except Refusal as error:
        print("REFUSED_NONTRUTH:",error)
        raise SystemExit(2)
