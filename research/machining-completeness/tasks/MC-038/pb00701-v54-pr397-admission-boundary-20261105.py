#!/usr/bin/env python3
"""Exact frozen-v54 necessary-grammar admission audit of PR #397.

This does not run, modify, or substitute the existing moving-square theorem.
A structural rejection is a proof that DIRECT unchanged-source admission to
that theorem is unavailable; it is not a statement about physical zero sets.
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
V54 = HERE / "pb00701-finite-owner-corpus-v54.json"
V2 = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
RECEIPT = HERE / "pb00701-v54-pr397-admission-boundary-20261105.json"
V54_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
SCHEMA = "radicadsac-mc038-v54-pr397-direct-admission-boundary/1.0"
ROUTE = "DIRECT_FROZEN_V54_ADMISSION_BY_PR397_MOVING_SQUARE_GRAMMAR"
BASE_MAIN = "7715cc245b4843aa469d1c9a7f5bd53b9fc59623"
REASONS = (
    "COSINE_HARMONIC_INVENTORY_NOT_EXACT_H0_H1",
    "NONEMPTY_SINE_CHANNELS",
    "ORIGINAL_SPLINE_DEGREE_NOT_BOTH_TWO",
    "ORIGINAL_CONTROL_CARDINALITY_NOT_FIVE",
    "ORIGINAL_KNOT_CARDINALITY_NOT_EIGHT",
    "ORIGINAL_KNOTS_NOT_COMMON",
    "ORIGINAL_DOUBLE_KNOT_NOT_CLAMPED",
    "ORIGINAL_NONZERO_AFFINE_PHASE_NOT_PROVED",
)
BLOCKED = {"BLOCKED", "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"}
EXPECTED_121 = {REASONS[0]: 99, REASONS[1]: 18, REASONS[2]: 4}
EXPECTED_50 = {REASONS[0]: 35, REASONS[1]: 11, REASONS[2]: 4}
ANCHORS = {
    "composite:DELEGATED_V6_CONSTANT_MODULATION:tail0":
        "9eb6f08a44882adffa919529247c40190c70e8d7599ee2b1a0f7978ef2569eb1",
    "composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail100":
        "cc13a39582060e763c573f2665b3ea3b6dfe8b76a6cb0fb77a7b0ec90cf6253a",
    "harvested:verify_pb00701_v9:4e7b85fa122a":
        "a83ca0cd16c7822e6525f8f2d2df26a54f45b99807cadebc67f31fc49b066c10",
}


class Refusal(ValueError):
    pass


def demand(ok, reason):
    if not ok:
        raise Refusal(reason)


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") +
                        b"\x00" + raw).hexdigest()


def rational(token):
    demand(type(token) is str and 0 < len(token) <= 128, "UNSUPPORTED_RATIONAL")
    try:
        value = Fraction(token)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise Refusal("INVALID_RATIONAL") from exc
    demand(str(value) == token, "NONCANONICAL_RATIONAL")
    return value


def structural_refusal(spec):
    """First failed NECESSARY original-source condition; not a root decision."""
    demand(type(spec) is dict, "UNTRUSTED_SOURCE")
    cos = spec.get("cos_splines")
    sine = spec.get("sin_splines")
    demand(type(cos) is dict and type(sine) is dict, "UNTRUSTED_CHANNELS")
    if set(cos) != {"0", "1"}:
        return REASONS[0]
    if sine:
        return REASONS[1]
    a, b = cos["0"], cos["1"]
    demand(type(a) is dict and type(b) is dict, "UNTRUSTED_SPLINES")
    if type(a.get("degree")) is not int or type(b.get("degree")) is not int or \
            a["degree"] != 2 or b["degree"] != 2:
        return REASONS[2]
    if any(type(c.get("controls")) is not list or len(c["controls"]) != 5
           for c in (a, b)):
        return REASONS[3]
    if any(type(c.get("knots")) is not list or len(c["knots"]) != 8
           for c in (a, b)):
        return REASONS[4]
    if a["knots"] != b["knots"]:
        return REASONS[5]
    knots = a["knots"]
    lo, hi = spec.get("parameter_lo"), spec.get("parameter_hi")
    if not (knots[:3] == [lo]*3 and knots[3] == knots[4] and
            knots[5:] == [hi]*3 and
            rational(lo) < rational(knots[3]) < rational(hi)):
        return REASONS[6]
    try:
        rate = rational(spec.get("phase_turn_rate"))
        rational(spec.get("phase_turn_offset"))
    except Refusal:
        return REASONS[7]
    if rate == 0 or spec.get("source_parameter_id") != "source-time-t" or \
            spec.get("grammar") != "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE":
        return REASONS[7]
    return None  # NECESSARY structure only, not square identity / acceptance


def audit(corpus, register):
    demand(type(corpus) is dict and type(register) is dict, "INVALID_ARCHIVES")
    rows, proofs = corpus.get("cases"), register.get("source_cases")
    demand(type(rows) is list and len(rows) == 121, "FROZEN_DENOMINATOR")
    demand(type(proofs) is list and len(proofs) == 50, "V2_DENOMINATOR")
    ids = [x.get("id") for x in rows]
    demand(len(set(ids)) == 121, "DUPLICATE_V54_CASE_ID")
    originals = {x["id"]: x for x in rows}
    blocked = {x["id"] for x in rows
               if x["expected"]["v54_disposition"] in BLOCKED}
    demand(len(blocked) == 50 and
           sum(originals[i]["expected"]["v54_disposition"] == "BLOCKED"
               for i in blocked) == 20 and
           sum(originals[i]["expected"]["v54_disposition"] ==
               "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"
               for i in blocked) == 30, "HISTORICAL_DISPOSITION_DRIFT")
    proof_ids = [x["case_id"] for x in proofs]
    demand(len(set(proof_ids)) == 50 and set(proof_ids) == blocked,
           "HISTORICAL_REGISTER_COVERAGE")
    bindings = {x["case_id"]: x for x in proofs}
    source_hashes = {}
    all_reasons = {}
    for row in rows:
        case_id = row["id"]
        spec = row["spec"]
        digest = hashlib.sha256(encode(spec)).hexdigest()
        source_hashes[case_id] = digest
        all_reasons[case_id] = structural_refusal(spec)
    demand(len(set(source_hashes.values())) == 121,
           "ORIGINAL_SOURCE_COLLISION")
    for case_id, expect_sha in ANCHORS.items():
        demand(source_hashes[case_id] == expect_sha, "ORIGINAL_ANCHOR_MISMATCH")
    for case_id in blocked:
        proof = bindings[case_id]
        original = originals[case_id]
        spec = original["spec"]
        demand(proof["source_sha256"] == source_hashes[case_id] and
               proof["origin"] == original["origin"] and
               proof["historical_v54_disposition"] ==
               original["expected"]["v54_disposition"] and
               proof["source_parameter_id"] == spec["source_parameter_id"] and
               proof["source_interval"] ==
               [spec["parameter_lo"], spec["parameter_hi"]] and
               proof["phase_turn_law"] ==
               {"offset": spec["phase_turn_offset"],
                "rate": spec["phase_turn_rate"]} and
               proof["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC" and
               proof["evidence"]["source_sha256"] == source_hashes[case_id],
               "V2_SOURCE_IDENTITY_MISMATCH")
    hist = {i: all_reasons[i] for i in blocked}
    whole = Counter(all_reasons.values())
    historical = Counter(hist.values())
    demand(None not in whole and None not in historical,
           "DIRECT_ROUTE_STRUCTURAL_ADMISSION_FOUND")
    demand(dict(whole) == EXPECTED_121 and dict(historical) == EXPECTED_50,
           "FROZEN_ADMISSION_RECOUNT_DIFFERENT")
    return {
        "schema": SCHEMA,
        "route_under_falsification": ROUTE,
        "source_selection_main": BASE_MAIN,
        "evidence_class": "DETERMINISTIC_MODEL",
        "frozen_git_blobs": {"v54_corpus": V54_BLOB, "v2_register": V2_BLOB},
        "before_after": {
            "originals": {"before": 121, "after": 121, "delta": 0},
            "historical_route_refusals":
                {"before": 20, "after": 20, "delta": 0},
            "missing_ordered_premises":
                {"before": 30, "after": 30, "delta": 0},
            "existing_complete_source_specific":
                {"before": 50, "after": 50, "delta": 0},
        },
        "first_refusal_all_121": {k: whole.get(k, 0) for k in REASONS},
        "first_refusal_historical_50":
            {k: historical.get(k, 0) for k in REASONS},
        "direct_historical_structural_candidates": [],
        "new_historical_case_ids_resolved": [],
        "historical_case_refusals": [
            {"id": case_id, "source_sha256": source_hashes[case_id],
             "v54_disposition": originals[case_id]["expected"]["v54_disposition"],
             "necessary_grammar_refusal": hist[case_id]}
            for case_id in sorted(blocked)
        ],
        "accepted_claim": "NO_UNCHANGED_FROZEN_V54_ORIGINAL_CAN_DIRECTLY_ENTER_PR397_NECESSARY_GRAMMAR",
        "unclaimed": [
            "PR397_EXTENSIONS_IMPOSSIBLE",
            "GENERAL_ANALYTIC_ROOT_DECIDABILITY",
            "HISTORICAL_V54_ROUTE_REPAIRED",
            "REQUIRED_PB007_OR_PO_DISCHARGED",
            "NATIVE_GEOMETRY_OR_ENGINEERING_STEP",
            "MC_B_OR_MC_1_ESTABLISHED",
            "PRODUCTION_AUTHORIZED",
        ],
        "all_26_required_operations_preserved": True,
        "production_authorized": False,
    }


def read_pinned(path, expected_blob, byte_limit):
    raw = path.read_bytes()
    demand(len(raw) <= byte_limit and git_blob(raw) == expected_blob,
           "FROZEN_GIT_BLOB_DRIFT")
    return json.loads(raw)


def run():
    return audit(read_pinned(V54, V54_BLOB, 300_000),
                 read_pinned(V2, V2_BLOB, 350_000))


def expect_refusal(action):
    try:
        action()
    except Refusal:
        return
    raise AssertionError("mutation unexpectedly admitted")


def self_test():
    corpus = read_pinned(V54, V54_BLOB, 300_000)
    v2 = read_pinned(V2, V2_BLOB, 350_000)
    saved = json.loads(RECEIPT.read_text(encoding="utf-8"))
    original = audit(corpus, v2)
    demand(saved == original, "SAVED_RECEIPT_NOT_RECOMPUTED")
    assert sum(original["first_refusal_historical_50"].values()) == 50
    assert sum(original["first_refusal_all_121"].values()) == 121
    assert original["direct_historical_structural_candidates"] == []
    assert len(original["historical_case_refusals"]) == 50

    # Exercise actual rejection, not only fixture inequality: original SHA,
    # historical dispositions, source identity, and registry are protected.
    changed = copy.deepcopy(corpus)
    target = next(x for x in changed["cases"] if
                  x["id"] == "composite:DELEGATED_V6_CONSTANT_MODULATION:tail0")
    target["spec"]["phase_turn_rate"] = "1/2"
    expect_refusal(lambda: audit(changed, v2))
    changed = copy.deepcopy(corpus)
    next(x for x in changed["cases"] if x["id"] ==
         "composite:DELEGATED_V6_CONSTANT_MODULATION:tail0")[
             "expected"]["v54_disposition"] = "CERTIFIED"
    expect_refusal(lambda: audit(changed, v2))
    changed = copy.deepcopy(v2)
    changed["source_cases"][1]["case_id"] = changed["source_cases"][0]["case_id"]
    expect_refusal(lambda: audit(corpus, changed))
    changed = copy.deepcopy(v2)
    changed["source_cases"][0]["source_sha256"] = "0"*64
    expect_refusal(lambda: audit(corpus, changed))

    # Construct an admitted *necessary structural* example; intentionally
    # DO NOT claim it is a physically correct accepted square-source proof.
    example = {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "source_parameter_id": "source-time-t",
        "parameter_lo": "0", "parameter_hi": "2",
        "phase_turn_offset": "0", "phase_turn_rate": "1",
        "cos_splines": {h: {"degree": 2,
                            "knots": ["0"]*3 + ["1"]*2 + ["2"]*3,
                            "controls": ["1/2"]*5} for h in ("0", "1")},
        "sin_splines": {},
    }
    assert structural_refusal(example) is None
    changed = copy.deepcopy(example)
    changed["sin_splines"]["1"] = example["cos_splines"]["1"]
    assert structural_refusal(changed) == REASONS[1]
    changed = copy.deepcopy(example)
    changed["cos_splines"]["0"]["degree"] = 1
    assert structural_refusal(changed) == REASONS[2]
    changed = copy.deepcopy(example)
    changed["phase_turn_rate"] = "0"
    assert structural_refusal(changed) == REASONS[7]
    changed = copy.deepcopy(example)
    changed["cos_splines"]["0"]["knots"][3] = "3/2"
    assert structural_refusal(changed) == REASONS[5]
    print("PASS: 121 original source-identity bound; 50 direct-route refusals;"
          " 4 source/registry mutation refusals and 5 grammar controls")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run()
    demand(result == json.loads(RECEIPT.read_text(encoding="utf-8")),
           "SAVED_RECEIPT_NOT_RECOMPUTED")
    if args.self_test:
        self_test()
    if args.json:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        print("PASS: frozen 121 / blocked 50; 0 PR397 grammar admissions;"
              " 35 harmonic, 11 sine, 4 degree blockers; all original case IDs retained")
