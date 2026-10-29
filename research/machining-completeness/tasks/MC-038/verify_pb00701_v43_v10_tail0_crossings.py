#!/usr/bin/env python3
"""Exact source-bound four-crossing probe for the frozen V10 tail0 V43 refusal.

Deterministic research only: not a V43 route, general zero-isolation theorem,
whole-source composition, or MC-B/MC-1/native/B-rep/STEP qualification.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research/machining-completeness/tasks/MC-038"
CORPUS = TASK / "pb00701-finite-owner-corpus-v54.json"
PREDECESSOR = TASK / "verify_pb00701_v43_refusal_cone.py"
AUTHORITY = ROOT / "handoffs/current-authority.json"
PROGRAMME = ROOT / "research/machining-completeness/programme-v1.json"
DOMAIN = ROOT / "research/machining-completeness/tasks/MC-002/domain-contract-v1.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
PREDECESSOR_BLOB = "2a8079ee2cf012bc2a12794c4c5ff19ebd760007"
CASE_ID = "composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail0"
V10_OWNER = "PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO"
V43_OWNER = "PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF"
REFUSAL = "CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED"
SCHEMA = "radicadsac-pb00701-v43-v10-tail0-four-crossings/1.0"

EXPECTED_SPEC = {
    "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
    "source_parameter_id": "source-time-t",
    "parameter_lo": "0",
    "parameter_hi": "2",
    "phase_turn_offset": "-1/2",
    "phase_turn_rate": "2",
    "cos_splines": {
        "0": {
            "degree": 0,
            "knots": ["0", "1", "2"],
            "controls": ["0", "0"],
        },
        "1": {
            "degree": 0,
            "knots": ["0", "1", "2"],
            "controls": ["1", "1"],
        },
    },
    "sin_splines": {
        "1": {
            "degree": 1,
            "knots": ["0", "0", "1", "1", "2", "2"],
            "controls": ["1/2", "-1/2", "-1/2", "-1/2"],
        },
    },
}
EXPECTED_HISTORICAL = {
    "id": CASE_ID,
    "observed": {
        "status": "BLOCKED",
        "spans": [
            [V10_OWNER, "CERTIFIED", None],
            [V43_OWNER, "BLOCKED", REFUSAL],
        ],
    },
    "v54_disposition": "BLOCKED",
}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def blob_sha(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_lowerer():
    require(blob_sha(PREDECESSOR) == PREDECESSOR_BLOB,
            "accepted source B-spline helper Git blob changed")
    spec = importlib.util.spec_from_file_location(
        "v43_source_bound_linear_lowerer", PREDECESSOR)
    module = importlib.util.module_from_spec(spec)
    require(spec.loader is not None, "source-lowering helper unavailable")
    spec.loader.exec_module(module)
    require(blob_sha(PREDECESSOR) == PREDECESSOR_BLOB,
            "accepted lowerer drifted during import")
    return module


LOWERER = load_lowerer()


def frozen_case(corpus):
    require(corpus.get("schema") ==
            "radicadsac-pb00701-finite-owner-corpus/54.0",
            "historical v54 schema changed")
    rows = corpus.get("cases")
    require(isinstance(rows, list) and len(rows) == 121 and
            len({x["id"] for x in rows}) == 121,
            "historical v54 source denominator changed")
    refusals = [
        row for row in rows if
        [V43_OWNER, "BLOCKED", REFUSAL] in
        row["expected"]["observed"]["spans"]
    ]
    require(len(refusals) == 11 and
            sum(x["kind"] == "HARVESTED" for x in refusals) == 1 and
            sum(x["kind"] == "COMPOSITE_TAIL" for x in refusals) == 10,
            "historical V43 refusal denominator changed")
    selected = [row for row in rows if row["id"] == CASE_ID]
    require(len(selected) == 1, "selected V10 tail0 absent or duplicated")
    case = selected[0]
    require(case.get("origin") == "verify_pb00701_v10" and
            case.get("kind") == "COMPOSITE_TAIL",
            "original V10 tail0 provenance changed")
    require(case.get("spec") == EXPECTED_SPEC,
            "original source/knot/control/phase identity changed")
    require(case.get("expected") == EXPECTED_HISTORICAL,
            "historical V10/V43 ownership or refusal was relabelled")
    return case


def exact_source_channels(source):
    """Check the physical source, including original knot continuity."""
    first, second = (Q(0), Q(1)), (Q(1), Q(2))
    channel_pairs = (
        ("cos_splines", "0"),
        ("cos_splines", "1"),
        ("sin_splines", "1"),
    )
    pieces = {}
    for channel, harmonic in channel_pairs:
        before = LOWERER.linear_piece(source, channel, harmonic, *first)
        after = LOWERER.linear_piece(source, channel, harmonic, *second)
        require(LOWERER.evaluate_poly(before, Q(1)) ==
                LOWERER.evaluate_poly(after, Q(1)),
                "source is discontinuous at original physical knot")
        pieces[channel, harmonic] = (before, after)
    require(set(source["cos_splines"]) == {"0", "1"} and
            set(source["sin_splines"]) == {"1"},
            "unaccounted original harmonic")
    require(pieces["cos_splines", "0"] ==
            ((Q(0), Q(0)), (Q(0), Q(0))),
            "V10 tail0 harmonic zero differs from C0(s)=0")
    require(pieces["cos_splines", "1"] ==
            ((Q(1), Q(0)), (Q(1), Q(0))),
            "V10 tail0 cosine differs from C1(s)=1")
    require(pieces["sin_splines", "1"] ==
            ((Q(1, 2), Q(-1)), (Q(-1, 2), Q(0))),
            "V10 tail0 sine differs from S1(s)=-1/2 on second span")
    return pieces


def phase_turn(source, s):
    return (LOWERER.rational(source["phase_turn_offset"]) +
            LOWERER.rational(source["phase_turn_rate"]) * s)


def analyze(corpus):
    case = frozen_case(corpus)
    source = case["spec"]
    exact_source_channels(source)

    # On the original V43-refused second physical span [1,2]:
    #   F(s) = cos(theta(s)) - (1/2) sin(theta(s)),
    #   theta(s) = 2*pi*(-1/2+2*s) = 4*pi*s-pi.
    # Quarter-source points are exactly half-cycle boundaries in theta.
    quarter_points = [Q(1) + Q(i, 4) for i in range(5)]
    turns = [phase_turn(source, point) for point in quarter_points]
    require(turns == [Q(3, 2), Q(2), Q(5, 2), Q(3), Q(7, 2)],
            "half-turn phase offset or quarter-point source mapping changed")
    theta_pi = [2 * x for x in turns]
    require(theta_pi == [Q(3), Q(4), Q(5), Q(6), Q(7)],
            "exact half-cycle chart changed")
    # At integer multiples of pi: sin=0 and cos=(-1)^n.
    endpoint_values = [Q(-1) if int(x) % 2 else Q(1) for x in theta_pi]
    require(endpoint_values == [Q(-1), Q(1), Q(-1), Q(1), Q(-1)],
            "source half-cycle endpoint signs changed")

    # With alpha=atan(2),  pi/4 < alpha < pi/2, because tan is strictly
    # increasing from 1 to +infinity over [pi/4, pi/2). Every zero has
    # theta=alpha+n*pi (tan(theta)=2). Exactly n=3,4,5,6 lie in the
    # original open theta interval (3*pi,7*pi). Each is simple:
    # cos(theta)=(1/2)sin(theta) implies
    # F'(s)=4*pi*(-sin(theta)-(1/2)cos(theta))
    #      =-5*pi*sin(theta) != 0.
    # The sign of sin at theta=3*pi+alpha+k*pi is (-1)^(3+k),
    # giving alternating upward/downward source crossings.
    roots = []
    for i in range(4):
        source_left = quarter_points[i]
        source_right = quarter_points[i + 1]
        bound_lo = source_left + Q(1, 16)
        bound_hi = source_left + Q(1, 8)
        require(source_left < bound_lo < bound_hi < source_right,
                "implicit root bracket escaped its half-cycle")
        left_sign = "NEGATIVE" if i % 2 == 0 else "POSITIVE"
        right_sign = "POSITIVE" if i % 2 == 0 else "NEGATIVE"
        require((endpoint_values[i] < 0) == (left_sign == "NEGATIVE") and
                (endpoint_values[i + 1] > 0) == (right_sign == "POSITIVE"),
                "crossing directions disagree with source endpoint signs")
        roots.append({
            "source_order_index": i,
            "source_identity": "1+k/4+atan(2)/(4*pi), k=source_order_index",
            "tan_half_angle_identity": "theta=3*pi+atan(2)+k*pi",
            "strict_source_bracket": [str(bound_lo), str(bound_hi)],
            "half_cycle_open_source_interval": [
                str(source_left), str(source_right)],
            "multiplicity": 1,
            "event_kind": "SIMPLE_CROSSING",
            "physical_sign_before": left_sign,
            "physical_sign_after": right_sign,
            "derivative_at_root_nonzero": True,
            "algebraic_or_rational_source_coordinate_claimed": False,
        })
    require([x["strict_source_bracket"] for x in roots] == [
        ["17/16", "9/8"], ["21/16", "11/8"],
        ["25/16", "13/8"], ["29/16", "15/8"]],
        "four exact rational source brackets changed")

    return {
        "schema": SCHEMA,
        "evidence_class": "DETERMINISTIC_EXACT_SOURCE_BOUND_CASE_PROOF_ONLY",
        "source_case": CASE_ID,
        "original_source_parameter_id": source["source_parameter_id"],
        "historical_v43_refusals": 11,
        "historical_v54_disposition": "BLOCKED",
        "physical_source_span": ["1", "2"],
        "quarter_points": [str(p) for p in quarter_points],
        "phase_turns": [str(t) for t in turns],
        "exact_endpoint_values": [str(x) for x in endpoint_values],
        "exact_open_roots": 4,
        "ordered_open_roots": roots,
        "all_roots_simple_crossings": True,
        "complete_sign_cells": [
            "NEGATIVE", "POSITIVE", "NEGATIVE", "POSITIVE", "NEGATIVE"],
        "first_span_historical_certification_unchanged": True,
        "whole_source_composition_claimed": False,
        "general_v43_route_or_ordered_event_theorem_claimed": False,
        "v54_dispositions_changed": False,
        "mc_b_or_mc1_or_native_claimed": False,
    }


def validate_report(report, corpus):
    """Source-specific replay; NOT an independent general root verifier."""
    require(report == analyze(corpus),
            "submitted V10 tail0 research report differs from exact source replay")
    return True


def contract():
    require(blob_sha(CORPUS) == CORPUS_BLOB, "frozen v54 corpus drifted")
    require(blob_sha(PREDECESSOR) == PREDECESSOR_BLOB,
            "reviewed source lowerer drifted")
    authority = load_json(AUTHORITY)
    programme = load_json(PROGRAMME)
    domain = load_json(DOMAIN)
    require(authority["programme"] == "MC-1" and
            authority["capability_status"] == "NOT_ESTABLISHED" and
            authority["production_authorized"] is False,
            "MC-1/production authority incorrectly promoted")
    require(programme["capability_status"] == "NOT_ESTABLISHED" and
            programme["production_authorized"] is False and
            any(g["id"] == "MC-B" and g["state"] == "NOT_ESTABLISHED"
                for g in programme["gates"]),
            "MC-B programme capability incorrectly promoted")
    require(len(domain["coverage_rule"]["required_operation_ids"]) == 26,
            "26-operation machining domain changed")
    return analyze(load_json(CORPUS))


def self_test():
    corpus = load_json(CORPUS)
    report = analyze(corpus)
    validate_report(report, corpus)
    require(report["exact_open_roots"] == 4 and
            report["exact_endpoint_values"] == ["-1", "1", "-1", "1", "-1"] and
            report["all_roots_simple_crossings"] is True,
            "V10 tail0 four-crossing proof result changed")

    def reject_source(mutator, label):
        forged = copy.deepcopy(corpus)
        case = next(x for x in forged["cases"] if x["id"] == CASE_ID)
        mutator(case)
        try:
            analyze(forged)
        except (ValueError, KeyError, IndexError, TypeError):
            return
        raise AssertionError("altered original source accepted: " + label)

    reject_source(lambda x: x["spec"].__setitem__("phase_turn_offset", "0"),
                  "half-turn phase offset")
    reject_source(lambda x: x["spec"].__setitem__("phase_turn_rate", "1"),
                  "phase rate")
    reject_source(lambda x: x["spec"].__setitem__("source_parameter_id", "other"),
                  "source parameter")
    reject_source(lambda x: x["spec"]["cos_splines"]["0"]["controls"].__setitem__(1, "100"),
                  "harmonic zero ramp")
    reject_source(lambda x: x["spec"]["cos_splines"]["1"]["controls"].__setitem__(1, "-1"),
                  "first-harmonic cosine")
    reject_source(lambda x: x["spec"]["sin_splines"]["1"]["controls"].__setitem__(2, "1/2"),
                  "second-span sine coefficient")
    reject_source(lambda x: x["spec"]["sin_splines"]["1"]["controls"].__setitem__(1, "1/2"),
                  "first-span sine and knot continuity")
    reject_source(lambda x: x["spec"]["sin_splines"]["1"]["knots"].__setitem__(2, "3/4"),
                  "original source knot")
    reject_source(lambda x: x["spec"]["cos_splines"].__setitem__("2", {
        "degree": 0, "knots": ["0", "1", "2"], "controls": ["1", "1"]}),
        "unaccounted harmonic")
    reject_source(lambda x: x.__setitem__("origin", "verify_pb00701_v11"),
                  "historical origin")
    reject_source(lambda x: x["expected"]["observed"]["spans"][0].__setitem__(
        0, V43_OWNER), "first-span historical V10 owner")
    reject_source(lambda x: x["expected"]["observed"]["spans"][1].__setitem__(
        1, "CERTIFIED"), "second-span historical V43 refusal")
    reject_source(lambda x: x["expected"].__setitem__(
        "v54_disposition", "CERTIFIED"), "frozen v54 disposition")
    reject_source(lambda x: x["spec"]["sin_splines"]["1"]["controls"].__setitem__(
        3, "-0.5"), "unreviewed decimal source notation")

    def reject_report(mutator, label):
        changed = copy.deepcopy(report)
        mutator(changed)
        try:
            validate_report(changed, corpus)
        except ValueError:
            return
        raise AssertionError("forged source-specific report accepted: " + label)

    reject_report(lambda x: x.__setitem__("exact_open_roots", 3),
                  "missing crossing count")
    reject_report(lambda x: x["ordered_open_roots"].pop(2),
                  "omitted root")
    reject_report(lambda x: x["ordered_open_roots"][1].__setitem__(
        "source_order_index", 0), "duplicate root index")
    reject_report(lambda x: x["ordered_open_roots"][0].__setitem__(
        "strict_source_bracket", ["1", "5/4"]), "widened bracket")
    reject_report(lambda x: x["ordered_open_roots"][0].__setitem__(
        "physical_sign_before", "POSITIVE"), "crossing sign")
    reject_report(lambda x: x.__setitem__(
        "general_v43_route_or_ordered_event_theorem_claimed", True),
        "general V43 owner promotion")
    print("PASS: original V10 tail0 source/knot/phase and 11 historical V43 refusals")
    print("PASS: four exact simple crossings and disjoint rational source brackets")
    print("PASS: source/owner/phase/bracket/root-order/sign/nonpromotion mutations")
    print(json.dumps(report, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        print("PASS: pinned corpus/lowerer/domain/programme and V10 tail0 proof")
        print(json.dumps(contract(), sort_keys=True))
    if args.self_test:
        self_test()


if __name__ == "__main__":
    main()
