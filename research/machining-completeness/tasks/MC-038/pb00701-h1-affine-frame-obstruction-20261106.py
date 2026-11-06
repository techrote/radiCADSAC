#!/usr/bin/env python3
"""Original-source H1 affine-frame obstruction; no universal PB-007 claim."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
FROZEN = HERE / "pb00701-finite-owner-corpus-v54.json"
REGISTER = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
PRIOR_PATH = HERE / "pb00701-v54-pr397-admission-boundary-20261105.py"
RECEIPT = HERE / "pb00701-h1-affine-frame-obstruction-20261106.json"
FROZEN_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
REGISTER_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
PRIOR_BLOB = "944565a534adc6703189291ac2cc55b97ad4736c"
SCHEMA = "radicadsac-pb00701-h1-affine-frame-obstruction/1.0"
ROUTE = "AFFINE_PHASE_FRAME_ERASES_H1_SINE_WITH_UNRESTRICTED_AMPLITUDE"
NAMES = (
    "composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail0",
    "harvested:verify_pb00701_v9:4e7b85fa122a",
)
SOURCES = (
    "4d1ef1cbecceeb4a43b4e30fd37327fa204164cc9ce25dfe4f1744a052cebcc2",
    "a83ca0cd16c7822e6525f8f2d2df26a54f45b99807cadebc67f31fc49b066c10",
)
ROWS = (
    "406ec73609a8213051afd3361478416e496c782b2b89ae2a857b772146059279",
    "62346bbddca22c4271a14c10aa130327013ac7cf8daa0b0ae515257e8f28cfad",
)
DISPOSITIONS = (
    "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE",
    "BLOCKED",
)


class Refusal(ValueError):
    """Nontruth refusal; a resource or grammar limit is not zero evidence."""


def need(value, code):
    if not value:
        raise Refusal(code)


def git_blob(raw):
    return hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    ).hexdigest()


def text_rational(value):
    need(type(value) is str and 0 < len(value) <= 100, "INVALID_RATIONAL_TOKEN")
    try:
        result = Fraction(value)
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise Refusal("INVALID_RATIONAL") from exc
    need(str(result) == value, "NONCANONICAL_RATIONAL")
    need(max(result.numerator.bit_length(), result.denominator.bit_length()) <= 256,
         "RATIONAL_BIT_BUDGET")
    return result


def trim(poly):
    p = list(poly)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def checked_poly(values):
    need(type(values) is list and 0 < len(values) <= 9, "DEGREE_BUDGET")
    p = []
    for value in values:
        need(type(value) is Fraction, "POLY_COEFFICIENT_NOT_EXACT")
        need(max(value.numerator.bit_length(), value.denominator.bit_length()) <= 256,
             "POLY_COEFFICIENT_BIT_BUDGET")
        p.append(value)
    return trim(p)


def multiply(a, b):
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, u in enumerate(a):
        for j, v in enumerate(b):
            out[i + j] += u * v
    return trim(out)


def subtract(a, b):
    return trim([(a[i] if i < len(a) else 0) -
                 (b[i] if i < len(b) else 0)
                 for i in range(max(len(a), len(b)))])


def add(a, b):
    return trim([(a[i] if i < len(a) else 0) +
                 (b[i] if i < len(b) else 0)
                 for i in range(max(len(a), len(b)))])


def derivative(a):
    return [Fraction(i) * a[i] for i in range(1, len(a))] or [Fraction(0)]


def rational_polynomial_witness(c_values, s_values):
    """Exact W=C*S'-S*C', q=C^2+S^2; this is NOT a root oracle."""
    c, s = checked_poly(c_values), checked_poly(s_values)
    need(any(c) or any(s), "IDENTITY_ZERO_HAS_NO_ORIENTATION")
    w = subtract(multiply(c, derivative(s)), multiply(s, derivative(c)))
    q = add(multiply(c, c), multiply(s, s))
    degree = max(len(c), len(s)) - 1
    # Nonzero real leading-coefficient squares prevent cancellation in q.
    need(len(q) == 2 * degree + 1 and q[-1] > 0,
         "POLYNOMIAL_DEGREE_INVARIANT")
    need(not any(max(v.numerator.bit_length(), v.denominator.bit_length()) > 4096
                 for v in w + q), "DERIVED_BIT_BUDGET")
    need(not any(w) or len(w) <= 2 * degree,
         "WRONSKIAN_DEGREE_INVARIANT")
    return {
        "C_coefficients_ascending": [str(x) for x in c],
        "S_coefficients_ascending": [str(x) for x in s],
        "W_coefficients_ascending": [str(x) for x in w],
        "q_coefficients_ascending": [str(x) for x in q],
        "nonzero_wronskian_blocks_every_affine_phase": any(w),
    }


def first_span_affine(channel, one_span):
    need(type(channel) is dict and set(channel) ==
         {"degree", "knots", "controls"}, "CHANNEL_GRAMMAR")
    degree, knots, controls = (
        channel["degree"], channel["knots"], channel["controls"]
    )
    need(type(degree) is int and type(knots) is list and
         type(controls) is list, "SPLINE_GRAMMAR")
    all_controls = [text_rational(x) for x in controls]
    if degree == 1:
        expected = (["0", "0", "1", "1"] if one_span else
                    ["0", "0", "1", "1", "2", "2"])
        need(knots == expected and len(all_controls) ==
             (2 if one_span else 4), "SOURCE_KNOT_OR_CONTROL_MISMATCH")
        return [all_controls[0], all_controls[1] - all_controls[0]]
    if degree == 0 and not one_span:
        need(knots == ["0", "1", "2"] and len(all_controls) == 2,
             "SOURCE_KNOT_OR_CONTROL_MISMATCH")
        return [all_controls[0], Fraction(0)]
    raise Refusal("UNSUPPORTED_FIRST_SPAN_GRAMMAR")


def original_case(row, v2, which, prior):
    name = NAMES[which]
    need(row["id"] == name and row["origin"] ==
         ("verify_pb00701_v10" if which == 0 else "verify_pb00701_v9"),
         "ORIGINAL_PROVENANCE")
    need(row["kind"] == ("COMPOSITE_TAIL" if which == 0 else "HARVESTED"),
         "ORIGINAL_KIND")
    spec = row["spec"]
    need(hashlib.sha256(prior.encode(spec)).hexdigest() == SOURCES[which] and
         hashlib.sha256(prior.encode(row)).hexdigest() == ROWS[which],
         "SOURCE_OR_ROW_SHA256_DRIFT")
    need(row["expected"]["v54_disposition"] == DISPOSITIONS[which] and
         row["expected"]["observed"]["status"] ==
         ("CERTIFIED" if which == 0 else "BLOCKED"),
         "HISTORICAL_REFUSAL_DRIFT")
    need(spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE" and
         spec.get("source_parameter_id") == "source-time-t" and
         spec.get("parameter_lo") == "0" and
         spec.get("parameter_hi") == ("2" if which == 0 else "1") and
         spec.get("phase_turn_offset") == "0" and
         spec.get("phase_turn_rate") == "1/8", "SOURCE_PHASE_OR_INTERVAL")
    need(set(spec["cos_splines"]) ==
         ({"0", "1"} if which == 0 else {"1"}) and
         set(spec["sin_splines"]) == {"1"}, "SOURCE_HARMONIC_INVENTORY")
    one = which == 1
    if not one:
        need(spec["cos_splines"]["0"] ==
             {"degree": 0, "knots": ["0", "1", "2"],
              "controls": ["0", "0"]}, "H0_CHANGED")
    c = first_span_affine(spec["cos_splines"]["1"], one)
    s = first_span_affine(spec["sin_splines"]["1"], one)
    witness = rational_polynomial_witness(c, s)
    need(witness["C_coefficients_ascending"] ==
         (["-1/2", "1"] if which == 0 else ["1"]) and
         witness["S_coefficients_ascending"] ==
         (["1"] if which == 0 else ["-1/2", "1"]) and
         witness["W_coefficients_ascending"] ==
         (["-1"] if which == 0 else ["1"]) and
         witness["q_coefficients_ascending"] == ["5/4", "-1", "1"] and
         witness["nonzero_wronskian_blocks_every_affine_phase"],
         "ORIGINAL_WRONSKIAN_OR_NORM_MISMATCH")
    need(v2["source_sha256"] == SOURCES[which] and
         v2["original_row_sha256"] == ROWS[which] and
         v2["historical_v54_disposition"] == DISPOSITIONS[which] and
         v2["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC" and
         v2["evidence"]["source_sha256"] == SOURCES[which],
         "COMPLETE_V2_SOURCE_WITNESS_DRIFT")
    return {
        "case_id": name,
        "source_sha256": SOURCES[which],
        "source_row_sha256": ROWS[which],
        "historical_v54_disposition": DISPOSITIONS[which],
        "first_original_span": ["0", "1"],
        "true_original_source_knot": ("1" if which == 0 else None),
        "phase_turns_offset": "0",
        "phase_turns_rate": "1/8",
        **witness,
    }


def load_prior():
    raw = PRIOR_PATH.read_bytes()
    need(len(raw) <= 32_768 and git_blob(raw) == PRIOR_BLOB,
         "PRIOR_PINNED_CENSUS_CHECKER_DRIFT")
    spec = importlib.util.spec_from_file_location("pinned_v54_audit", PRIOR_PATH)
    need(spec is not None and spec.loader is not None, "PINNED_CHECKER_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def audit(corpus, register, prior):
    baseline = prior.audit(corpus, register)
    need(len(baseline["historical_case_refusals"]) == 50 and
         baseline["before_after"]["originals"]["before"] == 121 and
         baseline["before_after"]["historical_route_refusals"]["before"] == 20 and
         baseline["before_after"]["missing_ordered_premises"]["before"] == 30 and
         baseline["before_after"]["existing_complete_source_specific"]["before"] == 50,
         "PINNED_CENSUS_MISMATCH")
    rows = {x["id"]: x for x in corpus["cases"]}
    proofs = {x["case_id"]: x for x in register["source_cases"]}
    cases = [original_case(rows[NAMES[i]], proofs[NAMES[i]], i, prior)
             for i in range(2)]
    counts = {
        "frozen_original_sources": {"before": 121, "after": 121, "delta": 0},
        "historical_route_refusals": {"before": 20, "after": 20, "delta": 0},
        "historical_missing_ordered": {"before": 30, "after": 30, "delta": 0},
        "already_complete_v2_originals": {"before": 50, "after": 50, "delta": 0},
    }
    return {
        "schema": SCHEMA,
        "proposed_route": ROUTE,
        "disposition": "FALSIFIED_FOR_TWO_FROZEN_ORIGINAL_FIRST_SPANS",
        "evidence_class": "DETERMINISTIC_MODEL",
        "frozen_corpus_git_blob": FROZEN_BLOB,
        "frozen_v2_git_blob": REGISTER_BLOB,
        "pinned_census_checker_git_blob": PRIOR_BLOB,
        "proof_method": "EXACT_NONZERO_WRONSKIAN_AND_POLYNOMIAL_DEGREE_CONTRADICTION",
        "cases": cases,
        "matched_census": counts,
        "new_historical_ids_closed": [],
        "required_pb_po_discharges": 0,
        "claim_boundaries": {
            "all_polynomial_pairs_with_nonzero_W_block_affine_frame": True,
            "unrestricted_nonlinear_phase_excluded": False,
            "rational_amplitude_assumed": False,
            "root_solver_constructed": False,
            "general_analytic_event_theorem": False,
            "mc_b_or_mc1_established": False,
            "native_geometry": False,
            "independent_oracle": False,
            "engineering_step": False,
            "production_authorized": False,
            "supported_operations_preserved": 26,
        },
    }


def pinned_inputs(prior):
    return (
        prior.read_pinned(FROZEN, FROZEN_BLOB, 300_000),
        prior.read_pinned(REGISTER, REGISTER_BLOB, 350_000),
    )


def reject(call):
    try:
        call()
    except (Refusal, prior_refusal()):
        return
    raise AssertionError("adversary was not refused")


def prior_refusal():
    return PRIOR_REFUSAL


PRIOR_REFUSAL = Refusal


def duplicate_rejecting_json(raw):
    def unique(pairs):
        out = {}
        for k, v in pairs:
            need(k not in out, "DUPLICATE_JSON_KEY")
            out[k] = v
        return out
    def no_constant(x):
        raise Refusal("NONFINITE_JSON")
    try:
        return json.loads(raw, object_pairs_hook=unique, parse_constant=no_constant)
    except (ValueError, UnicodeDecodeError, RecursionError) as exc:
        raise Refusal("INVALID_RECEIPT_JSON") from exc


def read_receipt():
    with RECEIPT.open("rb") as stream:
        raw = stream.read(65_537)
    need(len(raw) <= 65_536, "RECEIPT_BYTE_BUDGET")
    return duplicate_rejecting_json(raw)


def self_test(prior, corpus, register, expected):
    global PRIOR_REFUSAL
    PRIOR_REFUSAL = prior.Refusal
    need(read_receipt() == expected, "RECOMPUTED_RECEIPT_MISMATCH")
    a = lambda *values: [Fraction(v) for v in values]
    # Necessary-condition negative and positive exact controls, without
    # pretending that this obstruction is a universal root-count algorithm.
    need(rational_polynomial_witness(a("-1/2", "1"), a("1"))
         ["nonzero_wronskian_blocks_every_affine_phase"], "NEGATIVE_V9")
    need(rational_polynomial_witness(a("1"), a("-1/2", "1"))
         ["nonzero_wronskian_blocks_every_affine_phase"], "NEGATIVE_V43")
    need(rational_polynomial_witness(a("3", "3"), a("4", "4"))
         ["nonzero_wronskian_blocks_every_affine_phase"] is False,
         "PROPORTIONAL_POSITIVE")
    need(rational_polynomial_witness(a("0"), a("1"))
         ["nonzero_wronskian_blocks_every_affine_phase"] is False,
         "CONSTANT_DIRECTION_POSITIVE")
    # Exact isolated zero from a scalar changing sign: the frame stays fixed.
    need(rational_polynomial_witness(a("-1/2", "1"), a("0"))
         ["nonzero_wronskian_blocks_every_affine_phase"] is False,
         "SIMPLE_ZERO_NOT_A_FRAME_OBSTRUCTION")
    # Even-order tangency with polynomial (t-1/2)^2, and two roots separated
    # by 2^-120: W=0 in both, so do not mistake zero events for frame failure.
    tangency = a("1/4", "-1", "1")
    need(not rational_polynomial_witness(tangency, a("0"))
         ["nonzero_wronskian_blocks_every_affine_phase"], "TANGENCY_CONTROL")
    gap = Fraction(1, 2**120)
    close = [Fraction(1, 4) + gap / 2, -1 - gap, Fraction(1)]
    need(not rational_polynomial_witness(close, a("0"))
         ["nonzero_wronskian_blocks_every_affine_phase"], "CLOSE_ROOT_CONTROL")
    need(gap > 0 and close[0] ==
         Fraction(1, 2) * (Fraction(1, 2) + gap),
         "CLOSE_ROOT_EXACTNESS")
    reject(lambda: rational_polynomial_witness(a("0"), a("0")))
    reject(lambda: rational_polynomial_witness([True], a("1")))
    reject(lambda: rational_polynomial_witness(a("1"), a("1") * 10))
    mutated = copy.deepcopy(corpus)
    x = next(c for c in mutated["cases"] if c["id"] == NAMES[0])
    x["spec"]["phase_turn_rate"] = "1/4"
    reject(lambda: audit(mutated, register, prior))
    mutated = copy.deepcopy(corpus)
    x = next(c for c in mutated["cases"] if c["id"] == NAMES[1])
    x["spec"]["sin_splines"]["1"]["controls"][0] = "-1/3"
    reject(lambda: audit(mutated, register, prior))
    mutated = copy.deepcopy(corpus)
    x = next(c for c in mutated["cases"] if c["id"] == NAMES[0])
    x["spec"]["cos_splines"]["1"]["knots"][2] = "1/2"
    reject(lambda: audit(mutated, register, prior))
    mutated = copy.deepcopy(corpus)
    next(c for c in mutated["cases"] if c["id"] == NAMES[0])[
        "expected"]["v54_disposition"] = "CERTIFIED"
    reject(lambda: audit(mutated, register, prior))
    mutated = copy.deepcopy(register)
    next(p for p in mutated["source_cases"] if p["case_id"] == NAMES[1])[
        "source_sha256"] = "0" * 64
    reject(lambda: audit(corpus, mutated, prior))
    mutated = copy.deepcopy(expected)
    mutated["matched_census"]["historical_missing_ordered"]["after"] = 29
    need(mutated != expected, "FALSE_DELTA_GUARD")
    reject(lambda: need(mutated == expected, "FALSE_HISTORICAL_CLOSURE"))
    mutated = copy.deepcopy(expected)
    mutated["cases"][0]["W_coefficients_ascending"] = ["1"]
    reject(lambda: need(mutated == expected, "FAKE_SIGNED_WRONSKIAN"))
    reject(lambda: duplicate_rejecting_json(b'{"a":1,"a":2}'))
    reject(lambda: duplicate_rejecting_json(b'{"a":NaN}'))
    print("PASS: two actual frozen original Wronskians, complete pinned "
          "121/50 census; positive/negative/tangency/2^-120 controls "
          "and 11+ adversarial refusals")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    prior = load_prior()
    corpus, register = pinned_inputs(prior)
    result = audit(corpus, register, prior)
    need(read_receipt() == result, "RECOMPUTED_RECEIPT_MISMATCH")
    if args.self_test:
        self_test(prior, corpus, register, result)
    if args.json:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        print("PASS: original V9 W=-1, original V43 W=+1, "
              "q=t^2-t+5/4; no affine phase frame; "
              "121/20/30/50 unchanged; zero PB discharge")


if __name__ == "__main__":
    main()
