#!/usr/bin/env python3
"""Exact original-source challenge: signed roots evade a square-phase lattice.

Reuse merged V17 full-source proof for authenticated mathematical premises;
add candidate-exhaustiveness falsification, not a new whole-source oracle.
"""
import argparse
import copy
from fractions import Fraction as Q
import json
from pathlib import Path

import verify_pb00701_v17_negative_multiplier_sign_erasure as v17

HERE=Path(__file__).resolve().parent
RECEIPT=HERE/"pb00701-v17-signed-nonlattice-20261105.json"
ROUTE="GENERALIZED_SQUARE_PHASE_LATTICE_ENUMERATES_SIGNED_MULTI_HARMONIC_EVENTS"

class Refused(ValueError):
    pass

def need(condition,reason):
    if not condition:
        raise Refused(reason)

def candidate_set(spec):
    """Naive candidate-only transfer: affine carrier factors + phase grid."""
    need(spec==v17.EXPECTED_SPEC,"SOURCE_NOT_AUTHENTICATED")
    offset=Q(spec["phase_turn_offset"])
    rate=Q(spec["phase_turn_rate"])
    need(rate==Q(1,4) and offset==0,"ORIGINAL_PHASE_CHANGED")
    candidates={Q(1,3),Q(2,3)}
    # Enlarge the naive half-integer-turn grid to quarter-turn nodes, making
    # the falsification stricter, never omitting a proposed phase candidate.
    for n in range(-8,9):
        t=(Q(n,4)-offset)/rate
        if 0<=t<=1:
            candidates.add(t)
    return sorted(candidates)

def falsify(candidate_points, brackets):
    need(candidate_points==[Q(0),Q(1,3),Q(2,3),Q(1)],
         "PROPOSED_CANDIDATE_INTERFACE_CHANGED")
    need(brackets==[(Q(1,6),Q(1,4)),(Q(3,4),Q(5,6))],
         "ORIGINAL_EXACT_ROOT_BRACKETS_CHANGED")
    for lo,hi in brackets:
        need(lo<hi and all(not lo<=v<=hi for v in candidate_points),
             "SIGNED_ORIGINAL_ROOT_INSIDE_CANDIDATE_SET")
    return True

def expected_receipt():
    population={"original_sources":121,"route_refusals":20,
                "missing_ordered_premises":30,
                "complete_source_witnesses":50}
    return {
       "schema":"radicadsac-mc038-v17-signed-nonlattice/1.0",
       "task":"MC-038","evidence_class":"DETERMINISTIC_MODEL",
       "original_case_id":v17.ID,"source_sha256":v17.SOURCE_SHA,
       "original_row_sha256":v17.ROW_SHA,
       "frozen_corpus_git_blob":v17.CORPUS_BLOB,
       "v2_register_git_blob":v17.V2_BLOB,
       "source_parameter_id":"source-time-t",
       "original_closed_interval":["0","2"],"true_original_knot":"1",
       "phase_turns":"t/4","candidate_route":ROUTE,
       "result":"BOUNDED_C_ROUTE_FALSIFIED",
       "candidate_coordinates":["0","1/3","2/3","1"],
       "actual_root_open_brackets":[["1/6","1/4"],["3/4","5/6"]],
       "actual_root_count":2,"actual_root_multiplicities":[1,1],
       "physical_sign_cells":[1,-1,1],
       "physical_crossing_orientations":[-1,1],
       "original_knot_value":"2/3","right_exterior_value":"304/3",
       "historical_census":{"before":population,"after":population,
           "delta":{key:0 for key in population},"newly_closed_original_ids":[]},
       "claims":{"bounded_negative_result_C":True,
           "new_frozen_source_closure_A":False,
           "required_PB_discharge_B":False,
           "general_event_theorem":False,
           "invalidates_narrow_square_theorem":False,
           "independent_oracle":False,"native_geometry":False,
           "engineering_STEP":False,"MC_B_established":False,
           "MC_1_established":False,"production_authorized":False,
           "required_operations":26}
    }

def test_adversaries(row):
    prior=v17.run_self_test(row)
    points=[Q(0),Q(1,3),Q(2,3),Q(1)]
    brackets=[(Q(1,6),Q(1,4)),(Q(3,4),Q(5,6))]
    adversaries=[
       (points+[Q(1,5)],brackets),
       (points+[Q(4,5)],brackets),
       (points,[(Q(0),Q(1,4)),brackets[1]]),
       (points,[brackets[0],(Q(3,4),Q(1))]),
       ([Q(0),Q(1)],brackets)]
    for ps,bs in adversaries:
        try:falsify(ps,bs)
        except Refused:continue
        raise AssertionError("ADVERSARIAL_CANDIDATE_OR_EVENT_MUTATION_ACCEPTED")
    for change in (
       lambda x:x["claims"].__setitem__("MC_B_established",True),
       lambda x:x["historical_census"]["delta"].__setitem__("route_refusals",-1),
       lambda x:x["actual_root_multiplicities"].__setitem__(0,2)):
        fake=expected_receipt()
        change(fake)
        need(fake!=expected_receipt(),"FORGED_RECEIPT_NOT_REFUSED")
    t=Q(1,2)
    need((t-t)**2==0 and (Q(0)-t)**2==Q(1,4),
         "EVEN_TANGENCY_PROSPECTIVE")
    e=Q(1,2**100)
    f=lambda x:(x-t)**2-e**2
    need(f(t-e)==0 and f(t+e)==0 and f(t)<0 and 2*e==Q(1,2**99),
         "CLOSE_ROOT_PROSPECTIVE")
    laurent={}
    for a,s in ((2,1),(-2,-1)):
        for b,c in ((1,1),(-1,1)):
            laurent[a+b]=laurent.get(a+b,0)+s*c
    need(laurent=={3:1,1:1,-1:-1,-3:-1},
         "IDENTITY_ZERO_PROSPECTIVE")
    return {"inherited_v17_adversarial_mutations":prior,
            "new_candidate_mutations_refused":len(adversaries),
            "new_receipt_mutations_refused":3,
            "new_prospective_nonclaim_controls":3}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--contract",action="store_true")
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    frozen=v17.checked_json(v17.CORPUS,v17.CORPUS_BLOB)
    v2=v17.checked_json(v17.V2,v17.V2_BLOB)
    row=v17.census(frozen,v2)
    spec=v17.check_source(row)
    v17.check_factor_and_events(spec)
    v17.check_report(json.loads(v17.REPORT.read_text(encoding="utf-8")))
    ps=candidate_set(spec)
    brackets=[(Q(1,6),Q(1,4)),(Q(3,4),Q(5,6))]
    falsify(ps,brackets)
    receipt=json.loads(RECEIPT.read_text(encoding="utf-8"))
    need(receipt==expected_receipt(),"MACHINE_RECEIPT_DRIFT")
    controls=test_adversaries(row) if a.self_test else {}
    print(json.dumps({"status":"BOUNDED_C_ONLY","case_id":v17.ID,
                      "candidate_route":ROUTE,"frozen_case_delta":0,
                      "adversaries":controls},sort_keys=True))

if __name__=="__main__":
    main()
