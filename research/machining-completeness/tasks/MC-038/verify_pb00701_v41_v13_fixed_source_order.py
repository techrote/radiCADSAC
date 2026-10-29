#!/usr/bin/env python3
"""Exact bounded V41/V13 original-source root-order probe; no general composition theorem."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from functools import lru_cache
from math import factorial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "research/machining-completeness/tasks/MC-038"
CORPUS = TASK / "pb00701-finite-owner-corpus-v54.json"
LOWERER = TASK / "verify_pb00701_v43_refusal_cone.py"
AUTH = ROOT / "handoffs/current-authority.json"
PROGRAMME = ROOT / "research/machining-completeness/programme-v1.json"
DOMAIN = ROOT / "research/machining-completeness/tasks/MC-002/domain-contract-v1.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
LOWERER_BLOB = "2a8079ee2cf012bc2a12794c4c5ff19ebd760007"
SOURCE_ID = "harvested:verify_pb00701_v13:c426f65b5c10"
OWNER = "PB00701_V41_EXACT_ROTATED_COORDINATE_ORIENTATION_ROOT_PARTITION_COMPOSITION"
REASON = "V41_COMPLETE_V43_CHILD_NOT_COMPOSABLE"
SCHEMA = "radicadsac-pb00701-v41-v13-fixed-source-order/1.0"
N = 128
F_LIPSCHITZ = Q(14)
D_LIPSCHITZ = Q(60)
TAYLOR_ERR = Q(7**41, factorial(41))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git_blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def expected_source():
    def piece(values):
        return {"degree": 1, "controls": values, "knots": ["0", "0", "1", "1"]}
    return {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "source_parameter_id": "source-time-t",
        "parameter_lo": "0",
        "parameter_hi": "1",
        "phase_turn_offset": "0",
        "phase_turn_rate": "1/4",
        "cos_splines": {
            "1": piece(["-5/6", "5/3"]),
            "3": piece(["-1/6", "1/3"]),
        },
        "sin_splines": {
            "1": piece(["1", "-1/2"]),
            "4": piece(["1/3", "-1/6"]),
        },
    }


def check_source(corpus):
    require(corpus.get("schema") == "radicadsac-pb00701-finite-owner-corpus/54.0",
            "frozen v54 schema drift")
    cases = corpus["cases"]
    require(len(cases) == 121 and len({r["id"] for r in cases}) == 121,
            "frozen v54 case denominator drift")
    require(corpus["summary"]["v54_dispositions"][
        "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"] == 30,
        "historical missing-premise count changed")
    v41 = [r for r in cases if any(
        span[0] == OWNER for span in r["expected"]["observed"]["spans"])]
    require(len(v41) == 2, "historical V41 owner case count changed")
    found = [r for r in v41 if r["id"] == SOURCE_ID]
    require(len(found) == 1, "original blocked V41/V13 source missing")
    row = found[0]
    require(row["kind"] == "HARVESTED" and row["origin"] == "verify_pb00701_v13",
            "original V41/V13 producer changed")
    require(row["expected"] == {
        "id": SOURCE_ID,
        "observed": {"status": "BLOCKED", "spans": [[OWNER, "BLOCKED", REASON]]},
        "v54_disposition": "BLOCKED",
    }, "original historical V41 refusal changed")
    source = row["spec"]
    require(source == expected_source(), "original spline/phase/source identity changed")
    require(git_blob(LOWERER) == LOWERER_BLOB, "accepted exact source lowerer changed")
    spec = importlib.util.spec_from_file_location("v41_v13_pinned_lowerer", LOWERER)
    require(spec is not None and spec.loader is not None, "source lowerer unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for channel, harmonic, coefficients in (
        ("cos_splines", "1", (Q(-5, 6), Q(5, 2))),
        ("cos_splines", "3", (Q(-1, 6), Q(1, 2))),
        ("sin_splines", "1", (Q(1), Q(-3, 2))),
        ("sin_splines", "4", (Q(1, 3), Q(-1, 2))),
    ):
        actual = module.linear_piece(source, channel, harmonic, Q(0), Q(1))
        require(actual == coefficients, "original physical spline lowering mismatch")
    return row


def arctan_bounds(x, terms=12):
    result = sum(((-1)**j) * x**(2*j+1) / (2*j+1) for j in range(terms))
    remainder = x**(2*terms+1) / (2*terms+1)
    return ((result, result + remainder) if terms % 2 == 0
            else (result - remainder, result))


@lru_cache(maxsize=1)
def pi_bounds():
    lo5, hi5 = arctan_bounds(Q(1, 5))
    lo239, hi239 = arctan_bounds(Q(1, 239))
    lo, hi = 16*lo5 - 4*hi239, 16*hi5 - 4*lo239
    require(Q(3) < lo < hi < Q(22, 7), "Machin pi bound incorrect")
    floor = lo * 10**12
    pi0 = Q(floor.numerator // floor.denominator, 10**12)
    require(pi0 <= lo and hi-pi0 < Q(1, 10**11), "rational pi center too coarse")
    return lo, hi, pi0


def interval(x, upper=None):
    return (x, x if upper is None else upper)


def add(a, b):
    return (a[0]+b[0], a[1]+b[1])


def mul(a, b):
    products = [x*y for x in a for y in b]
    return (min(products), max(products))


def sincos(k, s):
    _, hi, pi0 = pi_bounds()
    x = Q(k)*s*pi0/2
    require(Q(0) <= x <= Q(7), "Taylor argument outside certified range")
    sin_value, cos_value = Q(0), Q(0)
    sin_power, cos_power = x, Q(1)
    for j in range(21):
        sign = -1 if j % 2 else 1
        sin_value += sign*sin_power
        cos_value += sign*cos_power
        sin_power *= x*x / Q((2*j+2)*(2*j+3))
        cos_power *= x*x / Q((2*j+1)*(2*j+2))
    # Taylor's Lagrange bound applies on [0,7]. Both trigonometric
    # functions are 1-Lipschitz in their argument; pi0 <= true pi <= hi.
    error = TAYLOR_ERR + Q(k)*s*(hi-pi0)/2
    return (interval(sin_value-error, sin_value+error),
            interval(cos_value-error, cos_value+error))


def function_and_derivative(s):
    lo, hi, _ = pi_bounds()
    s1, c1 = sincos(1, s)
    s3, c3 = sincos(3, s)
    s4, c4 = sincos(4, s)
    a, b = interval((3*s-1)/6), interval((2-3*s)/2)
    e = add(mul(interval(Q(5)), c1), c3)
    h = add(s1, mul(interval(Q(1, 3)), s4))
    et = add(mul(interval(Q(-5)), s1), mul(interval(Q(-3)), s3))
    ht = add(c1, mul(interval(Q(4, 3)), c4))
    f = add(mul(a, e), mul(b, h))
    derivative = add(
        add(mul(interval(Q(1, 2)), e),
            mul(mul(a, et), interval(lo/2, hi/2))),
        add(mul(interval(Q(-3, 2)), h),
            mul(mul(b, ht), interval(lo/2, hi/2))),
    )
    return f, derivative


def prove_zone(left, right, property_name):
    """Exact midpoint enclosure + global first/second-derivative Lipschitz."""
    left, right = Q(left), Q(right)
    require(Q(0) <= left < right <= 1, "invalid rational proof zone")
    which = "D" if property_name.endswith("DERIVATIVE") else "F"
    positive = property_name.startswith("POSITIVE")
    limit = D_LIPSCHITZ if which == "D" else F_LIPSCHITZ
    for i in range(N):
        start = left + (right-left)*Q(i, N)
        end = left + (right-left)*Q(i+1, N)
        midpoint, radius = (start+end)/2, (end-start)/2
        f, derivative = function_and_derivative(midpoint)
        value = derivative if which == "D" else f
        signed_lower = value[0] if positive else -value[1]
        require(signed_lower > limit*radius,
                "unproved exact interval sign: " + property_name +
                " at rational subcell " + str(i))
    return {"source_interval": [str(left), str(right)],
            "property": property_name, "subcells": N, "strict": True}


@lru_cache(maxsize=1)
def exact_math_report():
    # A=(3s-1)/6 and B=(2-3s)/2; theta=pi*s/2.
    # E=5*cos(theta)+cos(3theta), H=sin(theta)+sin(4theta)/3.
    # Bounds on s in [0,1]:
    # |A|<=1/3, |B|<=1, |E|<=6, |H|<=4/3,
    # |E_theta|<=8, |H_theta|<=7/3,
    # |E_thetatheta|<=14, |H_thetatheta|<=19/3.
    # pi/2 < 11/7. Hence |F'|<14 and |F''|<60 globally.
    t = Q(11, 7)
    require(Q(3)+Q(1, 3)*8*t+Q(2)+Q(7, 3)*t < F_LIPSCHITZ,
            "invalid global first derivative bound")
    require(8*t+Q(14, 3)*t*t+7*t+Q(19, 3)*t*t < D_LIPSCHITZ,
            "invalid global second derivative bound")
    zones = [
        prove_zone(Q(0), Q(3, 20), "NEGATIVE_F"),
        prove_zone(Q(3, 20), Q(1, 5), "POSITIVE_DERIVATIVE"),
        prove_zone(Q(1, 5), Q(4, 5), "POSITIVE_F"),
        prove_zone(Q(4, 5), Q(17, 20), "NEGATIVE_DERIVATIVE"),
        prove_zone(Q(17, 20), Q(1), "NEGATIVE_F"),
    ]
    # Each derivative zone has strictly opposite signs at its endpoints,
    # supplied by adjacent sign zones. IVT + derivative strictness prove
    # one and only one simple root in each bracket.
    return {"schema": SCHEMA, "source_id": SOURCE_ID,
            "historical_owner": OWNER, "historical_status": "BLOCKED",
            "original_phase_turns": ["0", "1/4"],
            "root_brackets": [["3/20", "1/5"], ["4/5", "17/20"]],
            "simple_open_roots": 2,
            "closed_endpoint_roots": 0,
            "sign_cells": ["NEGATIVE", "POSITIVE", "NEGATIVE"],
            "zones": zones, "pi_method": "MACHIN_ALTERNATING_RATIONAL",
            "trig_method": "TAYLOR_RATIONAL_LAGRANGE_AND_LIPSCHITZ",
            "source_specific_only": True,
            "generic_v27_v41_child_composition_claimed": False,
            "pb007_mc_b_mc1_native_brep_step_claimed": False}


def authority_contract(auth, programme, domain):
    require(auth["programme"] == "MC-1" and
            auth["capability_status"] == "NOT_ESTABLISHED" and
            auth["production_authorized"] is False, "authority was promoted")
    require(programme["capability_status"] == "NOT_ESTABLISHED" and
            programme["production_authorized"] is False and
            any(g["id"] == "MC-B" and g["state"] == "NOT_ESTABLISHED"
                for g in programme["gates"]), "programme gate was promoted")
    require(len(domain["coverage_rule"]["required_operation_ids"]) == 26,
            "26-operation domain changed")


def analyze(corpus):
    check_source(corpus)
    return copy.deepcopy(exact_math_report())


def contract():
    require(git_blob(CORPUS) == CORPUS_BLOB, "frozen v54 corpus Git blob changed")
    authority_contract(load(AUTH), load(PROGRAMME), load(DOMAIN))
    return analyze(load(CORPUS))


def validate_report(candidate, corpus):
    require(candidate == analyze(corpus), "forged V41/V13 root classification")


def self_test():
    corpus = load(CORPUS)
    report = contract()
    validate_report(report, corpus)
    for name, mutation in (
        ("phase", lambda r: r["spec"].__setitem__("phase_turn_rate", "1/8")),
        ("knot", lambda r: r["spec"]["cos_splines"]["1"]["knots"].__setitem__(2, "1/2")),
        ("cosine", lambda r: r["spec"]["cos_splines"]["3"]["controls"].__setitem__(1, "1/2")),
        ("sine", lambda r: r["spec"]["sin_splines"]["4"]["controls"].__setitem__(1, "-1/3")),
        ("source", lambda r: r["spec"].__setitem__("source_parameter_id", "forged")),
        ("owner", lambda r: r["expected"]["observed"]["spans"][0].__setitem__(0, "V19")),
        ("disposition", lambda r: r["expected"].__setitem__("v54_disposition", "CERTIFIED")),
        ("producer", lambda r: r.__setitem__("origin", "verify_pb00701_v41")),
    ):
        forged = copy.deepcopy(corpus)
        row = next(r for r in forged["cases"] if r["id"] == SOURCE_ID)
        mutation(row)
        try:
            analyze(forged)
        except (ValueError, KeyError):
            continue
        raise AssertionError("forged source accepted: " + name)
    for name, mutation in (
        ("lost root", lambda r: r.__setitem__("simple_open_roots", 1)),
        ("reversed sign", lambda r: r["sign_cells"].__setitem__(0, "POSITIVE")),
        ("forged bracket", lambda r: r["root_brackets"][0].__setitem__(0, "0")),
        ("lost strictness", lambda r: r["zones"][0].__setitem__("strict", False)),
        ("general theorem", lambda r: r.__setitem__(
            "generic_v27_v41_child_composition_claimed", True)),
        ("engineering claim", lambda r: r.__setitem__(
            "pb007_mc_b_mc1_native_brep_step_claimed", True)),
    ):
        forged = copy.deepcopy(report)
        mutation(forged)
        try:
            validate_report(forged, corpus)
        except ValueError:
            continue
        raise AssertionError("forged report accepted: " + name)
    auth, programme, domain = load(AUTH), load(PROGRAMME), load(DOMAIN)
    for name, obj, mutation in (
        ("production", auth, lambda x: x.__setitem__("production_authorized", True)),
        ("MC-B", programme, lambda x: x.__setitem__("capability_status", "ACCEPTED")),
        ("domain", domain, lambda x: x["coverage_rule"]["required_operation_ids"].pop()),
    ):
        a, p, d = copy.deepcopy(auth), copy.deepcopy(programme), copy.deepcopy(domain)
        mutation({"production": a, "MC-B": p, "domain": d}[name])
        try:
            authority_contract(a, p, d)
        except ValueError:
            continue
        raise AssertionError("forged gate authority accepted: " + name)
    print("PASS: pinned V41/V13 original B-spline/source/phase/owner/refusal")
    print("PASS: exact rational pi/trig sign and derivative interval proof")
    print("PASS: exactly two simple, ordered physical roots and three sign cells")
    print("PASS: adversarial source/report/programme authority controls")


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
