#!/usr/bin/env python3
"""Exact same-source root-rank reconciliation between two bounded proof producers.

Only the three pinned V27/V41 original-source cases are admitted. Two strict
brackets overlapping does not imply equality: only two independent COMPLETE
ordered-root proofs for the SAME physical function justify same-index identity.
"""
from __future__ import annotations
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
from pathlib import Path

import pb00701_pinned_trig_child_views as fixed
import pb00701_transverse_original_source as transverse

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[3]
SCHEMA = "radicadsac-pb00701-dual-implicit-roots/1.0"
CASES = fixed.CASES
PINS = {
    TASK / "pb00701_pinned_trig_child_views.py": "c4a4d865226d01858d93685aa770987b14460e0b",
    TASK / "pb00701_transverse_original_source.py": "992ad17ddbdf34687bcb59acba46f672b2d4a1c4",
    TASK / "pb00701_transverse_trig_interval.py": "2320f92efe4316d865a89f6d848737e2c000ca4d",
    TASK / "pb00701-finite-owner-corpus-v54.json": "5841c331579489b25caef38cd412bdbf286f9134",
    ROOT / "handoffs/current-authority.json": "fa0233323a0804d8a5d3eb7cd892a274a6173fab",
    ROOT / "research/machining-completeness/tasks/MC-002/domain-contract-v1.json":
        "23de82f5240a72509f7afe4acd5948b65bc4ff13",
}

class Refusal(ValueError):
    pass

def require(ok, reason):
    if not ok:
        raise Refusal(reason)

def canonical(obj):
    try:
        return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False)
    except (ValueError, TypeError, OverflowError) as exc:
        raise Refusal("NONEXACT_OR_NONJSON_CERTIFICATE") from exc

def check_pins():
    for path, expected in PINS.items():
        raw = path.read_bytes()
        sha = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(sha == expected, "SOURCE_OR_PRODUCER_DRIFT:" + path.name)

def rational(value):
    require(type(value) is str and 0 < len(value) <= 128,
            "NONCANONICAL_RATIONAL_TYPE")
    try:
        q = Q(value)
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise Refusal("BAD_EXACT_RATIONAL") from exc
    require(str(q) == value and q.numerator.bit_length() <= 128 and
            q.denominator.bit_length() <= 128, "NONCANONICAL_RATIONAL")
    return q

def _reconcile_one(case_id, frozen, fixed_proofs, lowerer):
    row = frozen[case_id]
    f_input = fixed.reference_view(case_id, fixed_proofs)
    f = fixed.compose(f_input)
    t = transverse.original_case(case_id, frozen, lowerer)
    require(f["source_case_id"] == t["source_case_id"] == row["id"],
            "DIFFERENT_ORIGINAL_SOURCE")
    # The producer hash schemas intentionally differ (case_id versus id).
    # Bind each independently to the identical frozen physical source record.
    require(f["source_binding_sha256"] == fixed.source_binding(row) and
            t["source_binding_sha256"] == transverse.source_binding(row),
            "SOURCE_HASH_OR_GRAMMAR_DISAGREEMENT")
    require(f_input["source_parameter_id"] == t["source_parameter_id"] ==
            row["spec"]["source_parameter_id"], "SOURCE_PARAMETER_MISMATCH")
    require(t["phase_turns"] == [row["spec"]["phase_turn_offset"],
            row["spec"]["phase_turn_rate"]], "SOURCE_PHASE_MISMATCH")
    require(t["historical_v54_disposition"] == row["expected"]["v54_disposition"],
            "HISTORICAL_DISPOSITION_MISMATCH")
    require(f["status"] == "PINNED_TRIGONOMETRIC_CHILD_VIEWS_RECONCILED_RESEARCH_ONLY"
            and t["status"] == "CHECKED_BOUNDED_TRANSVERSE_RESEARCH",
            "MISSING_COMPLETE_ROOT_PROOF")
    a, b = f["ordered_implicit_root_events"], t["ordered_implicit_roots"]
    require(f["distinct_open_roots_proved_for_this_fixed_source"] ==
            t["complete_simple_open_roots"] == len(a) == len(b) == 2,
            "INCOMPLETE_OR_COUNT_ONLY_ROOT_PROOF")
    signs = [c["sign"] for c in f["maximal_open_physical_sign_cells"]]
    require(signs == ["POSITIVE" if s == 1 else "NEGATIVE" if s == -1
                       else "UNDECIDED" for s in t["maximal_physical_signs"]],
            "SOURCE_PHYSICAL_SIGN_CELLS_MISMATCH")
    require(t["true_knot_zero_supported"] is False,
            "UNSUPPORTED_KNOT_ZERO")
    for knot in f["true_source_knots"]:
        require(knot["is_physical_zero"] is False and
                knot["left_sign"] == knot["right_sign"] == "NEGATIVE",
                "KNOT_SOURCE_CONTRADICTION")
    matches = []
    prior_end = None
    for rank, (x, y) in enumerate(zip(a, b)):
        require(x["source_case_id"] == case_id and
                x["smooth_physical_multiplicity"] ==
                y["smooth_multiplicity"] == 1 and
                x["parity"] == "ODD_CROSSING" and
                y["crossing"] in ("POSITIVE_TO_NEGATIVE", "NEGATIVE_TO_POSITIVE"),
                "MISSING_SIMPLE_ROOT_OR_PARITY")
        expect_left = ("POSITIVE" if y["crossing"] == "POSITIVE_TO_NEGATIVE"
                       else "NEGATIVE")
        expect_right = ("NEGATIVE" if expect_left == "POSITIVE" else "POSITIVE")
        require(x["left_sign"] == expect_left and
                x["right_sign"] == expect_right, "ROOT_CROSSING_DISAGREEMENT")
        owner = [c["owner"] for c in f_input["children"]
                 if c["interval"] == x["source_span"]]
        require(len(owner) == 1 and owner[0] == y["owner"],
                "PHYSICAL_SOURCE_OWNER_DISAGREEMENT")
        sl, sr = map(rational, x["source_span"])
        fl, fr = map(rational, x["strict_bracket"])
        tl, tr = map(rational, y["strict_bracket"])
        require(sl <= fl < fr <= sr and sl <= tl < tr <= sr,
                "ROOT_BRACKET_OUTSIDE_SOURCE_SPAN")
        # Equality follows from same rank in two independently COMPLETE
        # lists for the same F, never merely from bracket overlap.
        lo, hi = max(fl, tl), min(fr, tr)
        require(lo < hi, "CONTRADICTORY_SAME_RANK_BRACKETS")
        if prior_end is not None:
            require(prior_end <= lo, "DUPLICATED_OR_REORDERED_ROOTS")
        prior_end = hi
        matches.append({
            "rank": rank,
            "relation": "SAME_SOURCE_ROOT_BY_TWO_COMPLETE_ORDERED_PROOFS",
            "owner": owner[0], "source_span": x["source_span"],
            "fixed_bracket": x["strict_bracket"],
            "transverse_bracket": y["strict_bracket"],
            "strict_intersection_bracket": [str(lo), str(hi)],
            "smooth_multiplicity": 1, "crossing": y["crossing"],
            "source_root_closed_form_claimed": False,
        })
    require(all(f[k] is False for k in (
        "historical_child_certified", "general_v27_v41_theorem_claimed",
        "pb00701_certified", "mc_b_established", "mc1_established",
        "native_brep_or_step_qualified", "production_authorized")) and
        all(t[k] is False for k in (
        "historical_child_certified", "general_trig_theorem_claimed",
        "mc_b_mc1_native_brep_step_claimed", "production_authorized")),
        "PRODUCER_CAPABILITY_PROMOTION")
    return {
        "schema": SCHEMA, "status": "SAME_SOURCE_DUAL_ROOT_PROOFS_RECONCILED",
        "case_id": case_id, "source_parameter_id": row["spec"]["source_parameter_id"],
        "fixed_source_sha256": fixed.source_binding(row),
        "transverse_source_sha256": transverse.source_binding(row),
        "source_phase_turns": t["phase_turns"],
        "historical_v54_disposition": t["historical_v54_disposition"],
        "root_matches": matches, "complete_open_roots": len(matches),
        "physical_signs": signs,
        "overlap_alone_is_not_root_equality_evidence": True,
        "source_root_closed_form_claimed": False,
        "historical_child_certified": False, "general_v27_v41_theorem": False,
        "nontransverse_qualified": False, "pb00701_certified": False,
        "mc_b_established": False, "mc1_established": False,
        "native_brep_or_step_qualified": False, "production_authorized": False,
    }

@lru_cache(maxsize=1)
def _catalogue_json():
    check_pins()
    fixed_proofs = fixed.replay_original_proofs()
    frozen = transverse.custody()
    lowerer = transverse.v27.exact_lowerer()
    reports = {case: _reconcile_one(case, frozen, fixed_proofs, lowerer)
               for case in CASES}
    check_pins()
    return canonical(reports)

def catalogue():
    check_pins()
    return json.loads(_catalogue_json())

def refusal(reason, status="BLOCKED"):
    return {"schema": SCHEMA, "status": status, "reason": reason,
            "is_truth_value": False, "historical_child_certified": False,
            "mc_b_established": False, "production_authorized": False}

def validate(candidate):
    """Caller-provided roots are not authority; reconstruct both exact proofs."""
    try:
        data = canonical(candidate)
        if len(data) > 16384:
            return refusal("REPORT_RESOURCE_LIMIT", "RESOURCE_REFUSAL")
        require(type(candidate) is dict and candidate.get("case_id") in CASES,
                "UNSUPPORTED_ORIGINAL_SOURCE")
        expected = catalogue()[candidate["case_id"]]
        require(data == canonical(expected), "UNVERIFIED_ROOT_PROOF_OR_FORGED_METADATA")
        return expected
    except (Refusal, KeyError, IndexError, TypeError, fixed.InvalidView,
            transverse.InvalidOriginal) as exc:
        return refusal(str(exc))
    except (MemoryError, OverflowError, RecursionError):
        return refusal("RUNTIME_RESOURCE_LIMIT", "RESOURCE_REFUSAL")

def compare(left_report, i, right_report, j):
    left, right = validate(left_report), validate(right_report)
    if left.get("status") != "SAME_SOURCE_DUAL_ROOT_PROOFS_RECONCILED" or (
        right.get("status") != "SAME_SOURCE_DUAL_ROOT_PROOFS_RECONCILED"):
        return refusal("MISSING_PROVED_SOURCE_ROOTS")
    if left["case_id"] != right["case_id"] or (
        left["transverse_source_sha256"] != right["transverse_source_sha256"]):
        return refusal("DIFFERENT_ORIGINAL_SOURCE")
    if (type(i) is not int or type(j) is not int or
        i not in range(len(left["root_matches"])) or
        j not in range(len(right["root_matches"]))):
        return refusal("UNPROVED_OR_NONINTEGER_RANK")
    return {"schema": SCHEMA, "status": "CHECKED_SAME_SOURCE_ORDER",
            "case_id": left["case_id"], "left_rank": i, "right_rank": j,
            "relation": "SAME" if i == j else "LESS" if i < j else "GREATER",
            "source_sha256": left["transverse_source_sha256"],
            "historical_child_certified": False,
            "mc_b_established": False, "production_authorized": False}
