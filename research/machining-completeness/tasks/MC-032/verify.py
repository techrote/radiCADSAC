#!/usr/bin/env python3
from __future__ import annotations
import argparse
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from event_engine import *

def require(cond,msg):
    if not cond:
        raise AssertionError(msg)

def self_test():
    require(exact_event([-1,1],0)["relation"]=="NEGATIVE","signed negative")
    require(exact_event([-1,1],2)["relation"]=="POSITIVE","signed positive")
    e=exact_event([-1,1],1)
    require(e["relation"]=="ZERO" and e["multiplicity"]==1 and e["sign_change"],"simple exact zero")
    eps=Fraction(1,1_000_000)
    require(exact_event([-1,1],1-eps)["relation"]=="NEGATIVE","signed left neighbour")
    require(exact_event([-1,1],1+eps)["relation"]=="POSITIVE","signed right neighbour")

    even=exact_event([1,-2,1],1)
    require(even["multiplicity"]==2 and even["singular"] and not even["sign_change"] and even["event_kind"]=="MULTIPLE_TANGENCY","even multiple")
    odd=exact_event([8,12,6,1],-2)
    require(odd["multiplicity"]==3 and odd["singular"] and odd["sign_change"] and odd["event_kind"]=="MULTIPLE_CROSSING","odd multiple")

    require(distinct_roots_open([-1,0,1],-1,1)==0,"endpoint roots must be excluded")
    require(distinct_roots_open([1,-2,1],0,2)==1,"multiple root is one distinct event")
    require(classify_open_interval([2,0,1],-1,1)["status"]=="DECIDED","root-free positive interval")
    require(classify_open_interval([-1,0,1],0,2)["status"]=="BLOCKED","interior critical event routed")
    require(classify_open_interval([-1,1],1,2)["reason"]=="CRITICAL_EVENT_AT_INTERVAL_ENDPOINT","endpoint exact zero routed")

    try:
        exact_event([-1,1],1.0)
        raise AssertionError("float accepted")
    except TypeError:
        pass

    sep=validate_analytic_evidence({
        "certified":True,"kind":"SEPARATED_INTERVAL","source_parameter_id":"q",
        "lower_bound":"1/1000000","upper_bound":"3/10"
    })
    require(sep["status"]=="CERTIFIED" and sep["relation"]=="NO_ZERO","separated analytic")
    trans=validate_analytic_evidence({
        "certified":True,"kind":"TRANSVERSAL_ROOT","source_parameter_id":"q",
        "unique_root":True,"derivative_abs_lower":"1/1000",
        "parameter_lo":"1/3","parameter_hi":"2/3"
    })
    require(trans["status"]=="CERTIFIED","transversal analytic")
    tangent=validate_analytic_evidence({
        "certified":True,"kind":"TANGENTIAL_ROOT","source_parameter_id":"q"
    })
    require(tangent=={
        "status":"BLOCKED","reason":"TANGENTIAL_MULTIPLE_SINGULAR_OR_UNSUPPORTED_ANALYTIC_EVENT","blocker":"PB-007-01"
    },"general tangency must preserve PB-007-01")
    projected=validate_analytic_evidence({
        "certified":True,"kind":"SEPARATED_INTERVAL","source_parameter_id":"q",
        "parameter_projection":"theta","lower_bound":"1","upper_bound":"2"
    })
    require(projected["status"]=="SEMANTIC_BLOCKER","shared source parameter must not split")
    try:
        validate_analytic_evidence({
            "certified":True,"kind":"SEPARATED_INTERVAL","source_parameter_id":"q",
            "lower_bound":0.1,"upper_bound":0.2
        })
        raise AssertionError("float analytic bounds accepted")
    except ValueError:
        pass

    rr=resource_refusal()
    require(terminal_status(rr)=="RESOURCE_REFUSAL" and rr["is_truth_value"] is False,"resource refusal semantics")

    base={
        "event_evidence_status":"CERTIFIED","source_parameter_id":"q",
        "common_frame":"workpiece_common","input_revision":"rev-17","body_id":"body-A",
        "durable_identity_source":"canonical_journal",
    }
    touch=certify_topology_event({**base,"positive_volume_witness":"0","independent_connectivity_certificate":True})
    require(touch["relation"]=="TOUCHING_ONLY_NO_MATERIAL_TRANSITION" and not touch["body_transition"],"touching semantics")
    badid=certify_topology_event({**base,"positive_volume_witness":"1/1000000","independent_connectivity_certificate":True,"durable_identity_source":"backend_topology_id"})
    require(badid["status"]=="SEMANTIC_BLOCKER","backend topology identity")
    blocked=certify_topology_event({**base,"positive_volume_witness":"1/1000000","independent_connectivity_certificate":False})
    require(blocked["status"]=="BLOCKED" and blocked["blocker"]=="PB-007-04","universal topology blocker")
    cert=certify_topology_event({**base,"positive_volume_witness":"1/1000000","independent_connectivity_certificate":True})
    require(cert["status"]=="CERTIFIED" and cert["durable_transition_owner"]=="MC-033" and not cert["body_transition_committed"],"bounded topology cert")

    c=bind_event_certificate(
        input_digest="i"*64,canonical_digest="c"*64,sweep_digest="s"*64,
        challenge_id="MC049-017",configuration_digest="g"*64,
        decision={"status":"CERTIFIED","relation":"SIMPLE_ZERO_ISOLATED"}
    )
    require(verify_event_certificate(c,challenge_id="MC049-017",configuration_digest="g"*64),"binding valid")
    stale=deepcopy(c); stale["challenge_id"]="MC049-018"
    require(not verify_event_certificate(stale,challenge_id="MC049-018"),"binding mutation rejected")
    require(not verify_event_certificate(c,configuration_digest="x"*64),"config mismatch rejected")
    return True

def contract_test(root:Path):
    contract=json.loads((HERE/"critical-event-engine-contract-v1.json").read_text())
    outcome=json.loads((HERE/"outcome.json").read_text())
    require(contract["task"]=="MC-032" and outcome["task"]=="MC-032","task identity")
    require(contract["ownership"]==["MC032-A","MC032-B","MC032-C","CERT-026-A:event-classification"],"MC-026 ownership")
    require(contract["truth_authority"]["epsilon_or_tolerance"] is False,"epsilon must not be truth")
    require(contract["truth_authority"]["timeout_or_budget"] is False,"timeout must not be truth")
    require(contract["truth_authority"]["binary_float"] is False,"float must not be truth")
    require(contract["analytic_route"]["general_tangential_multiple_singular"]["terminal"]=="TRANSCENDENTAL_EVENT_BLOCKER","PB route")
    require(contract["analytic_route"]["general_tangential_multiple_singular"]["blocker"]=="PB-007-01","PB-007-01 preserved")
    require(contract["topology"]["universal_connectivity_blocker"]=="PB-007-04","PB-007-04 preserved")
    require(contract["topology"]["durable_transition_owner"]=="MC-033","ownership split")
    require(contract["topology"]["touching_is_material"] is False,"positive-volume semantics")
    require(contract["challenge_discipline"]["record_count"]==64,"MC-049 count")
    require(contract["challenge_discipline"]["custody"]=="PUBLIC_PRESELECTION_PREREGISTRATION","honest challenge label")
    require(contract["capability_promotions"]==[],"no capability promotion")

    deps={
        "MC-008":("research/machining-completeness/tasks/MC-008/outcome.json","COMPLETED_RESEARCH"),
        "MC-015":("research/machining-completeness/tasks/MC-015/outcome.json","COMPLETED_RESEARCH"),
        "MC-026":("research/machining-completeness/tasks/MC-026/outcome.json","COMPLETED_RESEARCH"),
    }
    dep_objs={}
    for tid,(rel,kind) in deps.items():
        obj=json.loads((root/rel).read_text())
        dep_objs[tid]=obj
        require(obj["task"]==tid and obj["result_kind"]==kind,f"{tid} dependency")

    proof=json.loads((root/"research/machining-completeness/proof-obligations-v1.json").read_text())
    obligations={entry["id"]:entry for entry in proof["obligations"]}
    require(obligations["PO-04"]["state"]=="OPEN" and obligations["PO-04"]["integration_owner"]=="MC-032","PO-04 must remain an open MC-032 integration obligation")
    require(obligations["PO-07"]["state"]=="OPEN" and obligations["PO-07"]["integration_owner"]=="MC-032","PO-07 must remain an open MC-032 integration obligation")
    own_blockers={b["id"]:b["status"] for b in outcome["blockers"]}
    require(own_blockers.get("PB-007-01")=="OPEN","PB-007-01 must remain open")
    require(own_blockers.get("PB-007-04")=="OPEN_PROPAGATED","PB-007-04 must remain propagated")
    require(contract["preserved_open_obligations"]==["PB-007-01","PB-007-04","PO-04","PO-07","MC-B"],"preserved-obligation contract drift")

    reg=json.loads((root/"research/machining-completeness/outcomes-v1.json").read_text())
    require(reg["tasks"]["MC-032"]["state"]=="COMPLETED_RESEARCH","registry state")
    require(any(a.endswith("MC-032/outcome.json") for a in reg["tasks"]["MC-032"]["accepted_artifacts"]),"registry artifact")
    require(reg["tasks"]["MC-032"]["blockers"]==outcome["blockers"],"registry blocker drift")

    attacks=[
        ("epsilon", lambda x: x["truth_authority"].__setitem__("epsilon_or_tolerance",True)),
        ("timeout", lambda x: x["truth_authority"].__setitem__("timeout_or_budget",True)),
        ("float", lambda x: x["truth_authority"].__setitem__("binary_float",True)),
        ("close-pb", lambda x: x["analytic_route"]["general_tangential_multiple_singular"].__setitem__("blocker","CLOSED")),
        ("topology-id", lambda x: x["topology"].__setitem__("durable_identity_authority","backend_topology_id")),
        ("held-out-lie", lambda x: x["challenge_discipline"].__setitem__("custody","SECRET_HELD_OUT")),
    ]
    def invariant(x):
        return (
            x["truth_authority"]["epsilon_or_tolerance"] is False and
            x["truth_authority"]["timeout_or_budget"] is False and
            x["truth_authority"]["binary_float"] is False and
            x["analytic_route"]["general_tangential_multiple_singular"]["blocker"]=="PB-007-01" and
            x["topology"]["durable_identity_authority"]=="canonical_journal_body_lineage" and
            x["challenge_discipline"]["custody"]=="PUBLIC_PRESELECTION_PREREGISTRATION"
        )
    require(invariant(contract),"baseline contract invariant")
    for name,mut in attacks:
        x=deepcopy(contract); mut(x)
        require(not invariant(x),f"attack not discriminated: {name}")
    return True

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--contract",action="store_true")
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    if not args.contract and not args.self_test:
        args.contract=args.self_test=True
    if args.self_test:
        self_test()
        print("MC-032 event engine self-test passed")
    if args.contract:
        root=HERE.parents[3]
        contract_test(root)
        self_test()
        print("MC-032 contract verification passed")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
