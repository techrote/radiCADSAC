#!/usr/bin/env python3
"""Adversarial proof checks and exact frozen v54/v2 corpus source-ID census."""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import unittest

import pb00701_discontinuous_knot_topology as m

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "pb00701-finite-owner-corpus-v54.json"
V2 = HERE / "pb00701-post-v54-evidence-reconciliation-v2.json"
REPORT = HERE / "pb00701-discontinuous-knot-topology.json"
CORPUS_BLOB = "5841c331579489b25caef38cd412bdbf286f9134"
V2_BLOB = "e52d3baf3692a011cf86234eeaa992ef407d99fd"


def git_blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def historical_census():
    if git_blob(CORPUS) != CORPUS_BLOB:
        raise ValueError("FROZEN_V54_CORPUS_DRIFT")
    if git_blob(V2) != V2_BLOB:
        raise ValueError("QUALIFIED_V2_REGISTRY_DRIFT")
    c = json.loads(CORPUS.read_text())
    v = json.loads(V2.read_text())
    cases = c["cases"]
    if len(cases) != 121 or len({r["id"] for r in cases}) != 121:
        raise ValueError("FROZEN_121_CASE_ID_DENOMINATOR_DRIFT")
    indexed = {r["id"]: r for r in cases}
    refused = {i for i,r in indexed.items()
               if r["expected"]["v54_disposition"] == "BLOCKED"}
    missing = {i for i,r in indexed.items()
               if r["expected"]["v54_disposition"] ==
               "BLOCKED:SPAN_OWNER_LACKS_EXACT_ORDERED_SPAN_PREMISE"}
    if len(refused) != 20 or len(missing) != 30 or refused & missing:
        raise ValueError("FROZEN_20_30_DISPOSITION_DENOMINATOR_DRIFT")
    rows = v["source_cases"]
    if len(rows) != 50 or {r["case_id"] for r in rows} != refused | missing:
        raise ValueError("V2_FIFTY_ORIGINAL_CASE_IDS_DRIFT")
    for row in rows:
        original = indexed[row["case_id"]]
        spec_sha = hashlib.sha256(m.canonical(original["spec"])).hexdigest()
        if not (row["source_sha256"] == spec_sha ==
                row["evidence"]["source_sha256"] and
                row["origin"] == original["origin"] and
                row["provenance_kind"] == original["kind"] and
                row["historical_v54_disposition"] ==
                    original["expected"]["v54_disposition"] and
                row["historical_disposition_changed"] is False and
                row["registered_evidence_level"] == "COMPLETE_SOURCE_SPECIFIC" and
                row["evidence"]["complete_original_source_zero_set"] is True and
                row["evidence"]["source_parameter_id"] ==
                    original["spec"]["source_parameter_id"] and
                row["evidence"]["phase_turn_law"] ==
                    {"offset": original["spec"]["phase_turn_offset"],
                     "rate": original["spec"]["phase_turn_rate"]}):
            raise ValueError("ORIGINAL_SOURCE_IDENTITY_OR_EVIDENCE_DRIFT:" +
                             row["case_id"])
    summary = v["summary"]
    if not (v["frozen_corpus_git_blob"] == CORPUS_BLOB and
            v["historical_v54"]["original_source_cases"] == 121 and
            v["historical_v54"]["route_refusals"] == 20 and
            v["historical_v54"]["missing_ordered_span_premises"] == 30 and
            summary["by_registered_evidence_level"]["COMPLETE_SOURCE_SPECIFIC"] == 50 and
            summary["complete_finite_sources"] == 49 and
            summary["complete_continuum_sources"] == 1 and
            summary["historical_route_refusals_with_complete_source_evidence"] == 20 and
            summary["historical_missing_ordered_premises_with_complete_source_evidence"] == 30):
        raise ValueError("FROZEN_OR_REGISTERED_CENSUS_DRIFT")
    if m.sha(m.SOURCE) != m.SOURCE_SHA or m.SOURCE_SHA in {
            hashlib.sha256(m.canonical(r["spec"])).hexdigest() for r in cases}:
        raise ValueError("PROSPECTIVE_ORIGINAL_SOURCE_COLLISION")
    return {"frozen_source_denominator": 121,
            "route_refusals_before_after": [20,20],
            "missing_premises_before_after": [30,30],
            "source_specific_complete_before_after": [50,50],
            "complete_finite": 49, "complete_continuum": 1,
            "new_historical_case_ids": [], "all_fifty_original_sha_and_ids_checked": True}


def original_degree_zero_basis_value(spec, x):
    # An independent literal Cox--de Boor degree-zero basis at rational points.
    spline = spec["cos_splines"]["1"]
    knots = [Q(k) for k in spline["knots"]]
    controls = [Q(c) for c in spline["controls"]]
    if x == knots[-1]:
        return controls[-1]  # explicit source terminal clamping
    return sum((c for i,c in enumerate(controls)
                if knots[i] <= x < knots[i+1]), Q(0))


class ExactSourceKnotTests(unittest.TestCase):
    def setUp(self):
        self.src = copy.deepcopy(m.SOURCE)

    def test_original_sha_and_true_original_degree_zero_knot(self):
        self.assertEqual(m.sha(self.src), m.SOURCE_SHA)
        for x, value in [(Q(0),Q(0)), (Q(1,2),Q(0)),
                         (Q(1)-Q(1,2**128),Q(0)), (Q(1),Q(1)),
                         (Q(1)+Q(1,10**24),Q(1)),(Q(2),Q(1))]:
            self.assertEqual(original_degree_zero_basis_value(self.src,x),value)

    def test_right_internal_half_open_identity_component(self):
        a = m.analyze(self.src)
        self.assertEqual(a["maximal_zero_components"],
                         [m.component(Q(0),Q(1),True,False,"ZERO")])
        self.assertEqual(a["maximal_constant_sign_components"],
                         [m.component(Q(1),Q(2),True,True,"POSITIVE")])
        self.assertEqual(a["actual_knot_point_sign"],1)
        self.assertFalse(a["zero_set_relatively_closed"])
        self.assertFalse(a["physical_continuity_at_knot"])

    def test_counterfactual_same_open_pieces_but_distinct_point(self):
        a=m.analyze(self.src,m.RIGHT)
        b=m.analyze(self.src,m.LEFT)
        self.assertEqual(a["original_open_piece_zero_relations"],
                         b["original_open_piece_zero_relations"])
        self.assertNotEqual(a["actual_knot_point_zero"],b["actual_knot_point_zero"])
        self.assertEqual(b["maximal_zero_components"],
                         [m.component(Q(0),Q(1),True,True,"ZERO")])

    def test_exact_nonclosedness_sequence(self):
        # Universal mathematical sequence x_n=1-2^-n; these exact
        # adversarial points challenge an implementation's boundary policy.
        for n in (1,2,8,40,128):
            self.assertEqual(original_degree_zero_basis_value(
                self.src,Q(1)-Q(1,2**n)),0)
        self.assertNotEqual(original_degree_zero_basis_value(self.src,Q(1)),0)

    def test_sign_jumps_without_zeros(self):
        for controls, sides in ((["1","-1"],[1,-1]),
                                (["-1","1"],[-1,1])):
            other=copy.deepcopy(self.src)
            other["cos_splines"]["1"]["controls"]=controls
            a=m.analyze(other)
            self.assertFalse(a["maximal_zero_components"])
            self.assertEqual([a["left_one_sided_sign"],a["right_one_sided_sign"]],
                             sides)
            self.assertEqual(len(a["maximal_constant_sign_components"]),2)

    def test_both_zero_has_one_closed_continuum(self):
        self.src["cos_splines"]["1"]["controls"]=["0","0"]
        for policy in (m.RIGHT,m.LEFT):
            a=m.analyze(self.src,policy)
            self.assertEqual(a["maximal_zero_components"],
                             [m.component(Q(0),Q(2),True,True,"ZERO")])
            self.assertEqual(a["maximal_constant_sign_components"],[])
            self.assertTrue(a["zero_set_relatively_closed"])

    def test_right_identity_open_or_closed_at_knot(self):
        self.src["cos_splines"]["1"]["controls"]=["1","0"]
        a=m.analyze(self.src,m.RIGHT)
        b=m.analyze(self.src,m.LEFT)
        self.assertEqual(a["maximal_zero_components"],
                         [m.component(Q(1),Q(2),True,True,"ZERO")])
        self.assertEqual(b["maximal_zero_components"],
                         [m.component(Q(1),Q(2),False,True,"ZERO")])

    def test_nonzero_discontinuous_same_sign_components_merge(self):
        self.src["cos_splines"]["1"]["controls"]=["1","2"]
        a=m.analyze(self.src)
        self.assertFalse(a["physical_continuity_at_knot"])
        self.assertEqual(a["maximal_constant_sign_components"],
                         [m.component(Q(0),Q(2),True,True,"POSITIVE")])

    def test_extremely_small_controls_are_not_zeros(self):
        for value,sign in ((Q(1,2**120),1),(-Q(1,2**120),-1)):
            self.src["cos_splines"]["1"]["controls"]=[str(value),"1"]
            a=m.analyze(self.src)
            self.assertFalse(a["maximal_zero_components"])
            self.assertEqual(a["left_one_sided_sign"],sign)

    def test_valid_nonzero_negative_or_stationary_phase(self):
        self.src["phase_turn_offset"]="1/8"
        self.src["phase_turn_rate"]="-1/16"
        self.assertEqual(m.analyze(self.src)["phase_turn_endpoints"],["1/8","0"])
        self.src["phase_turn_offset"]="0"
        self.src["phase_turn_rate"]="0"
        self.assertEqual(m.analyze(self.src)["phase_turn_endpoints"],["0","0"])

    def test_exact_boundary_and_out_of_sector_refuse_not_truth(self):
        for rate in ("1/8","1"):
            self.src["phase_turn_rate"]=rate
            a=m.attempt(self.src)
            self.assertEqual(a["status"],"BLOCKED")
            self.assertFalse(a["is_truth_value"])

    def test_noncanonical_rationals_or_binary_floats_refuse(self):
        for raw in ("0/1","1.0","invalid",True,0.0,1):
            other=copy.deepcopy(self.src)
            other["phase_turn_rate"]=raw
            self.assertEqual(m.attempt(other)["status"],"BLOCKED")

    def test_wrong_grammar_knot_degree_parameter_and_sine_refuse(self):
        mutations = [
            lambda x:x.__setitem__("source_parameter_id","caller-s"),
            lambda x:x["cos_splines"]["1"].__setitem__("degree",1),
            lambda x:x["cos_splines"]["1"].__setitem__("knots",["0","1","1"]),
            lambda x:x["sin_splines"].__setitem__("1",
                                                 copy.deepcopy(x["cos_splines"]["1"])),
            lambda x:x["cos_splines"].__setitem__("2",
                                                 copy.deepcopy(x["cos_splines"]["1"])),
            lambda x:x.__setitem__("caller_root_count",0),
        ]
        for mutate in mutations:
            other=copy.deepcopy(self.src)
            mutate(other)
            self.assertEqual(m.attempt(other)["status"],"BLOCKED")

    def test_unbound_point_policy_refuses(self):
        self.assertEqual(m.attempt(self.src,"INFER_FROM_OPEN_ROOTS")["status"],
                         "BLOCKED")

    def test_budget_is_atomic_nontruth(self):
        self.src["cos_splines"]["1"]["controls"]=[str(2**180),"1"]
        a=m.attempt(self.src)
        self.assertEqual(a["status"],"RESOURCE_REFUSAL")
        self.assertFalse(a["is_truth_value"])

    def test_source_and_policy_bound_forgery_checks(self):
        a=m.analyze(self.src)
        self.assertEqual(m.validate_report(self.src,m.RIGHT,a),a)
        self.assertEqual(m.validate_report(self.src,m.LEFT,a)["status"],"BLOCKED")
        for field,value in (("actual_knot_point_zero",True),
                            ("zero_set_relatively_closed",True),
                            ("pb00701_certified",True),
                            ("production_authorized",True),
                            ("source_sha256","fake")):
            forged=copy.deepcopy(a)
            forged[field]=value
            self.assertEqual(m.validate_report(self.src,m.RIGHT,forged)["status"],
                             "BLOCKED")
        forged=copy.deepcopy(a)
        forged["maximal_zero_components"][0]["right_closed"]=True
        self.assertEqual(m.validate_report(self.src,m.RIGHT,forged)["status"],
                         "BLOCKED")

    def test_negative_c_nonclaims_and_zero_delta(self):
        r=m.negative_c()
        self.assertEqual(r["historical_source_denominator_before_after"],[121,121])
        self.assertEqual(r["historical_route_refusals_before_after"],[20,20])
        self.assertEqual(r["historical_missing_premises_before_after"],[30,30])
        self.assertEqual(r["complete_source_specific_before_after"],[50,50])
        self.assertEqual(r["new_historical_case_ids_closed"],[])
        self.assertFalse(r["pb00701_certified"])

    def test_all_fifty_frozen_source_identities_when_in_checkout(self):
        if not (CORPUS.exists() and V2.exists()):
            self.skipTest("full frozen corpus only present in repository checkout")
        self.assertEqual(historical_census()["complete_continuum"],1)


def contract():
    census = historical_census()
    if not REPORT.exists() or REPORT.stat().st_size > 65536:
        raise ValueError("MACHINE_REPORT_MISSING_OR_RESOURCE_LIMIT")
    if m.canonical(json.loads(REPORT.read_text())) != m.canonical(m.negative_c()):
        raise ValueError("SAVED_MACHINE_NEGATIVE_C_MISMATCH")
    print("PASS: source/policy exact negative-C report and 121/20/30/50 pinned census")
    print(json.dumps(census,sort_keys=True))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract",action="store_true")
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    if not (args.contract or args.self_test):
        parser.error("specify --contract and/or --self-test")
    if args.contract:
        contract()
    if args.self_test:
        tests=unittest.defaultTestLoader.loadTestsFromTestCase(ExactSourceKnotTests)
        result=unittest.TextTestRunner(verbosity=2).run(tests)
        raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__=="__main__":
    main()
