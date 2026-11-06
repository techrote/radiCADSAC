#!/usr/bin/env python3
"""MC-038: exact original-H1 rational-amplitude rephasing obstruction.

This is an independently replayable bounded negative result, not an event solver.
A one-H1 rotation that removes sine while retaining a rational coefficient
amplitude would require C(t)^2 + S(t)^2 to be a square in R(t).
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import unittest
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "pb00701-finite-owner-corpus-v54.json"
REGISTER = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
RECEIPT = HERE / "pb00701-h1-rational-rephase-obstruction-20261106.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
REGISTER_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
SCHEMA = "radicadsac-pb00701-h1-rational-rephase-obstruction/1.0"
MAX_READ_BYTES = 600_000
EXPECTED = {
    "composite:PB00701_V9_EXACT_MONOTONE_SINGLE_HARMONIC_RATIO:tail0": {
        "sha256": "4d1ef1cbecceeb4a43b4e30fd37327fa204164cc9ce25dfe4f1744a052cebcc2",
        "disposition": "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE",
        "origin": "verify_pb00701_v10", "interval": ["0", "2"],
        "phase": ["0", "1/8"], "knot": "1",
        "C": ["-1/2", "1"], "S": ["1", "0"],
    },
    "harvested:verify_pb00701_v9:4e7b85fa122a": {
        "sha256": "a83ca0cd16c7822e6525f8f2d2df26a54f45b99807cadebc67f31fc49b066c10",
        "disposition": "BLOCKED", "origin": "verify_pb00701_v9",
        "interval": ["0", "1"], "phase": ["0", "1/8"], "knot": None,
        "C": ["1", "0"], "S": ["-1/2", "1"],
    },
}


class Refused(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise Refused(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      separators=(",", ":"), allow_nan=False).encode("ascii")


def unique_dict(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def invalid_constant(_value):
    raise Refused("NONFINITE_JSON")


def read_json(path, expected_git_blob=None):
    with path.open("rb") as handle:
        raw = handle.read(MAX_READ_BYTES + 1)
    need(len(raw) <= MAX_READ_BYTES, "SOURCE_READ_RESOURCE_REFUSAL")
    if expected_git_blob:
        git_blob = hashlib.sha1(
            b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
        ).hexdigest()
        need(git_blob == expected_git_blob, "PINNED_GIT_BLOB_MISMATCH")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_dict,
                          parse_constant=invalid_constant)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise Refused("INVALID_JSON") from exc


def rational(value):
    need(type(value) is str and 0 < len(value) <= 128,
         "NONCANONICAL_RATIONAL")
    try:
        q = Q(value)
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise Refused("BAD_RATIONAL") from exc
    need(str(q) == value, "NONCANONICAL_RATIONAL")
    need(max(abs(q.numerator).bit_length(), q.denominator.bit_length()) <= 256,
         "RATIONAL_RESOURCE_REFUSAL")
    return q


def affine_coefficients(spline, first_interval_end):
    """Exact clamped degree-0/1 original first-span B-spline extraction."""
    need(type(spline) is dict and set(spline) ==
         {"degree", "knots", "controls"}, "SOURCE_SPLINE_FIELDS")
    degree = spline["degree"]
    need(type(degree) is int and degree in (0, 1),
         "UNSUPPORTED_SPLINE_DEGREE")
    knots = [rational(x) for x in spline["knots"]]
    controls = [rational(x) for x in spline["controls"]]
    need(len(controls) + degree + 1 == len(knots),
         "ORIGINAL_SPLINE_CARDINALITY")
    need(knots[0] == 0 and knots[degree+1] == first_interval_end,
         "WRONG_FIRST_SPAN")
    need(all(x == 0 for x in knots[:degree+1]),
         "NONCLAMPED_FIRST_SPAN")
    if degree == 0:
        return (controls[0], Q(0))
    # On the first original fully clamped degree-one span [0,1],
    # N0=1-t, N1=t, irrespective of any later true physical knot.
    return (controls[0], controls[1]-controls[0])


def norm_quadratic(C, S):
    a, b = C
    c, d = S
    return a*a + c*c, 2*(a*b+c*d), b*b+d*d


def nonsquare_quadratic(C, S):
    """One sufficient, exact non-square proof in R(t), not a general solver.

    A real quadratic with positive leading coefficient and negative
    discriminant has two distinct simple conjugate zeros over C. The square
    of any rational function over R has even zero and pole orders over C,
    so this quadratic cannot be a rational-function square.
    """
    q0, q1, q2 = norm_quadratic(C, S)
    discriminant = q1*q1 - 4*q2*q0
    need(q2 > 0 and discriminant < 0, "NONSQUARE_NOT_PROVED")
    return (q0, q1, q2), discriminant


def source_pair(row, expected):
    need(row["origin"] == expected["origin"], "ORIGINAL_PRODUCER_CHANGED")
    need(row["expected"]["v54_disposition"] == expected["disposition"],
         "HISTORICAL_DISPOSITION_CHANGED")
    spec = row["spec"]
    need(spec["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE"
         and spec["source_parameter_id"] == "source-time-t",
         "SOURCE_GRAMMAR_OR_PARAMETER_CHANGED")
    need([spec["parameter_lo"], spec["parameter_hi"]] == expected["interval"],
         "ORIGINAL_SOURCE_INTERVAL_CHANGED")
    need([spec["phase_turn_offset"], spec["phase_turn_rate"]] ==
         expected["phase"], "ORIGINAL_PHASE_CHANGED")
    cos = spec["cos_splines"]
    sin = spec["sin_splines"]
    need(set(cos) == ({"0", "1"} if expected["knot"] else {"1"})
         and set(sin) == {"1"}, "ORIGINAL_HARMONIC_INVENTORY_CHANGED")
    if expected["knot"]:
        need(cos["0"]["degree"] == 0 and
             cos["0"]["knots"] == ["0", "1", "2"] and
             cos["0"]["controls"] == ["0", "0"],
             "NONZERO_OR_UNEXPECTED_H0")
        need(cos["1"]["knots"] == ["0","0","1","1","2","2"] and
             sin["1"]["knots"] == ["0","1","2"],
             "ORIGINAL_TRUE_KNOT_CHANGED")
    else:
        need(cos["1"]["knots"] == ["0","0","1","1"] and
             sin["1"]["knots"] == ["0","0","1","1"],
             "ORIGINAL_SINGLE_SPAN_CHANGED")
    C = affine_coefficients(cos["1"], Q(1))
    S = affine_coefficients(sin["1"], Q(1))
    need([str(x) for x in C] == expected["C"] and
         [str(x) for x in S] == expected["S"],
         "ORIGINAL_COEFFICIENTS_CHANGED")
    need(hashlib.sha256(canonical(spec)).hexdigest() ==
         expected["sha256"], "ORIGINAL_SOURCE_SHA256_MISMATCH")
    q, delta = nonsquare_quadratic(C, S)
    need(q == (Q(5,4), Q(-1), Q(1)) and delta == -4,
         "ORIGINAL_NORM_IDENTITY_CHANGED")
    return {"case_id": row["id"], "source_sha256": expected["sha256"],
            "historical_v54_disposition": expected["disposition"],
            "source_time": expected["interval"],
            "true_source_knot": expected["knot"],
            "phase_turns": expected["phase"],
            "first_original_span_C1_affine": expected["C"],
            "first_original_span_S1_affine": expected["S"],
            "squared_norm_coefficients_ascending": ["5/4", "-1", "1"],
            "discriminant": "-4",
            "rational_function_amplitude_exists": False,
            "physical_root_count_asserted": False}


def compute():
    frozen = read_json(CORPUS, CORPUS_BLOB)
    registered = read_json(REGISTER, REGISTER_BLOB)
    rows = frozen["cases"]
    need(len(rows) == 121, "FROZEN_POPULATION_CHANGED")
    lookup = {r["id"]:r for r in rows}
    need(len(lookup) == 121, "DUPLICATE_ORIGINAL_CASE_ID")
    source_hashes = [hashlib.sha256(canonical(r["spec"])).hexdigest()
                     for r in rows]
    need(len(set(source_hashes)) == 121, "DUPLICATE_SOURCE_SPECIFICATION")
    blocked = {i for i,r in lookup.items()
               if r["expected"]["v54_disposition"] == "BLOCKED"}
    missing = {i for i,r in lookup.items()
               if r["expected"]["v54_disposition"] ==
               "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"}
    need(len(blocked) == 20 and len(missing) == 30 and
         not blocked.intersection(missing), "HISTORICAL_DENOMINATOR_CHANGED")
    witnesses = registered["source_cases"]
    v2 = {x["case_id"]:x for x in witnesses}
    need(len(witnesses) == len(v2) == 50 and
         set(v2) == blocked.union(missing), "V2_SOURCE_COVERAGE_CHANGED")
    for i, witness in v2.items():
        spec = lookup[i]["spec"]
        need(witness["source_sha256"] ==
             hashlib.sha256(canonical(spec)).hexdigest()
             and witness["historical_v54_disposition"] ==
             lookup[i]["expected"]["v54_disposition"]
             and witness["registered_evidence_level"] ==
             "COMPLETE_SOURCE_SPECIFIC"
             and witness["origin"] == lookup[i]["origin"],
             "V2_PROVENANCE_MISMATCH")
    selected = [source_pair(lookup[i], expected)
                for i, expected in EXPECTED.items()]
    return {
        "schema": SCHEMA,
        "claim": "H1_RATIONAL_AMPLITUDE_REPHASING_REFUTED_FOR_TWO_ORIGINALS",
        "evidence_class": "DETERMINISTIC_MODEL",
        "frozen_inputs": {"corpus_git_blob": CORPUS_BLOB,
                          "v2_git_blob": REGISTER_BLOB},
        "cases": selected,
        "census": {
            "before": {"originals": 121, "route_refusals": 20,
                       "missing_ordered_premises": 30, "complete_v2": 50},
            "after": {"originals": 121, "route_refusals": 20,
                      "missing_ordered_premises": 30, "complete_v2": 50},
            "delta": {"originals": 0, "route_refusals": 0,
                      "missing_ordered_premises": 0, "complete_v2": 0},
            "newly_closed_historical_ids": [],
            "required_pb_po_discharges": 0
        },
        "nonclaims": {"physical_event_solver": False,
                      "generic_pb00701": False, "mc_b_established": False,
                      "mc1_established": False, "native_geometry": False,
                      "engineering_step": False,
                      "production_authorized": False,
                      "supported_operations": 26}
    }


def verify_receipt():
    computed = compute()
    saved = read_json(RECEIPT)
    need(canonical(saved) == canonical(computed), "STALE_OR_FORGED_RECEIPT")
    return computed


class Adversarial(unittest.TestCase):
    def test_pinned_originals_and_typed_receipt(self):
        self.assertEqual(verify_receipt()["census"]["delta"]["missing_ordered_premises"], 0)

    def test_synthetically_admitted_rational_amplitudes(self):
        # 3t cos + 4t sin has norm 25t^2, a rational amplitude 5t.
        # Neither a tangency nor a coefficient-space identity should be
        # misreported as a non-square obstruction.
        for C, S in [((Q(0),Q(3)), (Q(0),Q(4))),
                     ((Q(-1,2),Q(1)), (Q(0),Q(0))),
                     ((Q(0),Q(0)), (Q(0),Q(0)))]:
            with self.assertRaisesRegex(Refused, "NONSQUARE_NOT_PROVED"):
                nonsquare_quadratic(C,S)

    def test_arbitrarily_close_nonzero_sine_channel(self):
        eps = Q(1, 2**120)
        q, disc = nonsquare_quadratic((Q(-1,2),Q(1)),(eps,Q(0)))
        self.assertEqual(disc, -4 * eps * eps)
        self.assertGreater(q[2], 0)

    def test_exact_original_phase_and_control_mutations_refuse(self):
        original = read_json(CORPUS, CORPUS_BLOB)["cases"]
        row = next(x for x in original if x["id"] in EXPECTED)
        expect = EXPECTED[row["id"]]
        for field in ("phase_turn_rate","source_parameter_id"):
            bad = copy.deepcopy(row)
            bad["spec"][field] = "1/7" if field == "phase_turn_rate" else "local-u"
            with self.subTest(field=field):
                with self.assertRaises(Refused):
                    source_pair(bad,expect)
        bad = copy.deepcopy(row)
        bad["spec"]["sin_splines"]["1"]["controls"][0] = "0"
        with self.assertRaises(Refused):
            source_pair(bad,expect)
        bad = copy.deepcopy(row)
        bad["expected"]["v54_disposition"] = "CERTIFIED"
        with self.assertRaises(Refused):
            source_pair(bad,expect)

    def test_wrong_claim_type_and_new_closure_rejected(self):
        original = verify_receipt()
        for path, value in [
            (("census","delta","missing_ordered_premises"), True),
            (("census","newly_closed_historical_ids"), ["invented"]),
            (("nonclaims","native_geometry"), True),
            (("cases",0,"discriminant"), "0")]:
            forged = copy.deepcopy(original)
            d = forged
            for key in path[:-1]:
                d = d[key]
            d[path[-1]] = value
            self.assertNotEqual(canonical(forged), canonical(original))

    def test_duplicate_json_and_nonfinite_refuse(self):
        with self.assertRaises(Refused):
            json.loads('{"x":1,"x":2}', object_pairs_hook=unique_dict)
        with self.assertRaises(Refused):
            json.loads('{"x":NaN}', parse_constant=invalid_constant)

    def test_no_universal_impossibility_from_failed_premise(self):
        self.assertEqual(norm_quadratic((Q(-1,2),Q(1)),(Q(1),Q(0))),
                         (Q(5,4),Q(-1),Q(1)))
        # A polynomial square is a sufficient positive control, not a proof
        # that an arbitrary sine-bearing analytic event can be decided.
        self.assertEqual(norm_quadratic((Q(0),Q(3)),(Q(0),Q(4))),
                         (Q(0),Q(0),Q(25)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.contract or not args.self_test:
        proof = verify_receipt()
        print("QUALIFIED BOUNDED C candidate: original H1 rational amplitude "
              "rephasing impossible on two pinned cases")
        print("121 originals, 20 route refusals, 30 missing ordered, "
              "50 existing V2 signed proofs; zero new closures")
        assert proof["evidence_class"] == "DETERMINISTIC_MODEL"
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Adversarial)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() else 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Refused, OSError, KeyError, TypeError, ValueError) as exc:
        print("REFUSED:", exc)
        raise SystemExit(2)
