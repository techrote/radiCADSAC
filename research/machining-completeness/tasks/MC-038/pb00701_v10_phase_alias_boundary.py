#!/usr/bin/env python3
"""Exact original V10 source custody and phase-alias negative-C certificate.

The finite Python checks bind the frozen source and report. The real-variable
cotangent monotonicity proof is written in the paired RAG document, not
claimed machine-formalized here. No root decisions use floating-point scans.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "pb00701-finite-owner-corpus-v54.json"
V2 = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
RECEIPT = HERE / "pb00701-v10-phase-alias-boundary-20261105.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
CASE = "composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail0"
SOURCE_SHA = "57d3c14096ccedfb7faea5023f5a09bada2ca274748f2207c36d77bbc790927c"
ROW_SHA = "c5ba85453dc65e0d18675353986394ae5b34af6219a741ce14af0c332ffc47cd"
COMPANION_SHA = "21a0dde2ee6783f4465ab0c23dbef08fc400a4c8f2169cc5b851a3b0c3f5e23b"

class Refusal(ValueError):
    pass

def need(ok, why):
    if not ok:
        raise Refusal(why)

def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")

def sha256(value):
    return hashlib.sha256(encode(value)).hexdigest()

def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def read_pinned(path, digest):
    data = path.read_bytes()
    need(git_blob(data) == digest, "FROZEN_GIT_BLOB_DRIFT:" + path.name)
    return json.loads(data)

def expected_spec():
    return {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "source_parameter_id": "source-time-t",
        "parameter_lo": "0", "parameter_hi": "2",
        "phase_turn_offset": "-1/2", "phase_turn_rate": "2",
        "cos_splines": {
            "0": {"degree": 0, "knots": ["0", "1", "2"], "controls": ["0", "0"]},
            "1": {"degree": 0, "knots": ["0", "1", "2"], "controls": ["1", "1"]},
        },
        "sin_splines": {
            "1": {"degree": 1, "knots": ["0", "0", "1", "1", "2", "2"],
                  "controls": ["1/2", "-1/2", "-1/2", "-1/2"]},
        },
    }

def verify_case(row, evidence):
    need(row["id"] == CASE and row["expected"]["id"] == CASE, "CASE_ID")
    need(row["origin"] == "verify_pb00701_v10" and
         row["kind"] == "COMPOSITE_TAIL", "CASE_ORIGIN")
    spec = row["spec"]
    need(spec == expected_spec(), "SOURCE_GRAMMAR_OR_CONTROL_CHANGE")
    need(sha256(spec) == SOURCE_SHA, "SOURCE_CANONICAL_SHA")
    need(sha256(row) == ROW_SHA, "WHOLE_ROW_CANONICAL_SHA")
    expected_spans = [
        ["PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO", "CERTIFIED", None],
        ["PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF", "BLOCKED",
         "CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED"],
    ]
    need(row["expected"]["observed"] == {"status": "BLOCKED", "spans": expected_spans}
         and row["expected"]["v54_disposition"] == "BLOCKED", "ORIGINAL_FAILURE")
    need(evidence["case_id"] == CASE and evidence["source_sha256"] == SOURCE_SHA and
         evidence["original_row_sha256"] == ROW_SHA, "V2_SOURCE_CUSTODY")
    need(evidence["historical_v54_disposition"] == "BLOCKED" and
         evidence["historical_spans"] == expected_spans and
         evidence["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC" and
         evidence["historical_disposition_changed"] is False, "V2_STATUS_OR_PROOF")
    need(evidence["source_parameter_id"] == "source-time-t" and
         evidence["source_interval"] == ["0", "2"] and
         evidence["original_source_piece_edges"] == ["0", "1", "2"] and
         evidence["phase_turn_law"] == {"offset": "-1/2", "rate": "2"},
         "V2_ORIGINAL_PARAMETER_KNOT_PHASE")
    need(evidence["evidence"]["complete_original_source_zero_set"] is True,
         "V2_WITNESS_INCOMPLETE")
    # Independent exact original Bernstein reconstruction:
    # H0=0,H1=1 on both open pieces; S1=(1/2-t) on [0,1],
    # S1=-1/2 on [1,2]; the true source knot is continuous.
    sine = spec["sin_splines"]["1"]
    controls = [Q(token) for token in sine["controls"]]
    need(controls == [Q(1, 2), Q(-1, 2), Q(-1, 2), Q(-1, 2)],
         "ORIGINAL_BERNSTEIN_CONTROLS")
    a, b = controls[0], controls[1] - controls[0]
    need((a, b) == (Q(1, 2), -Q(1)), "ORIGINAL_FIRST_PIECE_AFFINE")
    need(a + b == controls[2], "TRUE_KNOT_POINT_CONTINUITY")
    need(controls[2] == controls[3] == Q(-1, 2), "TAIL_AFFINE")
    phase0 = Q(spec["phase_turn_offset"])
    rate = Q(spec["phase_turn_rate"])
    shift = Q(1, 2)
    need(rate * shift == 1, "PHASE_ALIAS_IS_ONE_FULL_TURN")
    # From cos(4*pi*t-pi)=-cos(4*pi*t), sin(4*pi*t-pi)=-sin(4*pi*t):
    # F_first= -cos(4*pi*t)+(t-1/2)*sin(4*pi*t).
    # At two source times t and t+1/2 (within first span), the cosine
    # coefficient is unchanged and the sine coefficient differs by +1/2.
    need(-b * shift == shift, "EXACT_NONZERO_ALIAS_AMPLITUDE_DIFFERENCE")
    # F(0)=F(1)=F(2)=-1; t=1 is a true, nonroot source knot.
    return {"first_sine_polynomial": ["-1/2", "1"],
            "second_sine_polynomial": ["1/2"],
            "phase_offset": str(phase0), "phase_rate": str(rate),
            "alias_shift": str(shift),
            "alias_physical_sine_coefficient_delta": str(-b * shift)}

def source_inventory(corpus, register):
    cases = corpus["cases"]
    need(len(cases) == 121 and len({x["id"] for x in cases}) == 121,
         "ORIGINAL_DENOMINATOR")
    hist = {}
    for row in cases:
        status = row["expected"]["v54_disposition"]
        hist[status] = hist.get(status, 0) + 1
    need(hist.get("BLOCKED") == 20 and
         hist.get("BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE") == 30,
         "HISTORICAL_CLASSIFICATION")
    blocked_ids = {r["id"] for r in cases if r["expected"]["v54_disposition"].startswith("BLOCKED")}
    need(len(blocked_ids) == 50, "HISTORICAL_BLOCKER_SET")
    rows = {r["id"]: r for r in cases}
    witnesses = register["source_cases"]
    need(len(witnesses) == 50 and len({x["case_id"] for x in witnesses}) == 50 and
         {x["case_id"] for x in witnesses} == blocked_ids, "EVIDENCE_POPULATION")
    for ev in witnesses:
        row = rows[ev["case_id"]]
        need(ev["source_sha256"] == sha256(row["spec"]) and
             ev["original_row_sha256"] == sha256(row) and
             ev["historical_v54_disposition"] == row["expected"]["v54_disposition"]
             and ev["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC",
             "EVIDENCE_IDENTITY_OR_CLASS")
    original = rows[CASE]
    ev = next(x for x in witnesses if x["case_id"] == CASE)
    ident = verify_case(original, ev)
    companion = rows[CASE.replace("tail0", "tail100")]
    need(sha256(companion["spec"]) == COMPANION_SHA and
         companion["spec"] != original["spec"], "COMPANION_DISTINCT")
    return ident

def make_report(corpus, register):
    ident = source_inventory(corpus, register)
    prefix_brackets = [[str(Q(k, 4)), str(Q(k+1, 4))] for k in range(4)]
    tail_brackets = [[str(Q(4+k, 4)), str(Q(5+k, 4))] for k in range(4)]
    return {
        "schema": "radicadsac-mc038-v10-phase-alias-negative/1.0",
        "date": "2026-11-05", "task": "MC-038", "obligation": "PB-007-01",
        "claim_kind": "C_BOUNDED_PHASE_MOD_ONE_EVENT_KEY_FALSIFIED",
        "evidence_class": "DETERMINISTIC_MODEL",
        "historical_case": CASE, "source_sha256": SOURCE_SHA,
        "original_row_sha256": ROW_SHA,
        "frozen_git_blobs": {"v54": CORPUS_BLOB, "v2": V2_BLOB},
        "original_interval": ["0", "2"], "true_knot": "1",
        "original_source_identity": ident,
        "phase_law_turns": {"offset": "-1/2", "rate": "2"},
        "proven_first_piece": {
            "formula": "-cos(4*pi*t)+(t-1/2)*sin(4*pi*t)",
            "root_brackets_strict": prefix_brackets,
            "one_root_per_bracket": True, "root_order_each": 1,
            "derivative_orientations": ["POSITIVE", "NEGATIVE", "POSITIVE", "NEGATIVE"],
            "reason": "g=t-1/2-cot(4*pi*t) strictly increases from -infinity to +infinity in every bracket; g'=1+4*pi*csc(4*pi*t)^2>0",
        },
        "proven_second_piece": {
            "formula": "-cos(4*pi*t)+(1/2)*sin(4*pi*t)",
            "root_brackets_strict": tail_brackets,
            "one_root_per_bracket": True, "root_order_each": 1,
            "derivative_orientations": ["POSITIVE", "NEGATIVE", "POSITIVE", "NEGATIVE"],
            "reason": "cot(4*pi*t)=1/2 strictly decreases from +infinity to -infinity once per pi-phase interval",
        },
        "closed_original_zero_set": {"type": "FINITE_IMPLICIT",
                                     "number_of_distinct_simple_roots": 8,
                                     "true_knot_is_root": False,
                                     "physical_cell_signs": ["NEGATIVE","POSITIVE","NEGATIVE","POSITIVE","NEGATIVE","POSITIVE","NEGATIVE","POSITIVE","NEGATIVE"]},
        "alias_counterexample": {
            "root_locator": "r0 unique in (0,1/4) with cot(4*pi*r0)=r0-1/2",
            "alias_locator": "r0+1/2 in (1/2,3/4)",
            "equal_phase_mod_one": True,
            "delta_phase_turns": "1",
            "physical_F_root": "0",
            "physical_F_alias": "(1/2)*sin(4*pi*r0)>0",
            "phase_mod_one_event_dedup": "REFUSED_AS_UNSOUND",
        },
        "before": {"frozen_original_sources":121,"historical_route_refusals":20,
                   "historical_missing_ordered_premises":30,"complete_source_specific_witnesses":50},
        "after": {"frozen_original_sources":121,"historical_route_refusals":20,
                  "historical_missing_ordered_premises":30,"complete_source_specific_witnesses":50},
        "delta": {"frozen_original_sources":0,"historical_route_refusals":0,
                  "historical_missing_ordered_premises":0,"complete_source_specific_witnesses":0},
        "new_historical_resolutions": [], "required_PB_discharged": False,
        "MC_B_established": False, "MC_1_established": False,
        "native_geometry_or_engineering_STEP": False, "production_authorized": False,
        "supported_operations_unchanged": 26,
        "limitations": "The checker binds rational source/census and symbolic coefficient identities; cotangent monotonicity and exact root existence/order are mathematical proof steps documented in RAG, not machine-formalized."
    }

def check_receipt(actual, expected):
    need(encode(actual) == encode(expected), "MACHINE_RECEIPT_FORGERY")

def self_test(corpus, register, expected):
    row = next(r for r in corpus["cases"] if r["id"] == CASE)
    ev = next(x for x in register["source_cases"] if x["case_id"] == CASE)
    count = 0
    mutations = [
        ("source-parameter", lambda x: x["spec"].update(source_parameter_id="phase-time")),
        ("phase-rate", lambda x: x["spec"].update(phase_turn_rate="1")),
        ("phase-offset", lambda x: x["spec"].update(phase_turn_offset="0")),
        ("interval", lambda x: x["spec"].update(parameter_hi="3")),
        ("true-knot", lambda x: x["spec"]["sin_splines"]["1"]["knots"].__setitem__(2, "1/2")),
        ("first-amplitude", lambda x: x["spec"]["sin_splines"]["1"]["controls"].__setitem__(0, "0")),
        ("tail-amplitude", lambda x: x["spec"]["sin_splines"]["1"]["controls"].__setitem__(3, "0")),
        ("cos-channel", lambda x: x["spec"]["cos_splines"]["1"]["controls"].__setitem__(0, "0")),
        ("identity-zero", lambda x: x["spec"]["cos_splines"]["1"]["controls"].__setitem__(1, "0")),
        ("extra-harmonic", lambda x: x["spec"]["cos_splines"].update({"2":{"degree":0,"knots":["0","1","2"],"controls":["1","1"]}})),
        ("historical-refusal", lambda x: x["expected"].update(v54_disposition="CERTIFIED")),
        ("different-source-id", lambda x: x.update(id=CASE.replace("tail0","tail100"))),
    ]
    for name, change in mutations:
        alt = copy.deepcopy(row)
        change(alt)
        try:
            verify_case(alt, ev)
        except Refusal:
            count += 1
        else:
            raise AssertionError("failed mutation refusal: " + name)
    # This original cannot claim a tangential, identity-zero, or 2^-100-close
    # synthetic variant was proved: those all change the exact source specification.
    for name, spec_change in [
        ("tangent", lambda x: x["sin_splines"]["1"]["controls"].__setitem__(0,"1/4")),
        ("continuum", lambda x: x["cos_splines"]["1"]["controls"].__setitem__(0,"0")),
        ("close-root", lambda x: x["sin_splines"]["1"]["controls"].__setitem__(1,str(Q(-1,2)+Q(1,2**100)))),
    ]:
        alt = copy.deepcopy(row)
        spec_change(alt["spec"])
        try:
            verify_case(alt, ev)
        except Refusal:
            count += 1
        else:
            raise AssertionError("wrongly admitted " + name)
    for field, bad in [("new_historical_resolutions",[CASE]),
                       ("required_PB_discharged",True),
                       ("MC_B_established",True),
                       ("supported_operations_unchanged",25),
                       ("alias_counterexample",{"equal_phase_mod_one":True}),
                       ("delta",{"historical_route_refusals":-1})]:
        alt = copy.deepcopy(expected); alt[field] = bad
        try:
            check_receipt(alt, expected)
        except Refusal:
            count += 1
        else:
            raise AssertionError("accepted forged receipt " + field)
    return count

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--contract", action="store_true")
    p.add_argument("--self-test", action="store_true")
    opts = p.parse_args()
    c = read_pinned(CORPUS, CORPUS_BLOB)
    v = read_pinned(V2, V2_BLOB)
    expected = make_report(c, v)
    saved = json.loads(RECEIPT.read_bytes())
    check_receipt(saved, expected)
    if opts.self_test:
        count = self_test(c, v, expected)
        assert count == 21, count
        print(f"21/21 source/receipt adversarial mutations refused")
    print(f"ORIGINAL_SOURCE_PROVENANCE_VALID; historical=121/20/30/50; new_historical_closure=0; exact C phase-alias proof RAG, root_claims=8 simple")
if __name__ == "__main__":
    main()
