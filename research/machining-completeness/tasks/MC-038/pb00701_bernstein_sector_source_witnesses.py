#!/usr/bin/env python3
"""Three exact original-source event witnesses from Bernstein/sector bounds.

Two small sufficient-condition checkers reconstruct every bound from the
original two-span B-spline controls. The frozen wrapper separately binds source,
whole-row provenance, historical dispositions and the original phase. Neither
checker changes a historical owner route or establishes a programme gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction as Q
from math import comb, gcd
from pathlib import Path
import re
import sys
import types

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SCHEMA = "radicadsac-mc038-bernstein-sector-source-witnesses/1.0"
REPORT = HERE / "pb00701-bernstein-sector-source-witnesses.json"
BASE_MAIN = "e0514500aeca59afa4924dcc2da3ca0c2688d9ac"
ORDER_GAP = "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"
V18 = "PB00701_V18_EXACT_NONVANISHING_SOURCE_MODULE_FACTOR"
V26 = "PB00701_V26_EXACT_POINTWISE_COMPONENT_CONE_RESIDUAL_ORTHANTS"
CASES = {
    "composite:" + V18 + ":tail0": {
        "source_sha256": "2c0db76bcf217c98b53d8b45ee537aec4da818c649df2436c27860a4d8c17111",
        "row_sha256": "06f88535a67c3d521d831f2205b69c3466ff4a2723cdb53b37c5e430b24c04c8",
        "origin": "verify_pb00701_v53", "first_owner": V18,
        "second_owner": "EXACT_RATIONAL_AMPLITUDE_DOMINANCE",
        "proof_family": "DOMINANCE_CONSTANT_TAIL", "root_count": 0,
    },
    "composite:" + V18 + ":tail100": {
        "source_sha256": "2b1f53109ad708bd6eab37e83529e1001a7cadfa82fe630ddf230d94f2132d29",
        "row_sha256": "fa9de27d0eead12eb2c8cee6e49b4b51ba6508e1b1c9dbc8b6e5620c2d15ddf6",
        "origin": "verify_pb00701_v53", "first_owner": V18,
        "second_owner": "PB00701_V19_EXACT_MULTI_HARMONIC_MONOTONE_ANCHOR",
        "proof_family": "DOMINANCE_INCREASING_TAIL", "root_count": 1,
    },
    "composite:" + V26 + ":tail0": {
        "source_sha256": "a9bb78a5415d1c45f54be7838f77739c8854cf329a97b36576f2a2fedf4ed3e4",
        "row_sha256": "333c1bf98905cd41773c7da92efd33f36dc2f1e1bc947b285d9175a4926a25ad",
        "origin": "verify_pb00701_v26", "first_owner": V26,
        "second_owner": "PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION",
        "proof_family": "BERNSTEIN_PHASE_SECTOR_CROSSING", "root_count": 1,
    },
}
PINS = {
    "pb00701-finite-owner-corpus-v54.json": "5841c331579489b25caef38cd412bdbf286f9134",
    "pb00701-finite-owner-inventory-v54.json": "8649c20ab77e199f9c3fa351b8b6742218f27abb",
    "pb00701-finite-owner-coverage-v54.json": "600ba29786f50397f29fd435fc5e2c57076088f9",
    "verify_pb00701_post_v54_frontier.py": "12c6efeb667a954ffc5a7e27849ae815d466580a",
}
ROOT_PINS = {
    "research/machining-completeness/tasks/MC-002/domain-contract-v1.json":
        "23de82f5240a72509f7afe4acd5948b65bc4ff13",
    "research/machining-completeness/programme-v1.json":
        "dee7045a1790b2870744df8ae7693429bd1d81a6",
    "handoffs/current-authority.json": "fa0233323a0804d8a5d3eb7cd892a274a6173fab",
}
MAX_JSON_BYTES = 262144
MAX_DEPENDENCY_BYTES = 1048576
MAX_NODES = 32768
MAX_DEPTH = 24
MAX_DEGREE = 12
MAX_DERIVED_BITS = 4096
RATIONAL_TOKEN = re.compile(r"(-?)(0|[1-9][0-9]{0,77})(?:/([1-9][0-9]{0,77}))?")
PI_LOWER = Q(3)
PI_UPPER = Q(22, 7)


class Refusal(ValueError):
    """Unsupported premises and resource limits are nontruth, never evidence."""


def need(ok, reason):
    if not ok:
        raise Refusal(reason)


def canonical(value):
    """Preflight bounded typed JSON before serialization, hashing or parsing."""
    stack, active = [(value, 0, False)], set()
    count = byte_budget = 0
    while stack:
        obj, depth, leaving = stack.pop()
        if leaving:
            active.remove(id(obj))
            continue
        count += 1
        need(count <= MAX_NODES and depth <= MAX_DEPTH,
             "RESOURCE_REFUSAL: JSON node/depth budget")
        if type(obj) in (dict, list):
            need(id(obj) not in active and len(obj) <= 512,
                 "RESOURCE_REFUSAL: JSON cycle/container budget")
            active.add(id(obj))
            byte_budget += 2 + 2 * len(obj)
            stack.append((obj, depth, True))
            if type(obj) is dict:
                for key, child in obj.items():
                    need(type(key) is str and len(key) <= 256,
                         "RESOURCE_REFUSAL: JSON key")
                    byte_budget += len(json.dumps(key, ensure_ascii=True))
                    stack.append((child, depth + 1, False))
            else:
                stack.extend((child, depth + 1, False) for child in obj)
        elif type(obj) is str:
            need(len(obj) <= 4096, "RESOURCE_REFUSAL: JSON string")
            byte_budget += len(json.dumps(obj, ensure_ascii=True))
        elif type(obj) is int:
            need(obj.bit_length() <= 256, "RESOURCE_REFUSAL: JSON integer")
            byte_budget += len(str(obj))
        else:
            need(obj is None or type(obj) is bool,
                 "SEMANTIC_BLOCKER: binary float or non-JSON scalar")
            byte_budget += 5
        need(byte_budget <= MAX_JSON_BYTES,
             "RESOURCE_REFUSAL: aggregate JSON bytes")
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=True, allow_nan=False).encode("ascii")
    need(len(raw) <= MAX_JSON_BYTES, "RESOURCE_REFUSAL: JSON bytes")
    return raw


def exact(value):
    """Canonical bounded ASCII rational; reject exponents before Fraction."""
    need(type(value) is str, "SEMANTIC_BLOCKER: rational string required")
    need(len(value) <= 160, "RESOURCE_REFUSAL: rational token length")
    token = RATIONAL_TOKEN.fullmatch(value)
    need(token is not None, "SEMANTIC_BLOCKER: noncanonical ASCII rational")
    sign, numerator_token, denominator_token = token.groups()
    need(not (sign and numerator_token == "0"),
         "SEMANTIC_BLOCKER: negative zero")
    numerator = int(numerator_token) * (-1 if sign else 1)
    denominator = int(denominator_token) if denominator_token is not None else 1
    need(max(numerator.bit_length(), denominator.bit_length()) <= 256,
         "RESOURCE_REFUSAL: rational bit budget")
    need(denominator_token is None or denominator > 1,
         "SEMANTIC_BLOCKER: denominator one is not canonical")
    need(gcd(abs(numerator), denominator) == 1,
         "SEMANTIC_BLOCKER: unreduced rational")
    return Q(numerator, denominator)


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def bounded_file(path, limit):
    try:
        with Path(path).open("rb") as stream:
            raw = stream.read(limit + 1)
    except OSError as exc:
        raise Refusal("SEMANTIC_BLOCKER: source file unavailable") from exc
    need(len(raw) <= limit, "RESOURCE_REFUSAL: file byte budget")
    return raw


def blob(path):
    raw = bounded_file(path, MAX_DEPENDENCY_BYTES)
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def pin(path, expected):
    pinned_bytes(path, expected)


def pinned_bytes(path, expected):
    raw = bounded_file(path, MAX_DEPENDENCY_BYTES)
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    need(actual == expected, "SEMANTIC_BLOCKER: pinned source drift: " + str(path))
    return raw


def unique_pairs(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, "SEMANTIC_BLOCKER: duplicate JSON key")
        out[key] = value
    return out


def json_integer(token):
    need(len(token.lstrip("-")) <= 78, "RESOURCE_REFUSAL: JSON integer token")
    value = int(token)
    need(value.bit_length() <= 256, "RESOURCE_REFUSAL: JSON integer bits")
    return value


def reject_nonexact(_):
    raise Refusal("SEMANTIC_BLOCKER: nonexact JSON numeric token")


def decode_json(raw):
    need(type(raw) is bytes and len(raw) <= MAX_DEPENDENCY_BYTES,
         "RESOURCE_REFUSAL: JSON decode input bytes")
    try:
        value = json.loads(raw, object_pairs_hook=unique_pairs,
                           parse_int=json_integer, parse_float=reject_nonexact,
                           parse_constant=reject_nonexact)
    except (RecursionError, UnicodeError, json.JSONDecodeError) as exc:
        raise Refusal("SEMANTIC_BLOCKER: invalid or excessive JSON") from exc
    canonical(value)
    return value


def read_json(path, *, dependency=False):
    raw = bounded_file(path, MAX_DEPENDENCY_BYTES if dependency else MAX_JSON_BYTES)
    return decode_json(raw)


def pinned_json(path, expected):
    # Hash and parse the same bounded byte buffer: no mutable-file reread
    # may substitute a different original after the custody check.
    return decode_json(pinned_bytes(path, expected))


def read_report(path=REPORT):
    return read_json(path)


def rational_controls(controls):
    need(type(controls) in (list, tuple) and 1 <= len(controls) <= MAX_DEGREE + 1,
         "RESOURCE_REFUSAL: bounded Bernstein control list required")
    need(all(type(x) is Q for x in controls),
         "SEMANTIC_BLOCKER: exact Fraction controls required")
    need(all(max(x.numerator.bit_length(), x.denominator.bit_length()) <=
             MAX_DERIVED_BITS for x in controls),
         "RESOURCE_REFUSAL: derived rational bit budget")
    return list(controls)


def power_coefficients(controls):
    """Exact expansion of a unit-span Bernstein polynomial, for identity checks."""
    controls = rational_controls(controls)
    n = len(controls) - 1
    result = [Q(0)] * (n + 1)
    for i, value in enumerate(controls):
        for j in range(n - i + 1):
            result[i+j] += value * comb(n, i) * comb(n-i, j) * (-1)**j
    return rational_controls(result)


def derivative_controls(controls):
    controls = rational_controls(controls)
    n = len(controls) - 1
    if n == 0:
        return [Q(0)]
    result = [n*(b-a) for a, b in zip(controls, controls[1:])]
    original_power = power_coefficients(controls)
    need(power_coefficients(result) ==
         [i*original_power[i] for i in range(1, len(original_power))],
         "SEMANTIC_BLOCKER: Bernstein derivative identity")
    return result


def split_controls(controls, at=Q(1, 2)):
    """de Casteljau controls for [0,at] and [at,1], each in local unit time."""
    controls = rational_controls(controls)
    need(type(at) is Q and Q(0) < at < Q(1) and
         max(at.numerator.bit_length(), at.denominator.bit_length()) <= 256,
         "SEMANTIC_BLOCKER: bounded interior rational subdivision required")
    layers = [controls]
    while len(layers[-1]) > 1:
        last = layers[-1]
        layers.append([(1-at)*a+at*b for a, b in zip(last, last[1:])])
    left, right = [x[0] for x in layers], [x[-1] for x in reversed(layers)]
    # Independently expand the affine substitution p(at+(1-at)*u).
    original = power_coefficients(controls)
    expected = [sum(original[k]*comb(k, j)*at**(k-j)*(1-at)**j
                    for k in range(j, len(original))) for j in range(len(original))]
    need(power_coefficients(right) == expected,
         "SEMANTIC_BLOCKER: right Bernstein restriction identity")
    need(power_coefficients(left) == [a*at**i for i, a in enumerate(original)],
         "SEMANTIC_BLOCKER: left Bernstein restriction identity")
    return left, right


def two_span_controls(spline):
    need(type(spline) is dict and set(spline) == {"degree", "knots", "controls"},
         "SEMANTIC_BLOCKER: unknown spline fields")
    degree = spline["degree"]
    need(type(degree) is int, "SEMANTIC_BLOCKER: integer degree required")
    need(0 <= degree <= MAX_DEGREE, "RESOURCE_REFUSAL: spline degree")
    width = degree + 1
    need(type(spline["knots"]) is list and
         spline["knots"] == ["0"]*width+["1"]*width+["2"]*width,
         "SEMANTIC_BLOCKER: not original fully clamped two-unit-span knots")
    need(type(spline["controls"]) is list and len(spline["controls"]) == 2*width,
         "SEMANTIC_BLOCKER: original two-span control count")
    controls = [exact(value) for value in spline["controls"]]
    left, right = controls[:width], controls[width:]
    need(left[-1] == right[0], "SEMANTIC_BLOCKER: discontinuous original source knot")
    return left, right


def parse_source(spec, cosine_keys, sine_keys, phase):
    canonical(spec)
    need(type(spec) is dict and set(spec) == {
        "grammar", "source_parameter_id", "parameter_lo", "parameter_hi",
        "phase_turn_offset", "phase_turn_rate", "cos_splines", "sin_splines"},
        "SEMANTIC_BLOCKER: unknown source fields")
    need(spec["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE" and
         type(spec["source_parameter_id"]) is str and
         0 < len(spec["source_parameter_id"]) <= 128,
         "SEMANTIC_BLOCKER: source grammar or parameter identity")
    need((exact(spec["parameter_lo"]), exact(spec["parameter_hi"])) == (Q(0), Q(2)),
         "SEMANTIC_BLOCKER: source interval is not [0,2]")
    need((exact(spec["phase_turn_offset"]), exact(spec["phase_turn_rate"])) == phase,
         "SEMANTIC_BLOCKER: phase does not satisfy the proved sectors")
    need(type(spec["cos_splines"]) is dict and set(spec["cos_splines"]) == cosine_keys
         and type(spec["sin_splines"]) is dict and set(spec["sin_splines"]) == sine_keys,
         "SEMANTIC_BLOCKER: unsupported harmonic or omitted residual")
    result = {}
    for prefix, key in (("C", "cos_splines"), ("S", "sin_splines")):
        for harmonic, spline in spec[key].items():
            result[prefix+harmonic] = two_span_controls(spline)
    return result


def blocks_record(blocks):
    return {name: {"degree": len(left)-1,
                   "first_span_controls": [str(x) for x in left],
                   "second_span_controls": [str(x) for x in right],
                   "original_knot_value": str(left[-1])}
            for name, (left, right) in sorted(blocks.items())}


def constant(controls):
    controls = rational_controls(controls)
    need(all(x == controls[0] for x in controls),
         "SEMANTIC_BLOCKER: required constant original amplitude is nonconstant")
    return controls[0]


def point(at):
    return {"kind": "RATIONAL", "value": str(at)}


def physical_events(spec, *, signs, knot_sign, endpoint_bounds,
                    bracket=None, monotone_span=None, proof_cuts=()):
    """Describe exact implicit roots, never rationalize their bracket endpoints."""
    events = []
    if bracket is not None:
        events.append({
            "event_id": "root-0", "location": "ORIGINAL_SOURCE_SPAN_INTERIOR",
            "coordinate": {"kind": "IMPLICIT_ORIGINAL_SOURCE_ROOT",
                           "original_source_sha256": digest(spec),
                           "source_parameter_id": spec["source_parameter_id"],
                           "defining_predicate": "ORIGINAL_SOURCE_F_EQUALS_ZERO",
                           "isolating_interval": [str(x) for x in bracket],
                           "isolating_interval_open": True,
                           "uniqueness_cell": [str(x) for x in monotone_span]},
            "analytic_order": 1, "left_sign": signs[0], "right_sign": signs[1],
            "multiplicity_basis": "STRICT_NONZERO_FIRST_DERIVATIVE_AT_ROOT",
        })
    edges = [point(0)] + ([{"kind": "EVENT_REFERENCE", "event_id": "root-0"}]
                         if events else []) + [point(2)]
    cells = [{"left": edges[i], "right": edges[i+1],
              "left_closed": i == 0, "right_closed": i == len(signs)-1,
              "sign": sign} for i, sign in enumerate(signs)]
    return {
        "source_interval": ["0", "2"], "original_source_piece_edges": ["0", "1", "2"],
        "closed_distinct_root_count": len(events), "open_distinct_root_count": len(events),
        "events": events, "maximal_sign_cells": cells,
        "exterior_endpoints": endpoint_bounds,
        "interior_source_knots": [{"parameter": "1", "source_continuous": True,
                                    "value_sign": knot_sign, "left_sign": knot_sign,
                                    "right_sign": knot_sign, "is_zero_event": False}],
        "proof_cuts": list(proof_cuts), "continuum_zero_component": False,
        "complete_for_original_closed_source": True,
    }


def endpoint(at, sign, bound_type, bound):
    return {"parameter": str(at), "sign": sign, "is_zero_event": False,
            "bound_type": bound_type, "bound": str(bound)}


def prove_dominance_source(spec):
    """Two-span C0+C1*cos(theta)+S2*sin(2theta), theta=pi*(1+t)/12.

    Strict first-span Bernstein amplitude dominance excludes all first roots.
    The second span has constant nonzero-harmonic amplitudes and an affine C0.
    It is either strictly negative everywhere, or has a positive derivative
    bound and an opposite-sign closed bracket inside the original second span.
    """
    blocks = parse_source(spec, {"0", "1"}, {"2"}, (Q(1, 24), Q(1, 24)))
    c0, c0_tail = blocks["C0"]
    c1, c1_tail = blocks["C1"]
    s2, s2_tail = blocks["S2"]
    c1_max, s2_max = max(map(abs, c1)), max(map(abs, s2))
    first_upper = max(c0) + c1_max + s2_max
    need(first_upper < 0, "SEMANTIC_BLOCKER: first-span strict dominance unavailable")
    a, b = constant(c1_tail), constant(s2_tail)
    slopes = derivative_controls(c0_tail)
    slope = constant(slopes)
    need(slope >= 0, "SEMANTIC_BLOCKER: tail slope outside nonnegative-ramp proof")
    tail_norm = abs(a) + abs(b)
    knot_upper = c0_tail[0] + tail_norm
    need(knot_upper < 0, "SEMANTIC_BLOCKER: original knot is not strictly negative")
    envelope = {
        "first_span": ["0", "1"], "first_C0_upper": str(max(c0)),
        "first_C1_absolute_upper": str(c1_max), "first_S2_absolute_upper": str(s2_max),
        "first_F_upper": str(first_upper), "original_knot_F_upper": str(knot_upper),
        "tail_C0_derivative_controls": [str(x) for x in slopes],
        "tail_C0_slope": str(slope), "tail_C1": str(a), "tail_S2": str(b),
        "tail_nonconstant_harmonic_absolute_upper": str(tail_norm),
    }
    cuts = []
    if slope == 0:
        family = "DOMINANCE_CONSTANT_TAIL"
        envelope["tail_F_upper"] = str(knot_upper)
        physical = physical_events(
            spec, signs=["NEGATIVE"], knot_sign="NEGATIVE",
            endpoint_bounds=[endpoint(0, "NEGATIVE", "UPPER", first_upper),
                             endpoint(2, "NEGATIVE", "UPPER", knot_upper)])
    else:
        family = "DOMINANCE_INCREASING_TAIL"
        derivative_lower = slope - PI_UPPER/Q(12)*(abs(a)+2*abs(b))
        right_bracket = Q(1001, 1000)
        bracket_lower = c0_tail[0] + slope*(right_bracket-1) - tail_norm
        endpoint_lower = c0_tail[-1] - tail_norm
        need(derivative_lower > 0,
             "SEMANTIC_BLOCKER: strict increasing tail derivative unavailable")
        need(bracket_lower > 0 and endpoint_lower > 0,
             "SEMANTIC_BLOCKER: positive tail bracket or exterior endpoint unavailable")
        envelope.update(tail_F_derivative_lower=str(derivative_lower),
                        bracket_right=str(right_bracket), bracket_right_F_lower=str(bracket_lower),
                        exterior_right_F_lower=str(endpoint_lower))
        cuts.append({"parameter": str(right_bracket), "kind": "BRACKET_ENDPOINT",
                     "value_sign": "POSITIVE", "is_zero_event": False})
        physical = physical_events(
            spec, signs=["NEGATIVE", "POSITIVE"], knot_sign="NEGATIVE",
            bracket=(Q(1), right_bracket), monotone_span=(Q(1), Q(2)), proof_cuts=cuts,
            endpoint_bounds=[endpoint(0, "NEGATIVE", "UPPER", first_upper),
                             endpoint(2, "POSITIVE", "LOWER", endpoint_lower)])
    return {"proof_family": family, "source_parameter_id": spec["source_parameter_id"],
            "phase_turn_law": {"offset": spec["phase_turn_offset"], "rate": spec["phase_turn_rate"]},
            "original_bernstein_blocks": blocks_record(blocks),
            "derived_envelopes": envelope, "physical_event_proof": physical}


def prove_sector_source(spec):
    """Quartic-or-bounded-degree positive amplitudes with theta=pi/3-2*pi*t/3.

    On [0,1/2], positive A/B and the first-quadrant phase prove F>0.
    On [1/2,1], right-half A'<=0 and a derived strict derivative bound give
    exactly one simple zero before the strictly negative original knot.
    Constant tails remain negative on two closed analytic phase sectors.
    """
    blocks = parse_source(spec, {"0", "1", "2"}, {"1"}, (Q(1, 6), Q(-1, 3)))
    need(all(x == 0 for side in blocks["C0"] for x in side),
         "SEMANTIC_BLOCKER: unaccounted harmonic-zero residual")
    a, a_tail = blocks["C1"]
    b, b_tail = blocks["S1"]
    eps = constant(blocks["C2"][0])
    need(constant(blocks["C2"][1]) == eps,
         "SEMANTIC_BLOCKER: second-harmonic residual changed across knot")
    need(min(a) > 0 and min(b) > 0,
         "SEMANTIC_BLOCKER: positive Bernstein amplitudes unavailable")
    tail_a, tail_b = constant(a_tail), constant(b_tail)
    first_lower = min(a)/2-abs(eps)
    need(first_lower > 0, "SEMANTIC_BLOCKER: first-half strict positivity unavailable")
    a_prime_right = split_controls(derivative_controls(a))[1]
    b_prime_right = split_controls(derivative_controls(b))[1]
    b_right = split_controls(b)[1]
    need(max(a_prime_right) <= 0,
         "SEMANTIC_BLOCKER: right-half A derivative has a positive control")
    b_prime_term = max(Q(0), -min(b_prime_right))
    b_right_lower = min(b_right)
    need(b_right_lower > 0, "SEMANTIC_BLOCKER: right-half B positivity unavailable")
    derivative_upper = b_prime_term-b_right_lower+4*PI_UPPER*abs(eps)/3
    need(derivative_upper < 0,
         "SEMANTIC_BLOCKER: strict decreasing crossing derivative unavailable")
    # At t=1: cos(theta)=1/2, sin(theta)=-sqrt(3)/2,
    # cos(2theta)=-1/2. Since sqrt(3)>1 and tail_b>0:
    knot_upper = (tail_a-tail_b)/2-eps/2
    sector_one_upper = (tail_a-tail_b)/2+abs(eps)
    sector_two_upper = -min(tail_a, tail_b)+abs(eps)
    need(knot_upper < 0 and sector_one_upper < 0 and sector_two_upper < 0,
         "SEMANTIC_BLOCKER: negative knot or tail phase-sector bound unavailable")
    # At t=2, theta=-pi, hence the exterior value is exact.
    exterior_right = -tail_a+eps
    need(exterior_right < 0, "SEMANTIC_BLOCKER: exterior right endpoint not negative")
    physical = physical_events(
        spec, signs=["POSITIVE", "NEGATIVE"], knot_sign="NEGATIVE",
        bracket=(Q(1, 2), Q(1)), monotone_span=(Q(1, 2), Q(1)),
        endpoint_bounds=[endpoint(0, "POSITIVE", "LOWER", first_lower),
                         endpoint(2, "NEGATIVE", "EXACT", exterior_right)],
        proof_cuts=[{"parameter": "1/2", "kind": "BRACKET_AND_PHASE_CELL_BOUNDARY",
                     "value_sign": "POSITIVE", "is_zero_event": False},
                    {"parameter": "5/4", "kind": "TAIL_PHASE_SECTOR_BOUNDARY",
                     "value_sign": "NEGATIVE", "is_zero_event": False}])
    return {
        "proof_family": "BERNSTEIN_PHASE_SECTOR_CROSSING",
        "source_parameter_id": spec["source_parameter_id"],
        "phase_turn_law": {"offset": spec["phase_turn_offset"], "rate": spec["phase_turn_rate"]},
        "original_bernstein_blocks": blocks_record(blocks),
        "derived_envelopes": {
            "first_half": ["0", "1/2"], "first_half_A_lower": str(min(a)),
            "first_half_B_lower": str(min(b)), "residual_C2": str(eps),
            "first_half_F_lower": str(first_lower),
            "right_half_A_derivative_controls": [str(x) for x in a_prime_right],
            "right_half_B_derivative_controls": [str(x) for x in b_prime_right],
            "right_half_B_controls": [str(x) for x in b_right],
            "right_half_B_lower": str(b_right_lower),
            "B_derivative_sine_upper": str(b_prime_term),
            "right_half_F_derivative_upper": str(derivative_upper),
            "original_knot_F_upper": str(knot_upper),
            "tail_constant_A": str(tail_a), "tail_constant_B": str(tail_b),
            "tail_sector_1": {"interval": ["1", "5/4"],
                              "phase_turn_interval": ["-1/4", "-1/6"],
                              "F_upper": str(sector_one_upper)},
            "tail_sector_2": {"interval": ["5/4", "2"],
                              "phase_turn_interval": ["-1/2", "-1/4"],
                              "F_upper": str(sector_two_upper)},
        },
        "physical_event_proof": physical,
    }


def historical_observation(case_id):
    item = CASES[case_id]
    return {"id": case_id, "observed": {"status": "CERTIFIED", "spans": [
        [item["first_owner"], "CERTIFIED", None],
        [item["second_owner"], "CERTIFIED", None]]}, "v54_disposition": ORDER_GAP}


def check_original(row):
    canonical(row)
    need(type(row) is dict and set(row) == {"id", "origin", "kind", "spec", "expected"},
         "SEMANTIC_BLOCKER: original row shape")
    need(type(row["id"]) is str and row["id"] in CASES,
         "SEMANTIC_BLOCKER: original source is outside the three-case selection")
    item = CASES[row["id"]]
    need(row["origin"] == item["origin"] and row["kind"] == "COMPOSITE_TAIL",
         "SEMANTIC_BLOCKER: original provenance drift")
    need(canonical(row["expected"]) == canonical(historical_observation(row["id"])),
         "SEMANTIC_BLOCKER: historical owner/disposition drift")
    need(digest(row["spec"]) == item["source_sha256"],
         "SEMANTIC_BLOCKER: original source SHA-256 drift")
    need(digest(row) == item["row_sha256"],
         "SEMANTIC_BLOCKER: original whole-row SHA-256 drift")
    proof = (prove_sector_source(row["spec"]) if item["first_owner"] == V26
             else prove_dominance_source(row["spec"]))
    need(proof["proof_family"] == item["proof_family"] and
         proof["physical_event_proof"]["closed_distinct_root_count"] == item["root_count"],
         "SEMANTIC_BLOCKER: frozen-source proof result changed")
    return proof


def load_originals():
    path = HERE / "verify_pb00701_post_v54_frontier.py"
    code = pinned_bytes(path, PINS[path.name])
    auditor = types.ModuleType("sector_witness_frozen_frontier")
    auditor.__file__ = str(path)
    exec(compile(code, str(path), "exec"), auditor.__dict__)
    # Only pinned original bytes reach the historical auditor/rational parser.
    # Public candidate reports and source helper inputs never flow into it.
    corpus, inventory, coverage = [pinned_json(HERE / name, PINS[name]) for name in
                                  list(PINS)[:3]]
    result = auditor.audit(corpus, inventory, coverage)
    need(result["cases"] == 121 and result["v54_dispositions"]["BLOCKED"] == 20 and
         result["v54_dispositions"][ORDER_GAP] == 30,
         "SEMANTIC_BLOCKER: frozen historical 121/20/30 census drift")
    selected = {row["id"]: row for row in corpus["cases"] if row["id"] in CASES}
    need(set(selected) == set(CASES), "SEMANTIC_BLOCKER: missing original source")
    domain, programme, auth = [pinned_json(ROOT / name, expected)
                               for name, expected in ROOT_PINS.items()]
    need(len(domain["coverage_rule"]["required_operation_ids"]) == 26,
         "SEMANTIC_BLOCKER: 26-operation domain drift")
    gates = {g["id"]: g["state"] for g in programme["gates"]}
    need(gates["MC-B"] == "NOT_ESTABLISHED" and
         programme["capability_status"] == auth["capability_status"] == "NOT_ESTABLISHED" and
         programme["production_authorized"] is False and auth["production_authorized"] is False,
         "SEMANTIC_BLOCKER: programme authority drift")
    for row in selected.values():
        check_original(row)
    return selected


def expected_report():
    originals = load_originals()
    witnesses = []
    for case_id in sorted(originals):
        row = originals[case_id]
        witnesses.append({
            "case_id": case_id, "original_source_sha256": digest(row["spec"]),
            "original_row_sha256": digest(row), "original_source": row["spec"],
            "historical_observation": row["expected"],
            "source_specific_proof": check_original(row),
        })
    return {
        "schema": SCHEMA, "task": "MC-038", "evidence_class": "DETERMINISTIC_MODEL",
        "source_baseline_main": BASE_MAIN,
        "dependencies": {"MC038_git_blobs": dict(PINS), "root_git_blobs": dict(ROOT_PINS)},
        "analytic_foundation": {"pi_bounds": {"lower": str(PI_LOWER), "upper": str(PI_UPPER),
                                              "both_strict": True,
                                              "basis": "CLASSICAL_ARCHIMEDEAN_BOUNDS"},
                                "bernstein_basis_nonnegative_partition_of_unity": True,
                                "de_casteljau_and_derivative_power_identities_rechecked": True,
                                "root_existence": "CONTINUITY_AND_OPPOSITE_STRICT_SIGNS",
                                "root_uniqueness_and_order": "STRICT_FIRST_DERIVATIVE_BOUND"},
        "source_witnesses": witnesses,
        "summary": {"complete_original_sources": 3, "root_free_sources": 1,
                    "one_simple_root_sources": 2, "continuum_sources": 0},
        "resources": {"native_campaign_run": False, "paid_campaign_run": False,
                      "method": "BOUNDED_EXACT_RATIONAL_BERNSTEIN_AND_PHASE_SECTOR_PROOFS",
                      "maximum_spline_degree": MAX_DEGREE,
                      "input_rational_bit_limit": 256,
                      "report_byte_limit": MAX_JSON_BYTES},
        "frozen_v54_census": {"original_sources": 121, "route_refusals": 20,
                              "missing_ordered_premises": 30,
                              "historical_dispositions_modified": False},
        "scope": {"selected_source_ids": sorted(CASES),
                  "complete_source_specific_mathematical_witnesses": True,
                  "historical_owner_routes_repaired": False,
                  "general_analytic_event_solver": False, "universal_proof_consumer": False,
                  "exhaustive_post_v54_census": False, "PB00701_closed": False,
                  "MC_B": "NOT_ESTABLISHED", "MC_1": "NOT_ESTABLISHED",
                  "production_authorized": False, "protected_operation_count": 26,
                  "native_material_topology_or_STEP_qualified": False},
    }


def validate_report(candidate):
    actual = canonical(candidate)
    need(actual == canonical(expected_report()),
         "SEMANTIC_BLOCKER: source-bound witness report disagrees with fresh proof")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    result = expected_report()
    if args.write_report:
        REPORT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
