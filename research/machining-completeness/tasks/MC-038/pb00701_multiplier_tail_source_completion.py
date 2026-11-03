#!/usr/bin/env python3
"""Five frozen multiplier sources: exact factor reconstruction and ramp tails.

The qualified provider supplies only its unbound unit-interval carrier lemma.
This leaf proves every original harmonic identity, multiplier nonvanishing and
original tail independently. It changes no historical owner or programme gate.
"""
from __future__ import annotations

import argparse
import builtins
import copy
from fractions import Fraction as Q
import hashlib
import json
from math import gcd
from pathlib import Path
import re
import sys
import types

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SCHEMA = "radicadsac-mc038-multiplier-tail-source-completion/1.0"
REPORT = HERE / "pb00701-multiplier-tail-source-completion-witness.json"
BASE_MAIN = "4d75edea493a3ee620d3bf64d81fa6e23356800e"
PREREGISTRATION_COMMENT = 6591866803
CARRIER_FILE = "pb00701_component_prefix_composition.py"
CARRIER_BLOB = "530e552bb41c020456fdf0f17506cb18577896f3"
CARRIER_RECEIPT_SHA = "d9c019f6104618d096d9b87d13bbdf700b958cd197546b6f64db904c8129bbf4"
ORDER_GAP = "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"
UNREGISTERED = "NO_REGISTERED_SOURCE_EVENT_OR_ORDER_WITNESS"
TAIL_OWNER = "PB00701_V19_EXACT_MULTI_HARMONIC_MONOTONE_ANCHOR"
MAX_BYTES, MAX_NODES, MAX_DEPTH, MAX_STRING = 1048576, 65536, 32, 8192
MAX_DERIVED_BITS = 4096
RATIONAL = re.compile(r"(-?)(0|[1-9][0-9]{0,77})(?:/([1-9][0-9]{0,77}))?")

PINS = {
    "pb00701-finite-owner-corpus-v54.json": "5841c331579489b25caef38cd412bdbf286f9134",
    "pb00701-finite-owner-inventory-v54.json": "8649c20ab77e199f9c3fa351b8b6742218f27abb",
    "pb00701-finite-owner-coverage-v54.json": "600ba29786f50397f29fd435fc5e2c57076088f9",
    "verify_pb00701_post_v54_frontier.py": "12c6efeb667a954ffc5a7e27849ae815d466580a",
    "pb00701-post-v54-evidence-reconciliation.json": "9f62dd6edc37206317eec054b2969bade02d7728",
    CARRIER_FILE: CARRIER_BLOB,
}
ROOT_PINS = {
    "research/machining-completeness/tasks/MC-002/domain-contract-v1.json":
        "23de82f5240a72509f7afe4acd5948b65bc4ff13",
    "research/machining-completeness/programme-v1.json":
        "dee7045a1790b2870744df8ae7693429bd1d81a6",
    "handoffs/current-authority.json": "fa0233323a0804d8a5d3eb7cd892a274a6173fab",
}
CASE_DATA = [
    ("V13", "PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC",
     "verify_pb00701_v13", "a7131bea021c5c71d0da2682cd6d4c1a982e8c86196c818ad3f69a926afda2e5",
     "094b31ab55141488e39589ab6e0deda02b21066f06ba8568110609a23cd0a003", 3),
    ("V14", "PB00701_V14_EXACT_STRICT_DOMINANCE_MULTITERM_MULTIPLIER",
     "verify_pb00701_v14", "bd10ad1d9503335b2d7f745c09805b82a421b8db7beea67329cf33d0c9d78ff2",
     "1940ec5f6aafb641a25fcda3f8941ff7dd9f2afc2bf13056da6920159c3f0e18", 3),
    ("V15", "PB00701_V15_EXACT_FINITE_STRICT_DOMINANCE_MULTIPLIER",
     "verify_pb00701_v15", "8e41009417dd65f9a47a04b492dd9a91b88a7682f12f45305ce64ac38dffd7b7",
     "3954e79fceefbcd6e4b5932197f0314dbd4b90891b8fbad8410f9572f746725d", 3),
    ("V17", "PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER",
     "verify_pb00701_v17", "e85d997c9f4d828b1b748c964b375c21e4acef1b1e9046e074b1f7e29011d08f",
     "41e86bc30392515873fb55bdd844d154236a81426fd3639c3bd5491dad30f05a", 2),
    ("V18_LAURENT", "PB00701_V18_EXACT_LAURENT_MODULE_FACTOR",
     "verify_pb00701_v14", "ed61c9b827417327b9dda32ec0469ba5f0eab9622fb531d4b1bc959a312aa4a1",
     "7c1304de8afc41ba322fb653f20a1f8b6c3e0ea27af8a7864e44058d6b4d60d1", 3),
]
CASES = {"composite:" + owner + ":tail100": {
    "family": family, "owner": owner, "origin": origin, "source_sha256": source,
    "original_row_sha256": row, "expected_closed_roots": count,
} for family, owner, origin, source, row, count in CASE_DATA}
EVEN_MULTIPLIERS = {
    "V13": {"0": "2", "2": "1"},
    "V14": {"0": "2", "2": "-1/2", "4": "1"},
    "V15": {"0": "4", "2": "1/2", "4": "-1/4", "6": "1"},
    "V18_LAURENT": {"0": "2", "2": "1", "4": "1"},
}


class Refusal(ValueError):
    """Invalid premises or exhausted resources are nontruth, never coverage."""


def need(condition, reason):
    if not condition:
        raise Refusal(reason)


def canonical(value):
    """Bound exact typed JSON before serialization, hashing or source parsing."""
    stack, active, nodes, budget = [(value, 0, False)], set(), 0, 0
    while stack:
        obj, depth, leaving = stack.pop()
        if leaving:
            active.remove(id(obj))
            continue
        nodes += 1
        need(nodes <= MAX_NODES and depth <= MAX_DEPTH, "RESOURCE_REFUSAL: nodes/depth")
        if type(obj) in (dict, list):
            need(id(obj) not in active and len(obj) <= 1024, "RESOURCE_REFUSAL: cycle/container")
            active.add(id(obj))
            budget += 2 + 2 * len(obj)
            stack.append((obj, depth, True))
            if type(obj) is dict:
                for key, child in obj.items():
                    need(type(key) is str and len(key) <= MAX_STRING, "RESOURCE_REFUSAL: key")
                    budget += len(json.dumps(key, ensure_ascii=True))
                    stack.append((child, depth + 1, False))
            else:
                stack.extend((child, depth + 1, False) for child in obj)
        elif type(obj) is str:
            need(len(obj) <= MAX_STRING, "RESOURCE_REFUSAL: string")
            budget += len(json.dumps(obj, ensure_ascii=True))
        elif type(obj) is int:
            need(obj.bit_length() <= 256, "RESOURCE_REFUSAL: integer")
            budget += len(str(obj))
        else:
            need(obj is None or type(obj) is bool, "NONEXACT_JSON_SCALAR")
            budget += 5
        need(budget <= MAX_BYTES, "RESOURCE_REFUSAL: aggregate bytes")
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=True, allow_nan=False).encode("ascii")
    need(len(raw) <= MAX_BYTES, "RESOURCE_REFUSAL: serialized bytes")
    return raw


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def exact(value):
    need(type(value) is str and len(value) <= 160, "INVALID_OR_OVERSIZED_RATIONAL")
    match = RATIONAL.fullmatch(value)
    need(match is not None, "NONCANONICAL_ASCII_RATIONAL")
    sign, numerator_text, denominator_text = match.groups()
    need(not (sign and numerator_text == "0"), "NONCANONICAL_NEGATIVE_ZERO")
    numerator = int(numerator_text) * (-1 if sign else 1)
    denominator = int(denominator_text) if denominator_text is not None else 1
    need(max(numerator.bit_length(), denominator.bit_length()) <= 256, "RESOURCE_REFUSAL: rational bits")
    need(denominator_text is None or denominator > 1, "NONCANONICAL_DENOMINATOR_ONE")
    need(gcd(abs(numerator), denominator) == 1, "NONCANONICAL_UNREDUCED_RATIONAL")
    return Q(numerator, denominator)


def bounded_file(path):
    try:
        with Path(path).open("rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
    except OSError as exc:
        raise Refusal("DEPENDENCY_UNAVAILABLE: " + str(path)) from exc
    need(len(raw) <= MAX_BYTES, "RESOURCE_REFUSAL: file bytes")
    return raw


def git_blob(path):
    raw = bounded_file(path)
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def pinned_bytes(path, expected):
    raw = bounded_file(path)
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    need(actual == expected, "PINNED_SOURCE_DRIFT: " + str(path))
    return raw


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def json_integer(token):
    need(len(token.lstrip("-")) <= 78, "RESOURCE_REFUSAL: JSON integer token")
    value = int(token)
    need(value.bit_length() <= 256, "RESOURCE_REFUSAL: JSON integer bits")
    return value


def nonexact_json(_):
    raise Refusal("NONEXACT_JSON_SCALAR")


def decode_json(raw):
    need(type(raw) is bytes and len(raw) <= MAX_BYTES, "RESOURCE_REFUSAL: JSON input bytes")
    try:
        value = json.loads(raw, object_pairs_hook=unique_pairs, parse_int=json_integer,
                           parse_float=nonexact_json, parse_constant=nonexact_json)
    except (RecursionError, UnicodeError, json.JSONDecodeError) as exc:
        raise Refusal("INVALID_OR_RESOURCE_JSON") from exc
    canonical(value)
    return value


def pinned_json(path, expected):
    return decode_json(pinned_bytes(path, expected))


def read_report(path=REPORT):
    return decode_json(bounded_file(path))


def pinned_module(path, expected):
    """The only consumed modules have no project imports in their pure path."""
    raw = pinned_bytes(path, expected)
    module = types.ModuleType("multiplier_private_" + Path(path).stem)
    module.__file__ = str(path)
    local_sys = types.SimpleNamespace(**vars(sys))
    local_sys.path = list(sys.path)

    def local_import(name, globals=None, locals=None, fromlist=(), level=0):
        need(level == 0, "UNREVIEWED_RELATIVE_IMPORT")
        need(name in {"__future__", "argparse", "builtins", "collections", "copy", "fractions",
                      "hashlib", "json", "math", "pathlib", "re", "sys", "types"},
             "UNREVIEWED_DEPENDENCY_IMPORT")
        return local_sys if name == "sys" else builtins.__import__(
            name, globals, locals, fromlist, level)

    module.__dict__["__builtins__"] = dict(vars(builtins), __import__=local_import)
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


def load_carrier():
    provider = pinned_module(HERE / CARRIER_FILE, CARRIER_BLOB)
    # No provider source wrapper, factor checker, tail producer or saved report
    # is used. This pure lemma binds no original source until our reconstruction.
    receipt = provider.carrier_prefix_proof()
    need(digest(receipt) == CARRIER_RECEIPT_SHA, "QUALIFIED_CARRIER_CONTRACT_DRIFT")
    return receipt


def qvector(values, maximum=16):
    need(type(values) in (list, tuple) and 1 <= len(values) <= maximum,
         "RESOURCE_REFUSAL: exact coefficient vector")
    for value in values:
        need(type(value) in (int, Q), "NONEXACT_DERIVED_COEFFICIENT")
        if type(value) is int:
            need(value.bit_length() <= MAX_DERIVED_BITS, "RESOURCE_REFUSAL: derived bits")
        else:
            need(max(value.numerator.bit_length(), value.denominator.bit_length()) <=
                 MAX_DERIVED_BITS, "RESOURCE_REFUSAL: derived bits")
    return [Q(value) for value in values]


def trim(values):
    out = qvector(values)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def add(a, b):
    a, b = qvector(a), qvector(b)
    out = [Q(0)] * max(len(a), len(b))
    for i, value in enumerate(a):
        out[i] += value
    for i, value in enumerate(b):
        out[i] += value
    return trim(out)


def scale(a, value):
    value = qvector([value])[0]
    return trim([x * value for x in qvector(a)])


def multiply(a, b):
    a, b = qvector(a), qvector(b)
    need(len(a) + len(b) - 1 <= 16, "RESOURCE_REFUSAL: product degree")
    out = [Q(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return trim(out)


def chebyshev():
    first, second = [[Q(1)], [Q(0), Q(1)]], [[Q(1)], [Q(0), Q(2)]]
    for _ in range(2, 8):
        first.append(add(multiply([0, 2], first[-1]), scale(first[-2], -1)))
        second.append(add(multiply([0, 2], second[-1]), scale(second[-2], -1)))
    return first, second


def two_span_powers(spline):
    need(type(spline) is dict and set(spline) == {"degree", "knots", "controls"},
         "INVALID_SPLINE_FIELDS")
    degree = spline["degree"]
    need(type(degree) is int and degree in (0, 1), "UNSUPPORTED_SPLINE_DEGREE")
    need(spline["knots"] == [x for x in ("0", "1", "2") for _ in range(degree + 1)],
         "ORIGINAL_CLAMPED_KNOTS_REQUIRED")
    need(type(spline["controls"]) is list and len(spline["controls"]) == 2 * (degree + 1),
         "SPLINE_CONTROL_COUNT")
    controls = [exact(x) for x in spline["controls"]]
    if degree == 0:
        return ((controls[0], Q(0)), (controls[1], Q(0)))
    return ((controls[0], controls[1] - controls[0]),
            (2 * controls[2] - controls[3], controls[3] - controls[2]))


def parse_source(spec):
    canonical(spec)
    need(type(spec) is dict and set(spec) == {
        "grammar", "source_parameter_id", "parameter_lo", "parameter_hi",
        "phase_turn_offset", "phase_turn_rate", "cos_splines", "sin_splines"},
        "UNREVIEWED_SOURCE_FIELDS")
    need(spec["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE" and
         type(spec["source_parameter_id"]) is str and
         0 < len(spec["source_parameter_id"]) <= 128, "SOURCE_GRAMMAR_OR_PARAMETER")
    need(tuple(exact(spec[k]) for k in ("parameter_lo", "parameter_hi",
                                      "phase_turn_offset", "phase_turn_rate")) ==
         (Q(0), Q(2), Q(0), Q(1, 4)), "ORIGINAL_INTERVAL_OR_PHASE")
    pieces, continuity = {}, []
    for channel, allowed in (("cos_splines", {"0", "1", "3", "5", "7"}),
                             ("sin_splines", {"1", "3", "5", "7"})):
        entries = spec[channel]
        need(type(entries) is dict and bool(entries) and set(entries) <= allowed,
             "UNACCOUNTED_SOURCE_HARMONIC")
        pieces[channel] = {int(h): two_span_powers(s) for h, s in entries.items()}
        for h, (left, right) in sorted(pieces[channel].items()):
            need(sum(left) == sum(right), "ORIGINAL_CHANNEL_KNOT_DISCONTINUITY")
            continuity.append({"channel": channel, "harmonic": h,
                               "left_value": str(sum(left)), "right_value": str(sum(right))})
    need(0 in pieces["cos_splines"], "ORIGINAL_ZERO_HARMONIC_MISSING")
    return pieces, continuity


def cardinal_value(pieces, source_piece, at):
    need(type(source_piece) is int and source_piece in (0, 1), "INVALID_SOURCE_PIECE")
    at = qvector([at])[0]
    need(at in (0, 1, 2) and source_piece <= at <= source_piece + 1,
         "UNPROVED_CARDINAL_POINT")
    values = ((Q(1), Q(0)), (Q(0), Q(1)), (Q(-1), Q(0)), (Q(0), Q(-1)))
    result = Q(0)
    for channel, trig_index in (("cos_splines", 0), ("sin_splines", 1)):
        for harmonic, spans in pieces[channel].items():
            constant, slope = spans[source_piece]
            trig = values[int(harmonic * at) % 4][trig_index]
            result += (constant + slope * at) * trig
    return qvector([result])[0]


def strict_sign(value):
    need(type(value) in (int, Q) and value != 0, "EXACT_ZERO_HAS_NO_STRICT_SIGN")
    return 1 if value > 0 else -1


def even_multiplier(series, *, square=False):
    canonical(series)
    need(type(series) is dict and "0" in series and set(series) <= {"0", "2", "4", "6"}
         and type(square) is bool, "INVALID_EVEN_MULTIPLIER")
    coefficients = {int(h): exact(v) for h, v in series.items()}
    t, _ = chebyshev()
    poly = [Q(0)]
    for harmonic, coefficient in coefficients.items():
        poly = add(poly, scale(t[harmonic], coefficient))
    if square:
        need(set(coefficients) == {0, 2, 4}, "UNSUPPORTED_SQUARE_MULTIPLIER")
        quadratic, linear, constant = (2 * coefficients[4], coefficients[2],
                                       coefficients[0] - coefficients[4])
        need(quadratic > 0, "SQUARE_LEADING_COEFFICIENT_NOT_POSITIVE")
        shift = linear / (2 * quadratic)
        margin = constant - linear * linear / (4 * quadratic)
        need(margin > 0, "MULTIPLIER_MAY_VANISH")
        # z=cos(2theta); cos(4theta)=2z²-1. Recheck the exact square identity.
        need(add(scale(multiply([shift, 1], [shift, 1]), quadratic), [margin]) ==
             [constant, linear, quadratic], "MULTIPLIER_SQUARE_IDENTITY")
        proof = {"method": "EXACT_POSITIVE_QUADRATIC_SQUARE",
                 "variable": "z=cos(2*theta)", "quadratic": str(quadratic),
                 "shift": str(shift), "positive_remainder": str(margin)}
    else:
        margin = coefficients[0] - sum(abs(v) for h, v in coefficients.items() if h)
        need(margin > 0, "MULTIPLIER_MAY_VANISH")
        proof = {"method": "STRICT_COSINE_L1_DOMINANCE",
                 "constant": str(coefficients[0]),
                 "residual_absolute_sum": str(sum(abs(v) for h, v in coefficients.items() if h))}
    return {"kind": "EVEN_COSINE", "cosine_series": dict(series), "use_square": square,
            "polynomial_in_cos_theta": [str(x) for x in poly], "sign": 1,
            "strict_nonzero_margin": str(margin), "nonvanishing_proof": proof}


def negative_sine_multiplier(constant="-2", amplitude="1"):
    c, d = exact(constant), exact(amplitude)
    upper = c + abs(d)
    need(upper < 0, "MULTIPLIER_MAY_VANISH")
    return {"kind": "CONSTANT_PLUS_SINE_2", "constant": constant, "amplitude": amplitude,
            "sign": -1, "strict_nonzero_margin": str(-upper),
            "nonvanishing_proof": {"method": "STRICT_NEGATIVE_SINE_ENVELOPE",
                                  "global_range": [str(c - abs(d)), str(upper)]}}


def multiplier_for(family):
    need(type(family) is str and family in set(EVEN_MULTIPLIERS) | {"V17"},
         "UNKNOWN_MULTIPLIER_FAMILY")
    return (negative_sine_multiplier() if family == "V17" else
            even_multiplier(EVEN_MULTIPLIERS[family], square=family == "V18_LAURENT"))


def factor_identity(spec, multiplier):
    """Conditional exact identity, independently checking all original channels."""
    canonical(multiplier)
    need(type(multiplier) is dict, "INVALID_MULTIPLIER_RECORD")
    if multiplier.get("kind") == "EVEN_COSINE":
        checked = even_multiplier(multiplier.get("cosine_series"),
                                  square=multiplier.get("use_square"))
        largest = max(int(h) for h in checked["cosine_series"])
    else:
        need(multiplier.get("kind") == "CONSTANT_PLUS_SINE_2", "UNKNOWN_MULTIPLIER_KIND")
        checked = negative_sine_multiplier(multiplier.get("constant"), multiplier.get("amplitude"))
        largest = 2
    need(canonical(multiplier) == canonical(checked), "FORGED_MULTIPLIER_BOUND")
    pieces, _ = parse_source(spec)
    harmonics = set(range(1, largest + 2, 2))
    need(set(pieces["cos_splines"]) == harmonics | {0} and
         set(pieces["sin_splines"]) == harmonics, "FACTOR_HARMONICS_MISSING_OR_ADDED")
    need(pieces["cos_splines"][0][0] == (Q(0), Q(0)), "NONZERO_PREFIX_BIAS")
    t, u = chebyshev()
    a, b = (Q(-1, 3), Q(1)), (Q(2, 3), Q(-1))
    result = []
    for degree in (0, 1):
        actual_cos, actual_sin = [Q(0)], [Q(0)]
        for harmonic in sorted(harmonics):
            actual_cos = add(actual_cos, scale(t[harmonic],
                             pieces["cos_splines"][harmonic][0][degree]))
            actual_sin = add(actual_sin, scale(u[harmonic - 1],
                             pieces["sin_splines"][harmonic][0][degree]))
        if checked["kind"] == "EVEN_COSINE":
            poly = [exact(x) for x in checked["polynomial_in_cos_theta"]]
            expected_cos, expected_sin = scale(multiply([0, 1], poly), a[degree]), scale(poly, b[degree])
        else:
            c, d = exact(checked["constant"]), exact(checked["amplitude"])
            expected_cos = [Q(0), c*a[degree] + 2*d*b[degree], Q(0), -2*d*b[degree]]
            expected_sin = [c*b[degree], Q(0), 2*d*a[degree]]
        need(actual_cos == trim(expected_cos) and actual_sin == trim(expected_sin),
             "ORIGINAL_HARMONIC_FACTOR_IDENTITY_FAILED")
        result.append({"source_t_power": degree,
                       "cosine_polynomial_in_cos_theta": [str(x) for x in actual_cos],
                       "sine_coefficient_polynomial_in_cos_theta": [str(x) for x in actual_sin]})
    return {"identity": "F(t)=M(theta(t))*R(t)", "original_interval": ["0", "1"],
            "all_original_harmonics_reconstructed": True, "multiplier": checked,
            "coefficient_identities": result,
            "simple_root_transfer": "(M*R)'=M*R' at R=0, with M nonzero"}


def _prefix_proof(spec, family, carrier):
    need(digest(carrier) == CARRIER_RECEIPT_SHA, "QUALIFIED_CARRIER_CONTRACT_DRIFT")
    identity = factor_identity(spec, multiplier_for(family))
    pieces, _ = parse_source(spec)
    multiplier_sign = identity["multiplier"]["sign"]
    signs = [multiplier_sign * x for x in (-1, 1, -1)]
    endpoints = [cardinal_value(pieces, 0, Q(x)) for x in (0, 1)]
    need([strict_sign(x) for x in endpoints] == [signs[0], signs[-1]], "PREFIX_ENDPOINT_SIGN_MISMATCH")
    return {"source_sha256": digest(spec), "source_interval": ["0", "1"],
            "source_parameter_id": spec["source_parameter_id"],
            "phase_turn_law": {"offset": "0", "rate": "1/4"},
            "carrier_receipt_sha256": CARRIER_RECEIPT_SHA,
            "factor_reconstruction": identity, "closed_distinct_root_count": 2,
            "root_brackets": copy.deepcopy(carrier["root_brackets"]),
            "simple_root_derivative_signs": [multiplier_sign, -multiplier_sign],
            "maximal_sign_cells": signs, "endpoint_values": [str(x) for x in endpoints],
            "proof_cuts": list(carrier["proof_cuts"]), "proof_cuts_are_physical_events": False,
            "complete_for_original_first_closed_span": True}


def prove_prefix(spec, family):
    canonical(spec)
    return _prefix_proof(spec, family, load_carrier())


def prove_tail(spec, bracket_right="11/10"):
    pieces, _ = parse_source(spec)
    cut = exact(bracket_right)
    need(1 < cut < 2, "TAIL_BRACKET_OUTSIDE_ORIGINAL_SPAN")
    cosine, sine = {}, {}
    for channel, selected in (("cos_splines", cosine), ("sin_splines", sine)):
        for harmonic, spans in pieces[channel].items():
            if harmonic == 0:
                continue
            constant, slope = spans[1]
            need(slope == 0, "TAIL_NONCONSTANT_HARMONIC_AMPLITUDE")
            selected[harmonic] = constant
    bias, slope = pieces["cos_splines"][0][1]
    norm = sum(abs(v) for v in cosine.values()) + sum(abs(v) for v in sine.values())
    weighted = sum(h*abs(v) for h, v in cosine.items()) + sum(h*abs(v) for h, v in sine.items())
    derivative_lower = slope - Q(11, 7) * weighted
    need(derivative_lower > 0, "TAIL_STRICT_DERIVATIVE_NOT_PROVED")
    knot, end = cardinal_value(pieces, 1, Q(1)), cardinal_value(pieces, 1, Q(2))
    need(knot != 0, "EXACT_KNOT_ZERO_OUTSIDE_THIS_LEAF")
    positive_bound = bias + slope * cut - norm
    if knot < 0:
        need(positive_bound > 0, "TAIL_STRICT_BRACKET_SIGN_NOT_PROVED")
        brackets, signs = [["1", bracket_right]], [-1, 1]
    else:
        brackets, signs = [], [1]
    need(end > 0, "TAIL_EXTERIOR_SIGN_CONTRADICTION")
    return {"source_sha256": digest(spec), "source_interval": ["1", "2"],
            "source_parameter_id": spec["source_parameter_id"],
            "phase_turn_law": {"offset": "0", "rate": "1/4"},
            "cosine_amplitudes": {str(h): str(v) for h, v in sorted(cosine.items())},
            "sine_amplitudes": {str(h): str(v) for h, v in sorted(sine.items())},
            "zero_harmonic_global_power_coefficients": [str(bias), str(slope)],
            "amplitude_absolute_sum": str(norm), "harmonic_weighted_absolute_sum": str(weighted),
            "phase_derivative_strict_upper_bound": "11/7",
            "phase_derivative_bound_basis": "theta'=pi/2, pi<22/7",
            "strict_derivative_lower_bound": str(derivative_lower),
            "bound_at_rational_proof_cut": {"position": bracket_right, "lower_bound": str(positive_bound),
                                          "is_physical_event": False},
            "endpoint_values": [str(knot), str(end)],
            "closed_distinct_root_count": len(brackets), "root_brackets": brackets,
            "simple_root_derivative_signs": [1] * len(brackets), "maximal_sign_cells": signs,
            "complete_for_original_second_closed_span": True}


def _compose(spec, prefix, tail, continuity):
    """Compose only fresh source-bound views produced by the two proofs above."""
    canonical(prefix)
    canonical(tail)
    source_sha = digest(spec)
    for view, interval in ((prefix, ["0", "1"]), (tail, ["1", "2"])):
        need(view["source_sha256"] == source_sha and view["source_interval"] == interval and
             view["source_parameter_id"] == spec["source_parameter_id"] and
             view["phase_turn_law"] == {"offset": "0", "rate": "1/4"},
             "SOURCE_VIEW_BINDING_MISMATCH")
        count = view["closed_distinct_root_count"]
        need(type(count) is int and count == len(view["root_brackets"]) ==
             len(view["simple_root_derivative_signs"]) and
             len(view["maximal_sign_cells"]) == count + 1, "INCOMPLETE_EVENT_OR_SIGN_VIEW")
        need(all(type(x) is int and x in (-1, 1) for x in
                 view["simple_root_derivative_signs"] + view["maximal_sign_cells"]),
             "NONEXACT_PHYSICAL_SIGN")
    need(prefix["complete_for_original_first_closed_span"] is True and
         tail["complete_for_original_second_closed_span"] is True and
         prefix["closed_distinct_root_count"] == 2 and tail["closed_distinct_root_count"] in (0, 1),
         "INCOMPLETE_ORIGINAL_SOURCE_PROOF")
    pieces, actual_continuity = parse_source(spec)
    need(canonical(continuity) == canonical(actual_continuity), "SOURCE_KNOT_CONTINUITY_VIEW_MISMATCH")
    knot = cardinal_value(pieces, 0, Q(1))
    need(knot == cardinal_value(pieces, 1, Q(1)) and knot != 0 and
         prefix["endpoint_values"][1] == tail["endpoint_values"][0] == str(knot) and
         prefix["maximal_sign_cells"][-1] == tail["maximal_sign_cells"][0] == strict_sign(knot),
         "SOURCE_KNOT_VALUE_OR_SIGN_MISMATCH")
    events, signs = [], list(prefix["maximal_sign_cells"])
    signs.extend(tail["maximal_sign_cells"][1:])
    for index, view in enumerate((prefix, tail)):
        for j, bracket in enumerate(view["root_brackets"]):
            lo, hi = map(exact, bracket)
            need(Q(index) <= lo < hi <= Q(index + 1), "ROOT_BRACKET_OUTSIDE_ORIGINAL_PIECE")
            if events:
                need(exact(events[-1]["coordinate"]["strict_bracket"][1]) < lo,
                     "ORIGINAL_ROOT_ORDER_OVERLAP")
            events.append({"root_ref": "ROOT_" + str(len(events) + 1),
                           "coordinate": {"kind": "UNIQUE_IMPLICIT_ZERO_OF_PINNED_ORIGINAL_SOURCE",
                                          "source_sha256": source_sha,
                                          "source_parameter_id": spec["source_parameter_id"],
                                          "source_piece_index": index,
                                          "strict_bracket": list(bracket)},
                           "smooth_physical_multiplicity": 1,
                           "derivative_sign_at_root": view["simple_root_derivative_signs"][j],
                           "left_sign": view["maximal_sign_cells"][j],
                           "right_sign": view["maximal_sign_cells"][j + 1]})
    need(len(signs) == len(events) + 1, "WHOLE_SOURCE_SIGN_COUNT")
    for i, event in enumerate(events):
        need(event["left_sign"] == signs[i] == -signs[i + 1] and
             event["right_sign"] == signs[i + 1] and
             event["derivative_sign_at_root"] == signs[i + 1], "WHOLE_SOURCE_SIGN_OR_SIMPLE_ORDER")
    boundaries = ["ORIGINAL_SOURCE_START"] + [e["root_ref"] for e in events] + ["ORIGINAL_SOURCE_END"]
    endpoints = [cardinal_value(pieces, 0, Q(0)), cardinal_value(pieces, 1, Q(2))]
    need([strict_sign(x) for x in endpoints] == [signs[0], signs[-1]], "EXTERIOR_SIGN_MISMATCH")
    return {"source_interval": ["0", "2"], "zero_set_kind": "FINITE",
            "closed_distinct_root_count": len(events), "events": events,
            "maximal_open_sign_cells": [{"left": boundaries[i], "right": boundaries[i + 1],
                                        "sign": value} for i, value in enumerate(signs)],
            "original_source_knot": {"position": "1", "value": str(knot),
                                    "channel_continuous": True, "left_sign": strict_sign(knot),
                                    "right_sign": strict_sign(knot), "is_physical_event": False},
            "exterior_endpoints": [{"position": str(i), "value": str(v), "sign": strict_sign(v),
                                   "is_physical_zero": False} for i, v in zip((0, 2), endpoints)],
            "complete_for_original_closed_source": True, "continuum_zero_component": False,
            "proof_cuts_and_bracket_endpoints_are_not_root_coordinates": True}


def check_original(row):
    canonical(row)
    need(type(row) is dict and set(row) == {"id", "origin", "kind", "spec", "expected"},
         "UNREVIEWED_ORIGINAL_ROW_FIELDS")
    need(type(row["id"]) is str and row["id"] in CASES, "SOURCE_OUTSIDE_SELECTED_FINITE_SET")
    metadata = CASES[row["id"]]
    need(digest(row["spec"]) == metadata["source_sha256"] and
         digest(row) == metadata["original_row_sha256"], "ORIGINAL_SOURCE_OR_WHOLE_ROW_DRIFT")
    need(row["kind"] == "COMPOSITE_TAIL" and row["origin"] == metadata["origin"],
         "ORIGINAL_PROVENANCE_DRIFT")
    expected = {"id": row["id"], "observed": {"status": "CERTIFIED", "spans": [
        [metadata["owner"], "CERTIFIED", None], [TAIL_OWNER, "CERTIFIED", None]]},
        "v54_disposition": ORDER_GAP}
    need(canonical(row["expected"]) == canonical(expected), "HISTORICAL_OWNER_OR_DISPOSITION_DRIFT")
    need(row["spec"]["source_parameter_id"] == "source-time-t", "ORIGINAL_PARAMETER_DRIFT")
    return metadata


def original_rows():
    corpus, inventory, coverage = [pinned_json(HERE / name, PINS[name]) for name in list(PINS)[:3]]
    auditor_name = "verify_pb00701_post_v54_frontier.py"
    auditor = pinned_module(HERE / auditor_name, PINS[auditor_name])
    census = auditor.audit(corpus, inventory, coverage)
    need(census["cases"] == 121 and census["v54_dispositions"]["BLOCKED"] == 20 and
         census["v54_dispositions"][ORDER_GAP] == 30, "HISTORICAL_121_20_30_DRIFT")
    prior_name = "pb00701-post-v54-evidence-reconciliation.json"
    prior = pinned_json(HERE / prior_name, PINS[prior_name])
    unregistered = {r["case_id"] for r in prior["source_cases"] if r["registered_evidence_level"] == UNREGISTERED}
    need(len(unregistered) == 8 and set(CASES) <= unregistered, "PRIOR_UNREGISTERED_COHORT_DRIFT")
    indexed = {row["id"]: row for row in corpus["cases"]}
    need(len(indexed) == len(corpus["cases"]) == 121 and set(CASES) <= set(indexed),
         "ORIGINAL_SOURCE_DENOMINATOR_OR_IDS")
    domain, programme, authority = [pinned_json(ROOT / name, expected)
                                   for name, expected in ROOT_PINS.items()]
    need(len(domain["coverage_rule"]["required_operation_ids"]) == 26, "DOMAIN_DENOMINATOR_DRIFT")
    need(programme["capability_status"] == authority["capability_status"] == "NOT_ESTABLISHED" and
         programme["production_authorized"] is False and authority["production_authorized"] is False and
         {g["id"]: g["state"] for g in programme["gates"]}["MC-B"] == "NOT_ESTABLISHED",
         "PROGRAMME_AUTHORITY_PROMOTION")
    result = {cid: indexed[cid] for cid in CASES}
    for row in result.values():
        check_original(row)
    return result


def _source_proof(row, carrier):
    metadata = check_original(row)
    spec = row["spec"]
    pieces, continuity = parse_source(spec)
    prefix, tail = _prefix_proof(spec, metadata["family"], carrier), prove_tail(spec)
    physical = _compose(spec, prefix, tail, continuity)
    need(physical["closed_distinct_root_count"] == metadata["expected_closed_roots"],
         "FROZEN_SOURCE_RESULT_DRIFT")
    return {"case_id": row["id"], "family": metadata["family"],
            "original_source_sha256": digest(spec), "original_row_sha256": digest(row),
            "original_source": copy.deepcopy(spec), "historical_observation": copy.deepcopy(row["expected"]),
            "source_parameter_id": spec["source_parameter_id"],
            "phase_turn_law": {"offset": "0", "rate": "1/4"}, "source_interval": ["0", "2"],
            "original_source_piece_edges": ["0", "1", "2"],
            "original_global_power_coefficients": {
                channel: {str(h): [[str(v) for v in span] for span in spans]
                          for h, spans in sorted(entries.items())}
                for channel, entries in pieces.items()},
            "original_channel_knot_continuity": continuity,
            "prefix_proof": prefix, "tail_proof": tail, "physical_event_proof": physical,
            "historical_disposition_changed": False}


def source_proof(row):
    check_original(row)
    return _source_proof(row, load_carrier())


def expected_report():
    originals, carrier = original_rows(), load_carrier()
    proofs = [_source_proof(originals[cid], carrier) for cid in sorted(CASES)]
    counts = {p["case_id"]: p["physical_event_proof"]["closed_distinct_root_count"] for p in proofs}
    need(list(counts.values()) == [3, 3, 3, 2, 3], "FIVE_SOURCE_RESULT_DRIFT")
    report = {"schema": SCHEMA, "task": "MC-038 / PB-007-01", "evidence_class": "DETERMINISTIC_MODEL",
              "source_baseline_main": BASE_MAIN, "preregistration_issue_100_comment": PREREGISTRATION_COMMENT,
              "dependencies": {"local_git_blobs": dict(PINS), "root_git_blobs": dict(ROOT_PINS)},
              "qualified_carrier": {"provider_code": CARRIER_FILE, "provider_git_blob": CARRIER_BLOB,
                                    "qualified_main": BASE_MAIN, "consumed_entrypoint": "carrier_prefix_proof",
                                    "receipt_sha256": CARRIER_RECEIPT_SHA, "receipt": carrier,
                                    "provider_whole_source_or_tail_producers_consumed": False,
                                    "original_source_binding_derived_in_this_leaf": True},
              "source_cases": proofs,
              "summary": {"complete_original_sources": 5, "finite_simple_roots": sum(counts.values()),
                          "by_case_closed_root_count": counts, "continuum_sources": 0,
                          "nonzero_original_knots": 5, "nonzero_exterior_endpoints": 10},
              "historical_v54": {"original_source_cases": 121, "route_refusals": 20,
                                "missing_ordered_span_premises": 30, "dispositions_changed": False},
              "resources": {"maximum_spline_degree": 1, "maximum_original_harmonic": 7,
                            "input_rational_bit_limit": 256, "derived_rational_bit_limit": MAX_DERIVED_BITS,
                            "byte_limit": MAX_BYTES, "native_campaign_run": False, "paid_campaign_run": False},
              "scope": {"complete_selected_original_source_mathematics_only": True,
                        "historical_owner_routes_repaired": False, "universal_proof_consumer": False,
                        "all_post_v54_sources_reconciled": False},
              "gates": {"PB-007-01": "OPEN", "PB-007-02": "OPEN_DEPENDENT",
                        "PB-007-03": "OPEN_PROPAGATED", "PB-007-04": "OPEN_PROPAGATED",
                        "MC-B": "NOT_ESTABLISHED", "MC-1": "NOT_ESTABLISHED",
                        "required_machining_operations": 26, "production_authorized": False,
                        "native_geometry_or_STEP_qualified": False}}
    canonical(report)
    return report


def validate_report(candidate):
    supplied = canonical(candidate)
    need(supplied == canonical(expected_report()), "REPORT_DISAGREES_WITH_FRESH_SOURCE_PROOF")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    if not args.write_report:
        parser.error("use --write-report or the dedicated contract verifier")
    report = expected_report()
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
