#!/usr/bin/env python3
"""Source-pinned original V9-tail100 Cayley algebraic-admission falsifier.

The classical infinite-monodromy lemma is mathematical, NOT machine formalized.
This verifier checks the precise frozen original, rational B-spline lowering,
Cayley algebra, source census and machine receipt. It does not solve a general
analytic event theorem or qualify native geometry.
"""
import argparse
import copy
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "pb00701-finite-owner-corpus-v54.json"
REGISTER = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
MACHINE = HERE / "pb00701-v9-cayley-monodromy-boundary-20261105.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
REGISTER_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
CASE_ID = "composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail100"
SRC_SHA = "cc13a39582060e763c573f2665b3ea3b6dfe8b76a6cb0fb77a7b0ec90cf6253a"
ROW_SHA = "6e122da708ff0c68a339e0bfa5daba1e5321cb79e15af9e27b63712fb1348b63"
SCHEMA = "radicadsac-v9-cayley-monodromy-boundary/1.0"

class Refusal(ValueError):
    pass

def require(condition, reason):
    if not condition:
        raise Refusal(reason)

def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("ascii")

def sha(obj):
    return hashlib.sha256(canon(obj)).hexdigest()

def gitblob(contents):
    return hashlib.sha1(b"blob " + str(len(contents)).encode("ascii")
                        + b"\x00" + contents).hexdigest()

def readp(path, pin):
    contents = path.read_bytes()
    require(gitblob(contents) == pin, "FROZEN_GIT_BLOB_DRIFT:" + path.name)
    return json.loads(contents)

def expected_spec():
    k0 = ["0", "1", "2"]
    k1 = ["0", "0", "1", "1", "2", "2"]
    return {
        "grammar": "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
        "source_parameter_id": "source-time-t",
        "parameter_lo": "0", "parameter_hi": "2",
        "phase_turn_offset": "0", "phase_turn_rate": "1/8",
        "cos_splines": {
            "0": {"degree": 1, "knots": k1, "controls": ["0", "0", "0", "100"]},
            "1": {"degree": 1, "knots": k1, "controls": ["-1/2", "1/2", "1/2", "1/2"]}
        },
        "sin_splines": {
            "1": {"degree": 0, "knots": k0, "controls": ["1", "1"]}
        }
    }

def source_parts(spec):
    """Extract original physical span coefficients, refusing altered source."""
    require(type(spec) is dict and spec == expected_spec(),
            "ORIGINAL_SOURCE_OR_PHASE_GRAMMAR_REFUSAL")
    require(sha(spec) == SRC_SHA, "CANONICAL_SOURCE_DIGEST_REFUSAL")
    cos0 = tuple(map(Q, spec["cos_splines"]["0"]["controls"]))
    cos1 = tuple(map(Q, spec["cos_splines"]["1"]["controls"]))
    sin1 = tuple(map(Q, spec["sin_splines"]["1"]["controls"]))
    require(cos0 == (0, 0, 0, 100)
            and cos1 == (Q(-1, 2), Q(1, 2), Q(1, 2), Q(1, 2))
            and sin1 == (1, 1), "RATIONAL_SPLINE_CONTROL_REFUSAL")
    # [0,0,1,1,2,2] is clamped degree 1 with first span [c0,c1]
    # and second span [c2,c3]; zero-degree [0,1,2] is piecewise constant.
    return {
        "left_cos0": (Q(0), Q(0)),
        "left_cos1": (Q(-1, 2), Q(1)),  # t-1/2
        "left_sin1": Q(1),
        "right_cos0": (Q(-100), Q(100)), # 100(t-1)
        "right_cos1": (Q(1, 2), Q(0)),
        "right_sin1": Q(1)
    }

def add(*polys):
    out = [Q(0)] * 3
    for p in polys:
        require(len(p) == 3, "POLYNOMIAL_DEGREE_REFUSAL")
        out = [a + b for a, b in zip(out, p)]
    return tuple(out)

def times(p, factor):
    return tuple(x * Q(factor) for x in p)

def polystr(p):
    return [str(x) for x in p]

def cayley_polynomials(parts):
    """D*F = (A(u)/pi)*atan(u) + B(u), D=1+u^2.

    u=tan(pi*t/8), theta=pi*t/4, t=(8/pi)*atan(u).
    Polynomial coefficients are exact rational, not sampled.
    """
    D = (Q(1), Q(0), Q(1))
    COS = (Q(1), Q(0), Q(-1))
    SIN = (Q(0), Q(2), Q(0))
    # For a*t+b, substitute a*(8/pi)*atan(u)+b.
    def lower(c0, c1, s):
        b, a = c0
        d, c = c1
        return (
            add(times(D, 8 * a), times(COS, 8 * c)),
            add(times(D, b), times(COS, d), times(SIN, s))
        )
    A0, B0 = lower(parts["left_cos0"], parts["left_cos1"],
                   parts["left_sin1"])
    A1, B1 = lower(parts["right_cos0"], parts["right_cos1"],
                   parts["right_sin1"])
    require(A0 == (Q(8), Q(0), Q(-8))
            and B0 == (Q(-1, 2), Q(2), Q(1, 2)),
            "FIRST_SPAN_CAYLEY_IDENTITY_REFUSAL")
    require(A1 == (Q(800), Q(0), Q(800))
            and B1 == (Q(-199, 2), Q(2), Q(-201, 2)),
            "SECOND_SPAN_CAYLEY_IDENTITY_REFUSAL")
    return [A0, B0, A1, B1]

def receipt(corpus, registry):
    rows = corpus["cases"]
    require(len(rows) == 121 and len({z["id"] for z in rows}) == 121,
            "FROZEN_121_DENOMINATOR")
    originals = {z["id"]: z for z in rows}
    bad = {cid for cid, z in originals.items()
           if z["expected"]["v54_disposition"] == "BLOCKED"}
    missing = {cid for cid, z in originals.items()
               if z["expected"]["v54_disposition"]
               == "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"}
    require(len(bad) == 20 and len(missing) == 30 and not bad & missing,
            "FROZEN_20_30_CENSUS")
    cases = registry["source_cases"]
    registration = {x["case_id"]: x for x in cases}
    require(len(cases) == 50 and len(registration) == 50
            and set(registration) == bad | missing, "V2_50_CASE_SET")
    for cid, x in registration.items():
        z = originals[cid]
        spec = z["spec"]
        require(x["source_sha256"] == sha(spec)
                and x["original_row_sha256"] == sha(z),
                "ORIGINAL_SOURCE_OR_ROW_PROVENANCE:" + cid)
        require(x["historical_v54_disposition"]
                == z["expected"]["v54_disposition"]
                and x["origin"] == z["origin"]
                and x["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC"
                and x["source_parameter_id"] == spec["source_parameter_id"]
                and x["source_interval"]
                == [spec["parameter_lo"], spec["parameter_hi"]]
                and x["phase_turn_law"] ==
                {"offset": spec["phase_turn_offset"],
                 "rate": spec["phase_turn_rate"]},
                "SOURCE_EVIDENCE_DRIFT:" + cid)
    row = originals[CASE_ID]
    evidence = registration[CASE_ID]
    require(sha(row) == ROW_SHA and evidence["source_sha256"] == SRC_SHA
            and row["origin"] == "verify_pb00701_v10"
            and row["expected"]["observed"]["status"] == "BLOCKED"
            and row["expected"]["v54_disposition"] == "BLOCKED",
            "HISTORICAL_V9_V43_REFUSAL_OR_DIGEST_DRIFT")
    require(row["expected"]["observed"]["spans"] ==
            [["PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO",
              "CERTIFIED", None],
             ["PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF",
              "BLOCKED", "CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED"]],
            "ORIGINAL_SPAN_OWNER_DRIFT")
    parts = source_parts(row["spec"])
    A0, B0, A1, B1 = cayley_polynomials(parts)
    # Strict algebraic sign margin for dF/dt first span:
    # cos(theta) >= sqrt(2)/2 > 7/10; pi < 22/7 implies
    # derivative > 7/10 - 11/28 = 43/140 > 0.
    require(Q(7, 5)**2 < 2 and Q(22, 7) > 3
            and Q(7, 10) - Q(11, 28) == Q(43, 140),
            "FIRST_SPAN_MONOTONICITY_MARGIN")
    before = {
        "original_sources": 121,
        "historical_route_refusals": 20,
        "historical_missing_ordered_premises": 30,
        "existing_complete_original_witnesses": 50
    }
    return {
        "schema": SCHEMA,
        "claim": "C_DIRECT_CAYLEY_SEMIALGEBRAIC_ELIMINATION_FALSE",
        "historical_case_id": CASE_ID,
        "source_sha256": SRC_SHA,
        "original_row_sha256": ROW_SHA,
        "source_parameter_id": "source-time-t",
        "source_interval": ["0", "2"],
        "true_knot": "1",
        "phase_turns": {"offset": "0", "rate": "1/8"},
        "cayley_variable": "u=tan(pi*t/8)",
        "original_span_physical_forms": [
            "(t-1/2)*cos(pi*t/4)+sin(pi*t/4)",
            "100*(t-1)+(1/2)*cos(pi*t/4)+sin(pi*t/4)"
        ],
        "cayley_numerator_pi_times_atan_coefficients": [
            polystr(A0), polystr(A1)
        ],
        "cayley_numerator_rational_residual_coefficients": [
            polystr(B0), polystr(B1)
        ],
        "analytic_non_algebraicity_lemma":
            "CLASSICAL_LOG_MONODROMY_INFINITE_BRANCHES_NOT_MACHINE_FORMALIZED",
        "pure_algebraic_cayley_reduction_admissible": False,
        "first_span_open_physical_roots": 1,
        "first_span_root_bracket": ["0", "1"],
        "first_span_root_order": 1,
        "first_span_crossing": "NEGATIVE_TO_POSITIVE",
        "second_span_open_physical_roots": 0,
        "source_endpoint_and_knot_signs": ["NEGATIVE", "POSITIVE", "POSITIVE"],
        "identity_zero_or_tangent_or_extremely_close_general_grammar_admitted": False,
        "before": before,
        "after": before,
        "delta": {key: 0 for key in before},
        "historical_case_ids_newly_closed": [],
        "evidence_class": "DETERMINISTIC_MODEL",
        "required_pb_discharge": False,
        "mc_b_established": False,
        "mc1_established": False,
        "native_geometry_qualified": False,
        "engineering_step_qualified": False,
        "supported_operations": 26,
        "production_authorized": False
    }

def check_record(actual, saved):
    require(type(saved) is dict and canon(actual) == canon(saved),
            "MACHINE_RECEIPT_TAMPERING_OR_DRIFT")
    return actual

def execute():
    corpus = readp(CORPUS, CORPUS_BLOB)
    registry = readp(REGISTER, REGISTER_BLOB)
    result = receipt(corpus, registry)
    return check_record(result, json.loads(MACHINE.read_text(encoding="utf-8")))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        result = execute()
        if args.self_test:
            for key in ("source_parameter_id", "phase_turn_rate", "parameter_hi"):
                bad = copy.deepcopy(expected_spec())
                bad[key] = "forged"
                try:
                    source_parts(bad)
                except Refusal:
                    pass
                else:
                    raise Refusal("SOURCE_MUTATION_ADMITTED:" + key)
            fake = copy.deepcopy(result)
            fake["after"]["historical_route_refusals"] = 19
            try:
                check_record(result, fake)
            except Refusal:
                pass
            else:
                raise Refusal("CENSUS_FORGERY_ADMITTED")
        print(json.dumps({"status": "PASS", "claim": result["claim"],
                          "historical_case_id": CASE_ID,
                          "new_historical_closures": 0,
                          "machine_formalized_monodromy": False,
                          "self_test": args.self_test}, sort_keys=True))
        return 0
    except (Refusal, KeyError, ValueError, TypeError, AssertionError) as exc:
        print(json.dumps({"status": "REFUSED", "reason": str(exc),
                          "refusal_is_mathematical_truth": False}, sort_keys=True))
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
