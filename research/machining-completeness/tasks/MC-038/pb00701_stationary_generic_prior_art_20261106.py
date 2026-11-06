#!/usr/bin/env python3
"""Independent, bounded prior-art audit of original stationary knot composition.

Falsifies only NEW_GENERIC_STATIONARY_TWO_SPAN_COMPOSITOR_REQUIRED when the
already-landed conditional compositor and the candidate prove the same
two original signed event/cell results. DETERMINISTIC_MODEL; no PB discharge.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OLD = HERE / "pb00701_stationary_knot_composition.py"
V54 = HERE / "pb00701-finite-owner-corpus-v54.json"
V2 = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
RECEIPT = HERE / "pb00701-stationary-generic-prior-art-20261106.json"
CANDIDATE_FILE = "research/machining-completeness/tasks/MC-038/pb00701_stationary_knot_successor_20261106.py"
OLD_BLOB = "d0fbe7e189066fd9398958f1b1814b8147a6a64e"
V54_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
CANDIDATE_BLOB = "01605f2f00abc327ffdba2ab600d4ff9588da619"
CANDIDATE_HEAD = "359784454c4eaeda173458b9f4919b07edbdacd8"
EXPECTED = {
    "composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail0":
        "f4c2d33cc4c5a52f355ff4ecc36ad6ee38af0ff0fa8c5159aaac5923a10125ff",
    "composite:EXACT_STATIONARY_PHASE_POLYNOMIAL:tail100":
        "a49b92bbb74a7e016eed471feb64808eb9109a6a42b3ef874243364981a396fd",
}

class Refused(ValueError):
    """Nontruth admission boundary."""

def need(ok, reason):
    if not ok:
        raise Refused(reason)

def read_bounded(path, limit, pin=None):
    with Path(path).open("rb") as stream:
        data = stream.read(limit + 1)
    need(len(data) <= limit, "INPUT_BYTE_LIMIT")
    digest = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if pin:
        need(digest == pin, "SOURCE_GIT_BLOB_DRIFT:" + str(path))
    return data

def obj_pairs(pairs):
    result = {}
    for k, v in pairs:
        need(k not in result, "DUPLICATE_JSON_KEY")
        result[k] = v
    return result

def finite_float(s):
    raise Refused("JSON_FLOAT_NOT_IN_CONTRACT")

def parse(data):
    return json.loads(data, object_pairs_hook=obj_pairs, parse_float=finite_float,
                      parse_constant=lambda _: (_ for _ in ()).throw(Refused("NONFINITE")))

def prior_module():
    read_bounded(OLD, 20000, OLD_BLOB)
    spec = importlib.util.spec_from_file_location("pinned_stationary_prior", OLD)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def data_and_census():
    v54 = parse(read_bounded(V54, 300000, V54_BLOB))
    v2 = parse(read_bounded(V2, 210000, V2_BLOB))
    cases = v54["cases"]
    source_cases = v2["source_cases"]
    need(len(cases) == len({x["id"] for x in cases}) == 121, "V54_DENOMINATOR")
    need(len(source_cases) == len({x["case_id"] for x in source_cases}) == 50, "V2_DENOMINATOR")
    dispositions = {x["id"]: x["expected"]["v54_disposition"] for x in cases}
    need(sum(s == "BLOCKED" for s in dispositions.values()) == 20, "HISTORICAL_REFUSAL_CENSUS")
    need(sum(s == "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"
             for s in dispositions.values()) == 30, "ORDERED_PREMISE_CENSUS")
    need({x["case_id"] for x in source_cases} ==
         {k for k, s in dispositions.items() if s.startswith("BLOCKED")}, "V2_SOURCE_SET")
    old_by_id = {x["case_id"]: x for x in source_cases}
    for case in cases:
        if case["id"] not in EXPECTED:
            continue
        ident = case["id"]
        need(dispositions[ident] == "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE",
             "NOT_HISTORICALLY_MISSING_ORDERED")
        spec = case["spec"]
        need(spec["source_parameter_id"] == "source-time-t" and
             spec["parameter_lo"] == "0" and spec["parameter_hi"] == "2" and
             spec["phase_turn_offset"] == spec["phase_turn_rate"] == "0",
             "ORIGINAL_TIME_AND_PHASE")
        raw = json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()
        need(hashlib.sha256(raw).hexdigest() == EXPECTED[ident], "ORIGINAL_SOURCE_SHA256")
        old = old_by_id[ident]
        need(old["source_sha256"] == EXPECTED[ident] and
             old["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC" and
             old["original_source_piece_edges"] == ["0", "1", "2"] and
             old["historical_v54_disposition"] == dispositions[ident] and
             old["evidence"]["complete_original_source_zero_set"] is True,
             "PRIOR_REGISTERED_COMPLETE_SOURCE")
    return v54, v2

def normalize_original(x):
    ev = x["ordered_physical_zero_events"]
    knot = x["true_source_knots"]
    cells = x["maximal_open_sign_cells"]
    need(len(ev) == 1 and ev[0]["coordinate"] == "1/2" and
         ev[0]["coordinate_kind"] == "EXACT_RATIONAL" and
         ev[0]["left_sign"] == "NEGATIVE" and
         ev[0]["right_sign"] == "POSITIVE" and
         ev[0]["multiplicity"] == 1 and ev[0]["event_kind"] == "CROSSING",
         "PRIOR_SIGNED_ROOT")
    need(len(knot) == 1 and knot[0]["position"] == "1" and
         knot[0]["kind"] == "NONZERO_KNOT_NOT_ROOT" and
         knot[0]["left_inward_sign"] == knot[0]["right_inward_sign"] == "POSITIVE",
         "PRIOR_KNOT_JOIN")
    need([z["sign"] for z in cells] == ["NEGATIVE", "POSITIVE"] and
         x["source_span_count"] == 2 and x["distinct_open_physical_zeros"] == 1,
         "PRIOR_SIGNED_CELLS")
    return {"root": "1/2", "order": 1, "parity": "CROSSING",
            "signed_cells": ["NEGATIVE", "POSITIVE"],
            "knot": "NONZERO_POSITIVE", "source_time": ["0", "2"]}

def baseline_originals(prior):
    produced = prior.replay_frozen_stationary_cases()
    found = {x["source_case_id"]: x for x in produced}
    need(all(x in found for x in EXPECTED), "PRIOR_ORIGINALS_MISSING")
    return [{"case_id": ident, "source_sha256": sha,
             "prior_full_original_signed": normalize_original(found[ident]),
             "previously_complete_in_v2": True,
             "new_unique_historical_closure": False}
            for ident, sha in EXPECTED.items()]

def span(prover, lo, hi, coeffs):
    poly = [Q(x) for x in coeffs]
    view = prover.build_polynomial_view(poly, source_left=Q(lo), source_right=Q(hi))
    return {"interval": [lo, hi], "polynomial": poly, "view": view}

def conditional_prior(prior, items):
    prover = prior.stationary()
    return prior.compose_polynomial_spans([span(prover, *row) for row in items], prover)

def synthetic_evidence(prior):
    base = conditional_prior(prior, [("0","1",["-1/2","1"]),("1","2",["1/2"])])
    need(normalize_original({**base, "source_span_count": 2})["knot"] == "NONZERO_POSITIVE",
         "PRIOR_NONZERO_GLUE")
    cross = conditional_prior(prior, [("0","1",["-1","1"]),("1","2",["0","1"])])
    need(len(cross["ordered_physical_zero_events"]) == 1 and
         cross["true_source_knots"][0]["event_kind"] == "CROSSING" and
         cross["true_source_knots"][0]["left_one_sided_order"] == 1 and
         cross["true_source_knots"][0]["right_one_sided_order"] == 1,
         "PRIOR_ZERO_KNOT_CROSSING")
    touch = conditional_prior(prior, [("0","1",["1","-2","1"]),("1","2",["0","0","1"])])
    need(len(touch["ordered_physical_zero_events"]) == 1 and
         touch["true_source_knots"][0]["event_kind"] == "TOUCHING" and
         touch["true_source_knots"][0]["left_one_sided_order"] == 2 and
         touch["true_source_knots"][0]["right_one_sided_order"] == 2,
         "PRIOR_ZERO_KNOT_TANGENCY")
    double = conditional_prior(prior, [("0","1",["1/4","-1","1"]),
                                       ("1","2",["1/4"])])
    need(len(double["ordered_physical_zero_events"]) == 1 and
         double["ordered_physical_zero_events"][0]["multiplicity"] == 2,
         "PRIOR_INTERIOR_DOUBLE_TANGENCY")
    delta = Q(1, 2**120)
    close = conditional_prior(prior, [
        ("0","1",[str(-1 + delta),"1"]), ("1","2",[str(delta)])])
    need(len(close["ordered_physical_zero_events"]) == 1 and
         close["ordered_physical_zero_events"][0]["kind"] == "OPEN_SOURCE_ROOT",
         "PRIOR_EXTREMELY_CLOSE_KNOT_ROOT")
    endpoint = conditional_prior(prior, [
        ("0","1",["0","1"]),("1","2",["1"])])
    need(endpoint["left_physical_endpoint"]["relation"] == "ZERO" and
         not endpoint["ordered_physical_zero_events"], "PRIOR_EXTERIOR_ZERO")
    three = conditional_prior(prior, [
        ("0","1",["1"]),("1","2",["1"]),("2","3",["1"])])
    need(three["source_span_count"] == 3 and
         not three["ordered_physical_zero_events"] and
         len(three["maximal_open_sign_cells"]) == 1,
         "PRIOR_GENERIC_THREE_SPAN_CAPABILITY")
    return {"verified_nonzero_knot_join": True, "verified_zero_knot_crossing": True,
            "verified_zero_knot_order2_touch": True, "verified_interior_tangency": True,
            "verified_root_distance_to_knot_below_2pow120": True,
            "verified_exterior_endpoint_zero": True,
            "verified_three_span_generalization": True}

def candidate_check(root):
    # Resolve before switching subprocess cwd; avoid doubling relative path.
    root = Path(root).resolve()
    path = root / CANDIDATE_FILE
    read_bounded(path, 25000, CANDIDATE_BLOB)
    try:
        head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"],
                                       text=True, timeout=8).strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise Refused("CANDIDATE_GIT_PROVENANCE_NOT_AVAILABLE") from exc
    need(head == CANDIDATE_HEAD, "CANDIDATE_LITERAL_SHA_MISMATCH")
    p = subprocess.run([sys.executable, str(path), "--contract", "--self-test"],
                       cwd=root, capture_output=True, text=True, timeout=150)
    need(p.returncode == 0, "CANDIDATE_EXACT_HEAD_TEST_FAILURE:" +
         (p.stderr + p.stdout)[-1800:])
    spec = importlib.util.spec_from_file_location("pinned_stationary_candidate", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    cases = m.source_case_outputs()["case_results"]
    need({x["case_id"] for x in cases} == set(EXPECTED),
         "CANDIDATE_ORIGINAL_POPULATION")
    for x in cases:
        v = x["physical"]
        ev = v["ordered_source_events"]
        need(len(ev) == 1 and ev[0].get("source_value") == "1/2" and
             ev[0]["multiplicity"] == 1 and ev[0]["event_kind"] == "CROSSING" and
             [c["sign"] for c in v["maximal_nonzero_cells"]] ==
             ["NEGATIVE", "POSITIVE"] and v["source_knot"]["relation"] == "POSITIVE",
             "CANDIDATE_DIFFERS_ON_ORIGINAL_SIGNED_RESULT")
    return True

def receipt(prior=None, candidate_root=None):
    data_and_census()
    prior = prior or prior_module()
    actual = baseline_originals(prior)
    tests = synthetic_evidence(prior)
    if candidate_root is not None:
        need(candidate_check(candidate_root), "CANDIDATE_COMPARISON_NOT_VERIFIED")
    return {
        "schema": "radicadsac-pb00701-stationary-generic-prior-art/1.0",
        "evidence_class": "DETERMINISTIC_MODEL",
        "challenged_route": "NEW_GENERIC_STATIONARY_TWO_SPAN_KNOT_COMPOSITION_REQUIRED",
        "baseline_compositor_git_blob": OLD_BLOB,
        "candidate_source_git_blob": CANDIDATE_BLOB,
        "candidate_head": CANDIDATE_HEAD,
        "frozen_v54_git_blob": V54_BLOB,
        "frozen_v2_git_blob": V2_BLOB,
        "prior_compositor_span_admission_limit": 32,
        "prior_compositor_event_resource_limit": 256,
        "existing_generic_conditional_composition": tests,
        "originals": actual,
        "historical_before": {"originals":121,"route_refusals":20,
                              "missing_ordered":30,"v2_complete":50},
        "historical_after": {"originals":121,"route_refusals":20,
                             "missing_ordered":30,"v2_complete":50},
        "accepted_historical_delta": {"originals":0,"route_refusals":0,
                                      "missing_ordered":0,"v2_complete":0},
        "new_generic_stationary_two_span_semantic_capability_identified": False,
        "all_nonstationary_and_universal_obligations_still_open": True,
        "required_pb_po_discharged": 0,
        "mc_b_established": False, "mc1_established": False,
        "production_authorized": False,
        "native_or_step_qualified": False,
    }

def typed_equal(a, b):
    left = json.dumps(a, sort_keys=True, separators=(",",":"), allow_nan=False)
    right = json.dumps(b, sort_keys=True, separators=(",",":"), allow_nan=False)
    return left == right

def tests():
    prior = prior_module()
    class Controls(unittest.TestCase):
        def test_replayed_source(self):
            self.assertEqual(len(baseline_originals(prior)), 2)
        def test_synthetic_exact(self):
            self.assertTrue(all(synthetic_evidence(prior).values()))
        def test_identity_zero_refusal(self):
            # The pinned complete child prover must refuse identity-zero
            # before source composition; its ValueError is also nontruth.
            with self.assertRaisesRegex(ValueError, "identity polynomial"):
                conditional_prior(prior,[("0","1",["0"]),("1","2",["0"])])
        def test_knot_discontinuity_refusal(self):
            with self.assertRaises(prior.InvalidComposition):
                conditional_prior(prior,[("0","1",["1"]),("1","2",["2"])])
        def test_type_alias_rejection(self):
            x = receipt(prior)
            y = json.loads(json.dumps(x))
            y["required_pb_po_discharged"] = False
            self.assertFalse(typed_equal(x, y))
            y = json.loads(json.dumps(x))
            y["historical_before"]["missing_ordered"] = 30.0
            self.assertFalse(typed_equal(x, y))
        def test_duplicate_and_nonfinite_refusal(self):
            for raw in [b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1e999}']:
                with self.assertRaises(Refused):
                    parse(raw)
        def test_oversized_ingress_refusal(self):
            import tempfile
            with tempfile.TemporaryDirectory() as t:
                path = Path(t) / "data"
                path.write_bytes(b"x" * 1025)
                with self.assertRaises(Refused):
                    read_bounded(path, 1024)
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(Controls))
    if not result.wasSuccessful():
        raise SystemExit(1)
    print("PRIOR_ART_ADVERSARIAL_METHODS", result.testsRun)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--candidate-root")
    ap.add_argument("--print-receipt", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        tests()
    got = receipt(candidate_root=args.candidate_root)
    saved = parse(read_bounded(RECEIPT, 16000))
    need(typed_equal(got, saved), "COMMITTED_PRIOR_ART_RECEIPT_MISMATCH")
    print("GENERIC_STATIONARY_PRIOR_ART", len(got["originals"]),
          "EXISTING_GENERIC_SPAN_LIMIT", got["prior_compositor_span_admission_limit"],
          "HISTORICAL_DELTA", 0)
    if args.print_receipt:
        print(json.dumps(got, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
