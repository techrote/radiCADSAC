#!/usr/bin/env python3
"""Source-bound sign probes for two historical V43 refusal cases.

Not a V43 derivative theorem, historical disposition rewrite, root ordering
authority, or MC-B/MC-1 capability acceptance.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research/machining-completeness/tasks/MC-038"
CORPUS = TASK / "pb00701-finite-owner-corpus-v54.json"
AUTHORITY = ROOT / "handoffs/current-authority.json"
PROGRAMME = ROOT / "research/machining-completeness/programme-v1.json"
DOMAIN = ROOT / "research/machining-completeness/tasks/MC-002/domain-contract-v1.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
OWNER = "PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF"
REFUSAL = "CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED"
HARVESTED = "harvested:verify_pb00701_v9:4e7b85fa122a"
COMPOSITE = "composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail100"
GRAMMAR = "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE"
SCHEMA = "radicadsac-pb00701-v43-refusal-cone-probe/1.0"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rational(value):
    require(type(value) is str and
            re.fullmatch(r"[+-]?\d+(?:/[1-9]\d*)?", value) is not None,
            "expected exact rational string, not float or unreviewed expression")
    return Q(value)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def blob_sha(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def linear_piece(source, channel, harmonic, left, right):
    entry = source[channel][harmonic]
    require(set(entry) == {"degree", "knots", "controls"}, "unreviewed spline field")
    degree = entry["degree"]
    require(type(degree) is int and degree in (0, 1),
            "nonconstant/nonlinear spline outside probe")
    knots = [rational(x) for x in entry["knots"]]
    controls = [rational(x) for x in entry["controls"]]
    block = degree + 1
    require(len(knots) % block == 0 and len(knots) >= 2 * block,
            "unrecognized fully-clamped piecewise spline")
    bounds = [knots[i] for i in range(0, len(knots), block)]
    require(all(a < b for a, b in zip(bounds, bounds[1:])),
            "nonincreasing knots")
    require(knots == [x for b in bounds for x in [b] * block],
            "spline is not independently clamped per piece")
    require(len(controls) == (len(bounds) - 1) * block,
            "B-spline knot/control cardinality mismatch")
    require(bounds[0] == rational(source["parameter_lo"]) and
            bounds[-1] == rational(source["parameter_hi"]),
            "spline does not cover full original source")
    require(left in bounds and bounds.index(left) < len(bounds) - 1,
            "requested span absent")
    i = bounds.index(left)
    require(bounds[i + 1] == right,
            "requested interval is not one physical source span")
    if degree == 0:
        return controls[i], Q(0)
    c0, c1 = controls[2 * i:2 * i + 2]
    slope = (c1 - c0) / (right - left)
    return c0 - slope * left, slope


def evaluate_poly(coefs, point):
    return coefs[0] + coefs[1] * point


def source_guard(case, *, kind, origin, cos_harmonics, sin_harmonics, source_hi):
    require(case["kind"] == kind and case["origin"] == origin,
            "case provenance mismatch")
    source = case["spec"]
    require(set(source) == {"grammar", "cos_splines", "sin_splines",
                            "parameter_lo", "parameter_hi", "phase_turn_offset",
                            "phase_turn_rate", "source_parameter_id"},
            "source authority changed")
    require(source["grammar"] == GRAMMAR and
            source["source_parameter_id"] == "source-time-t",
            "grammar/source-parameter mismatch")
    require(set(source["cos_splines"]) == cos_harmonics and
            set(source["sin_splines"]) == sin_harmonics,
            "unaccounted harmonic channel")
    require(rational(source["parameter_lo"]) == 0 and
            rational(source["parameter_hi"]) == source_hi and
            rational(source["phase_turn_offset"]) == 0 and
            rational(source["phase_turn_rate"]) == Q(1, 8),
            "source interval or exact phase map changed")
    return source


def find_cases(corpus):
    require(corpus["schema"].startswith("radicadsac-"),
            "wrong frozen corpus schema")
    rows = corpus["cases"]
    require(len(rows) == 121 and len(set(r["id"] for r in rows)) == 121,
            "frozen case denominator or identities changed")
    refused = [r for r in rows if any(span == [OWNER, "BLOCKED", REFUSAL]
               for span in r["expected"]["observed"]["spans"])]
    require(len(refused) == 11 and
            sum(r["kind"] == "HARVESTED" for r in refused) == 1 and
            sum(r["kind"] == "COMPOSITE_TAIL" for r in refused) == 10,
            "V43 historical refusal denominator changed")
    index = {r["id"]: r for r in rows}
    require(HARVESTED in index and COMPOSITE in index,
            "source-bound V43 probes missing")
    return index[HARVESTED], index[COMPOSITE]


def analyze(corpus):
    harvested, composite = find_cases(corpus)
    require(harvested["expected"] == {
        "id": HARVESTED,
        "observed": {"status": "BLOCKED", "spans": [[OWNER, "BLOCKED", REFUSAL]]},
        "v54_disposition": "BLOCKED"},
        "harvested V43 historical result changed")
    require(composite["expected"] == {
        "id": COMPOSITE,
        "observed": {"status": "BLOCKED", "spans": [
            ["PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO", "CERTIFIED", None],
            [OWNER, "BLOCKED", REFUSAL]]},
        "v54_disposition": "BLOCKED"},
        "composite V43 historical result changed")
    a = source_guard(harvested, kind="HARVESTED", origin="verify_pb00701_v9",
                     cos_harmonics={"1"}, sin_harmonics={"1"}, source_hi=Q(1))
    require(linear_piece(a, "cos_splines", "1", Q(0), Q(1)) == (Q(1), Q(0)),
            "harvested cosine differs from C1(s)=1")
    require(linear_piece(a, "sin_splines", "1", Q(0), Q(1)) == (Q(-1, 2), Q(1)),
            "harvested sine differs from S1(s)=s-1/2")
    # theta=2*pi*(s/8) in [0,pi/4]. cos >2/3 and 0<=sin<3/4.
    # Compare radicals with exact rational squares, never numerically.
    require(Q(2, 3)**2 < Q(1, 2) < Q(3, 4)**2,
            "invalid rational trigonometric cone constants")
    harvested_margin = Q(2, 3) - Q(1, 2) * Q(3, 4)
    require(harvested_margin == Q(7, 24) and harvested_margin > 0,
            "harvested sign margin is not strictly positive")

    b = source_guard(composite, kind="COMPOSITE_TAIL",
                     origin="verify_pb00701_v10", cos_harmonics={"0", "1"},
                     sin_harmonics={"1"}, source_hi=Q(2))
    first, second = (Q(0), Q(1)), (Q(1), Q(2))
    for channel, harmonic in (("cos_splines", "0"), ("cos_splines", "1"),
                              ("sin_splines", "1")):
        left_piece = linear_piece(b, channel, harmonic, *first)
        right_piece = linear_piece(b, channel, harmonic, *second)
        require(evaluate_poly(left_piece, Q(1)) ==
                evaluate_poly(right_piece, Q(1)),
                "manufactured source knot is not physically continuous")
    require(linear_piece(b, "cos_splines", "0", *second) == (Q(-100), Q(100)),
            "composite tail harmonic-zero offset differs from 100(s-1)")
    require(linear_piece(b, "cos_splines", "1", *second) == (Q(1, 2), Q(0)),
            "composite tail cosine differs from C1=1/2")
    require(linear_piece(b, "sin_splines", "1", *second) == (Q(1), Q(0)),
            "composite tail sine differs from S1=1")
    # theta=pi*s/4 in [pi/4,pi/2] on the V43-blocked second span:
    # 100(s-1)>=0, cos(theta)>=0, sin(theta)>2/3.
    tail_margin = Q(2, 3)
    require(tail_margin > 0, "composite tail sign margin is not positive")
    return {
        "schema": SCHEMA,
        "evidence_class": "DETERMINISTIC_SOURCE_BOUND_SIGN_PROBE_ONLY",
        "frozen_v43_refusals": 11,
        "probe_cases": [
            {"id": HARVESTED, "historical_disposition": "BLOCKED",
             "source_interval": ["0", "1"],
             "strict_lower_bound": str(harvested_margin),
             "sign": "POSITIVE_ON_CLOSED_SOURCE_SPAN"},
            {"id": COMPOSITE, "historical_disposition": "BLOCKED",
             "source_interval": ["1", "2"],
             "strict_lower_bound": str(tail_margin),
             "sign": "POSITIVE_ON_CLOSED_SOURCE_SPAN"},
        ],
        "v54_dispositions_changed": False,
        "general_v43_or_ordered_event_theorem_claimed": False,
        "mc_b_or_mc1_or_native_claimed": False,
    }


def contract():
    require(blob_sha(CORPUS) == CORPUS_BLOB,
            "frozen v54 corpus Git blob drifted")
    authority = load(AUTHORITY)
    programme = load(PROGRAMME)
    domain = load(DOMAIN)
    require(authority["programme"] == "MC-1" and
            authority["capability_status"] == "NOT_ESTABLISHED" and
            authority["production_authorized"] is False,
            "current authority unexpectedly promoted")
    require(programme["capability_status"] == "NOT_ESTABLISHED" and
            any(x["id"] == "MC-B" and x["state"] == "NOT_ESTABLISHED"
                for x in programme["gates"]),
            "programme gate unexpectedly promoted")
    require(len(domain["coverage_rule"]["required_operation_ids"]) == 26,
            "26-operation machining domain changed")
    return analyze(load(CORPUS))


def self_test():
    corpus = load(CORPUS)
    report = analyze(corpus)
    assert report["probe_cases"][0]["strict_lower_bound"] == "7/24"
    assert report["probe_cases"][1]["strict_lower_bound"] == "2/3"

    def rejects(mutator, label):
        changed = copy.deepcopy(corpus)
        h, c = find_cases(changed)
        mutator(h, c)
        try:
            analyze(changed)
        except (ValueError, KeyError, IndexError, TypeError):
            return
        raise AssertionError("adversarial mutation accepted: " + label)

    rejects(lambda h, c: h["spec"]["cos_splines"]["1"]["controls"].__setitem__(0, "0"),
            "alter harvested cosine")
    rejects(lambda h, c: h["spec"]["sin_splines"]["1"]["controls"].__setitem__(0, "-2"),
            "alter harvested sine")
    rejects(lambda h, c: h["spec"].__setitem__("phase_turn_rate", "1/4"),
            "alter harvested phase")
    rejects(lambda h, c: h["spec"]["cos_splines"].__setitem__("2", {
        "degree": 0, "knots": ["0", "1"], "controls": ["1"]}),
        "unaccounted harmonic")
    rejects(lambda h, c: h["expected"].__setitem__("v54_disposition", "CERTIFIED"),
            "historical positive relabelling")
    rejects(lambda h, c: c["spec"]["cos_splines"]["0"]["controls"].__setitem__(3, "-100"),
            "tail positive offset reversed")
    rejects(lambda h, c: c["spec"]["sin_splines"]["1"]["controls"].__setitem__(1, "-1"),
            "tail sine sign reversed")
    rejects(lambda h, c: c["spec"]["cos_splines"]["1"]["controls"].__setitem__(2, "-1/2"),
            "tail cosine sign reversed")
    rejects(lambda h, c: c["spec"].__setitem__("phase_turn_offset", "1/8"),
            "alter tail phase cell")
    rejects(lambda h, c: c["expected"]["observed"]["spans"][1].__setitem__(1, "CERTIFIED"),
            "historical V43 negative relabelling")
    rejects(lambda h, c: c["spec"]["sin_splines"]["1"]["controls"].__setitem__(0, "0.5"),
            "binary/decimal source notation")
    print("PASS: 11 frozen V43 refusals retained, 1 harvested and 10 tail cases")
    print("PASS: source-bound exact positive sign on two historical V43-blocked spans")
    print("PASS: adversarial source, phase, continuity, harmonic and refusal controls")
    print(json.dumps(report, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    options = parser.parse_args()
    if not (options.contract or options.self_test):
        parser.error("choose --contract and/or --self-test")
    if options.contract:
        result = contract()
        print("PASS: pinned v54 source corpus and unpromoted programme authority")
        print(json.dumps(result, sort_keys=True))
    if options.self_test:
        self_test()


if __name__ == "__main__":
    main()
