#!/usr/bin/env python3
"""Source-bound exact V10 phase-winding counterexample; NOT generic PB-007 closure.

Proof arithmetic uses Fraction and integer half-turns. No numerical root search.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent
CASE = "composite:PB00701_V10_EXACT_DUAL_PROJECTIVE_SINGLE_HARMONIC_RATIO:tail0"
SOURCE_SHA256 = "57d3c14096ccedfb7faea5023f5a09bada2ca274748f2207c36d77bbc790927c"
ROW_SHA256 = "c5ba85453dc65e0d18675353986394ae5b34af6219a741ce14af0c332ffc47cd"
V54_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
RECEIPT = ROOT / "pb00701-v10-winding-counterexample-20261106.json"

class Refused(Exception):
    """An admission or evidence condition failed; not a semantic zero result."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Refused(message)


def canonical(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def pinned_json(filename: str, blob: str) -> dict:
    path = ROOT / filename
    data = path.read_bytes()
    require(len(data) <= 300_000, "PINNED_SOURCE_SIZE")
    digest = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    require(digest == blob, "IMMUTABLE_GIT_BLOB_MISMATCH")
    return json.loads(data)


def proof_cell(left: F, right: F, offset: F, rate: F,
               s_left: F, s_right: F) -> dict:
    """Exactly one simple physical root for C=1, linearly nonincreasing S.

    Both phase endpoints are exact half-turns with one half-turn increment.
    The orientation angle arctan(S) changes by less than pi/2 when
    -1/2 <= S(right) <= S(left) <= 1/2. Hence delta=phase-angle is
    strictly increasing through (pi,3pi/2] and cannot contain three
    cosine zeros; alternating endpoint signs force exactly one.
    """
    require(right > left, "NONPOSITIVE_CELL")
    require(F(-1, 2) <= s_right <= s_left <= F(1, 2), "ORIENTATION_BOUND")
    a = 2 * (offset + rate * left)
    b = 2 * (offset + rate * right)
    require(a.denominator == 1 and b.denominator == 1, "NONEXACT_HALF_TURN_ENDPOINT")
    require(b - a == 1, "UNSUPPORTED_PHASE_WINDING")
    require(rate > 0, "NONPOSITIVE_PHASE_RATE")
    # sin(2pi*turns) = 0; cos(2pi*turns) = (-1)^(2*turns).
    left_sign = "POSITIVE" if a.numerator % 2 == 0 else "NEGATIVE"
    right_sign = "POSITIVE" if b.numerator % 2 == 0 else "NEGATIVE"
    require(left_sign != right_sign, "ENDPOINT_PARITY_CONTRADICTION")
    return {
        "left": str(left), "right": str(right),
        "left_sign": left_sign, "right_sign": right_sign,
        "interior_roots": 1, "physical_root_order": 1,
        "parity": "ODD", "multiplicity": 1,
        "left_and_right_zero": False,
    }


def original_cells(spec: dict) -> list[dict]:
    require(spec["grammar"] == "RATIONAL_BSPLINE_MODULATED_TRIG_AFFINE_PHASE",
            "ORIGINAL_GRAMMAR")
    require(spec["source_parameter_id"] == "source-time-t", "SOURCE_TIME_ID")
    require((spec["parameter_lo"], spec["parameter_hi"]) == ("0", "2"), "SOURCE_INTERVAL")
    require((spec["phase_turn_offset"], spec["phase_turn_rate"]) == ("-1/2", "2"), "PHASE_LAW")
    require(spec["cos_splines"] == {
        "0": {"degree": 0, "knots": ["0", "1", "2"], "controls": ["0", "0"]},
        "1": {"degree": 0, "knots": ["0", "1", "2"], "controls": ["1", "1"]},
    }, "COSINE_SOURCE_CHANNELS")
    require(spec["sin_splines"] == {
        "1": {"degree": 1, "knots": ["0", "0", "1", "1", "2", "2"],
              "controls": ["1/2", "-1/2", "-1/2", "-1/2"]}
    }, "SINE_SOURCE_CHANNELS")
    require(hashlib.sha256(canonical(spec)).hexdigest() == SOURCE_SHA256, "SOURCE_SHA256")
    cells = []
    for k in range(8):
        left, right = F(k, 4), F(k + 1, 4)
        s_left = F(1, 2) - left if k < 4 else F(-1, 2)
        s_right = F(1, 2) - right if k < 4 else F(-1, 2)
        cell = proof_cell(left, right, F(-1, 2), F(2), s_left, s_right)
        cell["span"] = 0 if k < 4 else 1
        cells.append(cell)
    require(cells[3]["right"] == "1" and cells[4]["left"] == "1", "TRUE_SOURCE_KNOT")
    require(cells[3]["right_sign"] == cells[4]["left_sign"] == "NEGATIVE",
            "KNOT_VALUE_NOT_CONTINUOUS")
    require(cells[0]["left_sign"] == cells[-1]["right_sign"] == "NEGATIVE",
            "EXTERIOR_SIGN_NOT_NEGATIVE")
    return cells


def prove_from_frozen() -> dict:
    corpus = pinned_json("pb00701-finite-owner-corpus-v54.json", V54_BLOB)
    v2 = pinned_json("pb00701-post-v54-evidence-reconciliation-v2.json", V2_BLOB)
    cases = corpus["cases"]
    require(len(cases) == len({c["id"] for c in cases}) == 121, "FROZEN_DENOMINATOR")
    refusals = sum(c["expected"]["v54_disposition"] == "BLOCKED" for c in cases)
    ordered = sum(c["expected"]["v54_disposition"] ==
                  "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE" for c in cases)
    require((refusals, ordered) == (20, 30), "FROZEN_DISPOSITION_CENSUS")
    rows = [c for c in cases if c["id"] == CASE]
    require(len(rows) == 1, "ORIGINAL_CASE_NOT_UNIQUE")
    row = rows[0]
    require(hashlib.sha256(canonical(row)).hexdigest() == ROW_SHA256, "ORIGINAL_ROW_SHA256")
    require(row["origin"] == "verify_pb00701_v10" and
            row["expected"]["v54_disposition"] == "BLOCKED", "HISTORICAL_REFUSAL_CHANGED")
    require(row["expected"]["observed"]["spans"][1] ==
            ["PB00701_V43_EXACT_CORRELATED_CLOSED_HANDOFF", "BLOCKED",
             "CORRELATED_CLOSED_HANDOFF_EVENT_NOT_CERTIFIED"], "V43_FAILURE_LOST")
    sources = v2["source_cases"]
    require(len(sources) == len({c["case_id"] for c in sources}) == 50, "V2_DENOMINATOR")
    previous = [c for c in sources if c["case_id"] == CASE]
    require(len(previous) == 1 and previous[0]["source_sha256"] == SOURCE_SHA256 and
            previous[0]["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC",
            "PRIOR_SOURCE_SPECIFIC_PROOF_NOT_PRESERVED")
    cells = original_cells(row["spec"])
    before = {"original_sources": len(cases), "route_refusals": refusals,
              "missing_ordered_premises": ordered, "complete_v2_source_witnesses": len(sources)}
    return {
        "schema": "radicadsac-mc038-v10-winding-counterexample/1.0",
        "evidence_class": "DETERMINISTIC_MODEL",
        "proposed_route_refused": "GLOBAL_STRICT_PHASE_DIFFERENCE_MONOTONICITY_PLUS_ENDPOINT_KNOT_SIGNS_IMPLIES_NO_HIDDEN_SIGN_EVENTS",
        "case_id": CASE, "original_source_sha256": SOURCE_SHA256,
        "original_row_sha256": ROW_SHA256,
        "frozen_v54_git_blob": V54_BLOB, "preexisting_v2_git_blob": V2_BLOB,
        "source_time": ["0", "2"], "true_knot": "1",
        "phase_turn_law": {"offset": "-1/2", "rate": "2"},
        "signed_open_cell_roots": cells, "root_count": 8,
        "root_order": "8 distinct simple interior roots: one in every open quarter-cell",
        "physical_source_knots_zero": False,
        "exterior_and_knot_signs": ["NEGATIVE", "NEGATIVE", "NEGATIVE"],
        "full_sign_cells": "NEGATIVE/POSITIVE alternating, beginning and ending NEGATIVE",
        "prior_v2_complete_source_witness": True,
        "population": {"before": before, "after": dict(before),
                       "delta": {k: 0 for k in before},
                       "newly_resolved_historical_case_ids": [],
                       "required_pb_po_discharges": 0},
        "pb00701_established": False, "mc_b_established": False,
        "mc1_established": False, "production_authorized": False,
        "native_geometry_qualified": False, "engineering_step_qualified": False,
        "supported_operations": 26,
    }


class Adversarial(unittest.TestCase):
    def test_original_source_bound_and_full_sign_transfer(self):
        result = prove_from_frozen()
        self.assertEqual(result["root_count"], 8)
        self.assertEqual([c["left_sign"] for c in result["signed_open_cell_roots"]],
                         ["NEGATIVE", "POSITIVE"] * 4)
        self.assertEqual(result["population"]["delta"]["missing_ordered_premises"], 0)

    def test_nonunit_phase_winding_refused(self):
        with self.assertRaises(Refused):
            proof_cell(F(0), F(1, 4), F(-1, 2), F(1), F(1, 2), F(1, 4))

    def test_endpoint_lattice_mismatch_refused(self):
        with self.assertRaises(Refused):
            proof_cell(F(0), F(1, 4), F(-3, 8), F(2), F(1, 2), F(1, 4))

    def test_orientation_reversal_and_overrange_refused(self):
        for a, b in [(F(-1, 2), F(1, 2)), (F(1), F(0))]:
            with self.assertRaises(Refused):
                proof_cell(F(0), F(1, 4), F(0), F(2), a, b)

    def test_phase_sign_and_knot_tamper_refused(self):
        base = pinned_json("pb00701-finite-owner-corpus-v54.json", V54_BLOB)
        spec = next(x["spec"] for x in base["cases"] if x["id"] == CASE)
        for mutated in [
            {**spec, "phase_turn_rate": "1/8"},
            {**spec, "cos_splines": {}},
            {**spec, "sin_splines": {}},
            {**spec, "parameter_hi": "1"},
            {**spec, "phase_turn_offset": "0"},
        ]:
            with self.assertRaises(Refused):
                original_cells(mutated)
        import copy
        changed = copy.deepcopy(spec)
        changed["sin_splines"]["1"]["knots"][3] = "3/2"
        with self.assertRaises(Refused):
            original_cells(changed)

    def test_identity_zero_and_tangency_not_laundered(self):
        # Mutate the *complete* original source, not a malformed stub.
        # These are semantic counterfamilies outside the exact C=1,
        # orientation-bound signed-winding grammar.
        import copy
        base = pinned_json("pb00701-finite-owner-corpus-v54.json", V54_BLOB)
        spec = next(x["spec"] for x in base["cases"] if x["id"] == CASE)

        zero = copy.deepcopy(spec)
        zero["cos_splines"]["1"]["controls"] = ["0", "0"]
        zero["sin_splines"]["1"]["controls"] = ["0", "0", "0", "0"]
        with self.assertRaises(Refused):
            original_cells(zero)  # Entire physical source identically zero.

        tangent = copy.deepcopy(spec)
        tangent["cos_splines"]["1"] = {
            "degree": 2, "knots": ["0", "0", "0", "1", "1", "1", "2", "2", "2"],
            "controls": ["1/4", "-1/4", "1/4", "1/4", "1/4", "1/4"],
        }
        tangent["sin_splines"]["1"]["controls"] = ["0", "0", "0", "0"]
        # First-span physical F=(t-1/2)^2 cos(theta) has a
        # second-order zero at t=1/2 (cos(theta)=-1 there).
        with self.assertRaises(Refused):
            original_cells(tangent)

    def test_extremely_close_root_cells(self):
        eps = F(1, 2**120)
        v = F(1, 2) / eps
        first = proof_cell(F(0), eps, F(0), v, F(0), F(0))
        second = proof_cell(eps, 2*eps, F(0), v, F(0), F(0))
        self.assertEqual((first["interior_roots"], second["interior_roots"]), (1, 1))
        self.assertEqual(first["right"], second["left"])
        self.assertNotEqual(first["right_sign"], second["right_sign"])

    def test_noncertified_receipt_refused(self):
        result = prove_from_frozen()
        self.assertFalse(result["pb00701_established"])
        self.assertEqual(result["population"]["newly_resolved_historical_case_ids"], [])
        self.assertEqual(result["population"]["required_pb_po_discharges"], 0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.contract:
        result = prove_from_frozen()
        expected = json.loads(RECEIPT.read_text(encoding="utf-8"))
        require(result == expected, "MACHINE_RECEIPT_DRIFT")
        print("V10 ORIGINAL source-bound eight-event proof: PASS")
        print("Frozen V54=121/20/30; preexisting V2=50; all deltas=0; new PB/PO=0")
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Adversarial)
        require(unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful(),
                "ADVERSARIAL_TESTS_FAILED")
    if not args.contract and not args.self_test:
        ap.error("choose --contract and/or --self-test")


if __name__ == "__main__":
    try:
        main()
    except Refused as exc:
        raise SystemExit(f"REFUSED_NONTRUTH:{exc}")
