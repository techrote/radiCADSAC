#!/usr/bin/env python3
"""Independent adversarial checks for exact rational-quarter physical knot jets."""
from __future__ import annotations
import argparse
import copy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import unittest
import pb00701_physical_knot_cyclotomic as m

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "pb00701-finite-owner-corpus-v54.json"
V2 = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
REPORT = HERE / "pb00701-physical-knot-cyclotomic.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"
HISTORICAL_ANCHOR = "composite:DELEGATED_V6_CONSTANT_MODULATION:tail0"
ANCHOR_SHA = "9eb6f08a44882adffa919529247c40190c70e8d7599ee2b1a0f7978ef2569eb1"

def blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def census():
    if blob(CORPUS) != CORPUS_BLOB or blob(V2) != V2_BLOB:
        raise ValueError("PINNED_ORIGINAL_SOURCE_OR_EVIDENCE_BYTES_DRIFT")
    corpus = json.loads(CORPUS.read_text())
    v2 = json.loads(V2.read_text())
    rows = corpus["cases"]
    if len(rows) != 121 or len({x["id"] for x in rows}) != 121:
        raise ValueError("INVALID_FROZEN_CASE_ID_DENOMINATOR")
    index = {r["id"]: r for r in rows}
    historical_sha = {r["id"]: m.sha(r["spec"]) for r in rows}
    if historical_sha[HISTORICAL_ANCHOR] != ANCHOR_SHA:
        raise ValueError("HISTORICAL_ANCHOR_SOURCE_HASH_DRIFT")
    refused = {i for i, r in index.items()
               if r["expected"]["v54_disposition"] == "BLOCKED"}
    missing = {i for i, r in index.items()
               if r["expected"]["v54_disposition"] ==
               "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"}
    if len(refused) != 20 or len(missing) != 30 or refused & missing:
        raise ValueError("FROZEN_V54_20_30_CENSUS_DRIFT")
    source_rows = v2["source_cases"]
    if len(source_rows) != 50 or {r["case_id"] for r in source_rows} != refused | missing:
        raise ValueError("REGISTERED_FIFTY_EXACT_CASE_IDS_DRIFT")
    for r in source_rows:
        original = index[r["case_id"]]
        if not (r["source_sha256"] == historical_sha[r["case_id"]] ==
                r["evidence"]["source_sha256"] and
                r["historical_v54_disposition"] ==
                    original["expected"]["v54_disposition"] and
                r["origin"] == original["origin"] and
                r["provenance_kind"] == original["kind"] and
                r["historical_disposition_changed"] is False and
                r["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC" and
                r["evidence"]["complete_original_source_zero_set"] is True):
            raise ValueError("REGISTERED_EXACT_ORIGINAL_SOURCE_DRIFT:" + r["case_id"])
    summary = v2["summary"]
    if not (summary["by_registered_evidence_level"]["COMPLETE_SOURCE_SPECIFIC"] == 50
            and summary["complete_finite_sources"] == 49
            and summary["complete_continuum_sources"] == 1
            and v2["frozen_corpus_git_blob"] == CORPUS_BLOB):
        raise ValueError("FIFTY_SOURCE_EVIDENCE_CENSUS_DRIFT")
    if (m.sha(m.SOURCE) != m.SOURCE_SHA256 or
            m.SOURCE_SHA256 in set(historical_sha.values())):
        raise ValueError("PROSPECTIVE_ORIGINAL_SOURCE_SHA_COLLISION")
    return {
        "frozen_original_source_denominator": 121,
        "route_refusals_before_after": [20, 20],
        "missing_ordered_premises_before_after": [30, 30],
        "complete_source_specific_before_after": [50, 50],
        "complete_finite": 49, "complete_continuum": 1,
        "new_historical_case_ids": [],
        "all_fifty_original_source_hashes_and_ids_checked": True,
    }

def expected_machine():
    return {
        "schema": m.SCHEMA, "evidence_class": "DETERMINISTIC_MODEL",
        "claim": "C_FOURIER_COEFFICIENT_MATCH_NOT_NECESSARY_FOR_PHYSICAL_KNOT_CONTINUITY",
        "prospective_source_sha256": m.SOURCE_SHA256,
        "frozen_historical_anchor_case_id": HISTORICAL_ANCHOR,
        "frozen_historical_anchor_source_sha256": ANCHOR_SHA,
        "frozen_corpus_git_blob": CORPUS_BLOB,
        "complete_v2_registry_git_blob": V2_BLOB,
        "actual_physical_knot": "1", "phase_turn_at_knot": "1/4",
        "physical_knot_value": "0", "physical_continuity": True,
        "fourier_coefficientwise_continuity": False,
        "left_one_sided_order": 1, "right_one_sided_order": 2,
        "left_sign": 1, "right_sign": 1,
        "exact_global_source_zero_set_for_selected_source": ["1"],
        "frozen_original_sources_before_after": [121, 121],
        "frozen_route_refusals_before_after": [20, 20],
        "frozen_missing_order_premises_before_after": [30, 30],
        "complete_source_specific_before_after": [50, 50],
        "new_frozen_case_ids_resolved": [],
        "pb00701_certified": False, "mc_b_established": False,
        "mc1_established": False, "production_authorized": False,
    }

class PhysicalKnotProofTests(unittest.TestCase):
    def setUp(self):
        self.src = copy.deepcopy(m.SOURCE)

    def test_exact_bound_source_and_continuous_physical_join_with_channel_jumps(self):
        r = m.analyze(self.src)
        self.assertEqual(m.sha(self.src), m.SOURCE_SHA256)
        self.assertTrue(r["physical_knot_continuous"])
        self.assertFalse(r["fourier_channels_coefficientwise_equal"])
        self.assertTrue(r["actual_knot_zero"])
        self.assertEqual([r["left_one_sided_zero_order"],
                          r["right_one_sided_zero_order"]], [1, 2])
        self.assertEqual([r["left_adjacent_sign"],
                          r["right_adjacent_sign"]], [1, 1])
        self.assertEqual(r["left_analytic"]["first_nonzero_scaled"], "-1")
        self.assertEqual(r["right_analytic"]["first_nonzero_scaled"], "2")

    def test_all_three_fourier_channels_jump(self):
        a, b = m.parse(self.src)
        self.assertEqual(sorted(a), [0, 1, 2])
        self.assertEqual(sorted(b), [0, 1, 2])
        self.assertTrue(all(a[h] != b[h] for h in (0,1,2)))
        self.assertEqual(m.point_jet(a)["point_value"], "0")
        self.assertEqual(m.point_jet(b)["point_value"], "0")

    def test_exact_global_single_root_justification_is_not_generic_claim(self):
        r=m.negative_c()
        self.assertEqual(r["complete_original_source_zero_set"],["1"])
        self.assertEqual(r["left_original_piece_identity"],"cos(pi*t/2)")
        self.assertFalse(r["source_bound_knot_certificate"]
                         ["physical_zero_set_outside_knot_determined"])
        self.assertFalse(r["general_analytic_event_decision_established"])

    def test_crossing_with_different_amplitude_same_physical_knot_value(self):
        other=copy.deepcopy(self.src)
        other["cos_splines"]={"1":{"degree":0,"knots":["0","1","2"],
                                   "controls":["1","2"]}}
        r=m.analyze(other)
        self.assertTrue(r["physical_knot_continuous"])
        self.assertFalse(r["fourier_channels_coefficientwise_equal"])
        self.assertEqual([r["left_one_sided_zero_order"],
                          r["right_one_sided_zero_order"]],[1,1])
        self.assertEqual([r["left_adjacent_sign"],r["right_adjacent_sign"]],
                         [1,-1])

    def test_actual_discontinuous_physical_join_refuses_continuity(self):
        other=copy.deepcopy(self.src)
        other["cos_splines"]={"0":{"degree":0,"knots":["0","1","2"],
                                   "controls":["1","2"]}}
        r=m.analyze(other)
        self.assertFalse(r["physical_knot_continuous"])
        self.assertEqual([r["left_analytic"]["point_value"],
                          r["right_analytic"]["point_value"]],["1","2"])
        self.assertFalse(r["actual_knot_zero"])

    def test_one_sided_identity_zero_not_invented_isolated_multiplicity(self):
        other=copy.deepcopy(self.src)
        other["cos_splines"]={"1":{"degree":0,"knots":["0","1","2"],
                                   "controls":["0","1"]}}
        r=m.analyze(other)
        self.assertTrue(r["physical_knot_continuous"])
        self.assertEqual(r["left_analytic"]["status"],"IDENTITY_ZERO")
        self.assertIsNone(r["left_one_sided_zero_order"])
        self.assertEqual(r["right_one_sided_zero_order"],1)
        self.assertEqual(r["right_adjacent_sign"],-1)

    def test_even_tangency_order_four_terminates_at_degree_bound(self):
        # cos(theta)^4 = (3+4*cos(2theta)+cos(4theta))/8
        other=copy.deepcopy(self.src)
        other["cos_splines"]={
            "0":{"degree":0,"knots":["0","1","2"],
                 "controls":["3/8","3/8"]},
            "2":{"degree":0,"knots":["0","1","2"],
                 "controls":["1/2","1/2"]},
            "4":{"degree":0,"knots":["0","1","2"],
                 "controls":["1/8","1/8"]},
        }
        r=m.analyze(other)
        self.assertEqual(r["left_one_sided_zero_order"],4)
        self.assertEqual(r["right_one_sided_zero_order"],4)
        self.assertEqual([r["left_adjacent_sign"],r["right_adjacent_sign"]],[1,1])
        self.assertEqual(r["left_analytic"]["finite_vandermonde_dimension"],5)

    def test_tiny_exact_nonzero_point_and_provably_nearby_open_root(self):
        # F=cos(pi*t/2)+eps on both spans; eps=2^-120.
        # For u=2^-118, sin(pi*u/2)>u>eps by sine chord bound.
        # F(1)=eps>0, F(1+u)<0; IVT and strict sine monotonicity
        # prove exactly one open root in (1,1+u) WITHOUT a sample scan.
        other=copy.deepcopy(self.src)
        eps=Q(1,2**120)
        other["cos_splines"]={
            "0":{"degree":0,"knots":["0","1","2"],
                 "controls":[str(eps),str(eps)]},
            "1":{"degree":0,"knots":["0","1","2"],
                 "controls":["1","1"]},
        }
        r=m.analyze(other)
        self.assertEqual(r["actual_knot_value"],str(eps))
        self.assertFalse(r["actual_knot_zero"])
        self.assertEqual(r["left_analytic"]["first_nonzero_order"],0)
        self.assertEqual(r["right_adjacent_sign"],1)
        self.assertTrue(eps < Q(1,2**118))

    def test_sine_quarter_cyclotomic_point_signs(self):
        other=copy.deepcopy(self.src)
        other["cos_splines"]={}
        other["sin_splines"]={
            "1":{"degree":0,"knots":["0","1","2"],
                 "controls":["1","1"]}}
        r=m.analyze(other)
        self.assertEqual(r["actual_knot_value"],"1")
        self.assertFalse(r["actual_knot_zero"])
        other["sin_splines"]={
            "2":{"degree":0,"knots":["0","1","2"],
                 "controls":["1","1"]}}
        r=m.analyze(other)
        self.assertTrue(r["actual_knot_zero"])
        self.assertEqual(r["right_one_sided_zero_order"],1)
        self.assertEqual(r["right_adjacent_sign"],-1)

    def test_zero_trig_polynomial_identity_has_no_fake_root_list(self):
        other=copy.deepcopy(self.src)
        other["cos_splines"]={
            "0":{"degree":0,"knots":["0","1","2"],
                 "controls":["0","0"]}}
        r=m.analyze(other)
        self.assertEqual(r["left_analytic"]["status"],"IDENTITY_ZERO")
        self.assertEqual(r["right_analytic"]["status"],"IDENTITY_ZERO")
        self.assertIsNone(r["left_one_sided_zero_order"])
        self.assertTrue(r["actual_knot_zero"])

    def test_noncanonical_and_malformed_source_fail_closed(self):
        for key,val in (("phase_turn_rate","0"),("phase_turn_rate",0.25),
                        ("source_parameter_id","caller-s"),
                        ("parameter_hi","3"),("phase_turn_offset","1/2")):
            other=copy.deepcopy(self.src)
            other[key]=val
            self.assertEqual(m.attempt(other)["status"],"BLOCKED")
        for mutate in (
            lambda s: s["cos_splines"]["0"].__setitem__("degree",1),
            lambda s: s["cos_splines"]["0"].__setitem__("knots",["0","1","3"]),
            lambda s: s["sin_splines"].__setitem__("0",copy.deepcopy(s["cos_splines"]["0"])),
            lambda s: s["cos_splines"].__setitem__("5",copy.deepcopy(s["cos_splines"]["0"])),
            lambda s: s.__setitem__("caller_multiplicity",1),
        ):
            other=copy.deepcopy(self.src)
            mutate(other)
            self.assertEqual(m.attempt(other)["status"],"BLOCKED")

    def test_resource_refusal_is_nontruth(self):
        other=copy.deepcopy(self.src)
        other["cos_splines"]["0"]["controls"]=[str(2**170),"0"]
        x=m.attempt(other)
        self.assertEqual(x["status"],"RESOURCE_REFUSAL")
        self.assertFalse(x["is_truth_value"])

    def test_forged_report_and_capability_promotion_refuse(self):
        report=m.analyze(self.src)
        self.assertEqual(m.validate_report(self.src,report),report)
        for key,val in (("physical_knot_continuous",False),
                        ("fourier_channels_coefficientwise_equal",True),
                        ("right_one_sided_zero_order",1),
                        ("pb00701_certified",True),
                        ("source_sha256","fake"),
                        ("production_authorized",True)):
            forged=copy.deepcopy(report)
            forged[key]=val
            self.assertEqual(m.validate_report(self.src,forged)["status"],"BLOCKED")

    def test_frozen_case_and_evidence_contract_when_checkout_present(self):
        if not (CORPUS.exists() and V2.exists()):
            self.skipTest("full immutable v54/v2 artifacts absent")
        result=census()
        self.assertEqual(result["frozen_original_source_denominator"],121)
        self.assertEqual(result["complete_finite"],49)
        self.assertEqual(result["complete_continuum"],1)

def contract():
    record = expected_machine()
    actual = m.negative_c()
    r = actual["source_bound_knot_certificate"]
    if not (r["physical_knot_continuous"] and
            not r["fourier_channels_coefficientwise_equal"] and
            r["actual_knot_value"] == record["physical_knot_value"] and
            [r["left_one_sided_zero_order"],r["right_one_sided_zero_order"]] ==
            [record["left_one_sided_order"],record["right_one_sided_order"]] and
            [r["left_adjacent_sign"],r["right_adjacent_sign"]] ==
            [record["left_sign"],record["right_sign"]]):
        raise ValueError("MACHINE_KNOT_PROOF_MISMATCH")
    if not REPORT.exists() or REPORT.stat().st_size > 65536:
        raise ValueError("SAVED_MACHINE_REPORT_MISSING_OR_RESOURCE_LIMIT")
    if m.canonical(json.loads(REPORT.read_text())) != m.canonical(record):
        raise ValueError("SAVED_MACHINE_CLAIM_MISMATCH")
    historical = census()
    for name, expected in (
            ("frozen_original_sources_before_after",[121,121]),
            ("frozen_route_refusals_before_after",[20,20]),
            ("frozen_missing_order_premises_before_after",[30,30]),
            ("complete_source_specific_before_after",[50,50])):
        if record[name] != expected:
            raise ValueError("BEFORE_AFTER_MACHINE_CENSUS_DRIFT")
    print("PASS: exact physical phase-aware knot certificate and source-specific negative C")
    print(json.dumps(historical,sort_keys=True))

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--contract",action="store_true")
    ap.add_argument("--self-test",action="store_true")
    flags=ap.parse_args()
    if not(flags.contract or flags.self_test):
        ap.error("specify --contract or --self-test")
    if flags.contract:
        contract()
    if flags.self_test:
        tests=unittest.defaultTestLoader.loadTestsFromTestCase(PhysicalKnotProofTests)
        outcome=unittest.TextTestRunner(verbosity=2).run(tests)
        raise SystemExit(0 if outcome.wasSuccessful() else 1)

if __name__ == "__main__":
    main()
