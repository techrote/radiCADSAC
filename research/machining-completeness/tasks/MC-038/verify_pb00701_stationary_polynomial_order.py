#!/usr/bin/env python3
"""MC-038 / PB-007-01: exact ordered roots for stationary-cardinal polynomial spans.

Research-only. This does not alter historical V6-V54 routes, select a general
analytic solver, or establish MC-B/MC-1/native/STEP capability.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
IDENTITY_HELPER = HERE / "verify_pb00701_affine_identity_frontier.py"
CORPUS = HERE / "pb00701-finite-owner-corpus-v54.json"
IDENTITY_HELPER_BLOB = "9fd150e97bce84fdb3c4bad075c9938f4df9136c"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
SCHEMA = "radicadsac-pb00701-stationary-polynomial-ordered-research/1.0"
OWNER = "EXACT_STATIONARY_PHASE_POLYNOMIAL"
MAX_BISECTIONS = 512
RESOURCE_ERRORS = (MemoryError, OverflowError, RecursionError)


class IsolationRefusal(RuntimeError):
    pass


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def load_identity_helper():
    require(git_blob(IDENTITY_HELPER.read_bytes()) == IDENTITY_HELPER_BLOB,
            "landed affine-identity helper drifted")
    spec = importlib.util.spec_from_file_location("pb00701_affine_identity_landed", IDENTITY_HELPER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    require(git_blob(IDENTITY_HELPER.read_bytes()) == IDENTITY_HELPER_BLOB,
            "landed affine-identity helper drifted during import")
    return module


IDENTITY = load_identity_helper()
V7 = IDENTITY.original_lowerer()
EE = V7.v6.base.EE


def trim(poly):
    out = [IDENTITY.q_exact(x) for x in poly]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out or [Q(0)]


def padd(a, b):
    out = [Q(0)] * max(len(a), len(b))
    for i, value in enumerate(trim(a)):
        out[i] += value
    for i, value in enumerate(trim(b)):
        out[i] += value
    return trim(out)


def pscale(poly, scalar):
    scalar = IDENTITY.q_exact(scalar)
    return trim([scalar * value for value in trim(poly)])


def pmul(a, b):
    aa, bb = trim(a), trim(b)
    out = [Q(0)] * (len(aa) + len(bb) - 1)
    for i, left in enumerate(aa):
        for j, right in enumerate(bb):
            out[i + j] += left * right
    return trim(out)


def ppow(poly, exponent):
    out = [Q(1)]
    for _ in range(exponent):
        out = pmul(out, poly)
    return out


def event_summary(event):
    return {
        key: event[key]
        for key in ("status", "relation", "multiplicity", "singular", "event_kind", "sign_change")
        if key in event
    }


def sign_name(value):
    value = IDENTITY.q_exact(value)
    require(value != 0, "sign requested for zero")
    return "POSITIVE" if value > 0 else "NEGATIVE"


def one_sided_rational_sign(poly, point, side):
    point = IDENTITY.q_exact(point)
    cur = trim(poly)
    order = 0
    while cur != [Q(0)]:
        value = EE.peval(cur, point)
        if value:
            result = 1 if value > 0 else -1
            if side == "left" and order % 2:
                result *= -1
            return result
        cur = EE.deriv(cur)
        order += 1
    raise ValueError("identity polynomial has no isolated one-sided sign")


def cardinal_pair(harmonic, phase_turn):
    quarter = 4 * IDENTITY.q_exact(phase_turn) * int(harmonic)
    if quarter.denominator != 1:
        return None
    return ((Q(1), Q(0)), (Q(0), Q(1)), (Q(-1), Q(0)), (Q(0), Q(-1)))[quarter.numerator % 4]


def source_stationary_spans(spec):
    """Re-lower the exact source without invoking historical route selection."""
    require(isinstance(spec, dict), "source must be an object")
    allowed = {
        "grammar", "cos_splines", "sin_splines", "parameter_lo", "parameter_hi",
        "phase_turn_offset", "phase_turn_rate", "source_parameter_id", "parameter_projection",
    }
    require(set(spec) <= allowed, "unreviewed source authority field")
    require(spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
            "source grammar outside stationary B-spline scope")
    source_id = spec.get("source_parameter_id")
    require(isinstance(source_id, str) and source_id, "missing shared source parameter")
    require(spec.get("parameter_projection") in (None, source_id),
            "independent source projection forbidden")
    lo = IDENTITY.q_exact(spec["parameter_lo"])
    hi = IDENTITY.q_exact(spec["parameter_hi"])
    offset = IDENTITY.q_exact(spec["phase_turn_offset"])
    rate = IDENTITY.q_exact(spec["phase_turn_rate"])
    require(lo < hi, "empty source interval")
    require(rate == 0, "nonstationary source outside this owner")
    cos_norm = V7._normalise_harmonic_splines(spec.get("cos_splines"), "cos_splines")
    sin_norm = V7._normalise_harmonic_splines(spec.get("sin_splines"), "sin_splines")
    require(cos_norm or sin_norm, "empty source expression")
    boundaries = V7._master_boundaries(list(cos_norm.values()) + list(sin_norm.values()), lo, hi)
    spans = []
    for index, (left, right) in enumerate(zip(boundaries, boundaries[1:])):
        if not left < right:
            continue
        cos_polys = {h: V7._piece_from_normal(normal, left, right)["coefficients"]
                     for h, normal in cos_norm.items()}
        sin_polys = {h: V7._piece_from_normal(normal, left, right)["coefficients"]
                     for h, normal in sin_norm.items()}
        if V7._dominance_certificate(cos_polys, sin_polys) is not None:
            spans.append({"span_index": index, "source_interval": (left, right),
                          "owner": "PRECEDING_AMPLITUDE_DOMINANCE"})
            continue
        total = [Q(0)]
        cardinal = True
        for harmonic in sorted(set(cos_polys) | set(sin_polys)):
            pair = cardinal_pair(harmonic, offset)
            if pair is None:
                cardinal = False
                break
            cosine, sine = pair
            if harmonic in cos_polys:
                total = padd(total, pscale(cos_polys[harmonic], cosine))
            if harmonic in sin_polys:
                total = padd(total, pscale(sin_polys[harmonic], sine))
        if not cardinal:
            spans.append({"span_index": index, "source_interval": (left, right),
                          "owner": "STATIONARY_NONCARDINAL_BOUNDARY"})
            continue
        total = trim(total)
        if total == [Q(0)]:
            spans.append({"span_index": index, "source_interval": (left, right),
                          "owner": "STATIONARY_IDENTITY_ZERO_CONTINUUM"})
            continue
        repeated = EE.pgcd(total, EE.deriv(total))
        spans.append({
            "span_index": index,
            "source_interval": (left, right),
            "owner": OWNER,
            "polynomial": total,
            "historical_summary": {
                "status": "CERTIFIED",
                "relation": "EXACT_STATIONARY_CARDINAL_POLYNOMIAL_EVENT",
                "polynomial_coefficients": [str(x) for x in total],
                "left_event": event_summary(EE.exact_event(total, Q(0))),
                "right_event": event_summary(EE.exact_event(total, Q(1))),
                "distinct_roots_open": EE.distinct_roots_open(total, Q(0), Q(1)),
                "multiple_roots_open": (
                    0 if EE.degree(repeated) <= 0
                    else EE.distinct_roots_open(repeated, Q(0), Q(1))
                ),
            },
        })
    return spans


def deflate(poly, root, multiplicity):
    out = trim(poly)
    factor = [-IDENTITY.q_exact(root), Q(1)]
    for _ in range(multiplicity):
        out, remainder = EE.pdivmod(out, factor)
        require(trim(remainder) == [Q(0)], "endpoint deflation was not exact")
    return trim(out)


class BisectionBudget:
    def __init__(self, limit):
        self.limit = int(limit)
        self.used = 0

    def spend(self):
        if self.used >= self.limit:
            raise IsolationRefusal("STATIONARY_POLYNOMIAL_ISOLATION_BUDGET_EXHAUSTED")
        self.used += 1


def refine_unique(square_free_poly, left, right, budget):
    """Shrink a unique-root interval away from both parent boundaries."""
    base_left, base_right = left, right
    while True:
        budget.spend()
        mid = (left + right) / 2
        if EE.peval(square_free_poly, mid) == 0:
            return {"kind": "RATIONAL_ROOT", "value": mid}
        n_left = EE.distinct_roots_open(square_free_poly, left, mid)
        n_right = EE.distinct_roots_open(square_free_poly, mid, right)
        require(n_left + n_right == 1, "unique-root refinement lost Sturm count")
        if n_left:
            right = mid
        else:
            left = mid
        if left > base_left and right < base_right:
            require(EE.peval(square_free_poly, left) != 0 and
                    EE.peval(square_free_poly, right) != 0,
                    "isolating interval endpoint became a root")
            return {"kind": "ALGEBRAIC_ROOT", "interval": (left, right)}


def isolate_open_roots(poly, max_bisections=MAX_BISECTIONS):
    poly = trim(poly)
    require(poly != [Q(0)], "identity polynomial cannot have isolated-root view")
    left_mult = EE.multiplicity_at(poly, Q(0))
    right_mult = EE.multiplicity_at(poly, Q(1))
    interior = deflate(poly, Q(0), left_mult)
    interior = deflate(interior, Q(1), right_mult)
    square_free_poly = EE.square_free(interior)
    total = EE.distinct_roots_open(square_free_poly, Q(0), Q(1))
    roots = []
    budget = BisectionBudget(max_bisections)

    def walk(left, right, count):
        if not count:
            return
        budget.spend()
        mid = (left + right) / 2
        if EE.peval(square_free_poly, mid) == 0:
            left_count = EE.distinct_roots_open(square_free_poly, left, mid)
            right_count = EE.distinct_roots_open(square_free_poly, mid, right)
            require(left_count + right_count + 1 == count,
                    "rational split lost a distinct root")
            walk(left, mid, left_count)
            roots.append({"kind": "RATIONAL_ROOT", "value": mid})
            walk(mid, right, right_count)
            return
        left_count = EE.distinct_roots_open(square_free_poly, left, mid)
        right_count = EE.distinct_roots_open(square_free_poly, mid, right)
        require(left_count + right_count == count, "Sturm split lost a distinct root")
        if count == 1:
            roots.append(refine_unique(square_free_poly, left, right, budget))
            return
        walk(left, mid, left_count)
        walk(mid, right, right_count)

    walk(Q(0), Q(1), total)
    require(len(roots) == total, "isolation did not return every distinct open root")
    roots.sort(key=lambda item: item["value"] if item["kind"] == "RATIONAL_ROOT"
               else item["interval"][0])
    return left_mult, right_mult, roots, budget.used


def multiplicity_in_view(poly, root):
    if root["kind"] == "RATIONAL_ROOT":
        return EE.multiplicity_at(poly, root["value"])
    left, right = root["interval"]
    multiplicity = 1
    repeated = EE.pgcd(poly, EE.deriv(poly))
    while EE.degree(repeated) > 0 and EE.distinct_roots_open(repeated, left, right):
        multiplicity += 1
        repeated = EE.pgcd(repeated, EE.deriv(repeated))
    return multiplicity


def build_polynomial_view(poly, *, source_left=Q(0), source_right=Q(1),
                          max_bisections=MAX_BISECTIONS):
    poly = trim(poly)
    require(poly != [Q(0)], "identity polynomial is a continuum-zero semantic case")
    left_mult, right_mult, isolated, used = isolate_open_roots(poly, max_bisections)
    width = source_right - source_left
    roots = []
    for index, raw in enumerate(isolated):
        multiplicity = multiplicity_in_view(poly, raw)
        if raw["kind"] == "RATIONAL_ROOT":
            value = raw["value"]
            left_sign = one_sided_rational_sign(poly, value, "left")
            right_sign = one_sided_rational_sign(poly, value, "right")
            descriptor = {
                "index": index, "kind": "RATIONAL_ROOT", "local_value": str(value),
                "source_value": str(source_left + width * value),
            }
        else:
            left, right = raw["interval"]
            left_sign = 1 if EE.peval(poly, left) > 0 else -1
            right_sign = 1 if EE.peval(poly, right) > 0 else -1
            descriptor = {
                "index": index, "kind": "UNIQUE_REAL_ALGEBRAIC_ROOT",
                "local_isolating_interval": [str(left), str(right)],
                "source_isolating_interval": [
                    str(source_left + width * left), str(source_left + width * right)
                ],
                "defining_polynomial": [str(x) for x in EE.square_free(poly)],
                "minimal_polynomial_claimed": False,
            }
        require((left_sign != right_sign) == bool(multiplicity % 2),
                "root parity disagrees with adjacent signs")
        descriptor.update({
            "multiplicity": multiplicity,
            "event_kind": "CROSSING" if multiplicity % 2 else "TANGENCY",
            "left_sign": left_sign, "right_sign": right_sign,
        })
        roots.append(descriptor)

    cells = []
    for index in range(len(roots) + 1):
        if index == 0:
            gap_left = Q(0)
        else:
            prev = roots[index - 1]
            gap_left = (Q(prev["local_value"]) if prev["kind"] == "RATIONAL_ROOT"
                        else Q(prev["local_isolating_interval"][1]))
        if index == len(roots):
            gap_right = Q(1)
        else:
            nxt = roots[index]
            gap_right = (Q(nxt["local_value"]) if nxt["kind"] == "RATIONAL_ROOT"
                         else Q(nxt["local_isolating_interval"][0]))
        require(gap_left < gap_right, "ordered root descriptors leave no root-free gap")
        sample = (gap_left + gap_right) / 2
        value = EE.peval(poly, sample)
        require(value != 0, "cell sample unexpectedly landed on a root")
        require(EE.distinct_roots_open(poly, gap_left, gap_right) == 0,
                "claimed sign cell contains an unrepresented root")
        cells.append({
            "index": index,
            "sample": str(sample),
            "sign": sign_name(value),
            "local_gap": [str(gap_left), str(gap_right)],
            "proof": "STURM_ZERO_ROOT_COUNT_PLUS_EXACT_RATIONAL_SAMPLE",
        })

    left_inward = one_sided_rational_sign(poly, Q(0), "right")
    right_inward = one_sided_rational_sign(poly, Q(1), "left")
    return {
        "schema": "radicadsac-stationary-polynomial-ordered-span/1.0",
        "polynomial_coefficients": [str(x) for x in poly],
        "source_affine_map": [str(source_left), str(source_right)],
        "left_endpoint": {
            "relation": "ZERO" if left_mult else sign_name(EE.peval(poly, Q(0))),
            "multiplicity": left_mult,
            "inward_sign": left_inward,
        },
        "right_endpoint": {
            "relation": "ZERO" if right_mult else sign_name(EE.peval(poly, Q(1))),
            "multiplicity": right_mult,
            "inward_sign": right_inward,
        },
        "ordered_open_roots": roots,
        "sign_cells": cells,
        "summary": {
            "distinct_roots_open": len(roots),
            "multiple_roots_open": sum(root["multiplicity"] > 1 for root in roots),
            "crossings_open": sum(root["multiplicity"] % 2 == 1 for root in roots),
            "tangencies_open": sum(root["multiplicity"] % 2 == 0 for root in roots),
            "left_endpoint_root": bool(left_mult),
            "right_endpoint_root": bool(right_mult),
            "total_distinct_roots_closed": len(roots) + bool(left_mult) + bool(right_mult),
        },
        "bisections_used": used,
        "identity_zero_claimed": False,
        "general_nonstationary_solver_claimed": False,
    }


def validate_polynomial_view(candidate, poly):
    require(isinstance(candidate, dict), "candidate view must be an object")
    poly = trim(poly)
    require(candidate.get("schema") == "radicadsac-stationary-polynomial-ordered-span/1.0",
            "wrong ordered-span schema")
    require([str(x) for x in poly] == candidate.get("polynomial_coefficients"),
            "candidate polynomial changed")
    roots = candidate.get("ordered_open_roots")
    require(isinstance(roots, list), "missing ordered roots")
    expected_count = EE.distinct_roots_open(poly, Q(0), Q(1))
    require(len(roots) == expected_count, "ordered root list is incomplete")
    previous_right = Q(0)
    for index, root in enumerate(roots):
        require(root.get("index") == index, "root index/order mismatch")
        kind = root.get("kind")
        if kind == "RATIONAL_ROOT":
            value = IDENTITY.q_exact(root["local_value"])
            require(Q(0) < value < Q(1) and EE.peval(poly, value) == 0,
                    "rational descriptor is not an open root")
            left, right = value, value
            multiplicity = EE.multiplicity_at(poly, value)
            left_sign = one_sided_rational_sign(poly, value, "left")
            right_sign = one_sided_rational_sign(poly, value, "right")
        else:
            require(kind == "UNIQUE_REAL_ALGEBRAIC_ROOT", "unknown root descriptor")
            left, right = map(IDENTITY.q_exact, root["local_isolating_interval"])
            require(Q(0) < left < right < Q(1), "bad algebraic isolating interval")
            require(EE.peval(poly, left) != 0 and EE.peval(poly, right) != 0,
                    "algebraic interval endpoint is a root")
            require(EE.distinct_roots_open(EE.square_free(poly), left, right) == 1,
                    "interval does not isolate exactly one root")
            multiplicity = multiplicity_in_view(poly, {
                "kind": "ALGEBRAIC_ROOT", "interval": (left, right)
            })
            left_sign = 1 if EE.peval(poly, left) > 0 else -1
            right_sign = 1 if EE.peval(poly, right) > 0 else -1
            require(root.get("defining_polynomial") == [str(x) for x in EE.square_free(poly)],
                    "defining polynomial changed")
            require(root.get("minimal_polynomial_claimed") is False,
                    "candidate invented a minimal polynomial")
        require(previous_right < left, "root descriptors overlap or are not strictly ordered")
        previous_right = right
        require(root.get("multiplicity") == multiplicity, "root multiplicity mismatch")
        require(root.get("left_sign") == left_sign and root.get("right_sign") == right_sign,
                "root adjacent sign mismatch")
        require(root.get("event_kind") == ("CROSSING" if multiplicity % 2 else "TANGENCY"),
                "root parity/event kind mismatch")
    require(previous_right < Q(1), "last root descriptor is not interior")

    cells = candidate.get("sign_cells")
    require(isinstance(cells, list) and len(cells) == len(roots) + 1,
            "sign-cell cover cardinality mismatch")
    for index, cell in enumerate(cells):
        left = Q(0) if index == 0 else (
            IDENTITY.q_exact(roots[index - 1]["local_value"])
            if roots[index - 1]["kind"] == "RATIONAL_ROOT"
            else IDENTITY.q_exact(roots[index - 1]["local_isolating_interval"][1])
        )
        right = Q(1) if index == len(roots) else (
            IDENTITY.q_exact(roots[index]["local_value"])
            if roots[index]["kind"] == "RATIONAL_ROOT"
            else IDENTITY.q_exact(roots[index]["local_isolating_interval"][0])
        )
        sample = IDENTITY.q_exact(cell["sample"])
        require(left < sample < right, "sign-cell sample is not inside its ordered gap")
        require(EE.distinct_roots_open(poly, left, right) == 0,
                "sign-cell gap contains an omitted root")
        value = EE.peval(poly, sample)
        require(value != 0 and cell.get("sign") == sign_name(value),
                "sign-cell relation mismatch")
    left_mult = EE.multiplicity_at(poly, Q(0))
    right_mult = EE.multiplicity_at(poly, Q(1))
    require(candidate["left_endpoint"]["multiplicity"] == left_mult and
            candidate["right_endpoint"]["multiplicity"] == right_mult,
            "endpoint multiplicity mismatch")
    require(candidate["left_endpoint"]["inward_sign"] ==
            one_sided_rational_sign(poly, Q(0), "right"),
            "left inward sign mismatch")
    require(candidate["right_endpoint"]["inward_sign"] ==
            one_sided_rational_sign(poly, Q(1), "left"),
            "right inward sign mismatch")
    summary = candidate.get("summary", {})
    require(summary.get("distinct_roots_open") == expected_count,
            "summary root count mismatch")
    require(summary.get("multiple_roots_open") ==
            sum(root["multiplicity"] > 1 for root in roots),
            "summary multiple-root count mismatch")
    require(candidate.get("identity_zero_claimed") is False and
            candidate.get("general_nonstationary_solver_claimed") is False,
            "candidate broadened the research claim")
    return True


def build_source_candidate(spec, max_bisections=MAX_BISECTIONS):
    source_digest = IDENTITY.hash_exact_source_record(spec)
    try:
        historical = V7.analyze_coupled_bspline_event(
            cos_splines=spec.get("cos_splines"),
            sin_splines=spec.get("sin_splines"),
            parameter_lo=spec.get("parameter_lo"),
            parameter_hi=spec.get("parameter_hi"),
            phase_turn_offset=spec.get("phase_turn_offset"),
            phase_turn_rate=spec.get("phase_turn_rate"),
            source_parameter_id=spec.get("source_parameter_id"),
            parameter_projection=spec.get("parameter_projection"),
        )
        reconstructed = source_stationary_spans(spec)
        views = []
        for span_index, span in enumerate(historical.get("spans", [])):
            if span.get("route_kind") != OWNER or span.get("route", {}).get("status") != "CERTIFIED":
                continue
            check = reconstructed[span_index]
            require(check.get("owner") == OWNER, "source reconstruction disagrees with historical owner")
            require(check["historical_summary"] == span["route"],
                    "source reconstruction disagrees with historical stationary route")
            left, right = check["source_interval"]
            view = build_polynomial_view(
                check["polynomial"], source_left=left, source_right=right,
                max_bisections=max_bisections)
            views.append({
                "span_index": span_index,
                "source_interval": [str(left), str(right)],
                "historical_owner": OWNER,
                "historical_route": copy.deepcopy(span["route"]),
                "ordered_view": view,
            })
        if not views:
            return {
                "schema": SCHEMA, "status": "OUTSIDE_STATIONARY_POLYNOMIAL_OWNER_SCOPE",
                "source_sha256": source_digest, "is_truth_value": False,
            }
        return {
            "schema": SCHEMA,
            "status": "STATIONARY_POLYNOMIAL_ORDERED_VIEWS_CERTIFIED",
            "source_sha256": source_digest,
            "source_parameter_id": spec.get("source_parameter_id"),
            "historical_span_count": len(historical.get("spans", [])),
            "stationary_span_count": len(views),
            "all_historical_spans_stationary": len(views) == len(historical.get("spans", [])),
            "views": views,
            "scope": "ORDERED_ROOTS_FOR_ACTUAL_NONIDENTITY_STATIONARY_CARDINAL_POLYNOMIAL_OWNER_ONLY",
            "mc_b_or_native_claimed": False,
        }
    except IsolationRefusal as exc:
        return {
            "schema": SCHEMA, "status": "RESOURCE_REFUSAL", "reason": str(exc),
            "source_sha256": source_digest, "is_truth_value": False,
            "mc_b_or_native_claimed": False,
        }
    except RESOURCE_ERRORS as exc:
        return {
            "schema": SCHEMA, "status": "RESOURCE_REFUSAL",
            "reason": "STATIONARY_POLYNOMIAL_RUNTIME_RESOURCE_LIMIT",
            "exception_type": type(exc).__name__, "source_sha256": source_digest,
            "is_truth_value": False, "mc_b_or_native_claimed": False,
        }


def validate_source_candidate(candidate, spec):
    require(candidate.get("schema") == SCHEMA, "wrong source-candidate schema")
    require(candidate.get("source_sha256") == IDENTITY.hash_exact_source_record(spec),
            "source record digest mismatch")
    require(candidate.get("status") == "STATIONARY_POLYNOMIAL_ORDERED_VIEWS_CERTIFIED",
            "candidate is not a certified stationary ordered-view result")
    reconstructed = source_stationary_spans(spec)
    views = candidate.get("views")
    require(isinstance(views, list) and views, "candidate has no ordered views")
    seen = set()
    for item in views:
        index = item.get("span_index")
        require(isinstance(index, int) and 0 <= index < len(reconstructed) and index not in seen,
                "span index invalid or duplicated")
        seen.add(index)
        span = reconstructed[index]
        require(span.get("owner") == OWNER, "candidate view is not source-bound to stationary owner")
        require(item.get("historical_owner") == OWNER, "historical owner relabelled")
        require(item.get("historical_route") == span["historical_summary"],
                "historical stationary witness changed")
        validate_polynomial_view(item["ordered_view"], span["polynomial"])
    require(candidate.get("stationary_span_count") == len(views),
            "stationary span count mismatch")
    require(candidate.get("all_historical_spans_stationary") ==
            (candidate.get("historical_span_count") == len(views)),
            "all-spans scope flag mismatch")
    require(candidate.get("mc_b_or_native_claimed") is False,
            "candidate promoted programme/native capability")
    return True


def polynomial_controls():
    endpoint_poly = pmul(ppow([Q(0), Q(1)], 2),
                         pmul(ppow([Q(-1), Q(1)], 3),
                              ppow([Q(-1, 2), Q(1)], 4)))
    view = build_polynomial_view(endpoint_poly)
    validate_polynomial_view(view, endpoint_poly)
    require(view["left_endpoint"]["multiplicity"] == 2, "left endpoint control failed")
    require(view["right_endpoint"]["multiplicity"] == 3, "right endpoint control failed")
    require(len(view["ordered_open_roots"]) == 1 and
            view["ordered_open_roots"][0]["multiplicity"] == 4,
            "rational repeated-root control failed")

    mixed = pmul(ppow([Q(-1), Q(0), Q(2)], 2), [Q(-1, 3), Q(1)])
    view = build_polynomial_view(mixed)
    validate_polynomial_view(view, mixed)
    require([root["multiplicity"] for root in view["ordered_open_roots"]] == [1, 2],
            "mixed rational/algebraic multiplicity control failed")
    require([root["event_kind"] for root in view["ordered_open_roots"]] ==
            ["CROSSING", "TANGENCY"], "mixed parity control failed")

    close = pmul([Q(-1, 3), Q(1)], [-(Q(1, 3) + Q(1, 2**20)), Q(1)])
    try:
        build_polynomial_view(close, max_bisections=1)
    except IsolationRefusal:
        pass
    else:
        raise AssertionError("isolation budget exhaustion was not refused")
    view = build_polynomial_view(close, max_bisections=MAX_BISECTIONS)
    validate_polynomial_view(view, close)
    require(len(view["ordered_open_roots"]) == 2, "close-root control lost a root")

    constant = [Q(7, 5)]
    validate_polynomial_view(build_polynomial_view(constant), constant)
    try:
        build_polynomial_view([Q(0)])
    except ValueError:
        pass
    else:
        raise AssertionError("identity-zero polynomial was treated as isolated roots")
    return True


def frozen_corpus_controls():
    require(git_blob(CORPUS.read_bytes()) == CORPUS_BLOB, "frozen v54 corpus drifted")
    corpus = json.loads(CORPUS.read_text())
    cases = [row for row in corpus["cases"]
             if OWNER in json.dumps(row.get("expected", {}), sort_keys=True)]
    require(len(cases) == 3, "unexpected stationary-owner frozen case count")
    results = []
    blocked_composites = 0
    for row in cases:
        candidate = build_source_candidate(row["spec"])
        require(candidate["status"] == "STATIONARY_POLYNOMIAL_ORDERED_VIEWS_CERTIFIED",
                f"frozen stationary case did not certify: {row['id']}")
        validate_source_candidate(candidate, row["spec"])
        require(candidate["all_historical_spans_stationary"] is True,
                f"frozen stationary case has an unexpected nonstationary owner: {row['id']}")
        expected_spans = row["expected"]["observed"]["spans"]
        require(candidate["historical_span_count"] == len(expected_spans),
                "frozen span count changed")
        if row["expected"]["v54_disposition"] ==                 "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE":
            blocked_composites += 1
        results.append((row["id"], candidate["stationary_span_count"],
                        sum(v["ordered_view"]["summary"]["distinct_roots_open"]
                            for v in candidate["views"])))
    require(blocked_composites == 2,
            "expected exactly two frozen multi-span ordered-premise blockers")
    return results


def mutation_controls():
    poly = pmul(ppow([Q(-1), Q(0), Q(2)], 2), [Q(-1, 3), Q(1)])
    base = build_polynomial_view(poly)
    for mutate in (
        lambda c: c["ordered_open_roots"][0].__setitem__("multiplicity", 9),
        lambda c: c["ordered_open_roots"][0].__setitem__("event_kind", "TANGENCY"),
        lambda c: c["sign_cells"][0].__setitem__(
            "sign", "POSITIVE" if c["sign_cells"][0]["sign"] == "NEGATIVE" else "NEGATIVE"),
        lambda c: c["ordered_open_roots"].pop(),
        lambda c: c["ordered_open_roots"].reverse(),
    ):
        candidate = copy.deepcopy(base)
        mutate(candidate)
        try:
            validate_polynomial_view(candidate, poly)
        except (ValueError, KeyError, IndexError):
            pass
        else:
            raise AssertionError("ordered-root mutation was accepted")
    return True


def self_test():
    polynomial_controls()
    mutation_controls()
    frozen = frozen_corpus_controls()

    one = {"degree": 0, "knots": ["0", "1"], "controls": ["1"]}
    dominance = {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "cos_splines": {"0": one}, "sin_splines": {},
        "parameter_lo": "0", "parameter_hi": "1",
        "phase_turn_offset": "0", "phase_turn_rate": "0",
        "source_parameter_id": "stationary-control-u",
    }
    require(build_source_candidate(dominance)["status"] ==
            "OUTSIDE_STATIONARY_POLYNOMIAL_OWNER_SCOPE",
            "preceding dominance owner was stolen")
    identity_zero = copy.deepcopy(dominance)
    identity_zero["cos_splines"] = {"1": one}
    identity_zero["phase_turn_offset"] = "1/4"
    require(build_source_candidate(identity_zero)["status"] ==
            "OUTSIDE_STATIONARY_POLYNOMIAL_OWNER_SCOPE",
            "identity-zero continuum was treated as isolated stationary roots")
    noncardinal = copy.deepcopy(dominance)
    noncardinal["cos_splines"] = {"1": one}
    noncardinal["phase_turn_offset"] = "1/8"
    require(build_source_candidate(noncardinal)["status"] ==
            "OUTSIDE_STATIONARY_POLYNOMIAL_OWNER_SCOPE",
            "stationary noncardinal source was silently broadened")

    print("PASS: exact Sturm ordering, multiplicity/parity/sign-cell and mutation controls")
    print("PASS: frozen v54 stationary cases:", json.dumps(frozen))
    print("PASS: 2 frozen v54 multi-span ordered-premise blockers receive complete stationary ordered views; historical v54 dispositions unchanged")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.contract:
        require(git_blob(IDENTITY_HELPER.read_bytes()) == IDENTITY_HELPER_BLOB,
                "affine-identity helper blob mismatch")
        require(git_blob(CORPUS.read_bytes()) == CORPUS_BLOB,
                "frozen v54 corpus blob mismatch")
        IDENTITY.original_lowerer()
        print("PASS: pinned landed identity/source chain and frozen v54 corpus")
    if args.self_test:
        self_test()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")


if __name__ == "__main__":
    main()
