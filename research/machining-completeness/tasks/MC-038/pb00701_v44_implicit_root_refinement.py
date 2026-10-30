#!/usr/bin/env python3
"""Frozen V44: strictly certified rational refinement of one implicit source root.

This is a deterministic-model source-coordinate bracket *refinement*, not an
algebraic child, a second complete-root theorem or a historical V54 route.
"""
from __future__ import annotations

import copy
from fractions import Fraction as Q

import pb00701_v44_source_proof_cell_atlas as atlas

SCHEMA = "radicadsac-pb00701-v44-implicit-root-refinement/1.0"
SUCCESS = "EXACT_FROZEN_V44_ORIGINAL_SOURCE_IMPLICIT_ROOT_REFINED_RESEARCH"
ATLAS_BLOB = "2028684883f78ceed14ce92865810ef11409b7eb"
POINT_CONSUMER_BLOB = "6d1805dacdf73f003d7431416d77754635e3f950"
MAX_REFINEMENT_STEPS = 12
MAX_REPORT_BYTES = 131072
MAX_REPORT_NESTING_DEPTH = 48
MAX_REPORT_VISITED_NODES = 20000


class Refusal(ValueError):
    pass


class ResourceRefusal(RuntimeError):
    pass


def require(condition, reason):
    if not condition:
        raise Refusal(reason)


def pins():
    previous = atlas.previous
    require(previous.git_blob(previous.TASK /
            "pb00701_v44_source_proof_cell_atlas.py") == ATLAS_BLOB,
            "PINNED_ATLAS_SOURCE_DRIFT")
    require(previous.git_blob(previous.TASK /
            "pb00701_v44_source_point_consumer.py") == POINT_CONSUMER_BLOB,
            "PINNED_EXACT_POINT_CONSUMER_SOURCE_DRIFT")
    atlas.pins()


def _validated_atlas(supplied):
    if supplied is None:
        result = atlas.prove()
    else:
        result = atlas.validate_report(supplied)
    require(result.get("status") == atlas.SUCCESS
            and result.get("parent_frozen_case_id") == atlas.previous.CASE_ID
            and result.get("parent_source_sha256") == atlas.SOURCE_SHA256
            and result.get("original_source_interval") == ["0", "1"]
            and result.get("original_affine_phase") ==
            {"offset": "-1/8", "rate": "1/16"}
            and result.get("complete_original_source_physical_root_count") == 1
            and result.get("one_physical_root_cell_index") == 1
            and result.get("proof_cuts_are_events") is False
            and result.get("actual_algebraic_child_analytic_chart_constructed")
            is False
            and result.get("closed_child_derivative_theorem_proved") is False
            and result.get("historical_v54_admitted") is False
            and result.get("mc_b_established") is False
            and result.get("production_authorized") is False,
            "SOURCE_REPLAYED_FROZEN_V44_ATLAS_REQUIRED")
    require(len(result["source_proof_cells"]) == 4
            and [c["physical_open_root_count"]
                 for c in result["source_proof_cells"]] == [0, 1, 0, 0],
            "FROZEN_PHYSICAL_ROOT_CELL_COUNTS_CHANGED")
    return result


def _strict_source_sign(span, x):
    """Exact rational Taylor/pi enclosure, no floating or zero assumption."""
    bounds = span.evaluate(x)
    sign = atlas.previous.trig.strict_sign(bounds)
    if sign == 0:
        raise ResourceRefusal("RATIONAL_SOURCE_MIDPOINT_SIGN_UNDECIDED")
    require(sign in (-1, 1)
            and bounds[0] <= bounds[1]
            and (bounds[0] > 0 if sign == 1 else bounds[1] < 0),
            "STRICT_SOURCE_TRIG_ENCLOSURE_INVALID")
    return sign, [str(bounds[0]), str(bounds[1])]


def refine(*, steps=8, supplied_atlas=None):
    """Return a narrower *strict* root bracket or typed nontruth on refusal."""
    pins()
    require(type(steps) is int and 0 <= steps <= MAX_REFINEMENT_STEPS,
            "INVALID_OR_OVERSIZED_REFINEMENT_STEP_BUDGET")
    view = _validated_atlas(supplied_atlas)
    cell = view["source_proof_cells"][1]
    require(cell.get("kind") == "EXACT_SOURCE_ONE_SIMPLE_ROOT_CELL"
            and cell.get("physical_open_root_count") == 1,
            "UNIQUE_SIMPLE_PHYSICAL_ROOT_CELL_REQUIRED")

    # Rebuild the original source from the pinned frozen corpus and prove its
    # complete root set anew; supplied atlas coefficients are never executable.
    span, full_proof, roots = atlas.previous._physical_root_proof(
        atlas.previous.frozen_row()
    )
    witness = cell["one_simple_physical_root_witness"]
    require(full_proof.get("complete_simple_root_count") == 1
            and len(roots) == 1 and roots[0] == witness
            and witness["smooth_multiplicity"] == 1
            and witness["derivative_sign"] in (-1, 1)
            and witness["left_sign"] == -witness["right_sign"]
            and witness["derivative_sign"] == witness["right_sign"],
            "INDEPENDENT_COMPLETE_ORIGINAL_SOURCE_ROOT_PROOF_MISMATCH")
    initial_lo, initial_hi = map(Q, witness["strict_isolation"])
    source_lo, source_hi = map(Q, witness["cell_interval"])
    require(Q(0) <= source_lo <= initial_lo < initial_hi <= source_hi <= Q(1),
            "ORIGINAL_ROOT_BRACKET_NOT_WITHIN_PROVED_SOURCE_CELL")
    left_sign, left_interval = _strict_source_sign(span, initial_lo)
    right_sign, right_interval = _strict_source_sign(span, initial_hi)
    require(left_sign == witness["left_sign"]
            and right_sign == witness["right_sign"]
            and left_sign != right_sign,
            "ORIGINAL_STRICT_BRACKET_ENDPOINT_SIGN_MISMATCH")

    lo, hi = initial_lo, initial_hi
    records = []
    for index in range(steps):
        mid = (lo + hi) / 2
        mid_sign, enclosure = _strict_source_sign(span, mid)
        require(lo < mid < hi, "NONSTRICT_RATIONAL_BISECTION")
        if mid_sign == left_sign:
            lo = mid
            selected = "LEFT_BOUND_MOVED_RIGHT"
        else:
            require(mid_sign == right_sign,
                    "MIDPOINT_SIGN_INCOMPATIBLE_WITH_SIMPLE_ROOT_CROSSING")
            hi = mid
            selected = "RIGHT_BOUND_MOVED_LEFT"
        records.append({
            "step": index + 1,
            "exact_original_source_midpoint": str(mid),
            "strict_physical_value_sign": atlas.name(mid_sign),
            "strict_rational_trig_enclosure": enclosure,
            "root_containing_half": selected,
            "new_strict_source_bracket": [str(lo), str(hi)],
            "midpoint_is_physical_zero": False,
        })
    require(lo < hi and hi - lo ==
            (initial_hi - initial_lo) / (2 ** steps),
            "STRICT_ROOT_BRACKET_WIDTH_NOT_CONSERVED")
    final_left, _ = _strict_source_sign(span, lo)
    final_right, _ = _strict_source_sign(span, hi)
    require(final_left == left_sign and final_right == right_sign,
            "REFINED_SOURCE_BRACKET_ENDPOINT_SIGN_DRIFT")
    pins()
    return {
        "schema": SCHEMA,
        "status": SUCCESS,
        "evidence_class": "DETERMINISTIC_MODEL",
        "frozen_case_id": atlas.previous.CASE_ID,
        "source_sha256": atlas.SOURCE_SHA256,
        "source_parameter_id": view["source_parameter_id"],
        "original_source_interval": copy.deepcopy(
            view["original_source_interval"]),
        "original_affine_phase": copy.deepcopy(
            view["original_affine_phase"]),
        "parent_atlas_schema": view["schema"],
        "root_cell_index": 1,
        "complete_original_source_physical_root_count": 1,
        "initial_strict_source_bracket": [str(initial_lo), str(initial_hi)],
        "initial_endpoint_signs": [atlas.name(left_sign),
                                   atlas.name(right_sign)],
        "initial_strict_endpoint_enclosures":
            [left_interval, right_interval],
        "requested_refinement_steps": steps,
        "refinement_trace": records,
        "final_strict_source_bracket": [str(lo), str(hi)],
        "final_bracket_width": str(hi - lo),
        "unique_simple_root_strictly_inside_final_bracket": True,
        "proof_method": "EXACT_RATIONAL_TRIG_ENCLOSURE_PLUS_COMPLETE_SINGLE_SIMPLE_ROOT_IVT",
        "refinement_is_root_set_restriction_only": True,
        "new_complete_root_isolation_theorem_claimed": False,
        "implicit_root_declared_rational_or_algebraic": False,
        "physical_proof_cuts_promoted_to_events": False,
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
        "schema": SCHEMA, "status": status, "reason": str(reason),
        "is_truth_value": False, "historical_v54_admitted": False,
        "pb00701_certified": False, "mc_b_established": False,
        "mc1_established": False, "production_authorized": False,
    }


def attempt(*, steps=8, supplied_atlas=None):
    try:
        return refine(steps=steps, supplied_atlas=supplied_atlas)
    except (ResourceRefusal, atlas.previous.ResourceRefusal,
            atlas.previous.cut_order.ResourceRefusal,
            MemoryError, RecursionError, OverflowError) as exc:
        return nontruth(str(exc), "RESOURCE_REFUSAL")
    except (Refusal, atlas.Refusal, atlas.previous.ResearchRefusal,
            atlas.previous.cut_order.ResearchRefusal,
            atlas.previous.trig.Refusal, ValueError, TypeError,
            KeyError, IndexError, ZeroDivisionError, AssertionError) as exc:
        return nontruth(str(exc))


def _bound_untrusted_report_structure(submitted):
    """Iterative, cycle-safe-by-depth budget before JSON report serialization."""
    todo = [(submitted, 0)]
    visited = 0
    while todo:
        value, depth = todo.pop()
        visited += 1
        if depth > MAX_REPORT_NESTING_DEPTH:
            raise ResourceRefusal("SUBMITTED_REFINEMENT_REPORT_NESTING_LIMIT")
        if visited > MAX_REPORT_VISITED_NODES:
            raise ResourceRefusal("SUBMITTED_REFINEMENT_REPORT_NODE_LIMIT")
        if type(value) is dict:
            todo.extend((v, depth + 1) for v in value.values())
        elif type(value) in (list, tuple):
            todo.extend((v, depth + 1) for v in value)


def validate_report(submitted, *, steps=8, supplied_atlas=None):
    try:
        _bound_untrusted_report_structure(submitted)
        claimed = atlas.previous.canonical(submitted)
        require(len(claimed) <= MAX_REPORT_BYTES,
                "SUBMITTED_REFINEMENT_REPORT_TOO_LARGE")
        replay = attempt(steps=steps, supplied_atlas=supplied_atlas)
        require(replay.get("status") == SUCCESS,
                "EXACT_ORIGINAL_SOURCE_REFINEMENT_NOT_ESTABLISHED")
        require(claimed == atlas.previous.canonical(replay),
                "FORGED_OR_INCONSISTENT_REFINED_SOURCE_ROOT_BRACKET")
        return replay
    except (ResourceRefusal, MemoryError, RecursionError) as exc:
        # Resource caps and encoder overflow must never become proof truth.
        return nontruth(str(exc), "RESOURCE_REFUSAL")
    except (Refusal, atlas.previous.ResearchRefusal,
            ValueError, TypeError, OverflowError) as exc:
        return nontruth(str(exc))
