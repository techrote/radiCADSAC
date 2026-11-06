#!/usr/bin/env python3
"""PB-007-01 / PO-05/08: source-bound V23 signed knot crossing.

This is one original frozen v54 nonstationary multi-span ordered-premise
candidate, NOT a general analytic event oracle or a PB-007 discharge.
All mathematical sign claims use exact rational inequalities, not sampling.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import re
import tempfile

HERE = Path(__file__).resolve().parent
CASE_ID = "composite:PB00701_V23_EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR:tail0"
CASE_SHA = "e8d2451833854ee7eaf73d4fb70b78b86ba72194b2688876f3bb9ee6ab132ffd"
ROW_SHA = "e52a27e5c3dcdf984919cdcd7bb925c52d2865550035da357cd87178b9fbfc89"
CORPUS = HERE / "pb00701-finite-owner-corpus-v54.json"
V2 = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
RECEIPT = HERE / "pb00701-v23-signed-knot-20261106.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
SCHEMA = "radicadsac-pb00701-v23-signed-knot-source/1.0"
EVIDENCE_CLASS = "DETERMINISTIC_MODEL"
MAX_CORPUS = 300000
MAX_V2 = 200000
MAX_RECEIPT = 30000


class Refused(ValueError):
    """Nontruth: the candidate is not admitted under the proved premises."""


def need(condition, reason):
    if not condition:
        raise Refused(reason)


def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def read_pinned(path, byte_limit, blob=None):
    with Path(path).open("rb") as stream:
        raw = stream.read(byte_limit + 1)
    need(len(raw) <= byte_limit, "INPUT_BYTE_BUDGET_REFUSAL")
    if blob is not None:
        need(git_blob(raw) == blob, "PINNED_GIT_BLOB_DRIFT")
    return raw


def unique_pairs(pairs):
    out = {}
    for k, v in pairs:
        need(k not in out, "DUPLICATE_JSON_KEY")
        out[k] = v
    return out


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique_pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(Refused("NONFINITE_JSON")))


def sha_json(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")).hexdigest()


TOKEN = re.compile(r"-?(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?\Z")


def q(text):
    need(type(text) is str and len(text) <= 128 and TOKEN.fullmatch(text),
         "NONCANONICAL_OR_OVERSIZED_RATIONAL_TOKEN")
    result = Q(text)
    need(result.denominator <= 2**512 and result.numerator.bit_length() <= 512,
         "RATIONAL_ARITHMETIC_BUDGET_REFUSAL")
    return result


def two_pieces(record):
    """Lower precisely the fully clamped degree-0/1 two-span rational splines.

    Each tuple is a polynomial (constant, t coefficient) in ORIGINAL global
    parameter t. One-sided knot limits are calculated independently.
    """
    need(type(record) is dict and set(record) == {"degree", "knots", "controls"},
         "CHANNEL_SCHEMA_REFUSAL")
    d = record["degree"]
    need(type(d) is int and d in (0, 1), "UNSUPPORTED_SPLINE_DEGREE")
    knots = record["knots"]
    controls = record["controls"]
    if d == 0:
        need(knots == ["0", "1", "2"] and type(controls) is list and len(controls) == 2,
             "NONCLAMPED_TWO_SPAN_CONSTANT_SPLINE")
        a, b = [q(v) for v in controls]
        return ((a, Q(0)), (b, Q(0)))
    need(knots == ["0", "0", "1", "1", "2", "2"] and
         type(controls) is list and len(controls) == 4,
         "NONCLAMPED_TWO_SPAN_LINEAR_SPLINE")
    a, b, c, d1 = [q(v) for v in controls]
    return ((a, b - a), (2*c - d1, d1 - c))


def at(poly, point):
    return poly[0] + poly[1] * point


def source_terms(spec):
    need(type(spec) is dict and set(spec) ==
         {"grammar", "source_parameter_id", "parameter_lo", "parameter_hi",
          "phase_turn_offset", "phase_turn_rate", "cos_splines", "sin_splines"},
         "ORIGINAL_SOURCE_SCHEMA_MISMATCH")
    need(spec["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE"
         and spec["source_parameter_id"] == "source-time-t"
         and [spec["parameter_lo"], spec["parameter_hi"]] == ["0", "2"]
         and [spec["phase_turn_offset"], spec["phase_turn_rate"]] == ["0", "1/12"],
         "SOURCE_TIME_OR_GLOBAL_PHASE_MISMATCH")
    need(type(spec["cos_splines"]) is dict and
         set(spec["cos_splines"]) == {"0", "2"} and
         type(spec["sin_splines"]) is dict and set(spec["sin_splines"]) == {"1"},
         "UNSUPPORTED_HARMONIC_INVENTORY")
    c0 = two_pieces(spec["cos_splines"]["0"])
    c2 = two_pieces(spec["cos_splines"]["2"])
    s1 = two_pieces(spec["sin_splines"]["1"])
    for channel in (c0, c2, s1):
        need(at(channel[0], Q(1)) == at(channel[1], Q(1)),
             "SOURCE_KNOT_CHANNEL_DISCONTINUITY")
    # These identities are coefficients RECONSTRUCTED from original controls.
    # They are the explicit narrow grammar for this single pinned historical ID.
    need(c0 == ((Q(-501,1000), Q(0)), (Q(-501,1000), Q(0))) and
         c2 == ((Q(0), Q(1,1000)), (Q(1,1000), Q(0))) and
         s1 == ((Q(1), Q(1,1000)), (Q(1001,1000), Q(0))),
         "SIGNED_V23_DERIVATIVE_SECTOR_GRAMMAR_REFUSAL")
    return c0, c2, s1


def prove_source(spec):
    """Derive an exhaustive sign/root claim solely from checked inequalities.

    theta=pi*t/6. F=C0(t)+C2(t)*cos(2theta)+S1(t)*sin(theta).
    3<pi<4; on t in [0,1], cos(2theta)>=1/2 and cos(theta)>=1/2;
    on [0,2], sin(2theta)<=1 and cos(theta)>=1/2; all required sines
    are nonnegative. The derivative bounds below are strict and uniform.
    """
    c0, c2, s1 = source_terms(spec)
    need(sha_json(spec) == CASE_SHA, "ORIGINAL_SOURCE_SHA256_DRIFT")
    left_c2_slope = c2[0][1]
    left_c2_max = at(c2[0], Q(1))
    left_s1_min = at(s1[0], Q(0))
    need(c0[0][1] == 0 and left_c2_slope >= 0 and left_c2_max >= 0 and
         s1[0][1] >= 0 and left_s1_min > 0,
         "LEFT_SECTOR_SIGN_PREMISE_REFUSAL")
    # Derivative C2' cos(2theta) - (pi/3) C2 sin(2theta)
    #           + S1' sin(theta) + (pi/6) S1 cos(theta).
    left_deriv_lower = left_c2_slope/2 - Q(4,3)*left_c2_max + left_s1_min/4
    need(left_deriv_lower == Q(299,1200) and left_deriv_lower > 0,
         "LEFT_STRICT_DERIVATIVE_NOT_PROVED")
    need(c0[1][1] == c2[1][1] == s1[1][1] == 0 and
         c2[1][0] >= 0 and s1[1][0] > 0,
         "RIGHT_SECTOR_SIGN_PREMISE_REFUSAL")
    # F'_right/pi >= -C2/3 + S1/12 via sin(2theta)<=1, cos(theta)>=1/2.
    right_pi_factor = s1[1][0]/12 - c2[1][0]/3
    need(right_pi_factor == Q(997,12000) and right_pi_factor > 0,
         "RIGHT_STRICT_DERIVATIVE_NOT_PROVED")
    f0 = at(c0[0], Q(0)) + at(c2[0], Q(0))  # cos0=1, sin0=0
    # theta(1)=pi/6, cos(2theta)=sin(theta)=1/2.
    knot_l = at(c0[0], Q(1)) + (at(c2[0], Q(1)) + at(s1[0], Q(1)))/2
    knot_r = at(c0[1], Q(1)) + (at(c2[1], Q(1)) + at(s1[1], Q(1)))/2
    # theta(2)=pi/3, cos(2theta)=-1/2, sin(theta)=sqrt(3)/2;
    # sqrt(3)>3/2 gives a strictly positive rational lower bound.
    f2_lower = at(c0[1], Q(2)) - at(c2[1], Q(2))/2 + 3*at(s1[1], Q(2))/4
    need(f0 == Q(-501,1000) and knot_l == knot_r == 0 and
         f2_lower == Q(997,4000) and f2_lower > 0,
         "ROOT_ENDPOINT_OR_KNOT_IDENTITY_NOT_PROVED")
    return {
        "case_id": CASE_ID, "source_sha256": CASE_SHA,
        "source_row_sha256": ROW_SHA, "evidence_class": EVIDENCE_CLASS,
        "source_interval": ["0", "2"], "physical_knot": "1",
        "phase_turns": {"offset": "0", "rate": "1/12"},
        "reconstructed_global_coefficients": {
            k: [[str(v) for v in pair] for pair in channel]
            for k, channel in (("cos0", c0), ("cos2", c2), ("sin1", s1))
        },
        "proof": {
            "method": "EXACT_TWO_PIECE_SIGNED_DERIVATIVE_SECTOR",
            "pi_strict_bounds": ["3", "4"],
            "left_piece_strict_derivative_rational_lower_bound": str(left_deriv_lower),
            "right_piece_strict_derivative_pi_factor_lower_bound": str(right_pi_factor),
            "F_at_0": str(f0), "F_at_1_left": str(knot_l),
            "F_at_1_right": str(knot_r),
            "F_at_2_strict_rational_lower_bound": str(f2_lower),
            "exact_open_root_count": 0,
            "source_knot_root": {
                "source_value": "1", "event_kind": "CROSSING",
                "left_inward_sign": "NEGATIVE", "right_inward_sign": "POSITIVE",
                "left_sided_order": 1, "right_sided_order": 1,
                "global_analytic_multiplicity_claimed": False,
            },
            "source_exteriors": {
                "0": {"relation": "NEGATIVE", "root": False},
                "2": {"relation": "POSITIVE", "root": False},
            },
            "maximal_nonzero_cells": [
                {"interval": ["0", "1"], "interior_sign": "NEGATIVE",
                 "left_endpoint_included": True, "right_endpoint_included": False},
                {"interval": ["1", "2"], "interior_sign": "POSITIVE",
                 "left_endpoint_included": False, "right_endpoint_included": True}
            ],
            "phase_monotonicity_substituted_for_physical_sign": False,
            "subdivision_scan_or_timeout_as_truth": False,
        }
    }


def case_and_v2():
    corpus = decode(read_pinned(CORPUS, MAX_CORPUS, CORPUS_BLOB))
    v2 = decode(read_pinned(V2, MAX_V2, V2_BLOB))
    cases = corpus["cases"]
    need(len(cases) == 121 and len({r["id"] for r in cases}) == 121,
         "FROZEN_121_SOURCE_DENOMINATOR_CHANGED")
    counts = Counter(r["expected"]["v54_disposition"] for r in cases)
    need(counts["BLOCKED"] == 20 and
         counts["BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"] == 30,
         "FROZEN_20_30_DENOMINATOR_CHANGED")
    need(len(v2["source_cases"]) == 50 and
         len({r["case_id"] for r in v2["source_cases"]}) == 50,
         "V2_SOURCE_WITNESS_DENOMINATOR_CHANGED")
    source = next(r for r in cases if r["id"] == CASE_ID)
    need(source["expected"]["v54_disposition"] ==
         "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE" and
         sha_json(source["spec"]) == CASE_SHA and
         sha_json(source) == ROW_SHA,
         "SELECTED_HISTORICAL_CASE_PROVENANCE_DRIFT")
    evidence = next(x for x in v2["source_cases"] if x["case_id"] == CASE_ID)
    need(evidence["source_sha256"] == CASE_SHA and
         evidence["original_row_sha256"] == ROW_SHA and
         evidence["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC" and
         evidence["historical_v54_disposition"] ==
             "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE",
         "PREEXISTING_SOURCE_SPECIFIC_WITNESS_DRIFT")
    need(evidence["source_interval"] == ["0","2"] and
         evidence["original_source_piece_edges"] == ["0","1","2"],
         "ORIGINAL_KNOT_OR_ENDPOINT_CUSTODY_DRIFT")
    return source["spec"]


def expected_receipt():
    proof = prove_source(case_and_v2())
    return {
        "schema": SCHEMA, "evidence_class": EVIDENCE_CLASS,
        "frozen_corpus_git_blob": CORPUS_BLOB,
        "preexisting_v2_git_blob": V2_BLOB,
        "case_certificate": proof,
        "before_after": {
            "frozen_source_population_before": 121,
            "frozen_source_population_after": 121,
            "historical_route_refusals_before": 20,
            "historical_route_refusals_after": 20,
            "historical_missing_ordered_before": 30,
            "historical_missing_ordered_after": 30,
            "existing_complete_v2_witnesses_before": 50,
            "existing_complete_v2_witnesses_after": 50,
            "new_source_specific_complete_witnesses": 0,
            "new_candidate_ordered_premise_case_ids": [CASE_ID],
            "standalone_candidate_missing_ordered_after": 29,
            "conditional_union_with_unmerged_421_after": 27,
            "conditional_union_not_authoritative": True,
            "required_PB007_or_PO_obligations_discharged": 0,
            "MC_B_or_MC1_established": False,
            "frozen_evidence_modified": False,
        },
    }


def validate_receipt(candidate, expected):
    need(type(candidate) is dict and candidate == expected, "RECEIPT_PROOF_OR_PROVENANCE_MISMATCH")
    return True


def refuse(fn):
    try:
        fn()
    except (Refused, ValueError, KeyError, TypeError):
        return
    raise AssertionError("adversarial source or claimed certificate was admitted")


def self_test():
    spec = case_and_v2()
    proof = prove_source(spec)
    need(proof["proof"]["source_knot_root"]["right_sided_order"] == 1,
         "LOST_ONE_SIDED_KNOT_ORDER")
    expected = expected_receipt()
    validate_receipt(expected, expected)
    for family, key, mutate in (
        ("cos_splines", "0", lambda x: x["controls"].__setitem__(0, "-500/1000")),
        ("cos_splines", "2", lambda x: x["controls"].__setitem__(1, "0")),
        ("sin_splines", "1", lambda x: x["controls"].__setitem__(1, "0")),
        ("cos_splines", "2", lambda x: x["knots"].__setitem__(2, "3/4")),
        ("sin_splines", "1", lambda x: x.__setitem__("degree", 2)),
    ):
        bad = deepcopy(spec)
        mutate(bad[family][key])
        refuse(lambda b=bad: prove_source(b))
    for field, value in (("phase_turn_rate", "0"), ("phase_turn_offset", "1/12"),
                         ("parameter_hi", "1"), ("source_parameter_id", "other")):
        bad = deepcopy(spec)
        bad[field] = value
        refuse(lambda b=bad: prove_source(b))
    # A true but arbitrarily tiny perturbation is not rounded into a knot zero.
    delta = Q(1, 2**120)
    need(delta > 0 and (Q(-501,1000) + delta) != Q(-501,1000),
         "RATIONAL_CLOSE_ROOT_CONTROL_FAILED")
    bad = deepcopy(spec)
    bad["cos_splines"]["0"]["controls"][1] = str(Q(-501,1000) + delta)
    refuse(lambda: prove_source(bad))
    # Identity-zero and repeated/tangential polynomial sources are outside
    # this strict sine-bearing derivative cone. Refusal != nonmonotonicity.
    zero = deepcopy(spec)
    for chan in ("cos_splines", "sin_splines"):
        for entry in zero[chan].values():
            entry["controls"] = ["0"] * len(entry["controls"])
    refuse(lambda: prove_source(zero))
    tangent = deepcopy(spec)
    tangent["cos_splines"]["0"] = {
        "degree": 2, "knots": ["0","0","0","1","1","1","2","2","2"],
        "controls": ["1","-1","1","1","-1","1"]
    }
    refuse(lambda: prove_source(tangent))
    for mutate in (
        lambda v: v["case_certificate"]["proof"]["source_knot_root"].__setitem__("left_sided_order", 2),
        lambda v: v["case_certificate"]["proof"]["maximal_nonzero_cells"][1].__setitem__("interior_sign", "NEGATIVE"),
        lambda v: v["before_after"].__setitem__("historical_missing_ordered_after", 29),
        lambda v: v["before_after"].__setitem__("required_PB007_or_PO_obligations_discharged", 1),
        lambda v: v["case_certificate"].__setitem__("source_sha256", "0"*64),
        lambda v: v["case_certificate"]["proof"]["source_knot_root"].__setitem__("global_analytic_multiplicity_claimed", True)
    ):
        bad = deepcopy(expected)
        mutate(bad)
        refuse(lambda b=bad: validate_receipt(b, expected))
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "oversize.json"
        p.write_bytes(b" " * 128)
        refuse(lambda: read_pinned(p, 64))
    print("V23 original source, signed-knot proof, 21+ adversarial controls: PASS")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    need(args.contract or args.self_test, "CONTRACT_OR_SELF_TEST_REQUIRED")
    expected = expected_receipt()
    saved = decode(read_pinned(RECEIPT, MAX_RECEIPT))
    validate_receipt(saved, expected)
    if args.self_test:
        self_test()
    print(json.dumps({"status": "SOURCE_BOUND_SIGNED_KNOT_CANDIDATE",
                      "case_id": CASE_ID, "missing_ordered_candidate_delta": -1,
                      "frozen_v54_delta": 0, "PB007_discharged": False},
                     sort_keys=True))


if __name__ == "__main__":
    main()
