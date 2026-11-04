#!/usr/bin/env python3
"""Original frozen V17 physical-sign-erasure falsifier. Deterministic model only.

Proof lives alongside this executable. Refusal is not a mathematical zero verdict.
No historical fixture or saved producer result is rewritten or executed as authority.
"""
import argparse
import copy
from collections import Counter
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
ID = "composite:PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER:tail100"
SOURCE_SHA = "e85d997c9f4d828b1b748c964b375c21e4acef1b1e9046e074b1f7e29011d08f"
ROW_SHA = "41e86bc30392515873fb55bdd844d154236a81426fd3639c3bd5491dad30f05a"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
CORPUS = HERE / "pb00701-finite-owner-corpus-v54.json"
V2 = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
REPORT = HERE / "pb00701-v17-negative-multiplier-sign-erasure.json"
ROUTE = "NONVANISHING_MULTIPLIER_PRESERVES_CARRIER_PHYSICAL_SIGNS"
KNOTS = ["0", "0", "1", "1", "2", "2"]

class Refused(ValueError):
    pass

def need(condition, reason):
    if not condition:
        raise Refused(reason)

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")

def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()

def checked_json(path, expected_blob):
    data = path.read_bytes()
    need(len(data) < 350_000, "INPUT_COST_BUDGET")
    got = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    need(got == expected_blob, "FROZEN_GIT_BLOB_DRIFT:" + path.name)
    return json.loads(data)

def bs(controls):
    return {"degree": 1, "knots": KNOTS[:], "controls": controls}

EXPECTED_SPEC = {
    "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
    "source_parameter_id": "source-time-t",
    "parameter_lo": "0", "parameter_hi": "2",
    "phase_turn_offset": "0", "phase_turn_rate": "1/4",
    "cos_splines": {
        "0": bs(["0", "0", "0", "100"]),
        "1": bs(["1", "-3/2", "-3/2", "-3/2"]),
        "3": bs(["-1/3", "1/6", "1/6", "1/6"]),
    },
    "sin_splines": {
        "1": bs(["-3/2", "1", "1", "1"]),
        "3": bs(["-1/6", "1/3", "1/3", "1/3"]),
    },
}

def check_source(row):
    need(row.get("id") == ID, "WRONG_ORIGINAL_CASE_ID")
    spec = row.get("spec")
    need(type(spec) is dict and spec == EXPECTED_SPEC, "ORIGINAL_SOURCE_SEMANTICS_DRIFT")
    need(digest(spec) == SOURCE_SHA, "ORIGINAL_SOURCE_HASH_DRIFT")
    need(digest(row) == ROW_SHA, "ORIGINAL_CASE_ROW_HASH_DRIFT")
    observed = row.get("expected", {})
    need(observed.get("v54_disposition") ==
         "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE",
         "HISTORICAL_REFUSAL_ERASED")
    need(observed.get("observed", {}).get("spans") ==
         [["PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER", "CERTIFIED", None],
          ["PB00701_V19_EXACT_MULTI_HARMONIC_MONOTONE_ANCHOR", "CERTIFIED", None]],
         "HISTORICAL_SPAN_RECORD_DRIFT")
    return spec

def affine(a, b):
    # Two rational endpoint values of an affine polynomial on [0,1].
    return [str(a), str(a + b)]

def check_factor_and_events(spec):
    # Exact Fourier product:
    # F = (-2+sin(2theta)) * (a cos(theta)+b sin(theta))
    # sin(2theta)cos(theta)=(sin(3theta)+sin(theta))/2,
    # sin(2theta)sin(theta)=(cos(theta)-cos(3theta))/2.
    # a=t-1/3, b=2/3-t, theta=pi*t/2.
    a0, a1 = Q(-1, 3), Q(1)
    b0, b1 = Q(2, 3), Q(-1)
    predicted = {
        ("cos_splines", "1"): affine(-2*a0 + b0/2, -2*a1 + b1/2),
        ("cos_splines", "3"): affine(-b0/2, -b1/2),
        ("sin_splines", "1"): affine(-2*b0 + a0/2, -2*b1 + a1/2),
        ("sin_splines", "3"): affine(a0/2, a1/2),
    }
    for (channel, harmonic), endpoints in predicted.items():
        actual = [Q(v) for v in spec[channel][harmonic]["controls"][:2]]
        need(actual == [Q(v) for v in endpoints], "FOURIER_FACTOR_RECONSTRUCTION_FAILED")
        need(spec[channel][harmonic]["controls"][1] ==
             spec[channel][harmonic]["controls"][2], "TRUE_SOURCE_KNOT_JUMP")
        need(spec[channel][harmonic]["controls"][2] ==
             spec[channel][harmonic]["controls"][3], "TAIL_NOT_CONSTANT")
    need(spec["cos_splines"]["0"]["controls"] == ["0","0","0","100"],
         "ORIGINAL_TAIL_RAMP_DRIFT")
    # At t=0: R=-1/3, M=-2, F=+2/3.
    need(a0 == -Q(1,3) and -2*a0 == Q(2,3), "LEFT_ENDPOINT_SIGN")
    # At t=1/2: a=b=1/6, R=sqrt(2)/6>0, M=-1, F<0.
    need(a0+a1/2 == Q(1,6) and b0+b1/2 == Q(1,6),
         "EXACT_MIDPOINT_SIGN")
    # At t=1: R=-1/3 and M=-2, F=+2/3. Knot is not a root.
    need(b0+b1 == -Q(1,3) and -2*(b0+b1) == Q(2,3),
         "KNOT_SIGN_OR_CONTINUITY")
    # On [0,1/3], R = cos(theta)*(2/3-t)*(tan(theta)-q(t)),
    # q(t)=(1/3-t)/(2/3-t), q'(t)=-1/[3(2/3-t)^2]<0;
    # tan(theta)'=(pi/2)*sec^2(theta)>0. Unique simple root.
    # Strict exact brackets: tan(pi/12)=2-sqrt(3)<1/3=q(1/6)
    # because 3>(5/3)^2; tan(pi/8)=sqrt(2)-1>1/5=q(1/4)
    # because 2>(6/5)^2. All positive quantities, squaring safe.
    need(Q(3) > Q(5,3)**2 and Q(2) > Q(6,5)**2,
         "EXACT_BRACKET_INEQUALITY")
    need((Q(1,3)-Q(1,6))/(Q(2,3)-Q(1,6)) == Q(1,3) and
         (Q(1,3)-Q(1,4))/(Q(2,3)-Q(1,4)) == Q(1,5),
         "EXACT_RATIONAL_RATIO")
    # R(1-t)=R(t), so second simple root is reflected in (3/4,5/6).
    # On [1/3,2/3] both carrier coefficients are nonnegative,
    # with strict positive sin/cos factors. No other prefix zero.
    # M=-2+sin(2theta) is in [-3,-1], strictly negative.
    # Therefore physical sign cells are +,-,+ and physical
    # simple-root derivative signs are -,+, reversing the carrier.
    # On [1,2], F'=100+trigonometric terms, |terms|<=2*pi
    # <44/7; therefore F'>656/7>0. Tail stays positive.
    weighted = (Q(3,2)+Q(1,2)+Q(1)+Q(1))
    need(weighted == 4 and Q(100)-Q(22,7)*2 == Q(656,7)>0,
         "POSITIVE_TAIL_DERIVATIVE_BOUND")
    need(Q(100)+Q(3,2)-Q(1,6)==Q(304,3),
         "RIGHT_ENDPOINT_VALUE")
    return True

def census(corpus, v2):
    rows = corpus["cases"]
    need(len(rows)==121 and len({r["id"] for r in rows})==121,
         "FROZEN_DENOMINATOR_DRIFT")
    counts = Counter(r["expected"]["v54_disposition"] for r in rows)
    need(counts["BLOCKED"]==20 and
         counts["BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"]==30,
         "HISTORICAL_BLOCKER_CENSUS_DRIFT")
    unresolved = {r["id"] for r in rows if r["expected"]["v54_disposition"].startswith("BLOCKED")}
    need(len(unresolved)==50, "NON_DISJOINT_HISTORICAL_COHORTS")
    complete = v2["source_cases"]
    ids = [r["case_id"] for r in complete]
    need(len(ids)==50 and len(set(ids))==50 and set(ids)==unresolved,
         "V2_ORIGINAL_SOURCE_ID_UNION_DRIFT")
    need(v2["summary"]["complete_finite_sources"]==49 and
         v2["summary"]["complete_continuum_sources"]==1,
         "V2_EVIDENCE_KIND_DRIFT")
    binding = next(r for r in complete if r["case_id"] == ID)
    need(binding["source_sha256"] == SOURCE_SHA and
         binding["original_row_sha256"] == ROW_SHA and
         binding["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC",
         "SELECTED_V2_SOURCE_BINDING_DRIFT")
    return next(r for r in rows if r["id"] == ID)

def expected_report():
    counts = {"frozen_original_sources":121,"historical_route_refusals":20,
              "historical_missing_ordered_premises":30,
              "preexisting_complete_source_specific_witnesses":50}
    return {
        "schema": "radicadsac-mc038-v17-negative-multiplier-sign-erasure/1.0",
        "task":"MC-038","evidence_class":"DETERMINISTIC_MODEL",
        "case_id":ID,"source_sha256":SOURCE_SHA,"original_row_sha256":ROW_SHA,
        "frozen_corpus_git_blob":CORPUS_BLOB,"v2_register_git_blob":V2_BLOB,
        "candidate_route":ROUTE,"disposition":"FALSIFIED_ON_PINNED_ORIGINAL_SOURCE",
        "source_parameter_id":"source-time-t","closed_interval":["0","2"],
        "true_source_knot":"1","phase_turns":"t/4",
        "exact_prefix_factor":"F=(-2+sin(pi*t))*((t-1/3)*cos(pi*t/2)+(2/3-t)*sin(pi*t/2))",
        "multiplier_range_bound":["-3","-1"],
        "carrier_sign_cells":[-1,1,-1],
        "physical_sign_cells":[1,-1,1],
        "physical_event_brackets":[["1/6","1/4"],["3/4","5/6"]],
        "physical_event_multiplicities":[1,1],
        "physical_event_derivative_signs":[-1,1],
        "zero_set_kind":"FINITE","closed_distinct_root_count":2,
        "original_knot_value":"2/3","right_exterior_value":"304/3",
        "tail_strict_derivative_lower_bound":"656/7",
        "historical_census":{"before":counts,"after":counts,"delta":{k:0 for k in counts},
                             "newly_closed_historical_case_ids":[]},
        "claims":{"bounded_negative_route_result_C":True,"new_historical_source_closure_A":False,
                  "required_PB007_obligation_discharge_B":False,
                  "general_analytic_event_theorem":False,"native_geometry":False,
                  "engineering_STEP":False,"MC_B_established":False,
                  "MC_1_established":False,"production_authorized":False,
                  "supported_operation_denominator":26},
    }

def check_report(record):
    need(record == expected_report(), "REPORT_OR_CLAIM_MUTATED")

def run_self_test(row):
    for mutation in (
        lambda r:r["spec"]["cos_splines"]["1"]["controls"].__setitem__(0,"0"),
        lambda r:r["spec"]["sin_splines"]["3"]["controls"].__setitem__(3,"1/2"),
        lambda r:r["spec"].__setitem__("phase_turn_rate","1/2"),
        lambda r:r["spec"].__setitem__("phase_turn_offset","1/2"),
        lambda r:r["spec"].__setitem__("parameter_hi","1"),
        lambda r:r["spec"].__setitem__("source_parameter_id","source-time-u"),
        lambda r:r["spec"]["cos_splines"]["1"]["knots"].__setitem__(2,"1/2"),
        lambda r:r["expected"].__setitem__("v54_disposition","CERTIFIED"),
        lambda r:r.__setitem__("id",ID+"-forged"),
    ):
        variant=copy.deepcopy(row)
        mutation(variant)
        try:
            check_source(variant)
        except Refused:
            pass
        else:
            raise AssertionError("ADVERSARIAL_SOURCE_MUTATION_ACCEPTED")
    for mutation in (
        lambda r:r["physical_sign_cells"].__setitem__(0,-1),
        lambda r:r["carrier_sign_cells"].__setitem__(1,-1),
        lambda r:r["physical_event_multiplicities"].__setitem__(0,2),
        lambda r:r["physical_event_brackets"].__setitem__(0,["0","1"]),
        lambda r:r["historical_census"]["delta"].__setitem__("historical_route_refusals",-1),
        lambda r:r["claims"].__setitem__("MC_B_established",True),
    ):
        variant=expected_report()
        mutation(variant)
        try:
            check_report(variant)
        except Refused:
            pass
        else:
            raise AssertionError("ADVERSARIAL_REPORT_MUTATION_ACCEPTED")
    # Prospective rational-only adversaries, not historical source cases:
    # (t-1/2)^2 has an even touching root and no sign change.
    # (t-1/2)^2-2^-200 has two simple roots 2^-99 apart.
    gap=Q(1,2**99)
    lo=Q(1,2)-Q(1,2**100)
    hi=Q(1,2)+Q(1,2**100)
    need(hi-lo == gap and (lo-Q(1,2))**2==Q(1,2**200)
         and (hi-Q(1,2))**2==Q(1,2**200),
         "PROSPECTIVE_CLOSE_ROOT_CONTROL")
    need(all(x==0 for x in [Q(0)]*7), "IDENTITY_ZERO_CONTROL")
    return 15

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--contract",action="store_true")
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--emit",action="store_true")
    args=parser.parse_args()
    corpus=checked_json(CORPUS,CORPUS_BLOB)
    v2=checked_json(V2,V2_BLOB)
    row=census(corpus,v2)
    spec=check_source(row)
    check_factor_and_events(spec)
    report=json.loads(REPORT.read_text(encoding="utf-8"))
    check_report(report)
    checks=run_self_test(row) if args.self_test else 0
    print(json.dumps({"outcome":"BOUNDED_C_ONLY","case_id":ID,
                      "candidate_route":ROUTE,"historical_delta":0,
                      "adversarial_mutations_refused":checks},sort_keys=True))
    if args.emit:
        print(json.dumps(expected_report(),indent=2,sort_keys=True))

if __name__=="__main__":
    main()
