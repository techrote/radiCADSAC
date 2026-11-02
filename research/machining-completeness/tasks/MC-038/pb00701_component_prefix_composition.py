#!/usr/bin/env python3
"""Complete five frozen original sources from exact carrier prefixes and tails.

The carrier lemma is independently reusable on its stated unit interval. The
whole-source wrapper admits exactly five frozen records and reexecutes their
pinned tail producers. It is not a generic V43 route or a public consumer of
caller-supplied truth assertions. Historical dispositions and gates stay open.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from math import gcd
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
SCHEMA = "radicadsac-mc038-component-prefix-composition/1.0"
REPORT = HERE / "pb00701-component-prefix-composition.json"
BASE_MAIN = "e0514500aeca59afa4924dcc2da3ca0c2688d9ac"
RECORDED_UTC = "2026-11-02T23:51:19Z"
PREREGISTRATION_COMMENT = 6591325199
MAX_BYTES = 1048576
MAX_NODES = 65536
MAX_DEPTH = 32
MAX_STRING = 8192
RATIONAL = re.compile(r"(-?)(0|[1-9][0-9]{0,77})(?:/([1-9][0-9]{0,77}))?")
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
    "V12": ("verify_pb00701_v43_v12_tail_contrast.py", "2b2e85f662f4cb2a97b82e264e007c38cada69fd"),
    "V13": ("verify_pb00701_v43_v13_even_factor.py", "998130ba26f553237ac261017f3edc13f5f57700"),
    "V16": ("verify_pb00701_v43_v16_chebyshev_crossing.py", "74bbdb48125f4168308fb6ffcbac4e5a08049c5d"),
    "V17": ("verify_pb00701_v43_v17_positive_turn.py", "e245b13045a96f549747baae1b25556da6cc9808"),
}
CASE_DATA = [
    ("PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC", 0, "v19", "V12",
     "ee15e947924b45640dd16634247a476bb230fdc145fef94407d9a7c219928cd5",
     "d0acef7c69cb8ac1ba128b988e83817a91feff78509dd18007d0e56a506336c3",
     "ba5874f4e56e4b76456c8028a891b28d87a896bedcb59ff75716a83a37a6a9ab"),
    ("PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC", 100, "v19", "V12",
     "65b71861fed07c4b609364dd79c8c1700abe72ca8bcb8f70aec0a54af90d94f7",
     "748ed522c8a2f7cc3d6bdb17cc2322d4d4fd3121378c3b5a0dc829861f88aa15",
     "b3142318e78b67236a9d4d0c2242996abc7e45518c213e99616a347a8b59ed41"),
    ("PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC", 0, "verify_pb00701_v13", "V13",
     "c7abfbbba43a61fbcfc72fc3833a0dc764b6c0d10a29ee4f6faf178c7db12b9b",
     "9a69a5d28c6808a54591cb8b72af59d752a1861ae860875fc858388d114c74af",
     "22d99b694e7688137b2b156846c55d8635240ac987549a5a535f6172509c3ae0"),
    ("PB00701_V16_EXACT_CHEBYSHEV_STURM_MULTIPLIER", 100, "verify_pb00701_v16", "V16",
     "89ff16b64ab62d1b3cd543e3c52c4f0f8c570dc29b3448545b391a8d798da9d6",
     "843557d83755db09aedfce1d145d2a41945ebe65accffa0b6077afee8d94c4b0",
     "dcbfe941df5960c186e2d7930ef961daf5e757b978a9f8a3d4ebe317f737db32"),
    ("PB00701_V17_EXACT_PROJECTIVE_EVEN_TRIG_MULTIPLIER", 0, "verify_pb00701_v17", "V17",
     "f4927df0e4db8a02af0905219d07fd1fdf4dfd8a50c0ef426323e633d6880d94",
     "a0e6a03211083aea1ad7db4aefd0cf813d9ec13780564d01f8ee8b556ccbc59e",
     "8ed5a9bdd2667dda168f387152358316b4317f01cb13488ae8422cd06c6bf5fd"),
]
CASES = {
    "composite:" + owner + ":tail" + str(tail): {
        "owner": owner, "tail": tail, "origin": origin, "family": family,
        "source_sha256": source_sha, "original_row_sha256": row_sha,
        "tail_replay_sha256": tail_sha,
    }
    for owner, tail, origin, family, source_sha, row_sha, tail_sha in CASE_DATA
}


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
    need(git_blob(path) == expected, "PINNED_SOURCE_DRIFT: " + str(path))


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


def read_report(path=REPORT):
    try:
        value = json.loads(_file_bytes(path), object_pairs_hook=_unique_pairs,
                           parse_int=_json_integer, parse_float=_nonexact_json,
                           parse_constant=_nonexact_json)
    except (ValueError, RecursionError, UnicodeError) as exc:
        raise Refusal("INVALID_OR_RESOURCE_JSON") from exc
    bounded_bytes(value)
    return value


def _module(filename, expected):
    path = HERE / filename
    pin(path, expected)
    spec = importlib.util.spec_from_file_location("component_prefix_" + path.stem, path)
    need(spec is not None and spec.loader is not None, "PINNED_MODULE_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    pin(path, expected)
    return module


def _inputs():
    for filename, expected in PINS.items():
        pin(HERE / filename, expected)
    for filename, expected in ROOT_PINS.items():
        pin(ROOT / filename, expected)
    for filename, expected in PRODUCERS.values():
        pin(HERE / filename, expected)
    corpus = read_report(HERE / "pb00701-finite-owner-corpus-v54.json")
    inventory = read_report(HERE / "pb00701-finite-owner-inventory-v54.json")
    coverage = read_report(HERE / "pb00701-finite-owner-coverage-v54.json")
    auditor = _module("verify_pb00701_post_v54_frontier.py", PINS["verify_pb00701_post_v54_frontier.py"])
    audit = auditor.audit(corpus, inventory, coverage)
    need(audit["cases"] == 121 and audit["v54_dispositions"]["BLOCKED"] == 20 and
         audit["v54_dispositions"]["BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"] == 30,
         "HISTORICAL_121_20_30_DRIFT")
    auth = read_report(ROOT / "handoffs/current-authority.json")
    programme = read_report(ROOT / "research/machining-completeness/programme-v1.json")
    domain = read_report(ROOT / "research/machining-completeness/tasks/MC-002/domain-contract-v1.json")
    need(auth["capability_status"] == programme["capability_status"] == "NOT_ESTABLISHED" and
         auth["production_authorized"] is False and programme["production_authorized"] is False and
         any(g["id"] == "MC-B" and g["state"] == "NOT_ESTABLISHED" for g in programme["gates"]),
         "AUTHORITY_OR_GATE_PROMOTED")
    need(len(domain["coverage_rule"]["required_operation_ids"]) == 26, "DOMAIN_DENOMINATOR_DRIFT")
    rows = [row for row in corpus["cases"] if row["id"] in CASES]
    need(len(rows) == 5 and {row["id"] for row in rows} == set(CASES), "FIVE_SOURCE_SCOPE_DRIFT")
    return {row["id"]: row for row in rows}


def original_rows():
    return copy.deepcopy(_inputs())


def _add(a, b):
    out = [Q(0)] * max(len(a), len(b))
    for i, value in enumerate(a):
        out[i] += value
    for i, value in enumerate(b):
        out[i] += value
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def _scale(a, value):
    return _add([x * value for x in a], [Q(0)])


def _multiply(a, b):
    out = [Q(0)] * (len(a) + len(b) - 1)
    for i, left in enumerate(a):
        for j, right in enumerate(b):
            out[i + j] += left * right
    return _add(out, [Q(0)])


def _chebyshev():
    first, second = [[Q(1)], [Q(0), Q(1)]], [[Q(1)], [Q(0), Q(2)]]
    for _ in range(2, 8):
        first.append(_add(_multiply([Q(0), Q(2)], first[-1]), _scale(first[-2], -1)))
        second.append(_add(_multiply([Q(0), Q(2)], second[-1]), _scale(second[-2], -1)))
    return first, second


def _two_pieces(spline):
    need(type(spline) is dict and set(spline) == {"degree", "knots", "controls"}, "UNREVIEWED_SPLINE_FIELDS")
    degree = spline["degree"]
    need(type(degree) is int and degree in (0, 1), "UNSUPPORTED_SPLINE_DEGREE")
    need(spline["knots"] == [x for x in ("0", "1", "2") for _ in range(degree + 1)], "ORIGINAL_KNOTS_CHANGED")
    need(type(spline["controls"]) is list and len(spline["controls"]) == 2 * (degree + 1), "CONTROL_COUNT")
    controls = [exact(x) for x in spline["controls"]]
    if degree == 0:
        return [(controls[0], Q(0)), (controls[1], Q(0))]
    first, second = controls[1] - controls[0], controls[3] - controls[2]
    return [(controls[0], first), (controls[2] - second, second)]


def _lower_source(source):
    bounded_bytes(source)
    need(type(source) is dict and set(source) == {
        "grammar", "source_parameter_id", "parameter_lo", "parameter_hi", "phase_turn_offset",
        "phase_turn_rate", "cos_splines", "sin_splines"}, "UNREVIEWED_SOURCE_FIELDS")
    need(source["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE" and
         source["source_parameter_id"] == "source-time-t", "SOURCE_GRAMMAR_OR_PARAMETER")
    need(tuple(exact(source[k]) for k in ("parameter_lo", "parameter_hi", "phase_turn_offset", "phase_turn_rate"))
         == (Q(0), Q(2), Q(0), Q(1, 4)), "ORIGINAL_INTERVAL_OR_PHASE")
    out = {}
    for channel, permitted in (("cos_splines", {"0", "1", "3", "5", "7"}),
                               ("sin_splines", {"1", "3", "5", "7"})):
        entries = source[channel]
        need(type(entries) is dict and bool(entries) and set(entries) <= permitted, "UNACCOUNTED_HARMONIC")
        out[channel] = {int(h): _two_pieces(spline) for h, spline in entries.items()}
    continuity = []
    for channel, entries in out.items():
        for harmonic, (left, right) in sorted(entries.items()):
            left_value, right_value = sum(left), sum(right)
            need(left_value == right_value, "DISCONTINUOUS_ORIGINAL_SOURCE_KNOT")
            continuity.append({"channel": channel, "harmonic": harmonic, "left_value": str(left_value),
                               "right_value": str(right_value)})
    return out, continuity


def check_original(row):
    bounded_bytes(row)
    need(type(row) is dict and set(row) == {"id", "origin", "kind", "spec", "expected"}, "ORIGINAL_ROW_FIELDS")
    need(type(row["id"]) is str and row["id"] in CASES, "UNREGISTERED_ORIGINAL_SOURCE")
    case = CASES[row["id"]]
    need(digest(row) == case["original_row_sha256"] and digest(row["spec"]) == case["source_sha256"],
         "ORIGINAL_SOURCE_OR_WHOLE_ROW_DIGEST")
    need(row["kind"] == "COMPOSITE_TAIL" and row["origin"] == case["origin"], "ORIGINAL_PROVENANCE")
    need(bounded_bytes(row["expected"]) == bounded_bytes({
        "id": row["id"], "observed": {"status": "BLOCKED", "spans": [
            [case["owner"], "CERTIFIED", None], [TAIL_OWNER, "BLOCKED", TAIL_REASON]]},
        "v54_disposition": "BLOCKED"}), "HISTORICAL_OWNER_OR_REFUSAL")
    return _lower_source(row["spec"])


def carrier_prefix_proof():
    """Exact lemma for R=(t-1/3)cos(pi*t/2)+(2/3-t)sin(pi*t/2).

    R(1-t)=R(t). R'>1/3 on [0,1/3]; R>0 on [1/3,2/3].
    Exact half-angle bounds give R(1/6)<0<R(1/4). Reflection supplies
    the second and only other simple root. This receipt by itself binds
    no original source: a consumer must prove its own coefficient identity.
    """
    a, b = (Q(-1, 3), Q(1)), (Q(2, 3), Q(-1))
    need((a[0] + a[1], -a[1]) == b and (b[0] + b[1], -b[1]) == a, "CARRIER_REFLECTION_IDENTITY")
    need(Q(5, 6)**2 < Q(3, 4) and Q(5, 6) - Q(1, 2) == Q(1, 3), "CARRIER_STRICT_DERIVATIVE_BOUND")
    need(Q(5, 3)**2 < 3 and Q(2) - Q(5, 3) == Q(1, 3), "CARRIER_NEGATIVE_BRACKET_SIGN")
    need(Q(6, 5)**2 < 2 and Q(6, 5) - 1 == Q(1, 5), "CARRIER_POSITIVE_BRACKET_SIGN")
    need(Q(1, 6) < Q(1, 4) < Q(1, 3) < Q(2, 3) < Q(3, 4) < Q(5, 6), "CARRIER_ROOT_ORDER")
    return {
        "kind": "EXACT_UNIT_INTERVAL_COMPONENT_CARRIER_LEMMA",
        "function": "(t-1/3)*cos(pi*t/2)+(2/3-t)*sin(pi*t/2)",
        "source_interval": ["0", "1"], "phase_turn_law": {"offset": "0", "rate": "1/4"},
        "cosine_amplitude_power_coefficients": [str(x) for x in a],
        "sine_amplitude_power_coefficients": [str(x) for x in b],
        "reflection_identity": "R(1-t)=R(t)",
        "strict_derivative_lower_bound": {"interval": ["0", "1/3"], "bound": "1/3"},
        "strict_positive_middle_interval": ["1/3", "2/3"],
        "exact_bracket_sign_reason": {
            "at_1_over_6": "tan(pi/12)=2-sqrt(3)<1/3", "sqrt3_lower_square": "25/9",
            "at_1_over_4": "tan(pi/8)=sqrt(2)-1>1/5", "sqrt2_lower_square": "36/25"},
        "root_brackets": [["1/6", "1/4"], ["3/4", "5/6"]],
        "root_multiplicities": [1, 1], "maximal_sign_cells": ["NEGATIVE", "POSITIVE", "NEGATIVE"],
        "closed_endpoint_values": ["-1/3", "-1/3"], "closed_endpoint_roots": 0,
        "proof_cuts": ["1/3", "2/3"], "proof_cuts_are_physical_events": False,
        "original_source_binding_supplied_by_this_lemma": False,
    }


def _factor_identity(pieces, family):
    need(family in PRODUCERS, "UNSUPPORTED_CARRIER_FACTOR")
    harmonics = {1} if family == "V12" else ({1, 3, 5, 7} if family == "V16" else {1, 3})
    need(set(pieces["cos_splines"]) == harmonics | {0} and set(pieces["sin_splines"]) == harmonics,
         "FACTOR_HARMONICS_MISSING_OR_ADDED")
    need(pieces["cos_splines"][0][0] == (Q(0), Q(0)), "NONZERO_PREFIX_BIAS")
    first, second = _chebyshev()
    a, b = (Q(-1, 3), Q(1)), (Q(2, 3), Q(-1))
    multiplier = ({"V12": [Q(1)], "V13": [Q(1), Q(0), Q(2)],
                   "V16": [Q(409), Q(0), Q(-782), Q(0), Q(352), Q(0), Q(32)]}.get(family))
    reconstructed = []
    for degree in range(2):
        cosine, sine = [Q(0)], [Q(0)]
        for harmonic in sorted(harmonics):
            cosine = _add(cosine, _scale(first[harmonic], pieces["cos_splines"][harmonic][0][degree]))
            sine = _add(sine, _scale(second[harmonic - 1], pieces["sin_splines"][harmonic][0][degree]))
        if family == "V17":
            # (sin(2theta)-2)(a*cos(theta)+b*sin(theta)), using
            # sin(2theta)=2*sin(theta)*cos(theta), sin²=1-cos².
            expected_cos = [Q(0), -2*a[degree] + 2*b[degree], Q(0), -2*b[degree]]
            expected_sin = [-2*b[degree], Q(0), 2*a[degree]]
        else:
            expected_cos = _scale(_multiply([Q(0), Q(1)], multiplier), a[degree])
            expected_sin = _scale(multiplier, b[degree])
        need(cosine == _add(expected_cos, [Q(0)]) and sine == _add(expected_sin, [Q(0)]),
             "ORIGINAL_HARMONIC_FACTOR_IDENTITY_FAILED")
        reconstructed.append({"t_power": degree, "cosine_polynomial_in_cos_theta": [str(x) for x in cosine],
                              "sine_coefficient_polynomial_in_cos_theta": [str(x) for x in sine]})
    if family == "V16":
        # z=cos²theta, w=1-z. P=11-18w+448w²-32w³.
        p = [Q(409), Q(-782), Q(352), Q(32)]
        converted, power = [Q(0)], [Q(1)]
        for coefficient in p:
            converted = _add(converted, _scale(power, coefficient))
            power = _multiply(power, [Q(1), Q(-1)])
        need(converted == [Q(11), Q(-18), Q(448), Q(-32)], "V16_POSITIVE_MULTIPLIER_TRANSFORM")
        need(Q(448)-Q(32) == 416 and Q(11)-Q(18)**2/(4*Q(416)) == Q(4495, 416) > 0,
             "V16_MULTIPLIER_POSITIVITY_FAILED")
        bound = {"kind": "POSITIVE_LOWER_BOUND", "value": "4495/416", "variable_range": ["0", "1"],
                 "P_1_minus_w": ["11", "-18", "448", "-32"],
                 "lower_quadratic": ["11", "-18", "416"]}
    else:
        bound = {"kind": "CLOSED_PREFIX_RANGE", "range":
                 {"V12": ["1", "1"], "V13": ["1", "3"], "V17": ["-2", "-1"]}[family]}
    return {
        "kind": "EXACT_ORIGINAL_HARMONIC_FACTOR_RECONSTRUCTION", "family": family,
        "carrier": "R(t)", "source_interval": ["0", "1"],
        "multiplier": {"V12": "1", "V13": "1+2*cos(theta)^2",
                       "V16": "409-782*cos(theta)^2+352*cos(theta)^4+32*cos(theta)^6",
                       "V17": "sin(2*theta)-2"}[family],
        "multiplier_sign": "NEGATIVE" if family == "V17" else "POSITIVE",
        "nonvanishing_proof": bound, "reconstructed_original_coefficients": reconstructed,
        "root_multiplicity_identity": "(M*R)'=M*R' at R=0; M!=0",
    }


def _value(pieces, source_piece, point):
    result = Q(0)
    for channel, entries in pieces.items():
        for harmonic, spans in entries.items():
            quadrant = Q(harmonic) * point
            need(quadrant.denominator == 1, "NON_QUADRANT_ENDPOINT_VALUE")
            # theta=pi*t/2, so h*theta is quadrant h*t.
            trig = ([1, 0, -1, 0] if channel == "cos_splines" else [0, 1, 0, -1])[int(quadrant) % 4]
            intercept, slope = spans[source_piece]
            result += (intercept + slope * point) * trig
    return result


def _sign(value):
    need(value != 0, "PHYSICAL_ZERO_REQUIRES_SEPARATE_EVENT_PROOF")
    return "POSITIVE" if value > 0 else "NEGATIVE"


def _opposite(sign):
    need(sign in ("NEGATIVE", "POSITIVE"), "UNPROVED_PHYSICAL_SIGN")
    return "POSITIVE" if sign == "NEGATIVE" else "NEGATIVE"


def _tail_receipts():
    receipts = {}
    for family, (filename, expected) in PRODUCERS.items():
        module = _module(filename, expected)
        proof = module.contract()  # Only pinned original repository input; no caller data.
        bounded_bytes(proof)
        views = proof["v12_v43_tail_reports"] if family == "V12" else [proof]
        wanted = {cid for cid, data in CASES.items() if data["family"] == family}
        need(len(views) == len(wanted) and {view["case_id"] for view in views} == wanted, "TAIL_SOURCE_SCOPE_DRIFT")
        for view in views:
            cid = view["case_id"]
            need(digest(view) == CASES[cid]["tail_replay_sha256"], "TAIL_REPLAY_RESULT_DRIFT")
            receipts[cid] = view
        pin(HERE / filename, expected)
    return receipts


def _tail_view(cid, receipt):
    case, family = CASES[cid], CASES[cid]["family"]
    need(digest(receipt) == case["tail_replay_sha256"], "TAIL_RECEIPT_UNTRUSTED")
    if family == "V12":
        interval = receipt["physical_source_span"]
        values, signs = receipt["exact_endpoint_values"], receipt["complete_sign_cells"]
        count = receipt["open_physical_root_count"]
        brackets = [] if count == 0 else [receipt["strict_open_source_bracket"]]
        need(count == (1 if case["tail"] else 0), "V12_TAIL_COUNT")
        if count:
            need(receipt["root_multiplicity"] == 1 and exact(receipt["strict_derivative_lower_rational"]) > 0,
                 "V12_TAIL_SIMPLE_ROOT_NOT_PROVED")
    elif family == "V16":
        interval = receipt["original_physical_source_span"]
        proof = receipt["proof"]
        values, signs = proof["source_endpoint_values"], proof["complete_physical_sign_cells"]
        count, brackets = receipt["exact_distinct_open_roots"], [receipt["root_isolation_source_open_interval"]]
        need(count == 1 and proof["single_root_multiplicity"] == 1 and
             exact(proof["strict_crossing_derivative_lower"]) > 0, "V16_TAIL_SIMPLE_ROOT_NOT_PROVED")
    else:
        interval = receipt["original_physical_source_span"]
        proof = receipt["exact_factor_proof"] if family == "V13" else receipt["exact_quadrant_proof"]
        values, signs = proof["physical_source_values_at_endpoints"], receipt["complete_physical_sign_cells"]
        count, brackets = receipt["exact_distinct_roots_open"], []
        need(count == 0, "ROOT_FREE_TAIL_COUNT")
    need(interval == ["1", "2"] and len(signs) == count + 1, "TAIL_INTERVAL_OR_SIGN_COUNT")
    return {"source_case_id": cid, "source_sha256": case["source_sha256"], "source_piece_index": 1,
            "source_interval": interval, "endpoint_values": values, "root_brackets": brackets,
            "root_multiplicities": [1] * count, "maximal_sign_cells": signs,
            "producer": PRODUCERS[family][0], "producer_git_blob": PRODUCERS[family][1],
            "replayed_result_sha256": digest(receipt),
            "proof_scope": "COMPLETE_ORIGINAL_SECOND_CLOSED_SPAN_ONLY"}


def _join_views(prefix, tail, knot_value):
    """Structural composition only; callers here already proved both views.

    This private helper does not establish the mathematical truth of arbitrary
    supplied views. Public entry points always construct prefix evidence and
    replay a pinned tail producer before reaching it.
    """
    need(prefix["source_interval"] == ["0", "1"] and tail["source_interval"] == ["1", "2"], "ORIGINAL_SPAN_PARTITION")
    need(prefix["source_case_id"] == tail["source_case_id"] and
         prefix["source_sha256"] == tail["source_sha256"], "CROSS_SOURCE_VIEW_SUBSTITUTION")
    knot_sign = _sign(knot_value)
    need(exact(prefix["endpoint_values"][1]) == exact(tail["endpoint_values"][0]) == knot_value,
         "KNOT_POINT_VALUE_NOT_IDENTICAL")
    need(prefix["maximal_sign_cells"][-1] == tail["maximal_sign_cells"][0] == knot_sign, "KNOT_SIGN_NOT_IDENTICAL")
    events = []
    for piece_index, view in enumerate((prefix, tail)):
        need(view["source_piece_index"] == piece_index and type(view["source_piece_index"]) is int, "SOURCE_PIECE_INDEX")
        brackets, multiplicities, signs = view["root_brackets"], view["root_multiplicities"], view["maximal_sign_cells"]
        need(len(signs) == len(brackets) + 1 == len(multiplicities) + 1, "INCOMPLETE_VIEW_CARDINALITY")
        lo, hi = [exact(x) for x in view["source_interval"]]
        previous = lo
        need(_sign(exact(view["endpoint_values"][0])) == signs[0] and
             _sign(exact(view["endpoint_values"][1])) == signs[-1], "EXTERIOR_SIGN_NOT_PROVED")
        for index, bracket in enumerate(brackets):
            need(type(bracket) is list and len(bracket) == 2, "ROOT_BRACKET_SHAPE")
            left, right = [exact(x) for x in bracket]
            need(lo <= previous <= left < right <= hi, "ROOT_ORDER_OR_ORIGINAL_INTERVAL")
            need(type(multiplicities[index]) is int and multiplicities[index] == 1 and
                 signs[index + 1] == _opposite(signs[index]), "SIMPLE_CROSSING_SIGN_OR_ORDER")
            events.append({"source_order_index": len(events), "source_piece_index": piece_index,
                           "piece_local_index": index, "strict_source_bracket": list(bracket),
                           "event_kind": "IMPLICIT_UNIQUE_ORIGINAL_SOURCE_ROOT", "multiplicity": 1,
                           "physical_sign_before": signs[index], "physical_sign_after": signs[index + 1],
                           "rational_or_algebraic_root_coordinate_claimed": False})
            previous = right
    signs = prefix["maximal_sign_cells"] + tail["maximal_sign_cells"][1:]
    need(len(signs) == len(events) + 1, "MAXIMAL_SIGN_CELL_MERGE_FAILED")
    return {"complete_for_original_closed_source": True, "source_interval": ["0", "2"],
            "closed_distinct_root_count": len(events), "open_distinct_root_count": len(events),
            "exterior_root_count": 0, "source_knot_root_count": 0, "continuum_zero_component": False,
            "events": events, "maximal_source_sign_cells": signs,
            "source_knot": {"at": "1", "point_value": str(knot_value), "sign": knot_sign,
                            "continuous": True, "is_physical_event": False,
                            "adjacent_equal_sign_cells_merged": True},
            "proof_cuts_are_physical_events": False}


def _source_proof(row, receipt):
    pieces, continuity = check_original(row)
    cid, case = row["id"], CASES[row["id"]]
    carrier = carrier_prefix_proof()
    factor = _factor_identity(pieces, case["family"])
    signs = list(carrier["maximal_sign_cells"])
    if factor["multiplier_sign"] == "NEGATIVE":
        signs = [_opposite(sign) for sign in signs]
    values = [_value(pieces, 0, Q(0)), _value(pieces, 0, Q(1)), _value(pieces, 1, Q(2))]
    need(_value(pieces, 1, Q(1)) == values[1], "SOURCE_KNOT_VALUE_MISMATCH")
    prefix = {"source_case_id": cid, "source_sha256": case["source_sha256"], "source_piece_index": 0,
              "source_interval": ["0", "1"], "endpoint_values": [str(x) for x in values[:2]],
              "root_brackets": carrier["root_brackets"], "root_multiplicities": [1, 1],
              "maximal_sign_cells": signs, "carrier_lemma_sha256": digest(carrier),
              "factor_reconstruction": factor, "proof_scope": "COMPLETE_ORIGINAL_FIRST_CLOSED_SPAN_ONLY"}
    tail = _tail_view(cid, receipt)
    need([exact(x) for x in tail["endpoint_values"]] == values[1:], "TAIL_ENDPOINTS_DO_NOT_MATCH_ORIGINAL_SOURCE")
    physical = _join_views(prefix, tail, values[1])
    need(physical["closed_distinct_root_count"] == (3 if case["tail"] else 2), "EXPECTED_COMPLETE_ROOT_COUNT")
    return {"source_case_id": cid, "original_source_sha256": case["source_sha256"],
            "original_row_sha256": case["original_row_sha256"], "original_source": copy.deepcopy(row["spec"]),
            "historical_observation": copy.deepcopy(row["expected"]), "source_parameter_id": "source-time-t",
            "original_source_piece_edges": ["0", "1", "2"], "phase_turn_law": {"offset": "0", "rate": "1/4"},
            "source_knot_channel_continuity": continuity, "prefix_proof": prefix, "tail_proof": tail,
            "physical_event_proof": physical, "historical_disposition_changed": False,
            "general_v43_route_or_universal_proof_consumer_established": False}


def source_proof(row):
    # Validate caller data before any legacy producer receives even pinned data.
    check_original(row)
    originals = _inputs()
    need(bounded_bytes(row) == bounded_bytes(originals[row["id"]]), "CALLER_ROW_NOT_FROZEN_ORIGINAL")
    return _source_proof(originals[row["id"]], _tail_receipts()[row["id"]])


def expected_report():
    rows, receipts = _inputs(), _tail_receipts()
    cases = [_source_proof(rows[cid], receipts[cid]) for cid in sorted(CASES)]
    result = {
        "schema": SCHEMA, "task": "MC-038", "evidence_class": "DETERMINISTIC_EXACT_SOURCE_BOUND_RESEARCH",
        "recorded_utc": RECORDED_UTC, "source_baseline_main": BASE_MAIN,
        "preregistration_issue_100_comment": PREREGISTRATION_COMMENT,
        "scope": "FIVE_FROZEN_COMPONENT_CARRIER_PREFIXES_AND_ORIGINAL_TAIL_COMPOSITION",
        "dependency_git_blobs": {**PINS, **ROOT_PINS, **{file: sha for file, sha in PRODUCERS.values()}},
        "historical_v54": {"original_source_cases": 121, "route_refusals": 20,
                           "missing_ordered_span_premises": 30, "dispositions_changed": False},
        "carrier_lemma": carrier_prefix_proof(), "source_cases": cases,
        "summary": {"complete_original_source_witnesses": 5,
                    "by_case_closed_root_count": {c["source_case_id"]: c["physical_event_proof"]["closed_distinct_root_count"] for c in cases},
                    "all_physical_roots_simple": True, "all_original_knots_continuous_nonzero": True,
                    "whole_registry_reconciliation_performed": False},
        "gates": {"PB-007-01": "OPEN", "PB-007-02": "OPEN_DEPENDENT", "PB-007-03": "OPEN_PROPAGATED",
                  "PB-007-04": "OPEN_PROPAGATED", "MC-B": "NOT_ESTABLISHED", "MC-1": "NOT_ESTABLISHED",
                  "native_geometry_or_STEP_qualified": False, "production_authorized": False},
    }
    bounded_bytes(result)
    return result


def validate_report(report):
    candidate = bounded_bytes(report)
    need(candidate == bounded_bytes(expected_report()), "REPORT_DOES_NOT_MATCH_FRESH_EXACT_SOURCE_REPLAY")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    report = expected_report()
    if args.write_report:
        REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    else:
        print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
