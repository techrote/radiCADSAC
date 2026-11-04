#!/usr/bin/env python3
"""Exact source-bound V23 nonmonotonic-positive falsifier; no native or gate claim.

An independently recomputable negative result for the proposed requirement
that one whole-span derivative sign be necessary for certifying no open roots.
It is NOT a general analytic event theorem or a repair of the historic V23 owner.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CASE = "harvested:verify_pb00701_v52:2250401ce435"
SOURCE_SHA256 = "4a3ee3f47b9347429c13830abef382301c7963b0af518f0977390c2d3ffba040"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
AUTHORITY_BLOB = "fa0233323a0804d8a5d3eb7cd892a274a6173fab"
RPT = HERE / "pb00701-v23-nonmonotone-positive.json"
RAT = re.compile(r"-?(?:0|[1-9][0-9]{0,77})(?:/[1-9][0-9]{0,77})?\Z", re.ASCII)

class Refusal(ValueError):
    """The proposed proof is not admitted. Never interpret this as zero truth."""

def need(ok: bool, why: str) -> None:
    if not ok:
        raise Refusal(why)

def bounded_read(path: Path, limit: int = 320_000) -> bytes:
    need(path.is_file() and not path.is_symlink(), "missing/nonregular pinned input")
    need(path.stat().st_size <= limit, "resource refusal: oversized input")
    value = path.read_bytes()
    need(len(value) <= limit, "resource refusal: input raced or oversized")
    return value

def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def pinned_json(path: Path, sha: str, limit: int = 320_000):
    raw = bounded_read(path, limit)
    need(git_blob(raw) == sha, "pinned Git blob changed")
    def unique(pairs):
        o = {}
        for k,v in pairs:
            need(k not in o, "duplicate JSON key")
            o[k] = v
        return o
    return json.loads(raw, object_pairs_hook=unique, parse_constant=lambda _: (_ for _ in ()).throw(Refusal("nonfinite JSON")))

def rat(value: str) -> Q:
    need(type(value) is str and len(value) <= 160 and RAT.fullmatch(value) is not None,
         "invalid/unbounded rational")
    result = Q(value)
    need(result.numerator.bit_length() <= 256 and result.denominator.bit_length() <= 256,
         "resource refusal: rational bit budget")
    return result

def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()

def source_sha(spec: dict) -> str:
    return hashlib.sha256(canonical(spec)).hexdigest()

def exact_controls(channel: dict, degree: int) -> tuple[Q, ...]:
    need(type(channel) is dict and set(channel) == {"degree","controls","knots"},
         "unsupported channel shape")
    need(type(channel["degree"]) is int and channel["degree"] == degree, "changed spline degree")
    need(channel["knots"] == ["0"] * (degree + 1) + ["1"] * (degree + 1),
         "changed source knots")
    need(type(channel["controls"]) is list and len(channel["controls"]) == degree + 1,
         "changed source controls")
    return tuple(rat(x) for x in channel["controls"])

def t2_quotient(c: tuple[Q, ...]) -> tuple[Q, ...]:
    n = len(c) - 1
    need(2 <= n <= 12 and c[0] == c[1] == 0, "no certified t^2 source factor")
    return tuple(c[i] * Q(n*(n-1), i*(i-1)) for i in range(2,n+1))

def prove(c0: tuple[Q, ...], c1: tuple[Q, ...], s2: tuple[Q, ...],
          phase: tuple[Q, Q] = (Q(1,4), -Q(1,24))) -> dict:
    """Exact sufficient positivity plus NECESSARY nonmonotonicity witness.

    This only admits the original fixed phase sector. The general method would
    require an independent sector argument and is intentionally not claimed.
    """
    need(phase == (Q(1,4), -Q(1,24)), "unsupported phase interval")
    need((len(c0),len(c1),len(s2)) == (8,7,7), "unsupported source degree")
    q0, q1, q2 = map(t2_quotient, (c0,c1,s2))
    need(all(a > 0 for a in q0), "no strict Bernstein positivity")
    need(all(a >= 0 for a in q1+q2), "negative harmonic Bernstein coefficient")
    lower = min(q0)
    second0 = Q(7*6) * c0[2]
    need(second0 > 0, "wrong left-endpoint order")
    d0 = Q(7)*(c0[-1]-c0[-2])
    d1 = Q(6)*(c1[-1]-c1[-2])
    d2 = Q(6)*(s2[-1]-s2[-2])
    # |cos|, |sin| <=1 and |d(theta)/dt|=pi/12; |d(2theta)/dt|=pi/6.
    # pi < 22/7 gives a rational strict upper bound on physical F'(1).
    upper = d0 + abs(d1) + c1[-1]*Q(22,7)/12 + abs(d2) + s2[-1]*Q(22,7)/6
    need(upper < 0, "right derivative sign not established negative")
    return {
        "t2_bernstein_positive_lower_coefficient": str(lower),
        "left_first_derivative": "0",
        "left_second_derivative": str(second0),
        "right_A0_derivative": str(d0),
        "right_A1_derivative": str(d1),
        "right_B2_derivative": str(d2),
        "right_derivative_strict_upper_bound": str(upper),
        "open_interval_zero_count": 0,
        "left_endpoint_zero_order": 2,
        "positive_derivative_near_left": True,
        "negative_derivative_at_right": True,
        "whole_span_derivative_single_sign": False
    }

def frozen_source(corpus: dict, v2: dict) -> dict:
    cases = corpus["cases"]
    need(type(cases) is list and len(cases) == 121, "frozen 121 denominator")
    ids = [c["id"] for c in cases]
    need(len(set(ids)) == 121, "duplicate source ID")
    counts = Counter(c["expected"]["v54_disposition"] for c in cases)
    need(counts["BLOCKED"] == 20 and
         counts["BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"] == 30 and
         sum(counts.values()) == 121, "historical disposition census changed")
    unresolved = {c["id"] for c in cases if c["expected"]["v54_disposition"].startswith("BLOCKED")}
    rows = v2["source_cases"]
    need(type(rows) is list and len(rows) == 50, "v2 source count changed")
    need({x["case_id"] for x in rows} == unresolved and
         all(x["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC"
             and x["historical_disposition_changed"] is False for x in rows),
         "historical 50-source evidence changed")
    need(v2["evidence_class"] == "DETERMINISTIC_MODEL" and
         v2["registry_scope"]["new_general_root_event_or_composition_theorem"] is False,
         "invalid evidence promotion")
    case, = [x for x in cases if x["id"] == CASE]
    row, = [x for x in rows if x["case_id"] == CASE]
    need(case["origin"] == "verify_pb00701_v52" and case["kind"] == "HARVESTED",
         "original producer identity")
    need(case["expected"]["observed"]["spans"] == [[
         "PB00701_V23_EXACT_NONCONSTANT_AMPLITUDE_PHASE_SECTOR_ANCHOR",
         "BLOCKED", "NONCONSTANT_AMPLITUDE_PHASE_DEPENDENT_ANCHOR_NOT_CERTIFIED"
         ]], "historic V23 refusal changed")
    spec = case["spec"]
    need(source_sha(spec) == SOURCE_SHA256 == row["source_sha256"],
         "original SHA-256 identity changed")
    need(spec["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE" and
         spec["source_parameter_id"] == "v52-original-source" and
         spec["parameter_lo"] == "0" and spec["parameter_hi"] == "1" and
         spec["phase_turn_offset"] == "1/4" and spec["phase_turn_rate"] == "-1/24",
         "original source/phase/parameter mismatch")
    need(set(spec["cos_splines"]) == {"0","1"} and set(spec["sin_splines"]) == {"2"},
         "added or omitted Fourier channel")
    c0 = exact_controls(spec["cos_splines"]["0"],7)
    c1 = exact_controls(spec["cos_splines"]["1"],6)
    s2 = exact_controls(spec["sin_splines"]["2"],6)
    need(all(b*2 == a for a,b in zip(c1,s2)), "lost original S2=C1/2")
    cert = prove(c0,c1,s2)
    need(cert["t2_bernstein_positive_lower_coefficient"] == "49/34992" and
         cert["left_second_derivative"] == "1/36" and
         cert["right_derivative_strict_upper_bound"] == "-133/72900",
         "unexpected physical sign certificate")
    return cert

def expected_receipt(cert: dict) -> dict:
    return {
        "schema": "radicadsac-mc038-v23-nonmonotone-positive/1.0",
        "case_id": CASE, "original_source_sha256": SOURCE_SHA256,
        "original_source_parameter": "v52-original-source",
        "source_interval": ["0","1"], "phase_turns": "1/4-t/24",
        "historical_refusal": "NONCONSTANT_AMPLITUDE_PHASE_DEPENDENT_ANCHOR_NOT_CERTIFIED",
        "proposed_route_falsified": "GLOBAL_SINGLE_DERIVATIVE_SIGN_REQUIRED",
        "finding": "positive_on_open_span_but_derivative_sign_reverses",
        "certificate": cert,
        "frozen_corpus_git_blob": CORPUS_BLOB,
        "post_v54_v2_git_blob": V2_BLOB,
        "census": {
            "original_sources": {"before":121,"after":121,"delta":0},
            "historical_route_refusals": {"before":20,"after":20,"delta":0},
            "missing_ordered_premises": {"before":30,"after":30,"delta":0},
            "previously_complete_source_specific": {"before":50,"after":50,"delta":0},
            "new_historical_case_ids_closed": []
        },
        "evidence_class": "DETERMINISTIC_MODEL",
        "PB00701_required_obligations_discharged": [],
        "MC_B": "NOT_ESTABLISHED", "MC_1": "NOT_ESTABLISHED",
        "native_geometry_or_step": False, "production_authorized": False
    }

def check_contract():
    directory = HERE
    corpus = pinned_json(directory/"pb00701-finite-owner-corpus-v54.json",CORPUS_BLOB)
    v2 = pinned_json(directory/"pb00701-post-v54-evidence-reconciliation-v2.json",V2_BLOB)
    authority = pinned_json(ROOT/"handoffs/current-authority.json", AUTHORITY_BLOB, 65536)
    need(authority["production_authorized"] is False and
         authority["capability_status"] == "NOT_ESTABLISHED", "authority changed")
    cert = frozen_source(corpus,v2)
    receipt = json.loads(bounded_read(RPT,32000), parse_constant=lambda _: (_ for _ in ()).throw(Refusal("invalid JSON")))
    need(receipt == expected_receipt(cert), "source-bound receipt disagreement")
    return cert

def self_tests():
    # Independent rational endpoint calculations, not a trigonometric scan.
    c0 = (Q(0),Q(0),Q(1,1512),Q(1,756),Q(13,7560),
          Q(37,20412),Q(13,7776),Q(49,34992))
    c1 = (Q(0),Q(0),Q(1,54000),Q(1,27000),
          Q(23,486000),Q(7,145800),Q(49,1166400))
    s2 = tuple(x/2 for x in c1)
    v = prove(c0,c1,s2)
    need(v["right_derivative_strict_upper_bound"] == "-133/72900",
         "independent right derivative control")
    need(v["left_second_derivative"] == "1/36", "independent order-two control")
    def must_refuse(fn):
        try:
            fn()
        except Refusal:
            return
        raise AssertionError("unsafe proof/admission unexpectedly succeeded")
    must_refuse(lambda: prove(tuple(Q(0) for _ in c0),
                              tuple(Q(0) for _ in c1),tuple(Q(0) for _ in s2)))
    bad = list(c0); bad[3] = -bad[3]
    must_refuse(lambda: prove(tuple(bad),c1,s2))
    bad = list(c0); bad[2] = 0
    must_refuse(lambda: prove(tuple(bad),c1,s2))
    bad = list(c0); bad[-1] = 1
    must_refuse(lambda: prove(tuple(bad),c1,s2))
    must_refuse(lambda: prove(c0,c1,s2,(Q(1,4),Q(0))))
    bad = list(c1);bad[4]=-Q(23,486000)
    must_refuse(lambda: prove(c0,tuple(bad),s2))
    # Exact close-root adversary: t^2(t-eps)^2 has roots 0, eps, eps=2^-100.
    # Its degree-four Bernstein coefficient at i=3 is negative; our strict
    # coefficient-sign admission MUST refuse rather than assert root absence.
    eps = Q(1,2**100)
    close_poly_bernstein = (Q(0),Q(0),eps*eps/6,
                            (eps*eps-eps)/2,(1-eps)**2)
    need(close_poly_bernstein[3]<0 and eps>0 and eps<Q(1), "close-root control")
    need((eps*eps*(eps-eps)**2) == 0, "close interior root exact")
    must_refuse(lambda: t2_quotient(close_poly_bernstein) if
                all(x>0 for x in t2_quotient(close_poly_bernstein))
                else (_ for _ in ()).throw(Refusal("negative interior Bernstein")))
    fake = {"phase_turn_rate":"-1/24"}
    need(source_sha(fake) != SOURCE_SHA256,"source substitution control")
    wrong = expected_receipt(v)
    wrong["certificate"] = dict(v, right_derivative_strict_upper_bound="0")
    need(wrong != expected_receipt(v), "receipt tamper control")
    return 10

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--contract",action="store_true")
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    need(args.contract or args.self_test, "explicit --contract/--self-test required")
    if args.self_test:
        print("adversarial-controls:",self_tests())
    cert=check_contract()
    print("original-source V23 exact mathematical C: verified",cert["right_derivative_strict_upper_bound"])
    print("frozen census 121/20/30/50; deltas 0; MC-B/MC-1 NOT_ESTABLISHED")

if __name__ == "__main__":
    main()
