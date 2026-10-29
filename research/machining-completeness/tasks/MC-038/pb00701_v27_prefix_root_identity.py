#!/usr/bin/env python3
"""MC-038: exact original-source restriction identity across two V27 histories.

Only two pinned V27 tail histories: common first source restriction means the
unique simple root on [0,1] is SAME despite distinct complete source records.
The second roots are strictly ordered from a different checked interval proof.
This is source-parameter arithmetic, not manufacturing-event/journal identity.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path

import pb00701_cross_source_strict_order as cross
import pb00701_dual_implicit_roots as dual
import pb00701_transverse_original_source as original

TASK = Path(__file__).resolve().parent
SCHEMA = "radicadsac-pb00701-v27-identical-prefix-root/1.0"
LEFT_CASE = original.v27.TAIL0
RIGHT_CASE = original.v27.TAIL100
PARAMETER = "source-time-t"
PRODUCERS = {
    TASK / "pb00701_cross_source_strict_order.py":
        "2ed13e8aa5ab3223af147250ecacc4688194c8d8",
    TASK / "pb00701_dual_implicit_roots.py":
        "9a7aee7f784e9aa37b4348b2bd78f047ba885fd4",
    TASK / "pb00701_transverse_original_source.py":
        "992ad17ddbdf34687bcb59acba46f672b2d4a1c4",
}

class Refusal(ValueError):
    pass

def require(test, code):
    if not test:
        raise Refusal(code)

def exact_json(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False)
    except (TypeError, ValueError, OverflowError) as exc:
        raise Refusal("NONEXACT_OR_NONJSON_CLAIM") from exc

def pin_sources():
    for path, expected in PRODUCERS.items():
        raw = path.read_bytes()
        actual = hashlib.sha1(
            b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
        require(actual == expected, "ORIGINAL_PROOF_PRODUCER_DRIFT:" + path.name)
    cross.source_pins()
    dual.check_pins()

def canonical_poly(coefficients):
    data = [Q(x) for x in coefficients]
    while len(data) > 1 and data[-1] == 0:
        data.pop()
    return [str(x) for x in data]

def canonical_restriction(row, lowerer):
    """Sufficient EXACT function-identity witness; no claim of complete equivalence."""
    spec = row["spec"]
    require(spec["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE" and
            spec["source_parameter_id"] == PARAMETER and
            Q(spec["parameter_lo"]) == 0 and Q(spec["parameter_hi"]) == 2,
            "SOURCE_DOMAIN_OR_PARAMETER_MISMATCH")
    parts = original.original_spans(row, lowerer)
    require(len(parts) == 2 and
            parts[0]["interval"] == (Q(0), Q(1)) and
            parts[1]["interval"] == (Q(1), Q(2)),
            "SOURCE_KNOTS_OR_INTERVALS_CHANGED")
    require(parts[0]["owner"] == original.v27.OWNER,
            "HISTORICAL_FIRST_SPAN_OWNER_DRIFT")
    phase = [str(Q(spec["phase_turn_offset"])),
             str(Q(spec["phase_turn_rate"]))]
    def terms(part):
        return [
            {"harmonic": h,
             "cos_poly": canonical_poly(co[0]),
             "sin_poly": canonical_poly(co[1])}
            for h, co in sorted(part["terms"].items())
        ]
    # Equality of exact harmonic channel polynomials with the same affine
    # phase suffices to prove equal restricted real functions for ALL s.
    return {
        "source_parameter": PARAMETER,
        "interval": ["0", "1"],
        "phase_turns": phase,
        "owner": parts[0]["owner"],
        "original_harmonic_coefficients": terms(parts[0]),
    }, terms(parts[1]), parts

def prove_restricted_equality(left_row, right_row, lowerer):
    """Mathematical lemma only; caller MUST separately pin source identities."""
    a, tail_a, parts_a = canonical_restriction(left_row, lowerer)
    b, tail_b, parts_b = canonical_restriction(right_row, lowerer)
    require(a == b, "FIRST_SPAN_ORIGINAL_SOURCE_EXPRESSIONS_DIFFER")
    require(tail_a != tail_b, "DIVERGENT_TAIL_NEGATIVE_CONTROL_IS_VACUOUS")
    return a, parts_a[0], parts_b[0]

def first_transverse_simple_root(part):
    # A complete sign/derivative dyadic partition is rebuilt for each source.
    proof = part["span"].prove(max_depth=14, max_nodes=20000)
    roots = [p for p in proof["partition"] if p["kind"] == "ONE_SIMPLE_ROOT"]
    require(proof["complete_simple_root_count"] == len(roots) == 1 and
            proof["endpoint_signs"] == [1, -1] and
            roots[0]["smooth_multiplicity"] == 1 and
            roots[0]["left_sign"] == 1 and roots[0]["right_sign"] == -1,
            "FIRST_SPAN_NOT_PROVED_SINGLE_SIMPLE_CROSSING")
    return roots[0]["strict_isolation"]

def strict_intersection(*brackets):
    intervals = []
    for bracket in brackets:
        require(type(bracket) in (tuple, list) and len(bracket) == 2,
                "NOT_A_STRICT_SOURCE_BRACKET")
        a, b = map(dual.rational, bracket)
        require(a < b and 0 <= a and b <= 1,
                "ROOT_BRACKET_OUTSIDE_COMMON_FIRST_SPAN")
        intervals.append((a, b))
    lo, hi = max(x[0] for x in intervals), min(x[1] for x in intervals)
    require(lo < hi, "CONTRADICTORY_UNIQUE_ROOT_BRACKETS")
    return [str(lo), str(hi)]

def _build():
    pin_sources()
    index = original.custody()
    require(LEFT_CASE in index and RIGHT_CASE in index and
            LEFT_CASE != RIGHT_CASE, "MISSING_DISTINCT_V27_SOURCE_RECORDS")
    left_row, right_row = index[LEFT_CASE], index[RIGHT_CASE]
    left_proven = dual.catalogue()[LEFT_CASE]
    right_proven = dual.catalogue()[RIGHT_CASE]
    for case, row, proof in (
        (LEFT_CASE, left_row, left_proven),
        (RIGHT_CASE, right_row, right_proven)
    ):
        require(proof["status"] == "SAME_SOURCE_DUAL_ROOT_PROOFS_RECONCILED" and
                proof["case_id"] == case and
                proof["complete_open_roots"] == 2 and
                proof["fixed_source_sha256"] == dual.fixed.source_binding(row) and
                proof["transverse_source_sha256"] == original.source_binding(row) and
                proof["source_parameter_id"] == PARAMETER,
                "COMPLETE_FROZEN_SOURCE_ROOT_PROOF_MISSING")
        require(proof["physical_signs"] == ["POSITIVE","NEGATIVE","POSITIVE"] and
                proof["root_matches"][0]["source_span"] == ["0","1"] and
                proof["root_matches"][1]["source_span"] == ["1","2"] and
                all(root["smooth_multiplicity"] == 1 for root in
                    proof["root_matches"]),
                "ROOT_COUNT_OR_SOURCE_SPAN_PROOF_MISMATCH")
    require(left_proven["transverse_source_sha256"] !=
            right_proven["transverse_source_sha256"],
            "WHOLE_HISTORIES_NOT_DISTINCT")
    lowerer = original.v27.exact_lowerer()
    common, left_part, right_part = prove_restricted_equality(
        left_row, right_row, lowerer)
    # The same exact function on [0,1] has exactly one zero; independent
    # interval proofs on each source establish existence, uniqueness, signs.
    a = first_transverse_simple_root(left_part)
    b = first_transverse_simple_root(right_part)
    first_left = left_proven["root_matches"][0]
    first_right = right_proven["root_matches"][0]
    first_root = strict_intersection(
        a, b, first_left["strict_intersection_bracket"],
        first_right["strict_intersection_bracket"])
    order = cross.compare(left_proven, 1, right_proven, 1)
    require(order["status"] == "CHECKED_STRICT_PARAMETER_ORDER" and
            order["relation"] == "GREATER" and
            order["left_case_id"] == LEFT_CASE and
            order["right_case_id"] == RIGHT_CASE and
            order["physical_temporal_sequence_claimed"] is False and
            order["root_equality_claimed"] is False,
            "DIVERGENT_TAIL_STRICT_ORDER_NOT_ESTABLISHED")
    pin_sources()
    return {
        "schema": SCHEMA,
        "status": "CHECKED_IDENTICAL_PREFIX_ROOT_AND_DIVERGENT_TAIL",
        "evidence_class": "DETERMINISTIC_MODEL",
        "case_ids": [LEFT_CASE, RIGHT_CASE],
        "whole_source_sha256": [
            original.source_binding(left_row),
            original.source_binding(right_row)],
        "source_parameter": PARAMETER,
        "exact_common_restriction": common,
        "common_restriction_sha256":
            hashlib.sha256(exact_json(common).encode("ascii")).hexdigest(),
        "first_root": {
            "rank_in_each_original_source": 0,
            "relation": "SAME_UNIQUE_SOURCE_PARAMETER_ROOT",
            "proof": "EXACT_EQUAL_SOURCE_RESTRICTIONS_AND_EACH_HAS_ONE_SIMPLE_ROOT",
            "strict_rational_isolation": first_root,
            "multiplicity_in_each_span": 1,
            "crossing": "POSITIVE_TO_NEGATIVE",
            "coordinate_closed_form_claimed": False,
            "same_physical_manufacturing_event_claimed": False,
        },
        "divergent_second_roots": {
            "rank_in_each_original_source": 1,
            "relation": "LEFT_GREATER_THAN_RIGHT_SOURCE_PARAMETER_VALUE",
            "left_strict_bracket":
                left_proven["root_matches"][1]["strict_intersection_bracket"],
            "right_strict_bracket":
                right_proven["root_matches"][1]["strict_intersection_bracket"],
            "proved_by": "REPLAYED_STRICT_SOURCE_PARAMETER_BRACKET_SEPARATION",
            "same_physical_manufacturing_event_claimed": False,
        },
        "no_shared_physical_clock_or_journal_claimed": True,
        "historical_child_certified": False,
        "general_v27_v41_composition_proved": False,
        "nontransverse_events_qualified": False,
        "pb00701_certified": False, "mc_b_established": False,
        "mc1_established": False, "native_brep_or_step_qualified": False,
        "production_authorized": False,
    }

@lru_cache(maxsize=1)
def _replayed():
    return exact_json(_build())

def checked_result():
    pin_sources()
    result = json.loads(_replayed())
    pin_sources()
    return result

def refusal(code, status="BLOCKED"):
    return {"schema": SCHEMA, "status": status, "reason": code,
            "is_truth_value": False, "physical_event_identity_claimed": False,
            "pb00701_certified": False, "mc_b_established": False,
            "production_authorized": False}

def validate_claim(claim):
    try:
        payload = exact_json(claim)
        if len(payload) > 16384:
            return refusal("REPORT_RESOURCE_LIMIT", "RESOURCE_REFUSAL")
        require(type(claim) is dict, "CLAIM_NOT_OBJECT")
        expected = checked_result()
        require(payload == exact_json(expected),
                "FORGED_OR_UNCHECKED_PREFIX_ROOT_IDENTITY")
        return expected
    except (Refusal, original.InvalidOriginal, dual.Refusal,
            cross.Refusal, original.trig.Refusal, KeyError, ValueError,
            TypeError, IndexError, OverflowError) as exc:
        return refusal(str(exc))
    except (MemoryError, RecursionError):
        return refusal("RUNTIME_RESOURCE_LIMIT", "RESOURCE_REFUSAL")
