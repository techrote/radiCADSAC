#!/usr/bin/env python3
"""PB-007-01 exact original-source knot-signature information-loss falsifier.

DETERMINISTIC_MODEL, bounded C only. Neither an event-isolation solver nor a gate.
Uses exact rationals, original v54/v2 hash custody and symbolic trig inequalities.
"""
import argparse
import copy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research/machining-completeness/tasks/MC-038"
CORPUS = TASK / "pb00701-finite-owner-corpus-v54.json"
EVIDENCE = TASK / "pb00701-post-v54-evidence-reconciliation-v2.json"
RECEIPT = TASK / "pb00701-knot-unsigned-sign-erasure-20261105.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
EVIDENCE_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
AUTH_BLOB = "fa0233323a0804d8a5d3eb7cd892a274a6173fab"
BASE = {
    "composite:DELEGATED_V6_CONSTANT_MODULATION:tail0": {
        "source_sha256": "9eb6f08a44882adffa919529247c40190c70e8d7599ee2b1a0f7978ef2569eb1",
        "row_sha256": "145ac5ce5b533c447c7356e8dc721dbfa5a44562cdc3a37422278fd7bd0199fc",
        "cos0": {"degree": 0, "knots": ["0", "1", "2"], "controls": ["0", "0"]},
        "right_sign": "-",
        "v54": "V27_CHILD_LEFT_ENDPOINT_MULTIPLICITY_NOT_COMPOSABLE",
    },
    "composite:DELEGATED_V6_CONSTANT_MODULATION:tail100": {
        "source_sha256": "f6a0eb06c66af415fbb8abdfe62f9b36a2a2bf154e535d83307a80228e044ad5",
        "row_sha256": "0801317d3452c77733a129148d58eaac2f06aa9cd26396a44892e82c524e1db2",
        "cos0": {"degree": 1, "knots": ["0", "0", "1", "1", "2", "2"], "controls": ["0", "0", "0", "100"]},
        "right_sign": "+",
        "v54": "V27_CHILD_NOT_CERTIFIED",
    },
}
H1 = {"degree": 0, "knots": ["0", "1", "2"], "controls": ["1", "1"]}

def require(ok, why):
    if not ok:
        raise AssertionError(why)

def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha256(data):
    return hashlib.sha256(canonical(data)).hexdigest()

def verified_json(path, blob):
    data = path.read_bytes()
    got = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
    require(got == blob, f"Git blob drift: {path} {got}")
    return json.loads(data)

def expected_spec(entry):
    return {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "source_parameter_id": "source-time-t",
        "parameter_lo": "0", "parameter_hi": "2",
        "phase_turn_offset": "0", "phase_turn_rate": "1/4",
        "cos_splines": {"0": entry["cos0"], "1": H1},
        "sin_splines": {},
    }

def check_case(row, ident):
    entry = BASE[ident]
    require(row["id"] == ident, "original case ID changed")
    require(row["origin"] == "verify_pb00701_v7", "original provenance changed")
    require(row["kind"] == "COMPOSITE_TAIL", "original provenance kind changed")
    require(row["spec"] == expected_spec(entry), "original B-spline/phase/coordinate altered")
    require(sha256(row["spec"]) == entry["source_sha256"], "canonical source SHA-256 changed")
    require(sha256(row) == entry["row_sha256"], "whole-row SHA-256 changed")
    observed = row["expected"]["observed"]
    require(row["expected"]["v54_disposition"] == "BLOCKED", "historical v54 disposition changed")
    require(observed["status"] == "BLOCKED", "historical whole-source refusal changed")
    require(observed["spans"] == [
        ["DELEGATED_V6_CONSTANT_MODULATION", "CERTIFIED", None],
        ["PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION",
         "BLOCKED", entry["v54"]],
    ], "historical V27 refusal/spans changed")
    return True

def atan_bounds(x, n=30):
    """Alternating rational enclosure, 0 < x < 1."""
    require(Q(0) < x < Q(1) and n > 0, "invalid rational arctangent enclosure")
    partial = sum(((-1) ** k) * x ** (2*k+1) / Q(2*k+1) for k in range(n))
    nxt = x ** (2*n+1) / Q(2*n+1)
    return ((partial, partial+nxt) if n % 2 == 0
            else (partial-nxt, partial))

def pi_bounds():
    """Machin identity pi = 16 atan(1/5) - 4 atan(1/239), rational enclosure."""
    l5, u5 = atan_bounds(Q(1, 5))
    l239, u239 = atan_bounds(Q(1, 239))
    lo, hi = 16*l5-4*u239, 16*u5-4*l239
    require(Q(3) < lo < hi < Q(4), "pi bounds incoherent")
    return lo, hi

def proof_controls():
    lo, hi = pi_bounds()
    # Exact tangent subtraction: tan(4 atan(1/5))=120/119,
    # tan(4 atan(1/5)-atan(1/239))=1; quadrant gives pi/4.
    require((Q(120,119)-Q(1,239)) /
            (1+Q(120,119)*Q(1,239)) == 1, "Machin angle identity")
    require(-hi/2 < -lo/2 < 0, "left signed first jet")
    require(Q(100)-hi/2 > Q(98), "positive right first jet for original ramp")
    require(lo/2 > 0, "negative right first jet for original flat tail")

    # Adversarial arbitrarily-close rational slopes on either side of pi/2:
    # classification is of the *right knot germ*, NOT whole-source root count.
    below = Q(157079632679489661922, 10**20)
    above = Q(157079632679489661924, 10**20)
    require(below < lo/2 and above > hi/2, "close signed-germ boundaries not proved")
    require(above-below == Q(2,10**20), "close gap changed")
    # Left/right polynomial multiplicities alone are not signed jets:
    # (t-1)^2 has (2,2) and (+,+); (t-1)^3 has (3,3) and (-,+).
    for order, signs in ((2, ("+","+",)), (3, ("-","+",))):
        delta = Q(1,10**24)
        left = (-delta) ** order
        right = delta ** order
        require(("+" if left > 0 else "-",
                 "+" if right > 0 else "-") == signs, "polynomial order/parity control")
    return {"pi_half_interval_width_lt": "1/10^30",
            "close_rational_ramp_gap": "2/10^20",
            "signed_right_germs": {"near_below": "-", "near_above": "+"},
            "synthetic_order2": ["+", "+"], "synthetic_order3": ["-", "+"]}

def signature(ident):
    """Exact established result for *only* the two fully checked original sources."""
    require(ident in BASE, "unsupported source: no fabricated finite proof")
    # Left: cos(pi*t/2)>0 for 0<=t<1, first jet -pi/2 at t=1.
    # Flat right: cos(pi*t/2)<0 for 1<t<=2.
    # Ramp right: F(1+x)=100*x-sin(pi*x/2)>98*x>0, 0<x<=1.
    # Both share sole source-knot root t=1, one-sided orders [1,1].
    return {
        "physical_zero_set": ["1"], "knot": "1",
        "parameter": "source-time-t", "interval": ["0","2"],
        "phase": ["0","1/4"], "one_sided_orders": [1,1],
        "physical_sign_cells": ["+", BASE[ident]["right_sign"]],
        "event": "CROSSING" if BASE[ident]["right_sign"] == "-" else "TOUCHING",
        "global_smooth_multiplicity": None,
    }

def compute(root=ROOT):
    corpus = verified_json(root / CORPUS.relative_to(ROOT), CORPUS_BLOB)
    v2 = verified_json(root / EVIDENCE.relative_to(ROOT), EVIDENCE_BLOB)
    authority = verified_json(root / "handoffs/current-authority.json", AUTH_BLOB)
    require(authority["production_authorized"] is False and
            authority["capability_status"] == "NOT_ESTABLISHED", "authority promotion")
    rows = corpus["cases"]
    require(len(rows) == len({r["id"] for r in rows}) == 121, "frozen denominator/ID")
    blocked = [r for r in rows if r["expected"]["v54_disposition"] == "BLOCKED"]
    ordered = [r for r in rows if r["expected"]["v54_disposition"].startswith("BLOCKED:")]
    require(len(blocked) == 20 and len(ordered) == 30, "historical refusal population")
    records = v2["source_cases"]
    require(len(records) == len({r["case_id"] for r in records}) == 50, "v2 population/duplicates")
    unresolved_ids = {r["id"] for r in blocked + ordered}
    require({r["case_id"] for r in records} == unresolved_ids, "v2 case set mismatch")
    require(all(r["evidence"]["complete_original_source_zero_set"] is True and
                r["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC"
                for r in records), "v2 complete-source authority changed")
    require(v2["gates"]["required_machining_operations"] == 26 and
            v2["gates"]["MC-B"] == "NOT_ESTABLISHED" and
            v2["gates"]["MC-1"] == "NOT_ESTABLISHED", "protected gate/operation status")
    byid = {r["id"]: r for r in rows}
    witnesses = {r["case_id"]: r for r in records}
    for ident, entry in BASE.items():
        check_case(byid[ident], ident)
        witness = witnesses[ident]
        require(witness["source_sha256"] == entry["source_sha256"] and
                witness["original_row_sha256"] == entry["row_sha256"], "v2 source binding")
        require(witness["evidence"]["scope"] == "COMPLETE_FINITE_SOURCE_ZERO_SET",
                "original finite evidence changed")
        require(witness["historical_v54_disposition"] == "BLOCKED",
                "original historical case classification changed")
    a, b = (signature(x) for x in BASE)
    selected = ("physical_zero_set","knot","parameter","interval","phase","one_sided_orders")
    require(all(a[k] == b[k] for k in selected), "not indistinguishable to underspecified handoff")
    require(a["physical_sign_cells"] != b["physical_sign_cells"] and
            a["event"] != b["event"], "no certified information-loss counterexample")
    proof_controls()
    return True

def self_test():
    proof_controls()
    a,b = list(BASE)
    require(signature(a)["event"] == "CROSSING", "flat-tail sign error")
    require(signature(b)["event"] == "TOUCHING", "ramp-tail sign error")
    for bad in ("harvested:verify_pb00701_v53:cb01c327d5f1","unknown"):
        try: signature(bad)
        except AssertionError: pass
        else: raise AssertionError("unproved source admitted")
    # 12 independent source/status/provenance mutation refusals on frozen shapes.
    originals = {
        k: {"id": k, "origin": "verify_pb00701_v7", "kind": "COMPOSITE_TAIL",
            "spec": expected_spec(v), "expected": {"v54_disposition": "BLOCKED",
               "observed": {"status": "BLOCKED",
                 "spans": [["DELEGATED_V6_CONSTANT_MODULATION","CERTIFIED",None],
                    ["PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION",
                     "BLOCKED",v["v54"]]]}}}
        for k,v in BASE.items()
    }
    # Frozen rows are whole-row and canonical-spec SHA checked; these copies
    # independently reproduce canonical bytes, avoiding a hand-authored oracle.
    for ident,row in originals.items(): check_case(row, ident)
    changes = [
        lambda r: r.update(id="forged"),
        lambda r: r.update(origin="verify_pb00701_v9"),
        lambda r: r.update(kind="HARVESTED"),
        lambda r: r["spec"].update(phase_turn_rate="1/2"),
        lambda r: r["spec"].update(phase_turn_offset="1/4"),
        lambda r: r["spec"].update(parameter_lo="-1"),
        lambda r: r["spec"].update(source_parameter_id="chart-u"),
        lambda r: r["spec"]["cos_splines"]["1"]["controls"].__setitem__(1,"2"),
        lambda r: r["spec"]["cos_splines"]["0"]["controls"].__setitem__(-1,"99"),
        lambda r: r["spec"]["cos_splines"]["0"]["knots"].__setitem__(-1,"3"),
        lambda r: r["expected"]["observed"].update(status="CERTIFIED"),
        lambda r: r["expected"]["observed"]["spans"][1].__setitem__(2,"CERTIFIED"),
        lambda r: r["spec"].update(parameter_projection="source-time-t"),
    ]
    for ident,original in originals.items():
        for mutate in changes:
            altered=copy.deepcopy(original)
            mutate(altered)
            try: check_case(altered, ident)
            except AssertionError: pass
            else: raise AssertionError("adversarial mutation was accepted")
    return True

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--contract",action="store_true")
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--proof-only-self-test",action="store_true")
    args=ap.parse_args()
    if args.self_test or args.proof_only_self_test: self_test()
    if not args.proof_only_self_test:
        compute()
        receipt=json.loads(RECEIPT.read_text())
        require(receipt["result"] == "BOUNDED_C" and
                receipt["before_after"]["newly_resolved_case_ids"] == [] and
                all(v["delta"] == 0 for k,v in receipt["before_after"].items()
                    if isinstance(v,dict) and "delta" in v), "receipt fake gate or closure")
        require(receipt["candidate"]=="KNOT_SIGN_FROM_ROOT_SET_AND_UNSIGNED_SIDE_ORDERS_ONLY",
                "candidate boundary changed")
    print("PASS exact source-bound knot-signature falsification; historical Δ=0; DETERMINISTIC_MODEL")

if __name__=="__main__": main()
