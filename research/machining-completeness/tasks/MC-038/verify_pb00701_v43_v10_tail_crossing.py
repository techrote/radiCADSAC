#!/usr/bin/env python3
"""Exact source-bound single-crossing probe for frozen V10 tail100 V43 refusal.

Research only. Not a replacement V43 selecting route, whole-source composition,
general analytic root theorem, or MC-B/MC-1/native/B-rep/STEP qualification.
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
CASE_ID = "composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail100"
V10_OWNER = "PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO"
V43_OWNER = "PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF"
REFUSAL = "CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED"
SCHEMA = "radicadsac-pb00701-v43-v10-tail-crossing/1.0"

EXPECTED_SPEC = {
    "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
    "source_parameter_id": "source-time-t",
    "parameter_lo": "0", "parameter_hi": "2",
    "phase_turn_offset": "-1/2", "phase_turn_rate": "2",
    "cos_splines": {
        "0": {
            "degree": 1, "knots": ["0", "0", "1", "1", "2", "2"],
            "controls": ["0", "0", "0", "100"],
        },
        "1": {
            "degree": 0, "knots": ["0", "1", "2"],
            "controls": ["1", "1"],
        },
    },
    "sin_splines": {
        "1": {
            "degree": 1, "knots": ["0", "0", "1", "1", "2", "2"],
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


def git_blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_predecessor():
    require(git_blob(PREDECESSOR) == PREDECESSOR_BLOB,
            "reviewed V43 source-lowering predecessor changed")
    spec = importlib.util.spec_from_file_location(
        "reviewed_pb00701_v43_source_lowering", PREDECESSOR)
    module = importlib.util.module_from_spec(spec)
    require(spec.loader is not None, "V43 predecessor loader unavailable")
    spec.loader.exec_module(module)
    require(git_blob(PREDECESSOR) == PREDECESSOR_BLOB,
            "V43 source-lowering predecessor drifted during import")
    return module


LOWERER = load_predecessor()


def frozen_case(corpus):
    require(corpus.get("schema") ==
            "radicadsac-pb00701-finite-owner-corpus/54.0",
            "historical v54 schema changed")
    rows = corpus.get("cases")
    require(isinstance(rows, list) and len(rows) == 121 and
            len({r["id"] for r in rows}) == 121,
            "frozen v54 source denominator or case identities changed")
    refusals = [
        row for row in rows if
        [V43_OWNER, "BLOCKED", REFUSAL] in
        row["expected"]["observed"]["spans"]
    ]
    require(len(refusals) == 11 and
            sum(row["kind"] == "HARVESTED" for row in refusals) == 1 and
            sum(row["kind"] == "COMPOSITE_TAIL" for row in refusals) == 10,
            "original V43 refusal denominator changed")
    selected = [row for row in rows if row["id"] == CASE_ID]
    require(len(selected) == 1, "frozen V10 tail identity missing or duplicated")
    case = selected[0]
    require(case.get("kind") == "COMPOSITE_TAIL" and
            case.get("origin") == "verify_pb00701_v10",
            "V10 tail provenance changed")
    require(case.get("expected") == EXPECTED_HISTORICAL,
            "historical V10/V43 owner, refusal or disposition changed")
    require(case.get("spec") == EXPECTED_SPEC,
            "exact original V10 source/knot/phase identity changed")
    return case


def source_coefficients(source):
    """Re-lower original degree-0/1 clamped splines, not the V43 route."""
    first = (Q(0), Q(1))
    second = (Q(1), Q(2))
    triples = {}
    for channel, harmonic in (
        ("cos_splines", "0"), ("cos_splines", "1"),
        ("sin_splines", "1")
    ):
        a = LOWERER.linear_piece(source, channel, harmonic, *first)
        b = LOWERER.linear_piece(source, channel, harmonic, *second)
        require(LOWERER.evaluate_poly(a, Q(1)) ==
                LOWERER.evaluate_poly(b, Q(1)),
                "source channel is discontinuous at original knot s=1")
        triples[channel, harmonic] = (a, b)
    require(triples["cos_splines", "0"] ==
            ((Q(0), Q(0)), (Q(-100), Q(100))),
            "harmonic-zero tail linear ramp changed")
    require(triples["cos_splines", "1"] ==
            ((Q(1), Q(0)), (Q(1), Q(0))),
            "single cosine harmonic changed")
    require(triples["sin_splines", "1"] ==
            ((Q(1, 2), Q(-1)), (Q(-1, 2), Q(0))),
            "single sine harmonic changed")
    require(set(source["cos_splines"]) == {"0", "1"} and
            set(source["sin_splines"]) == {"1"},
            "unaccounted harmonic source term")
    return triples


def phase_turn(source, s):
    return (LOWERER.rational(source["phase_turn_offset"]) +
            LOWERER.rational(source["phase_turn_rate"]) * s)


def analyze(corpus):
    case = frozen_case(corpus)
    source = case["spec"]
    source_coefficients(source)
    left, right, witness = Q(1), Q(2), Q(101, 100)
    require(left < witness < right, "invalid strict root bracket")
    # The *original source* phase is -1/2+2*s, not 2*s. Its half-turn
    # offset reverses the cosine and sine relative to 4*pi*s.
    require([phase_turn(source, s) for s in (left, witness, right)] ==
            [Q(3, 2), Q(38, 25), Q(7, 2)],
            "original rational-turn phase map changed")

    # F=100(s-1)+cos(theta)-(1/2)sin(theta),
    # theta=2*pi*(-1/2+2*s)=4*pi*s-pi.
    # At s=1: theta=3*pi, F=-1. At s=2: theta=7*pi, F=99.
    left_value, right_value = Q(-1), Q(99)
    require(left_value < 0 < right_value, "V10 tail endpoint signs incorrect")

    # At s=101/100, theta=3*pi+pi/25:
    # F=1-cos(pi/25)+(1/2)*sin(pi/25)>0 because
    # 0<pi/25<pi/2, cos(pi/25)<1, sin(pi/25)>0.
    # This is an analytic sign proof, NOT numerical trigonometry.
    require(Q(0) < Q(1, 25) < Q(1, 2),
            "rational phase witness outside first quadrant")
    require(Q(100) * (witness - left) == 1,
            "exact source offset at witness changed")

    # F'=100-4*pi*sin(theta)-2*pi*cos(theta).
    # |sin|,|cos| <= 1 and the classical 3<pi<22/7 give
    # F'>=100-6*pi>100-6*(22/7)=568/7>0 on [1,2].
    pi_upper = Q(22, 7)
    derivative_margin = Q(100) - 6 * pi_upper
    require(Q(3) < pi_upper and derivative_margin == Q(568, 7) and
            derivative_margin > 0, "strict derivative margin missing")

    return {
        "schema": SCHEMA,
        "evidence_class": "DETERMINISTIC_EXACT_SOURCE_BOUND_CASE_PROOF_ONLY",
        "source_case": CASE_ID,
        "original_source_parameter_id": source["source_parameter_id"],
        "historical_v43_refusals": 11,
        "historical_v54_disposition": "BLOCKED",
        "source_span": ["1", "2"],
        "phase_turns_at_bracket_and_right": ["3/2", "38/25", "7/2"],
        "left_exact_value": str(left_value),
        "right_exact_value": str(right_value),
        "strict_positive_witness": "101/100",
        "strict_open_root_bracket": ["1", "101/100"],
        "derivative_strict_lower_bound": str(derivative_margin),
        "strictly_increasing_on_closed_span": True,
        "exact_open_roots": 1,
        "root_event": "SIMPLE_NEGATIVE_TO_POSITIVE_CROSSING",
        "physical_sign_before_root": "NEGATIVE",
        "physical_sign_after_root": "POSITIVE",
        "first_span_historical_certification_unchanged": True,
        "whole_source_composition_claimed": False,
        "general_v43_route_or_ordered_event_theorem_claimed": False,
        "v54_dispositions_changed": False,
        "mc_b_or_mc1_or_native_claimed": False,
    }


def contract():
    require(git_blob(CORPUS) == CORPUS_BLOB, "original v54 corpus drifted")
    require(git_blob(PREDECESSOR) == PREDECESSOR_BLOB,
            "accepted V43 lowerer drifted")
    authority = load_json(AUTHORITY)
    programme = load_json(PROGRAMME)
    domain = load_json(DOMAIN)
    require(authority["programme"] == "MC-1" and
            authority["capability_status"] == "NOT_ESTABLISHED" and
            authority["production_authorized"] is False,
            "MC-1/production authority incorrectly promoted")
    require(programme["capability_status"] == "NOT_ESTABLISHED" and
            any(g["id"] == "MC-B" and g["state"] == "NOT_ESTABLISHED"
                for g in programme["gates"]),
            "MC-B gate incorrectly promoted")
    require(len(domain["coverage_rule"]["required_operation_ids"]) == 26,
            "26-operation domain changed")
    return analyze(load_json(CORPUS))


def self_test():
    corpus = load_json(CORPUS)
    report = analyze(corpus)
    require(report["left_exact_value"] == "-1" and
            report["right_exact_value"] == "99" and
            report["strict_open_root_bracket"] == ["1", "101/100"] and
            report["derivative_strict_lower_bound"] == "568/7" and
            report["exact_open_roots"] == 1,
            "single-crossing report invariant changed")

    def rejected(mutator, label):
        candidate = copy.deepcopy(corpus)
        record = next(x for x in candidate["cases"] if x["id"] == CASE_ID)
        mutator(record)
        try:
            analyze(candidate)
        except (ValueError, KeyError, IndexError, TypeError):
            return
        raise AssertionError("adversarial original-source mutation accepted: " + label)

    rejected(lambda c: c["spec"].__setitem__("phase_turn_offset", "0"),
             "omit half-turn and invert endpoint sign")
    rejected(lambda c: c["spec"].__setitem__("phase_turn_rate", "1"),
             "change affine phase rate")
    rejected(lambda c: c["spec"].__setitem__("source_parameter_id", "forged"),
             "change original source parameter")
    rejected(lambda c: c["spec"]["cos_splines"]["0"]["controls"].__setitem__(3, "-100"),
             "invert tail offset slope")
    rejected(lambda c: c["spec"]["cos_splines"]["1"]["controls"].__setitem__(1, "-1"),
             "invert tail harmonic cosine")
    rejected(lambda c: c["spec"]["sin_splines"]["1"]["controls"].__setitem__(2, "1/2"),
             "alter tail harmonic sine")
    rejected(lambda c: c["spec"]["sin_splines"]["1"]["controls"].__setitem__(1, "1/2"),
             "alter first-span endpoint continuity")
    rejected(lambda c: c["spec"]["cos_splines"]["0"]["knots"].__setitem__(2, "9/10"),
             "forged original source knot")
    rejected(lambda c: c["spec"]["cos_splines"].__setitem__("2", {
        "degree": 0, "knots": ["0", "1", "2"], "controls": ["1", "1"]}),
        "unaccounted harmonic")
    rejected(lambda c: c.__setitem__("origin", "verify_pb00701_v9"),
             "forged origin")
    rejected(lambda c: c["expected"]["observed"]["spans"][1].__setitem__(1, "CERTIFIED"),
             "relabel historical V43 refusal")
    rejected(lambda c: c["expected"].__setitem__("v54_disposition", "CERTIFIED"),
             "rewrite historical v54 disposition")
    rejected(lambda c: c["expected"]["observed"]["spans"][0].__setitem__(0, V43_OWNER),
             "relabel original V10-certified first span")

    print("PASS: pinned original V10 tail source, physical knot, phase and 11 historical V43 refusals")
    print("PASS: exact -1 -> positive crossing in (1,101/100), F'>568/7, unique simple root")
    print("PASS: source/phase/knot/owner/historical refusal adversarial controls")
    print(json.dumps(report, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("choose --contract and/or --self-test")
    if args.contract:
        print("PASS: corpus/helper/programme/domain pins and exact source proof")
        print(json.dumps(contract(), sort_keys=True))
    if args.self_test:
        self_test()


if __name__ == "__main__":
    main()
