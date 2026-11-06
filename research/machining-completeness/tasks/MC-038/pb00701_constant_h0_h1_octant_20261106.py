#!/usr/bin/env python3
"""Exact restricted constant-H0/H1 source-time event/sign transfer.

A source-side deterministic model, not a general analytic-event oracle.
No historical closure, native geometry, STEP, MC gate or production claim.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
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
LIMIT = 400000
INPUT_BITS = 512
DERIVED_BITS = 2048

class Refusal(ValueError):
    """An unproved/unadmitted source is NONTRUTH, not root-free."""

def require(ok, reason):
    if not ok:
        raise Refusal(reason)

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")

def checked_json(path, blob=None):
    with Path(path).open("rb") as f:
        raw = f.read(LIMIT + 1)
    require(len(raw) <= LIMIT, "RAW_BYTE_LIMIT")
    if blob:
        actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(actual == blob, "IMMUTABLE_GIT_BLOB_DRIFT")
    depth = 0
    quoted = False
    escape = False
    for c in raw:
        if quoted:
            if escape:
                escape = False
            elif c == 92:
                escape = True
            elif c == 34:
                quoted = False
        elif c == 34:
            quoted = True
        elif c in (91, 123):
            depth += 1
            require(depth <= 32, "JSON_DEPTH_LIMIT")
        elif c in (93, 125):
            depth -= 1
            require(depth >= 0, "JSON_DEPTH_MALFORMED")
    require(depth == 0 and not quoted, "JSON_STRUCTURE_MALFORMED")
    def pairs(items):
        out = {}
        for key, val in items:
            require(key not in out, "DUPLICATE_JSON_KEY")
            out[key] = val
        return out
    def integer(token):
        require(len(token) <= 12, "INTEGER_TOKEN_LIMIT")
        return int(token)
    def noninteger(_):
        raise Refusal("NONINTEGER_JSON_NUMBER")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                          parse_int=integer, parse_float=noninteger,
                          parse_constant=noninteger)
    except Refusal:
        raise
    except (UnicodeError, ValueError, RecursionError, OverflowError) as exc:
        raise Refusal("INVALID_JSON") from exc

def budget(value, limit=DERIVED_BITS):
    require(isinstance(value, Q), "NONRATIONAL")
    require(max(abs(value.numerator).bit_length(),
                value.denominator.bit_length()) <= limit, "EXACT_BIT_BUDGET")

def rat(raw):
    require(type(raw) is str and 0 < len(raw) <= 640, "RATIONAL_TOKEN_LIMIT")
    try:
        result = Q(raw)
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise Refusal("INVALID_RATIONAL") from exc
    require(str(result) == raw, "NONCANONICAL_RATIONAL")
    budget(result, INPUT_BITS)
    return result

def sgn(value):
    return (value > 0) - (value < 0)

def sqrt2_sign(a, b):
    """Sign of exact rational a + b*sqrt(2), without floating point."""
    budget(a)
    budget(b)
    if not a:
        return sgn(b)
    if not b or sgn(a) == sgn(b):
        return sgn(a)
    lhs, rhs = a * a, 2 * b * b
    budget(lhs)
    budget(rhs)
    require(lhs != rhs, "IMPOSSIBLE_NONZERO_RATIONAL_SQRT2_EQUALITY")
    return sgn(a) if lhs > rhs else sgn(b)

HALF = Q(1, 2)
# cos(k*pi/4), sin(k*pi/4) as pairs (rational, sqrt(2) coefficient).
OCTANTS = (
    ((Q(1), Q(0)), (Q(0), Q(0))),
    ((Q(0), HALF), (Q(0), HALF)),
    ((Q(0), Q(0)), (Q(1), Q(0))),
    ((Q(0), -HALF), (Q(0), HALF)),
    ((Q(-1), Q(0)), (Q(0), Q(0))),
    ((Q(0), -HALF), (Q(0), -HALF)),
    ((Q(0), Q(0)), (Q(-1), Q(0))),
    ((Q(0), HALF), (Q(0), -HALF)),
)

def endpoint_signs(h, c, s, rate, k):
    co, si = OCTANTS[k % 8]
    f = sqrt2_sign(h + c * co[0] + s * si[0],
                   c * co[1] + s * si[1])
    d = sqrt2_sign(rate * (-c * si[0] + s * co[0]),
                   rate * (-c * si[1] + s * co[1]))
    return f, d

def critical_sign(h, q, kind):
    """Exact sign of h - sqrt(q) (MIN) or h + sqrt(q) (MAX)."""
    budget(q)
    require(q > 0, "ZERO_H1_VECTOR")
    if kind == "MIN":
        if h <= 0:
            return -1
        return sgn(h * h - q)
    require(kind == "MAX", "CRITICAL_KIND")
    if h >= 0:
        return 1
    return -sgn(h * h - q)

def cell_count(f0, f1, d0, d1, h, q):
    require(f0 != 0 and f1 != 0, "PHYSICAL_NODE_ZERO")
    require(not (d0 == 0 and d1 == 0), "DERIVATIVE_ENDPOINT_DEGENERACY")
    # The phase traverses exactly pi/4, shorter than pi. Consecutive
    # derivative zeros of nonzero constant phasor are pi apart.
    if d0 == 0 or d1 == 0 or d0 == d1:
        return int(f0 != f1), 1, "MONOTONE"
    kind = "MIN" if d0 < 0 else "MAX"
    ext = critical_sign(h, q, kind)
    if ext == 0:
        require(f0 == f1 == (1 if kind == "MIN" else -1),
                "TANGENCY_SIGN_CONTRADICTION")
        return 1, 2, "INTERIOR_ORDER_TWO_" + kind
    number = int(f0 != ext) + int(f1 != ext)
    require(number != 2, "TWO_ROOTS_SAME_OCTANT_UNBRACKETED")
    return number, 1, "INTERIOR_" + kind

def certify(spec):
    keys = {"source_parameter_id", "parameter_lo", "parameter_hi",
            "h0", "h1_cos", "h1_sin",
            "phase_turn_offset", "phase_turn_rate"}
    require(type(spec) is dict and set(spec) == keys, "SOURCE_FIELDS")
    require(spec["source_parameter_id"] == "source-time-t", "SOURCE_PARAMETER")
    lo, hi = rat(spec["parameter_lo"]), rat(spec["parameter_hi"])
    h, c, s = rat(spec["h0"]), rat(spec["h1_cos"]), rat(spec["h1_sin"])
    off, rate = rat(spec["phase_turn_offset"]), rat(spec["phase_turn_rate"])
    require(Q(0) <= lo < hi <= Q(2) and rate != 0 and abs(rate) <= 4,
            "DOMAIN_OR_NONSTATIONARY_PHASE")
    q = c*c + s*s
    budget(q)
    require(q > 0, "ZERO_H1_VECTOR")
    x0, x1 = 8 * (off + rate*lo), 8 * (off + rate*hi)
    require(x0.denominator == x1.denominator == 1, "NONOCTANT_EXTERIOR")
    n = abs(int(x1-x0))
    require(0 < n <= 128, "OCTANT_CELL_BUDGET")
    step = sgn(rate)
    indices = [int(x0)+i*step for i in range(n+1)]
    nodes = [(Q(k, 8)-off)/rate for k in indices]
    require(nodes[0] == lo and nodes[-1] == hi and
            all(nodes[i] < nodes[i+1] for i in range(n)),
            "SOURCE_NODE_ORDER")
    signs, derivatives = [], []
    for k in indices:
        f, d = endpoint_signs(h, c, s, rate, k)
        require(f != 0, "PHYSICAL_OCTANT_NODE_ZERO")
        signs.append(f)
        derivatives.append(d)
    events, details = [], []
    current, regions = signs[0], ["POSITIVE" if signs[0] > 0 else "NEGATIVE"]
    for i in range(n):
        count, order, method = cell_count(
            signs[i], signs[i+1], derivatives[i], derivatives[i+1], h, q)
        if count:
            events.append({"strict_rational_bracket": [str(nodes[i]), str(nodes[i+1])],
                           "multiplicity": order, "event_kind":
                           "TANGENCY" if order == 2 else "SIMPLE_CROSSING"})
            if order == 1:
                current = -current
            regions.append("POSITIVE" if current > 0 else "NEGATIVE")
        require(current == signs[i+1], "SIGNED_CELL_TRANSFER_CONTRADICTION")
        details.append({"cell": [str(nodes[i]), str(nodes[i+1])],
                        "endpoint_signs": [signs[i], signs[i+1]],
                        "derivative_signs": [derivatives[i], derivatives[i+1]],
                        "method": method, "root_count": count})
    return {"status": "COMPLETE_RESTRICTED_CONSTANT_H0_H1_OCTANT_SOURCE",
            "evidence_class": "DETERMINISTIC_MODEL",
            "source_sha256": hashlib.sha256(canonical(spec)).hexdigest(),
            "octant_nodes": [str(t) for t in nodes],
            "node_signs": ["POSITIVE" if x > 0 else "NEGATIVE" for x in signs],
            "ordered_events": events, "ordered_signed_regions": regions,
            "root_count": len(events), "cell_certificates": details,
            "new_historical_closures": [], "required_pb_po_discharges": 0,
            "pb00701_established": False, "mc_b_established": False,
            "mc1_established": False, "production_authorized": False}

def attempt(spec):
    try:
        return certify(spec)
    except (Refusal, ValueError, TypeError, IndexError, KeyError,
            OverflowError, ZeroDivisionError, RecursionError, MemoryError) as exc:
        return {"status": "REFUSED_NONTRUTH", "reason": str(exc),
                "pb00701_established": False, "mc1_established": False}

def source(h="7/10", c="2/3", s="-1/3", off="0", rate="1/4",
           lo="1", hi="2"):
    return {"source_parameter_id": "source-time-t",
            "parameter_lo": lo, "parameter_hi": hi,
            "h0": h, "h1_cos": c, "h1_sin": s,
            "phase_turn_offset": off, "phase_turn_rate": rate}

def original_v12():
    return {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "source_parameter_id": "source-time-t",
        "parameter_lo": "0", "parameter_hi": "2",
        "phase_turn_offset": "0", "phase_turn_rate": "1/4",
        "cos_splines": {
            "0": {"degree": 0, "knots": ["0","1","2"], "controls": ["0","0"]},
            "1": {"degree": 1, "knots": ["0","0","1","1","2","2"],
                  "controls": ["-1/3","2/3","2/3","2/3"]}},
        "sin_splines": {
            "1": {"degree": 1, "knots": ["0","0","1","1","2","2"],
                  "controls": ["2/3","-1/3","-1/3","-1/3"]}}
    }

def historical_contract():
    rows = checked_json(CORPUS, V54_BLOB)["cases"]
    v2 = checked_json(V2, V2_BLOB)["source_cases"]
    require(type(rows) is list and len(rows) == 121, "ORIGINAL_121")
    by_id = {r["id"]: r for r in rows}
    require(len(by_id) == 121, "ORIGINAL_IDS")
    refused = {r["id"] for r in rows
               if r["expected"]["v54_disposition"] == "BLOCKED"}
    missing = {r["id"] for r in rows if r["expected"]["v54_disposition"] ==
               "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"}
    require(len(refused) == 20 and len(missing) == 30 and not refused & missing,
            "HISTORICAL_FRONTIER")
    require(type(v2) is list and len(v2) == 50 and
            {p["case_id"] for p in v2} == refused | missing, "V2_50")
    for entry in v2:
        row = by_id[entry["case_id"]]
        require(entry["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC" and
                entry["source_sha256"] == hashlib.sha256(canonical(row["spec"])).hexdigest()
                and entry["evidence"]["original_row_sha256"] ==
                hashlib.sha256(canonical(row)).hexdigest(), "V2_CUSTODY")
    row = by_id[V12]
    require(hashlib.sha256(canonical(row["spec"])).hexdigest() == SOURCE_SHA and
            hashlib.sha256(canonical(row)).hexdigest() == ROW_SHA and
            row["spec"] == original_v12(), "FROZEN_V12_DRIFT")
    # Only the historical H1 constant tail is extracted. H0 is prospective.
    tail = source(h="7/10",
                  c=row["spec"]["cos_splines"]["1"]["controls"][2],
                  s=row["spec"]["sin_splines"]["1"]["controls"][2],
                  off=row["spec"]["phase_turn_offset"],
                  rate=row["spec"]["phase_turn_rate"])
    require(row["spec"]["cos_splines"]["1"]["controls"][2:] == ["2/3","2/3"]
            and row["spec"]["sin_splines"]["1"]["controls"][2:] == ["-1/3","-1/3"]
            and row["spec"]["cos_splines"]["0"]["controls"] == ["0","0"],
            "NOT_CONSTANT_ORIGINAL_TAIL")
    positive = certify(tail)
    negative = certify({**tail, "h0": "3/4"})
    require(positive["ordered_events"] == [
                {"strict_rational_bracket":["1","3/2"],
                 "multiplicity":1,"event_kind":"SIMPLE_CROSSING"},
                {"strict_rational_bracket":["3/2","2"],
                 "multiplicity":1,"event_kind":"SIMPLE_CROSSING"}] and
            positive["ordered_signed_regions"] ==
            ["POSITIVE","NEGATIVE","POSITIVE"] and
            negative["root_count"] == 0, "V12_BIASED_TAIL_EVENT_CONTRADICTION")
    return {"frozen_original": V12, "v54_git_blob": V54_BLOB,
            "v2_git_blob": V2_BLOB, "original_source_sha256": SOURCE_SHA,
            "original_row_sha256": ROW_SHA,
            "historical_before_after": {"originals": 121, "refused": 20,
                                       "missing_ordered": 30, "prior_complete": 50},
            "historical_deltas": {"originals": 0, "refused": 0,
                                  "missing_ordered": 0, "prior_complete": 0},
            "prospective_h0_7_10_tail": positive,
            "prospective_h0_3_4_tail": negative,
            "newly_closed_originals": [], "required_pb_po_discharges": 0,
            "pb00701_established": False, "mc_b_established": False,
            "mc1_established": False, "production_authorized": False}

class Tests(unittest.TestCase):
    def refuses(self, spec):
        self.assertEqual(attempt(spec)["status"], "REFUSED_NONTRUTH")

    def test_v12_prospective_positive_two_ordered_simple_events(self):
        out = certify(source())
        self.assertEqual(out["root_count"], 2)
        self.assertEqual(out["node_signs"], ["POSITIVE","NEGATIVE","POSITIVE"])
        self.assertEqual(out["ordered_signed_regions"],
                         ["POSITIVE","NEGATIVE","POSITIVE"])
        self.assertTrue(all(e["multiplicity"] == 1 for e in out["ordered_events"]))

    def test_v12_prospective_root_free_control(self):
        out = certify(source(h="3/4"))
        self.assertEqual(out["root_count"], 0)
        self.assertEqual(out["node_signs"], ["POSITIVE"]*3)

    def test_exact_irrational_phase_order_two_tangency(self):
        out = certify(source(h="1", c="-3/5", s="-4/5",
                             off="1/8", rate="1/8", lo="0", hi="1"))
        self.assertEqual(out["root_count"], 1)
        self.assertEqual(out["ordered_events"][0]["multiplicity"], 2)
        self.assertEqual(out["ordered_signed_regions"], ["POSITIVE","POSITIVE"])

    def test_two_hidden_roots_inside_one_octant_refuse(self):
        # Both endpoints positive, unique internal min h - sqrt(1) < 0.
        self.refuses(source(h="199/200", c="-3/5", s="-4/5",
                            off="1/8", rate="1/8", lo="0", hi="1"))

    def test_negative_rate_with_real_simple_crossing(self):
        out = certify(source(h="0", c="1", s="1/2",
                             off="3/8", rate="-1/4", lo="0", hi="1"))
        self.assertEqual(out["root_count"], 1)
        self.assertEqual(out["ordered_signed_regions"], ["NEGATIVE","POSITIVE"])

    def test_node_zero_and_zero_h1_vector_refuse(self):
        self.refuses(source(h="0", c="1", s="0",
                            off="3/8", rate="-1/4", lo="0", hi="1"))
        self.refuses(source(c="0", s="0"))

    def test_exact_sqrt2_no_float_and_strict_source_grammar(self):
        self.assertEqual(sqrt2_sign(Q(7,10), -Q(1,2)), -1)
        self.assertEqual(sqrt2_sign(Q(3,4), -Q(1,2)), 1)
        self.refuses({**source(), "h0": "0.7"})
        self.refuses({**source(), "phase_turn_rate": "0"})
        self.refuses({**source(), "h1_cos": "1"*5000})

    def test_bounded_disk_json_refusals(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"source.json"
            for raw in (b'{"h0":1,"h0":2}', b'['*40+b'0'+b']'*40,
                        b'{"integer":'+b'1'*5000+b'}',
                        b'{"x":NaN}', b' '*400001):
                path.write_bytes(raw)
                with self.assertRaises(Refusal):
                    checked_json(path)
            # Many brackets inside a JSON string do not consume nesting budget.
            path.write_text(json.dumps({"x": "["*200}), encoding="utf-8")
            self.assertEqual(checked_json(path)["x"], "["*200)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--source", type=Path)
    args = ap.parse_args()
    if args.contract:
        print(json.dumps(historical_contract(), indent=2, sort_keys=True))
    if args.self_test:
        run = unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
        if not run.wasSuccessful():
            raise SystemExit(1)
    if args.source:
        try:
            result = attempt(checked_json(args.source))
        except (OSError, Refusal) as e:
            result = {"status": "REFUSED_NONTRUTH", "reason": str(e),
                      "pb00701_established": False, "mc1_established": False}
        print(json.dumps(result, indent=2, sort_keys=True))
    if not (args.contract or args.self_test or args.source):
        ap.print_help()

if __name__ == "__main__":
    main()
