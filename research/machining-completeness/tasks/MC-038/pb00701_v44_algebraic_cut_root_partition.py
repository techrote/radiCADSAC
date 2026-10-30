#!/usr/bin/env python3
"""MC-038/PB-007-01: frozen V44 proof-cut / physical-root partition research.

For one exact frozen single-span source, combine:
* historical V44 fail-closed boundary reproduction,
* #296 complete simple physical-root proof on the original rational source span,
* #306 exact ordered rational/algebraic proof-cut descriptors, and
* V46 exact nonzero physical value at the algebraic orientation cut.

The result partitions an already-proved physical root set across proof cells.
It does NOT certify algebraic child analytic functions, promote proof cuts to
events, rewrite historical v54 evidence, or establish PB-007-01/MC-B/native.
"""
from __future__ import annotations

import copy
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

import pb00701_algebraic_endpoint_model as v46
import pb00701_algebraic_monotone_cut_model as v47
import pb00701_algebraic_orientation_cut_model as v44
import pb00701_transverse_original_source as transverse
import pb00701_v41_algebraic_cut_order as cut_order

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research/machining-completeness/tasks/MC-038"
CORPUS = TASK / "pb00701-finite-owner-corpus-v54.json"
DOMAIN = ROOT / "research/machining-completeness/tasks/MC-002/domain-contract-v1.json"
AUTH = ROOT / "handoffs/current-authority.json"

SCHEMA = "radicadsac-pb00701-v44-algebraic-cut-root-partition/1.0"
CASE_ID = "harvested:verify_pb00701_v44:ffaea08e30c9"
MAX_REPORT_BYTES = 131072
MAX_CUT_REFINEMENTS = 256

PINS = {
    CORPUS: "5841c331579489b25caef38cd412bdbf286f9134",
    DOMAIN: "23de82f5240a72509f7afe4acd5948b65bc4ff13",
    AUTH: "fa0233323a0804d8a5d3eb7cd892a274a6173fab",
    TASK / "pb00701_transverse_original_source.py":
        "992ad17ddbdf34687bcb59acba46f672b2d4a1c4",
    TASK / "pb00701_transverse_trig_interval.py":
        "2320f92efe4316d865a89f6d848737e2c000ca4d",
    TASK / "pb00701_v41_algebraic_cut_order.py":
        "e15944ee0fd7819b818c8c556f2c079039d042b7",
    TASK / "pb00701_algebraic_orientation_cut_model.py":
        "a56d6487963d269405ab82f3db4cce58a0165520",
    TASK / "pb00701_algebraic_endpoint_model.py":
        "77c18cb5c8c0700072c65969c973e8f3c4c12a99",
    TASK / "pb00701_algebraic_monotone_cut_model.py":
        "07b092f9c7df8b3325c2b15d17ca7abe9781cb10",
}


class ResearchRefusal(ValueError):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


class ResourceRefusal(RuntimeError):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def require(ok, reason):
    if not ok:
        raise ResearchRefusal(reason)


def git_blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    ).hexdigest()


def canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ResearchRefusal("NONCANONICAL_OR_NONJSON_EVIDENCE") from exc


def pins():
    for path, expected in PINS.items():
        require(git_blob(path) == expected,
                "PINNED_SOURCE_DRIFT:" + path.name)
    transverse.custody()
    cut_order.pins()
    auth = json.loads(AUTH.read_text())
    domain = json.loads(DOMAIN.read_text())
    require(auth["capability_status"] == "NOT_ESTABLISHED" and
            auth["production_authorized"] is False,
            "AUTHORITY_PROMOTION_DETECTED")
    require(len(domain["coverage_rule"]["required_operation_ids"]) == 26,
            "MACHINING_DOMAIN_DENOMINATOR_DRIFT")


def frozen_row():
    corpus = json.loads(CORPUS.read_text())
    require(corpus.get("schema") ==
            "radicadsac-pb00701-finite-owner-corpus/54.0",
            "FROZEN_CORPUS_SCHEMA_DRIFT")
    rows = [row for row in corpus.get("cases", []) if row.get("id") == CASE_ID]
    require(len(rows) == 1, "FROZEN_V44_CASE_CARDINALITY_DRIFT")
    row = rows[0]
    expected = row.get("expected", {})
    spans = expected.get("observed", {}).get("spans", [])
    require(row.get("origin") == "verify_pb00701_v44" and
            row.get("kind") == "HARVESTED" and
            expected.get("v54_disposition") == "BLOCKED" and
            expected.get("observed", {}).get("status") == "BLOCKED" and
            spans == [[
                "PB00701_V44_EXACT_REAL_ALGEBRAIC_ORIENTATION_CUT_BOUNDARY",
                "BLOCKED",
                "ALGEBRAIC_ORIENTATION_COORDINATE_CERTIFIED_BUT_EXACT_CONSUMPTION_AUTHORITY_MISSING",
            ]],
            "FROZEN_V44_HISTORICAL_DISPOSITION_DRIFT")
    return row


def source_sha256(spec):
    return hashlib.sha256(canonical(spec).encode("ascii")).hexdigest()


def _historical_boundary(spec):
    result = v44.classify_required_analytic_event(spec)
    require(result.get("status") == "BLOCKED",
            "CURRENT_V44_NO_LONGER_REPRODUCES_BLOCKER")
    spans = result.get("spans", [])
    require(len(spans) == 1, "CURRENT_V44_SPAN_CARDINALITY_CHANGED")
    route = spans[0].get("route", {})
    require(
        spans[0].get("route_kind") ==
        "PB00701_V44_EXACT_REAL_ALGEBRAIC_ORIENTATION_CUT_BOUNDARY"
        and route.get("status") == "BLOCKED"
        and route.get("reason") ==
        "ALGEBRAIC_ORIENTATION_COORDINATE_CERTIFIED_BUT_EXACT_CONSUMPTION_AUTHORITY_MISSING",
        "CURRENT_V44_BLOCKER_IDENTITY_CHANGED",
    )
    return result


def _physical_root_proof(row, *, max_depth=14, max_nodes=20000):
    require(type(max_depth) is int and 0 <= max_depth <= 18 and
            type(max_nodes) is int and 1 <= max_nodes <= 20000,
            "INVALID_PHYSICAL_ROOT_RESOURCE_BUDGET")
    lowerer = transverse.v27.exact_lowerer()
    views = transverse.original_spans(row, lowerer)
    require(len(views) == 1 and views[0]["interval"] == (Q(0), Q(1)),
            "FROZEN_V44_NOT_ONE_RATIONAL_SOURCE_SPAN")
    span = views[0]["span"]
    try:
        proof = span.prove(max_depth=max_depth, max_nodes=max_nodes,
                           bracket_width=Q(1, 64))
    except transverse.trig.Refusal as exc:
        reason = str(exc)
        if "RESOURCE" in reason or "NODE" in reason or "UNDECIDED" in reason:
            raise ResourceRefusal(reason) from exc
        raise ResearchRefusal(reason) from exc
    roots = []
    for cell in proof["partition"]:
        if cell["kind"] != "ONE_SIMPLE_ROOT":
            continue
        roots.append({
            "cell_interval": copy.deepcopy(cell["interval"]),
            "strict_isolation": copy.deepcopy(cell["strict_isolation"]),
            "derivative_sign": int(cell["derivative_sign"]),
            "left_sign": int(cell["left_sign"]),
            "right_sign": int(cell["right_sign"]),
            "smooth_multiplicity": int(cell["smooth_multiplicity"]),
        })
    require(len(roots) == proof["complete_simple_root_count"],
            "PHYSICAL_ROOT_PARTITION_COUNT_MISMATCH")
    require(len(roots) == 1 and roots[0]["smooth_multiplicity"] == 1,
            "FROZEN_V44_COMPLETE_ONE_SIMPLE_ROOT_NOT_ESTABLISHED")
    return span, proof, roots


def _algebraic_endpoint(spec):
    result = v46.decide_required_event_endpoints(spec)
    require(result.get("status") == "ENDPOINTS_CERTIFIED",
            "V46_ALGEBRAIC_ENDPOINT_NOT_CERTIFIED")
    rows = result.get("span_endpoint_evidence", [])
    require(len(rows) == 1, "V46_SPAN_ENDPOINT_CARDINALITY_CHANGED")
    endpoints = rows[0].get("endpoint_evidence", {}).get("endpoints", [])
    require(len(endpoints) == 1, "FROZEN_V44_EXPECTED_ONE_ALGEBRAIC_ENDPOINT")
    endpoint = endpoints[0]
    require(endpoint.get("status") == "ENDPOINT_CERTIFIED" and
            endpoint.get("relation") in ("POSITIVE", "NEGATIVE") and
            endpoint.get("physical_multiplicity") == 0 and
            endpoint.get("whole_span_certified") is False,
            "ALGEBRAIC_PROOF_CUT_NOT_PROVED_PHYSICAL_NONROOT")
    return result, endpoint


def _cut_sign_at_rational(span, value):
    enclosure = span.evaluate(value)
    sign = transverse.trig.strict_sign(enclosure)
    require(sign in (-1, 1), "RATIONAL_PROOF_CUT_VALUE_ZERO_OR_UNRESOLVED")
    return sign


def _coord_bounds(coord):
    kind = coord.get("kind")
    if kind in ("RATIONAL_ROOT", "RATIONAL_PROOF_CUT"):
        value = cut_order.q(coord["local_value"])
        return value, value
    require(kind == "ISOLATED_REAL_ROOT",
            "UNKNOWN_PROOF_CUT_COORDINATE_KIND")
    lo, hi = map(cut_order.q, coord["local_isolating_interval"])
    require(Q(0) < lo < hi < Q(1), "INVALID_ALGEBRAIC_PROOF_CUT_INTERVAL")
    return lo, hi


def _relation_to_root(coord, root, span, algebraic_endpoint, *,
                      max_cut_refinements):
    require(type(max_cut_refinements) is int and
            0 <= max_cut_refinements <= MAX_CUT_REFINEMENTS,
            "INVALID_CUT_REFINEMENT_BUDGET")
    root_lo, root_hi = map(Q, root["strict_isolation"])
    cell_lo, cell_hi = map(Q, root["cell_interval"])
    current = copy.deepcopy(coord)
    refinements = 0
    while True:
        lo, hi = _coord_bounds(current)
        if hi <= root_lo:
            relation = "CUT_BEFORE_PHYSICAL_ROOT"
            break
        if lo >= root_hi:
            relation = "PHYSICAL_ROOT_BEFORE_CUT"
            break

        kind = current["kind"]
        if kind in ("RATIONAL_ROOT", "RATIONAL_PROOF_CUT"):
            value = cut_order.q(current["local_value"])
            require(cell_lo <= value <= cell_hi,
                    "OVERLAPPING_RATIONAL_CUT_OUTSIDE_ROOT_PROOF_CELL")
            sign = _cut_sign_at_rational(span, value)
            if sign == root["left_sign"]:
                relation = "CUT_BEFORE_PHYSICAL_ROOT"
            elif sign == root["right_sign"]:
                relation = "PHYSICAL_ROOT_BEFORE_CUT"
            else:
                raise ResearchRefusal("RATIONAL_CUT_SIGN_NOT_COMPATIBLE_WITH_SIMPLE_ROOT")
            break

        # Algebraic cuts may be refined exactly by the #306 Sturm descriptor.
        # If the whole descriptor is already inside the one-root monotone cell,
        # the independently certified physical sign at alpha also orders it.
        endpoint_sign = 1 if algebraic_endpoint["relation"] == "POSITIVE" else -1
        if cell_lo < lo and hi < cell_hi:
            if endpoint_sign == root["left_sign"]:
                relation = "CUT_BEFORE_PHYSICAL_ROOT"
                break
            if endpoint_sign == root["right_sign"]:
                relation = "PHYSICAL_ROOT_BEFORE_CUT"
                break
            raise ResearchRefusal("ALGEBRAIC_CUT_SIGN_NOT_COMPATIBLE_WITH_SIMPLE_ROOT")
        if refinements >= max_cut_refinements:
            raise ResourceRefusal("ALGEBRAIC_CUT_VS_PHYSICAL_ROOT_REFINEMENT_EXHAUSTED")
        try:
            budget = cut_order.ComparisonBudget(1)
            current = cut_order._refine(current, budget, Q(0), Q(1))
        except cut_order.ResearchRefusal as exc:
            raise ResearchRefusal(str(exc)) from exc
        except cut_order.ResourceRefusal as exc:
            raise ResourceRefusal(str(exc)) from exc
        refinements += 1

    expected_sign = (
        root["left_sign"] if relation == "CUT_BEFORE_PHYSICAL_ROOT"
        else root["right_sign"]
    )
    if current["kind"] in ("RATIONAL_ROOT", "RATIONAL_PROOF_CUT"):
        sign = _cut_sign_at_rational(
            span, cut_order.q(current["local_value"])
        )
    else:
        sign = 1 if algebraic_endpoint["relation"] == "POSITIVE" else -1
    require(sign == expected_sign,
            "PROOF_CUT_PHYSICAL_SIGN_DISAGREES_WITH_ROOT_ORDER")
    return relation, current, refinements, sign


def prove(*, max_depth=14, max_nodes=20000, max_cut_refinements=128):
    pins()
    row = frozen_row()
    spec = copy.deepcopy(row["spec"])
    historical = _historical_boundary(spec)

    # V47 is intentionally a sufficient derivative-family route; this exact
    # historical source must not be silently reclassified as its witness.
    current_v47 = v47.classify_required_analytic_event(spec)
    require(current_v47.get("status") != "CERTIFIED",
            "FROZEN_V44_SOURCE_UNEXPECTEDLY_OWNED_BY_V47")

    span, physical, roots = _physical_root_proof(
        row, max_depth=max_depth, max_nodes=max_nodes
    )
    ordered = cut_order.source_bound_view(spec)
    require(
        ordered.get("status") ==
        "EXACT_SOURCE_BOUND_V41_IMPLICIT_PROOF_CUT_ORDER_RESEARCH",
        "V41_ALGEBRAIC_PROOF_CUT_ORDER_NOT_ESTABLISHED",
    )
    endpoint_report, endpoint = _algebraic_endpoint(spec)
    irrational = [
        cut for cut in ordered["ordered_proof_cuts"]
        if cut["coordinate"]["kind"] == "ISOLATED_REAL_ROOT"
    ]
    require(len(irrational) == 1,
            "FROZEN_V44_EXPECTED_ONE_ALGEBRAIC_ORIENTATION_CUT")
    defining = tuple(map(cut_order.q,
                         irrational[0]["coordinate"]["defining_square_free_polynomial"]))
    endpoint_poly = tuple(map(cut_order.q, endpoint["field"]["minimal_polynomial"]))
    require(defining == endpoint_poly,
            "V46_ENDPOINT_AND_V41_CUT_MINIMAL_POLYNOMIAL_MISMATCH")

    root = roots[0]
    relations = []
    seen_after = False
    before_count = 0
    total_refinements = 0
    for cut in ordered["ordered_proof_cuts"]:
        relation, refined, used, sign = _relation_to_root(
            cut["coordinate"], root, span, endpoint,
            max_cut_refinements=max_cut_refinements-total_refinements,
        )
        total_refinements += used
        if relation == "CUT_BEFORE_PHYSICAL_ROOT":
            require(not seen_after,
                    "ORDERED_PROOF_CUTS_CROSS_PHYSICAL_ROOT_MORE_THAN_ONCE")
            before_count += 1
        else:
            seen_after = True
        relations.append({
            "proof_cut_index": cut["index"],
            "coordinate": refined,
            "relation_to_physical_root": relation,
            "physical_value_sign": sign,
            "causes": copy.deepcopy(cut["causes"]),
            "proof_cut_is_physical_event": False,
        })

    cell_counts = [0] * (len(relations) + 1)
    cell_counts[before_count] = 1
    require(sum(cell_counts) == physical["complete_simple_root_count"] == 1,
            "PROOF_CELL_ROOT_COUNT_CONSERVATION_FAILED")

    pins()
    return {
        "schema": SCHEMA,
        "status": "EXACT_FROZEN_V44_PROOF_CUT_ROOT_SET_PARTITION_RESEARCH",
        "evidence_class": "DETERMINISTIC_MODEL",
        "frozen_case_id": CASE_ID,
        "source_sha256": source_sha256(spec),
        "source_parameter_id": spec["source_parameter_id"],
        "source_interval": [spec["parameter_lo"], spec["parameter_hi"]],
        "phase_turn_law": {
            "offset": spec["phase_turn_offset"],
            "rate": spec["phase_turn_rate"],
        },
        "historical_v54_disposition": row["expected"]["v54_disposition"],
        "historical_v44_blocker":
            historical["spans"][0]["route"]["reason"],
        "v47_still_certifies_this_frozen_source": False,
        "complete_physical_root_count":
            physical["complete_simple_root_count"],
        "physical_endpoint_signs": physical["endpoint_signs"],
        "physical_root": copy.deepcopy(root),
        "physical_partition_nodes": physical["nodes"],
        "ordered_proof_cut_count": len(relations),
        "proof_cut_relations": relations,
        "proof_cell_open_root_counts": cell_counts,
        "root_occupying_proof_cell_index": before_count,
        "algebraic_cut_endpoint_relation": endpoint["relation"],
        "algebraic_cut_physical_multiplicity":
            endpoint["physical_multiplicity"],
        "algebraic_cut_is_physical_event": False,
        "all_proof_cuts_are_event_neutral": True,
        "cut_vs_root_refinements_used": total_refinements,
        "root_count_conserved_across_proof_cells": True,
        "algebraic_child_reparameterization_claimed": False,
        "closed_child_derivative_theorem_claimed": False,
        "historical_v54_admitted": False,
        "historical_v54_dispositions_changed": False,
        "pb00701_certified": False,
        "mc_b_established": False,
        "mc1_established": False,
        "native_brep_or_step_qualified": False,
        "production_authorized": False,
        "source_bound_cut_order_evidence": {
            "source_sha256": ordered["source_sha256"],
            "current_v41_boundary": ordered["current_v41_boundary"],
            "ordered_cut_count": len(ordered["ordered_proof_cuts"]),
            "orientation_roots_are_proof_geometry_only":
                ordered["orientation_roots_are_proof_geometry_only"],
        },
        "v46_endpoint_evidence_status": endpoint_report["status"],
    }


def nontruth(reason, status="BLOCKED"):
    return {
        "schema": SCHEMA,
        "status": status,
        "reason": reason,
        "is_truth_value": False,
        "historical_v54_admitted": False,
        "pb00701_certified": False,
        "mc_b_established": False,
        "production_authorized": False,
    }


def attempt(**budgets):
    try:
        return prove(**budgets)
    except ResourceRefusal as exc:
        return nontruth(exc.reason, "RESOURCE_REFUSAL")
    except (ResearchRefusal, cut_order.ResearchRefusal,
            transverse.InvalidOriginal, ValueError, KeyError, IndexError,
            TypeError, ZeroDivisionError, AssertionError) as exc:
        reason = str(exc)
        status = (
            "RESOURCE_REFUSAL"
            if any(tag in reason for tag in
                   ("RESOURCE", "EXHAUSTED", "UNDECIDED", "LIMIT"))
            else "BLOCKED"
        )
        return nontruth(reason, status)
    except (MemoryError, RecursionError, OverflowError) as exc:
        return nontruth(type(exc).__name__, "RESOURCE_REFUSAL")


def validate_report(submitted, **budgets):
    try:
        claimed = canonical(submitted)
        if len(claimed) > MAX_REPORT_BYTES:
            return nontruth("SUBMITTED_REPORT_RESOURCE_LIMIT",
                            "RESOURCE_REFUSAL")
        checked = attempt(**budgets)
        require(
            checked.get("status") ==
            "EXACT_FROZEN_V44_PROOF_CUT_ROOT_SET_PARTITION_RESEARCH",
            "EXACT_FROZEN_V44_PARTITION_PROOF_MISSING",
        )
        require(claimed == canonical(checked),
                "FORGED_V44_PROOF_CUT_ROOT_PARTITION_REPORT")
        return checked
    except ResearchRefusal as exc:
        return nontruth(exc.reason)
    except (ValueError, TypeError, OverflowError) as exc:
        return nontruth(str(exc))
