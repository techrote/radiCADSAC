#!/usr/bin/env python3
"""Exact physical-source sign and turning controls for one frozen V13/V43 refusal.

Deterministic case-specific research only. Not general V43 ordered-root authority,
PB-007-01, MC-B/MC-1, native geometry, B-rep, STEP or production authorization.
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
CASE_ID = "composite:PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC:tail0"
FIRST_OWNER = "PB00701_V13_EXACT_NONVANISHING_EVEN_MULTIPLIER_MULTIHARMONIC"
SECOND_OWNER = "PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF"
REFUSAL = "CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED"
SCHEMA = "radicadsac-pb00701-v43-v13-even-factor-probe/1.0"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def blob_sha(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def load_lowerer():
    require(blob_sha(LOWERER_SOURCE) == LOWERER_BLOB,
            "accepted V43 exact source lowerer Git blob changed")
    spec = importlib.util.spec_from_file_location("accepted_v43_v13_source_lowerer",
                                                  LOWERER_SOURCE)
    module = importlib.util.module_from_spec(spec)
    require(spec.loader is not None, "V43 lowerer unavailable")
    spec.loader.exec_module(module)
    require(blob_sha(LOWERER_SOURCE) == LOWERER_BLOB,
            "source helper drifted during module import")
    return module


LOWERER = load_lowerer()


def expected_spec():
    def linear(controls):
        return {"degree": 1, "knots": ["0", "0", "1", "1", "2", "2"],
                "controls": controls}
    return {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "source_parameter_id": "source-time-t",
        "parameter_lo": "0", "parameter_hi": "2",
        "phase_turn_offset": "0", "phase_turn_rate": "1/4",
        "cos_splines": {
            "0": {"degree": 0, "knots": ["0", "1", "2"],
                  "controls": ["0", "0"]},
            "1": linear(["-5/6", "5/3", "5/3", "5/3"]),
            "3": linear(["-1/6", "1/3", "1/3", "1/3"]),
        },
        "sin_splines": {
            "1": linear(["1", "-1/2", "-1/2", "-1/2"]),
            "3": linear(["1/3", "-1/6", "-1/6", "-1/6"]),
        },
    }


def frozen_case(corpus):
    require(corpus.get("schema") ==
            "radicadsac-pb00701-finite-owner-corpus/54.0",
            "historical corpus schema changed")
    rows = corpus.get("cases")
    require(isinstance(rows, list) and len(rows) == 121 and
            len({r["id"] for r in rows}) == 121,
            "121-case historical corpus denominator or IDs changed")
    refused = [r for r in rows if
               [SECOND_OWNER, "BLOCKED", REFUSAL]
               in r["expected"]["observed"]["spans"]]
    require(len(refused) == 11 and
            sum(r["kind"] == "HARVESTED" for r in refused) == 1 and
            sum(r["kind"] == "COMPOSITE_TAIL" for r in refused) == 10,
            "11 original V43 refusal dispositions changed")
    matches = [r for r in rows if r["id"] == CASE_ID]
    require(len(matches) == 1, "frozen V13 original source missing or duplicated")
    row = matches[0]
    require(row.get("kind") == "COMPOSITE_TAIL" and
            row.get("origin") == "verify_pb00701_v13",
            "original V13 source provenance changed")
    require(row.get("spec") == expected_spec(),
            "original V13 B-spline/knot/phase/source identity changed")
    require(row.get("expected") == {
        "id": CASE_ID,
        "observed": {"status": "BLOCKED", "spans": [
            [FIRST_OWNER, "CERTIFIED", None],
            [SECOND_OWNER, "BLOCKED", REFUSAL],
        ]},
        "v54_disposition": "BLOCKED",
    }, "frozen V13 first-span owner or V43 refusal relabelled")
    return row


def original_pieces(source):
    require(set(source["cos_splines"]) == {"0", "1", "3"} and
            set(source["sin_splines"]) == {"1", "3"},
            "unaccounted original harmonic")
    expected = {
        ("cos_splines", "0"): ((Q(0), Q(0)), (Q(0), Q(0))),
        ("cos_splines", "1"): ((Q(-5, 6), Q(5, 2)), (Q(5, 3), Q(0))),
        ("cos_splines", "3"): ((Q(-1, 6), Q(1, 2)), (Q(1, 3), Q(0))),
        ("sin_splines", "1"): ((Q(1), Q(-3, 2)), (Q(-1, 2), Q(0))),
        ("sin_splines", "3"): ((Q(1, 3), Q(-1, 2)), (Q(-1, 6), Q(0))),
    }
    for (channel, harmonic), pair in expected.items():
        left = LOWERER.linear_piece(source, channel, harmonic, Q(0), Q(1))
        right = LOWERER.linear_piece(source, channel, harmonic, Q(1), Q(2))
        require((left, right) == pair,
                "original clamped V13 source channel polynomial changed")
        require(LOWERER.evaluate_poly(left, Q(1)) ==
                LOWERER.evaluate_poly(right, Q(1)),
                "original V13 physical source knot is discontinuous")
    require(LOWERER.rational(source["phase_turn_offset"]) == 0 and
            LOWERER.rational(source["phase_turn_rate"]) == Q(1, 4) and
            LOWERER.rational(source["parameter_lo"]) == 0 and
            LOWERER.rational(source["parameter_hi"]) == 2 and
            source["source_parameter_id"] == "source-time-t",
            "V13 original physical parameter or affine phase changed")
    return True


def exact_factor_coefficient_proof(source):
    # Derive the four constant coefficients from the ORIGINAL second span.
    # Don't use a replacement first-harmonic surrogate to classify V13.
    c1 = LOWERER.linear_piece(source, "cos_splines", "1", Q(1), Q(2))[0]
    c3 = LOWERER.linear_piece(source, "cos_splines", "3", Q(1), Q(2))[0]
    s1 = LOWERER.linear_piece(source, "sin_splines", "1", Q(1), Q(2))[0]
    s3 = LOWERER.linear_piece(source, "sin_splines", "3", Q(1), Q(2))[0]
    require((c1, c3, s1, s3) ==
            (Q(5, 3), Q(1, 3), Q(-1, 2), Q(-1, 6)),
            "unreviewed physical V13 harmonic coefficients")

    # cos(3θ)=4c³-3c; sin(3θ)=3v-4v³; v³=v(1-c²).
    # Hence F=A*c+B*c³+D*v+E*c²*v, c=cosθ, v=sinθ:
    a = c1 - 3*c3
    b = 4*c3
    d = s1 + 3*s3 - 4*s3
    e = 4*s3
    require((a, b, d, e) ==
            (Q(2, 3), Q(4, 3), Q(-1, 3), Q(-2, 3)),
            "triple-angle V13 exact coefficient reduction failed")
    require(a != 0 and b == 2*a and e == 2*d,
            "same strictly positive even multiplier not established")
    # F=(1+2c²)*((2/3)c-(1/3)v), not merely a root-count claim.
    # θ=πs/2 lies in [π/2,π]; u=-c>=0,v>=0,u²+v²=1.
    # (2u+v)²-(u²+v²)=3u²+4uv>=0, so 2u+v>=1.
    # Therefore inner factor=-(2u+v)/3<=-1/3;
    # 1+2c²>=1; consequently F<=-1/3<0 on closed [1,2].
    require(a == Q(2, 3) and d == Q(-1, 3) and Q(3) > 0,
            "strict V13 sign bound not established")
    theta_derivative_left = -c1 + 3*c3     # θ=π/2: sinθ=1,sin3θ=-1
    theta_derivative_right = -s1 - 3*s3    # θ=π: cosθ=cos3θ=-1
    require(theta_derivative_left == Q(-2, 3) and
            theta_derivative_right == Q(1),
            "exact physical endpoint derivatives changed")
    # Multiply the above by dθ/ds=π/2, positive. Opposite signs
    # disprove monotonicity and entail an interior turning point.
    return {
        "cos_c": str(a), "cos_cubed": str(b),
        "sin_linear_after_reduction": str(d),
        "sin_times_cos_squared": str(e),
        "positive_even_multiplier": "1+2*cos(theta)^2",
        "strict_even_multiplier_range": ["1", "3"],
        "inner_signed_factor": "(2*cos(theta)-sin(theta))/3",
        "strict_closed_source_upper_bound": "-1/3",
        "theta_over_pi_at_source_endpoints": ["1/2", "1"],
        "physical_source_values_at_endpoints": ["-1/3", "-2"],
        "theta_derivative_at_endpoints": ["-2/3", "1"],
        "source_derivative_at_endpoints": ["-pi/3", "pi/2"],
        "source_derivative_signs": ["NEGATIVE", "POSITIVE"],
        "interior_turning_point_exists": True,
    }


def analyze(corpus):
    row = frozen_case(corpus)
    source = row["spec"]
    original_pieces(source)
    proof = exact_factor_coefficient_proof(source)
    return {
        "schema": SCHEMA,
        "evidence_class": "DETERMINISTIC_EXACT_SOURCE_BOUND_SINGLE_CASE_ONLY",
        "historical_v54_cases": 121,
        "historical_v43_refusals": 11,
        "case_id": CASE_ID,
        "original_source_parameter_id": "source-time-t",
        "original_physical_source_span": ["1", "2"],
        "historical_first_owner": FIRST_OWNER,
        "historical_second_owner": SECOND_OWNER,
        "historical_second_span_refusal": REFUSAL,
        "historical_whole_v54_disposition": "BLOCKED",
        "classification": "STRICT_NEGATIVE_GENUINELY_NONMONOTONE_ROOT_FREE",
        "exact_distinct_roots_open": 0,
        "complete_physical_sign_cells": ["NEGATIVE"],
        "exact_factor_proof": proof,
        "historical_v54_dispositions_changed": False,
        "general_v43_ordered_event_or_composition_theorem_claimed": False,
        "mc_b_mc1_native_brep_step_or_production_claimed": False,
    }


def validate_report(report, corpus):
    require(report == analyze(corpus),
            "submitted V13 proof differs from exact source-bound replay")
    return True


def authority_contract(authority, programme, domain):
    require(authority["programme"] == "MC-1" and
            authority["capability_status"] == "NOT_ESTABLISHED" and
            authority["production_authorized"] is False,
            "MC-1 production authorization unexpectedly promoted")
    require(programme["capability_status"] == "NOT_ESTABLISHED" and
            programme["production_authorized"] is False and
            any(g["id"] == "MC-B" and g["state"] == "NOT_ESTABLISHED"
                for g in programme["gates"]),
            "MC-B capability unexpectedly promoted")
    require(len(domain["coverage_rule"]["required_operation_ids"]) == 26,
            "26-operation domain denominator changed")


def contract():
    require(blob_sha(CORPUS) == CORPUS_BLOB,
            "original 121-case v54 Git blob drifted")
    require(blob_sha(LOWERER_SOURCE) == LOWERER_BLOB,
            "accepted V43 degree-0/1 exact lowerer drifted")
    authority_contract(load_json(AUTHORITY), load_json(PROGRAMME),
                       load_json(DOMAIN))
    return analyze(load_json(CORPUS))


def self_test():
    corpus = load_json(CORPUS)
    result = analyze(corpus)
    validate_report(result, corpus)
    require(result["exact_distinct_roots_open"] == 0 and
            result["complete_physical_sign_cells"] == ["NEGATIVE"] and
            result["exact_factor_proof"]["strict_closed_source_upper_bound"] == "-1/3" and
            result["exact_factor_proof"]["source_derivative_signs"] ==
            ["NEGATIVE", "POSITIVE"], "V13 exact classification changed")

    def rejects_source(mutate, name):
        forged = copy.deepcopy(corpus)
        row = next(r for r in forged["cases"] if r["id"] == CASE_ID)
        mutate(row)
        try:
            analyze(forged)
        except (ValueError, KeyError, TypeError, IndexError):
            return
        raise AssertionError("forged V13 original source accepted: " + name)

    rejects_source(lambda r: r["spec"].__setitem__("phase_turn_rate", "1/2"),
                   "phase rate")
    rejects_source(lambda r: r["spec"].__setitem__("phase_turn_offset", "1/4"),
                   "phase offset")
    rejects_source(lambda r: r["spec"].__setitem__("source_parameter_id", "forged"),
                   "physical source identity")
    rejects_source(lambda r: r.__setitem__("origin", "v19"), "provenance")
    rejects_source(lambda r: r["spec"]["cos_splines"]["1"]["controls"].__setitem__(2, "3/2"),
                   "first harmonic cosine")
    rejects_source(lambda r: r["spec"]["cos_splines"]["3"]["controls"].__setitem__(3, "1/2"),
                   "third harmonic cosine")
    rejects_source(lambda r: r["spec"]["sin_splines"]["1"]["controls"].__setitem__(2, "1/2"),
                   "first harmonic sine")
    rejects_source(lambda r: r["spec"]["sin_splines"]["3"]["controls"].__setitem__(2, "1/6"),
                   "third harmonic sine")
    rejects_source(lambda r: r["spec"]["cos_splines"]["1"]["knots"].__setitem__(3, "3/2"),
                   "source physical knot")
    rejects_source(lambda r: r["spec"]["sin_splines"]["3"].__setitem__("degree", 0),
                   "unreviewed channel degree")
    rejects_source(lambda r: r["spec"]["cos_splines"].__setitem__(
        "2", {"degree": 0, "knots": ["0", "1", "2"], "controls": ["1", "1"]}),
        "unaccounted harmonic")
    rejects_source(lambda r: r["spec"]["cos_splines"]["0"]["controls"].__setitem__(1, "1"),
                   "unreviewed harmonic-zero bias")
    rejects_source(lambda r: r["expected"]["observed"]["spans"][0].__setitem__(
        1, "BLOCKED"), "historical V13 certification")
    rejects_source(lambda r: r["expected"]["observed"]["spans"][1].__setitem__(
        1, "CERTIFIED"), "historical V43 refusal")
    rejects_source(lambda r: r["expected"].__setitem__("v54_disposition", "CERTIFIED"),
                   "historical whole-source disposition")

    def rejects_report(mutate, name):
        forged = copy.deepcopy(result)
        mutate(forged)
        try:
            validate_report(forged, corpus)
        except ValueError:
            return
        raise AssertionError("forged V13 proof accepted: " + name)

    rejects_report(lambda r: r.__setitem__("exact_distinct_roots_open", 1),
                   "fabricated open root")
    rejects_report(lambda r: r.__setitem__("complete_physical_sign_cells", ["POSITIVE"]),
                   "reversed sign cell")
    rejects_report(lambda r: r["exact_factor_proof"].__setitem__(
        "positive_even_multiplier", "1-2*cos(theta)^2"), "nonpositive multiplier")
    rejects_report(lambda r: r["exact_factor_proof"].__setitem__(
        "strict_closed_source_upper_bound", "0"), "weakened strict margin")
    rejects_report(lambda r: r["exact_factor_proof"].__setitem__(
        "source_derivative_signs", ["NEGATIVE", "NEGATIVE"]), "forged monotonicity")
    rejects_report(lambda r: r.__setitem__(
        "general_v43_ordered_event_or_composition_theorem_claimed", True),
        "general V43 promotion")
    rejects_report(lambda r: r.__setitem__(
        "mc_b_mc1_native_brep_step_or_production_claimed", True),
        "unsupported engineering capability")

    authority = load_json(AUTHORITY)
    programme = load_json(PROGRAMME)
    domain = load_json(DOMAIN)
    for name, original, mutate in (
        ("production", authority, lambda x: x.__setitem__("production_authorized", True)),
        ("MC-B", programme, lambda x: x.__setitem__("capability_status", "ACCEPTED")),
        ("domain", domain, lambda x: x["coverage_rule"]["required_operation_ids"].pop()),
    ):
        forged = copy.deepcopy(original)
        mutate(forged)
        try:
            authority_contract(forged if name == "production" else authority,
                               forged if name == "MC-B" else programme,
                               forged if name == "domain" else domain)
        except (ValueError, KeyError):
            continue
        raise AssertionError("forged programme authority accepted: " + name)
    print("PASS: pinned V13 original source, two continuous physical spans and v54 refusal")
    print("PASS: exact 1+2cos² positive factor, strict negative sign and turning point")
    print("PASS: source, certificate and programme adversarial mutation controls")
    print(json.dumps(result, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    opts = parser.parse_args()
    if not (opts.contract or opts.self_test):
        parser.error("choose --contract and/or --self-test")
    if opts.contract:
        print("PASS: frozen corpus, exact lowerer, authority/domain controls")
        print(json.dumps(contract(), sort_keys=True))
    if opts.self_test:
        self_test()


if __name__ == "__main__":
    main()
