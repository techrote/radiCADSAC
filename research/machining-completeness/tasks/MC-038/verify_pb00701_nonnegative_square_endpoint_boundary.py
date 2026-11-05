#!/usr/bin/env python3
"""Exact original-source negative-endpoint boundary for direct nonnegative squares.

DETERMINISTIC_MODEL. This falsifies only the proposed UNIVERSAL direct
nonnegative-squares representation of all frozen v54 blocked originals.
It is not an event/root solver, a PB-007 discharge, or a critique of the
separately owned bounded moving-square implementation (PR #397).
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "pb00701-finite-owner-corpus-v54.json"
REGISTRY = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
RECEIPT = HERE / "pb00701-nonnegative-square-endpoint-boundary-20261105.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
REGISTRY_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
ORDER_GAP = "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"
ROUTE = "BLOCKED"
SCHEMA = "radicadsac-mc038-nonnegative-square-endpoint-boundary/1.0"
METHOD = "DIRECT_NONNEGATIVE_SQUARE_COMPONENT_COVERAGE_OF_ALL_FROZEN_V54_BLOCKED_ORIGINALS"
CLAIM = "NEGATIVE_C_BOUNDED_DIRECT_UNIVERSAL_SQUARE_ADMISSION"
EVIDENCE = "DETERMINISTIC_MODEL"
ANCHORS = {
    "composite:DELEGATED_V6_CONSTANT_MODULATION:tail0":
        ("9eb6f08a44882adffa919529247c40190c70e8d7599ee2b1a0f7978ef2569eb1", "2", "-1"),
    "composite:PB00701_V14_EXACT_STRICT_DOMINANCE_MULTITERM_MULTIPLIER:tail100":
        ("bd10ad1d9503335b2d7f745c09805b82a421b8db7beea67329cf33d0c9d78ff2", "0", "-5/6"),
    "composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail0":
        ("9abbed355812241cdef20f3ce3b3522619bdd682c3a73fb01828d8f95c72f0af", "2", "-1/2"),
}


class Refusal(ValueError):
    """Invalid source, claimed evidence, or provenance; never a zero decision."""


def need(cond: bool, reason: str):
    if not cond:
        raise Refusal(reason)


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("ascii")


def digest(obj) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def reject_duplicate_pairs(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def read_pinned(path: Path, expected_blob: str):
    raw = path.read_bytes()
    need(len(raw) <= 4_000_000, "PINNED_SOURCE_SIZE_REFUSAL")
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") +
                        b"\0" + raw).hexdigest()
    need(blob == expected_blob, "PINNED_GIT_BLOB_IDENTITY_MISMATCH")
    return json.loads(raw.decode("utf8"), object_pairs_hook=reject_duplicate_pairs,
                      parse_constant=lambda v: (_ for _ in ()).throw(Refusal("NONFINITE_JSON")))


def exact_rational(value) -> Fraction:
    need(type(value) is str and 0 < len(value) <= 256, "NONCANONICAL_RATIONAL")
    try:
        fraction = Fraction(value)
    except (ValueError, ZeroDivisionError, TypeError, OverflowError) as exc:
        raise Refusal("MALFORMED_RATIONAL") from exc
    need(str(fraction) == value, "NONCANONICAL_RATIONAL")
    need(max(abs(fraction.numerator).bit_length(), fraction.denominator.bit_length())
         <= 4096, "RATIONAL_RESOURCE_REFUSAL_NOT_TRUTH")
    return fraction


def endpoint_components(spec, side: str):
    need(type(spec) is dict and spec.get("source_parameter_id") == "source-time-t",
         "WRONG_ORIGINAL_SOURCE_PARAMETER")
    need(spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
         "WRONG_ORIGINAL_SOURCE_GRAMMAR")
    lo, hi = exact_rational(spec["parameter_lo"]), exact_rational(spec["parameter_hi"])
    need(lo < hi, "NONINCREASING_SOURCE_TIME")
    need(side in ("lo", "hi"), "INVALID_ENDPOINT")
    t = lo if side == "lo" else hi
    beta = exact_rational(spec["phase_turn_offset"]) + (
        exact_rational(spec["phase_turn_rate"]) * t)
    need(beta.numerator.bit_length() <= 4096 and beta.denominator.bit_length() <= 4096,
         "PHASE_RESOURCE_REFUSAL_NOT_TRUTH")
    terms = []
    for channel, factor_table in (("cos_splines", (1, 0, -1, 0)),
                                  ("sin_splines", (0, 1, 0, -1))):
        splines = spec.get(channel)
        need(type(splines) is dict, "MISSING_SPLINE_CHANNEL")
        for hstr, spline in sorted(splines.items(), key=lambda pair: int(pair[0])):
            need(type(hstr) is str and hstr.isdecimal() and
                 str(int(hstr)) == hstr and int(hstr) <= 1000,
                 "INVALID_HARMONIC")
            need(type(spline) is dict and
                 set(spline) == {"degree", "knots", "controls"},
                 "INVALID_ORIGINAL_SPLINE_FIELDS")
            degree = spline["degree"]
            knots, controls = spline["knots"], spline["controls"]
            need(type(degree) is int and 0 <= degree <= 100 and
                 type(knots) is list and type(controls) is list and
                 len(knots) == len(controls) + degree + 1 and
                 len(controls) > degree, "INVALID_ORIGINAL_SPLINE_SIZE")
            k = [exact_rational(x) for x in knots]
            c = [exact_rational(x) for x in controls]
            need(all(a <= b for a, b in zip(k, k[1:])) and
                 k[:degree+1] == [lo]*(degree+1) and
                 k[-degree-1:] == [hi]*(degree+1) and
                 all(lo <= x <= hi for x in k),
                 "ORIGINAL_CLAMPED_ENDPOINT_KNOTS_REQUIRED")
            phase_quarters = 4 * int(hstr) * beta
            if phase_quarters.denominator != 1:
                # This endpoint is INDETERMINATE for this rational-only oracle;
                # do not infer a sign from an approximate transcendental phase.
                return {"status": "INDETERMINATE_NONQUARTER_PHASE",
                        "t": str(t), "beta_turns": str(beta)}
            signed_factor = factor_table[int(phase_quarters) % 4]
            component = c[0 if side == "lo" else -1] * signed_factor
            terms.append({"channel": channel, "harmonic": int(hstr),
                          "endpoint_control": str(c[0 if side == "lo" else -1]),
                          "quarter_turn_multiplier": signed_factor,
                          "physical_contribution": str(component)})
    total = sum((exact_rational(v["physical_contribution"]) for v in terms),
                Fraction(0))
    return {"status": "EXACT_QUARTER_PHASE_ENDPOINT",
            "t": str(t), "beta_turns": str(beta),
            "F": str(total), "negative": total < 0, "terms": terms}


def audit(corpus, registry):
    need(type(corpus) is dict and type(registry) is dict and
         type(corpus.get("cases")) is list and
         type(registry.get("source_cases")) is list,
         "PINNED_RECORD_SHAPE_MISMATCH")
    rows = corpus["cases"]
    need(len(rows) == 121 and
         len({x["id"] for x in rows}) == 121, "FROZEN_121_ID_CUSTODY_MISMATCH")
    originals = {row["id"]: row for row in rows}
    disposition = Counter(row["expected"]["v54_disposition"] for row in rows)
    need(disposition == Counter({"CERTIFIED": 40,
         "FINITE_OWNER_SOURCE_EVIDENCE_CERTIFIED": 26,
         "MIXED_OWNER_SOURCE_EVIDENCE_CERTIFIED": 5,
         ROUTE: 20, ORDER_GAP: 30}), "FROZEN_DISPOSITION_MISMATCH")
    records = registry["source_cases"]
    need(len(records) == 50 and
         len({x["case_id"] for x in records}) == 50,
         "REGISTERED_50_ID_CUSTODY_MISMATCH")
    registered = {x["case_id"]: x for x in records}
    blocked = {row["id"] for row in rows if
               row["expected"]["v54_disposition"] in (ROUTE, ORDER_GAP)}
    need(set(registered) == blocked, "REGISTERED_BLOCKED_ID_SET_MISMATCH")
    negative = []
    exact_endpoints = 0
    unknown_endpoints = 0
    for case_id in sorted(blocked):
        row, r = originals[case_id], registered[case_id]
        spec = row["spec"]
        need(r["source_sha256"] == digest(spec) and
             r["original_row_sha256"] == digest(row) and
             r["evidence"]["source_sha256"] == r["source_sha256"] and
             r["evidence"]["original_row_sha256"] == r["original_row_sha256"],
             "ORIGINAL_SOURCE_OR_ROW_DIGEST_MISMATCH")
        need(r["historical_v54_disposition"] ==
             row["expected"]["v54_disposition"] and
             r["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC" and
             r["source_parameter_id"] == spec["source_parameter_id"] and
             r["origin"] == row["origin"] and
             r["source_interval"] == [spec["parameter_lo"], spec["parameter_hi"]] and
             r["phase_turn_law"] ==
             {"offset": spec["phase_turn_offset"], "rate": spec["phase_turn_rate"]},
             "ORIGINAL_REGISTERED_PROVENANCE_MISMATCH")
        sides = []
        for side in ("lo", "hi"):
            e = endpoint_components(spec, side)
            if e["status"] == "EXACT_QUARTER_PHASE_ENDPOINT":
                exact_endpoints += 1
            else:
                unknown_endpoints += 1
            if e.get("negative"):
                sides.append(e)
        if sides:
            negative.append({
                "case_id": case_id,
                "source_sha256": r["source_sha256"],
                "original_row_sha256": r["original_row_sha256"],
                "historical_v54_disposition": r["historical_v54_disposition"],
                "negative_endpoints": sides})
    need(len(negative) == 22 and
         Counter(x["historical_v54_disposition"] for x in negative) ==
         Counter({ROUTE: 10, ORDER_GAP: 12}),
         "NEGATIVE_ORIGINAL_ENDPOINT_POPULATION_DRIFT")
    indexed = {x["case_id"]: x for x in negative}
    for cid, (sha, t, value) in ANCHORS.items():
        need(indexed[cid]["source_sha256"] == sha and
             any(x["t"] == t and x["F"] == value for x in
                 indexed[cid]["negative_endpoints"]),
             "SOURCE_BOUND_NEGATIVE_ENDPOINT_ANCHOR_FALSE")
    return {
        "schema": SCHEMA,
        "candidate_route": METHOD,
        "result": CLAIM, "evidence_class": EVIDENCE,
        "frozen_source_population": 121,
        "historical_uncertified_routes": 20,
        "historical_missing_ordered_premises": 30,
        "existing_complete_original_source_witnesses": 50,
        "strictly_negative_endpoint_originals": 22,
        "negative_route_refusal_originals": 10,
        "negative_missing_ordered_premise_originals": 12,
        "exactly_admitted_endpoint_evaluations": exact_endpoints,
        "nonquarter_endpoint_evaluations_not_claimed": unknown_endpoints,
        "negative_original_case_records": negative,
        "newly_closed_historical_case_ids": [],
        "pb00701_or_required_po_discharged": False,
        "mc_b_established": False, "mc1_established": False,
        "native_geometry_qualified": False, "engineering_step_qualified": False,
        "production_authorized": False
    }


def verify_receipt(actual, receipt):
    need(type(receipt) is dict and
         receipt.get("schema") == SCHEMA and
         receipt.get("candidate_route") == METHOD and
         receipt.get("evidence_class") == EVIDENCE and
         receipt.get("result") == CLAIM, "RECEIPT_CLAIM_MISMATCH")
    expected_ids = receipt["negative_original_case_ids"]
    need(type(expected_ids) is list and len(expected_ids) == len(set(expected_ids)) == 22,
         "RECEIPT_NEGATIVE_IDS_INVALID")
    need(expected_ids == sorted(x["case_id"]
                              for x in actual["negative_original_case_records"]),
         "RECEIPT_NEGATIVE_CASE_SET_MISMATCH")
    for key in ("frozen_source_population", "historical_uncertified_routes",
                "historical_missing_ordered_premises",
                "existing_complete_original_source_witnesses",
                "strictly_negative_endpoint_originals",
                "negative_route_refusal_originals",
                "negative_missing_ordered_premise_originals"):
        need(receipt[key] == actual[key], "RECEIPT_COUNT_MISMATCH")
    need(receipt["frozen_corpus_git_blob"] == CORPUS_BLOB and
         receipt["frozen_v2_register_git_blob"] == REGISTRY_BLOB,
         "RECEIPT_FROZEN_BLOB_MISMATCH")
    need(receipt["before_after"] == {
        "before": [121, 20, 30, 50],
        "after": [121, 20, 30, 50],
        "delta": [0, 0, 0, 0],
        "newly_closed_historical_case_ids": []}, "RECEIPT_FALSE_CLOSURE")
    need(receipt["pb00701"] == "OPEN" and
         receipt["mc_b"] == "NOT_ESTABLISHED" and
         receipt["mc1"] == "NOT_ESTABLISHED" and
         receipt["production_authorized"] is False,
         "UNAUTHORIZED_CAPABILITY_PROMOTION")


def self_test(c, r, receipt, actual):
    verify_receipt(actual, receipt)
    assert actual["strictly_negative_endpoint_originals"] == 22
    originals = {row["id"]: row for row in c["cases"]}
    cid = "composite:DELEGATED_V6_CONSTANT_MODULATION:tail0"
    baseline = endpoint_components(originals[cid]["spec"], "hi")
    assert baseline["F"] == "-1" and baseline["negative"]
    for mutation in ("phase", "amplitude", "knot", "parameter", "row"):
        corrupted = copy.deepcopy(c)
        indexed = {row["id"]: row for row in corrupted["cases"]}
        bad = indexed[cid]
        if mutation == "phase":
            bad["spec"]["phase_turn_rate"] = "1/8"
        elif mutation == "amplitude":
            bad["spec"]["cos_splines"]["1"]["controls"][-1] = "0"
        elif mutation == "knot":
            bad["spec"]["cos_splines"]["1"]["knots"][-1] = "3"
        elif mutation == "parameter":
            bad["spec"]["source_parameter_id"] = "carrier-u"
        else:
            bad["expected"]["v54_disposition"] = "CERTIFIED"
        try:
            audit(corrupted, r)
        except Refusal:
            pass
        else:
            raise AssertionError("mutated original source admitted: " + mutation)
    for bad_key in ("negative_original_case_ids", "before_after", "production_authorized"):
        forged = copy.deepcopy(receipt)
        if bad_key == "negative_original_case_ids":
            forged[bad_key] = forged[bad_key][1:]
        elif bad_key == "before_after":
            forged[bad_key]["delta"][1] = -1
        else:
            forged[bad_key] = True
        try:
            verify_receipt(actual, forged)
        except Refusal:
            pass
        else:
            raise AssertionError("forged receipt accepted: " + bad_key)
    sample = copy.deepcopy(originals[cid]["spec"])
    sample["phase_turn_rate"] = "1/7"
    uncertain = endpoint_components(sample, "hi")
    assert uncertain["status"] == "INDETERMINATE_NONQUARTER_PHASE"
    # A zero-valued original is not a new negative source or a root proof.
    sample = copy.deepcopy(originals[cid]["spec"])
    sample["cos_splines"]["1"]["controls"] = ["0", "0"]
    assert endpoint_components(sample, "hi")["F"] == "0"
    # Distinct rational signs, not floating point epsilon comparisons.
    assert Fraction(-1, 2**80) < 0 < Fraction(1, 2**80)
    print("PASS: source-bound 22 negative originals; 10 route/12 ordered; "
          "quarter-turn exactness, mutation refusals and unchanged 121/20/30/50")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    c = read_pinned(CORPUS, CORPUS_BLOB)
    r = read_pinned(REGISTRY, REGISTRY_BLOB)
    receipt = json.loads(RECEIPT.read_text(encoding="utf8"),
                         object_pairs_hook=reject_duplicate_pairs)
    actual = audit(c, r)
    verify_receipt(actual, receipt)
    if args.self_test or args.contract:
        self_test(c, r, receipt, actual)
    else:
        print(json.dumps(actual, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
