#!/usr/bin/env python3
"""Exact, source-bound *coordinate-only* comparison of separated implicit roots.

Uses two already-complete, pinned, separately validated original-source
reports from PR #299. Disjoint strict rational brackets establish < or > in
the SAME named source parameter; overlap never establishes SAME or order.
Different physical source histories are NOT composed or equated.
"""
from __future__ import annotations

from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

import pb00701_dual_implicit_roots as dual

SCHEMA = "radicadsac-pb00701-cross-source-strict-parameter-order/1.0"
SCOPE = "PINNED_CROSS_SOURCE_STRICT_RATIONAL_BRACKET_ORDER_ONLY"
PARAMETER = "source-time-t"
DUAL_BLOB = "9a7aee7f784e9aa37b4348b2bd78f047ba885fd4"


class Refusal(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise Refusal(reason)


def source_pins():
    path = Path(dual.__file__).resolve()
    need(path == dual.TASK / "pb00701_dual_implicit_roots.py",
         "UNEXPECTED_DUAL_PROOF_PATH")
    raw = path.read_bytes()
    digest = hashlib.sha1(
        b"blob " + str(len(raw)).encode() + b"\0" + raw
    ).hexdigest()
    need(digest == DUAL_BLOB, "DUAL_PROOF_SOURCE_DRIFT")
    dual.check_pins()


def refusal(reason, status="BLOCKED"):
    return {
        "schema": SCHEMA, "status": status, "reason": reason,
        "is_truth_value": False, "root_equality_claimed": False,
        "physical_temporal_sequence_claimed": False,
        "pb00701_certified": False, "mc_b_established": False,
        "mc1_established": False, "production_authorized": False,
    }


def _strict_bracket(item):
    bracket = item["strict_intersection_bracket"]
    need(type(bracket) is list and len(bracket) == 2,
         "UNSUPPORTED_ROOT_BRACKET")
    lo, hi = (dual.rational(s) for s in bracket)
    need(lo < hi, "NONSTRICT_ROOT_BRACKET")
    return lo, hi


def _relation(a, b):
    """Only strict interval separation; never infer equality from overlap."""
    al, ah = a
    bl, bh = b
    need(al < ah and bl < bh, "NONSTRICT_ROOT_BRACKET")
    if ah <= bl:
        return "LESS"
    if bh <= al:
        return "GREATER"
    raise Refusal("OVERLAPPING_BRACKETS_UNRESOLVED")


def compare(left_report, left_rank, right_report, right_rank):
    """Validated source-specific proof inputs; fail closed on every gap."""
    try:
        source_pins()
        left = dual.validate(left_report)
        right = dual.validate(right_report)
        accepted = "SAME_SOURCE_DUAL_ROOT_PROOFS_RECONCILED"
        for label, report in (("LEFT", left), ("RIGHT", right)):
            if report.get("status") != accepted:
                status = ("RESOURCE_REFUSAL" if
                          report.get("status") == "RESOURCE_REFUSAL" else
                          "BLOCKED")
                return refusal(label + "_COMPLETE_PROOF_MISSING", status)
        need(left["case_id"] != right["case_id"],
             "SAME_SOURCE_USE_DUAL_ROOT_RANK_PROOF")
        need(left["case_id"] in dual.CASES and
             right["case_id"] in dual.CASES,
             "UNPINNED_SOURCE_CASE")
        need(left["source_parameter_id"] ==
             right["source_parameter_id"] == PARAMETER,
             "SOURCE_PARAMETER_COORDINATE_MISMATCH")
        need(left["transverse_source_sha256"] !=
             right["transverse_source_sha256"],
             "SOURCE_RECORD_BINDING_AMBIGUITY")
        need(type(left_rank) is int and
             0 <= left_rank < left["complete_open_roots"] and
             type(right_rank) is int and
             0 <= right_rank < right["complete_open_roots"],
             "UNVERIFIED_OR_NONINTEGER_RANK")
        lhs = left["root_matches"][left_rank]
        rhs = right["root_matches"][right_rank]
        a, b = _strict_bracket(lhs), _strict_bracket(rhs)
        relation = _relation(a, b)
        source_pins()
        return {
            "schema": SCHEMA, "status": "CHECKED_STRICT_PARAMETER_ORDER",
            "scope": SCOPE, "coordinate_id": PARAMETER,
            "left_case_id": left["case_id"],
            "right_case_id": right["case_id"],
            "left_rank": left_rank, "right_rank": right_rank,
            "left_source_sha256": left["transverse_source_sha256"],
            "right_source_sha256": right["transverse_source_sha256"],
            "left_phase_turns": left["source_phase_turns"],
            "right_phase_turns": right["source_phase_turns"],
            "left_strict_bracket": lhs["strict_intersection_bracket"],
            "right_strict_bracket": rhs["strict_intersection_bracket"],
            "relation": relation, "distinct_source_records": True,
            "strict_separation_proved": True,
            "root_equality_claimed": False,
            "physical_temporal_sequence_claimed": False,
            "historical_child_certified": False,
            "general_implicit_root_theorem": False,
            "nontransverse_qualified": False,
            "pb00701_certified": False,
            "mc_b_established": False, "mc1_established": False,
            "native_brep_or_step_qualified": False,
            "production_authorized": False,
        }
    except (Refusal, dual.Refusal, KeyError, IndexError, TypeError,
            ValueError, OverflowError) as exc:
        return refusal(str(exc))
    except (MemoryError, RecursionError):
        return refusal("RUNTIME_RESOURCE_LIMIT", "RESOURCE_REFUSAL")


def validate_claim(left_report, left_rank, right_report, right_rank, claim):
    """No caller-supplied comparison or metadata is itself evidence."""
    try:
        serialized = json.dumps(
            claim, sort_keys=True, separators=(",", ":"),
            ensure_ascii=True, allow_nan=False)
        if len(serialized) > 16384:
            return refusal("REPORT_RESOURCE_LIMIT", "RESOURCE_REFUSAL")
        actual = compare(left_report, left_rank, right_report, right_rank)
        need(actual.get("status") == "CHECKED_STRICT_PARAMETER_ORDER",
             "SOURCE_PROOF_OR_STRICT_SEPARATION_MISSING")
        need(type(claim) is dict and serialized == json.dumps(
            actual, sort_keys=True, separators=(",", ":"),
            ensure_ascii=True, allow_nan=False),
             "FORGED_CROSS_SOURCE_ORDER_CLAIM")
        return actual
    except (Refusal, TypeError, ValueError, OverflowError) as exc:
        return refusal(str(exc))
    except (MemoryError, RecursionError):
        return refusal("RUNTIME_RESOURCE_LIMIT", "RESOURCE_REFUSAL")
