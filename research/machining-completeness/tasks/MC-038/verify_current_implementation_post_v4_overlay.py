#!/usr/bin/env python3
"""Check dated MC-038 navigation overlay against immutable v54/v2 evidence.

This is descriptive source-bound custody checking, not PB-007 root/event proof.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OVERLAY = HERE / "current-implementation-post-v4-overlay-20261104.json"
DOC = ROOT / "docs/machining-completeness/77-MC038-CURRENT-IMPLEMENTATION-STATE.md"
PINS = {
    "pb00701-finite-owner-corpus-v54.json": "5841c331579489b25caef38cd412bdbf286f9134",
    "pb00701-finite-owner-inventory-v54.json": "8649c20ab77e199f9c3fa351b8b6742218f27abb",
    "pb00701-finite-owner-coverage-v54.json": "600ba29786f50397f29fd435fc5e2c57076088f9",
    "pb00701-post-v54-evidence-reconciliation-v2.json": "e52d3baf3692a011cf86234eeaa992ef407d99fd",
    "current-implementation-state-v4.json": "81124b7c607b7257747f635ee4bc5f810317914d",
}
AUTH = "fa0233323a0804d8a5d3eb7cd892a274a6173fab"
DOMAIN = "23de82f5240a72509f7afe4acd5948b65bc4ff13"
CASES = {
    "composite:DELEGATED_V6_CONSTANT_MODULATION:tail100": (
        374, "POSITIVE_EXTERIOR_KNOT_OMITS_INTERIOR_ROOT_PROSPECTIVE_CONTROL"),
    "composite:PB00701_V8_EXACT_COMMON_FACTOR_REDUCTION:tail0": (
        376, "FINITE_Z_CAYLEY_ONLY"),
    "composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:tail0": (
        378, "ENDPOINT_SAME_SIGN_IMPLIES_EMPTY_INTERIOR"),
    "harvested:verify_pb00701_v52:2250401ce435": (
        382, "GLOBAL_SINGLE_DERIVATIVE_SIGN_REQUIRED"),
    "harvested:verify_pb00701_v9:4e7b85fa122a": (
        385, "DIRECT_AFFINE_H1_CAYLEY_RATIONAL_POLYNOMIALIZATION"),
}
MERGES = {374:"8178ee868654b741ffee381b85659893c5e62ce5",
          376:"2db9b72ca7652c94cad76e452247414c5c004827",
          378:"1344943ce7c96f31d6439b3282f689293b0ee08b",
          382:"34e91a5691b9f83ff1afd746fc964c7666bf142b",
          385:"87b3bfa4387a014f0915a23c7fdf8a6816bcf8c2"}
DENOM = {"frozen_original_sources":121,"historical_route_refusals":20,
         "historical_missing_ordered_premises":30,"complete_source_specific_witnesses":50}

def require(ok, why):
    if not ok:
        raise ValueError(why)

def canon_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",",":"),
                                     ensure_ascii=True).encode("utf-8")).hexdigest()

def git_blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()

def load(path, max_bytes=300000):
    require(path.is_file() and path.stat().st_size <= max_bytes,
            "MISSING_OR_OVERSIZE_INPUT: "+str(path))
    return json.loads(path.read_text(encoding="utf-8"))

def read_pinned():
    for filename, sha in PINS.items():
        require(git_blob(HERE/filename)==sha,"HISTORICAL_BLOB_DRIFT: "+filename)
    auth = ROOT/"handoffs/current-authority.json"
    domain = ROOT/"research/machining-completeness/tasks/MC-002/domain-contract-v1.json"
    require(git_blob(auth)==AUTH and git_blob(domain)==DOMAIN,
            "DOMAIN_OR_AUTHORITY_DRIFT")
    a,d=load(auth),load(domain)
    require(a["capability_status"]=="NOT_ESTABLISHED" and
            a["production_authorized"] is False and
            len(d["coverage_rule"]["required_operation_ids"])==26,
            "UNAUTHORIZED_CAPABILITY_OR_DOMAIN_CHANGE")
    return (load(HERE/"pb00701-finite-owner-corpus-v54.json"),
            load(HERE/"pb00701-post-v54-evidence-reconciliation-v2.json"),
            load(HERE/"current-implementation-state-v4.json"))

def validate(overlay, corpus, registry, base):
    require(overlay["schema"]=="radicadsac-mc038-current-implementation-post-v4-overlay/1.0"
            and overlay["as_of"]=="2026-11-04" and
            overlay["snapshot_kind"]=="POST_V4_QUALIFIED_NEGATIVE_METHOD_BOUNDARIES_NOT_GATE_AUTHORITY",
            "WRONG_OVERLAY_AUTHORITY")
    require(base["as_of"]=="2026-11-03" and
            overlay["base_v4_snapshot"]["git_blob"]==PINS["current-implementation-state-v4.json"],
            "HISTORICAL_V4_REWRITTEN")
    pins=overlay["source_authority_historical_pins"]
    for filename,label in [
        ("pb00701-finite-owner-corpus-v54.json","v54_corpus_git_blob"),
        ("pb00701-finite-owner-inventory-v54.json","v54_inventory_git_blob"),
        ("pb00701-finite-owner-coverage-v54.json","v54_coverage_git_blob"),
        ("pb00701-post-v54-evidence-reconciliation-v2.json","post_v54_v2_git_blob")]:
        require(pins[label]==PINS[filename], "OVERLAY_PIN_DRIFT: "+label)
    rows=corpus["cases"]
    require(len(rows)==121 and len({r["id"] for r in rows})==121 and
            len({canon_hash(r["spec"]) for r in rows})==121,
            "ORIGINAL_SOURCE_DENOMINATOR_OR_DUPLICATE_SOURCE_SPEC")
    historical={r["id"]:r for r in rows if r["expected"]["v54_disposition"].startswith("BLOCKED")}
    refusal=sum(r["expected"]["v54_disposition"]=="BLOCKED" for r in historical.values())
    ordered=sum(r["expected"]["v54_disposition"]==
                "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"
                for r in historical.values())
    require((refusal,ordered,len(historical))==(20,30,50),"WRONG_HISTORICAL_CENSUS")
    records=registry["source_cases"]
    require(len(records)==50 and len({r["case_id"] for r in records})==50,
            "REGISTERED_SOURCE_POPULATION_CHANGED")
    evidence={r["case_id"]:r for r in records}
    require(set(evidence)==set(historical),"REGISTERED_UNION_NOT_EQUAL_TO_FROZEN")
    for id,r in evidence.items():
        h=historical[id]
        require(r["origin"]==h["origin"] and
                r["source_sha256"]==canon_hash(h["spec"]) and
                r["original_row_sha256"]==canon_hash(h) and
                r["historical_v54_disposition"]==h["expected"]["v54_disposition"] and
                r["registered_evidence_level"]=="COMPLETE_SOURCE_SPECIFIC" and
                r["evidence"]["complete_original_source_zero_set"] is True and
                r["historical_disposition_changed"] is False,
                "SOURCE_PROVENANCE_OR_COVERAGE_MISMATCH: "+id)
    require(registry["summary"]["complete_finite_sources"]==49 and
            registry["summary"]["complete_continuum_sources"]==1 and
            registry["summary"]["selected_producer_families"]==14,
            "V2_SOURCE_TYPE_OR_PRODUCER_DRIFT")
    require(overlay["frozen_before"]==DENOM and overlay["frozen_after"]==DENOM and
            overlay["frozen_deltas"]=={k:0 for k in DENOM} and
            overlay["newly_resolved_historical_case_ids"]==[],
            "UNWARRANTED_HISTORICAL_PROMOTION")
    original=overlay["registered_original_cases_with_bounded_route_falsifiers"]
    require(len(original)==len(CASES) and
            {r["original_case_id"] for r in original}==set(CASES),
            "FALSIFICATION_CASE_SCOPE_CHANGED")
    for r in original:
        id=r["original_case_id"]
        v=evidence[id]
        pr,route=CASES[id]
        require(r["merged_pr"]==pr and r["negative_route"]==route and
                r["original_source_sha256"]==v["source_sha256"] and
                r["original_row_sha256"]==v["original_row_sha256"] and
                r["phase_turn_law"]==v["phase_turn_law"] and
                r["original_source_interval"]==v["source_interval"] and
                r["historical_v54_disposition"]==v["historical_v54_disposition"] and
                r["prior_v2_coverage"]=="COMPLETE_SOURCE_SPECIFIC" and
                r["original_case_newly_resolved_by_pr"] is False,
                "FALSE_ROUTE_CASE_ORIGINAL_SOURCE_BINDING: "+id)
    landings=overlay["reviewed_merged_results"]
    require(len(landings)==len(MERGES) and
            {r["pr"] for r in landings}==set(MERGES) and
            all(r["merged_main"]==MERGES[r["pr"]] for r in landings),
            "QUALIFIED_MERGE_RECORD_MISMATCH")
    require(overlay["open_required"]==["PB-007-01","PB-007-02","PB-007-03","PB-007-04",
             "PO-02","PO-04","PO-05","PO-07","PO-08"] and
            overlay["mc_b"]=="NOT_ESTABLISHED" and
            overlay["mc_1"]=="NOT_ESTABLISHED" and
            overlay["required_operation_count"]==26 and
            overlay["production_authorized"] is False and
            overlay["evidence_class"]=="DETERMINISTIC_MODEL",
            "GLOBAL_GATE_OR_EVIDENCE_PROMOTION")
    require("overlay-20261104.json" in DOC.read_text(encoding="utf-8") and
            "resolve zero new historical cases" in DOC.read_text(encoding="utf-8"),
            "DOC_MACHINE_BINDING_MISSING")
    return {"status":"DESCRIPTIVE_NAVIGATION_CHECKED_NOT_PB_PROOF",
            "matched_frozen_case_ids":50,"frozen_before":DENOM,
            "frozen_after":DENOM,"newly_resolved_historical_case_ids":[],
            "qualified_negative_prs":sorted(MERGES)}

def self_test(original, corpus, registry, base):
    def reject(field, val, label):
        test=copy.deepcopy(original)
        test[field]=val
        try: validate(test, corpus, registry, base)
        except (ValueError,KeyError,TypeError,AssertionError): return
        raise AssertionError("mutation accepted: "+label)
    reject("mc_b","ESTABLISHED","false gate")
    reject("production_authorized",True,"false production")
    reject("frozen_after",{**DENOM,"complete_source_specific_witnesses":51},"false source")
    reject("newly_resolved_historical_case_ids",["fabricated"],"invented closure")
    reject("frozen_deltas",{**original["frozen_deltas"],"historical_route_refusals":-1},
           "false route admission")
    damaged=copy.deepcopy(original["registered_original_cases_with_bounded_route_falsifiers"])
    damaged[0]["original_source_sha256"]="0"*64
    reject("registered_original_cases_with_bounded_route_falsifiers",damaged,
           "original source tampering")
    damaged=copy.deepcopy(original["registered_original_cases_with_bounded_route_falsifiers"])
    damaged[1]["original_case_newly_resolved_by_pr"]=True
    reject("registered_original_cases_with_bounded_route_falsifiers",damaged,
           "old witness double count")
    damaged=copy.deepcopy(original["reviewed_merged_results"])
    damaged[-1]["merged_main"]="0"*40
    reject("reviewed_merged_results",damaged,"wrong merge identity")
    damaged=copy.deepcopy(corpus)
    damaged["cases"][0]["spec"]=copy.deepcopy(damaged["cases"][1]["spec"])
    try: validate(original,damaged,registry,base)
    except (ValueError,KeyError,TypeError): pass
    else: raise AssertionError("duplicate original source spec accepted")
    damaged=copy.deepcopy(corpus)
    next(row for row in damaged["cases"] if row["expected"]["v54_disposition"].startswith("BLOCKED"))["spec"]["phase_turn_rate"]="37"
    try: validate(original,damaged,registry,base)
    except (ValueError,KeyError,TypeError): pass
    else: raise AssertionError("corrupted source accepted")
    damaged=copy.deepcopy(registry)
    damaged["source_cases"][0]["registered_evidence_level"]="PARTIAL_ORDERED_CHILD"
    try: validate(original,corpus,damaged,base)
    except (ValueError,KeyError,TypeError): pass
    else: raise AssertionError("registry downgrade accepted")
    return {"adversarial_mutations_rejected":11}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--contract",action="store_true")
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    c,r,v4=read_pinned()
    x=load(OVERLAY)
    result=validate(x,c,r,v4)
    if args.self_test:
        result.update(self_test(x,c,r,v4))
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__":
    main()
