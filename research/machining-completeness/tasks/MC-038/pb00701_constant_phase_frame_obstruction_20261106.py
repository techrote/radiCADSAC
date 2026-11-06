#!/usr/bin/env python3
"""PB-007-01 narrow C: source-bound obstruction to CONSTANT H1 phase-frame rotation.

This checks necessary coefficient-frame geometry, NOT physical root isolation.
An exactly nonzero determinant of two original coefficient vectors is a complete
counterexample to the claim that ONE constant phase shift/reflection removes S1.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "pb00701-finite-owner-corpus-v54.json"
V2 = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
RECEIPT = HERE / "pb00701-constant-phase-frame-obstruction-20261106.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
MAX_CORPUS = 300000
MAX_V2 = 220000
MAX_RECEIPT = 65536
SCHEMA = "radicadsac-pb00701-constant-phase-frame-obstruction/1.0"
EVIDENCE = "DETERMINISTIC_MODEL"
SELECTED = {
    "composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail0": {
        "sha": "4d1ef1cbecceeb4a43b4e30fd37327fa204164cc9ce25dfe4f1744a052cebcc2",
        "row": "406ec73609a8213051afd3361478416e496c782b2b89ae2a857b772146059279",
        "disposition": "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE",
        "interval": ["0", "2"], "knot": ["0", "1", "2"],
        "det": "-1/2",
    },
    "harvested:verify_pb00701_v9:4e7b85fa122a": {
        "sha": "a83ca0cd16c7822e6525f8f2d2df26a54f45b99807cadebc67f31fc49b066c10",
        "row": "62346bbddca22c4271a14c10aa130327013ac7cf8daa0b0ae515257e8f28cfad",
        "disposition": "BLOCKED", "interval": ["0", "1"],
        "knot": ["0", "1"], "det": "1/2",
    },
}


class Refusal(ValueError):
    """Source, proof-scope or resource failure: never a physical truth claim."""


def require(predicate, reason):
    if not predicate:
        raise Refusal(reason)


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def bytes_bounded(path, limit):
    with path.open("rb") as f:
        raw = f.read(limit + 1)
    require(len(raw) <= limit, "BYTE_BUDGET_REFUSAL")
    return raw


def no_duplicate_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "DUPLICATE_JSON_KEY_REFUSAL")
        result[key] = value
    return result


def refuse_constant(value):
    raise Refusal("NONFINITE_JSON_REFUSAL:" + value)


def read_json(path, limit, blob=None):
    raw = bytes_bounded(path, limit)
    if blob is not None:
        require(git_blob(raw) == blob, "PINNED_GIT_BLOB_DRIFT")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=no_duplicate_pairs,
                          parse_constant=refuse_constant)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise Refusal("JSON_INGRESS_REFUSAL") from exc


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def rational(text):
    require(type(text) is str and len(text) < 100, "NONCANONICAL_RATIONAL")
    try:
        value = Q(text)
    except (ValueError, ZeroDivisionError) as exc:
        raise Refusal("INVALID_RATIONAL") from exc
    require(abs(value.numerator).bit_length() <= 256 and value.denominator.bit_length() <= 256,
            "RATIONAL_BIT_BUDGET_REFUSAL")
    return value


def spline_at(spline, t):
    """Exact Cox-de Boor evaluator for strict interior ORIGINAL source time."""
    require(type(spline) is dict and set(spline) == {"degree", "controls", "knots"},
            "UNSUPPORTED_SPLINE_GRAMMAR")
    p = spline["degree"]
    require(type(p) is int and 0 <= p <= 3, "SPLINE_DEGREE_BUDGET")
    ctrl = [rational(x) for x in spline["controls"]]
    knots = [rational(x) for x in spline["knots"]]
    require(1 <= len(ctrl) <= 12 and len(knots) == len(ctrl) + p + 1,
            "SPLINE_CARDINALITY_REFUSAL")
    require(all(a <= b for a, b in zip(knots, knots[1:])),
            "UNSORTED_ORIGINAL_KNOTS")
    require(knots[p] < t < knots[-p-1], "NOT_AN_INTERIOR_SOURCE_POINT")
    work = [Q(1) if knots[i] <= t < knots[i+1] else Q(0)
            for i in range(len(knots)-1)]
    for order in range(1, p+1):
        next_work = []
        for i in range(len(work)-1):
            left_den = knots[i+order] - knots[i]
            right_den = knots[i+order+1] - knots[i+1]
            left = Q(0) if left_den == 0 else (t-knots[i])*work[i]/left_den
            right = Q(0) if right_den == 0 else (knots[i+order+1]-t)*work[i+1]/right_den
            next_work.append(left + right)
        work = next_work
    require(len(work) == len(ctrl) and sum(work) == 1,
            "INVALID_ORIGINAL_BSPLINE_PARTITION")
    return sum((c*n for c,n in zip(ctrl,work)), Q(0))


def vector_at(spec, t):
    require(spec["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
            "SOURCE_GRAMMAR_MISMATCH")
    require(spec["source_parameter_id"] == "source-time-t",
            "SOURCE_PARAMETER_MISMATCH")
    require(spec["phase_turn_offset"] == "0" and spec["phase_turn_rate"] == "1/8",
            "SOURCE_PHASE_MISMATCH")
    require("1" in spec["cos_splines"] and "1" in spec["sin_splines"],
            "MISSING_ORIGINAL_H1_CHANNEL")
    require(set(spec["cos_splines"]) <= {"0", "1"} and
            set(spec["sin_splines"]) == {"1"},
            "UNSUPPORTED_ADDITIONAL_HARMONICS")
    if "0" in spec["cos_splines"]:
        require(all(rational(x) == 0 for x in spec["cos_splines"]["0"]["controls"]),
                "NONZERO_H0_NOT_IN_THIS_COMPARISON")
    return (spline_at(spec["cos_splines"]["1"], t),
            spline_at(spec["sin_splines"]["1"], t))


def determinant(u, v):
    return u[0]*v[1] - v[0]*u[1]


def frame_challenge(spec, t0=Q(1,4), t1=Q(3,4)):
    require(t0 != t1, "DISTINCT_SOURCE_SAMPLES_REQUIRED")
    a, b = vector_at(spec, t0), vector_at(spec, t1)
    d = determinant(a, b)
    # If d=0, never turn a two-point observation into an affirmative theorem.
    return {"sample_source_t": [str(t0), str(t1)],
            "H1_vectors": [[str(c) for c in a], [str(c) for c in b]],
            "exact_rank_determinant": str(d),
            "constant_orthogonal_phase_frame_cosine_only_refuted": d != 0,
            "full_physical_zero_or_order_certificate": False}


def provenance():
    corpus = read_json(CORPUS, MAX_CORPUS, CORPUS_BLOB)
    v2 = read_json(V2, MAX_V2, V2_BLOB)
    rows = corpus["cases"]
    require(len(rows) == 121 and len({r["id"] for r in rows}) == 121,
            "ORIGINAL_SOURCE_DENOMINATOR_DRIFT")
    counts = Counter(r["expected"]["v54_disposition"] for r in rows)
    require(counts["BLOCKED"] == 20 and
            counts["BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"] == 30,
            "HISTORICAL_V54_REFUSAL_DENOMINATOR_DRIFT")
    vr = v2["source_cases"]
    require(len(vr) == 50 and len({r["case_id"] for r in vr}) == 50,
            "V2_WITNESS_DENOMINATOR_DRIFT")
    require(v2["summary"]["complete_finite_sources"] == 49 and
            v2["summary"]["complete_continuum_sources"] == 1,
            "V2_FINITE_CONTINUUM_CUSTODY_DRIFT")
    indexed = {r["id"]: r for r in rows}
    expected_unresolved = {r["id"] for r in rows if r["expected"]["v54_disposition"] in
                           {"BLOCKED", "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"}}
    require({r["case_id"] for r in vr} == expected_unresolved,
            "V2_SOURCE_UNION_MISMATCH")
    for witness in vr:
        original = indexed[witness["case_id"]]
        require(witness["source_sha256"] == sha(original["spec"]) and
                witness["original_row_sha256"] == sha(original) and
                witness["historical_v54_disposition"] == original["expected"]["v54_disposition"] and
                witness["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC",
                "V2_ORIGINAL_SOURCE_HASH_OR_DISPOSITION_MISMATCH")
    return indexed, {r["case_id"]: r for r in vr}


def produce():
    indexed, witnesses = provenance()
    results = []
    for case_id, expected in SELECTED.items():
        row = indexed[case_id]
        spec = row["spec"]
        require(sha(spec) == expected["sha"] and sha(row) == expected["row"],
                "SELECTED_ORIGINAL_SHA_MISMATCH")
        require(row["expected"]["v54_disposition"] == expected["disposition"] and
                witnesses[case_id]["source_sha256"] == expected["sha"],
                "SELECTED_V54_OR_V2_ROUTE_MISMATCH")
        require([spec["parameter_lo"], spec["parameter_hi"]] == expected["interval"] and
                spec["phase_turn_offset"] == "0" and spec["phase_turn_rate"] == "1/8",
                "ORIGINAL_INTERVAL_OR_PHASE_MISMATCH")
        all_knots = sorted({k for s in list(spec["cos_splines"].values())+
                            list(spec["sin_splines"].values()) for k in s["knots"]},
                           key=rational)
        require(all_knots == expected["knot"], "ORIGINAL_SOURCE_PIECE_KNOT_MISMATCH")
        witness = frame_challenge(spec)
        require(witness["exact_rank_determinant"] == expected["det"] and
                witness["constant_orthogonal_phase_frame_cosine_only_refuted"] is True,
                "NECESSARY_PHASE_FRAME_OBSTRUCTION_NOT_ESTABLISHED")
        results.append({"case_id": case_id, "source_sha256": expected["sha"],
                        "original_row_sha256": expected["row"],
                        "historical_v54_disposition": expected["disposition"],
                        "source_interval": expected["interval"],
                        "original_piece_edges": expected["knot"],
                        "phase_turn_law": {"offset": "0", "rate": "1/8"},
                        **witness})
    return {"schema": SCHEMA, "task": "MC-038", "evidence_class": EVIDENCE,
            "claim": "ONE_GLOBAL_CONSTANT_PHASE_SHIFT_ELIMINATES_H1_SINE_REFUTED_FOR_TWO_ORIGINALS",
            "frozen_corpus_git_blob": CORPUS_BLOB, "frozen_v2_registry_git_blob": V2_BLOB,
            "cases": results,
            "before_after": {"original_sources": [121,121], "route_refusals": [20,20],
                             "missing_ordered": [30,30], "v2_complete_witnesses": [50,50],
                             "required_pb_po_discharges": [0,0],
                             "newly_closed_historical_case_ids": []},
            "limits": {"source_specific": True, "variable_phase_reparam_excluded": True,
                       "original_source_event_theorem_claimed": False,
                       "mc_b_or_mc1_established": False,
                       "production_authorized": False}}


def expect_refusal(thunk):
    try:
        thunk()
    except (Refusal, ValueError, KeyError, TypeError):
        return
    raise AssertionError("negative mutation was incorrectly admitted")


def self_test():
    rows, _ = provenance()
    for case_id in SELECTED:
        spec = rows[case_id]["spec"]
        assert frame_challenge(spec)["constant_orthogonal_phase_frame_cosine_only_refuted"]
        for field, changed in [("phase_turn_rate", "1/7"),
                               ("source_parameter_id", "substituted-u")]:
            mutated = deepcopy(spec)
            mutated[field] = changed
            expect_refusal(lambda mutated=mutated: vector_at(mutated, Q(1,4)))
        altered = deepcopy(spec)
        altered["cos_splines"]["1"]["controls"][0] = "17/19"
        assert sha(altered) != SELECTED[case_id]["sha"]
        expect_refusal(lambda altered=altered: require(
            sha(altered) == SELECTED[case_id]["sha"], "ORIGINAL_CONTROL_MUTATION"))
    v9 = rows["composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail0"]["spec"]
    close = frame_challenge(v9, Q(1,2), Q(1,2)+Q(1,2**120))
    assert Q(close["exact_rank_determinant"]) == -Q(1,2**120)
    assert close["constant_orthogonal_phase_frame_cosine_only_refuted"]
    # A pair of proportional vectors proves NO universal positive admission.
    parallel = determinant((Q(1),Q(2)), (Q(3),Q(6)))
    assert parallel == 0
    assert determinant((Q(0),Q(0)), (Q(0),Q(0))) == 0  # identity-zero: not a root witness
    # A polynomial varying between sampled positions might have determinant=0
    # at the pair; zero is INCONCLUSIVE, not permission to eliminate sine.
    assert determinant((Q(1),Q(0)), (Q(1),Q(0))) == 0
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "bad.json"
        p.write_text('{"claim":0,"claim":true}', encoding="utf-8")
        expect_refusal(lambda: read_json(p, MAX_RECEIPT))
        p.write_text('{"claim":NaN}', encoding="utf-8")
        expect_refusal(lambda: read_json(p, MAX_RECEIPT))
        p.write_bytes(b" " * (MAX_RECEIPT + 1))
        expect_refusal(lambda: read_json(p, MAX_RECEIPT))
    expected = produce()
    tampered = deepcopy(expected)
    tampered["before_after"]["missing_ordered"][1] = 28
    require(canonical(tampered) != canonical(expected), "RECEIPT_TYPE_OR_CENSUS_ALIAS")
    tampered = deepcopy(expected)
    tampered["limits"]["production_authorized"] = 0
    require(canonical(tampered) != canonical(expected), "RECEIPT_BOOL_INT_ALIAS")
    assert len(expected["cases"]) == 2
    print("PASS: two pinned originals, exact rank obstruction, provenance and adversarial refusals")


def main():
    args = argparse.ArgumentParser()
    args.add_argument("--contract", action="store_true")
    args.add_argument("--self-test", action="store_true")
    args.add_argument("--report", action="store_true")
    opts = args.parse_args()
    try:
        if opts.self_test:
            self_test()
        result = produce()
        if opts.contract:
            saved = read_json(RECEIPT, MAX_RECEIPT)
            require(canonical(saved) == canonical(result), "MACHINE_RECEIPT_NOT_REPRODUCED")
        if opts.report:
            print(json.dumps(result, sort_keys=True, indent=2))
        elif not opts.self_test:
            print("PASS: exact constant-phase-frame counterexample; historical deltas all zero")
    except (Refusal, ValueError, TypeError, KeyError, OSError, MemoryError,
            RecursionError, OverflowError) as exc:
        print("REFUSED: " + str(exc), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
