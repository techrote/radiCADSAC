#!/usr/bin/env python3
"""MC-038 / PB-007-01: source-ordered roots for delegated V6 constant modulation.

Research-only. Isolates exact roots in V6's rational tan-half chart and transfers
their order/sign/multiplicity to the original source through the certified
pole-free monotone phase map. No source-coordinate algebraic closed form is
invented, and historical V6-V54 evidence is read-only.
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
SCHEMA = "radicadsac-pb00701-v6-source-order-research/1.1"
OWNER = "DELEGATED_V6_CONSTANT_MODULATION"
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
V6 = V7.v6
EE = V6.base.EE


def trim(poly):
    out = [IDENTITY.q_exact(x) for x in poly]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out or [Q(0)]


def x_rational(value):
    return {"kind": "RATIONAL", "value": IDENTITY.q_exact(value)}


def endpoint_bounds(endpoint):
    if endpoint["kind"] == "RATIONAL":
        value = IDENTITY.q_exact(endpoint["value"])
        return value, value
    return IDENTITY.q_exact(endpoint["lo"]), IDENTITY.q_exact(endpoint["hi"])


class BisectionBudget:
    def __init__(self, limit):
        self.limit = int(limit)
        self.used = 0

    def spend(self, stage="unspecified"):
        if self.used >= self.limit:
            raise IsolationRefusal(
                f"V6_TAN_HALF_ISOLATION_BUDGET_EXHAUSTED:"
                f"stage={stage}:used={self.used}:limit={self.limit}")
        self.used += 1


def rational_between(left_endpoint, right_endpoint, budget):
    """Return an exact rational strictly between two exact ordered endpoints.

    Algebraic V6 phase endpoints are refined only as algebraic numbers in x;
    their defining-polynomial degree stays fixed. This avoids constructing
    tan(pi*t) at successively finer rational source turns.
    """
    left = copy.deepcopy(left_endpoint)
    right = copy.deepcopy(right_endpoint)
    while True:
        left_lo, left_hi = endpoint_bounds(left)
        right_lo, right_hi = endpoint_bounds(right)
        if left_hi < right_lo:
            return (left_hi + right_lo) / 2, left, right
        budget.spend("separate-exact-endpoints")
        changed = False
        if left["kind"] != "RATIONAL":
            left = V6._refine_endpoint(left)
            changed = True
        if right["kind"] != "RATIONAL":
            right = V6._refine_endpoint(right)
            changed = True
        require(changed, "ordered endpoints could not be separated")


def endpoint_descriptor(endpoint):
    if endpoint["kind"] == "RATIONAL":
        return {"kind": "RATIONAL_X", "value": str(IDENTITY.q_exact(endpoint["value"]))}
    return {
        "kind": "ALGEBRAIC_X",
        "turn": str(endpoint["turn"]),
        "principal_turn": str(endpoint["principal_turn"]),
        "defining_polynomial": [str(x) for x in endpoint["defining_polynomial"]],
        "isolating_interval": [str(endpoint["lo"]), str(endpoint["hi"])],
        "root_rank_abs": int(endpoint["root_rank_abs"]),
        "denominator": int(endpoint["denominator"]),
    }


def endpoint_from_descriptor(description, *, certified_phase_endpoints):
    """Bind inherited algebraic brackets to the actual original V6 endpoint.

    Exact root/sign predicates consume polynomial and interval, not descriptive
    phase/turn metadata. Recheck that metadata and prove the candidate bracket
    isolates the *same* tangent root as the canonical source-phase endpoint.
    A refined interval is allowed; a different root/turn is not.
    """
    kind = description.get("kind")
    if kind == "RATIONAL_X":
        return x_rational(description["value"])
    require(kind == "ALGEBRAIC_X", "unknown tan-half endpoint descriptor")
    turn = IDENTITY.q_exact(description["turn"])
    require(turn in certified_phase_endpoints,
            "algebraic tan-half endpoint is not a source phase-window endpoint")
    canonical = certified_phase_endpoints[turn]
    require(canonical["kind"] == "ALGEBRAIC_TAN_RATIONAL_TURN",
            "algebraic descriptor contradicts exact rational-turn endpoint")
    candidate = {
        "kind": "ALGEBRAIC",
        "turn": turn,
        "principal_turn": IDENTITY.q_exact(description["principal_turn"]),
        "defining_polynomial": [
            IDENTITY.q_exact(x) for x in description["defining_polynomial"]],
        "lo": IDENTITY.q_exact(description["isolating_interval"][0]),
        "hi": IDENTITY.q_exact(description["isolating_interval"][1]),
        "root_rank_abs": int(description["root_rank_abs"]),
        "denominator": int(description["denominator"]),
    }
    for field in ("principal_turn", "defining_polynomial", "root_rank_abs", "denominator"):
        require(candidate[field] == canonical[field],
                f"algebraic tan-half endpoint {field} disagrees with source")
    lo, hi = candidate["lo"], candidate["hi"]
    require(lo < hi, "algebraic tan-half bracket is empty or reversed")
    poly = canonical["defining_polynomial"]
    require(EE.distinct_roots_open(poly, lo, hi) == 1,
            "algebraic tan-half bracket is not a one-root interval")
    overlap_lo = max(lo, canonical["lo"])
    overlap_hi = min(hi, canonical["hi"])
    require(overlap_lo < overlap_hi and
            EE.distinct_roots_open(poly, overlap_lo, overlap_hi) == 1,
            "algebraic tan-half bracket does not identify the source-phase endpoint root")
    return candidate


def isolate_x_roots(poly, left_endpoint, right_endpoint, *,
                    max_bisections=MAX_BISECTIONS):
    """Partition the exact V6 x-window into one-root brackets.

    Unique brackets may retain an exact algebraic *window* endpoint. There is
    no need to shrink them away from it: complete source sign cells are bounded
    by the exact roots themselves, not by arbitrary rational witness gaps.
    """
    poly = trim(poly)
    require(poly != [Q(0)], "identity tan-half numerator has continuum semantics")
    total = V6._distinct_roots_open(poly, left_endpoint, right_endpoint)
    roots = []
    budget = BisectionBudget(max_bisections)

    def one_root(left, right):
        budget.spend("single-root-cut")
        mid, left, right = rational_between(left, right, budget)
        mid_endpoint = x_rational(mid)
        if EE.peval(poly, mid) == 0:
            return {"kind": "RATIONAL_TAN_HALF_ROOT", "x_value": mid}
        left_count = V6._distinct_roots_open(poly, left, mid_endpoint)
        right_count = V6._distinct_roots_open(poly, mid_endpoint, right)
        require(left_count + right_count == 1,
                "single-root tan-half cut lost root count")
        if left_count:
            return {
                "kind": "UNIQUE_TAN_HALF_ROOT",
                "left_endpoint": left,
                "right_endpoint": mid_endpoint,
            }
        return {
            "kind": "UNIQUE_TAN_HALF_ROOT",
            "left_endpoint": mid_endpoint,
            "right_endpoint": right,
        }

    def walk(left, right, count):
        if not count:
            return
        if count == 1:
            roots.append(one_root(left, right))
            return
        budget.spend("split-root-set")
        mid, left, right = rational_between(left, right, budget)
        mid_endpoint = x_rational(mid)
        if EE.peval(poly, mid) == 0:
            left_count = V6._distinct_roots_open(poly, left, mid_endpoint)
            right_count = V6._distinct_roots_open(poly, mid_endpoint, right)
            require(left_count + right_count + 1 == count,
                    "rational tan-half split lost a root")
            walk(left, mid_endpoint, left_count)
            roots.append({"kind": "RATIONAL_TAN_HALF_ROOT", "x_value": mid})
            walk(mid_endpoint, right, right_count)
            return
        left_count = V6._distinct_roots_open(poly, left, mid_endpoint)
        right_count = V6._distinct_roots_open(poly, mid_endpoint, right)
        require(left_count + right_count == count, "tan-half split lost a root")
        walk(left, mid_endpoint, left_count)
        walk(mid_endpoint, right, right_count)

    walk(copy.deepcopy(left_endpoint), copy.deepcopy(right_endpoint), total)
    require(len(roots) == total, "tan-half isolation did not return every open root")
    return roots, budget.used


def x_root_multiplicity(poly, root):
    poly = trim(poly)
    if root["kind"] == "RATIONAL_TAN_HALF_ROOT":
        return EE.multiplicity_at(poly, root["x_value"])
    left = root["left_endpoint"]
    right = root["right_endpoint"]
    multiplicity = 1
    repeated = EE.pgcd(poly, EE.deriv(poly))
    while EE.degree(repeated) > 0:
        count = V6._distinct_roots_open(repeated, left, right)
        require(count in (0, 1), "repeated-factor exact bracket contains multiple roots")
        if not count:
            break
        multiplicity += 1
        repeated = EE.pgcd(repeated, EE.deriv(repeated))
    return multiplicity


def x_root_signs(poly, root):
    if root["kind"] == "RATIONAL_TAN_HALF_ROOT":
        value = root["x_value"]
        return EE._one_sided_sign(poly, value, "left"), EE._one_sided_sign(poly, value, "right")
    return (
        V6._one_sided_sign_at_endpoint(poly, root["left_endpoint"], "right"),
        V6._one_sided_sign_at_endpoint(poly, root["right_endpoint"], "left"),
    )

def source_v6_spans(spec):
    """Reconstruct certified V6-owner spans from the exact original source."""
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
        if V7._dominance_certificate(cos_polys, sin_polys) is not None:
            owner = "PRECEDING_AMPLITUDE_DOMINANCE"
            route = None
        elif rate == 0:
            owner = "STATIONARY_OWNER_BOUNDARY"
            route = None
        elif not all(V7._is_constant(poly)
                     for poly in list(cos_polys.values()) + list(sin_polys.values())):
            owner = "NONCONSTANT_MODULATION_BOUNDARY"
            route = None
        else:
            cos_coefficients = {
                str(h): str(trim(poly)[0])
                for h, poly in cos_polys.items() if trim(poly)[0] != 0}
            sin_coefficients = {
                str(h): str(trim(poly)[0])
                for h, poly in sin_polys.items() if trim(poly)[0] != 0}
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
            owner = OWNER if route.get("status") == "CERTIFIED" else "V6_NONCERTIFIED_BOUNDARY"
        spans.append({
            "span_index": index,
            "source_interval": (left, right),
            "phase_turn_interval": (turn_left, turn_right),
            "phase_offset": offset,
            "phase_rate": rate,
            "owner": owner,
            "route": route,
        })
    return spans


def build_v6_view(route, *, source_left, source_right, phase_offset, phase_rate,
                  max_bisections=MAX_BISECTIONS):
    require(route.get("status") == "CERTIFIED", "V6 route is not certified")
    poly = trim(route["numerator_coefficients"])
    require(poly != [Q(0)], "identity V6 route cannot have isolated roots")
    source_left = IDENTITY.q_exact(source_left)
    source_right = IDENTITY.q_exact(source_right)
    phase_offset = IDENTITY.q_exact(phase_offset)
    phase_rate = IDENTITY.q_exact(phase_rate)
    require(source_left < source_right and phase_rate != 0, "invalid source/phase map")

    turn_source_left = phase_offset + phase_rate * source_left
    turn_source_right = phase_offset + phase_rate * source_right
    phase_lo = min(turn_source_left, turn_source_right)
    phase_hi = max(turn_source_left, turn_source_right)
    require(route.get("turn_interval") == [str(phase_lo), str(phase_hi)],
            "historical V6 turn interval does not match source phase map")
    left_x_endpoint = V6.rational_turn_endpoint(phase_lo)
    right_x_endpoint = V6.rational_turn_endpoint(phase_hi)

    x_roots, used = isolate_x_roots(
        poly, left_x_endpoint, right_x_endpoint, max_bisections=max_bisections)
    require(len(x_roots) == route["distinct_roots_open"],
            "isolated tan-half root count disagrees with V6 route")

    x_descriptors = []
    for x_index, raw in enumerate(x_roots):
        multiplicity = x_root_multiplicity(poly, raw)
        x_left_sign, x_right_sign = x_root_signs(poly, raw)
        if raw["kind"] == "RATIONAL_TAN_HALF_ROOT":
            descriptor = {
                "tan_half_kind": "RATIONAL",
                "tan_half_value": str(raw["x_value"]),
            }
        else:
            descriptor = {
                "tan_half_kind": "UNIQUE_REAL_ALGEBRAIC",
                "tan_half_bracket": {
                    "left": endpoint_descriptor(raw["left_endpoint"]),
                    "right": endpoint_descriptor(raw["right_endpoint"]),
                },
                "tan_half_defining_polynomial": [str(x) for x in EE.square_free(poly)],
            }
        descriptor.update({
            "x_order_index": x_index,
            "multiplicity": multiplicity,
            "x_left_sign": x_left_sign,
            "x_right_sign": x_right_sign,
            "source_identity": (
                "UNIQUE_PREIMAGE_UNDER_AFFINE_PHASE_AND_POLE_FREE_MONOTONE_TAN_HALF"),
            "minimal_source_polynomial_claimed": False,
            "source_closed_form_claimed": False,
        })
        x_descriptors.append(descriptor)

    source_roots = x_descriptors if phase_rate > 0 else list(reversed(x_descriptors))
    roots = []
    for source_index, raw in enumerate(source_roots):
        item = copy.deepcopy(raw)
        item["source_order_index"] = source_index
        if phase_rate > 0:
            source_left_sign = item["x_left_sign"]
            source_right_sign = item["x_right_sign"]
        else:
            source_left_sign = item["x_right_sign"]
            source_right_sign = item["x_left_sign"]
        item["source_left_sign"] = source_left_sign
        item["source_right_sign"] = source_right_sign
        item["event_kind"] = "CROSSING" if item["multiplicity"] % 2 else "TANGENCY"
        require((source_left_sign != source_right_sign) == bool(item["multiplicity"] % 2),
                "source parity disagrees with tan-half multiplicity")
        roots.append(item)

    source_left_endpoint = V6.rational_turn_endpoint(turn_source_left)
    source_right_endpoint = V6.rational_turn_endpoint(turn_source_right)
    source_left_event = V6._event_at_endpoint(poly, source_left_endpoint)
    source_right_event = V6._event_at_endpoint(poly, source_right_endpoint)
    left_mult = int(source_left_event.get("multiplicity", 0))         if source_left_event.get("relation") == "ZERO" else 0
    right_mult = int(source_right_event.get("multiplicity", 0))         if source_right_event.get("relation") == "ZERO" else 0
    left_phase_side = "right" if phase_rate > 0 else "left"
    right_phase_side = "left" if phase_rate > 0 else "right"
    left_inward = V6._one_sided_sign_at_endpoint(poly, source_left_endpoint, left_phase_side)
    right_inward = V6._one_sided_sign_at_endpoint(poly, source_right_endpoint, right_phase_side)

    cells = []
    for index in range(len(roots) + 1):
        if index == 0:
            source_left_boundary = {"kind": "LEFT_SOURCE_ENDPOINT"}
            expected_sign = left_inward
        else:
            source_left_boundary = {"kind": "ROOT", "root_index": index - 1}
            expected_sign = roots[index - 1]["source_right_sign"]
        if index == len(roots):
            source_right_boundary = {"kind": "RIGHT_SOURCE_ENDPOINT"}
            require(expected_sign == right_inward,
                    "final source cell disagrees with right endpoint inward sign")
        else:
            source_right_boundary = {"kind": "ROOT", "root_index": index}
            require(expected_sign == roots[index]["source_left_sign"],
                    "source cell sign disagrees across adjacent root")
        cells.append({
            "index": index,
            "left_boundary": source_left_boundary,
            "right_boundary": source_right_boundary,
            "sign": "POSITIVE" if expected_sign > 0 else "NEGATIVE",
            "complete_open_source_cell": True,
            "proof": (
                "COMPLETE_SOURCE_ROOT_ORDER_PLUS_ANALYTIC_NO_ZERO_BETWEEN_"
                "ADJACENT_ROOTS_AND_EXACT_ONE_SIDED_SIGNS"
            ),
        })


    return {
        "schema": "radicadsac-v6-source-ordered-span/1.1",
        "source_interval": [str(source_left), str(source_right)],
        "phase_affine_map": [str(phase_offset), str(phase_rate)],
        "phase_turn_interval_source_order": [str(turn_source_left), str(turn_source_right)],
        "phase_turn_window_sorted": [str(phase_lo), str(phase_hi)],
        "tan_half_numerator": [str(x) for x in poly],
        "left_endpoint": {
            "relation": source_left_event["relation"],
            "multiplicity": left_mult,
            "inward_sign": left_inward,
        },
        "right_endpoint": {
            "relation": source_right_event["relation"],
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
        "source_root_coordinates_closed_form_claimed": False,
        "mc_b_or_native_claimed": False,
    }


def validate_v6_view(candidate, route, *, source_left, source_right,
                     phase_offset, phase_rate):
    require(candidate.get("schema") == "radicadsac-v6-source-ordered-span/1.1",
            "wrong V6 source-order schema")
    source_left = IDENTITY.q_exact(source_left)
    source_right = IDENTITY.q_exact(source_right)
    phase_offset = IDENTITY.q_exact(phase_offset)
    phase_rate = IDENTITY.q_exact(phase_rate)
    poly = trim(route["numerator_coefficients"])
    turn_left = phase_offset + phase_rate * source_left
    turn_right = phase_offset + phase_rate * source_right
    phase_lo, phase_hi = min(turn_left, turn_right), max(turn_left, turn_right)
    require(candidate.get("source_interval") == [str(source_left), str(source_right)],
            "V6 source interval changed")
    require(candidate.get("phase_affine_map") == [str(phase_offset), str(phase_rate)],
            "V6 phase affine map changed")
    require(candidate.get("phase_turn_interval_source_order") ==
            [str(turn_left), str(turn_right)], "V6 source-order phase interval changed")
    require(candidate.get("phase_turn_window_sorted") ==
            [str(phase_lo), str(phase_hi)], "V6 sorted phase window changed")
    require(candidate.get("tan_half_numerator") == [str(x) for x in poly],
            "V6 tan-half numerator changed")

    left_endpoint = V6.rational_turn_endpoint(phase_lo)
    right_endpoint = V6.rational_turn_endpoint(phase_hi)
    expected_count = V6._distinct_roots_open(poly, left_endpoint, right_endpoint)
    roots = candidate.get("ordered_open_roots")
    require(isinstance(roots, list) and len(roots) == expected_count,
            "V6 ordered source-root list incomplete")

    certified_phase_endpoints = {phase_lo: left_endpoint, phase_hi: right_endpoint}
    seen_x_ranks = set()
    for index, root in enumerate(roots):
        require(root.get("source_order_index") == index, "source root index changed")
        require(root.get("source_identity") ==
                "UNIQUE_PREIMAGE_UNDER_AFFINE_PHASE_AND_POLE_FREE_MONOTONE_TAN_HALF",
                "source-root identity changed")
        kind = root.get("tan_half_kind")
        if kind == "RATIONAL":
            x = IDENTITY.q_exact(root["tan_half_value"])
            require(EE.peval(poly, x) == 0, "rational tan-half descriptor is not a root")
            raw = {"kind": "RATIONAL_TAN_HALF_ROOT", "x_value": x}
            root_left = root_right = x_rational(x)
        else:
            require(kind == "UNIQUE_REAL_ALGEBRAIC", "unknown tan-half root kind")
            bracket = root.get("tan_half_bracket")
            require(isinstance(bracket, dict), "missing exact tan-half root bracket")
            root_left = endpoint_from_descriptor(
                bracket["left"], certified_phase_endpoints=certified_phase_endpoints)
            root_right = endpoint_from_descriptor(
                bracket["right"], certified_phase_endpoints=certified_phase_endpoints)
            require(V6._distinct_roots_open(
                EE.square_free(poly), root_left, root_right) == 1,
                "exact tan-half bracket does not isolate one root")
            require(root.get("tan_half_defining_polynomial") ==
                    [str(x) for x in EE.square_free(poly)],
                    "tan-half defining polynomial changed")
            raw = {
                "kind": "UNIQUE_TAN_HALF_ROOT",
                "left_endpoint": root_left,
                "right_endpoint": root_right,
            }

        x_rank = V6._distinct_roots_open(poly, left_endpoint, root_left)
        # The open count excludes a rational root at the isolating left
        # boundary. Include it when this is a later nonrational root, but
        # never include the original (open) source-window endpoint.
        if kind == "UNIQUE_REAL_ALGEBRAIC" and root_left["kind"] == "RATIONAL":
            boundary = root_left["value"]
            if not (left_endpoint["kind"] == "RATIONAL" and
                    left_endpoint["value"] == boundary):
                if EE.peval(poly, boundary) == 0:
                    x_rank += 1
        require(x_rank not in seen_x_ranks, "duplicate tan-half root rank")
        seen_x_ranks.add(x_rank)
        require(root.get("x_order_index") == x_rank,
                "tan-half root rank disagrees with exact left root count")
        expected_source_index = x_rank if phase_rate > 0 else expected_count - 1 - x_rank
        require(index == expected_source_index,
                "tan-half root rank was not transferred to source order")

        multiplicity = x_root_multiplicity(poly, raw)
        x_left_sign, x_right_sign = x_root_signs(poly, raw)
        require(root.get("multiplicity") == multiplicity,
                "V6 root multiplicity changed")
        require(root.get("x_left_sign") == x_left_sign and
                root.get("x_right_sign") == x_right_sign,
                "V6 tan-half adjacent sign changed")
        expected_source_left = x_left_sign if phase_rate > 0 else x_right_sign
        expected_source_right = x_right_sign if phase_rate > 0 else x_left_sign
        require(root.get("source_left_sign") == expected_source_left and
                root.get("source_right_sign") == expected_source_right,
                "V6 source-order adjacent sign changed")
        require(root.get("event_kind") == ("CROSSING" if multiplicity % 2 else "TANGENCY"),
                "V6 root parity/event kind changed")
        require(root.get("minimal_source_polynomial_claimed") is False and
                root.get("source_closed_form_claimed") is False,
                "candidate invented source-coordinate algebraic authority")
    require(seen_x_ranks == set(range(expected_count)),
            "V6 candidate did not cover every exact tan-half root rank")

    source_left_endpoint = V6.rational_turn_endpoint(turn_left)
    source_right_endpoint = V6.rational_turn_endpoint(turn_right)
    left_event = V6._event_at_endpoint(poly, source_left_endpoint)
    right_event = V6._event_at_endpoint(poly, source_right_endpoint)
    left_mult = int(left_event.get("multiplicity", 0)) if left_event.get("relation") == "ZERO" else 0
    right_mult = int(right_event.get("multiplicity", 0)) if right_event.get("relation") == "ZERO" else 0
    left_phase_side = "right" if phase_rate > 0 else "left"
    right_phase_side = "left" if phase_rate > 0 else "right"
    left_inward = V6._one_sided_sign_at_endpoint(poly, source_left_endpoint, left_phase_side)
    right_inward = V6._one_sided_sign_at_endpoint(poly, source_right_endpoint, right_phase_side)
    require(candidate["left_endpoint"] == {
                "relation": left_event["relation"],
                "multiplicity": left_mult,
                "inward_sign": left_inward,
            }, "V6 left source endpoint changed")
    require(candidate["right_endpoint"] == {
                "relation": right_event["relation"],
                "multiplicity": right_mult,
                "inward_sign": right_inward,
            }, "V6 right source endpoint changed")

    cells = candidate.get("sign_cells")
    require(isinstance(cells, list) and len(cells) == len(roots) + 1,
            "V6 source sign-cell cardinality mismatch")
    for index, cell in enumerate(cells):
        require(cell.get("index") == index and
                cell.get("complete_open_source_cell") is True,
                "V6 source cell index/completeness changed")
        expected_left_boundary = (
            {"kind": "LEFT_SOURCE_ENDPOINT"} if index == 0
            else {"kind": "ROOT", "root_index": index - 1})
        expected_right_boundary = (
            {"kind": "RIGHT_SOURCE_ENDPOINT"} if index == len(roots)
            else {"kind": "ROOT", "root_index": index})
        require(cell.get("left_boundary") == expected_left_boundary and
                cell.get("right_boundary") == expected_right_boundary,
                "V6 source cell exact boundaries changed")
        expected_sign = (
            left_inward if index == 0 else roots[index - 1]["source_right_sign"])
        if index < len(roots):
            require(expected_sign == roots[index]["source_left_sign"],
                    "V6 adjacent source-root signs disagree")
        else:
            require(expected_sign == right_inward,
                    "V6 final source-cell sign disagrees with endpoint")
        require(cell.get("sign") == ("POSITIVE" if expected_sign > 0 else "NEGATIVE"),
                "V6 complete source-cell sign changed")

    summary = candidate.get("summary", {})
    expected_multiple = sum(root["multiplicity"] > 1 for root in roots)
    expected_crossings = sum(root["multiplicity"] % 2 == 1 for root in roots)
    expected_tangencies = sum(root["multiplicity"] % 2 == 0 for root in roots)
    require(summary.get("distinct_roots_open") == expected_count,
            "V6 summary distinct-root count changed")
    require(summary.get("multiple_roots_open") == expected_multiple,
            "V6 summary multiple-root count changed")
    require(summary.get("crossings_open") == expected_crossings and
            summary.get("tangencies_open") == expected_tangencies,
            "V6 summary parity counts changed")
    require(summary.get("left_endpoint_root") is bool(left_mult) and
            summary.get("right_endpoint_root") is bool(right_mult),
            "V6 summary endpoint-root flags changed")
    require(summary.get("total_distinct_roots_closed") ==
            expected_count + int(bool(left_mult)) + int(bool(right_mult)),
            "V6 summary closed-root count changed")
    require(candidate.get("tan_half_chart_is_internal_only") is True and
            candidate.get("source_root_coordinates_closed_form_claimed") is False and
            candidate.get("mc_b_or_native_claimed") is False,
            "V6 candidate broadened chart/programme authority")
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
            "schema": SCHEMA, "status": "RESOURCE_REFUSAL",
            "reason": str(exc), "source_sha256": source_digest,
            "is_truth_value": False, "mc_b_or_native_claimed": False,
        }
    except RESOURCE_ERRORS as exc:
        return {
            "schema": SCHEMA, "status": "RESOURCE_REFUSAL",
            "reason": "V6_SOURCE_ORDER_RUNTIME_RESOURCE_LIMIT",
            "exception_type": type(exc).__name__, "source_sha256": source_digest,
            "is_truth_value": False, "mc_b_or_native_claimed": False,
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
        index for index, span in enumerate(reconstructed) if span.get("owner") == OWNER}
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
        "cos_splines": cos or {}, "sin_splines": sin or {},
        "parameter_lo": lo, "parameter_hi": hi,
        "phase_turn_offset": offset, "phase_turn_rate": rate,
        "source_parameter_id": "v6-source-u",
    }


def synthetic_controls():
    positive = fixture(
        cos={"0": spline_constant("-1/3"), "1": spline_constant(1)},
        offset="-1/4", rate="1/2")
    negative = fixture(
        cos={"0": spline_constant("-1/3"), "1": spline_constant(1)},
        offset="1/4", rate="-1/2")
    p = build_source_candidate(positive)
    n = build_source_candidate(negative)
    require(p["status"] == n["status"] == "V6_SOURCE_ORDERED_VIEWS_CERTIFIED",
            "positive/negative V6 order controls did not certify")
    validate_source_candidate(p, positive)
    validate_source_candidate(n, negative)
    p_roots = p["views"][0]["ordered_view"]["ordered_open_roots"]
    n_roots = n["views"][0]["ordered_view"]["ordered_open_roots"]
    require(len(p_roots) == len(n_roots) == 2, "expected two nonrational V6 roots")
    require([root["x_order_index"] for root in p_roots] == [0, 1],
            "positive-rate source order does not follow tan-half order")
    require([root["x_order_index"] for root in n_roots] == [1, 0],
            "negative-rate source order was not reversed")

    # x*(1-5*x*x) has a rational split root at x=0 and irrational
    # roots at +/-1/sqrt(5). The right root retains x=0 as its initial
    # open isolating boundary; its rank must still include that root.
    mixed = fixture(
        sin={"1": spline_constant("1"), "2": spline_constant("-3/4")},
        offset="-1/4", rate="1/2")
    mixed_candidate = build_source_candidate(mixed)
    require(mixed_candidate["status"] == "V6_SOURCE_ORDERED_VIEWS_CERTIFIED",
            "mixed rational/algebraic V6 control did not certify")
    validate_source_candidate(mixed_candidate, mixed)
    mixed_roots = mixed_candidate["views"][0]["ordered_view"]["ordered_open_roots"]
    require(len(mixed_roots) == 3 and
            [root["x_order_index"] for root in mixed_roots] == [0, 1, 2] and
            [root["tan_half_kind"] for root in mixed_roots] ==
            ["UNIQUE_REAL_ALGEBRAIC", "RATIONAL", "UNIQUE_REAL_ALGEBRAIC"],
            "mixed rational/algebraic root ranks are incomplete or misordered")

    repeated = fixture(
        cos={
            "0": spline_constant("11/18"),
            "1": spline_constant("-2/3"),
            "2": spline_constant("1/2"),
        },
        offset="-1/4", rate="1/2")
    result = build_source_candidate(repeated)
    require(result["status"] == "V6_SOURCE_ORDERED_VIEWS_CERTIFIED",
            "repeated V6 control did not certify")
    validate_source_candidate(result, repeated)
    roots = result["views"][0]["ordered_view"]["ordered_open_roots"]
    require([root["multiplicity"] for root in roots] == [2, 2] and
            all(root["event_kind"] == "TANGENCY" for root in roots),
            "V6 multiplicity/parity transfer failed")

    # Exact source-endpoint roots with no open roots. The second case uses
    # negative phase rate so source-right maps to the lower phase endpoint.
    left_endpoint_root = fixture(
        sin={"1": spline_constant(1)}, offset="0", rate="1/4")
    left_result = build_source_candidate(left_endpoint_root)
    require(left_result["status"] == "V6_SOURCE_ORDERED_VIEWS_CERTIFIED",
            "left source-endpoint root control did not certify")
    validate_source_candidate(left_result, left_endpoint_root)
    left_view = left_result["views"][0]["ordered_view"]
    require(left_view["summary"]["distinct_roots_open"] == 0 and
            left_view["left_endpoint"]["relation"] == "ZERO" and
            left_view["left_endpoint"]["multiplicity"] == 1 and
            left_view["summary"]["left_endpoint_root"] is True and
            left_view["summary"]["right_endpoint_root"] is False,
            "left source-endpoint root evidence mismatch")

    right_endpoint_root_negative = fixture(
        sin={"1": spline_constant(1)}, offset="1/4", rate="-1/4")
    right_result = build_source_candidate(right_endpoint_root_negative)
    require(right_result["status"] == "V6_SOURCE_ORDERED_VIEWS_CERTIFIED",
            "negative-rate right source-endpoint root control did not certify")
    validate_source_candidate(right_result, right_endpoint_root_negative)
    right_view = right_result["views"][0]["ordered_view"]
    require(right_view["summary"]["distinct_roots_open"] == 0 and
            right_view["right_endpoint"]["relation"] == "ZERO" and
            right_view["right_endpoint"]["multiplicity"] == 1 and
            right_view["summary"]["right_endpoint_root"] is True and
            right_view["summary"]["left_endpoint_root"] is False,
            "negative-rate right source-endpoint root evidence mismatch")

    refused = build_source_candidate(positive, max_bisections=0)
    require(refused["status"] == "RESOURCE_REFUSAL" and
            refused["is_truth_value"] is False,
            "V6 isolation budget was treated as mathematical truth")

    identity = fixture(cos={"0": spline_constant(0)}, offset="0", rate="1/4")
    require(build_source_candidate(identity)["status"] ==
            "OUTSIDE_CERTIFIED_V6_CONSTANT_MODULATION_SCOPE",
            "V6 identity-zero route was treated as isolated roots")

    pole = fixture(cos={"1": spline_constant(1)}, offset="1/4", rate="1/2")
    require(build_source_candidate(pole)["status"] ==
            "OUTSIDE_CERTIFIED_V6_CONSTANT_MODULATION_SCOPE",
            "V6 pole-crossing route was treated as source ordered")
    return True


def mutation_controls():
    spec = fixture(
        cos={"0": spline_constant("-1/3"), "1": spline_constant(1)},
        offset="-1/4", rate="1/2")
    candidate = build_source_candidate(spec)
    validate_source_candidate(candidate, spec)

    def rejected(mutator, reason, *, original=candidate, source=spec):
        forged = copy.deepcopy(original)
        mutator(forged)
        try:
            validate_source_candidate(forged, source)
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
        "complete_open_source_cell", False), "downgraded V6 source cell was accepted")
    rejected(lambda c: c["views"][0]["ordered_view"].__setitem__(
        "phase_affine_map", ["0", "999"]), "forged V6 phase map was accepted")
    rejected(lambda c: c["views"][0]["ordered_view"]["summary"].__setitem__(
        "crossings_open", 99), "forged V6 summary was accepted")

    # Phase +/-1/5 has genuine algebraic tangent window endpoints; the roots
    # cos(2*pi*t)=1/3 lie strictly within that window and near its boundaries.
    # Changing only a serialized turn or root-rank metadata used to pass the
    # numerical root/sign checks despite falsifying the physical source claim.
    boundary_spec = fixture(
        cos={"0": spline_constant("-1/3"), "1": spline_constant(1)},
        offset="-1/5", rate="2/5")
    boundary_candidate = build_source_candidate(boundary_spec)
    require(boundary_candidate["status"] == "V6_SOURCE_ORDERED_VIEWS_CERTIFIED",
            "algebraic endpoint provenance control did not certify")
    validate_source_candidate(boundary_candidate, boundary_spec)

    def algebraic_boundaries(candidate):
        return [
            end
            for view in candidate["views"]
            for root in view["ordered_view"]["ordered_open_roots"]
            if root["tan_half_kind"] == "UNIQUE_REAL_ALGEBRAIC"
            for end in root["tan_half_bracket"].values()
            if end["kind"] == "ALGEBRAIC_X"
        ]

    require(algebraic_boundaries(boundary_candidate),
            "algebraic endpoint provenance mutation control is vacuous")

    def wrong_turn(candidate):
        algebraic_boundaries(candidate)[0]["turn"] = "7/9"

    def wrong_rank(candidate):
        algebraic_boundaries(candidate)[0]["root_rank_abs"] += 1

    def wrong_principal(candidate):
        algebraic_boundaries(candidate)[0]["principal_turn"] = "7/9"

    def wrong_denominator(candidate):
        algebraic_boundaries(candidate)[0]["denominator"] += 1

    def wrong_polynomial(candidate):
        endpoint = algebraic_boundaries(candidate)[0]
        endpoint["defining_polynomial"][0] = str(
            IDENTITY.q_exact(endpoint["defining_polynomial"][0]) + 1)

    def wrong_interval(candidate):
        algebraic_boundaries(candidate)[0]["isolating_interval"] = ["0", "1/100"]

    rejected(wrong_turn, "forged algebraic endpoint source turn was accepted",
             original=boundary_candidate, source=boundary_spec)
    rejected(wrong_rank, "forged algebraic endpoint root rank was accepted",
             original=boundary_candidate, source=boundary_spec)
    rejected(wrong_principal, "forged algebraic endpoint principal turn was accepted",
             original=boundary_candidate, source=boundary_spec)
    rejected(wrong_denominator, "forged algebraic endpoint denominator was accepted",
             original=boundary_candidate, source=boundary_spec)
    rejected(wrong_polynomial, "forged algebraic endpoint polynomial was accepted",
             original=boundary_candidate, source=boundary_spec)
    rejected(wrong_interval, "forged algebraic endpoint interval was accepted",
             original=boundary_candidate, source=boundary_spec)

    # Nonvacuous omitted-span attack: preserve a valid remaining view and
    # adjust the declared count so only exact set-equality can reject it.
    two_span_spec = fixture(
        cos={"1": {
            "degree": 0,
            "knots": ["0", "1", "2"],
            "controls": ["1", "1"],
        }},
        offset="0", rate="1/8", lo="0", hi="2")
    two_span_candidate = build_source_candidate(two_span_spec)
    require(two_span_candidate["status"] == "V6_SOURCE_ORDERED_VIEWS_CERTIFIED" and
            two_span_candidate["v6_span_count"] == 2 and
            len(two_span_candidate["views"]) == 2,
            "two-span omission control did not construct two V6 views")
    forged = copy.deepcopy(two_span_candidate)
    forged["views"].pop()
    forged["v6_span_count"] = 1
    try:
        validate_source_candidate(forged, two_span_spec)
    except ValueError as exc:
        require(str(exc) == "candidate omitted or invented a certified V6 span",
                f"two-span omission rejected for the wrong reason: {exc}")
    else:
        raise AssertionError("multi-span V6 omission with adjusted count was accepted")
    return True


def frozen_corpus_controls():
    require(git_blob(CORPUS.read_bytes()) == CORPUS_BLOB, "frozen v54 corpus drifted")
    corpus = json.loads(CORPUS.read_text())
    mentioned = [
        row for row in corpus["cases"]
        if OWNER in json.dumps(row.get("expected", {}), sort_keys=True)]
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
                    f"frozen certified V6 case failed: {row['id']} "
                    f"status={candidate.get('status')} reason={candidate.get('reason')}")
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
    print("PASS: monotone-chart source order including negative phase rate, repeated-root parity and typed refusal")
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
