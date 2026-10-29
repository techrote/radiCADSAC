#!/usr/bin/env python3
"""MC-038: checked *fixed-source* V27/V41 trigonometric ordered child views.

Research only. This deliberately does NOT consume the historical count-only
V27/V41 child certificates or extend the fully split rational-polynomial
checker. An implicit root is identified only by its pinned original physical
source, proof family and strict rational uniqueness bracket.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

import verify_pb00701_v27_fixed_source_order as v27
import verify_pb00701_v41_v13_fixed_source_order as v41

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research/machining-completeness/tasks/MC-038"
CORPUS = TASK / "pb00701-finite-owner-corpus-v54.json"
DOMAIN = ROOT / "research/machining-completeness/tasks/MC-002/domain-contract-v1.json"
AUTH = ROOT / "handoffs/current-authority.json"
SCHEMA = "radicadsac-pb00701-pinned-trig-child-views/1.0"
DESCRIPTOR = "UNIQUE_IMPLICIT_ZERO_OF_PINNED_ORIGINAL_PHYSICAL_SOURCE"
V27_PROOF_BLOB = "006272b173a66bfb53cc4ddf0f5597857a42362b"
V41_PROOF_BLOB = "358dd4071ef968635bcd85f61dfa1965e51abda1"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
DOMAIN_BLOB = "23de82f5240a72509f7afe4acd5948b65bc4ff13"
AUTH_BLOB = "fa0233323a0804d8a5d3eb7cd892a274a6173fab"
CASES = (v27.TAIL0, v27.TAIL100, v41.SOURCE_ID)
MAX_PAYLOAD_BYTES = 16384


class InvalidView(ValueError):
    """Untrusted or contradicted child-view assertion, not a certification."""


def need(condition, reason):
    if not condition:
        raise InvalidView(reason)


def git_blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def canonical(obj):
    try:
        return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                          allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise InvalidView("non-JSON or nonfinite child-view value") from exc


def rational(s):
    need(type(s) is str and 0 < len(s) <= 128, "non-string/oversized rational")
    try:
        x = Q(s)
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise InvalidView("invalid rational") from exc
    need(str(x) == s, "noncanonical rational; floating root coordinates prohibited")
    return x


def source_binding(row):
    return hashlib.sha256(canonical({
        "case_id": row["id"], "kind": row["kind"],
        "origin": row["origin"], "spec": row["spec"],
        "expected": row["expected"],
    }).encode("ascii")).hexdigest()


def replay_original_proofs():
    """Full unchanged-source and authority checks before using a fixed proof."""
    for path, sha in (
        (CORPUS, CORPUS_BLOB), (DOMAIN, DOMAIN_BLOB), (AUTH, AUTH_BLOB),
        (TASK / "verify_pb00701_v27_fixed_source_order.py", V27_PROOF_BLOB),
        (TASK / "verify_pb00701_v41_v13_fixed_source_order.py", V41_PROOF_BLOB),
    ):
        need(git_blob(path) == sha, "frozen source, authority or proof-driver blob drift: " +
             path.name)
    first = v27.contract()
    second = v41.contract()
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    indexed = {row["id"]: row for row in corpus["cases"]}
    need(set(CASES) <= set(indexed), "original source records missing")
    need(first["first_span"]["simple_roots"] == 1 and
         first["shared_source_knot"] == {
             "s": "1", "relation": "NEGATIVE", "zero_event": False,
             "continuous": True},
         "V27 original-source span/knot proof changed")
    for tail in ("tail0", "tail100"):
        need(first[tail]["whole_source_open_roots"] == 2 and
             first[tail]["whole_source_signs"] == [
                 "POSITIVE", "NEGATIVE", "POSITIVE"],
             "V27 complete source-order proof changed")
    need(second["simple_open_roots"] == 2 and
         second["closed_endpoint_roots"] == 0 and
         second["sign_cells"] == ["NEGATIVE", "POSITIVE", "NEGATIVE"],
         "V41 exact interval proof changed")
    return first, second, indexed


def event(bracket, left, right):
    return {
        "descriptor": DESCRIPTOR, "strict_bracket": list(bracket),
        "smooth_physical_multiplicity": 1, "parity": "ODD_CROSSING",
        "left_sign": left, "right_sign": right,
    }


def reference_view(case_id, proofs):
    """Reconstruct only known original-source views from independently replayed proofs."""
    first, second, indexed = proofs
    need(case_id in CASES, "not a pinned original-source case")
    row = indexed[case_id]
    if case_id in (v27.TAIL0, v27.TAIL100):
        tail = "tail0" if case_id == v27.TAIL0 else "tail100"
        spans = [
            {"interval": ["0", "1"], "owner": v27.OWNER, "roots": [
                event(first["first_span"]["source_bracket"], "POSITIVE", "NEGATIVE")]},
            {"interval": ["1", "2"],
             "owner": v27.OWNER if tail == "tail0" else v27.V19,
             "roots": [event(first[tail]["source_bracket"], "NEGATIVE", "POSITIVE")]},
        ]
        knots = [{"position": "1", "left_sign": "NEGATIVE",
                  "right_sign": "NEGATIVE", "is_physical_zero": False}]
        cuts = ["3/4", "1", "9/8", "3/2"]
        proof_family = "REPLAYED_FIXED_V27_ANALYTIC_SECTORS"
    else:
        need(len(second["root_brackets"]) == 2,
             "V41 two distinct source-isolated roots not established")
        spans = [{"interval": ["0", "1"], "owner": v41.OWNER, "roots": [
            event(second["root_brackets"][0], "NEGATIVE", "POSITIVE"),
            event(second["root_brackets"][1], "POSITIVE", "NEGATIVE")]}]
        knots, cuts = [], ["3/20", "1/5", "4/5", "17/20"]
        proof_family = "REPLAYED_FIXED_V41_RATIONAL_INTERVAL_PROOF"
    return {
        "schema": SCHEMA, "source_case_id": case_id,
        "source_parameter_id": row["spec"]["source_parameter_id"],
        "original_source_binding_sha256": source_binding(row),
        "proof_family": proof_family, "children": spans,
        "true_source_knots": knots, "certificate_cuts": cuts,
    }


def nontruth(status, reason):
    return {"status": status, "reason": reason, "is_truth_value": False,
            "historical_child_certified": False, "production_authorized": False}


def compose(candidate):
    """Validate complete fixed-case views, then compose physical sign cells.

    The caller's counts, coordinates and event claims are NEVER authority.
    There is no arbitrary trigonometric child grammar or generic theorem.
    """
    packed = canonical(candidate)
    if len(packed) > MAX_PAYLOAD_BYTES:
        return nontruth("RESOURCE_REFUSAL", "PINNED_VIEW_PAYLOAD_BUDGET_EXCEEDED")
    need(type(candidate) is dict, "view must be a dictionary")
    case_id = candidate.get("source_case_id")
    if case_id not in CASES:
        return nontruth("BLOCKED", "UNSUPPORTED_ORIGINAL_TRIGONOMETRIC_SOURCE")
    proof_data = replay_original_proofs()
    expected = reference_view(case_id, proof_data)
    need(packed == canonical(expected),
         "child view disagrees with independently replayed pinned source/proof")
    spans = expected["children"]
    all_roots = []
    prior_end = None
    for child in spans:
        a, b = map(rational, child["interval"])
        need(a < b and (prior_end is None or prior_end == a),
             "physical source span gap/overlap")
        prior_end = b
        for root in child["roots"]:
            lo, hi = map(rational, root["strict_bracket"])
            need(a <= lo < hi <= b, "root bracket is not strictly inside its source")
            need(root["smooth_physical_multiplicity"] == 1 and
                 root["parity"] == "ODD_CROSSING" and
                 root["left_sign"] != root["right_sign"],
                 "a claimed simple crossing is not a crossing")
            if all_roots:
                need(rational(all_roots[-1]["strict_bracket"][1]) <= lo,
                     "ordered implicit brackets overlap or reverse")
                need(all_roots[-1]["right_sign"] == root["left_sign"],
                     "incompatible adjacent physical sign cells")
            all_roots.append(root)
    need(len(all_roots) == 2, "only two-root proof families are currently admissible")
    for knot in expected["true_source_knots"]:
        at = rational(knot["position"])
        need(any(rational(s["interval"][1]) == at for s in spans[:-1]),
             "claimed source knot not a true original-source knot")
        need(not knot["is_physical_zero"] and
             knot["left_sign"] == knot["right_sign"] == "NEGATIVE",
             "original-source knot sign/zero claim contradicted")
    # Cuts refine a proof; no cut by itself is a physical event.
    cuts = [rational(x) for x in expected["certificate_cuts"]]
    need(cuts == sorted(set(cuts)) and
         all(rational(spans[0]["interval"][0]) < x <
             rational(spans[-1]["interval"][1]) for x in cuts),
         "invalid proof cuts")
    signs = [all_roots[0]["left_sign"]] + [r["right_sign"] for r in all_roots]
    endpoints = ["ORIGINAL_SOURCE_START", "IMPLICIT_ROOT_1",
                 "IMPLICIT_ROOT_2", "ORIGINAL_SOURCE_END"]
    physical_cells = [
        {"left": endpoints[i], "right": endpoints[i + 1], "sign": signs[i]}
        for i in range(3)
    ]
    witnessed_events = []
    for child in spans:
        for root in child["roots"]:
            witnessed_events.append({
                "root_ref": f"IMPLICIT_ROOT_{len(witnessed_events)+1}",
                "source_case_id": case_id, "source_span": child["interval"], **root})
    return {
        "status": "PINNED_TRIGONOMETRIC_CHILD_VIEWS_RECONCILED_RESEARCH_ONLY",
        "schema": SCHEMA, "source_case_id": case_id,
        "source_binding_sha256": expected["original_source_binding_sha256"],
        "proof_family": expected["proof_family"],
        "ordered_implicit_root_events": witnessed_events,
        "maximal_open_physical_sign_cells": physical_cells,
        "true_source_knots": expected["true_source_knots"],
        "proof_cuts_not_physical_events": expected["certificate_cuts"],
        "distinct_open_roots_proved_for_this_fixed_source": 2,
        "exact_root_coordinates_claimed": False,
        "historical_v54_disposition_changed": False,
        "historical_child_certified": False,
        "general_v27_v41_theorem_claimed": False,
        "pb00701_certified": False, "mc_b_established": False,
        "mc1_established": False, "native_brep_or_step_qualified": False,
        "production_authorized": False,
    }
