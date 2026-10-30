#!/usr/bin/env python3
"""One frozen V44 source: exact whole-closed-source positive derivative proof.

Original rational B-spline source and phase only. The closed dyadic-cover
certificate uses a universal |F''| bound and exact outward trig enclosures.
It does not construct a Q(alpha) analytic child or admit historical v54.
"""
from __future__ import annotations

import copy
from fractions import Fraction as Q

import pb00701_v44_implicit_root_refinement as predecessor

atlas = predecessor.atlas
previous = atlas.previous
trig = previous.trig

SCHEMA = "radicadsac-pb00701-v44-global-source-derivative/1.0"
SUCCESS = "EXACT_FROZEN_V44_WHOLE_SOURCE_POSITIVE_DERIVATIVE_RESEARCH"
PREDECESSOR_BLOB = "3adb5630b929b051153e43b423a6ad2e7893dc5f"
ALLOWED_CELL_COUNTS = (8, 16, 32)
DYADIC_ENCLOSURE_BITS = 32
MAX_REPORT_BYTES = 65536
EXPECTED_M2 = Q(335000000121, 19600000000)
EXPECTED_TERMS = {
    1: ((Q(-3, 2), Q(1), Q(2)), (Q(-1, 2), Q(-1), Q(2))),
    2: ((Q(1, 100000000),), (Q(0),)),
}


class Refusal(ValueError):
    pass


class ResourceRefusal(RuntimeError):
    pass


def require(condition, reason):
    if not condition:
        raise Refusal(reason)


def pins():
    require(previous.git_blob(previous.TASK /
            "pb00701_v44_implicit_root_refinement.py") == PREDECESSOR_BLOB,
            "PINNED_V44_REFINEMENT_SOURCE_DRIFT")
    predecessor.pins()


def _independent_second_derivative_bound(span):
    """Recompute M2 directly from every original-source amplitude channel.

    F'' = (P'' + 2k Q' - k*k P) cos(theta)
        + (Q'' - 2k P' - k*k Q) sin(theta), k=2*pi*h*rate.
    Since 2*pi < 44/7, all sine/cosine magnitudes <=1, and |t|<=1,
    coefficient l1 norms give a rational global |F''| upper bound.
    """
    bound = Q(0)
    radius = max(Q(1), abs(span.left), abs(span.right))
    for h, (p, s) in span.terms.items():
        dp, ds = trig.derivative(p), trig.derivative(s)
        ddp, dds = trig.derivative(dp), trig.derivative(ds)
        k = Q(44, 7) * abs(h * span.rate)
        bound += (
            trig.norm_bound(ddp, radius) + trig.norm_bound(dds, radius)
            + 2 * k * (trig.norm_bound(dp, radius)
                       + trig.norm_bound(ds, radius))
            + k * k * (trig.norm_bound(p, radius)
                       + trig.norm_bound(s, radius))
        )
    return bound


def _source_snapshot(supplied_atlas):
    view = predecessor._validated_atlas(supplied_atlas)
    span, complete, roots = previous._physical_root_proof(previous.frozen_row())
    require(
        span.left == Q(0) and span.right == Q(1)
        and span.offset == Q(-1, 8) and span.rate == Q(1, 16)
        and span.terms == EXPECTED_TERMS,
        "FROZEN_V44_ORIGINAL_SOURCE_OR_PHASE_COEFFICIENT_DRIFT",
    )
    require(
        complete.get("complete_simple_root_count") == 1 and len(roots) == 1
        and roots[0] == view["source_proof_cells"][1][
            "one_simple_physical_root_witness"]
        and roots[0]["left_sign"] == -1 and roots[0]["right_sign"] == 1
        and roots[0]["smooth_multiplicity"] == 1
        and view["complete_original_source_physical_root_count"] == 1
        and view["one_physical_root_cell_index"] == 1
        and view["proof_cuts_are_events"] is False,
        "FROZEN_COMPLETE_ROOT_AND_PROOF_CELL_REPLAY_MISMATCH",
    )
    lo_pi, hi_pi = trig.pi_bounds()
    require(Q(3) < lo_pi < hi_pi < Q(22, 7),
            "EXACT_TRIG_PI_INTERVAL_DRIFT")
    m2 = _independent_second_derivative_bound(span)
    require(m2 == span.m2 == EXPECTED_M2 and m2 > 0,
            "UNIVERSAL_ORIGINAL_SOURCE_SECOND_DERIVATIVE_BOUND_DRIFT")
    return view, span, roots[0], m2


def _outward_dyadic(value, *, upward):
    require(type(value) is Q, "NONRATIONAL_DERIVATIVE_ENCLOSURE")
    scale = 1 << DYADIC_ENCLOSURE_BITS
    scaled = value * scale
    integer = scaled.numerator // scaled.denominator
    if upward and Q(integer) < scaled:
        integer += 1
    return Q(integer, scale)


def _cell(span, m2, index, count):
    left, right = Q(index, count), Q(index + 1, count)
    midpoint, radius = (left + right) / 2, (right - left) / 2
    actual = span.evaluate(midpoint, first_derivative=True)
    require(type(actual) is tuple and len(actual) == 2
            and all(type(x) is Q for x in actual)
            and actual[0] <= actual[1],
            "INVALID_EXACT_PHYSICAL_DERIVATIVE_POINT_ENCLOSURE")
    low = _outward_dyadic(actual[0], upward=False)
    high = _outward_dyadic(actual[1], upward=True)
    require(low <= actual[0] <= actual[1] <= high,
            "DERIVATIVE_POINT_ENCLOSURE_ROUNDED_INWARD")
    drift = m2 * radius
    strict_lower = low - drift
    require(strict_lower > 0,
            "CLOSED_DYADIC_CELL_DERIVATIVE_POSITIVITY_NOT_ESTABLISHED")
    return {
        "index": index,
        "closed_original_source_interval": [str(left), str(right)],
        "exact_rational_midpoint": str(midpoint),
        "outward_rounded_physical_derivative_enclosure":
            [str(low), str(high)],
        "universal_second_derivative_drift": str(drift),
        "strict_physical_derivative_lower_bound": str(strict_lower),
        "derivative_positive_everywhere_on_closed_cell": True,
    }


def _closed_proof_children(view):
    """Inheritance, not a new Q(alpha) child analytic chart or classifier.

    Source replay proves all five endpoints strictly ordered in [0,1].
    On each closed proof child t=a+(b-a)*u, dt/du=b-a>0, so a
    source-wide strict F'(t)>0 gives dF/du>0 even for irrational a/b.
    """
    boundaries = view["proof_boundaries"]
    cells = view["source_proof_cells"]
    require(len(boundaries) == 5 and len(cells) == 4,
            "NONEXHAUSTIVE_ORIGINAL_SOURCE_PROOF_CUT_PARTITION")
    out = []
    for i, cell in enumerate(cells):
        require(cell["index"] == i
                and cell["left_boundary_id"] == boundaries[i]["boundary_id"]
                and cell["right_boundary_id"] == boundaries[i+1]["boundary_id"],
                "PROOF_CHILD_SOURCE_ENDPOINT_OR_ORDER_MISMATCH")
        out.append({
            "index": i,
            "left_boundary_id": boundaries[i]["boundary_id"],
            "right_boundary_id": boundaries[i+1]["boundary_id"],
            "physical_open_root_count": cell["physical_open_root_count"],
            "normalized_affine_child_width_strictly_positive_by_exact_cut_order": True,
            "strict_positive_child_derivative_inherited_by_chain_rule": True,
            "irrational_endpoint_trig_evaluation_required": False,
            "child_analytic_chart_constructed": False,
        })
    return out


def prove(*, cells=16, supplied_atlas=None):
    pins()
    require(type(cells) is int and cells in ALLOWED_CELL_COUNTS,
            "INVALID_OR_EXCESSIVE_DYADIC_CELL_BUDGET")
    view, span, root, m2 = _source_snapshot(supplied_atlas)
    # The exact endpoint enclosures are also checked independently from the
    # previous complete-root proof and its proof-cell sign atlas.
    endpoints = [span.evaluate(Q(0)), span.evaluate(Q(1))]
    require(endpoints[0][1] < 0 < endpoints[1][0]
            and root["left_sign"] == -1 and root["right_sign"] == 1,
            "EXACT_SOURCE_ENDPOINT_CROSSING_NOT_ESTABLISHED")
    trace = [_cell(span, m2, i, cells) for i in range(cells)]
    require(len(trace) == cells and trace[0][
        "closed_original_source_interval"][0] == "0" and trace[-1][
        "closed_original_source_interval"][1] == "1",
        "DYADIC_COVER_INCOMPLETE")
    for prior_cell, next_cell in zip(trace, trace[1:]):
        require(prior_cell["closed_original_source_interval"][1] ==
                next_cell["closed_original_source_interval"][0],
                "DYADIC_COVER_GAP_OR_OVERLAP")
    global_lower = min(
        Q(cell["strict_physical_derivative_lower_bound"]) for cell in trace
    )
    require(global_lower > 0, "WHOLE_SOURCE_DERIVATIVE_NOT_STRICTLY_POSITIVE")
    proof_children = _closed_proof_children(view)
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
        "exact_original_harmonic_terms": {
            str(h): [[str(v) for v in p], [str(v) for v in s]]
            for h, (p, s) in sorted(span.terms.items())
        },
        "universal_abs_second_derivative_upper_bound": str(m2),
        "point_derivative_outward_dyadic_precision_bits": DYADIC_ENCLOSURE_BITS,
        "requested_dyadic_cells": cells,
        "closed_dyadic_cover": trace,
        "whole_closed_source_strict_derivative_lower_bound": str(global_lower),
        "whole_closed_source_derivative_strictly_positive": True,
        "certified_endpoint_physical_value_signs": ["NEGATIVE", "POSITIVE"],
        "exactly_one_simple_physical_root_from_IVT_and_global_monotonicity": True,
        "previous_complete_source_root_proof_crosschecked": True,
        "original_source_proof_cut_children": proof_children,
        "closed_proof_children_derivative_positive_by_restriction": True,
        "proof_cuts_are_physical_events": False,
        "general_algebraic_child_analytic_chart_constructed": False,
        "general_v41_v47_child_derivative_interface_certified": False,
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


def attempt(*, cells=16, supplied_atlas=None):
    try:
        return prove(cells=cells, supplied_atlas=supplied_atlas)
    except (ResourceRefusal, predecessor.ResourceRefusal,
            previous.ResourceRefusal, previous.cut_order.ResourceRefusal,
            MemoryError, RecursionError, OverflowError) as exc:
        return nontruth(str(exc), "RESOURCE_REFUSAL")
    except (Refusal, predecessor.Refusal, atlas.Refusal,
            previous.ResearchRefusal, previous.cut_order.ResearchRefusal,
            trig.Refusal, ValueError, TypeError, KeyError, IndexError,
            ZeroDivisionError, AssertionError) as exc:
        return nontruth(str(exc))


def validate_report(submitted, *, cells=16, supplied_atlas=None):
    try:
        # Bound untrusted structural complexity before canonical JSON
        # serialization, including cyclic/deep hostile Python inputs.
        predecessor._bound_untrusted_report_structure(submitted)
        claimed = previous.canonical(submitted)
        if len(claimed) > MAX_REPORT_BYTES:
            raise ResourceRefusal("SUBMITTED_GLOBAL_DERIVATIVE_REPORT_SIZE_LIMIT")
        replay = attempt(cells=cells, supplied_atlas=supplied_atlas)
        require(replay.get("status") == SUCCESS,
                "FROZEN_WHOLE_SOURCE_DERIVATIVE_PROOF_NOT_ESTABLISHED")
        require(claimed == previous.canonical(replay),
                "FORGED_OR_INCONSISTENT_WHOLE_SOURCE_DERIVATIVE_CERTIFICATE")
        return replay
    except (ResourceRefusal, predecessor.ResourceRefusal,
            MemoryError, RecursionError) as exc:
        return nontruth(str(exc), "RESOURCE_REFUSAL")
    except (Refusal, previous.ResearchRefusal, ValueError, TypeError,
            OverflowError) as exc:
        return nontruth(str(exc))
