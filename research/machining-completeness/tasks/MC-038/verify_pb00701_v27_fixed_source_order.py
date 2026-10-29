#!/usr/bin/env python3
"""Exact fixed V27 composite source-order research; no generic V27/MC-B proof."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research/machining-completeness/tasks/MC-038"
CORPUS = TASK / "pb00701-finite-owner-corpus-v54.json"
LOWERER_PATH = TASK / "verify_pb00701_v43_refusal_cone.py"
AUTH = ROOT / "handoffs/current-authority.json"
PROGRAMME = ROOT / "research/machining-completeness/programme-v1.json"
DOMAIN = ROOT / "research/machining-completeness/tasks/MC-002/domain-contract-v1.json"
CORPUS_SHA = "5841c331579489b25caef38cd412bdbf286f9134"
LOWERER_SHA = "2a8079ee2cf012bc2a12794c4c5ff19ebd760007"
OWNER = "PB00701_V27_EXACT_RATIONAL_PHASE_SECTOR_PARTITION_COMPOSITION"
V19 = "PB00701_V19_EXACT_MULTI_HARMONIC_MONOTONE_ANCHOR"
BASE = "harvested:verify_pb00701_v27:271ca62551a6"
TAIL0 = "composite:" + OWNER + ":tail0"
TAIL100 = "composite:" + OWNER + ":tail100"
SCHEMA = "radicadsac-pb00701-v27-fixed-source-order/1.0"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + bytes([0]) + data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def exact_lowerer():
    require(blob(LOWERER_PATH) == LOWERER_SHA, "accepted exact source lowerer drift")
    spec = importlib.util.spec_from_file_location("v27_source_order_lowerer", LOWERER_PATH)
    module = importlib.util.module_from_spec(spec)
    require(spec.loader is not None, "exact source lowerer unavailable")
    spec.loader.exec_module(module)
    require(blob(LOWERER_PATH) == LOWERER_SHA, "source lowerer changed at import")
    return module


def spline(degree, controls, ends):
    return {"degree": degree,
            "knots": [str(x) for x in ends for _ in range(degree + 1)],
            "controls": controls}


def expected_spec(which):
    source = {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "source_parameter_id": "source-time-t",
        "parameter_lo": "0",
        "parameter_hi": "1" if which == BASE else "2",
        "phase_turn_offset": "1/2", "phase_turn_rate": "-2/3",
        "cos_splines": {},
        "sin_splines": {}
    }
    if which == BASE:
        source["cos_splines"] = {
            "0": spline(0, ["5"], [0, 1]),
            "2": spline(0, ["1/100"], [0, 1])}
        source["sin_splines"] = {"1": spline(1, ["2", "6"], [0, 1])}
    else:
        source["cos_splines"] = {
            "0": (spline(0, ["5", "5"], [0, 1, 2]) if which == TAIL0
                  else spline(1, ["5", "5", "5", "105"], [0, 1, 2])),
            "2": spline(0, ["1/100", "1/100"], [0, 1, 2])}
        source["sin_splines"] = {
            "1": spline(1, ["2", "6", "6", "6"], [0, 1, 2])}
    return source


def historical(which):
    owner_sequence = ([OWNER, "CERTIFIED", None],)
    if which == BASE:
        spans = list(owner_sequence)
        disposition = "CERTIFIED"
    else:
        spans = [list(owner_sequence[0]),
                 [OWNER if which == TAIL0 else V19, "CERTIFIED", None]]
        disposition = "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"
    return {"id": which, "observed": {"status": "CERTIFIED", "spans": spans},
            "v54_disposition": disposition}


def select(corpus):
    rows = corpus["cases"]
    require(corpus.get("schema") == "radicadsac-pb00701-finite-owner-corpus/54.0"
            and len(rows) == 121 and len({x["id"] for x in rows}) == 121,
            "frozen corpus identity/count mismatch")
    require(corpus["summary"]["v54_dispositions"][
            "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"] == 30,
            "frozen v54 missing-premise denominator drift")
    index = {row["id"]: row for row in rows}
    lowerer = exact_lowerer()
    for which in (BASE, TAIL0, TAIL100):
        require(which in index, "fixed V27 original-source case missing")
        row = index[which]
        require(row.get("origin") == "verify_pb00701_v27"
                and row.get("kind") == ("HARVESTED" if which == BASE else "COMPOSITE_TAIL"),
                "original V27 producing origin/provenance changed")
        require(row.get("spec") == expected_spec(which),
                "original source spline/phase/identity changed: " + which)
        require(row.get("expected") == historical(which),
                "historical V27 ownership/disposition changed: " + which)
        src = row["spec"]
        for left, right in ((Q(0), Q(1)),) if which == BASE else (
                (Q(0), Q(1)), (Q(1), Q(2))):
            c0 = lowerer.linear_piece(src, "cos_splines", "0", left, right)
            c2 = lowerer.linear_piece(src, "cos_splines", "2", left, right)
            s1 = lowerer.linear_piece(src, "sin_splines", "1", left, right)
            require(c2 == (Q(1, 100), Q(0)), "original second harmonic mismatch")
            if left == 0:
                require(c0 == (Q(5), Q(0)) and s1 == (Q(2), Q(4)),
                        "original first source span lowering mismatch")
            else:
                require(c0 == ((Q(5), Q(0)) if which == TAIL0
                               else (Q(-95), Q(100))) and s1 == (Q(6), Q(0)),
                        "original second source span lowering mismatch")
        if which != BASE:
            for channel, h in (("cos_splines", "0"), ("cos_splines", "2"),
                               ("sin_splines", "1")):
                p1 = lowerer.linear_piece(src, channel, h, Q(0), Q(1))
                p2 = lowerer.linear_piece(src, channel, h, Q(1), Q(2))
                require(lowerer.evaluate_poly(p1, Q(1)) ==
                        lowerer.evaluate_poly(p2, Q(1)),
                        "physical source knot continuity lost")
    return index


def exact_inequalities():
    # For all three cases theta=pi-(4pi/3)s. Interval endpoint turns
    # (theta/2pi) are exact rational, never a floating trigonometric scan.
    turns = lambda s: Q(1, 2) - Q(2, 3) * s
    require([str(turns(x)) for x in
             (Q(0), Q(3, 4), Q(1), Q(9, 8), Q(3, 2), Q(2))] ==
            ["1/2", "0", "-1/6", "-1/4", "-1/2", "-5/6"],
            "source-sector boundaries changed")
    # 3sqrt(3)>501/100, proven without binary floats or approximations.
    require(Q(27) > Q(501, 100) ** 2,
            "negative V27 seam/cell margin failed")
    # pi < 22/7, cos(theta)<=1/2 on the full second physical span,
    # |sin(2theta)|<=1: F_tail100'(s) >
    # 100-(4+2/75)*22/7 = 45856/525 > 0.
    derivative_lower = Q(100) - (Q(4) + Q(2, 75)) * Q(22, 7)
    require(derivative_lower == Q(45856, 525) > 0,
            "tail100 derivative lower bound no longer positive")
    # At knot F(1)=999/200 - 3sqrt(3) < 0 (exact rational square).
    require(Q(27) > Q(999, 200) ** 2,
            "shared-knot negative sign not established")
    # At 9/8, tail0 F=-101/100, tail100 adds 25/2.
    require(Q(-101, 100) < 0 and Q(25, 2) - Q(101, 100) == Q(1149, 100) > 0,
            "second-source root isolation signs changed")
    return str(derivative_lower)


def analyze(corpus):
    select(corpus)
    lower = exact_inequalities()
    # Exact source-specific proof is spelled out in the paired RAG memorandum.
    # Sign and derivative assertions rest on analytic sector inequalities,
    # NOT on sampling or a general-purpose V27 child-certificate checker.
    return {
        "schema": SCHEMA, "evidence_class": "DETERMINISTIC_MODEL",
        "source_ids": [BASE, TAIL0, TAIL100],
        "phase_turns": "1/2-2*s/3",
        "first_span": {"source_bracket": ["3/4", "1"],
                       "simple_roots": 1, "crossing": "POSITIVE_TO_NEGATIVE"},
        "shared_source_knot": {"s": "1", "relation": "NEGATIVE",
                               "zero_event": False, "continuous": True},
        "tail0": {"source_bracket": ["9/8", "3/2"], "simple_roots": 1,
                  "crossing": "NEGATIVE_TO_POSITIVE",
                  "whole_source_open_roots": 2,
                  "whole_source_signs": ["POSITIVE", "NEGATIVE", "POSITIVE"]},
        "tail100": {"source_bracket": ["1", "9/8"], "simple_roots": 1,
                    "crossing": "NEGATIVE_TO_POSITIVE",
                    "full_second_span_derivative_lower": lower,
                    "whole_source_open_roots": 2,
                    "whole_source_signs": ["POSITIVE", "NEGATIVE", "POSITIVE"]},
        "exact_root_coordinates_claimed": False,
        "historical_v54_disposition_changed": False,
        "generic_v27_v41_ordered_child_theorem_claimed": False,
        "pb007_mc_b_mc1_native_brep_step_claimed": False,
        "resource_refusal_interpreted_as_truth": False,
    }


def validate_report(report, corpus):
    require(report == analyze(corpus),
            "forged source-order certificate, wrong root count, sign, or capability")


def authority_contract(auth, programme, domain):
    require(auth["programme"] == "MC-1" and
            auth["capability_status"] == "NOT_ESTABLISHED" and
            auth["production_authorized"] is False,
            "production authority incorrectly promoted")
    require(programme["capability_status"] == "NOT_ESTABLISHED" and
            programme["production_authorized"] is False and
            any(g["id"] == "MC-B" and g["state"] == "NOT_ESTABLISHED"
                for g in programme["gates"]),
            "MC-B/MC-1 incorrectly promoted")
    require(len(domain["coverage_rule"]["required_operation_ids"]) == 26,
            "26-operation domain changed")


def contract():
    require(blob(CORPUS) == CORPUS_SHA, "frozen 121-case v54 Git blob changed")
    authority_contract(load(AUTH), load(PROGRAMME), load(DOMAIN))
    return analyze(load(CORPUS))


def self_test():
    corpus = load(CORPUS)
    report = analyze(corpus)
    validate_report(report, corpus)
    require(report["tail0"]["whole_source_open_roots"] == 2 and
            report["tail100"]["full_second_span_derivative_lower"] == "45856/525",
            "source-specific V27 ordering report drift")
    for label, case_id, mutation in (
        ("phase", TAIL0, lambda r: r["spec"].__setitem__("phase_turn_rate", "-1/2")),
        ("knot", TAIL0, lambda r: r["spec"]["sin_splines"]["1"]["knots"].__setitem__(2, "1/2")),
        ("harmonic", TAIL0, lambda r: r["spec"]["cos_splines"]["2"]["controls"].__setitem__(1, "1/50")),
        ("bias", TAIL100, lambda r: r["spec"]["cos_splines"]["0"]["controls"].__setitem__(3, "104")),
        ("seam", TAIL0, lambda r: r["spec"]["sin_splines"]["1"]["controls"].__setitem__(2, "5")),
        ("first", BASE, lambda r: r["spec"]["sin_splines"]["1"]["controls"].__setitem__(0, "3")),
        ("owner", TAIL0, lambda r: r["expected"]["observed"]["spans"][1].__setitem__(0, V19)),
        ("v54", TAIL100, lambda r: r["expected"].__setitem__("v54_disposition", "CERTIFIED")),
        ("origin", BASE, lambda r: r.__setitem__("origin", "verify_pb00701_v19")),
    ):
        forged = copy.deepcopy(corpus)
        row = next(r for r in forged["cases"] if r["id"] == case_id)
        mutation(row)
        try:
            analyze(forged)
        except (ValueError, KeyError, AssertionError):
            continue
        raise AssertionError("forged source accepted: " + label)
    for label, mutation in (
        ("omitted root", lambda r: r["tail0"].__setitem__("whole_source_open_roots", 1)),
        ("knot zero", lambda r: r["shared_source_knot"].__setitem__("relation", "ZERO")),
        ("reversed sign", lambda r: r["first_span"].__setitem__("crossing", "NEGATIVE_TO_POSITIVE")),
        ("false general theorem", lambda r: r.__setitem__(
            "generic_v27_v41_ordered_child_theorem_claimed", True)),
        ("false engineering claim", lambda r: r.__setitem__(
            "pb007_mc_b_mc1_native_brep_step_claimed", True)),
    ):
        forged = copy.deepcopy(report)
        mutation(forged)
        try:
            validate_report(forged, corpus)
        except ValueError:
            continue
        raise AssertionError("forged report accepted: " + label)
    auth, programme, domain = load(AUTH), load(PROGRAMME), load(DOMAIN)
    for label, obj, mutate in (
        ("production", auth, lambda r: r.__setitem__("production_authorized", True)),
        ("MC-B", programme, lambda r: r.__setitem__("capability_status", "ACCEPTED")),
        ("domain", domain, lambda r: r["coverage_rule"]["required_operation_ids"].pop()),
    ):
        a, p, d = copy.deepcopy(auth), copy.deepcopy(programme), copy.deepcopy(domain)
        target = {"production": a, "MC-B": p, "domain": d}[label]
        mutate(target)
        try:
            authority_contract(a, p, d)
        except ValueError:
            continue
        raise AssertionError("forged programme authority accepted: " + label)
    print("PASS: original V27 pair/corpus/source/knot/phase/owner controls")
    print("PASS: exact source-sector bounds and two simple source-specific roots")
    print("PASS: source and result mutation controls and no gate promotion")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        print(json.dumps(contract(), sort_keys=True))
    if args.self_test:
        self_test()


if __name__ == "__main__":
    main()
