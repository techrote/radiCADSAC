#!/usr/bin/env python3
"""Exact bounded orientation-preserving H1 angular-drift source-event research.

No mathematical truth is inferred from scanning, timeouts or resource caps.
Source-specific V2 proofs predate this optional reusable subgrammar.
DETERMINISTIC_MODEL, not PB-007 or engineering/native STEP certification.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import tempfile
import unittest
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "pb00701-finite-owner-corpus-v54.json"
V2 = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
RECEIPT = HERE / "pb00701-affine-h1-angular-drift-20261106.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
SCHEMA = "radicadsac-mc038-h1-oriented-angular-drift/1.0"
GRAMMAR = "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE"
MISSING = "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"
MAX_RAW_BYTES = 400_000
MAX_JSON_DEPTH = 32
MAX_Q_BITS = 256
V9 = "composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail0"
V43 = "harvested:verify_pb00701_v9:4e7b85fa122a"
PINNED = {
    V9: "4d1ef1cbecceeb4a43b4e30fd37327fa204164cc9ce25dfe4f1744a052cebcc2",
    V43: "a83ca0cd16c7822e6525f8f2d2df26a54f45b99807cadebc67f31fc49b066c10",
}
STATUS = "COMPLETE_BOUNDED_ORIENTED_H1_SIGNED_EVENT_CERTIFICATE"


class Refusal(ValueError):
    pass


def need(ok, why):
    if not ok:
        raise Refusal(why)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()


def nesting_guard(raw):
    depth = 0
    quote = escape = False
    for c in raw:
        if quote:
            if escape:
                escape = False
            elif c == 92:
                escape = True
            elif c == 34:
                quote = False
        elif c == 34:
            quote = True
        elif c in (91, 123):
            depth += 1
            need(depth <= MAX_JSON_DEPTH, "JSON_DEPTH_REFUSAL")
        elif c in (93, 125):
            depth -= 1
            need(depth >= 0, "JSON_STRUCTURE_REFUSAL")
    need(depth == 0 and not quote, "JSON_STRUCTURE_REFUSAL")


def duplicate_reject(pairs):
    obj = {}
    for key, val in pairs:
        need(key not in obj, "DUPLICATE_JSON_KEY_REFUSAL")
        obj[key] = val
    return obj


def bounded_int(token):
    need(len(token) <= 12, "JSON_INTEGER_TOKEN_BUDGET")
    val = int(token)
    need(abs(val) <= (1 << 40), "JSON_INTEGER_VALUE_BUDGET")
    return val


def refuse_float(_):
    raise Refusal("JSON_NONINTEGER_REFUSAL")


def read_json(path, expected_blob=None):
    try:
        with path.open("rb") as handle:
            raw = handle.read(MAX_RAW_BYTES + 1)
    except OSError as exc:
        raise Refusal("JSON_READ_FAILURE") from exc
    need(len(raw) <= MAX_RAW_BYTES, "JSON_BYTE_BUDGET")
    if expected_blob is not None:
        need(git_blob(raw) == expected_blob, "PINNED_SOURCE_BLOB_DRIFT")
    nesting_guard(raw)
    try:
        return json.loads(raw.decode("utf-8"),
                          object_pairs_hook=duplicate_reject,
                          parse_int=bounded_int,
                          parse_float=refuse_float,
                          parse_constant=refuse_float)
    except Refusal:
        raise
    except (UnicodeError, ValueError, RecursionError, OverflowError, TypeError) as exc:
        raise Refusal("JSON_PARSE_REFUSAL") from exc


def rational(s):
    need(type(s) is str and 0 < len(s) <= 128, "NONCANONICAL_RATIONAL")
    try:
        v = Q(s)
    except (ValueError, TypeError, OverflowError, ZeroDivisionError) as exc:
        raise Refusal("INVALID_RATIONAL") from exc
    need(str(v) == s, "NONCANONICAL_RATIONAL")
    budget(v)
    return v


def budget(*values):
    for v in values:
        need(max(abs(v.numerator).bit_length(), v.denominator.bit_length())
             <= MAX_Q_BITS, "EXACT_RATIONAL_BIT_REFUSAL")


def sign(v):
    need(v != 0, "EXACT_ENDPOINT_OR_KNOT_ZERO_UNADMITTED")
    return "POSITIVE" if v > 0 else "NEGATIVE"


def exact_span(c0, c1, s0, s1):
    """Sufficient angular certificate for an arbitrary rational affine H1 pair.

    u in [0,1], theta=pi*t/4. q=C^2+S^2 is exact quadratic.
    W=C*S'-S*C' constant. delta'=pi/4-W/q. Strict rational bounds
    3/4 < pi/4 < 11/14; total drift <3<pi.
    """
    c0, c1, s0, s1 = (rational(v) for v in (c0, c1, s0, s1))
    dc, ds = c1 - c0, s1 - s0
    a = dc*dc + ds*ds
    b = c0*dc + s0*ds
    q0, q1 = c0*c0+s0*s0, c1*c1+s1*s1
    qmax = max(q0, q1)
    qmin = min(q0, q1)
    if a > 0:
        vertex = -b/a
        if 0 < vertex < 1:
            qmin = min(qmin, q0 - b*b/a)
    w = c0*ds - s0*dc
    budget(a, b, qmin, qmax, w)
    need(qmin > 0, "IDENTITY_OR_SHARED_AMPLITUDE_ZERO_REFUSAL")
    if w < 0:
        direction, upper = "INCREASING", Q(11,14) + (-w)/qmin
    elif Q(3,4) - w/qmin > 0:
        direction, upper = "INCREASING", Q(11,14)
    elif Q(11,14) - w/qmax < 0:
        direction, upper = "DECREASING", w/qmin - Q(3,4)
    else:
        raise Refusal("ANGULAR_DERIVATIVE_SIGN_UNPROVED")
    budget(upper)
    need(0 < upper < 3, "ANGULAR_DRIFT_NOT_STRICTLY_BELOW_PI")
    return {
        "C_endpoints": [str(c0), str(c1)],
        "S_endpoints": [str(s0), str(s1)],
        "q_min": str(qmin), "q_max": str(qmax),
        "wronskian_local": str(w),
        "delta_direction": direction,
        "strict_abs_delta_change_upper": str(upper),
        "root_count_justification":
            "q>0; exact strict delta derivative sign; |delta(b)-delta(a)|<3<pi; "
            "every cosine zero has nonzero derivative; opposite endpoint signs imply one root"
    }


def spline_piece_values(entry, edges):
    need(type(entry) is dict and set(entry) ==
         {"degree", "knots", "controls"}, "SPLINE_FIELD_REFUSAL")
    degree = entry["degree"]
    need(type(degree) is int and degree in (0, 1),
         "ONLY_PIECEWISE_AFFINE_H1_ADMITTED")
    n = len(edges) - 1
    expected_knots = (
        [str(x) for x in edges] if degree == 0 else
        [str(x) for edge in edges for x in (edge, edge)]
    )
    need(entry["knots"] == expected_knots, "ORIGINAL_KNOT_STRUCTURE")
    need(type(entry["controls"]) is list and
         len(entry["controls"]) == n * (degree + 1),
         "ORIGINAL_CONTROL_CARDINALITY")
    vals = [rational(v) for v in entry["controls"]]
    if degree == 0:
        pieces = [(v, v) for v in vals]
    else:
        pieces = [(vals[2*j], vals[2*j+1]) for j in range(n)]
    if n == 2:
        need(pieces[0][1] == pieces[1][0],
             "ORIGINAL_KNOT_COEFFICIENT_DISCONTINUITY")
    return pieces


def analyze(spec):
    need(type(spec) is dict and set(spec) ==
         {"grammar", "source_parameter_id", "parameter_lo", "parameter_hi",
          "phase_turn_offset", "phase_turn_rate", "cos_splines",
          "sin_splines"}, "ORIGINAL_SOURCE_FIELD_REFUSAL")
    need(spec["grammar"] == GRAMMAR and
         spec["source_parameter_id"] == "source-time-t" and
         spec["parameter_lo"] == "0" and
         spec["parameter_hi"] in ("1", "2") and
         spec["phase_turn_offset"] == "0" and
         spec["phase_turn_rate"] == "1/8",
         "ORIGINAL_TIME_OR_PHASE_REFUSAL")
    edges = [Q(0), Q(1)] if spec["parameter_hi"] == "1" else [
        Q(0), Q(1), Q(2)]
    cos, sine = spec["cos_splines"], spec["sin_splines"]
    need(type(cos) is dict and type(sine) is dict and
         "1" in cos and set(cos).issubset({"0","1"}) and
         set(sine) == {"1"}, "H1_ORIENTATION_PRESERVATION_GRAMMAR")
    if "0" in cos:
        pieces_0 = spline_piece_values(cos["0"],edges)
        need(all(a == b == 0 for a,b in pieces_0),
             "NONZERO_H0_NOT_ADMITTED")
    cc, ss = spline_piece_values(cos["1"],edges), spline_piece_values(sine["1"],edges)
    certificates = []
    for j in range(len(edges)-1):
        a, b = edges[j], edges[j+1]
        C0,C1 = cc[j]
        S0,S1 = ss[j]
        cert = exact_span(str(C0), str(C1), str(S0), str(S1))
        # Exact source angular facts: theta(0)=0, theta(1)=pi/4,
        # theta(2)=pi/2. Endpoint signs are rational times positive sqrt(2)/2.
        left = sign(C0 if a == 0 else C0+S0)
        right = sign(C1+S1 if b == 1 else S1)
        num_roots = int(left != right)
        cert.update({
            "source_span":[str(a),str(b)],
            "left_exact_sign":left, "right_exact_sign":right,
            "isolated_root_count":num_roots,
            "isolated_root_locator": {
                "open_original_source_interval":[str(a),str(b)],
                "unique_simple_root":True,
                "coordinate_is_implicit_not_rational":True
            } if num_roots else None,
            "all_nonzero_sign_cells":[left,right] if num_roots else [left]})
        certificates.append(cert)
    for i in range(len(certificates)-1):
        need(certificates[i]["right_exact_sign"] ==
             certificates[i+1]["left_exact_sign"],
             "ORIGINAL_PHYSICAL_KNOT_SIGN_MISMATCH")
    count = sum(x["isolated_root_count"] for x in certificates)
    signs = [certificates[0]["left_exact_sign"]]
    for cert in certificates:
        if cert["isolated_root_count"]:
            signs.append(cert["right_exact_sign"])
    return {
        "schema":SCHEMA, "status":STATUS,
        "evidence_class":"DETERMINISTIC_MODEL",
        "source_sha256":hashlib.sha256(canonical(spec)).hexdigest(),
        "source_interval":[str(edges[0]),str(edges[-1])],
        "true_source_knots":["1"] if len(edges)==3 else [],
        "global_phase_turns":{"offset":"0","rate":"1/8"},
        "orientation_preserved":True,
        "spans":certificates,
        "total_isolated_roots":count,
        "total_zero_continua":0,
        "root_multiplicity":"SIMPLE_EACH_COUNTED_ROOT",
        "maximal_nonzero_cell_signs":signs,
        "source_specific_complete_within_admitted_grammar":True,
        "historical_originals_newly_closed":[],
        "required_pb_po_discharges":0,
        "pb00701_established":False, "mc_b_established":False,
        "mc1_established":False, "native_geometry_qualified":False,
        "engineering_step_qualified":False,"production_authorized":False
    }


def attempt(spec):
    try:
        return analyze(spec)
    except (Refusal, ValueError, TypeError, KeyError, IndexError, OverflowError,
            ZeroDivisionError, MemoryError, RecursionError) as exc:
        return {"status":"REFUSED_NONTRUTH", "reason":str(exc),
                "pb00701_established":False, "mc_b_established":False,
                "production_authorized":False}


def historical_contract():
    corpus = read_json(CORPUS,CORPUS_BLOB)
    register = read_json(V2,V2_BLOB)
    rows = corpus["cases"]
    need(type(rows) is list and len(rows)==121, "V54_121_CORPUS_DRIFT")
    originals = {r["id"]: r for r in rows}
    need(len(originals)==121, "DUPLICATE_ORIGINAL_ID")
    refused = {r["id"] for r in rows if r["expected"]["v54_disposition"] == "BLOCKED"}
    missing = {r["id"] for r in rows if r["expected"]["v54_disposition"] == MISSING}
    need(len(refused)==20 and len(missing)==30, "HISTORICAL_V54_CLASSIFICATION_DRIFT")
    v2_rows = register["source_cases"]
    indexed = {r["case_id"]:r for r in v2_rows}
    need(len(v2_rows)==len(indexed)==50 and set(indexed)==refused | missing,
         "FIFTY_SOURCE_V2_REGISTER_DRIFT")
    for case_id,prior in indexed.items():
        row=originals[case_id]
        need(prior["origin"]==row["origin"] and
             prior["source_sha256"]==
             hashlib.sha256(canonical(row["spec"])).hexdigest() and
             prior["evidence"]["original_row_sha256"]==
             hashlib.sha256(canonical(row)).hexdigest() and
             prior["historical_v54_disposition"]==
             row["expected"]["v54_disposition"] and
             prior["registered_evidence_level"]=="COMPLETE_SOURCE_SPECIFIC",
             "EXISTING_V2_PROVENANCE_DRIFT")
    cases = {}
    for case_id in (V9,V43):
        row = originals[case_id]
        need(hashlib.sha256(canonical(row["spec"])).hexdigest()==PINNED[case_id],
             "PINNED_ORIGINAL_SOURCE_SHA256_DRIFT")
        need(row["expected"]["v54_disposition"] ==
             (MISSING if case_id==V9 else "BLOCKED"),
             "HISTORICAL_STATUS_DRIFT")
        cert = analyze(row["spec"])
        if case_id==V9:
            need(cert["total_isolated_roots"]==1 and
                 cert["maximal_nonzero_cell_signs"]==
                 ["NEGATIVE","POSITIVE"] and
                 [s["isolated_root_count"] for s in cert["spans"]]==[1,0],
                 "ORIGINAL_V9_SIGNED_ROOT_CONTRADICTION")
        else:
            need(cert["total_isolated_roots"]==0 and
                 cert["maximal_nonzero_cell_signs"]==["POSITIVE"] and
                 cert["spans"][0]["delta_direction"]=="DECREASING",
                 "ORIGINAL_HARVESTED_V43_SIGN_CONTRADICTION")
        cases[case_id] = {
            "original_source_sha256":PINNED[case_id],
            "original_row_sha256":indexed[case_id]["evidence"]["original_row_sha256"],
            "historical_v54_status":row["expected"]["v54_disposition"],
            "preexisting_v2_source_specific":True, "new_original_closure":False,
            "certificate":cert}
    return {
        "schema":SCHEMA,"task":"MC-038","evidence_class":"DETERMINISTIC_MODEL",
        "bounded_method":"PI_RATIONAL_ANGULAR_DRIFT_W_Q_ORIENTED_H1",
        "frozen_v54_git_blob":CORPUS_BLOB,"v2_git_blob":V2_BLOB,
        "population":{
            "before":{"frozen_originals":121,"route_refusals":20,
                      "missing_ordered_premises":30,"existing_v2_witnesses":50},
            "after":{"frozen_originals":121,"route_refusals":20,
                     "missing_ordered_premises":30,"existing_v2_witnesses":50},
            "delta":{"frozen_originals":0,"route_refusals":0,
                     "missing_ordered_premises":0,"existing_v2_witnesses":0},
            "newly_closed_historical_case_ids":[],
            "required_pb_po_discharges":0},
        "original_source_cases":cases,
        "pb00701_established":False,"pb00702_established":False,
        "pb00703_established":False,"pb00704_established":False,
        "mc_b_established":False,"mc1_established":False,
        "native_geometry_qualified":False,
        "engineering_step_qualified":False,
        "production_authorized":False,
        "supported_operations_unchanged":26}


def contract():
    actual = historical_contract()
    receipt = read_json(RECEIPT)
    need(canonical(actual)==canonical(receipt),
         "PINNED_RECEIPT_OR_PROOF_CLAIM_MISMATCH")
    return actual


def synthetic(c_values,s_values):
    """Original-like two-span degree-one source, exact shared knot."""
    def channel(vals):
        return {"degree":1, "knots":["0","0","1","1","2","2"],
                "controls":[str(v) for v in vals]}
    return {"grammar":GRAMMAR,"source_parameter_id":"source-time-t",
            "parameter_lo":"0","parameter_hi":"2",
            "phase_turn_offset":"0","phase_turn_rate":"1/8",
            "cos_splines":{"1":channel(c_values)},
            "sin_splines":{"1":channel(s_values)}}


def near_knot_control():
    """Prove two separate roots lie <2^-100 on either side of physical knot.

    Not a scan. Exact signs at 1±h follow sin(d)<d<11h/14,
    cos(d)>1-d^2/2>99/100, d=pi*h/4, h=2^-100.
    """
    h, eps = Q(1,2**100), Q(1,2**120)
    spec=synthetic(["-1"]*4,["0",str(1+eps),str(1+eps),"-1"])
    out=analyze(spec)
    need(out["total_isolated_roots"]==2 and
         out["maximal_nonzero_cell_signs"]==
         ["NEGATIVE","POSITIVE","NEGATIVE"] and
         all(s["isolated_root_count"]==1 for s in out["spans"]),
         "CLOSE_ROOT_PAIR_NOT_CERTIFIED")
    # t=1-h: F*sqrt(2)=(eps-(1+eps)h)*cos(d)
    #                      -(2+eps-(1+eps)h)*sin(d)<0.
    need(0 < eps < h and (2+eps)-(1+eps)*h > 0,
         "CLOSE_LEFT_SIGN_ASSUMPTIONS")
    # t=1+h: F*sqrt(2)=(eps-(2+eps)h)*cos(d)
    #                      +(2+eps-(2+eps)h)*sin(d).
    # As first coeff <0,  cos(d)>99/100, sin(d)<11h/14.
    upper=Q(99,100)*(eps-(2+eps)*h)+(2+eps)*Q(11,14)*h
    need(eps-(2+eps)*h<0 and upper<0 and
         Q(11,14)*h < Q(1,10), "CLOSE_RIGHT_STRICT_NEGATIVE_SIGN")
    return {"h":str(h),"epsilon":str(eps),
            "left_root_in":[str(1-h),"1"],
            "right_root_in":["1",str(1+h)],
            "strict_pair_distance_upper":str(2*h)}


class Tests(unittest.TestCase):
    def assert_refused(self, spec):
        result=attempt(spec)
        self.assertEqual(result["status"],"REFUSED_NONTRUTH")
        self.assertFalse(result["pb00701_established"])

    def test_exact_source_v54_v2_custody_and_prior_art(self):
        result=historical_contract()
        self.assertEqual(set(result["original_source_cases"]),set(PINNED))
        self.assertEqual(result["population"]["delta"],
                         {k:0 for k in result["population"]["delta"]})
        self.assertEqual(result["population"]["newly_closed_historical_case_ids"],[])

    def test_strict_nonstationary_orientation_decreasing(self):
        s=exact_span("1","1","-1/2","1/2")
        self.assertEqual(s["delta_direction"],"DECREASING")
        self.assertEqual(s["wronskian_local"],"1")
        self.assertEqual(s["q_min"],"1")
        self.assertEqual(s["q_max"],"5/4")
        self.assertLess(Q(s["strict_abs_delta_change_upper"]),3)

    def test_strict_nonstationary_orientation_increasing(self):
        s=exact_span("-1/2","1/2","1","1")
        self.assertEqual(s["delta_direction"],"INCREASING")
        self.assertEqual(s["wronskian_local"],"-1")
        self.assertEqual(s["q_min"],"1")

    def test_close_two_distinct_simple_roots_across_real_knot(self):
        witness=near_knot_control()
        self.assertEqual(Q(witness["strict_pair_distance_upper"]),Q(1,2**99))

    def test_identity_zero_shared_amplitude_and_tangency_refusals(self):
        self.assert_refused(synthetic(["0"]*4,["0"]*4))
        # Affine coefficient pair vanishes at interior u=1/2: source
        # physically has a tangential/multiple root, not admitted here.
        self.assert_refused(synthetic(["-1","1","1","1"],
                                      ["-1","1","1","1"]))
        self.assert_refused(synthetic(["0","0","-1","-1"],
                                      ["1","1","1","1"]))

    def test_knot_and_endpoint_zero_refusals(self):
        self.assert_refused(synthetic(["0","1","1","1"],["1"]*4))
        self.assert_refused(synthetic(["-1","-1","-1","-1"],["1","1","1","0"]))
        self.assert_refused(synthetic(["1","-1","-1","-1"],["1"]*4))

    def test_source_phase_knot_harmonic_and_continuity_refusals(self):
        base=synthetic(["-1"]*4,["0","1","1","-1"])
        for field,value in [("phase_turn_rate","1/9"),
                            ("phase_turn_offset","1/8"),
                            ("source_parameter_id","path-s")]:
            obj=copy.deepcopy(base)
            obj[field]=value
            self.assert_refused(obj)
        obj=copy.deepcopy(base)
        obj["cos_splines"]["1"]["knots"][2]="3/4"
        self.assert_refused(obj)
        obj=copy.deepcopy(base)
        obj["cos_splines"]["2"]=obj["cos_splines"]["1"]
        self.assert_refused(obj)
        obj=copy.deepcopy(base)
        obj["sin_splines"]["1"]["controls"][2]="3/2"
        self.assert_refused(obj)
        obj=copy.deepcopy(base)
        obj["cos_splines"]["1"]["degree"]=2
        self.assert_refused(obj)

    def test_resource_refusal_not_math_false(self):
        self.assert_refused(synthetic(["-1"]*4,
                                      ["0",str(Q(1,2**300)),
                                       str(Q(1,2**300)),"-1"]))

    def test_json_ingress_on_disk_adversaries(self):
        def check(data, ok=False):
            with tempfile.TemporaryDirectory() as directory:
                path=Path(directory)/"input.json"
                path.write_bytes(data)
                if ok:
                    return read_json(path)
                with self.assertRaises(Refusal):
                    read_json(path)
        check(b"["*10_000+b"null"+b"]"*10_000)
        check(b'{"n":'+b"9"*5000+b"}")
        check(b" "* (MAX_RAW_BYTES+1))
        check(b'{"a":false,"a":true}')
        check(b'{"a":NaN}')
        check(b'{"a":0.1}')
        check(b'{"a":"[\\\"{]"}',True)

    def test_receipt_false_promotions_rejected(self):
        evidence=historical_contract()
        for mutation in [
            ("population","after","missing_ordered_premises",28),
            ("population","delta","missing_ordered_premises",-2),
            ("production_authorized",True),
            ("pb00701_established",True),
        ]:
            obj=copy.deepcopy(evidence)
            if len(mutation)==4:
                obj[mutation[0]][mutation[1]][mutation[2]]=mutation[3]
            else:
                obj[mutation[0]]=mutation[1]
            self.assertNotEqual(canonical(obj),canonical(evidence))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--contract",action="store_true")
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--json",action="store_true")
    args=parser.parse_args()
    if args.self_test:
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            return 1
    if args.contract:
        try:
            result=contract()
        except Refusal as exc:
            print("REFUSED: "+str(exc))
            return 1
        print(json.dumps(result if args.json else {
            "status":"PASS","original_case_ids":list(PINNED),
            "new_historical_closures":0,"required_po_discharges":0
        },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
