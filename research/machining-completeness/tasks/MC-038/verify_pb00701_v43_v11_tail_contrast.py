#!/usr/bin/env python3
"""Frozen V11 V43-refused pair: exact original-source root/sign contrast.

Research only. Does not certify a general V43 route, whole-source composition,
MC-B/MC-1, native geometry, B-rep, STEP or a production handoff.
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
LOWERER_SOURCE = TASK / "verify_pb00701_v43_refusal_cone.py"
AUTHORITY = ROOT / "handoffs/current-authority.json"
PROGRAMME = ROOT / "research/machining-completeness/programme-v1.json"
DOMAIN = ROOT / "research/machining-completeness/tasks/MC-002/domain-contract-v1.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
LOWERER_BLOB = "2a8079ee2cf012bc2a12794c4c5ff19ebd760007"
CASE_PREFIX = "composite:PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO:"
FIRST_OWNER = "PB00701_V11_EXACT_PHASE_DOMINANCE_SINGLE_HARMONIC_RATIO"
SECOND_OWNER = "PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF"
REFUSAL = "CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED"
SCHEMA = "radicadsac-pb00701-v43-v11-tail-contrast/1.0"


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def blob_sha(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_lowerer():
    require(blob_sha(LOWERER_SOURCE) == LOWERER_BLOB,
            "accepted source-lowering helper drifted")
    spec = importlib.util.spec_from_file_location(
        "v43_v11_accepted_linear_source_lowerer", LOWERER_SOURCE)
    module = importlib.util.module_from_spec(spec)
    require(spec.loader is not None, "source helper unavailable")
    spec.loader.exec_module(module)
    require(blob_sha(LOWERER_SOURCE) == LOWERER_BLOB,
            "source helper drifted during import")
    return module


LOWERER = load_lowerer()


def expected_spec(tail):
    require(tail in (0, 100), "unknown V11 tail")
    c0 = ({"degree": 0, "knots": ["0", "1", "2"],
           "controls": ["0", "0"]} if tail == 0 else
          {"degree": 1, "knots": ["0", "0", "1", "1", "2", "2"],
           "controls": ["0", "0", "0", "100"]})
    return {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "source_parameter_id": "source-time-t",
        "parameter_lo": "0", "parameter_hi": "2",
        "phase_turn_offset": "0", "phase_turn_rate": "2",
        "cos_splines": {
            "0": c0,
            "1": {
                "degree": 2,
                "knots": ["0", "0", "0", "1", "1", "1", "2", "2", "2"],
                "controls": ["1/8", "-3/8", "1/8", "1/8", "1/8", "1/8"],
            },
        },
        "sin_splines": {
            "1": {"degree": 0, "knots": ["0", "1", "2"],
                  "controls": ["1", "1"]},
        },
    }


def frozen_cases(corpus):
    require(corpus.get("schema") ==
            "radicadsac-pb00701-finite-owner-corpus/54.0",
            "historical v54 corpus schema changed")
    rows = corpus.get("cases")
    require(isinstance(rows, list) and len(rows) == 121 and
            len({x["id"] for x in rows}) == 121,
            "frozen case denominator/identities changed")
    refused = [x for x in rows if
               [SECOND_OWNER, "BLOCKED", REFUSAL]
               in x["expected"]["observed"]["spans"]]
    require(len(refused) == 11 and
            sum(x["kind"] == "HARVESTED" for x in refused) == 1 and
            sum(x["kind"] == "COMPOSITE_TAIL" for x in refused) == 10,
            "historical V43 refusals changed")
    selected = []
    for tail in (0, 100):
        identifier = CASE_PREFIX + "tail" + str(tail)
        matching = [x for x in rows if x["id"] == identifier]
        require(len(matching) == 1, "V11 original-source case absent or duplicated")
        case = matching[0]
        require(case.get("kind") == "COMPOSITE_TAIL" and
                case.get("origin") == "verify_pb00701_v11",
                "V11 original fixture provenance changed")
        require(case.get("spec") == expected_spec(tail),
                "V11 source controls/knot/phase/parameter identity changed")
        require(case.get("expected") == {
            "id": identifier,
            "observed": {"status": "BLOCKED", "spans": [
                [FIRST_OWNER, "CERTIFIED", None],
                [SECOND_OWNER, "BLOCKED", REFUSAL],
            ]},
            "v54_disposition": "BLOCKED",
        }, "V11/V43 historical owner/refusal/disposition relabelled")
        selected.append((tail, case))
    return selected


def quadratic_bezier_pieces(source):
    """Independent exact lowering for the pinned two-piece clamped degree-2 C1.

    Each piece has local Bernstein controls (b0,b1,b2). Expand in local
    u=s-left using b0*(1-u)^2 + 2*b1*u*(1-u) + b2*u^2.
    This is intentionally not the historical V11 selecting route.
    """
    entry = source["cos_splines"]["1"]
    require(set(entry) == {"degree", "knots", "controls"} and
            type(entry["degree"]) is int and entry["degree"] == 2,
            "unreviewed V11 quadratic spline")
    knots = [LOWERER.rational(x) for x in entry["knots"]]
    controls = [LOWERER.rational(x) for x in entry["controls"]]
    require(knots == [Q(0)] * 3 + [Q(1)] * 3 + [Q(2)] * 3 and
            len(controls) == 6, "quadratic physical-knot/control structure changed")
    local = []
    for i in (0, 1):
        a, b, c = controls[3*i:3*i+3]
        local.append((a, 2 * (b-a), a-2*b+c))
    require(local == [
        (Q(1, 8), Q(-1), Q(1)),
        (Q(1, 8), Q(0), Q(0)),
    ], "original V11 exact Bernstein polynomial differs")
    left_at_knot = sum(local[0])
    right_at_knot = local[1][0]
    require(left_at_knot == right_at_knot == Q(1, 8),
            "original degree-2 source knot is discontinuous")
    return local


def exact_source_channels(source, tail):
    require(set(source["cos_splines"]) == {"0", "1"} and
            set(source["sin_splines"]) == {"1"},
            "unaccounted source harmonic")
    c1 = quadratic_bezier_pieces(source)
    for channel, harmonic, pieces in (
        ("cos_splines", "0", (
            (Q(0), Q(0)),
            (Q(-100), Q(100)) if tail == 100 else (Q(0), Q(0)))),
        ("sin_splines", "1", (
            (Q(1), Q(0)), (Q(1), Q(0)))),
    ):
        before = LOWERER.linear_piece(source, channel, harmonic, Q(0), Q(1))
        after = LOWERER.linear_piece(source, channel, harmonic, Q(1), Q(2))
        require((before, after) == pieces,
                "exact first/second original source channel changed")
        require(LOWERER.evaluate_poly(before, Q(1)) ==
                LOWERER.evaluate_poly(after, Q(1)),
                "original physical source knot discontinuity")
    require(LOWERER.rational(source["phase_turn_offset"]) == 0 and
            LOWERER.rational(source["phase_turn_rate"]) == 2 and
            LOWERER.rational(source["parameter_lo"]) == 0 and
            LOWERER.rational(source["parameter_hi"]) == 2 and
            source["source_parameter_id"] == "source-time-t",
            "exact affine phase/source identity changed")
    return c1[1]


def analyze(corpus):
    reports = []
    for tail, case in frozen_cases(corpus):
        source = case["spec"]
        c1 = exact_source_channels(source, tail)
        require(c1 == (Q(1, 8), Q(0), Q(0)),
                "V43-refused second-span C1 is not constant 1/8")
        # theta=2*pi*(2*s)=4*pi*s, s in [1,2]; S1=1 exactly.
        # g(s)=(1/8)*cos(theta)+sin(theta).
        # Five consecutive half-cycle endpoints have alternating signs.
        points = [Q(1) + Q(i, 4) for i in range(5)]
        turns = [LOWERER.rational(source["phase_turn_offset"]) +
                 LOWERER.rational(source["phase_turn_rate"])*s for s in points]
        theta_over_pi = [2 * turn for turn in turns]
        require(turns == [Q(2), Q(5, 2), Q(3), Q(7, 2), Q(4)] and
                theta_over_pi == [Q(4), Q(5), Q(6), Q(7), Q(8)],
                "source half-cycle phase mapping changed")
        base_values = [Q(1, 8) if i % 2 == 0 else Q(-1, 8)
                       for i in range(5)]
        require(base_values == [Q(1, 8), Q(-1, 8), Q(1, 8),
                                Q(-1, 8), Q(1, 8)],
                "V11 half-cycle boundary signs changed")
        if tail == 0:
            # tan(theta)=-1/8; alpha=atan(1/8) in (0,pi/4).
            # In (4*pi,8*pi) the four and only four simple roots have:
            # theta_k=(5+k)*pi-alpha, k=0..3.
            # Use exact rational open brackets with no decimal or source
            # algebraicity claim. atan(x)>x-x^3/3 for 0<x<=1.
            alpha_lower = Q(1, 8) - Q(1, 8)**3 / 3
            require(alpha_lower == Q(191, 1536) and
                    alpha_lower > Q(1, 10) and
                    Q(7, 880) > Q(1, 128),
                    "rational atan lower / pi upper bracket proof changed")
            roots = []
            for k in range(4):
                right = points[k+1]
                lo = right - Q(1, 16)
                hi = right - Q(1, 128)
                require(points[k] < lo < hi < right,
                        "root bracket not strictly within half-cycle")
                before = "POSITIVE" if k % 2 == 0 else "NEGATIVE"
                after = "NEGATIVE" if k % 2 == 0 else "POSITIVE"
                roots.append({
                    "source_order_index": k,
                    "source_identity": (
                        "1+(k+1)/4-atan(1/8)/(4*pi), k=source_order_index"),
                    "exact_phase_identity": "(5+k)*pi-atan(1/8)",
                    "half_cycle_open_source_interval": [
                        str(points[k]), str(right)],
                    "strict_source_bracket": [str(lo), str(hi)],
                    "multiplicity": 1,
                    "event_kind": "SIMPLE_CROSSING",
                    "physical_sign_before": before,
                    "physical_sign_after": after,
                    "derivative_at_root_identity": (
                        "(-1)^(k+1)*pi*sqrt(65)/2"),
                    "source_rational_or_algebraic_coordinate_claimed": False,
                })
            report = {
                "case_id": case["id"],
                "classification": "FOUR_EXACT_SIMPLE_ALTERNATING_CROSSINGS",
                "physical_source_span": ["1", "2"],
                "phase_theta_over_pi_at_halfcycles": [
                    str(x) for x in theta_over_pi],
                "exact_halfcycle_endpoint_values": [
                    str(x) for x in base_values],
                "exact_open_physical_roots": 4,
                "ordered_open_roots": roots,
                "complete_sign_cells": [
                    "POSITIVE", "NEGATIVE", "POSITIVE",
                    "NEGATIVE", "POSITIVE"],
                "phase_chart_poles_crossed": True,
                "general_v6_cross_pole_authority_claimed": False,
            }
        else:
            # |g'|<=4*pi*(1+1/8)=9*pi/2<99/7.
            # F'(s)=100+g'(s)>601/7>0 and F(1)=1/8>0.
            # Hence F>0 and no root exists on the *closed* second span.
            derivative_lower = Q(100) - Q(9, 2) * Q(22, 7)
            require(derivative_lower == Q(601, 7) > 0,
                    "positive monotonic source derivative margin changed")
            report = {
                "case_id": case["id"],
                "classification": "STRICT_POSITIVE_STRICT_INCREASING_ROOT_FREE",
                "physical_source_span": ["1", "2"],
                "phase_theta_over_pi_at_halfcycles": [
                    str(x) for x in theta_over_pi],
                "exact_source_endpoint_values": ["1/8", "801/8"],
                "exact_open_physical_roots": 0,
                "strict_source_derivative_lower_rational": str(derivative_lower),
                "complete_sign_cells": ["POSITIVE"],
            }
        report["first_span_historical_v11_owner_unchanged"] = True
        reports.append(report)
    return {
        "schema": SCHEMA,
        "evidence_class": "DETERMINISTIC_EXACT_SOURCE_BOUND_PAIR_ONLY",
        "historical_v54_cases": 121,
        "historical_v43_refusals": 11,
        "original_source_parameter_id": "source-time-t",
        "v11_v43_tail_reports": reports,
        "historical_v54_dispositions_changed": False,
        "general_v43_owner_or_ordered_span_premise_claimed": False,
        "whole_source_composition_claimed": False,
        "mc_b_or_mc1_or_native_or_step_claimed": False,
    }


def validate_report(report, corpus):
    require(report == analyze(corpus),
            "submitted V11 source proof report differs from exact replay")
    return True


def contract():
    require(blob_sha(CORPUS) == CORPUS_BLOB, "frozen v54 corpus drifted")
    require(blob_sha(LOWERER_SOURCE) == LOWERER_BLOB,
            "reviewed source helper drifted")
    authority = load_json(AUTHORITY)
    programme = load_json(PROGRAMME)
    domain = load_json(DOMAIN)
    require(authority["programme"] == "MC-1" and
            authority["capability_status"] == "NOT_ESTABLISHED" and
            authority["production_authorized"] is False,
            "MC-1/production authority unexpectedly promoted")
    require(programme["capability_status"] == "NOT_ESTABLISHED" and
            programme["production_authorized"] is False and
            any(x["id"] == "MC-B" and x["state"] == "NOT_ESTABLISHED"
                for x in programme["gates"]),
            "MC-B programme gate incorrectly promoted")
    require(len(domain["coverage_rule"]["required_operation_ids"]) == 26,
            "26-operation machining denominator changed")
    return analyze(load_json(CORPUS))


def self_test():
    corpus = load_json(CORPUS)
    result = analyze(corpus)
    validate_report(result, corpus)
    left, right = result["v11_v43_tail_reports"]
    require(left["exact_open_physical_roots"] == 4 and
            [x["source_order_index"] for x in left["ordered_open_roots"]]
            == [0, 1, 2, 3] and
            left["complete_sign_cells"] ==
            ["POSITIVE", "NEGATIVE", "POSITIVE", "NEGATIVE", "POSITIVE"] and
            right["exact_open_physical_roots"] == 0 and
            right["strict_source_derivative_lower_rational"] == "601/7",
            "expected V11 tail contrast changed")

    def rejects_source(tail, mutate, label):
        changed = copy.deepcopy(corpus)
        row = next(x for x in changed["cases"]
                   if x["id"] == CASE_PREFIX + "tail" + str(tail))
        mutate(row)
        try:
            analyze(changed)
        except (ValueError, KeyError, IndexError, TypeError):
            return
        raise AssertionError("forged original V11 source accepted: " + label)

    rejects_source(0, lambda r: r["spec"].__setitem__("phase_turn_rate", "1"),
                   "phase rate")
    rejects_source(0, lambda r: r["spec"].__setitem__("phase_turn_offset", "1/2"),
                   "phase offset")
    rejects_source(0, lambda r: r["spec"].__setitem__("source_parameter_id", "forged"),
                   "source identity")
    rejects_source(0, lambda r: r["spec"]["cos_splines"]["1"]["controls"].__setitem__(
        1, "-1/2"), "first-span Bernstein curvature")
    rejects_source(0, lambda r: r["spec"]["cos_splines"]["1"]["controls"].__setitem__(
        4, "1/4"), "second-span cosine amplitude")
    rejects_source(0, lambda r: r["spec"]["cos_splines"]["1"]["knots"].__setitem__(
        4, "3/2"), "original degree-2 physical knot")
    rejects_source(0, lambda r: r["spec"]["sin_splines"]["1"]["controls"].__setitem__(
        1, "-1"), "second-span sine amplitude")
    rejects_source(0, lambda r: r["spec"]["cos_splines"].__setitem__(
        "2", {"degree": 0, "knots": ["0", "1", "2"],
              "controls": ["1", "1"]}), "unaccounted harmonic")
    rejects_source(100, lambda r: r["spec"]["cos_splines"]["0"]["controls"].__setitem__(
        3, "-100"), "positive ramp reversed")
    rejects_source(100, lambda r: r["spec"]["cos_splines"]["0"]["controls"].__setitem__(
        2, "1"), "knot discontinuity")
    rejects_source(100, lambda r: r.__setitem__("origin", "verify_pb00701_v10"),
                   "historical origin")
    rejects_source(0, lambda r: r["expected"]["observed"]["spans"][0].__setitem__(
        0, SECOND_OWNER), "first-span V11 owner")
    rejects_source(100, lambda r: r["expected"]["observed"]["spans"][1].__setitem__(
        1, "CERTIFIED"), "historical V43 refusal")
    rejects_source(100, lambda r: r["expected"].__setitem__(
        "v54_disposition", "CERTIFIED"), "historical v54 disposition")
    rejects_source(100, lambda r: r["spec"]["cos_splines"]["1"]["controls"].__setitem__(
        3, "0.125"), "unreviewed decimal notation")

    def rejects_report(mutate, label):
        changed = copy.deepcopy(result)
        mutate(changed)
        try:
            validate_report(changed, corpus)
        except ValueError:
            return
        raise AssertionError("forged V11 source proof accepted: " + label)

    rejects_report(lambda r: r["v11_v43_tail_reports"][0].__setitem__(
        "exact_open_physical_roots", 3), "omitted crossing")
    rejects_report(lambda r: r["v11_v43_tail_reports"][0]["ordered_open_roots"].pop(1),
                   "omitted root record")
    rejects_report(lambda r: r["v11_v43_tail_reports"][0]["ordered_open_roots"][1].__setitem__(
        "source_order_index", 0), "duplicate root index")
    rejects_report(lambda r: r["v11_v43_tail_reports"][0]["ordered_open_roots"][0].__setitem__(
        "strict_source_bracket", ["1", "5/4"]), "widened source bracket")
    rejects_report(lambda r: r["v11_v43_tail_reports"][0]["ordered_open_roots"][0].__setitem__(
        "physical_sign_before", "NEGATIVE"), "forged crossing sign")
    rejects_report(lambda r: r["v11_v43_tail_reports"][1].__setitem__(
        "strict_source_derivative_lower_rational", "0"), "forged derivative margin")
    rejects_report(lambda r: r.__setitem__(
        "general_v43_owner_or_ordered_span_premise_claimed", True),
        "unearned general V43 promotion")
    rejects_report(lambda r: r.__setitem__(
        "mc_b_or_mc1_or_native_or_step_claimed", True),
        "unearned engineering capability")
    print("PASS: pinned original V11 source/phase/degree-2 knot and 11 frozen V43 refusals")
    print("PASS: four alternating simple tail0 crossings; positive increasing tail100")
    print("PASS: exact source brackets/derivative and source/report mutation controls")
    print(json.dumps(result, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    options = parser.parse_args()
    if not (options.contract or options.self_test):
        parser.error("choose --contract and/or --self-test")
    if options.contract:
        print("PASS: frozen corpus, source-lowering, programme/domain authority")
        print(json.dumps(contract(), sort_keys=True))
    if options.self_test:
        self_test()


if __name__ == "__main__":
    main()
