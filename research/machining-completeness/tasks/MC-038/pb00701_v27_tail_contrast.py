#!/usr/bin/env python3
"""MC-038 bounded exact source-tail contrast, not physical event identity.

For two different frozen original V27 histories, lower every source harmonic
before comparing their *second* restrictions. A certified strictly positive
difference G-F, together with independently proved unique negative-to-positive
simple roots, gives root(G) < root(F) without interval-disjointness as a premise.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as Q
from functools import lru_cache
from math import comb
from pathlib import Path

import pb00701_transverse_original_source as original
import pb00701_dual_implicit_roots as dual

TASK = Path(__file__).resolve().parent
SCHEMA = "radicadsac-pb00701-v27-tail-contrast/1.0"
LEFT = original.v27.TAIL0
RIGHT = original.v27.TAIL100
PARAMETER = "source-time-t"
PRODUCERS = {
    TASK / "pb00701_transverse_original_source.py":
        "992ad17ddbdf34687bcb59acba46f672b2d4a1c4",
    TASK / "pb00701_dual_implicit_roots.py":
        "9a7aee7f784e9aa37b4348b2bd78f047ba885fd4",
}

class Refusal(ValueError):
    pass

def need(ok, reason):
    if not ok:
        raise Refusal(reason)

def pin_sources():
    for path, expected in PRODUCERS.items():
        raw = path.read_bytes()
        actual = hashlib.sha1(
            b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
        need(actual == expected, "PINNED_PRODUCER_DRIFT:" + path.name)
    dual.check_pins()
    original.custody()

def canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False)
    except (ValueError, TypeError, OverflowError) as exc:
        raise Refusal("NONCANONICAL_RESULT") from exc

def rational(x):
    need(type(x) in (str, int, Q), "NONEXACT_RATIONAL_TYPE")
    if type(x) is str:
        need(0 < len(x) <= 128, "RATIONAL_LITERAL_RESOURCE_LIMIT")
    try:
        y = Q(x)
    except (ValueError, TypeError, ZeroDivisionError, OverflowError) as exc:
        raise Refusal("INVALID_EXACT_RATIONAL") from exc
    need(y.numerator.bit_length() <= 128 and
         y.denominator.bit_length() <= 128, "RATIONAL_RESOURCE_LIMIT")
    return y

def trim(coefficients):
    a = [rational(x) for x in coefficients]
    need(0 < len(a) <= 16, "POLYNOMIAL_DEGREE_RESOURCE_LIMIT")
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a

def subtract(a, b):
    """a - b, exact coefficientwise with absent coefficients equal to zero."""
    a, b = trim(a), trim(b)
    return trim([(a[i] if i < len(a) else Q(0)) -
                 (b[i] if i < len(b) else Q(0))
                 for i in range(max(len(a), len(b)))])

def source_tail_contrast(left, right):
    """Reconstruct the complete function difference, not only a selected term."""
    for row in (left, right):
        spec = row["spec"]
        need(row["kind"] == "COMPOSITE_TAIL" and
             spec["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE" and
             spec["source_parameter_id"] == PARAMETER and
             (rational(spec["parameter_lo"]), rational(spec["parameter_hi"])) ==
             (Q(0), Q(2)), "ORIGINAL_SOURCE_GRAMMAR_MISMATCH")
        need((rational(spec["phase_turn_offset"]),
              rational(spec["phase_turn_rate"])) == (Q(1, 2), Q(-2, 3)),
             "ORIGINAL_AFFINE_PHASE_MISMATCH")
    need(left["id"] == LEFT and right["id"] == RIGHT and
         original.source_binding(left) != original.source_binding(right),
         "NOT_DISTINCT_PINNED_ORIGINAL_HISTORIES")
    lowerer = original.v27.exact_lowerer()
    la = original.original_spans(left, lowerer)
    rb = original.original_spans(right, lowerer)
    need(len(la) == len(rb) == 2 and
         la[1]["interval"] == rb[1]["interval"] == (Q(1), Q(2)),
         "SECOND_SOURCE_SPAN_MISSING")
    need(la[1]["owner"] == original.v27.OWNER and
         rb[1]["owner"] == original.v27.V19,
         "DISTINCT_ORIGINAL_SECOND_SPAN_OWNERS_NOT_PRESERVED")
    terms_a, terms_b = la[1]["terms"], rb[1]["terms"]
    h0_delta = None
    checked_channels = []
    for h in sorted(set(terms_a) | set(terms_b)):
        for channel, name in enumerate(("cos", "sin")):
            ca = terms_a[h][channel] if h in terms_a else (Q(0),)
            cb = terms_b[h][channel] if h in terms_b else (Q(0),)
            delta = subtract(cb, ca)
            checked_channels.append({"harmonic": h, "channel": name,
                                     "difference": [str(x) for x in delta]})
            if h == 0 and channel == 0:
                h0_delta = delta
            else:
                need(delta == [0], "UNCANCELLED_TRIG_HARMONIC_DIFFERENCE")
    need(h0_delta is not None and h0_delta != [0],
         "NO_NONZERO_RATIONAL_SOURCE_CONTRAST")
    return h0_delta, checked_channels, la[1], rb[1]

def positive_contrast_on_unit_tail(poly_t):
    """Sufficient exact positivity: D(1+u)=u^k R(u), Bernstein R>0.

    For 0<u<=1, u^k>0. Every Bernstein basis value is nonnegative,
    sums to one, and strictly positive coefficients imply R(u)>0.
    This is NOT a complete positivity/functional-equivalence decision.
    """
    p = trim(poly_t)
    # Exact translation t=1+u, using binomial expansion of each t^i.
    shifted = trim([sum(p[i] * comb(i, j) for i in range(j, len(p)))
                    for j in range(len(p))])
    need(shifted != [0], "IDENTITY_ZERO_CONTRAST")
    order = next(i for i, v in enumerate(shifted) if v != 0)
    need(order >= 1, "SOURCE_KNOT_CONTRAST_NOT_ZERO")
    quotient = shifted[order:]
    n = len(quotient) - 1
    bernstein = [
        sum(quotient[j] * Q(comb(k, j), comb(n, j))
            for j in range(k + 1))
        for k in range(n + 1)]
    need(all(0 < x and x.numerator.bit_length() <= 4096 and
             x.denominator.bit_length() <= 4096 for x in bernstein),
         "STRICT_POSITIVE_BERNSTEIN_WITNESS_NOT_AVAILABLE")
    return {"difference_polynomial_t": [str(x) for x in p],
            "difference_polynomial_u": [str(x) for x in shifted],
            "source_knot_order": order,
            "positive_quotient_bernstein": [str(x) for x in bernstein],
            "certified_interval_t": ["1", "2"],
            "certified_strict_on": "1<t<=2"}

def unique_tail_crossing(part):
    proof = part["span"].prove(max_depth=14, max_nodes=20000)
    roots = [c for c in proof["partition"] if c["kind"] == "ONE_SIMPLE_ROOT"]
    need(proof["source_interval"] == ["1", "2"] and
         proof["endpoint_signs"] == [-1, 1] and
         proof["complete_simple_root_count"] == len(roots) == 1,
         "TAIL_NOT_COMPLETE_UNIQUE_NEG_TO_POS_ROOT")
    root = roots[0]
    need(root["smooth_multiplicity"] == 1 and
         root["left_sign"] == -1 and root["right_sign"] == 1 and
         Q(1) <= rational(root["strict_isolation"][0]) <
         rational(root["strict_isolation"][1]) <= Q(2),
         "TAIL_ROOT_NOT_STRICT_SIMPLE_CROSSING")
    return root["strict_isolation"]

def _build():
    pin_sources()
    index = original.custody()
    need(LEFT in index and RIGHT in index, "PINNED_SOURCE_CASE_MISSING")
    a, b = index[LEFT], index[RIGHT]
    difference, channels, left_tail, right_tail = source_tail_contrast(a, b)
    positive = positive_contrast_on_unit_tail(difference)
    lbracket = unique_tail_crossing(left_tail)
    rbracket = unique_tail_crossing(right_tail)
    # Distinct complete source-proof methods, checked separately. These are
    # corroboration, not the mathematical premise for the contrast-order lemma.
    records = dual.catalogue()
    for case, row, bracket in ((LEFT, a, lbracket), (RIGHT, b, rbracket)):
        report = records[case]
        need(report["status"] == "SAME_SOURCE_DUAL_ROOT_PROOFS_RECONCILED" and
             report["case_id"] == case and
             report["complete_open_roots"] == 2 and
             report["transverse_source_sha256"] == original.source_binding(row) and
             report["source_parameter_id"] == PARAMETER and
             report["root_matches"][1]["source_span"] == ["1", "2"] and
             report["root_matches"][1]["smooth_multiplicity"] == 1,
             "SECOND_METHOD_SOURCE_OR_ROOT_PROOF_MISSING")
        need(rational(bracket[0]) < rational(bracket[1]),
             "INVALID_SOURCE_PROOF_BRACKET")
    pin_sources()
    return {
        "schema": SCHEMA, "status": "CHECKED_STRICT_SOURCE_TAIL_CONTRAST",
        "evidence_class": "DETERMINISTIC_MODEL",
        "case_ids": [LEFT, RIGHT],
        "whole_source_sha256": [original.source_binding(a),
                                original.source_binding(b)],
        "source_parameter": PARAMETER,
        "phase_turns": ["1/2", "-2/3"],
        "original_second_span_owners":
            [left_tail["owner"], right_tail["owner"]],
        "all_original_harmonic_differences_checked": channels,
        "strict_positive_difference_certificate": positive,
        "unique_second_root_strict_brackets": [lbracket, rbracket],
        "root_order_relation": "RIGHT_LESS_THAN_LEFT",
        "root_noncoincidence_proved": True,
        "order_reason": "STRICT_POSITIVE_RIGHT_MINUS_LEFT_AND_EACH_UNIQUE_NEG_TO_POS_ROOT",
        "disjoint_brackets_needed_for_order_proof": False,
        "shared_knot_difference_zero": True,
        "source_parameter_math_only": True,
        "common_physical_clock_or_event_claimed": False,
        "shared_manufacturing_journal_or_material_claimed": False,
        "general_nontransverse_or_composition_proved": False,
        "historical_v54_dispositions_changed": False,
        "pb00701_certified": False, "mc_b_established": False,
        "mc1_established": False, "native_brep_or_step_qualified": False,
        "production_authorized": False,
    }

@lru_cache(maxsize=1)
def _replayed():
    return canonical(_build())

def checked_result():
    pin_sources()
    result = json.loads(_replayed())
    pin_sources()
    return result

def refusal(reason, status="BLOCKED"):
    return {"schema": SCHEMA, "status": status, "reason": str(reason),
            "is_truth_value": False, "pb00701_certified": False,
            "mc_b_established": False, "production_authorized": False}

def attempt():
    try:
        return checked_result()
    except (Refusal, original.InvalidOriginal, dual.Refusal, ValueError,
            TypeError, KeyError, IndexError, OverflowError) as exc:
        return refusal(str(exc))
    except (MemoryError, RecursionError):
        return refusal("RUNTIME_RESOURCE_LIMIT", "RESOURCE_REFUSAL")

def validate_claim(candidate):
    try:
        need(type(candidate) is dict, "CLAIM_NOT_OBJECT")
        data = canonical(candidate)
        if len(data) > 16384:
            return refusal("REPORT_RESOURCE_LIMIT", "RESOURCE_REFUSAL")
        actual = checked_result()
        need(data == canonical(actual), "UNVERIFIED_OR_FORGED_CONTRAST_CLAIM")
        return actual
    except (Refusal, original.InvalidOriginal, dual.Refusal, ValueError,
            TypeError, KeyError, IndexError, OverflowError) as exc:
        return refusal(str(exc))
    except (MemoryError, RecursionError):
        return refusal("RUNTIME_RESOURCE_LIMIT", "RESOURCE_REFUSAL")
