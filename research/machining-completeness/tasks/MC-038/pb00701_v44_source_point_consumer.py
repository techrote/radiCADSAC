#!/usr/bin/env python3
"""Frozen V44: exact rational original-source point consumer of the #311 atlas.

A bounded research consumer, not a V41/V47 algebraic analytic child chart.
The independent #298 cyclotomic point jet decides physical value/event truth.
The source-replayed #311 atlas supplies exact proof-cut position and cell scope.
"""
from __future__ import annotations

import copy
from fractions import Fraction as Q

import pb00701_rational_phase_point as jets
import pb00701_v44_source_proof_cell_atlas as atlas

SCHEMA = "radicadsac-pb00701-v44-source-point-consumer/1.0"
REQUEST_SCHEMA = "radicadsac-pb00701-v44-exact-source-point-request/1.0"
SUCCESS = "EXACT_FROZEN_V44_SOURCE_RATIONAL_POINT_CONSUMED_RESEARCH"
ATLAS_BLOB = "2028684883f78ceed14ce92865810ef11409b7eb"
POINT_BLOB = "9fc344e045fa800fb24d30902a641e534a1e197b"
MAX_COORDINATE_BYTES = 128
MAX_CUT_COMPARISONS = 96


class Refusal(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise Refusal(reason)


def pins():
    previous = atlas.previous
    require(previous.git_blob(previous.TASK /
            "pb00701_v44_source_proof_cell_atlas.py") == ATLAS_BLOB,
            "PINNED_REPLAYED_ATLAS_SOURCE_DRIFT")
    require(previous.git_blob(previous.TASK /
            "pb00701_rational_phase_point.py") == POINT_BLOB,
            "PINNED_INDEPENDENT_RATIONAL_POINT_JET_DRIFT")
    atlas.pins()


def coordinate(value):
    """Canonical exact rational source coordinate; reject floats and aliases."""
    require(type(value) is str and 0 < len(value) <= MAX_COORDINATE_BYTES,
            "NONCANONICAL_OR_OVERSIZED_SOURCE_COORDINATE")
    try:
        x = Q(value)
    except (ValueError, TypeError, ZeroDivisionError, OverflowError) as exc:
        raise Refusal("INVALID_EXACT_RATIONAL_SOURCE_COORDINATE") from exc
    require(str(x) == value and Q(0) <= x <= Q(1),
            "NONCANONICAL_OR_OUTSIDE_SOURCE_COORDINATE")
    return x


def request_for(value):
    """Construct one typed *request*, not a trusted source certificate."""
    return {
        "schema": REQUEST_SCHEMA,
        "requested_capability": "EXACT_ORIGINAL_SOURCE_RATIONAL_POINT",
        "frozen_case_id": atlas.previous.CASE_ID,
        "source_sha256": atlas.SOURCE_SHA256,
        "source_parameter_id": "pb00701-v44-algebraic-orientation",
        "source_coordinate": value,
    }


def _validate_request(request):
    require(type(request) is dict and set(request) == {
        "schema", "requested_capability", "frozen_case_id",
        "source_sha256", "source_parameter_id", "source_coordinate",
    }, "REQUEST_SHAPE_NOT_EXACTLY_SOURCE_BOUND")
    require(request["schema"] == REQUEST_SCHEMA
            and request["requested_capability"] ==
            "EXACT_ORIGINAL_SOURCE_RATIONAL_POINT",
            "ANALYTIC_CHILD_OR_UNSUPPORTED_CONSUMER_CAPABILITY")
    require(request["frozen_case_id"] == atlas.previous.CASE_ID
            and request["source_sha256"] == atlas.SOURCE_SHA256
            and request["source_parameter_id"] ==
            "pb00701-v44-algebraic-orientation",
            "POINT_REQUEST_SOURCE_IDENTITY_MISMATCH")
    return coordinate(request["source_coordinate"])


def _validated_atlas(supplied):
    if supplied is None:
        view = atlas.prove()
    else:
        view = atlas.validate_report(supplied)
    require(view.get("status") == atlas.SUCCESS
            and view.get("parent_source_sha256") == atlas.SOURCE_SHA256
            and view.get("source_coordinate_restrictions_only") is True
            and view.get("actual_algebraic_child_analytic_chart_constructed")
            is False
            and view.get("closed_child_derivative_theorem_proved") is False
            and view.get("v41_v47_historical_child_route_certified") is False
            and view.get("historical_v54_admitted") is False
            and view.get("mc_b_established") is False
            and view.get("production_authorized") is False,
            "FROZEN_SOURCE_ATLAS_NOT_EXACTLY_REPLAY_VERIFIED")
    require(len(view["proof_boundaries"]) == 5
            and len(view["source_proof_cells"]) == 4
            and view["complete_original_source_physical_root_count"] == 1
            and view["one_physical_root_cell_index"] == 1,
            "FROZEN_PROOF_CELL_ATLAS_CARDINALITY_CHANGED")
    return view


def _locate_rational_point(view, x):
    """Order exact rational query against EVERY source-owned proof cut."""
    if x == 0:
        return {"kind": "ORIGINAL_SOURCE_ENDPOINT",
                "boundary_index": 0, "comparison_methods": []}
    if x == 1:
        return {"kind": "ORIGINAL_SOURCE_ENDPOINT",
                "boundary_index": 4, "comparison_methods": []}

    requested = {"kind": "RATIONAL_PROOF_CUT", "local_value": str(x)}
    cut_order = atlas.previous.cut_order
    methods, n_before, equal, seen_after = [], 0, None, False
    for i, boundary in enumerate(view["proof_boundaries"][1:-1], 1):
        budget = cut_order.ComparisonBudget(MAX_CUT_COMPARISONS)
        rel, method, _, _ = cut_order.compare_coordinates(
            boundary["coordinate_descriptor"], requested, budget, Q(0), Q(1),
        )
        require(rel in ("LEFT_BEFORE_RIGHT", "RIGHT_BEFORE_LEFT", "EQUAL"),
                "UNDECIDED_EXACT_SOURCE_POINT_CUT_ORDER")
        methods.append(method)
        if rel == "LEFT_BEFORE_RIGHT":
            require(not seen_after and equal is None,
                    "POINT_CUT_ORDER_NOT_STRICTLY_CONSISTENT")
            n_before += 1
        elif rel == "RIGHT_BEFORE_LEFT":
            seen_after = True
        else:
            require(equal is None, "DUPLICATE_EXACT_PROOF_CUT_POINT")
            equal = i
            seen_after = True
    if equal is not None:
        require(n_before == equal-1, "POINT_CUT_EQUALITY_ORDER_MISMATCH")
        return {"kind": "EXACT_NONPHYSICAL_SOURCE_PROOF_CUT",
                "boundary_index": equal, "comparison_methods": methods}
    require(n_before in range(4), "POINT_NOT_IN_SOURCE_PROOF_PARTITION")
    return {"kind": "ORIGINAL_SOURCE_OPEN_PROOF_CELL",
            "cell_index": n_before, "comparison_methods": methods}


def _point_evidence(x, view, location):
    # The span is REBUILT from the complete independently pinned frozen source;
    # never reconstructed from the caller's atlas or a supplied child chart.
    span, _, roots = atlas.previous._physical_root_proof(
        atlas.previous.frozen_row()
    )
    require(len(roots) == 1
            and roots[0] == view["source_proof_cells"][
                view["one_physical_root_cell_index"]
            ]["one_simple_physical_root_witness"],
            "ATLAS_AND_INDEPENDENT_ORIGINAL_SOURCE_ROOT_DRIFT")
    point = jets.point(span, x)
    require(point.get("status") in (
        "EXACT_NONZERO_RATIONAL_POINT", "EXACT_RATIONAL_POINT_EVENT"
    ) and point.get("coordinate") == str(x)
            and point.get("source_binding_sha256") == jets.span_binding(span)
            and point.get("phase_turn") ==
            str(span.offset + span.rate * x)
            and point.get("exact_zero_decision") ==
            "ROOT_OF_UNITY_AND_PI_TRANSCENDENCE"
            and point.get("historical_v54_admitted") is False
            and point.get("complete_open_roots_claimed") is False,
            "INDEPENDENT_EXACT_POINT_JET_NOT_SOURCE_BOUND")

    zero = point["status"] == "EXACT_RATIONAL_POINT_EVENT"
    if location["kind"] != "ORIGINAL_SOURCE_OPEN_PROOF_CELL":
        boundary = view["proof_boundaries"][location["boundary_index"]]
        require(not zero and boundary["is_physical_zero"] is False
                and atlas.name(point["value_sign"]) ==
                boundary["physical_value_sign"],
                "PHYSICAL_PROOF_BOUNDARY_POINT_SIGN_OR_EVENT_CONTRADICTION")
    else:
        cell = view["source_proof_cells"][location["cell_index"]]
        if cell["physical_open_root_count"] == 0:
            require(not zero and cell["kind"] ==
                    "EXACT_SOURCE_ROOT_FREE_SIGN_CELL"
                    and atlas.name(point["value_sign"]) ==
                    cell["root_free_constant_sign"],
                    "ROOT_FREE_SOURCE_CELL_POINT_SIGN_OR_EVENT_CONTRADICTION")
        else:
            require(location["cell_index"] ==
                    view["one_physical_root_cell_index"]
                    and cell["kind"] == "EXACT_SOURCE_ONE_SIMPLE_ROOT_CELL",
                    "POINT_IN_UNCERTIFIED_PHYSICAL_ROOT_CELL")
            witness = cell["one_simple_physical_root_witness"]
            rlo, rhi = map(Q, witness["strict_isolation"])
            if zero:
                require(rlo < x < rhi
                        and point["one_sided_order"] == 1
                        and point["event_kind"] == "CROSSING"
                        and point["left_sign"] == witness["left_sign"]
                        and point["right_sign"] == witness["right_sign"]
                        and point["first_nonzero_derivative_sign"] ==
                        witness["derivative_sign"],
                        "RATIONAL_POINT_EVENT_CONTRADICTS_COMPLETE_ROOT_PROOF")
            elif x <= rlo:
                require(point["value_sign"] == witness["left_sign"],
                        "POINT_LEFT_OF_ROOT_HAS_INCONSISTENT_SIGN")
            elif x >= rhi:
                require(point["value_sign"] == witness["right_sign"],
                        "POINT_RIGHT_OF_ROOT_HAS_INCONSISTENT_SIGN")
            # A nonzero rational point INSIDE the proven isolating bracket
            # has an exact jet sign; its side of the root is NOT fabricated
            # from bracket overlap, approximate comparison or sampling.
    return point


def consume(request, supplied_atlas=None):
    """One original-source point query, with no historical-route promotion."""
    pins()
    x = _validate_request(request)
    view = _validated_atlas(supplied_atlas)
    location = _locate_rational_point(view, x)
    point = _point_evidence(x, view, location)
    return {
        "schema": SCHEMA,
        "status": SUCCESS,
        "evidence_class": "DETERMINISTIC_MODEL",
        "frozen_case_id": atlas.previous.CASE_ID,
        "source_sha256": atlas.SOURCE_SHA256,
        "source_parameter_id": view["source_parameter_id"],
        "source_coordinate": str(x),
        "original_source_interval": copy.deepcopy(
            view["original_source_interval"]),
        "original_affine_phase": copy.deepcopy(
            view["original_affine_phase"]),
        "point_location": location,
        "exact_point_evidence": point,
        "physical_point_is_zero":
            point["status"] == "EXACT_RATIONAL_POINT_EVENT",
        "physical_point_sign": (
            None if point["status"] == "EXACT_RATIONAL_POINT_EVENT"
            else atlas.name(point["value_sign"])
        ),
        "root_set_complete_for_original_source":
            view["complete_original_source_physical_root_count"] == 1,
        "proof_cuts_are_physical_events": False,
        "source_coordinate_point_query_only": True,
        "algebraic_child_analytic_chart_constructed": False,
        "closed_child_derivative_theorem_proved": False,
        "historical_v41_v47_route_certified": False,
        "historical_v54_disposition": "BLOCKED",
        "historical_v54_admitted": False,
        "pb00701_certified": False,
        "mc_b_established": False,
        "mc1_established": False,
        "native_material_or_step_qualified": False,
        "production_authorized": False,
    }


def nontruth(reason, status="BLOCKED"):
    return {
        "schema": SCHEMA, "status": status,
        "reason": str(reason), "is_truth_value": False,
        "historical_v54_admitted": False, "pb00701_certified": False,
        "mc_b_established": False, "mc1_established": False,
        "production_authorized": False,
    }


def attempt(request, supplied_atlas=None):
    try:
        return consume(request, supplied_atlas)
    except (atlas.previous.ResourceRefusal,
            atlas.previous.cut_order.ResourceRefusal,
            MemoryError, RecursionError, OverflowError) as exc:
        return nontruth(str(exc), "RESOURCE_REFUSAL")
    except (jets.Refusal, Refusal, atlas.Refusal,
            atlas.previous.ResearchRefusal,
            atlas.previous.cut_order.ResearchRefusal,
            ValueError, TypeError, KeyError, IndexError,
            ZeroDivisionError, AssertionError) as exc:
        reason = str(exc)
        status = ("RESOURCE_REFUSAL" if any(
            token in reason for token in
            ("RESOURCE", "LIMIT", "EXHAUSTED", "UNDECIDED")
        ) else "BLOCKED")
        return nontruth(reason, status)


def validate_report(request, submitted, supplied_atlas=None):
    try:
        claimed = atlas.previous.canonical(submitted)
        require(len(claimed) <= atlas.MAX_REPORT_BYTES,
                "SUBMITTED_POINT_CONSUMER_REPORT_TOO_LARGE")
        checked = attempt(request, supplied_atlas)
        require(checked.get("status") == SUCCESS,
                "SOURCE_POINT_CONSUMER_PROOF_NOT_ESTABLISHED")
        require(claimed == atlas.previous.canonical(checked),
                "FORGED_SOURCE_POINT_CONSUMER_REPORT")
        return checked
    except (Refusal, atlas.previous.ResearchRefusal, ValueError,
            TypeError, OverflowError) as exc:
        return nontruth(str(exc))
