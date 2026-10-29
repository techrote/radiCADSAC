#!/usr/bin/env python3
"""Exact original-source V16/V43 tail100 crossing research.

Single frozen deterministic source only. NOT general V43 ordered-child authority,
PB-007, MC-B/MC-1, native geometry, B-rep, engineering STEP or production.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from math import comb
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
CASE_ID = "composite:PB00701_V16_EXACT_CHEBYSHEV_STURM_MULTIPLIER:tail100"
FIRST_OWNER = "PB00701_V16_EXACT_CHEBYSHEV_STURM_MULTIPLIER"
SECOND_OWNER = "PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF"
REFUSAL = "CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED"
SCHEMA = "radicadsac-pb00701-v43-v16-chebyshev-crossing/1.0"


def require(predicate, reason):
    if not predicate:
        raise ValueError(reason)


def json_canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def blob_sha(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def load_lowerer():
    require(blob_sha(LOWERER_SOURCE) == LOWERER_BLOB,
            "accepted V43 degree-0/1 source lowerer drifted")
    spec = importlib.util.spec_from_file_location("accepted_v43_v16_lowerer",
                                                   LOWERER_SOURCE)
    module = importlib.util.module_from_spec(spec)
    require(spec.loader is not None, "accepted exact source lowerer unavailable")
    spec.loader.exec_module(module)
    require(blob_sha(LOWERER_SOURCE) == LOWERER_BLOB,
            "accepted source helper changed during import")
    return module


LOWERER = load_lowerer()


def source_spec():
    def linear(first, at_knot, last=None):
        return {"degree": 1, "knots": ["0", "0", "1", "1", "2", "2"],
                "controls": [first, at_knot, at_knot,
                             at_knot if last is None else last]}
    return {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "source_parameter_id": "source-time-t",
        "parameter_lo": "0", "parameter_hi": "2",
        "phase_turn_offset": "0", "phase_turn_rate": "1/4",
        "cos_splines": {
            "0": linear("0", "0", "100"),
            "1": linear("-20", "40"),
            "3": linear("25", "-50"),
            "5": linear("-17/2", "17"),
            "7": linear("-1/6", "1/3"),
        },
        "sin_splines": {
            "1": linear("520/3", "-260/3"),
            "3": linear("-250/3", "125/3"),
            "5": linear("49/3", "-49/6"),
            "7": linear("1/3", "-1/6"),
        },
    }


def frozen_case(corpus):
    require(corpus.get("schema") == "radicadsac-pb00701-finite-owner-corpus/54.0",
            "frozen source corpus schema changed")
    rows = corpus.get("cases")
    require(isinstance(rows, list) and len(rows) == 121 and
            len({row["id"] for row in rows}) == 121,
            "frozen 121-case corpus denominator or IDs changed")
    refused = [r for r in rows if
               [SECOND_OWNER, "BLOCKED", REFUSAL]
               in r["expected"]["observed"]["spans"]]
    require(len(refused) == 11 and
            sum(r["kind"] == "HARVESTED" for r in refused) == 1 and
            sum(r["kind"] == "COMPOSITE_TAIL" for r in refused) == 10,
            "11 original V43 refusal dispositions changed")
    matches = [r for r in rows if r["id"] == CASE_ID]
    require(len(matches) == 1, "V16 tail100 source missing or duplicated")
    row = matches[0]
    require(row.get("kind") == "COMPOSITE_TAIL" and
            row.get("origin") == "verify_pb00701_v16",
            "V16 original-producing provenance changed")
    require(json_canonical(row.get("spec")) == json_canonical(source_spec()),
            "original V16 B-spline, knots, phase or source identity changed")
    require(json_canonical(row.get("expected")) == json_canonical({
        "id": CASE_ID,
        "observed": {"status": "BLOCKED", "spans": [
            [FIRST_OWNER, "CERTIFIED", None],
            [SECOND_OWNER, "BLOCKED", REFUSAL],
        ]},
        "v54_disposition": "BLOCKED",
    }), "historical V16/V43 owners or blocked disposition changed")
    return row


def exact_original_pieces(source):
    require(set(source["cos_splines"]) == {"0", "1", "3", "5", "7"} and
            set(source["sin_splines"]) == {"1", "3", "5", "7"},
            "unaccounted source harmonic")
    for channel in ("cos_splines", "sin_splines"):
        for harmonic, spline in source[channel].items():
            a, b, c, d = map(LOWERER.rational, spline["controls"])
            require(b == c, "original physical source knot altered")
            first = LOWERER.linear_piece(source, channel, harmonic, Q(0), Q(1))
            second = LOWERER.linear_piece(source, channel, harmonic, Q(1), Q(2))
            require(first == (a, b - a) and
                    second == (c + (c - d), d - c),
                    "original V16 two-piece polynomial lowering mismatched")
            require(LOWERER.evaluate_poly(first, Q(1)) ==
                    LOWERER.evaluate_poly(second, Q(1)),
                    "source polynomial discontinuity at physical knot")
    require(LOWERER.rational(source["phase_turn_offset"]) == 0 and
            LOWERER.rational(source["phase_turn_rate"]) == Q(1, 4) and
            LOWERER.rational(source["parameter_lo"]) == 0 and
            LOWERER.rational(source["parameter_hi"]) == 2 and
            source["source_parameter_id"] == "source-time-t",
            "V16 exact physical parameter or phase changed")


def poly_add(a, b):
    return tuple((a[i] if i < len(a) else Q(0)) +
                 (b[i] if i < len(b) else Q(0))
                 for i in range(max(len(a), len(b))))


def poly_scale(a, q):
    return tuple(q * x for x in a)


def poly_times_x(a):
    return (Q(0),) + tuple(a)


def chebyshev():
    # T_n(x)=cos(n*theta), sin(n*theta)=sin(theta)*U_(n-1)(x).
    t = [(Q(1),), (Q(0), Q(1))]
    u = [(Q(1),), (Q(0), Q(2))]
    for n in range(2, 8):
        t.append(poly_add(poly_scale(poly_times_x(t[-1]), 2),
                          poly_scale(t[-2], -1)))
        u.append(poly_add(poly_scale(poly_times_x(u[-1]), 2),
                          poly_scale(u[-2], -1)))
    return t, u


def exact_coefficients(source):
    # Read the accepted original exact lowerer, not a replacement trigonometric
    # function and not an inferred proof owner.
    c0 = LOWERER.linear_piece(source, "cos_splines", "0", Q(1), Q(2))
    require(c0 == (Q(-100), Q(100)),
            "V16 original affine source tail changed")
    c, sn = {}, {}
    for k in (1, 3, 5, 7):
        cp = LOWERER.linear_piece(source, "cos_splines", str(k), Q(1), Q(2))
        sp = LOWERER.linear_piece(source, "sin_splines", str(k), Q(1), Q(2))
        require(cp[1] == 0 and sp[1] == 0,
                "original physical tail not constant-coefficient harmonics")
        c[k], sn[k] = cp[0], sp[0]
    require(c == {1: Q(40), 3: Q(-50), 5: Q(17), 7: Q(1, 3)} and
            sn == {1: Q(-260, 3), 3: Q(125, 3),
                   5: Q(-49, 6), 7: Q(-1, 6)},
            "V16 original second-span harmonic coefficients changed")

    t, u = chebyshev()
    a = (Q(0),)
    b = (Q(0),)
    for n in (1, 3, 5, 7):
        a = poly_add(a, poly_scale(t[n], c[n]))
        b = poly_add(b, poly_scale(u[n - 1], sn[n]))
    require(a == (Q(0), Q(818, 3), Q(0), Q(-1564, 3),
                  Q(0), Q(704, 3), Q(0), Q(64, 3)) and
            b == (Q(-409, 3), Q(0), Q(782, 3), Q(0),
                  Q(-352, 3), Q(0), Q(-32, 3)),
            "V16 exact Chebyshev expansion changed")
    require(a == poly_scale(poly_times_x(b), -2),
            "V16 common Chebyshev factor not derived from original source")
    p = tuple(-3 * b[2 * j] for j in range(4))
    require(p == (Q(409), Q(-782), Q(352), Q(32)),
            "original Chebyshev multiplier polynomial changed")
    # Let c=cos(theta)=-u and v=sin(theta). Thus
    # A(c)+vB(c)=-(2u+v)*P(u^2)/3, retaining all 8 harmonics.
    return c, sn, p


def poly_eval(coeffs, x):
    return sum(q * x**i for i, q in enumerate(coeffs))


def exact_proof(c, sn, p):
    dp = tuple((i + 1) * p[i + 1] for i in range(3))
    ddp = tuple((i + 1) * dp[i + 1] for i in range(2))
    w_coeffs = tuple(sum(p[k] * comb(k, j) * (-1)**j
                          for k in range(j, 4)) for j in range(4))
    require(w_coeffs == (Q(11), Q(-18), Q(448), Q(-32)),
            "V16 P(1-w) expansion does not match source")
    # For z in [0,1], w=1-z in [0,1]:
    # P=11-18w+448w²-32w³>=11-18w+416w²>=4495/416>0.
    require(Q(11) - Q(81, 416) == Q(4495, 416) > 0 and
            poly_eval(ddp, Q(0)) == 704 and
            poly_eval(ddp, Q(1)) == 896,
            "V16 positive P and convexity preconditions failed")
    require(poly_eval(p, Q(1, 2)) == 110 and
            poly_eval(p, Q(3, 4)) == 34 and
            poly_eval(p, Q(1)) == 11 and
            poly_eval(dp, Q(1, 2)) == -406 and
            poly_eval(dp, Q(7, 8)) == -Q(185, 2),
            "V16 rational interval and derivative controls failed")

    # Quadrant: theta=pi*s/2 in [pi/2,pi], u=-cos(theta)>=0,
    # v=sin(theta)>=0, u²+v²=1, z=u² increases from 0 to 1.
    # sqrt(2) in (7/5,3/2) via positive rational squares;
    # hence u(5/4)=sin(pi/8)>3/8, v>=sqrt(2)/2>7/10
    # on [5/4,3/2], and z(7/4)=cos²(pi/8) in (3/4,7/8).
    require(Q(7, 5)**2 < 2 < Q(3, 2)**2 and
            Q(23, 16)**2 > 2 and
            (Q(3, 8)**2 == (2 - Q(23, 16)) / 4) and
            Q(7, 10)**2 < Q(1, 2) and
            (2 + Q(3, 2)) / 4 == Q(7, 8),
            "rational eighth-angle interval guards failed")

    # P' grows on [0,1], yet P'(7/8)<0; P decreases on [0,7/8].
    # [1,5/4]: z<1/2, P>=110, 2u+v>=1, 100(s-1)<=25.
    left_upper = Q(25) - Q(110, 3)
    require(left_upper == -Q(35, 3) < 0,
            "V16 left source interval no longer strictly negative")
    # [5/4,3/2]: P>=110, u>3/8, v>=sqrt(2)/2>7/10.
    mid_left_upper = Q(50) - (Q(110, 3) * Q(29, 20))
    require(mid_left_upper == -Q(19, 6) < 0,
            "V16 second negative source interval proof failed")
    # At 3/2: F=50-55sqrt(2)<0 as sqrt(2)>1.
    require(Q(50) - Q(55) < 0, "V16 crossing left endpoint sign failed")

    # [7/4,2]: z>3/4, P(z)<=max(P(3/4),P(1))=34 by
    # convexity. Cauchy-Schwarz: 2u+v<=sqrt(5)<3.
    right_lower = Q(75) - Q(34)
    require(Q(5) < Q(9) and right_lower == 41 > 0,
            "V16 right tail positivity proof failed")

    # [3/2,7/4]: 1/2<=z<7/8, P'>0 is FALSE; P'<0,
    # P>0 and P<=110. For G=(2u+v)*P(z)/3:
    # dG/dtheta = ((2v-u)P + (2u+v)*2uv*P')/3.
    # 2v-u decreases on quadrant u>=v and is <=sqrt(2)/2<3/4.
    # Hence dG/dtheta < (3/4)*110/3=55/2.
    # F'=100-(pi/2)*dG/dtheta >100-55*pi/4
    # >100-55*(22/7)/4=795/14>0.
    derivative_lower = Q(100) - Q(55, 4) * Q(22, 7)
    require(poly_eval(dp, Q(7, 8)) < 0 and
            derivative_lower == Q(795, 14) > 0,
            "V16 crossing derivative strict bound failed")

    # Endpoint source derivatives include the C0'=100 term.
    left_theta = -sum(n*c[n] * (1 if n % 4 == 1 else -1)
                      for n in (1, 3, 5, 7))
    right_theta = -sum(n*sn[n] for n in (1, 3, 5, 7))
    require(left_theta == -Q(818, 3) and
            right_theta == Q(11, 3) and
            Q(100) - Q(818, 3) * Q(3, 2) < 0,
            "V16 endpoint derivative signs not established")
    # F'(1)=100-409*pi/3<0 (pi>3), F'(2)=100+11*pi/6>0.
    # Combined with F'>795/14 in the crossing bracket, the
    # full span is genuinely nonmonotone despite a unique simple root.
    return {
        "exact_chebyshev_factor": "-(2*u+v)*P(u^2)/3",
        "P_z_ascending": [str(q) for q in p],
        "P_1_minus_w_ascending": [str(q) for q in w_coeffs],
        "strict_P_lower_bound": "4495/416",
        "P_prime_at_half": str(poly_eval(dp, Q(1, 2))),
        "P_prime_at_seven_eighths": str(poly_eval(dp, Q(7, 8))),
        "negative_source_interval_bounds": [
            {"span": ["1", "5/4"], "upper": str(left_upper)},
            {"span": ["5/4", "3/2"], "strict_upper": str(mid_left_upper)},
            {"at": "3/2", "value": "50-55*sqrt(2)", "sign": "NEGATIVE"},
        ],
        "positive_source_interval_bound": {
            "span": ["7/4", "2"], "strict_lower": str(right_lower)},
        "crossing_interval": ["3/2", "7/4"],
        "strict_crossing_derivative_lower": str(derivative_lower),
        "source_endpoint_values": ["-409/3", "278/3"],
        "source_endpoint_derivatives": ["100-409*pi/3", "100+11*pi/6"],
        "derivative_sign_at_source_endpoints": ["NEGATIVE", "POSITIVE"],
        "complete_physical_sign_cells": ["NEGATIVE", "POSITIVE"],
        "single_root_multiplicity": 1,
        "single_root_direction": "NEGATIVE_TO_POSITIVE",
        "genuinely_nonmonotone_full_span": True,
    }


def analyze(corpus):
    row = frozen_case(corpus)
    source = row["spec"]
    exact_original_pieces(source)
    c, sn, p = exact_coefficients(source)
    proof = exact_proof(c, sn, p)
    return {
        "schema": SCHEMA,
        "evidence_class": "DETERMINISTIC_EXACT_SOURCE_BOUND_SINGLE_CASE_ONLY",
        "historical_v54_cases": 121,
        "historical_v43_refusals": 11,
        "case_id": CASE_ID,
        "source_parameter_id": "source-time-t",
        "original_physical_source_span": ["1", "2"],
        "historical_first_owner": FIRST_OWNER,
        "historical_second_owner": SECOND_OWNER,
        "historical_second_span_refusal": REFUSAL,
        "historical_whole_v54_disposition": "BLOCKED",
        "classification": "EXACTLY_ONE_SIMPLE_CROSSING_GLOBALLY_NONMONOTONE",
        "exact_distinct_open_roots": 1,
        "root_isolation_source_open_interval": ["3/2", "7/4"],
        "proof": proof,
        "historical_v54_dispositions_changed": False,
        "general_v43_event_or_child_composition_theorem_claimed": False,
        "pb007_mc_b_mc1_native_brep_step_production_claimed": False,
    }


def validate_report(report, corpus):
    require(json_canonical(report) == json_canonical(analyze(corpus)),
            "submitted V16 certificate differs from exact pinned source replay")


def authority_contract(authority, programme, domain):
    require(authority["programme"] == "MC-1" and
            authority["capability_status"] == "NOT_ESTABLISHED" and
            authority["production_authorized"] is False,
            "MC-1 production authority unexpectedly promoted")
    require(programme["capability_status"] == "NOT_ESTABLISHED" and
            programme["production_authorized"] is False and
            any(g["id"] == "MC-B" and g["state"] == "NOT_ESTABLISHED"
                for g in programme["gates"]),
            "MC-B capability unexpectedly promoted")
    require(len(domain["coverage_rule"]["required_operation_ids"]) == 26,
            "26-operation domain denominator changed")


def contract():
    require(blob_sha(CORPUS) == CORPUS_BLOB, "frozen v54 corpus Git blob drifted")
    require(blob_sha(LOWERER_SOURCE) == LOWERER_BLOB,
            "accepted exact source lowerer Git blob drifted")
    authority_contract(load_json(AUTHORITY), load_json(PROGRAMME),
                       load_json(DOMAIN))
    return analyze(load_json(CORPUS))


def self_test():
    corpus = load_json(CORPUS)
    report = analyze(corpus)
    validate_report(report, corpus)
    require(report["exact_distinct_open_roots"] == 1 and
            report["proof"]["strict_crossing_derivative_lower"] == "795/14" and
            report["proof"]["complete_physical_sign_cells"] ==
            ["NEGATIVE", "POSITIVE"],
            "V16 exact crossing classification changed")

    def reject_source(mutate, label):
        forged = copy.deepcopy(corpus)
        row = next(r for r in forged["cases"] if r["id"] == CASE_ID)
        mutate(row)
        try:
            analyze(forged)
        except (ValueError, KeyError, TypeError, IndexError):
            return
        raise AssertionError("forged V16 original source accepted: " + label)

    reject_source(lambda r: r["spec"].__setitem__("phase_turn_rate", "1/2"), "phase rate")
    reject_source(lambda r: r["spec"].__setitem__("phase_turn_offset", "1/4"), "phase offset")
    reject_source(lambda r: r["spec"].__setitem__("source_parameter_id", "forged"), "source ID")
    reject_source(lambda r: r.__setitem__("origin", "V19"), "original provenance")
    reject_source(lambda r: r["spec"]["cos_splines"]["0"]["controls"].__setitem__(3, "99"),
                  "affine tail bias")
    reject_source(lambda r: r["spec"]["cos_splines"]["1"]["controls"].__setitem__(0, "-19"),
                  "first physical source span")
    for channel in ("cos_splines", "sin_splines"):
        for harmonic in source_spec()[channel]:
            reject_source(lambda r, c=channel, h=harmonic:
                          r["spec"][c][h]["controls"].__setitem__(
                              2, str(Q(r["spec"][c][h]["controls"][2]) + Q(1))),
                          channel + harmonic + " tail coefficient")
    reject_source(lambda r: r["spec"]["cos_splines"]["7"]["knots"].__setitem__(3, "3/2"),
                  "physical source knot")
    reject_source(lambda r: r["spec"]["sin_splines"]["5"].__setitem__("degree", True),
                  "bool numeric degree")
    reject_source(lambda r: r["spec"]["sin_splines"]["3"].__setitem__("degree", 0),
                  "changed spline degree")
    reject_source(lambda r: r["spec"]["cos_splines"].__setitem__(
                      "9", {"degree": 0, "knots": ["0", "1", "2"],
                            "controls": ["1", "1"]}), "extra harmonic")
    reject_source(lambda r: r["expected"]["observed"]["spans"][0].__setitem__(
                      1, "BLOCKED"), "original V16 certification")
    reject_source(lambda r: r["expected"]["observed"]["spans"][1].__setitem__(
                      1, "CERTIFIED"), "historical V43 refusal")
    reject_source(lambda r: r["expected"].__setitem__(
                      "v54_disposition", "CERTIFIED"), "historical v54 outcome")

    def reject_report(mutate, label):
        forged = copy.deepcopy(report)
        mutate(forged)
        try:
            validate_report(forged, corpus)
        except ValueError:
            return
        raise AssertionError("forged V16 proof accepted: " + label)

    reject_report(lambda r: r.__setitem__("exact_distinct_open_roots", 0), "root omission")
    reject_report(lambda r: r.__setitem__("root_isolation_source_open_interval",
                                          ["1", "2"]), "weakened root bracket")
    reject_report(lambda r: r["proof"].__setitem__(
                      "P_z_ascending", ["409", "-782", "352", "33"]), "wrong Chebyshev P")
    reject_report(lambda r: r["proof"].__setitem__(
                      "strict_P_lower_bound", "0"), "lost strict P proof")
    reject_report(lambda r: r["proof"].__setitem__(
                      "strict_crossing_derivative_lower", "0"), "lost simple root")
    reject_report(lambda r: r["proof"].__setitem__(
                      "complete_physical_sign_cells", ["POSITIVE", "NEGATIVE"]),
                  "reversed crossing")
    reject_report(lambda r: r["proof"].__setitem__(
                      "genuinely_nonmonotone_full_span", False), "false monotone claim")
    reject_report(lambda r: r.__setitem__(
                      "general_v43_event_or_child_composition_theorem_claimed", True),
                  "unsupported general V43 certificate")
    reject_report(lambda r: r.__setitem__(
                      "pb007_mc_b_mc1_native_brep_step_production_claimed", True),
                  "unsupported engineering promotion")

    authority = load_json(AUTHORITY)
    programme = load_json(PROGRAMME)
    domain = load_json(DOMAIN)
    for label, src, mutate in (
        ("production", authority, lambda a: a.__setitem__("production_authorized", True)),
        ("MC-B", programme, lambda p: p.__setitem__("capability_status", "ACCEPTED")),
        ("domain", domain, lambda d: d["coverage_rule"]["required_operation_ids"].pop()),
    ):
        forged = copy.deepcopy(src)
        mutate(forged)
        try:
            authority_contract(forged if label == "production" else authority,
                               forged if label == "MC-B" else programme,
                               forged if label == "domain" else domain)
        except (ValueError, KeyError):
            continue
        raise AssertionError("forged MC-1 authority accepted: " + label)

    print("PASS: pinned original 121-case V16 and 11 historical V43 refusals")
    print("PASS: original two-piece B-spline channels, knot continuity and phase")
    print("PASS: exact 8-harmonic Chebyshev factor and source-bound interval signs")
    print("PASS: single simple crossing (3/2,7/4), nonmonotone global source")
    print("PASS: original source, proof and MC-1 authority adversarial mutations")
    print(json.dumps(report, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    options = parser.parse_args()
    if not (options.contract or options.self_test):
        parser.error("choose --contract and/or --self-test")
    if options.contract:
        print("PASS: frozen blob, exact source lowerer, authority and domain controls")
        print(json.dumps(contract(), sort_keys=True))
    if options.self_test:
        self_test()


if __name__ == "__main__":
    main()
