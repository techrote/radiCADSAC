#!/usr/bin/env python3
"""Exact source-pinned C falsification: V12/V43 constant-H0 bias and two hidden tail roots.

DETERMINISTIC_MODEL only. Analytic justification is in the adjacent RAG Markdown.
No sampling, native geometry, MC-B or proof-obligation promotion.
"""
import argparse
import copy
from fractions import Fraction
import hashlib
import json
from math import isqrt
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "pb00701-finite-owner-corpus-v54.json"
V2 = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
RECEIPT = HERE / "pb00701-v12-h0-bias-tail-20261106.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
ID = "composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail0"
SOURCE_SHA = "ee15e947924b45640dd16634247a476bb230fdc145fef94407d9a7c219928cd5"
ROW_SHA = "d0acef7c69cb8ac1ba128b988e83817a91feff78509dd18007d0e56a506336c3"
BIAS_SHA = {"7/10": "3e7483c5556dd4faaef1462b3cad3483400eb1aa4a83c12b1f646edf4e1f2261",
            "3/4": "abb0e4e9ff27cbf26e83ffe56c19165b02774fe086995e5e45d0dfc07a302c02"}
LIMIT = 400000
SCHEMA = "pb00701-v12-h0-bias-tail-c/1"

class Refusal(ValueError):
    pass

def require(condition, reason):
    if not condition:
        raise Refusal(reason)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")

def sha256(value):
    return hashlib.sha256(canonical(value)).hexdigest()

def pairs_unique(pairs):
    out = {}
    for k, v in pairs:
        require(k not in out, "DUPLICATE_JSON_KEY")
        out[k] = v
    return out

def int_token(s):
    require(len(s) <= 128, "JSON_INTEGER_BUDGET")
    return int(s)

def no_float(_s):
    raise Refusal("JSON_FLOAT_NONTRUTH")

def read_json(path, expected_blob=None):
    try:
        with Path(path).open("rb") as f:
            raw = f.read(LIMIT + 1)
    except OSError as e:
        raise Refusal("FILE_READ") from e
    require(len(raw) <= LIMIT, "FILE_SIZE_BUDGET")
    if expected_blob is not None:
        actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(actual == expected_blob, "PINNED_GIT_BLOB_CHANGED")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs_unique,
                          parse_int=int_token, parse_float=no_float,
                          parse_constant=no_float)
    except Refusal:
        raise
    except (ValueError, UnicodeError, RecursionError, TypeError, OverflowError) as e:
        raise Refusal("JSON_INVALID") from e

def rational(token):
    require(type(token) is str and 1 <= len(token) <= 100, "RATIONAL_TOKEN")
    try:
        value = Fraction(token)
    except (ValueError, ZeroDivisionError, OverflowError) as e:
        raise Refusal("RATIONAL_PARSE") from e
    require(str(value) == token, "RATIONAL_NOT_CANONICAL")
    require(value.numerator.bit_length() <= 1024 and
            value.denominator.bit_length() <= 1024, "RATIONAL_BITS")
    return value

def original_spec():
    return {
      "grammar":"RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
      "source_parameter_id":"source-time-t",
      "parameter_lo":"0", "parameter_hi":"2",
      "phase_turn_offset":"0", "phase_turn_rate":"1/4",
      "cos_splines":{
        "0":{"degree":0,"knots":["0","1","2"],"controls":["0","0"]},
        "1":{"degree":1,"knots":["0","0","1","1","2","2"],
             "controls":["-1/3","2/3","2/3","2/3"]}},
      "sin_splines":{
        "1":{"degree":1,"knots":["0","0","1","1","2","2"],
             "controls":["2/3","-1/3","-1/3","-1/3"]}}
    }

def check_anchor(spec):
    require(type(spec) is dict and spec == original_spec(), "ORIGINAL_SOURCE_GRAMMAR")
    require(sha256(spec) == SOURCE_SHA, "ORIGINAL_SOURCE_IDENTITY")

def mutated_spec(spec, b_token):
    check_anchor(spec)
    b = rational(b_token)
    require(Fraction(2,3) < b <= Fraction(3,4), "BIAS_ADMISSION_RANGE")
    new = copy.deepcopy(spec)
    new["cos_splines"]["0"]["controls"] = [b_token, b_token]
    require(new["phase_turn_rate"] == "1/4" and
            new["source_parameter_id"] == "source-time-t" and
            new["cos_splines"]["1"] == spec["cos_splines"]["1"] and
            new["sin_splines"] == spec["sin_splines"], "ORIGINAL_H1_PHASE_CHANGED")
    return new

def classify(spec, b_token):
    """Complete rational bias subgrammar; roots implicit, never numeric coordinates.

    Proof: prefix symmetric carrier has minimum -1/3, so b>2/3 makes
    it positive. Tail has exactly one strict minimum b-sqrt(5)/3,
    endpoint/knot values b-2/3 and b-1/3 positive. Strict convexity
    and endpoint derivative signs give two simple events iff 9*b*b<5.
    Equality requires irrational b, outside rational original grammar.
    """
    b = rational(b_token)
    source = mutated_spec(spec, b_token)
    discriminator = 9*b*b - 5
    require(discriminator != 0, "IRRATIONAL_TANGENCY_NOT_RATIONAL")
    two = discriminator < 0
    return {
      "source_sha256": sha256(source),
      "source_time": ["0", "1", "2"],
      "source_phase_turns": "t/4",
      "rational_h0_bias": b_token,
      "original_h1_norm_sq_tail": "5/9",
      "original_endpoint_signs": ["POSITIVE","POSITIVE","POSITIVE"],
      "tail_root_count": 2 if two else 0,
      "complete_original_root_count": 2 if two else 0,
      "root_multiplicities": [1, 1] if two else [],
      "maximal_physical_signs": (["POSITIVE","NEGATIVE","POSITIVE"]
                                 if two else ["POSITIVE"]),
      "root_description": ("two distinct simple strict tail-interior zeros, "
                            "one on each side of the unique harmonic minimum"
                            if two else "strictly positive on the entire original [0,2]"),
      "root_decision_exact": ("9*b^2<5" if two else "9*b^2>5"),
      "root_coordinates": "IMPLICIT_NOT_RATIONAL" if two else "NONE",
      "gate_claim": "NO_PB_OR_MC_GATE_DISCHARGE",
      "evidence_class": "DETERMINISTIC_MODEL",
    }

def close_pair(n):
    require(type(n) is int and 4 <= n <= 256, "CLOSE_PAIR_BUDGET")
    scale = 1 << n
    # floor(2^n * sqrt(5)/3), exact integer arithmetic.
    floor_scaled = isqrt((5*scale*scale)//9)
    b = Fraction(floor_scaled, scale)
    require(Fraction(2,3) < b < Fraction(3,4) and 9*b*b < 5,
            "CLOSE_PAIR_OUTSIDE_TWO_ROOT_REGIME")
    # 0 < sqrt(5)/3 - b < 2^-n.
    # 1-cos eta >= 2*eta^2/pi^2; 3<pi<22/7 and sqrt(5)/3>2/3.
    # Thus 0 < gap < 4 sqrt(delta) < 4*2^(-n/2).
    return {"rational_bias": str(b), "n": n,
            "bias_below_irrational_threshold_by": "strictly less than 2^-n",
            "two_root_gap_upper": "strictly less than 4*2^(-n/2)",
            "gap_below_2^-120": n >= 246}

def historical_contract():
    rows = read_json(CORPUS, CORPUS_BLOB)["cases"]
    priors = read_json(V2, V2_BLOB)["source_cases"]
    require(type(rows) is list and len(rows) == 121, "V54_DENOMINATOR")
    idx = {row["id"]:row for row in rows}
    require(len(idx) == 121, "V54_DUPLICATE")
    refused = {r["id"] for r in rows if r["expected"]["v54_disposition"]=="BLOCKED"}
    ordered = {r["id"] for r in rows if r["expected"]["v54_disposition"]==
               "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"}
    require(len(refused)==20 and len(ordered)==30 and not (refused&ordered),
            "V54_CENSUS")
    pidx = {p["case_id"]:p for p in priors}
    require(len(priors)==len(pidx)==50 and
            set(pidx)==refused|ordered, "V2_ID_DENOMINATOR")
    for case_id,p in pidx.items():
        row=idx[case_id]
        require(p["source_sha256"]==sha256(row["spec"]) and
                p["evidence"]["original_row_sha256"]==sha256(row) and
                p["registered_evidence_level"]=="COMPLETE_SOURCE_SPECIFIC",
                "V2_PRIOR_PROVENANCE")
    row=idx[ID]
    check_anchor(row["spec"])
    require(sha256(row)==ROW_SHA and row["origin"]=="v19" and
            row["expected"]["v54_disposition"]=="BLOCKED" and
            row["expected"]["observed"]["spans"][1]==[
              "PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF",
              "BLOCKED","CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED"],
            "V12_HISTORICAL_ROUTE_MISMATCH")
    require(pidx[ID]["source_sha256"]==SOURCE_SHA, "V12_ALREADY_V2_COMPLETE")
    return {"original_count":121,"refused_routes":20,"missing_ordered":30,
            "prior_v2_complete":50,"new_original_closures":[],
            "required_pb_po_discharges":0}

def expected_receipt():
    spec=original_spec()
    return {"schema":SCHEMA,"anchor_case_id":ID,"anchor_source_sha256":SOURCE_SHA,
            "anchor_row_sha256":ROW_SHA,"immutable_v54_blob":CORPUS_BLOB,
            "immutable_v2_blob":V2_BLOB,
            "original_time_knot_phase":"source-time-t [0,1,2] beta=t/4",
            "hypothesis_refuted":
                "ORIGINAL_H1_EVENT_ORDER_SURVIVES_CONSTANT_H0_BIAS_IF_EXTERIOR_AND_KNOT_SIGNS_AGREE",
            "historical_before":historical_contract(),
            "historical_after":historical_contract(),
            "historical_deltas":{"original_count":0,"refused_routes":0,
                                 "missing_ordered":0,"prior_v2_complete":0},
            "adversarial_prospective_two_root":classify(spec,"7/10"),
            "prospective_positive_root_free":classify(spec,"3/4"),
            "near_tangent_rational":close_pair(256),
            "analytic_tangency_threshold":"b=sqrt(5)/3, irrational not admitted",
            "evidence_class":"DETERMINISTIC_MODEL",
            "pb00701_established":False,"mc_b_established":False,
            "mc1_established":False,"production_authorized":False,
            "supported_operations_unchanged":26}

class Tests(unittest.TestCase):
    def test_actual_frozen_source_canonical_identity(self):
        self.assertEqual(sha256(original_spec()), SOURCE_SHA)
        self.assertEqual(historical_contract()["prior_v2_complete"], 50)
    def test_two_simple_roots_original_h1_unchanged(self):
        d=classify(original_spec(),"7/10")
        self.assertEqual(d["source_sha256"],BIAS_SHA["7/10"])
        self.assertEqual(d["complete_original_root_count"],2)
        self.assertEqual(d["maximal_physical_signs"],
                         ["POSITIVE","NEGATIVE","POSITIVE"])
    def test_exact_nonroot_positive_control(self):
        d=classify(original_spec(),"3/4")
        self.assertEqual(d["source_sha256"],BIAS_SHA["3/4"])
        self.assertEqual(d["complete_original_root_count"],0)
        self.assertEqual(d["maximal_physical_signs"],["POSITIVE"])
    def test_extremely_close_separate_roots(self):
        p=close_pair(256)
        self.assertTrue(p["gap_below_2^-120"])
        b=Fraction(p["rational_bias"])
        self.assertTrue(9*b*b < 5 and b>Fraction(2,3))
        self.assertEqual(classify(original_spec(),str(b))["root_multiplicities"],[1,1])
    def test_tangency_is_irrational_and_unadmitted(self):
        self.assertEqual(isqrt(5),2)
        for token in ("sqrt(5)/3","0.7453559925","2/3","1/2","5/7","7/10 "):
            with self.assertRaises(Refusal):
                classify(original_spec(),token)
        # A genuine analytic second-order tangency occurs at b=sqrt(5)/3;
        # 9*p^2=5*q^2 has no nonzero rational solution (5-adic parity).
    def test_identity_and_source_phase_knot_h0_continuity_refusal(self):
        bad=[]
        for channel in ("cos_splines","sin_splines"):
            s=copy.deepcopy(original_spec())
            s[channel]["1"]["controls"]=["0"]*4
            bad.append(s)
        for field,new in (("phase_turn_rate","1/8"),
                          ("source_parameter_id","reparameterized")):
            s=copy.deepcopy(original_spec());s[field]=new;bad.append(s)
        s=copy.deepcopy(original_spec())
        s["cos_splines"]["1"]["knots"][2]="3/4";bad.append(s)
        s=copy.deepcopy(original_spec())
        s["cos_splines"]["0"]["controls"][0]="1";bad.append(s)
        for s in bad:
            with self.assertRaises(Refusal):
                classify(s,"7/10")
    def test_disk_receipt_ingress(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"data.json"
            path.write_text('{"ok":1}')
            self.assertEqual(read_json(path),{"ok":1})
            for raw in ('{"x":1,"x":2}', '{"x":1.25}', '{"x":NaN}',
                        '{"x":'+("9"*5000)+'}', "{"+" "*(LIMIT+1),
                        "["*10000+"null"+"]"*10000):
                path.write_text(raw)
                with self.assertRaises(Refusal):
                    read_json(path)
    def test_machine_receipt_exact_not_freeform_claim(self):
        self.assertEqual(read_json(RECEIPT), expected_receipt())

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--contract",action="store_true")
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    require(args.contract or args.self_test, "SELECT_A_GATE")
    if args.contract:
        result=expected_receipt()
        require(read_json(RECEIPT)==result,"MACHINE_RECEIPT_DRIFT")
        print(json.dumps({"status":"QUALIFIED_BOUNDED_NEGATIVE_C",
                          "anchor":ID,"originals":121,"blocked":20,
                          "missing_ordered":30,"complete_v2":50,
                          "historical_delta":0,"pb_po_discharges":0,
                          "prospective_bias7_10_roots":2,
                          "prospective_bias3_4_roots":0},sort_keys=True))
    if args.self_test:
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
        run=unittest.TextTestRunner(verbosity=2).run(suite)
        if not run.wasSuccessful():
            return 1
    return 0

if __name__=="__main__":
    try:
        sys.exit(main())
    except Refusal as e:
        print("REFUSED_NONTRUTH:",str(e))
        sys.exit(2)
