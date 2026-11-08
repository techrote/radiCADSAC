#!/usr/bin/env python3
"""Exact two-right-root theorem at a genuine nonzero V6-like source knot.

Research-only deterministic prospective source. No historical or gate promotion.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "pb00701-finite-owner-corpus-v54.json"
V2 = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
RECEIPT = HERE / "pb00701-v6-nonzero-knot-two-roots-20261108.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
ORIGINAL_ID = "composite:DELEGATED_V6_CONSTANT_MODULATION:tail0"
ORIGINAL_SOURCE_SHA = "9eb6f08a44882adffa919529247c40190c70e8d7599ee2b1a0f7978ef2569eb1"
MAX_FILE_BYTES = 400000
MAX_RECEIPT_BYTES = 16000

class Refusal(ValueError):
    """Typed NONTRUTH for unsupported or tampered input."""

def require(cond, reason):
    if not cond:
        raise Refusal(reason)

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")

def unique_pairs(pairs):
    obj = {}
    for k, v in pairs:
        require(k not in obj, "DUPLICATE_JSON_KEY")
        obj[k] = v
    return obj

def parse_bounded(raw, budget):
    require(len(raw) <= budget, "INPUT_BYTE_BUDGET")
    depth, in_string, escaped = 0, False, False
    for c in raw:
        if in_string:
            if escaped:
                escaped = False
            elif c == 92:
                escaped = True
            elif c == 34:
                in_string = False
        elif c == 34:
            in_string = True
        elif c in (91, 123):
            depth += 1
            require(depth <= 32, "JSON_DEPTH_BUDGET")
        elif c in (93, 125):
            depth -= 1
            require(depth >= 0, "JSON_BRACKET_ORDER")
    require(depth == 0 and not in_string, "JSON_NESTING")
    def limited_int(s):
        require(len(s) <= 12, "JSON_INTEGER_BUDGET")
        return int(s)
    def reject(_):
        raise Refusal("NONINTEGER_JSON_NUMBER")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs,
                          parse_int=limited_int, parse_float=reject,
                          parse_constant=reject)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise Refusal("INVALID_JSON") from exc

def read_bounded(path, budget):
    with path.open("rb") as f:
        return f.read(budget + 1)

def frozen(path, blob):
    raw = read_bounded(path, MAX_FILE_BYTES)
    require(len(raw) <= MAX_FILE_BYTES, "FROZEN_FILE_TOO_LARGE")
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\\0" + raw).hexdigest()
    require(actual == blob, "FROZEN_GIT_BLOB_DRIFT")
    return parse_bounded(raw, MAX_FILE_BYTES)

def rational(s):
    require(type(s) is str and 0 < len(s) <= 160 and
            all(c in "0123456789-/" for c in s), "INVALID_RATIONAL_TOKEN")
    try:
        value = Fraction(s)
    except (ZeroDivisionError, ValueError) as exc:
        raise Refusal("INVALID_RATIONAL") from exc
    require(str(value) == s, "NONCANONICAL_RATIONAL")
    require(max(abs(value.numerator).bit_length(),
                value.denominator.bit_length()) <= 256, "RATIONAL_BIT_BUDGET")
    return value

def certify(m_text, b_text, *, phase="t/4", claim_original=False):
    require(phase == "t/4" and claim_original is False,
            "UNSUPPORTED_PHASE_OR_ORIGINAL_IDENTITY")
    m, b = rational(m_text), rational(b_text)
    q = m + b / 2
    # Strict rational sufficient conditions. F_R(1/2)=q-sqrt(2)/2.
    require(m > 0 and m + b > 1 and q > 0 and 2*q*q < 1,
            "TWO_ROOT_CONVEXITY_PRECONDITION_NOT_PROVEN")
    zero1 = {"source_time": None, "open_rational_source_bracket": ["1", "3/2"],
             "kind": "SIMPLE_CROSSING", "left_sign": "POSITIVE",
             "right_sign": "NEGATIVE", "one_sided_orders": [1, 1]}
    zero2 = {"source_time": None, "open_rational_source_bracket": ["3/2", "2"],
             "kind": "SIMPLE_CROSSING", "left_sign": "NEGATIVE",
             "right_sign": "POSITIVE", "one_sided_orders": [1, 1]}
    return {
        "evidence_class": "DETERMINISTIC_MODEL",
        "result": "EXACT_PROSPECTIVE_TWO_RIGHT_ROOTS_NONZERO_KNOT",
        "source_parameter": "source-time-t",
        "interval": ["0", "2"],
        "phase_turns": "t/4",
        "degree": 2,
        "knots": ["0", "0", "0", "1", "1", "2", "2", "2"],
        "parameters": {"m": str(m), "b": str(b)},
        "source_controls": {
            "H0": [str(m), str(m), str(m), str(m + b/2), str(m + b)],
            "H1_cos": ["1"] * 5, "H1_sin": ["0"] * 5},
        "physical_left": "m+cos(pi*t/2)",
        "physical_right": "m+b*x-sin(pi*x/2); x=t-1",
        "true_knot": {"source_time": "1", "value": str(m),
                      "zero": False, "event": False,
                      "left_inward_sign": "POSITIVE",
                      "right_inward_sign": "POSITIVE"},
        "strict_exact_conditions": ["m>0", "m+b>1",
                                    "q=m+b/2>0", "2*q^2<1"],
        "strict_convexity": "F_right_second=(pi/2)^2*sin(pi*x/2)>0 for 0<x<1",
        "critical_midpoint_sign": "NEGATIVE_BY_EXACT_SQUARE_COMPARISON",
        "ordered_physical_events": [zero1, zero2],
        "maximal_nonzero_signs": ["POSITIVE", "NEGATIVE", "POSITIVE"],
        "physical_zero_count": 2,
        "original_source_case": None,
        "new_original_witnesses": [],
        "required_pb_po_discharges": 0,
        "pb00701_established": False,
        "mc_b_established": False,
        "mc1_established": False,
        "production_authorized": False,
    }

def custody():
    v54 = frozen(CORPUS, CORPUS_BLOB)
    v2 = frozen(V2, V2_BLOB)
    cases, witnesses = v54["cases"], v2["source_cases"]
    require(len(cases) == len({x["id"] for x in cases}) == 121,
            "FROZEN_CENSUS")
    blocked = [x for x in cases if x["expected"]["v54_disposition"] == "BLOCKED"]
    missing = [x for x in cases if x["expected"]["v54_disposition"] ==
               "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"]
    require(len(blocked) == 20 and len(missing) == 30 and
            len(witnesses) == 50 and
            len({x["case_id"] for x in witnesses}) == 50,
            "FROZEN_WITNESS_CENSUS")
    row = next(x for x in cases if x["id"] == ORIGINAL_ID)
    spec = row["spec"]
    require(hashlib.sha256(canonical(spec)).hexdigest() == ORIGINAL_SOURCE_SHA,
            "FROZEN_REFERENCE_SHA")
    require(spec["source_parameter_id"] == "source-time-t" and
            (spec["parameter_lo"], spec["parameter_hi"]) == ("0", "2") and
            (spec["phase_turn_offset"], spec["phase_turn_rate"]) ==
            ("0", "1/4") and not spec["sin_splines"] and
            spec["cos_splines"]["1"] ==
            {"degree": 0, "knots": ["0", "1", "2"], "controls": ["1", "1"]},
            "FROZEN_REFERENCE_GRAMMAR")
    return {
        "frozen_v54_blob": CORPUS_BLOB,
        "frozen_v2_blob": V2_BLOB,
        "reference_original_id": ORIGINAL_ID,
        "reference_source_sha256": ORIGINAL_SOURCE_SHA,
        "reference_only_not_same_h0": True,
        "historical": {"originals": 121, "route_refusals": 20,
                       "missing_ordered_premises": 30,
                       "preexisting_v2_witnesses": 50,
                       "newly_closed_originals": 0,
                       "required_pb_po_discharges": 0},
    }

def expected_receipt():
    return {"schema": "radicadsac-mc038-v6-nonzero-knot-two-roots/1.0",
            "prospective": True,
            "custody": custody(),
            "certificate": certify("1/5", "9/10")}

def verify_receipt_bytes(raw):
    actual = parse_bounded(raw, MAX_RECEIPT_BYTES)
    require(canonical(actual) == canonical(expected_receipt()),
            "RECEIPT_CLAIM_OR_TYPE_DRIFT")
    return actual

def contract():
    return verify_receipt_bytes(read_bounded(RECEIPT, MAX_RECEIPT_BYTES))

class Tests(unittest.TestCase):
    def test_literal_receipt_and_frozen_reference(self):
        self.assertEqual(contract(), expected_receipt())

    def test_two_exact_open_brackets_and_nonzero_knot(self):
        c = certify("1/5", "9/10")
        self.assertEqual(c["physical_zero_count"], 2)
        self.assertEqual(c["ordered_physical_events"][0]
                         ["open_rational_source_bracket"], ["1", "3/2"])
        self.assertEqual(c["ordered_physical_events"][1]
                         ["open_rational_source_bracket"], ["3/2", "2"])
        self.assertEqual(c["maximal_nonzero_signs"],
                         ["POSITIVE", "NEGATIVE", "POSITIVE"])
        self.assertEqual(c["true_knot"]["value"], "1/5")
        self.assertFalse(c["true_knot"]["event"])

    def test_rational_open_region(self):
        for m,b in (("1/5","9/10"), ("1/4","4/5"), ("1/3","7/10")):
            self.assertEqual(certify(m,b)["physical_zero_count"], 2)

    def test_refusal_outside_proven_region(self):
        for m,b in (("0","9/10"), ("1/5","4/5"), ("1/5","2"),
                    ("-1","2"), ("1/5","0"), ("1/4","3/4")):
            with self.subTest(m=m,b=b), self.assertRaises(Refusal):
                certify(m,b)

    def test_refusal_of_noncanonical_and_false_original(self):
        for s in ("01/5", "0/0", "1e-5", "1/0", "1/1",
                  "1/" + str(2**300)):
            with self.subTest(token=s), self.assertRaises(Refusal):
                certify(s,"9/10")
        for kw in ({"phase":"t/8"}, {"claim_original":True}):
            with self.assertRaises(Refusal):
                certify("1/5","9/10",**kw)

    def test_exact_quadratic_bspline_controls(self):
        knots = [Fraction(x) for x in ("0","0","0","1","1","2","2","2")]
        def basis(i,p,t):
            if p == 0:
                return Fraction(int(knots[i] <= t < knots[i+1]))
            a,b = knots[i+p]-knots[i], knots[i+p+1]-knots[i+1]
            return ((t-knots[i])*basis(i,p-1,t)/a if a else 0) + (
                (knots[i+p+1]-t)*basis(i+1,p-1,t)/b if b else 0)
        for m,b in ((Fraction(1,5),Fraction(9,10)),
                    (Fraction(1,4),Fraction(4,5))):
            c=certify(str(m),str(b))
            for name,controls in c["source_controls"].items():
                co=[Fraction(z) for z in controls]
                for t in map(Fraction,("0","1/4","1/2","1","5/4","3/2","7/4","2")):
                    actual = co[-1] if t == 2 else sum(
                        (co[i]*basis(i,2,t) for i in range(5)), Fraction(0))
                    x=t-1
                    want=(m if t <= 1 else m+b*x) if name=="H0" else (
                        Fraction(1) if name=="H1_cos" else Fraction(0))
                    self.assertEqual(actual,want)

    def test_mutated_receipts_and_duplicate_keys_refused(self):
        import copy
        orig=expected_receipt()
        for key, val in (("physical_zero_count",3),
                         ("maximal_nonzero_signs",["POSITIVE"]*3),
                         ("pb00701_established",True),
                         ("production_authorized",True),
                         ("required_pb_po_discharges",False)):
            x=copy.deepcopy(orig)
            x["certificate"][key]=val
            with self.subTest(key=key), self.assertRaises(Refusal):
                verify_receipt_bytes(canonical(x))
        for raw in (canonical(orig).replace(b'"schema":', b'"schema":"BAD","schema":',1),
                    b'['*33+b'0'+b']'*33,
                    b' '* (MAX_RECEIPT_BYTES+1),
                    b'{"x":'+b'9'*5000+b'}',
                    b'{"x":NaN}',b'{"x":1.25}',b'{"x":[1}}'):
            with self.subTest(raw=raw[:40]), self.assertRaises(Refusal):
                verify_receipt_bytes(raw)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--contract",action="store_true")
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.contract:
        contract()
        print(json.dumps(expected_receipt(),sort_keys=True))
    if args.self_test:
        result=unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
        if not result.wasSuccessful():
            raise SystemExit(1)
    if not (args.contract or args.self_test):
        p.error("use --contract and/or --self-test")

if __name__=="__main__":
    main()
