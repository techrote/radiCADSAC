#!/usr/bin/env python3
"""MC-038 / PB-007-01: source-ordered roots for delegated V6 constant modulation.

Research-only. Uses the historical exact tan-half route as a monotone internal
chart, but isolates/labels roots in the original rational source coordinate.
Does not modify V6/V7, frozen v54 evidence, or establish PB-007-01 / MC-B / MC-1.
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
SCHEMA = "radicadsac-pb00701-v6-source-order-research/1.0"
OWNER = "DELEGATED_V6_CONSTANT_MODULATION"
MAX_BISECTIONS = 768
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
V6 = V7.v6
EE = V6.base.EE


def trim(poly):
    out = [IDENTITY.q_exact(x) for x in poly]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out or [Q(0)]


def relation_sign(event):
    relation = event.get("relation")
    require(relation in ("POSITIVE", "NEGATIVE"), "expected nonzero endpoint event")
    return 1 if relation == "POSITIVE" else -1


def source_phase(offset, rate, source_u):
    return IDENTITY.q_exact(offset) + IDENTITY.q_exact(rate) * IDENTITY.q_exact(source_u)


def phase_endpoint(turn):
    return V6.rational_turn_endpoint(IDENTITY.q_exact(turn))


def ordered_phase_endpoints(turn_a, turn_b):
    turn_a = IDENTITY.q_exact(turn_a)
    turn_b = IDENTITY.q_exact(turn_b)
    require(turn_a != turn_b, "phase interval collapsed")
    if turn_a < turn_b:
        return phase_endpoint(turn_a), phase_endpoint(turn_b)
    return phase_endpoint(turn_b), phase_endpoint(turn_a)


def count_source_roots(poly, offset, rate, source_left, source_right):
    source_left = IDENTITY.q_exact(source_left)
    source_right = IDENTITY.q_exact(source_right)
    require(source_left < source_right, "source root count requires increasing interval")
    turn_left = source_phase(offset, rate, source_left)
    turn_right = source_phase(offset, rate, source_right)
    left_endpoint, right_endpoint = ordered_phase_endpoints(turn_left, turn_right)
    return V6._distinct_roots_open(trim(poly), left_endpoint, right_endpoint)


def event_at_source(poly, offset, rate, source_u):
    return V6._event_at_endpoint(trim(poly), phase_endpoint(source_phase(offset, rate, source_u)))


def source_one_sided_sign(poly, offset, rate, source_u, side):
    require(side in ("left", "right"), "invalid source side")
    rate = IDENTITY.q_exact(rate)
    require(rate != 0, "V6 source ordering requires nonzero phase rate")
    phase_side = side if rate > 0 else ("right" if side == "left" else "left")
    return V6._one_sided_sign_at_endpoint(
        trim(poly), phase_endpoint(source_phase(offset, rate, source_u)), phase_side)


def source_v6_spans(spec):
    """Reconstruct V6-owner spans from the exact original source."""
    require(isinstance(spec, dict), "source must be an object")
    allowed = {
        "grammar", "cos_splines", "sin_splines", "parameter_lo", "parameter_hi",
        "phase_turn_offset", "phase_turn_rate", "source_parameter_id", "parameter_projection",
    }
    require(set(spec) <= allowed, "unreviewed source authority field")
    require(spec.get("grammar") == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
            "source grammar outside coupled B-spline scope")
    source_id = spec.get("source_parameter_id")
    require(isinstance(source_id, str) and source_id, "missing shared source parameter")
    require(spec.get("parameter_projection") in (None, source_id),
            "independent source projection forbidden")

    lo = IDENTITY.q_exact(spec["parameter_lo"])
    hi = IDENTITY.q_exact(spec["parameter_hi"])
    offset = IDENTITY.q_exact(spec["phase_turn_offset"])
    rate = IDENTITY.q_exact(spec["phase_turn_rate"])
    require(lo < hi, "empty source interval")
    cos_norm = V7._normalise_harmonic_splines(spec.get("cos_splines"), "cos_splines")
    sin_norm = V7._normalise_harmonic_splines(spec.get("sin_splines"), "sin_splines")
    require(cos_norm or sin_norm, "empty source expression")

    boundaries = V7._master_boundaries(
        list(cos_norm.values()) + list(sin_norm.values()), lo, hi)
    spans = []
    for index, (left, right) in enumerate(zip(boundaries, boundaries[1:])):
        if not left < right:
            continue
        cos_polys = {
            h: V7._piece_from_normal(normal, left, right)["coefficients"]
            for h, normal in cos_norm.items()
        }
        sin_polys = {
            h: V7._piece_from_normal(normal, left, right)["coefficients"]
            for h, normal in sin_norm.items()
        }
        turn_left = offset + rate * left
        turn_right = offset + rate * right

        dominance = V7._dominance_certificate(cos_polys, sin_polys)
        if dominance is not None:
            spans.append({
                "span_index": index, "source_interval": (left, right),
                "phase_turn_interval": (turn_left, turn_right),
                "owner": "PRECEDING_AMPLITUDE_DOMINANCE",
            })
            continue
        if rate == 0:
            spans.append({
                "span_index": index, "source_interval": (left, right),
                "phase_turn_interval": (turn_left, turn_right),
                "owner": "STATIONARY_OWNER_BOUNDARY",
            })
            continue
        if not all(V7._is_constant(poly)
                   for poly in list(cos_polys.values()) + list(sin_polys.values())):
            spans.append({
                "span_index": index, "source_interval": (left, right),
                "phase_turn_interval": (turn_left, turn_right),
                "owner": "NONCONSTANT_MODULATION_BOUNDARY",
            })
            continue

        cos_coefficients = {
            str(h): str(trim(poly)[0])
            for h, poly in cos_polys.items()
            if trim(poly)[0] != 0
        }
        sin_coefficients = {
            str(h): str(trim(poly)[0])
            for h, poly in sin_polys.items()
            if trim(poly)[0] != 0
        }
        route = V6.analyze_rational_turn_window(
            cos_coefficients=cos_coefficients,
            sin_coefficients=sin_coefficients,
            turn_lo=min(turn_left, turn_right),
            turn_hi=max(turn_left, turn_right),
            source_parameter_id=source_id,
            parameter_projection=source_id,
        )
        route = dict(route)
        route["delegated_route"] = "PB00701_V6_CONSTANT_COEFFICIENT_RATIONAL_TURN"
        spans.append({
            "span_index": index,
            "source_interval": (left, right),
            "phase_turn_interval": (turn_left, turn_right),
            "owner": OWNER if route.get("status") == "CERTIFIED" else "V6_NONCERTIFIED_BOUNDARY",
            "route": route,
            "phase_offset": offset,
            "phase_rate": rate,
        })
    return spans


class BisectionBudget:
    def __init__(self, limit):
        self.limit = int(limit)
        self.used = 0

    def spend(self):
        if self.used >= self.limit:
            raise IsolationRefusal("V6_SOURCE_ORDER_ISOLATION_BUDGET_EXHAUSTED")
        self.used += 1


def refine_unique_source(poly, offset, rate, left, right, base_left, base_right, budget):
    while True:
        budget.spend()
        mid = (left + right) / 2
        event = event_at_source(poly, offset, rate, mid)
        if event.get("relation") == "ZERO":
            return {"kind": "RATIONAL_SOURCE_ROOT", "source_value": mid}
        left_count = count_source_roots(poly, offset, rate, left, mid)
        right_count = count_source_roots(poly, offset, rate, mid, right)
        require(left_count + right_count == 1, "unique source-root refinement lost count")
        if left_count:
            right = mid
        else:
            left = mid
        if left > base_left and right < base_right:
            require(event_at_source(poly, offset, rate, left).get("relation") != "ZERO" and
                    event_at_source(poly, offset, rate, right).get("relation") != "ZERO",
                    "source isolating interval endpoint is a root")
            return {"kind": "UNIQUE_SOURCE_ROOT", "source_interval": (left, right)}


def isolate_source_roots(poly, offset, rate, source_left, source_right,
                         max_bisections=MAX_BISECTIONS):
    poly = trim(poly)
    offset = IDENTITY.q_exact(offset)
    rate = IDENTITY.q_exact(rate)
    source_left = IDENTITY.q_exact(source_left)
    source_right = IDENTITY.q_exact(source_right)
    require(poly != [Q(0)], "identity tan-half numerator has continuum semantics")
    require(rate != 0 and source_left < source_right, "invalid V6 source map")

    total = count_source_roots(poly, offset, rate, source_left, source_right)
    roots = []
    budget = BisectionBudget(max_bisections)

    def walk(left, right, count):
        if not count:
            return
        budget.spend()
        mid = (left + right) / 2
        event = event_at_source(poly, offset, rate, mid)
        if event.get("relation") == "ZERO":
            left_count = count_source_roots(poly, offset, rate, left, mid)
            right_count = count_source_roots(poly, offset, rate, mid, right)
            require(left_count + right_count + 1 == count,
                    "rational source split lost a distinct root")
            walk(left, mid, left_count)
            roots.append({"kind": "RATIONAL_SOURCE_ROOT", "source_value": mid})
            walk(mid, right, right_count)
            return
        left_count = count_source_roots(poly, offset, rate, left, mid)
        right_count = count_source_roots(poly, offset, rate, mid, right)
        require(left_count + right_count == count, "source split lost a distinct root")
        if count == 1:
            roots.append(refine_unique_source(
                poly, offset, rate, left, right, source_left, source_right, budget))
            return
        walk(left, mid, left_count)
        walk(mid, right, right_count)

    walk(source_left, source_right, total)
    require(len(roots) == total, "source isolation did not return every open root")
    roots.sort(key=lambda item: (
        item["source_value"] if item["kind"] == "RATIONAL_SOURCE_ROOT"
        else item["source_interval"][0]))
    return roots, budget.used


def multiplicity_in_source_interval(poly, offset, rate, root):
    if root["kind"] == "RATIONAL_SOURCE_ROOT":
        event = event_at_source(poly, offset, rate, root["source_value"])
        require(event.get("relation") == "ZERO", "rational source descriptor is not a root")
        return int(event["multiplicity"])
    left, right = root["source_interval"]
    multiplicity = 1
    repeated = EE.pgcd(trim(poly), EE.deriv(trim(poly)))
    while EE.degree(repeated) > 0 and count_source_roots(
            repeated, offset, rate, left, right):
        require(count_source_roots(repeated, offset, rate, left, right) == 1,
                "repeated-factor interval contains multiple roots")
        multiplicity += 1
        repeated = EE.pgcd(repeated, EE.deriv(repeated))
    return multiplicity


def build_v6_view(route, *, source_left, source_right, phase_offset, phase_rate,
                  max_bisections=MAX_BISECTIONS):
    require(route.get("status") == "CERTIFIED", "V6 route is not certified")
    poly = trim(route["numerator_coefficients"])
    require(poly != [Q(0)], "identity V6 route cannot have isolated root view")
    source_left = IDENTITY.q_exact(source_left)
    source_right = IDENTITY.q_exact(source_right)
    phase_offset = IDENTITY.q_exact(phase_offset)
    phase_rate = IDENTITY.q_exact(phase_rate)
    require(source_left < source_right and phase_rate != 0, "invalid source/phase map")

    roots_raw, used = isolate_source_roots(
        poly, phase_offset, phase_rate, source_left, source_right, max_bisections)
    roots = []
    for index, raw in enumerate(roots_raw):
        multiplicity = multiplicity_in_source_interval(
            poly, phase_offset, phase_rate, raw)
        if raw["kind"] == "RATIONAL_SOURCE_ROOT":
            value = raw["source_value"]
            left_sign = source_one_sided_sign(
                poly, phase_offset, phase_rate, value, "left")
            right_sign = source_one_sided_sign(
                poly, phase_offset, phase_rate, value, "right")
            descriptor = {
                "index": index,
                "kind": "RATIONAL_SOURCE_ROOT",
                "source_value": str(value),
                "phase_turn": str(source_phase(phase_offset, phase_rate, value)),
                "tan_half_endpoint": V6._endpoint_description(
                    phase_endpoint(source_phase(phase_offset, phase_rate, value))),
            }
        else:
            left, right = raw["source_interval"]
            left_event = event_at_source(poly, phase_offset, phase_rate, left)
            right_event = event_at_source(poly, phase_offset, phase_rate, right)
            left_sign = relation_sign(left_event)
            right_sign = relation_sign(right_event)
            descriptor = {
                "index": index,
                "kind": "UNIQUE_SOURCE_ROOT",
                "source_isolating_interval": [str(left), str(right)],
                "phase_turn_isolating_interval": [
                    str(source_phase(phase_offset, phase_rate, left)),
                    str(source_phase(phase_offset, phase_rate, right)),
                ],
                "tan_half_defining_polynomial": [str(x) for x in EE.square_free(poly)],
                "minimal_source_polynomial_claimed": False,
                "transcendental_source_closed_form_claimed": False,
            }
        require((left_sign != right_sign) == bool(multiplicity % 2),
                "source root parity disagrees with adjacent signs")
        descriptor.update({
            "multiplicity": multiplicity,
            "event_kind": "CROSSING" if multiplicity % 2 else "TANGENCY",
            "left_sign": left_sign,
            "right_sign": right_sign,
        })
        roots.append(descriptor)

    left_event = event_at_source(poly, phase_offset, phase_rate, source_left)
    right_event = event_at_source(poly, phase_offset, phase_rate, source_right)
    left_mult = int(left_event.get("multiplicity", 0)) if left_event.get("relation") == "ZERO" else 0
    right_mult = int(right_event.get("multiplicity", 0)) if right_event.get("relation") == "ZERO" else 0
    left_inward = source_one_sided_sign(
        poly, phase_offset, phase_rate, source_left, "right")
    right_inward = source_one_sided_sign(
        poly, phase_offset, phase_rate, source_right, "left")

    cells = []
    for index in range(len(roots) + 1):
        if index == 0:
            witness_left = source_left
            left_boundary = {"kind": "LEFT_SOURCE_ENDPOINT"}
            expected_sign = left_inward
        else:
            prev = roots[index - 1]
            witness_left = (
                IDENTITY.q_exact(prev["source_value"])
                if prev["kind"] == "RATIONAL_SOURCE_ROOT"
                else IDENTITY.q_exact(prev["source_isolating_interval"][1])
            )
            left_boundary = {"kind": "ROOT", "root_index": index - 1}
            expected_sign = prev["right_sign"]
        if index == len(roots):
            witness_right = source_right
            right_boundary = {"kind": "RIGHT_SOURCE_ENDPOINT"}
            require(expected_sign == right_inward,
                    "final cell sign disagrees with right source endpoint")
        else:
            nxt = roots[index]
            witness_right = (
                IDENTITY.q_exact(nxt["source_value"])
                if nxt["kind"] == "RATIONAL_SOURCE_ROOT"
                else IDENTITY.q_exact(nxt["source_isolating_interval"][0])
            )
            right_boundary = {"kind": "ROOT", "root_index": index}
            require(expected_sign == nxt["left_sign"],
                    "cell sign disagrees across adjacent source roots")
        require(witness_left < witness_right, "source witness gap collapsed")
        require(count_source_roots(
            poly, phase_offset, phase_rate, witness_left, witness_right) == 0,
            "source sign-cell witness gap contains an omitted root")
        sample = (witness_left + witness_right) / 2
        sample_event = event_at_source(poly, phase_offset, phase_rate, sample)
        sample_sign = relation_sign(sample_event)
        require(sample_sign == expected_sign, "source cell sample sign mismatch")
        cells.append({
            "index": index,
            "left_boundary": left_boundary,
            "right_boundary": right_boundary,
            "source_witness_gap": [str(witness_left), str(witness_right)],
            "source_sample": str(sample),
            "sign": "POSITIVE" if sample_sign > 0 else "NEGATIVE",
            "complete_open_cell": True,
            "proof": (
                "COMPLETE_SOURCE_ORDER_PLUS_EXACT_V6_STURM_ZERO_ROOT_WITNESS_"
                "AND_EXACT_ALGEBRAIC_ENDPOINT_SIGN"
            ),
        })

    return {
        "schema": "radicadsac-v6-source-ordered-span/1.0",
        "source_interval": [str(source_left), str(source_right)],
        "phase_affine_map": [str(phase_offset), str(phase_rate)],
        "phase_turn_interval": [
            str(source_phase(phase_offset, phase_rate, source_left)),
            str(source_phase(phase_offset, phase_rate, source_right)),
        ],
        "tan_half_numerator": [str(x) for x in poly],
        "left_endpoint": {
            "relation": left_event["relation"],
            "multiplicity": left_mult,
            "inward_sign": left_inward,
        },
        "right_endpoint": {
            "relation": right_event["relation"],
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
            "total_distinct_roots_closed": len(roots) + int(bool(left_mult)) + int(bool(right_mult)),
        },
        "bisections_used": used,
        "tan_half_chart_is_internal_only": True,
        "source_order_claimed": True,
        "mc_b_or_native_claimed": False,
    }


def validate_v6_view(candidate, route, *, source_left, source_right,
                     phase_offset, phase_rate):
    require(candidate.get("schema") == "radicadsac-v6-source-ordered-span/1.0",
            "wrong V6 source-order schema")
    source_left = IDENTITY.q_exact(source_left)
    source_right = IDENTITY.q_exact(source_right)
    phase_offset = IDENTITY.q_exact(phase_offset)
    phase_rate = IDENTITY.q_exact(phase_rate)
    poly = trim(route["numerator_coefficients"])
    require(candidate.get("source_interval") == [str(source_left), str(source_right)],
            "source interval changed")
    require(candidate.get("phase_affine_map") == [str(phase_offset), str(phase_rate)],
            "phase affine map changed")
    require(candidate.get("phase_turn_interval") == [
                str(source_phase(phase_offset, phase_rate, source_left)),
                str(source_phase(phase_offset, phase_rate, source_right)),
            ], "phase-turn interval changed")
    require(candidate.get("tan_half_numerator") == [str(x) for x in poly],
            "tan-half numerator changed")

    roots = candidate.get("ordered_open_roots")
    require(isinstance(roots, list), "missing ordered source roots")
    expected_count = count_source_roots(
        poly, phase_offset, phase_rate, source_left, source_right)
    require(len(roots) == expected_count, "ordered source root list is incomplete")
    previous_right = source_left
    for index, root in enumerate(roots):
        require(root.get("index") == index, "source root index mismatch")
        kind = root.get("kind")
        if kind == "RATIONAL_SOURCE_ROOT":
            value = IDENTITY.q_exact(root["source_value"])
            event = event_at_source(poly, phase_offset, phase_rate, value)
            require(source_left < value < source_right and event.get("relation") == "ZERO",
                    "rational source descriptor is not an open root")
            require(root.get("phase_turn") ==
                    str(source_phase(phase_offset, phase_rate, value)),
                    "rational source-root phase binding changed")
            left = right = value
            multiplicity = int(event["multiplicity"])
            left_sign = source_one_sided_sign(
                poly, phase_offset, phase_rate, value, "left")
            right_sign = source_one_sided_sign(
                poly, phase_offset, phase_rate, value, "right")
        else:
            require(kind == "UNIQUE_SOURCE_ROOT", "unknown source-root descriptor")
            left, right = map(IDENTITY.q_exact, root["source_isolating_interval"])
            require(source_left < left < right < source_right,
                    "bad rational source isolating interval")
            require(event_at_source(poly, phase_offset, phase_rate, left).get("relation") != "ZERO" and
                    event_at_source(poly, phase_offset, phase_rate, right).get("relation") != "ZERO",
                    "source isolating interval endpoint is a root")
            require(count_source_roots(
                EE.square_free(poly), phase_offset, phase_rate, left, right) == 1,
                "source interval does not isolate exactly one physical root")
            require(root.get("phase_turn_isolating_interval") == [
                        str(source_phase(phase_offset, phase_rate, left)),
                        str(source_phase(phase_offset, phase_rate, right)),
                    ], "source root phase interval changed")
            require(root.get("tan_half_defining_polynomial") ==
                    [str(x) for x in EE.square_free(poly)],
                    "tan-half defining polynomial changed")
            require(root.get("minimal_source_polynomial_claimed") is False and
                    root.get("transcendental_source_closed_form_claimed") is False,
                    "candidate invented source algebraic/closed-form authority")
            multiplicity = multiplicity_in_source_interval(
                poly, phase_offset, phase_rate,
                {"kind": "UNIQUE_SOURCE_ROOT", "source_interval": (left, right)})
            left_sign = relation_sign(event_at_source(poly, phase_offset, phase_rate, left))
            right_sign = relation_sign(event_at_source(poly, phase_offset, phase_rate, right))
        require(previous_right < left, "source root descriptors overlap or are not ordered")
        previous_right = right
        require(root.get("multiplicity") == multiplicity, "source root multiplicity mismatch")
        require(root.get("left_sign") == left_sign and root.get("right_sign") == right_sign,
                "source root adjacent sign mismatch")
        require(root.get("event_kind") == ("CROSSING" if multiplicity % 2 else "TANGENCY"),
                "source root parity/event-kind mismatch")
    require(previous_right < source_right, "last source root is not interior")

    left_event = event_at_source(poly, phase_offset, phase_rate, source_left)
    right_event = event_at_source(poly, phase_offset, phase_rate, source_right)
    left_mult = int(left_event.get("multiplicity", 0)) if left_event.get("relation") == "ZERO" else 0
    right_mult = int(right_event.get("multiplicity", 0)) if right_event.get("relation") == "ZERO" else 0
    require(candidate["left_endpoint"]["relation"] == left_event["relation"] and
            candidate["right_endpoint"]["relation"] == right_event["relation"],
            "source endpoint relation mismatch")
    require(candidate["left_endpoint"]["multiplicity"] == left_mult and
            candidate["right_endpoint"]["multiplicity"] == right_mult,
            "source endpoint multiplicity mismatch")
    require(candidate["left_endpoint"]["inward_sign"] ==
            source_one_sided_sign(poly, phase_offset, phase_rate, source_left, "right"),
            "left source inward sign mismatch")
    require(candidate["right_endpoint"]["inward_sign"] ==
            source_one_sided_sign(poly, phase_offset, phase_rate, source_right, "left"),
            "right source inward sign mismatch")

    cells = candidate.get("sign_cells")
    require(isinstance(cells, list) and len(cells) == len(roots) + 1,
            "source sign-cell cardinality mismatch")
    for index, cell in enumerate(cells):
        expected_left = (
            {"kind": "LEFT_SOURCE_ENDPOINT"} if index == 0
            else {"kind": "ROOT", "root_index": index - 1})
        expected_right = (
            {"kind": "RIGHT_SOURCE_ENDPOINT"} if index == len(roots)
            else {"kind": "ROOT", "root_index": index})
        require(cell.get("left_boundary") == expected_left and
                cell.get("right_boundary") == expected_right and
                cell.get("complete_open_cell") is True,
                "source sign cell lost exact boundary/completeness")
        witness_left, witness_right = map(
            IDENTITY.q_exact, cell["source_witness_gap"])
        sample = IDENTITY.q_exact(cell["source_sample"])
        require(witness_left < sample < witness_right,
                "source sign sample outside witness gap")
        require(count_source_roots(
            poly, phase_offset, phase_rate, witness_left, witness_right) == 0,
            "source sign witness contains an omitted root")
        sample_sign = relation_sign(event_at_source(
            poly, phase_offset, phase_rate, sample))
        require(cell.get("sign") == ("POSITIVE" if sample_sign > 0 else "NEGATIVE"),
                "source sign-cell relation mismatch")

    summary = candidate.get("summary", {})
    expected_multiple = sum(root["multiplicity"] > 1 for root in roots)
    expected_crossings = sum(root["multiplicity"] % 2 == 1 for root in roots)
    expected_tangencies = sum(root["multiplicity"] % 2 == 0 for root in roots)
    require(summary.get("distinct_roots_open") == expected_count,
            "source summary distinct-root count mismatch")
    require(summary.get("multiple_roots_open") == expected_multiple,
            "source summary multiple-root count mismatch")
    require(summary.get("crossings_open") == expected_crossings and
            summary.get("tangencies_open") == expected_tangencies,
            "source summary parity counts mismatch")
    require(summary.get("left_endpoint_root") is bool(left_mult) and
            summary.get("right_endpoint_root") is bool(right_mult),
            "source summary endpoint-root flags mismatch")
    require(summary.get("total_distinct_roots_closed") ==
            expected_count + int(bool(left_mult)) + int(bool(right_mult)),
            "source summary closed-root count mismatch")
    require(candidate.get("tan_half_chart_is_internal_only") is True and
            candidate.get("source_order_claimed") is True and
            candidate.get("mc_b_or_native_claimed") is False,
            "candidate broadened chart/programme authority")
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
        reconstructed = source_v6_spans(spec)
        views = []
        for index, span in enumerate(historical.get("spans", [])):
            if span.get("route_kind") != OWNER or span.get("route", {}).get("status") != "CERTIFIED":
                continue
            check = reconstructed[index]
            require(check.get("owner") == OWNER,
                    "source reconstruction disagrees with historical V6 owner")
            require(check["route"] == span["route"],
                    "source reconstruction disagrees with historical V6 route")
            require(span.get("source_interval") ==
                    [str(check["source_interval"][0]), str(check["source_interval"][1])],
                    "historical V6 source interval drifted")
            require(span.get("phase_turn_interval") ==
                    [str(check["phase_turn_interval"][0]), str(check["phase_turn_interval"][1])],
                    "historical V6 phase interval drifted")
            left, right = check["source_interval"]
            view = build_v6_view(
                span["route"], source_left=left, source_right=right,
                phase_offset=check["phase_offset"], phase_rate=check["phase_rate"],
                max_bisections=max_bisections)
            views.append({
                "span_index": index,
                "source_interval": [str(left), str(right)],
                "historical_owner": OWNER,
                "historical_route": copy.deepcopy(span["route"]),
                "ordered_view": view,
            })
        if not views:
            return {
                "schema": SCHEMA,
                "status": "OUTSIDE_CERTIFIED_V6_CONSTANT_MODULATION_SCOPE",
                "source_sha256": source_digest,
                "is_truth_value": False,
                "mc_b_or_native_claimed": False,
            }
        return {
            "schema": SCHEMA,
            "status": "V6_SOURCE_ORDERED_VIEWS_CERTIFIED",
            "source_sha256": source_digest,
            "source_parameter_id": spec.get("source_parameter_id"),
            "historical_span_count": len(historical.get("spans", [])),
            "v6_span_count": len(views),
            "views": views,
            "scope": "SOURCE_ORDER_FOR_CERTIFIED_DELEGATED_V6_CONSTANT_MODULATION_ONLY",
            "mc_b_or_native_claimed": False,
        }
    except (IsolationRefusal, V6.EndpointIsolationRefusal) as exc:
        return {
            "schema": SCHEMA,
            "status": "RESOURCE_REFUSAL",
            "reason": str(exc),
            "source_sha256": source_digest,
            "is_truth_value": False,
            "mc_b_or_native_claimed": False,
        }
    except RESOURCE_ERRORS as exc:
        return {
            "schema": SCHEMA,
            "status": "RESOURCE_REFUSAL",
            "reason": "V6_SOURCE_ORDER_RUNTIME_RESOURCE_LIMIT",
            "exception_type": type(exc).__name__,
            "source_sha256": source_digest,
            "is_truth_value": False,
            "mc_b_or_native_claimed": False,
        }


def validate_source_candidate(candidate, spec):
    require(candidate.get("schema") == SCHEMA, "wrong V6 source-candidate schema")
    require(candidate.get("source_sha256") == IDENTITY.hash_exact_source_record(spec),
            "V6 source digest mismatch")
    require(candidate.get("status") == "V6_SOURCE_ORDERED_VIEWS_CERTIFIED",
            "candidate is not a V6 source-order result")
    reconstructed = source_v6_spans(spec)
    views = candidate.get("views")
    require(isinstance(views, list) and views, "candidate has no V6 views")
    seen = set()
    for item in views:
        index = item.get("span_index")
        require(isinstance(index, int) and 0 <= index < len(reconstructed) and index not in seen,
                "V6 span index invalid or duplicated")
        seen.add(index)
        span = reconstructed[index]
        require(span.get("owner") == OWNER, "candidate view is not source-bound to V6 owner")
        require(item.get("historical_owner") == OWNER, "historical V6 owner relabelled")
        require(item.get("historical_route") == span["route"],
                "historical V6 route changed")
        left, right = span["source_interval"]
        require(item.get("source_interval") == [str(left), str(right)],
                "candidate V6 source interval changed")
        validate_v6_view(
            item["ordered_view"], span["route"],
            source_left=left, source_right=right,
            phase_offset=span["phase_offset"], phase_rate=span["phase_rate"])
    expected = {
        index for index, span in enumerate(reconstructed)
        if span.get("owner") == OWNER
    }
    require(seen == expected, "candidate omitted or invented a certified V6 span")
    require(candidate.get("historical_span_count") == len(reconstructed),
            "historical span count mismatch")
    require(candidate.get("v6_span_count") == len(expected),
            "V6 span count mismatch")
    require(candidate.get("source_parameter_id") == spec.get("source_parameter_id"),
            "source parameter identity changed")
    require(candidate.get("scope") ==
            "SOURCE_ORDER_FOR_CERTIFIED_DELEGATED_V6_CONSTANT_MODULATION_ONLY",
            "candidate V6 scope changed")
    require(candidate.get("mc_b_or_native_claimed") is False,
            "candidate promoted programme/native capability")
    return True


def spline_constant(value, *, lo="0", hi="1"):
    return {"degree": 0, "knots": [lo, hi], "controls": [str(value)]}


def fixture(*, cos=None, sin=None, offset="0", rate="1/4", lo="0", hi="1"):
    return {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "cos_splines": cos or {},
        "sin_splines": sin or {},
        "parameter_lo": lo,
        "parameter_hi": hi,
        "phase_turn_offset": offset,
        "phase_turn_rate": rate,
        "source_parameter_id": "v6-source-u",
    }


def synthetic_controls():
    # Negative phase slope: sin(2*pi*phase) crosses zero at source u=1/2.
    negative = fixture(
        sin={"1": spline_constant(1)}, offset="1/8", rate="-1/4")
    result = build_source_candidate(negative)
    require(result["status"] == "V6_SOURCE_ORDERED_VIEWS_CERTIFIED",
            "negative-rate V6 control did not certify")
    validate_source_candidate(result, negative)
    roots = result["views"][0]["ordered_view"]["ordered_open_roots"]
    require(len(roots) == 1 and roots[0]["kind"] == "RATIONAL_SOURCE_ROOT" and
            roots[0]["source_value"] == "1/2" and roots[0]["multiplicity"] == 1,
            "negative-rate source ordering/root binding failed")

    # cos(theta)=1/3 has two nonrational source roots on [-1/4,+1/4].
    irrational = fixture(
        cos={"0": spline_constant("-1/3"), "1": spline_constant(1)},
        offset="-1/4", rate="1/2")
    result = build_source_candidate(irrational)
    require(result["status"] == "V6_SOURCE_ORDERED_VIEWS_CERTIFIED",
            "nonrational V6 source control did not certify")
    validate_source_candidate(result, irrational)
    roots = result["views"][0]["ordered_view"]["ordered_open_roots"]
    require(len(roots) == 2 and all(root["kind"] == "UNIQUE_SOURCE_ROOT" for root in roots),
            "nonrational source roots were not rationally isolated in source order")

    # (cos(theta)-1/3)^2 = 11/18 - 2/3 cos(theta) + 1/2 cos(2theta).
    repeated = fixture(
        cos={
            "0": spline_constant("11/18"),
            "1": spline_constant("-2/3"),
            "2": spline_constant("1/2"),
        },
        offset="-1/4", rate="1/2")
    result = build_source_candidate(repeated)
    require(result["status"] == "V6_SOURCE_ORDERED_VIEWS_CERTIFIED",
            "repeated V6 source control did not certify")
    validate_source_candidate(result, repeated)
    roots = result["views"][0]["ordered_view"]["ordered_open_roots"]
    require(len(roots) == 2 and [root["multiplicity"] for root in roots] == [2, 2] and
            all(root["event_kind"] == "TANGENCY" for root in roots),
            "V6 source multiplicity/parity transfer failed")

    refused = build_source_candidate(irrational, max_bisections=1)
    require(refused["status"] == "RESOURCE_REFUSAL" and
            refused["is_truth_value"] is False,
            "V6 source isolation budget was treated as truth")

    identity = fixture(cos={"0": spline_constant(0)}, offset="0", rate="1/4")
    require(build_source_candidate(identity)["status"] ==
            "OUTSIDE_CERTIFIED_V6_CONSTANT_MODULATION_SCOPE",
            "identity-zero V6 route was treated as isolated roots")

    pole = fixture(cos={"1": spline_constant(1)}, offset="1/4", rate="1/2")
    require(build_source_candidate(pole)["status"] ==
            "OUTSIDE_CERTIFIED_V6_CONSTANT_MODULATION_SCOPE",
            "tan-half pole-crossing route was treated as ordered source roots")
    return True


def mutation_controls():
    spec = fixture(
        sin={"1": spline_constant(1)}, offset="1/8", rate="-1/4")
    candidate = build_source_candidate(spec)
    validate_source_candidate(candidate, spec)

    def rejected(mutator, reason):
        forged = copy.deepcopy(candidate)
        mutator(forged)
        try:
            validate_source_candidate(forged, spec)
        except (ValueError, KeyError, IndexError):
            return
        raise AssertionError(reason)

    rejected(lambda c: c["views"].pop(), "omitted V6 span was accepted")
    rejected(lambda c: c.__setitem__("source_parameter_id", "forged"),
             "forged V6 source parameter was accepted")
    rejected(lambda c: c["views"][0]["ordered_view"]["ordered_open_roots"][0].__setitem__(
        "multiplicity", 9), "forged V6 multiplicity was accepted")
    rejected(lambda c: c["views"][0]["ordered_view"]["ordered_open_roots"][0].__setitem__(
        "event_kind", "TANGENCY"), "forged V6 parity was accepted")
    rejected(lambda c: c["views"][0]["ordered_view"]["sign_cells"][0].__setitem__(
        "complete_open_cell", False), "downgraded V6 sign cell was accepted")
    rejected(lambda c: c["views"][0]["ordered_view"].__setitem__(
        "phase_affine_map", ["0", "999"]), "forged V6 phase map was accepted")
    rejected(lambda c: c["views"][0]["ordered_view"]["summary"].__setitem__(
        "crossings_open", 99), "forged V6 summary was accepted")
    return True


def frozen_corpus_controls():
    require(git_blob(CORPUS.read_bytes()) == CORPUS_BLOB, "frozen v54 corpus drifted")
    corpus = json.loads(CORPUS.read_text())
    mentioned = [
        row for row in corpus["cases"]
        if OWNER in json.dumps(row.get("expected", {}), sort_keys=True)
    ]
    require(len(mentioned) == 22, "unexpected frozen V6 owner case count")

    certified = 0
    ordered_premise = 0
    ordered_premise_views = 0
    rows = []
    for row in mentioned:
        has_certified = any(
            span[0] == OWNER and span[1] == "CERTIFIED"
            for span in row["expected"]["observed"]["spans"])
        candidate = build_source_candidate(row["spec"])
        if has_certified:
            require(candidate["status"] == "V6_SOURCE_ORDERED_VIEWS_CERTIFIED",
                    f"frozen certified V6 case failed: {row['id']}")
            validate_source_candidate(candidate, row["spec"])
            certified += 1
            if row["expected"]["v54_disposition"] ==                     "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE":
                ordered_premise += 1
                ordered_premise_views += candidate["v6_span_count"]
            rows.append([
                row["id"], candidate["v6_span_count"],
                sum(v["ordered_view"]["summary"]["distinct_roots_open"]
                    for v in candidate["views"])
            ])
        else:
            require(candidate["status"] ==
                    "OUTSIDE_CERTIFIED_V6_CONSTANT_MODULATION_SCOPE",
                    f"frozen noncertified V6 case gained truth: {row['id']}")
    require(certified == 21, "unexpected frozen certified V6 case count")
    require(ordered_premise == 18 and ordered_premise_views == 18,
            "frozen V6 ordered-premise denominator changed")
    return rows


def self_test():
    synthetic_controls()
    mutation_controls()
    rows = frozen_corpus_controls()
    print("PASS: negative-rate source order, nonrational source isolation, repeated-root parity and typed refusal controls")
    print("PASS: V6 source-order mutation controls")
    print("PASS: frozen v54 V6 cases:", json.dumps(rows))
    print("PASS: 18 frozen v54 V6 ordered-premise spans receive complete source-ordered views; historical dispositions unchanged")


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
        print("PASS: pinned source/parser chain and frozen v54 corpus")
    if args.self_test:
        self_test()
    if not args.contract and not args.self_test:
        parser.error("choose --contract and/or --self-test")


if __name__ == "__main__":
    main()
