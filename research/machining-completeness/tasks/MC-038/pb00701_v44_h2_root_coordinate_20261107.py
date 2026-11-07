#!/usr/bin/env python3
"""V44 original-source exact event-identity falsifier. DETERMINISTIC_MODEL only.

Refutes carrying over an H1-only zero as an exact physical zero after deleting
the strictly positive tiny H2 channel. Never claims a new v54 closure.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "pb00701-finite-owner-corpus-v54.json"
V2 = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
RECEIPT = HERE / "pb00701-v44-h2-root-coordinate-20261107.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
CASE_ID = "harvested:verify_pb00701_v44:ffaea08e30c9"
SPEC_SHA = "d3b3a90024ea283dfd96811b8fc2b66ceff621b3b48defc44c77f85557adbba2"
ROW_SHA = "7423adadf8c52ff28d47d9f63effbc5a2a7a630bdaf7efe6f8eeb1d2a85c5600"
BASE_MAIN = "48222d6c40b15ad42cc36d56e6d25f3b284e7fc9"
EPSILON = Q(1, 100000000)
MAX_BYTES = 400000
MAX_BITS = 512

class Refusal(ValueError):
    """A bounded/nonadmitted mathematical claim must remain NONTRUTH."""


def require(condition, reason):
    if not condition:
        raise Refusal(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def checked_json(path, blob=None):
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    require(len(raw) <= MAX_BYTES, "BYTE_BUDGET_NONTRUTH")
    if blob is not None:
        require(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw)
                .hexdigest() == blob, "FROZEN_GIT_BLOB_DRIFT")
    depth, quoted, escaped = 0, False, False
    for b in raw:
        if quoted:
            if escaped:
                escaped = False
            elif b == 92:
                escaped = True
            elif b == 34:
                quoted = False
        elif b == 34:
            quoted = True
        elif b in (91, 123):
            depth += 1
            require(depth <= 32, "JSON_DEPTH_BUDGET")
        elif b in (93, 125):
            depth -= 1
            require(depth >= 0, "JSON_NESTING_MALFORMED")
    require(depth == 0 and not quoted, "JSON_NESTING_MALFORMED")
    def pairs(seq):
        out = {}
        for k, v in seq:
            require(k not in out, "DUPLICATE_JSON_KEY")
            out[k] = v
        return out
    def integer(s):
        require(len(s) <= 12, "INTEGER_TOKEN_BUDGET")
        return int(s)
    def reject(s):
        raise Refusal("NONINTEGER_JSON_NUMBER")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                          parse_int=integer, parse_float=reject,
                          parse_constant=reject)
    except (ValueError, UnicodeError, RecursionError) as e:
        raise Refusal("JSON_PARSE_NONTRUTH") from e


def parse_rational(s):
    require(type(s) is str and 0 < len(s) <= 320 and
            all(c in "0123456789-/" for c in s), "RATIONAL_TOKEN_NONTRUTH")
    try:
        x = Q(s)
    except (ValueError, ZeroDivisionError) as e:
        raise Refusal("INVALID_RATIONAL_NONTRUTH") from e
    require(str(x) == s and max(abs(x.numerator).bit_length(),
                              x.denominator.bit_length()) <= MAX_BITS,
            "NONCANONICAL_OR_OVERSIZED_RATIONAL")
    return x


def bernstein_quadratic(c, t):
    return c[0]*(1-t)**2 + 2*c[1]*t*(1-t) + c[2]*t*t


def verify_original(source_override=None):
    rows = checked_json(CORPUS, CORPUS_BLOB)["cases"]
    witnesses = checked_json(V2, V2_BLOB)["source_cases"]
    ids = [r["id"] for r in rows]
    require(len(ids) == len(set(ids)) == 121, "ORIGINAL_121_DENOMINATOR")
    blocked = [r for r in rows if r["expected"]["v54_disposition"] == "BLOCKED"]
    ordered = [r for r in rows if r["expected"]["v54_disposition"] ==
               "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"]
    require(len(blocked) == 20 and len(ordered) == 30,
            "ORIGINAL_V54_FAILURE_DENOMINATOR")
    by_id = {r["id"]: r for r in rows}
    v2_by_id = {r["case_id"]: r for r in witnesses}
    require(len(v2_by_id) == len(witnesses) == 50 and
            set(v2_by_id) == {r["id"] for r in blocked + ordered},
            "PREEXISTING_50_ID_SET")
    for cid, w in v2_by_id.items():
        row = by_id[cid]
        require(w["source_sha256"] ==
                hashlib.sha256(canonical(row["spec"])).hexdigest() and
                w["original_row_sha256"] ==
                hashlib.sha256(canonical(row)).hexdigest() and
                w["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC",
                "V2_EVIDENCE_PROVENANCE")
    row, witness = by_id[CASE_ID], v2_by_id[CASE_ID]
    source = row["spec"] if source_override is None else source_override
    require(source == {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "source_parameter_id": "pb00701-v44-algebraic-orientation",
        "parameter_lo": "0", "parameter_hi": "1",
        "phase_turn_offset": "-1/8", "phase_turn_rate": "1/16",
        "cos_splines": {
            "1": {"degree": 2, "knots": ["0","0","0","1","1","1"],
                  "controls": ["-3/2","-1","3/2"]},
            "2": {"degree": 0, "knots": ["0","1"],
                  "controls": ["1/100000000"]}},
        "sin_splines": {
            "1": {"degree": 2, "knots": ["0","0","0","1","1","1"],
                  "controls": ["-1/2","-1","1/2"]}}},
        "ORIGINAL_V44_GRAMMAR_OR_PARAMETER_MISMATCH")
    require(hashlib.sha256(canonical(source)).hexdigest() == SPEC_SHA and
            hashlib.sha256(canonical(row)).hexdigest() == ROW_SHA and
            witness["source_sha256"] == SPEC_SHA and
            witness["original_row_sha256"] == ROW_SHA and
            witness["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC" and
            row["expected"]["observed"]["spans"] == [[
                "PB00701_V44_EXACT_REAL_ALGEBRAIC_ORIENTATION_CUT_BOUNDARY",
                "BLOCKED",
                "ALGEBRAIC_ORIENTATION_COORDINATE_CERTIFIED_BUT_EXACT_CONSUMPTION_AUTHORITY_MISSING"
            ]], "FROZEN_V44_IDENTITY_OR_REFUSAL_DRIFT")
    cos = [Q(x) for x in source["cos_splines"]["1"]["controls"]]
    sin = [Q(x) for x in source["sin_splines"]["1"]["controls"]]
    for t in (Q(0), Q(1, 4), Q(1, 2), Q(3, 4), Q(1)):
        require(bernstein_quadratic(cos, t) ==
                -Q(3,2) + t + 2*t*t and
                bernstein_quadratic(sin, t) ==
                -Q(1,2) - t + 2*t*t,
                "V44_BERNSTEIN_POLYNOMIAL_MISMATCH")
    return {"row": row, "witness": witness, "v2_map": v2_by_id}


def classify(epsilon, *, grammar="PINNED_V44_H1_AND_H2"):
    """Symbolic signed-root theorem; no numerical root locator is emitted.

    C=-3/2+t+2t², S=-1/2-t+2t², theta=-pi/4+pi*t/8.
    G=C+S*tan(theta), H=cos(2theta)/cos(theta).
    G'(t)>3/8 and 0<H'(t)<2, hence (G+eps*H)'>1/3
    for |eps|<=1/100. Each has a unique simple interior physical root.
    """
    require(grammar == "PINNED_V44_H1_AND_H2",
            "TANGENCY_IDENTITY_ZERO_OR_DIFFERENT_GRAMMAR_NONTRUTH")
    eps = parse_rational(epsilon)
    require(abs(eps) <= Q(1,100), "UNADMITTED_PERTURBATION_NONTRUTH")
    # Rational checks of all conservative analytic inequalities:
    # pi<4, S>=-5/8, sec²(theta)<=2, theta'=pi/8.
    require(Q(1) - Q(5,8)*2*Q(4,8) == Q(3,8),
            "DERIVATIVE_BOUND_ARITHMETIC")
    require(Q(3,8) - 2*Q(1,100) > Q(1,3),
            "POSITIVE_DERIVATIVE_MARGIN")
    require(Q(3,2) - Q(1,2) - Q(1,100) > 0,
            "POSITIVE_RIGHT_ENDPOINT_MARGIN")
    if eps > 0:
        order = "FULL_ROOT_STRICTLY_BEFORE_H1_ROOT"
    elif eps < 0:
        order = "FULL_ROOT_STRICTLY_AFTER_H1_ROOT"
    else:
        order = "COINCIDENT_ROOTS_ONLY_WHEN_H2_IS_ZERO"
    return {
        "status": "COMPLETE_RESTRICTED_V44_SIGNED_ROOT_ORDER",
        "evidence_class": "DETERMINISTIC_MODEL",
        "admitted_rational_h2_coefficient": str(eps),
        "original_case_claim": eps == EPSILON,
        "dominant_h1_only_root": {"type": "UNIQUE_SIMPLE_IMPLICIT",
                                  "strict_open_rational_bracket": ["0","1"]},
        "full_h1_h2_root": {"type": "UNIQUE_SIMPLE_IMPLICIT",
                            "strict_open_rational_bracket": ["0","1"]},
        "ordered_physical_signs": ["NEGATIVE", "POSITIVE"],
        "exact_root_order": order,
        "root_separation": ("0<ABS_DIFFERENCE<3*ABS(EPSILON)" if eps
                            else "ZERO"),
        "no_exact_root_coordinate_substitution": eps != 0,
        "newly_resolved_historical_case_ids": [],
        "required_pb_po_discharges": 0, "mc_b_established": False,
        "mc1_established": False, "production_authorized": False,
    }


def before_after():
    original = verify_original()
    v2 = original["v2_map"]
    rows = []
    for cid in sorted(v2):
        x = v2[cid]
        rows.append({
            "case_id": cid, "original_source_sha256": x["source_sha256"],
            "original_row_sha256": x["original_row_sha256"],
            "original_v54_disposition": x["historical_v54_disposition"],
            "after_v54_disposition": x["historical_v54_disposition"],
            "evidence": x["registered_evidence_level"],
            "changed": False,
        })
    counts = {"original_sources": 121, "uncertified_routes": 20,
              "missing_ordered_premises": 30,
              "preexisting_complete_v2": 50,
              "required_pb_po_discharges": 0}
    return {"schema":"mc038-v44-h2-root-coordinate-falsifier/1.0",
            "frozen_v54_git_blob": CORPUS_BLOB, "frozen_v2_git_blob": V2_BLOB,
            "base_main":BASE_MAIN,
            "frozen_case":CASE_ID,"source_sha256":SPEC_SHA,"row_sha256":ROW_SHA,
            "historical_before":counts,"historical_after":dict(counts),
            "historical_delta":{k:0 for k in counts},
            "original_fifty_cases":rows,
            "newly_resolved_historical_case_ids":[],
            "negative_route":"DELETE_NONZERO_TINY_H2_AND_REUSE_H1_ROOT_COORDINATE",
            "bounded_falsification":classify(str(EPSILON)),
            "required_pb_po_discharges":0,
            "evidence_class":"DETERMINISTIC_MODEL",
            "native_geometry_evidence":False,"engineering_step_evidence":False}


class Tests(unittest.TestCase):
    def test_source_original_sha_row_and_census(self):
        x=verify_original()
        self.assertEqual(x["witness"]["source_sha256"],SPEC_SHA)
        self.assertEqual(len(x["v2_map"]),50)

    def test_original_v44_exact_root_coordinate_mismatch(self):
        a=classify("1/100000000")
        self.assertEqual(a["exact_root_order"],
                         "FULL_ROOT_STRICTLY_BEFORE_H1_ROOT")
        self.assertTrue(a["no_exact_root_coordinate_substitution"])
        self.assertEqual(a["ordered_physical_signs"],["NEGATIVE","POSITIVE"])

    def test_zero_h2_is_the_exact_positive_control(self):
        self.assertEqual(classify("0")["exact_root_order"],
                         "COINCIDENT_ROOTS_ONLY_WHEN_H2_IS_ZERO")
        self.assertFalse(classify("0")["no_exact_root_coordinate_substitution"])

    def test_negative_h2_reverse_shift_prospective(self):
        a=classify("-1/100000000")
        self.assertEqual(a["exact_root_order"],
                         "FULL_ROOT_STRICTLY_AFTER_H1_ROOT")

    def test_extremely_close_distinct_roots_still_refuse_exact_reuse(self):
        eps=Q(1,2**300)
        a=classify(str(eps))
        self.assertTrue(a["no_exact_root_coordinate_substitution"])
        self.assertTrue(3*eps < Q(1,2**298))
        self.assertEqual(a["root_separation"],
                         "0<ABS_DIFFERENCE<3*ABS(EPSILON)")

    def test_admitted_endpoints_positive_and_negative_epsilon(self):
        for e in ("1/100","-1/100"):
            self.assertEqual(classify(e)["ordered_physical_signs"],
                             ["NEGATIVE","POSITIVE"])

    def test_out_of_domain_and_uncertified_perturbation_refusal(self):
        for e in ("11/1000","-11/1000","1/0","1/1","1e-8",
                  "1/"+str(2**600)):
            with self.assertRaises(Refusal):
                classify(e)

    def test_tangency_identity_zero_and_changed_harmonics_refuse(self):
        for grammar in ("IDENTITY_ZERO","ORDER_TWO_TANGENCY",
                        "H1_CHANGED", "SOURCE_PHASE_CHANGED"):
            with self.assertRaises(Refusal):
                classify("1/100000000",grammar=grammar)

    def test_canonical_source_mutation_refuses(self):
        spec=verify_original()["row"]["spec"]
        altered=json.loads(json.dumps(spec))
        altered["cos_splines"]["2"]["controls"]=["0"]
        with self.assertRaises(Refusal):
            verify_original(altered)
        altered=json.loads(json.dumps(spec))
        altered["phase_turn_rate"]="1/8"
        with self.assertRaises(Refusal):
            verify_original(altered)

    def test_source_bernstein_endpoint_controls_and_phase(self):
        s=verify_original()["row"]["spec"]
        self.assertEqual(s["source_parameter_id"],
                         "pb00701-v44-algebraic-orientation")
        self.assertEqual((s["phase_turn_offset"],s["phase_turn_rate"]),
                         ("-1/8","1/16"))
        self.assertEqual(bernstein_quadratic([Q("-3/2"),Q("-1"),Q("3/2")],Q(1)),
                         Q(3,2))
        self.assertEqual(bernstein_quadratic([Q("-1/2"),Q("-1"),Q("1/2")],Q(1)),
                         Q(1,2))

    def test_bound_margin_and_no_mathematical_timeout(self):
        self.assertGreater(Q(3,8)-Q(1,50),Q(1,3))
        for e in ("0","1/100000000","-1/100000000"):
            self.assertEqual(classify(e)["status"],
                             "COMPLETE_RESTRICTED_V44_SIGNED_ROOT_ORDER")

    def test_receipt_exact_fifty_identity_and_no_authority_promotion(self):
        got=checked_json(RECEIPT)
        self.assertEqual(got,before_after())
        self.assertEqual(got["historical_delta"]["missing_ordered_premises"],0)
        self.assertEqual(got["required_pb_po_discharges"],0)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--contract",action="store_true")
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.contract:
        got=before_after()
        require(checked_json(RECEIPT)==got,"RECEIPT_REPRODUCTION_MISMATCH")
        print(json.dumps(got,sort_keys=True))
    if args.self_test:
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            raise SystemExit(1)
    if not (args.contract or args.self_test):
        p.error("use --contract and/or --self-test")

if __name__ == "__main__":
    main()
