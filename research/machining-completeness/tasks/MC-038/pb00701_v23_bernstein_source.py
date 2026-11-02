#!/usr/bin/env python3
"""Exact Bernstein/sector proof for one original V23-refused source.

The small positivity checker admits one clamped polynomial span on [0,1],
three specified harmonics, a rational phase sector, and exact nonnegative
Bernstein quotients after removing t**2. The frozen-source wrapper separately
attests the complete original source and its unchanged historical refusal.
This is deterministic-model research, not a new historical route or gate.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from fractions import Fraction as Q
from math import comb, gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CASE_ID = "harvested:verify_pb00701_v52:2250401ce435"
SOURCE_SHA256 = "4a3ee3f47b9347429c13830abef382301c7963b0af518f0977390c2d3ffba040"
OWNER = "PB00701_V23_EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR"
REASON = "NONCONSTANT_AMPLITUDE_PHASE_DEPENDENT_ANCHOR_NOT_CERTIFIED"
SCHEMA = "radicadsac-mc038-v23-bernstein-source/1.0"
REPORT = HERE / "pb00701-v23-bernstein-source-witness.json"
PINS = {
    "pb00701-finite-owner-corpus-v54.json": "5841c331579489b25caef38cd412bdbf286f9134",
    "pb00701-finite-owner-inventory-v54.json": "8649c20ab77e199f9c3fa351b8b6742218f27abb",
    "pb00701-finite-owner-coverage-v54.json": "600ba29786f50397f29fd435fc5e2c57076088f9",
    "verify_pb00701_post_v54_frontier.py": "12c6efeb667a954ffc5a7e27849ae815d466580a",
}
DOMAIN = ROOT / "research/machining-completeness/tasks/MC-002/domain-contract-v1.json"
AUTHORITY = ROOT / "handoffs/current-authority.json"
DOMAIN_BLOB = "23de82f5240a72509f7afe4acd5948b65bc4ff13"
AUTHORITY_BLOB = "fa0233323a0804d8a5d3eb7cd892a274a6173fab"
MAX_JSON_BYTES = 65536
MAX_DEPENDENCY_BYTES = 1048576
MAX_DEGREE = 12
RATIONAL_TOKEN = re.compile(r"(-?)(0|[1-9][0-9]{0,77})(?:/([1-9][0-9]{0,77}))?")


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def canonical(value):
    """Bound untrusted JSON, including cycles, before hashing or comparison."""
    active = set()
    stack = [(value, 0, False)]
    nodes = 0
    while stack:
        obj, depth, leaving = stack.pop()
        if leaving:
            active.remove(id(obj))
            continue
        nodes += 1
        need(nodes <= 4096 and depth <= 16,
             "RESOURCE_REFUSAL: JSON node/depth budget")
        if type(obj) in (dict, list):
            need(id(obj) not in active and len(obj) <= 128,
                 "RESOURCE_REFUSAL: JSON cycle/container budget")
            active.add(id(obj))
            stack.append((obj, depth, True))
            if type(obj) is dict:
                for key, child in obj.items():
                    need(type(key) is str and len(key) <= 256,
                         "RESOURCE_REFUSAL: JSON key")
                    stack.append((child, depth + 1, False))
            else:
                stack.extend((child, depth + 1, False) for child in obj)
        elif type(obj) is str:
            need(len(obj) <= 4096, "RESOURCE_REFUSAL: JSON string")
        elif type(obj) is int:
            need(obj.bit_length() <= 256, "RESOURCE_REFUSAL: JSON integer")
        else:
            need(obj is None or type(obj) is bool,
                 "SEMANTIC_BLOCKER: non-JSON or binary float scalar")
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                     allow_nan=False).encode("utf-8")
    need(len(raw) <= MAX_JSON_BYTES, "RESOURCE_REFUSAL: JSON byte budget")
    return raw


def exact(value):
    need(type(value) is str, "SEMANTIC_BLOCKER: rational must be a string")
    need(len(value) <= 160, "RESOURCE_REFUSAL: rational string")
    # Fraction accepts decimal/exponent strings. Lexically exclude them BEFORE
    # construction so a short exponent cannot request an enormous integer.
    token = RATIONAL_TOKEN.fullmatch(value)
    need(token is not None, "SEMANTIC_BLOCKER: noncanonical ASCII rational token")
    sign, numerator_token, denominator_token = token.groups()
    need(not (sign and numerator_token == "0"),
         "SEMANTIC_BLOCKER: noncanonical negative zero")
    numerator = int(numerator_token)
    if sign:
        numerator = -numerator
    denominator = int(denominator_token) if denominator_token is not None else 1
    need(max(numerator.bit_length(), denominator.bit_length()) <= 256,
         "RESOURCE_REFUSAL: rational bit budget")
    need(denominator_token is None or denominator > 1,
         "SEMANTIC_BLOCKER: noncanonical denominator one")
    need(gcd(abs(numerator), denominator) == 1,
         "SEMANTIC_BLOCKER: unreduced rational")
    return Q(numerator, denominator)


def blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def pin(path, digest):
    need(path.is_file(), "SEMANTIC_BLOCKER: pinned source missing: " + str(path))
    need(path.stat().st_size <= MAX_DEPENDENCY_BYTES,
         "RESOURCE_REFUSAL: pinned dependency file size")
    need(blob(path) == digest,
         "SEMANTIC_BLOCKER: pinned source drift: " + str(path))


def no_duplicate_keys(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, "SEMANTIC_BLOCKER: duplicate JSON key")
        out[key] = value
    return out


def read_report(path=REPORT):
    need(path.stat().st_size <= MAX_JSON_BYTES,
         "RESOURCE_REFUSAL: report file size")
    try:
        value = json.loads(path.read_text(encoding="utf-8"),
                           object_pairs_hook=no_duplicate_keys)
    except (RecursionError, json.JSONDecodeError) as exc:
        raise ValueError("SEMANTIC_BLOCKER: invalid report JSON") from exc
    canonical(value)
    return value


def power_coefficients(controls):
    """Independent exact expansion of sum c_i C(n,i)t^i(1-t)^(n-i)."""
    n = len(controls) - 1
    out = [Q(0)] * (n + 1)
    for i, c in enumerate(controls):
        for j in range(n - i + 1):
            out[i + j] += c * comb(n, i) * comb(n - i, j) * (-1) ** j
    return out


def factor_t_squared(controls):
    """Construct and independently check the exact Bernstein quotient by t²."""
    n = len(controls) - 1
    need(2 <= n <= MAX_DEGREE and all(type(x) is Q for x in controls),
         "SEMANTIC_BLOCKER: bounded rational Bernstein controls required")
    need(controls[0] == controls[1] == 0,
         "SEMANTIC_BLOCKER: amplitude lacks a double boundary factor")
    quotient = [controls[i] * Q(n * (n - 1), i * (i - 1))
                for i in range(2, n + 1)]
    need(power_coefficients(controls) ==
         [Q(0), Q(0)] + power_coefficients(quotient),
         "SEMANTIC_BLOCKER: Bernstein factor identity failed")
    return quotient


def clamped_controls(spline):
    need(type(spline) is dict and set(spline) == {"degree", "knots", "controls"},
         "SEMANTIC_BLOCKER: unknown spline fields")
    n = spline["degree"]
    need(type(n) is int, "SEMANTIC_BLOCKER: integer spline degree required")
    need(2 <= n <= MAX_DEGREE, "RESOURCE_REFUSAL: degree outside bounded proof")
    need(type(spline["knots"]) is list and
         spline["knots"] == ["0"] * (n + 1) + ["1"] * (n + 1),
         "SEMANTIC_BLOCKER: not one fully clamped [0,1] source span")
    need(type(spline["controls"]) is list and len(spline["controls"]) == n + 1,
         "SEMANTIC_BLOCKER: wrong source control count")
    return [exact(x) for x in spline["controls"]]


def prove_sector_source(spec):
    """Conditional complete proof for a narrowly bounded Bernstein grammar.

    F=A0+A1*cos(theta)+B2*sin(2*theta), theta/(2*pi)=1/4+r*t,
    -1/24<=r<=0, on the original t interval [0,1]. Each amplitude is
    t² times a nonnegative Bernstein polynomial; A0's quotient controls
    are strictly positive. Convexity of the Bernstein basis proves
    F(t)>=min(A0_quotient)*t², hence the full zero set is {0}.

    At t=0 the nonconstant trig factors vanish, while every amplitude
    and its first derivative vanish. Thus F''(0)=2*A0_quotient(0)>0.
    No numerical trig evaluation, root sampling or search cap proves truth.
    """
    canonical(spec)
    need(type(spec) is dict and set(spec) == {
        "grammar", "source_parameter_id", "parameter_lo", "parameter_hi",
        "phase_turn_offset", "phase_turn_rate", "cos_splines", "sin_splines"},
        "SEMANTIC_BLOCKER: unsupported source fields")
    need(spec["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE" and
         type(spec["source_parameter_id"]) is str and bool(spec["source_parameter_id"]),
         "SEMANTIC_BLOCKER: unsupported source grammar/identity")
    lo, hi, offset, rate = [exact(spec[k]) for k in
                            ("parameter_lo", "parameter_hi",
                             "phase_turn_offset", "phase_turn_rate")]
    need((lo, hi) == (Q(0), Q(1)), "SEMANTIC_BLOCKER: source interval is not [0,1]")
    need(offset == Q(1, 4) and Q(-1, 24) <= rate <= 0,
         "SEMANTIC_BLOCKER: phase leaves the nonnegative quadrant proof")
    need(type(spec["cos_splines"]) is dict and set(spec["cos_splines"]) == {"0", "1"}
         and type(spec["sin_splines"]) is dict and set(spec["sin_splines"]) == {"2"},
         "SEMANTIC_BLOCKER: unsupported harmonic or omitted residual")
    channels = {}
    for name, key, harmonic in (("C0", "cos_splines", "0"),
                                ("C1", "cos_splines", "1"),
                                ("S2", "sin_splines", "2")):
        controls = clamped_controls(spec[key][harmonic])
        quotient = factor_t_squared(controls)
        need(all(q > 0 for q in quotient) if name == "C0" else
             all(q >= 0 for q in quotient),
             "SEMANTIC_BLOCKER: nonnegative Bernstein sector certificate unavailable")
        channels[name] = {
            "degree": len(controls) - 1,
            "original_controls": [str(x) for x in controls],
            "t_squared_quotient_degree": len(quotient) - 1,
            "t_squared_quotient_controls": [str(x) for x in quotient],
            "quotient_lower_bound": str(min(quotient)),
        }
    lower = exact(channels["C0"]["quotient_lower_bound"])
    derivative = 2 * exact(channels["C0"]["t_squared_quotient_controls"][0])
    need(lower > 0 and derivative > 0, "SEMANTIC_BLOCKER: strict proof lost")
    return {
        "kind": "SINGLE_CLAMPED_BERNSTEIN_SECTOR_POSITIVITY",
        "source_parameter_id": spec["source_parameter_id"],
        "source_interval": ["0", "1"],
        "phase_turn_interval": [str(offset + rate), str(offset)],
        "cosine_harmonic_1_nonnegative": True,
        "sine_harmonic_2_nonnegative": True,
        "channels": channels,
        "strict_lower_bound": {"coefficient": str(lower), "factor": "t^2",
                               "valid_on_closed_interval": ["0", "1"]},
        "left_endpoint_value": "0",
        "left_endpoint_first_derivative": "0",
        "left_endpoint_second_derivative": str(derivative),
        "physical_event_proof": {
            "closed_distinct_root_count": 1,
            "open_distinct_root_count": 0,
            "interior_source_knots": [],
            "events": [{"coordinate": {"kind": "RATIONAL", "value": "0"},
                        "location": "SOURCE_EXTERIOR_LEFT_ENDPOINT",
                        "analytic_order": 2,
                        "left_sign": None,
                        "right_sign": "POSITIVE"}],
            "sign_cells": [{"interval": ["0", "1"], "left_closed": False,
                            "right_closed": True, "sign": "POSITIVE"}],
            "continuum_zero_component": False,
            "complete_for_original_closed_source": True,
        },
    }


def historical_observation():
    return {"id": CASE_ID, "observed": {"status": "BLOCKED", "spans": [
        [OWNER, "BLOCKED", REASON]]}, "v54_disposition": "BLOCKED"}


def check_original(row):
    canonical(row)
    need(type(row) is dict and set(row) == {"id", "origin", "kind", "spec", "expected"},
         "SEMANTIC_BLOCKER: unknown original row fields")
    need(row["id"] == CASE_ID and row["origin"] == "verify_pb00701_v52" and
         row["kind"] == "HARVESTED", "SEMANTIC_BLOCKER: original source origin drift")
    need(canonical(row["expected"]) == canonical(historical_observation()),
         "SEMANTIC_BLOCKER: historical owner/refusal drift")
    need(hashlib.sha256(canonical(row["spec"])).hexdigest() == SOURCE_SHA256,
         "SEMANTIC_BLOCKER: original source SHA-256 drift")
    proof = prove_sector_source(row["spec"])
    need(proof["source_parameter_id"] == "v52-original-source" and
         proof["phase_turn_interval"] == ["5/24", "1/4"] and
         proof["left_endpoint_second_derivative"] == "1/36" and
         proof["strict_lower_bound"]["coefficient"] == "49/34992",
         "SEMANTIC_BLOCKER: frozen-source exact result changed")
    c1 = [exact(x) for x in proof["channels"]["C1"]["original_controls"]]
    s2 = [exact(x) for x in proof["channels"]["S2"]["original_controls"]]
    need(len(c1) == len(s2) and all(a == 2*b for a, b in zip(c1, s2)),
         "SEMANTIC_BLOCKER: original S2=C1/2 coefficient identity lost")
    return proof


def load_original():
    for name, digest in PINS.items():
        pin(HERE / name, digest)
    pin(DOMAIN, DOMAIN_BLOB)
    pin(AUTHORITY, AUTHORITY_BLOB)
    path = HERE / "verify_pb00701_post_v54_frontier.py"
    spec = importlib.util.spec_from_file_location("v23_pinned_frontier", path)
    need(spec is not None and spec.loader is not None, "pinned audit import failed")
    auditor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(auditor)
    corpus, inventory, boundary = auditor.inputs()
    census = auditor.audit(corpus, inventory, boundary)
    need(census["cases"] == 121 and census["v54_dispositions"]["BLOCKED"] == 20 and
         census["v54_dispositions"][
             "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"] == 30,
         "SEMANTIC_BLOCKER: frozen historical denominator drift")
    matches = [row for row in corpus["cases"] if row["id"] == CASE_ID]
    need(len(matches) == 1, "SEMANTIC_BLOCKER: source missing or duplicated")
    need(sum(row["expected"]["observed"]["spans"] == [[OWNER, "BLOCKED", REASON]]
             for row in corpus["cases"]) == 1,
         "SEMANTIC_BLOCKER: V23 historical refusal denominator drift")
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    auth = json.loads(AUTHORITY.read_text(encoding="utf-8"))
    need(len(domain["coverage_rule"]["required_operation_ids"]) == 26,
         "SEMANTIC_BLOCKER: 26-operation domain changed")
    need(auth["capability_status"] == "NOT_ESTABLISHED" and
         auth["production_authorized"] is False,
         "SEMANTIC_BLOCKER: current programme authority changed")
    check_original(matches[0])
    return matches[0]


def expected_report():
    row = load_original()
    proof = check_original(row)
    return {
        "schema": SCHEMA,
        "evidence_class": "DETERMINISTIC_MODEL",
        "case_id": CASE_ID,
        "original_source_sha256": SOURCE_SHA256,
        "original_source": row["spec"],
        "historical_observation": row["expected"],
        "dependencies": {"MC038_git_blobs": dict(PINS),
                         "domain_git_blob": DOMAIN_BLOB,
                         "authority_git_blob": AUTHORITY_BLOB},
        "source_specific_proof": proof,
        "frozen_v54_census": {"original_sources": 121, "route_refusals": 20,
                              "missing_ordered_premises": 30,
                              "historical_dispositions_modified": False},
        "scope": {"complete_source_specific_mathematical_witness": True,
                  "selected_source_ids": [CASE_ID],
                  "exhaustive_post_v54_census": False,
                  "historical_V23_route_repaired": False,
                  "general_analytic_event_solver": False,
                  "PB00701_closed": False, "MC_B": "NOT_ESTABLISHED",
                  "MC_1": "NOT_ESTABLISHED", "production_authorized": False,
                  "native_material_topology_or_STEP_qualified": False,
                  "protected_operation_count": 26},
    }


def validate_report(report):
    actual = canonical(report)
    need(actual == canonical(expected_report()),
         "SEMANTIC_BLOCKER: source-bound mathematical report mismatch")
    return True
