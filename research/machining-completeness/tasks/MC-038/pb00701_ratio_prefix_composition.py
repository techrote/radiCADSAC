#!/usr/bin/env python3
"""Four original-source completions from conditional tangent/cotangent charts.

Chart lemmas reconstruct strict derivative and sign premises from original
Bernstein controls. Frozen wrappers separately bind complete original records
and freshly replay three historical tail contracts. No historical route or
programme gate is changed by these finite source-specific witnesses.
"""
from __future__ import annotations

import argparse
import builtins
import copy
from fractions import Fraction as Q
import hashlib
import json
from math import comb, gcd
from pathlib import Path
import re
import sys
import types

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SCHEMA = "radicadsac-mc038-ratio-prefix-composition/1.0"
REPORT = HERE / "pb00701-ratio-prefix-composition.json"
BASE_MAIN = "e8108b98af35c4c4fd72a0cbf224a4b1aea0740c"
RECORDED_UTC = "2026-11-03T00:15:07Z"
PREREGISTRATION_COMMENTS = [6591720927, 6591724660]
MAX_BYTES = 1048576
MAX_NODES = 65536
MAX_DEPTH = 32
MAX_STRING = 8192
MAX_DEGREE = 6
RATIONAL = re.compile(r"(-?)(0|[1-9][0-9]{0,77})(?:/([1-9][0-9]{0,77}))?")
V10 = "PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO"
V11 = "PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO"
TAIL_OWNER = "PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF"
TAIL_REASON = "CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED"
PINS = {
    "pb00701-finite-owner-corpus-v54.json": "5841c331579489b25caef38cd412bdbf286f9134",
    "pb00701-finite-owner-inventory-v54.json": "8649c20ab77e199f9c3fa351b8b6742218f27abb",
    "pb00701-finite-owner-coverage-v54.json": "600ba29786f50397f29fd435fc5e2c57076088f9",
    "verify_pb00701_post_v54_frontier.py": "12c6efeb667a954ffc5a7e27849ae815d466580a",
    "verify_pb00701_v43_refusal_cone.py": "2a8079ee2cf012bc2a12794c4c5ff19ebd760007",
}
ROOT_PINS = {
    "research/machining-completeness/tasks/MC-002/domain-contract-v1.json":
        "23de82f5240a72509f7afe4acd5948b65bc4ff13",
    "research/machining-completeness/programme-v1.json":
        "dee7045a1790b2870744df8ae7693429bd1d81a6",
    "handoffs/current-authority.json": "fa0233323a0804d8a5d3eb7cd892a274a6173fab",
}
PRODUCERS = {
    "V10_ZERO": ("verify_pb00701_v43_v10_tail0_crossings.py", "5bf6f85f1432b513ba89d17f5e4da17d1bce212d"),
    "V10_RAMP": ("verify_pb00701_v43_v10_tail_crossing.py", "ada50468fe840625bd652c5a0042e0e3d75607d6"),
    "V11_PAIR": ("verify_pb00701_v43_v11_tail_contrast.py", "a978284ce2672ce05d0ae45a9e2a9043c227a4f2"),
}
CASE_DATA = [
    (V10, 0, "verify_pb00701_v10", "V10_ZERO", 8,
     "57d3c14096ccedfb7faea5023f5a09bada2ca274748f2207c36d77bbc790927c",
     "c5ba85453dc65e0d18675353986394ae5b34af6219a741ce14af0c332ffc47cd",
     "5fd2d417ce4f8313bbb6214622b14bd6d81a24f1d2be8f1b1aee167174f9263f"),
    (V10, 100, "verify_pb00701_v10", "V10_RAMP", 5,
     "21a0dde2ee6783f4465ab0c23dbef08fc400a4c8f2169cc5b851a3b0c3f5e23b",
     "cdd45c443caa2e240e4b87736b227070371f7d4a94ac69c98987a3bc9d293632",
     "d7fe2699b430979f84c3f0c9f7b85b1d77087759b5cd5e1e7b3f0b00ae7ff752"),
    (V11, 0, "verify_pb00701_v11", "V11_PAIR", 8,
     "1535f364cd4d3c1a3bf34f57f394ad70a17ad1327880a0a47f25f3ecff5c7560",
     "cf16b962fba955f1bf66b2412beb9c15e10aa263f3197172cc2961737bd6b804",
     "f94ad20bdd7c383255f4bee38294cd67b5ba0f1aac504026f529d62050f9a457"),
    (V11, 100, "verify_pb00701_v11", "V11_PAIR", 4,
     "f70a884ea00042d46f517577ab598d8c85152ad511d48ea0bb8b2e6d7c55d0d5",
     "dd2744103931e0c754809f3db0376aa7a5aa986af2644fc7ae4ba7dd9348fce1",
     "cccc4c6968d4ba40f0f702ac7e97b8994ed7f7815a810a365458a89d1cb669f6"),
]
CASES = {"composite:" + owner + ":tail" + str(tail): {
    "owner": owner, "tail": tail, "origin": origin, "producer": producer,
    "closed_root_count": count, "source_sha256": source, "row_sha256": row,
    "tail_replay_sha256": receipt}
    for owner, tail, origin, producer, count, source, row, receipt in CASE_DATA}


class Refusal(ValueError):
    """Invalid or resource-refused evidence never becomes a mathematical fact."""


def need(condition, reason):
    if not condition:
        raise Refusal(reason)


def bounded_bytes(value):
    """Bound exact JSON before serialization, hashing or historical parsing."""
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
    data = json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")
    need(len(data) <= MAX_BYTES, "RESOURCE_REFUSAL: serialized bytes")
    return data


def digest(value):
    return hashlib.sha256(bounded_bytes(value)).hexdigest()


def exact(value):
    need(type(value) is str and len(value) <= 160, "NONCANONICAL_OR_OVERSIZED_RATIONAL")
    token = RATIONAL.fullmatch(value)
    need(token is not None, "NONCANONICAL_ASCII_RATIONAL")
    sign, numerator_text, denominator_text = token.groups()
    need(not (sign and numerator_text == "0"), "NONCANONICAL_NEGATIVE_ZERO")
    numerator = int(numerator_text) * (-1 if sign else 1)
    denominator = int(denominator_text) if denominator_text is not None else 1
    need(max(numerator.bit_length(), denominator.bit_length()) <= 256, "RESOURCE_REFUSAL: rational bits")
    need(denominator_text is None or denominator > 1, "NONCANONICAL_DENOMINATOR_ONE")
    need(gcd(abs(numerator), denominator) == 1, "NONCANONICAL_UNREDUCED_RATIONAL")
    return Q(numerator, denominator)


def _file_bytes(path):
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    need(len(raw) <= MAX_BYTES, "RESOURCE_REFUSAL: file bytes")
    return raw


def git_blob(path):
    raw = _file_bytes(path)
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def pin(path, expected):
    _pinned_bytes(path, expected)


def _pinned_bytes(path, expected):
    raw = _file_bytes(path)
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    need(actual == expected, "PINNED_SOURCE_DRIFT: " + str(path))
    return raw


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def _json_integer(token):
    need(len(token) <= 79, "RESOURCE_REFUSAL: JSON integer token")
    value = int(token)
    need(value.bit_length() <= 256, "RESOURCE_REFUSAL: JSON integer bits")
    return value


def _nonexact_json(_):
    raise Refusal("NONEXACT_JSON_SCALAR")


def _decode_json(raw):
    need(type(raw) is bytes and len(raw) <= MAX_BYTES, "RESOURCE_REFUSAL: JSON input bytes")
    try:
        value = json.loads(raw, object_pairs_hook=_unique_pairs,
                           parse_int=_json_integer, parse_float=_nonexact_json,
                           parse_constant=_nonexact_json)
    except (ValueError, RecursionError, UnicodeError) as exc:
        raise Refusal("INVALID_OR_RESOURCE_JSON") from exc
    bounded_bytes(value)
    return value


def read_report(path=REPORT):
    return _decode_json(_file_bytes(path))


def _pinned_json(path, expected):
    return _decode_json(_pinned_bytes(path, expected))


def _verified_lowerer_spec(name, path):
    """Legacy import facade: only the one pinned transitive lowerer is allowed."""
    original = HERE / "verify_pb00701_v43_refusal_cone.py"
    need(Path(path).resolve() == original.resolve(), "UNPINNED_TRANSITIVE_MODULE")
    raw = _pinned_bytes(original, PINS[original.name])
    return types.SimpleNamespace(name=name, origin=str(original),
        loader=types.SimpleNamespace(exec_module=lambda module: _execute_module(module, original, raw)))


def _module_from_verified_spec(spec):
    module = types.ModuleType(spec.name)
    module.__file__ = spec.origin
    return module


def _execute_module(module, path, raw):
    """Compile the bytes just pinned, bypassing every filesystem bytecode cache.

    Three historical producers import their lowerer at module initialization.
    A module-local importlib.util facade applies the same rule transitively;
    global import machinery and the historical files remain unchanged.
    """
    original_import = builtins.__import__
    facade = types.SimpleNamespace(util=types.SimpleNamespace(
        spec_from_file_location=_verified_lowerer_spec,
        module_from_spec=_module_from_verified_spec))

    def verified_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "importlib.util" and level == 0:
            need(not fromlist, "UNREVIEWED_IMPORTLIB_INTERFACE")
            return facade
        return original_import(name, globals, locals, fromlist, level)

    module.__file__ = str(path)
    module.__dict__["__builtins__"] = dict(vars(builtins), __import__=verified_import)
    exec(compile(raw, str(path), "exec"), module.__dict__)


def _module(filename, expected):
    path = HERE / filename
    raw = _pinned_bytes(path, expected)
    module = types.ModuleType("ratio_prefix_" + path.stem)
    _execute_module(module, path, raw)
    return module


def _dependency_expected(path):
    resolved = Path(path).resolve()
    allowed = {str((HERE / name).resolve()): sha for name, sha in PINS.items()}
    allowed.update({str((ROOT / name).resolve()): sha for name, sha in ROOT_PINS.items()})
    need(str(resolved) in allowed, "UNPINNED_LEGACY_INPUT")
    return allowed[str(resolved)]


def _dependency_json(path):
    return _pinned_json(path, _dependency_expected(path))


def _dependency_blob(path):
    expected = _dependency_expected(path)
    pin(path, expected)
    return expected


def _controls(values):
    need(type(values) in (list, tuple) and 1 <= len(values) <= MAX_DEGREE + 1,
         "BOUNDED_BERNSTEIN_CONTROLS_REQUIRED")
    need(all(type(x) is Q and max(x.numerator.bit_length(), x.denominator.bit_length()) <= 4096
             for x in values), "EXACT_BOUNDED_DERIVED_RATIONALS_REQUIRED")
    return list(values)


def _power(values):
    values = _controls(values)
    n = len(values) - 1
    result = [Q(0)] * (n + 1)
    for i, value in enumerate(values):
        for j in range(n - i + 1):
            result[i+j] += value * comb(n, i) * comb(n-i, j) * (-1)**j
    return _controls(result)


def _derivative(values):
    values = _controls(values)
    n = len(values) - 1
    if n == 0:
        return [Q(0)]
    result = [n*(right-left) for left, right in zip(values, values[1:])]
    power = _power(values)
    need(_power(result) == [i*power[i] for i in range(1, len(power))],
         "BERNSTEIN_DERIVATIVE_IDENTITY")
    return result


def _evaluate(values, at):
    values = _controls(values)
    need(type(at) is Q and Q(0) <= at <= Q(1) and
         max(at.numerator.bit_length(), at.denominator.bit_length()) <= 256,
         "BOUNDED_UNIT_PARAMETER_REQUIRED")
    n = len(values) - 1
    value = sum(c*comb(n, i)*at**i*(1-at)**(n-i) for i, c in enumerate(values))
    need(value == sum(c*at**i for i, c in enumerate(_power(values))),
         "BERNSTEIN_POINT_IDENTITY")
    return value


def _two_spans(spline):
    bounded_bytes(spline)
    need(type(spline) is dict and set(spline) == {"degree", "knots", "controls"},
         "ORIGINAL_SPLINE_FIELDS")
    n = spline["degree"]
    need(type(n) is int and 0 <= n <= MAX_DEGREE, "BOUNDED_INTEGER_SPLINE_DEGREE")
    width = n + 1
    need(type(spline["knots"]) is list and
         spline["knots"] == ["0"]*width+["1"]*width+["2"]*width,
         "ORIGINAL_FULLY_CLAMPED_UNIT_PIECES_REQUIRED")
    need(type(spline["controls"]) is list and len(spline["controls"]) == 2*width,
         "ORIGINAL_CONTROL_COUNT")
    values = [exact(x) for x in spline["controls"]]
    first, second = values[:width], values[width:]
    need(first[-1] == second[0], "DISCONTINUOUS_ORIGINAL_SOURCE_KNOT")
    return first, second


def _parse_source(source, owner):
    bounded_bytes(source)
    need(type(source) is dict and set(source) == {
        "grammar", "source_parameter_id", "parameter_lo", "parameter_hi",
        "phase_turn_offset", "phase_turn_rate", "cos_splines", "sin_splines"},
        "ORIGINAL_SOURCE_FIELDS")
    need(source["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE" and
         type(source["source_parameter_id"]) is str and 0 < len(source["source_parameter_id"]) <= 128,
         "SOURCE_GRAMMAR_OR_PARAMETER")
    need((exact(source["parameter_lo"]), exact(source["parameter_hi"])) == (Q(0), Q(2)),
         "ORIGINAL_INTERVAL_REQUIRED")
    phase = (exact(source["phase_turn_offset"]), exact(source["phase_turn_rate"]))
    need(owner in (V10, V11) and phase == ((Q(-1, 2) if owner == V10 else Q(0)), Q(2)),
         "ORIGINAL_RATIO_PHASE_REQUIRED")
    need(type(source["cos_splines"]) is dict and set(source["cos_splines"]) == {"0", "1"} and
         type(source["sin_splines"]) is dict and set(source["sin_splines"]) == {"1"},
         "UNACCOUNTED_HARMONIC_OR_RESIDUAL")
    blocks = {"C0": _two_spans(source["cos_splines"]["0"]),
              "C1": _two_spans(source["cos_splines"]["1"]),
              "S1": _two_spans(source["sin_splines"]["1"])}
    return blocks, phase


def _value(blocks, phase, at, piece):
    need(type(piece) is int and piece in (0, 1), "ORIGINAL_PIECE_INDEX")
    quadrants = 4*(phase[0]+phase[1]*at)
    need(quadrants.denominator == 1, "EXACT_QUADRANT_POINT_REQUIRED")
    quadrant = int(quadrants) % 4
    local = at - piece
    return (_evaluate(blocks["C0"][piece], local) +
            _evaluate(blocks["C1"][piece], local)*[1, 0, -1, 0][quadrant] +
            _evaluate(blocks["S1"][piece], local)*[0, 1, 0, -1][quadrant])


def _sign(value):
    need(value != 0, "EXACT_ZERO_REQUIRES_SEPARATE_EVENT_BRANCH")
    return "POSITIVE" if value > 0 else "NEGATIVE"


def _opposite(sign):
    need(sign in ("NEGATIVE", "POSITIVE"), "UNPROVED_PHYSICAL_SIGN")
    return "NEGATIVE" if sign == "POSITIVE" else "POSITIVE"


def _chart_bracket(blocks, phase, left, right, midpoint=None):
    left_value, right_value = (_value(blocks, phase, at, 0) for at in (left, right))
    need(left_value*right_value < 0, "CHART_ENDPOINT_SIGNS_NOT_OPPOSITE")
    if midpoint is not None:
        middle_value = _value(blocks, phase, midpoint, 0)
        need(middle_value != 0, "EXACT_CHART_MIDPOINT_ZERO_REQUIRES_SEPARATE_BRANCH")
        if left_value*middle_value < 0:
            right, right_value = midpoint, middle_value
        else:
            left, left_value = midpoint, middle_value
    need(left < right and left_value*right_value < 0, "STRICT_OPEN_ROOT_BRACKET_REQUIRED")
    return {"strict_open_interval": [str(left), str(right)],
            "exact_boundary_values": [str(left_value), str(right_value)]}


def _prefix_record(source, blocks, phase, family, derivative_controls, derivative_bound,
                   charts, brackets, poles):
    roots = [chart for chart in charts if chart["root_count"] == 1]
    need(len(roots) == len(brackets) == 4, "FOUR_PREFIX_ROOTS_REQUIRED")
    initial = _sign(_value(blocks, phase, Q(0), 0))
    signs = [initial]
    for _ in roots:
        signs.append(_opposite(signs[-1]))
    need(signs[-1] == _sign(_value(blocks, phase, Q(1), 0)), "PREFIX_ENDPOINT_SIGN_MISMATCH")
    cuts = set(poles)
    for bracket in brackets:
        cuts.update(exact(x) for x in bracket["strict_open_interval"])
    cuts = sorted(at for at in cuts if 0 < at < 1)
    return {
        "proof_family": family, "source_sha256": digest(source),
        "source_parameter_id": source["source_parameter_id"], "source_piece_index": 0,
        "source_interval": ["0", "1"], "complete_first_closed_span": True,
        "conditional_lemma_not_frozen_source_acceptance": True,
        "original_prefix_power_coefficients": {name: [str(x) for x in _power(sides[0])]
                                               for name, sides in blocks.items()},
        "original_amplitude_derivative_controls": [str(x) for x in derivative_controls],
        "strict_ratio_derivative_bound": derivative_bound,
        "charts": charts, "root_brackets": [x["strict_open_interval"] for x in brackets],
        "bracket_sign_proofs": brackets, "root_uniqueness_cells": [x["interval"] for x in roots],
        "root_multiplicities": [1]*4,
        "root_simplicity_basis": "NONZERO_CHART_MULTIPLIER_TIMES_STRICT_RATIO_DERIVATIVE",
        "endpoint_values": [str(_value(blocks, phase, at, 0)) for at in (Q(0), Q(1))],
        "maximal_sign_cells": signs,
        "proof_cuts": [{"parameter": str(at), "kind": "RATIO_CHART_POLE" if at in poles else
                        "EXACT_BRACKET_SIGN_WITNESS", "exact_source_value": str(_value(blocks, phase, at, 0)),
                        "value_sign": _sign(_value(blocks, phase, at, 0)), "is_zero_event": False}
                       for at in cuts],
        "chart_poles_are_nonzero_original_source_points": True,
    }


def cotangent_prefix_proof(source):
    """Sufficient conditions for four simple prefix roots of cos(theta)+B*sin(theta).

    theta=4*pi*t-pi. On each open quarter-span chart H=cot(theta)+B.
    The Bernstein derivative upper bound B'<12 gives H'<B'_upper-12<0.
    The cotangent limits are +infinity and -infinity; sin is nonzero inside.
    At every chart pole the original F is the nonzero cosine value.
    """
    blocks, phase = _parse_source(source, V10)
    need(all(x == 0 for x in blocks["C0"][0]) and all(x == 1 for x in blocks["C1"][0]),
         "COTANGENT_FACTOR_IDENTITY_REQUIRES_ZERO_BIAS_AND_UNIT_COSINE")
    derivative = _derivative(blocks["S1"][0])
    upper = max(derivative)
    need(upper < 12, "STRICT_DECREASING_COTANGENT_PREMISE_UNAVAILABLE")
    grid = [Q(i, 4) for i in range(5)]
    charts, brackets = [], []
    for left, right in zip(grid, grid[1:]):
        charts.append({"interval": [str(left), str(right)], "open_at_both_poles": True,
                       "ratio_left_limit": "POSITIVE_INFINITY", "ratio_right_limit": "NEGATIVE_INFINITY",
                       "root_count": 1, "nonzero_chart_multiplier": "sin(theta)"})
        brackets.append(_chart_bracket(blocks, phase, left, right, (left+right)/2))
    return _prefix_record(source, blocks, phase, "STRICT_DECREASING_COTANGENT_CHARTS",
                          derivative, {"direction": "UPPER", "value": str(upper-12),
                                       "strict": True, "pi_lower_bound": "3"}, charts, brackets, grid)


def tangent_prefix_proof(source):
    """Sufficient conditions for four simple prefix roots of A*cos(theta)+sin(theta).

    theta=4*pi*t. H=A+tan(theta) has H'>A'_lower+12>=0 when A'_lower>=-12.
    Positive A(0),A(1) exclude the initial truncated chart and give one root
    in the final chart. Each of the three full middle charts has one root.
    """
    blocks, phase = _parse_source(source, V11)
    need(all(x == 0 for x in blocks["C0"][0]) and all(x == 1 for x in blocks["S1"][0]),
         "TANGENT_FACTOR_IDENTITY_REQUIRES_ZERO_BIAS_AND_UNIT_SINE")
    amplitude = blocks["C1"][0]
    derivative = _derivative(amplitude)
    lower = min(derivative)
    need(lower >= -12, "STRICT_INCREASING_TANGENT_PREMISE_UNAVAILABLE")
    need(amplitude[0] > 0 and amplitude[-1] > 0, "POSITIVE_TRUNCATED_CHART_ENDPOINTS_REQUIRED")
    poles = [Q(1, 8)+Q(i, 4) for i in range(4)]
    charts = [{"interval": ["0", "1/8"], "left_closed": True, "right_closed": False,
               "ratio_left_value": str(amplitude[0]), "ratio_right_limit": "POSITIVE_INFINITY",
               "root_count": 0, "nonzero_chart_multiplier": "cos(theta)"}]
    brackets = []
    for left, right in zip(poles, poles[1:]):
        charts.append({"interval": [str(left), str(right)], "open_at_both_poles": True,
                       "ratio_left_limit": "NEGATIVE_INFINITY", "ratio_right_limit": "POSITIVE_INFINITY",
                       "root_count": 1, "nonzero_chart_multiplier": "cos(theta)"})
        brackets.append(_chart_bracket(blocks, phase, left, right, (left+right)/2))
    charts.append({"interval": ["7/8", "1"], "left_closed": False, "right_closed": True,
                   "ratio_left_limit": "NEGATIVE_INFINITY", "ratio_right_value": str(amplitude[-1]),
                   "root_count": 1, "nonzero_chart_multiplier": "cos(theta)"})
    brackets.append(_chart_bracket(blocks, phase, Q(7, 8), Q(1)))
    return _prefix_record(source, blocks, phase, "STRICT_INCREASING_TANGENT_CHARTS",
                          derivative, {"direction": "LOWER", "value": str(lower+12),
                                       "strict": True, "pi_lower_bound": "3"}, charts, brackets, poles)


def check_original(row):
    bounded_bytes(row)
    need(type(row) is dict and set(row) == {"id", "origin", "kind", "spec", "expected"},
         "ORIGINAL_ROW_FIELDS")
    need(type(row["id"]) is str and row["id"] in CASES, "UNREGISTERED_ORIGINAL_SOURCE")
    case = CASES[row["id"]]
    need(digest(row["spec"]) == case["source_sha256"] and digest(row) == case["row_sha256"],
         "ORIGINAL_SOURCE_OR_WHOLE_ROW_DIGEST")
    need(row["origin"] == case["origin"] and row["kind"] == "COMPOSITE_TAIL",
         "ORIGINAL_PROVENANCE")
    need(bounded_bytes(row["expected"]) == bounded_bytes({
        "id": row["id"], "observed": {"status": "BLOCKED", "spans": [
            [case["owner"], "CERTIFIED", None], [TAIL_OWNER, "BLOCKED", TAIL_REASON]]},
        "v54_disposition": "BLOCKED"}), "HISTORICAL_OWNER_OR_REFUSAL")
    return _parse_source(row["spec"], case["owner"])


def original_rows():
    for name, expected in PINS.items():
        pin(HERE / name, expected)
    for name, expected in ROOT_PINS.items():
        pin(ROOT / name, expected)
    for name, expected in PRODUCERS.values():
        pin(HERE / name, expected)
    corpus, inventory, coverage = [_dependency_json(HERE / name) for name in list(PINS)[:3]]
    auditor = _module("verify_pb00701_post_v54_frontier.py", PINS["verify_pb00701_post_v54_frontier.py"])
    audit = auditor.audit(corpus, inventory, coverage)
    need(audit["cases"] == 121 and audit["v54_dispositions"]["BLOCKED"] == 20 and
         audit["v54_dispositions"]["BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"] == 30,
         "HISTORICAL_121_20_30_DRIFT")
    domain, programme, authority = [_dependency_json(ROOT / name) for name in ROOT_PINS]
    need(len(domain["coverage_rule"]["required_operation_ids"]) == 26, "DOMAIN_DENOMINATOR_DRIFT")
    need(authority["capability_status"] == programme["capability_status"] == "NOT_ESTABLISHED" and
         authority["production_authorized"] is False and programme["production_authorized"] is False and
         any(x["id"] == "MC-B" and x["state"] == "NOT_ESTABLISHED" for x in programme["gates"]),
         "AUTHORITY_OR_GATE_PROMOTED")
    rows = [row for row in corpus["cases"] if row["id"] in CASES]
    need(len(rows) == 4 and {row["id"] for row in rows} == set(CASES), "FOUR_SOURCE_SCOPE_DRIFT")
    for row in rows:
        check_original(row)
    return {row["id"]: row for row in rows}


def _tail_receipts():
    results = {}
    for producer, (filename, expected) in PRODUCERS.items():
        module = _module(filename, expected)
        module.load_json = _dependency_json
        module.blob_sha = _dependency_blob
        module.git_blob = _dependency_blob  # V10 ramp uses this historical spelling.
        proof = module.contract()
        bounded_bytes(proof)
        views = proof["v11_v43_tail_reports"] if producer == "V11_PAIR" else [proof]
        wanted = {cid for cid, case in CASES.items() if case["producer"] == producer}
        observed = [view.get("case_id", view.get("source_case")) for view in views]
        need(len(views) == len(wanted) and set(observed) == wanted, "TAIL_SOURCE_SCOPE_DRIFT")
        for cid, view in zip(observed, views):
            need(digest(view) == CASES[cid]["tail_replay_sha256"], "TAIL_REPLAY_RESULT_DRIFT")
            results[cid] = view
        pin(HERE / filename, expected)
    return results


def _tail_view(cid, receipt):
    case = CASES[cid]
    need(digest(receipt) == case["tail_replay_sha256"], "TAIL_RECEIPT_UNTRUSTED")
    if case["producer"] == "V10_RAMP":
        interval = receipt["source_span"]
        values = [receipt["left_exact_value"], receipt["right_exact_value"]]
        signs = [receipt["physical_sign_before_root"], receipt["physical_sign_after_root"]]
        brackets, uniqueness = [receipt["strict_open_root_bracket"]], [interval]
        need(receipt["exact_open_roots"] == 1 and exact(receipt["derivative_strict_lower_bound"]) > 0 and
             receipt["root_event"] == "SIMPLE_NEGATIVE_TO_POSITIVE_CROSSING", "V10_TAIL_CROSSING_PROOF")
    elif case["tail"] == 0:
        interval = receipt["physical_source_span"]
        point_values = receipt["exact_endpoint_values"] if case["owner"] == V10 else receipt["exact_halfcycle_endpoint_values"]
        values = [point_values[0], point_values[-1]]
        roots = receipt["ordered_open_roots"]
        count = receipt["exact_open_roots"] if case["owner"] == V10 else receipt["exact_open_physical_roots"]
        need(count == len(roots) == 4 and all(root["multiplicity"] == 1 and
             root["event_kind"] == "SIMPLE_CROSSING" for root in roots), "FOUR_SIMPLE_TAIL_ROOTS")
        brackets = [root["strict_source_bracket"] for root in roots]
        uniqueness = [root["half_cycle_open_source_interval"] for root in roots]
        signs = receipt["complete_sign_cells"]
    else:
        interval = receipt["physical_source_span"]
        values, signs = receipt["exact_source_endpoint_values"], receipt["complete_sign_cells"]
        brackets, uniqueness = [], []
        need(receipt["exact_open_physical_roots"] == 0 and
             exact(receipt["strict_source_derivative_lower_rational"]) > 0 and
             exact(values[0]) > 0, "V11_POSITIVE_ROOT_FREE_TAIL")
    need(interval == ["1", "2"] and len(signs) == len(brackets)+1, "TAIL_INTERVAL_OR_SIGN_COUNT")
    return {"source_sha256": case["source_sha256"], "source_interval": interval,
            "endpoint_values": values, "root_brackets": brackets, "root_uniqueness_cells": uniqueness,
            "root_multiplicities": [1]*len(brackets), "maximal_sign_cells": signs,
            "producer": PRODUCERS[case["producer"]][0],
            "producer_git_blob": PRODUCERS[case["producer"]][1],
            "fresh_replay_sha256": digest(receipt), "complete_second_closed_span": True}


def _compose(row, blocks, phase, prefix, tail):
    """Structural compositor for views freshly proved by this fixed wrapper."""
    cid, source = row["id"], row["spec"]
    need(prefix["source_sha256"] == tail["source_sha256"] == digest(source), "CROSS_SOURCE_VIEW_SUBSTITUTION")
    need(prefix["source_interval"] == ["0", "1"] and tail["source_interval"] == ["1", "2"],
         "ORIGINAL_PIECE_PARTITION")
    left, knot_left, knot_right, right = [_value(blocks, phase, at, piece) for at, piece in
                                        ((Q(0), 0), (Q(1), 0), (Q(1), 1), (Q(2), 1))]
    need(knot_left == knot_right, "ORIGINAL_KNOT_CONTINUITY")
    need([str(left), str(knot_left)] == prefix["endpoint_values"] and
         [str(knot_right), str(right)] == tail["endpoint_values"], "ACTUAL_SOURCE_ENDPOINT_MISMATCH")
    knot_sign = _sign(knot_left)
    need(prefix["maximal_sign_cells"][-1] == tail["maximal_sign_cells"][0] == knot_sign,
         "NONZERO_KNOT_SIGN_MISMATCH")
    events, all_brackets = [], []
    for piece, view in enumerate((prefix, tail)):
        brackets, signs = view["root_brackets"], view["maximal_sign_cells"]
        need(len(signs) == len(brackets)+1 and len(view["root_uniqueness_cells"]) == len(brackets) and
             view["root_multiplicities"] == [1]*len(brackets), "COMPLETE_SIMPLE_VIEW_SHAPE")
        need(signs[0] == _sign(exact(view["endpoint_values"][0])) and
             signs[-1] == _sign(exact(view["endpoint_values"][1])), "VIEW_EXTERIOR_SIGN_MISMATCH")
        previous = Q(piece)
        for j, (bracket, unique) in enumerate(zip(brackets, view["root_uniqueness_cells"])):
            lo, hi = map(exact, bracket)
            unique_lo, unique_hi = map(exact, unique)
            need(Q(piece) <= unique_lo <= lo < hi <= unique_hi <= Q(piece+1) and previous <= lo,
                 "ORDERED_ORIGINAL_ROOT_BRACKETS_REQUIRED")
            need(signs[j+1] == _opposite(signs[j]), "SIMPLE_ROOT_SIGN_REVERSAL_REQUIRED")
            previous = hi
            all_brackets.append([str(lo), str(hi)])
            events.append({"event_id": "root-"+str(len(events)), "source_piece_index": piece,
                           "coordinate": {"kind": "IMPLICIT_ORIGINAL_SOURCE_ROOT",
                                          "source_case_id": cid, "original_source_sha256": digest(source),
                                          "source_parameter_id": source["source_parameter_id"],
                                          "defining_predicate": "ORIGINAL_SOURCE_F_EQUALS_ZERO",
                                          "strict_open_isolating_interval": [str(lo), str(hi)],
                                          "uniqueness_cell": unique},
                           "analytic_order": 1, "left_sign": signs[j], "right_sign": signs[j+1]})
    signs = prefix["maximal_sign_cells"]+tail["maximal_sign_cells"][1:]
    edges = [{"kind": "RATIONAL", "value": "0"}]+[
        {"kind": "EVENT_REFERENCE", "event_id": event["event_id"]} for event in events]+[
        {"kind": "RATIONAL", "value": "2"}]
    cuts = copy.deepcopy(prefix["proof_cuts"])
    for at in (Q(5, 4), Q(3, 2), Q(7, 4)):
        value = _value(blocks, phase, at, 1)
        cuts.append({"parameter": str(at), "kind": "TAIL_HALF_CYCLE_BOUNDARY",
                     "exact_source_value": str(value), "value_sign": _sign(value), "is_zero_event": False})
    return {"source_interval": ["0", "2"], "original_piece_edges": ["0", "1", "2"],
            "closed_distinct_root_count": len(events), "open_distinct_root_count": len(events),
            "events": events, "strict_ordered_root_brackets": all_brackets,
            "maximal_sign_cells": [{"left": edges[i], "right": edges[i+1], "sign": sign,
                                    "left_closed": i == 0, "right_closed": i == len(signs)-1}
                                   for i, sign in enumerate(signs)],
            "exterior_endpoints": [{"parameter": str(at), "exact_value": str(value),
                                    "value_sign": _sign(value), "is_zero_event": False}
                                   for at, value in ((0, left), (2, right))],
            "original_source_knot": {"parameter": "1", "source_continuous": True,
                                     "exact_left_value": str(knot_left), "exact_right_value": str(knot_right),
                                     "value_sign": knot_sign, "is_zero_event": False},
            "proof_cuts": cuts, "continuum_zero_component": False,
            "complete_for_original_closed_source": True}


def _source_proof(row, receipt):
    blocks, phase = check_original(row)
    case = CASES[row["id"]]
    prefix = (cotangent_prefix_proof(row["spec"]) if case["owner"] == V10 else
              tangent_prefix_proof(row["spec"]))
    tail = _tail_view(row["id"], receipt)
    physical = _compose(row, blocks, phase, prefix, tail)
    need(physical["closed_distinct_root_count"] == case["closed_root_count"], "FROZEN_RESULT_CHANGED")
    return {"source_case_id": row["id"], "original_source_sha256": case["source_sha256"],
            "original_row_sha256": case["row_sha256"], "original_source": row["spec"],
            "historical_observation": row["expected"], "prefix_proof": prefix,
            "tail_proof": tail, "fresh_tail_receipt": receipt, "physical_event_proof": physical}


def source_proof(row):
    check_original(row)
    originals = original_rows()
    receipts = _tail_receipts()
    return _source_proof(originals[row["id"]], receipts[row["id"]])


def expected_report():
    originals, receipts = original_rows(), _tail_receipts()
    proofs = [_source_proof(originals[cid], receipts[cid]) for cid in sorted(CASES)]
    return {"schema": SCHEMA, "task": "MC-038", "evidence_class": "DETERMINISTIC_EXACT_SOURCE_BOUND_MODEL",
            "recorded_utc": RECORDED_UTC, "source_baseline_main": BASE_MAIN,
            "preregistration_comments": list(PREREGISTRATION_COMMENTS),
            "dependencies": {"local_git_blobs": dict(PINS), "root_git_blobs": dict(ROOT_PINS),
                             "tail_producers": {name: {"path": value[0], "git_blob": value[1]}
                                                for name, value in PRODUCERS.items()}},
            "analytic_foundation": {"pi_strict_lower_bound": "3",
                                     "bernstein_basis_nonnegative_partition_of_unity": True,
                                     "derivative_and_point_power_identities_rechecked": True,
                                     "ratio_asymptotes_and_nonzero_chart_multipliers": True},
            "source_cases": proofs,
            "summary": {"complete_original_source_witnesses": 4,
                        "by_case_closed_root_count": {p["source_case_id"]: p["physical_event_proof"][
                            "closed_distinct_root_count"] for p in proofs},
                        "all_physical_roots_simple": True, "original_knot_roots": 0, "exterior_roots": 0},
            "historical_v54": {"original_sources": 121, "route_refusals": 20,
                               "missing_ordered_premises": 30, "dispositions_changed": False},
            "resources": {"maximum_spline_degree": MAX_DEGREE, "input_rational_bit_limit": 256,
                          "byte_limit": MAX_BYTES, "native_campaign_run": False, "paid_campaign_run": False},
            "scope": {"historical_owner_routes_repaired": False, "universal_proof_consumer": False,
                      "general_ratio_or_v43_event_solver": False, "PB00701_closed": False,
                      "MC_B": "NOT_ESTABLISHED", "MC_1": "NOT_ESTABLISHED",
                      "production_authorized": False, "protected_operation_count": 26,
                      "native_material_topology_or_STEP_qualified": False}}


def validate_report(candidate):
    actual = bounded_bytes(candidate)
    need(actual == bounded_bytes(expected_report()), "FRESH_SOURCE_PROOF_REPORT_MISMATCH")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    result = expected_report()
    if args.write_report:
        REPORT.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()


