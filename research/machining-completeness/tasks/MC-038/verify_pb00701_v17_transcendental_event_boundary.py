#!/usr/bin/env python3
"""Source-bound V17 algebraic-coordinate-only event falsifier.

This checks the pinned original source and exact rational proof premises.
The Gelfond--Schneider theorem is cited in the RAG mathematical proof;
this script does NOT claim a machine formalization of that theorem.
"""
import argparse
import copy
from fractions import Fraction as Q
from math import isqrt
import json
from pathlib import Path

import verify_pb00701_v17_negative_multiplier_sign_erasure as v17

HERE = Path(__file__).resolve().parent
RECEIPT = HERE / "pb00701-v17-transcendental-event-boundary-20261105.json"
ROUTE = "ALGEBRAIC_COORDINATES_ONLY_FOR_ALL_RATIONAL_AFFINE_PHASE_PHYSICAL_EVENTS"

class Refused(ValueError):
    pass

def need(ok, why):
    if not ok:
        raise Refused(why)

def q1(t):
    return (Q(1, 3) - t) / (Q(2, 3) - t)

def q2(t):
    return (t - Q(1, 3)) / (t - Q(2, 3))

def rational_square(x):
    if x < 0:
        return False
    a, b = isqrt(x.numerator), isqrt(x.denominator)
    return a*a == x.numerator and b*b == x.denominator

def algebraic_integer_tangent_lemma():
    """Exact rational computation supporting the roots-of-unity proof.

    For rational t, z=exp(i*pi*t) is a root of unity.
    If u=tan(pi*t/2) is rational and finite, then
       m=z+z^-1=2*(1-u^2)/(1+u^2)
    is both rational and an algebraic integer: m in {-2,-1,0,1,2}.
    Solving (m+2)*u^2=2-m and requiring a rational square gives
    exactly u^2 in {0,1}, not any candidate in (0,1) or (1,infinity).
    The root-of-unity/algebraic-integer implications are mathematical
    premises, not certified by this finite enumeration.
    """
    possibilities = []
    for m in range(-2, 3):
        if m == -2:
            # The equation would read 0=4, so no finite tangent.
            need(Q(2) - m == 4, "BAD_MINUS_TWO_LIMIT")
            continue
        square = Q(2 - m, m + 2)
        if rational_square(square):
            possibilities.append((m, square))
    need(possibilities == [(0, Q(1)), (2, Q(0))],
         "RATIONAL_ROOT_OF_UNITY_TANGENT_LEMMA_FAILED")
    return possibilities

def exact_original_root_premises(spec):
    need(spec == v17.EXPECTED_SPEC, "SOURCE_NOT_THE_FROZEN_ORIGINAL")
    need(spec["source_parameter_id"] == "source-time-t" and
         spec["parameter_lo"] == "0" and spec["parameter_hi"] == "2" and
         spec["phase_turn_offset"] == "0" and
         spec["phase_turn_rate"] == "1/4", "SOURCE_TIME_OR_PHASE_DRIFT")
    need(spec["cos_splines"]["1"]["knots"] == v17.KNOTS,
         "ORIGINAL_TRUE_KNOT_DRIFT")
    # Source-bound carrier/tangent relation: R(t)=0 iff
    # tan(pi*t/2)=(1/3-t)/(2/3-t), away from t=2/3.
    # The prior V17 verifier independently checks exact original
    # Fourier/B-spline factorization, uniqueness, simplicity and
    # strict rational brackets by algebraic inequalities.
    need(q1(Q(1, 6)) == Q(1, 3) and
         q1(Q(1, 4)) == Q(1, 5), "FIRST_ORIGINAL_TANGENT_RATIO_DRIFT")
    need(q2(Q(3, 4)) == 5 and
         q2(Q(5, 6)) == 3, "SECOND_ORIGINAL_TANGENT_RATIO_DRIFT")
    # Derivatives of q1, q2 have negative numerator -1/3.
    need((-1)*Q(2, 3) + Q(1, 3) == -Q(1, 3),
         "RATIO_MONOTONICITY_LOST")
    need(-Q(2, 3) + Q(1, 3) == -Q(1, 3),
         "REFLECTED_RATIO_MONOTONICITY_LOST")
    # Exact inequalities for first bracket root sign, no float scan.
    need(Q(3) > Q(5, 3)**2 and
         Q(2) > Q(6, 5)**2, "EXACT_ROOT_BRACKETS_LOST")
    brackets = [(Q(1, 6), Q(1, 4)), (Q(3, 4), Q(5, 6))]
    need(brackets[1] == (1-brackets[0][1], 1-brackets[0][0]),
         "SOURCE_REFLECTION_LOST")
    # On every point in either open bracket, the rational carrier
    # ratio lies strictly in (1/5,1/3) or (3,5), respectively.
    # Those sets are disjoint from {-1,0,+1}; thus a rational root
    # coordinate contradicts the exact root-of-unity lemma above.
    need(0 < q1(Q(1, 4)) < q1(Q(1, 6)) < 1 and
         1 < q2(Q(5, 6)) < q2(Q(3, 4)),
         "RATIONAL_TANGENT_EXCLUSION_LOST")
    # If t is algebraic irrational instead, the rational function q(t)
    # is algebraic, making exp(i*pi*t)=(1+i*q)/(1-i*q) algebraic.
    # Gelfond--Schneider says every branch (-1)^t is transcendental:
    # a contradiction. See the full RAG proof for branch and domain.
    return brackets

def expected_receipt():
    count={"original_sources":121,"route_refusals":20,
           "missing_ordered_premises":30,
           "complete_source_specific_witnesses":50}
    return {
      "schema":"radicadsac-mc038-v17-transcendental-event-boundary/1.0",
      "task":"MC-038","obligation":"PB-007-01",
      "downstream_proof_obligations":["PO-04","PO-05","PO-08"],
      "evidence_class":"DETERMINISTIC_MODEL",
      "frozen_original_id":v17.ID,
      "original_source_sha256":v17.SOURCE_SHA,
      "original_row_sha256":v17.ROW_SHA,
      "frozen_v54_git_blob":v17.CORPUS_BLOB,
      "complete_v2_git_blob":v17.V2_BLOB,
      "source_parameter_id":"source-time-t",
      "source_interval":["0","2"],"true_knot":"1",
      "phase_turns":"t/4",
      "original_first_span_carrier":
          "(t-1/3)*cos(pi*t/2)+(2/3-t)*sin(pi*t/2)",
      "nonzero_signed_multiplier":"-2+sin(pi*t)",
      "verified_simple_root_brackets":[["1/6","1/4"],["3/4","5/6"]],
      "root_count":2,"multiplicities":[1,1],
      "physical_sign_cells":[1,-1,1],
      "root_coordinate_class":["TRANSCENDENTAL","TRANSCENDENTAL"],
      "proposed_route":ROUTE,
      "disposition":"FALSIFIED_ON_FROZEN_ORIGINAL_SOURCE",
      "required_mathematical_dependencies":[
          "roots_of_unity_are_algebraic_integers",
          "rational_algebraic_integers_are_integers",
          "Gelfond_Schneider_theorem_for_minus_one_to_algebraic_irrational"
      ],
      "proof_scope":"THE_CLASS_OF_EXACT_ALGEBRAIC_COORDINATES_NOT_IMPLICIT_ROOT_BRACKETS",
      "machine_formalization_of_Gelfond_Schneider":False,
      "historical_census":{"before":count,"after":count,
          "delta":{k:0 for k in count},"newly_closed_historical_ids":[]},
      "claims":{
          "bounded_C":True,
          "new_frozen_source_closure_A":False,
          "full_required_PB_discharge_B":False,
          "general_root_isolation_impossible":False,
          "implicit_transcendental_root_brackets_invalid":False,
          "native_geometry":False,"independent_oracle":False,
          "engineering_STEP":False,"MC_B_established":False,
          "MC_1_established":False,"production_authorized":False,
          "supported_operations":26
      }
    }

def check_receipt(record):
    """Fail closed on the real machine receipt, including claim and census drift."""
    need(record == expected_receipt(), "MACHINE_EVIDENCE_OR_NONPROMOTION_DRIFT")

def adversaries(row):
    inherited = v17.run_self_test(row)
    mutations=[
       lambda s:s["cos_splines"]["3"]["controls"].__setitem__(0, "0"),
       lambda s:s["sin_splines"]["1"]["controls"].__setitem__(1, "2"),
       lambda s:s.__setitem__("phase_turn_rate","1/8"),
       lambda s:s.__setitem__("parameter_lo","1/10"),
       lambda s:s["cos_splines"]["0"]["knots"].__setitem__(2, "3/4")
    ]
    for change in mutations:
        tamper=copy.deepcopy(row)
        change(tamper["spec"])
        try:
            v17.check_source(tamper)
        except v17.Refused:
            continue
        raise AssertionError("SOURCE_MUTATION_ACCEPTED")
    for edit in (
        lambda d:d.__setitem__("root_coordinate_class",["ALGEBRAIC","ALGEBRAIC"]),
        lambda d:d.__setitem__("machine_formalization_of_Gelfond_Schneider",True),
        lambda d:d["claims"].__setitem__("MC_B_established",True),
        lambda d:d["historical_census"]["delta"].__setitem__("route_refusals",-1),
        lambda d:d.__setitem__("verified_simple_root_brackets",[["0","1"],["3/4","5/6"]]),
    ):
        forged=expected_receipt()
        edit(forged)
        # Exercise the SAME production receipt validation predicate used by
        # main(), not merely inequality between a forged and expected fixture.
        try:
            check_receipt(forged)
        except Refused as exc:
            need(str(exc) == "MACHINE_EVIDENCE_OR_NONPROMOTION_DRIFT",
                 "UNEXPECTED_RECEIPT_REFUSAL")
        else:
            raise AssertionError("ADVERSARIAL_RECEIPT_MUTATION_ACCEPTED")
    # Prospective exact controls, nonclaims for the general grammar.
    half=Q(1,2)
    f=lambda t:(t-half)**2
    need(f(half)==0 and f(0)==Q(1,4) and f(1)==Q(1,4),
         "PROSPECTIVE_TANGENCY_FAILED")
    eps=Q(1,2**100)
    g=lambda t:(t-half)**2-eps**2
    need(g(half-eps)==0 and g(half+eps)==0 and
         g(half)<0 and 2*eps==Q(1,2**99),
         "PROSPECTIVE_CLOSE_ROOT_FAILED")
    # Formal trig identity sin(2x)cos(x)=(sin(3x)+sin(x))/2;
    # integer exponent convolution supplies an identity-zero control.
    conv={}
    for e1,c1 in ((2,1),(-2,-1)):
        for e2,c2 in ((1,1),(-1,1)):
            conv[e1+e2]=conv.get(e1+e2,0)+c1*c2
    need(conv=={3:1,1:1,-1:-1,-3:-1},
         "PROSPECTIVE_IDENTITY_ZERO_FAILED")
    return {"inherited_mutation_refusals":inherited,
            "new_source_mutations_refused":len(mutations),
            "new_claim_mutations_refused":5,
            "prospective_nonclaim_controls":3}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--contract",action="store_true")
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    corpus=v17.checked_json(v17.CORPUS,v17.CORPUS_BLOB)
    v2=v17.checked_json(v17.V2,v17.V2_BLOB)
    row=v17.census(corpus,v2)
    spec=v17.check_source(row)
    v17.check_factor_and_events(spec)
    exact_original_root_premises(spec)
    algebraic_integer_tangent_lemma()
    check_receipt(json.loads(RECEIPT.read_text(encoding="utf-8")))
    tests=adversaries(row) if args.self_test else {}
    print(json.dumps({"outcome":"BOUNDED_C_TRANSCENDENTAL_ORIGINAL_ROOTS",
                      "original_case_id":v17.ID,
                      "root_count":2,"newly_closed_historical_ids":[],
                      "historical_delta":0,
                      "gelfond_schneider_machine_formalized":False,
                      "checks":tests},sort_keys=True))

if __name__=="__main__":
    main()
