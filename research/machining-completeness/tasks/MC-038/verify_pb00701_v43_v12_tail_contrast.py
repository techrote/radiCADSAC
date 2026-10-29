#!/usr/bin/env python3
"""Exact original-source sign/turning/crossing probes for frozen V12 V43 tails.

Deterministic case-specific research only; NOT general V43 ordered-root
authority, MC-B/MC-1 qualification, native geometry, or STEP construction.
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
CASE_PREFIX = "composite:PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC:"
FIRST_OWNER = "PB00701_V12_EXACT_COMPONENT_ROOT_PARTITION_SINGLE_HARMONIC"
SECOND_OWNER = "PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF"
REFUSAL = "CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED"
SCHEMA = "radicadsac-pb00701-v43-v12-tail-contrast/1.0"


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
            "accepted original-source lowerer Git blob drifted")
    spec = importlib.util.spec_from_file_location(
        "accepted_pb00701_v43_source_lowerer", LOWERER_SOURCE)
    module = importlib.util.module_from_spec(spec)
    require(spec.loader is not None, "source lowerer unavailable")
    spec.loader.exec_module(module)
    require(blob_sha(LOWERER_SOURCE) == LOWERER_BLOB,
            "source lowerer drifted during import")
    return module


LOWERER = load_lowerer()


def expected_spec(tail):
    require(tail in (0, 100), "unknown V12 tail")
    c0 = ({"degree": 0, "knots": ["0", "1", "2"],
           "controls": ["0", "0"]} if tail == 0 else
          {"degree": 1, "knots": ["0", "0", "1", "1", "2", "2"],
           "controls": ["0", "0", "0", "100"]})
    return {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "source_parameter_id": "source-time-t",
        "parameter_lo": "0", "parameter_hi": "2",
        "phase_turn_offset": "0", "phase_turn_rate": "1/4",
        "cos_splines": {
            "0": c0,
            "1": {
                "degree": 1, "knots": ["0", "0", "1", "1", "2", "2"],
                "controls": ["-1/3", "2/3", "2/3", "2/3"],
            },
        },
        "sin_splines": {
            "1": {
                "degree": 1, "knots": ["0", "0", "1", "1", "2", "2"],
                "controls": ["2/3", "-1/3", "-1/3", "-1/3"],
            },
        },
    }


def frozen_cases(corpus):
    require(corpus.get("schema") ==
            "radicadsac-pb00701-finite-owner-corpus/54.0",
            "frozen v54 corpus schema changed")
    rows = corpus.get("cases")
    require(isinstance(rows, list) and len(rows) == 121 and
            len({r["id"] for r in rows}) == 121,
            "frozen v54 case denominator or identities changed")
    refusals = [r for r in rows if
                [SECOND_OWNER, "BLOCKED", REFUSAL]
                in r["expected"]["observed"]["spans"]]
    require(len(refusals) == 11 and
            sum(r["kind"] == "HARVESTED" for r in refusals) == 1 and
            sum(r["kind"] == "COMPOSITE_TAIL" for r in refusals) == 10,
            "historical V43 refusal denominator changed")

    selected = []
    for tail in (0, 100):
        identifier = CASE_PREFIX + "tail" + str(tail)
        matches = [r for r in rows if r["id"] == identifier]
        require(len(matches) == 1, "frozen V12 source missing or duplicated")
        case = matches[0]
        require(case.get("kind") == "COMPOSITE_TAIL" and
                case.get("origin") == "v19",
                "original V12 case provenance changed")
        require(case.get("spec") == expected_spec(tail),
                "original V12 spline/knot/control/source/phase identity changed")
        require(case.get("expected") == {
            "id": identifier,
            "observed": {"status": "BLOCKED", "spans": [
                [FIRST_OWNER, "CERTIFIED", None],
                [SECOND_OWNER, "BLOCKED", REFUSAL],
            ]},
            "v54_disposition": "BLOCKED",
        }, "frozen V12/V43 owner, refusal, or disposition relabelled")
        selected.append((tail, case))
    return selected


def exact_source_pieces(source, tail):
    require(set(source["cos_splines"]) == {"0", "1"} and
            set(source["sin_splines"]) == {"1"},
            "unaccounted harmonic channel")
    expected = {
        ("cos_splines", "0"): (
            (Q(0), Q(0)), (Q(-100), Q(100)) if tail else (Q(0), Q(0))),
        ("cos_splines", "1"): (
            (Q(-1, 3), Q(1)), (Q(2, 3), Q(0))),
        ("sin_splines", "1"): (
            (Q(2, 3), Q(-1)), (Q(-1, 3), Q(0))),
    }
    for (channel, harmonic), (before_expected, after_expected) in expected.items():
        before = LOWERER.linear_piece(source, channel, harmonic, Q(0), Q(1))
        after = LOWERER.linear_piece(source, channel, harmonic, Q(1), Q(2))
        require((before, after) == (before_expected, after_expected),
                "original V12 source polynomial lowering changed")
        require(LOWERER.evaluate_poly(before, Q(1)) ==
                LOWERER.evaluate_poly(after, Q(1)),
                "original source has unproved knot continuity")
    require(LOWERER.rational(source["phase_turn_offset"]) == 0 and
            LOWERER.rational(source["phase_turn_rate"]) == Q(1, 4) and
            LOWERER.rational(source["parameter_lo"]) == 0 and
            LOWERER.rational(source["parameter_hi"]) == 2 and
            source["source_parameter_id"] == "source-time-t",
            "source parameter interval/phase authority changed")
    return True


def analyze(corpus):
    reports = []
    for tail, case in frozen_cases(corpus):
        source = case["spec"]
        exact_source_pieces(source, tail)

        # The original source's second physical span is s in [1,2].
        # theta = 2*pi*(s/4)=pi*s/2 is in [pi/2,pi].
        # g(s)=2/3*cos(theta)-1/3*sin(theta)<0 throughout [1,2],
        # since cos<=0, sin>=0 and they never vanish together.
        # g'(s)=-pi/3*sin(theta)-pi/6*cos(theta).
        theta_over_pi_at_endpoints = [Q(1, 2), Q(1)]
        require(theta_over_pi_at_endpoints == [
            2 * (LOWERER.rational(source["phase_turn_offset"]) +
                 LOWERER.rational(source["phase_turn_rate"]) * point)
            for point in (Q(1), Q(2))],
            "source endpoint phase identity changed")
        endpoint_values = [Q(-1, 3), Q(tail) - Q(2, 3)]
        require(endpoint_values == [
            Q(-1, 3), (Q(-2, 3) if tail == 0 else Q(298, 3))],
            "original second-span endpoint sign changed")
        require(Q(22, 7) < Q(4), "rational pi upper bound unavailable")
        if tail == 0:
            # g'(1)=-pi/3 < 0 and g'(2)=+pi/6 > 0, so turning occurs.
            report = {
                "case_id": case["id"],
                "physical_source_span": ["1", "2"],
                "phase_theta_over_pi_at_endpoints": ["1/2", "1"],
                "exact_endpoint_values": [str(x) for x in endpoint_values],
                "classification": "STRICT_NEGATIVE_NONMONOTONE_ROOT_FREE",
                "open_physical_root_count": 0,
                "complete_sign_cells": ["NEGATIVE"],
                "exact_derivative_endpoint_signs": ["NEGATIVE", "POSITIVE"],
                "interior_turning_point_exists": True,
                "first_span_historical_owner_unchanged": True,
            }
        else:
            # F(s)=100(s-1)+g(s), and |sin|,|cos|<=1 imply
            # F'(s)>=100-pi/2>100-11/7=689/7>0.
            # At s=101/100, delta=pi/200:
            # F=1-(2/3)sin(delta)-(1/3)cos(delta)
            # >2/3-pi/300>689/1050>0; F(1)=-1/3.
            derivative_lower = Q(100) - Q(22, 7) / 2
            bracket_positive_lower = Q(2, 3) - Q(22, 7) / 300
            require(derivative_lower == Q(689, 7) > 0 and
                    bracket_positive_lower == Q(689, 1050) > 0,
                    "strict source derivative/bracket inequalities changed")
            report = {
                "case_id": case["id"],
                "physical_source_span": ["1", "2"],
                "phase_theta_over_pi_at_endpoints": ["1/2", "1"],
                "exact_endpoint_values": [str(x) for x in endpoint_values],
                "classification": "STRICT_INCREASING_EXACTLY_ONE_SIMPLE_CROSSING",
                "open_physical_root_count": 1,
                "root_source_identity": (
                    "UNIQUE_PREIMAGE_IN_(1,101/100)_OF_"
                    "100*(s-1)+(2/3)*cos(pi*s/2)-(1/3)*sin(pi*s/2)=0"),
                "strict_open_source_bracket": ["1", "101/100"],
                "physical_sign_before": "NEGATIVE",
                "physical_sign_after": "POSITIVE",
                "root_multiplicity": 1,
                "strict_derivative_lower_rational": str(derivative_lower),
                "strict_bracket_right_value_lower_rational": str(bracket_positive_lower),
                "complete_sign_cells": ["NEGATIVE", "POSITIVE"],
                "first_span_historical_owner_unchanged": True,
            }
        reports.append(report)

    return {
        "schema": SCHEMA,
        "evidence_class": "DETERMINISTIC_EXACT_SOURCE_BOUND_PAIR_ONLY",
        "historical_v54_cases": 121,
        "historical_v43_refusals": 11,
        "original_source_parameter_id": "source-time-t",
        "v12_v43_tail_reports": reports,
        "historical_v54_dispositions_changed": False,
        "general_v43_owner_or_ordered_span_premise_claimed": False,
        "whole_source_composition_claimed": False,
        "mc_b_or_mc1_or_native_or_step_claimed": False,
    }


def validate_report(report, corpus):
    """Exact source-specific replay, not a general trigonometric root verifier."""
    require(report == analyze(corpus),
            "source-bound V12 pair report failed independent replay comparison")
    return True


def contract():
    require(blob_sha(CORPUS) == CORPUS_BLOB,
            "frozen v54 corpus Git blob changed")
    require(blob_sha(LOWERER_SOURCE) == LOWERER_BLOB,
            "accepted source lowerer Git blob changed")
    authority = load_json(AUTHORITY)
    programme = load_json(PROGRAMME)
    domain = load_json(DOMAIN)
    require(authority["programme"] == "MC-1" and
            authority["capability_status"] == "NOT_ESTABLISHED" and
            authority["production_authorized"] is False,
            "MC-1/production authorization unexpectedly promoted")
    require(programme["capability_status"] == "NOT_ESTABLISHED" and
            programme["production_authorized"] is False and
            any(x["id"] == "MC-B" and x["state"] == "NOT_ESTABLISHED"
                for x in programme["gates"]),
            "MC-B programme gate changed")
    require(len(domain["coverage_rule"]["required_operation_ids"]) == 26,
            "26-operation domain denominator changed")
    return analyze(load_json(CORPUS))


def self_test():
    corpus = load_json(CORPUS)
    report = analyze(corpus)
    validate_report(report, corpus)
    left, right = report["v12_v43_tail_reports"]
    require(left["open_physical_root_count"] == 0 and
            left["classification"] == "STRICT_NEGATIVE_NONMONOTONE_ROOT_FREE" and
            right["open_physical_root_count"] == 1 and
            right["strict_derivative_lower_rational"] == "689/7" and
            right["strict_bracket_right_value_lower_rational"] == "689/1050",
            "expected source-bound V12 contrast changed")

    def reject_source(tail, mutate, description):
        forged = copy.deepcopy(corpus)
        case = next(x for x in forged["cases"]
                    if x["id"] == CASE_PREFIX + "tail" + str(tail))
        mutate(case)
        try:
            analyze(forged)
        except (ValueError, KeyError, IndexError, TypeError):
            return
        raise AssertionError("forged V12 original source accepted: " + description)

    reject_source(0, lambda x: x["spec"].__setitem__("phase_turn_rate", "1/2"),
                  "phase rate")
    reject_source(0, lambda x: x["spec"].__setitem__("phase_turn_offset", "1/4"),
                  "phase offset")
    reject_source(0, lambda x: x["spec"].__setitem__("source_parameter_id", "other"),
                  "shared source parameter")
    reject_source(0, lambda x: x["spec"]["cos_splines"]["1"]["controls"].__setitem__(2, "1"),
                  "second-span cosine amplitude")
    reject_source(0, lambda x: x["spec"]["sin_splines"]["1"]["controls"].__setitem__(2, "1/3"),
                  "second-span sine sign")
    reject_source(0, lambda x: x["spec"]["cos_splines"]["1"]["knots"].__setitem__(3, "3/2"),
                  "original source clamped knot")
    reject_source(0, lambda x: x["spec"]["cos_splines"].__setitem__("2", {
        "degree": 0, "knots": ["0", "1", "2"], "controls": ["1", "1"]}),
        "unaccounted harmonic")
    reject_source(100, lambda x: x["spec"]["cos_splines"]["0"]["controls"].__setitem__(3, "-100"),
                  "signed tail ramp")
    reject_source(100, lambda x: x["spec"]["cos_splines"]["0"]["controls"].__setitem__(2, "1"),
                  "knot continuity")
    reject_source(100, lambda x: x["spec"]["sin_splines"]["1"]["controls"].__setitem__(1, "-0.3333333333"),
                  "unreviewed decimal source")
    reject_source(100, lambda x: x.__setitem__("origin", "verify_pb00701_v12"),
                  "historical origin")
    reject_source(0, lambda x: x["expected"]["observed"]["spans"][1].__setitem__(1, "CERTIFIED"),
                  "historical V43 refusal")
    reject_source(100, lambda x: x["expected"]["observed"]["spans"][0].__setitem__(0, SECOND_OWNER),
                  "historical V12 owner")
    reject_source(100, lambda x: x["expected"].__setitem__("v54_disposition", "CERTIFIED"),
                  "frozen V54 disposition")

    def reject_report(mutate, description):
        forged = copy.deepcopy(report)
        mutate(forged)
        try:
            validate_report(forged, corpus)
        except ValueError:
            return
        raise AssertionError("forged V12 proof report accepted: " + description)

    reject_report(lambda x: x["v12_v43_tail_reports"][0].__setitem__(
        "open_physical_root_count", 1), "false tail0 root")
    reject_report(lambda x: x["v12_v43_tail_reports"][1].__setitem__(
        "open_physical_root_count", 0), "omitted tail100 root")
    reject_report(lambda x: x["v12_v43_tail_reports"][1].__setitem__(
        "strict_open_source_bracket", ["1", "2"]), "widened root bracket")
    reject_report(lambda x: x["v12_v43_tail_reports"][1].__setitem__(
        "physical_sign_before", "POSITIVE"), "forged crossing orientation")
    reject_report(lambda x: x["v12_v43_tail_reports"][1].__setitem__(
        "strict_derivative_lower_rational", "0"), "forged derivative bound")
    reject_report(lambda x: x.__setitem__(
        "general_v43_owner_or_ordered_span_premise_claimed", True),
        "unearned general V43 certification")
    reject_report(lambda x: x.__setitem__(
        "mc_b_or_mc1_or_native_or_step_claimed", True),
        "unearned programme and native capability")
    print("PASS: exact V12 first/second source pieces, knot/phase and 11 frozen V43 refusals")
    print("PASS: tail0 negative nonmonotone root-free; tail100 one simple crossing")
    print("PASS: rational derivative/bracket bounds and source/report mutation controls")
    print(json.dumps(report, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    options = parser.parse_args()
    if options.contract:
        contract()
        print("PASS: original corpus/source lowerer/MC-B/MC-1/domain contract")
    if options.self_test:
        self_test()
    if not options.contract and not options.self_test:
        parser.error("choose --contract and/or --self-test")


if __name__ == "__main__":
    main()
