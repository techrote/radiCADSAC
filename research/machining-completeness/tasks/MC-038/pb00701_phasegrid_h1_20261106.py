#!/usr/bin/env python3
"""PB-007-01: exact rational quarter-turn grid, oriented affine-H1 source events.

Restricted sufficient theorem. Refusal is NONTRUTH, never a zero-root verdict.
Not a general analytic solver, native/STEP qualifier, or historical closure.
"""
from __future__ import annotations
import argparse
import copy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "pb00701-finite-owner-corpus-v54.json"
V2 = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
ID = "composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail0"
SOURCE_SHA = "57d3c14096ccedfb7faea5023f5a09bada2ca274748f2207c36d77bbc790927c"
ROW_SHA = "c5ba85453dc65e0d18675353986394ae5b34af6219a741ce14af0c332ffc47cd"
SCHEMA = "radicadsac-pb00701-oriented-h1-quarterturn-grid/1.0"
GRAMMAR = "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE"
LIMIT = 400000
MAX_DEPTH = 32
MAX_BITS = 512
MAX_CELLS = 128

class Refusal(ValueError):
    pass

def need(value, reason):
    if not value:
        raise Refusal(reason)

def canonical(data):
    return json.dumps(data,sort_keys=True,separators=(",",":"),ensure_ascii=True,
                      allow_nan=False).encode("ascii")

def git_blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def bounded_rational(token):
    need(type(token) is str and 0 < len(token) <= 128, "RATIONAL_TOKEN_BUDGET")
    try:
        q = Q(token)
    except (ValueError,TypeError,ZeroDivisionError,OverflowError) as exc:
        raise Refusal("BAD_RATIONAL") from exc
    need(str(q) == token, "NONCANONICAL_RATIONAL")
    exact_budget(q)
    return q

def exact_budget(*args):
    for q in args:
        need(max(abs(q.numerator).bit_length(),q.denominator.bit_length())
             <= MAX_BITS, "EXACT_RATIONAL_BIT_BUDGET")

def json_depth(raw):
    depth=0
    quoted=False
    escape=False
    for c in raw:
        if quoted:
            if escape:
                escape=False
            elif c == 92:
                escape=True
            elif c == 34:
                quoted=False
        elif c == 34:
            quoted=True
        elif c in (91,123):
            depth+=1
            need(depth <= MAX_DEPTH, "JSON_DEPTH_BUDGET")
        elif c in (93,125):
            depth-=1
            need(depth >= 0, "JSON_CLOSE_WITHOUT_OPEN")
    need(depth==0 and not quoted, "UNBALANCED_JSON")

def unique_pairs(pairs):
    obj={}
    for k,v in pairs:
        need(k not in obj,"DUPLICATE_JSON_KEY")
        obj[k]=v
    return obj

def parsed_int(token):
    need(len(token) <= 12, "JSON_NUMBER_TOKEN_BUDGET")
    n=int(token)
    need(abs(n) <= 1<<40,"JSON_INTEGER_VALUE_BUDGET")
    return n

def reject_number(_token):
    raise Refusal("NONINTEGER_JSON_NUMBER")

def read_json(path,expected_blob=None):
    try:
        with path.open("rb") as handle:
            raw=handle.read(LIMIT+1)
    except OSError as exc:
        raise Refusal("JSON_READ_FAILURE") from exc
    need(len(raw) <= LIMIT,"JSON_BYTE_BUDGET")
    if expected_blob:
        need(git_blob(raw)==expected_blob,"PINNED_GIT_BLOB_DRIFT")
    json_depth(raw)
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs,
                          parse_int=parsed_int,parse_float=reject_number,
                          parse_constant=reject_number)
    except Refusal:
        raise
    except (UnicodeError,ValueError,RecursionError,OverflowError,TypeError) as exc:
        raise Refusal("JSON_PARSE_REFUSAL") from exc

def spline_pieces(entry,edges):
    need(type(entry) is dict and set(entry)=={"degree","knots","controls"},
         "SPLINE_FIELDS")
    degree=entry["degree"]
    need(type(degree) is int and degree in (0,1), "AFFINE_H1_ONLY")
    n=len(edges)-1
    knots=([str(x) for x in edges] if degree==0
           else [str(x) for e in edges for x in (e,e)])
    need(entry["knots"]==knots,"ORIGINAL_KNOT_STRUCTURE")
    controls=entry["controls"]
    need(type(controls) is list and len(controls)==n*(degree+1),
         "SPLINE_CONTROL_COUNT")
    values=[bounded_rational(x) for x in controls]
    pieces=([(v,v) for v in values] if degree==0 else
            [(values[2*j],values[2*j+1]) for j in range(n)])
    need(all(pieces[j][1]==pieces[j+1][0] for j in range(n-1)),
         "COEFFICIENT_KNOT_DISCONTINUITY")
    return pieces

def angle_endpoint(C,S,quarter_index):
    # cos(pi*k/2), sin(pi*k/2) belong to {0,+/-1} exactly.
    return (C,S,-C,-S)[quarter_index % 4]

def local_cert(C0,C1,S0,S1,delta_turn):
    # For u in [0,1], physical theta' = 2*pi*delta_turn.
    # delta = theta - atan2(S,C); delta' = 2*pi*delta_turn - W/q.
    dC,dS=C1-C0,S1-S0
    a=dC*dC+dS*dS
    b=C0*dC+S0*dS
    q0=C0*C0+S0*S0
    q1=C1*C1+S1*S1
    qmin,qmax=min(q0,q1),max(q0,q1)
    if a:
        vertex=-b/a
        if 0<vertex<1:
            qmin=min(qmin,q0-b*b/a)
    W=C0*dS-S0*dC
    exact_budget(a,b,qmin,qmax,W)
    need(qmin>0,"SHARED_COEFFICIENT_ZERO_OR_IDENTITY")
    wlo,whi=((W/qmax,W/qmin) if W>=0 else (W/qmin,W/qmax))
    # Strict 3 < pi < 22/7; signs reversed for negative phase rate.
    lo,hi=sorted((6*delta_turn,Q(44,7)*delta_turn))
    dlo,dhi=lo-whi,hi-wlo
    exact_budget(wlo,whi,dlo,dhi)
    if dlo>0:
        direction,upper="INCREASING",dhi
    elif dhi<0:
        direction,upper="DECREASING",-dlo
    else:
        raise Refusal("ORIENTATION_DERIVATIVE_SIGN_UNPROVED")
    exact_budget(upper)
    need(0<upper<3,"ANGULAR_DRIFT_NOT_CERTIFIED_BELOW_PI")
    return {"qmin":str(qmin),"qmax":str(qmax),"W_local":str(W),
            "delta_direction":direction,"strict_drift_upper":str(upper)}

def analyze(spec):
    keys={"grammar","source_parameter_id","parameter_lo","parameter_hi",
          "phase_turn_offset","phase_turn_rate","cos_splines","sin_splines"}
    need(type(spec) is dict and set(spec)==keys,"SOURCE_FIELDS")
    need(spec["grammar"]==GRAMMAR and
         spec["source_parameter_id"]=="source-time-t" and
         spec["parameter_lo"]=="0" and
         spec["parameter_hi"] in ("1","2"),"SOURCE_GRAMMAR_OR_TIME")
    edges=[Q(0),Q(1)] if spec["parameter_hi"]=="1" else [Q(0),Q(1),Q(2)]
    off=bounded_rational(spec["phase_turn_offset"])
    rate=bounded_rational(spec["phase_turn_rate"])
    need(rate!=0 and abs(rate)<=4,"PHASE_RATE_UNADMITTED")
    cos,sine=spec["cos_splines"],spec["sin_splines"]
    need(type(cos) is dict and type(sine) is dict and
         "1" in cos and set(cos).issubset({"0","1"}) and
         set(sine)=={"1"},"H1_CHANNEL_GRAMMAR")
    C=spline_pieces(cos["1"],edges)
    S=spline_pieces(sine["1"],edges)
    if "0" in cos:
        H0=spline_pieces(cos["0"],edges)
        need(all(x==y==0 for x,y in H0),"NONZERO_H0")
    # Exact quarter-turn physical grid must contain every original knot.
    knot_indices=[4*(off+rate*t) for t in edges]
    need(all(k.denominator==1 for k in knot_indices),
         "ORIGINAL_KNOT_NOT_ON_QUARTER_TURN_GRID")
    ki,kf=int(knot_indices[0]),int(knot_indices[-1])
    n=abs(kf-ki)
    need(0<n<=MAX_CELLS,"FINITE_PHASE_GRID_CELL_BUDGET")
    step=1 if kf>ki else -1
    indices=[ki+j*step for j in range(n+1)]
    nodes=[(Q(k,4)-off)/rate for k in indices]
    need(nodes[0]==edges[0] and nodes[-1]==edges[-1] and
         all(nodes[j]<nodes[j+1] for j in range(n)),
         "PHASE_GRID_ORDER_OR_CUSTODY")
    need(all(e in nodes for e in edges),"SOURCE_KNOT_MISSING_FROM_GRID")
    samples=[]
    for t,k in zip(nodes,indices):
        j=next((i for i in range(len(edges)-1)
                if edges[i]<=t<=edges[i+1]),None)
        need(j is not None,"GRID_OUTSIDE_ORIGINAL_SOURCE")
        width=edges[j+1]-edges[j]
        u=(t-edges[j])/width
        c=C[j][0]+(C[j][1]-C[j][0])*u
        s=S[j][0]+(S[j][1]-S[j][0])*u
        f=angle_endpoint(c,s,k)
        need(f!=0,"PHASE_GRID_PHYSICAL_ZERO_NOT_ADMITTED")
        samples.append({"t":str(t),"quarter_index":k,
                        "exact_F":str(f),
                        "sign":"POSITIVE" if f>0 else "NEGATIVE"})
    brackets=[]
    certificates=[]
    cell_signs=[samples[0]["sign"]]
    for j in range(n):
        l,r=nodes[j],nodes[j+1]
        midpoint=(l+r)/2
        piece=next((i for i in range(len(edges)-1)
                    if edges[i]<=midpoint<edges[i+1]),None)
        need(piece is not None,"CELL_CROSSES_UNKNOWN_KNOT")
        width=edges[piece+1]-edges[piece]
        def value(pair,t):
            u=(t-edges[piece])/width
            return pair[0]+(pair[1]-pair[0])*u
        c0,c1=value(C[piece],l),value(C[piece],r)
        s0,s1=value(S[piece],l),value(S[piece],r)
        info=local_cert(c0,c1,s0,s1,rate*(r-l))
        left,right=samples[j]["sign"],samples[j+1]["sign"]
        roots=int(left!=right)
        if roots:
            brackets.append([str(l),str(r)])
            cell_signs.append(right)
        certificates.append({"cell":[str(l),str(r)],"piece":piece,
                             "roots":roots,**info})
    return {"schema":SCHEMA,"status":"COMPLETE_RESTRICTED_ORIENTED_H1_SOURCE",
            "evidence_class":"DETERMINISTIC_MODEL",
            "source_sha256":hashlib.sha256(canonical(spec)).hexdigest(),
            "phase_turn_law":{"offset":str(off),"rate":str(rate)},
            "true_source_knots":[str(t) for t in edges[1:-1]],
            "phase_grid_cells":n,"node_signs":[x["sign"] for x in samples],
            "node_evidence":samples,"local_certificates":certificates,
            "root_count":len(brackets),"root_brackets":brackets,
            "simple_root_multiplicity":True,
            "maximal_nonzero_cell_signs":cell_signs,
            "historical_newly_closed":[],"required_pb_po_discharges":0,
            "pb00701_established":False,"mc_b_established":False,
            "mc1_established":False,"production_authorized":False}

def attempt(spec):
    try:
        return analyze(spec)
    except (Refusal,ValueError,TypeError,KeyError,IndexError,OverflowError,
            RecursionError,ZeroDivisionError,MemoryError) as exc:
        return {"status":"REFUSED_NONTRUTH","reason":str(exc),
                "pb00701_established":False,"mc1_established":False}

def v10_spec():
    def piece0(values):
        return {"degree":0,"knots":["0","1","2"],"controls":values}
    return {"grammar":GRAMMAR,"source_parameter_id":"source-time-t",
            "parameter_lo":"0","parameter_hi":"2",
            "phase_turn_offset":"-1/2","phase_turn_rate":"2",
            "cos_splines":{"0":piece0(["0","0"]),
                           "1":piece0(["1","1"])},
            "sin_splines":{"1":{"degree":1,
                                "knots":["0","0","1","1","2","2"],
                                "controls":["1/2","-1/2","-1/2","-1/2"]}}}

EXPECTED_BRACKETS=[
    ["1/8","1/4"],["3/8","1/2"],["1/2","5/8"],["3/4","7/8"],
    ["1","9/8"],["5/4","11/8"],["3/2","13/8"],["7/4","15/8"]
]

def historical_contract():
    corpus=read_json(CORPUS,CORPUS_BLOB)
    register=read_json(V2,V2_BLOB)
    rows=corpus["cases"]
    need(type(rows) is list and len(rows)==121,"FROZEN_121_DRIFT")
    indexed={r["id"]:r for r in rows}
    need(len(indexed)==121,"DUPLICATE_FROZEN_ID")
    missing="BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"
    refused={r["id"] for r in rows if r["expected"]["v54_disposition"]=="BLOCKED"}
    ordered={r["id"] for r in rows if r["expected"]["v54_disposition"]==missing}
    need(len(refused)==20 and len(ordered)==30,"FROZEN_STATUS_DRIFT")
    prior=register["source_cases"]
    indexed_prior={r["case_id"]:r for r in prior}
    need(len(indexed_prior)==len(prior)==50 and
         set(indexed_prior)==refused|ordered,"PRIOR_V2_50_DRIFT")
    for case_id,p in indexed_prior.items():
        row=indexed[case_id]
        need(p["origin"]==row["origin"] and
             p["source_sha256"]==hashlib.sha256(canonical(row["spec"])).hexdigest() and
             p["evidence"]["original_row_sha256"]==
             hashlib.sha256(canonical(row)).hexdigest() and
             p["registered_evidence_level"]=="COMPLETE_SOURCE_SPECIFIC",
             "PRIOR_V2_SOURCE_OR_ROW_MISMATCH")
    selected=indexed[ID]
    need(hashlib.sha256(canonical(selected["spec"])).hexdigest()==SOURCE_SHA
         and hashlib.sha256(canonical(selected)).hexdigest()==ROW_SHA
         and selected["expected"]["v54_disposition"]=="BLOCKED"
         and selected["spec"]==v10_spec(),"V10_PINNED_ORIGINAL_DRIFT")
    result=analyze(selected["spec"])
    need(result["root_count"]==8 and
         result["root_brackets"]==EXPECTED_BRACKETS and
         result["maximal_nonzero_cell_signs"]==
         ["NEGATIVE","POSITIVE","NEGATIVE","POSITIVE","NEGATIVE",
          "POSITIVE","NEGATIVE","POSITIVE","NEGATIVE"],
         "V10_EXACT_SIGNED_EVENT_CONTRADICTION")
    need(all(c["delta_direction"]=="INCREASING" for c in
             result["local_certificates"]),"V10_ORIENTATION_NOT_PROVED")
    return {"selected_id":ID,"v54_blob":CORPUS_BLOB,"v2_blob":V2_BLOB,
            "selected_source_sha256":SOURCE_SHA,"selected_row_sha256":ROW_SHA,
            "historic":{"originals":121,"blocked_routes":20,
                      "missing_ordered":30,"prior_complete_v2":50},
            "all_historical_deltas_zero":True,
            "preexisting_v2_complete":True,
            "root_count":result["root_count"],
            "brackets":result["root_brackets"],
            "maximal_signs":result["maximal_nonzero_cell_signs"],
            "required_pb_po_discharges":0,
            "pb00701_established":False,"mc_b_established":False,
            "mc1_established":False}

class Tests(unittest.TestCase):
    def refuses(self,s):
        self.assertEqual(attempt(s)["status"],"REFUSED_NONTRUTH")

    def test_exact_original_eight_simple_events(self):
        c=analyze(v10_spec())
        self.assertEqual(c["phase_grid_cells"],16)
        self.assertEqual(c["root_brackets"],EXPECTED_BRACKETS)
        self.assertEqual(c["root_count"],8)
        self.assertEqual(len(c["maximal_nonzero_cell_signs"]),9)
        self.assertTrue(all(c0["strict_drift_upper"] and
                            Q(c0["strict_drift_upper"])<3 for c0
                            in c["local_certificates"]))

    def test_prospective_affine_h1_not_preexisting_v10_source(self):
        # Different phase, coefficient orientation and signed event pattern:
        # original-like C=1, S=t+1/4 on [0,2], beta=1/2.
        s=v10_spec()
        s["phase_turn_offset"]="0"
        s["phase_turn_rate"]="1/2"
        s["sin_splines"]["1"]["controls"]=["1/4","5/4","5/4","9/4"]
        cert=analyze(s)
        self.assertEqual(cert["phase_grid_cells"],4)
        self.assertEqual(cert["root_brackets"],[["1/2","1"],["3/2","2"]])
        self.assertEqual(cert["maximal_nonzero_cell_signs"],
                         ["POSITIVE","NEGATIVE","POSITIVE"])
        self.assertTrue(all(c["delta_direction"]=="INCREASING" for c
                            in cert["local_certificates"]))

    def test_reversed_phase_orientation(self):
        s=v10_spec()
        s["phase_turn_offset"]="7/2"
        s["phase_turn_rate"]="-2"
        c=analyze(s)
        self.assertEqual(c["root_count"],8)
        self.assertTrue(all(k["delta_direction"]=="DECREASING" for k
                            in c["local_certificates"]))

    def test_large_rational_perturbation_no_root_collapsing(self):
        s=v10_spec()
        s["sin_splines"]["1"]["controls"][0]=str(Q(1,2)+Q(1,2**120))
        self.assertEqual(analyze(s)["root_count"],8)

    def test_phase_knot_harmonic_and_knot_continuity_refusals(self):
        base=v10_spec()
        for change in (
            lambda s:s.update({"phase_turn_rate":"1/7"}),
            lambda s:s.update({"phase_turn_offset":"1/16"}),
            lambda s:s["cos_splines"].update({"2":s["cos_splines"]["1"]}),
            lambda s:s["cos_splines"]["0"].update({"controls":["1","1"]}),
            lambda s:s["sin_splines"]["1"]["controls"].__setitem__(2,"0"),
            lambda s:s.update({"source_parameter_id":"not-source-t"}),
        ):
            s=copy.deepcopy(base)
            change(s)
            self.refuses(s)

    def test_grid_zero_and_common_coefficient_zero_refusals(self):
        s=v10_spec()
        s["sin_splines"]["1"]["controls"]=["0"]*4
        # At quarter-turn cos=0 and S=0: exact node zero, never a count.
        self.refuses(s)
        s=v10_spec()
        s["cos_splines"]["1"]["controls"]=["0","0"]
        self.refuses(s)

    def test_safe_json_disk_ingress(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"receipt.json"
            good={"quoted": '[ " { ]', "flag":False}
            p.write_text(json.dumps(good))
            self.assertEqual(read_json(p),good)
            for raw in ('{"a":1,"a":2}',"["*10000+"null"+"]"*10000,
                        '{"a":'+("9"*5000)+"}",'{"a":1.5}',
                        '{"a":NaN}',"{"+" "* (LIMIT+1)):
                p.write_text(raw)
                with self.assertRaises(Refusal):
                    read_json(p)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--contract",action="store_true")
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    need(args.contract or args.self_test,"SELECT_AT_LEAST_ONE_GATE")
    if args.contract:
        print(json.dumps(historical_contract(),sort_keys=True))
    if args.self_test:
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            return 1
    return 0

if __name__=="__main__":
    try:
        raise SystemExit(main())
    except Refusal as exc:
        print("REFUSED_NONTRUTH:",exc)
        raise SystemExit(2)
