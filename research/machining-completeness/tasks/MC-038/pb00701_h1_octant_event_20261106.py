#!/usr/bin/env python3
"""PB-007-01: rational octant-node oriented H1 event/sign certificate.

Restricted source-side sufficient theorem, NEVER a generic/root-free decision on refusal.
No native geometry, STEP, PB discharge or original historical closure.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "pb00701-finite-owner-corpus-v54.json"
V2 = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
V54_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
V12 = "composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail0"
SOURCE_SHA = "ee15e947924b45640dd16634247a476bb230fdc145fef94407d9a7c219928cd5"
ROW_SHA = "d0acef7c69cb8ac1ba128b988e83817a91feff78509dd18007d0e56a506336c3"
GRAMMAR = "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE"
LIMIT = 400000
MAX_BITS = 512

class Refusal(ValueError):
    pass

def check(condition, reason):
    if not condition:
        raise Refusal(reason)

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",",":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")

def checked_json(path, expected_blob=None):
    with Path(path).open("rb") as handle:
        raw = handle.read(LIMIT+1)
    check(len(raw) <= LIMIT, "BYTE_LIMIT")
    if expected_blob:
        git_hash = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        check(git_hash == expected_blob, "IMMUTABLE_BLOB_DRIFT")
    # Reject huge nesting *before* recursive JSON conversion.
    depth = 0; quoted = False; escaped = False
    for ch in raw:
        if quoted:
            if escaped: escaped = False
            elif ch == 92: escaped = True
            elif ch == 34: quoted = False
        elif ch == 34: quoted = True
        elif ch in (91,123):
            depth += 1
            check(depth <= 32, "JSON_DEPTH_LIMIT")
        elif ch in (93,125):
            depth -= 1
            check(depth >= 0, "JSON_DEPTH_MALFORMED")
    check(depth == 0 and not quoted, "JSON_STRUCTURE_MALFORMED")
    def pairs(values):
        d = {}
        for k,v in values:
            check(k not in d, "DUPLICATE_JSON_KEY")
            d[k] = v
        return d
    def integer(token):
        check(len(token) <= 12, "INTEGER_TOKEN_LIMIT")
        return int(token)
    def refuse_nonint(token):
        raise Refusal("NONINTEGER_JSON_NUMBER")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                          parse_int=integer, parse_float=refuse_nonint,
                          parse_constant=refuse_nonint)
    except Refusal:
        raise
    except (ValueError,UnicodeError,RecursionError,OverflowError) as e:
        raise Refusal("INVALID_JSON") from e

def rat(token):
    check(type(token) is str and 0 < len(token) <= 128, "RATIONAL_TOKEN")
    try:
        q = F(token)
    except (ValueError,TypeError,ZeroDivisionError,OverflowError) as e:
        raise Refusal("INVALID_RATIONAL") from e
    check(str(q) == token, "NONCANONICAL_RATIONAL")
    budget(q)
    return q

def budget(*qs):
    for q in qs:
        check(max(abs(q.numerator).bit_length(), q.denominator.bit_length()) <= MAX_BITS,
              "EXACT_BIT_LIMIT")

def pieces(src, edges):
    check(type(src) is dict and set(src) == {"degree","knots","controls"}, "SPLINE_FIELDS")
    degree = src["degree"]
    check(type(degree) is int and degree in (0,1), "AFFINE_ONLY")
    n = len(edges)-1
    knots = ([str(x) for x in edges] if degree == 0 else
             [str(x) for edge in edges for x in (edge,edge)])
    check(src["knots"] == knots, "SPLINE_KNOTS")
    cs = src["controls"]
    check(type(cs) is list and len(cs) == n*(degree+1), "SPLINE_CONTROLS")
    vals = [rat(s) for s in cs]
    ps = ([(x,x) for x in vals] if degree == 0 else
          [(vals[2*j],vals[2*j+1]) for j in range(n)])
    check(all(ps[i][1] == ps[i+1][0] for i in range(n-1)), "KNOT_DISCONTINUITY")
    return ps

def octant_sign(c,s,k):
    # cos(k*pi/4),sin(k*pi/4): for odd k the common 1/sqrt(2)>0 cancels.
    return (c,c+s,s,-c+s,-c,-c-s,-s,c-s)[k%8]

def interp(pair, t, lo, hi):
    return pair[0] + (pair[1]-pair[0])*(t-lo)/(hi-lo)

def q_and_w(c0,c1,s0,s1):
    dc,ds = c1-c0,s1-s0
    a,b = dc*dc+ds*ds,c0*dc+s0*ds
    q0,q1 = c0*c0+s0*s0,c1*c1+s1*s1
    qmin = min(q0,q1)
    if a and 0 < -b/a < 1:
        qmin = min(qmin, q0-b*b/a)
    W = c0*ds-s0*dc
    budget(a,b,q0,q1,qmin,W)
    check(qmin > 0,"SHARED_H1_ZERO_OR_IDENTITY")
    return qmin,W

def certify(spec):
    keys = {"grammar","source_parameter_id","parameter_lo","parameter_hi",
            "phase_turn_offset","phase_turn_rate","cos_splines","sin_splines"}
    check(type(spec) is dict and set(spec) == keys,"SOURCE_FIELDS")
    check(spec["grammar"] == GRAMMAR and
          spec["source_parameter_id"] == "source-time-t" and
          spec["parameter_lo"] == "0" and spec["parameter_hi"] in ("1","2"),
          "SOURCE_TIME_GRAMMAR")
    edges = [F(0),F(1)] if spec["parameter_hi"] == "1" else [F(0),F(1),F(2)]
    off,rate = rat(spec["phase_turn_offset"]),rat(spec["phase_turn_rate"])
    check(rate != 0 and abs(rate) <= 4, "PHASE_RATE")
    cs,ss = spec["cos_splines"], spec["sin_splines"]
    check(type(cs) is dict and type(ss) is dict and "1" in cs and
          set(cs).issubset({"0","1"}) and set(ss) == {"1"}, "H1_ONLY")
    C,S = pieces(cs["1"],edges),pieces(ss["1"],edges)
    if "0" in cs:
        H = pieces(cs["0"],edges)
        check(all(a == b == 0 for a,b in H),"NONZERO_H0")
    levels = [8*(off+rate*t) for t in edges]
    check(all(k.denominator == 1 for k in levels),"SOURCE_KNOT_NOT_OCTANT_NODE")
    n = abs(int(levels[-1]-levels[0]))
    check(0 < n <= 128, "OCTANT_CELL_BUDGET")
    step = 1 if rate > 0 else -1
    indices = [int(levels[0])+step*i for i in range(n+1)]
    nodes = [(F(k,8)-off)/rate for k in indices]
    check(nodes[0] == edges[0] and nodes[-1] == edges[-1] and
          all(nodes[i] < nodes[i+1] for i in range(n)) and
          all(e in nodes for e in edges), "OCTANT_SOURCE_TIME_ORDER")
    samples = []
    for t,k in zip(nodes,indices):
        piece = next(j for j in range(len(edges)-1) if edges[j] <= t <= edges[j+1])
        c,s = interp(C[piece],t,edges[piece],edges[piece+1]), interp(S[piece],t,edges[piece],edges[piece+1])
        v = octant_sign(c,s,k)
        check(v != 0, "PHYSICAL_OCTANT_NODE_ZERO")
        samples.append("POSITIVE" if v > 0 else "NEGATIVE")
    brackets, certificates, cells = [],[],[samples[0]]
    for i in range(n):
        lo,hi = nodes[i],nodes[i+1]
        mid = (lo+hi)/2
        j = next(k for k in range(len(edges)-1) if edges[k] <= mid < edges[k+1])
        c0,c1 = interp(C[j],lo,edges[j],edges[j+1]),interp(C[j],hi,edges[j],edges[j+1])
        s0,s1 = interp(S[j],lo,edges[j],edges[j+1]),interp(S[j],hi,edges[j],edges[j+1])
        qmin,W = q_and_w(c0,c1,s0,s1)
        turn = rate*(hi-lo)
        check(abs(turn) == F(1,8) and turn*W <= 0, "ORIENTATION_NOT_COUNTER_ROTATING")
        # delta=theta-arg(C+iS) is strictly monotone because rate*W<=0.
        # A nonzero affine vector segment has |delta arg|<pi; hence
        # |delta phase| < pi+pi/4 < 2*pi. Opposite signs certify ONE root.
        opposite = samples[i] != samples[i+1]
        if not opposite:
            # Same signs require the stronger |delta phase|<pi guarantee.
            # 3<pi<22/7; |theta change|=pi/4<11/14.
            upper = F(11,14) + abs(W)/qmin
            budget(upper)
            check(upper < 3, "SAME_SIGN_WINDING_NOT_CERTIFIED")
        else:
            brackets.append([str(lo),str(hi)])
            cells.append(samples[i+1])
        certificates.append({"cell":[str(lo),str(hi)],"qmin":str(qmin),
                             "W_local":str(W),"mode":("OPPOSITE_ONE_SIMPLE" if opposite
                                               else "SAME_ZERO_STRICT_DRIFT"),
                             "root_count":int(opposite)})
    return {"status":"COMPLETE_RESTRICTED_OCTANT_H1_SOURCE",
            "evidence_class":"DETERMINISTIC_MODEL",
            "source_sha256":hashlib.sha256(canonical(spec)).hexdigest(),
            "octant_nodes":[str(t) for t in nodes],"node_signs":samples,
            "original_knots":[str(e) for e in edges[1:-1]],
            "root_brackets":brackets,"root_count":len(brackets),
            "root_multiplicities":[1]*len(brackets),"maximal_sign_cells":cells,
            "certificates":certificates,"new_historical_closures":[],
            "required_pb_po_discharges":0,"pb00701_established":False,
            "mc_b_established":False,"mc1_established":False,"production_authorized":False}

def try_certify(spec):
    try:
        return certify(spec)
    except (Refusal,TypeError,ValueError,IndexError,KeyError,ZeroDivisionError,
            OverflowError,RecursionError,MemoryError) as e:
        return {"status":"REFUSED_NONTRUTH","reason":str(e),
                "pb00701_established":False,"mc1_established":False}

def v12_spec():
    return {"grammar":GRAMMAR,"source_parameter_id":"source-time-t",
            "parameter_lo":"0","parameter_hi":"2",
            "phase_turn_offset":"0","phase_turn_rate":"1/4",
            "cos_splines":{"0":{"degree":0,"knots":["0","1","2"],"controls":["0","0"]},
                           "1":{"degree":1,"knots":["0","0","1","1","2","2"],
                                "controls":["-1/3","2/3","2/3","2/3"]}},
            "sin_splines":{"1":{"degree":1,"knots":["0","0","1","1","2","2"],
                                 "controls":["2/3","-1/3","-1/3","-1/3"]}}}

def historical_contract():
    corpus = checked_json(CORPUS,V54_BLOB)
    v2 = checked_json(V2,V2_BLOB)
    rows = corpus["cases"]
    check(type(rows) is list and len(rows) == 121, "CORPUS_121")
    selected = {r["id"]:r for r in rows}
    check(len(selected) == 121, "CORPUS_IDS")
    blocked = {r["id"] for r in rows if r["expected"]["v54_disposition"] == "BLOCKED"}
    missing = {r["id"] for r in rows if r["expected"]["v54_disposition"] == "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"}
    check(len(blocked) == 20 and len(missing) == 30 and not blocked & missing,
          "FRONTIER_20_30")
    prior = v2["source_cases"]
    check(type(prior) is list and len(prior)==50 and
          {p["case_id"] for p in prior} == blocked|missing, "V2_50")
    for p in prior:
        r = selected[p["case_id"]]
        check(p["source_sha256"] == hashlib.sha256(canonical(r["spec"])).hexdigest() and
              p["evidence"]["original_row_sha256"] == hashlib.sha256(canonical(r)).hexdigest() and
              p["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC", "V2_SOURCE_OR_ROW_DRIFT")
    row = selected[V12]
    check(hashlib.sha256(canonical(row["spec"])).hexdigest() == SOURCE_SHA and
          hashlib.sha256(canonical(row)).hexdigest() == ROW_SHA and
          row["spec"] == v12_spec(), "ORIGINAL_V12_DRIFT")
    result = certify(row["spec"])
    check(result["root_brackets"] == [["0","1/2"],["1/2","1"]] and
          result["node_signs"] == ["NEGATIVE","POSITIVE","NEGATIVE","NEGATIVE","NEGATIVE"] and
          result["maximal_sign_cells"] == ["NEGATIVE","POSITIVE","NEGATIVE"] and
          result["root_count"] == 2, "V12_OCTANT_EVENT_CONTRADICTION")
    return {"selected_original":V12,"v54_git_blob":V54_BLOB,"v2_git_blob":V2_BLOB,
            "source_sha256":SOURCE_SHA,"row_sha256":ROW_SHA,
            "historical_counts":{"originals":121,"route_refusals":20,
                                 "missing_ordered":30,"prior_complete_v2":50},
            "historical_deltas":{"originals":0,"route_refusals":0,
                                 "missing_ordered":0,"prior_complete_v2":0},
            "prior_complete":True,"root_count":2,"root_brackets":result["root_brackets"],
            "newly_closed_originals":[], "required_pb_po_discharges":0,
            "pb00701_established":False,"mc_b_established":False,
            "mc1_established":False}

class Tests(unittest.TestCase):
    def refuses(self,s):
        self.assertEqual(try_certify(s)["status"],"REFUSED_NONTRUTH")

    def test_v12_octant_two_ordered_events(self):
        r = certify(v12_spec())
        self.assertEqual(r["root_brackets"],[["0","1/2"],["1/2","1"]])
        self.assertEqual(r["node_signs"],["NEGATIVE","POSITIVE","NEGATIVE","NEGATIVE","NEGATIVE"])
        self.assertEqual(r["maximal_sign_cells"],["NEGATIVE","POSITIVE","NEGATIVE"])
        self.assertEqual(r["certificates"][0]["mode"],"OPPOSITE_ONE_SIMPLE")
        self.assertEqual(r["certificates"][2]["mode"],"SAME_ZERO_STRICT_DRIFT")

    def test_reverse_rate_one_event(self):
        s = v12_spec(); s["parameter_hi"]="1"
        s["phase_turn_rate"]="-1/8"
        s["cos_splines"]={"1":{"degree":0,"knots":["0","1"],"controls":["1"]}}
        s["sin_splines"]={"1":{"degree":0,"knots":["0","1"],"controls":["2"]}}
        self.assertEqual(certify(s)["root_brackets"],[["0","1"]])

    def test_exact_close_to_endpoint_is_not_a_separation_claim(self):
        s = v12_spec(); s["parameter_hi"]="1"
        s["phase_turn_rate"]="1/8"
        s["cos_splines"]={"1":{"degree":0,"knots":["0","1"],
                                  "controls":[str(F(1,2**150))]}}
        s["sin_splines"]={"1":{"degree":0,"knots":["0","1"],"controls":["-1"]}}
        r = certify(s)
        self.assertEqual(r["root_brackets"],[["0","1"]])

    def test_uncertified_same_sign_winding_refuses(self):
        # Genuine two-root octant cell with NEGATIVE signs at both endpoints.
        # At t=1/2, C=99/200>0, S=-1/200, beta=1/16:
        # cos(pi/8)>9/10 and sin(pi/8)<1/2 imply F(1/2)>0.
        # Never infer zero roots from identical node signs without drift < pi.
        s = v12_spec(); s["parameter_hi"]="1"
        s["phase_turn_rate"]="1/8"
        s["cos_splines"]={"1":{"degree":1,"knots":["0","0","1","1"],
                                  "controls":["-1/100","1"]}}
        s["sin_splines"]={"1":{"degree":1,"knots":["0","0","1","1"],
                                  "controls":["1","-101/100"]}}
        self.assertLess(octant_sign(F(-1,100),F(1),0),0)
        self.assertLess(octant_sign(F(1),F(-101,100),1),0)
        self.refuses(s)

    def test_source_h0_and_shared_vector_and_node_zero(self):
        s = v12_spec(); s["cos_splines"]["0"]["controls"]=["1","1"]
        self.refuses(s)
        s = v12_spec(); s["cos_splines"]["1"]["controls"]=["0","0","0","0"]
        s["sin_splines"]["1"]["controls"]=["0","0","0","0"]
        self.refuses(s)
        s = v12_spec(); s["cos_splines"]["1"]["controls"]=["1","1","1","1"]
        s["sin_splines"]["1"]["controls"]=["-1","-1","-1","-1"]
        self.refuses(s)

    def test_malformed_and_excessive_phases(self):
        s=v12_spec(); s["phase_turn_offset"]="1/7"
        self.refuses(s)
        s=v12_spec(); s["phase_turn_rate"]="5"
        self.refuses(s)
        s=v12_spec(); s["sin_splines"]={}
        self.refuses(s)

    def test_disk_json_ingress_refusal(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"untrusted.json"
            for bad in [b'{"x":1,"x":2}',b'['*40+b'0'+b']'*40,
                        b'{"n":'+b'1'*5000+b'}',b'{"n":NaN}',b' '*400001]:
                p.write_bytes(bad)
                with self.assertRaises(Refusal):
                    checked_json(p)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args=parser.parse_args()
    if args.contract:
        print(json.dumps(historical_contract(),sort_keys=True,indent=2))
    if args.self_test:
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
        outcome=unittest.TextTestRunner(verbosity=2).run(suite)
        if not outcome.wasSuccessful():
            raise SystemExit(1)
    if not args.contract and not args.self_test:
        parser.print_help()

if __name__ == "__main__":
    main()
