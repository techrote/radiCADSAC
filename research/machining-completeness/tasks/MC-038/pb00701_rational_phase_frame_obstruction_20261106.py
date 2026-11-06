#!/usr/bin/env python3
"""Exact source-bound H1 rational-phase-frame obstruction; not a root solver.

The proposed information-preserving route seeks C=A*cos(theta), S=A*sin(theta)
with rational theta(t) and arbitrary differentiable real nonzero amplitude A.
For affine C,S, W=C*S'-S*C' is constant and q=C*C+S*S is quadratic.
When W!=0, W/q has nonzero simple complex-pole residues, while the derivative
of any rational function has zero residues. This excludes the proposed route.
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
RECEIPT = HERE / "pb00701-rational-phase-frame-obstruction-20261106.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
SCHEMA = "radicadsac-mc038-h1-rational-phase-obstruction/1.0"
MISSING = "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"
MAX_RAW_BYTES = 400_000
MAX_JSON_DEPTH = 32
MAX_JSON_INTEGER_DIGITS = 12
MAX_JSON_INTEGER_ABS = 1 << 40
MAX_Q_BITS = 256

# IDs/SHA-256 are original frozen source identities, not generated examples.
PINNED = {
    "V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC": "a7131bea021c5c71d0da2682cd6d4c1a982e8c86196c818ad3f69a926afda2e5",
    "V14_EXACT_STRICT_DOMINANCE_MULTITERM_MULTIPLIER": "bd10ad1d9503335b2d7f745c09805b82a421b8db7beea67329cf33d0c9d78ff2",
    "V15_EXACT_FINITE_STRICT_DOMINANCE_MULTIPLIER": "8e41009417dd65f9a47a04b492dd9a91b88a7682f12f45305ce64ac38dffd7b7",
    "V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER": "e85d997c9f4d828b1b748c964b375c21e4acef1b1e9046e074b1f7e29011d08f",
    "V18_EXACT_LAURENT_MODULE_FACTOR": "ed61c9b827417327b9dda32ec0469ba5f0eab9622fb531d4b1bc959a312aa4a1",
    "V24_EXACT_MIXED_QUADRATURE_PHASE_ANCHOR": "e565ddf6bb0bab080128aeda16be5ea60466b3b971aa98d0408ea9a96da3d052",
    "V38_EXACT_DIRECT_ROTATED_COORDINATE_TWO_QUADRATURE": "9b7429ae290de259b2990b39740f40495c02b407e4e906e7eece77ea65c43f03",
    "V39_EXACT_SIGNED_A_DIRECT_ROTATED_COORDINATE": "daeafb37dd81d27fbba1c97dd09b14767531e37046237449aab3eaa9adfc1061",
    "V40_EXACT_SIGNED_B_ANTI_DIAGONAL_DIRECT_ROTATED_COORDINATE": "90a5df370094bcd8cef37be171f9bb12264c15a32237300b5435dc8871c6c2bf",
    "V43_EXACT_CORRELATED_CLOSED_HANDOFF": "28cd4b4be4c74e6404b1a307d2217b2dc5a8b708b28c5ad75309c35e48092efd",
}
EXPECTED_W = {
    "V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC": "-5/4",
    "V14_EXACT_STRICT_DOMINANCE_MULTITERM_MULTIPLIER": "-21/16",
    "V15_EXACT_FINITE_STRICT_DOMINANCE_MULTIPLIER": "-85/16",
    "V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER": "-5/4",
    "V18_EXACT_LAURENT_MODULE_FACTOR": "-5/4",
    "V24_EXACT_MIXED_QUADRATURE_PHASE_ANCHOR": "0",
    "V38_EXACT_DIRECT_ROTATED_COORDINATE_TWO_QUADRATURE": "-1/50",
    "V39_EXACT_SIGNED_A_DIRECT_ROTATED_COORDINATE": "-1/50",
    "V40_EXACT_SIGNED_B_ANTI_DIAGONAL_DIRECT_ROTATED_COORDINATE": "1/5",
    "V43_EXACT_CORRELATED_CLOSED_HANDOFF": "7/240",
}

class Refusal(ValueError):
    pass

def need(ok, why):
    if not ok:
        raise Refusal(why)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")

def duplicate_key_reject(pairs):
    result = {}
    for k, v in pairs:
        need(k not in result, "DUPLICATE_JSON_KEY")
        result[k] = v
    return result

def json_nesting_guard(raw):
    """Bound JSON container depth before Python's recursive decoder runs.

    Quoted brackets and escaped quotes/backslashes do not change nesting.
    JSON syntax, bracket kinds and UTF-8 are checked by json.loads below.
    """
    depth = 0
    quoted = False
    escaped = False
    for byte in raw:
        if quoted:
            if escaped:
                escaped = False
            elif byte == 92:  # backslash
                escaped = True
            elif byte == 34:  # double quote
                quoted = False
        elif byte == 34:
            quoted = True
        elif byte in (91, 123):  # [ {
            depth += 1
            need(depth <= MAX_JSON_DEPTH, "JSON_DEPTH_BUDGET")
        elif byte in (93, 125):  # ] }
            depth -= 1
            need(depth >= 0, "JSON_UNBALANCED_BRACKETS")
    need(not quoted and depth == 0, "JSON_UNCLOSED_STRUCTURE")


def bounded_json_integer(token):
    """Frozen source metadata uses small integer fields, not floats."""
    need(len(token) <= MAX_JSON_INTEGER_DIGITS, "JSON_INTEGER_DIGIT_BUDGET")
    value = int(token)
    need(abs(value) <= MAX_JSON_INTEGER_ABS, "JSON_INTEGER_VALUE_BUDGET")
    return value


def refuse_json_float(_):
    raise Refusal("JSON_FLOAT_NOT_ADMITTED")


def read_json(path, expected_blob=None):
    # Never allocate an entire adversarial file to discover its size afterward.
    try:
        with path.open("rb") as source:
            raw = source.read(MAX_RAW_BYTES + 1)
    except OSError as exc:
        raise Refusal("JSON_READ_FAILURE") from exc
    need(len(raw) <= MAX_RAW_BYTES, "RAW_FILE_BUDGET")
    if expected_blob:
        actual = hashlib.sha1(b"blob " + str(len(raw)).encode() +
                              b"\0" + raw).hexdigest()
        need(actual == expected_blob, "PINNED_GIT_BLOB_DRIFT")
    json_nesting_guard(raw)
    try:
        return json.loads(
            raw,
            object_pairs_hook=duplicate_key_reject,
            parse_int=bounded_json_integer,
            parse_float=refuse_json_float,
            parse_constant=lambda _: (_ for _ in ()).throw(Refusal("NONFINITE_JSON")),
        )
    except Refusal:
        raise
    except (ValueError, RecursionError, UnicodeError, OverflowError, TypeError) as exc:
        raise Refusal("INVALID_OR_EXCESSIVE_JSON") from exc

def rational(token):
    need(type(token) is str and 0 < len(token) <= 128, "INVALID_RATIONAL")
    try:
        x = Q(token)
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise Refusal("INVALID_RATIONAL") from exc
    need(str(x) == token, "NONCANONICAL_RATIONAL")
    need(max(abs(x.numerator).bit_length(), x.denominator.bit_length()) <= MAX_Q_BITS,
         "RATIONAL_BIT_BUDGET")
    return x

def affine_certificate(c0, c1, s0, s1):
    """Exact general lemma for first-span affine H1 coefficient pair."""
    a, b, c, d = (rational(x) for x in (c0, c1, s0, s1))
    dc, ds = b-a, d-c
    w = a*ds-c*dc
    q0, q1, q2 = a*a+c*c, 2*(a*dc+c*ds), dc*dc+ds*ds
    delta = q1*q1-4*q0*q2
    need(delta == -4*w*w, "WRONSKIAN_DISCRIMINANT_IDENTITY")
    if q0 == q1 == q2 == 0:
        return {"verdict": "REFUSE_IDENTITY_ZERO_ORIENTATION",
                "wronskian": "0", "norm_discriminant": "0"}
    if w == 0:
        return {"verdict": "NO_OBSTRUCTION_ESTABLISHED",
                "wronskian": "0", "norm_discriminant": "0"}
    need(q2 > 0 and delta < 0 and q0 > 0, "SIMPLE_COMPLEX_POLE_PREMISE")
    return {"verdict": "NO_RATIONAL_SOURCE_TIME_PHASE_FRAME",
            "wronskian": str(w), "norm_discriminant": str(delta)}

def is_selected(row):
    if row["expected"]["v54_disposition"] != MISSING:
        return False
    co = row["spec"]["cos_splines"].get("1")
    si = row["spec"]["sin_splines"].get("1")
    return bool(co and si and co["degree"] == si["degree"] == 1 and
                co["knots"] == si["knots"] ==
                ["0", "0", "1", "1", "2", "2"] and
                len(co["controls"]) == len(si["controls"]) == 4)

def check_row(row, expected_sha, v2_row):
    spec = row["spec"]
    need(hashlib.sha256(canonical(spec)).hexdigest() == expected_sha,
         "ORIGINAL_SOURCE_SHA256_DRIFT")
    need(v2_row["source_sha256"] == expected_sha and
         v2_row["evidence"]["source_sha256"] == expected_sha,
         "V2_SOURCE_IDENTITY_DRIFT")
    need(hashlib.sha256(canonical(row)).hexdigest() ==
         v2_row["evidence"]["original_row_sha256"], "ORIGINAL_ROW_SHA256_DRIFT")
    need(spec["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE" and
         spec["source_parameter_id"] == "source-time-t" and
         [spec["parameter_lo"], spec["parameter_hi"]] == ["0", "2"] and
         rational(spec["phase_turn_rate"]) != 0,
         "ORIGINAL_TIME_OR_PHASE_SEMANTICS")
    need(is_selected(row) and
         v2_row["historical_v54_disposition"] == MISSING and
         v2_row["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC",
         "ORIGINAL_CASE_OR_PRIOR_EVIDENCE_MISMATCH")
    co = spec["cos_splines"]["1"]["controls"]
    si = spec["sin_splines"]["1"]["controls"]
    need(co[1] == co[2] and si[1] == si[2],
         "ORIGINAL_TRUE_SOURCE_KNOT_CONTINUITY")
    return affine_certificate(co[0], co[1], si[0], si[1])

def corpus_contract():
    corpus = read_json(CORPUS, CORPUS_BLOB)
    register = read_json(V2, V2_BLOB)
    rows = corpus["cases"]
    indexed = {r["id"]: r for r in rows}
    need(len(rows) == len(indexed) == 121, "FROZEN_121_DENOMINATOR")
    refused = {r["id"] for r in rows if
               r["expected"]["v54_disposition"] == "BLOCKED"}
    missing = {r["id"] for r in rows if
               r["expected"]["v54_disposition"] == MISSING}
    need(len(refused) == 20 and len(missing) == 30, "HISTORICAL_REFUSAL_DENOMINATORS")
    v2_rows = register["source_cases"]
    known = {r["case_id"]: r for r in v2_rows}
    need(len(v2_rows) == len(known) == 50 and
         set(known) == refused | missing, "FROZEN_V2_SOURCE_SET")
    for case_id, prior in known.items():
        orig = indexed[case_id]
        need(prior["origin"] == orig["origin"] and
             prior["source_sha256"] == hashlib.sha256(canonical(orig["spec"])).hexdigest() and
             prior["evidence"]["original_row_sha256"] ==
             hashlib.sha256(canonical(orig)).hexdigest() and
             prior["historical_v54_disposition"] ==
             orig["expected"]["v54_disposition"] and
             prior["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC",
             "REUSED_V2_WITNESS_PROVENANCE")
    selected = [r for r in rows if is_selected(r)]
    need(len(selected) == len(PINNED) == 10, "ORIGINAL_SUBGRAMMAR_CARDINALITY")
    by_family = {}
    for row in selected:
        matches = [k for k in PINNED if row["id"] ==
                   "composite:PB00701_" + k +
                   (":tail100" if k.startswith(("V13_", "V14_", "V15_", "V17_", "V18_")) else ":tail0")]
        need(len(matches) == 1, "PINNED_CASE_ID_SET_DRIFT")
        key = matches[0]
        cert = check_row(row, PINNED[key], known[row["id"]])
        need(cert["wronskian"] == EXPECTED_W[key], "EXACT_W_DRIFT")
        by_family[key] = {"case_id": row["id"], "source_sha256": PINNED[key],
                          "original_row_sha256":
                          known[row["id"]]["evidence"]["original_row_sha256"],
                          **cert}
    need(set(by_family) == set(PINNED), "PINNED_FAMILY_SET_DRIFT")
    ruled_out = [k for k,v in by_family.items()
                  if v["verdict"] == "NO_RATIONAL_SOURCE_TIME_PHASE_FRAME"]
    not_ruled = [k for k,v in by_family.items()
                  if v["verdict"] == "NO_OBSTRUCTION_ESTABLISHED"]
    need(len(ruled_out) == 9 and not_ruled ==
         ["V24_EXACT_MIXED_QUADRATURE_PHASE_ANCHOR"],
         "NINE_OF_TEN_CLASSIFICATION")
    return {
        "schema": SCHEMA, "evidence_class": "DETERMINISTIC_MODEL",
        "method": "EXACT_AFFINE_H1_WRONSKIAN_SIMPLE_COMPLEX_RESIDUE",
        "population": {
            "before": {"original_sources": 121, "route_refusals": 20,
                       "missing_ordered_premises": 30,
                       "complete_v2_source_witnesses": 50},
            "after": {"original_sources": 121, "route_refusals": 20,
                      "missing_ordered_premises": 30,
                      "complete_v2_source_witnesses": 50},
            "delta": {"original_sources": 0, "route_refusals": 0,
                      "missing_ordered_premises": 0,
                      "complete_v2_source_witnesses": 0},
            "newly_resolved_historical_case_ids": [],
            "required_pb_po_discharges": 0},
        "subgrammar_size": 10, "obstructed_h1_originals": 9,
        "proportional_nonobstructed_originals": 1,
        "cases": by_family,
        "pb00701_certified": False, "mc_b_established": False,
        "mc1_established": False, "production_authorized": False,
        "native_geometry_qualified": False,
        "engineering_step_qualified": False, "supported_operations": 26}

def contract():
    actual = corpus_contract()
    receipt = read_json(RECEIPT)
    need(canonical(receipt) == canonical(actual), "RECEIPT_CLAIM_OR_PROVENANCE_DRIFT")
    return actual

class AdversarialTests(unittest.TestCase):
    def test_real_file_json_ingress_refusal_and_quoted_positive(self):
        def from_disk(raw, refusal=True):
            with tempfile.TemporaryDirectory() as temp_dir:
                target = Path(temp_dir) / "candidate.json"
                target.write_bytes(raw)
                if refusal:
                    with self.assertRaises(Refusal):
                        read_json(target)
                else:
                    return read_json(target)

        # These are actual valid on-disk JSON payloads that crashed the
        # former unbounded decoder outside its declared Refusal type.
        from_disk(b"[" * 10_000 + b"null" + b"]" * 10_000)
        from_disk(b'{"n":' + b"9" * 5_000 + b"}")
        from_disk(b" " * (MAX_RAW_BYTES + 1))
        from_disk(b'{"n":1.5}')
        from_disk(b'{"n":NaN}')
        from_disk(b'{"n":1,"n":2}')
        from_disk(b'{"n":[}')
        from_disk(b"\xff")
        from_disk(b"[" * (MAX_JSON_DEPTH + 1) +
                  b"0" + b"]" * (MAX_JSON_DEPTH + 1))
        # Pinned V2 includes genuine integer byte counts (e.g. 2344668).
        # A default parse_int rejection would wrongly reject frozen evidence.
        legal = {"bytes": 2_344_668,
                 "quoted": 'literal [ ] { } and escaped " quote and backslash \\',
                 "sequence": [0, {"k": "v"}]}
        self.assertEqual(
            from_disk(json.dumps(legal).encode("utf-8"), refusal=False),
            legal)
        self.assertEqual(from_disk(b"[" * MAX_JSON_DEPTH +
                                   b"0" + b"]" * MAX_JSON_DEPTH,
                                   refusal=False)[0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0][0], 0)

    def test_pinned_all_originals_and_receipt(self):
        actual = contract()
        self.assertEqual((actual["obstructed_h1_originals"],
                          actual["proportional_nonobstructed_originals"]), (9,1))
        self.assertEqual(actual["population"]["newly_resolved_historical_case_ids"], [])
    def test_complex_pole_very_close_not_rounded(self):
        eps = Q(1,2**120)
        r = affine_certificate("0","1","1",str(1+eps))
        self.assertEqual(r["wronskian"],"-1")
        self.assertEqual(r["norm_discriminant"],"-4")
    def test_identity_zero_and_tangency_like_degeneracy(self):
        self.assertEqual(affine_certificate("0","0","0","0")["verdict"],
                         "REFUSE_IDENTITY_ZERO_ORIENTATION")
        self.assertEqual(affine_certificate("-1","0","-1","0")["verdict"],
                         "NO_OBSTRUCTION_ESTABLISHED")
    def test_proportional_positive_control(self):
        r = affine_certificate("-1","-1001/1000","1","1001/1000")
        self.assertEqual(r["verdict"],"NO_OBSTRUCTION_ESTABLISHED")
    def test_nonzero_at_2_to_minus_120(self):
        eps=Q(1,2**120)
        r=affine_certificate("1","1", "1",str(1+eps))
        self.assertEqual(r["wronskian"],str(eps))
        self.assertEqual(r["norm_discriminant"],str(-4*eps*eps))
    def test_mutated_original_source_and_phase_refused(self):
        corpus = read_json(CORPUS, CORPUS_BLOB)
        register = {r["case_id"]:r for r in read_json(V2,V2_BLOB)["source_cases"]}
        row = next(r for r in corpus["cases"] if
                   r["id"] == "composite:PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER:tail100")
        for change in ("control","phase","knot"):
            altered=copy.deepcopy(row)
            if change=="control":
                altered["spec"]["cos_splines"]["1"]["controls"][0]="2"
            elif change=="phase":
                altered["spec"]["phase_turn_rate"]="1/3"
            else:
                altered["spec"]["cos_splines"]["1"]["knots"][2]="1/2"
            with self.assertRaises(Refusal):
                check_row(altered,PINNED["V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER"],
                          register[row["id"]])
    def test_noncanonical_and_false_residue_claim(self):
        for s in ("1.0","2/4","nan","1e-10"):
            with self.assertRaises(Refusal):
                rational(s)
        with self.assertRaises(Refusal):
            duplicate_key_reject([("a",1),("a",2)])
        with self.assertRaises(Refusal):
            affine_certificate("0","0","0","1e-10")
        result=contract()
        forged=copy.deepcopy(result)
        forged["obstructed_h1_originals"]=10
        self.assertNotEqual(canonical(result),canonical(forged))
    def test_synthetic_conjugate_poles_approach_real_axis(self):
        eps=Q(1,2**120)
        # C=t-1, S=t-1+eps: q has two simple conjugate poles
        # separated by O(eps); no real physical event is asserted.
        r=affine_certificate("-1","0",str(-1+eps),str(eps))
        self.assertEqual(r["wronskian"],str(-eps))
        self.assertEqual(r["norm_discriminant"],str(-4*eps*eps))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--contract",action="store_true")
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    if args.contract:
        print(json.dumps({"status":"PASS", "summary":{
            k:v for k,v in contract().items()
            if k in ("subgrammar_size","obstructed_h1_originals",
                     "proportional_nonobstructed_originals","population")}},
            sort_keys=True))
    if args.self_test:
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(AdversarialTests)
        outcome=unittest.TextTestRunner(verbosity=2).run(suite)
        if not outcome.wasSuccessful():
            return 1
    return 0 if args.contract or args.self_test else 2

if __name__=="__main__":
    raise SystemExit(main())
