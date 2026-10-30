#!/usr/bin/env python3
"""Frozen V44 source derivative -> actual V45 Q(alpha) split (research only).

This is a source-coordinate restriction proof, not a new analytic Q(alpha)
trigonometric zero solver or authority to consume historical V41/V47 routes.
All source/field/phase/physical-event facts are replayed from pinned producers.
"""
from __future__ import annotations

import copy
from fractions import Fraction as Q

import pb00701_algebraic_child_map_model as v45
import pb00701_v44_global_derivative as derivative

predecessor = derivative.predecessor
atlas = derivative.atlas
previous = derivative.previous
cut_order = previous.cut_order

SCHEMA = "radicadsac-pb00701-v44-v45-monotone-child-bridge/1.0"
SUCCESS = "EXACT_FROZEN_V44_V45_SINGLE_CUT_MONOTONIC_RESTRICTION_RESEARCH"
V45_BLOB = "c055e7f392a921b386a1a99cc70b5004121ae7f6"
DERIVATIVE_BLOB = "2c1282de6b0a03088b1cbd86c62d43b192301d20"
MAX_REPORT_BYTES = 65536


class Refusal(ValueError):
    pass


class ResourceRefusal(RuntimeError):
    pass


def require(test, reason):
    if not test:
        raise Refusal(reason)


def pins():
    require(previous.git_blob(previous.TASK /
            "pb00701_algebraic_child_map_model.py") == V45_BLOB,
            "PINNED_HISTORICAL_V45_SOURCE_DRIFT")
    require(previous.git_blob(previous.TASK /
            "pb00701_v44_global_derivative.py") == DERIVATIVE_BLOB,
            "PINNED_FROZEN_GLOBAL_DERIVATIVE_SOURCE_DRIFT")
    derivative.pins()


def _source_material(span, view):
    cos = {h: list(polys[0]) for h, polys in span.terms.items()}
    sin = {h: list(polys[1]) for h, polys in span.terms.items()}
    return v45._material(cos, sin, view["source_parameter_id"],
                         (span.left, span.right), span.offset, span.rate)


def _field(record):
    require(type(record) is dict and set(record) == {
        "minimal_polynomial", "isolating_interval",
        "root_index_in_open_unit_interval", "authority",
    }, "INVALID_V45_FIELD_RECORD_SHAPE")
    require(record["authority"] ==
            "FINITE_EXACT_KRONECKER_FACTORIZATION_AND_MC032_STURM",
            "V45_FIELD_AUTHORITY_DRIFT")
    field = v45.RealField(
        tuple(record["minimal_polynomial"]),
        tuple(Q(x) for x in record["isolating_interval"]),
        record["root_index_in_open_unit_interval"],
    )
    require(field.record() == record, "V45_FIELD_RECORD_NOT_CANONICAL")
    return field


def _exact_alpha_boundary(view, field):
    descriptor = {
        "kind": "ISOLATED_REAL_ROOT",
        "local_isolating_interval": [str(x) for x in field.interval],
        "source_isolating_interval": [str(x) for x in field.interval],
        "defining_square_free_polynomial": [
            str(x) for x in field.minimal
        ],
        "minimal_polynomial_claimed": True,
    }
    candidates = [
        (i, b) for i, b in enumerate(view["proof_boundaries"])
        if b.get("coordinate_descriptor", {}).get("kind") ==
        "ISOLATED_REAL_ROOT"
    ]
    require(len(candidates) == 1,
            "FROZEN_ORIGINAL_SOURCE_ALGEBRAIC_CUT_NOT_UNIQUE")
    index, boundary = candidates[0]
    budget = cut_order.ComparisonBudget(128)
    relation, method, _, _ = cut_order.compare_coordinates(
        boundary["coordinate_descriptor"], descriptor, budget, Q(0), Q(1)
    )
    require(relation == "EQUAL" and method ==
            "EXACT_POLYNOMIAL_GCD_PLUS_STURM_COMMON_ROOT",
            "V45_FIELD_ALPHA_NOT_EXACTLY_SOURCE_V41_V46_CUT")
    require(boundary["is_physical_zero"] is False
            and boundary["is_proof_geometry_only"] is True
            and boundary["physical_value_sign"] in ("POSITIVE", "NEGATIVE"),
            "V45_ALPHA_NOT_A_PROVED_NONZERO_EVENT_NEUTRAL_CUT")
    require(0 < index < len(view["proof_boundaries"]) - 1,
            "V45_CUT_OUTSIDE_ORIGINAL_SOURCE_INTERIOR")
    return index, boundary, method


def _check_children(rep, field, span):
    require(rep.get("status") == "REPRESENTATION_CERTIFIED"
            and rep.get("coverage") ==
            "EXACT_SINGLE_CUT_BISECTION_OF_PARENT_NO_GAP_OR_OVERLAP"
            and rep.get("analytic_cut_consumed") is False
            and rep.get("physical_event_inferred_from_orientation_root")
            is False
            and rep.get("internal_phase_kind") ==
            "ALGEBRAIC_IRRATIONAL"
            and rep.get("endpoint_event_authority") == v45.ENDPOINT_BLOCKER,
            "V45_HISTORICAL_REPRESENTATION_BOUNDARY_PROMOTED")
    children = rep.get("children")
    require(type(children) is list and len(children) == 2,
            "V45_SINGLE_CUT_NOT_TWO_CHILDREN")
    alpha = field.element([0, 1])
    zero, one = field.element(0), field.element(1)
    require(alpha.sign() == 1 and (one - alpha).sign() == 1,
            "V45_ALGEBRAIC_CHILD_WIDTH_NOT_STRICTLY_POSITIVE")
    parent_left, parent_right = span.left, span.right
    parent_width = parent_right - parent_left
    require(parent_left == 0 and parent_right == 1
            and parent_width > 0, "V45_SOURCE_INTERVAL_DRIFT")
    for i, (child, side, local_offset, local_width) in enumerate(zip(
        children, ("left", "right"), (zero, alpha), (alpha, one - alpha)
    )):
        require(child.get("side") == side and
                child.get("local_parameter_interval") == ["0", "1"]
                and child.get("exact_polynomial_roundtrip") is True,
                "V45_CHILD_IDENTITY_OR_ROUNDTRIP_DRIFT")
        parent_map = child["parent_local_map"]
        source_map = child["parent_source_map"]
        actual_local_offset = field.element(parent_map["offset"])
        actual_local_width = field.element(parent_map["width"])
        source_offset = field.element(source_map["offset"])
        source_width = field.element(source_map["width"])
        require(actual_local_offset == local_offset
                and actual_local_width == local_width
                and actual_local_width.sign() == 1
                and source_offset == field.element(parent_left) +
                    local_offset * parent_width
                and source_width == local_width * parent_width
                and source_width.sign() == 1,
                "V45_CHILD_AFFINE_MAP_NOT_ORIGINAL_SOURCE_BOUND")
        endpoints = child["parent_source_interval"]
        require(field.element(endpoints[0]) == source_offset
                and field.element(endpoints[1]) == source_offset + source_width,
                "V45_CHILD_SOURCE_INTERVAL_MISMATCH")
        phase = child["phase_turn_law"]
        require(field.element(phase["offset"]) ==
                field.element(span.offset) + source_offset * span.rate
                and field.element(phase["rate"]) ==
                source_width * span.rate,
                "V45_CHILD_PHASE_NOT_ORIGINAL_SOURCE_BOUND")
        for key, channel in (("cos_polynomials", 0),
                             ("sin_polynomials", 1)):
            actual = child["restricted_polynomials"][key]
            require(set(actual) == {str(h) for h in span.terms},
                    "V45_CHILD_HARMONIC_CHANNEL_LOSS")
            for h, terms in span.terms.items():
                expected = v45.compose_affine(
                    terms[channel], local_offset, local_width)
                require(actual[str(h)] == [x.record() for x in expected],
                        "V45_CHILD_POLYNOMIAL_RESTRICTION_MISMATCH")
        if i == 0:
            require(source_offset == zero
                    and source_offset + source_width == alpha,
                    "V45_LEFT_CHILD_END_NOT_ALPHA")
        else:
            require(source_offset == alpha
                    and source_offset + source_width == one,
                    "V45_RIGHT_CHILD_END_NOT_SOURCE_END")
    require(field.element(rep["internal_phase_turn"]) ==
            field.element(span.offset) + alpha * span.rate,
            "V45_CUT_PHASE_NOT_ORIGINAL_SOURCE_PHASE")
    return children


def prove(*, supplied_atlas=None):
    pins()
    view, span, root, _ = derivative._source_snapshot(supplied_atlas)
    derivative_report = derivative.prove(cells=16, supplied_atlas=view)
    require(derivative_report["status"] == derivative.SUCCESS
            and derivative_report["whole_closed_source_derivative_strictly_positive"]
            is True
            and derivative_report["closed_proof_children_derivative_positive_by_restriction"]
            is True
            and derivative_report["historical_v54_admitted"] is False,
            "PINNED_WHOLE_SOURCE_MONOTONICITY_NOT_PROVED")
    lower = Q(derivative_report["whole_closed_source_strict_derivative_lower_bound"])
    require(lower > 0, "NO_STRICT_RATIONAL_SOURCE_DERIVATIVE_LOWER")
    source_material = _source_material(span, view)
    representation = v45.build_orientation_child_maps(
        {h: list(terms[0]) for h, terms in span.terms.items()},
        {h: list(terms[1]) for h, terms in span.terms.items()},
        view["source_parameter_id"], (span.left, span.right),
        span.offset, span.rate,
    )
    require(representation.get("status") == "REPRESENTATION_CERTIFIED"
            and representation.get("source_material") == source_material
            and representation.get("analytic_cut_consumed") is False
            and representation.get("consumption_decision") ==
            "DO_NOT_CONSUME_ANALYTIC_CUT",
            "SOURCE_BOUND_V45_SPLIT_NOT_AVAILABLE")
    alternatives = representation["independent_single_cut_bisections"]
    require(type(alternatives) is list and len(alternatives) == 1,
            "FROZEN_V44_NOT_EXACTLY_ONE_V45_ALGEBRAIC_SPLIT")
    bisection = alternatives[0]
    require(bisection["source_parameter_id"] ==
            view["source_parameter_id"]
            and bisection["source_binding_sha256"] ==
            v45.sha256(v45._json(source_material).encode()).hexdigest(),
            "V45_SPLIT_SOURCE_IDENTITY_OR_PHASE_MISMATCH")
    field = _field(bisection["field"])
    children = _check_children(bisection, field, span)
    index, boundary, identity_method = _exact_alpha_boundary(view, field)
    cells = view["source_proof_cells"]
    left_count = sum(c["physical_open_root_count"] for c in cells[:index])
    right_count = sum(c["physical_open_root_count"] for c in cells[index:])
    require(left_count + right_count == 1
            and (left_count, right_count) in ((1, 0), (0, 1))
            and view["complete_original_source_physical_root_count"] == 1
            and root["smooth_multiplicity"] == 1,
            "V45_CHILD_ROOT_PARTITION_NOT_CONSERVED")
    alpha_sign = boundary["physical_value_sign"]
    require((alpha_sign == "POSITIVE" and (left_count, right_count) == (1, 0))
            or (alpha_sign == "NEGATIVE" and
                (left_count, right_count) == (0, 1)),
            "V45_CHILD_ROOT_LOCATION_CONFLICTS_WITH_STRICT_MONOTONICITY")
    summaries = []
    for child, count in zip(children, (left_count, right_count)):
        summaries.append({
            "side": child["side"],
            "parent_source_map": copy.deepcopy(child["parent_source_map"]),
            "source_parameter_id": view["source_parameter_id"],
            "closed_child_source_width_strictly_positive": True,
            "exact_polynomial_roundtrip_replayed": True,
            "original_source_phase_affine_restriction_replayed": True,
            "inherited_physical_child_derivative_lower_bound":
                "parent_source_strict_bound_times_positive_algebraic_width",
            "closed_child_physical_derivative_strictly_positive": True,
            "complete_open_physical_root_count": count,
            "new_algebraic_phase_trig_endpoint_evaluation": False,
        })
    pins()
    return {
        "schema": SCHEMA,
        "status": SUCCESS,
        "evidence_class": "DETERMINISTIC_MODEL",
        "frozen_case_id": previous.CASE_ID,
        "source_sha256": atlas.SOURCE_SHA256,
        "source_parameter_id": view["source_parameter_id"],
        "original_source_interval": copy.deepcopy(view["original_source_interval"]),
        "original_affine_phase": copy.deepcopy(view["original_affine_phase"]),
        "v45_field": field.record(),
        "v45_source_binding_sha256": bisection["source_binding_sha256"],
        "source_algebraic_proof_boundary_id": boundary["boundary_id"],
        "source_algebraic_boundary_nonzero_sign": alpha_sign,
        "alpha_identity_method": identity_method,
        "strict_rational_whole_source_physical_derivative_lower_bound": str(lower),
        "v45_closed_children": summaries,
        "complete_original_source_simple_root_count": 1,
        "complete_v45_split_open_root_counts": [left_count, right_count],
        "root_count_conserved_without_cut_event": True,
        "algebraic_cut_is_physical_event": False,
        "historical_v45_irrational_phase_endpoint_authority": "DEFERRED",
        "new_algebraic_child_trig_zero_solver_constructed": False,
        "general_v41_v47_child_event_route_certified": False,
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
        "schema": SCHEMA, "status": status, "reason": str(reason),
        "is_truth_value": False, "historical_v54_admitted": False,
        "pb00701_certified": False, "mc_b_established": False,
        "mc1_established": False, "production_authorized": False,
    }


def attempt(*, supplied_atlas=None):
    try:
        return prove(supplied_atlas=supplied_atlas)
    except (ResourceRefusal, derivative.ResourceRefusal,
            predecessor.ResourceRefusal, previous.ResourceRefusal,
            cut_order.ResourceRefusal, MemoryError, RecursionError,
            OverflowError) as exc:
        return nontruth(str(exc), "RESOURCE_REFUSAL")
    except (Refusal, derivative.Refusal, predecessor.Refusal, atlas.Refusal,
            previous.ResearchRefusal, cut_order.ResearchRefusal,
            ValueError, TypeError, KeyError, IndexError, ZeroDivisionError,
            AssertionError, AttributeError) as exc:
        return nontruth(str(exc))


def validate_report(submitted, *, supplied_atlas=None):
    try:
        predecessor._bound_untrusted_report_structure(submitted)
        claimed = previous.canonical(submitted)
        if len(claimed) > MAX_REPORT_BYTES:
            raise ResourceRefusal("SUBMITTED_V45_BRIDGE_REPORT_SIZE_LIMIT")
        checked = attempt(supplied_atlas=supplied_atlas)
        require(checked.get("status") == SUCCESS,
                "V45_SINGLE_CUT_MONOTONICITY_BRIDGE_NOT_PROVED")
        require(claimed == previous.canonical(checked),
                "FORGED_OR_INCONSISTENT_V45_BRIDGE_REPORT")
        return checked
    except (ResourceRefusal, predecessor.ResourceRefusal, MemoryError,
            RecursionError, OverflowError) as exc:
        return nontruth(str(exc), "RESOURCE_REFUSAL")
    except (Refusal, previous.ResearchRefusal, ValueError,
            TypeError, KeyError) as exc:
        return nontruth(str(exc))
