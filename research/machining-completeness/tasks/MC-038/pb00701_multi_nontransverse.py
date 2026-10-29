#!/usr/bin/env python3
"""MC-038: conditional complete ordered multiple nontransverse roots of ONE source.

An exact rational jet plus a strict derivative guard proves one root per guard.
Complete signed dyadic covers of ALL complementary intervals, including the
intervals between guards, prove there are no omitted roots. Research only.
"""
from __future__ import annotations

import hashlib
from fractions import Fraction as Q
from pathlib import Path

import pb00701_jet_guarded_nontransverse as single

SCHEMA = "radicadsac-pb00701-multi-nontransverse/1.0"
MAX_CERT_BYTES = 32768
SINGLE_BLOB = "37c0271852e1468aa5ecfa9078d6f950841e4194"


class Refusal(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise Refusal(reason)


def pins():
    single.pins()
    p = Path(single.__file__)
    raw = p.read_bytes()
    got = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    require(got == SINGLE_BLOB, "PINNED_SINGLE_ROOT_PRODUCER_DRIFT")


def rational(value):
    return single.rat(value)


def guard_proof(span, root, a, b, max_order):
    """Independent per-root Taylor guard; NEVER a whole-span conclusion."""
    point, interval = single.point, single.interval
    event = point.point(span, root, max_order=max_order)
    require(event.get("status") == "EXACT_RATIONAL_POINT_EVENT" and
            event.get("source_binding_sha256") == point.span_binding(span) and
            event.get("coordinate") == str(root) and
            type(event.get("first_nonzero_derivative_order")) is int and
            event["first_nonzero_derivative_order"] >= 2,
            "EXACT_NONTRANSVERSE_JET_NOT_ESTABLISHED")
    m = event["first_nonzero_derivative_order"]
    sign = event["first_nonzero_derivative_sign"]
    require(m <= max_order and sign in (-1, 1) and
            event.get("one_sided_order") == m and
            event.get("exact_vanishing_derivatives") == list(range(m)),
            "INCOMPLETE_EXACT_RATIONAL_JET")
    upper = single.derivative_limit(span, m+1)
    center = point.derivative_interval(span, root, m)
    checked = interval.widen(center, upper * max(root-a, b-root))
    require(interval.strict_sign(checked) == sign,
            "LOCAL_MTH_DERIVATIVE_SIGN_UNDECIDED")
    left_sign = sign if m % 2 == 0 else -sign
    right_sign = sign
    require(event.get("left_sign") == left_sign and
            event.get("right_sign") == right_sign and
            event.get("event_kind") ==
            ("TANGENCY" if m % 2 == 0 else "CROSSING"),
            "JET_GUARD_PARITY_INCONSISTENT")
    require(interval.strict_sign(span.evaluate(a)) == left_sign and
            interval.strict_sign(span.evaluate(b)) == right_sign,
            "GUARD_ENDPOINT_EXACT_SIGN_UNDECIDED")
    return {
        "root": str(root),
        "multiplicity": m,
        "kind": event["event_kind"],
        "left_sign": left_sign,
        "right_sign": right_sign,
        "guard": [str(a), str(b)],
        "global_abs_derivative_m_plus_1_bound": str(upper),
        "mth_derivative_guard_enclosure": [str(checked[0]), str(checked[1])],
        "point_jet": event,
    }


def prove(source, roots, guards, *, max_order=4, max_depth=18,
          max_nodes=20000):
    pins()
    require(type(max_order) is int and 2 <= max_order <= 6 and
            type(max_depth) is int and 0 <= max_depth <= 18 and
            type(max_nodes) is int and 1 <= max_nodes <= 20000,
            "INVALID_PROOF_RESOURCE_BUDGET")
    require(type(roots) is list and 2 <= len(roots) <= 8 and
            type(guards) is list and len(guards) == len(roots),
            "INVALID_FINITE_ROOT_GUARD_CARDINALITY")
    span = single.source_span(source)
    xs = [rational(s) for s in roots]
    pairs = []
    for pair in guards:
        require(type(pair) is list and len(pair) == 2,
                "INVALID_RATIONAL_GUARD_PAIR")
        pairs.append((rational(pair[0]), rational(pair[1])))
    for i, (r, (a, b)) in enumerate(zip(xs, pairs)):
        require(span.left < a < r < b < span.right,
                "RATIONAL_ROOT_NOT_STRICTLY_INSIDE_OWN_GUARD")
        if i:
            require(xs[i-1] < r and pairs[i-1][1] < a,
                    "UNORDERED_OR_OVERLAPPING_EXACT_ROOT_GUARDS")

    events = [guard_proof(span, r, a, b, max_order)
              for r, (a, b) in zip(xs, pairs)]
    gaps = [(span.left, pairs[0][0], events[0]["left_sign"])]
    for i in range(len(xs)-1):
        require(events[i]["right_sign"] == events[i+1]["left_sign"],
                "INTER_GUARD_SIGN_PARITY_CONFLICT")
        gaps.append((pairs[i][1], pairs[i+1][0],
                     events[i]["right_sign"]))
    gaps.append((pairs[-1][1], span.right, events[-1]["right_sign"]))
    m1 = single.derivative_limit(span, 1)
    covers = []
    cumulative_nodes = 0
    for i, (a, b, sign) in enumerate(gaps):
        require(a < b, "INCOMPLETE_OR_OVERLAPPING_SOURCE_COVER")
        require(single.interval.strict_sign(span.evaluate(a)) == sign and
                single.interval.strict_sign(span.evaluate(b)) == sign,
                "GAP_ENDPOINT_SIGN_UNPROVED")
        remaining = max_nodes - cumulative_nodes
        require(remaining > 0, "TOTAL_COMPLEMENT_COVER_NODE_RESOURCE_LIMIT")
        part = single.no_root_cover(
            span, a, b, sign, m1,
            {"max_nodes": remaining, "max_depth": max_depth})
        cumulative_nodes += part["nodes"]
        require(cumulative_nodes <= max_nodes,
                "TOTAL_COMPLEMENT_COVER_NODE_RESOURCE_LIMIT")
        part["gap_index"] = i
        covers.append(part)

    # Ordered guard and gap intervals form a strictly contiguous partition
    # [L,a0] + [a0,b0] + [b0,a1] ... [bn,R].
    cursor = span.left
    for i, event in enumerate(events):
        require(rational(covers[i]["source_interval"][0]) == cursor and
                rational(covers[i]["source_interval"][1]) == pairs[i][0],
                "SOURCE_PARTITION_GAP_OR_UNJUSTIFIED_OVERLAP")
        cursor = pairs[i][1]
    require(rational(covers[-1]["source_interval"][0]) == cursor and
            rational(covers[-1]["source_interval"][1]) == span.right,
            "FINAL_SOURCE_PARTITION_GAP")
    pins()
    return {
        "schema": SCHEMA,
        "status": "COMPLETE_ORDERED_MULTIPLE_NONTRANSVERSE_ROOTS_RESEARCH",
        "evidence_class": "DETERMINISTIC_MODEL",
        "source_parameter_id": source["source_parameter_id"],
        "source_sha256": hashlib.sha256(
            single.canonical(source).encode("ascii")).hexdigest(),
        "source_binding_sha256": single.point.span_binding(span),
        "source_interval": [str(span.left), str(span.right)],
        "phase_turns": [str(span.offset), str(span.rate)],
        "root_count": len(xs),
        "ordered_rational_roots": [str(r) for r in xs],
        "ordered_multiplicities": [e["multiplicity"] for e in events],
        "ordered_event_kinds": [e["kind"] for e in events],
        "gap_signs": [g[2] for g in gaps],
        "global_abs_derivative_1_bound": str(m1),
        "root_guard_witnesses": events,
        "complete_complement_covers": covers,
        "total_cover_nodes": cumulative_nodes,
        "historical_v54_dispositions_changed": False,
        "frozen_v27_v41_owner_certified": False,
        "pb00701_certified": False,
        "mc_b_established": False,
        "mc1_established": False,
        "native_brep_or_step_qualified": False,
        "production_authorized": False,
    }


def nontruth(reason, status="BLOCKED"):
    return {"schema": SCHEMA, "status": status, "reason": reason,
            "is_truth_value": False, "historical_child_certified": False,
            "mc_b_established": False, "production_authorized": False}


def attempt(source, roots, guards, **budget):
    try:
        return prove(source, roots, guards, **budget)
    except (Refusal, single.Refusal, single.point.Refusal,
            single.interval.Refusal, ValueError, TypeError, KeyError,
            IndexError, OverflowError, ZeroDivisionError) as exc:
        reason = str(exc)
        status = "RESOURCE_REFUSAL" if any(x in reason for x in
                  ("RESOURCE", "UNDECIDED", "UNRESOLVED", "EXHAUSTED")) else "BLOCKED"
        return nontruth(reason, status)
    except (MemoryError, RecursionError) as exc:
        return nontruth(type(exc).__name__, "RESOURCE_REFUSAL")


def validate_report(source, roots, guards, submitted, **budget):
    try:
        claimed = single.canonical(submitted)
        if len(claimed) > MAX_CERT_BYTES:
            return nontruth("SUBMITTED_REPORT_RESOURCE_LIMIT", "RESOURCE_REFUSAL")
        proof = attempt(source, roots, guards, **budget)
        require(proof.get("status") ==
                "COMPLETE_ORDERED_MULTIPLE_NONTRANSVERSE_ROOTS_RESEARCH",
                "EXACT_COMPLETE_MULTIPLE_ROOT_PROOF_MISSING")
        require(claimed == single.canonical(proof),
                "FORGED_COMPLETE_MULTIPLE_ROOT_REPORT")
        return proof
    except (Refusal, single.Refusal, ValueError, TypeError, OverflowError) as exc:
        return nontruth(str(exc))
    except (MemoryError, RecursionError) as exc:
        return nontruth(type(exc).__name__, "RESOURCE_REFUSAL")
