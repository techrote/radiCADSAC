#!/usr/bin/env python3
"""MC-038: complete single zero at an exact two-span source knot.

Conditional deterministic-model research only. Two exact rational-polynomial
finite-harmonic source spans meet at one rational real-source knot. Exact
one-sided jets plus derivative-sign guards and exhaustive zero-free outer
covers prove that the shared knot is the only physical zero in the union.
The shared boundary zero is counted once; no global smooth knot multiplicity
is invented. No historical V27/V41, MC-B, native B-rep, STEP, or production
capability is implied.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pb00701_jet_guarded_nontransverse as guarded
import pb00701_rational_phase_point as point
import pb00701_transverse_trig_interval as interval

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[3]
SCHEMA = "radicadsac-pb00701-knot-zero-cover/1.0"
MAX_CERT_BYTES = 32768
PINS = {
    TASK / "pb00701_jet_guarded_nontransverse.py":
        "37c0271852e1468aa5ecfa9078d6f950841e4194",
    TASK / "pb00701_rational_phase_point.py":
        "9fc344e045fa800fb24d30902a641e534a1e197b",
    TASK / "pb00701_transverse_trig_interval.py":
        "2320f92efe4316d865a89f6d848737e2c000ca4d",
    TASK / "pb00701-finite-owner-corpus-v54.json":
        "5841c331579489b25caef38cd412bdbf286f9134",
    ROOT / "research/machining-completeness/tasks/MC-002/domain-contract-v1.json":
        "23de82f5240a72509f7afe4acd5948b65bc4ff13",
    ROOT / "handoffs/current-authority.json":
        "fa0233323a0804d8a5d3eb7cd892a274a6173fab",
}


class Refusal(ValueError):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def require(ok, reason):
    if not ok:
        raise Refusal(reason)


def canonical(obj):
    try:
        return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False)
    except (TypeError, ValueError, OverflowError) as exc:
        raise Refusal("NONJSON_OR_NONFINITE_EVIDENCE") from exc


def git_blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def pins():
    for path, expected in PINS.items():
        require(git_blob(path) == expected,
                "ORIGINAL_PRODUCER_OR_FROZEN_SOURCE_DRIFT:" + path.name)
    # Recheck the transitive custody enforced by the reviewed #303 primitive.
    guarded.pins()


def source_sha256(source):
    return hashlib.sha256(canonical(source).encode("ascii")).hexdigest()


def one_sided_guard(span, knot, edge, event, side):
    require(side in ("LEFT", "RIGHT"), "INVALID_ONE_SIDED_GUARD_DIRECTION")
    order = event["one_sided_order"]
    require(type(order) is int and 2 <= order <= 6,
            "NONTRANSVERSE_SOURCE_KNOT_JET_NOT_ESTABLISHED")
    derivative_sign = event["first_nonzero_derivative_sign"]
    require(derivative_sign in (-1, 1) and
            event["exact_vanishing_derivatives"] == list(range(order)),
            "INCOMPLETE_SOURCE_KNOT_DERIVATIVE_JET")
    if side == "LEFT":
        require(span.left < edge < knot == span.right,
                "INVALID_LEFT_SOURCE_KNOT_GUARD")
        distance = knot - edge
        physical_sign = event["left_sign"]
        require(event["left_in_source"] and not event["right_in_source"],
                "LEFT_SOURCE_KNOT_ENDPOINT_ORIENTATION_MISMATCH")
        outer_endpoint = span.left
    else:
        require(span.left == knot < edge < span.right,
                "INVALID_RIGHT_SOURCE_KNOT_GUARD")
        distance = edge - knot
        physical_sign = event["right_sign"]
        require(not event["left_in_source"] and event["right_in_source"],
                "RIGHT_SOURCE_KNOT_ENDPOINT_ORIENTATION_MISMATCH")
        outer_endpoint = span.right

    next_bound = guarded.derivative_limit(span, order + 1)
    center = point.derivative_interval(span, knot, order)
    enclosure = interval.widen(center, next_bound * distance)
    require(interval.strict_sign(enclosure) == derivative_sign,
            "ONE_SIDED_KNOT_DERIVATIVE_SIGN_UNDECIDED")
    require(interval.strict_sign(span.evaluate(edge)) == physical_sign and
            interval.strict_sign(span.evaluate(outer_endpoint)) == physical_sign,
            "SOURCE_OR_KNOT_GUARD_ENDPOINT_SIGN_UNPROVED")
    return {
        "side": side,
        "source_interval": [str(span.left), str(span.right)],
        "guard_interval": ([str(edge), str(knot)] if side == "LEFT"
                           else [str(knot), str(edge)]),
        "one_sided_order": order,
        "first_nonzero_derivative_sign": derivative_sign,
        "physical_side_sign": physical_sign,
        "global_abs_derivative_order_plus_1_bound": str(next_bound),
        "guard_order_derivative_enclosure":
            [str(enclosure[0]), str(enclosure[1])],
    }


def prove(left_source, right_source, knot, guards, *,
          max_order=4, max_depth=18, max_nodes=20000):
    pins()
    require(type(left_source) is dict and type(right_source) is dict,
            "INVALID_SOURCE_RECORD_TYPE")
    left = guarded.source_span(left_source)
    right = guarded.source_span(right_source)
    knot = guarded.rat(knot)
    require(type(guards) is list and len(guards) == 2,
            "INVALID_KNOT_GUARD_TYPE")
    left_edge, right_edge = (guarded.rat(v) for v in guards)
    require(left_source["source_parameter_id"] ==
            right_source["source_parameter_id"] == "source-time-t",
            "SOURCE_KNOT_PARAMETER_ID_MISMATCH")
    require(left.right == knot == right.left and
            (left.offset, left.rate) == (right.offset, right.rate),
            "SOURCE_KNOT_PHASE_OR_COORDINATE_MISMATCH")
    require(type(max_order) is int and 2 <= max_order <= 6 and
            type(max_depth) is int and 0 <= max_depth <= 18 and
            type(max_nodes) is int and 2 <= max_nodes <= 20000,
            "INVALID_PROOF_RESOURCE_BUDGET")

    knot_event = point.compose_knot(left, right, knot, max_order=max_order)
    require(knot_event["status"] == "EXACT_SINGLE_SOURCE_KNOT_ZERO" and
            knot_event["physical_zero_events"] == 1 and
            knot_event["coordinate"] == str(knot),
            "EXACT_ZERO_SOURCE_KNOT_NOT_ESTABLISHED")
    left_event = point.point(left, knot, max_order=max_order)
    right_event = point.point(right, knot, max_order=max_order)
    require(left_event["status"] == right_event["status"] ==
            "EXACT_RATIONAL_POINT_EVENT",
            "SOURCE_KNOT_POINT_EVENT_MISSING")
    require(left_event["source_binding_sha256"] ==
            point.span_binding(left) and
            right_event["source_binding_sha256"] ==
            point.span_binding(right),
            "SOURCE_KNOT_SOURCE_BINDING_MISMATCH")

    left_guard = one_sided_guard(left, knot, left_edge, left_event, "LEFT")
    right_guard = one_sided_guard(right, knot, right_edge, right_event, "RIGHT")
    require(left_guard["physical_side_sign"] == knot_event["left_sign"] and
            right_guard["physical_side_sign"] == knot_event["right_sign"],
            "SOURCE_KNOT_PHYSICAL_SIGN_DISAGREEMENT")
    require(knot_event["event_kind"] ==
            ("CROSSING" if knot_event["left_sign"] != knot_event["right_sign"]
             else "TOUCHING"),
            "SOURCE_KNOT_EVENT_KIND_DISAGREEMENT")

    left_m1 = guarded.derivative_limit(left, 1)
    right_m1 = guarded.derivative_limit(right, 1)
    left_cover = guarded.no_root_cover(
        left, left.left, left_edge, knot_event["left_sign"], left_m1,
        {"max_nodes": max_nodes, "max_depth": max_depth})
    remaining = max_nodes - left_cover["nodes"]
    require(remaining >= 1, "COMBINED_OUTER_COVER_NODE_RESOURCE_LIMIT")
    right_cover = guarded.no_root_cover(
        right, right_edge, right.right, knot_event["right_sign"], right_m1,
        {"max_nodes": remaining, "max_depth": max_depth})
    require(left_cover["nodes"] + right_cover["nodes"] <= max_nodes,
            "COMBINED_OUTER_COVER_NODE_RESOURCE_LIMIT")

    # The union is exactly:
    # [left endpoint, left guard edge] + [left edge, knot] +
    # [knot, right edge] + [right edge, right endpoint].
    # The first and last pieces are complete strict-sign covers; the two knot
    # guards contain only their shared boundary zero by Taylor's theorem.
    require(left_cover["source_interval"] ==
            [str(left.left), str(left_edge)] and
            left_guard["guard_interval"] ==
            [str(left_edge), str(knot)] and
            right_guard["guard_interval"] ==
            [str(knot), str(right_edge)] and
            right_cover["source_interval"] ==
            [str(right_edge), str(right.right)],
            "TWO_SPAN_SOURCE_KNOT_COVER_INCOMPLETE")

    pins()
    return {
        "schema": SCHEMA,
        "status": "COMPLETE_SINGLE_SOURCE_KNOT_ZERO_UNION_RESEARCH",
        "evidence_class": "DETERMINISTIC_MODEL",
        "source_parameter_id": "source-time-t",
        "complete_union_source_interval":
            [str(left.left), str(right.right)],
        "phase_turns": [str(left.offset), str(left.rate)],
        "knot_coordinate": str(knot),
        "left_source_record_sha256": source_sha256(left_source),
        "right_source_record_sha256": source_sha256(right_source),
        "left_source_binding_sha256": point.span_binding(left),
        "right_source_binding_sha256": point.span_binding(right),
        "left_source_interval": [str(left.left), str(left.right)],
        "right_source_interval": [str(right.left), str(right.right)],
        "left_one_sided_order": knot_event["left_one_sided_order"],
        "right_one_sided_order": knot_event["right_one_sided_order"],
        "physical_left_sign": knot_event["left_sign"],
        "physical_right_sign": knot_event["right_sign"],
        "event_kind": knot_event["event_kind"],
        "physical_zero_events": 1,
        "source_knot_counted_once": True,
        "global_smooth_multiplicity_claimed": False,
        "left_point_derivative_jet": left_event,
        "right_point_derivative_jet": right_event,
        "left_knot_guard": left_guard,
        "right_knot_guard": right_guard,
        "left_zero_free_outer_cover": left_cover,
        "right_zero_free_outer_cover": right_cover,
        "combined_outer_cover_nodes":
            left_cover["nodes"] + right_cover["nodes"],
        "complete_other_source_roots_excluded": True,
        "historical_v54_admitted": False,
        "general_v27_v41_source_knot_certified": False,
        "pb00701_certified": False,
        "mc_b_established": False,
        "mc1_established": False,
        "native_brep_or_step_qualified": False,
        "production_authorized": False,
    }


def nontruth(reason, status="BLOCKED"):
    return {
        "schema": SCHEMA, "status": status, "reason": reason,
        "is_truth_value": False,
        "historical_v54_admitted": False,
        "mc_b_established": False,
        "production_authorized": False,
    }


def attempt(left_source, right_source, knot, guards, **budget):
    try:
        return prove(left_source, right_source, knot, guards, **budget)
    except (Refusal, guarded.Refusal, point.Refusal, interval.Refusal,
            ValueError, KeyError, IndexError, TypeError, ZeroDivisionError,
            OverflowError) as exc:
        reason = str(exc)
        status = ("RESOURCE_REFUSAL" if any(tag in reason for tag in
                  ("RESOURCE", "UNDECIDED", "UNRESOLVED", "EXHAUSTED"))
                  else "BLOCKED")
        return nontruth(reason, status)
    except (MemoryError, RecursionError) as exc:
        return nontruth(type(exc).__name__, "RESOURCE_REFUSAL")


def validate_report(left_source, right_source, knot, guards, submitted, **budget):
    try:
        claimed = canonical(submitted)
        if len(claimed) > MAX_CERT_BYTES:
            return nontruth("SUBMITTED_REPORT_RESOURCE_LIMIT", "RESOURCE_REFUSAL")
        checked = attempt(left_source, right_source, knot, guards, **budget)
        require(checked.get("status") ==
                "COMPLETE_SINGLE_SOURCE_KNOT_ZERO_UNION_RESEARCH",
                "EXACT_COMPLETE_SOURCE_KNOT_PROOF_MISSING")
        require(claimed == canonical(checked),
                "FORGED_SOURCE_KNOT_COMPLETE_ROOT_REPORT")
        return checked
    except (Refusal, ValueError, TypeError, OverflowError) as exc:
        return nontruth(str(exc))
    except (MemoryError, RecursionError) as exc:
        return nontruth(type(exc).__name__, "RESOURCE_REFUSAL")
